from app.utils.serpapi_parser import SerpApiParser


def test_parse_hotel_maps_gps():
    raw = {
        "name": "Grand Hotel",
        "gps_coordinates": {"latitude": 10.77, "longitude": 106.69},
        "extracted_hotel_class": 4,
    }
    parsed = SerpApiParser.parse_hotel(raw)
    assert parsed["name"] == "Grand Hotel"
    assert parsed["latitude"] == 10.77
    assert parsed["longitude"] == 106.69
    assert parsed["extracted_hotel_class"] == 4
    assert parsed["raw_data"] == raw


def test_parse_hotel_missing_fields_safe():
    parsed = SerpApiParser.parse_hotel({})
    assert parsed["name"] == "Khách sạn chưa rõ tên"
    assert parsed["latitude"] is None
    assert parsed["raw_data"] == {}


def test_parse_destination_operating_hours():
    raw = {
        "place_id": "abc123",
        "title": "War Remnants Museum",
        "operating_hours": {"monday": "07:30-18:00"},
    }
    parsed = SerpApiParser.parse_destination(raw)
    assert parsed["place_id"] == "abc123"
    assert parsed["operating_hours_monday"] == "07:30-18:00"
    assert parsed["operating_hours_tuesday"] is None


def test_parse_hotels_list():
    parsed = SerpApiParser.parse_hotels_list([{"name": "A"}, {"name": "B"}])
    assert len(parsed) == 2
    assert parsed[0]["name"] == "A"


def test_parse_destinations_list_filters_missing_place_id():
    parsed = SerpApiParser.parse_destinations_list([
        {"place_id": "x1", "title": "Keep"},
        {"title": "Drop"},
    ])
    assert len(parsed) == 1
    assert parsed[0]["place_id"] == "x1"
