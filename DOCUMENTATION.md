# TECHNICAL DOCUMENTATION
**Project Q3 - Telemetry Analytics on AROL Capping Machines**

This document fulfills the technical documentation requirements for the AROL telemetry analytics project. It provides an in-depth overview of the system's underlying engineering principles, architectural patterns, and analytical methodologies.

---

## 1. Architecture
The system breaks away from traditional monolithic data processing scripts by implementing a decentralized **Multi-Agent System (MAS)** architecture. This approach enforces the Single Responsibility Principle and allows for localized fault tolerance.

### 1.1 The Deterministic Backend (WP2)
The data refinement pipeline is strictly deterministic to prevent mathematical hallucinations. It operates through a chain of sequential agents:
- **`IngestionAgent`**: Responsible for secure data retrieval, format normalization (CSV/Parquet), and initial structural validation. It implements a **Direct-to-RAM** streaming protocol to bypass disk I/O bottlenecks.
- **`DataQualityAgent`**: Acts as a noise filter. It maps continuous polling states into discrete, human-readable events (e.g., "Closure OK", "No Load") and detects anomalies like `Counter Recovery` resets and `Data Gaps`.
- **`AnalyticsAgent`**: The computational core. It applies statistical algorithms to the cleaned data to extract operational throughput and mechanical insights (drifts, anomalies, correlations).
- **`ReportAgent`**: The aggregation layer. It queries the distributed findings of the previous agents and compiles them into a unified, strictly typed schema.

### 1.2 The Generative Frontend (WP4)
The interface is handled by the **`AgenticOrchestrator`**. This agent leverages Google's Gemini LLM within a **ReAct (Reason and Act)** loop powered by LangGraph. It acts as a cognitive bridge, receiving natural language queries from the CLI (`bot.py`) and binding them to deterministic Python tools. 

### 1.3 Scalability and Memory Management
To process industrial-scale Big Data (55M+ rows) without triggering Out-Of-Memory (OOM) crashes, the architecture utilizes **Incremental State Enrichment**. 
- Data is processed in sequential chunks. 
- Averages and Variances are computed incrementally using weighted formulas (e.g., Sum of Squares for variance).
- Upon finalization, a **State Purging** routine explicitly deletes massive DataFrames from memory (`del context["dataframe"]`), serializing only the distilled ~10KB state dictionary into `context.pkl`.

---

## 2. Data Schema
The system manages data across three distinct lifecycle schemas, optimizing for computational speed and semantic clarity.

### 2.1 Raw Telemetry Schema (Input)
The raw dataset is a wide-format, time-series matrix characterized by high-frequency asynchronous polling.
- **Structure**: `timestamp`, `H01 Count`, `H01 AppTorque`, `H01 Status`, ..., up to `H48`.
- **Dynamic Configuration**: The system dynamically scans the column headers to adapt to machines with 36, 48, or any number of capping heads without hardcoded limits.

### 2.2 Clean Event Schema (In-Memory)
During execution, the `DataQualityAgent` pivots the wide matrix into a narrow, event-driven schema.
- **Structure**: `timestamp`, `Head`, `Count`, `AppTorque`, `Status`, `Previous Count`, `Count Difference`.
- **Optimization**: Stored entirely in Pandas DataFrames leveraging columnar memory layouts for SIMD vectorized execution.

### 2.3 Knowledge Schema (Output)
The final artifact (`context.pkl`) is a highly structured JSON-like dictionary, purposefully designed to be parsed by an LLM without cognitive overload.
- **Nodes**:
  - `goal`: String defining the report's purpose.
  - `data`: Bounding timestamps and total cycle metadata.
  - `analyses`: List of invoked analytical methods.
  - `findings`: Granular dictionary of success rates, anomalies, and correlations.
  - `confidence_and_limits`: Explicit statistical warnings (e.g., "Correlation does not imply causation") to enforce LLM safety.
  - `next_checks`: Actionable maintenance recommendations.

---

## 3. Analytics Methods
The `AnalyticsAgent` employs a suite of advanced heuristics to detect mechanical wear before catastrophic failures occur.

### 3.1 Closure Detection & Deduplication
To isolate real capping events from background polling noise, the system utilizes the `pandas.shift(1)` method. By calculating the discrete derivative of the cumulative counter column (`Count Difference = Current - Previous`), the system discards rows with a difference of 0 (Polling Noise) and registers rows with a difference > 0 as true physical events.

### 3.2 Dynamic Outlier Detection (IQR Method)
Instead of relying on hardcoded torque thresholds (which vary per head), the system uses the **Interquartile Range (IQR)** method. 
- It calculates the Q1 (25th percentile) and Q3 (75th percentile) of the applied torque distribution for each individual head.
- Closures falling outside the dynamically calculated bounds ($Q1 - 3*IQR$ to $Q3 + 3*IQR$) are flagged as statistical anomalies.

### 3.3 Torque Drift Detection
The system tracks mechanical fatigue (e.g., a relaxing spring) over time. It computes a **7-Day Moving Average** baseline. If a head's current daily average torque deviates from this historical baseline by more than a predefined threshold (e.g., 0.1 Nm), a `Drift Warning` (Increase/Decrease) is triggered.

### 3.4 Residual Head Correlation
To identify tandem wear (e.g., heads sharing a faulty cam track), the system calculates the Pearson Correlation matrix between heads. Crucially, it operates on **Residual Torque** (subtracting the global daily machine average from the head's daily average). This filters out environmental noise (like a stiffer batch of plastic caps affecting all heads) and highlights purely mechanical correlations.

---

## 4. Agent Decision Flow
The interaction loop between the human operator and the backend data is governed by the `AgenticOrchestrator` via a strict decision flow.

1. **User Query**: The operator inputs a natural language query via the `bot.py` CLI.
2. **Context Verification**: The bot verifies the existence of `context.pkl` (Fail-Fast mechanism).
3. **ReAct Loop Initiation**: The LLM receives the query alongside a strict System Prompt (`temperature=0.0`) that enforces an industrial expert persona.
4. **Tool Selection (Think & Select)**: The LLM parses the docstrings of the available Python tools (e.g., `get_success_rates`, `get_idle_periods`) and autonomously selects the appropriate function based on semantic intent.
5. **Tool Execution (Observe)**: The Python environment executes the tool, directly querying the deterministic JSON data within `context.pkl`, entirely bypassing the LLM for calculations.
6. **Response Generation (Respond)**: The LLM receives the raw numbers from the tool and formats them into an explainable, professional natural language response, optionally returning the filepath to dynamically generated Matplotlib charts.
