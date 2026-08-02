# app/db/models.py
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    
    refresh_token = Column(String, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HotelModel(Base):
    __tablename__ = "hotels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    type = Column(String, nullable=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    check_in_time = Column(String, nullable=True)
    check_out_time = Column(String, nullable=True)
    
    rate_per_night = Column(JSON, nullable=True)
    total_rate = Column(JSON, nullable=True)
    nearby_places = Column(JSON, nullable=True)
    extracted_hotel_class = Column(Integer, nullable=True)
    images = Column(JSON, nullable=True)
    
    overall_rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    ratings_5_stars = Column(Integer, nullable=True)
    ratings_4_stars = Column(Integer, nullable=True)
    ratings_3_stars = Column(Integer, nullable=True)
    ratings_2_stars = Column(Integer, nullable=True)
    ratings_1_stars = Column(Integer, nullable=True)
    location_rating = Column(Float, nullable=True)
    
    reviews_breakdown = Column(JSON, nullable=True)
    amenities = Column(JSON, nullable=True)
    
    raw_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DestinationModel(Base):
    __tablename__ = "destinations"

    place_id = Column(String, primary_key=True) 
    
    title = Column(String, nullable=False, index=True)
    
    gps_coordinates = Column(JSON, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    
    type = Column(String, nullable=True)
    types = Column(JSON, nullable=True)
    type_id = Column(String, nullable=True)
    type_ids = Column(JSON, nullable=True)
    
    address = Column(Text, nullable=True)
    country = Column(String, nullable=True)
    
    operating_hours_monday = Column(String, nullable=True)
    operating_hours_tuesday = Column(String, nullable=True)
    operating_hours_wednesday = Column(String, nullable=True)
    operating_hours_thursday = Column(String, nullable=True)
    operating_hours_friday = Column(String, nullable=True)
    operating_hours_saturday = Column(String, nullable=True)
    operating_hours_sunday = Column(String, nullable=True)
    
    phone = Column(String, nullable=True)
    website = Column(Text, nullable=True)
    
    extensions = Column(JSON, nullable=True)
    unsupported_extensions = Column(JSON, nullable=True)
    service_options = Column(JSON, nullable=True)
    
    thumbnail = Column(Text, nullable=True)
    user_review = Column(Text, nullable=True)
    reserve_a_table = Column(Text, nullable=True)
    
    raw_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClusterModel(Base):
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_lat = Column(Float, index=True)
    grid_lng = Column(Float, index=True)
    restaurant_place_ids = Column(JSON, default=list)
    last_updated = Column(DateTime, default=datetime.utcnow)

class TripModel(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False) 
    
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    max_budget = Column(Float, nullable=False)
    total_estimated_cost = Column(Float, nullable=False)
    is_within_budget = Column(Boolean, default=True)
    
    itinerary_data = Column(JSON, nullable=False)
    google_maps_route_url = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class APIQueryCacheModel(Base):
    __tablename__ = "api_query_cache"

    query_hash = Column(String, primary_key=True) 
    response_data = Column(JSON, nullable=False) 
    expires_at = Column(DateTime, nullable=False, index=True) 
    created_at = Column(DateTime, default=datetime.utcnow)