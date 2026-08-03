from datetime import date

import pytest
from fastapi.testclient import TestClient

import app.api.v1.planner as planner_module
from app.db.database import AsyncSessionLocal
from app.db.models import APIQueryCacheModel, ClusterModel, DestinationModel, HotelModel, TripModel, UserModel
from app.schemas.response import TravelPlanResponse
from main import app

MODELS_TO_CLEAR = [TripModel, UserModel, HotelModel, DestinationModel, ClusterModel, APIQueryCacheModel]


@pytest.fixture(autouse=True)
async def _clean_db():
    """Wipe all tables between tests so fixtures are fully isolated."""
    yield
    async with AsyncSessionLocal() as session:
        for model in MODELS_TO_CLEAR:
            await session.execute(model.__table__.delete())
        await session.commit()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _register(client, email="zoe@example.com"):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Zoe"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _login(client, email="zoe@example.com"):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _trip_payload():
    return {
        "origin": "HAN",
        "destination": "SGN",
        "departure_date": date(2026, 12, 1).isoformat(),
        "return_date": date(2026, 12, 5).isoformat(),
        "max_budget": 1500.0,
    }


def _fake_plan(monkeypatch, total_cost_min=900.0, total_cost_max=950.0):
    plan = TravelPlanResponse(
        status="SUCCESS",
        message="Trip planning completed successfully.",
        itinerary_options=[{
            "option_name": "Test option",
            "selected_hotel": {"name": "Test Hotel", "latitude": 10.0, "longitude": 106.0},
            "summary_cost": {
                "total_cost_min": total_cost_min,
                "total_cost_max": total_cost_max,
            },
        }],
        candidates={"flights": [], "hotels": [], "foods": [], "activities": []},
    ).model_dump(mode="json")

    async def fake_run_trip_planner(request):
        return plan

    monkeypatch.setattr(planner_module, "run_trip_planner", fake_run_trip_planner)


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_login(client):
    _register(client)
    token = _login(client)
    assert len(token) > 20


def test_register_duplicate_email_rejected(client):
    _register(client)
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "zoe@example.com", "password": "secret123"},
    )
    assert resp.status_code == 400


def test_plan_trip_requires_auth(client):
    resp = client.post("/api/v1/plan-trip", json=_trip_payload())
    assert resp.status_code == 401


def test_plan_trip_saves_within_budget(client, monkeypatch):
    _fake_plan(monkeypatch, total_cost_min=900.0, total_cost_max=950.0)
    _register(client)
    token = _login(client)
    resp = client.post(
        "/api/v1/plan-trip",
        json=_trip_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers.get("X-Trip-Id")

    trip_id = resp.headers["X-Trip-Id"]
    detail = client.get(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    body = detail.json()
    assert body["selected_hotel"]["name"] == "Test Hotel"
    assert body["summary_cost"]["total_cost_min"] == 900.0


def test_plan_trip_over_budget_flag(client, monkeypatch):
    _fake_plan(monkeypatch, total_cost_min=2000.0, total_cost_max=2100.0)
    _register(client)
    token = _login(client)
    resp = client.post(
        "/api/v1/plan-trip",
        json=_trip_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    trip_id = resp.headers["X-Trip-Id"]

    trips = client.get(
        "/api/v1/trips",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert trips.status_code == 200
    listed = trips.json()
    assert len(listed) == 1
    assert listed[0]["id"] == trip_id
    assert listed[0]["is_within_budget"] is False


def test_list_trips_empty(client):
    _register(client, email="empty@example.com")
    token = _login(client, email="empty@example.com")
    resp = client.get("/api/v1/trips", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_trip_404_for_other_user(client, monkeypatch):
    _fake_plan(monkeypatch)
    _register(client, email="alice@example.com")
    token_alice = _login(client, email="alice@example.com")
    resp = client.post(
        "/api/v1/plan-trip",
        json=_trip_payload(),
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    trip_id = resp.headers["X-Trip-Id"]

    _register(client, email="bob@example.com")
    token_bob = _login(client, email="bob@example.com")
    resp = client.get(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert resp.status_code == 404


def test_delete_trip(client, monkeypatch):
    _fake_plan(monkeypatch)
    _register(client)
    token = _login(client)
    resp = client.post(
        "/api/v1/plan-trip",
        json=_trip_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    trip_id = resp.headers["X-Trip-Id"]

    resp = client.delete(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204

    resp = client.get(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_delete_trip_404(client):
    _register(client)
    token = _login(client)
    resp = client.delete(
        "/api/v1/trips/does-not-exist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_plan_trip_invalid_dates_rejected(client):
    _register(client)
    token = _login(client)
    payload = _trip_payload()
    payload["return_date"] = "2026-11-01"  # before departure
    resp = client.post(
        "/api/v1/plan-trip",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
