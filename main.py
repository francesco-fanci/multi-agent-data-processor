import argparse
import os

from src.ingestion.cloud_sync import sync_from_cloud
from src.ingestion.loader import list_data_files
from src.logging_config import setup_logger
from src.agents.coordinator import MultiAgentCoordinator

logger = setup_logger()
coordinator = MultiAgentCoordinator()

parser = argparse.ArgumentParser(
    description="Industrial IoT data processing pipeline"
)

parser.add_argument(
    "--input",
    default="data/raw",
    help="Folder containing input ZIP files"
)

parser.add_argument(
    "--cloud-url",
    default="s3://arol-telemetry-bucket/raw",
    help="Cloud storage URL to pull raw datasets from"
)

parser.add_argument(
    "--sync-cloud",
    action="store_true",
    help="Enable synchronization from Cloud before processing"
)


args = parser.parse_args()

if args.sync_cloud:
    logger.info("Starting Cloud Data Synchronization...")
    sync_from_cloud(args.cloud_url, args.input)

if not os.path.isdir(args.input):
    parser.error(
        f"Input folder does not exist: {args.input}"
    )

zip_paths = []

for filename in os.listdir(args.input):

    if filename.lower().endswith(".zip"):
        zip_paths.append(
            os.path.join(
                args.input,
                filename
            )
        )

zip_paths.sort()

if len(zip_paths) == 0:
    parser.error(
        f"No ZIP files found in input folder: {args.input}"
    )


context = {
    "torque_stats": {},
    "daily_torque_stats": {},
    "anomaly_stats": {},
    "idle_periods": [],
    "total_cycles": 0,
    "success_metrics": {
        "overall": {},
        "by_head": {}
    }
}

total_raw_events = 0
total_clean_events = 0

total_valid = 0
total_counter_recovery = 0
total_data_gap = 0

max_count_difference = 0
events_with_difference_greater_than_one = 0
count_difference_distribution = {}
unknown_status_distribution = {}

total_counter_drops = 0
largest_counter_drop = None
counter_drops_to_zero = 0
counter_drops_not_zero = 0
counter_drop_timestamps = set()


logger.info("Pipeline started")


for zip_path in zip_paths:

    logger.info(
        "Processing zip: %s",
        zip_path
    )

    data_files = list_data_files(
        zip_path
    )

    for filename in data_files:

        logger.info(
            "Processing file: %s",
            filename
        )

        try:
            context = coordinator.process_file(
                zip_path,
                filename,
                context
            )

        except Exception as error:
            logger.error(
                "Unable to process %s - %s",
                filename,
                error
            )
            continue

        dataframe = context["dataframe"]

        validation_problems = context[
            "validation_problems"
        ]

        classified_events = context[
            "events"
        ]

        clean_events = context[
            "clean_events"
        ]

        counter_drops = context[
            "counter_drops"
        ]

        for problem in validation_problems:
            logger.warning(
                "%s - %s",
                filename,
                problem
            )

        total_counter_drops += len(
            counter_drops
        )

        if len(counter_drops) > 0:

            counter_drops_to_zero += len(
                counter_drops[
                    counter_drops["Count"] == 0
                ]
            )

            counter_drops_not_zero += len(
                counter_drops[
                    counter_drops["Count"] != 0
                ]
            )

            for timestamp in counter_drops[
                "timestamp"
            ]:
                counter_drop_timestamps.add(
                    timestamp
                )

            current_largest_drop = (
                counter_drops.loc[
                    counter_drops[
                        "Count Difference"
                    ].idxmin()
                ]
            )

            if (
                largest_counter_drop is None
                or current_largest_drop[
                    "Count Difference"
                ]
                < largest_counter_drop[
                    "Count Difference"
                ]
            ):
                largest_counter_drop = (
                    current_largest_drop
                )

        unknown_events = clean_events[
            clean_events["Event Type"]
            == "Unknown"
        ]

        for status in unknown_events[
            "Status"
        ]:

            status = int(status)

            if (
                status
                not in unknown_status_distribution
            ):
                unknown_status_distribution[
                    status
                ] = 0

            unknown_status_distribution[
                status
            ] += 1

        total_valid += len(
            classified_events[
                classified_events[
                    "Data Quality"
                ] == "Valid"
            ]
        )

        total_counter_recovery += len(
            classified_events[
                classified_events[
                    "Data Quality"
                ] == "Counter Recovery"
            ]
        )

        total_data_gap += len(
            classified_events[
                classified_events[
                    "Data Quality"
                ] == "Data Gap"
            ]
        )

        total_raw_events += len(
            classified_events
        )

        total_clean_events += len(
            clean_events
        )

        for difference in clean_events[
            "Count Difference"
        ]:

            difference = int(
                difference
            )

            if (
                difference
                not in count_difference_distribution
            ):
                count_difference_distribution[
                    difference
                ] = 0

            count_difference_distribution[
                difference
            ] += 1

        if len(clean_events) > 0:

            current_max = clean_events[
                "Count Difference"
            ].max()

            if (
                current_max
                > max_count_difference
            ):
                max_count_difference = (
                    current_max
                )

            events_with_difference_greater_than_one += len(
                clean_events[
                    clean_events[
                        "Count Difference"
                    ] > 1
                ]
            )

        for event_type, count in clean_events["Event Type"].value_counts().items():
            context["success_metrics"]["overall"][event_type] = context["success_metrics"]["overall"].get(event_type, 0) + count

        for (head, event_type), count in clean_events.groupby(["Head", "Event Type"]).size().items():
            if head not in context["success_metrics"]["by_head"]:
                context["success_metrics"]["by_head"][head] = {}
            context["success_metrics"]["by_head"][head][event_type] = context["success_metrics"]["by_head"][head].get(event_type, 0) + count

        logger.info(
            "%s - Rows: %d | Raw events: %d | Clean events: %d",
            filename,
            len(dataframe),
            len(classified_events),
            len(clean_events)
        )


context = coordinator.finalize(
    context
)

# Save context for BOT interface and remove heavy dataframes
if "dataframe" in context: del context["dataframe"]
if "events" in context: del context["events"]
if "clean_events" in context: del context["clean_events"]

import pickle
import os
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/context.pkl", "wb") as f:
    pickle.dump(context, f)
print("Context saved to data/processed/context.pkl for BOT interface.")



logger.info(
    "Pipeline completed successfully"
)