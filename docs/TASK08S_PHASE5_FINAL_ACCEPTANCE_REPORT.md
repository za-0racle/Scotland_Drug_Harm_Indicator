# SDHI Phase 5 — Final local acceptance and release readiness

Date: 17 November 2026. Baseline: `13c2844`. Local implementation only; no push, merge, deployment, DNS or hosting setting was changed.

## Executive summary and release candidate

The cleanup replaces on-screen JSON with structured research inspection, simplifies Overview source previews, and restricts the menu button to the existing mobile navigation breakpoint. Existing charts, filters, exact data, record inspection and export formats remain intact. Local acceptance is complete; the tested release candidate SHA is recorded below. Production acceptance is a separate, unpassed gate.

## Technical-content cleanup

| Location inspected | Finding and correction |
| --- | --- |
| Overview source and forecast disclosures | Intentional full provenance dumps were inappropriate in ordinary previews. Removed those payloads and internal source paths; kept publication/cutoff information and links to Research. Added the adopted study aim before the mortality lead. |
| Comparison source rows and provenance | Intentional raw JSON inspection replaced with labelled, nested records. Both original subjects and all provenance remain available. |
| Toxicology/geographic profiles and source details | Intentional JSON record dumps replaced with structured inspection. Removed the geographic registry identifier from the ordinary profile heading; it remains in the secondary complete record. |
| Research findings/source records and shared inspector | Complete records remain inspectable with readable field labels, explicit unavailable values and exact precision. Nested collections load when expanded. No developer console was added. |
| Generic object-to-text fallback | `JSON.stringify` was a potential cause of code-like ordinary content. Removed this UI fallback rather than hiding its output with CSS. Serialisation used for exports and integrity checks is unchanged. |
| Loading/error views | Reader-facing fallback messages replace generic HTTP/debug wording and the checksum-handler message. Status codes remain available to application logic. No stack trace is introduced. |

There was no evidence of executing source code being inserted as HTML. The earlier dumps were intentional inspection features whose presentation was unsuitable. The replacement uses DOM text nodes throughout; a focused hostile-string test verifies that code-like text cannot create an element or execute. Ordinary browser JavaScript bundles are legitimate public assets, not an exposure defect.

## Navigation and visual consistency

The existing JavaScript and CSS breakpoint is 900 px. Above it, the sidebar remains accessible and the menu button is hidden from display and keyboard access. At or below it, the button operates the drawer with Escape, focus trapping and restoration. Crossing 900/901 px closes the drawer, clears inert states and restores focus to an accessible control. Theme switching and route highlighting remain.

No completed analytical layout was rebuilt. Small changes improve profile unit labels, remove an ordinary registry identifier, and correct the malformed year separators in the historical Phase 4 report. Scientific ranges and definitions are unchanged.

## Files changed

- `src/platform/record-inspection.js` and its consumers: `dashboard.js`, `overview.js`, `comparison.js`, `comparison-studio.js`, `geography.js`, `substance.js`, `research.js`.
- `src/platform/shell.js`, `shared.css`, and `src/api/client.js`: navigation, structured-record wrapping and safe reader-facing errors.
- `e2e/phase5.spec.js`, updated shell/branding regressions, and Phase 4 capture destinations. Phase 1–4 screenshots are preserved.
- `scripts/verify-phase5-public.py`, `docs/evidence/task08s-phase5/`, `docs/images/task08s-phase5/`, this report and two Phase 4 report character corrections.

Protected research inputs, analysis/model code, frozen outputs, backend contracts, database schemas, dependency content, branding and metadata remain outside the implementation change. The earlier Phase 3 history is preserved.

## Local screen acceptance

All eight screens passed local browser acceptance across the full run and targeted retries. Existing regressions cover source switching, filters, chart legends, exact tables, search, pagination, scope-correct downloads, empty/unavailable/failure states and record inspection. New checks cover ordinary content and desktop/mobile captures on every screen.

| Screen | Desktop | Mobile |
| --- | --- | --- |
| Study overview | [Capture](images/task08s-phase5/overview-desktop.png) | [Capture](images/task08s-phase5/overview-mobile.png) |
| Comparison Studio | [Capture](images/task08s-phase5/comparison-desktop.png) | [Capture](images/task08s-phase5/comparison-mobile.png) |
| Mortality trends | [Capture](images/task08s-phase5/trends-desktop.png) | [Capture](images/task08s-phase5/trends-mobile.png) |
| Toxicology patterns | [Capture](images/task08s-phase5/substance-desktop.png) | [Capture](images/task08s-phase5/substance-mobile.png) |
| Geographic patterns | [Capture](images/task08s-phase5/geography-desktop.png) | [Capture](images/task08s-phase5/geography-mobile.png) |
| Statistical monitoring | [Capture](images/task08s-phase5/anomalies-desktop.png) | [Capture](images/task08s-phase5/anomalies-mobile.png) |
| Forecast evaluation | [Capture](images/task08s-phase5/forecasting-desktop.png) | [Capture](images/task08s-phase5/forecasting-mobile.png) |
| Research, sources and downloads | [Capture](images/task08s-phase5/reports-desktop.png) | [Capture](images/task08s-phase5/reports-mobile.png) |

Additional evidence: [mobile navigation](images/task08s-phase5/navigation-mobile-open.png), [monitoring record inspection](images/task08s-phase5/monitoring-inspection-mobile.png), [research record inspection](images/task08s-phase5/research-inspection-mobile.png). Screenshots use actual configured observations; test-only intercepted failures and hostile strings are not research data.

## Scientific integrity

Acceptance preserves separate provisional suspected deaths and registered drug misuse deaths; non-additive forensic categories and unavailable denominators; treatment-opioid exclusions; ASSIST's irregular windows; council/locality/board boundaries; exactly 14 board peers with Scotland and Unknown separate; published five-year rates and confidence intervals; and missing versus zero values. No Greenock outcome, new rate or individual-chemical emergence is inferred.

Original rolling Negative Binomial/EWMA, separate opioid-share CUSUM and later historical comparisons remain distinct. The fixed 2017–2020 versus rolling-baseline discrepancy remains documented. Flags are not confirmed incidents; RADAR validation, detection sensitivity, specificity and lead time remain unvalidated. Forecasting retains four candidates and 12 shared retrospective targets, baseline MAE 21.58, the same-target selection limitation, the saved 248 estimate for elapsed 2026 Q1 and its original intervals. No current forecast, operational warning or PHS endorsement is claimed. S08 charts were not implemented.

## Existing public backend — read-only observations

The read-only probe found HTTP 200 with expected data on all 19 routes below. Each returned backend revision `07993a5fd2ceeccc2b326e926584ba5742d7cefe`. No retry was needed. Typed analytical endpoints use their observation collection shape rather than the legacy envelope's `state` field.

| Route under `https://scotland-drug-harm-api.onrender.com/api/v1/` | HTTP | Content type | Evidence |
| --- | --- | --- | --- |
| `health` | 200 | application/json | Data returned |
| `overview` | 200 | application/json | Data returned |
| `geographies` | 200 | application/json | Data returned |
| `analytical/v1/mortality-trends?limit=1` | 200 | application/json | Data returned |
| `analytical/v1/forensic-toxicology?limit=1` | 200 | application/json | Data returned |
| `mortality/annual?limit=1` | 200 | application/json | Data returned |
| `toxicology/assist?limit=1` | 200 | application/json | Data returned |
| `toxicology/treatment?limit=1` | 200 | application/json | Data returned |
| `geography/inverclyde?limit=1` | 200 | application/json | Data returned |
| `geography/comparisons?limit=1` | 200 | application/json | Data returned |
| `anomalies?limit=1` | 200 | application/json | Data returned |
| `anomalies/models?limit=1` | 200 | application/json | Data returned |
| `monitoring/results?limit=1` | 200 | application/json | Data returned |
| `forecasting/models?limit=1` | 200 | application/json | Data returned |
| `forecasting/results?limit=1` | 200 | application/json | Data returned |
| `sources?limit=1` | 200 | application/json | Data returned |
| `reports` | 200 | application/json | Data returned |
| `exports?resource=forecast_models&format=json&limit=1` | 200 | application/json | Data returned |
| `database/v1/naloxone-activity?limit=1` | 200 | application/json | Data returned |

The deployed revision contains the two CRLF output rules in `.gitattributes` and descends from the checksum repair commit `c20c99e`. The measured artifact-backed failures from the earlier report were not reproduced. This verifies the existing running revision and sampled endpoint data, not deployment of Phase 5 or complete production browser acceptance. No backend repair or infrastructure change was needed. Detailed timestamps, returned counts, response field names and retry history are in [public endpoint evidence](evidence/task08s-phase5/public-endpoints.json); dataset bodies and credentials are not stored there.

## Branding, metadata and canonical host

The local branding suite checks SVG variants, the square symbol, PNG dimensions, the six-resolution ICO and Apple icon. Built initial HTML retains the requested title/description, language, viewport, theme colour, canonical URL, Open Graph fields/image dimensions/type/alternative text, Twitter large-image fields and icon links. [Build evidence](evidence/task08s-phase5/build-and-revision.json) records metadata and file digests.

Existing public apex and `www` pages returned HTTP 200 after apex redirected to `www`. They already contain the SDHI research title and social metadata; all nine checked branding/icon URLs, including the OG PNG, returned HTTP 200 with image content types. Existing HTML points canonical and OG URLs to `https://sdhi.cc/`, so the host preference remains inconsistent. The existing frontend does not expose a reliable commit SHA; its script URL is recorded in the endpoint evidence.

Recommend the approved **apex host `https://sdhi.cc/`** consistently for canonical/OG URLs and hosting, with `www` redirected to apex after owner approval. No host or DNS was silently changed. Existing public metadata/image availability is not a newly published release check. WhatsApp, Facebook and LinkedIn preview rendering/caches are **not yet tested**.

## Security, accessibility and automated tests

Targeted runtime-source/public-asset/build inspection found no sensitive token/private-key patterns; no environment values were printed. Original private configuration and restricted intelligence were not added to the frontend. This is not penetration testing or a security certification. See [exposure inspection](evidence/task08s-phase5/security-check.json).

Responsive checks cover 320, 390, 768, 900, 901, 1024 and 1440 px, including transition focus and drawer behaviour. Existing regressions cover visible keyboard focus, accessible control names, heading labels, disclosures, themes, scrollable tables and sampled contrast. The local responsive checks passed; no formal WCAG certification is claimed.

| Check | Status |
| --- | --- |
| Frontend unit suite | Passed: 113 tests |
| Production build | Passed: 40 modules |
| Focused navigation and safe inspection | Passed: 2 browser cases |
| Full browser suite, all screens and captures | Initial 66-case run: 60 passed, 6 failed. Targeted six-case retry: 5 passed, 1 resize check failed. Mortality subsequently passed the diagnostic check and final capture check. All 66 cases verified across runs; no uninterrupted 66-pass run. |
| Local backend and analysis suite | Passed: 169 tests; one existing Starlette/HTTPX deprecation warning |
| Existing public endpoints and branding | Passed sampled read-only checks, as qualified above |
| Newly deployed Phase 5 / production browser acceptance | Not yet tested; publication not authorised |
| Social application previews | Not yet tested |

The initial browser run found one obsolete assertion requiring the internal forecast filename removed by this task, and five new chart-screen capture checks sampling overflow immediately after viewport resize. The Overview assertion now requires the Research link instead; the new responsive checks wait for the chart/layout resize to settle, matching existing responsive-test practice. Four resize checks passed on the first retry. Mortality required a further settling interval: the diagnostic then showed a 390 px document at a 390 px viewport; wider SVG/table content remained within its intended scrolling containers. The final check removes the diagnostic and allows 500 ms for resize animation before polling. No application code or CSS was changed to suppress these test failures. Retry outcomes are recorded separately; this is not described as an uninterrupted 66-case pass.

## Publication procedure and go/no-go

After owner approval: publish the exact reviewed candidate through the existing frontend/backend workflow; confirm deployed frontend commit through hosting deployment records and built asset digests (build fingerprints depend on the approved production API environment; retain the existing Render API base rather than deploying a development-only relative API configuration); confirm backend `X-SDHI-Revision` and required data routes; rerun all eight public screen, filter, inspection and export checks; verify public assets and initial metadata; confirm canonical redirects; inspect actual social previews where accessible; record any failures separately and apply only approved repairs. Do not treat `/health` alone as acceptance. No DNS, host preference or production setting should change implicitly.

**Local decision: GO for owner review of the release candidate.** No outstanding application test failures remain after the documented retries. Release candidate: `fca20c513ed3cbdee5ccd77c1b0767bda9ab8fe3`. The subsequent report-only commit identifies this tested application tree without changing it. Production publication is not authorised, so production acceptance is **not passed**. Remaining scientific limits are historical cutoffs, sparse/model-dependent monitoring, unavailable source denominators/locality data, reporting changes, forecast uncertainty and incomplete external validation. These are not repaired by interface changes.

## Subsequent forecasting integration correction

A later review found that rolling-origin predictions used source fields not recognised by the chart period helper. The [forecast integration fix report](TASK08S_PHASE5_FORECAST_INTEGRATION_FIX_REPORT.md) records the correction, genuine-data screenshots and new verification results. Its final browser results include one intermittent Toxicology Patterns responsive failure followed by an unchanged passing retry; they must not be described as an uninterrupted clean full-suite pass. Earlier evidence above remains tied to its stated release candidate.
