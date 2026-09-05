# AROL Capping Machine — Anomaly & Diagnostics Report

**Observation Period**: 2026-01-31 16:00:06 to 2026-04-30 16:59:59

## High-Level Hardware Diagnostics

- **Total Torque Anomalies (IQR Method):** 104,462
- **Total Torque Drift Events:** 468

## Per-Head Anomaly Breakdown

Components ranked by statistical outlier frequency. High anomaly counts may suggest mechanical wear, spring fatigue, or sensor calibration issues.

| Rank | Head | Anomalies Detected | Lowest Peak | (Timestamp) | Highest Peak | (Timestamp) |
|---|---|---|---|---|---|---|
| 1 | **H09** | 2,945 | 0.00 Nm | *2026-02-01 02:02:56* | 2.29 Nm | *2026-03-01 22:47:05* |
| 2 | **H01** | 2,941 | 0.00 Nm | *2026-02-01 02:04:27* | 2.23 Nm | *2026-04-09 07:07:54* |
| 3 | **H14** | 2,935 | 0.00 Nm | *2026-02-01 02:04:28* | 2.21 Nm | *2026-02-28 15:57:07* |
| 4 | **H05** | 2,929 | 0.00 Nm | *2026-02-01 02:04:28* | 2.21 Nm | *2026-03-03 16:59:31* |
| 5 | **H13** | 2,927 | 0.00 Nm | *2026-02-01 02:02:56* | 2.32 Nm | *2026-02-01 14:33:09* |
| 6 | **H17** | 2,923 | 0.00 Nm | *2026-02-01 02:04:09* | 2.28 Nm | *2026-02-13 05:52:52* |
| 7 | **H11** | 2,921 | 0.00 Nm | *2026-02-01 02:02:56* | 2.21 Nm | *2026-04-11 09:46:33* |
| 8 | **H20** | 2,921 | 0.00 Nm | *2026-01-31 23:16:01* | 2.28 Nm | *2026-04-22 17:58:23* |
| 9 | **H35** | 2,910 | 0.00 Nm | *2026-02-01 02:04:27* | 2.51 Nm | *2026-02-19 22:09:49* |
| 10 | **H12** | 2,909 | 0.00 Nm | *2026-02-01 00:22:55* | 2.56 Nm | *2026-02-24 04:01:21* |
| 11 | **H29** | 2,909 | 0.00 Nm | *2026-02-01 02:04:27* | 2.46 Nm | *2026-02-15 22:52:55* |
| 12 | **H18** | 2,907 | 0.00 Nm | *2026-02-01 02:04:21* | 2.29 Nm | *2026-03-03 14:06:10* |
| 13 | **H06** | 2,906 | 0.00 Nm | *2026-02-01 02:02:56* | 2.23 Nm | *2026-01-31 23:59:16* |
| 14 | **H31** | 2,905 | 0.00 Nm | *2026-02-01 02:04:27* | 2.20 Nm | *2026-02-28 13:21:14* |
| 15 | **H02** | 2,904 | 0.00 Nm | *2026-02-01 02:03:28* | 2.74 Nm | *2026-02-17 04:54:27* |
| 16 | **H24** | 2,903 | 0.00 Nm | *2026-02-01 02:04:29* | 2.28 Nm | *2026-02-20 07:42:15* |
| 17 | **H32** | 2,902 | 0.00 Nm | *2026-02-01 02:04:27* | 2.39 Nm | *2026-03-03 17:12:30* |
| 18 | **H16** | 2,900 | 0.00 Nm | *2026-02-01 02:04:28* | 2.34 Nm | *2026-03-02 16:27:54* |
| 19 | **H08** | 2,899 | 0.00 Nm | *2026-02-01 02:02:56* | 2.21 Nm | *2026-02-28 13:29:09* |
| 20 | **H23** | 2,897 | 0.00 Nm | *2026-02-01 02:04:26* | 2.33 Nm | *2026-02-04 06:12:50* |
| 21 | **H03** | 2,896 | 0.00 Nm | *2026-02-01 02:04:28* | 2.21 Nm | *2026-02-28 13:27:59* |
| 22 | **H36** | 2,896 | 0.00 Nm | *2026-02-01 02:04:27* | 2.21 Nm | *2026-03-03 16:59:26* |
| 23 | **H33** | 2,894 | 0.00 Nm | *2026-02-01 02:04:27* | 2.21 Nm | *2026-02-28 13:24:34* |
| 24 | **H04** | 2,893 | 0.00 Nm | *2026-02-01 02:04:28* | 2.32 Nm | *2026-03-01 09:28:42* |
| 25 | **H15** | 2,893 | 0.00 Nm | *2026-02-01 02:04:28* | 2.20 Nm | *2026-02-28 13:25:03* |
| 26 | **H19** | 2,892 | 0.00 Nm | *2026-02-01 02:04:29* | 2.43 Nm | *2026-03-01 04:44:07* |
| 27 | **H27** | 2,892 | 0.00 Nm | *2026-02-01 02:04:27* | 2.39 Nm | *2026-02-02 18:01:54* |
| 28 | **H34** | 2,889 | 0.00 Nm | *2026-02-01 02:04:27* | 2.21 Nm | *2026-03-03 16:59:24* |
| 29 | **H25** | 2,887 | 0.00 Nm | *2026-02-01 02:04:27* | 2.20 Nm | *2026-03-03 17:23:53* |
| 30 | **H21** | 2,885 | 0.00 Nm | *2026-02-01 02:04:29* | 2.21 Nm | *2026-02-28 13:23:48* |
| 31 | **H22** | 2,883 | 0.00 Nm | *2026-01-31 23:25:17* | 2.23 Nm | *2026-02-03 14:35:08* |
| 32 | **H07** | 2,882 | 0.00 Nm | *2026-02-01 02:02:56* | 3.13 Nm | *2026-03-14 16:23:43* |
| 33 | **H26** | 2,881 | 0.00 Nm | *2026-02-01 02:04:27* | 2.24 Nm | *2026-04-24 10:16:50* |
| 34 | **H10** | 2,871 | 0.00 Nm | *2026-02-01 02:02:56* | 2.20 Nm | *2026-02-28 15:04:32* |
| 35 | **H30** | 2,870 | 0.00 Nm | *2026-02-01 02:04:27* | 2.33 Nm | *2026-02-03 21:17:29* |
| 36 | **H28** | 2,865 | 0.00 Nm | *2026-02-01 02:04:27* | 2.21 Nm | *2026-02-28 12:38:06* |

## Severe Torque Drifts

Detects gradual shifts in baseline torque application. Listed by magnitude of drift.

| Head | Date | Baseline Torque | Shifted Torque | Difference | Direction |
|---|---|---|---|---|---|
| **H09** | 2026-03-31 | 1.6862 | 2.1965 | **0.5103** | Increase |
| **H16** | 2026-03-31 | 1.6878 | 2.1974 | **0.5096** | Increase |
| **H08** | 2026-03-31 | 1.6884 | 2.1978 | **0.5094** | Increase |
| **H14** | 2026-03-31 | 1.6880 | 2.1969 | **0.5090** | Increase |
| **H07** | 2026-03-31 | 1.6861 | 2.1950 | **0.5089** | Increase |
| **H15** | 2026-03-31 | 1.6884 | 2.1965 | **0.5081** | Increase |
| **H17** | 2026-03-31 | 1.6895 | 2.1976 | **0.5081** | Increase |
| **H13** | 2026-03-31 | 1.6891 | 2.1971 | **0.5080** | Increase |
| **H03** | 2026-03-31 | 1.6867 | 2.1947 | **0.5079** | Increase |
| **H26** | 2026-03-31 | 1.6893 | 2.1971 | **0.5078** | Increase |

## Machine Downtime (Idle Periods)

- **Total Idle Instances:** 3,489
- **Total Idle Time:** 1418.30 ore
- **Longest Continuous Idle:** Da *2026-04-26 07:33:10* a *2026-04-28 18:47:44* (3554.6 minuti)

## Structural Stress (Top Residual Correlations)

Residual correlations highlight strong mechanical relationships between specific heads, neutralizing machine-wide trends. Useful for identifying shared subsystem vibrations.

| Head A | Head B | Pearson Correlation |
|---|---|---|
| **H21** | **H24** | 0.9010 |
| **H24** | **H25** | 0.8638 |
| **H06** | **H21** | -0.8550 |
| **H22** | **H25** | 0.8420 |
| **H06** | **H24** | -0.8375 |
| **H16** | **H21** | -0.8277 |
| **H22** | **H24** | 0.8225 |
| **H21** | **H25** | 0.8217 |
| **H17** | **H18** | 0.8051 |
| **H16** | **H24** | -0.7949 |

## Recommendations & Next Checks

- [ ] Review detected torque drifts and anomalies with machine context.
- [ ] Investigate long idle periods.
- [ ] Review strong residual correlations between heads.
- [ ] Confirm AppTorque measurement unit from machine documentation.

## Confidence Limits (AI Transparency)

- *Torque anomalies are statistical outliers and do not directly indicate machine failures.*
- *Correlation between heads does not imply causation.*
- *Production speed is an average over the observed time interval.*
- *Unit validation: Missing unit metadata: AppTorque*
