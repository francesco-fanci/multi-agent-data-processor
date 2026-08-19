import pandas as pd
import pytest

from src.agents.data_quality_agent import (
    DataQualityAgent
)

from src.agents.analytics_agent import (
    AnalyticsAgent
)


def create_dataframe(counts, start_time):

    rows = len(counts)

    data = {
        "timestamp": pd.date_range(
            start_time,
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


def test_analytics_agent():

    dataframe = create_dataframe(
        [10, 11, 12],
        "2026-02-01 10:00:00"
    )

    quality_agent = DataQualityAgent()
    analytics_agent = AnalyticsAgent()

    context = quality_agent.run({
        "dataframe": dataframe
    })

    result = analytics_agent.run(
        context
    )

    assert result["total_cycles"] == 2

    assert (
        result["total_production_pieces"]
        == 2
    )

    assert (
        result["torque_stats"]["H01"]["count"]
        == 2
    )

    assert (
        result["torque_stats"]["H01"]["sum"]
        == 4.0
    )

    assert result["cycle_speed"] == pytest.approx(
        7200.0
    )

    assert (
        result["production_speed"]
        == pytest.approx(7200.0)
    )


def test_analytics_state_between_files():

    quality_agent = DataQualityAgent()
    analytics_agent = AnalyticsAgent()

    first_dataframe = create_dataframe(
        [10, 11],
        "2026-02-01 10:00:00"
    )

    context = quality_agent.run({
        "dataframe": first_dataframe
    })

    context = analytics_agent.run(
        context
    )

    second_dataframe = create_dataframe(
        [12, 13],
        "2026-02-01 10:00:02"
    )

    context["dataframe"] = (
        second_dataframe
    )

    context = quality_agent.run(
        context
    )

    context = analytics_agent.run(
        context
    )

    assert context["total_cycles"] == 3

    assert (
        context["total_production_pieces"]
        == 3
    )

    assert (
        context["torque_stats"]["H01"]["count"]
        == 3
    )

    assert context["cycle_speed"] == pytest.approx(
        5400.0
    )


def test_missing_dataframe():

    agent = AnalyticsAgent()

    with pytest.raises(
        ValueError,
        match="Missing dataframe in context"
    ):
        agent.run({})

def test_finalize_analytics():

    dataframe = create_dataframe(
        [10, 11, 12],
        "2026-02-01 10:00:00"
    )

    quality_agent = DataQualityAgent()
    analytics_agent = AnalyticsAgent()

    context = quality_agent.run({
        "dataframe": dataframe
    })

    context = analytics_agent.run(
        context
    )

    result = analytics_agent.finalize(
        context
    )

    assert "torque_results" in result

    assert (
        result["torque_results"]["H01"]["count"]
        == 2
    )

    assert "daily_torque_results" in result
    assert "drift_results" in result
    assert "correlation_matrix" in result

    assert (
        "residual_correlation_matrix"
        in result
    )

    assert "top_correlations" in result

    assert (
        "top_residual_correlations"
        in result
    )