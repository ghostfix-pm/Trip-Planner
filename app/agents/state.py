# app/agents/state.py
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

def update_value(old_val: Any, new_val: Any) -> Any:
    if new_val is not None and new_val != [] and new_val != {}:
        return new_val
    return old_val

class AgentState(TypedDict):
    user_intent: Dict[str, Any]
    flight_candidates: Annotated[List[Dict[str, Any]], update_value]
    hotel_candidates: Annotated[List[Dict[str, Any]], update_value]
    food_candidates: Annotated[List[Dict[str, Any]], update_value]
    activity_candidates: Annotated[List[Dict[str, Any]], update_value]

    activity_clusters: Annotated[List[Dict[str, Any]], update_value]

    itinerary_options: Annotated[List[Dict[str, Any]], update_value]
    final_itinerary_markdown: Annotated[str, update_value]
    
    map_routes: Annotated[List[Dict[str, Any]], update_value]
    messages: Annotated[List[str], operator.add]