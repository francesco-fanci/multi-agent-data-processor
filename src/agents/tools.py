from langchain_core.tools import tool

# Global context to be initialized before agent starts
_context = {}

def init_tools_context(context):
    global _context
    _context.clear()
    _context.update(context)

@tool
def get_overall_kpis() -> str:
    """Returns the overall production KPIs, including total cycles, production pieces, cycle speed, and production speed."""
    if not _context:
         return "Context is not initialized."
    return (
        f"Total Cycles: {_context.get('total_cycles')}\n"
        f"Production Pieces: {_context.get('total_production_pieces')}\n"
        f"Cycle Speed: {_context.get('cycle_speed')} pieces/hour\n"
        f"Production Speed: {_context.get('production_speed')} pieces/hour"
    )

@tool
def get_head_performance(head_id: str) -> str:
    """Returns torque statistics for a specific head (e.g., 'H01', 'H02')."""
    if not _context:
         return "Context is not initialized."
    
    head_id = head_id.upper()
    torque_results = _context.get("torque_results", {})
    if head_id not in torque_results:
        return f"No data found for head {head_id}."
    
    stats = torque_results[head_id]
    return (
        f"Performance for {head_id}:\n"
        f"Events: {stats['count']}\n"
        f"Average Torque: {stats['average']} Nm\n"
        f"Min Torque: {stats['min']} Nm\n"
        f"Max Torque: {stats['max']} Nm\n"
        f"Standard Deviation: {stats['standard_deviation']}\n"
    )

@tool
def get_torque_anomalies_summary() -> str:
    """Returns a summary of torque anomalies detected across all heads."""
    if not _context:
         return "Context is not initialized."
    
    anomaly_stats = _context.get("anomaly_stats", {})
    total_anomalies = sum(item["count"] for item in anomaly_stats.values())
    
    details = []
    for head, stats in anomaly_stats.items():
        if stats["count"] > 0:
            details.append(f"{head}: {stats['count']} anomalies (Highest: {stats['highest_value']} at {stats['highest_timestamp']})")
            
    summary = f"Total Torque Anomalies: {total_anomalies}\n"
    summary += "\n".join(details)
    return summary

@tool
def get_torque_drift_summary() -> str:
    """Returns a summary of torque drift events detected across all heads."""
    if not _context:
         return "Context is not initialized."
         
    drift_results = _context.get("drift_results", {})
    total_drifts = sum(len(items) for items in drift_results.values())
    
    if total_drifts == 0:
        return "No torque drift detected."
        
    summary = f"Total Drift Events: {total_drifts}\n"
    for head, drifts in drift_results.items():
        for drift in drifts:
            summary += f"{head} on {drift['date']}: {drift['direction']} (Avg: {drift['average']}, Baseline: {drift['baseline']})\n"
            
    return summary

@tool
def get_idle_periods() -> str:
    """Returns information about machine idle periods (downtime)."""
    if not _context:
         return "Context is not initialized."
         
    idle_periods = _context.get("idle_periods", [])
    total_idle_seconds = sum(period["duration_seconds"] for period in idle_periods)
    total_idle_hours = total_idle_seconds / 3600
    
    if not idle_periods:
        return "No idle periods detected."
        
    longest_idle = max(idle_periods, key=lambda p: p["duration_seconds"])
    
    return (
        f"Total Idle Periods: {len(idle_periods)}\n"
        f"Total Idle Hours: {total_idle_hours:.2f} hours\n"
        f"Longest Idle Period: {longest_idle['duration_seconds']/60:.2f} minutes (from {longest_idle['start']} to {longest_idle['end']})"
    )

@tool
def get_top_correlations() -> str:
    """Returns the top residual correlations between machine heads to identify heads behaving similarly."""
    if not _context:
         return "Context is not initialized."
         
    correlations = _context.get("top_residual_correlations", [])
    if not correlations:
        return "No correlations found."
        
    summary = "Top Residual correlations between heads:\n"
    for result in correlations[:10]:
        summary += f"{result['head_1']} - {result['head_2']}: {result['correlation']:.4f}\n"
        
    return summary

@tool
def get_success_rates() -> str:
    """Returns the success rates (percentage of successful capping operations excluding No Load) overall and per head."""
    if not _context:
        return "Context is not initialized."
    
    success_metrics = _context.get("success_metrics")
    if not success_metrics:
        return "No success metrics available."
        
    overall = success_metrics.get("overall", {})
    closure_ok = overall.get("Closure OK", 0)
    
    # Total attempted closures = everything except 'No Load'
    total_attempted = sum(count for event, count in overall.items() if event != "No Load")
    
    if total_attempted == 0:
        return "No capping operations were attempted."
        
    overall_rate = (closure_ok / total_attempted) * 100
    summary = f"Overall Success Rate: {overall_rate:.2f}%\n"
    summary += f"Total Closures Attempted: {total_attempted}, Successful: {closure_ok}\n\n"
    
    summary += "Success Rate by Head:\n"
    by_head = success_metrics.get("by_head", {})
    for head, metrics in sorted(by_head.items()):
        head_ok = metrics.get("Closure OK", 0)
        head_attempted = sum(count for event, count in metrics.items() if event != "No Load")
        if head_attempted > 0:
            rate = (head_ok / head_attempted) * 100
            summary += f"- {head}: {rate:.2f}% ({head_ok}/{head_attempted})\n"
            
    return summary

import json

@tool
def get_structured_report() -> str:
    """Returns the comprehensive, structured markdown report generated by the Report Agent containing all requested specifications (goal, data, analyses, findings, confidence_and_limits, next_checks)."""
    if not _context:
        return "Context is not initialized."
        
    report = _context.get("report")
    if not report:
        return "No structured report found in context."
        
    return json.dumps(report, indent=2, default=str)
