from __future__ import annotations
import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Response, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import db
from app.db.database import get_db
from app.db.models import TripModel, UserModel
from app.api.v1.deps import get_current_user

from app.agents.graph import run_trip_planner
from app.schemas.request import TripRequest
from fastapi.encoders import jsonable_encoder
from app.schemas.response import TravelPlanResponse

router = APIRouter(tags=["planner"])
logger = logging.getLogger("trip_planner.api")
logger.setLevel(logging.INFO)

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
    
    opt_data = plan.get("best_recommended_itinerary", {})
    total_cost = opt_data.get("total_estimated_cost", 0.0)
    
    safe_itinerary_data = jsonable_encoder(opt_data) 
    
    new_trip = TripModel(
        id=trip_id,
        user_id=current_user.id,
        origin=request.origin,
        destination=request.destination,
        duration_days=duration_days,
        max_budget=request.max_budget,
        total_estimated_cost=total_cost,
        is_within_budget=True,
        itinerary_data=safe_itinerary_data,
    )
    
    db.add(new_trip)
    await db.commit()
    logger.info("Saved trip %s to database.", trip_id)

    response.headers["X-Trip-Id"] = trip_id
    return plan

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