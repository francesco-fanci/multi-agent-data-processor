def classify_events(events):
    classified_events=events.copy()

    classified_events["Event Type"] = "Unknown"

    classified_events.loc[classified_events["Status"]==0, "Event Type"] = "Closure OK"

    classified_events.loc[classified_events["Status"]==2, "Event Type"] = "No Load"

    classified_events.loc[classified_events["Status"]==65, "Event Type"] = "Bad Closure"

    return classified_events
    