# Task 08 — Geographic Explorer

## Delivered scope
Implemented the dedicated Geographic Explorer at `#geography` in the existing Vite/vanilla JavaScript, Chart.js and FastAPI application. The White & Gold shell and completed Task 02–07 screens are preserved. The existing source trends workspace remains at `#exploration`. No backend routes, Supabase permissions, dependencies, statistical models, frozen research files or Phase 9 integration were changed. Work stops after Task 08.

## Files created or modified
- Added `src/platform/geography-data.js`: approved geographic source contracts, registry identity validation, complete source loading, compatible rankings, period/area selection, profile preparation, searchable coverage preparation, map-unavailable contract and published-rate validation.
- Added `src/platform/geography.js`: introduction, boundary/source/indicator/area/period controls, verified summary cards, ranking bars, area histories, paginated observations, complete CSV/JSON history exports, modal profile drawer, same-boundary comparisons and CSV exports, published-rate context, searchable/paginated coverage, source disclosures and Comparison Studio navigation.
- Modified `src/platform/dashboard.js`: dedicated screen lifecycle and retained selections; removal of superseded geographic preview; compatible mortality-scope handoff to Comparison Studio. The generic source workspace remains available at `#exploration`.
- Modified `src/platform/chart-data.js`: verified Monday-week handling and missing-week display slots for the existing naloxone source, retaining the Task 02 series identity, null and irregular-period rules.
- Modified `src/platform/style.css`: responsive controls, cards, table containment and drawer styles using existing design tokens.
- Added `tests/geography.test.js` and `e2e/geography.spec.js`.
- Updated existing geographic browser assertions in `e2e/shell.spec.js`, `e2e/dashboard.spec.js`, `e2e/acceptance.spec.js`; generic-filter regression tests in `e2e/comparison.spec.js`, `e2e/usability.spec.js` and `e2e/local-api.spec.js` use the retained source workspace when they exercise its original controls.
- Added this report.

## Components
- Geographic research introduction and explicit boundary integrity/Greenock caveats.
- Boundary-first, source-aware indicator and area selection, with source-correct reporting-period ranges. No arbitrary chart-type control.
- Source-labelled summary cards for compatible scopes, reported periods, latest returned area value and units. No count-to-rate conversion or cross-boundary aggregation.
- Zero-based horizontal rankings at one source/indicator/boundary/reporting period; missing observations excluded with explicit notes, genuine zero values preserved.
- Selected-area line history for verified regular periods, null gaps and accessible source tooltips/legends. ASSIST remains unconnected ordinal study-period points.
- Area profile drawer with name, API identifier, actual boundary, available indicators, source-specific coverage/history, limitations and original provenance; modal focus containment, reverse-Tab wrapping, Escape and opener restoration.
- Full selected-area eligible observations with table pagination and complete eligible CSV/JSON exports; chart calculations do not depend on the visible table page.
- Same-boundary peer comparison using shared Comparison Studio `verifyDefinitions`, `verifyAreaSubjects`, `comparisonTable`, `completeComparison` and CSV logic. Unsupported peers remain unavailable rather than substituting broader scopes.
- Published NRS five-year ASRs and original 95% confidence intervals, with standard population, source cells, five-year death totals and population-vintage limitations.
- Searchable coverage/availability table across every registered scope and approved source, including Greenock's unavailable state, source failures and separate published-rate entries. Coverage search is independent of analytical filters.
- Explicit map-unavailable panel; no geometry or decorative regions are invented.
- Navigation to Comparison Studio. Supported mortality selections retain their boundary, area, source and period scope; other source types are labelled as navigation to the Studio's admitted mortality/category comparisons, with same-boundary activity comparisons available directly in the Explorer.

## APIs and artifacts
All calls use the existing API client and read-only endpoints:
- `/api/v1/geographies`: retained application registry, passed to the screen. API-generated identifiers identify evidence scopes, not official GIS polygons.
- `/api/v1/exports?resource=mortality_trends&format=json`: Phase 4 `mortality_quarterly.csv`, Police Scotland suspected-death quarters.
- `/api/v1/mortality/annual`: Phase 6 `validated_geographic_observations.csv`, NRS registered drug misuse deaths, Persons, annual registration years.
- `/api/v1/naloxone/activity`: Phase 4 `naloxone_weekly.csv`, weekly ambulance naloxone activity.
- `/api/v1/toxicology/forensic`, `/api/v1/toxicology/assist`, `/api/v1/toxicology/treatment`: Phase 4 `forensic_counts.csv`, `assist_percentages.csv`, `treatment_counts.csv`.
- `/api/v1/geographies/{area}/comparisons`: complete compatible peer observations, filtered to the selected exact reporting-period range after retrieval.
- `/api/v1/exports?resource=rates&format=json`: Phase 6 `published_five_year_rates.csv`, original Table C4 rates, intervals and source cells.
- `/api/v1/geography/inverclyde`: Phase 6 `dashboard_data_contract.json`, source definitions, standard-population/population-vintage notes, territorial allocation, unavailable annual crude-rate contract and Greenock restrictions.

Every source history is retrieved across all API pages. Stable totals/hashes and pagination completeness are checked; failed sources remain independently unavailable. Source observations retain original source labels while identity is checked against the API-supplied canonical `name`, identifier and boundary; no new alias crosswalk is inferred. Source checksums, source paths, cutoffs, publication fields and artifact metadata remain available in disclosures and exports. A bounded page is never silently presented as complete history.

## Verified geographic coverage
The registry supplies eight distinct boundary/scope types:
- **Local authority / council:** Inverclyde; 2010–2024 NRS registered drug misuse death counts. Only one admitted council exists, so no council peer ranking is possible.
- **Police Scotland divisions:** 13 divisions, including Renfrewshire and Inverclyde; 2017–2025 suspected-death quarters. Divisions are not local authorities.
- **NHS health boards:** 14 boards for ambulance naloxone activity; treatment urine detections only in NHS Greater Glasgow and Clyde. Different service/sample measures remain separate.
- **Scotland country total:** separately labelled national registered deaths, suspected deaths and naloxone observations. National totals are never included as peer divisions/boards or summed with their constituent areas.
- **Greenock locality:** no compatible direct outcome series. No council, police or health-board outcome is assigned to Greenock.
- **National forensic testing sample:** source-specific detection categories; a sampling scope, not a polygon or representative population.
- **ASSIST study sample:** selected emergency-department cohort percentages, unequal study periods and unavailable denominators; not a territorial population.
- **Unassigned geography:** source 'Unknown' records, explicitly not a verified region or peer ranking area.

Compatible count rankings are available for police divisions and health boards when two or more observed same-period values exist. Treatment, forensic and ASSIST sources have only one admitted scope each and do not fabricate geographic peers. NRS counts have one council and one country, which are not interchangeable boundaries.

## Published rates and unavailable measures
Published Table C4 five-year age-standardised rates exist for Inverclyde and Scotland, windows 2010–2014 through 2020–2024, per 100,000 using the **2013 European Standard Population**. The interface displays original published values and confidence limits; it does not recalculate rates, derive new ratios/differences, back-solve populations or use unrelated health-board denominators.

The published table is contextual source evidence: Inverclyde is a council and Scotland a containing national total. It is explicitly separated from the same-boundary peer-comparison function and rankings. Scotland includes Inverclyde, adjacent five-year windows overlap four years, and neither source-provided confidence limits nor descriptive differences establish independent-sample significance or causation. Published windows are explicitly independent of the annual trend filter.

The source contract documents revised population vintages and 2013 ESP standardisation. Numerical annual council and age-specific population denominators are not provided by these API records. Annual local crude rates and population-adjusted rankings are therefore unavailable. The frozen NRS 2024 publication vintage is labelled as historical, not the latest release. Registration years are not exact occurrence dates; territorial coverage does not establish resident-only council incidence.

No map geometry, spatial crosswalk or official geographic identifier-to-polygon contract was found. No choropleth is implemented. No Phase 9 individual substances, Greenock-specific mortality estimates, causal geography claims or operational alerts are introduced.

## Tests and build
Final execution results and screenshot paths are recorded after browser verification.

## Validation record
- Final `npm test`: **83 passed, 0 failed**, including 12 geographic tests covering boundary/source identity, API-provided canonical names, rank eligibility, counts versus rates, missing quarters/weeks, area profiles, same-boundary comparison safeguards, unavailable geometry, coverage search/pagination, published-rate windows/provenance and complete weekly source loading.
- Final `npm run build`: **passed**, 29 modules transformed; no dependencies added.
- Browser tests cover default council context, all source/boundary control transitions, police and health-board peer rankings, complete same-boundary comparisons, Studio handoff, quick-dialog defaults, profile focus/Escape, published rate restrictions, complete CSV/JSON exports, availability search, unavailable sources, tablet/mobile overflow, and the existing Task 02–07 screens.
- Initial geographic browser verification exposed source-label aliases such as `Scotland national total` versus the API canonical `Scotland` name. Validation now checks the API-provided canonical name, identifier and boundary and retains the original source label unchanged. A focused regression test covers this.
- The first full browser run completed 35 cases: 32 passed; one obsolete Overview assertion and two localhost-specific checks failed. The old assertion now checks the current outage message location. The existing service on localhost:5173 returned HTML for `/api/v1/health`; it was left running.
- Added an optional `E2E_LOCAL_PORT` override to `playwright.config.js` and the localhost regression tests so the full suite can use an isolated test server. The default remains 5173; the final run uses 55173 without changing the application's API or server configuration. `playwright.config.js` is an additional modified file.
- The final full browser run uses the production preview for the main application and the isolated local Vite server for the explicit localhost proxy test:

```powershell
$env:E2E_LOCAL_PORT='55173'
npx playwright test --config playwright.overview.config.js
```

Final browser outcome and screenshot evidence are appended after execution.

## Remaining limitations
No geometry/crosswalk or official identifier-to-polygon mapping is admitted. Only Inverclyde council and Scotland have integrated NRS geographic data; other councils and Greenock do not gain synthetic outcomes. Comparable denominators are not available for annual local crude rates. Health-board activity/detection measures and selected toxicology cohorts do not measure community prevalence or confirmed overdose incidence. Published ASRs retain their historical source vintage and overlapping-window/nested-area limitations. Coverage is limited to the existing approved sources, not every Scottish geographic measure. First load retrieves complete approved histories to establish coverage; table pages do not limit analysis. A failed geographic registry bootstrap remains an explicit shell error rather than a fabricated fallback. The existing localhost:5173 service was not repaired or replaced by this task.
