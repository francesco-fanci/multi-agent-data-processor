from src.ingestion.loader import read_first_part

zip_path = (
    "data/raw/"
    "telemetry_MCC777eda3db57348ef8a3113a642ae74db_2026-02.zip"
)

result = read_first_part(zip_path)

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