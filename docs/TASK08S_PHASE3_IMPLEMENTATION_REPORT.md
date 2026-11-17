# SDHI Phase 3 — Statistical monitoring and forecast evaluation

Date: 17 November 2026. S07 and S09 implemented locally against Phase 2 commit `08f46e7`. S08 assessed only. No publication or Phase 4 implementation is included. A concurrent local commit, `07993a5` (`Uograde`), captured the initial Phase 3 source changes during implementation; it is preserved, with final refinements and evidence committed separately.

## Implemented

| Change | Result | Study objectives |
| --- | --- | --- |
| S07: monitoring | Original monitoring results lead, with explicit stored statistic, limits, flags and separate CUSUM components. A configuration selector and bounded scrolling table make the original records easier to inspect without removing rows. Original settings remain accessible. Additional historical screens, parameter comparisons, consecutive flags and validation retain separate explanations and existing controls. Full records and source details remain inspectable. | O1/O2/O3/O5 |
| S09: forecasting | Four candidate scores lead, with MAE in deaths, a result statement derived from the loaded scores, the 12 shared retrospective targets and the selection limitation explained. Fuller methods and uncertainty explanations sit in a disclosure. The saved elapsed projection follows the evaluation. Historical observations, rolling-origin predictions, complete result inspection and existing page-scoped exports remain available. | O2/O4/O5 |

The last-observation baseline has MAE 21.58, compared with 25.26 for the Negative Binomial trend, 25.99 for simple exponential smoothing and 32.17 for the seasonal baseline. Display rounding does not alter saved values, record details or exports. Selection and evaluation used the same targets; there is no independent post-selection test. The saved 248 estimate for 2026 Q1 uses observations through 2025 Q4; its saved 80% and 95% bounds remain unchanged. It is not an observed total or a current forecast.

Original rolling Negative Binomial residual monitoring with EWMA, separate opioid-share CUSUM, later moments-based count comparisons, the forecasting trend model and the median/MAD screen remain distinct. Flags and runs do not count verified incidents. Parameter sensitivity does not measure detection sensitivity. The unresolved fixed 2017–2020 design versus rolling 8/12/16-quarter implementation discrepancy remains visible in the methods disclosure and preserved research documents. No RADAR validation, lead time, specificity, operational warning or PHS endorsement is claimed.

## S08 feasibility assessment — no charts implemented

Evidence inspected: [earlier dashboard report](dashboard-phase-1.md), [existing series transformations](../src/analytics.js), [earlier chart code](../src/charts.js), and the reviewed backend monitoring fields. The earlier frontend remains inactive.

| Requirement | Available evidence and decision |
| --- | --- |
| Series identity and time | `configuration_id`, joined `configuration_label`, `observation_year`, `observation_quarter` and `computation_reference` exist. Configuration records include method, baseline description and window. A future implementation must select one configuration, sort quarters and retain missing-quarter gaps. |
| EWMA statistic and limits | `statistic_value`, `lower_limit`, `upper_limit` and the stored `signal_flag` are sufficient for a stored-statistic chart with exact per-period limits. Earlier evidence records the 16-quarter 2022 Q3 flag at −1.16480084 with limits ±0.9873333333. These are residual-scale statistics, not death counts. No browser threshold reclassification is justified. |
| CUSUM components and decision limit | `cusum_positive` and `cusum_negative` are separate fields. Use their stored values and `upper_limit`; zero `lower_limit` denotes a reset baseline, not a lower alarm. Configuration K = 0.5 SD and H = 4.77 SD must not replace the stored-scale decision limit. |
| Coverage and missing evidence | Earlier reviewed evidence identifies calibration in 2022 Q1–2023 Q4, reset in 2024 Q1 and only four 2024 monitoring outputs. Calibration observations are not supplied in the monitoring response. Do not reconstruct or extend them. Null components/limits must remain unavailable, and empty access must not become zero flags. |
| Interpretation risks | A generic marker using `statistic_value` may not identify which CUSUM component signalled. A future chart must preserve the stored flag without attributing an unsupported component crossing. Configuration notes and computation references require inspection; the original baseline discrepancy remains unresolved. |
| Frontend feasibility | Feasible for saved monitoring periods using existing Chart.js and API responses, with configuration-specific semantics, gap handling, accessible tables and recorded flags. No model calculation or API change is required. This is conditional display feasibility, not validation of the original model. Dedicated EWMA/CUSUM charts require separate approval. |

## Files and preservation

Application changes: `src/platform/dashboard.js`, `filters.js`, `presentation.js`, `shared.css` and new `research-presentation.js`. Browser specifications explicitly select the supporting projection where needed; the Phase 2 capture suite now writes regression captures to `test-results`, preserving its approved screenshots. New Phase 3 tests and screenshots accompany this report.

Backend contracts, database schemas, model code, research data, frozen outputs, dependencies, metadata and branding remain outside the change. Existing original-monitoring endpoints do not offer the analytical export resource contract; no unsupported export link or backend extension was added. Their complete records and configurations remain readable. The monitoring configuration selector filters the current returned page and states that scope explicitly. Existing analytical page exports retain their original scope and precision.

## Verification

| Check | Result |
| --- | --- |
| Focused monitoring/forecast and shared-browser checks | Initial run: 11 passed, one geographic loading timeout; the same geographic case subsequently passed in the full run. |
| Final focused browser checks | 7 passed, including separate CUSUM components, configuration selection, run direction, pending validation, forecast ordering, values, exports and desktop/mobile overflow. |
| Full frontend unit suite | 113 passed, including saved-interval preservation and suppression of unsupported candidate conclusions. |
| Production build | Passed; 38 modules transformed. |
| Full browser regression | 51 passed in one uninterrupted run. After final explicit-column and scientific-wording refinements, the affected monitoring/forecast and usability suite also passed all 7 cases. |
| Research and Phase 1 preservation | No differences against `08f46e7` in backend, analysis, datasets, Supabase, dependencies, initial HTML, public branding or `.gitattributes`. |

The first sandboxed unit attempt could not spawn Node workers (`EPERM`); the permitted process run passed. The initial browser timeout occurred while unchanged Geographic Patterns was loading, not an asserted statistical mismatch. Later all-screen acceptance and that geographic regression passed. Deliberate intercepted failures and malformed responses remain test-only; no application fallback or fabricated data was introduced.

| Actual analytical screenshots | Desktop | Mobile |
| --- | --- | --- |
| Original monitoring | [Desktop](images/task08s-phase3/monitoring-desktop.png) | [Mobile](images/task08s-phase3/monitoring-mobile.png) |
| Forecast evaluation | [Desktop](images/task08s-phase3/forecast-desktop.png) | [Mobile](images/task08s-phase3/forecast-mobile.png) |

Captures use actual configured data at 1440 and 390 pixels. Sampled shared text contrast exceeded 4.5:1 in browser checks; this is not an accessibility certification. Screenshot review prompted bounded monitoring tables, configuration selection and a shorter forecast introduction; these changes preserve complete record access.

## Remaining work

Scientific limitations include the small forecast evaluation sample, revised publication vintage, model interval assumptions, historical monitoring coverage and pending external alert validation. No outstanding frontend test failures remain. The initial geographic loading timeout did not recur in the full run; cold-start and external-service availability remain practical limits rather than evidence of statistical failure. Phase 4 is ready for owner review, not implementation. Publication and S08 chart implementation remain unauthorised. The final local commit contains the refinements, report and screenshots; nothing was pushed or deployed.
