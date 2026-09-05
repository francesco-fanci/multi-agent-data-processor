# Methodology and Data Logic

This document details the analytical heuristics and mathematical rules implemented by the Multi-Agent Data Processor.

## Event Detection
Closure events are detected by comparing the cumulative counter of each head with its previous value.
For each head:
`Count Difference = Current Count - Previous Count`
A positive difference represents one or more closure cycles.

The detected event contains:
- timestamp
- head
- current count
- previous count
- count difference
- AppTorque
- machine status

## Status Classification
The currently known status codes are:
* **0**: Closure OK
* **2**: No Load
* **65**: Bad Closure
* **other**: Unknown (intentionally preserved)

## Data Quality
Detected events are classified into the following data-quality categories:

* **Valid**: The event is considered valid.
* **Counter Recovery**: A large positive counter increment occurring after a previous counter value of zero. These events are excluded from the cleaned event set because they may represent counter reinitialisation rather than real production.
* **Data Gap**: An event occurring after an unusually large timestamp gap. Data Gap events are retained but explicitly marked.
* **Counter Drops**: Negative counter differences are analysed separately. Counter drops to zero may be consistent with counter resets or reinitialisation, but the software does not assume a specific machine cause.

## Production KPIs
Two production speed metrics are calculated.

### Cycle Speed
Based on the total number of counter increments.
`cycle speed = total closure cycles / elapsed time`
The result is expressed in pieces per hour.

### Production Speed
Production pieces include:
* Closure OK
* Bad Closure
No Load events are excluded from production.
`production speed = production pieces / elapsed time`
The system updates production speed incrementally while processing consecutive files.

## Torque Analysis
Torque analytics are performed independently for every machine head. Calculated statistics include number of events, average, standard deviation, minimum, maximum, and number of zero values. The physical unit of `AppTorque` is not specified in the available dataset and the project does not assume one.

## Daily Torque Trend
The system calculates daily torque averages for each head. A configurable moving average is also calculated to highlight longer-term behaviour (default 7 days).

## Torque Drift Detection
Torque drift is detected by comparing the current daily average with a baseline calculated from previous days.
Main configuration parameters (from `src/config.py`):
* `DRIFT_WINDOW_DAYS = 7`
* `DRIFT_THRESHOLD = 0.1`
* `DRIFT_MIN_EVENTS = 500`

## Torque Anomaly Detection
Torque anomalies are detected statistically using the interquartile range (IQR).
* `ANOMALY_IQR_MULTIPLIER = 3.0`
* `ANOMALY_MINIMUM_MARGIN = 0.05`
* `ANOMALY_MIN_EVENTS = 100`
Detected anomalies are statistical outliers. They do not automatically represent machine failures.

## Head Correlation Analysis
The system calculates correlations between machine heads using their daily torque behaviour.
* **Raw Correlation**: Calculated directly from daily head averages.
* **Residual Correlation**: The machine-wide daily average is removed before calculating correlation. This helps reduce common machine-level trends and highlight relationships that may be more specific to individual heads.

## Idle Period Detection
The system identifies periods where all 36 machine heads simultaneously have `Status = 2` (No Load).
A period is considered idle when the condition is sustained for at least `IDLE_MIN_DURATION_SECONDS = 60`. The algorithm also verifies continuity between timestamps (`IDLE_MAX_GAP_SECONDS = 2`).
