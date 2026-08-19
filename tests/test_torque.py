from datetime import date

import pandas as pd
import pytest

from src.analytics.torque import (
    update_torque_statistics,
    calculate_torque_results,
    update_daily_torque_statistics,
    calculate_daily_torque_results,
    calculate_torque_moving_average,
    detect_torque_drift
)


def test_torque_statistics():

    events = pd.DataFrame({
        "Head": ["H01", "H01", "H01"],
        "AppTorque": [1.0, 2.0, 3.0]
    })

    stats = {}

    update_torque_statistics(
        stats,
        events
    )

    results = calculate_torque_results(
        stats
    )

    assert results["H01"]["count"] == 3
    assert results["H01"]["average"] == 2.0
    assert results["H01"]["standard_deviation"] == pytest.approx(0.81649658)
    assert results["H01"]["min"] == 1.0
    assert results["H01"]["max"] == 3.0


def test_zero_torque_count():

    events = pd.DataFrame({
        "Head": ["H01", "H01", "H01"],
        "AppTorque": [0.0, 2.0, 0.0]
    })

    stats = {}

    update_torque_statistics(
        stats,
        events
    )

    results = calculate_torque_results(
        stats
    )

    assert results["H01"]["zero_count"] == 2


def test_torque_statistics_multiple_updates():

    first_events = pd.DataFrame({
        "Head": ["H01", "H01"],
        "AppTorque": [1.0, 2.0]
    })

    second_events = pd.DataFrame({
        "Head": ["H01"],
        "AppTorque": [3.0]
    })

    stats = {}

    update_torque_statistics(
        stats,
        first_events
    )

    update_torque_statistics(
        stats,
        second_events
    )

    results = calculate_torque_results(
        stats
    )

    assert results["H01"]["count"] == 3
    assert results["H01"]["average"] == 2.0
    assert results["H01"]["min"] == 1.0
    assert results["H01"]["max"] == 3.0


def test_daily_torque_statistics():

    events = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-02-01 10:00:00",
            "2026-02-01 11:00:00",
            "2026-02-02 10:00:00"
        ]),
        "Head": [
            "H01",
            "H01",
            "H01"
        ],
        "AppTorque": [
            2.0,
            4.0,
            6.0
        ]
    })

    daily_stats = {}

    update_daily_torque_statistics(
        daily_stats,
        events
    )

    results = calculate_daily_torque_results(
        daily_stats
    )

    assert len(results["H01"]) == 2

    assert results["H01"][0]["date"] == date(
        2026,
        2,
        1
    )

    assert results["H01"][0]["average"] == 3.0
    assert results["H01"][0]["count"] == 2

    assert results["H01"][1]["average"] == 6.0
    assert results["H01"][1]["count"] == 1


def test_weighted_moving_average():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 100
            },
            {
                "date": date(2026, 2, 2),
                "average": 4.0,
                "count": 300
            }
        ]
    }

    result = calculate_torque_moving_average(
        results,
        window_days=2
    )

    assert result["H01"][0]["moving_average"] == 2.0

    assert result["H01"][1]["moving_average"] == pytest.approx(
        3.5
    )


def test_detect_torque_drift_increase():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 1000
            },
            {
                "date": date(2026, 2, 2),
                "average": 2.2,
                "count": 1000
            }
        ]
    }

    drift = detect_torque_drift(
        results,
        window_days=7,
        threshold=0.1,
        min_events=500
    )

    assert len(drift["H01"]) == 1
    assert drift["H01"][0]["direction"] == "Increase"
    assert drift["H01"][0]["baseline"] == 2.0
    assert drift["H01"][0]["difference"] == pytest.approx(
        0.2
    )


def test_detect_torque_drift_decrease():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 1000
            },
            {
                "date": date(2026, 2, 2),
                "average": 1.8,
                "count": 1000
            }
        ]
    }

    drift = detect_torque_drift(
        results,
        window_days=7,
        threshold=0.1,
        min_events=500
    )

    assert len(drift["H01"]) == 1
    assert drift["H01"][0]["direction"] == "Decrease"
    assert drift["H01"][0]["difference"] == pytest.approx(
        -0.2
    )


def test_no_drift_below_threshold():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 1000
            },
            {
                "date": date(2026, 2, 2),
                "average": 2.05,
                "count": 1000
            }
        ]
    }

    drift = detect_torque_drift(
        results,
        window_days=7,
        threshold=0.1,
        min_events=500
    )

    assert drift["H01"] == []


def test_drift_ignores_low_event_days():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 1000
            },
            {
                "date": date(2026, 2, 2),
                "average": 3.0,
                "count": 100
            }
        ]
    }

    drift = detect_torque_drift(
        results,
        window_days=7,
        threshold=0.1,
        min_events=500
    )

    assert drift["H01"] == []