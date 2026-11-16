# Task 08B — frontend and backend regression baseline

Executed on 12 November 2026 against the existing application, without application/test changes to obtain passing results.

| Check | Current result | Evidence |
|---|---|---|
| Existing frontend unit tests | **83 passed, 0 failed** | `frontend-tests.txt` |
| Production Vite build | **Passed; 29 modules** | `build.txt` |
| Existing backend tests | **19 passed**, one existing dependency deprecation warning | `backend-tests.txt` |
| Full existing browser suite | **35 passed, 0 failed; 3.8 minutes** | `browser-tests.txt` |

Commands:

```powershell
npm test
npm run build
.\analysis\.venv\Scripts\python.exe -B -m pytest backend/tests -q -p no:cacheprovider
$env:E2E_LOCAL_PORT='55173'
npx playwright test --config playwright.overview.config.js
```

Initial sandboxed Node test/build attempts failed because Windows denied child-process spawning (`EPERM`). The existing commands passed when rerun with the necessary process access. Initial sandboxed database reads were unavailable; approved network reads succeeded. Initial evidence is retained in `frontend-tests-sandbox.txt`, `build-sandbox.txt` and `database-sandbox.json`; it is not misreported as an application test failure or absent database table.

The browser configuration uses the built production preview for the main app and the existing isolated local-port override. It permits reuse of existing local servers, so this is not a clean remote deployment certification. No service on the developer's port 5173 was replaced. The installed Windows Edge browser was used; no dependencies or browser downloads were installed.

## Screen behaviour preserved

| Completed screen | Existing baseline behaviour | Principal existing evidence |
|---|---|---|
| Intelligence Overview | Complete-year descriptive mortality, source disclosures, forecast context and independent outage states | `tests/overview.test.js`, `e2e/overview.spec.js`, `e2e/usability.spec.js` |
| Mortality Analytics | Source-aware quarter/year controls, boundary restrictions, rankings, search, exports and unavailable sources | mortality unit tests; `e2e/mortality.spec.js` |
| Substance Intelligence | Source-specific categories/units, irregular ASSIST periods, profile drawer, exports and independent source errors | substance unit tests; `e2e/substance.spec.js` |
| Comparison Studio | Same-boundary/definition compatibility, eligible categories, complete exports, changed-selection protection and keyboard navigation | comparison unit tests; `e2e/comparison-studio.spec.js`, `e2e/comparison.spec.js` |
| Geographic Explorer | Boundary-first controls, compatible count rankings, historical gaps, profile focus, published-rate context, coverage search, complete exports and unavailable map/locality evidence | `tests/geography.test.js`, `e2e/geography.spec.js` |

The full browser run additionally covers shell, acceptance, dashboard, presentation, local proxy, responsive layouts and keyboard interactions. Existing later-screen smoke/navigation checks do not implement or integrate later analytical work. Existing screenshot-producing checks may refresh ignored `test-results` artifacts; those are not frozen research files.

Backend tests exercise artifact integrity handling, envelope/pagination/filter contracts, geographic compatibility and reviewed DB access behaviour. Some backend scenarios intentionally use synthetic fixtures. They are regression evidence, not substitutes for the separate live database verification.

The dependency warning concerns Starlette's current httpx TestClient integration. It did not fail checks; no dependency was changed. Passing tests are not comprehensive accessibility certification, scientific external validation, prospective forecasting validation or operational deployment approval.
