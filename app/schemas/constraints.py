from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date

from app.settings.tags_config import (
    HotelCategory, HotelAmenity, FoodCategory, ActivityCategory,
    FlightClass, HotelPriceLevel, FoodPriceLevel, TravelPace, DietaryRestriction
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
    
    hotel_price_level: HotelPriceLevel = "moderate"
    hotel_amenities: List[HotelAmenity] = []
    
    food_price_level: FoodPriceLevel = "standard"
    food_categories: List[FoodCategory] = []
    dietary_restrictions: List[DietaryRestriction] = ["none"]
    
    activity_categories: List[ActivityCategory] = []
    
    flight_class: FlightClass = "Economy"
    non_stop_only: bool = False
    travel_pace: TravelPace = "balanced"

TripConstraints = ExtractedConstraints