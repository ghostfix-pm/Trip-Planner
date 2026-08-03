from app.agents.nodes.helpers import (
    build_mapbox_routes,
    clean_and_deduplicate_candidates,
    is_place_in_target_country,
)


def test_build_mapbox_routes_basic():
    hotel = {"name": "Base Hotel", "latitude": 10.0, "longitude": 106.0, "fsq_place_id": "h1"}
    schedule = [
        {"day": 1, "items": [
            {"name": "Museum", "latitude": 10.1, "longitude": 106.1, "fsq_place_id": "p1"},
        ]},
    ]
    routes, hotel_point = build_mapbox_routes(hotel, schedule)
    assert len(routes) == 1
    day1 = routes[0]
    assert day1["day"] == 1
    # hotel start + 1 place + hotel end
    assert len(day1["waypoints"]) == 3
    assert day1["waypoints"][0]["type"] == "hotel"
    assert day1["waypoints"][1]["name"] == "Museum"
    assert day1["waypoints"][2]["type"] == "hotel"
    assert hotel_point["name"] == "Base Hotel"


def test_build_mapbox_routes_default_coords_fallback():
    hotel = {"name": "NoCoords"}
    routes, hotel_point = build_mapbox_routes(hotel, [{"day": 1, "items": []}])
    assert hotel_point["latitude"] == 38.8951
    assert hotel_point["longitude"] == -77.0364


def test_clean_and_deduplicate_interleaves():
    acts = [{"fsq_place_id": "a1", "name": "Act1"}]
    foods = [{"fsq_place_id": "f1", "name": "Food1"}, {"fsq_place_id": "f2", "name": "Food2"}]
    items = clean_and_deduplicate_candidates(acts, foods)
    assert [i["name"] for i in items] == ["Act1", "Food1", "Food2"]
    assert items[0]["type"] == "activity"
    assert items[1]["type"] == "food"


def test_clean_and_deduplicate_removes_dupes():
    acts = [{"fsq_place_id": "same", "name": "A"}, {"fsq_place_id": "same", "name": "A2"}]
    foods = [{"fsq_place_id": "same", "name": "A"}]
    items = clean_and_deduplicate_candidates(acts, foods)
    assert len(items) == 1


def test_is_place_in_target_country():
    assert is_place_in_target_country({"country": "Vietnam"}, "vietnam")
    assert not is_place_in_target_country({"country": "Cambodia"}, "vietnam")
    assert is_place_in_target_country({"country": "Vietnam"}, "")
    assert is_place_in_target_country({}, "vietnam")
    assert is_place_in_target_country({"country": ""}, "vietnam")
