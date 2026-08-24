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
        "top_residual_correlations": [],

        "unit_validation_problems": [
            "Missing unit metadata: AppTorque"
        ],

        "quality_summary": {
            "raw_events": 1000,
            "clean_events": 990,
            "valid": 980,
            "counter_recovery": 10,
            "data_gap": 10
        },

        "counter_drop_summary": {
            "total": 5,
            "to_zero": 4,
            "to_non_zero": 1,
            "timestamps": {
                "2026-02-01 10:00:00",
                "2026-02-01 11:00:00"
            }
        }
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

    assert (
        report["findings"][
            "data_quality"
        ]["raw_events"]
        == 1000
    )

    assert (
        report["findings"][
            "data_quality"
        ]["clean_events"]
        == 990
    )

    assert (
        report["findings"][
            "data_quality"
        ]["counter_recovery"]
        == 10
    )

    assert (
        report["findings"][
            "data_quality"
        ]["data_gap"]
        == 10
    )

    assert (
        "Unit validation: "
        "Missing unit metadata: AppTorque"
        in report["confidence_and_limits"]
    )

    assert (
        report["findings"][
            "counter_drops"
        ]["total"]
        == 5
    )

    assert (
        report["findings"][
            "counter_drops"
        ]["to_zero"]
        == 4
    )

    assert (
        report["findings"][
            "counter_drops"
        ]["to_non_zero"]
        == 1
    )

    assert (
        report["findings"][
            "counter_drops"
        ]["unique_timestamps"]
        == 2
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