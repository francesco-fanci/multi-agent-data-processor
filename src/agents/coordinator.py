from src.agents.ingestion_agent import (IngestionAgent)

from src.agents.data_quality_agent import (DataQualityAgent)

from src.agents.analytics_agent import (AnalyticsAgent)

from src.agents.report_agent import (ReportAgent)


class MultiAgentCoordinator:

    def __init__(self):

        self.ingestion_agent = (IngestionAgent())

        self.data_quality_agent = (DataQualityAgent())

        self.analytics_agent = (AnalyticsAgent())

        self.report_agent = (ReportAgent())

    def process_file(self,zip_path,filename,context=None):

        if context is None:
            context = {}

        context = context.copy()

        context["zip_path"] = zip_path
        context["filename"] = filename

        context = self.ingestion_agent.run(context)

        context = self.data_quality_agent.run(context)

        context = self.analytics_agent.run(context)

        return context

    def finalize(self, context):

        context = self.analytics_agent.finalize(context)

        context = self.report_agent.run(context)

        return context