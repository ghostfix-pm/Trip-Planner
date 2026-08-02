import logging
import random
import re
import asyncio
from collections import defaultdict
from app.agents.state import AgentState
from app.schemas.request import TravelRequest
from app.services.serpapi_service import SerpApiQueryBuilder, SerpApiClient
from app.services.db_service import db_service
from app.utils.serpapi_parser import SerpApiParser
from app.db.database import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger("trip_planner")
api_client = SerpApiClient(api_key=settings.SERPAPI_KEY)

def parse_meal_hours(hours_str: str):
    if not hours_str or not isinstance(hours_str, str):
        return True, True, True
    h_str = hours_str.lower()
    if "24" in h_str:
        return True, True, True
    matches = re.findall(r'(\d{1,2})(?::\d{2})?\s*(am|pm)', h_str)
    if len(matches) >= 2:
        times = []
        for hr, period in matches:
            h = int(hr)
            if period == 'pm' and h != 12: h += 12
            elif period == 'am' and h == 12: h = 0
            times.append(h)
        start_h, end_h = times[0], times[-1]
        if end_h < start_h: end_h += 24
        return (start_h <= 9 and end_h >= 9), (start_h <= 13 and end_h >= 12), (start_h <= 19 and end_h >= 18)
    return True, True, True

async def food_finder_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    food_categories = user_intent.get("food_categories", [])
    clusters = state.get("activity_clusters", [])

    destination_str = user_intent.get("destination", "").lower()
    target_country = destination_str.split(",")[-1].strip() if "," in destination_str else ""
    
    all_foods_flat = []
    updated_clusters = []
    
    async with AsyncSessionLocal() as session:
        for cluster in clusters:
            lat = round(cluster["center_lat"], 3)
            lng = round(cluster["center_lng"], 3)
            
            db_restaurants = await db_service.get_cluster_restaurants(session, lat, lng)
            
            if db_restaurants:
                logger.info("Retrieved cluster (%f, %f) data from database.", lat, lng)
                final_foods = db_restaurants
            else:
                ll_param = f"@{lat},{lng},15z" 
                logger.info("Calling SerpApi to create a new cluster at coordinates %s...", ll_param)
                
                food_query_params = SerpApiQueryBuilder.build_food_query(ll_param)
                
                raw_foods = await asyncio.to_thread(api_client.fetch_maps_places, food_query_params, duration_days=1)
                parsed_foods = SerpApiParser.parse_destinations_list(raw_foods)

                valid_foods = []
                if parsed_foods:
                    for p in parsed_foods: 
                        place_id = p.get("place_id")
                        place_country = str(p.get("country") or "").strip().lower()
                        if place_id and place_country and target_country:
                            if place_country not in target_country and target_country not in place_country:
                                place_name = p.get('title') or p.get('name', 'Unknown')
                                logger.warning("Blocked restaurant '%s' due to country mismatch (%s != %s)", place_name, place_country, target_country)
                                continue
                                
                        p["place_type"] = "food"
                        valid_foods.append(p)
                        
                    if valid_foods:
                        await db_service.upsert_destinations(session, valid_foods)
                        place_ids = [p["place_id"] for p in valid_foods if p.get("place_id")]
                        await db_service.upsert_cluster(session, lat, lng, place_ids)
                    
                final_foods = valid_foods
            
            if final_foods:
                for f in final_foods:
                    try:
                        base_rating = float(f.get("rating") or 0.0)
                    except (ValueError, TypeError):
                        base_rating = 0.0
                        
                    try:
                        reviews = int(f.get("reviews") or 0)
                    except (ValueError, TypeError):
                        reviews = 0
                        
                    C = 4.0
                    m = 20
                    
                    if reviews > 0:
                        f["base_score"] = (base_rating * reviews + C * m) / (reviews + m)
                    else:
                        f["base_score"] = 0.0
                        
                    text_to_search = f"{f.get('name', '')} {f.get('type', '')} {f.get('description', '')}".lower()
                    matched_tags = [cat for cat in food_categories if cat.lower() in text_to_search]
                    f["matched_tags"] = matched_tags

                dynamic_sorted_foods = []
                pool = list(final_foods)
                
                tag_usage_count = defaultdict(int)
                type_usage_count = defaultdict(int)

                while pool:
                    best_score = -999.0
                    best_idx = -1
                    
                    for idx, f in enumerate(pool):
                        current_score = f["base_score"]
                        
                        for tag in f["matched_tags"]:
                            times_used = tag_usage_count[tag]
                            bonus = 1.0 / (times_used + 1)
                            current_score += bonus
                            
                        f_type = str(f.get("type", "")).strip()
                        if f_type:
                            times_type_used = type_usage_count[f_type]
                            penalty = times_type_used * 0.25
                            current_score -= penalty
                            
                        if current_score > best_score:
                            best_score = current_score
                            best_idx = idx
                            
                    selected_food = pool.pop(best_idx)
                    dynamic_sorted_foods.append(selected_food)
                    
                    for tag in selected_food["matched_tags"]:
                        tag_usage_count[tag] += 1
                        
                    f_type = str(selected_food.get("type", "")).strip()
                    if f_type:
                        type_usage_count[f_type] += 1
                        
                final_foods = dynamic_sorted_foods
            
            target_foods_count = random.randint(2, 3)
            selected_foods = []
            
            needs = ["lunch", "dinner"] if target_foods_count == 2 else ["breakfast", "lunch", "dinner"]
            filled = set()
            
            for f in final_foods:
                if len(selected_foods) == target_foods_count:
                    break
                    
                hours_str = str(f.get("hours") or f.get("operating_hours") or "")
                b, l, d = parse_meal_hours(hours_str)
                
                assigned = False
                if "breakfast" in needs and "breakfast" not in filled and b:
                    filled.add("breakfast")
                    selected_foods.append(f)
                    assigned = True
                elif not assigned and "lunch" in needs and "lunch" not in filled and l:
                    filled.add("lunch")
                    selected_foods.append(f)
                    assigned = True
                elif not assigned and "dinner" in needs and "dinner" not in filled and d:
                    filled.add("dinner")
                    selected_foods.append(f)
                    assigned = True
                    
            if len(selected_foods) < target_foods_count:
                for f in final_foods:
                    if len(selected_foods) == target_foods_count:
                        break
                    if f not in selected_foods:
                        selected_foods.append(f)
            
            cluster["foods"] = selected_foods
            updated_clusters.append(cluster)
            all_foods_flat.extend(selected_foods)

    unique_foods = list({f["place_id"]: f for f in all_foods_flat if f.get("place_id")}.values())

    return {
        "activity_clusters": updated_clusters,
        "food_candidates": unique_foods,
        "messages": [f"Food agent distributed {len(unique_foods)} quality restaurants across {len(clusters)} location clusters."]
    }