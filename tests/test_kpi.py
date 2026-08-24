import pytest
from src.analytics.kpi import (
    calculate_speed,
    calculate_cycle_speed,
    calculate_production_speed,
    update_incremental_speed
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

def test_incremental_speed_first_interval():

    speed, elapsed = update_incremental_speed(
        current_speed=0.0,
        current_elapsed_seconds=0,
        new_pieces=100,
        new_elapsed_seconds=1800
    )

    assert speed == 200.0
    assert elapsed == 1800


def test_incremental_speed_multiple_intervals():

    speed, elapsed = update_incremental_speed(
        current_speed=0.0,
        current_elapsed_seconds=0,
        new_pieces=100,
        new_elapsed_seconds=1800
    )

    speed, elapsed = update_incremental_speed(
        current_speed=speed,
        current_elapsed_seconds=elapsed,
        new_pieces=100,
        new_elapsed_seconds=3600
    )

    assert speed == pytest.approx(
        133.3333333333
    )

    assert elapsed == 5400


def test_incremental_speed_zero_interval():

    speed, elapsed = update_incremental_speed(
        current_speed=100.0,
        current_elapsed_seconds=3600,
        new_pieces=50,
        new_elapsed_seconds=0
    )

    assert speed == 100.0
    assert elapsed == 3600