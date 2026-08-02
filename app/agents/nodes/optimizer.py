import logging
import json
from typing import List, Dict, Any, Tuple
from app.agents.state import AgentState
from app.services.mapbox_service import get_mapbox_matrix_distances, calculate_distance_km
from app.utils.cost_calculator import extract_act_cost, extract_food_cost_range, extract_hotel_cost
from app.utils.tsp_algorithm import solve_tsp_greedy

logger = logging.getLogger("trip_planner")
ESTIMATED_COST_PER_KM = 1.2
MAX_MATRIX_COORDS = 25
MAX_HOTEL_SHORTLIST = 3


def _parse_raw_data(raw_value: Any) -> Dict[str, Any]:
    if isinstance(raw_value, dict):
        return raw_value
    if isinstance(raw_value, str):
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _extract_raw_data_list(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_parse_raw_data(item.get("raw_data")) for item in items]


def _extract_flight_cost_per_traveler(flight: Dict[str, Any]) -> float:
    for key in ("price_per_person", "price"):
        value = flight.get(key)
        try:
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def _extract_flight_airline(flight: Dict[str, Any]) -> str:
    direct_airline = flight.get("airline")
    if isinstance(direct_airline, str) and direct_airline.strip():
        return direct_airline
    flights = flight.get("flights")
    if isinstance(flights, list) and flights:
        first_leg = flights[0]
        if isinstance(first_leg, dict):
            leg_airline = first_leg.get("airline")
            if isinstance(leg_airline, str) and leg_airline.strip():
                return leg_airline
    return "Chuyến bay"


def _build_selected_hotel_payload(hotel: Dict[str, Any]) -> Dict[str, Any]:
    raw_data = _parse_raw_data(hotel.get("raw_data"))
    gps = raw_data.get("gps_coordinates") if isinstance(raw_data.get("gps_coordinates"), dict) else {}
    if "name" not in raw_data and hotel.get("name"):
        raw_data["name"] = hotel.get("name")
    if "address" not in raw_data and hotel.get("address"):
        raw_data["address"] = hotel.get("address")
    if "latitude" not in raw_data and hotel.get("latitude") is not None:
        raw_data["latitude"] = hotel.get("latitude")
    if "longitude" not in raw_data and hotel.get("longitude") is not None:
        raw_data["longitude"] = hotel.get("longitude")
    if isinstance(gps, dict):
        if "latitude" not in raw_data and gps.get("latitude") is not None:
            raw_data["latitude"] = gps.get("latitude")
        if "longitude" not in raw_data and gps.get("longitude") is not None:
            raw_data["longitude"] = gps.get("longitude")
    return raw_data


def _has_valid_lat_lng(item: Dict[str, Any]) -> bool:
    return item.get("latitude") is not None and item.get("longitude") is not None


def _collect_cluster_points(cluster: Dict[str, Any]) -> List[Dict[str, Any]]:
    points: List[Dict[str, Any]] = []
    for activity in cluster.get("activities", []):
        if _has_valid_lat_lng(activity):
            points.append(activity)
    for food in cluster.get("foods", []):
        if _has_valid_lat_lng(food):
            points.append(food)
    return points


def _fallback_segment_distance(hotel: Dict[str, Any], points: List[Dict[str, Any]]) -> float:
    if not points:
        return 0.0

    h_lat = float(hotel["latitude"])
    h_lng = float(hotel["longitude"])
    matrix_size = len(points) + 1
    matrix = [[0.0 for _ in range(matrix_size)] for _ in range(matrix_size)]

    for i in range(matrix_size):
        for j in range(matrix_size):
            if i == j:
                continue

            if i == 0:
                src_lat, src_lng = h_lat, h_lng
            else:
                src = points[i - 1]
                src_lat, src_lng = float(src["latitude"]), float(src["longitude"])

            if j == 0:
                dst_lat, dst_lng = h_lat, h_lng
            else:
                dst = points[j - 1]
                dst_lat, dst_lng = float(dst["latitude"]), float(dst["longitude"])

            matrix[i][j] = calculate_distance_km(src_lat, src_lng, dst_lat, dst_lng)

    return solve_tsp_greedy(matrix)


def _tsp_distance_from_matrix(
    matrix: List[List[float]],
    hotel_index: int,
    point_indices: List[int]
) -> float:
    if not point_indices:
        return 0.0

    route_indices = [hotel_index] + point_indices
    sub_matrix = []
    for row_idx in route_indices:
        row = []
        for col_idx in route_indices:
            row.append(matrix[row_idx][col_idx])
        sub_matrix.append(row)
    return solve_tsp_greedy(sub_matrix)


def _build_cluster_segments(clusters: List[Dict[str, Any]], point_capacity: int) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    for cluster_idx, cluster in enumerate(clusters):
        points = _collect_cluster_points(cluster)
        if not points:
            continue

        if len(points) <= point_capacity:
            segments.append({"cluster_idx": cluster_idx, "points": points})
            continue

        logger.warning(
            "Cluster %s has %s points exceeding the limit %s, splitting segment to call matrix.",
            cluster_idx + 1,
            len(points),
            point_capacity
        )
        start = 0
        while start < len(points):
            segments.append({
                "cluster_idx": cluster_idx,
                "points": points[start:start + point_capacity]
            })
            start += point_capacity
    return segments


def _pack_segments_for_batches(
    segments: List[Dict[str, Any]],
    point_capacity: int
) -> List[List[Dict[str, Any]]]:
    batches: List[List[Dict[str, Any]]] = []
    current_batch: List[Dict[str, Any]] = []
    current_points = 0

    for segment in segments:
        seg_size = len(segment["points"])
        if current_batch and (current_points + seg_size > point_capacity):
            batches.append(current_batch)
            current_batch = []
            current_points = 0

        current_batch.append(segment)
        current_points += seg_size

    if current_batch:
        batches.append(current_batch)

    return batches


async def optimizer_agent(state: AgentState) -> dict:
    user_intent = state.get("user_intent", {})
    max_budget = float(user_intent.get("max_budget", 999999.0))
    duration_days = int(user_intent.get("duration_days", 1))
    num_adults = int(user_intent.get("num_adults", 1))
    num_children = int(user_intent.get("num_children", 0))
    total_people = num_adults + (num_children * 0.5)
    paid_travelers = num_adults + num_children

    flight_candidates = state.get("flight_candidates", [])
    hotel_candidates = state.get("hotel_candidates", [])
    clusters = state.get("activity_clusters", [])

    if not flight_candidates or not hotel_candidates or not clusters:
        return {"status": "WAITING"}

    valid_hotels = [hotel for hotel in hotel_candidates if _has_valid_lat_lng(hotel)]
    if not valid_hotels:
        return {
            "optimized_itinerary": {},
            "itinerary_options": [],
            "status": "NO_MATCH",
            "messages": ["No hotels with valid coordinates found for route optimization."]
        }

    selected_activities: List[Dict[str, Any]] = []
    selected_foods: List[Dict[str, Any]] = []
    for cluster in clusters:
        selected_activities.extend(cluster.get("activities", []))
        selected_foods.extend(cluster.get("foods", []))

    rough_hotel_scores: List[Tuple[float, Dict[str, Any]]] = []
    for hotel in valid_hotels:
        h_lat = float(hotel["latitude"])
        h_lng = float(hotel["longitude"])
        rough_transport = 0.0
        for cluster in clusters:
            c_lat = cluster.get("center_lat")
            c_lng = cluster.get("center_lng")
            if c_lat is None or c_lng is None:
                continue
            rough_transport += calculate_distance_km(h_lat, h_lng, float(c_lat), float(c_lng)) * 2
        rough_hotel_scores.append((rough_transport, hotel))

    rough_hotel_scores.sort(key=lambda x: x[0])
    shortlisted_hotels = [hotel for _, hotel in rough_hotel_scores[:MAX_HOTEL_SHORTLIST]]
    if not shortlisted_hotels:
        return {
            "optimized_itinerary": {},
            "itinerary_options": [],
            "status": "NO_MATCH",
            "messages": ["Failed to create hotel shortlist."]
        }

    point_capacity = MAX_MATRIX_COORDS - len(shortlisted_hotels)
    if point_capacity <= 0:
        return {
            "optimized_itinerary": {},
            "itinerary_options": [],
            "status": "NO_MATCH",
            "messages": ["Insufficient matrix slots after subtracting shortlisted hotels."]
        }

    segments = _build_cluster_segments(clusters, point_capacity)
    batches = _pack_segments_for_batches(segments, point_capacity)
    hotel_transport_km = [0.0 for _ in shortlisted_hotels]

    for batch in batches:
        coords = [f"{float(h['longitude'])},{float(h['latitude'])}" for h in shortlisted_hotels]
        segment_indices: List[List[int]] = []
        segment_points: List[List[Dict[str, Any]]] = []

        for segment in batch:
            indices = []
            points = segment["points"]
            for point in points:
                coords.append(f"{float(point['longitude'])},{float(point['latitude'])}")
                indices.append(len(coords) - 1)
            segment_indices.append(indices)
            segment_points.append(points)

        matrix = await get_mapbox_matrix_distances(coords)
        matrix_ready = bool(matrix) and len(matrix) == len(coords) and all(len(row) == len(coords) for row in matrix)

        for hotel_idx, hotel in enumerate(shortlisted_hotels):
            for seg_idx, point_indices in enumerate(segment_indices):
                if not point_indices:
                    continue

                if matrix_ready:
                    segment_dist = _tsp_distance_from_matrix(matrix, hotel_idx, point_indices)
                else:
                    segment_dist = _fallback_segment_distance(hotel, segment_points[seg_idx])

                hotel_transport_km[hotel_idx] += segment_dist

    best_hotel_idx = min(range(len(shortlisted_hotels)), key=lambda idx: hotel_transport_km[idx])
    best_hotel = shortlisted_hotels[best_hotel_idx]
    best_transport_km = hotel_transport_km[best_hotel_idx]

    hotel_cost = extract_hotel_cost(best_hotel) * duration_days
    activity_cost = sum(extract_act_cost(item, 20.0) for item in selected_activities) * total_people
    food_cost_min = 0.0
    food_cost_max = 0.0
    for item in selected_foods:
        f_min, f_max = extract_food_cost_range(item)
        food_cost_min += f_min * total_people
        food_cost_max += f_max * total_people
    transport_cost = best_transport_km * ESTIMATED_COST_PER_KM

    best_flight_choice = None
    best_flight_airline = "Chuyến bay"
    best_total_min = -1.0
    best_total_max = 0.0
    best_flight_cost = 0.0
    for flight in flight_candidates:
        flight_cost = _extract_flight_cost_per_traveler(flight) * paid_travelers
        total_min = flight_cost + hotel_cost + activity_cost + food_cost_min + transport_cost
        total_max = flight_cost + hotel_cost + activity_cost + food_cost_max + transport_cost
        if total_min > max_budget:
            continue
        if total_min > best_total_min:
            best_total_min = total_min
            best_total_max = total_max
            best_flight_cost = flight_cost
            best_flight_choice = flight
            best_flight_airline = _extract_flight_airline(flight)

    if not best_flight_choice:
        return {
            "optimized_itinerary": {},
            "itinerary_options": [],
            "status": "NO_MATCH",
            "messages": ["No flights found that keep the total cost within the maximum budget."]
        }

    optimized_option = {
        "option_name": f"Lộ trình Tối ưu: {best_flight_airline} & {best_hotel.get('name', '')[:15]}",
        "selected_flight": best_flight_choice,
        "selected_hotel": _build_selected_hotel_payload(best_hotel),
        "selected_activities": _extract_raw_data_list(selected_activities),
        "selected_foods": _extract_raw_data_list(selected_foods),
        "summary_cost": {
            "flight_cost": round(best_flight_cost, 2),
            "hotel_cost": round(hotel_cost, 2),
            "activity_cost": round(activity_cost, 2),
            "estimated_food_cost_min": round(food_cost_min, 2),
            "estimated_food_cost_max": round(food_cost_max, 2),
            "estimated_transport_cost": round(transport_cost, 2),
            "total_cost_min": round(best_total_min, 2),
            "total_cost_max": round(best_total_max, 2)
        },
        "total_travel_distance_km": round(best_transport_km, 2)
    }

    return {
        "status": "SUCCESS",
        "itinerary_options": [optimized_option],
        "messages": [
            f"Selected hotel with lowest transport cost among shortlist of {len(shortlisted_hotels)} and flight closest to max budget without exceeding it."
        ]
    }