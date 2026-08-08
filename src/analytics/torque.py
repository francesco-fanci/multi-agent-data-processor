def update_torque_statistics(torque_stats, events):

    for number in range(1, 37):
        head = f"H{number:02d}"

        head_events = events[
            events["Head"] == head
        ]

        torque_values = head_events[
            "AppTorque"
        ].dropna()

        if len(torque_values) == 0:
            continue

        if head not in torque_stats:
            torque_stats[head] = {
                "count": 0,
                "sum": 0.0,
                "min": None,
                "max": None,
                "zero_count": 0
            }

        torque_stats[head]["count"] += len(torque_values)

        torque_stats[head]["sum"] += (
            torque_values.sum()
        )

        torque_stats[head]["zero_count"] += (
            torque_values == 0
        ).sum()

        current_min = torque_values.min()
        current_max = torque_values.max()

        if (
            torque_stats[head]["min"] is None
            or current_min < torque_stats[head]["min"]
        ):
            torque_stats[head]["min"] = current_min

        if (
            torque_stats[head]["max"] is None
            or current_max > torque_stats[head]["max"]
        ):
            torque_stats[head]["max"] = current_max


def calculate_torque_results(torque_stats):

    results = {}

    for head in torque_stats:

        count = torque_stats[head]["count"]

        if count == 0:
            average = 0.0
        else:
            average = (
                torque_stats[head]["sum"]
                / count
            )

        results[head] = {
            "count": count,
            "average": average,
            "min": torque_stats[head]["min"],
            "max": torque_stats[head]["max"],
            "zero_count": torque_stats[head]["zero_count"]
        }

    return results