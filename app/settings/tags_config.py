# app/config/tags_config.py

# Import trực tiếp các Enum gốc từ Schema
from app.schemas.request import (
    FoodCategory, 
    ActivityCategory, 
    HotelAmenity, 
    HotelPriceLevel, 
    FoodPriceLevel, 
    FlightClass
)

# ==========================================
# 1. DANH SÁCH TAGS CƠ BẢN (Lấy tự động từ Enum, không gõ tay lại)
# ==========================================
ALL_FOOD_TAGS = [member.value for member in FoodCategory]
ALL_ACTIVITY_TAGS = [member.value for member in ActivityCategory]

POPULAR_FOOD_BACKUPS = [
    FoodCategory.cafe.value, 
    FoodCategory.street_food.value, 
    FoodCategory.seafood.value, 
    FoodCategory.dessert.value, 
    FoodCategory.bbq.value
]

POPULAR_ACTIVITY_BACKUPS = [
    ActivityCategory.landmark.value, 
    ActivityCategory.park.value, 
    ActivityCategory.shopping.value, 
    ActivityCategory.museum.value, 
    ActivityCategory.nature.value
]

# ==========================================
# 2. DICTIONARY MAPPING (Sử dụng Enum làm Key để bảo vệ logic)
# ==========================================

# Ánh xạ Tiện ích Khách sạn sang ID chuẩn của SerpApi
AMENITY_TO_ID_MAP = {
    HotelAmenity.free_wifi: "35",       
    HotelAmenity.swimming_pool: "6",    
    HotelAmenity.gym: "7",              
    HotelAmenity.free_breakfast: "9",   
    HotelAmenity.parking: "3",          
    HotelAmenity.spa: "10",             
    HotelAmenity.pet_friendly: "19",     
    HotelAmenity.free_parking: "1",
    HotelAmenity.wheelchair_accessible: "53",
    HotelAmenity.restaurant: "8"
}

# Ánh xạ Hạng sao
HOTEL_CLASS_MAP = {
    HotelPriceLevel.budget: "2,3",      
    HotelPriceLevel.moderate: "3,4",    
    HotelPriceLevel.upscale: "4,5",     
    HotelPriceLevel.luxury: "5"         
}

# Ánh xạ Mức giá Quán ăn (Food Price Level -> Min/Max Price)
FOOD_PRICE_MAP = {
    FoodPriceLevel.budget: {"max_price": 2},       
    FoodPriceLevel.standard: {},                   
    FoodPriceLevel.gourmet: {"min_price": 3}       
}

# Ánh xạ Hạng ghế Máy bay
FLIGHT_CLASS_MAP = {
    FlightClass.economy: 1, 
    FlightClass.premium_economy: 2, 
    FlightClass.business: 3, 
    FlightClass.first: 4
}

CITIES_DB = [
    {"name": "Hà Nội", "iata": "HAN", "region": "", "country": "Vietnam"},
    {"name": "Hồ Chí Minh", "iata": "SGN", "region": "", "country": "Vietnam"},
    {"name": "Đà Nẵng", "iata": "DAD", "region": "", "country": "Vietnam"},
    {"name": "Phú Quốc", "iata": "PQC", "region": "", "country": "Vietnam"},
    {"name": "Nha Trang", "iata": "CXR", "region": "", "country": "Vietnam"},
    {"name": "Đà Lạt", "iata": "DLI", "region": "", "country": "Vietnam"},
    {"name": "Hải Phòng", "iata": "HPH", "region": "", "country": "Vietnam"},
    {"name": "Bangkok", "iata": "BKK", "region": "", "country": "Thailand"},
    {"name": "Singapore", "iata": "SIN", "region": "", "country": "Singapore"},
    {"name": "Seoul", "iata": "ICN", "region": "", "country": "South Korea"},
    {"name": "Tokyo", "iata": "HND", "region": "", "country": "Japan"},
    {"name": "Osaka", "iata": "KIX", "region": "", "country": "Japan"},
    {"name": "Taipei", "iata": "TPE", "region": "", "country": "Taiwan"},
    {"name": "Paris", "iata": "CDG", "region": "", "country": "France"},
    {"name": "London", "iata": "LHR", "region": "", "country": "United Kingdom"},
    {"name": "New York", "iata": "JFK", "region": "NY", "country": "United States"},
    {"name": "Washington DC", "iata": "IAD", "region": "DC", "country": "United States"},
    {"name": "Los Angeles", "iata": "LAX", "region": "CA", "country": "United States"},
    {"name": "Sydney", "iata": "SYD", "region": "NSW", "country": "Australia"}
]

CITY_TO_IATA_MAP = {
    "Hà Nội": "HAN",
    "Hồ Chí Minh": "SGN",
    "Đà Nẵng": "DAD",
    "Phú Quốc": "PQC",
    "Nha Trang": "CXR",
    "Đà Lạt": "DLI",
    "Hải Phòng": "HPH",
    "Bangkok": "BKK",
    "Singapore": "SIN",
    "Seoul": "ICN",
    "Tokyo": "HND",
    "Osaka": "KIX",
    "Taipei": "TPE",
    "Paris": "CDG",
    "London": "LHR",
    "New York": "JFK",
    "Washington DC": "IAD",
    "Los Angeles": "LAX",
    "Sydney": "SYD"
}