# Phase 8 final acceptance report

Review date: 10 November 2026. Scope: end-to-end acceptance of the Phase 7 local research prototype, demonstrable application fixes and documentation. No broad analytical development, retraining, source acquisition, migration, RLS/permission change, database write, dissertation edit, deployment or operational alert activation occurred. Earlier unrelated working-tree changes were preserved.

## Readiness decision

**Suitable for a supervised local research demonstration, with the limitations below. Not approved for production, institutional adoption or operational warnings.** Acceptance covers the available reviewed data and frozen outputs; it does not establish predictive or clinical validity, complete accessibility conformance, security certification or PHS approval.

## Acceptance matrix

| Criterion | Result and evidence |
| --- | --- |
| Frontend -> FastAPI -> storage -> chart/table | Passed. Active `src/main.js` imports only the platform interface; its central HTTP client uses `/api/v1`. Browser request monitoring found no direct Supabase requests. Overview exercises live database access; geographic/anomaly/forecast views exercise verified artifacts. Changed test-only API prediction changes both displayed value and rendered canvas pixels |
| Actual filters and exports | Passed. Browser year changes alter HTTP query strings and Inverclyde results from 15 to five years. Area/substance/model/date filtering is tested against actual source rows. Current-page exports now match the displayed filters. Comparison responses are bounded after combining areas |
| Geographic coverage | Passed for all admitted data. 13 police divisions, 14 health boards, Inverclyde council, Scotland, forensic/study samples and Unknown geography. Registry has 33 entries, of which Greenock locality explicitly has no admitted series. Backend acceptance iterates every available area and its listed indicators, matching observation values to source artifacts |
| Compatible comparisons | Passed. Same-boundary board comparison returns 878 observations across two series, retains provenance and paginates the combined representation. Different boundaries are rejected. A specific indicator is required. No invented geographic crosswalk or map |
| Eight navigation sections | Passed. Every section loads without an application error. Tabs cover source inventory, source gaps, method sensitivity, runs/evidence and historical forecasts; controls irrelevant to whole-page metadata/forecast views are hidden. No unsupported Greenock findings |
| Scientific values and definitions | Passed for the tested artifact/DB representations; see scientific cross-check table below. No analytical calculation or threshold was changed |
| Failure handling | Passed for simulated backend and Supabase outages, empty/RLS-style access, malformed JSON/contract, missing/corrupted artifacts, invalid filters, incompatible scope and slow responses. No mocked fallback exists in the application; test substitutions are isolated to test transports |
| Security boundaries | Passed for defined local checks: credential/bundle scan, anon-only database repository, CORS, GET-only data routes, resource/column allowlists, invalid parameters and bounded pagination. Full authentication, rate-limiting, infrastructure and penetration testing remain deployment blockers |
| Performance | Local sampled API and UI measurements recorded below. Adequate in sampled single-user use. Not a concurrency/load-test or availability guarantee; cold artifact parsing remains a limitation |
| Accessibility and responsive presentation | Sampled checks passed: keyboard skip/focus, labels, equivalent tables, canvas label, seven contrast pairs and mobile overflow. Full assistive-technology/zoom/user testing remains open |
| Preservation | Passed: 85 protected earlier-phase hashes verified; Phase 6 input/code/output hashes match its unchanged manifest. Analytical tests regenerate only into ignored scratch |
| Production/operational readiness | Not met and outside scope. No identity/role system, production reliability/security sign-off, prospective validation or complete external event reference. No PHS endorsement |

## Defects found and corrected

| Defect | Correction and regression evidence |
| --- | --- |
| Comparison API independently paginated each area, reported a page-sized total, dropped artifact metadata and could return twice the requested limit | Select an explicit compatible indicator; combine full source series, sort deterministically and apply one bounded page. Preserve artifact version/hash/source. Backend regression checks seven-row pages and total 878; browser verifies two-area pagination |
| Export links rebuilt filters differently from displayed requests, stripping Inverclyde geography/indicator or dropping the implicit robust model | Export links retain the actual effective request parameters. Browser fetches the link and asserts five Inverclyde records from 2020 onward; backend asserts exact page equivalence |
| Failed loads left previous export links/pagination/details active | Clear and disable these at the start of every load; failure test confirms exports hidden and next-page disabled |
| Overview rendered six source rows with the enclosing one-record overview total | Set the source-table total from the returned sources; no hardcoded research count |
| Source-quality report extracted ten nested rows from a one-row envelope with the wrong count/provenance | Add read-only `/api/v1/sources/gaps` over the existing allowlisted artifact; UI now uses its correct envelope, count, pagination and export |
| Some global controls appeared applicable on metadata/forecast pages that did not use them | Hide the filter panel where inapplicable; disable analytical-model/compare controls on incompatible sections. Geography/trends clear model filters |
| Browser back/forward navigation did not restore sections | Navigation uses history entries and a popstate handler, retaining the existing page loader |
| Slow artifact first-load could exceed the original 20-second client timeout | Increase bounded timeout to 60 seconds and retain explicit loading/timeout errors. A targeted unit test exercises actual AbortController timeout handling; no static substitution |
| Source/version information and forecast origin/target required opening JSON details | Add visible source/version/cutoff summaries and origin/target table columns. Cutoff labels explicitly distinguish observation cutoffs from publication dates |
| A stale asynchronous case-study response could append after leaving the section | Guard case-study rendering with the current request ticket |
| Mobile overflow on the large-series presentation test | Wrap long provenance paths, retain chart resize settling, and verify no page overflow at 390px. Strengthen form-control borders and keep mobile navigation in its scrollable row |
| Literal question marks replaced punctuation in the Phase 7 report | Repair only the affected documentation punctuation, using portable text; historical scientific artifacts remain untouched |

## Data-flow and geographic verification

Representative real flows:

1. Intelligence Overview -> `/api/v1/overview` -> Supabase repository -> reviewed mortality rows plus artifact coverage -> accessible row count/source table. A simulated database outage displays an error for the database while keeping clearly identified artifact research summaries; it never substitutes static mortality observations.
2. Geographic Explorer -> source-derived geography/indicator registry -> `/geographies/{id}/trends` -> Phase 4/6 artifact checksum validation -> original observations -> Chart.js and equivalent table. Year filtering and comparisons use backend query parameters.
3. Anomaly Detection -> `/anomalies` with optional method -> Phase 5 or 5C output -> exact stored flags/bounds. Original robust flags remain distinct from conditional count-model results.
4. Surveillance Signals -> runs/evidence/validation APIs -> original 44 runs, candidate compatibility records or explicit FOI-pending metadata. No official alert is inferred from a statistical result.
5. Forecasting -> frozen Phase 2 results -> elapsed target 2026 Q1 from origin 2025 Q4 -> displayed point/intervals and historical disclaimer. No current forecast is issued.

Coverage checks include all available police/board/council area-indicator combinations, unknown/unsupported IDs, council/board incompatibility, suppressed counts and date/category filters. Eight suppressed mortality values remain null. Greenock is an explicit unavailable locality; Inverclyde council, Renfrewshire and Inverclyde police division and NHS GG&C retain their own measurements and boundaries. No wider observation is relabelled Greenock.

## Scientific cross-checks

| Research result | Verified representation |
| --- | --- |
| Original mortality | All 36 live Supabase `(year, quarter, suspected_deaths)` tuples exactly match the frozen validated Phase 2 CSV; 2017 Q1 through 2025 Q4, no interpolation |
| Phase 4 trends | Full artifact-record values preserved for mortality, forensic, ASSIST, treatment and naloxone; every admitted area's indicator values equal the source rows. Period definitions and null values remain unchanged |
| Phase 5 original screen | 47 original flagged observations; sensitivity remains a separate artifact. No threshold retuning or claim that flags are independent toxicity events |
| Phase 5C enhanced methods | Original numerical output fields preserved across all model records; NB2-moments returns 40 flagged observations. Conditional 99% bounds are not relabelled equivalent to robust k=3 limits |
| Original runs | 44 original robust statistical runs. A statistical run is not an official alert or independently validated incident |
| Cross-source evidence | 4,512 method-specific evidence rows over 2,256 candidate pairs remain artifact-backed; compatibility information is attached from the candidate output, not inferred from matching place names. No joint corroboration is fabricated |
| Forecast | Origin 2025 Q4, target 2026 Q1, naive point 248. Bounds and model/backtest artifacts are preserved; target is explicitly historical/elapsed |
| Inverclyde registered mortality | 15 annual observations, 2010-2024; 2024 count 25. Separate from Police Scotland suspected deaths |
| Published rates | 2020-2024 published five-year ASR: Inverclyde 35.6, 95% CI 29.3-41.8; Scotland 22.5, CI 21.9-23.1 per 100,000. These are not annual crude rates; no compatible annual council denominator is invented |
| Official alerts / FOI | Pending and non-evaluable. Absence of local records is not absence of official alerts. No alert-based sensitivity, specificity or warning lead time calculated |

The exact-record regression reads original outputs, then checks every original key/value against the API service representation for the main observation, anomaly, enhanced-model, run, forecast and rate resources. It does not refit models or validate underlying clinical causation. Existing historical reproduction/leakage/model tests remain part of the complete Python run.

## Executed commands and results

Run from the repository root:

```powershell
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests backend/tests -q -p no:cacheprovider
npm test
npm run build
npm run test:e2e
git diff --check
```

- Complete Python run: 99 passed, one existing HTTPX deprecation warning, in 426.32 seconds (81 analytical + 18 backend/acceptance tests).
- Targeted backend run before the complete run: 18 passed in 84.36 seconds (12 existing API tests plus six new acceptance tests).
- JavaScript: 23 passed, including the new slow-request timeout regression.
- Final build: passed, 14 modules; CSS 9.23 kB / 2.78 kB gzip; JavaScript 221.73 kB / 76.79 kB gzip; local output only.
- Final browser run: nine passed in 47.9 seconds. Microsoft Edge, Playwright, one worker. Active-frontend requests, navigation, all board/division options, effective filters/exports, API-driven canvas change, comparisons, error/empty/unavailable states and mobile/keyboard/contrast checks executed.
- Read-only live smoke: 36 mortality, four configurations, 76 results; all results have configuration labels. Exact live mortality values match the frozen CSV. No credential was printed.
- Final analytical guard: 85 protected hashes match; Phase 6 input/code/output hashes unchanged. No baseline output regenerated in its original directory.
- `git diff --check`: passed, with existing working-tree CRLF notices only. A direct whitespace check also covers new acceptance/report files.

One browser presentation test initially failed mobile overflow; wrapping/resize handling was corrected and the complete browser suite rerun. Starting extra local servers initially reported ports already in use: the existing Vite server was reused, and the known existing API was restarted to load the fixes. Neither was deployed. Python tests emit the existing Starlette TestClient HTTPX deprecation warning; no failing assertions are hidden by it.

## Performance and accessibility observations

Single local warmed-server HTTP samples (seconds): health 0.061; overview including Supabase 0.859; mortality 0.549; configurations 0.594; results with labels 1.268; NB2 flags 0.800; 1,000-row naloxone response from 7,024 total 0.216. These are one request each during acceptance, not p95/p99 estimates or concurrency benchmarks. The UI bounds tables/charts to 100 records per page, with pagination; a board's 439-week source is not claimed to render all at once.

Final browser timing/contrast sample: dashboard ready 1,373ms; area selection ready 541ms; seven sampled text-colour pairs all above 4.5:1. Earlier accepted sample: dashboard ready 1,522ms, area selection ready 539ms; seven text colour pairs ranged from 5.41:1 to 14.30:1. Source paths now wrap on mobile. Accessible control labels, canvas/table equivalence, keyboard skip link, visible focus and 390px reflow were exercised. Full screen-reader, zoom/400% reflow, touch-target, motion, cognitive accessibility and exhaustive contrast testing were not performed. Review against the complete [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) is still required; sampled tests do not establish conformance.

Cold large-artifact parsing was approximately 14.6 seconds in Phase 7's concurrent local test context. The API caches parsed artifacts by manifest/file modification time. No cold-start production performance or multi-user reliability claim is made. The 60-second client timeout fails explicitly; it does not guarantee an acceptable service level.

## Security and governance findings

Built JS was checked against the actual configured database URL/key without printing either; neither was found. Secret/service-role markers were absent. Backend access remains anon-only with explicit columns on the three reviewed tables, read pagination/cap detection and sanitized connectivity errors. CORS rejects untrusted origins; analytical routes are GET-only. Arbitrary resource paths/SQL fields, invalid limits and incompatible boundaries are rejected. Missing/corrupted artifacts return unavailable/error responses. Exports are allowlisted public aggregate/model artifacts; private RADAR intelligence and unreviewed tables are not accessible. Row limits are enforced, including the corrected comparison API; a global response-byte/concurrency quota remains unimplemented.

These checks do not replace a security assessment. Identity/RBAC, production transport/proxy/host security, rate limiting, secret rotation, durable access/export audit logs, dependency review, monitoring/recovery and independent penetration testing remain institutional deployment blockers. CORS is not authentication. The local CLI refresh stays private, destination-restricted and separate from data publication.

## Demonstration workflow

Start the API and frontend in separate terminals as documented in `backend/README.md`:

```powershell
.\analysis\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
```

Open http://127.0.0.1:4173; API contracts are at http://127.0.0.1:8000/docs . Existing local credentials are unchanged. The API/frontend local processes may already occupy these ports; reuse the running instance or stop that known local process before restarting.

1. Overview: introduce research-prototype status, live database access status, frozen source cutoffs, original flags/runs and the absence of operational validation.
2. Trends & Patterns: select country -> Scotland -> the suspected-death indicator. Review the original quarterly counts; use the year range and record details. Choose a different explicitly named source indicator without pooling registered and suspected deaths.
3. Geographic Explorer: choose police division or health board and a supported indicator; compare two areas of the same boundary type. Explain counts versus rates, pagination and source differences.
4. Anomaly Detection: clear scope filters for the full original 47-flag view, then select NB2-moments for its separate 40-flag comparison. Use sensitivity/diagnostic tabs without describing one method as validated truth.
5. Surveillance Signals: choose the original robust model and appropriate/cleared filters for 44 runs. Review cross-source candidate compatibility and the FOI-pending external-validation status; a lack of joint signals is not evidence of no harm.
6. Geographic Explorer -> Explore Inverclyde annual series: inspect 2010-2024 registered deaths, filter from 2020, show the five-year ASR/CI context and the explicit absence of Greenock-specific outcomes. Download the filtered page to demonstrate provenance and matching scope.
7. Forecasting: show origin 2025 Q4, elapsed target 2026 Q1 and intervals/backtest limitations. Never describe it as a new current prediction.
8. Reports & Exports / Data & Methodology: review source gaps, versions, sampling differences and the adoption gap assessment before inviting feedback.

For full-dataset anomaly/run counts after a scoped exploration, clear boundary, reporting area, indicator, substance and year fields. Changing these fields intentionally filters the result; a filtered zero is not a no-harm conclusion.

## Files changed for Phase 8

Application fixes: `backend/services/platform.py`, `backend/main.py`, `src/api/client.js`, `src/platform/dashboard.js`, `src/platform/data.js`, `src/platform/style.css`.

Acceptance tests: new `backend/tests/test_acceptance.py`, `e2e/acceptance.spec.js`, `e2e/presentation.spec.js`; updated `tests/platform.test.js` and `e2e/dashboard.spec.js`.

Documentation: new this report and `docs/PHS_FUTURE_ADOPTION_GAP_ASSESSMENT.md`; corrected punctuation in `docs/PHASE7_FULLSTACK_IMPLEMENTATION_REPORT.md`. No research artifact or calculation module was edited.

Local evidence: `test-results/phase8-desktop.png`, `test-results/phase8-mobile.png`, Playwright presentation attachment, and ignored `analysis/test_scratch.local/phase8_acceptance/smoke.json`. These are verification artifacts. Screenshots should be checked for current filter/source labels before reuse; no secret-bearing configuration should be captured.

## Remaining limitations and deployment blockers

No Greenock-specific outcomes, compatible annual council denominators, newly issued forecast, current threat score, independent alert/event validation, complete original publication-vintage reconstruction or institutional endorsement exists. Testing/sample exposure, recording changes and source compatibility remain scientific limitations documented in prior reviews. No new map or incompatible geographic rate was invented.

Research demonstration acceptance is distinct from future PHS or other institutional evaluation. The separate [future-adoption gap assessment](PHS_FUTURE_ADOPTION_GAP_ASSESSMENT.md) lists ownership, permissions, identity/roles, audit, reliability, hosting, accessibility, source-vintage and model/external-validation gates. Those gates remain open; no deployment or operational decision is authorised by this report.

Stop after Phase 8 acceptance for research-team review.

## Post-acceptance P0 correction: actual user-port API routing

The subsequent manual report at `http://localhost:5173/#overview` revealed a genuine environment-specific integration failure: the user's older Vite process did not load the new API proxy and served non-JSON responses at `/api/v1/geographies?`. The original acceptance run on 4173 did not verify that already-running process. Its general readiness statement must be read with this correction.

The stale 5173 process was identified and restarted. Development now explicitly loads the proxy configuration and uses strict-port behaviour. The client reports distinct response/network/configuration errors, and Refresh API data retries full registry bootstrap after an initial failure. Real stopped-backend -> started-backend recovery at the actual user URL was verified without intercepted API responses. Both registry/indicator loading and actual division/board chart/table retrieval work after restoration and on page reload.

The corrected complete browser suite passed **11 tests** across real services on 5173/4173; **26 JavaScript tests** passed and the production build passed. Final repeated Python result: 99 passed in 382.62 seconds; one existing HTTPX deprecation warning. No research findings, data, schema or RLS were modified. Local processes were left running for review, not deployed. Startup/recovery instructions, exact HTTP evidence, screenshots and known limitations are recorded in [the dashboard API defect report](PHASE8_DASHBOARD_API_DEFECT_REPORT.md).
