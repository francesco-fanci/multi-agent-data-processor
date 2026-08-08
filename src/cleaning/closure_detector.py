import pandas as pd

def detect_closures(dataframe, head, previous_count=None):
    count_column=head + " Count"
    torque_column=head + " AppTorque"
    status_column=head + " Status"

    required_columns=["timestamp", count_column, torque_column, status_column]

    for column in required_columns:
        if column not in dataframe.columns:
            raise ValueError("Missing required column: " + column)

    data=dataframe[required_columns].copy()

    data["Previous Count"]=data[count_column].shift(1)
    data["Previous Timestamp"] = data["timestamp"].shift(1)

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data["Previous Timestamp"] = pd.to_datetime(
        data["Previous Timestamp"]
    )

    if previous_count is not None:
        data.loc[data.index[0], "Previous Count"]=previous_count

    data["Count Difference"]=data[count_column] - data["Previous Count"]

    data["Time Difference"] = (
    data["timestamp"] - data["Previous Timestamp"]).dt.total_seconds()

    closures=data[data["Count Difference"] > 0].copy()

    closures["Head"]=head

    closures=closures.rename(columns={count_column: "Count", torque_column: "AppTorque", status_column: "Status"})

    closures=closures[["timestamp", "Head", "Count", "AppTorque", "Status", "Previous Count", "Count Difference", "Previous Timestamp", "Time Difference"]]

    return closures

def detect_all_closures(dataframe, previous_counts=None):
    all_closures=[]

    if previous_counts is None:
        previous_counts = {}

    new_previous_counts={}

    for number in range(1,37):
        head = f"H{number:02d}"

        previous_count=previous_counts.get(head)

        closures=detect_closures(dataframe, head, previous_count)

        all_closures.append(closures)

        count_column=head + " Count"

        new_previous_counts[head]=dataframe[count_column].iloc[-1]
    
    result=pd.concat(all_closures, ignore_index=True)

    result=result.sort_values(by=["timestamp", "Head"]).reset_index(drop=True)
    return result, new_previous_counts