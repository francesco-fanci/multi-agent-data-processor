def add_quality_flags(events,counter_recovery_threshold=100,data_gap_threshold_seconds=5):
    data = events.copy()

    data["Data Quality"] = "Valid"

    counter_recovery = ((data["Previous Count"] == 0) & (data["Count Difference"] > counter_recovery_threshold))

    data.loc[counter_recovery,"Data Quality"] = "Counter Recovery"

    data_gap = ((data["Time Difference"] > data_gap_threshold_seconds) & (~counter_recovery))

    data.loc[data_gap,"Data Quality"] = "Data Gap"

    return data