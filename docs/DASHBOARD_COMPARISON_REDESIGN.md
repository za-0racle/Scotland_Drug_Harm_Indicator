# Dashboard comparison and visual refresh

Implemented locally using Vite, vanilla JavaScript, CSS, Chart.js and the existing FastAPI endpoints. All eight navigation modules remain. No backend, Supabase, credential, RLS, research-data, statistical-method or dissertation changes were made. Nothing was deployed.

## Comparison experience

Compare Data is available from Intelligence Overview, Geographic Explorer and Trends & Patterns. It opens a native modal dialog with an accessible name/description, explicit close button, backdrop dismissal, Escape support, browser-managed focus containment/background inertness, restored trigger focus and body-scroll locking. The responsive dialog preserves the underlying page filters. Reset restores the current dashboard's area, measure and year defaults; closing discards the modal results without changing dashboard selections.

The modal uses the existing `/geographies` registry, `/geographies/{id}/indicators` metadata and `/geographies/{id}/comparisons` endpoint. Both the inline filters and modal share the same available-area/boundary/indicator compatibility helper. Registered and suspected mortality remain distinct measures. Single-area scopes, including Inverclyde council, explain why no same-boundary comparator is available; wider boundaries are never substituted. Unequal study periods do not offer unsupported calendar-year controls.

Changing selections clears previous results, and sequence tokens discard stale responses. Metadata failures, loading, unavailable/incompatible scopes, empty results and request errors have separate states; failed requests provide retry. Inverted year ranges are rejected. Comparisons retrieve the complete bounded response through pagination, with a 10,000-observation safety cap requiring a narrower period. No partial response is presented as a complete comparison. The existing inline Reset control is disabled during metadata/result updates and re-enabled after completion or error. Pointer activation preserves field focus until the reset transaction begins, preventing blur-triggered changes and layout updates from swallowing the click. Changes during that transaction are ignored, and focus moves to geographic scope. The unchanged existing reset regression passes. Reset defaults and scientific filter meanings remain unchanged.

The result includes side-by-side source-row counts, a shared-period chart, aligned observation table and source/definition disclosure. Values remain unchanged; unavailable values and periods remain missing rather than zero. Units, indicators, reporting bases, definitions and boundaries must agree before rendering. Duplicate period/area measurements fail visibly rather than being combined. CSV exports exactly the displayed aligned values, missingness states and both original records plus response metadata; formula-leading text is escaped. No significance, population-rate difference, alert or causal conclusion is calculated.

## Presentation and motion

Default dark-navy palette, optional persistent light mode, clearer navigation state, grouped workspace actions, consistent cards and fields, scrollable tables, mobile layouts and accessible focus outlines. Chart colours and labels follow the palette. Chart instances are managed per canvas so comparison and dashboard charts coexist and are destroyed safely. Short chart/modal/hover transitions and loading skeletons respect `prefers-reduced-motion`; no new dependency was added.

## Changed files

- `src/platform/dashboard.js`: comparison entry points, workspace actions and theme control.
- `src/platform/comparison.js`: modal lifecycle, dependent metadata, requests, states, result rendering and export.
- `src/platform/comparison-data.js`: shared compatibility, definition checks, period alignment and safe CSV formatting.
- `src/platform/filters.js`: uses shared compatibility helper; existing controls remain.
- `src/platform/charts.js`: independent chart lifecycles, palette-aware labels/series and reduced-motion handling.
- `src/platform/style.css`: theme, navigation, cards, tables, modal, responsive and animation styles.
- `tests/comparison.test.js`: compatibility, missing/zero values, ordering, reporting definitions and CSV regressions.
- `e2e/comparison.spec.js`: real API comparisons/download, keyboard/focus, retry, stale result clearing, unavailable scopes, empty state, mobile and theme checks.
- This report.

`src/main.js` and `src/api/client.js` were inspected and retained. The central HTTP client remains the only transport; no frontend database credential or direct Supabase request was introduced.

## Verification

Executed verification:

| Command/check | Actual result |
| --- | --- |
| `npm test` | **33 passed**, including four new comparison transformation/export tests |
| `npm run build` | **Passed**: Vite 8.3.5, 18 modules, JS 245.88 kB / 84.29 kB gzip; CSS 16.48 kB / 4.36 kB gzip |
| `.\analysis\.venv\Scripts\python.exe -m pytest backend/tests -q -p no:cacheprovider` | **19 passed** in 181.07 seconds; existing TestClient deprecation warning |
| `npm run test:e2e -- --retries=1` | **16 passed, 3 failed**, 8.6 minutes; all three new comparison tests passed, as did reset, presentation and artifact-backed coverage |
| Original isolated filter-reset regression after fix | **Passed**, with its original assertions |
| Sampled presentation contrast | All seven samples above 4.5:1; lowest 6.39:1 (refresh control) |
| Research integrity | Original input workbooks, 105 protected earlier-phase files, all Phase 9 non-manifest outputs and figures verified unchanged |
| `git diff --check` / direct new-file whitespace checks | Passed, with existing Git line-ending notices |

The final browser failures are the existing all-eight-sections acceptance bootstrap, backend-connected dashboard bootstrap and mobile overview bootstrap. Each expected a ready live overview but received `Supabase read failed; check backend connectivity and approved RLS access`, including the permitted retry. Earlier executions exercised these views successfully; the final suite is **not fully green**. The new comparison uses actual existing artifact-backed API endpoints and passed independently of those live reads. Live overview acceptance must be repeated when upstream reads are reliable. No data substitution, credential change, policy change or weakened assertion was used to conceal the failures.

The first restricted `npm test` and build attempts could not spawn child processes (`EPERM`); authorised executions outside that restriction ran successfully. Initial browser checks caught inherited status-text contrast in the dark theme and a case-sensitive new-test selector; these were corrected. Reset debugging showed that pointer-down focused Reset but blur-driven field updates prevented the subsequent click; the transaction/focus fix passed the unchanged regression. A targeted run was interrupted while source edits caused a transient Vite import-analysis error; completed source syntax checks and subsequent production builds passed. Backend tests emit the existing Starlette/HTTPX TestClient deprecation warning, without assertion failures. No full historical Python re-analysis was necessary or executed for these frontend changes.

Screenshots are local verification artifacts under `test-results/comparison-desktop.png`, `test-results/comparison-mobile.png`, `test-results/phase8-desktop.png` and `test-results/phase8-mobile.png`. These are reproducible captures of API-backed research views, not published assets. Keyboard/native-dialog and sampled contrast checks are not a complete accessibility certification. The feature intentionally supports same-dataset, same-boundary geographic comparison, not arbitrary cross-source measurement joins or a new Inverclyde-versus-country count comparison.
