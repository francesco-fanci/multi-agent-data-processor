import pandas as pd
import pytest

from src.analytics.idle import (
    detect_idle_periods,
    finalize_idle_period
)


def create_dataframe(timestamps):

    data = {
        "timestamp": pd.to_datetime(timestamps)
    }

    for number in range(1, 37):

        head = f"H{number:02d}"

        data[head + " Status"] = [2] * len(timestamps)

    return pd.DataFrame(data)


def test_idle_period_detected():

    dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01",
        "2026-02-01 10:00:02",
        "2026-02-01 10:00:03"
    ])

    dataframe.loc[
        3,
        "H01 Status"
    ] = 0

    periods, state = detect_idle_periods(
        dataframe,
        min_duration_seconds=2,
        max_gap_seconds=2
    )

    assert len(periods) == 1

    assert periods[0]["duration_seconds"] == 2

    assert periods[0]["start"] == pd.Timestamp(
        "2026-02-01 10:00:00"
    )

    assert periods[0]["end"] == pd.Timestamp(
        "2026-02-01 10:00:02"
    )


def test_short_idle_period_is_ignored():

    dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01",
        "2026-02-01 10:00:02"
    ])

    dataframe.loc[
        2,
        "H01 Status"
    ] = 0

    periods, state = detect_idle_periods(
        dataframe,
        min_duration_seconds=2,
        max_gap_seconds=2
    )

    assert periods == []


def test_all_heads_must_be_no_load():

    dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01",
        "2026-02-01 10:00:02"
    ])

    dataframe.loc[
        2,
        "H07 Status"
    ] = 0

    periods, state = detect_idle_periods(
        dataframe,
        min_duration_seconds=1,
        max_gap_seconds=2
    )

    assert len(periods) == 1

    assert periods[0]["duration_seconds"] == 1


def test_large_gap_splits_idle_period():

    dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01",
        "2026-02-01 10:00:05"
    ])

    periods, state = detect_idle_periods(
        dataframe,
        min_duration_seconds=1,
        max_gap_seconds=2
    )

    assert len(periods) == 1

    assert periods[0]["start"] == pd.Timestamp(
        "2026-02-01 10:00:00"
    )

    assert periods[0]["end"] == pd.Timestamp(
        "2026-02-01 10:00:01"
    )

    assert state["start"] == pd.Timestamp(
        "2026-02-01 10:00:05"
    )


def test_idle_continuity_between_files():

    first_dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01"
    ])

    first_periods, state = detect_idle_periods(
        first_dataframe,
        min_duration_seconds=3,
        max_gap_seconds=2
    )

    assert first_periods == []

    second_dataframe = create_dataframe([
        "2026-02-01 10:00:02",
        "2026-02-01 10:00:03",
        "2026-02-01 10:00:04"
    ])

    second_dataframe.loc[
        2,
        "H01 Status"
    ] = 0

    second_periods, state = detect_idle_periods(
        second_dataframe,
        idle_state=state,
        min_duration_seconds=3,
        max_gap_seconds=2
    )

    assert len(second_periods) == 1

    assert second_periods[0]["start"] == pd.Timestamp(
        "2026-02-01 10:00:00"
    )

    assert second_periods[0]["end"] == pd.Timestamp(
        "2026-02-01 10:00:03"
    )

    assert second_periods[0]["duration_seconds"] == 3


def test_finalize_open_idle_period():

    dataframe = create_dataframe([
        "2026-02-01 10:00:00",
        "2026-02-01 10:00:01",
        "2026-02-01 10:00:02"
    ])

    periods, state = detect_idle_periods(
        dataframe,
        min_duration_seconds=2,
        max_gap_seconds=2
    )

    assert periods == []

    final_periods = finalize_idle_period(
        state,
        min_duration_seconds=2
    )

    assert len(final_periods) == 1
    assert final_periods[0]["duration_seconds"] == 2

