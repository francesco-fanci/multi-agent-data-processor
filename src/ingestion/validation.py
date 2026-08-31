import pandas as pd


def validate_dataframe(dataframe):

    problems = []

    if "timestamp" not in dataframe.columns:
        problems.append("Missing timestamp column")
        return problems

    # Dynamically find heads from columns
    heads = sorted(list(set(col[:3] for col in dataframe.columns if col.startswith("H") and col[1:3].isdigit() and col[3:4] == " ")))

    if not heads:
        problems.append("No head columns found in dataframe")
        return problems

    for head in heads:
        required_columns = [head + " Count",head + " AppTorque",head + " Status"]

        for column in required_columns:
            if column not in dataframe.columns:
                problems.append("Missing column: " + column)

    if len(problems) > 0:
        return problems

    invalid_timestamps = pd.to_datetime(dataframe["timestamp"],errors="coerce").isna().sum()

    if invalid_timestamps > 0:
        problems.append("Invalid timestamps: " + str(invalid_timestamps))

    missing_values = dataframe.isna().sum()
    total_missing = int(missing_values.sum())

    if total_missing > 0:
        problems.append("Missing values: " + str(total_missing))

    return problems