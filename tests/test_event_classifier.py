import pandas as pd

from src.cleaning.event_classifier import classify_events


def test_closure_ok():

    dataframe = pd.DataFrame({
        "Status": [0]
    })

    result = classify_events(dataframe)

    assert result["Event Type"].iloc[0] == "Closure OK"


def test_no_load():

    dataframe = pd.DataFrame({
        "Status": [2]
    })

    result = classify_events(dataframe)

    assert result["Event Type"].iloc[0] == "No Load"


def test_bad_closure():

    dataframe = pd.DataFrame({
        "Status": [65]
    })

    result = classify_events(dataframe)

    assert result["Event Type"].iloc[0] == "Bad Closure"


def test_unknown_status():

    dataframe = pd.DataFrame({
        "Status": [4]
    })

    result = classify_events(dataframe)

    assert result["Event Type"].iloc[0] == "Unknown"


def test_multiple_statuses():

    dataframe = pd.DataFrame({
        "Status": [0, 2, 65, 4, 9]
    })

    result = classify_events(dataframe)

    assert result["Event Type"].tolist() == [
        "Closure OK",
        "No Load",
        "Bad Closure",
        "Unknown",
        "Unknown"
    ]