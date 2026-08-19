import pandas as pd
import pytest

from src.agents.data_quality_agent import (
    DataQualityAgent
)


def create_dataframe(counts):

    rows = len(counts)

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
            data[head + " Count"] = counts
        else:
            data[head + " Count"] = [0] * rows

        data[head + " AppTorque"] = (
            [2.0] * rows
        )

        data[head + " Status"] = (
            [0] * rows
        )

    return pd.DataFrame(data)


def test_data_quality_agent():

    dataframe = create_dataframe(
        [10, 11, 11]
    )

    agent = DataQualityAgent()

    result = agent.run({
        "dataframe": dataframe
    })

    h01_events = result["events"][
        result["events"]["Head"] == "H01"
    ]

    assert len(h01_events) == 1

    assert (
        h01_events.iloc[0]["Count Difference"]
        == 1
    )

    assert (
        h01_events.iloc[0]["Event Type"]
        == "Closure OK"
    )

    assert (
        h01_events.iloc[0]["Data Quality"]
        == "Valid"
    )

    assert len(result["clean_events"]) == 1


def test_agent_preserves_continuity():

    agent = DataQualityAgent()

    first_dataframe = create_dataframe(
        [9, 10]
    )

    first_result = agent.run({
        "dataframe": first_dataframe
    })

    second_dataframe = create_dataframe(
        [11, 11]
    )

    second_dataframe["timestamp"] = (
        pd.date_range(
            "2026-02-01 10:00:02",
            periods=2,
            freq="s"
        )
    )

    second_result = agent.run({
        "dataframe": second_dataframe,
        "previous_counts": (
            first_result["previous_counts"]
        ),
        "previous_timestamp": (
            first_result["previous_timestamp"]
        )
    })

    h01_events = second_result["events"][
        second_result["events"]["Head"]
        == "H01"
    ]

    assert len(h01_events) == 1

    assert (
        h01_events.iloc[0]["Previous Count"]
        == 10
    )

    assert (
        h01_events.iloc[0]["Count"]
        == 11
    )


def test_missing_dataframe():

    agent = DataQualityAgent()

    with pytest.raises(
        ValueError,
        match="Missing dataframe in context"
    ):
        agent.run({})