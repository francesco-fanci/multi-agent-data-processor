# TECHNICAL DOCUMENTATION
**Project Q3 - Telemetry Analytics on AROL Capping Machines**

This document fulfills the technical documentation requirements for the AROL telemetry analytics project.

---

## 1. Architecture
The system is built as a decentralized **Multi-Agent System (MAS)**. Instead of relying on a monolithic script, the architecture is divided into specialized autonomous agents, adhering to the Single Responsibility Principle:
- **WP2 (Data Pipeline):** A deterministic backend consisting of the `IngestionAgent`, `DataQualityAgent`, `AnalyticsAgent`, and `ReportAgent`. These agents process data in a sequential, memory-optimized flow (chunking) to prevent Out-Of-Memory (OOM) errors.
- **WP4 (Agentic UI):** A generative frontend consisting of the `AgenticOrchestrator`. It exposes a CLI that acts as a bridge between the human operator and the backend's knowledge base.

## 2. Data Schema
The telemetry data is handled in-memory using **Pandas DataFrames** (columnar memory layout), optimizing sequential access and aggregations.
- **Raw Schema:** Wide format time-series matrices with asynchronous polling updates (e.g., `timestamp`, `H01 Count`, `H01 AppTorque`, `H01 Status`). The system is *configuration-driven* and dynamically detects the number of heads (e.g., 36 or 48).
- **Clean Event Schema:** Event-driven architecture. The raw tables are transformed into strict event rows containing: `timestamp`, `Head`, `Count`, `AppTorque`, `Status`, `Count Difference`.
- **Knowledge Schema:** The `ReportAgent` aggregates the entire database into a strict, lightweight JSON dictionary (`context.pkl`) containing structured metrics (`goal`, `data`, `analyses`, `findings`, `confidence_and_limits`, `next_checks`).

## 3. Analytics Methods
The `AnalyticsAgent` and `DataQualityAgent` perform deterministic heuristic analytics using vectorized operations (SIMD CPU instructions) to maximize speed:
- **Closure Detection & Deduplication:** Applies the `shift(1)` vectorial derivative on cumulative counters to isolate real physical events (`Count Difference > 0`) from polling noise (`Count Difference == 0`).
- **Torque Anomalies:** Utilizes the Interquartile Range (IQR) method to dynamically establish statistical thresholds for each specific head, flagging outliers without using hardcoded limits.
- **Torque Drift Detection:** Computes a 7-day Moving Average baseline. If the current daily torque average deviates beyond a predefined threshold (e.g., 0.1 Nm), a mechanical drift is flagged.
- **Head Correlation:** Calculates the Pearson Correlation matrix on *residual* torque averages (subtracting the global daily machine average) to detect tandem wear between heads while filtering out environmental noise.

## 4. Agent Decision Flow
The interaction between the user and the AI relies on a strictly governed **Agentic Flow** implemented via LangGraph:
1. **User Query:** The user inputs a natural language query via the terminal (CLI).
2. **ReAct Pattern:** The `AgenticOrchestrator` (powered by Gemini) receives the query. It is constrained by a strict System Prompt (`temperature=0.0`) that forbids hallucinatory math.
3. **Tool Binding:** The Agent evaluates its available Python Tools (`tools.py` and `visualization_tools.py`) and autonomously decides which tool to call based on the semantic intent of the query.
4. **Context Retrieval:** The invoked Python Tool reads the deterministic metrics from the `context.pkl` database.
5. **Final Output:** The Agent receives the ground-truth data from the tool, formats it into a human-readable explanation (or returns the path to a Matplotlib generated chart), and delivers the final response to the user.
