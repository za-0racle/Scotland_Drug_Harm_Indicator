# Task 08P — Production Integration Report

## Status

**Not production-complete.** The Vercel frontend is configured for the Render API and CORS permits the production origin, but several artifact-backed Render endpoints still return HTTP 503. The exact Render runtime cause and deployed commit cannot be established without access to the Render deployment settings, logs, or shell.

No frozen research artifact, scientific calculation, Supabase record, or policy was changed. Hash verification was not bypassed, and missing evidence was not regenerated.

## Root-cause investigation

The failure is reproducible on multiple independent artifact-backed routes:

| Production endpoint | Result |
|---|---|
| `/api/v1/health` | HTTP 200, `ready` |
| `/api/v1/overview` | HTTP 503, `unavailable_evidence` |
| `/api/v1/geographies` | HTTP 503, `unavailable_evidence` |
| `/api/v1/analytical/v1/mortality-trends` | HTTP 503, `unavailable_evidence` |
| `/api/v1/analytical/v1/forensic-toxicology` | HTTP 503, `unavailable_evidence` |
| `/api/v1/geography/comparisons` | HTTP 503, `unavailable_evidence` |
| `/api/v1/database/v1/data-sources` | HTTP 200 |
| `/api/v1/database/v1/geographic-areas` | HTTP 200; 18 rows returned, all classified as NHS boards |
| `/api/v1/database/v1/naloxone-activity` | HTTP 503, `unavailable_evidence` |

The failing responses use the same generic message: “Verified analytical resource unavailable; check server artifact integrity.” The production OpenAPI document contains the Task 08N `database-v1` routes, so those endpoint definitions are present in the running service.

Local repository checks found that:

- The expected artifact directories and manifests are present in the GitHub repository tree.
- Every expected output hash checked locally matches its manifest.
- `backend/config.py` derives `ROOT` from the backend package location, resolving to the repository root when the repository root is the deployment context. Artifact paths are resolved beneath that root by `backend/repositories/artifacts.py`.
- Artifact-backed failures span multiple analytical resources, rather than one named output. The working local paths and hashes do not reproduce the production failure.

This confirms an artifact-availability/integrity failure in the deployed runtime, but the externally visible error handler conceals whether the Render instance has an incorrect deployment root or missing files, or whether a runtime digest/validation check fails. No Render shell, deployment record, or logs were available to distinguish those cases. A repository-root/deployment-context mismatch is the leading explanation, not a proven exact cause. No evidence currently points to RAM exhaustion; resource limits cannot be fully ruled out without Render runtime metrics.

### Required Render owner action

1. In the Render service, confirm the Root Directory is the repository root (blank/default for this repository), not `backend/`. The deployed filesystem must contain both `backend/` and `analysis/`.
2. Inspect the runtime paths named by the manifests under `analysis/**/outputs/` and confirm their SHA-256 values match the committed manifests. Do not edit manifests or regenerate outputs to make a mismatch pass.
3. Check Render deploy logs and runtime memory metrics for the underlying path, digest, or validation error.
4. Redeploy after correcting any deployment-context or artifact-packaging issue, then repeat the endpoint checks in this report.

## Deployment synchronization

The last verified GitHub `main` and local `HEAD` at the start of this investigation were both:

`1a02dcad2881dba7dbb1a9b67fd5cb71d0653338`

The production OpenAPI document does not expose a build SHA, and Render deployment metadata was unavailable. Therefore the exact commit running on Render is **unverified**. The production API does contain the database snapshot endpoints and the existing 14-board classification implementation, but production naloxone results cannot be verified while its snapshot endpoint returns 503.

The local changes made for this task are:

- `src/platform/dashboard.js` — avoid calling the data loader from browser-history navigation before bootstrap has initialized the filters.
- `e2e/acceptance.spec.js` — add a regression test for browser back-navigation during delayed backend bootstrap.
- `docs/TASK08P_PRODUCTION_INTEGRATION_REPORT.md` — this report.

No backend implementation, manifests, research outputs, or Supabase data were changed.

## Frontend configuration and CORS

- The central API client in `src/api/client.js` reads `VITE_API_BASE_URL`.
- The production frontend JavaScript bundle loaded from `https://www.sdhi.cc` contains `https://scotland-drug-harm-api.onrender.com/api/v1`.
- The checked production bundle does not contain `localhost:8000`.
- An OPTIONS preflight from `https://www.sdhi.cc` to the Render health endpoint returned HTTP 200 and `Access-Control-Allow-Origin: https://www.sdhi.cc`.
- `vercel.json` configures the Vite static frontend; it does not host FastAPI.

## Verification results

| Check | Result |
|---|---|
| Frontend unit tests | Passed: 108 |
| Backend and analysis tests | Passed: 167; one existing Starlette/HTTPX deprecation warning |
| Vite production build | Passed |
| Full E2E suite before the focused frontend fix | Passed: 41 |
| Focused E2E after the fix | Passed: 2, including database snapshot browser coverage and the bootstrap-history regression |
| Eight primary screens against the local integrated backend after the fix | Passed: 1 acceptance test |
| Local naloxone pagination/reconciliation check | Passed: 7,024 rows over 15 pages; 7,024 unique keys; 439 weeks; 14 boards; Scotland reconciled to boards plus Unknown in 439/439 weeks |
| Local artifact manifest SHA-256 audit | Passed |
| Production API and CORS probes | Results recorded above; artifact-backed API coverage remains blocked |
| Production browser route sweep | All eight primary headings were found; production backend failures remain, and the pre-fix browser-history race was observed. The fix is local and is not yet confirmed on the deployed frontend. |

The full E2E suite result predates the focused frontend change; the focused regression and eight-screen acceptance tests were rerun afterward. Production naloxone pagination and Scotland/Unknown reconciliation remain unverified because the production naloxone endpoint returns HTTP 503. The local 7,024-row result is not a production result.

## Remaining blockers and completion criteria

1. Render owner access is required to inspect Root Directory, runtime artifact files, deployment logs, memory metrics, and the deployed commit SHA.
2. After Render is corrected, verify health, overview, geographies, mortality, forensic toxicology, and all database snapshot endpoints return their expected data.
3. Verify the production naloxone snapshot can be paged through all 7,024 records and that board-only comparisons exclude Scotland and Unknown without dropping those records from the underlying snapshot.
4. Publish the local frontend-history fix and verify the resulting Vercel deployment on all eight routes.
5. Re-run production browser checks after the API is healthy. Do not treat local test success as public deployment success.

Until these checks pass, the system is verified locally but production integration remains blocked. No claim is made that the Render artifact issue or production acceptance has been resolved.
