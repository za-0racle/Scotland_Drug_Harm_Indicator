# Phase 7 - full-stack research platform implementation

Completed locally on 10 November 2026. Stop for review; no deployment, database write, migration, RLS change, dissertation edit, source acquisition or replacement of Phase 2-6 research results was performed.

## Architecture and actual data flow

Vite + vanilla JavaScript + Chart.js -> central HTTP API client -> FastAPI -> either the three reviewed Supabase tables (server-side publishable/anon credential) or an allowlisted, SHA-256-verified saved analytical artifact. No active frontend component imports Supabase or a local analytical dataset. The older database/dashboard modules remain in the repository for historical compatibility and existing tests; `src/main.js` activates only the new platform. No React or alternative frontend framework was introduced.

Backend repositories handle storage, services handle geography/filtering, schemas validate bounded requests and responses, and routes expose read-only representations. The response envelope distinguishes `ready`, `empty`, `unavailable` and `error`, plus database observations, research results and metadata. Every artifact response carries its source path, manifest, analytical version, execution timestamp, checksum and limitations. Original row-level provenance is retained in record details and exports. Missing/suppressed observations remain null; no data are fabricated to fill a chart.

## Exact implementation files

Created:

- `backend/__init__.py`, `backend/config.py`, `backend/main.py`, `backend/refresh.py`, `backend/requirements.txt`, `backend/README.md`.
- `backend/api/__init__.py`, `backend/repositories/__init__.py`, `backend/repositories/artifacts.py`, `backend/repositories/supabase.py`, `backend/schemas/__init__.py`, `backend/services/__init__.py`, `backend/services/platform.py`.
- `backend/tests/conftest.py`, `backend/tests/test_api.py`.
- `src/api/client.js`, `src/platform/data.js`, `src/platform/charts.js`, `src/platform/dashboard.js`, `src/platform/style.css`.
- `tests/platform.test.js`, `vite.config.js`, this report.

Modified for Phase 7: `src/main.js`, `.env.example`, `e2e/dashboard.spec.js`, `playwright.config.js`. Existing unrelated working-tree changes were retained. Backend packages were installed in the existing local analysis virtual environment; `analysis/requirements.txt` and previous manifests were not edited. Direct backend dependency pins are in `backend/requirements.txt` (FastAPI 0.162.2, Uvicorn 0.54.0, HTTPX 0.28.1). Existing Chart.js/Vite/Playwright packages were used. Generated local `dist/`, test screenshots/results, bytecode and ignored research scratch are verification artifacts, not new source observations.

## API inventory

All analytical routes use `/api/v1`; interactive OpenAPI documentation is `/docs` on the backend.

| Routes | Data and purpose |
| --- | --- |
| `/health`, `/overview` | API status; real Supabase mortality access status plus artifact-derived coverage, counts and cutoffs |
| `/geographies`, `/geographies/{id}`, `/indicators`, `/geographies/{id}/indicators` | Actual source-derived area and indicator registries; Greenock explicitly unavailable |
| `/geographies/{id}/trends`, `/anomalies`, `/evidence`, `/comparisons` | Area-specific series, flags, contextual evidence and same-boundary comparisons (the latter four paths follow `/geographies/{id}`) |
| `/mortality/quarterly` | **Live Supabase** national quarterly observations, explicit columns and chronological order |
| `/monitoring/configurations`, `/monitoring/results` | **Live Supabase** reviewed configurations/results; results include associated configuration labels |
| `/mortality/annual` | Phase 6 registered-death observations, separate from suspected deaths |
| `/toxicology/forensic`, `/toxicology/assist`, `/toxicology/treatment`, `/naloxone/activity` | Phase 4 source-specific observations/trends |
| `/anomalies`, `/anomalies/runs`, `/anomalies/models`, `/anomalies/sensitivity`, `/anomalies/diagnostics`, `/anomalies/zero-baseline` | Phase 5 original screen and Phase 5C method comparisons, conditional bounds, runs and diagnostics |
| `/evidence/cross-source` | Phase 5C actual candidate compatibility and contextual assessments |
| `/forecasting/models`, `/forecasting/results`, `/forecasting/backtest`, `/forecasting/observations` | Frozen Phase 2 model scores, elapsed-period projection, rolling-origin records and history |
| `/geography/inverclyde`, `/geography/comparisons` | Phase 6 case-study contract and published five-year rate comparisons |
| `/sources`, `/methodology`, `/validation/status`, `/reports` | Source compatibility registry, methods/gaps, pending external validation and report catalogue |
| `/exports` | Allowlisted filtered CSV/JSON, bounded page, provenance/version/checksum/limitations; no arbitrary paths |

Common filters include geography ID, boundary, indicator/category, model, years, exact dates where supported, comparison area and pagination. Unsupported or inverted filters return errors; exact-date filters exclude undated study periods rather than inventing dates. Counts and denominators are not pooled into prevalence. Same-boundary comparisons retain source/area labels and do not create population rates. Comparison exports are deliberately hidden because a generic single-resource export would not reproduce both compared areas. Exports represent the bounded current page, not the entire underlying dataset.

## Geographic coverage and hierarchy

Registry verified from actual rows: **33 entries, 32 with data**.

| Boundary | Entries | Admitted data |
| --- | ---: | --- |
| Police division | 13 | Frozen quarterly suspected deaths, correctly labelled divisions |
| NHS health board | 14 | Weekly naloxone; GG&C treatment where available |
| Council | 1 | Inverclyde annual NRS registered drug misuse deaths |
| Country | 1 | Scotland national series with separately named measurement definitions |
| National forensic testing sample | 1 | Selected forensic detections, not national prevalence |
| ASSIST study sample | 1 | Source-labelled unequal study periods, not calendar quarters |
| Unknown | 1 | Unassigned naloxone geography; no hotspot attribution |
| Locality | 1 | Greenock: explicit no-compatible-local-series state |

All 13 divisions and 14 boards are selectable. No verified boundary geometry was available; selectors and comparative charts are provided without an invented map. Council, division, board, national sample and locality remain distinct. A reviewed naming alias for NHS Greater Glasgow & Clyde/and Clyde does not equate that board with a police division or council.

The featured Inverclyde case study displays the actual 2024 count **25**, and published **2020-2024** age-standardised rates **35.6 (95% CI 29.3-41.8)** versus Scotland **22.5 (21.9-23.1)** per 100,000. These are published five-year rates, not annual crude estimates. No compatible annual council denominator or Greenock-specific series is inferred.

## Frontend navigation and functionality

Eight functional sections: Intelligence Overview; Geographic Explorer; Trends & Patterns; Anomaly Detection; Surveillance Signals; Forecasting; Reports & Exports; Data & Methodology. Each requests FastAPI data. Dynamic geography/indicator/substance/year/model controls issue backend requests. Source series remain separate; charts with mixed indicators are suppressed rather than plotting incompatible measurements together. Single-indicator charts group areas into separate datasets, retain null gaps, preserve original values and destroy previous Chart.js instances safely. Tables and selectable record details expose precise values and full provenance; loading, empty, unavailable and error messages are distinct.

Anomalies expose original 47 flags, model-specific flags, sensitivity, diagnostics and sparse-count review. Signals expose runs, cross-source evidence, external-validation status and live database configurations/results. Historical forecasts are explicitly elapsed-period projections, with uncertainty bounds, model scores and backtest records; no new current forecast was generated. Reports expose the catalogue, geographic findings and source-quality gaps with controlled data exports. Desktop/mobile layouts, keyboard-focus controls, labelled filters and equivalent chart tables support accessibility; this is not a formal accessibility certification.

## Security and scientific gates

Only `mortality_quarterly`, `indicator_configurations` and `indicator_results` are requested from Supabase. Explicit columns, stable ordering, pagination and server-cap detection are retained. RLS remains enforced under anon access. Empty responses never assert a successful observation load. Credentials are read server-side, never returned or logged; secret/service-role credentials are refused. The frontend receives only its API base URL. CORS permits configured local origins; GET-only analytical endpoints accept validated filters, not SQL or filesystem paths. Artifact integrity/schema errors fail closed; no fake fallback data. CSV formula-leading text is escaped. No public script-execution, private narrative, `radar_intelligence` or unreviewed table endpoint exists.

Internal parameter/model robustness remains distinct from external alert validation. FOI remains pending; absent local alerts do not establish no-alert periods. No alert-based sensitivity, specificity, lead time, validated warning score, public-health endorsement or prospective performance is claimed. Source cutoffs and frozen-vintage limitations accompany research results. Source-specific live publication vintages and testing denominators remain unresolved.

Local refresh is an explicit CLI, documented in `backend/README.md`: allowlisted existing analytical pipelines may write only to a new private scratch directory. They cannot overwrite the baseline or automatically promote outputs to the API. No refresh/retraining was executed to replace research results in this phase.

## Actual verification

- Complete existing analytical suite plus the first 11 API tests: **92 passed in 346.05 seconds**. Subsequently, the final backend suite including the added refresh-destination guard and configuration-label implementation: **12 passed in 41.90 seconds**. Thus all 81 existing analytical tests and all 12 final backend tests ran successfully; these are separate executions, not a claimed single 93-test run.
- `npm test`: **22 passed** (19 existing + 3 new). Tests include HTTP contract/errors, API-driven values, chronological ordering, missing values and dynamic geographic choices.
- Final `npm run build`: **passed**, Vite 8.3.5, 14 modules; JS 220.86 kB and CSS 9.06 kB before gzip. Build output is local only.
- Final `npm run test:e2e`: **3 passed in 44.1 seconds**, Microsoft Edge/Playwright. Real backend/artifact checks cover all division/board choices, original/model flag counts, Inverclyde values, year-filter HTTP requests, historical-forecast disclaimer, FOI state, mobile overflow and explicit API error handling. A clearly labelled test-only intercepted response changes a displayed prediction from 248 to 999 and verifies the chart remains rendered; no application mock-data path was added. Pure chart-input tests independently verify changed API values alter chart data and preserve nulls.
- Initial browser run failed a short cold-load expectation and a query-string interception pattern; corrected test timeout/interception, then reran successfully. Cold enhanced-artifact parsing was measured at approximately 14.6 seconds in a separate process while tests were running. Subsequent artifact loads use the manifest/mtime cache.
- Final authorised read-only live Supabase smoke test: **36 mortality quarters, four configurations, 76 results; every result has a configuration label**. No credential values printed; no database permission change.
- Preservation: **85 protected earlier-phase hashes** validated by the existing guard; Phase 6 input/code/output hashes also match its unchanged manifest. Existing analytical tests reproduce outputs in ignored scratch rather than overwriting research artifacts.
- FastAPI/Starlette emits one TestClient HTTPX deprecation warning; tests pass. This does not imply production deployment readiness. No browser performance certification, penetration test or prospective scientific validation was performed.

## Run locally

From the repository root, terminal one:

```powershell
.\analysis\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\analysis\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal two:

```powershell
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173). Backend docs: http://127.0.0.1:8000/docs . During verification the frontend used http://127.0.0.1:4173 and the backend port 8000. Existing authorised publishable credentials are read from `.env.local` without changing it; preferred server variables and allowed origins are documented in `.env.example` and `backend/README.md`. A production frontend build alone does not provide an API server or production proxy.

## Screenshot locations

Generated browser captures: `test-results/phase7-geography-desktop.png` and `test-results/phase7-mobile.png` (local verification artifacts). Desktop shows Geographic Explorer -> featured Inverclyde -> annual series filtered from 2020; mobile shows Intelligence Overview. Reproduce in the running app before dissertation use.

VS Code evidence: `src/main.js:1` (active entry point), `src/api/client.js:1` (HTTP-only data access), `src/platform/dashboard.js:7` (eight-section interface and filters), `src/platform/charts.js:1` (Chart.js lifecycle), `backend/main.py:19` (API/CORS/exception handling), `backend/repositories/supabase.py:7` (approved explicit-column tables), `backend/repositories/artifacts.py:9` (artifact allowlist), `backend/services/platform.py:26` (source-derived geographic registry), `backend/tests/test_api.py:1` (API verification). These are screenshot starting lines; expand the relevant function in VS Code. No secret-bearing file should appear in screenshots.

## Limitations and Phase 8 acceptance readiness

Ready for local research acceptance testing, not deployment or operational warning use. Analytical routes intentionally expose historical verified artifacts rather than pretending unapproved raw database tables are public. No new observations, current forecast, local toxicity risk score, formal map, external reference-event metrics or Greenock outcomes were added. Comparative charts are bounded by pagination and use counts unless an explicit published rate is requested. First access to large analytical artifacts may be slow; cache invalidation follows file/manifest modification times. Deployment authentication, rate limits, production proxy/TLS, continuous audit logging and load testing remain future engineering work.

Phase 8 should perform researcher/user acceptance on every source/area combination, accessibility review, realistic-load/slow-network checks, report/export usability and independent scientific sign-off on source vintage/measurement labels. Any FOI response must pass completeness and harmonisation gates before an independently specified evaluation. No Phase 8 implementation or publication follows automatically from this completion.
