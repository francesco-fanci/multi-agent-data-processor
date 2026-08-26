import pickle
from src.agents.tools import init_tools_context, get_success_rates

with open("data/processed/context.pkl", "rb") as f:
    context = pickle.load(f)

init_tools_context(context)
print(get_success_rates.invoke({}))
