from datetime import date, timedelta

from app.agents.nodes.flight import calculate_flight_cache_ttl


def test_flight_today_short_ttl():
    ttl = calculate_flight_cache_ttl(date.today())
    assert ttl == 5


def test_flight_tomorrow_medium_ttl():
    ttl = calculate_flight_cache_ttl(date.today() + timedelta(days=1))
    assert ttl == 60


def test_flight_in_three_days():
    ttl = calculate_flight_cache_ttl(date.today() + timedelta(days=3))
    assert ttl == 360


def test_flight_in_ten_days_long_ttl():
    ttl = calculate_flight_cache_ttl(date.today() + timedelta(days=10))
    assert ttl == 1440


def test_flight_past_date_short_ttl():
    ttl = calculate_flight_cache_ttl(date.today() - timedelta(days=3))
    assert ttl == 5
