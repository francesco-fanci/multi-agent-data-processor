from datetime import date, timedelta

import pandas as pd
import pytest

from src.analytics.correlation import (
    calculate_head_correlations,
    calculate_head_residual_correlations,
    find_top_correlations
)


def create_daily_results():

    results = {
        "H01": [],
        "H02": [],
        "H03": []
    }

    start_date = date(2026, 2, 1)

    for index in range(5):

        current_date = start_date + timedelta(
            days=index
        )

        results["H01"].append({
            "date": current_date,
            "average": float(index + 1),
            "count": 1000
        })

        results["H02"].append({
            "date": current_date,
            "average": float((index + 1) * 2),
            "count": 1000
        })

        results["H03"].append({
            "date": current_date,
            "average": float(5 - index),
            "count": 1000
        })

    return results


def test_positive_head_correlation():

    results = create_daily_results()

    correlation_matrix = calculate_head_correlations(
        results,
        min_events=500,
        min_days=5
    )

    assert correlation_matrix.loc[
        "H01",
        "H02"
    ] == pytest.approx(1.0)


def test_negative_head_correlation():

    results = create_daily_results()

    correlation_matrix = calculate_head_correlations(
        results,
        min_events=500,
        min_days=5
    )

    assert correlation_matrix.loc[
        "H01",
        "H03"
    ] == pytest.approx(-1.0)


def test_low_event_days_are_filtered():

    results = {
        "H01": [
            {
                "date": date(2026, 2, 1),
                "average": 2.0,
                "count": 100
            }
        ]
    }

    correlation_matrix = calculate_head_correlations(
        results,
        min_events=500,
        min_days=1
    )

    assert correlation_matrix.empty


def test_minimum_number_of_days():

    results = create_daily_results()

    correlation_matrix = calculate_head_correlations(
        results,
        min_events=500,
        min_days=10
    )

    assert pd.isna(
        correlation_matrix.loc[
            "H01",
            "H02"
        ]
    )


def test_residual_correlation():

    results = {
        "H01": [],
        "H02": []
    }

    start_date = date(2026, 2, 1)

    for index in range(5):

        current_date = start_date + timedelta(
            days=index
        )

        results["H01"].append({
            "date": current_date,
            "average": float(index + 1),
            "count": 1000
        })

        results["H02"].append({
            "date": current_date,
            "average": float(10 - index),
            "count": 1000
        })

    correlation_matrix = (
        calculate_head_residual_correlations(
            results,
            min_events=500,
            min_days=5
        )
    )

    assert correlation_matrix.loc[
        "H01",
        "H02"
    ] == pytest.approx(-1.0)


def test_find_top_correlations():

    correlation_matrix = pd.DataFrame(
        {
            "H01": [1.0, 0.2, -0.9],
            "H02": [0.2, 1.0, 0.5],
            "H03": [-0.9, 0.5, 1.0]
        },
        index=[
            "H01",
            "H02",
            "H03"
        ]
    )

    result = find_top_correlations(
        correlation_matrix,
        top_n=2
    )

    assert len(result) == 2

    assert result[0]["head_1"] == "H01"
    assert result[0]["head_2"] == "H03"
    assert result[0]["correlation"] == pytest.approx(
        -0.9
    )

    assert result[1]["head_1"] == "H02"
    assert result[1]["head_2"] == "H03"
    assert result[1]["correlation"] == pytest.approx(
        0.5
    )