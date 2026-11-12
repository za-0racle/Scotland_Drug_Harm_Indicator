# Phase 5: local research anomaly screening

Approved scope: Python analysis only. No UI, database access, permission changes, new dependencies, private narratives or deployment. The historical NB2-EWMA/CUSUM and all Phase 2/3/4 artifacts remain independent and unchanged. These new screens are retrospective research signals, not forecasts or official alerts.

## Run and inspect

From the repository root:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase5.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
```

Only `analysis/phase5/outputs/` is written by default. `--output-dir` accepts a path inside a `.local` scratch directory. Saved Phase 4 inputs, code and sources are checked against their manifest; Phase 2 audit checks and complete protected artifact hashes run before and after execution. The manifest records Python version, code/test hashes, source/artifact hashes and execution time. All other outputs are deterministic for these inputs/configurations. No network acquisition is attempted.

## Statistical design

Counts are screened independently for each source, indicator, exact geography, period basis and unit. Only the immediately preceding **complete** window of exact ordinal periods is used. Neither the observation being screened nor later observations contribute. A missing/suppressed reference cell invalidates the window; current suppression makes analysis unavailable. Duplicates and invalid counts fail. No smoothing or imputation occurs.

Reference centre is the prior median; scale is `max(1.4826 * median absolute deviation, sqrt(max(median, 1)))`. The normal-consistency MAD multiplier is a scale convention, **not evidence that errors are normal**. The count-scale floor prevents zero-MAD and tiny low-count reference scales from creating arbitrarily narrow bounds. It is a pragmatic safeguard, not a fitted Poisson/NB2 model. Bounds are `[max(0, median - k*scale), median + k*scale]`; only strict exceedances flag. A zero lower bound cannot create a lower alarm. The stored robust score is not a calibrated z-test statistic. Bounds are neither forecast intervals nor NB2-EWMA/CUSUM limits.

| Dataset | Primary reference | Sensitivity windows | Rationale and limits |
| --- | ---: | --- | --- |
| Mortality, national and separate police divisions | 16 quarters | 12, 16 | Three/four annual cycles, low parameter count; suppression invalidates windows. No population rates, seasonality or trend adjustment. Legacy timing/revisions remain. |
| Forensic detection counts | 16 quarters | 12, 16 | Same count screen over several annual cycles, separately per overlapping substance group; testing volume/selection and missing denominators prevent prevalence or causal-death inference. |
| Treatment urine detections | 18 months | 12, 18 | One versus one-and-a-half annual cycles given only 28 observations. Small reference samples and testing-volume changes constrain interpretation. |
| Ambulance naloxone | 104 weeks | 52, 104 | One/two full-year windows, separate boards/national/Unknown; robust scale limits individual extreme influence. Not seasonally adjusted, direct overdose incidence or take-home supply. |
| ASSIST percentages | None | None | Only 12 unequal study periods, shortened Q9, unknown denominators and exact dates: `insufficient_data`; no binomial/count model or calendar reassignment. |
| Frozen forensic shares | None | None | Only 12 quarters with unresolved independent denominator lineage; `insufficient_data`. Historical CUSUM unchanged. |

Primary `k=3`; sensitivity `k=2.5,3,3.5` across both windows. Windows/thresholds are pragmatic research settings rather than tuned optimal rules. No threshold has a validated false-alarm probability here. Larger windows may lag structural changes; smaller windows can be unstable. Low-count floor activation and missing-window exclusions are counted for every indicator/geography/configuration. Annual totals and week-start-month sums are excluded to avoid duplicate monitoring and variable monthly weekly exposure.

Classifications: `no_detected_anomaly`, `statistically_unusual_observation`, `insufficient_data`, `unavailable_analysis`. These refer to screen eligibility/exceedance, not clinical significance. `reason`, reference count/completeness, source quality, publication dates, cutoffs and limitations accompany results. Ordinary Phase 4 percentage changes are never used as anomaly tests. Historical fixed-vintage analysis cannot establish as-issued warning timing.

## Evidence framework

Assess only exact geography, period label/bounds/basis and measurement-domain matches. No police-division/health-board joins, substance-name harmonisation, ASSIST calendar conversion or publication-date inference. A shared drug label does not establish equivalent outcomes. Default domains retain source indicator IDs. This deliberately prevents unsupported cross-source corroboration in these inputs.

One source with a flag yields `single_indicator_signal`; compatible same-direction flags from multiple sources would yield `multiple_supporting_indicators`. Opposite-direction flags yield `conflicting_indicators`; unflagged eligible screens yield `no_detected_signal` only when the group is fully assessed; otherwise `insufficient_evidence`. Multiple categories in one source cannot establish multi-source support. An unflagged indicator does not contradict a flagged one. Different sources may share cases: no independence or causality claim is made. These are historical evidence classes. Every current assessment is explicitly `insufficient_evidence` because cutoffs are stale, publication vintages incomplete and contextual harmonisation unavailable.

RADAR intelligence remains an explicit contextual gap: no private narrative is read or exported, and non-calendar reporting periods are not mapped speculatively. ASSIST/treatment/forensic indicators are assessed within their own measurement definitions; no absence-of-harm conclusion follows from lack of corroboration. No weighted risk score or confirmed-alert label is produced.

## Outputs and interpretation

- `anomaly_results.csv`: all observations, classification, method/parameters, original value, prior reference bounds/completeness, baseline/scale/threshold, direction, geography/substance and source provenance.
- `monitoring_configurations.json`: formulas, windows, threshold grid and selection rationale.
- `sensitivity_results.csv`: all attempted versus eligible choices, signal fraction and persistence for each screened observation.
- `signal_frequencies.json`: per-series/configuration observed flag counts/frequencies, exclusions and count-floor usage.
- `evidence_assessments.json`: compatible historical groups, supporting/unavailable indicators, publication dates, contextual gaps and current insufficiency.
- `quality_report.json`, `source_provenance.json`, `run_manifest.json`: quality, limitations, preserved inputs and hashes.
- `FINDINGS.md`: actual computed counts and all national-series flags. CSV contains all regional and substance flags.

All-choice persistence requires the same-direction flag across **all six** choices; incomplete windows cannot count as agreement. A signal can be choice-sensitive even when the primary setting does not flag. Historical signal frequencies are **not false-positive rates**: no adequate reference-event dataset exists. There is no validated sensitivity, specificity, detection lead time or operational threshold. Serial correlation, multiple comparisons, temporal trends, changing testing practices and revisions may create statistical flags. No claim of calibrated coverage or significance is made.

Tests cover prior-only references, future invariance, boundaries/directions/zero floors/MAD, suppressed/missing history, duplicate/invalid counts, geography/measurement separation, incompatible periods/domains, evidence classes, sensitivity denominators, real-data provenance, preservation and repeated-run reproducibility. The full suite additionally reproduces Phase 2 and Phase 4 outputs.

Stop after Phase 5. A separately approved next step should review methods and obtain compatible source vintages, testing denominators and contextual event definitions before any database or interface publication.
