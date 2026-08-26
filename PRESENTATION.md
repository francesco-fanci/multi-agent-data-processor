---
marp: true
theme: default
paginate: true
---

# Multi-Agent System for Industrial IoT Data Refinement
## Project Q3 - AROL S.p.A. Capping Machine Data Processing

---

## Project Objectives

1. **Data Ingestion & Local Synchronization**: Automated cloud data fetch.
2. **Agent-Based Data Cleaning**: Specialized agents filter noise.
3. **Deduplication & Logic Filtering**: Accurate detection of closures.
4. **Advanced Data Analytics**: KPI, Drift, Anomaly evaluation.
5. **Scalability**: MAS architecture overcoming monolithic limits.

---

## MAS Architecture

The pipeline is governed by specialized Agents:
- **IngestionAgent**: Local synchronization and structured DataFrame loading.
- **DataQualityAgent**: Filters noise, handles missing entries, deduplicates closure counts.
- **AnalyticsAgent**: Performs deterministic data analysis (Anomalies, KPIs, Correlation).
- **ReportAgent**: Condenses output into human-readable reporting.
- **AgenticOrchestrator**: Interactive chatbot LLM to query data context dynamically.

---

## Experimental Evaluation
*Note: Evaluated strictly as MAS. CPU SIMD vectorization used over GPU scaling.*

- **Robustness**: Fault-tolerant vs Monolithic approach (which fails completely on one bad telemetry file).
- **Memory Scaling**: OOM avoided by columnar state processing.
- **Agent Processing**: Deduplication applied locally for each of the 36 capping heads without locking.

---

## Final Findings

- **Volume Processed**: Over 55 Million Raw Telemetry events.
- **Deduplication Output**: Reconstructed 32 Million production pieces accurately.
- **Analytics Delivered**: 
    - 3,489 Idle Periods discovered.
    - 100k+ Torque Anomalies detected.
    - Strong inter-head correlation behaviors identified.

---
