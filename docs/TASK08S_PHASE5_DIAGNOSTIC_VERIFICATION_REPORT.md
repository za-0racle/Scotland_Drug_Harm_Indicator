# Phase 5 - Readiness, resizing and forecasting verification

Investigation: 17 November 2026. Final verification: 18 November 2026. Baseline: `5a50541`. Local diagnostics and corrections only; nothing pushed, published or deployed.

## Diagnosis

| Failure group | Evidence and conclusion | Correction |
| --- | --- | --- |
| Four database-dependent browser failures | Saved failures report the generic Supabase read error. Both URL and publishable credential are configured from `.env.local`; no process override is present. Direct reads of mortality, configurations and results returned HTTP 206 with records. Twenty consecutive complete mortality reads succeeded in 14.67 s. The new logs then reproduced the same generic failure during preflight: `URLError` wrapping `TimeoutError` while opening the mortality GET, returning HTTP 503 despite healthy `/health`. This establishes an intermittent upstream connection-setup timeout, not a layout or forecast defect. The original four failures lack underlying logs, so each cannot be retrospectively classified. No current evidence establishes invalid credentials, RLS denial or concurrent test workers. | Preserve visible failures, with sanitised server logs identifying table, offset, category, exception types, HTTP status and errno. No URLs, credentials, headers, bodies or exception messages are logged. The reviewed legacy read path retries connection-setup timeouts once, with both failure and recovery logged and the existing 12-second per-attempt bound. Persistent failures still return 503. Permission/HTTP errors, payload decoding and validation are not retried; paginated snapshot behaviour is unchanged. No cached or fabricated fallback is used. A real database preflight supplements `/health`. Tests start fresh servers by default; reuse requires explicit `E2E_REUSE_SERVERS=1`, preventing unnoticed stale configuration. One Playwright worker remains configured. |
| Geographic Patterns overflow | At the exact 390 x 1000 viewport after 1440 x 1000, `#geo-chart` retained width 1019.59 px and extended the document to 1053 px. It persisted after two seconds; other content fit. A later resize cleared it. This is a stale canvas/container sizing defect, not insufficient assertion waiting. | Constrain the canvas to its parent and give sizing to one observer, scheduling `chart.resize(width,height)` from current container dimensions. Disable the competing automatic Chart.js resize listener, retain window/DPR resize handling, and cancel/disconnect observers and listeners on destruction. No document overflow hiding or longer assertion timeout. Thirty post-fix measurements across geography/toxicology/mortality fit their viewports. New regressions verify visible canvas bounds, actual drawing-buffer size and each plotted point against its current x/y scales through repeated resizes and refresh. Size changes stop obsolete animations and redraw immediately; unchanged dimensions do not trigger another redraw. |
| Public forecast error reported by owner | A fresh browser fetched public bundle `/assets/index-x67rGT4o.js`, SHA-256 `6e0d9c72ad82847c017a1e3f5af2534e196316def807697a6ebd596b940fc752`. It contains the target fallback and Forecast target quarter label. The 17 November fresh-browser check returned all 48 predictions and 12 target quarters, with four model legends and no unavailable message. A further read-only check on 18 November fetched the same bundle and verified every predicted value and interval in all 48 public API rows against the checksum-validated local artifact. | No deployment was required or performed. The tested public code already contains the fix; its exact commit is not exposed. A previously cached browser/build is possible, but the owner's earlier session was not inspected, so that explanation is unconfirmed. Different build hashes alone do not prove outdated forecast logic. |

The local forecast regression checks all 48 predictions against their saved target quarters, model identity and exact intervals. The chart uses `target`, not `origin`; the historical window remains 2023 Q1 to 2025 Q4. No new statistical calculation or current forecast is introduced.

## Files and preservation

- `src/platform/charts.js`, `shared.css`: current-container resizing, lifecycle cleanup and canvas sizing.
- `backend/repositories/supabase.py`: sanitised error classification; one bounded, logged connection-timeout retry; persistent response/error contracts unchanged.
- `playwright.config.js`, new `e2e/readiness-setup.js`: fresh-server default and genuine database readiness checks.
- `e2e/dashboard.spec.js`: verifies refresh recovery after the existing simulated failure; `e2e/layout-resize.spec.js`: three repeated-resize regressions; `backend/tests/test_database_diagnostics.py`: sanitised failure/recovery logs, bounded retry, persistent failure, permission errors and invalid JSON.
- `e2e/phase5.spec.js`: regression captures go to `test-results`, preserving approved images.
- This report and [safe diagnostic evidence](evidence/task08s-phase5-diagnostics/): configuration flags, read-only probe outcomes, before/after geometry and public bundle/browser status. No credentials or response datasets are stored there.

Research outputs, manifest hashes, model code, statistical methods, database records, API payload contracts, metadata and branding are unchanged. No dependency, infrastructure, host or DNS change was made.

## Verification

| Check | Result |
| --- | --- |
| Previously failing cases, resize and forecasting regressions | 9 passed in 2.7 min before the final redraw synchronisation; includes all five reported cases, which are also covered by the final complete suite |
| Final point/axis, drawing-buffer and canvas resize checks | 3 passed in 1.8 min |
| Database failure/recovery and sanitisation regressions | Included in final Python suite; five cases |
| JavaScript suite | 114 passed |
| Production build | Passed, 40 modules; `index-BBTQQL8j.js`, `index-COuYk2Bq.css` |
| Python suite | 175 passed in 700.53 s; one existing Starlette/HTTPX deprecation warning |
| Complete Playwright suite, final sources | 70 passed in 7.4 min, one uninterrupted execution; no test retries |

One initial complete-suite attempt stopped at database preflight with HTTP 503 before any browser cases ran. That exposed the timeout and preceded the bounded-retry correction; it is not counted as a completed suite. An intermediate focused run passed the five reported cases but failed the stronger Mortality Trends buffer-width check (8 passed, 1 failed); a diagnostic rerun passed, confirming the race was intermittent. Sizing was then assigned to one observer rather than leaving automatic Chart.js sizing competing with it. An uninterrupted 70-case run then passed, but screenshot review identified a transient line/axis draw mismatch. Resize redraws were synchronised and point-to-axis checks added. The final complete run uses that refinement.

Focused checks overlap the complete suites and are not additive. The supplied 62/5 run and earlier 66/1 run remain historical evidence; no result has been rewritten.

Actual resize evidence: [before](images/task08s-phase5-diagnostics/geography-before.png), [final mobile](images/task08s-phase5-diagnostics/geography-mobile.png), [final desktop](images/task08s-phase5-diagnostics/geography-desktop.png). Final report captures come from the existing reduced-motion Phase 2 capture cases in the same final 70-test run, avoiding intermediate animation frames. They show the complete series aligned with its reporting years. Separate normal-motion regressions verify actual canvas size, drawing-buffer size and point-to-axis alignment; those assertions were not relaxed.

## Limits and release status

A matching connection timeout was reproduced and is now classified; the original four individual failures lack underlying exception logs. Current successful probes do not prove future Supabase availability. New logs provide evidence if it recurs. Simulated errors remain visible and recovery must succeed without fabricated observations. Public fresh-browser verification does not inspect every visitor cache or establish a public frontend commit. Statistical evidence remains historical, with the existing source, uncertainty and validation limitations. **Local acceptance: passed on 18 November 2026.** No outstanding local test failures remain on the final code. This is not full production acceptance, an uptime guarantee or authorisation to publish. Nothing was pushed or deployed.
