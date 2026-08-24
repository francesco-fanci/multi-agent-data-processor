from src.agents.base_agent import BaseAgent

from src.cleaning.closure_detector import (
    detect_all_closures,
    detect_counter_drops
)

from src.cleaning.event_classifier import (
    classify_events
)

from src.cleaning.data_quality import (
    add_quality_flags
)

from src.config import (
    COUNTER_RECOVERY_THRESHOLD,
    DATA_GAP_THRESHOLD_SECONDS
)


class DataQualityAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Data Quality Agent",
            goal="Detect and refine industrial closure events"
        )

    def run(self, context):

        if "dataframe" not in context:
            raise ValueError(
                "Missing dataframe in context"
            )

        dataframe = context["dataframe"]

        previous_counts = context.get(
            "previous_counts"
        )

        previous_timestamp = context.get(
            "previous_timestamp"
        )

        counter_drops = detect_counter_drops(
            dataframe,
            previous_counts
        )

        (
            events,
            new_previous_counts,
            new_previous_timestamp
        ) = detect_all_closures(
            dataframe,
            previous_counts,
            previous_timestamp
        )

        classified_events = classify_events(
            events
        )

        quality_events = add_quality_flags(
            classified_events,
            counter_recovery_threshold=(
                COUNTER_RECOVERY_THRESHOLD
            ),
            data_gap_threshold_seconds=(
                DATA_GAP_THRESHOLD_SECONDS
            )
        )

        clean_events = quality_events[
            quality_events["Data Quality"]
            != "Counter Recovery"
        ].copy()

        quality_summary = context.get(
            "quality_summary",
            {
                "raw_events": 0,
                "clean_events": 0,
                "valid": 0,
                "counter_recovery": 0,
                "data_gap": 0
            }
        )

        quality_summary["raw_events"] += len(
            quality_events
        )

        quality_summary["clean_events"] += len(
            clean_events
        )

        quality_summary["valid"] += len(
            quality_events[
                quality_events["Data Quality"]
                == "Valid"
            ]
        )

        quality_summary[
            "counter_recovery"
        ] += len(
            quality_events[
                quality_events["Data Quality"]
                == "Counter Recovery"
            ]
        )

        quality_summary["data_gap"] += len(
            quality_events[
                quality_events["Data Quality"]
                == "Data Gap"
            ]
        )

        counter_drop_summary = context.get(
            "counter_drop_summary",
            {
                "total": 0,
                "to_zero": 0,
                "to_non_zero": 0,
                "timestamps": set()
            }
        )

        counter_drop_summary["total"] += len(
            counter_drops
        )

        if len(counter_drops) > 0:

            counter_drop_summary["to_zero"] += len(
                counter_drops[
                    counter_drops["Count"] == 0
                ]
            )

            counter_drop_summary[
                "to_non_zero"
            ] += len(
                counter_drops[
                    counter_drops["Count"] != 0
                ]
            )

            for timestamp in counter_drops[
                "timestamp"
            ]:
                counter_drop_summary[
                    "timestamps"
                ].add(timestamp)

        result = context.copy()

        result["events"] = quality_events
        result["clean_events"] = clean_events
        result["counter_drops"] = counter_drops

        result["previous_counts"] = (
            new_previous_counts
        )

        result["previous_timestamp"] = (
            new_previous_timestamp
        )

        result["quality_summary"] = (
            quality_summary
        )

        result["counter_drop_summary"] = (
            counter_drop_summary
        )

        return result