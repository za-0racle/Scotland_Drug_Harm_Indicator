# SDHI implementation audit

18 November 2026. Application revision: `ddc554d`. Repository and local application review against the Task 08S structure register and Phase 1–5 implementation reports. This is an application audit, not an operating-system security assessment or production certification.

Subsequent owner approval authorised both S08 charts and publication. The findings below describe the earlier checkpoint; see the [S08 release report](TASK08S_S08_RELEASE_REPORT.md) for that later implementation and release outcome.

## Finding

All authorised Task 08S presentation changes are implemented in the active application. No missing authorised screen, disconnected screen module or outstanding implementation placeholder was identified. Dedicated S08 charts were never authorised: their feasibility assessment is complete, and their absence is intentional.

The entry point imports `platform/shared.css` after the existing styles and calls `mountPlatform` from `platform/dashboard.js`. The earlier frontend is not the mounted application. `platform/shell.js` defines eight primary destinations and preserves the `compare`, `signals`, `methodology` and `exploration` aliases. The dashboard connects the dedicated screen modules and existing API client rather than substituting demonstration data.

## Implementation coverage

Paths below are relative to `src/platform/`; browser specifications are under `e2e/`.

| Approved change | Implementation inspected | Verification coverage | Status |
| --- | --- | --- | --- |
| S01 shared shell; Phase 1 identity and metadata | `shell.js`, `dashboard.js`, `shared.css`, initial `index.html` and `public/brand/`; comparison actions, responsive drawer, focus, themes and reader-facing status | `branding`, `shell`, `phase5`; metadata/asset unit tests | Implemented |
| S02 Study overview | `overview.js`, `overview-data.js`, dashboard lead panel: study aim, mortality history, period-labelled values, geographic evidence and secondary previews | `overview`, `phase2`, `phase5` | Implemented |
| S03 Comparison Studio | `comparison-studio.js`, `comparison-data.js`: compatible subjects, aligned chart, coverage, exact records and complete comparison export | `comparison-studio`, `comparison`, `phase2`, `phase5` | Implemented |
| S04 Mortality trends | `mortality.js`, adapters/data: source-specific trend, controls, supporting distributions and exact series exports | `mortality`, `mortality-adapter`, `phase2`, `phase5` | Implemented |
| S05 Toxicology patterns | `substance.js`, data/forensic adapter: three active sources, source-specific history and supporting views; unavailable individual-substance integration explained in Research | `substance`, `forensic-migration`, `phase2`, `phase5` | Implemented |
| S06 Geographic patterns | `geography.js`, `geography-data.js`: selected history, published rates and intervals, compatible peers, profiles and scoped exports | `geography`, `phase2`, `phase5`, `layout-resize` | Implemented |
| S07 Statistical monitoring | `dashboard.js`, `research-presentation.js`, `filters.js`: original configurations/results, separate CUSUM components, later screens, runs and pending validation | `phase3`, `phase5`; analytical/research presentation unit tests | Implemented |
| S08 dedicated EWMA/CUSUM charts | Conditional feasibility assessment in the Phase 3 report; original records remain available | Scope checked against structure register and Phase 3 report | Assessment complete; charts deferred pending approval |
| S09 Forecast evaluation | `dashboard.js`, `chart-data.js`, `charts.js`, `research-presentation.js`: scores, elapsed saved estimate, historical observations/backtest, exact intervals and exports | `phase3`, `forecast-integration`, `phase5`; API artifact-preservation regression | Implemented, including target-quarter fix |
| S10 Research | `research.js`: adopted aim, five objective descriptions, evidence links, findings, sources, methods, downloads and secondary database records | `phase4`, `phase5`, `acceptance` | Implemented |
| S11 shared editorial separation; Phase 5 cleanup | `presentation.js`, `record-inspection.js` and screen consumers: structured exact records, accessible methods/source details, technical provenance outside ordinary previews | `presentation`, `phase4`, `phase5`, `overview` | Implemented |
| Phase 5 readiness and resizing corrections | Backend sanitised diagnostics and bounded connection-timeout retry; real database preflight, fresh test servers; single chart sizing observer and cleanup | `test_database_diagnostics.py`, `dashboard`, `local-api`, `layout-resize` | Implemented |

O1 is represented by source integration and provenance; O2 by the five core analytical screens; O3 by original monitoring and separate later screens; O4 by retrospective forecasting; O5 by interaction and software testing. Software completion does not establish scientific validation or a formal user-effectiveness study.

## Integrity and completeness checks

- Compared the protected `analysis`, `datasets`, `supabase`, `public`, initial HTML, dependency manifests and `.gitattributes` against Phase 1 commit `6755071`: no changes. The later backend differences are the documented Supabase diagnostics/retry and API/diagnostic tests.
- Rechecked every active artifact catalogue entry through the existing SHA-256-validating repository. Rechecked all 48 backtest API rows, including model, origin, target, prediction and four interval bounds, against the verified artifact; all 12 target quarters remain 2023 Q1–2025 Q4.
- Confirmed the chart period helper recognises `target`; training origin does not substitute for the forecast target. Model series and saved intervals remain separate.
- Inspected the adopted aim/objectives, historical warnings, unresolved baseline discrepancy, external-validation status, source-specific limitations, geographic boundaries and export descriptions. No claim of completed RADAR validation, current forecasting or a Greenock outcome was introduced.
- Searched active application/backend source for TODO, FIXME and unfinished-implementation markers. Matches were ordinary form input placeholders, not implementation gaps. Structured record inspection uses text nodes; static shell templates are not evidence that source records execute as HTML.
- Existing planning documents retain their original proposal status as historical records. Their subsequent implementation is recorded in the phase reports and this coverage table; old wording does not mean the application remains unimplemented.

## Verification

Fresh checks for this audit: JavaScript **114 passed**; production build **passed**, 40 modules, with the same `index-BBTQQL8j.js` and `index-COuYk2Bq.css` assets as the accepted revision. Focused Python catalogue/backtest checks: **2 passed**, 13 deselected, one existing Starlette/HTTPX deprecation warning.

Fresh browser acceptance: **10 passed in one uninterrupted 2.9-minute run**, no test retries. This covers all eight screens with genuine configured data at desktop/mobile sizes, navigation breakpoints/focus and safe exact-record inspection. Health, mortality, monitoring configuration and monitoring result preflights all returned HTTP 200 with records. Fresh screenshots are in ignored `test-results/task08s-phase5/`; approved documentation screenshots were not overwritten. Raw run log: ignored `artifacts/phase5-readiness/system-audit-browser.log`.

The latest full verification on the same application sources remains **70 Playwright tests passed in one uninterrupted run**, **175 Python tests passed**, and **114 JavaScript tests passed**. See the [diagnostic verification report](TASK08S_PHASE5_DIAGNOSTIC_VERIFICATION_REPORT.md) and its saved evidence. The full suites were not rerun merely to duplicate those results; this audit adds fresh all-screen acceptance and integrity checks without changing application sources.

## Remaining boundaries

No new application defect requiring a correction was found in this audit. Supabase remains an external dependency; successful checks cannot guarantee future availability. Persistent failures remain visible.

Publication, complete public-site acceptance, external sharing-preview caches and reconciliation of the apex canonical URL with the hosting `www` redirect remain separate release work. The prior read-only public forecast check verified the fix and all 48 values; this audit does not assert that the public site runs local revision `ddc554d`.

Dedicated S08 charts and individual-substance integration remain outside authorised implementation. Original Chapter One objective wording was unavailable in the earlier dissertation review, so the adopted descriptions must not be represented as verified verbatim quotations. External alert validation, the monitoring baseline discrepancy, forecast selection/evaluation limits and source/geographic evidence gaps remain research limitations.

Only this audit document was added. No research output, application, database, infrastructure or dependency change; no push or deployment.
