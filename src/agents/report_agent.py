from src.agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Report Agent",
            goal="Generate a structured industrial analytics report"
        )

    def run(self, context):

        required_keys = [
            "torque_results",
            "drift_results",
            "anomaly_stats",
            "idle_periods"
        ]

        for key in required_keys:
            if key not in context:
                raise ValueError(
                    "Missing " + key + " in context"
                )

        unit_validation_problems = context.get(
            "unit_validation_problems",
            []
        )

        quality_summary = context.get(
            "quality_summary",
            {}
        )

        counter_drop_summary = context.get(
            "counter_drop_summary",
            {}
        )

        total_anomalies = sum(
            item["count"]
            for item in context["anomaly_stats"].values()
        )

        total_drifts = sum(
            len(items)
            for items in context["drift_results"].values()
        )

        total_idle_seconds = sum(
            period["duration_seconds"]
            for period in context["idle_periods"]
        )

        total_idle_hours = (
            total_idle_seconds / 3600
        )

        report = {
            "goal": (
                "Refine industrial telemetry data and "
                "identify relevant production patterns."
            ),

            "data": {
                "first_timestamp": context.get(
                    "first_timestamp"
                ),
                "last_timestamp": context.get(
                    "last_timestamp"
                ),
                "total_cycles": context.get(
                    "total_cycles",
                    0
                ),
                "production_pieces": context.get(
                    "total_production_pieces",
                    0
                )
            },

            "analyses": [
                "Closure detection",
                "Data quality filtering",
                "Production speed",
                "Torque statistics",
                "Torque moving average",
                "Torque drift detection",
                "Torque anomaly detection",
                "Head correlation analysis",
                "Idle period detection"
            ],

            "findings": {
                "cycle_speed": context.get(
                    "cycle_speed",
                    0.0
                ),
                "production_speed": context.get(
                    "production_speed",
                    0.0
                ),

                "data_quality": {
                    "raw_events": quality_summary.get(
                        "raw_events",
                        0
                    ),
                    "clean_events": quality_summary.get(
                        "clean_events",
                        0
                    ),
                    "valid": quality_summary.get(
                        "valid",
                        0
                    ),
                    "counter_recovery": quality_summary.get(
                        "counter_recovery",
                        0
                    ),
                    "data_gap": quality_summary.get(
                        "data_gap",
                        0
                    )
                },

                "counter_drops": {
                    "total": counter_drop_summary.get(
                        "total",
                        0
                    ),
                    "to_zero": counter_drop_summary.get(
                        "to_zero",
                        0
                    ),
                    "to_non_zero": counter_drop_summary.get(
                        "to_non_zero",
                        0
                    ),
                    "unique_timestamps": len(
                        counter_drop_summary.get(
                            "timestamps",
                            set()
                        )
                    )
                },

                "torque_anomalies": total_anomalies,
                "torque_drift_events": total_drifts,
                "idle_periods": len(
                    context["idle_periods"]
                ),
                "idle_hours": total_idle_hours,
                "top_correlations": context.get(
                    "top_correlations",
                    []
                ),
                "top_residual_correlations": (
                    context.get(
                        "top_residual_correlations",
                        []
                    )
                )
            },

            "confidence_and_limits": [
                (
                    "Torque anomalies are statistical "
                    "outliers and do not directly indicate "
                    "machine failures."
                ),
                (
                    "Correlation between heads does not "
                    "imply causation."
                ),
                (
                    "Production speed is an average over "
                    "the observed time interval."
                )
            ],

            "next_checks": [
                (
                    "Review detected torque drifts and "
                    "anomalies with machine context."
                ),
                (
                    "Investigate long idle periods."
                ),
                (
                    "Review strong residual correlations "
                    "between heads."
                ),
                (
                    "Confirm AppTorque measurement unit "
                    "from machine documentation."
                )
            ]
        }

        for problem in unit_validation_problems:

            report[
                "confidence_and_limits"
            ].append(
                "Unit validation: "
                + problem
            )

        result = context.copy()
        result["report"] = report

        return result