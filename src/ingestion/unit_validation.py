UNIT_METADATA = {
    "Count": {
        "unit": None,
        "requires_physical_unit": False,
        "description": "Cumulative counter value"
    },

    "Status": {
        "unit": None,
        "requires_physical_unit": False,
        "description": "Categorical machine status code"
    },

    "AppTorque": {
        "unit": None,
        "requires_physical_unit": True,
        "description": (
            "Applied torque measurement. "
            "Physical unit is not specified "
            "in the available dataset."
        )
    }
}


def validate_units(unit_metadata=None):

    if unit_metadata is None:
        unit_metadata = UNIT_METADATA

    problems = []

    for measurement, metadata in (
        unit_metadata.items()
    ):

        requires_unit = metadata.get(
            "requires_physical_unit",
            False
        )

        unit = metadata.get(
            "unit"
        )

        if (
            requires_unit
            and (
                unit is None
                or str(unit).strip() == ""
            )
        ):
            problems.append(
                "Missing unit metadata: "
                + measurement
            )

    return problems