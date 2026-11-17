# Task 08S Phase 1 — Objective coverage matrix

Date: 17 November 2026. Status: proposal for owner review; no implementation authorised by this document.

## Adopted scope

The adopted aim supplied by the owner is:

> To develop a data analytics system for examining emerging illicit drug toxicity patterns.

The following identifiers refer to the five adopted objective areas supplied for this review. Their descriptions are not presented as verbatim dissertation quotations.

| ID | Adopted objective area | Evidence and qualification |
| --- | --- | --- |
| O1 | Integration of official Scottish datasets | Source-specific mortality, forensic, treatment, ASSIST, ambulance and geographic observations are served by the research application. Integration does not make their populations, units or periods interchangeable. |
| O2 | Historical mortality, toxicology and geographic analysis | Dedicated descriptive screens and compatible comparisons exist. Broad toxicology groups cannot establish the emergence of individual chemicals. Greenock-specific outcomes are unavailable. |
| O3 | Negative Binomial, EWMA and CUSUM statistical monitoring | Original monitoring results/configurations are retained. The active platform also displays median/MAD screens and count-model comparisons. These are separate analyses. Prominent original EWMA/CUSUM interpretation is a presentation gap. |
| O4 | Retrospective quarterly mortality forecasting and evaluation | Four candidates, 12 common evaluation targets and a saved national projection exist. Selection and scoring use the same targets; there is no independent post-selection test. |
| O5 | Development and testing of an interactive research dashboard | Eight primary screens, filters, comparisons and scoped exports exist, with local software acceptance evidence. This is not evidence of scientific validity, a formal user study or production recovery. |

## Dissertation and earlier formulation review

Reviewed the available `Project Report Chapter 2.docx` by extracting its paragraph text, [Chapter Four implementation evidence](CHAPTER4_IMPLEMENTATION_EVIDENCE.md), [earlier dashboard evidence](dashboard-phase-1.md), the frozen design records and analytical reports below. No Chapter One or approved five-objective wording was found in the available dissertation material. Chapter Two has no explicit aim, objective list or research-question list. A word-for-word comparison with an earlier approved formulation therefore cannot be certified. Obtain that original text when assembling the dissertation; do not invent a superseded quotation or edit the dissertation in this phase.

| Earlier material | Difference from adopted scope or current evidence | Treatment proposed for dashboard/dissertation cross-reference |
| --- | --- | --- |
| Chapter Two, sections 2.1–2.3 | Discusses emerging supply, polydrug harm and intelligence as motivation. Literature statements are not findings from this system. | Keep motivation separate from measured application results. Do not turn historical literature totals into dashboard indicators. |
| Chapter Two, sections 2.3.1–2.3.4 | Distinguishes suspected and registered deaths, overlapping toxicology categories, reporting changes and denominator limitations. | Preserve these distinctions under O1/O2. Do not infer shares from the active forensic counts without a valid denominator. |
| [PARAMETERS.txt](../g3-indicator/data/frozen/PARAMETERS.txt), items 4 and 6 | Earlier design envisages alert-quarter validation and refers to intelligence alert rows. This is a proposed validation design, not completed O3 evaluation. | Describe as earlier intended validation. Never label the intelligence row count as independently confirmed official alerts. |
| [ALERT_RULE_DECISION.txt](../g3-indicator/data/frozen/ALERT_RULE_DECISION.txt) | Distinguishes new published alerts from intelligence reports, records only three confirmed publications in its window, and acknowledges incomplete ascertainment. Its provisional zero quarters cannot establish absence of alerts. | Retain as historical research documentation. Show external validation as pending/unavailable; do not report sensitivity, specificity or lead time. |
| [Forecasting README](../analysis/README.md), frozen design and later implementation | Earlier fixed 2017–2020 baseline description differs from rolling 8/12/16-quarter original NB2 implementation. The expanding-window forecasting NB2 is another model. | Document the unresolved discrepancy in methods; preserve original results. Do not imply one uniform Negative Binomial analysis. |
| [Phase 5 findings](../analysis/phase5/outputs/FINDINGS.md), [analytical strengthening](../analysis/phase5c/README.md) | Median/MAD screens, conditional count models and grouped runs extend the presentation beyond original EWMA/CUSUM. Parameter agreement is not external alert validation. | Label each analysis separately under O3; avoid using later screens as proof that all original monitoring requirements are visibly covered. |
| [Forecast results](../analysis/PHASE2_RESULTS.md), [later evaluation review](../analysis/phase3/REPORT.md) | Retrospective forecasting is implemented. Compatible later outcomes were not acquired for independent evaluation; the 2026 Q1 target has elapsed. | O4 is a retrospective experiment, not current forecasting or prospective validation. |
| [Individual-substance report](../analysis/phase9_emerging_substances/REPORT.md) | Local individual-substance analyses exist but are not integrated into the active API. | No automatic scope expansion under the adopted aim. Integration is outside this content phase and outside the minimum redesign. |

## Screen coverage and research questions

These questions are proposed visitor questions derived from the adopted objectives, not newly approved dissertation research questions. All screens support O5 through interaction; that alone does not establish effectiveness with research users.

| Current screen / route | Primary objectives | Supporting objectives | Visitor question | Coverage judgement and proposed action |
| --- | --- | --- | --- | --- |
| Intelligence Overview / `#overview` | O2 | O1, O3, O4, O5 | What does the saved evidence show, and where should I explore further? | Broad coverage; finding hierarchy weak. S01/S02, P1. |
| Comparison Studio / `#comparison` | O2 | O1, O5 | How do two compatible areas or substance categories differ over the same periods? | Strong descriptive alignment; counts are not adjusted risk. S03, P1. |
| Mortality Analytics / `#trends` | O2 | O1, O5 | How have suspected or registered deaths changed within a defined source and boundary? | Strong descriptive coverage; supporting displays compete with time trend. S04, P1. |
| Substance Intelligence / `#substance` | O2 | O1, O5 | How do reported broad-category detections or cohort percentages vary over time? | Active sources support broad groups only. S05, P1; no individual-substance integration proposed. |
| Geographic Explorer / `#geography` | O2 | O1, O5 | What can be said about Inverclyde and compatible wider areas, and what remains unknown about Greenock? | Counts and published five-year rates exist; unavailable-map panel distracts. S06, P1. |
| Anomaly Detection & Surveillance Signals / `#anomalies`, related `#signals` | O3 | O1, O2, O5 | Which historical observations were unusual under each method, and how dependent are findings on assumptions? | Later screens prominent; original NB2/EWMA/CUSUM stored results are difficult to interpret in generic tables. S07, P1; original-method chart restoration S08, P2, subject to feasibility. |
| Forecasting Lab / `#forecasting` | O4 | O2, O5 | How well did simple and fitted models predict the next quarter in the retrospective experiment? | Evaluation should lead; saved elapsed projection currently leads. S09, P1. |
| Research, Data & Exports / `#reports`, related `#methodology` | O1, O5 | O2, O3, O4 | What do the sources measure, how were results produced, and what exactly can I export? | Useful evidence is mixed with repository and database detail. S10/S11, P1. |

Change IDs, rationale, priorities and screen assignments are defined in the [proposed structure](TASK08S_PROPOSED_DASHBOARD_STRUCTURE.md). P1 is the minimum content pass after owner review; P2 is a separately assessed refinement. Neither authorises implementation now.

## Boundaries of the coverage claim

The aim is supported by a system for examining historical patterns. It does not establish validated early detection of emerging drugs. No prospective warning, causal toxicity score, Greenock estimate, population prevalence from selected samples or PHS endorsement is supported. The [feasibility review](../analysis/early_warning_feasibility/FEASIBILITY_REPORT.md) retains the outstanding event, denominator and publication-vintage requirements. FOI/external validation remains pending in the application contract; receipt and suitability of any later material must be checked separately before changing that wording.
