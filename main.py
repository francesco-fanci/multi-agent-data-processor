import argparse
import os

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

args = parser.parse_args()

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
    "total_production_pieces": 0
}

total_raw_events = 0
total_clean_events = 0

total_closure_ok = 0
total_no_load = 0
total_bad_closure = 0
total_unknown = 0

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

        closure_ok = clean_events[
            clean_events["Event Type"]
            == "Closure OK"
        ]

        no_load = clean_events[
            clean_events["Event Type"]
            == "No Load"
        ]

        bad_closure = clean_events[
            clean_events["Event Type"]
            == "Bad Closure"
        ]

        unknown = clean_events[
            clean_events["Event Type"]
            == "Unknown"
        ]

        total_closure_ok += len(
            closure_ok
        )

        total_no_load += len(
            no_load
        )

        total_bad_closure += len(
            bad_closure
        )

        total_unknown += len(
            unknown
        )

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

total_cycles = context[
    "total_cycles"
]

total_production_pieces = context[
    "total_production_pieces"
]

cycle_speed = context[
    "cycle_speed"
]

production_speed = context[
    "production_speed"
]

first_timestamp = context[
    "first_timestamp"
]

last_timestamp = context[
    "last_timestamp"
]

torque_results = context[
    "torque_results"
]

daily_torque_results = context[
    "daily_torque_results"
]

torque_drift_results = context[
    "drift_results"
]

anomaly_stats = context[
    "anomaly_stats"
]

correlation_matrix = context[
    "correlation_matrix"
]

residual_correlation_matrix = context[
    "residual_correlation_matrix"
]

top_residual_correlations = context[
    "top_residual_correlations"
]

idle_periods = context[
    "idle_periods"
]


total_idle_seconds = 0
longest_idle = None

for period in idle_periods:

    total_idle_seconds += (
        period["duration_seconds"]
    )

    if (
        longest_idle is None
        or period["duration_seconds"]
        > longest_idle["duration_seconds"]
    ):
        longest_idle = period

longest_idle_periods = sorted(
    idle_periods,
    key=lambda period: period[
        "duration_seconds"
    ],
    reverse=True
)[:10]


print("\n===========================")
print("FINAL RESULTS")
print("===========================")

print("\nRaw events:")
print(total_raw_events)

print("\nClean events:")
print(total_clean_events)

print("\nTotal counter increments:")
print(total_cycles)

print("\nClosure OK:")
print(total_closure_ok)

print("\nNo Load:")
print(total_no_load)

print("\nBad Closure:")
print(total_bad_closure)

print("\nProduction pieces:")
print(total_production_pieces)

print("\nCycle speed:")
print(cycle_speed)

print("\nProduction speed:")
print(production_speed)

print("\nFirst timestamp:")
print(first_timestamp)

print("\nLast timestamp:")
print(last_timestamp)


print("\n===========================")
print("DATA QUALITY")
print("===========================")

print("\nValid:")
print(total_valid)

print("\nCounter Recovery:")
print(total_counter_recovery)

print("\nData Gap:")
print(total_data_gap)


print("\n===========================")
print("COUNT DIFFERENCE ANALYSIS")
print("===========================")

print("\nMaximum Count Difference:")
print(max_count_difference)

print("\nEvents with Count Difference > 1:")
print(
    events_with_difference_greater_than_one
)

print("\nCount Difference distribution:")

for difference in sorted(
    count_difference_distribution.keys()
)[:20]:

    print(
        difference,
        "->",
        count_difference_distribution[
            difference
        ]
    )


print("\nLargest Count Difference values:")

largest_differences = sorted(
    count_difference_distribution.keys(),
    reverse=True
)[:20]

for difference in largest_differences:

    print(
        difference,
        "->",
        count_difference_distribution[
            difference
        ]
    )


print("\n===========================")
print("UNKNOWN STATUS")
print("===========================")

print("\nUnknown events:")
print(
    sum(
        unknown_status_distribution.values()
    )
)

print("\nStatus values:")

for status in sorted(
    unknown_status_distribution.keys()
):

    print(
        status,
        "->",
        unknown_status_distribution[
            status
        ]
    )

print("\nUnknown:")
print(total_unknown)


print("\n===========================")
print("TORQUE ANALYSIS")
print("===========================")

for head in sorted(
    torque_results
):

    stats = torque_results[
        head
    ]

    print(
        head,
        "Events:",
        stats["count"],
        "Average:",
        stats["average"],
        "Std:",
        round(
            stats["standard_deviation"],
            4
        ),
        "Min:",
        stats["min"],
        "Max:",
        stats["max"],
        "Zero:",
        stats["zero_count"]
    )


print("\n===========================")
print("DAILY TORQUE TREND - H01")
print("===========================")

for day in daily_torque_results[
    "H01"
]:

    print(
        day["date"],
        "Average:",
        round(
            day["average"],
            4
        ),
        "Moving Average:",
        round(
            day["moving_average"],
            4
        ),
        "Events:",
        day["count"]
    )


print("\n===========================")
print("TORQUE DRIFT - H01")
print("===========================")

for drift in torque_drift_results[
    "H01"
]:

    print(
        drift["date"],
        "Average:",
        round(
            drift["average"],
            4
        ),
        "Baseline:",
        round(
            drift["baseline"],
            4
        ),
        "Difference:",
        round(
            drift["difference"],
            4
        ),
        "Direction:",
        drift["direction"],
        "Events:",
        drift["events"]
    )


print("\n===========================")
print("TORQUE ANOMALIES")
print("===========================")

for head in sorted(
    anomaly_stats
):

    stats = anomaly_stats[
        head
    ]

    print(
        head,
        "Anomalies:",
        stats["count"],
        "Lowest:",
        stats["lowest_value"],
        "at:",
        stats["lowest_timestamp"],
        "Highest:",
        stats["highest_value"],
        "at:",
        stats["highest_timestamp"]
    )


print("\n===========================")
print("HEAD CORRELATIONS - H01")
print("===========================")

h01_correlations = correlation_matrix[
    "H01"
].drop(
    "H01"
).dropna()

h01_correlations = (
    h01_correlations.sort_values(
        ascending=False
    )
)

for head, correlation in (
    h01_correlations.items()
):

    print(
        head,
        "Correlation:",
        round(
            correlation,
            4
        )
    )


print("\n===========================")
print("RESIDUAL CORRELATIONS - H01")
print("===========================")

h01_residual_correlations = (
    residual_correlation_matrix[
        "H01"
    ]
    .drop("H01")
    .dropna()
    .sort_values(
        ascending=False
    )
)

for head, correlation in (
    h01_residual_correlations.items()
):

    print(
        head,
        "Correlation:",
        round(
            correlation,
            4
        )
    )


print("\n===========================")
print("TOP RESIDUAL CORRELATIONS")
print("===========================")

for result in (
    top_residual_correlations
):

    print(
        result["head_1"],
        "-",
        result["head_2"],
        "Correlation:",
        round(
            result["correlation"],
            4
        )
    )


print("\n===========================")
print("IDLE ANALYSIS")
print("===========================")

print("\nIdle periods:")
print(
    len(
        idle_periods
    )
)

print("\nTotal idle hours:")
print(
    round(
        total_idle_seconds / 3600,
        2
    )
)

if longest_idle is not None:

    print("\nLongest idle period:")

    print(
        "Start:",
        longest_idle["start"]
    )

    print(
        "End:",
        longest_idle["end"]
    )

    print(
        "Duration minutes:",
        round(
            longest_idle[
                "duration_seconds"
            ] / 60,
            2
        )
    )


print("\nTop 10 longest idle periods:")

for period in longest_idle_periods:

    print(
        "Start:",
        period["start"],
        "End:",
        period["end"],
        "Minutes:",
        round(
            period[
                "duration_seconds"
            ] / 60,
            2
        )
    )


print("\n===========================")
print("COUNTER DROP ANALYSIS")
print("===========================")

print(
    "\nCounter drops:",
    total_counter_drops
)

print(
    "Unique drop timestamps:",
    len(
        counter_drop_timestamps
    )
)

print(
    "Drops to zero:",
    counter_drops_to_zero
)

print(
    "Drops to non-zero value:",
    counter_drops_not_zero
)

if largest_counter_drop is not None:

    print("\nLargest counter drop:")

    print(
        "Timestamp:",
        largest_counter_drop[
            "timestamp"
        ]
    )

    print(
        "Head:",
        largest_counter_drop[
            "Head"
        ]
    )

    print(
        "Previous:",
        largest_counter_drop[
            "Previous Count"
        ]
    )

    print(
        "Current:",
        largest_counter_drop[
            "Count"
        ]
    )

    print(
        "Difference:",
        largest_counter_drop[
            "Count Difference"
        ]
    )


report = context["report"]

print("\n===========================")
print("MULTI-AGENT REPORT")
print("===========================")

print("\nGOAL")
print(report["goal"])

print("\nDATA")

for key, value in report["data"].items():
    print(
        key,
        ":",
        value
    )

print("\nANALYSES")

for analysis in report["analyses"]:
    print(
        "-",
        analysis
    )

print("\nFINDINGS")

for key, value in report["findings"].items():

    if key in [
        "top_correlations",
        "top_residual_correlations"
    ]:
        continue

    print(
        key,
        ":",
        value
    )

print("\nTOP CORRELATIONS")

for correlation in report[
    "findings"
]["top_correlations"]:

    print(
        correlation["head_1"],
        "-",
        correlation["head_2"],
        ":",
        round(
            correlation["correlation"],
            4
        )
    )

print("\nTOP RESIDUAL CORRELATIONS")

for correlation in report[
    "findings"
]["top_residual_correlations"]:

    print(
        correlation["head_1"],
        "-",
        correlation["head_2"],
        ":",
        round(
            correlation["correlation"],
            4
        )
    )

print("\nCONFIDENCE AND LIMITS")

for item in report[
    "confidence_and_limits"
]:
    print(
        "-",
        item
    )

print("\nNEXT CHECKS")

for item in report[
    "next_checks"
]:
    print(
        "-",
        item
    )

logger.info(
    "Pipeline completed successfully"
)