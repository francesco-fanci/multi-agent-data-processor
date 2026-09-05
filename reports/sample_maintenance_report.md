# AROL Capping Machine - Predictive Maintenance Report

## 1. Goal
Identify mechanical wear and torque drifts to enable predictive maintenance.

## 2. Data Overview
* **Time Range:** 2026-02-01 to 2026-02-28
* **Total Cycles Analyzed:** 1,248,320

## 3. Mechanical Findings
* **Torque Anomalies (Statistical Outliers):** 124 detected across all heads.
* **Torque Drift Events:** 2 (Head 05 and Head 12 showing decreasing baseline torque).

### 3.1 High-Risk Heads
* **H05:** 89 anomalies (Min Outlier: 0.95 Nm)
* **H12:** Shows strong inverse correlation with H22 (-0.85).

## 4. Confidence & Limits
* Torque anomalies are statistical outliers and do not directly indicate confirmed machine failures.
* Correlation between heads does not imply causation.

## 5. Next Checks
* Review detected torque drifts on Head 05 with the maintenance team (possible spring wear).
* Investigate mechanical stress distribution between Head 12 and Head 22.
