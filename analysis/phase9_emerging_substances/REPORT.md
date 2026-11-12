# Phase 9: emerging-substance historical analysis

Assessment date: 10 November 2026. This isolated analysis concerns historical Scottish registered deaths. It does not establish chemical discovery, causation, population prevalence, a Greenock pattern or advance-warning success.

## Executive summary and research objective

The available evidence demonstrates changing **recorded involvement** of named substances. Bromazolam rose sharply in 2023 then declined in 2024; metonitazene, protonitazene and xylazine increased in the latest annual records. Etizolam declined markedly from its historical peak. These are national registration-year observations published later, with important changes in testing. Neither first positive year nor a rising count establishes actual first Scottish appearance or a validated emerging threat.

The objective is to describe individual-substance patterns, retain reporting definitions and relate them cautiously to existing broad-category research and official communications. No new anomaly model, parameter tuning, event matching or alert-performance metric is introduced.

## Sources, provenance and extraction

Inputs under `datasets/Group3_Item2_Data/`:

| Workbook | Sheets | Registration years | Cover publication |
| --- | --- | --- | --- |
| `nrs_drd_deaths_by_individual_substance.xlsx` | SUB1a, SUB1b, SUB2a, SUB2b | a: 2000-2024; b: 2008-2024 | 2 September 2025 |
| `nrs_drd_2023_sub1.xlsx` | SUB1a, SUB1b | a: 2000-2023; b: 2008-2023 | 20 August 2024 |
| `nrs_drd_2023_sub2.xlsx` | SUB2a, SUB2b | a: 2000-2023; b: 2008-2023 | 20 August 2024 |

The pipeline validates covers, exact sheet headers, consecutive years and count types. Footnoted year headers such as `2008 [b]` are parsed explicitly and retained verbatim. Every value retains workbook, SHA-256, sheet, value cell, original label cell, year cell, raw value, quality status, geography and definition regime. Workbooks are read without modification. No labels are silently normalised or merged.

Extraction yields **50,133 substance-year records**, **164 separately stored source-total cells** and **458 distinct original labels** across editions/sheets. Labels can include groups, variants or metabolites; this is not a claim of 458 independently verified chemicals. All actual extracted counts are numeric observed integers; no actual missing or suppression tokens were found. Handling of missing/suppressed/non-numeric cells is separately tested. Absent labels remain unavailable rather than zero. There are no duplicate edition/sheet/label/year keys. All **24,144** shared exact-label/year cells agree between editions; this limited vintage agreement does not establish an unrevised historical release sequence. See `quality_report.json`, `source_metadata.json` and `vintage_comparisons.csv`.

## Reporting definitions

SUB1 concerns drug misuse deaths; SUB2 uses the wider drug-poisoning definition. These endpoints remain separate. Suffix a describes substances implicated or potentially contributing from 2008; earlier years use reported substances not necessarily implicated. Suffix b describes presence not considered contributory and starts in 2008. Annual changes are not calculated across the 2008 definition boundary.

These are registration years, not necessarily occurrence years. A death can involve several drugs; counts across labels or sheets must not be summed into independent deaths. A detected substance is not automatically causal. Percentage change is undefined after a zero or unavailable preceding count. First/last positive years describe the available definition segment; a positive at its left boundary is left-censored.

The [official NRS 2024 publication](https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/), reviewed 10 November 2026, documents limited bromazolam and nitazene testing before 2023 and routine xylazine testing beginning in 2024. Apparent onset and growth can reflect testing expansion. The retained 2024 edition is historical, not a current surveillance feed.

## Individual-substance results

The following uses **2024-edition SUB1a, implicated/potentially contributing drug misuse deaths, Scotland, 2008-2024**. Earlier zero years are published zeros, not verified absence. Full annual values, zero lists, peaks and cells appear in `observations.csv`, `annual_changes.csv` and `selected_substance_results.json`.

| Original label | First positive in segment | 2023 | 2024 | Change | Percentage change | Historical peak in segment |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| BROMAZOLAM | 2022 | 426 | 346 | -80 | -18.78% | 426, 2023 |
| METONITAZENE | 2023 | 18 | 55 | +37 | +205.56% | 55, 2024 |
| PROTONITAZENE | 2022 | 11 | 56 | +45 | +409.09% | 56, 2024 |
| XYLAZINE | 2023 | 10 | 20 | +10 | +100% | 20, 2024 |
| ETIZOLAM | 2012 | 173 | 111 | -62 | -35.84% | 806, 2020 |
| DIAZEPAM | 2008, left boundary | 154 | 156 | +2 | +1.30% | 211, 2018 |
| ISOTONITAZENE | 2023 | 1 | 0 | -1 | -100% | 1, 2023 |

Exact 2024 workbook source rows for SUB1a: bromazolam 61, metonitazene 198, protonitazene 260, xylazine 303, etizolam 135, diazepam 109 and isotonitazene 161. The CSV identifies exact year-specific columns; the corresponding label cells are A61, A198, A260, A303, A135, A109 and A161. These are separately reported overlapping involvements, not additive deaths.

### Historical patterns and definition differences

Bromazolam records 54 in 2022, 426 in 2023 and 346 in 2024: a rise followed by decline, not continuing growth. Protonitazene records 1, 11 and 56 over those years: two consecutive annual increases, based on small initial counts. Metonitazene and xylazine first record positive values in 2023 in this segment, followed by increases; limited earlier testing prevents an absence/emergence interpretation. Isotonitazene records one in 2023 then zero; this does not establish disappearance. Diazepam is already positive at the segment boundary, so 2008 is not an onset claim. All original labels receive the same descriptive summaries; no post-hoc significance threshold or threat ranking is applied.

| Substance | SUB1a 2023 -> 2024 | SUB1b 2023 -> 2024 | SUB2a 2023 -> 2024 | SUB2b 2023 -> 2024 |
| --- | --- | --- | --- | --- |
| Bromazolam | 426 -> 346 | 19 -> 3 | 427 -> 346 | 25 -> 3 |
| Metonitazene | 18 -> 55 | 2 -> 2 | 18 -> 55 | 2 -> 2 |
| Protonitazene | 11 -> 56 | 1 -> 1 | 11 -> 56 | 1 -> 1 |
| Xylazine | 10 -> 20 | 1 -> 0 | 10 -> 20 | 1 -> 0 |

Contributing counts agree in direction between misuse and wider poisoning for these four examples, but present-only records do not show the same increases. This is a definition-dependent result, not independent replication. See `definition_comparisons.csv`; no sheet totals are combined.

## Relationship to existing analytical results

`broad_category_context.json` preserves the actual Phase 4 forensic opioid, street-benzodiazepine and prescribable-benzodiazepine rows with their original Phase 5 classifications/sensitivity and Phase 5C NB2 comparator states. These are contextual category mappings, not matches between the same people or periods. Xylazine has no admitted matching individual-substance monitoring category.

The original four-quarter street-benzodiazepine decline, 2024 Q4-2025 Q3, remains unchanged. Etizolam and bromazolam decline in annual 2024 registration records, but different periods, testing samples, exposure and registration delays prevent attributing the forensic decline to either molecule. Increasing named nitazene involvement can coexist with different broad opioid-category behaviour; the broad opioid decline in 2026 Q1 does not identify or disprove a nitazene-specific pattern. National forensic counts are not population incidence or an independent mortality cohort.

The original 47 flags, 17 grid-persistent flags, sensitivity matrices and Phase 5C model disagreements remain unchanged. Phase 5C's 2,256 candidate pairs contain 646 contextual, 1,592 incompatible and 18 unresolved pairs, with no joint directional contextual signal established under its declared comparisons. That earlier analysis did not contain these new NRS substance rows; it must not be represented as validating them. This phase performs contextual inspection, not a new corroboration classification or chemical-specific detector.

## Official communication chronology

The existing feasibility assessment supplies verified original nitazene issue date **24 January 2023**, bromazolam **5 July 2023**, and xylazine **9 May 2024**. Sources and later updates are retained separately in `communication_chronology.json`. Nitazene revisions, 2026 version dates and July 2026 page updates are not counted as new original alerts. No frozen curated alert date is overwritten.

The 2023 registration-year workbook was published **20 August 2024**, and the 2024 edition **2 September 2025**. A 2023 count from a later workbook is not established as pre-July-2023 information. Annual periods overlap communications but cannot locate event onset or establish signal availability. The chronology figure separates registration intervals, source releases and original communications. It computes no lead time. FOI remains pending in the admitted records; missing alerts never establish event-free periods. No sensitivity, specificity, precision or false-alarm rate is calculated.

## Figures and machine-readable deliverables

`figures/` contains five figures, each SVG and 220-dpi PNG:

1. `01_annual_selected`: four candidate annual involvement series, 2008-2024.
2. `02_selected_comparison`: seven separate substances, common SUB1a definition, 2023/2024.
3. `03_annual_changes`: four candidates, absolute annual changes, 2019-2024.
4. `04_communication_publication_timeline`: original issue dates versus registration intervals and later releases.
5. `05_reporting_definitions`: four distinct sheet definitions, 2024.

Bars retain observed annual values without interpolation. Captions state geography, source, definition and limitations. `outputs/` contains observations, separate totals, all-label inventory, annual changes, definitions, vintage comparisons, selected results, source metadata, quality, findings, broad-category context, chronology and manifest. Figures and outputs are local research artifacts, not deployed or published assets.

## Scientific limitations and MSc implications

The analysis strengthens the substance-specific historical evidence beyond broad categories, while demonstrating why a dashboard pattern is not a validated early warning. Testing changes, overlapping drugs, sparse counts, uncertain case overlap, registration delay, historical source vintages and incomplete original-alert ascertainment constrain inference. No population denominator is introduced. This national analysis supplies context for the MSc topic; it supplies no Greenock-locality or Inverclyde substance outcome. No quantitative causal contribution, uncertainty interval or significance test is implied by descriptive differences.

Future dashboard integration should be separately approved and show the exact sheet definition, national scope, publication cutoff, raw values/cells and testing caveats. Keep contributing/present-only controls distinct, preserve nulls and label the first positive as recorded involvement. Do not combine these counts with forensic denominators or promote them to warning scores. External alert validation remains subject to FOI completeness, harmonisation and a predefined independent protocol.

## Verification and preservation

Executed locally:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase9_emerging_substances.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/phase9_emerging_substances/tests -q -p no:cacheprovider
git diff --check
```

**17 tests passed in 85.49 seconds.** Two separate scratch runs produced byte-identical non-manifest data artifacts and all ten SVG/PNG files. Tests independently checked all extracted value, label and year cells against the original workbooks, source checksums, definition separation, chronological ordering, missing/suppressed/invalid counts, zero-denominator handling, absent labels, vintage pairing, intermittent patterns and overwrite refusal. An initial ordering assertion exposed regime-group order in the annual-change export; the new Phase 9 export was corrected to chronological order and the complete new suite passed. Earlier methods were not changed.

The completed pipeline and final independent manifest check verified **105 protected earlier-phase files**, including the original 85-file guard plus Phase 6 files, as well as all three input workbooks, seven contextual inputs, new code/supporting files, **12 non-manifest data artifacts** and **10 figure files**. The pipeline refuses output overwrites and verifies source and protected hashes before and after execution. The annual-series and chronology PNGs were visually inspected for labels, source attribution and separation of observation/publication dates. `git diff --check` passed with existing working-tree line-ending notices; a direct whitespace check covered the new files. Existing full historical/application suites were not rerun for this isolated extension; their artifacts were protected by checksum guards.

Created files are confined to `analysis/phase9_emerging_substances/`: `__init__.py`, `extract.py`, `analyse.py`, `context.py`, `figures.py`, `run.py`, `requirements.txt`, `README.md`, this report, `tests/conftest.py`, `tests/test_phase9.py`, the 13 files in `outputs/` including its manifest, and ten files in `figures/`. Ignored test/cache artifacts remain under `analysis/test_scratch.local/`. Matplotlib 3.11.2 and its required plotting dependencies were installed in the existing local virtual environment after a network-interrupted first attempt; earlier dependency files/manifests were not modified. Actual plotting package versions are retained in the run manifest.

No frontend, backend, Supabase, RLS, dissertation or frozen method is changed. No deployment, new observation acquisition or dashboard integration occurred. Stop after Phase 9 for scientific review.
