import logging
from app.agents.state import AgentState
from app.schemas.request import TravelRequest
from app.services.serpapi_service import SerpApiQueryBuilder, SerpApiClient
from app.services.db_service import db_service
from app.services.cache_service import cache_service # <-- IMPORT MỚI
from app.utils.serpapi_parser import SerpApiParser
from app.db.database import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger("trip_planner")
api_client = SerpApiClient(api_key=settings.SERPAPI_KEY)

async def hotel_finder_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    request_data = TravelRequest(**user_intent)
    duration_days = user_intent.get("duration_days", 1)
    
    query = SerpApiQueryBuilder.build_hotel_query(request_data)
    
    async with AsyncSessionLocal() as session:
        # Gọi cache_service với namespace "serpapi_hotel"
        cached_raw_data = await cache_service.get(session, "serpapi_hotel", query)
        
        if cached_raw_data:
            logger.info("⚡ [Hotel Node]: CACHE HIT!")
            raw_hotels = cached_raw_data
        else:
            logger.info("🐌 [Hotel Node]: CACHE MISS! Calling SerpApi...")
            raw_hotels = api_client.fetch_hotels(query, duration_days)
            parsed_hotels = SerpApiParser.parse_hotels_list(raw_hotels)
            
            if parsed_hotels:
                await db_service.upsert_hotels(session, parsed_hotels)
                # Ghi đè vào Cache
                await cache_service.set(session, "serpapi_hotel", query, raw_hotels, expire_minutes=262980) # 6 months

        final_hotels = SerpApiParser.parse_hotels_list(raw_hotels)

    return {
        "hotel_candidates": final_hotels,
        "messages": [f"[Hotel Agent]: Đã tìm thấy {len(final_hotels)} khách sạn."]
    }