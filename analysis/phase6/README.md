# Phase 6 — Inverclyde geographic case study

Local Python analytics only. Original workbook and all previous phase outputs are preserved. No Supabase, RLS, frontend, dependency or dissertation changes; no deployment. The scope is the frozen **2024 NRS publication vintage**, not the latest release or a current threat assessment.

## Run

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase6.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
```

Default outputs: `analysis/phase6/outputs/`. `--output-dir` accepts a `.local` scratch path. All non-manifest outputs are deterministic; the manifest records actual execution time, Python version, code/input/output hashes and earlier-artifact hashes. Raw input hash/structure checks fail on a changed vintage so new sources require separate review. No network is used by the pipeline.

## Sources and definition

`datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx`, SHA-256 `9a38a4f55e1ce8a21ef4b3edf64981ac67b541460eff1ee5616224ea7f887381`:

- `Table_C1`: 2010–2024 Persons annual registered drug misuse deaths, exact Inverclyde council and Scotland columns. Each count records its cell address. Year coverage, duplicates, integers and exact area labels are validated. Males+Females check Persons, and Scotland checks `Table_1`.
- `Table_C4`: original five-year age-standardised rates and 95% confidence bounds for Inverclyde/Scotland, windows 2010–2014 through 2020–2024. Every published five-year death total checks against the five C1 counts. Rates/intervals are extracted, not recomputed.
- Cover: publication 2 September 2025; registration-derived figures. `Definitions!A5:A8` and `Notes` specify the drug misuse definition and rate conventions, including NRS exclusions and 2013 European Standard Population. The cover includes deaths occurring in Scotland whose usual residence is elsewhere; no resident-only council incidence assumption is added. Council allocation follows the source table, not a new GIS boundary assignment.

[NRS 2024 publication](https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/) and its [methodology](https://www.nrscotland.gov.uk/media/lfzm3pbu/drug-related-deaths-methodology-annex.pdf) were reviewed on 10 November 2026. The 2024 publication page explicitly identifies it as an older edition; newer observations are outside this frozen extraction. A registration year is not an exact event-onset year. Registered drug misuse deaths are not Police Scotland suspected deaths, every drug poisoning, or all indirect harm from drug use. Testing, classification and revisions may affect comparisons.

## Methods

Annual changes and three/five/ten-year endpoint changes use exact years, with undefined percentage change for a zero/missing reference. Three/five-year means are **trailing complete windows including the labelled year**; no future count enters. They differ from centred moving averages in some NRS charts. Missing/suppressed values remain unavailable and break windows; observed zero is retained. Unrecognised symbols fail rather than becoming zero. Full-history peaks/lows are retrospective descriptions, not monitoring baselines.

Scotland comparisons require the same indicator, registration period, sex and source vintage. National totals include Inverclyde, so they are not independent samples. Local share of national deaths and a 2010=100 count index describe composition/trajectory, not individual population risk. No significance test is inferred from annual changes or overlapping/nested comparisons.

The inspected population CSVs have an `HB` geography key (2019 and 2006 health-board boundary vintages), not a verified Inverclyde council denominator. Annual local crude rates remain explicitly unavailable. `crude_rate` is a tested future adapter that refuses unmatched year, boundary, geography, sex or population definition/allocation verification; it is not invoked on synthetic denominators in actual outputs. Populations are never back-solved from rounded ASRs.

Published C4 five-year ASRs do support same-window age-adjusted descriptive comparisons. Original rate units, standard population, totals, source cells and confidence bounds are retained. These are **not annual crude rates**, their adjacent windows overlap four years, and their ratios are descriptive ratios of rounded published values, not new inferential estimates. Original population-vintage revisions in NRS notes are retained; imported confidence intervals do not quantify every registration/testing uncertainty.

Only 15 annual local observations, with counts 10–33, are available. Local anomaly detection is explicitly **not estimated**: short annual history, trend, small numbers and missing independent local event labels do not support a validated local screen. A ten-year reference would leave five evaluation targets. Peaks, local/national divergence and a higher published multi-year rate are not model alerts.

## Geographic and dashboard contract

The JSON hierarchy covers Greenock locality (no direct admitted outcome series), Inverclyde council (direct case study), Renfrewshire and Inverclyde police division (separate suspected-death context), NHS GG&C (service/sample context) and Scotland (matched registered comparator). It is an evidence hierarchy, not interchangeable polygons or a quantitative geographic allocation crosswalk. No wider-area outcome is assigned to Greenock.

`dashboard_data_contract.json` contains actual validated series, trends, compatible comparisons, source metadata, five-year ASRs/intervals, unavailable annual rate rows and required display labels/states. It is ready for a later approved frontend adapter; nothing is copied into the website or database. Default scope is **Inverclyde council**, with an explicit no-compatible-Greenock-series message, precise period/vintage labels and no threat/alert styling.

## Artifacts and checks

Outputs: validated observations; Inverclyde and Scotland trend CSVs; registered-count and published-rate comparison CSVs; published five-year rate CSV; unavailable annual population-rate CSV; hierarchy, quality, provenance, findings and dashboard-contract JSON; human-readable findings; timestamped manifest. Earlier Phase 2–5C hashes and all raw inputs are checked before/after execution. No existing research output is regenerated in its original directory.

Tests cover exact workbook values/cells, sex/national/five-year-total checks, year/geography/indicator separation, suppression/zero handling, missing years/windows, prior-only/trailing calculations, future invariance, rate bounds, population mismatch rejection, hierarchy and repeated-run byte reproducibility. See `IMPLEMENTATION_REPORT.md` for actual findings and executed test results.
