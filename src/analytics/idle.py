import pandas as pd


def detect_idle_periods(dataframe,idle_state=None,min_duration_seconds=60,max_gap_seconds=2):

    if idle_state is None:
        idle_state = {"start": None,"last": None}

    data = dataframe.copy()

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    status_columns = [col for col in data.columns if col.startswith("H") and col[1:3].isdigit() and col.endswith(" Status")]

    for column in status_columns:
        if column not in data.columns:
            raise ValueError("Missing required column: " + column)

    all_no_load = (data[status_columns] == 2).all(axis=1)

    idle_periods = []

    for timestamp, is_idle in zip(data["timestamp"],all_no_load):

        if is_idle:

            if idle_state["start"] is None:
                idle_state["start"] = timestamp
                idle_state["last"] = timestamp

            else:
                gap = (timestamp- idle_state["last"]).total_seconds()

                if gap <= max_gap_seconds:
                    idle_state["last"] = timestamp

                else:
                    duration = (idle_state["last"] - idle_state["start"]).total_seconds()

                    if duration >= min_duration_seconds:
                        idle_periods.append({"start": idle_state["start"],"end": idle_state["last"],"duration_seconds": duration})

                    idle_state["start"] = timestamp
                    idle_state["last"] = timestamp

        else:

            if idle_state["start"] is not None:

                duration = (idle_state["last"]- idle_state["start"]).total_seconds()

                if duration >= min_duration_seconds:
                    idle_periods.append({"start": idle_state["start"],"end": idle_state["last"],"duration_seconds": duration})

                idle_state["start"] = None
                idle_state["last"] = None

    return idle_periods, idle_state


def finalize_idle_period(idle_state,min_duration_seconds=60):

    idle_periods = []

    if idle_state["start"] is None:
        return idle_periods

    duration = (idle_state["last"] - idle_state["start"]).total_seconds()

    if duration >= min_duration_seconds:
        idle_periods.append({"start": idle_state["start"],"end": idle_state["last"],"duration_seconds": duration})

    return idle_periods