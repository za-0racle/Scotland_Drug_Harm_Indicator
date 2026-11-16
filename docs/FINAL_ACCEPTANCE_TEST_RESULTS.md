# Final Acceptance Test Results

**Execution date:** 16 November 2026  
**Environment:** Local Windows development environment; local Vite and FastAPI services; live database access was read-only.  
**Result:** All executed automated test suites and the production frontend build passed. This is not a public-deployment, penetration-test, or accessibility-certification result.

## Test outcomes

| Area | Command or check | Result |
|---|---|---|
| Frontend unit tests | `npm test` | **PASS — 108 tests** |
| Backend and analysis tests | `python -m pytest analysis/tests backend/tests -q -p no:cacheprovider` | **PASS — 167 tests.** One Starlette/HTTPX deprecation warning was reported. |
| Browser end-to-end | `npm run test:e2e` | **PASS — 41 tests.** Full run completed in 8.3 minutes with one worker. |
| Production frontend build | `npm run build` | **PASS — Vite 8.3.5.** |
| Live database API pagination | Read-only naloxone API, 500 rows per page | **PASS — 7,024 of 7,024 rows**, 15 pages, 7,024 unique geography-week keys, 439 weeks and 14 NHS boards. |
| Naloxone geography reconciliation | Compare Scotland with the 14 boards plus Unknown for each week | **PASS — 439/439 weeks reconciled.** Scotland and Unknown were kept outside board-only selectors, rankings and summaries; the browser acceptance test confirmed 14 health-board area options and 14 board ranking entries. |
| Exports and error handling | Playwright acceptance scenarios | **PASS.** Selected-scope exports, page-only snapshot CSV, retry behavior, stale-result clearing, and explicit unavailable/malformed/empty states were exercised. |
| Forecasting and anomaly screens | Eight-screen acceptance plus screen-specific browser tests | **PASS for rendering and stated limitations.** This does not establish prospective forecast or anomaly validity. |
| Responsive and accessibility smoke checks | Playwright mobile/keyboard flows and sampled contrast checks | **PASS for exercised smoke checks.** No full WCAG audit or certification was performed. |
| Browser/database boundary | Browser request/error assertions and production bundle scan | **PASS for these checks.** No direct browser Supabase requests were observed; neither configured Supabase URL/key value nor a secret/service-role marker was found in the built bundle. This is not a penetration test. |
| Research artifact preservation | Automated analysis/backend tests and change review | **PASS for the executed checks.** No database writes, schema changes, research recalculations, or frozen-artifact replacements were performed during this sprint. |

## Browser coverage

The full Playwright suite exercised the primary screens and additional flows for comparison, geography, mortality, forensic/substance evidence, exports, responsive layouts, keyboard interaction, API failure/retry behavior, database snapshots, and research-artifact separation. The all-eight-screen case saved genuine local application screenshots under `test-results/final-screenshots/`.

The full run emitted console warnings in tests that deliberately simulate unavailable, malformed, or failed API responses. Those scenarios passed their expected-state assertions; the warnings do not indicate test failures.

## Live read-only pagination details

The API returned 7,024 naloxone rows over 15 pages at a requested page size of 500. The retrieved set contained 7,024 unique geography-week keys, spanned 439 weeks, and contained 14 NHS boards. For each of the 439 weeks, the Scotland aggregate equaled the sum of those board values plus the separate Unknown value. The reconciliation confirms the retrieved representation and arithmetic; it does not resolve the disclosed provenance discrepancy for the 14 first-week moving-average values.

No write, mutation, schema, policy, or migration operation was issued against the database.

## Limitations and non-claims

- The browser suite uses the local demonstration stack. No public deployment was exercised.
- The Vercel configuration builds only the static frontend; a working public FastAPI host remains unverified.
- Contrast checks cover a limited set of rendered elements, and responsive/keyboard checks are smoke tests rather than formal accessibility certification.
- Bundle scanning and simulated error-path tests do not constitute a penetration test or security certification.
- Historical forecast and anomaly displays were checked for presentation and limitation wording, not prospective predictive performance or operational suitability.
- The 14 live naloxone moving-average values and 14 `geographic_areas.valid_to` values still require provenance confirmation before any research revision or temporal boundary interpretation.

## Screenshot evidence

The eight genuine local captures and their screen-by-screen review checklist are listed in [Final Screenshot Checklist](./FINAL_SCREENSHOT_CHECKLIST.md). The PNG files are ignored by Git and must be copied into the final dissertation/submission archive if they are required there.
