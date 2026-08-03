from __future__ import annotations

import inspect
import logging
from typing import Any, Callable

from langgraph.graph import END, START, StateGraph

from app.agents.nodes.activity import activity_finder_node
from app.agents.nodes.cluster import cluster_agent_node
from app.agents.nodes.extractor import intent_extractor_node
from app.agents.nodes.flight import flight_agent_node
from app.agents.nodes.food import food_finder_node
from app.agents.nodes.hotel import hotel_finder_node
from app.agents.nodes.optimizer import optimizer_agent
from app.agents.nodes.synthesizer import final_synthesizer_node
from app.agents.state import AgentState
from app.schemas.response import TravelPlanResponse

logger = logging.getLogger("trip_planner")
logger.setLevel(logging.INFO)

if not logger.handlers:
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    if uvicorn_error_logger.handlers:
        logger.handlers = uvicorn_error_logger.handlers
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(ch)

logger.propagate = True

def _log_state_update(key: str, val: Any) -> None:
    """Single implementation of state-diff logging shared by sync and async nodes."""
    if isinstance(val, list):
        logger.info("State updated [%s]: list with %d items", key, len(val))
        if val and isinstance(val[0], dict) and "name" in val[0]:
            sample_names = [item.get("name", "N/A") for item in val[:3]]
            logger.info("Sample data for %s: %s", key, sample_names)
    elif isinstance(val, dict):
        logger.info("State updated [%s]: dict with keys -> %s", key, list(val.keys()))
    else:
        logger.info("State updated [%s]: %s", key, str(val)[:100])

def log_node_execution(node_name: str, node_func: Callable) -> Callable:
    """Wrap a graph node with enter/exit logging.

    Handles both sync and async node functions through a single async wrapper;
    LangGraph awaits the wrapper, which dispatches to the underlying function.
    """
    async def wrapper(state: AgentState) -> dict:
        logger.info("Entering node: %s", node_name)
        try:
            if inspect.iscoroutinefunction(node_func):
                result = await node_func(state)
            else:
                result = node_func(state)

            logger.info("Successfully executed node: %s", node_name)
            if isinstance(result, dict):
                for key, val in result.items():
                    _log_state_update(key, val)

            return result
        except Exception as e:
            logger.error("Error executing node %s: %s", node_name, e)
            raise e

    return wrapper


def create_travel_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_extractor", log_node_execution("intent_extractor", intent_extractor_node))
    workflow.add_node("flight_agent", log_node_execution("flight_agent", flight_agent_node))
    workflow.add_node("hotel_agent", log_node_execution("hotel_agent", hotel_finder_node))
    workflow.add_node("activity_agent", log_node_execution("activity_agent", activity_finder_node))
    workflow.add_node("cluster_agent", log_node_execution("cluster_agent", cluster_agent_node))
    workflow.add_node("food_agent", log_node_execution("food_agent", food_finder_node))
    workflow.add_node("optimizer", log_node_execution("optimizer", optimizer_agent))
    workflow.add_node("synthesizer", log_node_execution("synthesizer", final_synthesizer_node))

    workflow.add_edge(START, "intent_extractor")

    workflow.add_edge("intent_extractor", "flight_agent")
    workflow.add_edge("intent_extractor", "hotel_agent")
    workflow.add_edge("intent_extractor", "activity_agent")

    workflow.add_edge("activity_agent", "cluster_agent")
    workflow.add_edge("cluster_agent", "food_agent")

    workflow.add_edge("flight_agent", "optimizer")
    workflow.add_edge("hotel_agent", "optimizer")
    workflow.add_edge("food_agent", "optimizer")

    workflow.add_edge("optimizer", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


travel_graph = create_travel_graph()


async def run_trip_planner(request: Any) -> dict:
    logger.info("Initializing trip planning request execution.")
    req_dict = request.model_dump(mode='json') if hasattr(request, "model_dump") else dict(request)

    min_budget = float(req_dict.get("min_budget", 0) or 0)
    max_budget = float(req_dict.get("max_budget", 0) or 0)

    req_dict["min_budget"] = min_budget
    req_dict["max_budget"] = max_budget

    initial_state = {
        "user_intent": req_dict,
        "flight_candidates": [],
        "hotel_candidates": [],
        "food_candidates": [],
        "activity_candidates": [],
        "itinerary_options": [],
        "final_itinerary_markdown": "",
        "map_routes": [],
        "status": "PROCESSING",
        "messages": []
    }

    try:
        final_state = await travel_graph.ainvoke(initial_state)
    except Exception as e:
        logger.exception("LangGraph workflow execution failed.")
        raise e

    status = final_state.get("status", "SUCCESS")

    return TravelPlanResponse(
        status=status,
        message="Trip planning completed successfully.",
        user_intent=final_state.get("user_intent", {}),
        itinerary_options=final_state.get("itinerary_options", []),
        markdown_itinerary=final_state.get("final_itinerary_markdown", ""),
        map_routes=final_state.get("map_routes", []),
        candidates={
            "flights": final_state.get("flight_candidates", []),
            "hotels": final_state.get("hotel_candidates", []),
            "foods": final_state.get("food_candidates", []),
            "activities": final_state.get("activity_candidates", [])
        },
        agent_messages=final_state.get("messages", [])
    ).model_dump(mode='json')
