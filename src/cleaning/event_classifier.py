def classify_events(events):
    classified_events=events.copy()

    classified_events["Event Type"] = "Unknown"

    status_map = {
        0: "Closure OK",
        2: "No Load",
        3: "Failing to reach first torque threshold",
        4: "No Closure",
        5: "Failing to reach final torque",
        8: "No InTorque",
        9: "Closure Head raises before TimeInTorque",
        16: "No CapTurns",
        17: "Cap closed but with less degrees",
        32: "Following Error",
        33: "Tracking error",
        64: "Bad Closure",
        65: "ClosureTorque reached but cap still rotating"
    }

    classified_events["Event Type"] = classified_events["Status"].map(status_map).fillna("Unknown")

    return classified_events
    