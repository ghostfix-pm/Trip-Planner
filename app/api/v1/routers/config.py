from fastapi import APIRouter
from app.schemas.request import (
    HotelPriceLevel, HotelAmenity, 
    FoodPriceLevel, FoodCategory, ActivityCategory,
    FlightClass, TravelPace
)

from app.settings.tags_config import (
    ALL_FOOD_TAGS, ALL_ACTIVITY_TAGS,
    POPULAR_FOOD_BACKUPS, POPULAR_ACTIVITY_BACKUPS,
    CITIES_DB,
)

router = APIRouter(tags=["Configuration"])

@router.get("/tag_config", summary="Get configuration tags for frontend form rendering")
async def get_tag_config():
    return {
        "hotel_price_levels": [e.value for e in HotelPriceLevel],
        "hotel_amenities": [e.value for e in HotelAmenity],
        "food_price_levels": [e.value for e in FoodPriceLevel],
        "food_categories": [e.value for e in FoodCategory],
        "activity_categories": [e.value for e in ActivityCategory],
        "flight_classes": [e.value for e in FlightClass],
        "travel_paces": [e.value for e in TravelPace],
        "cities" : CITIES_DB,
    }