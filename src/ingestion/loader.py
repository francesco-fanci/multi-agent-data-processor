import zipfile 
import pandas as pd

def list_csv_files(zip_path):
    csv_files=[]

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for filename in zip_ref.namelist():
            if filename.lower().endswith(".csv"):
                csv_files.append(filename)

    csv_files.sort()
    return csv_files


def read_first_part(zip_path, size=10000):

    csv_files=list_csv_files(zip_path)

    if len(csv_files)==0:
        print("No csv files found ")
        return None

    first_csv=csv_files[0]

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        with zip_ref.open(first_csv) as csv_file:

            reader=pd.read_csv(csv_file, chunksize=size)
            first_part=next(reader)
    return first_csv, first_part

def read_csv_file(zip_path, csv_name):
    with zipfile.ZipFile(zip_path, "r") as archive:
        with archive.open(csv_name) as csv_file:
            dataframe=pd.read_csv(csv_file)
    return dataframe

    