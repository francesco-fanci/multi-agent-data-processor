from src.ingestion.loader import read_first_part
from src.cleaning.closure_detector import detect_all_closures
from src.cleaning.event_classifier import classify_events

zip_path = (
    "data/raw/"
    "telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-02.zip"
)

result = read_first_part(zip_path, size=86400)

if result is not None:
    csv_name, dataframe=result

    print(f"First CSV file: {csv_name}")

    print("\nNumber of rows in the first part:", len(dataframe))

    print("\nFirst few rows of the dataframe:")
    print(dataframe.head())

    print("\nNumber of columns in the dataframe:", len(dataframe.columns))

    print("\nColumn names in the dataframe:")
    for column in dataframe.columns:
        print(column)

    closures=detect_all_closures(dataframe)
    classified_events=classify_events(closures)

    print("\nNumber of closures detected for all heads:")
    print(len(closures))

    print("\nFirst closures detected:")
    print(closures.head(20))

    print("\nNumber of counter increments for each head:")
    print(closures["Head"].value_counts().sort_index())

    print("\nStatus values found:")
    print(closures["Status"].value_counts().sort_index())

    print("\nTorque statistics for each status:")
    print(
        closures.groupby("Status")["AppTorque"].agg(
            ["count", "min", "mean", "max"]
        )
    )

    normal_events = closures[
    closures["Status"] == 0
    ].copy()

    no_load_events = closures[
        closures["Status"] == 2
    ].copy()

    unusual_events = closures[
        ~closures["Status"].isin([0, 2])
    ].copy()

    zero_torque_normal_events = closures[
        (closures["Status"] == 0) &
        (closures["AppTorque"] <= 0)
    ].copy()


    print("\nEvents with Status 0:")
    print(len(normal_events))

    print("\nEvents with Status 2:")
    print(len(no_load_events))

    print("\nEvents with unusual status:")
    print(len(unusual_events))

    print("\nStatus 0 events with zero torque:")
    print(len(zero_torque_normal_events))

    print("\nUnusual events:")
    print(unusual_events.head(20))

    print("\nEvent types:")
    print(classified_events["Event Type"].value_counts())

    print("\nFirst classified events:")
    print(classified_events.head(20))   