import pandas as pd


def detect_closures(dataframe, head):
    count_column=head + " Count"
    torque_column=head + " AppTorque"
    status_column=head + " Status"

    required_columns=["timestamp", count_column, torque_column, status_column]

    for column in required_columns:
        if column not in dataframe.columns:
            raise ValueError("Missing required column: " + column)

    data=dataframe[required_columns].copy()

    data["Previous Count"]=data[count_column].shift(1)

    data["Count Difference"]=data[count_column] - data["Previous Count"]

    closures=data[data["Count Difference"] > 0].copy()

    closures["Head"]=head

    closures=closures.rename(columns={count_column: "Count", torque_column: "AppTorque", status_column: "Status"})

    closures=closures[["timestamp", "Head", "Count", "AppTorque", "Status", "Previous Count", "Count Difference"]]

    return closures

def detect_all_closures(dataframe):
    all_closures=[]
    for number in range(1,37):
        head = f"H{number:02d}"

        closures=detect_closures(dataframe, head)
        all_closures.append(closures)
    
    result=pd.concat(all_closures, ignore_index=True)

    result=result.sort_values(by=["timestamp", "Head"]).reset_index(drop=True)
    return result 