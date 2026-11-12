# Phase 8 dashboard API defect correction

Date: 10 November 2026. Scope: restore the existing local dashboard data connection. No redesign, new analytical feature, database/schema/RLS change, data insertion, secret-key integration, migration, deployment, dissertation edit or modification of historical outputs was performed.

## Root cause and reproduction

The user's Vite process on **localhost:5173** was stale: its process start time predates the creation/update of `vite.config.js`. It served the current frontend modules through HMR but had not loaded the new `/api` proxy. FastAPI was already responding correctly on 127.0.0.1:8000, and the separate acceptance Vite process on 127.0.0.1:4173 correctly proxied the same requests. There was no `VITE_API_BASE_URL` override in the local settings. Changing Supabase credentials could not fix this routing defect.

The original Phase 8 tests used port 4173 and therefore failed to exercise the user's already-running process on port 5173. The earlier acceptance report overstated applicability to that process. This report supersedes that assumption and adds an explicit 5173 regression.

Observed before changing the process:

| Request | Actual response |
| --- | --- |
| `http://localhost:5173/api/v1/geographies?` (direct loopback, no system proxy) | **200**, `text/html`, 472 bytes, begins `<!doctype html>`; Vite SPA document rather than the registry |
| Same URL through the actual Edge fetch client | **404**, no JSON content type, non-JSON body; UI shows `Invalid API JSON response` |
| `http://localhost:5173/api/v1/health` (direct probe) | **200**, `text/html`, SPA document |
| `http://127.0.0.1:8000/api/v1/health` | **200**, `application/json`, valid health envelope |
| `http://127.0.0.1:4173/api/v1/health` | **200**, `application/json`, valid proxied envelope |

The HTML-versus-404 response depends on request content negotiation; both originate at the unproxied Vite server, not the FastAPI routes. Browser response evidence and the reproduced error screenshot were captured before restarting. The old process command was Vite in this repository; its verified PID was 5784. Only that stale Vite process was stopped. No secret values were printed.

## Fix

1. Restart the identified Vite process on the user's actual `localhost:5173` address so the API proxy is loaded.
2. Make `npm run dev` explicitly load `vite.config.js` and use strict-port behaviour. Keep `/api` targeting 127.0.0.1:8000; configure the same proxy for local preview. A busy port now fails rather than quietly moving the dashboard to an unexpected port.
3. Return a sanitized JSON 502 from the Vite proxy when the backend is unreachable. Do not return HTML or invented data.
4. Centralize and validate the API base for requests and exports: `/api/v1` by default, or an explicit HTTP(S) backend URL ending in `/api/v1`. Reject root/incorrect API paths and credential-bearing overrides without echoing their values.
5. Distinguish network/backend-unreachable, HTTP errors, non-JSON content, invalid JSON, unexpected schemas and timeouts. Preserve valid empty/unavailable response envelopes. Development diagnostics log only route, status, content type and error category, without bodies, headers, credentials or stack traces.
6. Retry full geographic bootstrap after a failed initial connection. Refresh now repopulates registries/indicators after backend restoration instead of merely loading overview while leaving the dropdowns empty. Empty or malformed registries get explicit errors. Hide irrelevant controls/empty chart until initialization succeeds.
7. Extend the browser harness to start missing FastAPI and Vite services and exercise both 4173 and the user's 5173 port. Reusing a stale 5173 server remains detectable by the real routing test.

## Real-browser verification

A real Edge browser loaded `http://localhost:5173/#overview`; no API interception was used for the outage/restart sequence:

- Stop the known test API; request `/api/v1/geographies?` returns **502 application/json** and the UI explicitly says the backend is unreachable.
- Start the actual FastAPI application on port 8000.
- Click **Refresh API data** in the same page, without reloading: registry and indicator requests return **200 application/json**, overview loads, and nine boundary options (eight source-derived boundary types plus the all-types option) appear.
- Reload the page: initialization works again.
- The full browser suite separately selects actual police-division and NHS-board areas on port 5173, observes real successful `/geographies/{id}/trends` requests, checks returned table rows and a rendered chart, and reloads successfully. It verifies all 13 division and 14 board options. Backend tests check the supported area's source observations.
- All eight sections are exercised by the retained real-backend suite. Synthetic transport substitutions remain confined to clearly labelled failure-regression tests, not application data.

Evidence retained under ignored `analysis/test_scratch.local/api_defect/`:

- `before.png`: original invalid-JSON dashboard reproduction.
- `outage.png`: actual backend stopped, explicit unreachable message.
- `restored.png`: actual backend restarted, data/bootstrap restored.
- `outage-recovery.json`: actual request URL/status/content-type/body-kind sequence, with 502 -> 200 recovery.
- `http-after.json`: post-fix real HTTP endpoint evidence through port 5173.

After the fix all the following proxied endpoints returned **200 application/json**, state `ready`: health; geographies (**33**); indicators (**21**); overview; mortality quarterly (**36**); monitoring configurations (**4**); monitoring results (**76**). Overview reported database state `ready`; every result had its associated configuration label. The existing publishable/anon key was used server-side. No privileged key was needed, stored or used.

## Modified files

- `vite.config.js`: explicit local port/strict behaviour, development/preview proxy and sanitized proxy outage JSON.
- `package.json`: explicit configuration/strict port in the existing dev command; no dependency change.
- `src/api/client.js`: one validated API base, response content-type/JSON/schema diagnostics, safe development logs.
- `src/platform/dashboard.js`: initialized-state tracking, full bootstrap retry, registry validation and initial visibility.
- `playwright.config.js`: actual backend plus both Vite addresses in the local test harness; corrected quoted Windows Python path.
- `tests/api-routing.test.js` (new): HTML, invalid JSON, HTTP/schema/network categories, invalid bases and proxy outage behaviour.
- `tests/platform.test.js`: realistic JSON headers on test response fixtures and schema diagnostic assertion.
- `e2e/local-api.spec.js` (new): real port-5173 JSON/data retrieval and empty-registry recovery.
- `backend/README.md`: exact restart/health diagnostic instructions.
- This report and an addendum to `docs/PHASE8_FINAL_ACCEPTANCE_REPORT.md`.

No analytical source/result module, backend database permission or dissertation chapter was changed.

## Verification results

```powershell
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests backend/tests -q -p no:cacheprovider
npm test
npm run test:e2e
npm run build
git diff --check
```

- JavaScript: **26 passed**, including three new routing/diagnostic tests.
- Python: **99 passed in 382.62 seconds**, one existing HTTPX deprecation warning.
- Full browser suite: **11 passed in 2.7 minutes**, including real user-port 5173 routing/observations and bootstrap recovery.
- Production build: **passed**, Vite 8.3.5; 14 modules, JavaScript 223.49 kB (77.40 kB gzip), CSS 9.23 kB (2.78 kB gzip).
- Preservation and final whitespace checks: **passed**: 85 protected earlier-phase hashes, all Phase 6 input/code/output hashes, configured-credential bundle scan; final whitespace check recorded below.
- Real manual outage/recovery and post-fix HTTP evidence: passed as described above, independently of mocked regressions.

One initial browser-harness launch failed before running assertions because Windows cmd interpreted an unquoted forward-slash Python path incorrectly. The command was corrected to a quoted Windows path. The next attempt was temporarily blocked by automatic approval-review usage limits, not rejected as unsafe; no bypass was attempted. After the user's continuation request, approval became available and the verification was resumed. Any current remaining test failure is recorded above rather than counted as a pass.

## Run/recover locally

From the repository root, start FastAPI in one terminal:

```powershell
.\analysis\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Stop any older Vite terminal with Ctrl+C, then in another terminal:

```powershell
npm run dev -- --host localhost --port 5173
```

Open **http://localhost:5173/#overview**. The browser-facing http://localhost:5173/api/v1/health and direct http://127.0.0.1:8000/api/v1/health must both return JSON. If the backend was temporarily down, start it and click Refresh API data. HTML at the browser-facing API URL means the Vite proxy is not loaded; stop the old Vite process and restart using the command above. Do not expose or replace database credentials to solve an HTML routing response.

## Remaining limitations

Both local services must be running; `npm run dev` starts Vite, not the backend. Saved analytics remain historical and subject to the scientific limitations in the Phase 8 report. Tests are local research verification, not PHS approval, production readiness or operational warning validation. No deployment/publication is performed. Stop for review after defect correction.
