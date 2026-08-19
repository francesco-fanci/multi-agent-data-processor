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
                    "The physical unit of AppTorque is "
                    "not specified in the available data."
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

        result = context.copy()
        result["report"] = report

        return result