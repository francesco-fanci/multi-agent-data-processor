import pandas as pd

from src.analytics.anomaly import update_torque_anomalies


def create_events(values):

    return pd.DataFrame({
        "timestamp": pd.date_range(
            "2026-02-01 10:00:00",
            periods=len(values),
            freq="s"
        ),
        "Head": ["H01"] * len(values),
        "AppTorque": values
    })


def test_no_anomalies():

    events = create_events(
        [2.0] * 100
    )

    stats = {}

    update_torque_anomalies(
        stats,
        events,
        min_events=100
    )

    assert stats["H01"]["count"] == 0
    assert stats["H01"]["lowest_value"] is None
    assert stats["H01"]["highest_value"] is None


def test_high_anomaly():

    events = create_events(
        [2.0] * 100 + [3.0]
    )

    stats = {}

    update_torque_anomalies(
        stats,
        events,
        min_events=100
    )

    assert stats["H01"]["count"] == 1
    assert stats["H01"]["highest_value"] == 3.0


def test_low_anomaly():

    events = create_events(
        [1.0] + [2.0] * 100
    )

    stats = {}

    update_torque_anomalies(
        stats,
        events,
        min_events=100
    )

    assert stats["H01"]["count"] == 1
    assert stats["H01"]["lowest_value"] == 1.0


def test_minimum_margin_prevents_small_difference():

    events = create_events(
        [2.0] * 100 + [2.04]
    )

    stats = {}

    update_torque_anomalies(
        stats,
        events,
        iqr_multiplier=3.0,
        minimum_margin=0.05,
        min_events=100
    )

    assert stats["H01"]["count"] == 0


def test_ignore_when_not_enough_events():

    events = create_events(
        [2.0, 2.0, 3.0]
    )

    stats = {}

    update_torque_anomalies(
        stats,
        events,
        min_events=100
    )

    assert stats["H01"]["count"] == 0


def test_anomalies_accumulate_between_updates():

    first_events = create_events(
        [2.0] * 100 + [3.0]
    )

    second_events = create_events(
        [2.0] * 100 + [3.5]
    )

    stats = {}

    update_torque_anomalies(
        stats,
        first_events,
        min_events=100
    )

    update_torque_anomalies(
        stats,
        second_events,
        min_events=100
    )

    assert stats["H01"]["count"] == 2
    assert stats["H01"]["lowest_value"] == 3.0
    assert stats["H01"]["highest_value"] == 3.5