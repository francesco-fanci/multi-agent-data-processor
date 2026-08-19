import zipfile

import pandas as pd
import pytest

from src.ingestion.loader import (
    list_data_files,
    read_data_file
)


def create_test_dataframe():

    return pd.DataFrame({
        "timestamp": [
            "2026-02-01 10:00:00",
            "2026-02-01 10:00:01"
        ],
        "value": [
            10,
            20
        ]
    })


def test_list_data_files(tmp_path):

    dataframe = create_test_dataframe()

    csv_path = tmp_path / "sample.csv"
    json_path = tmp_path / "sample.json"
    parquet_path = tmp_path / "sample.parquet"
    text_path = tmp_path / "notes.txt"

    dataframe.to_csv(
        csv_path,
        index=False
    )

    dataframe.to_json(
        json_path,
        orient="records"
    )

    dataframe.to_parquet(
        parquet_path,
        index=False
    )

    text_path.write_text(
        "unsupported file"
    )

    zip_path = tmp_path / "data.zip"

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            csv_path,
            arcname="sample.csv"
        )

        archive.write(
            json_path,
            arcname="sample.json"
        )

        archive.write(
            parquet_path,
            arcname="sample.parquet"
        )

        archive.write(
            text_path,
            arcname="notes.txt"
        )

    files = list_data_files(
        zip_path
    )

    assert files == [
        "sample.csv",
        "sample.json",
        "sample.parquet"
    ]


def test_read_csv(tmp_path):

    dataframe = create_test_dataframe()

    file_path = tmp_path / "sample.csv"

    dataframe.to_csv(
        file_path,
        index=False
    )

    zip_path = tmp_path / "csv.zip"

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            file_path,
            arcname="sample.csv"
        )

    result = read_data_file(
        zip_path,
        "sample.csv"
    )

    assert len(result) == 2
    assert result["value"].tolist() == [
        10,
        20
    ]


def test_read_json(tmp_path):

    dataframe = create_test_dataframe()

    file_path = tmp_path / "sample.json"

    dataframe.to_json(
        file_path,
        orient="records"
    )

    zip_path = tmp_path / "json.zip"

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            file_path,
            arcname="sample.json"
        )

    result = read_data_file(
        zip_path,
        "sample.json"
    )

    assert len(result) == 2
    assert result["value"].tolist() == [
        10,
        20
    ]


def test_read_parquet(tmp_path):

    dataframe = create_test_dataframe()

    file_path = tmp_path / "sample.parquet"

    dataframe.to_parquet(
        file_path,
        index=False
    )

    zip_path = tmp_path / "parquet.zip"

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            file_path,
            arcname="sample.parquet"
        )

    result = read_data_file(
        zip_path,
        "sample.parquet"
    )

    assert len(result) == 2
    assert result["value"].tolist() == [
        10,
        20
    ]


def test_corrupted_parquet(tmp_path):

    corrupted_path = (
        tmp_path / "broken.parquet"
    )

    corrupted_path.write_bytes(
        b"this is not a parquet file"
    )

    zip_path = tmp_path / "broken.zip"

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            corrupted_path,
            arcname="broken.parquet"
        )

    with pytest.raises(Exception):

        read_data_file(
            zip_path,
            "broken.parquet"
        )