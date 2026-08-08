import pandas as pd

def calculate_capping_speed(events):
    data=events.copy()

    data["timestamp"]= pd.to_datetime(data["timestamp"])

    data=data.sort_values("timestamp").reset_index(drop=True)

    data["Cumulative Pieces"]=data["Count Difference"].cumsum()

    start_time=data["timestamp"].iloc[0]

    data["Elapsed Seconds"]=(data["timestamp"] - start_time).dt.total_seconds()

    data["Capping Speed"] = 0.0

    valid_rows=data["Elapsed Seconds"] > 0

    data.loc[valid_rows, "Capping Speed"] = (data.loc[valid_rows, "Cumulative Pieces"] / data.loc[valid_rows, "Elapsed Seconds"] * 3600)

    return data


    
def calculate_production_speed(events):
    data=events.copy()

    data["timestamp"]= pd.to_datetime(data["timestamp"])

    data=data.sort_values("timestamp").reset_index(drop=True)

    data["Production Pieces"]=data["Count Difference"]

    data.loc[data["Event Type"] == "No Load", "Production Pieces"] = 0

    data["Cumulative Production Pieces"] = ( data["Production Pieces"]).cumsum()

    start_time=data["timestamp"].iloc[0]

    data["Elapsed Seconds"] = (data["timestamp"] - start_time).dt.total_seconds()

    data["Production Speed"] = 0.0

    valid_rows=data["Elapsed Seconds"] > 0

    data.loc[valid_rows, "Production Speed"] = (data.loc[valid_rows, "Cumulative Production Pieces"] / data.loc[valid_rows, "Elapsed Seconds"]* 3600)

    return data

    