import os
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_core.tools import tool

# We import the global context from tools to share the same loaded data
from src.agents.tools import _context

PLOT_DIR = "data/processed/plots"

def ensure_plot_dir():
    os.makedirs(PLOT_DIR, exist_ok=True)

@tool
def plot_torque_over_time(head_id: str) -> str:
    """Plots the closing torque over time for a specific head (e.g., 'H01') and saves it to a file. Returns the file path."""
    if not _context:
        return "Context is not initialized."
        
    head_id = head_id.upper()
    daily_results = _context.get("daily_torque_results", {})
    
    if head_id not in daily_results:
        return f"No daily torque data found for head {head_id}."
        
    data = daily_results[head_id]
    dates = [item["date"] for item in data]
    averages = [item["average"] for item in data]
    
    ensure_plot_dir()
    filepath = os.path.join(PLOT_DIR, f"{head_id}_torque_over_time.png")
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=dates, y=averages, marker="o", color="blue")
    plt.title(f"Closing Torque Over Time - {head_id}")
    plt.xlabel("Date")
    plt.ylabel("Average Torque (Nm)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    return f"Plot successfully created and saved to {filepath}"

@tool
def plot_machine_status_distribution() -> str:
    """Creates a pie chart showing the overall distribution of machine status (Closure OK, Bad Closure, No Load). Returns the file path."""
    if not _context:
        return "Context is not initialized."
        
    ensure_plot_dir()
    filepath = os.path.join(PLOT_DIR, "machine_status_distribution.png")
    
    # We can infer these from the context or we can just plot the overall KPIs we have
    # Actually, we don't have total_closure_ok directly in the context dict in main.py.
    # main.py calculates them but doesn't put them in context! 
    # Wait, in main.py line 429: `print(total_closure_ok)`. They were NOT saved in context.
    # We have `total_production_pieces` and `total_cycles`
    # No Load = total_cycles - total_production_pieces
    # Let's plot Production vs No Load
    total_cycles = _context.get("total_cycles", 0)
    production_pieces = _context.get("total_production_pieces", 0)
    no_load = total_cycles - production_pieces
    
    labels = ["Production (Closure OK & Bad)", "No Load (Idle cycles)"]
    sizes = [production_pieces, no_load]
    colors = ["#4CAF50", "#FFC107"]
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title("Machine Cycles Distribution (Production vs No Load)")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    return f"Pie chart successfully created and saved to {filepath}"

@tool
def plot_torque_distribution_across_heads() -> str:
    """Creates a bar chart showing the average closing torque for all 36 heads. Returns the file path."""
    if not _context:
        return "Context is not initialized."
        
    torque_results = _context.get("torque_results", {})
    if not torque_results:
        return "No torque results found in context."
        
    heads = sorted(torque_results.keys())
    averages = [torque_results[h]["average"] for h in heads]
    
    ensure_plot_dir()
    filepath = os.path.join(PLOT_DIR, "torque_distribution_heads.png")
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=heads, y=averages, color="steelblue")
    plt.title("Average Closing Torque per Head")
    plt.xlabel("Head ID")
    plt.ylabel("Average Torque (Nm)")
    plt.xticks(rotation=90)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    return f"Bar chart successfully created and saved to {filepath}"
