import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from src.agents.tools import (get_overall_kpis,get_head_performance,get_torque_anomalies_summary,get_torque_drift_summary,get_idle_periods,get_top_correlations,get_success_rates,get_structured_report)

from src.agents.visualization_tools import (plot_torque_over_time,plot_machine_status_distribution,plot_torque_distribution_across_heads)

from src.config import LLM_MODEL_NAME

class AgenticOrchestrator:
    def __init__(self, api_key: str = None):
        """Initializes the Agentic AI Orchestrator with tools and LLM."""
        
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY")
            
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set. Please provide it or set the environment variable.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            google_api_key=api_key,
            temperature=0.0
        )
        
        self.tools = [get_overall_kpis,get_head_performance,get_torque_anomalies_summary,get_torque_drift_summary,get_idle_periods,get_top_correlations,get_success_rates,get_structured_report,plot_torque_over_time,plot_machine_status_distribution,plot_torque_distribution_across_heads]
        
        system_prompt = (
            "You are an industrial Multi-Agent AI system acting as an expert assistant for AROL capping machines. "
            "You analyze telemetry data (such as torque, anomalies, drift, and downtime/idle periods) and generate "
            "explainable reports on demand for technical users in R&D and Service.\n\n"
            "Guidelines:\n"
            "- Interpret the user's request and autonomously decide which tools to call.\n"
            "- If the user asks to generate a comprehensive report, use the get_structured_report tool and return it accurately.\n"
            "- Extract findings from the data retrieved by the tools.\n"
            "- If the user asks for a chart, plot, or visualization, use the plotting tools and provide the user with the file path to the saved image.\n"
            "- Provide confident, structured answers with explanations.\n"
            "- Remember that torque anomalies are statistical outliers and do not directly indicate machine failures.\n"
            "- Remember that correlation between heads does not imply causation."
        )
        
        self.agent = create_react_agent(model=self.llm,tools=self.tools,prompt=system_prompt)

    def process_query(self, query: str) -> str:
        """Processes a natural language query and returns the agent's response."""
        result = self.agent.invoke({"messages": [("user", query)]})
        return result["messages"][-1].content
