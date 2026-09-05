def update_torque_anomalies(anomaly_stats, events, iqr_multiplier=3.0, minimum_margin=0.05, min_events=100):
    heads = events["Head"].unique()
    for head in heads:

        if head not in anomaly_stats:
            anomaly_stats[head] = {"count": 0,"lowest_value": None,"lowest_timestamp": None,"highest_value": None,"highest_timestamp": None,}
        head_events=events[events["Head"]==head]

        torque_values=head_events["AppTorque"].dropna()

        if len(torque_values) < min_events:
            continue

        q1=torque_values.quantile(0.25)
        q3=torque_values.quantile(0.75)

        iqr=q3-q1

        margin = max(    iqr_multiplier * iqr, minimum_margin)

        lower_limit = q1 - margin
        upper_limit = q3 + margin

        anomalies = head_events[(head_events["AppTorque"]< lower_limit)| (head_events["AppTorque"] > upper_limit)]

        if len(anomalies) == 0:
            continue

        anomaly_stats[head]["count"]+=len(anomalies)

        lowest_row=anomalies.loc[anomalies["AppTorque"].idxmin()]

        
        highest_row=anomalies.loc[anomalies["AppTorque"].idxmax()]

        lowest_value = lowest_row["AppTorque"]
        highest_value = highest_row["AppTorque"]

        if (anomaly_stats[head]["lowest_value"] is None or lowest_value < anomaly_stats[head]["lowest_value"]):
            anomaly_stats[head]["lowest_value"] = (lowest_value)

            anomaly_stats[head]["lowest_timestamp"] =  (lowest_row["timestamp"])

        if (anomaly_stats[head]["highest_value"] is None or highest_value > anomaly_stats[head]["highest_value"]):
            anomaly_stats[head]["highest_value"] = (highest_value)

            anomaly_stats[head]["highest_timestamp"] = (highest_row["timestamp"])