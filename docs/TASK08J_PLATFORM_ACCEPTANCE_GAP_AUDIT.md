# Task 08J — Platform acceptance and completion gap audit

**Review date:** 13 November 2026  
**Mode:** Read-only documentation, implementation, test, and evidence review. No application changes, new research outputs, recalculation, database activity, or live service tests were performed for this audit.

## 1. Executive summary

The available evidence supports a conclusion that the platform is **feature-complete for a supervised local research demonstration within its approved scope**. The eight primary navigation destinations resolve to implemented workflows; source-aware APIs and artifact-backed data are integrated; the acceptance reports record regression, preservation, and browser evidence. Task 08C–08H add and preserve the mortality and forensic analytical contracts, and Task 08I recommends retaining their separate pagination collectors.

That conclusion is narrower than production readiness or scientific/operational validation:

- The dashboard is explicitly a historical research prototype, not an operational warning service. Official-alert and prospective validation evidence is pending or unavailable.
- Hosting, authentication/roles, production observability, load/recovery testing, security certification, and comprehensive accessibility conformance are not established. The local CORS and anon-read arrangement is not an institutional deployment design.
- Current live Supabase/browser service status was not re-probed for this audit. The latest inspected acceptance reports document successful reads and a corrected local Vite proxy issue; those are dated evidence, not proof of present service availability.
- The standalone Task 08A audit and the MSc assessment rubric/supervisor acceptance criteria were not found in the repository. Task 08D records that Task 08A was supplied in conversation; Task 08E also notes that it is absent from the workspace. Its exact criteria cannot be independently traced here.

**No current functional defect was confirmed by this read-only review.** Earlier reported defects (including stale Vite proxy configuration and anomaly ordering) are documented as corrected with regressions. Remaining items are evidence/acceptance gaps or deployment/scientific gates, not a recommendation to add features. No P3 work is recommended automatically.

## 2. Approved scope and evidence hierarchy

### Approved for this project phase

The controlling local scope is the Phase 8 final acceptance decision and the preceding approved screen/task reports: retain the Vite/vanilla JavaScript, Chart.js, FastAPI and reviewed Supabase/artifact architecture; expose eight research workflows; use source-derived observations and frozen outputs; keep definitions, provenance, nulls and boundaries visible; support compatible filtering, comparisons and bounded exports; provide explicit loading/error/unavailable behavior; and verify the implementation without recalculating protected research outputs.

Tasks 08C–08H explicitly approve additive, versioned police mortality and forensic contracts, then controlled single-consumer migrations and source-neutral integrity helpers, subject to independent baselines and no change to legacy behavior. Task 08I is an audit only and recommends **no pagination extraction**. These task reports and their protected evidence are subordinate to, and consistent with, the Phase 8 supervised-demo boundary.

The Phase 8 report's readiness decision is: suitable for a supervised local research demonstration, **not approved for production, institutional adoption, or operational warnings**. “Complete” below is measured against that scope, not a broader institutional product.

### Proposed, deferred, or unapproved

The following are not missing deliverables for the current feature-frozen demonstration merely because they are desirable future work:

- Phase 9 integration; adding individual substances, raw RADAR intelligence, new sources, models, dashboards, or research methods.
- Forecast retraining, live/current threat scoring, automatic refresh/promotion, or alert activation.
- Official alert ingestion or sensitivity/specificity/lead-time calculations without a reviewed complete external event set.
- A map or geographic crosswalk where verified geometry/crosswalk evidence is absent.
- Combining source categories, boundary types, denominators, or death measures into unsupported totals or rates.
- New database policies, credentials, migrations, production hosting, institutional identity, or access roles.
- Pagination consolidation after Task 08I's recommendation to retain the separate collectors.

### Evidence reviewed and limitations

Reviewed the Phase 7/8 reports, eight-screen and usability reports, Task 08B preservation/API/regression evidence, Task 08C–08I reports, source/artifact manifests and baseline summaries, current screen modules, central frontend client, FastAPI routes, artifact and Supabase repositories, configuration, requirements and test/browser suites. Relevant evidence includes the **85-entry source/research manifest verification**, Phase 8 acceptance results, and Task 08H pre/post contract checks.

The 08A audit itself, the full original MSc brief/rubric, supervisor sign-off, and an external accessibility/security assessment were not present in the repository. This audit therefore does not invent requirements from navigation labels or treat future-adoption recommendations as approved deliverables.

## 3. Eight-screen implementation matrix

| Screen | Status | Existing functionality and data/API dependencies | Scientific constraints and relevant evidence | Missing approved work, defects, dependencies |
|---|---|---|---|---|
| **1. Intelligence Overview** | **Complete and verified** for the supervised local demo | Mortality headline/KPIs, historical quarter chart and heatmap, source/cutoff disclosures, forensic snapshot, monitoring context, elapsed forecast preview, coverage links. Uses `/overview` (including live database status), plus artifact-backed overview resources; resources fail independently. | Complete-year requirements prevent partial totals; missing values are not zero; forensic categories are not pooled; forecast origin/target and elapsed status remain explicit. Unit coverage: `tests/overview.test.js`; browser evidence: `e2e/overview.spec.js`, `e2e/usability.spec.js`, Phase 8 acceptance. | No functional gap established within current approved scope. **Current live Supabase availability is unverified in this audit**; the most recent inspected acceptance logs record successful live reads. |
| **2. Comparison Studio** | **Complete and verified** for its admitted comparison types | Compares two compatible areas or two same-source substance categories, aligns periods, shows coverage and original records, paginates complete eligible observations, and exports aligned CSV. Uses geography/comparison and legacy source APIs via the common client. | Rejects incompatible boundaries/definitions, avoids rate/population inference, preserves missing periods, and does not treat categories as additive. Unit tests: `tests/comparison-studio.test.js`; browsers: `e2e/comparison-studio.spec.js`, `e2e/comparison.spec.js`, `e2e/acceptance.spec.js`. | Different indicators, separate-period contrasts, model-output comparison, and incompatible subjects are deliberately unavailable—not missing approved functionality. |
| **3. Mortality Analytics** | **Complete and verified** for the existing research workspace | Dedicated source/year/boundary/area filters, quarterly and annual source views, charts, heatmap/distribution/ranking/table, profiles and exports. It remains on the existing source loaders; the versioned police contract migration is isolated to Geographic Explorer. | Suspected Police Scotland counts remain distinct from NRS registered deaths; original quarter qualifications and nulls are retained. Unit/browser evidence: `tests/mortality.test.js`, `e2e/mortality.spec.js`; Task 08D explicitly confirms this screen did not migrate. | No migration of this screen to the new contract is approved. Do not treat the Geographic Explorer migration as a platform-wide source switch. |
| **4. Substance Intelligence** | **Complete and verified** for the current source feed | Source/area/category/period filters; trends, heatmap, ranking, compatible comparisons, profiles and CSV exports. Only the screen's forensic feed uses the forensic v1 collector; ASSIST/treatment and other consumers remain on legacy routes. | Forensic output preserves 210 records, seven labels, 30 quarters and one real zero. Categories overlap and are non-additive; no sample denominator or prevalence is claimed. Unit tests: `tests/substance.test.js`, `tests/forensic-adapter.test.js`; browser: `e2e/substance.spec.js`, `e2e/forensic-migration.spec.js`; Task 08F baseline/export checks. | No additional forensic consumer migration is approved. Overview, other feeds, and comparison/Geographic Explorer consumers are intentionally not switched in Task 08F. |
| **5. Geographic Explorer** | **Complete and verified** for registered, supported scopes | Boundary-first source/indicator/area/period selection; rankings, selected-area history, profiles, coverage search, published-rate context, same-boundary comparisons, CSV/JSON history exports, and explicit unavailable-map panel. Police history uses the mortality v1 collector; other resources retain their existing APIs. | Police divisions, councils, boards, country, testing/study samples and unknown geography remain distinct. Greenock receives no inferred outcome; no map geometry or crosswalk is invented. Tests: `tests/geography.test.js`, `tests/mortality-adapter.test.js`; browsers: `e2e/geography.spec.js`, `e2e/mortality-adapter.spec.js`, `e2e/local-api.spec.js`; Task 08D and Task 08 final preservation evidence. | A map, additional geographies and unsupported peer comparisons are out of scope absent verified geometry/data. The former local proxy issue is documented as fixed; a running developer server still needs the documented correct startup configuration. |
| **6. Anomaly Detection & Surveillance Signals** | **Complete and verified** as retrospective analysis and explicit evidence-status reporting | Related views cover statistical flags, all stored observations, sensitivity, distribution adequacy, prior-window diagnostics, sparse/unknown counts, statistical runs, cross-source context, external-validation status and the three reviewed database monitoring tables. Uses `/anomalies*`, `/evidence/cross-source`, `/validation/status`, and `/monitoring/*`. | Stored flags are not alerts; robust and conditional model outputs remain distinct; cross-source candidate compatibility is not joint corroboration. FOI/official alerts are pending; no alert metrics are calculated. Phase 8 exact-record/acceptance evidence; `backend/tests/test_acceptance.py`; `e2e/acceptance.spec.js`, `e2e/usability.spec.js`. | External event validation is blocked by absent reviewed event data, but the approved behavior is to disclose this gap, not synthesize metrics. No operational warning/alert workflow is approved. |
| **7. Forecasting Lab** | **Complete and verified** for frozen historical forecast evidence | Tabs provide frozen projection, source observations, candidate model scores and rolling-origin backtest records. Uses `/forecasting/results`, `/observations`, `/models`, `/backtest`. | The recorded projection is historical: origin 2025 Q4, target 2026 Q1, point 248, with preserved intervals/method; it is not a current forecast. No retraining or future claim. `tests/overview.test.js`, browser coverage in `e2e/overview.spec.js`, `e2e/usability.spec.js`, and Phase 8 exact-record checks. | No current prediction, new model, calibration, or operational forecast is an approved deliverable. Currentness requires an explicitly approved new vintage and review. |
| **8. Research, Data & Exports** | **Complete and verified** for documented research access | Related views expose reports, case-study findings, source-quality gaps, source inventory, methods and validation status; bounded CSV/JSON exports retain record and provenance context. Uses `/reports`, `/sources`, `/sources/gaps`, `/methodology`, `/validation/status`, `/exports`, and case-study endpoints. | Exports are bounded pages, not necessarily full source histories; source/version/limitations are retained. Source manifest checks and Phase 8 tests cover values and export scope. | Full-source export, public publication, artifact promotion, source acquisition and institution-specific disclosure workflows are not approved. |

## 4. Backend and data integration assessment

### Route and data-flow status

The active platform uses the central frontend API client and FastAPI; the application reports no direct browser Supabase requests in its acceptance tests. `/api/v1` exposes health, overview, registries, geography/trend/comparison routes, mortality/toxicology/anomaly/forecast/report resources, monitoring reads, exports, and the two separate analytical contracts. Artifact resources are allow-listed and checked against saved SHA-256 manifests; the forensic adapter additionally verifies raw-source/artifact consistency. The two versioned routes validate strict source-specific schemas and collection tokens.

The shared response client has explicit HTTP, unavailable, malformed/non-JSON, schema, timeout, and transport error handling. Screen loaders clear stale evidence before new loads, and several source panels isolate failures instead of hiding working independent resources. Evidence for navigation, retry, stale-response protection, and no automatic legacy fallback includes the Task 08D/08F browser tests and Task 08H equivalence report.

### Pagination, filters and exports

Collectors reject changed tokens, incorrect offsets/counts, overlaps, truncation, duplicate identities, invalid metadata, and incomplete results; they do not return a partial analytical collection. Mortality and forensic frontend collectors remain separate in accordance with Task 08I. Other platform resources use bounded API pagination and compatible filters; comparison exports separately assemble their full eligible aligned result, while generic exports represent the current requested page.

Exact migration equivalence is documented: 504 mortality slots/eight nulls and 210 forensic records/one zero; response/token/identity/page fingerprints; existing presentations and CSVs. Task 08H records all 85 manifests, 72 prior evidence files, and three frozen source/artifact hashes matching. The browser tests cover filters, exports, failures, navigation lifecycle and responsive layout, but the audit did not execute a fresh full suite.

### Current runtime versus recorded evidence

The most recent documented live browser/API recovery exercise corrected a stale Vite process that served HTML instead of the API proxy, and verified a real 5173 outage/recovery sequence. Backend default origins and developer proxy settings are local. This audit did not probe current services, database policies, secrets, or credentials. Therefore:

- **Confirmed from code/reports:** active route architecture and local configuration; anon/publishable-only access in the backend repository; explicit reviewed table allowlist; local no-auth design; historical successful live reads in the acceptance report.
- **Unverified now:** current Supabase network/RLS availability, currently running Vite/FastAPI process behavior, current credential validity, and production-host routing.

These are not evidence of a current defect; they are boundaries on what this read-only audit can assert.

## 5. Scientific integrity assessment

| Topic | Finding |
|---|---|
| Frozen provenance | The Phase 8/Task 08B–08H reports record integrity manifests and independent baselines. The Task 08H evidence reports 85/85 source/research manifests and 72/72 earlier evidence hashes preserved. Passing hashes establish preservation, not truth or methodological validity. |
| Police mortality | Original suspected-death counts are not NRS registered deaths or population-adjusted risk. Quarterly timing qualification, original geography, value order, and eight unavailable/null slots are preserved. No interpolation or substitution is admitted. |
| Forensic toxicology | Source-reported `Number` is represented as detection counts per calendar quarter. Seven original source labels remain separate and explicitly overlapping/non-additive. The single observed zero remains zero; sample/testing definition and denominator are unknown, so prevalence and unique-death counts are unsupported. |
| Other substances and sources | ASSIST study periods and measures remain source-specific and are not forced onto calendar quarters. Treatment, naloxone, forensic detections and NRS mortality are not treated as interchangeable outcomes. |
| Geography | Police divisions, health boards, councils, country, testing/study samples and Unknown remain separate. Unsupported Greenock assignment, boundary crosswalk, map geometry and denominator-derived rates are not fabricated. Published five-year ASRs and intervals are presented as published context, not recalculated annual rates. |
| Anomaly/surveillance | Frozen results and method variants remain distinct. Internal robustness/sensitivity is not external validation; official-alert absence/pending status is not a negative event or evidence of no harm. No sensitivity/specificity/lead-time claim is supported. |
| Forecasting | Frozen origin, target, point and bounds are preserved and labelled elapsed/historical. No new forecast is generated, and no current-condition interpretation is justified by the saved output. |

No material scientific integrity defect was confirmed in the inspected evidence. New sources, revised vintages, retrospective recalculation, or stronger outcome claims would require separate approval and new independent baselines.

## 6. Security and accessibility assessment

### Security and Supabase

The code/report evidence describes a server-side publishable/anon key, explicit reads from three reviewed aggregate/model tables, explicit column selections, GET-only API routes, CORS allowlisting, artifact/resource allowlists, bounded query/page sizes, and sanitized failures. The Phase 8 report records a bundle scan and a successful live read, but this audit did not repeat either. No service-role key or browser-side database request is intended.

**Confirmed research-demo boundary, not a vulnerability finding:** there is no authentication/RBAC, rate limiting, global response-byte/concurrency quota, durable access/export audit system, production monitoring/recovery guarantee, or independent penetration/security assessment. CORS is not authentication. The future-adoption assessment treats these as gates before an institution-hosted evaluation. Current Supabase RLS state was not independently introspected here; the last dated live read is evidence of access at that time, not continuing permission assurance.

### Accessibility and responsive behavior

The platform includes keyboard navigation/focus patterns, labels, skip navigation, table equivalents for charts, responsive table/chart containers, reduced-motion handling, mobile layout and sampled contrast checks. Browser evidence includes 390px overflow checks, mobile navigation, keyboard/dialog behavior, and sampled contrast measurements.

**Implemented but insufficiently verified:** the reports explicitly do not claim WCAG 2.2 conformance. Screen-reader testing, 200–400% zoom/reflow, exhaustive contrast and target-size checks, assistive-technology testing, and representative-user evaluation were not established. An independent accessibility audit is a P2 completion check if required by the MSc rubric or before broader release; it is not evidence that the supervised local demo currently fails.

## 7. Testing and deployment readiness

### Recorded validation

| Evidence point | Recorded result | Interpretation |
|---|---|---|
| Task 08B pre-change regression baseline | 83 frontend unit tests, 19 backend tests, 35 browser tests; production build passed | Establishes the recorded prior baseline, not current full-system certification. |
| Phase 8 final acceptance | 99 combined analysis/backend Python tests, 23 JavaScript tests, build passed, 9 browser tests passed; later API-routing correction records 99 Python, 26 JavaScript, 11 browser tests and build passed | Supports the supervised-demo acceptance at the time. The later report supersedes the earlier stale-port assumption. |
| Task 08F clean browser rerun | 40/40 browser tests passed after one transient initial Overview/Supabase failure | Strong source-migration and full-browser evidence; initial cause remained unresolved in Task 08G. |
| Task 08H extraction validation | 83 backend tests, 106 frontend tests, 40 browser tests, build passed; exact API/presentation/export and evidence preservation checks passed | Latest inspected full cross-platform test/build record; one existing Starlette/httpx deprecation warning. The latest whole test commands are recorded across Task 08H and Phase 8, not as one newly run clean-environment certification. |
| Task 08I | Documentation-only feasibility review; no tests run | Correct for its read-only scope. |

No tests or builds were run for Task 08J. Historical results are quoted as evidence, not represented as a fresh run.

### Deployment

The project documentation instructs local FastAPI and Vite startup; the included Vercel configuration builds static `dist/` output and does not by itself establish deployment of the FastAPI service, Supabase network/RLS behavior, or a supported end-to-end hosted environment. Backend CORS defaults are local origins. There is no production deployment record or sign-off.

**Production/institutional readiness is blocked if it becomes a requirement** by unapproved hosting/network design, identity/role model, permissions/governance decisions, security testing, rate/response limits, monitoring, recovery/load testing, audit retention and ownership. These items are future-adoption gates, not approved feature work in this audit.

## 8. Confirmed defects and unresolved risks

### Confirmed defects in earlier versions, documented as corrected

- Stale Vite configuration on the user port returned non-JSON SPA content for API requests. The dedicated defect report records direct reproduction, restart/configuration changes, outage/recovery behavior and browser coverage. No present recurrence was observed by this audit because services were not run.
- Anomaly results were initially in storage order despite a chronological presentation. The repair report and backend/browser acceptance tests document chronological ordering without changing saved flags.
- Comparison pagination/export/context, stale export state, incomplete overview row counts, source-quality envelope handling, slow timeout, mobile overflow and navigation issues are reported fixed in the relevant Phase 8 reports and regressions.

### Unresolved or insufficiently verified

| Classification | Risk/gap | Consequence |
|---|---|---|
| **Unverified (current environment)** | Current Supabase connectivity/RLS, current Vite proxy process, and deployed API routing were not probed in this audit. | A dated passing acceptance report cannot guarantee today's local runtime or a deployed environment. |
| **Blocked for external validation** | FOI/official alert data are pending; completeness, revision, event/issue dates and geographic compatibility have not been independently established. | No alert-performance metrics or validated-warning claim can be made. |
| **Blocked for operational use** | Prospective validation, calibrated decision thresholds, human escalation, accountable ownership and operational monitoring are absent by design. | The prototype must not be used as an operational warning service. |
| **Insufficiently verified** | Full accessibility conformance and representative assistive-technology/user testing. | Automated samples are not a WCAG conformance claim. |
| **Insufficiently verified** | Concurrency/load, response-byte quotas, availability objectives, backup/recovery and cold-start behavior at a hosted scale. | Local timings and small browser suites are not service-level evidence. |
| **Evidence gap** | Task 08A document, MSc rubric, and explicit supervisor acceptance/sign-off were not located. | Exact academic completion criteria and any missing dissertation deliverable need confirmation. |
| **Unresolved historical event** | Task 08F recorded an initial transient browser/Supabase failure whose cause was not established; later isolated and clean reruns passed. | Do not attribute it to a confirmed application or infrastructure cause. |

No current functional/scientific regression was confirmed by this static/evidence review.

## 9. Completion matrix

Priorities are defined against the **supervised local MSc research demonstration**. P0 does not imply a feature should be implemented: it denotes a blocker to any stronger scientific/security claim. Each row is an auditable requirement group, not a claim that every possible extension is approved.

| Requirement ID | Requirement | Current status | Supporting evidence | Missing work | Priority | Dependency | Recommended next action |
|---|---|---|---|---|---|---|---|
| 08J-SCOPE-01 | Deliver the eight approved research workflows in the existing application | **Complete and verified** | Phase 8 acceptance; shell routes; per-screen tests and browser evidence | None identified for local-demo scope | P1 | None | Preserve feature freeze; do not infer scope from navigation labels alone. |
| 08J-DATA-01 | Use actual backend/API data and explicit unavailable/error states; no fabricated fallback | **Complete and verified** (historical acceptance); current runtime unverified | API client, backend routes, API-routing correction report, acceptance browsers | Fresh runtime probe only if a current demonstration is planned | P2 | Local services and approved environment | Follow documented startup/health/recovery workflow before demo. |
| 08J-DATA-02 | Preserve source/artifact provenance and frozen research evidence | **Complete and verified** | Task 08B manifest; Phase 8; Task 08H preservation: 85 manifests, 72 earlier evidence files, 3 frozen artifact/source hashes | No gap in recorded preservation | P1 | None | Retain immutable evidence; never regenerate expected baselines from current output. |
| 08J-SCI-01 | Preserve mortality values, nulls, units, periods, definitions and geography | **Complete and verified** | Task 08B/C/D/H baselines; 504 observations, eight nulls; source-specific tests | None identified | P1 | None | Keep suspected and registered mortality distinct. |
| 08J-SCI-02 | Preserve forensic category/source semantics, values, zero and non-additivity | **Complete and verified** | Task 08E/F/H baselines; 210 observations, seven categories, 30 quarters, one zero | No sample denominator/chemical definitions exist in source | P1 | New source evidence would require separate approval | Continue to show those unknowns; do not infer prevalence or aggregate categories. |
| 08J-SCI-03 | Restrict geographic claims and comparisons to supported boundaries/definitions | **Complete and verified** | Task 08 Geography, Task 07 comparison, Phase 8 source coverage and acceptance tests | Geometry/crosswalk unavailable; not an approved requirement | P1 | Verified external geography evidence for any future change | Retain explicit unavailable states; no map/crosswalk work is currently recommended. |
| 08J-SCI-04 | Label anomalies, runs, external validation and forecasts without unsupported operational interpretation | **Complete and verified** for retrospective presentation | Phase 8 final acceptance and usability correction; saved output checks and browser tests | Official-alert source and prospective validation remain absent | P0 for operational claims; P1 scope disclosure | Complete reviewed external event data and independent protocol, neither approved nor available | Keep operational claims disabled; expose pending/unavailable status only. |
| 08J-UI-01 | Support compatible filters, complete retrieval, exports, retries and navigation/lifecycle safety | **Complete and verified** for recorded baseline | Platform/adapter tests, 40 browser tests in Task 08H, API error and local proxy regressions | No confirmed gap; no fresh 08J execution | P2 | Test environment | Re-run the recorded suite if release/demo readiness requires current evidence. |
| 08J-UI-02 | Provide responsive and accessible interactions | **Implemented but insufficiently verified** | Keyboard, labels, table equivalents, mobile 390px, sampled contrast and reduced-motion tests | Independent screen-reader, zoom/reflow, exhaustive WCAG and user testing | P2 | Accessibility review resources and rubric | Verify academic acceptance criteria; commission broader audit only if required. |
| 08J-TEST-01 | Preserve regression, build and source-manifest checks after approved changes | **Implemented but insufficiently verified** as one final clean-state run | Phase 8/08H runs pass; Task 08H full backend/frontend/browser/build and preservation evidence | No single fresh clean-environment full run for this audit; live services not probed | P2 | Correct local Python/Node/Edge/service environment | Capture one final timestamped verification only when a final hand-in/demo is scheduled; do not alter frozen outputs. |
| 08J-SEC-01 | Keep current local research data access within reviewed read-only/allowlisted scope | **Implemented but insufficiently verified** for current remote policy state | Backend table/resource/column allowlists; GET-only routes; Phase 8 access and credential-bundle checks | Current RLS/policy introspection and fresh credential/bundle scan not performed in this audit | P2 for local demo; P0 before external/production access | Approved database inspection/access | Verify using approved read-only procedure before any broader environment; do not change policy/credentials under this audit. |
| 08J-DEPLOY-01 | Production or institutional deployment | **Out of scope or unapproved** | Phase 8 readiness decision, backend README, local CORS defaults, static-only Vercel config | Hosting, identity/RBAC, security/reliability gates, ownership and sign-off | P3 unless scope is formally changed; then blocker | Separate institutional approval and adoption plan | Do not deploy or expand access based on local acceptance. |
| 08J-VALID-01 | External-alert/performance validation | **Blocked** as a scientific evaluation objective; pending-status UI is complete | `/validation/status`, Phase 8 and future-adoption assessment | Reviewed complete reference events and pre-specified independent evaluation | P0 for any validation claim; not a current feature requirement | FOI response and scientific/governance review | Await and assess evidence under separate approval; never treat missing alerts as negative events. |
| 08J-ACADEMIC-01 | Demonstrate compliance with exact MSc rubric and supervisor acceptance criteria | **Partially implemented** | Reports, traceability evidence and dissertation Chapter Four pointers exist | Original rubric/brief, Task 08A document, supervisor sign-off, and final hand-in checklist not present | P1 | User/supervisor/institution documents | Obtain and map requirements before declaring academic completion. |
| 08J-ARCH-01 | Decide whether to consolidate pagination | **Complete and verified** as a feasibility decision; extraction not approved | Task 08I report recommends separate collectors; Task 08H says no pagination refactor | None unless new concrete maintenance evidence emerges | P3 | Separate approval and evidence of net benefit | Retain collectors; do not implement consolidation now. |
| 08J-SCOPE-02 | Add Phase 9, live alerting, new dashboards/models, maps or unsupported calculations | **Out of scope or unapproved** | Phase 8/Tasks 08C–08I strict restrictions and evidence limits | Not a completion gap | P3 | Explicit future authorization and source/scientific review | Do not add as part of this MSc completion audit. |

## 10. Prioritized completion backlog

### P0 — scientific integrity or security blockers

No P0 implementation blocker was found for the approved **local historical research demonstration**. The following are hard stops for broader claims or use:

1. Do not present saved anomalies as official alerts, mortality as causal attribution, forensic counts as prevalence, or elapsed forecasts as current predictions.
2. Do not calculate external warning metrics until a complete, compatible, independently reviewed alert/event reference set and evaluation plan exist.
3. Do not make this local prototype externally accessible or production-facing without separate authorization and security/governance review. Current CORS/anon/read-only controls are not authentication or production assurance.

### P1 — approved functionality required for project completion

1. **Resolve academic acceptance scope:** obtain the MSc brief/rubric, supervisor acceptance criteria, and final submission checklist. Trace each criterion to existing implementation, baseline, test, or Chapter Four evidence. This is the only major project-completion dependency not assessable from the repository.
2. **Restore the missing 08A evidence trail:** locate the original audit, add it to the project evidence through the normal approved process if appropriate, and check whether it contains requirements not reflected in the later acceptance matrix. Do not invent its conclusions from later reports.
3. **No additional screen feature is identified as required by the reviewed Phase 8 scope.** Do not treat the P2/P3 gates as reasons to expand feature work.

### P2 — acceptance testing, reliability, accessibility and documentation

1. If a final demonstration or hand-in is imminent, run a clean, timestamped full test/build/preservation sequence in the documented environment, including analysis tests, backend tests, frontend tests, browser suite, build, and the relevant immutable manifest checks. Existing reports already provide passing historical evidence; this step would establish current reproducibility rather than change functionality.
2. Before a live demonstration, verify current `/health`, registry bootstrap, Supabase read state, Vite proxy and one analytical route using the documented local workflow. Do not expose credentials in logs or screenshots.
3. Confirm whether the academic rubric requires broader accessibility evidence. If yes, add an independent WCAG/assistive-technology review as verification, not a dashboard redesign.
4. Include the approved scope, source limitations, frozen forecast cutoff, FOI-pending status, PHS non-endorsement, and validation boundaries in the dissertation/demo narration.

### P3 — optional work outside current feature freeze

No P3 feature is recommended for implementation. Institutional hosting, role-based access, monitoring, operational alerts, new source vintages, new maps, new analytical methods, and pagination abstraction require separate approval and are not necessary to close the evidenced local-demo scope.

## 11. Proposed sequence of small, controlled completion tasks

1. **08J-A — Academic criteria reconciliation (read-only):** obtain the rubric, supervisor criteria, and Task 08A; build a criterion-to-evidence checklist. Stop for clarification on any unmet or ambiguous criterion.
2. **08J-B — Hand-in/demo verification (only if scheduled):** use the documented environment to run the clean test/build/preservation checklist and a brief real-service smoke test. Record failures as failures; do not relax tests or regenerate frozen baselines.
3. **08J-C — Dissertation evidence assembly (if requested/approved):** prepare Chapter Four references to architecture, screen acceptance, provenance, tests, scientific limitations, and non-production status. Do not change application behavior or claim model/external validity.
4. Stop. Any external evaluation, accessibility certification, institutional deployment, operational alerting, source refresh, or feature expansion should be separately proposed and approved.

## 12. Evidence gaps requiring clarification

- Where is the authoritative Task 08A Data Quality & Analytical Architecture Audit, and does it impose requirements absent from Phase 8?
- What exact MSc rubric, supervisor-approved scope, and acceptance/sign-off criteria define “complete” for the dissertation?
- Is a clean final all-suite run required at submission time, or do the dated Phase 8/Task 08H runs suffice?
- Does the rubric require formal accessibility conformance or only the sampled responsive/keyboard evidence already documented?
- Is the final deliverable a local supervised demonstration, or has a separate deployment/institutional-evaluation scope been authorized? Current repository evidence supports only the former.
- Will official-alert/FOI evidence be available before submission? If not, pending status and non-evaluability must remain explicit; this does not justify a proxy metric.

## 13. Dissertation Chapter Four implications

Chapter Four can describe a completed **source-aware historical research prototype** and its implementation evidence: eight screen workflows; the Vite/FastAPI/data flow; artifact and source provenance; preservation of heterogeneous definitions, boundaries, nulls and genuine zero; controlled versioned adapters; API/browser regression results; and the Task 08H exact equivalence/preservation checks.

It should explicitly distinguish implementation verification from scientific validation. A passing test suite shows that code preserves the recorded contracts and values; it does not establish source truth, causal interpretation, forecast skill, alert sensitivity, prospective utility, or institutional approval. State that the Phase 8 readiness decision is a supervised local research demonstration only; the forecast is historical/elapsed; official-alert validation is pending; forensic categories overlap and have no supplied denominator; and the platform does not issue operational warnings.

Do not characterize the platform as deployed, PHS-endorsed, a validated surveillance service, or a current prediction system. Cite the missing Task 08A/rubric evidence as a completion limitation until reconciled with the supervisor. No dissertation edit was made in this audit.
