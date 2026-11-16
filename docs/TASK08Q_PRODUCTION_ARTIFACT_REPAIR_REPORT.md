# Task 08Q — Production Artifact Repair Report

## Status

**Root cause confirmed and correction pushed; production verification is pending.** This report will not claim production recovery until Render reports the expected revision and the artifact-backed endpoints return verified data.

## Confirmed root cause

Frozen artifact manifests hash the original output bytes, which use CRLF line endings. On the Windows development machine, `core.autocrlf=true` made the checked-out output files CRLF, so all 55 outputs audited across the Phase 4, 5, 5c, 6, and forecast directories matched their manifests. Git stores the normalized blobs with LF line endings. Render checks out those LF blobs on Linux, and `ArtifactRepository` hashes the raw runtime bytes; all 55 committed blobs therefore failed the existing manifest hashes.

The evidence is byte-level and reproducible:

- All 55 local output files matched their committed manifest hashes.
- All 55 Git blobs were exactly the LF-normalized form of their corresponding local files.
- Converting each committed blob to CRLF reproduced the manifest hash for all 55 outputs.
- A clean Git index checkout with `core.autocrlf=false` and the new attributes produced 55/55 manifest-matching outputs.
- The affected artifact paths and manifests are tracked. No `.dockerignore`, `render.yaml`, or other repository packaging exclusion was found.
- The owner-confirmed Render Root Directory is blank (repository root), and `backend/config.py` correctly resolves `ROOT` to the repository root. Root Directory was not the cause.

No artifact data or manifest was rewritten. SHA-256 verification remains enabled.

## Affected dependency paths

The failure was not assumed to be one shared resource; the route paths were traced:

- `/api/v1/analytical/v1/mortality-trends` loads the Phase 4 mortality artifact through `ArtifactRepository`.
- `/api/v1/analytical/v1/forensic-toxicology` loads the Phase 4 forensic artifact through the same repository implementation.
- `/api/v1/overview` reads the phase 5c summary and then the registry/base artifacts.
- `/api/v1/geographies` builds that registry from mortality, forensic, ASSIST, treatment, naloxone, and annual artifacts.
- `/api/v1/geography/comparisons` loads its Phase 6 comparison artifact.
- `/api/v1/database/v1/naloxone-activity` reads paginated Supabase rows and source provenance, then classifies each row through the artifact-backed geography registry. That registry load fails on the same line-ending/checksum mismatch before the returned snapshot can be classified.
- The data-sources and geographic-areas snapshot routes do not need the artifact repository, consistent with their production HTTP 200 responses. The naloxone failure is therefore not evidence of a general Supabase initialization failure.

The generic `ArtifactError` handler converted checksum failures into the observed HTTP 503 response. The failure was not caused by an incorrect root path, a missing committed artifact, a case-sensitive filename mismatch, or an extra query parameter.

## Correction and diagnostics

Commit `c20c99e` (`c20c99e` full SHA to be confirmed after push verification) adds:

- `.gitattributes` rules marking `analysis/**/outputs/**` as `text eol=crlf`, with an explicit rule for `analysis/outputs/**`. Git blobs and manifests remain unchanged; Git checkouts now restore the byte representation required by the existing hashes.
- Structured server-side logs for artifact stat, manifest stat, manifest/payload read, checksum, record-shape, required-field, and artifact-backed request failures. Logs use resource identifiers and repository-relative paths, omit dataset contents and digest values, and retain the generic public 503 body.
- An `X-SDHI-Revision` response header when Render provides a valid `RENDER_GIT_COMMIT` SHA. Invalid values are ignored.
- Regression coverage that loads every catalog artifact and verifies the mismatch diagnostic contains no absolute filesystem path.

The owner-configured Render service is set to auto-deploy on commits to `main`. The repair was pushed to `main`; the actual running Render revision and live recovery are recorded below after deployment verification.

## Local verification

| Check | Result |
|---|---|
| Artifact manifest audit | 55/55 working-tree outputs matched |
| Clean checkout packaging probe | 55/55 checked-out outputs matched |
| Backend artifact, snapshot, mortality, and forensic tests | 64 passed; one existing Starlette/HTTPX deprecation warning |
| Frontend unit tests | 108 passed |
| Vite production build | Passed |
| Local eight-screen browser acceptance | Passed |
| Local live-snapshot browser acceptance | Passed |
| Frozen analysis tree | No changes |

These are local or repository-checkout results, not production results.

## Production verification

### Before the repair

| Endpoint | Result |
|---|---|
| `/api/v1/health` | HTTP 200, `ready` |
| `/api/v1/overview` | HTTP 503, `unavailable_evidence` |
| `/api/v1/geographies` | HTTP 503, `unavailable_evidence` |
| `/api/v1/analytical/v1/mortality-trends?limit=1` | HTTP 503 |
| `/api/v1/analytical/v1/forensic-toxicology?limit=1` | HTTP 503 |
| `/api/v1/geography/comparisons` | HTTP 503 |
| `/api/v1/database/v1/data-sources?limit=1` | HTTP 200 |
| `/api/v1/database/v1/geographic-areas?limit=1` | HTTP 200 |
| `/api/v1/database/v1/naloxone-activity?limit=1` | HTTP 503 |

### After the repair

Pending Render auto-deploy and live HTTPS verification. The deployed revision must match the repair commit via `X-SDHI-Revision`; endpoint results, naloxone reconciliation, and browser acceptance will be added only after they are actually checked.

## Naloxone invariants

The required production verification is to page through all 7,024 records and confirm 7,024 unique geography-week keys, 439 weeks, 14 official NHS boards, separate Scotland and Unknown records, no Scotland/Unknown board classification, and Scotland reconciliation to the 14 boards plus Unknown for all 439 weeks.

Production verification is pending until the corrected snapshot endpoint is healthy. A prior local API verification found 7,024 records over 15 pages, 439 weeks, 14 boards, and reconciliation in 439/439 weeks; that result is not production evidence.

## Frontend acceptance

Production acceptance must check all eight primary screens for actual analytical data rendering, not only navigation or headings. It must also check filters, comparisons, exports, loading/error states, and that NHS-board selectors contain exactly the 14 official boards without Scotland or Unknown.

Production acceptance is pending until the Render endpoints return verified data. Local eight-screen acceptance passed; it does not establish production rendering.

## Remaining blockers and owner action

1. Wait for the Render deployment triggered by the pushed `main` commit to reach **Live**.
2. Confirm `X-SDHI-Revision` equals the repair commit SHA.
3. If it does not, use Render’s deployment page to deploy the latest `main` commit and inspect the new structured artifact log for the resource, relative path, and failing validation stage. Do not change Root Directory, manifests, artifact contents, or checksum verification.
4. Repeat the production endpoint, full naloxone pagination/reconciliation, and eight-screen data-rendering checks.

Until those checks pass, the cause and source correction are verified, but production acceptance remains unconfirmed.
