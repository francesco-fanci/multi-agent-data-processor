from src.agents.orchestrator_agent import AgenticOrchestrator
import os
os.environ["GOOGLE_API_KEY"] = "dummy_key"
try:
    orc = AgenticOrchestrator()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
