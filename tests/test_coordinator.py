import zipfile

import pandas as pd

from src.agents.coordinator import (
    MultiAgentCoordinator
)


def create_dataframe(counts, start_time):

    rows = len(counts)

    data = {
        "timestamp": pd.date_range(
            start_time,
            periods=rows,
            freq="s"
        )
    }

    for number in range(1, 37):

        head = f"H{number:02d}"

        if head == "H01":
            data[head + " Count"] = counts
        else:
            data[head + " Count"] = [0] * rows

        data[head + " AppTorque"] = (
            [2.0] * rows
        )

        data[head + " Status"] = (
            [0] * rows
        )

    return pd.DataFrame(data)


def create_zip(
    tmp_path,
    filename,
    dataframe
):

    csv_path = tmp_path / filename

    dataframe.to_csv(
        csv_path,
        index=False
    )

    zip_path = tmp_path / (
        filename + ".zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w"
    ) as archive:

        archive.write(
            csv_path,
            arcname=filename
        )

    return zip_path


def test_coordinator_processes_file(
    tmp_path
):

    dataframe = create_dataframe(
        [10, 11, 12],
        "2026-02-01 10:00:00"
    )

    zip_path = create_zip(
        tmp_path,
        "sample.csv",
        dataframe
    )

    coordinator = (
        MultiAgentCoordinator()
    )

    context = coordinator.process_file(
        zip_path,
        "sample.csv"
    )

    assert (
        context["validation_problems"]
        == []
    )

    assert context["total_cycles"] == 2

    assert (
        context["total_production_pieces"]
        == 2
    )

    assert (
        context["torque_stats"]["H01"]["count"]
        == 2
    )


def test_coordinator_preserves_state(
    tmp_path
):

    first_dataframe = create_dataframe(
        [10, 11],
        "2026-02-01 10:00:00"
    )

    second_dataframe = create_dataframe(
        [12, 13],
        "2026-02-01 10:00:02"
    )

    first_zip = create_zip(
        tmp_path,
        "first.csv",
        first_dataframe
    )

    second_zip = create_zip(
        tmp_path,
        "second.csv",
        second_dataframe
    )

    coordinator = (
        MultiAgentCoordinator()
    )

    context = coordinator.process_file(
        first_zip,
        "first.csv"
    )

    context = coordinator.process_file(
        second_zip,
        "second.csv",
        context
    )

    assert context["total_cycles"] == 3

    assert (
        context["total_production_pieces"]
        == 3
    )

    assert (
        context["previous_counts"]["H01"]
        == 13
    )


def test_coordinator_finalizes_report(
    tmp_path
):

    dataframe = create_dataframe(
        [10, 11, 12],
        "2026-02-01 10:00:00"
    )

    zip_path = create_zip(
        tmp_path,
        "sample.csv",
        dataframe
    )

    coordinator = (
        MultiAgentCoordinator()
    )

    context = coordinator.process_file(
        zip_path,
        "sample.csv"
    )

    result = coordinator.finalize(
        context
    )

    assert "report" in result

    assert (
        result["report"]["data"][
            "total_cycles"
        ]
        == 2
    )

    assert (
        result["report"]["data"][
            "production_pieces"
        ]
        == 2
    )

    assert "findings" in result["report"]

    assert (
        "confidence_and_limits"
        in result["report"]
    )

    assert (
        "next_checks"
        in result["report"]
    )