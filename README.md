#  Multi-Agent Data Processor for AROL Telemetry

An autonomous, multi-agent pipeline designed to ingest, clean, analyze, and report on high-frequency industrial telemetry data from AROL capping machines. This system leverages CPU vectorization for high-speed deterministic processing and Google Gemini (via LangGraph) for natural language querying, ensuring zero mathematical hallucinations.

---

## Quickstart & Demo

### 1. End-to-End Evaluation Demo (Recommended)
To fulfill the project specifications, we provide an automated demo script. It runs the entire pipeline on your raw data and automatically generates multiple formatted Markdown reports without requiring manual user interaction.
```bash
# Ensure your data is in data/raw/
python demo.py
```
*This will generate `reports/kpi_quality_report.md` and `reports/anomaly_diagnostics_report.md`.*

### 2. Manual Pipeline Execution
If you prefer to run the core pipeline manually without generating the final markdown reports:
```bash
python main.py --input data/raw
```
*This processes all telemetry, creates `logs/pipeline.log`, and saves the state to `data/processed/context.pkl`.*

### 3. Launch the AI Bot Interface
Once the data is processed, you can chat with your data using the LangGraph Orchestrator Agent:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
python bot.py
```

---

##  Installation

Requires Python 3.10+.
```bash
git clone <repository_url>
cd multi-agent-data-processor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

##  Technical Documentation

To maintain a clean repository, all heavy technical documentation, design choices, and mathematical heuristics are located in dedicated files.

*  **[Main Design Choices (CPU vs GPU, Memory)](DOCUMENTATION.md)**
*  **[Architecture & Layers](docs/architecture.md)**
*  **[Data Schema & State Management](docs/data_schema.md)**
* **[Analytics Methods & Mathematics](docs/analytics_methods.md)**
*  **[Agent Decision Flow (LangGraph)](docs/agent_flow.md)**

---

## Testing

The project is backed by a robust suite of automated unit and integration tests.
```bash
python -m pytest tests/ -v
```

---

## Project Structure

```text
multi-agent-data-processor/
├── data/               # Raw input ZIPs and processed context caches
├── docs/               # Detailed technical documentation and diagrams
├── logs/               # Execution logs
├── reports/            # Output folder for generated Markdown reports
├── src/
│   ├── agents/         # MAS Agents (Ingestion, Quality, Analytics, Report, Orchestrator)
│   ├── analytics/      # Deterministic analytical functions
│   ├── cleaning/       # Data sanitization logic
│   └── config.py       # Centralized thresholds (IQR, Drift, etc.)
├── tests/              # Pytest suite
├── demo.py             # End-to-End evaluation script
├── bot.py              # Interactive AI CLI
├── main.py             # Main data processing pipeline
└── DOCUMENTATION.md    # High-level design choices and experimental evaluation
```