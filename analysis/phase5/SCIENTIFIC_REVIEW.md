# Phase 5B — scientific validation and analytical review

Review date: **10 November 2026**. Scope: read-only review of existing methods and saved research artifacts; this document is the only new non-scratch deliverable. No monitoring rule, threshold, historical output, frozen input, database, frontend, dissertation or dependency was changed. No acquisition, model refit, publication, migration, deployment or Phase 6 work was performed.

## 1. Verified findings and review approach

**Computational results are reproducible; operational warning validity is not established.** Independent recomputation confirms 8,034 observations, 47 primary flags, 17 six-setting persistent flags and 30 setting-sensitive primary flags. The principal scientific issue is that all 8,034 evidence groups contain exactly one indicator. Consequently, the saved evidence classifications do not demonstrate a cross-source corroboration analysis. Absence of a combined signal is largely imposed by grouping rules, not empirical proof of absent support or conflict.

The independent audit read the saved Phase 4 raw observation fields and rebuilt complete prior windows with a separate sorted-value median calculation. It did **not** call `screen`, `sensitivity`, `assess` or the production pipeline. It checked original values, dates, provenance and unique keys for all 8,034 observations; primary numerical baselines/limits/scores for all 5,764 eligible observations; all 252 per-series/configuration frequency records; all 7,878 sensitivity rows; and all 8,034 evidence assessments. All nine Phase 5 output files were inspected, including the execution manifest and human-readable findings; the eight non-manifest output hashes matched. The original manifest's protected artifacts, code/test hashes and all six source hashes also matched. No numerical discrepancy was found.

Audit scripts and machine-readable recomputations are retained only under ignored `analysis/test_scratch.local/phase5b_review/`. This document records the substantive results. Audit scratch is not a new monitoring implementation or published analytical output.

| Dataset | All observations | Eligible | Primary flags | No anomaly | Insufficient | Unavailable | Flags / eligible |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mortality quarters | 504 | 256 | 3 | 253 | 240 | 8 | 1.1719% |
| Forensic detections | 210 | 98 | 11 | 87 | 112 | 0 | 11.2245% |
| Treatment detections | 140 | 50 | 0 | 50 | 90 | 0 | 0% |
| Weekly naloxone | 7024 | 5360 | 33 | 5327 | 1664 | 0 | 0.6157% |
| ASSIST percentages | 72 | 0 | Not estimated | 0 | 72 | 0 | Not applicable |
| Frozen forensic shares | 84 | 0 | Not estimated | 0 | 84 | 0 | Not applicable |
| Total | 8034 | 5764 | 47 | 5717 | 2262 | 8 | 0.8154% |

These denominators are correlated indicator/geography/period observations, not independent people or events. An unflagged screen is not evidence of no harm. Neither the Scotland national mortality series nor the national naloxone series has a primary flag under this method. Historical NB2-EWMA/CUSUM flags remain separate and unchanged.

### Flag counts by indicator and exact geography

| Dataset | Indicator / substance | Geography | Primary flags |
| --- | --- | --- | --- |
| mortality_quarterly | suspected_deaths | E: Edinburgh City | 1 |
| mortality_quarterly | suspected_deaths | G: Greater Glasgow | 1 |
| mortality_quarterly | suspected_deaths | K: Renfrewshire and Inverclyde | 1 |
| forensic_counts | Dissociatives | Scotland forensic testing sample | 3 |
| forensic_counts | Opioids | Scotland forensic testing sample | 1 |
| forensic_counts | Prescribable Benzodiazepines | Scotland forensic testing sample | 2 |
| forensic_counts | Stimulants | Scotland forensic testing sample | 1 |
| forensic_counts | Street Benzodiazepines | Scotland forensic testing sample | 4 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Ayrshire & Arran | 5 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Borders | 4 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Dumfries & Galloway | 4 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Fife | 3 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Forth Valley | 2 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Grampian | 4 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Highland | 3 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Lanarkshire | 1 |
| naloxone_weekly | ambulance_naloxone_activity | NHS Lothian | 1 |
| naloxone_weekly | ambulance_naloxone_activity | Unknown | 6 |

All other series have zero primary flags or are not estimated as shown above. ASSIST and frozen shares must not be reported as evidence of zero anomalies.

### Duplicate, overlapping and repeated flags

There are **zero duplicate exact observation keys**. Nevertheless, 47 flags cannot be called 47 independent events:

- The 11 forensic flags occupy ten calendar quarters. Prescribable benzodiazepines and stimulants both flag upward in 2023 Q2, within the same forensic sample source; overlapping substance detections may concern the same cases.
- Street benzodiazepines flag downward for four consecutive quarters, 2024 Q4 through 2025 Q3. This is a repeated run under overlapping reference windows, not evidence of four independent episodes. A persistent level/testing shift is a plausible alternative explanation, not established here.
- The 33 naloxone flags occupy 28 distinct weeks. Simultaneous areas may reflect shared drivers or recording practices; distinct boards do not establish statistical independence. No person-level IDs exist to deduplicate repeat attendance or shared events.
- Police divisions, health boards, Scotland totals and Unknown geography are not additive independent samples. National counts may contain regional observations; original overlapping geography rows were not pooled. No national primary flag duplicates a regional primary flag in this run.
- The six parameter choices use the same observed counts and strongly overlapping history. They are not six replications of an event.

| Week beginning | Simultaneous naloxone flag geographies |
| --- | --- |
| 2020-08-03 | NHS Fife; NHS Forth Valley |
| 2021-09-06 | NHS Ayrshire & Arran; NHS Dumfries & Galloway |
| 2025-03-17 | NHS Ayrshire & Arran; NHS Fife |
| 2025-06-16 | NHS Dumfries & Galloway; NHS Grampian; Unknown |

## 2. Independent baseline and threshold checks

For an observation at ordinal `t`, use exactly `t-w` through `t-1` within its own source/indicator/geography/period-basis/unit. The independent calculation confirmed:

```text
m = median(prior complete window)
MAD = median(abs(prior value - m))
s = max(1.4826 * MAD, sqrt(max(m, 1)))
L = max(0, m - k*s); U = m + k*s
flag increase iff y > U; flag decrease iff y < L
deviation = y - m; scaled deviation = (y - m)/s
```

Primary `k=3`, with 16 quarters for mortality/forensic, 18 months for treatment and 104 weeks for naloxone. All primary baseline values, MADs, scales, reference endpoints/counts, strict boundaries, original observations and scaled deviations matched the saved outputs to numerical tolerance (relative 1e-12, absolute 1e-10). Source period headers, Monday-week bounds and calendar-quarter ordinals were checked. The legacy mortality quarter label does not undo the source's ten-day reporting adjustment.

No look-ahead through observations is present in baseline construction: `range(t-w,t)` excludes `t` and later values; descriptive Phase 4 rolling averages are not used. The existing future-invariance tests also passed. However, the available frozen vintage includes later source revisions and full-series cutoff metadata. This is **retrospective, prior-observation-only screening**, not an as-published or prospective warning reconstruction.

The MAD definition and normal scaling convention are supported by the [SciPy MAD documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_abs_deviation.html) (reviewed 10 November 2026). That convention does not make these count scores normally distributed or supply tail probabilities.

### Data-quality exclusions

The 2,262 insufficient-data rows comprise 2,106 count-window exclusions plus 72 ASSIST and 84 frozen-share rows deliberately not modelled. The count-window exclusions are 216 mortality observations with initial short history, 24 further mortality observations whose established prior window contains suppression/missingness, 112 initial forensic observations, 90 initial treatment observations and 1,664 initial naloxone observations. Eight currently suppressed mortality values are `unavailable_analysis`; none became zero. Of the 224 nominal initial mortality positions (14 series × 16), eight are currently suppressed and therefore counted unavailable rather than insufficient.

There are no missing naloxone incident counts; 32 missing source moving averages do not affect this screen, which recalculates its own prior-count reference. None of the 47 primary flags has an incomplete reference window: **all six alternatives are eligible for every primary flag**. Missingness therefore does not directly explain the 30 sensitive classifications, although it changes which other observations can be assessed.

## 3. All 17 persistent flags

Source legend (exact source path; publisher and URL retained in `outputs/source_provenance.json`):

- **M** — Police Scotland, `datasets/Group3_Item2_Data/police_suspected_drug_deaths_Jan2017-Dec2025.xlsx`; [official frozen-vintage publication](https://www.gov.scot/publications/suspected-drug-deaths-scotland-october-december-2025/). Vintage publication date 17 March 2026; not proof of first availability for each older observation.
- **F** — PHS, `datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv`; [RADAR dashboard](https://scotland.shinyapps.io/phs-drugs-radar-dashboard/). Source-specific publication dates unknown.
- **N** — PHS, `datasets/Group3_Item2_Data/radar_sas_naloxone_weekly_by_board.csv`; same RADAR dashboard. Source-specific publication dates unknown.

These URLs identify the saved source lineage; this review did not acquire a new mortality/toxicology vintage or independently re-extract the live dashboard. Original hashes and local observation-to-source matches were verified. Frozen forensic shares have no verified original publisher URL in their saved provenance, an unresolved lineage limitation.

Values and limits below are rounded for presentation only; original numerical precision is retained in the unchanged CSV. `d` is signed count deviation from the prior median; `r=d/s` is the robust scaled deviation, **not a calibrated z-score**. Bounds shown are the **primary** window and k=3. Every row flags in the same direction for both windows at k=2.5, 3 and 3.5. Freshness gives observation-end age and source-cutoff age on 10 November 2026; both are distinct from publication lag.

| ID | Indicator / source | Substance | Exact geography | Observation period | Observed | Prior median (reference period) | Deviation d; scaled r | Primary monitoring bounds | Stability | Observation / source freshness | Interpretation and limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Suspected deaths / M | Not measured | E: Edinburgh City | 2023 Q1 | 46 | 23 (2019 Q1 to 2022 Q4) | 23; r=4.4324 | [7.4327, 38.5673]; w=16, k=3 | 6/6 increase | 1320d / 314d; cutoff 2025-12-31 | Retrospective division count increase; no substance attribution or population-rate inference |
| S02 | Dissociatives / F | Dissociatives | Scotland forensic testing sample | 2023 Q3 | 40 | 10.5 (2019 Q3 to 2023 Q2) | 29.5; r=7.959 | [0, 21.6195]; w=16, k=3 | 6/6 increase | 1137d / 224d; cutoff 2026-03-31 | Selected forensic detections; overlapping categories and unknown testing exposure |
| S03 | Prescribable Benzodiazepines / F | Prescribable Benzodiazepines | Scotland forensic testing sample | 2022 Q4 | 290 | 190 (2018 Q4 to 2022 Q3) | 100; r=4.2156 | [118.8352, 261.1648]; w=16, k=3 | 6/6 increase | 1410d / 224d; cutoff 2026-03-31 | Selected forensic detections; overlapping categories and unknown testing exposure |
| S04 | Stimulants / F | Stimulants | Scotland forensic testing sample | 2023 Q2 | 250 | 174.5 (2019 Q2 to 2023 Q1) | 75.5; r=3.6374 | [112.2308, 236.7692]; w=16, k=3 | 6/6 increase | 1229d / 224d; cutoff 2026-03-31 | Selected forensic detections; overlapping categories and unknown testing exposure |
| S05 | Street Benzodiazepines / F | Street Benzodiazepines | Scotland forensic testing sample | 2025 Q1 | 104 | 182.5 (2021 Q1 to 2024 Q4) | -78.5; r=-3.5298 | [115.783, 249.217]; w=16, k=3 | 6/6 decrease | 589d / 224d; cutoff 2026-03-31 | Selected forensic detections; overlapping categories and unknown testing exposure |
| S06 | Ambulance naloxone activity / N | Not measured | NHS Ayrshire & Arran | 2021-09-06 to 2021-09-12 | 22 | 9 (2019-09-09 to 2021-08-30) | 13; r=4.3333 | [0, 18]; w=104, k=3 | 6/6 increase | 1885d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S07 | Ambulance naloxone activity / N | Not measured | NHS Ayrshire & Arran | 2025-03-17 to 2025-03-23 | 20 | 7 (2023-03-20 to 2025-03-10) | 13; r=4.3842 | [0, 15.8956]; w=104, k=3 | 6/6 increase | 597d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S08 | Ambulance naloxone activity / N | Not measured | NHS Ayrshire & Arran | 2025-06-02 to 2025-06-08 | 24 | 7 (2023-06-05 to 2025-05-26) | 17; r=5.7332 | [0, 15.8956]; w=104, k=3 | 6/6 increase | 520d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S09 | Ambulance naloxone activity / N | Not measured | NHS Dumfries & Galloway | 2021-04-26 to 2021-05-02 | 8 | 2 (2019-04-29 to 2021-04-19) | 6; r=4.0469 | [0, 6.4478]; w=104, k=3 | 6/6 increase | 2018d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S10 | Ambulance naloxone activity / N | Not measured | NHS Grampian | 2023-08-21 to 2023-08-27 | 22 | 7 (2021-08-23 to 2023-08-14) | 15; r=5.0587 | [0, 15.8956]; w=104, k=3 | 6/6 increase | 1171d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S11 | Ambulance naloxone activity / N | Not measured | NHS Grampian | 2024-05-27 to 2024-06-02 | 20 | 7 (2022-05-30 to 2024-05-20) | 13; r=4.3842 | [0, 15.8956]; w=104, k=3 | 6/6 increase | 891d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S12 | Ambulance naloxone activity / N | Not measured | NHS Lanarkshire | 2026-03-09 to 2026-03-15 | 21 | 7 (2024-03-11 to 2026-03-02) | 14; r=4.7214 | [0, 15.8956]; w=104, k=3 | 6/6 increase | 240d / 163d; cutoff 2026-05-31 | Ambulance activity count; no overdose-incidence, drug-specific or causal inference |
| S13 | Ambulance naloxone activity / N | Not measured | Unknown | 2024-02-12 to 2024-02-18 | 6 | 0 (2022-02-14 to 2024-02-05) | 6; r=6 | [0, 3]; w=104, k=3 | 6/6 increase | 996d / 163d; cutoff 2026-05-31 | Unassigned geography; zero median and unit scale floor dominate; cannot locate a hotspot |
| S14 | Ambulance naloxone activity / N | Not measured | Unknown | 2024-04-08 to 2024-04-14 | 4 | 0 (2022-04-11 to 2024-04-01) | 4; r=4 | [0, 3]; w=104, k=3 | 6/6 increase | 940d / 163d; cutoff 2026-05-31 | Unassigned geography; zero median and unit scale floor dominate; cannot locate a hotspot |
| S15 | Ambulance naloxone activity / N | Not measured | Unknown | 2025-06-16 to 2025-06-22 | 4 | 0 (2023-06-19 to 2025-06-09) | 4; r=4 | [0, 3]; w=104, k=3 | 6/6 increase | 506d / 163d; cutoff 2026-05-31 | Unassigned geography; zero median and unit scale floor dominate; cannot locate a hotspot |
| S16 | Ambulance naloxone activity / N | Not measured | Unknown | 2025-09-08 to 2025-09-14 | 5 | 0 (2023-09-11 to 2025-09-01) | 5; r=5 | [0, 3]; w=104, k=3 | 6/6 increase | 422d / 163d; cutoff 2026-05-31 | Unassigned geography; zero median and unit scale floor dominate; cannot locate a hotspot |
| S17 | Ambulance naloxone activity / N | Not measured | Unknown | 2026-02-23 to 2026-03-01 | 7 | 0 (2024-02-26 to 2026-02-16) | 7; r=7 | [0, 3]; w=104, k=3 | 6/6 increase | 254d / 163d; cutoff 2026-05-31 | Unassigned geography; zero median and unit scale floor dominate; cannot locate a hotspot |

### What persistence means

The 17 comprise one mortality, four forensic and 12 naloxone flags. Five of the 12 naloxone flags have Unknown geography and prior median zero. Six persistent flags use the count-scale floor, including those five Unknown records. At median zero, scale is one, so a count of four exceeds every tested upper threshold (2.5, 3, 3.5) in both windows if each retains zero median. Persistence here may simply reflect the shared floor and discreteness, not six independent confirmations.

For a complete fixed reference window the three thresholds are nested. A same-direction exceedance at k=3.5 necessarily exceeds k=3 and k=2.5. Thus six-setting persistence mostly reduces to passing the most conservative threshold for **two related windows**; it demonstrates bounded parameter robustness within this grid, not robustness to seasonality, changing test exposure, data revisions, a different count model or alternative null distributions. No external event validation, causal explanation or clinical/operational validity follows. Only 17/47 (36.17%) primary flags have this limited persistence; the other 30 (63.83%) do not.

## 4. All 30 parameter-sensitive primary flags

In this table, each triplet gives outcomes at **k=2.5 / 3 / 3.5**, respectively. `+` means increase flag, `-` decrease flag, and `.` eligible with no flag. Short/long references are 12/16 quarters for mortality and forensic; 52/104 weeks for naloxone. No row is ineligible at any setting. Last-year values are descriptive same-quarter or 52-week-lag counts, **not** seasonally fitted reference values or new thresholds.

| ID | Indicator / source | Geography | Period | Observed | Short reference: k triplet | Long reference: k triplet | Parameter effect | Prior-year count | Primary scale floor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Suspected deaths / M | G: Greater Glasgow | 2022 Q1 | 50 | w=12: - / . / . | w=16: - / - / . | Both | 92 | No |
| P02 | Suspected deaths / M | K: Renfrewshire and Inverclyde | 2022 Q2 | 7 | w=12: - / . / . | w=16: - / - / . | Both | 16 | Yes |
| P03 | Dissociatives / F | Scotland forensic testing sample | 2023 Q1 | 22 | w=12: + / + / + | w=16: + / + / . | Both | 10 | No |
| P04 | Dissociatives / F | Scotland forensic testing sample | 2024 Q1 | 27 | w=12: . / . / . | w=16: + / + / + | Window only | 22 | Yes |
| P05 | Opioids / F | Scotland forensic testing sample | 2026 Q1 | 328 | w=12: - / - / - | w=16: - / - / . | Both | 456 | No |
| P06 | Prescribable Benzodiazepines / F | Scotland forensic testing sample | 2023 Q2 | 286 | w=12: + / . / . | w=16: + / + / . | Both | 247 | No |
| P07 | Street Benzodiazepines / F | Scotland forensic testing sample | 2024 Q4 | 117 | w=12: - / - / . | w=16: - / - / . | Threshold only | 194 | No |
| P08 | Street Benzodiazepines / F | Scotland forensic testing sample | 2025 Q2 | 98 | w=12: - / - / . | w=16: - / - / - | Both | 167 | No |
| P09 | Street Benzodiazepines / F | Scotland forensic testing sample | 2025 Q3 | 91 | w=12: . / . / . | w=16: - / - / . | Both | 131 | No |
| P10 | Ambulance naloxone activity / N | NHS Ayrshire & Arran | 2024-06-17 | 15 | w=52: + / . / . | w=104: + / + / . | Both | 6 | No |
| P11 | Ambulance naloxone activity / N | NHS Ayrshire & Arran | 2024-07-29 | 15 | w=52: + / + / . | w=104: + / + / . | Threshold only | 10 | No |
| P12 | Ambulance naloxone activity / N | NHS Borders | 2020-05-25 | 6 | w=52: + / + / + | w=104: + / + / . | Both | 1 | No |
| P13 | Ambulance naloxone activity / N | NHS Borders | 2021-02-22 | 6 | w=52: + / + / . | w=104: + / + / . | Threshold only | 0 | No |
| P14 | Ambulance naloxone activity / N | NHS Borders | 2021-06-28 | 6 | w=52: + / + / . | w=104: + / + / . | Threshold only | 0 | No |
| P15 | Ambulance naloxone activity / N | NHS Borders | 2024-05-06 | 6 | w=52: + / + / . | w=104: + / + / . | Threshold only | 1 | No |
| P16 | Ambulance naloxone activity / N | NHS Dumfries & Galloway | 2020-04-06 | 9 | w=52: + / + / . | w=104: + / + / + | Both | 1 | No |
| P17 | Ambulance naloxone activity / N | NHS Dumfries & Galloway | 2021-09-06 | 8 | w=52: . / . / . | w=104: + / + / + | Window only | 5 | No |
| P18 | Ambulance naloxone activity / N | NHS Dumfries & Galloway | 2025-06-16 | 7 | w=52: + / + / . | w=104: + / + / . | Threshold only | 1 | No |
| P19 | Ambulance naloxone activity / N | NHS Fife | 2020-08-03 | 15 | w=52: + / + / . | w=104: + / + / . | Threshold only | 10 | No |
| P20 | Ambulance naloxone activity / N | NHS Fife | 2020-08-31 | 15 | w=52: + / + / . | w=104: + / + / + | Both | 3 | Yes |
| P21 | Ambulance naloxone activity / N | NHS Fife | 2025-03-17 | 13 | w=52: + / + / + | w=104: + / + / . | Both | 2 | No |
| P22 | Ambulance naloxone activity / N | NHS Forth Valley | 2020-08-03 | 18 | w=52: + / + / + | w=104: + / + / . | Both | 13 | No |
| P23 | Ambulance naloxone activity / N | NHS Forth Valley | 2024-07-15 | 14 | w=52: + / + / + | w=104: + / + / . | Both | 5 | No |
| P24 | Ambulance naloxone activity / N | NHS Grampian | 2024-01-08 | 16 | w=52: . / . / . | w=104: + / + / . | Both | 8 | No |
| P25 | Ambulance naloxone activity / N | NHS Grampian | 2025-06-16 | 16 | w=52: . / . / . | w=104: + / + / . | Both | 8 | No |
| P26 | Ambulance naloxone activity / N | NHS Highland | 2020-01-06 | 9 | w=52: . / . / . | w=104: + / + / . | Both | 7 | Yes |
| P27 | Ambulance naloxone activity / N | NHS Highland | 2021-09-13 | 11 | w=52: . / . / . | w=104: + / + / . | Both | 1 | Yes |
| P28 | Ambulance naloxone activity / N | NHS Highland | 2023-07-10 | 13 | w=52: + / + / . | w=104: + / + / . | Threshold only | 8 | No |
| P29 | Ambulance naloxone activity / N | NHS Lothian | 2024-11-11 | 1 | w=52: . / . / . | w=104: - / - / . | Both | 12 | Yes |
| P30 | Ambulance naloxone activity / N | Unknown | 2026-04-06 | 4 | w=52: . / . / . | w=104: + / + / + | Window only | 0 | Yes |

**Window choice affects 22/30; threshold choice affects 27/30; 19 are affected by both.** The remaining three are window-only and eight threshold-only. Examples:

- Dissociatives in 2024 Q1 flag at every 16-quarter threshold but none of the 12-quarter thresholds; the observed count 27 follows 22 in the same quarter a year earlier. The longer reference retains older lower counts. Stability to shorter history is absent; neither trend nor seasonality was fitted.
- Street benzodiazepines in 2025 Q3 flag downward only with the longer window and k≤3; the shorter window has adapted to the prolonged lower level. Four consecutive primary flags may describe a sustained shift rather than repeated new events.
- NHS Dumfries & Galloway, 6 September 2021, and Unknown geography, 6 April 2026, flag at every long-window threshold but none of the short-window thresholds. This demonstrates baseline-window dependence even when threshold sensitivity alone would appear small.
- Several Borders counts of six lie close to the robust screen boundary; integer values, small median counts and scale-floor activation can make k=3 versus k=3.5 decisive.

Seasonality was **not adjusted or validated** in any setting. An annual-length window pools seasons; it does not estimate a seasonal expected count. The same-quarter/52-week lag values above are contextual diagnostics only (52 weeks is not exact calendar-year matching). No attribution to seasonality, changes in substance supply, COVID-19 or service practice can be established from these comparisons. Treatment has only 28 monthly observations; one alternative-setting flag exists, despite zero primary flags. The grid does not test seasonality, trend, observation exposure, alternative scale floors or source-vintage uncertainty. All 13 floor-active primary flags and missing-window exclusions remain visible in the original outputs.

### Historical frequency across all configurations

Each row pools the recorded series for one dataset and window. Counts at k=2.5, 3 and 3.5 are listed in order. Windows cover different eligible origins; these are **not** common-period performance comparisons. No count is an estimated false-positive rate.

| Dataset | Window | Eligible observations per k | Flags k=2.5 / 3 / 3.5 | Frequency at k=3 |
| --- | --- | --- | --- | --- |
| forensic_counts | 12 | 126 | 19 / 11 / 7 | 8.7302% |
| forensic_counts | 16 | 98 | 18 / 11 / 6 | 11.2245% |
| mortality_quarterly | 12 | 312 | 20 / 7 / 3 | 2.2436% |
| mortality_quarterly | 16 | 256 | 10 / 3 / 1 | 1.1719% |
| naloxone_weekly | 52 | 6192 | 151 / 71 / 31 | 1.1466% |
| naloxone_weekly | 104 | 5360 | 71 / 33 / 16 | 0.6157% |
| treatment_counts | 12 | 80 | 1 / 0 / 0 | 0.0000% |
| treatment_counts | 18 | 50 | 0 / 0 / 0 | 0.0000% |

Across all count observations, saved sensitivity labels are 17 persistent, 198 choice-sensitive, 6,495 with no flag among eligible choices and 1,168 with no eligible choice. The 198 include **168 observations without a primary flag** that flag under an alternative setting. An all-grid screen is therefore broader than the 47-primary-flag summary; selecting whichever setting flags would introduce an additional data-dependent selection rule not implemented or approved here.

## 5. Cross-source evidence and compatibility review

### Structural limitation of the saved evidence output

Independent grouping found **8,034 groups of size one**. In `run.py:58`, `evidence_domain` is set to the exact source indicator ID (`forensic:...`, `treatment:...`, etc.). `monitoring.py:148` additionally requires exact geography, period label/bounds and basis. Even a compatible substance category at a different source cannot enter the same domain without a separately reviewed mapping. Consequently, the 47 `single_indicator_signal`, 5,717 `no_detected_signal` and 2,270 `insufficient_evidence` labels simply restate each individual screen's eligibility/flag state in the present inputs. They do not establish a multi-source consensus, absence of contradictions or empirical independence. Multiple-support/conflict branches are unit-tested with compatible fixtures, not exercised by actual source combinations.

This conservatism avoids invalid joins but leaves the cross-source research objective **partially implemented**. The saved sentence that no compatible corroboration was established is defensible as a processing outcome; it must not be presented as evidence that other data were empirically examined and found not to support the signals. Current `insufficient_evidence` is assigned unconditionally in the code, appropriate for this frozen historical run but not a validated dynamic freshness classifier.

### Related periods reviewed without forcing agreement

The next table lists each of the 11 forensic flags and other **primary flags in its calendar quarter**, solely as a review index. A week is listed under its start-quarter for locating potential overlaps, not aggregated, reclassified or treated as equivalent to a quarterly outcome. Weeks may cross quarter boundaries. These coincidences are not new evidence classes or independent events. All 33 naloxone and three mortality flags are covered by this table or the per-flag compatibility index that follows.

| Forensic substance | Quarter | Direction | Mortality primary flags in quarter | Naloxone primary flags in quarter | Why not corroboration |
| --- | --- | --- | --- | --- | --- |
| Dissociatives | 2023 Q1 | increase | E: Edinburgh City increase | No primary naloxone flag | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Dissociatives | 2023 Q3 | increase | No primary mortality flag | NHS Grampian 2023-08-21 increase; NHS Highland 2023-07-10 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Dissociatives | 2024 Q1 | increase | No primary mortality flag | NHS Grampian 2024-01-08 increase; Unknown 2024-02-12 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Opioids | 2026 Q1 | decrease | No primary mortality flag | NHS Lanarkshire 2026-03-09 increase; Unknown 2026-02-23 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Prescribable Benzodiazepines | 2022 Q4 | increase | No primary mortality flag | No primary naloxone flag | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Prescribable Benzodiazepines | 2023 Q2 | increase | No primary mortality flag | No primary naloxone flag | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Stimulants | 2023 Q2 | increase | No primary mortality flag | No primary naloxone flag | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Street Benzodiazepines | 2024 Q4 | decrease | No primary mortality flag | NHS Lothian 2024-11-11 decrease | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Street Benzodiazepines | 2025 Q1 | decrease | No primary mortality flag | NHS Ayrshire & Arran 2025-03-17 increase; NHS Fife 2025-03-17 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Street Benzodiazepines | 2025 Q2 | decrease | No primary mortality flag | NHS Ayrshire & Arran 2025-06-02 increase; NHS Dumfries & Galloway 2025-06-16 increase; NHS Grampian 2025-06-16 increase; Unknown 2025-06-16 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |
| Street Benzodiazepines | 2025 Q3 | decrease | No primary mortality flag | Unknown 2025-09-08 increase | Same quarter can overlap; national testing sample vs separate divisions/boards; all-drug vs substance-specific; publication timing unknown |

Specific compatibility decisions:

- **Mortality:** Police divisions differ from health boards; Edinburgh City is not NHS Lothian, Greater Glasgow division is not NHS Greater Glasgow and Clyde, and Renfrewshire and Inverclyde division is not a council/Greenock measure. Mortality is all-drug originally suspected death, with legacy timing/revision differences; it does not identify the drugs driving a forensic flag. Forensic national sampling cannot establish a local mortality mechanism. Two early mortality flags (2022 Q1/Q2) occur before the longer-window forensic screen becomes eligible (2022 Q4), so unflagged or unavailable forensic history is not negative corroboration.
- **Forensic:** Groups overlap; prescribable/street/all benzodiazepines cannot be treated as independent drug exposures. Broad opioids do not identify nitazenes; dissociatives are not a proxy for all named published alerts. Scotland forensic testing samples are not national population-prevalence samples. Cases and tested denominators may change. The simultaneous 2023 Q2 stimulant and prescribable-benzodiazepine flags are internal sample context, not independent-source confirmation.
- **Naloxone:** Weekly board activity is all-drug and service-dependent; it cannot identify a specific forensic substance. Unknown geography cannot be matched to a board, division or local hotspot. Same-week flags in different boards do not establish a common source event. Months/quarters cannot be equated to a single weekly spike. National versus local scale mismatches remain even when calendar periods overlap.
- **Treatment:** GG&C monthly urine detections cover December 2023–March 2026, a selected treatment cohort. Primary flags are zero, but denominators/testing volume are unknown. The source opioid category explicitly excludes treatment opioids, so it is not equivalent to the forensic opioid category. NHS GG&C naming differs across files; no unreviewed geography alias was applied. Monthly spans overlap some later forensic/naloxone periods, but this does not create a matched clinical cohort or rule out effects elsewhere.
- **ASSIST:** Source Q4–Q15 are unequal study periods, Q9 is shortened, exact dates and denominators are unavailable, and the cohort is selected emergency-department samples. Benzodiazepine/Opioid categories are broader/differently named than forensic subgroups; no valid binomial uncertainty or calendar-quarter alignment is possible from the saved CSV. Percentages can provide labelled descriptive context, not confirmation of a count-based flag.
- **Frozen shares:** Only 2022–2024; original numerator/denominator arithmetic is checked but extraction lineage remains unresolved. They derive from the same forensic source domain and are not independent corroboration of forensic counts. Their preserved CUSUM belongs to a different historical analysis.
- **RADAR and published alerts:** Private intelligence narratives were not inspected or exposed. The existing curated public alert list supplies dates/topics, not complete event occurrence or no-event ascertainment. July 2026 alerts occur after the count-source cutoffs and are not contemporaneous validation. The listed January 2023 nitazene and July 2023 bromazolam alerts coincide with some broad mortality/dissociative periods, but are different outcomes/drug scopes; the May 2024 xylazine alert is not a labelled truth event for all-drug naloxone. No lead-time or correct-warning claim is supported.

### Per-flag compatibility index for regional mortality and naloxone

Each primary mortality/naloxone flag is indexed below. `F` refers to any forensic primary flag in the same quarter (not a matched test), and `T` to whether the period falls in the treatment source's calendar coverage. Lack of a flag elsewhere is not lack of harm. Geography, substance specificity, unknown source publication dates, differential reporting lag and unmatched sampling prevent a corroboration verdict for every indexed row. Unknown location rows have an additional absolute geography gap. No record was combined or rescored.

| Source | Geography | Period | Direction | Potential F period overlap | Treatment coverage | Compatibility finding |
| --- | --- | --- | --- | --- | --- | --- |
| M | E: Edinburgh City | 2023 Q1 | increase | Dissociatives increase | Outside T coverage | Division ≠ board/national sample; all-drug count |
| M | G: Greater Glasgow | 2022 Q1 | decrease | No primary F flag | Outside T coverage | Division ≠ board/national sample; all-drug count |
| M | K: Renfrewshire and Inverclyde | 2022 Q2 | decrease | No primary F flag | Outside T coverage | Division ≠ board/national sample; all-drug count |
| N | NHS Ayrshire & Arran | 2021-09-06 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Ayrshire & Arran | 2024-06-17 | increase | No primary F flag | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Ayrshire & Arran | 2024-07-29 | increase | No primary F flag | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Ayrshire & Arran | 2025-03-17 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Ayrshire & Arran | 2025-06-02 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Borders | 2020-05-25 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Borders | 2021-02-22 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Borders | 2021-06-28 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Borders | 2024-05-06 | increase | No primary F flag | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Dumfries & Galloway | 2020-04-06 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Dumfries & Galloway | 2021-04-26 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Dumfries & Galloway | 2021-09-06 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Dumfries & Galloway | 2025-06-16 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Fife | 2020-08-03 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Fife | 2020-08-31 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Fife | 2025-03-17 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Forth Valley | 2020-08-03 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Forth Valley | 2024-07-15 | increase | No primary F flag | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Grampian | 2023-08-21 | increase | Dissociatives increase | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Grampian | 2024-01-08 | increase | Dissociatives increase | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Grampian | 2024-05-27 | increase | No primary F flag | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Grampian | 2025-06-16 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Highland | 2020-01-06 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Highland | 2021-09-13 | increase | No primary F flag | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Highland | 2023-07-10 | increase | Dissociatives increase | Outside T coverage | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Lanarkshire | 2026-03-09 | increase | Opioids decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | NHS Lothian | 2024-11-11 | decrease | Street Benzodiazepines decrease | T dates overlap; different cohort/area | Board ≠ national forensic sample; weekly all-drug service activity |
| N | Unknown | 2024-02-12 | increase | Dissociatives increase | T dates overlap; different cohort/area | No location match; N publication unknown |
| N | Unknown | 2024-04-08 | increase | No primary F flag | T dates overlap; different cohort/area | No location match; N publication unknown |
| N | Unknown | 2025-06-16 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | No location match; N publication unknown |
| N | Unknown | 2025-09-08 | increase | Street Benzodiazepines decrease | T dates overlap; different cohort/area | No location match; N publication unknown |
| N | Unknown | 2026-02-23 | increase | Opioids decrease | T dates overlap; different cohort/area | No location match; N publication unknown |
| N | Unknown | 2026-04-06 | increase | No primary F flag | Outside T coverage | No location match; N publication unknown |

Publication timing cannot rescue these mismatches. The mortality file has a known March 2026 vintage publication date; forensic, ASSIST, treatment and naloxone publication dates are unknown in the source register. `publication_lag_days` on mortality is final-vintage publication minus an observation end, not historical first-report delay. Source-cutoff age is not reporting lag. Record-level source vintage/availability would be required to assess whether any indicator could have warned before another outcome.

## 6. Statistical validity and independent-reference assessment

### Defensible features for exploratory screening

Prior-only, explicitly complete windows; separate source/geography/measurement groups; no imputation or fabricated denominators; a transparent robust centre/scale; explicit unsupported-data states; preserved exact values; and a fully reported finite parameter grid are sound safeguards for reproducible exploratory work. The count-scale floor prevents zero MAD from creating a zero-width interval. They establish computational discipline, not a validated observation model.

### Assumptions still requiring validation

1. **Count model and estimated-reference uncertainty:** Symmetric median/MAD bounds with a square-root-median floor are a heuristic. A square-root-mean Poisson interpretation cannot simply be assigned to a square-root-median floor. Skewness, overdispersion, zero inflation and estimation uncertainty are not modelled; no fitted NB2 count distribution or finite-window tail calibration is present. The MAD multiplier is a normal-scale convention, not a guarantee of normal residuals. Labels must remain operational definitions of an exploratory screen, not hypothesis-test significance.
2. **Seasonality and nonstationarity:** Pooled annual/multi-annual histories do not fit seasonality; changing mortality/testing/service trends can move counts outside a historical reference or cause rolling adaptation. Four repeat street-benzodiazepine declines illustrate possible level-shift persistence. No residual autocorrelation or seasonal adequacy analysis was saved; this review did not fit an alternative model. NIST notes that serial dependence can alter false/true alarm behaviour in traditional charts: [NIST serial-correlation study](https://www.nist.gov/publications/serial-correlation-qc-data-use-proper-control-charts) (reviewed 10 November 2026). This supports caution, not a quantitative correction for this screen.
3. **Small and sparse samples:** Twelve/sixteen quarters or twelve/eighteen months yield few seasonal replicates; finite-window medians/MADs may change sharply. Near-zero medians and fixed floor thresholds are particularly relevant to Unknown/small-board counts. The grid keeps the same scale convention throughout, so scale-floor robustness itself is untested.
4. **Multiple comparisons and dependence:** There are 5,764 eligible primary comparisons across 42 count series, including nested geographies and overlapping substance categories. Six grid settings produce still more, highly dependent comparisons. No family-wise error or false-discovery control is implemented, and no valid null p-values exist to which such control could simply be applied. Do not compare the observed 0.8154% flag rate with a Gaussian three-sigma nominal error rate, infer an ARL, or multiply false-alarm probabilities as if observations/settings were independent. Conventional chart false-alarm formulas have distribution/stability assumptions; see [NIST chart guidance](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm).
5. **Exposure and selection:** Forensic and treatment counts can reflect changes in numbers tested, recruitment, testing panels or selection. Naloxone can reflect service use, recording and access, not just latent toxicity. ASSIST percentages without sample sizes cannot support a denominator-aware precision assessment. A stable count screen cannot remove these measurement limitations.
6. **Data vintage and geography:** Legacy suspected deaths are not registered drug-related deaths, and Databelt/manual reporting equivalence and revisions remain unresolved from Phase 3. The frozen time-series vintage does not reconstruct what an analyst knew then. Police divisions, boards, national samples and Unknown geography are not interchangeable; no population offsets or Greenock observations are available in this reviewed analysis.
7. **Decision protocol:** Saved hashes prove what code and inputs produced the outputs, not that windows/thresholds or interpretation were independently preregistered. The implementation states pragmatic pre-run settings; this review found no independent prospective protocol/event holdout proving selection was unaffected by prior data familiarity. No threshold was changed during review.

### External validation feasibility

`g3-indicator/data/derived/ALERT_LIST_2022_2026.csv` has six curated rows, only three counted primary alert dates in the original 2022 Q3–2024 Q4 window. `g3-indicator/data/frozen/ALERT_RULE_DECISION.txt` explicitly records incomplete alert enumeration and lack of confirmed no-event coverage. Published alerts are official communications, not a complete labelled set of toxicity episodes; broad count signals and alert-specific substances/geographies are not interchangeable targets. Alert date may also follow detection and cannot substitute for outcome onset or issue-time availability.

No adequate independent reference-event dataset or prospective issuance record exists here. Therefore **operational sensitivity, specificity, positive predictive value, false-warning rate and warning lead time cannot be established**. Descriptive co-occurrence with a listed alert is possible, but would not validate predictive performance; no such score was computed. Future validation would require a prospectively specified target, compatible event ascertainment including negatives, publication vintages, independent evaluation period, known issue times and event/run clustering rules.

## Pending FOI Response and External Alert Evaluation

The research team reports that its Freedom of Information request to Public Health Scotland concerning historical RADAR drug alerts has been submitted; the response is **pending**. No response records, response date, confirmed scope or completeness assessment are available in this review. The response is a **potential external reference dataset**, not an existing validated benchmark.

**Absence of a record in `radar_alerts`, the curated alert list or another local export means unknown ascertainment, not that no official alert occurred.** An empty database query is not a verified no-alert period. Even a complete list of issued alerts would establish communication history within its documented scope, not necessarily the presence or absence of underlying toxicity events.

### Proposed import specification — documentation only

The following is a specification for a separately reviewed local staging dataset after receipt, not an assertion about existing database columns. No importer, schema change or database population is authorised or implemented here. Retain the original response and attachments unchanged, with an extraction manifest; keep raw source fields alongside any normalised fields. Unknown values remain null with an explicit missingness reason; do not infer dates, categories, locations or withdrawal status.

| Field / group | Required representation | Import and interpretation rules |
| --- | --- | --- |
| Alert identifier | `issuer`, `official_alert_id_raw`, `official_alert_id`, `local_record_id`, `identifier_status` | Preserve the identifier exactly as supplied. Normalise only documented formatting differences. If no official ID is supplied, mark it unavailable; a local surrogate identifies the extracted record and must never be presented as an official alert number. Do not merge on title alone. |
| Issue and publication dates | Separate `issue_date`, `publication_date`, `first_publication_date`, raw date text, precision, timezone if supplied, and missingness reason | These dates may differ. Retain day/month/year precision and uncertainty; do not replace issue/publication dates with FOI receipt, download, event or detection dates. Do not invent a first-publication date from a later revision. |
| Event or detection date | Separate `event_date_start`, `event_date_end`, `detection_date`, raw text, precision and definition | Optional: preserve an interval when the response describes a period. Distinguish occurrence, detection, notification and publication. Unknown onset cannot be reconstructed from an alert date or assigned to a quarter as an exact event date. Flag inconsistent sequences for review, without silently correcting them. |
| Substance or substance group | Original names, supplied identifiers, normalised term(s), mapping version, mapping status and ambiguity notes | Allow multiple substances and overlapping categories. Use a reviewed crosswalk; retain unmapped/uncertain values. A specific drug is not automatically equivalent to a broad monitoring group; unknown substance is not an all-substances match. |
| Geographic coverage | Original geographic text; scope type, named area(s), official code/boundary version where available, and interpretation notes | Distinguish alert circulation coverage from event/detection location. Scotland-wide dissemination does not prove Scotland-wide occurrence. Police division, health board, council and locality remain separate; no Greenock attribution or inferred boundary equivalence. |
| Alert category and description | Original category/title; reviewed category mapping; public description or restricted-description status | Distinguish new official alerts, updates, intelligence communications and non-drug notices. Preserve classification rationale. Do not export private narratives, case-identifying details or material whose disclosure/publication status has not been reviewed. A redacted description remains explicitly redacted. |
| Source and provenance | FOI request/reference if supplied, issuing authority, response date, receipt date, attachment filename, document URL if available, page/sheet/row locator, file SHA-256, extraction date/method/reviewer and dataset version | Keep source issue/publication dates separate from response/receipt dates. Preserve the original attachment and link every extracted record to it. Unknown request IDs and dates remain unknown. Record corrections in an auditable extraction log rather than overwriting source text. |
| Revision or withdrawal | `record_version`, `revision_status`, `revised_at`, `withdrawal_status`, `withdrawn_at`, `supersedes_record_id`, parent alert ID and original status wording | Use explicit unknown status when not supplied; absence of a withdrawal field does not mean never withdrawn. Keep version history and link updates to the original alert. Do not count revisions as new alerts by default. Withdrawn communications remain documented historical records, with evaluation inclusion governed by a specified rule. |
| Completeness and limitations | Response scope, date coverage, coverage by geography/category, retrieval/search description if supplied, redactions, withheld/unavailable records, missing attachments, known gaps, extraction issues and completeness decision | Assess at dataset and record level. Distinguish complete within a stated scope, partial, unknown and incompatible. Do not interpret “not held”, an omitted record or an unanswered request component as proof that an alert/event did not exist. Record unresolved questions explicitly. |

### Receipt, compatibility and evaluation gates

1. **Receipt and preservation:** Confirm that the response and all referenced attachments were received. Record their provenance and hashes, request/response scope and any restrictions. Store raw material separately from an extracted staging dataset; this specification makes no claim that receipt or extraction has occurred.
2. **Completeness assessment:** Reconcile stated coverage, row counts where supplied, missing attachments, duplicate identifiers, revisions, withdrawals, redactions and known gaps against the response. Seek clarification where coverage is unclear. Establish which periods, areas and alert categories are actually ascertained. An unresolved or partial response cannot provide reliable negative labels outside its verified coverage.
3. **Record quality and deduplication:** Validate identifiers, date precision and relationships between original alerts and updates. Separate new-alert records from revisions without discarding historical versions. Preserve multiple-substance records without multiplying them into independent events. Quarantine ambiguous records for review rather than fabricating a match.
4. **Compatibility with monitoring data:** Document substance mappings, geographic containment/boundary versions, observation intervals and measurement definitions for each candidate match. Distinguish dissemination geography from occurrence geography, issued communications from clinical events, all-drug activity from substance-specific observations, and weekly/monthly/legacy-quarter counts from unequal ASSIST study periods. Exact date uncertainty or unavailable geography may make a record non-evaluable. Calendar overlap alone is descriptive context, not corroboration.
5. **Temporal availability:** Recover actual issue/publication dates and available monitoring-data vintages. Specify whether an analysis targets alert issuance, detection or event occurrence; do not interchange those endpoints. Frozen retrospective screens were not issued prospectively, so a reconstructed date difference cannot establish prospective warning lead time. Reporting and publication lags must be accounted for rather than inferred from source-cutoff age.
6. **Pre-specified external evaluation protocol:** Before calculating any metric, define the eligible scope, independent evaluation period, alert/event unit, revision/withdrawal inclusion, signal-run clustering, geographic/substance eligibility, allowable matching intervals, unmatched/ambiguous handling and negative-label ascertainment. Freeze these rules without retuning the existing screen to improve apparent agreement. Assess possible shared underlying data between RADAR alerts and monitoring sources; external documentation is not automatically an independent measurement process.
7. **Metric hold:** **Do not calculate alert-based sensitivity, specificity, precision, false-warning rate, lead time or other validation metrics until the FOI response has been received, assessed for completeness and harmonised with the monitoring data.** Receipt alone does not satisfy this gate. Even after harmonisation, a metric requires an appropriate denominator, ascertainment and temporal design; incomplete negatives, incompatible targets or unknown issue times may keep particular metrics unavailable. No retrospective result may be labelled prospective without actual prior issuance evidence.

The 17 flags persistent across six settings provide **internal statistical robustness within the existing parameter grid**. External evaluation against documented alerts would address a different question and remains pending. Neither internal persistence nor a future coincident alert proves causality, clinical significance or operational warning performance. Current readiness remains exploratory research presentation with limitations; external alert evaluation requires further validation.

This addition changes documentation only. No historical alert was fabricated, no record was added to `radar_alerts`, and no alert-based validation metric was computed. Future import, database publication and analytical implementation require separate approval.

## 7. Publication-readiness assessment

Readiness below concerns transparent research presentation, never clinical/operational deployment. A component may be presentable as an exploratory method while a stronger performance claim remains unpublishable.

| Component / proposed claim | Readiness class | Decision / required qualification |
| --- | --- | --- |
| Source counts, coverage, missingness and original descriptive trends | Ready for descriptive research presentation | Use exact dates/units/geography and frozen-vintage/provisional/sampling caveats; no current-threat framing. |
| ASSIST percentages as source-reported observations | Ready for descriptive research presentation | Preserve unequal study labels and unknown denominators; exclude national prevalence and inferential claims. |
| Frozen forensic shares as historical input values | Suitable for exploratory presentation with prominent limitations | Numerator/denominator arithmetic agrees, but independent extraction lineage remains unresolved; do not present as a newly verified official positivity series. |
| Reproducible robust-screen formula, primary flags and no-signal states | Suitable for exploratory presentation with prominent limitations | Use research-screen terminology; report eligibility, all settings, floor usage, uncalibrated bounds and source limitations. |
| 17 persistent flags and all six-setting comparisons | Suitable for exploratory presentation with prominent limitations | State bounded internal robustness only; five Unknown/zero-baseline persistent flags and nested thresholds must be disclosed. |
| 30 sensitive primary flags, frequencies and parameter matrices | Suitable for exploratory presentation with prominent limitations | Report full grid and changing eligible periods; no cherry-picked threshold or false-positive interpretation. |
| Matched multi-source corroboration capability | Requires further validation | Current 8,034 singleton groups do not exercise it; requires reviewed domain/boundary/period/exposure mapping and compatible actual data. |
| Scientific calibration of bounds and false-signal behaviour | Requires further validation | Assess count tails, seasonality/trend, sparse scales, revisions, dependence, multiplicity and independent event definitions. |
| Original NB2-EWMA/CUSUM and elapsed forecast as separate historical research | Suitable for exploratory presentation with prominent limitations | Not revalidated by Phase 5B; retain original assumptions, frozen vintage, limits and retrospective labels. |
| Claim that 47 flags represent 47 independent toxicity episodes | Not suitable for publication | Known repeat/overlap structure and no episode-level truth labels. |
| Claim of verified multi-source consensus, current emerging threat, Greenock hotspot or drug-specific overdose incidence | Not suitable for publication | Not supported by source compatibility, timeliness, geography or measurement. |
| Claim of validated prospective warning sensitivity/specificity/lead time or deployment readiness | Not suitable for publication | No adequate reference-event set, prospective issuance log or independent operational validation. |
| Private RADAR narratives or identifiable supporting case material | Not suitable for publication | Not reviewed or exported; no privacy/publication approval within this phase. |

## 8. Recommended corrective actions — recommendations only

1. **Correct the interpretation before research presentation:** state that the evidence layer currently returns single-indicator summaries; no actual cross-source combinations were evaluated. Show flag counts, exclusions and settings together; separate persistent statistical flags from published alerts and clinical outcomes. Disclose five persistent Unknown-geography/zero-baseline flags and repeated street-benzodiazepine declines.
2. **Review source lineage and coverage:** independently verify original forensic denominator extraction, publication dates, testing-volume/sample-size denominators, service recording changes, mortality reporting-system equivalence and vintage revisions. Keep incompatible later observations separate.
3. **Specify a scientific monitoring target and protocol before new tuning:** decide whether the intended target is death incidence, testing positivity, ambulance activity, a substance-specific event or an official communication. Predefine windows/threshold/scale alternatives and an untouched later evaluation set; do not adjust parameters to obtain a desired signal count.
4. **Evaluate modelling assumptions in a separately approved methods phase:** inspect seasonality, trend, residual dependence, sparse/zero counts and scale-floor behaviour; assess appropriate count/exposure models and null/shift simulations. Control interpretation for repeated comparisons and episode persistence. Simulations alone would not validate clinical warning performance.
5. **Design a reviewed corroboration crosswalk:** document compatible substance definitions, geographic nesting and calendar overlap rules; obtain exact ASSIST dates/denominators and issue-time metadata. Similar names or calendar overlap alone are insufficient. Keep unknown/incompatible states explicit. Treat repeated/multi-category flags as related observations without inventing episode IDs or collapsing counts.
6. **Obtain independent event ascertainment and prospective provenance before warning evaluation:** complete and qualify any alert/event reference, distinguish publication date from event onset, establish known-negative periods and record actual forecast/signal issue times. Only then define independent evaluation metrics.
7. **Keep publication/deployment separate:** no UI, Supabase, RLS, migration or Phase 6 implementation follows from this review. Obtain separate approval after methods/data readiness decisions.

No corrective action above was implemented during this review; existing methodology, thresholds and outputs remain unchanged.

## 9. Tests, preservation and exact changes

- Complete Python suite: `.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider` — **61 passed in 62.77 seconds**. This includes existing Phase 2/3/4 reproduction and Phase 5 leakage/threshold/evidence/reproducibility checks. Tests write only ignored research scratch artifacts.
- Independent audit: `analysis/test_scratch.local/phase5b_review/review.py` — all recomputation assertions passed; no production screen functions were invoked.
- Extra JavaScript check: `npm test` could not spawn test workers in this managed environment (`spawn EPERM`), so no test assertions ran under that default command. The same full 19-test unit suite ran successfully in process using `node --test --test-isolation=none tests/analytics.test.js tests/database.test.js` — **19 passed**. No application code or test configuration was changed. Browser/e2e and build were not run for this read-only analytical review.
- Exact new non-scratch file: **`analysis/phase5/SCIENTIFIC_REVIEW.md` only**. Original source/output hashes are checked against the original manifest and the review's before/after snapshot. No saved outputs were regenerated in their original directories. No database/network acquisition command ran.
- Final preservation check: **74 existing file hashes unchanged**, with original Phase 2 source-code hashes additionally verified against its manifest. The report contains exactly 17 persistent-signal rows and 30 sensitive-signal rows. `git diff --check` and a direct report whitespace check passed; Git emitted existing working-tree line-ending notices only.
- Ignored scratch audit scripts/results/snapshots are retained under `analysis/test_scratch.local/phase5b_review/`; they contain aggregate research data and verification calculations, not private narratives or credentials.

Stop after Phase 5B. Further analytical implementation, Phase 6 and publication remain pending separate approval.
