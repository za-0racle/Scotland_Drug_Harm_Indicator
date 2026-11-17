# Task 08S Phase 1 — Proposed dashboard structure

Date: 17 November 2026. **Awaiting owner review. Phase 2 must not begin until the owner has reviewed this proposal.** This document proposes changes; none has been implemented.

## Minimum scope

Keep the eight screens, existing routes, chart components, source choices that return data, filters, tables and export contracts. Improve wording, ordering and disclosure rather than rebuilding the frontend. Do not add a score, indicator, model, analysis, data source, decorative chart or inferred map. Existing measures may be foregrounded but must retain their reporting period and definition.

The common reading order is: main finding or question; most useful chart or comparison; short evidence explanation; filters and supporting observations; inspectable methods, limitations and sources. Essential source/area/period controls may sit beside the lead display so visitors can identify and change its scope without searching. This is a visual hierarchy, not a requirement to hide controls below a long chart.

One compact historical-research status remains visible across the application. Source-specific warnings stay next to the chart they qualify. Detailed methods belong in a consistent disclosure; repeating the same disclaimer in every card adds no protection.

## Change register

P1 = minimum content and layout pass for the next phase, after owner review. P2 = optional refinement requiring a separate feasibility decision. Priority does not authorise implementation. Objective IDs refer to the [coverage matrix](TASK08S_OBJECTIVE_COVERAGE_MATRIX.md). The IDs below cover all proposed changes in the four deliverables; examples in the language guide implement these same changes rather than adding scope.

| ID | Screen | Proposed change | Rationale | Objectives | Priority |
| --- | --- | --- | --- | --- | --- |
| S01 | All eight; shared shell | Shorten screen names as below; use one question-led introduction; retain one research-status notice; change “Refresh API data” to “Refresh data”; make global comparison entry clearly lead to the dedicated comparison workflow; consolidate repeated warning text | Reduce navigation and introductory overhead while preserving meaning, state distinctions and access | O5, plus each screen's mapped objective | P1 |
| S02 | Overview | Lead with existing mortality history and existing latest/annual values; place Inverclyde evidence next; use brief links/previews for toxicology, monitoring and forecast evaluation; make heatmap optional and move resource/coverage counts below findings | Findings should carry greater weight than the number of files or records | O1, O2, O3, O4, O5 | P1 |
| S03 | Comparison | Retain aligned chart and table; turn subject/coverage cards into compact labels; bring selection summary, compatible controls and export scope together; consolidate repeated method warnings | Make the actual comparison easier to read without implying adjusted risk or significance | O1, O2, O5 | P1 |
| S04 | Mortality | Keep source-specific trend first; demote coverage/valid-count cards; make heatmap, box plot and count ranking supporting views; put detailed quartile convention in methods | Time change answers the main question; distribution and peer counts answer different secondary questions | O1, O2, O5 | P1 |
| S05 | Toxicology | Lead with selected-source history; make heatmap/ranking/paired table supporting views; condense administrative cards; replace internal pending-source options with a short availability note in research documentation | Avoid implying individual-drug emergence or comparable prevalence from broad groups and selected samples | O1, O2, O5 | P1 |
| S06 | Geography | Show selected-area history first and existing published five-year rate comparison prominently when applicable; reduce map-unavailable panel to one note; disclose coverage; retain boundary-specific selection and separate Scotland/Unknown | Use space for available evidence while preventing geographic substitution | O1, O2, O5 | P1 |
| S07 | Statistical monitoring, including `#signals` | Clearly separate original NB2/EWMA/CUSUM, additional historical screens, method comparisons and validation status; use explicit field labels/order in existing tables; explain flags/runs and eligibility; put diagnostics in supporting methods | Align with O3 and prevent conflation of different methods and denominators | O1, O2, O3, O5 | P1 |
| S08 | Statistical monitoring | Assess reusing the earlier EWMA and separate two-sided CUSUM presentation with existing stored statistics, limits and configurations only | Original-method visual interpretation is weaker in the active platform than in earlier evidence | O3, O5 | P2 |
| S09 | Forecast evaluation | Make the existing candidate-score table the lead display and explain the baseline result; place saved elapsed projection after evaluation; retain rolling-origin detail, uncertainty and export | The study concerns retrospective evaluation; a large elapsed projection can look like a current prediction | O2, O4, O5 | P1 |
| S10 | Research, sources and downloads | Group aim/objective map, sources/cutoffs, methods/limitations and scoped downloads; place database records in a separate secondary view; distinguish snapshot and saved-result representations | Give visitors a scientific route to the evidence rather than a resource catalogue | O1, O2, O3, O4, O5 | P1 |
| S11 | All eight, especially provenance and research views | Use publication names in primary text; place phases/tasks/paths/manifests/contract strings behind technical access or link to repository documentation; retain all fields/files and technical export provenance | Separate research explanation from implementation history without weakening reproducibility | O1, O5; supports O2–O4 | P1 |

S08 is not a commitment to restore charts without checking the stored data contract. If existing fields cannot support an accurate display, document the gap and retain the readable table. Do not add an API endpoint, recompute a statistic or fabricate missing calibration observations within this content redesign.

## Proposed eight-screen reading order

Each row gives the five levels in order. Proposed names are labels only; existing routes and aliases remain stable. Findings must be shown only when the corresponding data have loaded successfully.

| Current → proposed name | 1. Main question or finding | 2. Lead evidence | 3. Brief interpretation | 4. Controls and support | 5. Inspection |
| --- | --- | --- | --- | --- | --- |
| Intelligence Overview → Study overview | What does the saved Scottish evidence show? | Existing national suspected-death trend with period-labelled latest/annual values | Short description of the displayed historical trajectory; no claim of present conditions | Mortality years; existing Inverclyde count/rate evidence; compact links to toxicology, monitoring and evaluation; optional heatmap | Source cutoffs, definitions and research limitations (S01/S02/S11; O1–O5; P1) |
| Comparison Studio → Compare areas and substances | How do the selected subjects compare within this source? | Existing aligned chart | Explain observed differences and gaps without causal or significance claims | Source/subject/period controls beside chart; exact table and complete-alignment export | Compatibility, definitions and original records (S01/S03/S11; O1/O2/O5; P1) |
| Mortality Analytics → Mortality trends | How have deaths changed in the selected reporting area? | Existing source-specific time series | Explain reporting basis and visible change; keep suspected and registered measures separate | Source/area/years; optional heatmap, distribution and count ranking; exact table/export | Source, missingness and descriptive conventions (S01/S04/S11; O1/O2/O5; P1) |
| Substance Intelligence → Toxicology patterns | How do reported detections vary within this sample? | Existing selected-source/category history | Explain what is measured, category overlap and limits of the sample | Source/category/period controls; optional heatmap, ranking and paired table; profiles/export | Denominator, ASSIST timing, testing changes and sources (S01/S05/S11; O1/O2/O5; P1) |
| Geographic Explorer → Geographic patterns | What can be said about this area at its actual boundary? | Existing selected-area history; existing published rate comparison when applicable | Explain counts versus five-year age-standardised rates; no Greenock attribution | Boundary/source/area/period controls; count peers, compatible comparison and profile; coverage disclosure | Boundary definitions, rate intervals, saved vintage and sources (S01/S06/S11; O1/O2/O5; P1) |
| Anomaly Detection & Surveillance Signals → Statistical monitoring | Which historical measurements were unusual under the chosen method? | Clearly labelled existing result table; existing compatible observation plot where available | Explain method-specific flag and insufficient-history states | Method/series/period controls; grouped runs, sensitivity and comparisons; original monitoring results readily accessible | Parameters, diagnostics, original-method discrepancy and one external-validation status (S01/S07/S11; O1/O2/O3/O5; P1). S08 chart refinement is P2. |
| Forecasting Lab → Forecast evaluation | Did fitted models improve on simple next-quarter baselines? | Existing candidate-score table | Last-observation baseline performed best on the 12 shared targets; same targets used for selection and evaluation | Saved projection with origin/elapsed target/interval; historical observations and rolling predictions; scoped exports | Protocol, metric definitions, interval method and lack of independent evaluation (S01/S09/S11; O2/O4/O5; P1) |
| Research, Data & Exports → Research, sources and downloads | What was studied, and how can the evidence be checked? | Aim and objective-to-evidence table; source inventory | Explain dataset differences and what a download represents | Methods, geographic findings and source gaps; downloads; separately labelled database records | Repository research reports and technical reproducibility records (S01/S10/S11; O1–O5; P1) |

Do not prewrite a fixed trend conclusion for every filter combination. Use a question-led title where an existing verified summary is unavailable. Any example numbers in the audit are saved-report evidence, not new constants to put in the interface.

## Smallest implementation sequence after review

1. Apply S01/S11 wording and consistent source/method disclosures, preserving all data and contracts.
2. Reorder existing components through S02–S06 and S09/S10. Do not introduce new statistical summaries.
3. Apply S07 table labels and method grouping. Assess S08 separately; do not allow it to turn the content pass into a monitoring rebuild.

## Review and later acceptance criteria

The owner should review the proposed names, hierarchy, objective mapping and explicit separation of S08 before Phase 2. This phase stops at these four documents.

For a later approved implementation, verify all eight screens using actual returned data. A visitor should be able to identify the question, measure, population/boundary, period and main limitation without opening JSON. Check that filters still affect the stated scope; chart and table values agree; exact values and export provenance remain available; current-page and full-selection downloads remain distinguished; missing, empty and failed states do not become zero; and unavailable data never leave a confident finding visible.

Verify keyboard access, readable mobile flow, visible legends and non-colour missingness/flag cues. Confirm all 14 NHS boards remain selectable without Scotland or Unknown being classified as boards. Check forecast origin/target and interval semantics, separate suspected/registered deaths, and non-operational statistical wording. These are future checks, not results of this document review. No production, accessibility-certification or scientific-validation claim follows from them.
