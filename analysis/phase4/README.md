# Phase 4 — multi-dataset descriptive trends

Completed locally on 10 November 2026 after closing the Phase 3 audit. No anomaly method, alert, weighted score, new forecast, dashboard modification or database publication is included. Phase 5 requires separate user approval.

## Commands

Use the existing pinned environment from the repository root:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase3.audit
.\analysis\.venv\Scripts\python.exe -m analysis.phase4.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
```

Default outputs are under `analysis/phase4/outputs/`, separate from the untouched Phase 2 baseline. `--output-dir` supports a different local directory. The explicit analysis date is 2026-11-10; it is not a claim of current observation coverage. No new dependency is required. `analysis/tests/conftest.py` provides Git-ignored workspace test scratch paths with inherited permissions for the managed Windows environment.

## Methods and scope

`trends.py` supplies exact-period comparisons, zero/missing-safe percentage calculations, percentage-point changes, complete-window means, complete-year sums, week-start-month grouping and within-source dense rankings. `run.py` reads the verified source files and attaches units, geography, provenance, data cutoffs and limitations.

| Dataset | Period basis | Descriptive metrics |
| --- | --- | --- |
| Mortality | Legacy calendar quarters and complete calendar years; Scotland and 13 police divisions | QoQ/YoY changes, four-quarter average, prior-eight-quarter reference; complete-year changes and prior-three-year reference. Division share of national count is not a population-adjusted rate. |
| Forensic toxicology | 30 calendar quarters, seven overlapping substance groups | Exact adjacent-quarter and prior-year changes, four-quarter average, prior-eight-quarter reference, source-period detection-count rankings. No count-based prevalence denominator is invented. |
| Frozen forensic shares | 12 denominator-backed quarters, 2022–2024, seven groups | Preserve original rounded shares; numerator/denominator arithmetic checks; percentage-point and relative changes. Independent Table 1 extraction lineage remains unresolved, so quality notes accompany every record. |
| ASSIST | 12 source-labelled study periods, not calendar quarters | Original detection percentages, adjacent-period percentage-point/relative changes and rankings. No pooled percentages, inferred exact dates or rolling means. Q9 shortened recruitment is flagged. |
| Treatment toxicology | 28 calendar months, five groups, NHS Greater Glasgow and Clyde urine samples | Monthly/YoY changes, three-month average, prior-12-month reference and source-period count rankings. Not national prevalence. |
| Ambulance naloxone | 439 Monday-start weeks, 14 health boards plus Scotland and Unknown | Weekly changes, four-week average, prior-52-week mean and 52-week-lag comparison. No pooling of overlapping geographic levels. |
| Naloxone week-start month | Whole weekly totals assigned to their Monday's month | Month-group changes, three-group average and prior-12-group reference only when all expected Mondays are available. These are NOT calendar-month incident totals or exposure-normalised rates; four/five-week groups can differ solely because of exposure. |

Reference windows use only preceding periods; rolling descriptive averages include the current period. Missing observations/periods propagate to unavailable comparisons and incomplete means. Duplicate keys and invalid/non-integer counts fail rather than being silently merged. Zero-reference percentage changes are undefined (`null`/empty CSV cell), not infinite or zero. Direction means only increase/decrease relative to the preceding exact period; no statistical significance is inferred. Rank is based on the stated count or detection percentage, within a single source, geography and period. Overlapping categories are never normalised to sum to 100%.

## Sources and provenance

- `datasets/Group3_Item2_Data/police_suspected_drug_deaths_Jan2017-Dec2025.xlsx`
- `datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv`
- `datasets/Group3_Item2_Data/radar_toxicology_assist.csv`
- `datasets/Group3_Item2_Data/radar_toxicology_treatment_glasgow.csv`
- `datasets/Group3_Item2_Data/radar_sas_naloxone_weekly_by_board.csv`
- `g3-indicator/public/data/quarterly_input_table.json` for denominator-backed historical shares only.
- `group3_data_sources_import.csv` supplies available publisher/source URLs; its hash is also recorded.

Each record carries the indicator, source path/hash, geography, period basis, observed value/unit, derived metrics, method, quality status, source cutoff, analysis date and limitations. The mortality source vintage publication date is 17 March 2026. Other source publication dates are not established and remain null; no download date or filename is substituted for publication. `publication_lag_days` for mortality is vintage-publication minus observation-end, not first-release delay. `data_age_days` is observation-cutoff age, not estimated reporting delay. ASSIST exact day cutoffs/ages are unavailable and source period labels are retained.

All six analytic input hashes, supporting metadata hash, code hashes and output hashes are in the new manifest. The original Phase 2 manifest and every recorded baseline hash are verified before and after the pipeline runs. CSV/findings/quality outputs are deterministic; the separate manifest records actual execution time. Tests generate two runs in scratch directories and compare all non-timestamped artifacts byte-for-byte.

## Saved outputs and actual findings

| Output CSV | Records | Meaning |
| --- | ---: | --- |
| mortality_quarterly.csv | 504 | 36 quarters × 14 national/division series; eight suppressed observations retained as missing. |
| mortality_annual.csv | 119 | Complete annual totals only; seven of 126 potential area-years excluded for suppression. |
| forensic_counts.csv | 210 | Seven groups × 30 quarters. |
| frozen_forensic_shares.csv | 84 | Seven groups × 12 historical denominator-backed quarters. |
| assist_percentages.csv | 72 | Six groups × 12 study periods. |
| treatment_counts.csv | 140 | Five groups × 28 months. |
| naloxone_weekly.csv | 7,024 | Separate geographic series; 32 missing source moving averages, no missing incident counts. |
| naloxone_week_start_month.csv | 1,616 | 16 separate series × 101 week-start-month groups. |

`findings.json` includes record/group counts and the latest record for each indicator/geography, including derived metrics and caveats. `quality_report.json` enumerates suppressed quarters and excluded annual totals. `run_manifest.json` identifies inputs, methods, code and output hashes.

Measured descriptive findings, not statistical alerts:

- National suspected deaths: **248 in 2025 Q4**, down **43 (14.78%)** from Q3; up **6.90%** from 2024 Q4. The four-quarter average is **286.5**. The **2025 total is 1,146**, up **81 (7.61%)** from 2024's 1,065, in the frozen legacy series.
- Forensic street-benzodiazepine detections: **97 in 2026 Q1**, up **23 (31.08%)** quarter-on-quarter, but down **6.73%** year-on-year. This illustrates why the comparison window matters; it does not establish increased population toxicity.
- Forensic opioids: **328 detections in 2026 Q1**, down **28.54%** quarter-on-quarter. No denominator-backed 2026 share is asserted.
- ASSIST benzodiazepine detection: **79.21% in source period Q15 (Feb–May 2026)**, up **9.98 percentage points** from Q14. This is a selected study cohort with unknown sample denominator in the CSV; it is not a national prevalence estimate.
- Greater Glasgow and Clyde treatment stimulant detections: **336 in March 2026**, down **7.95%** month-on-month and unchanged from March 2025. This is a treatment urine-sample count.
- Scotland ambulance naloxone: **59 incidents in the week beginning 25 May 2026**, down **3.28%** from the previous week; four-week mean **60.75**. The prior-52-week mean is **74.33**, and the latest count is **20.62%** below that descriptive reference. These are not direct overdose or toxicity incidence estimates.
- Supported regional context: the **Renfrewshire and Inverclyde police division** has a 2025 total of **46**, compared with **70** in 2024. This broader division is NOT Inverclyde council or Greenock; no Greenock-specific observation, population rate or case-study view was produced.

## Validation, limitations and next approval

The full Python suite covers Phase 2 reproduction, Phase 3 integrity/compatibility gates, and Phase 4 period alignment, zero denominators, missing observations, duplicates, complete aggregation, percentage points, geography separation, rankings and generated-output reproducibility. Actual test results are recorded in the completion report.

No p-values, significance claims, anomaly thresholds, false-signal rates, lead times or early-warning classifications are produced. Input cutoffs differ: mortality ends 2025, forensic/treatment data March 2026, naloxone May 2026, denominator-backed shares December 2024, and ASSIST uses study labels. They must not be presented as simultaneous current threats. Laboratory/sample changes and missing publication vintages remain important limitations. Existing RADAR intelligence narratives and unapproved database tables were not read by this pipeline or published.

No Phase 4 database extension is proposed or executed. The separate Phase 3 forecast-schema design remains unexecuted. **Stop here:** request user approval for Phase 5 before adding statistical anomaly detection, evidence-assessment classes, false-signal evaluation or dashboard/database integration. Approval for Phase 5 is not approval for migration, publication or deployment.
