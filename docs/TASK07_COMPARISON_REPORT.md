# Task 07 — Comparison Studio

## Delivered scope
A dedicated Comparison Studio is implemented at the retained `#comparison` route, with `#compare` accepted as an alias. Eight primary navigation destinations are retained. This is a local frontend change using the existing vanilla JavaScript, Vite, Chart.js, API client and White & Gold shell. No backend routes, Supabase permissions, analytical models, dependencies, frozen research artifacts or Phase 9 integration were changed. Work stops at Task 07.

## Files created or modified
- Added `src/platform/comparison-studio.js`: source/type controls, two named subjects, compatible boundary/geography selection, reporting-period controls, aligned chart, paired coverage summary, paginated aligned observations, original-record disclosures, methodology, retry handling and complete eligible CSV export.
- Modified `src/platform/comparison-data.js`: shared complete pagination loader; area/category validation and alignment; requested-subject validation; coverage summary; reporting-range preparation; original-category role assignment; CSV columns for subjects, units, indicator identities, source, definitions, coverage and provenance.
- Modified `src/platform/comparison.js`: retained quick dialog uses shared complete loader, subject validation, alignment and exports; explicit keyboard focus wrapping, native Escape dismissal and opener restoration are retained.
- Modified `src/platform/charts.js`: passes the explicit comparison kind to the shared compatibility validator without altering series identity or permitting arbitrary chart switching.
- Modified `src/platform/dashboard.js`: mounts, refreshes and disposes the studio; retains screen selections and the existing quick-dialog toolbar action.
- Modified `src/platform/shell.js`: adds the `#compare` alias without adding navigation destinations or breaking `#comparison`.
- Modified `src/platform/style.css`: responsive studio controls, cards, chart/table containment and methodology details within existing design tokens.
- Added `tests/comparison-studio.test.js` and `e2e/comparison-studio.spec.js`.
- Updated `e2e/shell.spec.js`: replaces obsolete Task 03 placeholder assertions with completed Substance/Comparison screen and quick-dialog focus assertions.
- Added this report.

## Comparison types
1. **Two geographic areas, one source and indicator**: Police Scotland suspected drug-death counts at the same police-division boundary. National totals are not offered as substitutes for divisions. NRS registered annual deaths remain a selectable source, with an explicit unavailable state because the integrated geographic dataset has only one area at each supported boundary (Scotland country and Inverclyde council). Suspected and registered definitions are never compared as one measure.
2. **Two original substance categories, one source and geography**: forensic detections, ASSIST reported cohort percentages or treatment urine-sample detections. Subjects retain their original indicator/category identities. The source, geographical coverage, measurement units, sample definition and reporting windows must match. Categories overlap and cannot be added into a composition or interpreted as independent death counts.

Separate-period contrasts and different-indicator comparisons are disabled with explanations. No rate comparisons, population denominators, arbitrary chart-type selector, statistical testing, causal analysis, new monitoring models, raw RADAR intelligence or Phase 9 individual substances are introduced.

## Reused components and existing APIs
- `completeMortality`, `validateMortality` and `mortalitySources` supply approved mortality source definitions and complete source history for subject/period controls.
- `completeSubstances`, `substanceOptions`, `categoryOf` and `compatibleSubstances` supply the existing source-specific substance contracts. No observation or label normalization is added.
- `comparison-data.js` is shared by the studio and quick dialog. Both use the same area compatibility validator, period alignment, complete comparison pagination and CSV serializer. Category comparisons explicitly opt into the source-compatible category validator while retaining original records.
- The retained chart component preserves Task 02 identity, null gaps, tooltips and accessible series controls. Regular quarters/months/years use aligned historical lines. ASSIST uses unconnected ordinal-sorted categorical points because unequal study intervals do not imply equal elapsed time.
- Existing shell/filter routing and API configuration are retained; the shared generic filter panel is hidden while the dedicated studio controls are active.

Existing endpoint calls (all read-only):
- `/api/v1/geographies` during retained shell initialization.
- `/api/v1/exports?resource=mortality_trends&format=json` for verified Police Scotland history and control options.
- `/api/v1/mortality/annual` for registered annual source options and explicit peer availability.
- `/api/v1/geographies/{first_area}/comparisons?indicator=...&compare_to=...&start_year=...&end_year=...&offset=...&limit=1000` for the complete eligible two-area comparison. Exact quarter selection is applied after retrieval; year filtering does not imply a whole-year-only display.
- `/api/v1/toxicology/forensic`, `/api/v1/toxicology/assist`, `/api/v1/toxicology/treatment` for complete approved source-specific category observations.
- The retained quick dialog also uses `/api/v1/geographies/{area}/indicators` and the same existing geographic comparison endpoint. No new API filter parameters are sent.

## Compatibility and completeness rules
- Areas must share source ID/path/hash, indicator identity, reporting definition, measurement units, period basis, geographic boundary and applicable model/window identity. Expected area-role IDs and indicator identity must match the selected request.
- Category comparisons allow distinct original category indicators only within the same source/hash/path, geography, boundary, measurement unit, reporting basis, endpoint/outcome, sampling definition and model identity. A comparison subject cannot contain multiple category definitions.
- Sex, age group, sample type, population/denominator definition and standard population must agree where supplied. Population-rate units are rejected because this contract does not verify compatible denominators and standardisation.
- Period labels must align with identical date boundaries, study-period IDs and ordinals where supplied. Duplicates fail closed. ASSIST never receives invented calendar dates or calendar-quarter reassignment.
- Complete pagination checks stable totals and artifact hashes, refuses overflows and empty intermediate pages, enforces a 10,000-comparison-row bound and ignores obsolete responses after selection changes or navigation. Partial results are not rendered or exported as complete comparisons. Endpoint artifact hashes must match the source used to configure studio selections.
- Missing periods remain absent source records represented by null alignment slots. Explicit unavailable values remain null; genuine recorded zeros remain zero. Shared source-record periods and observed paired periods are reported separately, with missing-period and unavailable-value counts.
- Table pagination never changes summary/chart scope. CSV contains the complete aligned comparison across every eligible API/table page, not only the visible page; its scope label states that this does not establish complete source history. Original source records, filters, subjects and provenance are exported. Spreadsheet formula escaping is retained.

## Scientific limitations
Police Scotland deaths are originally suspected and provisional, with the legacy ten-day quarter timing adjustment; they are not registered NRS deaths or population-adjusted risks. NRS is annual registration-year data, not occurrence-year data or a compatible police-division series. Council and police-division boundaries cannot be substituted, and wider-area results cannot be attributed to Greenock alone.

Forensic data describe a testing sample, not Scotland population prevalence or causal death counts. Treatment data describe selected urine samples in NHS Greater Glasgow and Clyde; source opioids exclude treatment opioids. ASSIST percentages describe selected participating emergency-department cohorts, with unequal periods and shortened Q9 recruitment; denominators are unavailable and percentages are never pooled. Testing and cohort selection changes limit temporal interpretation. No statistical significance, causal inference or operational-alert interpretation follows from any displayed comparison.

## Verification
Final command outcomes and screenshot paths are recorded below after browser verification.

## Validation details
- `npm test`: **71 passed, 0 failed**, including 9 new focused data tests for compatible areas, mismatched definitions/boundaries/units/models/populations, category comparisons, irregular ASSIST periods, missing paired observations, complete pagination, stale requests and provenance-safe exports.
- `npm run build`: **passed**, 27 modules transformed. No new dependency was introduced.
- Browser checks run against the production build through `playwright.overview.config.js`, using the existing FastAPI server and Microsoft Edge. They cover both studio routes, geographical/category comparisons, all three toxicology sources, explicit unsupported NRS peer states, CSV download, table pagination, retry, obsolete-response invalidation, quick-dialog keyboard focus and Escape, mobile navigation, retained selections, tablet/mobile overflow and the completed Overview/Mortality/Substance screens.
- The first browser run found a reverse-Tab escape immediately after opening the quick dialog; fixed with an explicit visible-control focus loop. It also exposed an obsolete shell test still expecting unimplemented Task 03 placeholders; the test now checks the completed Task 06/07 screens.
- Desktop and mobile screenshots were visually inspected. Screenshots use reduced-motion emulation and top-of-page scroll positions to show settled charts and the shell.

Screenshot artifacts:
- `test-results/task07-comparison-desktop.png` (1440 × 1100 viewport, full page)
- `test-results/task07-comparison-tablet.png` (900 × 1000 viewport, full page)
- `test-results/task07-comparison-mobile.png` (390 × 844 viewport, full page)

The final browser regression outcome is appended after execution. This remains a local implementation; no deployment or work on Geographic Explorer or subsequent tasks was performed.

Final production browser regression: **16 passed, 0 failed (2.1 minutes)** with:

```text
npx playwright test --config playwright.overview.config.js e2e/comparison-studio.spec.js e2e/comparison.spec.js e2e/substance.spec.js e2e/mortality.spec.js e2e/overview.spec.js e2e/shell.spec.js
```

This is a scoped regression run, not a claim that every repository end-to-end test was executed. All frontend tests and the production build also passed as recorded above. No required Task 07 work remains; unsupported comparison types remain explicitly unavailable.
