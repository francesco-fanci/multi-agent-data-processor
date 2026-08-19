import pytest

from src.agents.report_agent import ReportAgent


def create_context():

    return {
        "torque_results": {
            "H01": {
                "count": 100
            }
        },

        "drift_results": {
            "H01": [
                {
                    "direction": "Increase"
                }
            ],
            "H02": []
        },

        "anomaly_stats": {
            "H01": {
                "count": 3
            },
            "H02": {
                "count": 2
            }
        },

        "idle_periods": [
            {
                "start": "2026-02-01 10:00:00",
                "end": "2026-02-01 11:00:00",
                "duration_seconds": 3600
            }
        ],

        "total_cycles": 1000,
        "total_production_pieces": 800,

        "cycle_speed": 500.0,
        "production_speed": 400.0,

        "first_timestamp": (
            "2026-02-01 10:00:00"
        ),

        "last_timestamp": (
            "2026-02-01 12:00:00"
        ),

        "top_correlations": [],
        "top_residual_correlations": []
    }


def test_report_agent():

    agent = ReportAgent()

    result = agent.run(
        create_context()
    )

    report = result["report"]

    assert "goal" in report
    assert "data" in report
    assert "analyses" in report
    assert "findings" in report
    assert "confidence_and_limits" in report
    assert "next_checks" in report

    assert (
        report["data"]["total_cycles"]
        == 1000
    )

    assert (
        report["data"]["production_pieces"]
        == 800
    )

    assert (
        report["findings"]["torque_anomalies"]
        == 5
    )

    assert (
        report["findings"]["torque_drift_events"]
        == 1
    )

    assert (
        report["findings"]["idle_periods"]
        == 1
    )

    assert (
        report["findings"]["idle_hours"]
        == pytest.approx(1.0)
    )


def test_report_agent_name():

    agent = ReportAgent()

    assert agent.name == "Report Agent"


def test_missing_finalized_results():

    agent = ReportAgent()

    with pytest.raises(
        ValueError,
        match="Missing torque_results in context"
    ):
        agent.run({})