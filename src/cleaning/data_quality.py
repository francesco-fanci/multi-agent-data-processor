def add_quality_flags(events):
    data = events.copy()

    data["Data Quality"] = "Valid"

    counter_recovery = (
        (data["Previous Count"] == 0)
        & (data["Count Difference"] > 100)
    )

    data.loc[
        counter_recovery,
        "Data Quality"
    ] = "Counter Recovery"

    data_gap = (
        (data["Time Difference"] > 5)
        & (~counter_recovery)
    )

    data.loc[
        data_gap,
        "Data Quality"
    ] = "Data Gap"

    return data