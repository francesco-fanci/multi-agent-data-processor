import os
import sys
import pickle
import argparse

def create_markdown_reports(context):
    report_data = context.get("report", {})
    if not report_data:
        print("No report data found in context.")
        return

    os.makedirs("reports", exist_ok=True)
    
    # Extract data for processing
    heads = sorted(context.get("torque_results", {}).keys())
    success_metrics = context.get("success_metrics", {}).get("by_head", {})
    torque_results = context.get("torque_results", {})
    findings = report_data.get("findings", {})
    data = report_data.get("data", {})
    dq = findings.get("data_quality", {})
    
    # --- Advanced Computations for KPI Report ---
    head_stats = []
    for head in heads:
        head_success = success_metrics.get(head, {})
        ok = head_success.get("Closure OK", 0)
        # Sum all events that are not "Closure OK" and not "No Load" to get failed closures
        bad = sum(count for event, count in head_success.items() if event not in ["Closure OK", "No Load"])
        total_prod = ok + bad
        succ_pct = (ok / total_prod * 100) if total_prod > 0 else 0.0

        t_res = torque_results.get(head, {})
        head_stats.append({
            "head": head, "total": total_prod, "ok": ok, "bad": bad,
            "succ_pct": succ_pct, 
            "mean_t": t_res.get("average", 0.0), 
            "std_t": t_res.get("standard_deviation", 0.0),
            "min_t": t_res.get("min", 0.0), 
            "max_t": t_res.get("max", 0.0)
        })

    # Sort heads by success percentage (descending), then by total volume
    head_stats.sort(key=lambda x: (x["succ_pct"], x["total"]), reverse=True)
    
    overall_ok = sum(x["ok"] for x in head_stats)
    overall_prod = sum(x["total"] for x in head_stats)
    overall_succ_pct = (overall_ok / overall_prod * 100) if overall_prod > 0 else 0.0
    
    best_head = head_stats[0] if head_stats else {}
    worst_head = head_stats[-1] if head_stats else {}

    # --- Advanced Computations for Anomaly Report ---
    idle_periods = context.get("idle_periods", [])
    longest_idle = max(idle_periods, key=lambda x: x["duration_seconds"]) if idle_periods else None

    drift_results = context.get("drift_results", {})
    all_drifts = []
    for h, drifts in drift_results.items():
        for d in drifts:
            all_drifts.append({"head": h, **d})
    all_drifts.sort(key=lambda x: abs(x["difference"]), reverse=True)


    # ==========================================
    # 1. KPI & Quality Report (Rich Format)
    # ==========================================
    kpi_report = "reports/kpi_quality_report.md"
    with open(kpi_report, "w") as f:
        f.write("# AROL Capping Machine — KPI Dashboard\n\n")
        
        f.write(f"**Observation Period**: {data.get('first_timestamp', 'N/A')} to {data.get('last_timestamp', 'N/A')}\n")
        f.write("**Source**: Generated dynamically by `demo.py` analytical engine.\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|-----|-------|\n")
        f.write(f"| **Overall Success Rate** | **{overall_succ_pct:.4f}%** ({overall_ok:,} OK / {overall_prod:,} Total) |\n")
        f.write(f"| Machine Cycle Speed | {findings.get('cycle_speed', 0.0):,.2f} pcs/hr |\n")
        f.write(f"| Machine Production Speed | {findings.get('production_speed', 0.0):,.2f} pcs/hr |\n")
        if best_head and worst_head:
            f.write(f"| Best-Performing Head | **{best_head['head']}** ({best_head['succ_pct']:.4f}%) |\n")
            f.write(f"| Worst-Performing Head | **{worst_head['head']}** ({worst_head['succ_pct']:.4f}%) |\n")
        f.write("\n> **Note on Throughput:** *Machine Cycle Speed* includes all operational cycles (including No Load), whereas *Machine Production Speed* isolates actual capping operations (Closure OK and Bad Closure).\n\n")

        f.write("## Data Quality & Pipeline Integrity\n\n")
        f.write("| Integrity Metric | Count | Description |\n")
        f.write("|-----|-------|---|\n")
        f.write(f"| Raw Events Processed | {dq.get('raw_events', 0):,} | Total telemetry rows ingested |\n")
        f.write(f"| Valid Events Filtered | {dq.get('valid', 0):,} | Events passing basic PLC validation |\n")
        f.write(f"| Detected Data Gaps | {dq.get('data_gap', 0):,} | Temporal discontinuities flagged |\n")
        f.write(f"| Counter Recoveries | {dq.get('counter_recovery', 0):,} | Sudden PLC counter resets managed |\n\n")

        f.write("## Head Performance Summary\n\n")
        f.write("All 36 machine heads, ranked by Success Rate (best to worst).\n\n")
        f.write("| Rank | Head | Total Prod. | Successful | Failed | Success % | Mean Torque (Nm) | Torque Std (Nm) | Min | Max |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        
        for idx, stat in enumerate(head_stats, start=1):
            f.write(f"| {idx} | **{stat['head']}** | {stat['total']:,} | {stat['ok']:,} | {stat['bad']:,} | {stat['succ_pct']:.4f}% | {stat['mean_t']:.4f} | {stat['std_t']:.4f} | {stat['min_t']:.2f} | {stat['max_t']:.2f} |\n")


    # ==========================================
    # 2. Anomaly & Diagnostics Report (Rich Format)
    # ==========================================
    anomaly_report = "reports/anomaly_diagnostics_report.md"
    with open(anomaly_report, "w") as f:
        f.write("# AROL Capping Machine — Anomaly & Diagnostics Report\n\n")
        f.write(f"**Observation Period**: {data.get('first_timestamp', 'N/A')} to {data.get('last_timestamp', 'N/A')}\n\n")
        
        f.write("## High-Level Hardware Diagnostics\n\n")
        f.write(f"- **Total Torque Anomalies (IQR Method):** {findings.get('torque_anomalies', 0):,}\n")
        f.write(f"- **Total Torque Drift Events:** {findings.get('torque_drift_events', 0):,}\n\n")
        
        f.write("## Per-Head Anomaly Breakdown\n\n")
        f.write("Components ranked by statistical outlier frequency. High anomaly counts may suggest mechanical wear, spring fatigue, or sensor calibration issues.\n\n")
        f.write("| Rank | Head | Anomalies Detected | Lowest Peak | (Timestamp) | Highest Peak | (Timestamp) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        anomaly_stats = context.get("anomaly_stats", {})
        sorted_anomalies = sorted(anomaly_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        for idx, (head, stats) in enumerate(sorted_anomalies, start=1):
            count = stats.get("count", 0)
            if count > 0:
                lowest = stats.get("lowest_value", 0.0)
                low_ts = stats.get("lowest_timestamp", "N/A")
                highest = stats.get("highest_value", 0.0)
                high_ts = stats.get("highest_timestamp", "N/A")
                f.write(f"| {idx} | **{head}** | {count:,} | {lowest:.2f} Nm | *{low_ts}* | {highest:.2f} Nm | *{high_ts}* |\n")
                
        if all_drifts:
            f.write("\n## Severe Torque Drifts\n\n")
            f.write("Detects gradual shifts in baseline torque application. Listed by magnitude of drift.\n\n")
            f.write("| Head | Date | Baseline Torque | Shifted Torque | Difference | Direction |\n")
            f.write("|---|---|---|---|---|---|\n")
            for d in all_drifts[:10]: # Show top 10 drifts
                f.write(f"| **{d['head']}** | {d['date']} | {d['baseline']:.4f} | {d['average']:.4f} | **{d['difference']:.4f}** | {d['direction']} |\n")

        f.write("\n## Machine Downtime (Idle Periods)\n\n")
        f.write(f"- **Total Idle Instances:** {findings.get('idle_periods', 0):,}\n")
        f.write(f"- **Total Idle Time:** {findings.get('idle_hours', 0.0):.2f} ore\n")
        if longest_idle:
            f.write(f"- **Longest Continuous Idle:** Da *{longest_idle['start']}* a *{longest_idle['end']}* ({longest_idle['duration_seconds']/60:.1f} minuti)\n")
        
        f.write("\n## Structural Stress (Top Residual Correlations)\n\n")
        f.write("Residual correlations highlight strong mechanical relationships between specific heads, neutralizing machine-wide trends. Useful for identifying shared subsystem vibrations.\n\n")
        f.write("| Head A | Head B | Pearson Correlation |\n")
        f.write("|---|---|---|\n")
        for corr in findings.get("top_residual_correlations", []):
            f.write(f"| **{corr['head_1']}** | **{corr['head_2']}** | {corr['correlation']:.4f} |\n")
            
        f.write("\n## Recommendations & Next Checks\n\n")
        for check in report_data.get("next_checks", []):
            f.write(f"- [ ] {check}\n")
            
        f.write("\n## Confidence Limits (AI Transparency)\n\n")
        for limit in report_data.get("confidence_and_limits", []):
            f.write(f"- *{limit}*\n")

    print(f"✅ Generated {kpi_report}")
    print(f"✅ Generated {anomaly_report}")


def main():
    parser = argparse.ArgumentParser(description="Run the end-to-end demo and generate rich reports.")
    parser.add_argument("--skip-pipeline", action="store_true", help="Skip running the pipeline and just generate reports from existing context.")
    args = parser.parse_args()

    print("========================================")
    print("Multi-Agent Data Processor - End-to-End Demo")
    print("========================================")
    
    if not args.skip_pipeline:
        print("\n[1/3] Running the data processing pipeline (main.py)...")
        # Use sys.executable to ensure the correct python interpreter is used
        # Added quotes around sys.executable to handle spaces in the path
        exit_code = os.system(f'"{sys.executable}" main.py')
        if exit_code != 0:
            print("Pipeline execution failed.")
            sys.exit(1)
    else:
        print("\n[1/3] Skipping pipeline execution as requested.")
        
    print("\n[2/3] Loading processed context...")
    context_path = "data/processed/context.pkl"
    if not os.path.exists(context_path):
        print(f"Error: {context_path} not found.")
        print("Run without --skip-pipeline to generate it.")
        sys.exit(1)
        
    with open(context_path, "rb") as f:
        context = pickle.load(f)
        
    print("\n[3/3] Generating final rich reports...")
    create_markdown_reports(context)
    
    print("\n🎉 Demo completed successfully! Check the 'reports/' folder.")

if __name__ == "__main__":
    main()
