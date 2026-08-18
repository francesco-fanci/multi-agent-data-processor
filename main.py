from src.ingestion.loader import list_data_files, read_data_file
from src.cleaning.closure_detector import (detect_all_closures,detect_counter_drops)
from src.cleaning.event_classifier import classify_events
from src.cleaning.data_quality import add_quality_flags
from src.analytics.kpi import (calculate_cycle_speed,calculate_production_speed)
from src.analytics.torque import (update_torque_statistics,calculate_torque_results,update_daily_torque_statistics,calculate_daily_torque_results,calculate_torque_moving_average,detect_torque_drift)
from src.analytics.anomaly import (update_torque_anomalies)
from src.analytics.correlation import (calculate_head_correlations,calculate_head_residual_correlations,find_top_correlations)
from src.analytics.idle import (detect_idle_periods,finalize_idle_period)
from src.ingestion.validation import validate_dataframe
from src.config import (ANOMALY_IQR_MULTIPLIER,ANOMALY_MINIMUM_MARGIN,ANOMALY_MIN_EVENTS,DRIFT_WINDOW_DAYS,DRIFT_THRESHOLD,DRIFT_MIN_EVENTS,CORRELATION_MIN_EVENTS,CORRELATION_MIN_DAYS,IDLE_MIN_DURATION_SECONDS,IDLE_MAX_GAP_SECONDS,MOVING_AVERAGE_WINDOW_DAYS,COUNTER_RECOVERY_THRESHOLD,DATA_GAP_THRESHOLD_SECONDS)

zip_paths = [
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-02.zip",
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-03.zip",
    "data/raw/telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-04.zip"
]


previous_counts = {}
previous_timestamp = None
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
daily_torque_stats={}
anomaly_stats = {}

first_timestamp = None
last_timestamp = None

idle_state = None
idle_periods = []

total_counter_drops = 0
largest_counter_drop = None
counter_drops_to_zero = 0
counter_drops_not_zero = 0
counter_drop_timestamps = set()

for zip_path in zip_paths:

    print("\nProcessing zip:")
    print(zip_path)

    data_files = list_data_files(zip_path)

    for filename in data_files:

        print("\nProcessing:", filename)

        dataframe = read_data_file(
            zip_path,
            filename
        )

        validation_problems = validate_dataframe(
            dataframe
            )

        if len(validation_problems) > 0:
            print("Validation warnings:")

            for problem in validation_problems:
                print("-", problem)

        new_idle_periods, idle_state = (
            detect_idle_periods(
                dataframe,
                idle_state, 
                min_duration_seconds=IDLE_MIN_DURATION_SECONDS,
                max_gap_seconds=IDLE_MAX_GAP_SECONDS
            )
        )

        idle_periods.extend(
            new_idle_periods
        )
        
        counter_drops = detect_counter_drops(dataframe,previous_counts)

        total_counter_drops += len(counter_drops)

        if len(counter_drops) > 0:
            counter_drops_to_zero += len(counter_drops[counter_drops["Count"] == 0])
            counter_drops_not_zero += len(counter_drops[counter_drops["Count"] != 0])

            for timestamp in counter_drops["timestamp"]:
                counter_drop_timestamps.add(timestamp)

            current_largest_drop = counter_drops.loc[counter_drops["Count Difference"].idxmin()]

            if largest_counter_drop is None or current_largest_drop["Count Difference"] < largest_counter_drop["Count Difference"]:
                largest_counter_drop = current_largest_drop

        (closures,previous_counts,previous_timestamp) = detect_all_closures(dataframe,previous_counts,previous_timestamp)

        classified_events = classify_events(closures)

        classified_events = add_quality_flags(
            classified_events,
            counter_recovery_threshold=COUNTER_RECOVERY_THRESHOLD,
            data_gap_threshold_seconds=DATA_GAP_THRESHOLD_SECONDS
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

        update_daily_torque_statistics(
        daily_torque_stats,
        torque_events
    )
        update_torque_anomalies(
            anomaly_stats,
            torque_events,
            iqr_multiplier=ANOMALY_IQR_MULTIPLIER,
            minimum_margin=ANOMALY_MINIMUM_MARGIN,
            min_events=ANOMALY_MIN_EVENTS)

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
torque_results = calculate_torque_results(torque_stats)
daily_torque_results = calculate_daily_torque_results(daily_torque_stats)
daily_torque_results = calculate_torque_moving_average(daily_torque_results, window_days=MOVING_AVERAGE_WINDOW_DAYS)
torque_drift_results = detect_torque_drift(daily_torque_results, window_days=DRIFT_WINDOW_DAYS, threshold=DRIFT_THRESHOLD, min_events=DRIFT_MIN_EVENTS)
correlation_matrix = calculate_head_correlations(daily_torque_results, min_events=CORRELATION_MIN_EVENTS, min_days=CORRELATION_MIN_DAYS)       
residual_correlation_matrix = (calculate_head_residual_correlations(daily_torque_results, min_events=CORRELATION_MIN_EVENTS, min_days=CORRELATION_MIN_DAYS))
top_residual_correlations = find_top_correlations(residual_correlation_matrix,top_n=10)
final_idle_periods = finalize_idle_period(idle_state, min_duration_seconds=IDLE_MIN_DURATION_SECONDS)
idle_periods.extend(final_idle_periods)

total_idle_seconds = 0
longest_idle = None

for period in idle_periods:

    total_idle_seconds += (period["duration_seconds"])

    if (longest_idle is None or period["duration_seconds"] > longest_idle["duration_seconds"]):
        longest_idle = period

longest_idle_periods = sorted(idle_periods,key=lambda period: period["duration_seconds"],reverse=True)[:10]

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
        "Std:", round(stats["standard_deviation"], 4),
        "Min:", stats["min"],
        "Max:", stats["max"],
        "Zero:", stats["zero_count"],

    ) 

print("\n===========================")
print("DAILY TORQUE TREND - H01")
print("===========================")

for day in daily_torque_results["H01"]:
    print(
        day["date"],
        "Average:", round(day["average"], 4),
        "Moving Average:",
        round(day["moving_average"], 4),
        "Events:", day["count"]
    )

print("\n===========================")
print("TORQUE DRIFT - H01")
print("===========================")

for drift in torque_drift_results["H01"]:

    print(
        drift["date"],
        "Average:", round(drift["average"], 4),
        "Baseline:", round(drift["baseline"], 4),
        "Difference:", round(drift["difference"], 4),
        "Direction:", drift["direction"],
        "Events:", drift["events"]
    )

print("\n===========================")
print("TORQUE ANOMALIES")
print("===========================")

for head in sorted(anomaly_stats):

    stats = anomaly_stats[head]

    print(
        head,
        "Anomalies:", stats["count"],
        "Lowest:", stats["lowest_value"],
        "at:", stats["lowest_timestamp"],
        "Highest:", stats["highest_value"],
        "at:", stats["highest_timestamp"]
    )

print("\n===========================")
print("HEAD CORRELATIONS - H01")
print("===========================")

h01_correlations = correlation_matrix[
    "H01"
].drop("H01").dropna()

h01_correlations = h01_correlations.sort_values(
    ascending=False
)

for head, correlation in h01_correlations.items():

    print(
        head,
        "Correlation:",
        round(correlation, 4)
    )

print("\n===========================")
print("RESIDUAL CORRELATIONS - H01")
print("===========================")

h01_residual_correlations = (
    residual_correlation_matrix["H01"]
    .drop("H01")
    .dropna()
    .sort_values(ascending=False)
)

for head, correlation in h01_residual_correlations.items():

    print(
        head,
        "Correlation:",
        round(correlation, 4)
    )

print("\n===========================")
print("TOP RESIDUAL CORRELATIONS")
print("===========================")

for result in top_residual_correlations:

    print(
        result["head_1"],
        "-",
        result["head_2"],
        "Correlation:",
        round(result["correlation"], 4)
    )

print("\n===========================")
print("IDLE ANALYSIS")
print("===========================")

print("\nIdle periods:")
print(len(idle_periods))

print("\nTotal idle hours:")
print(
    round(
        total_idle_seconds / 3600,
        2
    )
)

if longest_idle is not None:

    print("\nLongest idle period:")
    print("Start:", longest_idle["start"])
    print("End:", longest_idle["end"])
    print(
        "Duration minutes:",
        round(
            longest_idle["duration_seconds"] / 60,
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
            period["duration_seconds"] / 60,
            2
        )
    )

print("\n===========================")
print("COUNTER DROP ANALYSIS")
print("===========================")

print("\nCounter drops:", total_counter_drops)
print("Unique drop timestamps:", len(counter_drop_timestamps))
print("Drops to zero:", counter_drops_to_zero)
print("Drops to non-zero value:", counter_drops_not_zero)

if largest_counter_drop is not None:
    print("\nLargest counter drop:")
    print("Timestamp:", largest_counter_drop["timestamp"])
    print("Head:", largest_counter_drop["Head"])
    print("Previous:", largest_counter_drop["Previous Count"])
    print("Current:", largest_counter_drop["Count"])
    print("Difference:", largest_counter_drop["Count Difference"])