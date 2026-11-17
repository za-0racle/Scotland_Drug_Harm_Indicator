# SDHI Phase 2 — Core analytical dashboard

Date: 17 November 2026. Local implementation of S02–S06, based on Phase 1 commit `6755071`. Implementation and local verification are complete. No push, publication or Phase 3 work is authorised by this report.

## Five screens completed

| Screen / change | Implemented behaviour | Objective coverage |
| --- | --- | --- |
| Study overview — S02 | National mortality chart and two existing, period-labelled mortality values lead. Year controls sit in the chart panel; text distinguishes the selected chart years from full-dataset headline values. Inverclyde registered deaths and existing published rates follow. Heatmap, toxicology/monitoring/forecast details and source inventory are secondary disclosures, with direct links to the analytical screens. | O2 primary; O1/O3/O4/O5 supported through source distinctions, research summaries and navigation |
| Comparison Studio — S03 | Removes the large introductory and unavailable-feature panels. The existing aligned chart precedes exact values and complete CSV export. Subject names identify the selection, while two compact coverage summaries explain shared periods and periods with reported values for both subjects. Compatibility restrictions, original records, missingness and export scope remain intact. | O1/O2/O5 |
| Mortality trends — S04 | Source-specific time series leads; existing latest observation and coverage information use compact supporting text. Heatmap, descriptive distribution and count ranking remain inspectable in disclosures. Quartile/whisker conventions move to methods. Search, pagination, record inspection and matching-series CSV remain available. | O1/O2/O5 |
| Toxicology patterns — S05 | Selected-source history leads, with compact period/category coverage. Forensic, treatment and ASSIST remain active choices. Heatmap, ranking and paired-category table become supporting views; profiles, exact observations and exports remain available. Pending individual-substance and raw-intelligence choices are removed from the selector; their availability is explained in the research screen. | O1/O2/O5 |
| Geographic patterns — S06 | Selected-area chart leads with its source, boundary and period together. Existing published five-year NRS rates and confidence intervals follow as two readable values when applicable; the original exact-value table and source details remain inspectable. Peer ranking, compatible comparison and coverage move to disclosures. One short map-availability note replaces the standalone panel. Profiles and complete selected-history/comparison exports remain available. | O1/O2/O5 |

O1 = official dataset integration; O2 = historical mortality, toxicology and geographic analysis; O3 = statistical monitoring; O4 = retrospective forecasting; O5 = interactive dashboard development/testing. Phase 2 changes the presentation of existing O3/O4 summaries on the overview, not their methods or dedicated screens.

## Evidence and scientific limits

Interpretations identify the loaded source, selection and reporting periods. Where no safe result summary exists, wording explains the question and measurement rather than inventing a directional finding. Existing counts, rates, forecasting results and statistical classifications were not recalculated by new analyses. Shared chart axes use readable unit labels; original fields and values remain in records and exports.

Suspected and registered deaths remain separate. Toxicology categories retain overlap and source exclusions; selected samples do not establish population prevalence. ASSIST retains unequal study windows, unconnected points and its percentage definitions. Inverclyde does not substitute for Greenock. Published five-year age-standardised rates and confidence intervals are imported values, with an explanation of age structure and remaining population differences. NHS-board peers remain the 14 official boards; Scotland and Unknown remain separate. The possible April 2024 naloxone recording break is stated without estimating its effect.

Missing values remain gaps, genuine zeros remain zeros, and failed loads clear the chart. Empty chart space is suppressed when no observed values can be plotted. Exact-value tables are collapsed by default; opening them retains search, pagination, source inspection and downloads. Statistical flags remain retrospective research measurements; no RADAR validation, operational warning, current forecast or PHS endorsement is claimed.

## Files changed

- `src/platform/overview.js`, `comparison-studio.js`, `mortality.js`, `substance.js`, `geography.js`: screen-specific order, compact summaries, explanations and supporting views.
- `src/platform/analytical-layout.js`: small native-disclosure, explanation and display-unit helpers; no framework or package added.
- `src/platform/dashboard.js`: overview lead-panel placement and cleanup across routes; research-source availability note.
- `src/platform/shared.css`: extends the Phase 1 presentation for lead evidence and supporting disclosures.
- Relevant browser specifications, `e2e/supporting-evidence.js` and `e2e/phase2.spec.js`: open supporting views through their controls and verify the five screens with actual data.
- This report and `docs/images/task08s-phase2/`: desktop/mobile analytical screenshots.

Phase 1 metadata, branding assets, navigation, focus behaviour, themes and responsive foundation remain the baseline. Backend, data contracts, research inputs, frozen outputs, model code and dependency manifests are outside this change.

## Verification

| Check | Result |
| --- | --- |
| Focused overview tests | 6 passed |
| Focused comparison tests | 13 passed |
| Focused mortality and adapter tests | 15 passed |
| Focused toxicology and adapter tests | 18 passed |
| Focused geography tests | 13 passed |
| Full frontend unit suite | 110 passed |
| Production build | Passed; 37 modules transformed |
| Full browser regression suite | 45 passed in the final full 49-case run; four overview/presentation cases encountered a Supabase read failure. All four passed on the targeted retry. All 49 cases verified across these runs; not a single uninterrupted 49-pass run |
| Desktop/mobile analytical screenshots | Ten actual captures reviewed, covering lead charts, controls, explanations and supporting disclosures at 1440 and 390 pixels; tablet and 320-pixel shell checks also passed |
| Protected-tree and Phase 1 asset comparison | Unchanged against `6755071`: research/backend/Supabase trees, contracts, metadata, branding, shared navigation/chart implementation, dependencies and original Phase 1 screenshots |

Focused counts overlap the full unit suite and must not be added to it. Browser checks use real configured data; intercepted empty/error/malformed responses are explicit test-only cases. An initial focused run was interrupted after an obsolete pending-source assertion and a development-server module-cache disruption during editing. The first complete run passed 48 of 49 checks and identified the geographic period label's placement outside the chart panel. That label was moved into the panel. Mobile screenshot review also prompted default-collapsed exact-value tables. The final run used the finished sources. Its four transient Supabase failures passed on retry; no application fallback or backend change was introduced. No browser errors were recorded in the final five-screen capture checks. Sampled shared text contrast exceeded 4.5:1; this is not an accessibility certification.

## Screenshots

| Screen | Desktop | Mobile |
| --- | --- | --- |
| Study overview | [Desktop](images/task08s-phase2/overview-desktop.png) | [Mobile](images/task08s-phase2/overview-mobile.png) |
| Comparison Studio | [Desktop](images/task08s-phase2/comparison-desktop.png) | [Mobile](images/task08s-phase2/comparison-mobile.png) |
| Mortality trends | [Desktop](images/task08s-phase2/trends-desktop.png) | [Mobile](images/task08s-phase2/trends-mobile.png) |
| Toxicology patterns | [Desktop](images/task08s-phase2/substance-desktop.png) | [Mobile](images/task08s-phase2/substance-mobile.png) |
| Geographic patterns | [Desktop](images/task08s-phase2/geography-desktop.png) | [Mobile](images/task08s-phase2/geography-mobile.png) |

## Remaining work and publication status

This is a local redesign, not evidence of production analytical recovery. No deployment or external social-preview validation was attempted. Source cutoffs, absent testing denominators, geographic gaps, uncertainty and pending external alert validation remain scientific limitations rather than interface defects. There are no outstanding frontend test failures after the retry. The observed external Supabase read interruption remains a service-availability limitation. Phase 2 is ready for owner review; Phase 3 has not started and must await that review. This work is committed locally, with no push or deployment.
