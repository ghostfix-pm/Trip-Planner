from typing import Any, Dict, List, Tuple


def build_mapbox_routes(
    selected_hotel: Dict[str, Any],
    daily_schedule: List[Dict[str, Any]],
    default_coords: Tuple[float, float] = (38.8951, -77.0364)
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    map_routes = []

    hotel_lat = float(selected_hotel.get("latitude") or default_coords[0])
    hotel_lng = float(selected_hotel.get("longitude") or default_coords[1])

    hotel_point = {
        "id": selected_hotel.get("fsq_place_id", "hotel_base"),
        "name": selected_hotel.get("name", "Khách sạn trung tâm"),
        "type": "hotel",
        "day": 0,
        "order": 0,
        "latitude": hotel_lat,
        "longitude": hotel_lng,
        "address": selected_hotel.get("address", "")
    }

    for item in daily_schedule:
        day_num = item.get("day", 1)
        places = item.get("items", [])
        waypoints = [hotel_point.copy()]

        for idx, p in enumerate(places):
            waypoints.append({
                "id": p.get("fsq_place_id", f"p_{day_num}_{idx}"),
                "name": p.get("name", "Điểm ghé thăm"),
                "type": p.get("type", "activity"),
                "day": day_num,
                "order": len(waypoints),
                "latitude": float(p.get("latitude") or hotel_lat),
                "longitude": float(p.get("longitude") or hotel_lng),
                "address": p.get("address", "")
            })

        end_h = hotel_point.copy()
        end_h["order"] = len(waypoints)
        waypoints.append(end_h)

        map_routes.append({"day": day_num, "waypoints": waypoints})

    return map_routes, hotel_point


def is_place_in_target_country(place: Dict[str, Any], target_country: str) -> bool:
    """True when a place's country matches (or overlaps) the requested destination country.

    Used by both the activity and food agents to filter out results SerpApi
    returns from neighbouring countries for searches near a border.
    """
    place_country = str(place.get("country") or "").strip().lower()
    target = str(target_country or "").strip().lower()
    if not place_country or not target:
        return True
    return place_country in target or target in place_country


def clean_and_deduplicate_candidates(
    selected_acts: List[Dict[str, Any]],
    selected_foods: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    seen_ids = set()
    unique_acts = []
    unique_foods = []

    for act in selected_acts:
        pid = act.get("fsq_place_id") or act.get("name")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            act["type"] = "activity"
            unique_acts.append(act)

    for food in selected_foods:
        pid = food.get("fsq_place_id") or food.get("name")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            food["type"] = "food"
            unique_foods.append(food)

    interleaved_items = []
    max_len = max(len(unique_acts), len(unique_foods))

    for i in range(max_len):
        if i < len(unique_acts):
            interleaved_items.append(unique_acts[i])
        if i < len(unique_foods):
            interleaved_items.append(unique_foods[i])

    return interleaved_items
