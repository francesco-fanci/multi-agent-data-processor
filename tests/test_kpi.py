from src.analytics.kpi import (
    calculate_speed,
    calculate_cycle_speed,
    calculate_production_speed
)


def test_speed_one_hour():

    speed = calculate_speed(
        100,
        "2026-02-01 10:00:00",
        "2026-02-01 11:00:00"
    )

    assert speed == 100


def test_speed_half_hour():

    speed = calculate_speed(
        100,
        "2026-02-01 10:00:00",
        "2026-02-01 10:30:00"
    )

    assert speed == 200


def test_speed_zero_elapsed_time():

    speed = calculate_speed(
        100,
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:00"
    )

    assert speed == 0.0


def test_speed_missing_timestamp():

    speed = calculate_speed(
        100,
        None,
        "2026-02-01 11:00:00"
    )

    assert speed == 0.0


def test_cycle_speed():

    speed = calculate_cycle_speed(
        3600,
        "2026-02-01 10:00:00",
        "2026-02-01 11:00:00"
    )

    assert speed == 3600


def test_production_speed():

    speed = calculate_production_speed(
        1800,
        "2026-02-01 10:00:00",
        "2026-02-01 11:00:00"
    )

    assert speed == 1800