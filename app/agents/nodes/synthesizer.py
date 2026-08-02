from __future__ import annotations
import logging
import math
import json
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.core.llm import get_llm
from app.agents.nodes.helpers import build_mapbox_routes

logger = logging.getLogger("trip_planner")

def _parse_raw_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}

def _normalize_hotel(raw_hotel: Any) -> Dict[str, Any]:
    hotel = _parse_raw_json(raw_hotel)
    gps = hotel.get("gps_coordinates", {}) if isinstance(hotel.get("gps_coordinates"), dict) else {}
    latitude = hotel.get("latitude", gps.get("latitude"))
    longitude = hotel.get("longitude", gps.get("longitude"))
    return {
        "name": hotel.get("name", "Khách sạn trung tâm"),
        "address": hotel.get("address", ""),
        "latitude": latitude,
        "longitude": longitude,
        "fsq_place_id": hotel.get("fsq_place_id")
    }

def _normalize_place(raw_place: Any, fallback_type: str) -> Dict[str, Any]:
    place = _parse_raw_json(raw_place)
    gps = place.get("gps_coordinates", {}) if isinstance(place.get("gps_coordinates"), dict) else {}
    latitude = place.get("latitude", gps.get("latitude"))
    longitude = place.get("longitude", gps.get("longitude"))
    name = place.get("name", place.get("title", "Điểm ghé thăm"))
    return {
        "name": name,
        "title": place.get("title", name),
        "type": place.get("type", fallback_type),
        "description": place.get("description"),
        "rating": place.get("rating"),
        "reviews": place.get("reviews"),
        "price": place.get("price", place.get("price_level")),
        "hours": place.get("hours", place.get("operating_hours")),
        "latitude": latitude,
        "longitude": longitude,
        "address": place.get("address", ""),
        "fsq_place_id": place.get("fsq_place_id")
    }

def _resolve_primary_option(itinerary_options: Any) -> Dict[str, Any]:
    if isinstance(itinerary_options, dict):
        return itinerary_options
    if not isinstance(itinerary_options, list) or not itinerary_options:
        return {}

    first = itinerary_options[0]
    if isinstance(first, dict):
        return first
    if isinstance(first, list) and first and isinstance(first[0], dict):
        return first[0]
    return {}

async def final_synthesizer_node(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    opt_data = _resolve_primary_option(state.get("itinerary_options"))
    status = state.get("status", "SUCCESS")

    if status == "WAITING":
        return {"messages": ["Skipping this step as the system is waiting for data."]}

    destination = user_intent.get("destination", "Destination")
    duration_days = int(user_intent.get("duration_days", 1))
    min_budget = user_intent.get("min_budget", 0.0)
    
    try:
        max_budget = float(user_intent.get("max_budget", 0.0))
    except ValueError:
        max_budget = 0.0

    if status == "NO_MATCH" or not opt_data:
        fallback_msg = f"""# NOTICE: UNABLE TO OPTIMIZE ITINERARY

Unfortunately, the system AI could not find any itinerary combination that fully satisfies your strict criteria at **{destination}**.

### 🔍 ANALYSIS OF CAUSES (EXPERT AI INSIGHTS):
1. **Budget Limit Conflict:** Your maximum budget (${max_budget:,.2f} USD) is currently too low compared to the minimum actual market costs (including flights, hotels, transportation, and dining for {duration_days} days).
2. **Over-constrained Tags Conflict:** You may have selected too many simultaneous criteria for activities/dining. Within a geographic cluster's space, the system could not find enough destinations meeting all these tags.
3. **Data Availability Shortage:** Flights or hotels matching your required quality may be fully booked or unavailable during this timeframe.
4. **Travel Pace Conflict:** Your desired number of destinations is too high, but travel time between clusters is too far; the algorithm must reject this to ensure your actual comfort and experience.

### 💡 PROPOSED SOLUTIONS:
- **Relax Budget:** Try increasing your budget by 20-30% or accepting lower lodging standards (e.g., from 5-star down to 3-4 star).
- **Refine Criteria:** Remove some non-mandatory auxiliary amenity tags.
- **Adjust Itinerary:** Modify the number of travel days or choose a more relaxed travel pace.
"""
        return {
            "final_itinerary_markdown": fallback_msg,
            "map_routes": [],
            "messages": ["Detected budget mismatch or data noise error. Detailed error notification generated."]
        }

    selected_hotel = _normalize_hotel(opt_data.get("selected_hotel", {}))
    selected_flight = opt_data.get("selected_flight", {})
    summary_cost = opt_data.get("summary_cost", {})
    
    raw_acts = [_normalize_place(item, "activity") for item in opt_data.get("selected_activities", [])]
    raw_foods = [_normalize_place(item, "food") for item in opt_data.get("selected_foods", [])]

    for item in raw_acts + raw_foods:
        if "title" in item and "name" not in item:
            item["name"] = item["title"]
            
    daily_schedule_data = []
    cluster_text_for_llm = ""
    google_maps_links = []
    
    hotel_lat = selected_hotel.get('latitude', 0)
    hotel_lng = selected_hotel.get('longitude', 0)
    origin_point = f"{hotel_lat},{hotel_lng}"

    acts_per_day = math.ceil(len(raw_acts) / duration_days) if duration_days > 0 else 1
    foods_per_day = math.ceil(len(raw_foods) / duration_days) if duration_days > 0 else 1
    
    for d in range(duration_days):
        day_num = d + 1
        
        start_act = d * acts_per_day
        end_act = start_act + acts_per_day if d < duration_days - 1 else len(raw_acts)
        day_acts = raw_acts[start_act:end_act]

        start_food = d * foods_per_day
        end_food = start_food + foods_per_day if d < duration_days - 1 else len(raw_foods)
        day_foods = raw_foods[start_food:end_food]
        
        day_items = day_acts + day_foods
        
        daily_schedule_data.append({
            "day": day_num,
            "items": day_items
        })
        
        llm_acts = [{"name": a.get("name"), "type": a.get("type"), "description": a.get("description"), "rating": a.get("rating"), "reviews": a.get("reviews"), "price": a.get("price", a.get("price_level")), "hours": a.get("hours", a.get("operating_hours"))} for a in day_acts]
        llm_foods = [{"name": f.get("name"), "type": f.get("type"), "description": f.get("description"), "rating": f.get("rating"), "reviews": f.get("reviews"), "price": f.get("price", f.get("price_level")), "hours": f.get("hours", f.get("operating_hours"))} for f in day_foods]
        
        cluster_text_for_llm += f"\n\n### DAY {day_num} (Cluster Area {day_num})\n"
        cluster_text_for_llm += "**Activities List (JSON Details):**\n"
        cluster_text_for_llm += json.dumps(llm_acts, ensure_ascii=False, indent=2) + "\n"
        cluster_text_for_llm += "**Dining List (JSON Details):**\n"
        cluster_text_for_llm += json.dumps(llm_foods, ensure_ascii=False, indent=2) + "\n"

        waypoints = "|".join([f"{item.get('latitude')},{item.get('longitude')}" for item in day_items if item.get('latitude') and item.get('longitude')])
        if waypoints:
            gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin_point}&destination={origin_point}&waypoints={waypoints}&travelmode=driving"
            google_maps_links.append(f"📍 **[Google Maps Route for Day {day_num}]({gmaps_url})**")

    gmaps_markdown = "\n".join(google_maps_links)
    map_routes, hotel_point = build_mapbox_routes(selected_hotel, daily_schedule_data)

    prompt = f"""
    You are an expert Senior Travel Planner and local guide. Transform the location cluster data below into a detailed **TIMELINE Itinerary** in Markdown (Vietnamese).

    --- TRIP INFORMATION ---
    - Destination: {destination} ({duration_days} days)
    - Required Budget: ${min_budget:,.2f} - ${max_budget:,.2f} USD
    - Flight: Airline {selected_flight.get('airline', 'N/A')}
    - Hotel: {selected_hotel.get('name')} (Address: {selected_hotel.get('address')})
    
    --- DAILY GOOGLE MAPS LINKS LIST ---
    {gmaps_markdown}

    --- CLUSTERED LOCATION DATA (JSON BY DAY) ---
    {cluster_text_for_llm}

    --- ACTUAL COST BREAKDOWN ---
    - Flights: ${summary_cost.get('flight_cost', 0):,.2f} USD
    - Hotel: ${summary_cost.get('hotel_cost', 0):,.2f} USD
    - Activities: ${summary_cost.get('activity_cost', 0):,.2f} USD
    - Dining (estimated): ${summary_cost.get('estimated_food_cost_min', 0):,.2f} - ${summary_cost.get('estimated_food_cost_max', 0):,.2f} USD
    - Transport (Grab/Taxi): ${summary_cost.get('estimated_transport_cost', 0):,.2f} USD
    => **TOTAL: ${summary_cost.get('total_cost_min', 0):,.2f} - ${summary_cost.get('total_cost_max', 0):,.2f} USD**

    --- MANDATORY TIMELINE RULES (STRICT RULES) ---
    1. **Flexible & Realistic Time Allocation**: 
    - DO NOT assign rigid 30-minute intervals between points. Base it on realistic travel behavior (e.g., museums take 2-3 hours, sightseeing takes 1 hour, relaxed dinners take 1.5-2 hours, walking takes 45 minutes).
    - Automatically estimate reasonable travel times between points based on urban logic.
    - Mornings start from the hotel ({selected_hotel.get('name')}), evenings end by returning to the hotel.
    - Pay special attention to the "hours" field in the JSON strings to avoid scheduling sightseeing or dining when a location is closed.
    2. **Descriptions & Introductions (Guide Persona)**:
    - For EVERY location in the timeline, write 1-2 concise, engaging introductory sentences based on fields provided in the JSON file (rating, reviews, type, description...).
    3. **Markdown Layout Presentation**:
    - Place the ```mapbox-embed``` tag right below the main title.
    - Insert the "Google Maps Links List" right below the mapbox map.
    - Section ✈️ **Accommodation & Transportation Info**.
    - Section 📅 **Detailed Itinerary Timeline (Hour by Hour & With Descriptions)**.
    - Section 💰 **Budget Summary Table ($ USD)**.
    """

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        markdown_output = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error("Error invoking LLM Synthesizer: %s", e)
        markdown_output = "# LLM initialization error. Please try again!"

    return {
        "final_itinerary_markdown": markdown_output,
        "map_routes": map_routes,
        "messages": ["Successfully synthesized flexible timeline based on detailed cluster JSON data."]
    }

synthesizer_node = final_synthesizer_node