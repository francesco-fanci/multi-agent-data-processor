import pandas as pd

from src.cleaning.data_quality import add_quality_flags


def test_valid_event():

    dataframe = pd.DataFrame({
        "Previous Count": [10],
        "Count Difference": [1],
        "Time Difference": [1]
    })

    result = add_quality_flags(dataframe)

    assert result["Data Quality"].iloc[0] == "Valid"


def test_counter_recovery():

    dataframe = pd.DataFrame({
        "Previous Count": [0],
        "Count Difference": [150],
        "Time Difference": [1]
    })

    result = add_quality_flags(
        dataframe,
        counter_recovery_threshold=100,
        data_gap_threshold_seconds=5
    )

    assert result["Data Quality"].iloc[0] == "Counter Recovery"


def test_data_gap():

    dataframe = pd.DataFrame({
        "Previous Count": [10],
        "Count Difference": [5],
        "Time Difference": [10]
    })

    result = add_quality_flags(
        dataframe,
        counter_recovery_threshold=100,
        data_gap_threshold_seconds=5
    )

    assert result["Data Quality"].iloc[0] == "Data Gap"


def test_counter_recovery_has_priority_over_data_gap():

    dataframe = pd.DataFrame({
        "Previous Count": [0],
        "Count Difference": [150],
        "Time Difference": [10]
    })

    result = add_quality_flags(
        dataframe,
        counter_recovery_threshold=100,
        data_gap_threshold_seconds=5
    )

    assert result["Data Quality"].iloc[0] == "Counter Recovery"


def test_multiple_quality_flags():

    dataframe = pd.DataFrame({
        "Previous Count": [10, 0, 10],
        "Count Difference": [1, 150, 5],
        "Time Difference": [1, 1, 10]
    })

    result = add_quality_flags(
        dataframe,
        counter_recovery_threshold=100,
        data_gap_threshold_seconds=5
    )

    assert result["Data Quality"].tolist() == [
        "Valid",
        "Counter Recovery",
        "Data Gap"
    ]