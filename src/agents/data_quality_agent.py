from src.agents.base_agent import BaseAgent

from src.cleaning.closure_detector import (detect_all_closures,detect_counter_drops)

from src.cleaning.event_classifier import (
    classify_events)

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

        return result