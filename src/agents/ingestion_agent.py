from src.agents.base_agent import BaseAgent
from src.ingestion.loader import read_data_file
from src.ingestion.validation import validate_dataframe


class IngestionAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Ingestion Agent",
            goal="Load and validate industrial telemetry data"
        )

    def run(self, context):

        if "zip_path" not in context:
            raise ValueError(
                "Missing zip_path in context"
            )

        if "filename" not in context:
            raise ValueError(
                "Missing filename in context"
            )

        dataframe = read_data_file(
            context["zip_path"],
            context["filename"]
        )

        validation_problems = validate_dataframe(
            dataframe
        )

        result = context.copy()

        result["dataframe"] = dataframe
        result["validation_problems"] = (
            validation_problems
        )

        return result