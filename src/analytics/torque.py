from datetime import timedelta
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

def update_daily_torque_statistics(daily_stats, events):
    data=events.copy()
    data["Date"]=data["timestamp"].dt.date

    for number in range(1,37):
        head=f"H{number:02d}"

        head_events=data[data["Head"] == head]

        if len(head_events) ==0:
            continue
        daily_values=head_events.groupby("Date")["AppTorque"].agg(["sum", "count"])

        for date, row in daily_values.iterrows():
            key=(head,date)

            if key not in daily_stats:
                daily_stats[key]={"sum": 0.0, "count": 0}

            daily_stats[key]["sum"]+= row["sum"]
            daily_stats[key]["count"]+= int(row["count"])

def calculate_daily_torque_results(daily_stats):

    results={}

    for key in daily_stats:
        head, date= key

        total_sum=daily_stats[key]["sum"]
        count=daily_stats[key]["count"]

        average=total_sum/count

        if head not in results:
            results[head]=[]

        results[head].append({"date": date, "average": average, "count": count})

    for head in results:
        results[head].sort(key=lambda item: item["date"])
    
    return results

def calculate_torque_moving_average(daily_torque_results, window_days=7):
    for head in daily_torque_results:
        days=daily_torque_results[head]

        for current_day in days:

            current_date = current_day["date"]

            start_date = (current_date - timedelta(days=window_days-1))

            total_sum = 0.0
            total_count = 0

            for day in days: 
                if (day["date"]>=start_date and day["date"]<=current_date):

                    total_sum+=(day["average"]*day["count"])

                    total_count+=day["count"]

            if total_count == 0:
                moving_average = 0.0
            else:
               moving_average=(total_sum/total_count)

            current_day["moving_average"]= (moving_average)
    return daily_torque_results

def detect_torque_drift(daily_torque_results, window_days=7, threshold=0.1, min_events=500):
    drift_results={}

    for head in daily_torque_results:
        days=daily_torque_results[head]

        drift_results[head]=[]

        for current_day in days:
            if current_day["count"]<min_events:
                continue

            current_date=current_day["date"]

            start_date=(current_date - timedelta(days=window_days))

            total_sum=0.0
            total_count = 0

            for day in days:

                if(day["date"]>=start_date and day["date"] < current_date):

                    total_sum+=(day["average"]*day["count"])

                    total_count +=day["count"]
            
            if total_count < min_events:
                continue
            baseline = (total_sum / total_count)

            difference = (current_day["average"] - baseline)

            if abs(difference) >=threshold:
                if difference > 0:
                    direction = "Increase"
                else:
                    direction = "Decrease"
                
                drift_results[head].append(
                     {
                        "date": current_date,
                        "average": current_day["average"],
                        "baseline": baseline,
                        "difference": difference,
                        "direction": direction,
                        "events": current_day["count"]
                    }
                )
    return drift_results