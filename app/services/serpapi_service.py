import requests
import math
import random
from app.schemas.request import TravelRequest

from app.settings.tags_config import (
    CITY_TO_IATA_MAP, 
    FLIGHT_CLASS_MAP, 
    HOTEL_CLASS_MAP, 
    AMENITY_TO_ID_MAP, 
    FOOD_PRICE_MAP
)

class SerpApiQueryBuilder:
    
    @staticmethod
    def build_flight_query(request: TravelRequest) -> dict:
        raw_origin = request.origin.split(",")[0].strip()
        raw_dest = request.destination.split(",")[0].strip()
        
        origin_iata = CITY_TO_IATA_MAP.get(raw_origin, raw_origin)
        destination_iata = CITY_TO_IATA_MAP.get(raw_dest, raw_dest)

        travel_class_id = FLIGHT_CLASS_MAP.get(request.flight_class, 1)
        stops_count = 1 if request.non_stop_only else 0

        return {
            "engine": "google_flights",
            "departure_id": origin_iata,            
            "arrival_id": destination_iata,         
            "outbound_date": request.departure_date.strftime("%Y-%m-%d"),
            "return_date": request.return_date.strftime("%Y-%m-%d"),
            "adults": request.num_adults,
            "children": request.num_children,
            "infants_in_seat": request.num_infants,
            "travel_class": travel_class_id,
            "type": 1, 
            "stops": stops_count
        }
    
    @staticmethod
    def build_hotel_query(request: TravelRequest) -> dict:
        mapped_hotel_classes = HOTEL_CLASS_MAP.get(request.hotel_price_level, "3,4")
        amenity_ids = [AMENITY_TO_ID_MAP[am] for am in request.hotel_amenities if am in AMENITY_TO_ID_MAP]

        search_query = f"{request.destination} hotels"

        payload = {
            "engine": "google_hotels",
            "q": search_query.strip(),
            "check_in_date": request.departure_date.strftime("%Y-%m-%d"),
            "check_out_date": request.return_date.strftime("%Y-%m-%d"),
            "adults": request.num_adults,
            "currency": "USD",
            "hotel_classes": mapped_hotel_classes
        }
            
        if getattr(request, "num_children", 0) > 0:
            payload["children"] = request.num_children
            payload["children_ages"] = ",".join(["7"] * request.num_children)

        if amenity_ids:
            payload["amenities"] = ",".join(amenity_ids)

        return payload

    @staticmethod
    def build_activity_queries(request: TravelRequest) -> list[dict]:
        queries = []

        queries.append({
            "engine": "google_maps",
            "q": f"best tourist attractions in {request.destination}",
            "type": "search",
            "google_domain": "google.com",
            "hl": "en"
        })

        if request.activity_categories:
            safe_act_tags = random.sample(
                request.activity_categories, 
                min(5, len(request.activity_categories))
            )
            for tag in safe_act_tags:
                queries.append({
                    "engine": "google_maps",
                    "q": f"{tag} in {request.destination}".strip(),
                    "type": "search",
                    "google_domain": "google.com",
                    "hl": "en"
                })

        return queries

    @staticmethod
    def build_food_query(ll_param: str) -> dict:
        return {
            "engine": "google_maps",
            "q": "restaurants",
            "ll": ll_param,
            "type": "search",
            "hl": "en"
        }

class SerpApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"

    def fetch_flights(self, query_params: dict) -> dict:
        params = {**query_params, "api_key": self.api_key}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "best_flights": data.get("best_flights", []),
                "other_flights": data.get("other_flights", [])
            }
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy dữ liệu chuyến bay: {e}")
            return {"best_flights": [], "other_flights": []}

    def fetch_hotels(self, query_params: dict, duration_days: int) -> list:
        params = {**query_params, "api_key": self.api_key}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("properties", [])
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy dữ liệu khách sạn: {e}")
            return []

    def fetch_maps_places(self, query_params: dict, duration_days: int) -> list:
        target_pages = min(3, max(1, math.ceil(duration_days / 3.5)))
        return self._fetch_paginated_data(query_params, target_pages, result_key="local_results")

    def _fetch_paginated_data(self, query_params: dict, target_pages: int, result_key: str) -> list:
        all_results = []
        
        for page in range(target_pages):
            start_offset = page * 20
            params = {**query_params, "api_key": self.api_key, "start": start_offset}
            
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                items = data.get(result_key, [])
                if not items:
                    break
                    
                all_results.extend(items)
                
                pagination = data.get("serpapi_pagination", {})
                if "next" not in pagination:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Lỗi khi gọi SerpApi ở trang {page + 1}: {e}")
                break
                
        return all_results