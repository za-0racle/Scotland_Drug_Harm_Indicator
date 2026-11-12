# Phase 9: historical individual-substance analysis

Isolated descriptive analysis of three existing NRS workbooks. No application, database or earlier analytical output is changed. Counts describe Scotland, not Greenock. No warning performance is calculated.

Run from the repository root:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase9_emerging_substances.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/phase9_emerging_substances/tests -q -p no:cacheprovider
```

The pipeline refuses to overwrite existing outputs. Reproduction uses `--output-dir analysis/test_scratch.local/new-phase9-run`; its figures are saved inside that scratch destination. The default produces `outputs/` and sibling `figures/`. Original workbooks remain untouched. Matplotlib is an additional local plotting dependency; the earlier analysis requirements and manifests remain unchanged.

`extract.py` validates workbook covers, year headers, source definitions, labels and non-negative integer counts. Every observation retains workbook SHA-256, sheet, original label, label/year/value cells, raw value, quality state and publication date. Source totals are separate. Unknown, missing and suppressed observations remain null. Absent labels are never converted to zero. No synonyms are merged; the inventory is an inventory of original source labels, not a verified chemical taxonomy.

SUB1 is drug misuse; SUB2 is broader drug poisoning. Suffix a reports implicated/potentially contributing substances from 2008, and earlier reported substances under a different regime. Suffix b reports presence not considered contributory, from 2008. Changes never cross that regime boundary. Annual changes require adjacent observed years; percentage changes require a strictly positive preceding count. First/last positive and zero-year lists concern only the available reporting segment. Intermittence requires a recorded zero between two positive years. Consecutive increases are descriptive, with no significance threshold.

All labels receive summaries, changes and exact-label shared-edition comparisons. Seven selected labels receive definition comparisons and focused figures: four requested candidates, etizolam and diazepam for contrast, and isotonitazene as a sparse recorded-involvement example. Selection is explanatory, not a statistical ranking or exhaustive threat assessment.

`context.py` preserves existing broad-category rows, original flags, sensitivity and NB2 comparator records. Substance-to-category mappings provide context only: annual death-registration counts and forensic quarters are not equivalent observations or independent cohorts. Xylazine has no admitted matching individual-substance monitoring category. Chronology separates original alerts, revisions, source releases and registration intervals; it never computes lead time. FOI remains pending in the admitted research record.

The [NRS 2024 publication](https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/) documents limited bromazolam/nitazene testing before 2023 and routine xylazine testing beginning in 2024. Testing expansion can create apparent emergence. Counts overlap between substances; do not add them into unique deaths, infer prevalence, causation, first Scottish appearance or advance warning. The available workbooks are historical vintages, not complete as-of release histories.

Outputs include all observations, separate source totals, per-definition inventory, annual changes, shared-vintage comparisons, selected definitions, provenance, quality, context, chronology and findings. The manifest records input/context/code/output/figure checksums and protected earlier artifacts. Execution time is the only intentionally variable manifest field. SVG and 220-dpi PNG figures use fixed rendering metadata and preserve annual observed bars without interpolation.
