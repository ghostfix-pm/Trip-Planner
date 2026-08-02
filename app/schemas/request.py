from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from enum import Enum

class HotelAmenity(str, Enum):
    free_wifi = "free wifi"
    swimming_pool = "swimming pool"
    gym = "gym"
    free_breakfast = "free breakfast"
    parking = "parking"
    spa = "spa"
    pet_friendly = "pet friendly"
    free_parking = "free parking"
    wheelchair_accessible = "wheelchair accessible"
    restaurant = "restaurant"

class FoodCategory(str, Enum):
    vietnamese = "vietnamese"
    japanese = "japanese"
    korean = "korean"
    chinese = "chinese"
    thai = "thai"
    italian = "italian"
    french = "french"
    indian = "indian"
    bbq = "bbq"
    steakhouse = "steakhouse"
    seafood = "seafood"
    vegetarian = "vegetarian"
    vegan = "vegan"
    street_food = "street food"
    cafe = "cafe"
    dessert = "dessert"
    sushi = "sushi"
    ramen = "ramen"

class ActivityCategory(str, Enum):
    museum = "museum"
    park = "park"
    landmark = "landmark"
    historical_site = "historical site"
    temple = "temple"
    beach = "beach"
    nature = "nature"
    shopping = "shopping"
    nightlife = "nightlife"
    entertainment = "entertainment"
    family = "family"
    adventure = "adventure"
    art_gallery = "art gallery"

class FlightClass(str, Enum):
    economy = "economy"
    premium_economy = "premium economy"
    business = "business"
    first = "first"

class HotelPriceLevel(str, Enum):
    budget = "budget"
    moderate = "moderate"
    upscale = "upscale"
    luxury = "luxury"

class FoodPriceLevel(str, Enum):
    budget = "budget"
    standard = "standard"
    gourmet = "gourmet"

class TravelPace(str, Enum):
    relaxed = "relaxed"
    balanced = "balanced"
    packed = "packed"


class TravelPlannerRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    origin: str = Field(..., description="Điểm xuất phát", example="HAN")
    destination: str = Field(..., description="Điểm đến", example="SGN")
    departure_date: date = Field(...)
    return_date: date = Field(...)

    min_budget: Optional[float] = Field(default=0.0, ge=0)
    max_budget: float = Field(..., gt=0)

    num_adults: int = Field(default=1, ge=1)
    num_children: int = Field(default=0, ge=0)
    num_infants: int = Field(default=0, ge=0)
    num_elderly: int = Field(default=0, ge=0)

    hotel_price_level: Optional[HotelPriceLevel] = Field(default=HotelPriceLevel.moderate)
    hotel_amenities: List[HotelAmenity] = Field(default=[])

    food_price_level: Optional[FoodPriceLevel] = Field(default=FoodPriceLevel.standard)
    food_categories: List[FoodCategory] = Field(default=[])

    activity_categories: List[ActivityCategory] = Field(default=[])

    flight_class: Optional[FlightClass] = Field(default=FlightClass.economy)
    non_stop_only: bool = Field(default=False)

    travel_pace: Optional[TravelPace] = Field(default=TravelPace.balanced)

TravelRequest = TravelPlannerRequest
TripRequest = TravelPlannerRequest