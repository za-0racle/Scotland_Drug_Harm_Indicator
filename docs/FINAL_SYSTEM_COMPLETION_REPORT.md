# Final System Completion Report

**Review date:** 16 November 2026  
**Project:** Scotland Drug Harm Intelligence Platform (SDHI)  
**Completion status:** Ready for a supervised local demonstration and dissertation evidence review. Not deployed or approved for operational use.

## Executive outcome

Task 08N and the current completion sprint deliver a read-only, versioned view of confirmed live database updates alongside the existing frozen research outputs. The implementation retains the eight-screen platform, separate source contracts, and the 14-board comparison boundary. No database writes, schema changes, research recalculations, or frozen-artifact replacements were made.

The configured local Vite-to-FastAPI demonstration is the supported end-to-end deployment. Vercel is configured for a static frontend build only. A deployed API origin, Vercel project/credentials, and verified free FastAPI host are not available in this environment, so public deployment is explicitly blocked rather than represented as complete.

## Task 08N completion

- Added the `database-v1` read-only snapshot surface for the allow-listed `data_sources`, `geographic_areas`, and `naloxone_activity` tables. Pages require exact totals and consistent offsets; responses retain database/source version and provenance.
- Added the Research, Data & Exports screen's live snapshot view, with bounded 100-row pages, explicit empty/error states, page-only CSV export, and visible distinction from frozen Phase 4/5 artifacts.
- Incorporated currently confirmed source metadata and geographic-validity values as displayed database fields. The live naloxone moving average is shown as source-reported data, not recomputed or substituted into the frozen research series.
- Classified live naloxone rows as NHS board, national Scotland, or Unknown using the reviewed source registry. Scotland and Unknown remain separate records and are excluded from board-only selectors, peer rankings, and board-level summaries.
- Kept raw RADAR narratives and unreviewed tables outside the API allowlist. No Supabase policy, credential, or schema change was attempted.

The current live read-only API pagination check retrieved **7,024/7,024** naloxone rows over 15 pages of 500, with **7,024 unique geography-week keys**, 439 weeks, and 14 boards. Scotland equalled the sum of the 14 boards plus Unknown for **439/439** weeks. This confirms the current API representation and arithmetic; it does not resolve source lineage for the 14 additional first-week moving-average values described in [Task 08M](./TASK08M_FULL_SUPABASE_REAUDIT.md).

## Application and architecture

The active system is:

**Vite + vanilla JavaScript + Chart.js → central HTTP API client → FastAPI → reviewed Supabase reads and/or SHA-256-verified frozen artifacts.**

The browser does not query Supabase directly. API routes are GET-only, use explicit resource/table allowlists, bounded query parameters and sanitized errors. The API distinguishes ready, empty, unavailable and error results. Missing values remain missing; zeros remain observations. Refreshing data does not retrain models or promote new research.

The eight primary destinations are Intelligence Overview, Comparison Studio, Mortality Analytics, Substance Intelligence, Geographic Explorer, Anomaly Detection & Surveillance Signals, Forecasting Lab, and Research, Data & Exports. A fresh Playwright run captured each screen; see [the screenshot checklist](./FINAL_SCREENSHOT_CHECKLIST.md).

## Scientific and geographic safeguards

- Police suspected deaths remain distinct from NRS registered deaths; forensic and ASSIST measures, naloxone activity, population estimates, and RADAR intelligence are not pooled.
- The frozen Phase 4 naloxone series remains unchanged. Live database moving-average differences are disclosed as a provenance discrepancy, not treated as an approved research update.
- Scotland is a national aggregate and Unknown remains a separate source label. Neither is an NHS board or a board peer.
- Health-board selectors and board-only summaries use the health-board boundary; cross-boundary comparisons and rankings are rejected.
- Greenock-specific outcomes, unverified maps/crosswalks, population-risk rankings, current forecasts, and operational alerts are not inferred.
- Statistical anomalies are retrospective research signals, not confirmed incidents or public-health alerts. External/FOI validation remains pending.

## Verification summary

Current results and command details are recorded in [Final Acceptance Test Results](./FINAL_ACCEPTANCE_TEST_RESULTS.md). The successful checks include 108 frontend unit tests, 167 analysis/backend tests, a production frontend build, live API pagination and reconciliation, and a focused browser run that navigated and captured all eight screens. The full browser suite was rerun after correcting its acceptance-test navigation; its final result is recorded in the acceptance report.

The production bundle check found none of the two configured Supabase URL/key values and no secret/service-role marker. This is a local bundle check, not a penetration test or deployment security certification.

## Deployment status and blocker

The repository's [Vercel configuration](../vercel.json) builds the Vite frontend into `dist`; it does not host or route to FastAPI. No Vercel CLI or configured deployment project is available, and no free, reliable FastAPI host has been verified. A static build must not be described as a working public deployment. The local demonstration remains usable with the commands in [README](../README.md) and [backend README](../backend/README.md); no paid service was introduced.

Before any public or institutional deployment, an owner must select and verify an API host, confirm cost/limits, configure its server-side publishable credential and exact CORS origins, and complete authentication, rate limiting, monitoring, recovery, and security review. Those are deployment gates, not blockers to the local demonstration.

## Known limitations and outstanding provenance

1. The source lineage of the 14 live naloxone moving averages populated on 2018-01-01 remains unexplained. Frozen source values are preserved.
2. The provenance of 14 populated `geographic_areas.valid_to` fields needs confirmation before temporal boundary logic relies on them.
3. The PostgREST metadata root returned HTTP 401 during Task 08M; deployed SQL types, constraints, policies and grants are not verified. `radar_alerts` had zero visible rows and its schema remains unknown.
4. The project is a historical research prototype, not an operational alert service. Prospective and external event validation, formal accessibility certification, and institutional endorsement are absent.
5. The final MSc rubric/supervisor acceptance criteria should be checked by the project group; the Task 08J audit noted that the original Task 08A brief was not present in the repository.

## Final disposition

The application and evidence package are ready for a supervised local demonstration and dissertation review, subject to accurately stating the limitations above. Public hosting and operational use remain out of scope until their explicit approval and readiness gates are met.
