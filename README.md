# Scotland Drug Harm Indicator

Run the application from the repository root with `npm install` and `npm run dev`. Build with `npm run build`.

For local development, copy `.env.example` to `.env.local`. Set the Supabase project URL and publishable key for the backend; keep `VITE_API_BASE_URL=/api/v1` so Vite proxies requests to the local FastAPI server. Never put a Supabase key in a `VITE_` variable or use a service-role key.

The active frontend mounts `src/platform/dashboard.js` from `src/main.js` and reads through FastAPI using `src/api/client.js`. Supabase credentials remain on the backend. Earlier direct-database frontend modules are retained as historical code and are not the mounted application. Eight screens provide source-specific analysis, compatible comparisons, original monitoring records and configuration-specific EWMA/CUSUM charts, retrospective forecast evaluation and research documentation. Missing observations remain gaps; empty access does not establish absence of harm.

The Research, sources and downloads screen also provides a separate `database-v1` read-only snapshot for the reviewed source catalog, geographic registry and naloxone activity tables. It uses exact-count paging and exports only the visible page. Live database values remain separate from frozen Phase 4/5 artifacts; the documented moving-average and geography-validity provenance questions are not silently resolved or recalculated.

Run `npm test` for transformation and database reader tests, `npm run build` for production validation, and `npm run test:e2e` for live browser verification. Browser tests require the configured public read access and the current research dataset; they never mutate Supabase. They use installed Edge on Windows; on other systems install Chromium with `npx playwright install chromium`. Current browser regression captures are saved under `test-results/` (ignored by Git); approved historical captures and phase reports are retained under `docs/`.

See `docs/dashboard-phase-1.md` for implementation details, limitations and Section 4.6 screenshot locations. `docs/supabase-integration-review.md` is the earlier public-data review. Existing policies are preserved; do not apply the historical migration again or run `db push` automatically.

The repository root is the active frontend. `g3-indicator` contains research inputs used by analysis scripts; its former placeholder frontend is archived in `g3-indicator/prototype-archive/` and is no longer an npm app. Keep `g3-indicator/public/data/quarterly_input_table.json` in place unless its analysis references are updated.

## Vercel frontend deployment

The root `vercel.json` configures Vercel to build this Vite frontend with `npm run build` and serve `dist`. Set the Vercel project Root Directory to the repository root.

**Release workflow reviewed 18 November 2026.** The existing public frontend is `https://sdhi.cc/` (redirecting to `www`) and its API is `https://scotland-drug-harm-api.onrender.com/api/v1`. GitHub commit statuses identify the existing Vercel integration; the owner has approved publication through the existing `main` workflow. Preserve the configured production API origin and CORS settings. A local build alone does not establish deployment or production acceptance. See [the S08 release report](docs/TASK08S_S08_RELEASE_REPORT.md) for the verified release outcome and [the Phase 5 diagnostic report](docs/TASK08S_PHASE5_DIAGNOSTIC_VERIFICATION_REPORT.md) for earlier checks.

In the Vercel project, open **Settings → Environment Variables** and add:

| Name | Value | Environments |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `https://<your-backend-host>/api/v1` | Production; Preview only when that preview origin is allowed by backend CORS |

Use the public URL of the deployed FastAPI backend, not a localhost URL, Supabase URL, or secret. The frontend currently defaults to `/api/v1` for the local Vite proxy; that default is not a production API deployment. Redeploy after adding or changing the variable because Vite embeds it at build time.

The API must be hosted separately from this static frontend. On the backend host, configure `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` as server-side environment variables, and set `API_CORS_ORIGINS` to the exact Vercel production origin (for example, `https://your-project.vercel.app`) and any approved custom domain. Do not put these Supabase variables in Vercel's frontend environment. Never expose a service-role key.
