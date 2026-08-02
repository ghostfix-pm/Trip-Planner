import asyncio
import logging
from collections import defaultdict
from app.agents.state import AgentState
from app.schemas.request import TravelRequest
from app.services.serpapi_service import SerpApiQueryBuilder, SerpApiClient
from app.services.db_service import db_service
from app.services.cache_service import cache_service
from app.utils.serpapi_parser import SerpApiParser
from app.db.database import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger("trip_planner")
api_client = SerpApiClient(api_key=settings.SERPAPI_KEY)

async def activity_finder_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    request_data = TravelRequest(**user_intent)
    duration_days = user_intent.get("duration_days", 1)
    
    all_queries_raw = SerpApiQueryBuilder.build_activity_queries(request_data)
    
    default_query_str = str(all_queries_raw[0]) if all_queries_raw else ""
    
    all_queries = []
    seen_queries = set()
    
    for q in all_queries_raw:
        q_hash = str(q)
        if q_hash not in seen_queries:
            seen_queries.add(q_hash)
            all_queries.append(q)
            
    place_map = {}
    place_sources = defaultdict(set)
    semaphore = asyncio.Semaphore(3)
    
    async def fetch_and_process(query):
        async with semaphore: 
            async with AsyncSessionLocal() as session:
                try:
                    cache_key = str(query)
                    cached_raw_data = await cache_service.get(session, "serpapi_activity", cache_key)
                    
                    if cached_raw_data:
                        logger.info(f"Cache hit for query {query.get('q')}")
                        return query, cached_raw_data
                    else:
                        logger.info(f"Cache miss for query {query.get('q')}. Calling SerpApi...")
                        raw_activities = await asyncio.to_thread(api_client.fetch_maps_places, query, duration_days)
                        
                        if raw_activities:
                            await cache_service.set(session, "serpapi_activity", cache_key, raw_activities, expire_minutes=262980)
                        
                        return query, raw_activities
                except Exception as e:
                    logger.error(f"Error processing query {query}: {e}")
                    return query, None

    tasks = [fetch_and_process(q) for q in all_queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    unique_places_to_db = {}
    
    for result in results:
        if isinstance(result, Exception) or not result:
            continue
            
        query, raw_data = result
        if not raw_data:
            continue
            
        destination_str = user_intent.get("destination", "").lower()
        target_country = destination_str.split(",")[-1].strip() if "," in destination_str else ""

        parsed = SerpApiParser.parse_destinations_list(raw_data)
        for place in parsed:
            place_id = place.get("place_id")
            place_country = str(place.get("country") or "").strip().lower()
            if place_id and place_country and target_country:
                if place_country not in target_country and target_country not in place_country:
                    logger.warning(f"Blocked {place.get('title')} due to country mismatch")
                    continue 
            
            if place_id:
                place["place_type"] = "activity"
                place_map[place_id] = place
                unique_places_to_db[place_id] = place
                place_sources[place_id].add(str(query))

    if unique_places_to_db:
        async with AsyncSessionLocal() as session:
            try:
                await db_service.upsert_destinations(session, list(unique_places_to_db.values()))
            except Exception as e:
                logger.error(f"Batch database insert failed: {e}")

    for pid, place in place_map.items():
        try:
            rating = float(place.get("rating") or 0.0)
        except (ValueError, TypeError):
            rating = 0.0
            
        try:
            reviews = int(place.get("reviews") or 0)
        except (ValueError, TypeError):
            reviews = 0
            
        C = 4.0 
        m = 50 
        
        if reviews > 0:
            place["base_score"] = (rating * reviews + C * m) / (reviews + m)
        else:
            place["base_score"] = 0.0

    final_activities = []
    pool = list(place_map.values())
    
    query_usage_count = defaultdict(int)
    type_usage_count = defaultdict(int)

    while pool:
        best_score = -999.0
        best_idx = -1
        
        for idx, place in enumerate(pool):
            pid = place.get("place_id")
            sources = place_sources[pid]
            
            current_score = place["base_score"]
            
            if default_query_str in sources:
                current_score += 0.5 
                
            user_queries = sources - {default_query_str}
            for q in user_queries:
                times_used = query_usage_count[q]
                bonus = 2.0 / (times_used + 1)
                current_score += bonus
                
            place_type = str(place.get("type", "")).strip()
            if place_type:
                times_type_used = type_usage_count[place_type]
                penalty = times_type_used * 0.15 
                current_score -= penalty
                
            if current_score > best_score:
                best_score = current_score
                best_idx = idx
                
        selected_place = pool.pop(best_idx)
        final_activities.append(selected_place)
        
        pid = selected_place.get("place_id")
        user_queries = place_sources[pid] - {default_query_str}
        for q in user_queries:
            query_usage_count[q] += 1
            
        place_type = str(selected_place.get("type", "")).strip()
        if place_type:
            type_usage_count[place_type] += 1

    return {
        "activity_candidates": final_activities,
        "messages": [f"Found {len(final_activities)} activity places."]
    }