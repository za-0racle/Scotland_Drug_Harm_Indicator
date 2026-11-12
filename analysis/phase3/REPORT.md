# Phase 3 — completed audit, with acquisition limitation

Review date: 9 November 2026. No baseline output, frozen input, monitoring record, application file, Supabase table or policy was modified. No acquisition or audit process remains running. Phase 4 may proceed on the existing verified local sources; no newer observations have been admitted to the modelling series.

## Existing run verification

`python -m analysis.phase3.audit` verifies every saved output, input and source-code hash against the original run manifest, independently recomputes MAE/RMSE and interval coverage from exported predictions, and checks selected-model/cutoff agreement. All 18 recorded hashes match. The selected naive model, 2025 Q4 cutoff, 2026 Q1 target and 248 projection agree with Phase 2 records. `test_phase3.py` also regenerates the entire run in a temporary directory at its original timestamp and compares every artifact byte-for-byte, without overwriting the baseline.

The expanding backtest passes only each historical training prefix to the candidate model. Feature scales use that prefix. No direct target/future-data leakage was found. However, the current revised data vintage is not an as-published vintage, and the same 12 origins are used for model selection and performance reporting. Those are important evaluation limitations.

## Official newer-data findings

The [October RADAR report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-october-2026/about-this-release/printversion), published 27 October 2026 and inspected 9 November 2026, identifies Police Scotland data acquired by PHS on 7 September. Its suspected-death chart covers 27 May 2024–30 August 2026; the live [linked dashboard](https://scotland.shinyapps.io/phs-drugs-radar-dashboard/) advertises coverage from 25 December 2016. Live browser inspection confirmed its 27 October update (a cached search representation showed July and was not relied upon).

The headline 232 deaths covers **1 June–30 August 2026 (13 weeks)**. The preceding 320 covers **2 March–31 May**, not a calendar quarter. The separate monthly total 234 covers **1 June–31 August**, comprising June 70, July 88 and August 76. None is calendar Q1, Q2 or Q3. Weekly aggregates cannot be split at calendar-quarter boundaries without the requisite day-level information. No missing month or quarter was inferred.

Databelt-derived data from January 2025 replace manual divisional reporting in the newer releases. Quality assurance found differences and late COPFS cases can be added retrospectively; the latest release supersedes older figures. These operational suspected deaths are distinct from registered/confirmed NRS drug-related deaths, naloxone incidents, admissions and toxicology detections. The [legacy methodology annex](https://www.gov.scot/publications/suspected-drug-deaths-scotland-october-december-2025/pages/7/) also describes retaining originally suspected cases and a ten-day time adjustment. Equivalent timing and case-retention rules have not been established for the newer export.

Public download controls were located, but the acquisition command was **not executed**: automatic approval review could not complete because of a usage limit. It was not retried. `acquire_radar.mjs` is prepared but unexecuted; there is no saved raw export or source-snapshot checksum. `official_source_review.json` records inspected URLs, dates, attributed totals, definitions and this limitation. Do not confuse these audit transcriptions with a verified new model input series.

## Later evaluation decision

No exact, independently verified and definition-compatible calendar-quarter outcome was acquired. Therefore no later-period MAE, RMSE, errors, interval coverage or model reselection is reported. The original 12-origin development evaluation remains separate. Even a later successful comparison would be **retrospective**, because the Phase 2 artifact was issued in November after the 2026 Q1 outcome period. No prospective validation is claimed.

## Prediction intervals

Naive intervals assume stable, approximately Gaussian one-step errors, using the standard deviation of training first differences. Seasonal-naive uses lag-four differences; SES uses training residual SSE/(n-2); both are plug-in Gaussian approximations with lower bounds clipped at zero. NB2 uses conditional count-distribution quantiles, excluding parameter uncertainty. These are observation intervals, not monitoring limits. At the 12 development targets naive coverage was 11/12 for 80% and 12/12 for 95%, with mean 95% width 183.81 deaths. The small sample, broad bounds and post-selection reporting do not establish calibrated operational coverage.

## Proposed publication design

`proposed_forecast_schema.sql` is a design file outside the migration directory, not executed. It proposes a private `forecast_research` schema containing sources/vintages, runs, run-source links, values, intervals, evaluations and outcome cases. Foreign keys connect forecasts to model/training/run/source metadata. Publication dates and issue/execution dates are separate. New objects would default-deny; no public grants/policies are supplied. Existing objects are untouched. Publisher-side checks or triggers would still be needed for issue-before-target prospective claims, evaluation sample counts, interval nesting and observed-error consistency. Future publication must approve safe aggregates and read policies separately.

## Files and next step

Validation: **34 Python tests passed** with `python -m pytest analysis/tests -q -p no:cacheprovider`, including all Phase 2 tests and complete baseline artifact reproduction. Added `analysis/tests/conftest.py` uses ordinary inherited-permission workspace scratch directories because Windows mode-0700 pytest temporary directories are unreadable to the managed token. Scratch artifacts are kept under the already Git-ignored `analysis/test_scratch.local/`; no approval boundary or public-download block is bypassed.

Added only `analysis/phase3/__init__.py`, `audit.py`, `compatibility.py`, `acquire_radar.mjs`, `official_source_review.json`, `proposed_forecast_schema.sql`, this report, and `analysis/tests/test_phase3.py`. The acquisition remains blocked; resolve review availability before running it. Confirm exact calendar-period exports and a definition bridge before adding data or scoring the locked naive model. The next authorised implementation is Phase 4 local multi-dataset descriptive trends, not anomaly detection or dashboard integration.
