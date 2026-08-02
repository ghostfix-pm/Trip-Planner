import re
from typing import Tuple

def extract_act_cost(item: dict, default_usd: float = 15.0) -> float:
    if "price" in item and isinstance(item["price"], (int, float)):
        return float(item["price"])
    price_level = item.get("price_level")
    if price_level:
        mapping = {1: 10.0, 2: 25.0, 3: 60.0, 4: 150.0}
        return mapping.get(int(price_level), default_usd)
    return default_usd

def extract_food_cost_range(item: dict) -> Tuple[float, float]:
    price_level = item.get("price_level")
    if price_level is not None:
        mapping = {1: (5.0, 15.0), 2: (15.0, 35.0), 3: (35.0, 75.0), 4: (75.0, 150.0)}
        return mapping.get(int(price_level), (10.0, 25.0))
    
    price_str = str(item.get("price", ""))
    if "-" in price_str or "–" in price_str:
        nums = re.findall(r'\d+', price_str)
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
    
    return 10.0, 25.0

def extract_hotel_cost(hotel: dict) -> float:
    if hotel.get("type") == "vacation_rental" or "prices" in hotel:
        prices = hotel.get("prices", [])
        if prices:
            rate = prices[0].get("rate_per_night", {})
            if "extracted_lowest" in rate:
                return float(rate["extracted_lowest"])
    
    hotel_class = hotel.get("extracted_hotel_class")
    if hotel_class:
        class_mapping = {1: 30.0, 2: 40.0, 3: 60.0, 4: 100.0, 5: 200.0}
        return class_mapping.get(int(hotel_class), 50.0)
    
    return 50.0