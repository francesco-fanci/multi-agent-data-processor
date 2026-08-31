import io
import zipfile
import pandas as pd


SUPPORTED_EXTENSIONS = (".csv",".json",".parquet")


def list_data_files(zip_path):
    data_files = []

    with zipfile.ZipFile(zip_path, "r") as archive:
        for filename in archive.namelist():

            if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                data_files.append(filename)

    data_files.sort()

    return data_files


def read_data_file(zip_path, filename):

    with zipfile.ZipFile(zip_path, "r") as archive:
        file_content = archive.read(filename)

    file_buffer = io.BytesIO(file_content)

    lower_filename = filename.lower()

    if lower_filename.endswith(".csv"):
        dataframe = pd.read_csv(file_buffer)

    elif lower_filename.endswith(".json"):
        dataframe = pd.read_json(file_buffer)

    elif lower_filename.endswith(".parquet"):
        dataframe = pd.read_parquet(file_buffer)

    else:
        raise ValueError("Unsupported file format: " + filename)

    # Deduplication: remove redundant entries to maintain data integrity
    dataframe = dataframe.drop_duplicates().copy()

    return dataframe