import pandas as pd
import pytest

from src.cleaning.closure_detector import (
    detect_closures,
    detect_all_closures,
    detect_counter_drops
)


def create_dataframe(h01_counts):

    rows = len(h01_counts)

    data = {
        "timestamp": pd.date_range(
            "2026-02-01 10:00:00",
            periods=rows,
            freq="s"
        )
    }

    for number in range(1, 37):

        head = f"H{number:02d}"

        if head == "H01":
            data[head + " Count"] = h01_counts
        else:
            data[head + " Count"] = [0] * rows

        data[head + " AppTorque"] = [2.0] * rows
        data[head + " Status"] = [0] * rows

    return pd.DataFrame(data)


def test_detect_single_closure():

    dataframe = create_dataframe(
        [10, 10, 11, 11]
    )

    result = detect_closures(
        dataframe,
        "H01"
    )

    assert len(result) == 1
    assert result.iloc[0]["Count"] == 11
    assert result.iloc[0]["Previous Count"] == 10
    assert result.iloc[0]["Count Difference"] == 1


def test_detect_multiple_counter_increment():

    dataframe = create_dataframe(
        [10, 12]
    )

    result = detect_closures(
        dataframe,
        "H01"
    )

    assert len(result) == 1
    assert result.iloc[0]["Count Difference"] == 2


def test_no_closure_without_increment():

    dataframe = create_dataframe(
        [10, 10, 10]
    )

    result = detect_closures(
        dataframe,
        "H01"
    )

    assert len(result) == 0


def test_continuity_between_files():

    first_dataframe = create_dataframe(
        [9, 10]
    )

    (
        first_result,
        previous_counts,
        previous_timestamp
    ) = detect_all_closures(
        first_dataframe
    )

    second_dataframe = create_dataframe(
        [11, 11]
    )

    second_dataframe["timestamp"] = pd.date_range(
        "2026-02-01 10:00:02",
        periods=2,
        freq="s"
    )

    (
        second_result,
        new_previous_counts,
        new_previous_timestamp
    ) = detect_all_closures(
        second_dataframe,
        previous_counts,
        previous_timestamp
    )

    h01_closures = second_result[
        second_result["Head"] == "H01"
    ]

    assert len(h01_closures) == 1
    assert h01_closures.iloc[0]["Previous Count"] == 10
    assert h01_closures.iloc[0]["Count"] == 11
    assert h01_closures.iloc[0]["Count Difference"] == 1
    assert h01_closures.iloc[0]["Time Difference"] == 1


def test_detect_counter_drop():

    dataframe = create_dataframe(
        [10, 10, 0, 0]
    )

    result = detect_counter_drops(
        dataframe
    )

    h01_drops = result[
        result["Head"] == "H01"
    ]

    assert len(h01_drops) == 1
    assert h01_drops.iloc[0]["Previous Count"] == 10
    assert h01_drops.iloc[0]["Count"] == 0
    assert h01_drops.iloc[0]["Count Difference"] == -10


def test_missing_required_column():

    dataframe = create_dataframe(
        [10, 11]
    )

    dataframe = dataframe.drop(
        columns=["H01 AppTorque"]
    )

    with pytest.raises(
        ValueError,
        match="Missing required column: H01 AppTorque"
    ):
        detect_closures(
            dataframe,
            "H01"
        )