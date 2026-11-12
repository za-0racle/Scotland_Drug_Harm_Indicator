# Phase 3 audit closure and Phase 4 implementation — 10 November 2026

## Scope and status

Phase 3 was closed before starting Phase 4. No other audit/acquisition process is running. Phase 4 is implemented and executed locally. **Stop before Phase 5 pending user approval.** No dissertation, web-interface file, dependency, database record, RLS policy, frozen input, historical monitoring result or saved Phase 2 artifact was changed during this work. No deployment/publication occurred.

## Phase 3 findings

- All 18 recorded baseline input/code/output hash checks passed. Selected model, metrics, cutoff and forecast agree. All nine Phase 2 artifacts reproduced byte-for-byte in a separate scratch run at the original timestamp; the originals remained unchanged.
- The official October 2026 PHS RADAR release was inspected, including its live linked dashboard. Its 232 suspected deaths cover 1 June–30 August (13 weeks); 234 cover June–August calendar months. Neither is calendar Q3. Databelt replaces manual reporting from January 2025 and supports retrospective additions. Legacy ten-day timing and case-retention equivalence is unresolved.
- The public aggregate download command was not executed because automatic approval review could not complete due to a usage limit. It was not retried. No raw export/snapshot was acquired. The prepared acquisition script is not a completed download.
- No independently verified, compatible later calendar-quarter outcome was acquired. Later-period MAE/RMSE/errors/interval coverage are therefore not calculated. No observations were appended, no later-data model reselection occurred, and no prospective validation is claimed.
- Original interval methods remain approximate observation intervals: Gaussian training-difference errors for naive/seasonal naive; additive residual errors for SES; plug-in NB2 quantiles excluding parameter uncertainty. The small 12-target development sample and common selection/reporting period do not establish calibrated operational coverage.
- A private forecast schema is designed in `analysis/phase3/proposed_forecast_schema.sql`, outside the migrations folder. It separates source vintages, runs, run-source links, forecast values, intervals, evaluations and outcome cases. It remains unexecuted, with no public policies/grants. Cross-table publication/issue-time gates still need implementation and review before use.

Full source URLs, retrieval-review dates, compatibility details and limitations: `analysis/phase3/REPORT.md` and `official_source_review.json`. `audit_result.json` preserves machine-readable baseline checks and the explicit no-later-evaluation decision.

## Phase 4 work and verified findings

The package reads six existing local analytic sources plus the source metadata register. It computes exact-period changes, year-reference comparisons, complete-window rolling/reference means, complete annual sums, within-source rankings, original denominator-backed historical shares and explicitly labelled naloxone week-start-month groups. It preserves geography, non-calendar study periods, missing/suppressed values, overlapping substance groups and unknown publication dates. It does not calculate significance, anomaly classifications or risk scores.

Verified outputs: 504 mortality quarters (eight suppressed), 119 complete annual area totals (seven incomplete area-years excluded), 210 forensic count rows, 84 historical share rows, 72 ASSIST percentages, 140 treatment count rows, 7,024 separate-geography naloxone weeks, and 1,616 week-start-month groups. Missing source naloxone moving averages: 32; missing incident counts: zero.

Actual findings:

| Observation | Descriptive result |
| --- | --- |
| Scotland mortality, 2025 Q4 | 248; QoQ -14.78%; YoY +6.90%; four-quarter average 286.5. |
| Scotland mortality, 2025 | 1,146; +7.61% from 1,065 in 2024, in the frozen legacy series. |
| Forensic street benzodiazepines, 2026 Q1 | 97 detections; QoQ +31.08%, YoY -6.73%. |
| Forensic opioids, 2026 Q1 | 328 detections; QoQ -28.54%; no 2026 share inferred. |
| ASSIST benzodiazepines, source Q15 Feb–May 2026 | 79.21% of tested study samples; +9.98 percentage points from Q14; selected cohort, not national prevalence. |
| GG&C treatment stimulant detections, March 2026 | 336 urine-sample detections; MoM -7.95%; unchanged YoY. |
| Scotland ambulance naloxone, week beginning 25 May 2026 | 59 incidents; previous week -3.28%; four-week mean 60.75; 20.62% below prior-52-week mean. Not direct overdose incidence. |

Supported police-division comparisons remain correctly labelled. No Greenock-specific observations, population rates, case-study interface or cross-boundary joins were created. No outdated series is represented as a current threat. Detailed methods, sources and caveats are in `analysis/phase4/README.md`; machine-readable results are in its `outputs/` directory.

## Exact files added

Phase 3:

- `analysis/phase3/__init__.py`
- `analysis/phase3/audit.py`
- `analysis/phase3/compatibility.py`
- `analysis/phase3/acquire_radar.mjs` (prepared, not executed)
- `analysis/phase3/official_source_review.json`
- `analysis/phase3/proposed_forecast_schema.sql` (design, not executed)
- `analysis/phase3/audit_result.json`
- `analysis/phase3/REPORT.md`
- `analysis/tests/test_phase3.py`
- `analysis/tests/conftest.py` (workspace scratch directories using inherited permissions)

Phase 4:

- `analysis/phase4/__init__.py`
- `analysis/phase4/trends.py`
- `analysis/phase4/run.py`
- `analysis/phase4/README.md`
- `analysis/tests/test_phase4.py`
- `analysis/phase4/outputs/mortality_quarterly.csv`
- `analysis/phase4/outputs/mortality_annual.csv`
- `analysis/phase4/outputs/forensic_counts.csv`
- `analysis/phase4/outputs/frozen_forensic_shares.csv`
- `analysis/phase4/outputs/assist_percentages.csv`
- `analysis/phase4/outputs/treatment_counts.csv`
- `analysis/phase4/outputs/naloxone_weekly.csv`
- `analysis/phase4/outputs/naloxone_week_start_month.csv`
- `analysis/phase4/outputs/findings.json`
- `analysis/phase4/outputs/quality_report.json`
- `analysis/phase4/outputs/run_manifest.json`
- `analysis/PHASE3_PHASE4_RESULTS.md`

No pre-existing application or analysis source file was modified by this implementation. Earlier working-tree changes remain intact. Git-ignored test scratch files are under `analysis/test_scratch.local/`; an inaccessible failed pytest scratch attempt is under `analysis/phase3/validation.local/`. These contain only generated test artifacts, not application changes.

## Tests and commands

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase3.audit
.\analysis\.venv\Scripts\python.exe -m analysis.phase4.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
```

Final suite: **45 passed**. Coverage includes source matching, original run reproduction, leakage checks, forecast intervals/errors, compatibility rejection, exact period alignment, duplicate rejection, missing/zero handling, count validity, annual completeness, weekly-month grouping, rankings, geographic separation, denominator scope and reproducibility of Phase 4 CSV/findings/quality artifacts. The Phase 4 manifest is execution-timestamped; the non-timestamped artifacts were byte-identical across two test runs.

All eight original output hashes and ten Phase 4 output hashes were independently verified. The 2025 national annual sum was independently recomputed from quarterly exports as 1,146. `git diff --check` passed. JavaScript/build commands were not rerun because this phase did not change application code, dependencies or the UI; dashboard integration belongs to a later approved phase.

## Remaining limitations and next decision

Resolve the official-download approval-review availability before any acquisition retry. Do not compute later forecast scores until exact calendar periods and definitions are verified. Table 1 denominator extraction lineage, study recruitment/testing changes, unknown publication dates, non-calendar periods, stale cutoffs and suppressed regional cells constrain interpretation. Month-of-week-start sums cannot identify true calendar-month incidence. None of these descriptive changes is a statistical anomaly or validated warning.

The next recommended action is approval of **Phase 5 only**: dataset-appropriate, prior-only anomaly baselines; explicit insufficient-data states; parameter and false-signal sensitivity checks; and transparent research-evidence classes. Keep historical NB2-EWMA/CUSUM unchanged. No weighted risk score, official-alert claim, permission change, database publication, geographic case-study view or dashboard integration is authorised by that approval alone.
