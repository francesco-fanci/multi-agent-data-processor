# Data Schema

The Multi-Agent Data Processor manages data across three distinct lifecycle schemas. This progressive transformation minimizes RAM footprint while maximizing computational speed and LLM readability.

---

## 1. Raw Telemetry Schema (Input)

The raw datasets pulled from the `data/raw/` ZIP archives are wide-format, time-series CSV matrices characterized by asynchronous, high-frequency PLC polling.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `timestamp` | `Datetime` | The exact microsecond the row was polled by the PLC. |
| `H01 Count` | `Integer` | The absolute cumulative counter of closures for Head 1. |
| `H01 AppTorque` | `Float` | The physical torque applied, measured in Nm (Newton-meters). |
| `H01 Status` | `Integer` | The raw machine-state code for Head 1 at that microsecond. |
| *(Repeated)* | ... | Columns are repeated dynamically for all 36 (or 48) heads. |

> **Note:** Because this schema is "wide", a single row contains the state of all heads simultaneously. The system dynamically scans column headers at runtime, ensuring it is never hardcoded to a specific number of heads.

---

## 2. Clean Event Schema (In-Memory)

Retaining the wide format is extremely inefficient for per-head analytics. During execution, the `DataQualityAgent` filters out "polling noise" (where the counter hasn't changed) and pivots the matrix into a narrow, **event-driven schema**. 

This schema is stored entirely in memory as a Pandas DataFrame, optimized with columnar SIMD types.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `timestamp` | `DatetimeIndex` | Used as the DataFrame index for lightning-fast time-series slicing. |
| `Head` | `String` | The identifier of the active head (e.g., `"H01"`, `"H36"`). |
| `Count` | `Integer` | The current value of the cumulative PLC counter. |
| `Previous Count` | `Integer` | The counter value during the previous valid event. |
| `Count Difference` | `Integer` | The discrete derivative (`Count - Previous Count`). Values > 0 indicate true physical closures. |
| `AppTorque` | `Float` | The physical torque applied during this specific event. |
| `Status` | `Integer` | The specific status code associated with this physical event. |

### PLC Status Code Mapping
The raw integer `Status` is classified into human-readable industrial events:
* **`0`**: `Closure OK` (Standard successful capping).
* **`2`**: `No Load` (Spindle rotated but no bottle/cap was present).
* **`65`**: `ClosureTorque reached but cap still rotating` (Thread failure/Stripped cap).
* **Other**: Handled dynamically as generic `Bad Closure` variants.

---

## 3. Distilled Knowledge Schema (Output)

Once the `AnalyticsAgent` finishes its deterministic computations, the massive event-driven DataFrame is purged from RAM to prevent crashes. 

The resulting insights are serialized into `context.pkl`—a highly structured dictionary schema purposefully designed to be queried instantly by the LLM (LangGraph tools) without cognitive overload or hallucination risks.

```json
{
  "data": {
    "first_timestamp": "2026-01-31 16:00:06",
    "last_timestamp": "2026-04-30 16:59:59",
    "total_cycles": 55888606,
    "production_pieces": 32202426
  },
  "success_metrics": {
    "overall": {
      "Closure OK": 31669636,
      "No Load": 23458288,
      "ClosureTorque reached but cap still rotating": 1072
    },
    "by_head": {
      "H01": { "Closure OK": 879511, "No Load": 651817 }
    }
  },
  "torque_results": {
    "H01": {
      "average": 2.0136,
      "standard_deviation": 0.0849,
      "min": 0.00,
      "max": 2.231
    }
  },
  "anomaly_stats": {
    "H01": {
      "count": 2941,
      "lowest_value": 0.0,
      "highest_value": 2.231
    }
  },
  "idle_periods": [
    {
      "start": "2026-02-15 08:00:00",
      "end": "2026-02-15 09:15:00",
      "duration_seconds": 4500
    }
  ],
  "drift_results": {},
  "top_residual_correlations": []
}
```

> **Why this matters for the AI:** When a user asks *"How many anomalies were on Head 1?"*, the LLM doesn't have to scan 55 million rows. It simply queries `context["anomaly_stats"]["H01"]["count"]`, guaranteeing a $O(1)$ lookup time and a mathematically un-hallucinatable answer.
