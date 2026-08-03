from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.request import (
    ActivityCategory,
    FlightClass,
    FoodCategory,
    FoodPriceLevel,
    HotelAmenity,
    HotelPriceLevel,
    TravelPace,
)


class ExtractedConstraints(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    origin: str = ""
    destination: str = ""
    departure_date: Optional[date] = None
    return_date: Optional[date] = None

    min_budget: float = 0.0
    max_budget: float = 0.0

    num_adults: int = 1
    num_children: int = 0
    num_infants: int = 0
    num_elderly: int = 0

    hotel_price_level: HotelPriceLevel = HotelPriceLevel.moderate
    hotel_amenities: List[HotelAmenity] = []

    food_price_level: FoodPriceLevel = FoodPriceLevel.standard
    food_categories: List[FoodCategory] = []

    activity_categories: List[ActivityCategory] = []

    flight_class: FlightClass = FlightClass.economy
    non_stop_only: bool = False
    travel_pace: TravelPace = TravelPace.balanced


TripConstraints = ExtractedConstraints
