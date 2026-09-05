# Analytics Methods

The `src/analytics/` and `src/cleaning/` modules implement a suite of deterministic, stateless heuristics over the raw telemetry data. Each method is designed to provide mathematically rigorous insights for the `AnalyticsAgent` and `DataQualityAgent`. 

Shared configurations and thresholds live in `src/config.py`.

---

## 1. `event_detection` (Closure Cycle Extraction)

**What it computes.** Extracts discrete physical machine cycles (closures) from a continuous, asynchronous high-frequency polling stream.

**Method.** Calculates the discrete derivative (difference) of the cumulative counter column for each head (`Count Difference = Current Count - Previous Count`). The system discards rows with a difference of 0 (polling noise) and registers rows with a difference > 0 as true physical events.

**Configuration.** Triggered across all 36+ dynamic head columns.

**Interpreting results.** Reduces dataset size by ~90% by discarding background PLC noise, leaving only exact timestamps of mechanical action.

**Limitations.** Assumes the PLC counter never decreases during normal operation. 

---

## 2. `data_quality_analysis` (Noise & Gap Detection)

**What it computes.** Classifies detected events into quality categories: Valid, Counter Recovery, Data Gap, and Counter Drops.

**Method.** 
- *Valid*: Normal incremental operation.
- *Counter Recovery*: Large positive counter increment occurring immediately after a counter value of zero.
- *Data Gap*: Time elapsed since the previous event exceeds the expected polling frequency significantly.
- *Counter Drops*: Negative counter differences indicating a reset.

**Configuration.** Evaluates PLC status codes mapped in `event_classifier.py` (`0`: Closure OK, `2`: No Load, `65`: ClosureTorque reached but cap still rotating).

**Interpreting results.** Ensures that statistical KPIs are not skewed by sudden machine restarts or missing telemetry files. 

**Limitations.** The system does not assume a specific mechanical cause for counter drops to zero, only flagging them for maintenance review.

---

## 3. `throughput_metrics` (Production KPIs)

**What it computes.** Two distinct operational speeds: *Machine Cycle Speed* and *Machine Production Speed*.

**Method.** 
- *Cycle Speed*: `total closure cycles / elapsed time` (includes No Load operations).
- *Production Speed*: `production pieces / elapsed time` (Production pieces = `Closure OK` + `Bad Closure`; strictly excludes `No Load` states).

**Configuration.** Speeds are aggregated globally and updated incrementally during chunk processing.

**Interpreting results.** A large divergence between Cycle Speed and Production Speed indicates the machine is running empty (starved of bottles or caps) for long periods. Speeds are expressed in pieces per hour (pcs/hr).

**Limitations.** Highly dependent on accurate timestamp bounding (`last_timestamp - first_timestamp`).

---

## 4. `torque_anomaly_detection` (IQR Statistical Outliers)

**What it computes.** Identifies statistically anomalous torque applications (either too high or too low) on a per-head basis.

**Method.** **Interquartile Range (IQR)**. Computes Q1 (25th percentile) and Q3 (75th percentile) for each head independently. An event is flagged as an anomaly if its `AppTorque` falls outside the bounds: $[Q1 - (3.0 \times IQR)]$ to $[Q3 + (3.0 \times IQR)]$.

**Configuration.** Defined in `src/config.py`:
- `ANOMALY_IQR_MULTIPLIER = 3.0` (Strict bounds to prevent false positives).
- `ANOMALY_MINIMUM_MARGIN = 0.05` Nm.
- `ANOMALY_MIN_EVENTS = 100` (Minimum sample size).

**Interpreting results.** A torque of exactly `0.00 Nm` will be correctly flagged as a severe anomaly (e.g., missing cap). These are statistical outliers, not necessarily confirmed hardware failures.

**Limitations.** Susceptible to flagging batch-wide changes (e.g., a harder batch of plastic caps) if the sample window is too short.

---

## 5. `torque_drift_tracking` (Fatigue Monitoring)

**What it computes.** Detects slow, gradual shifts in a head's baseline torque application, indicative of mechanical fatigue (e.g., relaxing tension springs).

**Method.** Moving Average Baseline. Compares the current daily torque average of a head against a historical moving average. 

**Configuration.** 
- `DRIFT_WINDOW_DAYS = 7` (Baseline calculation window).
- `DRIFT_THRESHOLD = 0.1` Nm (Minimum shift required to trigger a warning).
- `DRIFT_MIN_EVENTS = 500`.

**Interpreting results.** Identifies the magnitude (`difference`) and the `direction` (Increase/Decrease). Vital for predictive maintenance scheduling.

**Limitations.** Requires at least 7 days of continuous historical data to establish a reliable baseline.

---

## 6. `head_stress_correlation` (Shared Wear Analysis)

**What it computes.** The mathematical relationship between the torque behavior of different machine heads to find shared mechanical stress (e.g., heads mounted on the same faulty cam track).

**Method.** Pearson Correlation matrix applied to **Residual Torque**. The global daily machine average is subtracted from the head's daily average to isolate the head's unique variance from environmental noise.

**Configuration.** Computed dynamically across an $N \times N$ matrix.

**Interpreting results.** High positive residual correlation between two heads suggests they are being affected by the same localized mechanical issue.

**Limitations.** Correlation does not imply causation. Two heads opposite each other may correlate due to harmonic vibrations rather than direct structural links.

---

## 7. `idle_downtime_detection` (No Load Sustained)

**What it computes.** Identifies true machine downtime vs momentary pauses.

**Method.** Scans for contiguous time blocks where *all 36 machine heads* simultaneously report `Status = 2` (No Load). 

**Configuration.** 
- `IDLE_MIN_DURATION_SECONDS = 60` (Ignores micro-stops).
- `IDLE_MAX_GAP_SECONDS = 2` (Ensures continuity).

**Interpreting results.** Returns the start timestamp, end timestamp, and total duration (in seconds) of the halt.

**Limitations.** If even one head misreports its status due to sensor lag, the idle period might be fragmented into two shorter blocks.
