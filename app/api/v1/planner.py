from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.agents.graph import run_trip_planner
from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.db.models import TripModel, UserModel
from app.schemas.request import TripRequest
from app.schemas.response import TravelPlanResponse, TripSummaryResponse

router = APIRouter(tags=["planner"])
logger = logging.getLogger("trip_planner.api")
logger.setLevel(logging.INFO)


def _extract_optimized_option(plan: dict) -> dict:
    """Pull the best itinerary option from a plan response.

    The response model exposes candidates under ``itinerary_options``;
    ``best_recommended_itinerary`` was a leftover key that never existed,
    which silently persisted empty itinerary data for every trip.
    """
    options = plan.get("itinerary_options") or []
    if not options:
        return {}
    first = options[0]
    if isinstance(first, list) and first:
        return first[0]
    return first if isinstance(first, dict) else {}


@router.post("/plan-trip", response_model=TravelPlanResponse)
async def plan_trip(
    request: TripRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> TravelPlanResponse:
    logger.info("User %s requested a travel plan to %s", current_user.email, request.destination)

    plan = await run_trip_planner(request)
    logger.info("Successfully generated travel plan.")

    trip_id = str(uuid4())
    duration_days = max(1, (request.return_date - request.departure_date).days)

    opt_data = _extract_optimized_option(plan)
    summary_cost = opt_data.get("summary_cost", {}) if isinstance(opt_data, dict) else {}
    total_cost_min = summary_cost.get("total_cost_min", 0.0) or 0.0
    total_cost_max = summary_cost.get("total_cost_max", total_cost_min) or total_cost_min

    safe_itinerary_data = jsonable_encoder(opt_data)

    new_trip = TripModel(
        id=trip_id,
        user_id=current_user.id,
        origin=request.origin,
        destination=request.destination,
        duration_days=duration_days,
        max_budget=request.max_budget,
        total_estimated_cost=total_cost_min,
        is_within_budget=total_cost_max <= float(request.max_budget or 0),
        itinerary_data=safe_itinerary_data,
    )

    db.add(new_trip)
    await db.commit()
    logger.info("Saved trip %s to database.", trip_id)

    response.headers["X-Trip-Id"] = trip_id
    return plan


@router.get("/trips", response_model=list[TripSummaryResponse])
async def list_trips(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> list[TripSummaryResponse]:
    """List all trips belonging to the current user, newest first."""
    logger.info("Listing trips for user %s", current_user.email)

    stmt = (
        select(TripModel)
        .where(TripModel.user_id == current_user.id)
        .order_by(TripModel.created_at.desc())
    )
    result = await db.execute(stmt)
    trips = result.scalars().all()

    return [
        TripSummaryResponse(
            id=trip.id,
            origin=trip.origin,
            destination=trip.destination,
            duration_days=trip.duration_days,
            max_budget=trip.max_budget,
            total_estimated_cost=trip.total_estimated_cost,
            is_within_budget=trip.is_within_budget,
            created_at=trip.created_at,
        )
        for trip in trips
    ]


@router.get("/trips/{trip_id}")
async def get_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    logger.info("Fetching trip with id: %s", trip_id)

    stmt = select(TripModel).where(
        (TripModel.id == trip_id) &
        (TripModel.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    trip = result.scalars().first()

    if trip is None:
        logger.warning("Trip %s not found or unauthorized access attempt", trip_id)
        raise HTTPException(status_code=404, detail="Trip not found or access denied.")

    logger.info("Successfully retrieved trip data.")
    return trip.itinerary_data


@router.delete("/trips/{trip_id}", status_code=204)
async def delete_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> None:
    """Delete one of the current user's trips."""
    logger.info("Deleting trip with id: %s", trip_id)

    stmt = select(TripModel).where(
        (TripModel.id == trip_id) &
        (TripModel.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    trip = result.scalars().first()

    if trip is None:
        logger.warning("Trip %s not found or unauthorized access attempt", trip_id)
        raise HTTPException(status_code=404, detail="Trip not found or access denied.")

    await db.delete(trip)
    await db.commit()
    logger.info("Deleted trip %s.", trip_id)
