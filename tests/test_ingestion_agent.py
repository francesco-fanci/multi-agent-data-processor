import zipfile

import pandas as pd
import pytest

from src.agents.ingestion_agent import IngestionAgent


def create_valid_dataframe():

    data = {
        "timestamp": [
            "2026-02-01 10:00:00",
            "2026-02-01 10:00:01"
        ]
    }

    for number in range(1, 37):

        head = f"H{number:02d}"

        data[head + " Count"] = [1, 2]
        data[head + " AppTorque"] = [2.0, 2.1]
        data[head + " Status"] = [0, 0]

    return pd.DataFrame(data)


def test_ingestion_agent(tmp_path):

    dataframe = create_valid_dataframe()

    csv_path = tmp_path / "sample.csv"

    dataframe.to_csv(
        csv_path,
        index=False
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

    agent = IngestionAgent()

    context = {
        "zip_path": zip_path,
        "filename": "sample.csv"
    }

    result = agent.run(context)

    assert len(result["dataframe"]) == 2
    assert result["validation_problems"] == []
    assert result[
        "unit_validation_problems"
    ] == [
        "Missing unit metadata: AppTorque"
    ]

    assert agent.name == "Ingestion Agent"


def test_missing_zip_path():

    agent = IngestionAgent()

    context = {
        "filename": "sample.csv"
    }

    with pytest.raises(
        ValueError,
        match="Missing zip_path in context"
    ):
        agent.run(context)


def test_missing_filename():

    agent = IngestionAgent()

    context = {
        "zip_path": "data.zip"
    }

    with pytest.raises(
        ValueError,
        match="Missing filename in context"
    ):
        agent.run(context)