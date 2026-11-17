# Task 08S Phase 1 — Language and presentation guide

Date: 17 November 2026. Proposed editorial rules for owner review. No interface text has been changed. Change IDs and priorities refer to the [structure register](TASK08S_PROPOSED_DASHBOARD_STRUCTURE.md); objective IDs refer to the [coverage matrix](TASK08S_OBJECTIVE_COVERAGE_MATRIX.md).

## Writing principles

Use natural British English: analyse, modelling, standardised and catalogue. Prefer a specific subject and verb: “The chart shows quarterly suspected deaths in Scotland.” Follow with what can reasonably be concluded, then the relevant limitation. Avoid promotional claims and repeated sentence templates.

Do not routinely use “context”, “insights”, “leveraging”, “robust” or “comprehensive”. Use “robust” only where it identifies the actual statistical estimator, with an explanation. Avoid stacked adjectives and unnecessary hyphens. Keep necessary scientific terms such as Negative Binomial, age-standardised rate, EWMA, CUSUM and prediction interval; define them where first needed.

Questions are safer than fixed findings for heavily filtered displays. A finding must describe the loaded evidence, not a hard-coded default selection. Do not invent percentages, totals, risk levels or statistical comparisons to make the page more engaging. (All screens; S01/S11; O1–O5; P1.)

## Preferred wording

Examples are proposed presentation copy, not changes to source labels, scientific definitions, API fields or export values.

| Current term or pattern | Proposed user wording / explanation | Screen, change, objective, priority |
| --- | --- | --- |
| “Latest available” without period | “Latest observation in this dataset: [reporting period]”. Keep period next to value. | Overview, mortality, toxicology; S02/S04/S05; O1/O2/O5; P1 |
| “Frozen analytical resource families” | “Saved research datasets”; explain that their reporting periods differ. Do not call resource families independent sources. | Overview/research; S02/S10/S11; O1/O5; P1 |
| “Historical robust screen” | “Historical median-based screen”; methods: “Compares each observation with the median and median absolute deviation of earlier observations.” Retain original method identifier in technical details. | Monitoring; S07; O3/O5; P1 |
| “Anomaly” used as an incident | “Unusual historical observation” or “statistical flag”. A flag is a method-specific classification, not a confirmed toxicity event. | Monitoring/overview; S02/S07; O3/O5; P1 |
| “Prior-window diagnostics” | “Checks on the earlier observations used by the model”. Retain technical diagnostic names in methods/table labels. | Monitoring; S07; O3/O5; P1 |
| “Distribution adequacy” | “How well the count models describe the recorded values”. This does not mean independently validated prediction or warning performance. | Monitoring; S07; O3/O5; P1 |
| “Statistical runs” | “Consecutive flagged periods”; explain that each group belongs to one series, method and direction. | Monitoring; S07; O3/O5; P1 |
| “Six-setting sensitivity” | “How results change across six settings”. Distinguish parameter sensitivity from alert-detection sensitivity. | Monitoring; S07; O3/O5; P1 |
| Negative Binomial / NB2 | “Negative Binomial count model”; explain extra count variability beyond the Poisson assumption. Distinguish original regression, moments comparator and forecasting trend model. | Monitoring/forecast; S07/S09; O3/O4/O5; P1 |
| EWMA | “Exponentially weighted moving average (EWMA)”; gives more weight to recent residuals. State that the original display concerns stored model statistics, not raw death counts. | Monitoring; S07, optional S08; O3/O5; P1 wording, P2 charts |
| CUSUM | “Cumulative sum (CUSUM)”; tracks accumulated departures from a reference. Keep positive and negative components separate; a reset baseline is not a lower alarm limit. | Monitoring; S07, optional S08; O3/O5; P1 wording, P2 charts |
| “Historical-origin projection” | “Saved estimate for 2026 Q1, based on observations through 2025 Q4”. Add “The target period has elapsed. This is not a current forecast.” | Forecast/overview; S09/S02; O4/O5; P1 |
| MAE / rolling-origin evaluation | “Mean absolute error (MAE): average absolute prediction error, in deaths.” “Each prediction used only the earlier quarters available in this retrospective dataset.” | Forecast; S09; O4/O5; P1 |
| “Paired values” | “Periods with a reported value for both subjects”. Distinguish missing records from unavailable values in returned records. | Comparison; S03; O1/O2/O5; P1 |
| “Allowlisted live database snapshot” | “Read-only database records”. State the observation period separately; connection status does not establish current evidence. | Research; S10/S11; O1/O5; P1 |
| “Refresh API data” | “Refresh data”. Errors: “These results could not be loaded. Try again.” Keep no matching observations and unavailable evidence as distinct states. | All screens; S01/S11; O5; P1 |
| “Verify source records and artifact provenance” | “Sources and analysis details”, then optional “Technical reproducibility details”. | All screens; S11; O1/O5; P1 |

## Model evidence statements

These examples illustrate the length and precision required. They use existing report findings, not a new calculation. They must remain attached to their source/period and must not be rendered when evidence is unavailable.

- **Geography:** “Inverclyde recorded 25 registered drug misuse deaths in 2024. These council figures do not describe Greenock separately.” For the separate rate display: “The published 2020–2024 age-standardised rate was 35.6 per 100,000 in Inverclyde and 22.5 in Scotland.” Display the existing confidence intervals alongside it. Explain that age standardisation allows comparison after accounting for age structure; it does not remove all differences between populations. (S06; O2/O5; P1; [source](../analysis/phase6/outputs/RESEARCH_FINDINGS.md).)
- **Forecast evaluation:** “The last-observation baseline had the lowest average absolute error across the 12 evaluation quarters. The same quarters were used to select and compare the models, so this is not an independent test of the selected model.” (S09; O4/O5; P1; [source](../analysis/PHASE2_RESULTS.md).)
- **Monitoring:** “The original median-based screen recorded 47 historical flags. Repeated observations and overlapping series mean these are not 47 separate incidents.” Do not combine this total with later model counts. (S07/S02; O3/O5; P1; [source](../analysis/phase5/outputs/FINDINGS.md).)
- **Toxicology:** “These counts describe detections in the forensic testing sample. Categories overlap and should not be added. Without the number tested, they cannot show population prevalence.” Use the ASSIST-specific percentage definition instead when that source is selected. (S05; O1/O2/O5; P1.)

Avoid “Scotland's emerging toxicity threat”, “validated early warning”, “real-time surveillance”, “high-risk board”, “no harm detected” or “accurate forecast” as summaries of this evidence. Do not interpret missing official-alert records as no-alert periods. (Overview/monitoring/forecast/geography; S01/S02/S06/S07/S09; O2/O3/O4/O5; P1.)

## Warnings and methods placement

| Placement | Retain | Avoid repeating | Screen/change/objective/priority |
| --- | --- | --- | --- |
| Shared compact status | Historical research; not an operational warning service. Preserve lack of PHS endorsement in an accessible research-status explanation. | Full multi-sentence global disclaimer in every card | All; S01/S11; O5; P1 |
| Next to chart | Measure, unit, source population/boundary, actual reporting period and limitation essential to that display | Repository paths and full technical method narrative | All; S02–S07/S09; O1–O5 as mapped; P1 |
| Mortality source selector | Suspected deaths are provisional and distinct from registered drug misuse deaths | The same distinction in every subordinate table row | Mortality/overview/geography; S02/S04/S06; O1/O2/O5; P1 |
| Toxicology source explanation | Overlap, selected sample, unavailable denominators; ASSIST unequal periods and shortened Q9; treatment-opioid exclusion | Generic causal disclaimer repeated below every view | Toxicology/comparison; S03/S05; O1/O2/O5; P1 |
| Geographic display | Actual boundary; counts versus rates; Greenock evidence gap where local inference is likely; Scotland/Unknown separate from boards | Large unavailable-map card and repeated boundary manifesto | Geography; S06; O1/O2/O5; P1 |
| Forecast display | Origin, cutoff, elapsed target and model interval; no current prediction | Duplicate elapsed-period warning in several paragraphs | Forecast/overview; S09/S02; O4/O5; P1 |
| Monitoring finding | Method and eligible period; retrospective/non-operational meaning | Validation status in every diagnostic block | Monitoring; S07; O3/O5; P1 |
| Methods and sources disclosure | Full assumptions, unresolved baseline discrepancy, correlated comparisons, sparse history, reporting breaks, uncertainty and publication vintage limitations | A second copy of the same disclosure on the page | All; S11 with S04/S05/S06/S07/S09/S10; O1–O5; P1 |

Preserve the naloxone recording-system change from April 2024 as a possible measurement break; its effect is not quantified. Preserve distinctions between source moving averages and analytical representations, rather than silently filling missing values. Group repeated qualifications within one explanation without dropping a unique warning.

## Visual and numerical presentation

Give the question and main evidence the strongest type and space. Coverage counts, record totals and version metadata should use supporting text, not compete with analytical results as large headline cards. Keep the present palette and components initially; typography, spacing and ordering can achieve the proposed hierarchy. Avoid a new design system or decorative imagery. (All; S01–S07/S09–S11; objectives as mapped; P1.)

Use zero-based bars for count ranking, preserve time gaps and retain ASSIST's unequal-period categorical treatment. Explain heatmap intensity as magnitude within that source, not risk. Keep the mortality box plot available as a secondary distribution view; its outliers are not monitoring flags. No chart should be added merely to fill a panel. (Comparison/mortality/toxicology/geography; S03–S06; O2/O5; P1.)

Use British date formats in prose, such as 17 November 2026, and preserve source-specific quarter/week/study labels. Observation cutoff, publication date, analysis execution date and database refresh time are different dates. Never substitute one for another. Use readable rounding for presentation while retaining existing exact table/export values; do not round a count observation into a fractional death. Approximate projected counts may be labelled as estimates. (All; S11 with S02–S07/S09/S10; O1–O5; P1.)

Explain confidence intervals for published rates, model observation/prediction intervals for forecasts and control limits for EWMA/CUSUM separately. Do not rename all three “risk bands”. Use text and shapes as well as colour for unavailable values and flags. Keep chart equivalents in tables and keyboard-accessible disclosures. (Geography/monitoring/forecast and shared presentation; S01/S06/S07/S09; O2/O3/O4/O5; P1; optional chart refinement S08 is P2.)

## Sources, technical detail and exports

Primary source text should identify publisher, measure, period and publication link. Secondary technical access may retain original identifiers, source cells, versions and hashes. Phase names, task IDs, manifest paths, storage types and API-contract strings belong in repository documentation or technical disclosures. This is a presentation separation, not removal from the backend or research files. Do not alter source terminology inside a quoted definition or exported original field. (All; S11; O1/O5; P1.)

Place export scope at the action: “Download this page” for generic paginated and database-snapshot exports; describe the full selected series or complete aligned comparison only where the component actually exports it. Keep filters, units, source identifiers, missing values and limitations in the existing export representation. Repository documentation links must resolve to the actual approved repository location before publication; do not invent a GitHub URL or expose restricted intelligence. (Research/comparison and dedicated series screens; S03/S04/S05/S06/S10/S11; O1/O2/O5; P1.)

## Editorial completion check for the next phase

For each screen, check that its first question matches the lead evidence; the source, period, unit and boundary are clear; interpretations use loaded results; unique warnings survive consolidation; technical detail remains inspectable; and export wording matches actual scope. Read the page aloud for repetitive phrasing. Confirm that none of the copy implies completed RADAR validation, current forecasting, a Greenock estimate or individual-drug detection from broad groups. These checks are proposed implementation acceptance, not work completed in this phase.
