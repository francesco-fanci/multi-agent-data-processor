from src.ingestion.unit_validation import (
    UNIT_METADATA,
    validate_units
)


def test_missing_app_torque_unit():

    problems = validate_units()

    assert (
        "Missing unit metadata: AppTorque"
        in problems
    )


def test_count_does_not_require_physical_unit():

    problems = validate_units()

    assert (
        "Missing unit metadata: Count"
        not in problems
    )


def test_status_does_not_require_physical_unit():

    problems = validate_units()

    assert (
        "Missing unit metadata: Status"
        not in problems
    )


def test_valid_app_torque_unit_metadata():

    metadata = {
        "AppTorque": {
            "unit": "documented-unit",
            "requires_physical_unit": True
        }
    }

    problems = validate_units(
        metadata
    )

    assert problems == []


def test_empty_unit_is_invalid():

    metadata = {
        "AppTorque": {
            "unit": "",
            "requires_physical_unit": True
        }
    }

    problems = validate_units(
        metadata
    )

    assert problems == [
        "Missing unit metadata: AppTorque"
    ]