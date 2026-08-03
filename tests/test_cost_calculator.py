from app.utils.cost_calculator import (
    extract_act_cost,
    extract_food_cost_range,
    extract_hotel_cost,
)


def test_extract_act_cost_numeric_price():
    assert extract_act_cost({"price": 25}) == 25.0


def test_extract_act_cost_price_level_mapping():
    assert extract_act_cost({"price_level": 2}) == 25.0
    assert extract_act_cost({"price_level": 4}) == 150.0


def test_extract_act_cost_default():
    assert extract_act_cost({}) == 15.0
    assert extract_act_cost({"price_level": 99}) == 15.0


def test_extract_food_cost_range_by_level():
    assert extract_food_cost_range({"price_level": 1}) == (5.0, 15.0)
    assert extract_food_cost_range({"price_level": 3}) == (35.0, 75.0)


def test_extract_food_cost_range_from_price_string():
    assert extract_food_cost_range({"price": "$10 - $20"}) == (10.0, 20.0)


def test_extract_food_cost_range_default():
    assert extract_food_cost_range({}) == (10.0, 25.0)


def test_extract_hotel_cost_vacation_rental():
    hotel = {
        "type": "vacation_rental",
        "prices": [{"rate_per_night": {"extracted_lowest": 88.5}}],
    }
    assert extract_hotel_cost(hotel) == 88.5


def test_extract_hotel_cost_by_class():
    assert extract_hotel_cost({"extracted_hotel_class": 3}) == 60.0
    assert extract_hotel_cost({"extracted_hotel_class": 5}) == 200.0


def test_extract_hotel_cost_default():
    assert extract_hotel_cost({}) == 50.0
