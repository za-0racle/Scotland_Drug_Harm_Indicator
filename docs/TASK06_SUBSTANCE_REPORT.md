# Task 06 — Substance Intelligence

Implemented locally in the existing Vite / vanilla JavaScript and Chart.js application. No backend, Supabase permissions, models, frozen artifacts or other screen feature scope changed.

## Files
- Added `src/platform/substance-data.js`: source contracts, complete pagination, validation, compatible selection, heatmap/ranking/profile/table preparation and CSV scope.
- Added `src/platform/substance.js`: dedicated source controls, source introduction, verified cards, history chart, heatmap, horizontal ranking, modal profile drawer, paired category comparison, searchable paginated observations and provenance.
- Modified `src/platform/dashboard.js`: mount/cleanup and retained source selections at `#substance`.
- Modified `src/platform/charts.js`: optional concise category display labels, retaining full series identity and tooltip metadata.
- Modified `src/platform/chart-data.js`: verified calendar-month slots, preserving absent months as null. Existing identity and missing-period safeguards remain.
- Modified `src/platform/style.css`: responsive White & Gold screen and drawer styles.
- Added `tests/substance.test.js` and `e2e/substance.spec.js`.
- Added this report.

## API and reporting definitions
The screen requests all pages of the existing `/api/v1/toxicology/forensic`, `/api/v1/toxicology/assist` or `/api/v1/toxicology/treatment` endpoint through the retained API client. Stable totals and artifact hashes are required across pages; incomplete responses fail closed. Shared shell initialization continues to use its existing endpoints. No new endpoint is introduced. CSV is generated from all eligible table search matches with original records, provenance and filters; it is explicitly not limited to the visible page.

Forensic: quarterly detections in the Scotland forensic testing sample, not a representative Scottish population sample. Treatment: monthly urine-sample detections in NHS Greater Glasgow and Clyde; source opioids exclude treatment opioids. ASSIST: percentages in a selected participating emergency-department cohort, with unequal source study periods and shortened Q9 recruitment. Exact dates and sample denominators are unavailable for ASSIST. Unconnected categorical points preserve source ordinal ordering; no calendar reassignment or pooling. ASSIST heatmap is deliberately unavailable because comparable calendar intervals and denominators are absent.

All sources retain original category identities, units, geographic coverage, reporting periods, quality notes, source paths, source hashes, source URLs where present and publication/cutoff fields. Profile histories describe the selected eligible scope. First dataset appearance is explicitly not first occurrence in Scotland. Missing and suppressed values remain missing; recorded zeros remain zero. Calendar-only gaps are display slots, not fabricated observations. Cards count reported periods and categories, not sums of overlapping detections.

Ranking is constrained to one reporting window/source/unit/geography and retains overlapping categories as separate observations. Within-screen comparison aligns two original categories in the same source and geography without pooled totals, causation claims or model changes. Comparison Studio and its existing area-comparison dialog are preserved. No arbitrary chart switching is added.

RADAR raw intelligence is not exposed by an approved API resource. Its selectable unavailable state explains this and refers to the retained Surveillance Signals contextual evidence. No raw database table access is added. Existing NRS annual mortality resources do not expose individual substances.

## Phase 9 proposal — pending separate approval
Confirmed existing files under `analysis/phase9_emerging_substances/outputs/`: `observations.csv`, `source_totals.csv`, `substance_inventory.csv`, `annual_changes.csv`, `vintage_comparisons.csv`, `definition_comparisons.csv`, `selected_substance_results.json`, `source_metadata.json`, `quality_report.json`, `run_manifest.json`, `findings.json`, `broad_category_context.json`, `communication_chronology.json`. These are not in the active backend artifact catalog. They were inspected without modification; no runtime Phase 9 data is loaded.

Proposed, unimplemented API contract:

`GET /api/v1/substances/nrs/observations?vintage=2024&endpoint=drug_misuse&reporting_definition=implicated_or_potentially_contributing&substance_label=<exact label>&start_year=2008&end_year=2024&offset=0&limit=1000`

Return the existing envelope shape: `state`, `kind`, `data`, `total`, `offset`, `limit`, `metadata`, `message`. Each row must preserve the actual artifact fields `vintage`, `publication_date`, `geography`, `year`, `year_header_raw`, `sheet`, `endpoint`, `reporting_definition`, `substance_label`, `count`, `quality_status`, `raw_value`, `source_workbook`, `source_sha256`, `source_cell`, `label_cell`, `year_cell`, `label_class`. Add explicit unit (`registered_death_involvement_count`), annual registration-year basis and stable observation identity without overwriting original fields. Null and quality states must survive serialization. Metadata must carry artifact/manifest hashes, publication vintage, source metadata and limitations. Source totals must be a separate resource, never synthetic substance observations.

Integration requirements:
1. Separately approve backend routes and any change to frozen feature scope.
2. Admit approved Phase 9 files to the checksum-verified artifact catalog and schema validation; verify manifest hashes and provenance.
3. Extend the API filter allowlist/schema with exact original label, vintage, endpoint and reporting definition. This proposed URL is not compatible with the current client allowlist yet.
4. Prevent default mixing of publication vintages, SUB1 drug misuse versus SUB2 broader poisoning, and suffix-a contribution versus suffix-b presence not considered contributory. Separate the pre-2008 reporting regime from 2008 onward.
5. Keep original labels, overlapping involvement, suppression and missingness; never normalize synonyms automatically or sum into unique deaths.
6. Test total/hash stability, pagination completeness, definition boundaries, annual slots, null handling, original source cells, safe CSV and full versus page export labels. Add frontend integration only after approved API delivery.
7. Carry testing-expansion caveats: limited bromazolam/nitazene testing before 2023 and routine xylazine testing from 2024, as documented in the existing research record. Apparent emergence does not establish new arrival or advance warning.

## Verification
Results and screenshot paths are recorded below after execution. This task stops at Task 06.
## Test and build results
- Final `npm test`: 62 passed, 0 failed (11 test files, including 8 new substance tests covering all ten requested data behaviours).
- Final `npm run build`: passed; 26 modules transformed. No dependencies were added.
- Browser checks use Microsoft Edge, the existing FastAPI server and the production preview configuration. Existing Overview, Mortality and Comparison tests and Task 06 source/drawer/export/responsive checks are included.
- An initial browser check exposed a default end-period selection bug (only the earliest period was selected); fixed to default to the complete available history. A subsequent 10-test browser run passed. Final browser result and screenshots follow.
- Initial sandbox execution blocked child processes with EPERM. The authorized checks succeeded with child processes enabled.

## Remaining limitations
This is retrospective research, not live surveillance or a warning service. Raw RADAR intelligence and NRS individual-substance Phase 9 observations remain unavailable in the active API. No denominator-supported prevalence claims are possible. ASSIST uses source study periods rather than elapsed calendar time and deliberately has no comparable-period heatmap. Heatmap colour intensity and rankings describe the selected source observations, not population risk or independent death totals. The browser regression run is scoped to the changed screen and the existing Overview, Mortality and Comparison screens, not the entire end-to-end suite. No deployment was requested or performed.

Final production browser result: **11 passed, 0 failed (52.4 seconds)** using `npx playwright test --config playwright.overview.config.js e2e/substance.spec.js e2e/mortality.spec.js e2e/overview.spec.js e2e/comparison.spec.js`.

Screenshots (captured from the final production build):
- Desktop, 1440 × 1100 viewport: `test-results/task06-substance-desktop.png`
- Tablet, 900 × 1000 viewport: `test-results/task06-substance-tablet.png`
- Mobile, 390 × 844 viewport: `test-results/task06-substance-mobile.png`

Browser assertions confirm no document-wide horizontal overflow at tablet/mobile sizes; data tables retain their own horizontal scrolling. The profile uses a native modal dialog presented as a right drawer, with keyboard focus containment, Escape dismissal and opener focus restoration. Source changes clear old evidence, reset incompatible controls and independently recover from an unavailable source. No work beyond Task 06 was undertaken.
Screenshot-only stabilization: reduced-motion emulation and scroll-to-top were added to the browser test. Both Task 06 browser tests passed again (2/2, 38.8 seconds), and the screenshots were refreshed and visually inspected. Application source and production output were unchanged after the successful 11-test regression run.
