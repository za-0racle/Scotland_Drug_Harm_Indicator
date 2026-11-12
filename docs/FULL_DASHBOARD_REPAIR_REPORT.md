# Full dashboard audit and repair report

Assessment date: 10 November 2026. Scope: read-only audit of current dashboard behavior and surgical repair of confirmed anomaly-result ordering/context defects. Validated analytical outputs, Supabase permissions, database records and the existing Vite/JavaScript/Chart.js/FastAPI architecture were not changed.

## Executive summary

The project already contains a working eight-section research platform, API-backed filters, checksum-verified analytical artifacts, bounded exports and substantial automated coverage. The audit did not find evidence that Supabase RLS causes the reported anomaly ordering issue. It was caused by anomaly rows being filtered from a saved artifact and returned in artifact storage order, while the interface described the first and last displayed periods as a chronological range.

The displayed count of three records was verified to be the three saved suspected-death flags, not three total observations and not a reason to create more flags. The anomaly page now offers a separate **All observations** view, with stored classifications preserved, and flag results are ordered chronologically before pagination. No model, threshold, statistical result or input artifact was changed.

## Audit findings and root causes

| Severity | Component | Finding / root cause | Correction |
|---|---|---|---|
| High | Anomaly API and displayed time range | The three national/divisional suspected-death flags were emitted in saved CSV order (2023 Q1, 2022 Q1, 2022 Q2), so downstream first-to-last display could look reversed. Filtering itself retained the correct three flags. | Deterministically sort anomaly and enhanced-model rows by period, geography, indicator, method and window before pagination. |
| Medium | Anomaly context | The default flags view correctly showed only stored flags, but did not provide a nearby view of other saved classifications for context. | Add a separate all-observations tab using the existing `signals_only=false` API behavior. It shows stored flag, non-flag, insufficient and unavailable classifications without recalculation. |
| Low | Anomaly table interpretation | Classification status was not among the first seven columns selected for the table; enum-like status text could be difficult to interpret. | Prioritize period, method, classification and observed value in visible columns; provide plain-language labels and show eight columns. |
| Not reproduced | More filters | The control is implemented as an expandable native disclosure; it exposes supported year, model, comparison and category controls when applicable. It hides when none apply. | No nonfunctional control was added. Browser tests exercise model/year controls and reset behavior. |
| Not established as a defect | Other dashboard sections | The project already contains acceptance tests for all eight sections, API flows, filters, exports, geography, forecasts, errors and mobile layout. No separate current failure was reproduced for the remaining modules. | Preserve existing behavior; run the suite rather than introduce unnecessary rewrites. |

## Repairs by module

### Anomaly Detection

- Corrected chronological ordering of saved original and enhanced flags before filtering results are paginated.
- Kept the default statistical-flags view as flags only; the verified original count remains **47 overall**, including **3 suspected-death flags**.
- Added **All observations**, which requests the same saved anomaly artifact with `signals_only=false`. This is context, not a recalculation; each record retains its original classification and value.
- Added a regression test that confirms chronological order for the three suspected-death flags, counts the broader context separately, and checks that original artifact records and values are preserved.
- Kept sensitivity analysis, distribution adequacy, prior-window diagnostics and sparse/unknown-count views unchanged.

### Other modules and global behavior

The audit exercised the existing overview, geographic explorer, trends, surveillance, forecasting, reports/exports and methodology interfaces. Their previously implemented safeguards remain in place: distinct suspected versus registered death labels; actual geography boundaries; no fabricated Greenock estimate; null gaps; historical forecast disclaimers; bounded, provenance-bearing exports; explicit empty/error states; and no broad anonymous table access.

The all-eight-sections Playwright acceptance test now also fails on browser page errors or console errors while navigating sections. Expected API/network failures in dedicated failure-state tests are reported as structured development warnings and are not browser console errors.

## Backend, data integrity and security

- Supabase access remains restricted to the three reviewed tables in the existing repository. The active database role remains the server-side anon/publishable role.
- No migration, RLS policy, grant, database record, service-role key, source dataset or analytical artifact was changed.
- The new backend ordering is a presentation/query ordering only. Sorting is stable and occurs before applying offset/limit, so pagination remains chronological.
- Comparison behavior, API schemas, validation, artifact hashes and export behavior were not broadened or replaced.
- Existing security controls (GET-only endpoints, resource allowlists, bounded filters and pages, server-side credentials, provenance metadata) are retained.

## Files changed for this repair

- `backend/services/platform.py` — chronological ordering for saved anomaly results.
- `backend/tests/test_acceptance.py` — ordering, context-state and artifact-value preservation regressions.
- `src/platform/dashboard.js` — all-observations tab and explicit contextual description; wider result table.
- `src/platform/data.js` — put analysis status and observed value among higher-priority table columns.
- `src/platform/presentation.js` — label suspected deaths and anomaly classifications.
- `e2e/usability.spec.js` — browser checks for chronological flags and contextual observations.
- `e2e/acceptance.spec.js` — fail if the eight-section navigation produces page or console errors.

## Verification performed

| Check | Result |
|---|---|
| Full Python analysis and backend suite before the focused repair | **99 passed**, one Starlette/httpx deprecation warning (439.14 seconds). |
| Targeted Python regressions after the repair | **2 passed**, including exact flagged-quarter ordering and record/value preservation across the unchanged artifacts (88.41 seconds). |
| JavaScript unit suite after the repair | **29 passed**. |
| Full Playwright suite after the repair | **16 passed** (1.4 minutes), including all eight sections, the new anomaly context/order checks, navigation, responsive behavior, filters and exports. |
| Browser console/page errors during eight-section navigation | **None**; the acceptance test now asserts this explicitly. Dedicated outage tests still verify visible error states. |
| Production frontend build after final edits | **Passed**, Vite 8.3.5; 16 modules transformed. |
| `git diff --check` | Passed. |

The test fixtures and intercepted API responses used by existing browser tests are test-only. No application fallback data was introduced. A stale test-owned backend initially served pre-repair ordering; after identifying and restarting that specific local process, the targeted browser test and the complete suite passed against the repaired code.

## Remaining limitations

- No live database policy introspection was performed; this repair did not require or authorize a permission change.
- Existing external-alert completeness, prospective validation, official endorsement, current-condition and operational-warning limitations remain unchanged.
- Accessibility checks are project-level automated/manual samples, not formal WCAG or assistive-technology certification.
- A Starlette/httpx deprecation warning remains in the existing Python test environment.

## Run and demonstrate locally

From the repository root, start the backend and Vite frontend in separate PowerShell terminals:

```powershell
.\analysis\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). For browser acceptance tests, run:

```powershell
npm run test:e2e
```

The Playwright configuration starts/reuses its local FastAPI and Vite services. On the Anomaly Detection page, use **Statistical flags** to inspect saved flags and **All observations** to inspect the broader saved classification context; the two counts answer different questions. Do not describe the flags as confirmed events or operational alerts.
