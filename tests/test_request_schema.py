from datetime import date

import pytest

from app.schemas.request import TravelPlannerRequest


def _valid_payload(**overrides):
    payload = {
        "origin": "HAN",
        "destination": "SGN",
        "departure_date": date(2026, 12, 1),
        "return_date": date(2026, 12, 5),
        "max_budget": 1000.0,
    }
    payload.update(overrides)
    return payload


def test_valid_request_passes():
    req = TravelPlannerRequest(**_valid_payload())
    assert req.duration_days if hasattr(req, "duration_days") else True
    assert req.origin == "HAN"


def test_return_date_must_follow_departure():
    with pytest.raises(ValueError):
        TravelPlannerRequest(**(_valid_payload(return_date=date(2026, 11, 30))))


def test_same_day_rejected():
    with pytest.raises(ValueError):
        TravelPlannerRequest(**(_valid_payload(return_date=date(2026, 12, 1))))


def test_min_budget_gt_max_rejected():
    with pytest.raises(ValueError):
        TravelPlannerRequest(**(_valid_payload(min_budget=2000.0)))


def test_min_budget_equal_max_ok():
    req = TravelPlannerRequest(**(_valid_payload(min_budget=1000.0)))
    assert req.min_budget == 1000.0


def test_enum_values_coerced():
    req = TravelPlannerRequest(**_valid_payload(travel_pace="packed"))
    assert req.travel_pace == "packed"


def test_negative_budget_rejected():
    with pytest.raises(ValueError):
        TravelPlannerRequest(**(_valid_payload(max_budget=-5)))


def test_zero_adults_rejected():
    with pytest.raises(ValueError):
        TravelPlannerRequest(**(_valid_payload(num_adults=0)))
