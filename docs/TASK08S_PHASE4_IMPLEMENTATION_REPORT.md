# SDHI Phase 4 — Research presentation and editorial consistency

Date: 17 November 2026. Local S10 and remaining S11 implementation against Phase 3 commit `26c39f0`. No push, deployment, Phase 5 acceptance or S08 chart implementation is included.

## Research screen and objective coverage

The research screen and its sources/methods route now lead with the adopted study aim and five objective descriptions. The descriptions are explicitly distinguished from verified verbatim Chapter One quotations. Each objective links to the relevant existing analytical screens; interface implementation and software checks are not presented as scientific validation or a user-effectiveness study.

Seven sections organise the explanation: study purpose; objectives and evidence; saved geographic findings; official sources and periods; methods and limitations; scoped downloads; secondary technical records. Original source definitions and complete metadata remain accessible through disclosures. Source loading and geographic findings fail independently, with no inferred values or fallback datasets.

| Objective | Presentation evidence |
| --- | --- |
| O1: official datasets | Separate Police Scotland, NRS, forensic, treatment, ASSIST and ambulance source explanations, reporting periods and source links. Earlier forensic percentage records are labelled as derived research, not an independent official source. |
| O2: historical analysis | Links to mortality, toxicology, geography and compatible comparisons; loaded Inverclyde registered counts and published rates retain their reporting period, confidence intervals and actual council boundary. |
| O3: monitoring | Original Negative Binomial/EWMA and separate opioid-share CUSUM distinguished from later screens; baseline discrepancy and pending external alert validation remain inspectable. |
| O4: forecasting | Retrospective evaluation, 12 shared targets, post-selection limitation and elapsed 2026 Q1 projection explained, with links to the existing forecast evidence. |
| O5: dashboard | Screen-to-objective links, explicit download scope, keyboard-accessible disclosures and tested independent loading states. No formal user-study claim. |

No new research finding, model calculation, rate, indicator or statistical classification was introduced. The page uses the existing geographic contract for the 2024 Inverclyde count and five-year rate comparison; it displays saved intervals without recalculation. Greenock is not assigned those observations. Category overlap, unavailable denominators, ASSIST's unequal windows and shortened Q9, the source opioid category's exclusion of treatment opioids and the possible April 2024 naloxone recording break remain explicit.

## Documentation and download links

The actual remote is `https://github.com/za-0racle/Scotland_Drug_Harm_Indicator`. Unauthenticated GitHub API checks confirmed public visibility and HTTP 200 for each linked file on 17 November 2026:

| Visitor label | Verified repository file |
| --- | --- |
| Data preparation and source provenance | `analysis/phase4/README.md` |
| Original monitoring presentation and interpretation | `docs/dashboard-phase-1.md` |
| Additional statistical methods and limitations | `analysis/phase5c/README.md` |
| Forecasting methodology | `analysis/README.md` |
| Saved forecast evaluation and results | `analysis/PHASE2_RESULTS.md` |
| Geographic findings and published rates | `analysis/phase6/outputs/RESEARCH_FINDINGS.md` |
| Earlier local implementation and testing evidence | `docs/FINAL_ACCEPTANCE_TEST_RESULTS.md` |

The dashboard labels the testing document as earlier evidence, not a current acceptance result. Unpublished local Phase 4 documentation is intentionally not linked as though already public. No private or invented repository link was added. Existing PHS RADAR, Scottish Government suspected-death and NRS 2024 publication links also returned HTTP 200. This confirms link access, not publication of this implementation or verification of current observations.

Downloads distinguish the current analytical/database page, complete eligible selected series, and complete aligned comparison. Direct saved-result links explicitly request only the first page, up to 100 records without selection filters. Existing export contracts and provenance are retained. Database pages, source inventory, source gaps and original records remain secondary inspection routes.

## Editorial changes and files

Added `src/platform/research.js`; integrated its existing API reads in `dashboard.js`; extended `shared.css` using the established design. Small wording corrections in `overview.js`, `overview-data.js`, `mortality.js`, `comparison-studio.js`, `substance.js` and `database-snapshots.js` replace implementation terminology in visitor-facing explanations and source-detail labels. Source terminology and technical identifiers inside original records and exports remain unchanged. The malformed baseline-year separator was corrected to 2017–2020 without changing its meaning.

Browser updates are in `e2e/phase4.spec.js`, `acceptance.spec.js` and `usability.spec.js`. Phase 3 regression captures now go to `test-results` so its approved screenshots remain preserved. No dependencies were added. Research, backend, data contracts, model code, frozen outputs, initial metadata, branding and prior screenshots remain protected.

## Verification and screenshots

| Check | Result |
| --- | --- |
| Full frontend unit suite | 113 passed on the final sources. |
| Production build | Passed; 39 modules transformed. |
| Initial focused research checks | Four passed; one new cross-screen test initially omitted Comparison Studio's required Compare action. Its setup was corrected; this was not an application or external-service failure. |
| Full browser regression and final research checks | 56 passed in one uninterrupted final run, including all five Phase 4 cases and the eight-screen wording check. |
| Public documentation and source links | Public GitHub visibility and seven document paths verified through unauthenticated API requests; three existing official publication URLs returned HTTP 200. |
| Protected-tree comparison | No changes against `26c39f0` in backend, analysis, datasets, Supabase, dependencies, initial HTML, branding, `.gitattributes` or Phase 1–3 screenshots. |

Source-specific regression checks cover separate suspected/registered deaths, non-additive forensic categories, categorical ASSIST periods, no Greenock substitution, 14 official NHS-board peers with Scotland/Unknown separate, and missing versus zero values. Monitoring flags remain historical research; forecast evaluation is retrospective and its saved 2026 Q1 projection remains elapsed. Shared non-operational and no-endorsement warnings remain accessible.

No unintended external-service failure occurred in the final run. Deliberately intercepted failures and malformed responses are test-only. No mock data or runtime fallback was added. The local tests and public documentation-link checks do not constitute production verification.

| Research evidence | Desktop | Mobile |
| --- | --- | --- |
| Study, findings, sources and downloads | [Desktop](images/task08s-phase4/research-desktop.png) | [Mobile](images/task08s-phase4/research-mobile.png) |

Both actual screenshots were reviewed at 1440 and 390 pixels. Research-page overflow and keyboard disclosure checks passed. Shared responsive/theme/focus regressions passed; sampled existing text contrast exceeded 4.5:1. These are targeted checks, not accessibility certification.

## Remaining limitations and Phase 5 readiness

Historical source cutoffs, missing Greenock outcomes, sample denominators, overlapping categories, boundary differences, uncertainty and incomplete external validation remain scientific limits. Local tests do not establish production recovery or public acceptance. No outstanding frontend test failures or known blocking application defects remain from this phase. Phase 4 is ready for owner review before Phase 5 acceptance testing. The work is committed locally; nothing was pushed or deployed.
