import logging
from datetime import datetime
from app.agents.state import AgentState
from app.schemas.request import TravelRequest
from app.services.serpapi_service import SerpApiQueryBuilder, SerpApiClient
from app.services.cache_service import cache_service
from app.db.database import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger("trip_planner")
api_client = SerpApiClient(api_key=settings.SERPAPI_KEY)

def calculate_flight_cache_ttl(departure_date) -> int:
    today = datetime.now().date()
    days_until_flight = (departure_date - today).days

    if days_until_flight <= 0:
        return 5
    elif days_until_flight <= 2:
        return 60
    elif days_until_flight <= 7:
        return 60 * 6
    else:
        return 60 * 24

async def flight_agent_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    request_data = TravelRequest(**user_intent)
    
    query = SerpApiQueryBuilder.build_flight_query(request_data)
    
    logger.info("Searching flights from %s to %s...", request_data.origin, request_data.destination)
    
    cache_minutes = calculate_flight_cache_ttl(request_data.departure_date)
    logger.info("Flight cache TTL set to %d minutes.", cache_minutes)

    async with AsyncSessionLocal() as session:
        cached_data = await cache_service.get(session, "serpapi_flight", query)
        
        if cached_data:
            logger.info("Cache hit for flights. Retrieving cached data.")
            flights = cached_data
        else:
            logger.info("Cache miss for flights. Fetching from Google Flights API...")
            results = api_client.fetch_flights(query)
            
            flights = results.get("best_flights", []) + results.get("other_flights", [])
            
            if flights:
                await cache_service.set(
                    session=session, 
                    namespace="serpapi_flight", 
                    params=query, 
                    data=flights, 
                    expire_minutes=cache_minutes
                )
    
    return {
        "flight_candidates": flights,
        "messages": [f"Flight agent found {len(flights)} flights."]
    }