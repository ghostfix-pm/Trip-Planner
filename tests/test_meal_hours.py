from app.agents.nodes.food import parse_meal_hours


def test_no_hours_returns_all_true():
    assert parse_meal_hours("") == (True, True, True)
    assert parse_meal_hours(None) == (True, True, True)


def test_24h_returns_all_true():
    assert parse_meal_hours("Open 24 hours") == (True, True, True)


def test_breakfast_hours():
    breakfast, lunch, dinner = parse_meal_hours("6:00 am - 10:00 am")
    assert breakfast is True
    assert lunch is False
    assert dinner is False


def test_lunch_hours():
    breakfast, lunch, dinner = parse_meal_hours("11:00 am - 2:00 pm")
    assert breakfast is False
    assert lunch is True
    assert dinner is False


def test_dinner_hours():
    breakfast, lunch, dinner = parse_meal_hours("5:00 pm - 10:00 pm")
    assert breakfast is False
    assert lunch is False
    assert dinner is True


def test_overnight_hours():
    breakfast, lunch, dinner = parse_meal_hours("5:00 pm - 2:00 am")
    assert dinner is True
