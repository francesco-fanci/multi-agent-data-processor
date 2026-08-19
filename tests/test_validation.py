import pandas as pd

from src.ingestion.validation import validate_dataframe


def create_valid_dataframe():

    data = {
        "timestamp": ["2026-02-01 10:00:00"]
    }

    for number in range(1, 37):

        head = f"H{number:02d}"

        data[head + " Count"] = [1]
        data[head + " AppTorque"] = [2.0]
        data[head + " Status"] = [0]

    return pd.DataFrame(data)


def test_valid_dataframe():

    dataframe = create_valid_dataframe()

    problems = validate_dataframe(dataframe)

    assert problems == []


def test_missing_timestamp():

    dataframe = create_valid_dataframe()
    dataframe = dataframe.drop(columns=["timestamp"])

    problems = validate_dataframe(dataframe)

    assert "Missing timestamp column" in problems


def test_missing_required_column():

    dataframe = create_valid_dataframe()
    dataframe = dataframe.drop(columns=["H01 Count"])

    problems = validate_dataframe(dataframe)

    assert "Missing column: H01 Count" in problems


def test_invalid_timestamp():

    dataframe = create_valid_dataframe()
    dataframe.loc[0, "timestamp"] = "not-a-date"

    problems = validate_dataframe(dataframe)

    assert "Invalid timestamps: 1" in problems


def test_missing_value():

    dataframe = create_valid_dataframe()
    dataframe.loc[0, "H01 AppTorque"] = None

    problems = validate_dataframe(dataframe)

    assert "Missing values: 1" in problems