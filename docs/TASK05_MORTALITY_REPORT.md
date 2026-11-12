# Task 05: Mortality Analytics

Implemented locally on 11 November 2026. Work is limited to Mortality Analytics and the shared routing, heatmap reuse and testing changes needed to preserve the existing application. No backend endpoint, Supabase policy, database schema, statistical model, frozen analytical artifact or dependency was changed.

## Files

| File | Change |
| --- | --- |
| `src/platform/mortality.js` | New dedicated source-aware mortality UI, controls, descriptive box plot, horizontal ranking, search/pagination, CSV and source drill-down |
| `src/platform/mortality-data.js` | Complete API loading, validation, compatible selection, distribution, ranking and table/export preparation |
| `src/platform/dashboard.js` | Dedicated screen mounting, cleanup, source/area/year persistence across refresh, and reuse of the source-detail drawer |
| `src/platform/overview.js` | Exports the existing heatmap and provenance helpers; heatmap caption accepts the actual geography while retaining the overview's Scotland default |
| `src/platform/filters.js` | Retains the former multi-source filter behaviour under `#exploration` |
| `src/platform/shell.js` | Related links between Mortality Analytics and the retained multi-source trends workspace |
| `src/platform/presentation.js` | Mortality-specific research description and legacy workspace description |
| `src/platform/style.css` | Scoped mortality controls, charts, rankings, SVG distribution and responsive table styles |
| `tests/mortality.test.js` | Seven focused regression tests covering the requested data-handling cases |
| `e2e/mortality.spec.js` | Source switching, refresh preservation, ranking, table independence, export, unavailable source and responsive screenshots |
| `e2e/comparison.spec.js`, `e2e/usability.spec.js`, `e2e/presentation.spec.js` | Existing multi-source exploration checks follow the retained `#exploration` route |
| `playwright.overview.config.js` | Tests the production preview at 4173 without HMR or reserving development port 5173 |
| `docs/TASK05_MORTALITY_REPORT.md` | This report |
| `artifacts/task05/` | Desktop, tablet and mobile screenshots |

The build regenerated ignored `dist/` output. The eight primary navigation entries remain unchanged. `#trends` is the dedicated Mortality Analytics destination; the former shared source exploration and compatible comparison functionality remain available through **Other source trends** at `#exploration` and through Geographic Explorer. No Substance Intelligence or Comparison Studio redesign was performed.

## Screen components

- Source selection, source-specific geographic boundaries, reporting area and year controls, plus reset.
- Verified latest observation, period coverage, valid-count coverage and reporting-basis cards.
- Dedicated quarterly suspected-death or annual registered-death line using unchanged Task 02 chart preparation.
- Reused accessible year-by-quarter heatmap for suspected deaths. The annual view explains why a quarterly heatmap is not applicable.
- A one-area, one-source descriptive distribution with median, quartiles, whiskers, outliers and an equivalent numeric summary table.
- Descending horizontal count bars for compatible peer areas at one explicitly selected reporting period. National totals, police divisions and councils are never mixed.
- Searchable table with 12 rows per page, exact reporting labels, source, units, quality notes and original-record drill-down.
- CSV containing all search matches across pages, original record JSON, artifact provenance and explicit source/area/year/search scope.
- Visible source definitions, limitations and documented methods. Selected source/area/year filters survive refresh and theme redraw; deliberate source switching resets dependent controls to compatible defaults.

## API and source coverage

| Source | Existing API | Verified local coverage and limitations |
| --- | --- | --- |
| Police Scotland suspected deaths | `/api/v1/exports?resource=mortality_trends&format=json` with bounded pagination | Existing Phase 4 `mortality_quarterly.csv`; 504 source observations across Scotland and 13 police divisions, 2017 Q1–2025 Q4. Legacy ten-day timing adjustment and suppressed/null observations are retained. Divisions are not council or locality boundaries. |
| NRS registered drug misuse deaths | `/api/v1/mortality/annual` with bounded pagination | Existing Phase 6 `validated_geographic_observations.csv`; 30 annual Persons observations for Scotland and Inverclyde council, 2010–2024. These are registration years and the NRS drug misuse definition, not occurrence quarters or wider drug-poisoning counts. |

The existing JSON export endpoint is consumed through the central FastAPI client as a provenance-bearing read representation; no new endpoint was created. All API pages are fetched before charts are prepared. Truncated responses, changed totals/checksums during pagination, duplicate area-period records, incompatible definitions and invalid values fail closed. The loader has an explicit 10,000-record ceiling rather than silently truncating history.

## Distribution convention

The display uses **Hyndman–Fan type-7 quartiles**, with linear interpolation at zero-based sorted index `(n−1)p`. R documents type 7 as its default sample-quantile method. [R sample quantile documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/quantile.html).

Whiskers end at the most extreme observed values within `Q1 − 1.5×IQR` and `Q3 + 1.5×IQR`; values beyond those fences are shown as descriptive outliers. The 1.5-IQR whisker convention is documented in [R box-plot statistics](https://stat.ethz.ch/R-manual/R-devel/library/grDevices/html/boxplot.stats.html). The UI explicitly distinguishes its type-7 quartiles from R's separate boxplot hinge calculation. No notches or confidence intervals are inferred.

The minimum of eight observed comparable periods is an explicit screen display rule, not statistical validation. Nulls are excluded without becoming zero; zeros are included. Groups never pool different areas, sources, units or reporting definitions. Time trends and temporal dependence limit interpretation; an outlier is not an operational anomaly or public-health alert.

## Scientific safeguards

Suspected and registered deaths remain distinct. Source changes update every dependent control and visualisation. Annual records cannot acquire quarterly values. Missing reporting periods remain gaps in the line and unavailable cells in the heatmap. Counts are never converted into unsupported rates, percentage changes or population risk.

Rankings use a single source, boundary, reporting period and period-boundary definition. Missing area values are listed as unavailable, not ranked as zero. The NRS dataset contains only one council and one country total, so a same-boundary peer ranking is unavailable; a national total is not substituted for a council peer.

Table search and pagination only affect the table and its explicitly labelled matching-record export. They never change summaries, the line, heatmap, distribution or ranking. Search covers the displayed period, area, measure, source name, quality and notes; hidden workbook filenames do not spuriously match a requested year. Original filenames, source cells and records remain available in provenance and CSV.

## Tests and visual verification

- `npm test`: **54 passed, 0 failed**.
- `npm run build`: **passed**, 24 modules transformed.
- Final selected browser regression run against the production build: **17 passed, 0 failed**, approximately 1.7 minutes, Microsoft Edge.
- Browser command: `npx playwright test --config playwright.overview.config.js e2e/mortality.spec.js e2e/overview.spec.js e2e/shell.spec.js e2e/comparison.spec.js e2e/usability.spec.js e2e/presentation.spec.js --workers=2`.
- Unit cases cover source/boundary compatibility, quarterly versus annual basis, missing quarters and zeros, heatmap preparation, independently specified quartiles and whiskers, outliers and insufficient samples, geographic compatibility, search/pagination independence, CSV provenance/safety, complete API pagination and fail-closed validation.
- Mortality browser checks cover both sources, unavailable quarterly data with independent annual access, source reset, source/area preservation across refresh, all 13 police-division bars, search scope independence, page navigation, CSV download and record details.
- Desktop (1440px), tablet (900px) and mobile (390px) checks include page overflow, chart visibility and scientific text. The distribution and detailed table scroll internally at narrow widths. Screenshots use reduced motion and start at the page top.
- Sampled existing shell contrast checks remained approximately 6.0:1–15.3:1. These samples and browser checks are not a complete accessibility certification.
- An initial browser run found that searching for a year also matched hidden workbook filenames. Search was corrected to use the visible source name; a unit assertion now covers that case. An interim development-server run was interrupted by Vite hot reload during final edits, so final browser verification uses the built preview without HMR.

## Screenshots

- [Desktop mortality](../artifacts/task05/mortality-desktop.png)
- [Tablet mortality](../artifacts/task05/mortality-tablet.png)
- [Mobile mortality](../artifacts/task05/mortality-mobile.png)

## Remaining limits

These are frozen retrospective source vintages, not a live surveillance service. The NRS data support Scotland and Inverclyde only, not all councils. Greenock-specific outcomes, compatible annual council denominators and additional same-boundary registered-death peers remain unavailable. Distribution summaries describe historical variation and do not remove temporal dependence or changing source practices. Search text and table page reset on scope changes/refresh, while valid source/area/year selections are retained.

No new dependency, permission change or backend approval is required. Nothing was published. Work stops after Task 05; the next analytical screen requires separate approval.
