# Phase 5C implementation — 10 November 2026

## Scope and implemented functionality

Phase 5C adds working local Python analytical modules and actual versioned outputs. It does not replace Phase 2 forecasts, Phase 4 trends, the original 47 Phase 5 flags or historical NB2-EWMA/CUSUM. No application file, database table, RLS policy, migration, dependency or dissertation was changed. No deployment, new current forecast or publication occurred. FOI remains pending; no real alert record was created or imported.

The implementation reviewed existing phase code/reports, forecasting modules, `src/database.js`, `src/supabase.js`, `src/main.js`, the documented schema in `docs/supabase-integration-review.md` and the existing migration text. The frontend still reads the three approved aggregate/model tables with explicit columns. No live Supabase schema/state verification was attempted in this analytical phase; local documentation is not a claim that production was re-audited.

New modules implement:

- A six-dataset source compatibility registry with source/sample/measurement/substance/geography/period/denominator/completeness/dependence metadata.
- Candidate-level cross-source comparison of actual observations, with original and separately computed monitoring states, all compatibility dimensions and explicit incompatible/unresolved outcomes.
- Four prior-only conditional count-model candidates, rolling-origin distribution evaluation, sparse/zero-baseline comparisons and descriptive diagnostics.
- Consecutive statistical run grouping with exact configuration/geography/source-family separation and original observation IDs.
- A source-gap register, verified source-review notes, local-asset inventory and geographic dashboard data contract; no dashboard.
- A callable, local JSON FOI staging/validation CLI with original records, source hashes, quarantine and permanently closed external-metric/publication gates in this version.

See `README.md` for complete formulas, commands and interpretation rules. Model references use only exact prior periods; no source observations are interpolated, combined into prevalence or joined to incompatible population denominators.

## Actual cross-source progress

There are **2,256 distinct two-observation candidate comparisons**, replacing Phase 5's singleton-only evidence processing:

| Compatibility outcome | Candidate pairs |
| --- | ---: |
| Compatible contextual evidence | 646 |
| Incompatible | 1,592 |
| Unresolved mapping | 18 |

These are pair-level comparisons, not independent episodes or confirmed evidence groups. Candidate families are national mortality versus overlapping national naloxone/forensic observations; forensic versus treatment/frozen shares; and latest forensic versus final source-labelled ASSIST observations. Other possible pair families are outside this declared universe. The same quarterly observation can appear in multiple pairs; no count is an independent event denominator.

The 646 contextual pairs permit a comparison, but do not equate national forensic sampling with population rates, weekly counts with quarterly totals or distinct collections with independent people. Local treatment versus national forensic scope is rejected as a matched geography; forensic counts versus historical shares cannot independently corroborate their own underlying source; ASSIST's missing exact dates remain unresolved. No source boundary or substance mapping invents local effects.

| Evidence result | Original robust states | NB2-moments states |
| --- | ---: | ---: |
| Compatible context, monitoring states unavailable | 277 | 277 |
| No joint detected signal, not evidence of no harm | 359 | 364 |
| Single signal with unflagged context | 10 | 5 |
| No compatible cross-source evidence | 1,610 | 1,610 |
| Supporting or opposing joint contextual signals | 0 | 0 |

Thus **actual cross-source comparisons now execute, but no joint directional contextual signal is established in the declared pairs under either method**. This is a documented result, not a forced confirmation. There are 369 pairs with both states assessable in each method. Historical publication availability remains unknown/not as-issued; no current early-warning or causal claim follows. The engine has tested supporting/opposing branches but the actual data do not exercise them.

## Alternative model findings and original-flag comparison

Each model uses complete prior history only; primary enhanced flags use strict exceedance of a discrete 99% predictive interval. Robust k=3 bounds have no equivalent established nominal coverage. Models are compared, **not selected or promoted** by flag count or apparent agreement.

| Method | Successful historical origins | Enhanced flags at 99% |
| --- | ---: | ---: |
| Stationary Gamma–Poisson | 5,764 | 240 |
| NB2 moments / Poisson boundary | 5,764 | 40 |
| Seasonal Gamma–Poisson | 4,050 | 151 |
| Log-linear trend Poisson | 404 | 48 |

The seasonal method requires four same-phase observations: quarterly history uses 16 quarters; weekly history uses 208 weeks, with approximate 52-week seasons. The 18-month treatment series cannot meet four annual-cycle requirements. Weekly trend-only Poisson is not applied because seasonal/recording-break specification is unresolved. Model exclusions, warnings and denominators are explicit in every result and summary.

For the same **20 national mortality targets, 2021 Q1–2025 Q4**, all four candidates are available:

| Method | 95% interval coverage | Mean negative log predictive score | Mean 95% interval score |
| --- | ---: | ---: | ---: |
| Gamma–Poisson | 65% | 6.1260 | 358.35 |
| NB2 moments | 95% | 5.1476 | 180.10 |
| Seasonal Gamma–Poisson | 75% | 5.8117 | 298.50 |
| Trend Poisson | 55% | 6.6828 | 449.75 |

Lower log/interval scores are preferable within this comparable set. This supports further investigation of overdispersed count distributions for this series, **not a claim of established calibration or superiority on independent data**. Twenty correlated revised-vintage targets are a small retrospective comparison; the Phase 2 naive forecast's original evaluation/model selection is unchanged. Coverage near 95% alone does not validate an operational model. Full series-level available/common-origin metrics, eligible participants and interval widths are saved separately; source-wide pooling must not imply independent observations.

NB2-moments versus the original 47 robust flags over the same 5,764 eligible observations:

- 20 observations flag under both approaches (direction and exact bounds remain in the output).
- 27 original flags do not flag under NB2-moments.
- 20 NB2-moments flags are not original robust flags.
- 5,697 observations flag under neither.

These disagreements reflect both distribution assumptions and different bound construction; they are not counts of corrected false alarms or newly confirmed events. All 47 original flags remain available unchanged.

### Unknown geography and sparse-count findings

All six original Unknown-geography naloxone flags were retained and re-evaluated. Five had persisted across the Phase 5 grid. Their observed values and conditional 99% upper limits show sensitivity beyond the original median/MAD scale floor:

| Week beginning | Observed | Original upper bound | Gamma–Poisson upper99 | NB2 upper99 | Seasonal upper99 | NB2 flag |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2024-02-12 | 6 | 3 | 3 | 3 | 4 | Increase |
| 2024-04-08 | 4 | 3 | 3 | 4 | 3 | None |
| 2025-06-16 | 4 | 3 | 3 | 5 | 3 | None |
| 2025-09-08 | 5 | 3 | 3 | 5 | 5 | None |
| 2026-02-23 | 7 | 3 | 3 | 5 | 2 | Increase |
| 2026-04-06 | 4 | 3 | 4 | 6 | 5 | None |

Only two of the five previously persistent Unknown flags exceed the NB2 conditional 99% bounds; observations were not discarded or reassigned. This demonstrates model dependence of the original robustness claim. It does not prove the other observations were false signals. With an entirely zero prior window NB2 dispersion is unidentifiable and yields insufficient data; Gamma–Poisson remains mathematically defined but its interval may still be narrow under its assumptions. Zero inflation, the Gamma prior and sampling changes need further calibration. Unknown remains unassigned geography and cannot identify a hotspot.

## Signal-run analysis

The original 47 observations form **44 statistical runs: 43 isolated flags and one sustained four-quarter decline in forensic street benzodiazepines, 2024 Q4–2025 Q3**. Peak original scaled deviation is -3.5683 in 2025 Q2. All four original observation IDs and values remain traceable. Other original simultaneous areas/categories are not merged.

Enhanced methods have their own run/configuration sets: Gamma–Poisson 140 isolated plus 34 sustained; NB2-moments 38 isolated plus one sustained; seasonal Gamma–Poisson 73 isolated plus 24 sustained; trend Poisson 32 isolated plus six sustained. Different modelling methods, windows and deviation units remain separate. A sustained statistical run is not a confirmed toxicity incident or an independent-event label.

## Source gaps and geographic readiness

**Partially resolved:** explicit scope/category aliases and incompatible boundaries are now machine-readable; source dependencies and undated periods are classified rather than silently excluded; source recording-change context is documented; Inverclyde council data availability is verified at workbook-metadata level; future FOI validation is executable.

The official [PHS January 2025 report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-january-2025/), published 28 January 2025 and reviewed 10 November 2026, identifies a naloxone clinical recording-system rollout from April 2024. This is a potential measurement break. Its board-specific impact is not quantified; no count adjustment or attribution was made. Prior-only diagnostics and the gap register retain that uncertainty.

Local `nrs_drd_2024_data.xlsx`, `Table_C1`, explicitly contains an Inverclyde column of annual **registered drug misuse deaths**, 2010–2024. This is an identified unintegrated case-study asset; no count was imported into the suspected-death series. Local health-board population data extend through 2025 but do not establish a compatible police-division denominator. SDMD `NumberAssessed` is a different population/outcome from monthly urine tests. The local naloxone FOI `.xls` is binary OLE and was not parsed by the existing openpyxl environment. No dependency was added or denominator guessed.

**Unresolved:** forensic/treatment testing denominators; ASSIST exact dates and sample sizes; testing-panel and category-history equivalence; original frozen-share extraction lineage; source-specific publication vintages; legacy/Databelt mortality equivalence; full recording-rollout effects; compatible external event labels and the pending FOI response. No additional dataset download was retried after the earlier approval-review blocker. Ten gap-register entries document affected analysis, exact requirement/workaround and interpretation consequence; engineering progress is not represented as resolution of missing data.

The geographic contract distinguishes Greenock locality, Inverclyde council, Renfrewshire and Inverclyde police division, NHS GG&C and Scotland. Police-division mortality trends and GG&C treatment/naloxone context are available at their original wider boundaries. Greenock has no admitted mortality/toxicity series. Population rates are not computed. The dashboard data contract requires precise boundary labels, source cutoffs, measurements, limitations and an explicit no-compatible-local-data state. No geographic dashboard was built.

## FOI readiness and external validation hold

`python -m analysis.phase5c.foi input.json new-local-staging.json` is an implemented adapter for a reviewed JSON extraction of the future response. It preserves submitted records and input hash, refuses overwrites, checks dates/IDs/versions/status fields and response metadata, detects duplicate versions and unresolved revision parents, and quarantines ambiguous records. Extraction of an actual PDF/workbook/email remains a human-reviewed upstream task. Original attachments, uncertain raw dates and field-specific missingness notes must be retained.

All automated alert fixtures are clearly labelled synthetic test data; none is saved as an actual alert output. The generated FOI artifact is a specification, not a populated alert table. Even a syntactically valid “complete” response cannot open the external-evaluation/publication gate in this version. No record was written to `radar_alerts`. Missing local/FOI records never establish no-alert periods. Operational sensitivity, specificity, precision, false-warning rate and lead time remain unavailable pending completeness, compatibility and a predefined protocol. Internal methodological comparison and external alert validation remain distinct.

## Exact files and verification

New source/documentation files only:

- `analysis/phase5c/__init__.py`
- `analysis/phase5c/models.py`
- `analysis/phase5c/compatibility.py`
- `analysis/phase5c/runs.py`
- `analysis/phase5c/sources.py`
- `analysis/phase5c/foi.py`
- `analysis/phase5c/run.py`
- `analysis/phase5c/README.md`
- `analysis/phase5c/IMPLEMENTATION_REPORT.md`
- `analysis/tests/test_phase5c.py`

Generated under `analysis/phase5c/outputs/`: `source_compatibility_registry.json`, `cross_source_candidates.json`, `cross_source_evidence.json`, `enhanced_model_results.csv`, `model_evaluation_metrics.csv`, `statistical_diagnostics.csv`, `signal_runs.json`, `robustness_comparisons.csv`, `zero_baseline_review.json`, `source_gap_register.json`, `geographic_evidence.json`, `foi_staging_specification.json`, `official_source_review.json`, `local_source_inventory.json`, `observation_index.csv`, `summary.json` and `run_manifest.json`.

No pre-existing source or research output file was modified by this phase. Research scratch outputs are stored under the existing ignored `analysis/test_scratch.local/`.

Actual executed commands and results:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase5c.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
git diff --check
```

**73 Python tests passed in 251.23 seconds**: all 61 existing tests plus 12 new Phase 5C tests. The new suite covers source/substance/geographic/time/dependence compatibility, contextual evidence branches, count-distribution assumptions and discrete thresholds, zero histories, prior-only construction and future invariance, missing history, signal runs, FOI structural validation/quarantine/no-overwrite/closed metric gates, geographic contracts and full repeated-run reproduction. A separate synthetic manual check exercised the exact-scope compatibility branch; no synthetic alert entered actual analytical outputs.

All **16 non-manifest Phase 5C artifacts reproduced byte-for-byte** across two full scratch runs. Final saved output hashes, all seven module hashes and supporting README/test hashes match the final execution manifest. **59 protected earlier-phase artifact hashes remained unchanged**, and the earlier **74-file scientific-review snapshot** also remained unchanged. Original Phase 2 input/code/output and Phase 4 source/code/output guards passed. `git diff --check` passed with existing working-tree line-ending notices; a direct whitespace check covers the newly created files as well.

JavaScript tests/build were not rerun: no frontend, dependency, configuration or application test file was touched. No browser/e2e, live database change, migration or deployment command was executed. The execution manifest is timestamped; all other generated results are deterministic within the existing pinned environment.

## Scientific limitations and next implementation stage

Implemented functionality is demonstrated by actual pair comparisons, conditional predictive outputs, diagnostics, runs and FOI validation tests. Scientifically supported findings include preservation of original observations and source incompatibilities, actual historical coverage/scores, and observed model dependence. Statistical flags and contextual direction comparisons remain exploratory. Missing denominators/vintages/events, serial dependence, seasonality and recording changes still limit interpretation. No formal zero-inflation/break test, parameter-bootstrap NB2/GLM interval, independent holdout or operational validation is claimed.

The next proposed local implementation should calibrate the NB2/trend/seasonal uncertainty model on a pre-specified common-origin design, examine prior and sparse-count sensitivity, add verified source-vintage/denominator adapters, and assess the FOI response when received. A separately approved dashboard stage can then expose versioned historical research outputs with explicit scope/freshness/limitations. No current public-health warning, geographic dashboard, database publication or Phase 6 work is authorised by completion of this phase.
