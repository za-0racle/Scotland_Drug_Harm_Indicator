# Phase 7 local research API

Run from the repository root in two terminals:

```powershell
.\analysis\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\analysis\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

```powershell
npm install
npm run dev
```

Vite proxies `/api` to port 8000. API documentation: http://127.0.0.1:8000/docs . Configure server-only `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `backend/.env` or the process environment. Existing `.env.local` Vite-named publishable credentials are accepted server-side for compatibility; the active frontend does not import them. Never configure a service-role key. `VITE_API_BASE_URL` is the frontend API base URL, not a database URL. CORS is restricted to configured local frontend origins. This is a local research prototype, without deployment authentication/rate-limiting infrastructure.

All HTTP analytical routes are GET-only. Only three reviewed aggregate/model Supabase tables are read. Analytical filenames are allowlisted and validated against saved SHA-256 manifests; unavailable or corrupted artifacts return an explicit error. No HTTP route executes analytical scripts, accepts arbitrary file paths or publishes data.

## Controlled refresh

Refreshing the browser re-reads API data; it does not retrain a model or acquire newer observations. A researcher may explicitly generate a private scratch run:

```powershell
.\analysis\.venv\Scripts\python.exe -m backend.refresh phase6 analysis/test_scratch.local/phase7_refresh/review-001
```

Only phase4/phase5/phase5c/phase6 are supported. The destination must be new and beneath the shown ignored scratch root. Existing inputs/results are not overwritten. This command was not used to update research baselines during Phase 7. Review source compatibility, tests and manifests before any separately approved catalogue promotion; scratch results are never automatically served. Source acquisition, revised observations, forecast reselection, FOI import and publication require their own review.

## Verification

```powershell
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests backend/tests -q -p no:cacheprovider
npm test
npm run build
npm run test:e2e
```

Start the backend before Playwright. Tests use synthetic fixtures only within tests; the application has no mock-data fallback. CSV/JSON exports are bounded pages, retain research provenance and never write Supabase.

## If the dashboard reports non-JSON API data

Use the Vite process started from this repository after `vite.config.js` exists. Stop an older Vite terminal with Ctrl+C, then run `npm run dev -- --host localhost --port 5173`. The dev command explicitly loads the proxy config and fails if the port is already occupied. Do not start another dashboard on an unexpected fallback port. Start FastAPI separately on 127.0.0.1:8000 using the command above. Both http://localhost:5173/api/v1/health and http://127.0.0.1:8000/api/v1/health must return JSON. HTML at the frontend API URL indicates the proxy is not loaded; credentials cannot repair that routing error. After restoring the backend, use Refresh API data to retry geographic bootstrap, or reload the page. No secret/service-role credential is needed.

Playwright now starts missing local backend and Vite services for ports 8000, 4173 and 5173. It reuses existing servers in local runs, so an already-running stale Vite server is deliberately exposed by the routing test rather than silently bypassed. A clean test run requires the existing Python virtual environment and backend dependencies.
