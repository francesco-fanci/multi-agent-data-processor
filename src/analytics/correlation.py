import pandas as pd

def calculate_head_correlations(daily_torque_results, min_events=500, min_days=10):
    rows=[]

    for head in daily_torque_results:
        for day in daily_torque_results[head]:

            if day["count"] < min_events:
                continue
            rows.append({"date": day["date"], "head": head, "average": day["average"]})

    data=pd.DataFrame(rows)

    if len(data) == 0:
        return pd.DataFrame()

    torque_table=data.pivot(index="date", columns="head", values="average")

    correlation_matrix=torque_table.corr(min_periods=min_days)


    return correlation_matrix

def calculate_head_residual_correlations(daily_torque_results,min_events=500,min_days=10):
    rows = []

    for head in daily_torque_results:

        for day in daily_torque_results[head]:

            if day["count"] < min_events:
                continue

            rows.append({"date": day["date"],"head": head,"average": day["average"]})

    data = pd.DataFrame(rows)

    if len(data) == 0:
        return pd.DataFrame()

    torque_table = data.pivot(index="date",columns="head",values="average")

    daily_machine_average = (torque_table.mean(axis=1))

    residual_table = torque_table.sub(daily_machine_average,axis=0)

    correlation_matrix = residual_table.corr(min_periods=min_days)

    return correlation_matrix

def find_top_correlations(correlation_matrix,top_n=10):
    correlations = []

    heads = correlation_matrix.columns

    for i in range(len(heads)):
        for j in range(i + 1, len(heads)):

            head_1 = heads[i]
            head_2 = heads[j]

            correlation = correlation_matrix.loc[head_1,head_2]

            if pd.isna(correlation):
                continue

            correlations.append({"head_1": head_1,"head_2": head_2,"correlation": correlation})

    correlations.sort(key=lambda item: abs(item["correlation"]),reverse=True)

    return correlations[:top_n]