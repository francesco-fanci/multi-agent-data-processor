import pandas as pd

def detect_closures(dataframe, head, previous_count=None, previous_timestamp=None):
    count_column=head + " Count"
    torque_column=head + " AppTorque"
    status_column=head + " Status"

    required_columns=["timestamp", count_column, torque_column, status_column]

    for column in required_columns:
        if column not in dataframe.columns:
            raise ValueError("Missing required column: " + column)

    data=dataframe[required_columns].copy()
    data = data.dropna(subset=[count_column]).copy()

    data["Previous Count"]=data[count_column].shift(1)
    data["Previous Timestamp"] = data["timestamp"].shift(1)

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data["Previous Timestamp"] = pd.to_datetime(
        data["Previous Timestamp"]
    )

    if len(data) > 0:
        if previous_count is not None:
            data.loc[data.index[0], "Previous Count"] = (previous_count)

        if previous_timestamp is not None:
            data.loc[data.index[0], "Previous Timestamp"] = (previous_timestamp)

    data["Count Difference"]=data[count_column] - data["Previous Count"]

    data["Time Difference"] = (
    data["timestamp"] - data["Previous Timestamp"]).dt.total_seconds()

    closures=data[data["Count Difference"] > 0].copy()

    closures["Head"]=head

    closures=closures.rename(columns={count_column: "Count", torque_column: "AppTorque", status_column: "Status"})

    closures=closures[["timestamp", "Head", "Count", "AppTorque", "Status", "Previous Count", "Count Difference", "Previous Timestamp", "Time Difference"]]

    return closures

def detect_all_closures(dataframe, previous_counts=None, previous_timestamp=None):
    all_closures=[]

    if previous_counts is None:
        previous_counts = {}

    new_previous_counts={}

    heads = sorted(list(set(col[:3] for col in dataframe.columns if col.startswith("H") and col[1:3].isdigit() and col[3:4] == " ")))
    for head in heads:

        previous_count=previous_counts.get(head)

        closures=detect_closures(dataframe, head, previous_count, previous_timestamp)

        all_closures.append(closures)

        count_column=head + " Count"

        valid_counts = dataframe[count_column].dropna()

        if len(valid_counts) > 0:
            new_previous_counts[head] = (valid_counts.iloc[-1])
        else:
            new_previous_counts[head] = (previous_count)
    
    result=pd.concat(all_closures, ignore_index=True)

    result=result.sort_values(by=["timestamp", "Head"]).reset_index(drop=True)
    
    new_previous_timestamp = pd.to_datetime(dataframe["timestamp"].iloc[-1])

    return (result,new_previous_counts,new_previous_timestamp)

def detect_counter_drops(dataframe,previous_counts=None):
    counter_drops = []

    if previous_counts is None:
        previous_counts = {}

    heads = sorted(list(set(col[:3] for col in dataframe.columns if col.startswith("H") and col[1:3].isdigit() and col[3:4] == " ")))
    for head in heads:
        count_column = head + " Count"

        data = dataframe[["timestamp", count_column]].copy()
        data = data.dropna(subset=[count_column]).copy()

        data["Previous Count"] = (data[count_column].shift(1))

        previous_count = previous_counts.get(head)

        if len(data) > 0 and previous_count is not None:
            data.loc[data.index[0],"Previous Count"] = previous_count

        data["Count Difference"] = (data[count_column] - data["Previous Count"])

        drops = data[data["Count Difference"] < 0].copy()

        if len(drops) == 0:
            continue

        drops["Head"] = head

        drops = drops.rename(columns={count_column: "Count"})

        drops = drops[["timestamp","Head","Count","Previous Count","Count Difference"]]

        counter_drops.append(drops)

    if len(counter_drops) == 0:
        return pd.DataFrame(columns=["timestamp","Head","Count","Previous Count","Count Difference"])

    result = pd.concat(counter_drops,ignore_index=True)

    result = result.sort_values(by=["timestamp", "Head"]).reset_index(drop=True)

    return result