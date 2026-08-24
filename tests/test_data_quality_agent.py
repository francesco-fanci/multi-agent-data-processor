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

    assert (
        result["quality_summary"]["raw_events"]
        == 1
    )

    assert (
        result["quality_summary"]["clean_events"]
        == 1
    )

    assert (
        result["quality_summary"]["valid"]
        == 1
    )

    assert (
        result["quality_summary"][
            "counter_recovery"
        ]
        == 0
    )

    assert (
        result["quality_summary"]["data_gap"]
        == 0
    )

    assert (
        result["counter_drop_summary"]["total"]
        == 0
    )

    assert (
        result["counter_drop_summary"]["to_zero"]
        == 0
    )


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

    second_context = first_result.copy()

    second_context["dataframe"] = (
        second_dataframe
    )

    second_result = agent.run(
        second_context
    )

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

    assert (
        second_result[
            "quality_summary"
        ]["raw_events"] == 2
    )


def test_counter_drop_summary():

    dataframe = create_dataframe(
        [10, 10, 0]
    )

    agent = DataQualityAgent()

    result = agent.run({
        "dataframe": dataframe
    })

    summary = result[
        "counter_drop_summary"
    ]

    assert summary["total"] == 1
    assert summary["to_zero"] == 1
    assert summary["to_non_zero"] == 0

    assert len(
        summary["timestamps"]
    ) == 1


def test_missing_dataframe():

    agent = DataQualityAgent()

    with pytest.raises(
        ValueError,
        match="Missing dataframe in context"
    ):
        agent.run({})