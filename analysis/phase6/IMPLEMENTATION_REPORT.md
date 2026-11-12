# Phase 6 — Inverclyde geographic case study

Implemented locally on **10 November 2026**. The analysis contains actual validated Inverclyde and matched Scotland registered-mortality results, trend metrics, original published multi-year rates, an evidence hierarchy and a populated dashboard data contract. Raw sources, earlier analytics, frontend, Supabase/RLS and dissertation files remain unchanged. No deployment, migration or database publication occurred.

## Actual Inverclyde findings

`Table_C1` of the frozen local NRS workbook provides these exact Persons counts:

| Registration year | Inverclyde council | Scotland, same registered definition |
| --- | ---: | ---: |
| 2010 | 17 | 485 |
| 2011 | 20 | 584 |
| 2012 | 13 | 581 |
| 2013 | 10 | 527 |
| 2014 | 17 | 614 |
| 2015 | 16 | 706 |
| 2016 | 20 | 868 |
| 2017 | 23 | 934 |
| 2018 | 24 | 1,187 |
| 2019 | 33 | 1,280 |
| 2020 | 33 | 1,339 |
| 2021 | 16 | 1,330 |
| 2022 | 29 | 1,051 |
| 2023 | 26 | 1,172 |
| 2024 | 25 | 1,017 |

Inverclyde's annual series fell to its observed low of **10 in 2013**, then generally rose to a joint high of **33 in 2019 and 2020**. The count fell to **16 in 2021**, rose to **29 in 2022**, then declined to **26 in 2023 and 25 in 2024**. These are historical descriptive patterns, not statistical alarms or evidence of a particular drug mechanism.

- **2024 versus 2023:** Inverclyde -1 death (**-3.85%**); Scotland -155 (**-13.23%**). This compares the same NRS registered indicator, not the Police Scotland suspected series.
- **2010 versus 2024:** Inverclyde 17 to 25 (**+47.06%**); Scotland 485 to 1,017 (**+109.69%**). Count trajectories do not account for population size/age change.
- **From the Inverclyde peak of 33 to 2024:** -8 (**-24.24%**).
- **2024 trailing means:** three-year **26.67**; five-year **25.80** deaths/year, each using complete windows ending in 2024.
- **Non-overlapping five-year blocks:** 2010–2014 total **77**, mean **15.4**; 2020–2024 total **129**, mean **25.8**, a **67.53%** increase in the block mean. This longer comparison tempers interpretation of single-year fluctuations without removing them.
- Local/national annual direction differed in **2015, 2020, 2022 and 2023**. In 2020 Inverclyde was unchanged while Scotland rose. In 2022 Inverclyde rose **81.25%** while Scotland fell **20.98%**; in 2023 Inverclyde fell **10.34%** while Scotland rose **11.51%**. These contrasts are descriptive, correlated and potentially affected by small counts; they are not significant divergence tests.

All 30 annual area/year cells are observed integers, with **no missing or suppressed values in the two extracted Persons series**. Original zeroes elsewhere in the workbook were not used as substitutes for missing values. Inverclyde source cells are `Table_C1!T6:T20`; Scotland cells are `C6:C20`. Each observation preserves its exact source cell, period, definition, boundary, vintage and workbook hash.

## Definition, boundary and source provenance

Source: `datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx`, SHA-256 `9a38a4f55e1ce8a21ef4b3edf64981ac67b541460eff1ee5616224ea7f887381`. Workbook cover and [NRS publication](https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/) agree on publication **2 September 2025**. This is the frozen 2024 edition; the official page identifies it as superseded. No later edition or 2025 observation was appended.

The indicator is **NRS registered drug misuse deaths**, by calendar year of registration and Persons (all sexes), as defined in `Definitions!A5:A8`. The underlying-cause categories are **F11–F16 and F19**, or **X40–X44, X60–X64, X85 and Y10–Y14 with a controlled drug present**, subject to NRS exclusions detailed in the methodology. It is not all drug poisonings, indirect drug-attributable harm, an illicit-drug-only indicator or Police Scotland suspected deaths. Registration date is not an exact event/detection date. Death certification, pathology/toxicology and classification can affect ascertainment.

Geography is the NRS-assigned **Inverclyde council area**, not Greenock locality, Renfrewshire and Inverclyde police division or NHS GG&C. The workbook cover includes deaths occurring in Scotland whose usual residence is elsewhere; no additional resident-only local incidence assumption or unverified GIS allocation was introduced. Boundary labels and source-assigned areas are preserved. The [NRS methodology](https://www.nrscotland.gov.uk/media/lfzm3pbu/drug-related-deaths-methodology-annex.pdf), Annex D, cautions about large percentage fluctuations in small-area annual counts. These source pages were reviewed on 10 November 2026; there was no new dataset download or change to the raw workbook.

Validation independently cross-checks Persons against Males+Females for both areas, all 15 national counts against `Table_1`, and each published five-year death total against the corresponding five C1 years. Exact headers, years, indicator text, original vintage hash, publication date and standard-population notes are checked. Unknown cell symbols, invalid counts, duplicate/absent year rows, incompatible scopes and changed vintages fail rather than being guessed.

## Population denominators and supported rate comparisons

Both existing population CSVs were inspected in full:

| Local population source | Observed coverage | Boundary | Council-rate decision |
| --- | --- | --- | --- |
| `datasets/Group3_Item2_Data/nhs_scotland_population_estimates_hb2019.csv` | 1981–2025; 2,025 rows | Health board (`HB`), 2019-boundary file | Rejected as an Inverclyde council denominator |
| `datasets/Additional_Group3_Item2_Data/Scotland_population_estimate/hb2006_pop_est_01072020.csv` | 1981–2013; 1,485 rows | Health board (`HB`), 2006-boundary file | Rejected as an Inverclyde council denominator |

Neither has a verified same-year Inverclyde council population/allocation match. **No annual Inverclyde crude mortality rates were calculated.** `annual_population_rates.csv` contains 15 explicit unavailable rows, not fabricated values or zero rates. The tested future denominator adapter requires exact geography, boundary, year, sex and verified population-definition/allocation compatibility. Synthetic populations are used only in tests and never enter real outputs. No population is inferred by dividing counts by a rounded rate.

There is nevertheless genuine population-adjusted information already published in this workbook: **Table_C4 five-year age-standardised rates**, standardised to the **2013 European Standard Population**, with original 95% confidence intervals. The pipeline extracts 22 values (11 matching windows per area, 2010–2014 through 2020–2024) and verifies all 22 death totals against complete C1 windows. It imports these NRS rates; it does not recompute them from an unsupported denominator.

For **2020–2024**:

| Scope | Five-year deaths | Published ASR per 100,000 | Published 95% CI |
| --- | ---: | ---: | --- |
| Inverclyde council | 129 | **35.6** | **29.3–41.8** |
| Scotland | 5,909 | **22.5** | **21.9–23.1** |

The descriptive difference is **13.1 per 100,000** and ratio of rounded published ASRs **1.58**. This supports a higher published age-standardised multi-year rate for Inverclyde than Scotland in that window, not an annual individual risk estimate or Greenock-specific finding. No new confidence interval for the difference/ratio or significance test was manufactured. Country totals include the council, and adjacent five-year periods overlap four years. Rates incorporate the population-vintage revisions documented in NRS Notes 1/9; the underlying age-specific denominators were not independently reconstructed.

## Geographic hierarchy and anomaly feasibility

| Evidence scope | Supported finding | Interpretation boundary |
| --- | --- | --- |
| Greenock locality | No admitted direct mortality/toxicity series | No inferred Greenock outcome, hotspot or rate |
| Inverclyde council | 15 annual registered counts, trailing trends and NRS published five-year ASRs | Direct geographic case study; all-drug registered definition |
| Renfrewshire and Inverclyde police division | Existing separate legacy suspected-death context | Wider police boundary; not a council numerator |
| NHS Greater Glasgow and Clyde | Existing separate naloxone/treatment context | Wider board/service sample; not local mortality or a council denominator |
| Scotland | Matched C1 registered comparator and C4 ASRs | National aggregate includes Inverclyde; separate suspected indicators remain separate |

The hierarchy is an evidence-scope contract, not a claim that boundaries are interchangeable or that every layer supplies the same outcome. No numerical cross-boundary allocation, downscaling or Greenock attribution was performed.

Local anomaly-screen feasibility was evaluated and saved as **`not_estimated_insufficient_validation_support`**. Fifteen annual observations with counts 10–33, trend/revisions and no independent local reference events do not support a defensible validated annual warning rule. A ten-year reference would leave only five evaluation targets. Descriptive peaks, percentages and published rate intervals are useful results without labelling them statistically detected anomalies. No annual count confidence intervals, fabricated p-values or automatic alerts were produced.

## Dashboard integration readiness

`dashboard_data_contract.json` is populated with the actual annual series, trailing means, matched national comparisons, source rates/confidence bounds, annual-rate unavailable states, provenance and hierarchy. It requires explicit indicator, boundary, full period and vintage labels. The default scope is **Inverclyde council**, with an explicit message that there is no compatible Greenock-specific series. Published five-year ASRs must be displayed as multi-year age-standardised source rates; missing values must remain gaps. Wider police/board contexts must remain separate indicators.

This is a local, dashboard-ready analytical contract, not a frontend implementation or publication. No Supabase records, permissions or existing application modules were changed. FOI remains pending, missing alerts remain unknown, and no alert-based validation metric was computed.

## Files created and verification

New files:

- `analysis/phase6/__init__.py`
- `analysis/phase6/data.py`
- `analysis/phase6/analytics.py`
- `analysis/phase6/run.py`
- `analysis/phase6/README.md`
- `analysis/phase6/IMPLEMENTATION_REPORT.md`
- `analysis/tests/test_phase6.py`

Generated files under `analysis/phase6/outputs/`:

- `validated_geographic_observations.csv` — 30 area/year counts.
- `inverclyde_trends.csv` — 15 annual local metric rows.
- `scotland_trends.csv` — 15 same-indicator national metric rows.
- `registered_scotland_comparisons.csv` — 15 matched comparisons.
- `published_five_year_rates.csv` — 22 source rates and original intervals/totals.
- `published_rate_comparisons.csv` — 11 compatible period comparisons.
- `annual_population_rates.csv` — 15 explicitly unavailable annual local rates.
- `geographic_evidence_hierarchy.json`.
- `data_quality_report.json`.
- `source_provenance.json`.
- `research_findings.json`.
- `dashboard_data_contract.json`.
- `RESEARCH_FINDINGS.md`.
- `run_manifest.json`.

The manifest hashes raw inputs, code/tests/docs, non-timestamped results and 85 earlier-phase files. Raw workbook hash and all earlier Phase 2–5C artifacts are checked before and after execution. Tests cover exact extraction/cells/years, geographic and registered/suspected separation, missing/suppressed/zero handling, complete trailing windows and future invariance, rate validation, population mismatch rejection, hierarchy and repeated-run reproducibility. Test scratch remains under the existing ignored `analysis/test_scratch.local/`.

Commands:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase6.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
git diff --check
```

**Final result: 81 Python tests passed in 266.24 seconds**, comprising all 73 previous tests and eight Phase 6 tests. The first focused run identified a synthetic low-level fixture missing provenance; the fixture was corrected, and the complete suite passed. No analytical method or source value was changed to fix that test.

All **13 non-manifest Phase 6 artifacts reproduced byte-for-byte** across two full scratch runs. Final output, input, module, README and test hashes match the execution manifest. **85 earlier-phase artifact hashes remained unchanged**, including the saved Phase 5C outputs; the original workbook and both population files also match their before/after hashes. `git diff --check` and direct new-file whitespace checks passed, with existing Git line-ending notices only. JavaScript/build/browser checks were not rerun because no application, dependency or frontend test file changed.

## Remaining limits and stop point

Results are descriptive historical geographic research, not a current toxicity forecast or public-health warning. The population-adapter, local allocation, vintage and small-number limits remain explicit. This frozen 2024 vintage must not be presented as the latest available NRS publication. Further approved work can add a reviewed council population source, a separately versioned newer NRS vintage and a frontend adapter for the populated contract. No such acquisition, integration or publication is implied by this phase.

**Stop after Phase 6 for review.**
