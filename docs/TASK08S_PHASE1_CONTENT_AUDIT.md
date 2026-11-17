# Task 08S Phase 1 — Dashboard content audit

Date: 17 November 2026. Planning and review only. Application code, API contracts, methods, research data and saved outputs were not changed.

## Basis and limits

This is an inspection of the eight active screen implementations, their related views, source definitions and saved research reports. It is not a new browser acceptance run or live production verification. Layout observations follow the rendered component structure and CSS; exact viewport appearance remains to be checked during an approved implementation. Production recovery remains unconfirmed by this review; see [Task 08Q](TASK08Q_PRODUCTION_ARTIFACT_REPAIR_REPORT.md).

The active entry point is [main.js](../src/main.js), which mounts [platform/dashboard.js](../src/platform/dashboard.js). The older `src/dashboard.js` and archived prototype are not the active eight-screen interface. [shell.js](../src/platform/shell.js) defines eight primary routes and related aliases: `signals`, `methodology`, `exploration` and `compare`. The aliases are included below rather than counted as additional primary screens.

Objective IDs and the limits of the dissertation comparison are in the [coverage matrix](TASK08S_OBJECTIVE_COVERAGE_MATRIX.md). Every recommendation below refers to a prioritised change in the [structure proposal](TASK08S_PROPOSED_DASHBOARD_STRUCTURE.md).

## 1. Intelligence Overview

**Purpose and questions:** orient visitors to the historical evidence and direct them to analysis. O2, with O1/O3/O4/O5 support. What has changed in the saved mortality series? What geographic, toxicology, monitoring and forecasting evidence is available?

**Current content:** latest quarterly suspected deaths; latest complete annual total and existing annual change; mortality coverage and analytical-resource-family cards; quarterly mortality line; year-by-quarter heatmap; Inverclyde count and published age-standardised-rate comparison; latest forensic category list; historical flag/run totals and validation status; saved forecast with interval; resource coverage table; observation table, record/provenance disclosures and route links. Mortality year controls affect the line, heatmap and observations, while headline cards retain full returned coverage.

**Finding to foreground:** the national mortality history should lead, followed by the already documented Inverclyde registered-death/rate comparison. Forecast evaluation and method-dependent flags are research findings, not current threats. Do not promote resource counts as indicators of drug harm.

**Problems and recommendations:** the line and heatmap repeat one series at equal prominence; numerous preview cards dilute the main question. Coverage cards, coverage table and metadata repeat availability detail. “Frozen projection”, “resource families” and “coverage manifests” describe implementation rather than findings. “Latest” needs an adjacent reporting period and cannot imply current conditions. Keep one principal trend and a compact set of existing findings; make the heatmap optional and coverage supporting material (S01/S02, P1). Explain the scope of headline cards beside the year controls. Retain the warning that suspected and registered deaths differ. See [overview.js](../src/platform/overview.js) and [overview-data.js](../src/platform/overview-data.js).

## 2. Comparison Studio

**Purpose and questions:** compare two compatible areas or two categories within a source (O2; O1/O5). How do their recorded values differ over shared reporting periods?

**Current content:** comparison-kind, source, boundary, subject and period controls; apply action; four cards for subjects and shared/paired periods; aligned historical chart; paginated exact-value table with original records; complete aligned CSV export; methods and JSON provenance. ASSIST uses categorical points; calendar series preserve gaps.

**Finding to foreground:** the paired trajectories and whether observations are available for both subjects. A numerical difference alone does not establish population risk, significance or causation.

**Problems and recommendations:** large introduction, definition, subject cards, chart caption and methods repeat compatibility qualifications. Subject names can sit in the legend rather than large cards. “Paired observed values” and “alignment slots” need explanation: both subjects have a reported value, or a reporting period is missing. Put the chart first after a short selection summary, with compact coverage text, controls nearby, exact values and export below (S03, P1). Keep source/boundary restrictions visible and preserve full-comparison export wording. Avoid a second general comparison workflow competing with this screen; review the existing global “Compare Data” drawer for a clear route into this view (S01). See [comparison-studio.js](../src/platform/comparison-studio.js) and [comparison.js](../src/platform/comparison.js).

## 3. Mortality Analytics

**Purpose and questions:** examine suspected quarterly deaths or registered annual deaths separately (O2; O1/O5). How does the selected area's history change, and how does its count compare with compatible peers?

**Current content:** source, boundary, area and year controls; latest value, coverage, valid-count and reporting-basis cards; line chart; quarterly heatmap for suspected deaths; box plot with exact quartiles/whiskers and outliers; geographic count ranking; searchable paginated observations and selected-series CSV; source/method disclosures and record inspection. Related `#exploration` retains generic indicator-series and area-comparison views for other sources.

**Finding to foreground:** the historical trajectory within the selected source. For council analysis, the existing Inverclyde series provides a defensible local-authority case study; counts cannot be assigned to Greenock or interpreted as adjusted risk.

**Problems and recommendations:** record counts and reporting basis occupy headline-card space. The box plot removes time order and is secondary to the line; the full quartile convention dominates its interpretation. Heatmap, line and exact table should have distinct optional roles. Keep the trend prominent; put distribution and technical quartile rules in supporting disclosures, ranking as an optional count comparison and coverage in the caption (S04, P1). Explain suspected versus registered at source selection and “outlier” as a descriptive value, not a signal. Clarify that ranking uses compatible peers and is not restricted to the selected area. Keep the existing minimum-data rule unchanged. See [mortality.js](../src/platform/mortality.js).

## 4. Substance Intelligence

**Purpose and questions:** examine broad-category forensic and treatment detections or ASSIST cohort percentages (O2; O1/O5). Which groups vary within the selected source, and over which periods?

**Current content:** forensic, treatment and ASSIST choices plus unavailable RADAR and pending individual-substance options; source/area/category/period filters; period/category/geography/latest-period/observed-record cards; full-history trend; category-by-period heatmap; selected-period ranking; paired category table; detailed observations/export; category profile drawer; method and provenance sections.

**Finding to foreground:** patterns within a named testing or study sample, using original category definitions. The active API does not support an individual-drug emergence ranking. The local individual-substance report is not current screen content.

**Problems and recommendations:** five administrative cards and repeated missingness/overlap warnings crowd the trend. A large heatmap and ranking should be optional alternatives, not all equally prominent. Pending “Phase 9” and raw-intelligence options offer no analytical result; move their availability explanation to research documentation while retaining supported source choices (S05, P1). Explain detection counts, cohort percentages, missing denominators and unequal ASSIST periods in source-specific short text. Keep treatment opioids' exclusion explicit. Rename to “Toxicology patterns”; avoid implying category rank measures toxicity or mutually exclusive shares. Do not add the local individual-substance outputs under this redesign. See [substance.js](../src/platform/substance.js) and [source definitions](../src/platform/substance-data.js).

## 5. Geographic Explorer

**Purpose and questions:** explore compatible geographic evidence without transferring results between boundaries (O2; O1/O5). What is known about Inverclyde, its peers and wider areas? What is unavailable for Greenock?

**Current content:** boundary/source/indicator/area/period filters; summary cards and area-profile actions; map-unavailable panel; compatible count rankings; selected-area chart and history/export; same-boundary comparison; published geographic rates; coverage table/search; source/provenance disclosures and profile drawer. Sources include mortality, naloxone and testing/study samples, labelled at their actual scope.

**Finding to foreground:** [saved NRS findings](../analysis/phase6/outputs/RESEARCH_FINDINGS.md): Inverclyde had 25 registered drug misuse deaths in 2024. Published 2020–2024 age-standardised rates were 35.6 per 100,000 (95% CI 29.3–41.8) for Inverclyde and 22.5 (21.9–23.1) for Scotland. These are imported five-year rates from the saved vintage, not newly calculated annual rates. Greenock is not separately measured.

**Problems and recommendations:** the standalone map-availability panel consumes chart-sized space without analytical content. Boundary warnings recur in the introduction, footer, profile and methods. Coverage tables compete with the selected history. Bring selected-area history and the existing published-rate comparison forward when applicable; reduce map unavailability to one note, coverage to a disclosure, and comparisons to a clear supporting action (S06, P1). Explain age standardisation and the five-year interval beside the rates, and distinguish count ranking from adjusted comparison. NHS-board choices must remain exactly the 14 official boards; Scotland and Unknown remain separate scopes. Do not supply a decorative map. See [geography.js](../src/platform/geography.js) and [geography-data.js](../src/platform/geography-data.js).

## 6. Anomaly Detection & Surveillance Signals

**Purpose and questions:** examine unusual historical observations and monitoring assumptions (O3; O1/O2/O5). Which values were flagged, by which method, and how stable were those classifications?

**Current content:** `#anomalies` tabs for flags, all observations, six-setting sensitivity, distribution adequacy, prior-window diagnostics and Unknown/sparse counts; method/source/geography filters where supported; generic paginated tables and automatic observed-value charts when eligible; per-record and provenance details. Related `#signals` has runs, cross-source evidence, external-validation status, stored database monitoring results and configurations. Stored results/configurations have no specialised EWMA/CUSUM chart in the active platform branch.

**Findings to foreground:** the original median/MAD screen recorded 47 flags across 8,034 observations; these are correlated measurements, not 47 independent incidents. The existing sensitivity report shows dependence on settings. The later comparison found no joint directional supporting signal in its declared compatible pairs; that does not establish absence of harm. Original NB2/EWMA and opioid-share CUSUM should remain visible as distinct adopted-objective work, not be conflated with later count screens. Sources: [original findings](../analysis/phase5/outputs/FINDINGS.md), [later report](../analysis/phase5c/IMPLEMENTATION_REPORT.md), [earlier monitoring evidence](dashboard-phase-1.md).

**Problems and recommendations:** the long navigation label and dual-route tab sets obscure method relationships. Generic tables choose the first eight available fields, so important method/period/eligibility information is not assured prominence. “Robust screen”, “distribution adequacy”, “prior-window” and “runs” need short definitions. Group existing material as “Original NB2, EWMA and CUSUM”, “Additional historical screens” and “Method comparisons”; label tables explicitly, move detailed diagnostics behind methods, and keep one validation-status statement (S07, P1). Explain a run as consecutive flagged periods from one series/method, not repeated confirmed events. Any restoration of original stored-statistic charts is P2 feasibility work using existing values only (S08), not a new model or API change. No alert-performance metric is proposed.

## 7. Forecasting Lab

**Purpose and questions:** present retrospective next-quarter mortality prediction and evaluation (O4; O2/O5). Did fitted models improve on simple baselines in this experiment?

**Current content:** saved historical-origin projection, historical observations, candidate scores and rolling-origin predictions tabs; generic tables, eligible automatic observation/prediction chart, scoped CSV/JSON exports and provenance. The default saved projection is foregrounded; evaluation is another tab. There is no dedicated evaluation chart in this branch.

**Finding to foreground:** [recorded evaluation](../analysis/PHASE2_RESULTS.md) selected the last-observation baseline: MAE 21.58 deaths over 12 common quarterly targets, compared with 25.26 for NB2 trend. All candidates' 95% intervals covered 12/12 outcomes, but the sample is small and intervals wide. Selection used these same targets. The saved 248-death projection from 2025 Q4 to 2026 Q1 is an elapsed-period estimate, not an observation or current forecast.

**Problems and recommendations:** “Lab” suggests model execution; “historical-origin projection” is accurate but difficult as the entry message. Lead with the existing candidate-score table and a short statement about the simple baseline, retain rolling-origin results as supporting evidence, and place the saved projection second with origin, target and interval together (S09, P1). Define MAE as average absolute error in deaths and explain that each prediction used earlier observations only. Distinguish model observation intervals from EWMA/CUSUM control limits and rate confidence intervals. Do not claim reliable calibration from 12/12 coverage.

## 8. Research, Data & Exports

**Purpose and questions:** make methods, sources, limitations and scoped downloads inspectable (O1/O5; O2/O3/O4). What can visitors reproduce and what does an export contain?

**Current content:** report catalogue, Inverclyde research findings, source-quality gaps and read-only database snapshots; related `#methodology` views for methods/limitations, source inventory and external-validation status. Snapshot tables include naloxone activity, geographic registry and source catalogue, with paging and current-page CSV. Report/source metadata is rendered in generic readable cards, with technical JSON in disclosures.

**Finding to foreground:** the evidence can be traced to named publications and reporting periods. Database snapshots and saved analytical results are distinct representations; notably their moving-average missingness differs. A live connection does not make observations current.

**Problems and recommendations:** reports are resource catalogue entries, not necessarily opened analytical narratives. Multiple “reports”, “methodology” and “verify” mechanisms make navigation unclear. Terms such as “allowlisted”, “database-v1”, “frozen Phase 4”, resource IDs and checksums are presented alongside source explanations. Start with the adopted aim/objective map, source definitions/cutoffs, methods, limitations and clearly scoped downloads; group database records separately (S10/S11, P1). Describe moving averages as supplied values, retaining their representation difference without claiming recalculation. State export scope per component: generic and snapshot exports are current page; dedicated series and aligned comparisons can export complete selected data. See [database-snapshots.js](../src/platform/database-snapshots.js), [dashboard.js](../src/platform/dashboard.js), [backend metadata](../backend/main.py).

## Public implementation-language audit

This covers active visible copy, record disclosures and API metadata displayed by the frontend. Code comments, archived screens and repository-only reports are not current interface text. GitHub destinations below mean documentation within the repository; no remote repository URL or public availability was assumed.

| Category and current location | Remain visible | Rewrite for visitors | GitHub documentation / technical access | Change, objective, priority |
| --- | --- | --- | --- | --- |
| “Frozen” outputs: overview cards/captions, forecast note, reports and snapshot notes | Observation cutoff, saved analysis status and separate representations | “Saved research results using data through …”; retain explicit elapsed forecast target | Exact preservation procedure and output directories | S02/S09/S10; O1/O4/O5; P1 |
| Internal phases: pending Phase 9 source, snapshot Phase 4 note, versions in disclosures | Whether a source is available and whether two representations differ | “Individual-substance analysis is not available in this dashboard”; factual moving-average difference | Phase chronology, integration prerequisites and version strings | S05/S10/S11; O1/O2/O5; P1 |
| Manifest files: overview “Coverage manifests”, generic provenance, source metadata | Traceability and link to source publication | “Sources and analysis details” | Manifest filenames, output hashes and execution records | S11; all objectives; P1 |
| Development task identifiers | No active main-heading task ID found; returned metadata can expose historical notes | Use scientific topic for user headings | Task reports and regression evidence retain IDs unchanged | S11; O5; P1 |
| Repository resource names: source table, report `resource` entries, records/JSON, geographic IDs | Human source name, measure and actual boundary | Map `model_metrics`, `case_study` and similar keys to descriptive titles in presentation only | Stable IDs remain in technical records/exports for reproducibility | S02/S07/S10/S11; O1/O3/O5; P1 |
| Implementation notes: “Refresh API data”, backend/schema errors, “allowlisted”, storage/contract strings and raw JSON | Loading, unavailable, empty and failed states; retry action | “Refresh data”; “These results could not be loaded. Try again.” A separate no-matching-data message must remain distinct. | Backend paths, contract versions, diagnostics and architecture; retain technical disclosure when useful | S01/S11; O1/O5; P1 |
| Source hashes, original row/cell locators and versions | Publication, period, unit, source-specific limitations | Offer “Source and analysis details” first | Full technical provenance can remain available through a secondary disclosure and repository docs | S11; O1/O5; P1 |

Moving detail out of the main reading path must not strip metadata from backend responses, exports or integrity checks. No manifest, frozen file, research dependency or API field should be deleted or renamed for cosmetic reasons. Sensitive raw intelligence must not be exposed through a new documentation link.

## Overall judgement

The smallest useful change is an editorial and ordering pass over the existing components: one clear question, one lead display, a brief evidence statement and accessible supporting material. Preserve the eight-screen structure, existing scientific displays and safeguards. The [proposal register](TASK08S_PROPOSED_DASHBOARD_STRUCTURE.md) contains the reviewable scope; original-method chart work is explicitly optional and separate.
