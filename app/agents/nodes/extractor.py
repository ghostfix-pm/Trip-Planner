import logging
from app.agents.state import AgentState
from app.schemas.request import TravelRequest

logger = logging.getLogger("trip_planner")

def intent_extractor_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    request_data = TravelRequest(**user_intent)
    duration_days = (request_data.return_date - request_data.departure_date).days
    duration_days = max(1, duration_days) 
    user_intent["duration_days"] = duration_days

    logger.info("Processed intent successfully. Trip duration: %d days", duration_days)

    return {
        "user_intent": user_intent, 
        "messages": [f"Intent extractor received request. Trip duration is {duration_days} days."]
    }