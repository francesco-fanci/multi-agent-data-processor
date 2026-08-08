from src.ingestion.loader import list_csv_files, read_csv_file
from src.cleaning.closure_detector import detect_all_closures
from src.cleaning.event_classifier import classify_events
from src.cleaning.data_quality import add_quality_flags
from src.analytics.kpi import (
    calculate_cycle_speed,
    calculate_production_speed
)
from src.analytics.torque import (
    update_torque_statistics,
    calculate_torque_results
)

zip_paths = [
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-02.zip",
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-03.zip",
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-04.zip"
]


previous_counts = {}

total_raw_events = 0
total_clean_events = 0

total_cycles = 0
total_production_pieces = 0

total_closure_ok = 0
total_no_load = 0
total_bad_closure = 0

total_valid = 0
total_counter_recovery = 0
total_data_gap = 0

max_count_difference = 0
events_with_difference_greater_than_one = 0
count_difference_distribution = {}
unknown_status_distribution = {}
total_unknown = 0
torque_stats={}

first_timestamp = None
last_timestamp = None


for zip_path in zip_paths:

    print("\nProcessing zip:")
    print(zip_path)

    csv_files = list_csv_files(zip_path)

    for csv_name in csv_files:

        print("\nProcessing:", csv_name)

        dataframe = read_csv_file(
            zip_path,
            csv_name
        )

        closures, previous_counts = detect_all_closures(
            dataframe,
            previous_counts
        )

        classified_events = classify_events(closures)

        classified_events = add_quality_flags(
            classified_events
        )

        valid_events = classified_events[
        classified_events["Data Quality"] == "Valid"
    ]

        torque_events = valid_events[
            valid_events["Event Type"].isin(
                ["Closure OK", "Bad Closure"]
            )
        ]

        update_torque_statistics(
            torque_stats,
            torque_events
        )

        clean_events = classified_events[
            classified_events["Data Quality"] != "Counter Recovery"
        ]

        unknown_events = clean_events[
        clean_events["Event Type"] == "Unknown"
    ]

        for status in unknown_events["Status"]:
            status = int(status)

            if status not in unknown_status_distribution:
                unknown_status_distribution[status] = 0

            unknown_status_distribution[status] += 1

        total_valid += len(
            classified_events[
                classified_events["Data Quality"] == "Valid"
            ]
        )

        total_counter_recovery += len(
            classified_events[
                classified_events["Data Quality"] == "Counter Recovery"
            ]
        )

        total_data_gap += len(
            classified_events[
                classified_events["Data Quality"] == "Data Gap"
            ]
        )

        total_raw_events += len(classified_events)
        total_clean_events += len(clean_events)

        for difference in clean_events["Count Difference"]:

            difference = int(difference)

            if difference not in count_difference_distribution:
                count_difference_distribution[difference] = 0

            count_difference_distribution[difference] += 1

        if len(clean_events) > 0:

            current_max = clean_events["Count Difference"].max()

            if current_max > max_count_difference:
                max_count_difference = current_max

            events_with_difference_greater_than_one += len(
                clean_events[
                    clean_events["Count Difference"] > 1
                ]
            )

        print("Rows:", len(dataframe))
        print("Raw events:", len(classified_events))
        print("Clean events:", len(clean_events))

        total_cycles += clean_events[
            "Count Difference"
        ].sum()

        closure_ok = clean_events[
            clean_events["Event Type"] == "Closure OK"
        ]

        total_closure_ok += len(closure_ok)

        no_load = clean_events[
            clean_events["Event Type"] == "No Load"
        ]

        total_no_load += len(no_load)

        bad_closure = clean_events[
            clean_events["Event Type"] == "Bad Closure"
        ]

        unknown = clean_events[
        clean_events["Event Type"] == "Unknown"
        ]

        total_unknown += len(unknown)

        total_bad_closure += len(bad_closure)

        production_events = clean_events[
        clean_events["Event Type"].isin(
            ["Closure OK", "Bad Closure"]
        )
    ]

        total_production_pieces += production_events[
            "Count Difference"
        ].sum()

        if len(clean_events) > 0:

            current_first = clean_events[
                "timestamp"
            ].iloc[0]

            current_last = clean_events[
                "timestamp"
            ].iloc[-1]

            if first_timestamp is None:
                first_timestamp = current_first

            last_timestamp = current_last
        cycle_speed=calculate_cycle_speed(total_cycles, first_timestamp, last_timestamp)
        production_speed=calculate_production_speed(total_production_pieces, first_timestamp, last_timestamp)
        torque_results = calculate_torque_results(
        torque_stats
    )

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
print(events_with_difference_greater_than_one)

print("\nCount Difference distribution:")

for difference in sorted(
    count_difference_distribution.keys()
)[:20]:

    print(
        difference,
        "->",
        count_difference_distribution[difference]
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
        count_difference_distribution[difference]
    )

print("\n===========================")
print("UNKNOWN STATUS")
print("===========================")

print("\nUnknown events:")
print(sum(unknown_status_distribution.values()))

print("\nStatus values:")

for status in sorted(unknown_status_distribution.keys()):
    print(
        status,
        "->",
        unknown_status_distribution[status]
    )

print("\nUnknown:")
print(total_unknown)

print("\n===========================")
print("TORQUE ANALYSIS")
print("===========================")

for head in sorted(torque_results):
    stats = torque_results[head]

    print(
        head,
        "Events:", stats["count"],
        "Average:", stats["average"],
        "Min:", stats["min"],
        "Max:", stats["max"],
        "Zero:", stats["zero_count"],

    )