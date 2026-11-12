# Targeted early-warning feasibility assessment

Assessment date: **10 November 2026**. Scope: read-only inspection of local datasets, Phase 2-6 methods/outputs and official public references. No experiment, model fit, application development, acquisition of new observation data, database change or early-warning success is claimed.

## Decision at a glance

| Capability | Decision | Defensible interpretation |
| --- | --- | --- |
| A. Demonstrate unusual historical patterns under the frozen methods | **GO** | Existing count screens identify historical deviations. Retain direction, eligibility, reference windows and limitations; flags are not confirmed toxicity episodes |
| A. Demonstrate correct identification of an independently documented emerging-harm episode | **CONDITIONAL GO** | Requires compatible event ascertainment and a pre-specified comparison; parameter stability and coincidence are insufficient |
| B. Demonstrate advance warning before an independently verified harm event using then-available information | **NO-GO with current admitted evidence** | Predictor publication vintages, independent event-onset dates and an untouched evaluation design are missing |
| B. Evaluate anticipation of an official communication, rather than harm onset | **CONDITIONAL GO for a future study; not evaluable now** | Reconcile original issues/updates, complete the FOI/completeness review, obtain predictor vintages and freeze a matching protocol |
| C. Identify named chemicals in existing records | **GO for descriptive inventory** | NRS annual workbooks contain individual chemicals; processed monitoring CSVs largely use broad categories |
| C. Demonstrate newly emerging chemical identification from the current dashboard series | **NO-GO** | Broad groups cannot identify a molecule; annual named-substance records do not establish timely discovery |
| C. Analyse historical named-substance involvement after source review | **CONDITIONAL GO** | Requires separately approved extraction, naming/testing crosswalks, sheet-definition review and original vintages |
| Greenock-locality warning or substance-incidence claim | **NO-GO** | No admitted locality outcome/reference series. Council, division or board data cannot substitute |

**The strongest current demonstration is retrospective pattern analysis, not validated advance warning.**

## 1. Available evidence

Primary lineage: `analysis/phase5c/outputs/source_compatibility_registry.json`, `analysis/phase5/outputs/source_provenance.json` and `analysis/phase5c/outputs/source_gap_register.json`. These distinguish observation periods from publication dates. Record counts below are not independent people/events.

| Source / exact path | Observations and specificity | Availability, geography and outcome suitability |
| --- | --- | --- |
| `datasets/Group3_Item2_Data/police_suspected_drug_deaths_Jan2017-Dec2025.xlsx`; Phase 4 `outputs/mortality_quarterly.csv` | 504 quarterly records: 36 per national/13 divisional series, 2017 Q1-2025 Q4; eight suppressed cells. All-drug suspected deaths | Final-vintage publication 17 March 2026; no quarter-specific first-release/revision sequence. Legacy ten-day adjustment and originally suspected-case retention. Harm outcome, not chemical-specific or equivalent to registered deaths |
| `datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv`; Phase 4 `outputs/forensic_counts.csv` | 210 records, 2018 Q4-2026 Q1; seven broad categories: opioids, street/prescribable/all benzodiazepines, stimulants, dissociatives, gabapentinoids | National forensic testing sample. Publication vintages and testing denominators unknown. Presence/detection does not establish chemical causation or population incidence |
| `datasets/Group3_Item2_Data/radar_toxicology_treatment_glasgow.csv`; Phase 4 `outputs/treatment_counts.csv` | 140 monthly records, December 2023-March 2026; five broad groups, with treatment opioids excluded from its opioid category | Selected NHS GG&C urine samples, not national harm ascertainment. Unknown publication dates and testing exposure |
| `datasets/Group3_Item2_Data/radar_toxicology_assist.csv`; Phase 4 `outputs/assist_percentages.csv` | 72 percentages, Q4 May-August 2023 to Q15 February-May 2026; six groups, unequal study periods and shortened Q9 | Participating emergency-department sample. Exact verified dates, sample sizes and publication vintages absent; count screens intentionally unsupported |
| `datasets/Group3_Item2_Data/radar_sas_naloxone_weekly_by_board.csv`; Phase 4 `outputs/naloxone_weekly.csv` | 7,024 records, weeks starting 1 January 2018-25 May 2026; incident counts complete, 32 missing source moving averages | Fourteen boards, Scotland and Unknown. All-drug service activity, not confirmed overdose incidence or a chemical assay. First-availability dates unknown; April 2024 recording rollout is a possible break |
| `g3-indicator/public/data/quarterly_input_table.json`; Phase 4 `outputs/frozen_forensic_shares.csv` | 84 category-share records, 2022 Q1-2024 Q4; original numerator/denominator arithmetic checked | Same forensic lineage, not independent corroboration. Extraction lineage and historical publication timing unresolved |
| `datasets/Group3_Item2_Data/nrs_drd_2024_data.xlsx`, `Table_C1`/`Table_C4`; Phase 6 outputs | Thirty national/Inverclyde annual registered drug misuse death records, 2010-2024; published five-year age-standardised rates | Publication 2 September 2025; council/national scope. Eventual mortality context, not timely local discovery. Annual registered counts, five-year rates and suspected deaths remain separate |
| `datasets/Group3_Item2_Data/nrs_drd_deaths_by_individual_substance.xlsx`, `SUB1a`, `SUB1b`, `SUB2a`, `SUB2b` | National named-substance records: cover 2000-2024; present-only sheets start in 2008. Individual chemicals include BROMAZOLAM, METONITAZENE, PROTONITAZENE and XYLAZINE | Cover publication 2 September 2025. Not integrated into existing monitoring. Implicated/contributing versus present-only and misuse versus wider poisoning are distinct endpoints |
| `datasets/Group3_Item2_Data/nrs_drd_2023_sub1.xlsx`, `SUB1a`/`SUB1b`; `nrs_drd_2023_sub2.xlsx`, `SUB2a`/`SUB2b` | Earlier national chemical edition through 2023; cover publication 20 August 2024 | A second retained vintage is useful for limited revision review; it does not reconstruct pre-January/July-2023 availability |
| `datasets/Group3_Item2_Data/ndrdd_data_tables_2021-2022.xlsx`, `Index`/`Notes` | Deaths registered in 2021/2022, publication 17 March 2026; demographic/service/toxicology context | Delayed aggregate outcome context, not a timely incident stream; may concern the same deaths as NRS/forensic sources |
| `datasets/Group3_Item2_Data/radar_intelligence_reports_all.csv` | Schema/count inspected: 1,581 rows; Number, Date, Region, Area, Reason for Report, Primary drug(s), Appearance, Summary | Date semantics and public availability are unverified; report text is not a chemical assay. An intelligence report marked Alert is not necessarily an official published alert. No private narratives are reproduced or analysed |

Additional local assets were checked at file/header level:

- `datasets/Additional_Group3_Item2_Data/suspected_drug_deaths/table-police-scotland-drug-deaths-police-division-calendar-year-quarter-january-2017-september-2025.xlsx` retains an earlier period ending September 2025. Its filename is not an authenticated publication timestamp; it was not merged with the frozen later series.
- `datasets/Additional_Group3_Item2_Data/Naxolone_Administration_Ambulance_service_Scotland/Naloxone administration incidents by Scottish Ambulance ServiceAll.csv` has the same 7,024-row weekly schema, not an independent second outcome.
- `datasets/Group3_Item2_Data/sas_foi_215-26_naloxone.xls` and the additional-data `foi-215-26-1-1.xls` assets concern **ambulance naloxone FOI material, not the pending PHS historical-alert response**. No binary-XLS contents or availability timeline is asserted from filenames.
- Naloxone programme spreadsheets measure a different programme/service activity; SDMD assessment/population tables do not provide missing urine/forensic testing denominators or chemical-event truth labels.

### Individual chemical records: an important qualification

The local NRS 2024 `SUB1a` sheet contains BROMAZOLAM at row 61, METONITAZENE at row 198 and XYLAZINE at row 303. These locations establish the availability of chemical fields, not a newly extracted analytical series. `SUB1a` includes reported substances before 2008 and implicated/potentially contributing substances from 2008. `SUB1b` concerns substances present but not considered contributory. `SUB2` concerns the broader poisoning definition. Overlapping drugs and naming variants must not be summed as independent deaths or silently merged as synonyms.

The [official NRS 2024 publication](https://www.nrscotland.gov.uk/publications/drug-related-deaths-in-scotland-2024/) confirms its release date and cautions about limited bromazolam testing before 2023 and routine xylazine testing beginning in 2024. First recorded mentions can reflect testing expansion rather than first emergence. A chemical in a retrospectively published annual workbook is not evidence of real-time discovery. The 2024 edition is not the latest publication; no newer outcomes were imported.

## 2. Candidate reference events

Local evidence: `g3-indicator/data/derived/ALERT_LIST_2022_2026.csv` contains six curated rows. `g3-indicator/data/frozen/ALERT_RULE_DECISION.txt` acknowledges incomplete enumeration. `alerts_scraped.csv` records an HTTP 404, not a successful archived collection. Official references below were reviewed on **10 November 2026**; they are not admitted model inputs or immutable historical snapshots.

| Candidate | Definition and dates | Substance / geography / supporting evidence | Independence and development exposure |
| --- | --- | --- | --- |
| Nitazene alert, local ID 2023/04 | Original publication **24 January 2023**; harm-onset date unknown. Later reports describe detections from June 2022, not one independently dated episode | Nitazene group; Scotland dissemination. [PHS version history](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-alert-nitazenes/rapid-action-drug-alerts-and-response-radar-alert-nitazenes-version-20/public-health-alert-for-action-nitazene-type-drugs-in-scotland/) and [April 2023 report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-april-2023/main-points/) verify communication history | Already in frozen benchmark/reviews, not an untouched test event. Two official documents corroborate issuance, not independent clinical ascertainment. All-drug/aggregate opioid screens do not identify nitazenes |
| Bromazolam alert, local ID 2023/13 | Original issue **5 July 2023**; unique clinical event/onset not established | Individual benzodiazepine, Scotland dissemination. [PHS October 2023 report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-october-2023/) verifies issue date | Already in benchmark/reviews. Alert/forensic evidence may share cases; a street-benzodiazepine total cannot identify replacement by bromazolam |
| Xylazine alert, local ID 2024/09 | Issue/public news **9 May 2024**; exact harmful-event onset unknown | Individual substance, Scotland dissemination. [PHS contemporaneous news](https://publichealthscotland.scot/news/2024/may/radar-alert-issued-on-new-synthetic-drug-xylazine/) verifies publication | Already in benchmark/reviews. Laboratory/hospital context is not a complete independently enumerated event set. No admitted xylazine-specific monitoring series |
| Nitazene row labelled 14 July 2026 locally | Do not treat document/update date as a new first issue. Official history gives version 2.0 **12 August 2025**, original issue January 2023, and subsequent page changes | Nitazene group, Scotland; same [official version history](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-alert-nitazenes/rapid-action-drug-alerts-and-response-radar-alert-nitazenes-version-20/public-health-alert-for-action-nitazene-type-drugs-in-scotland/) | Outside original 2022-2024 window but already curated before Phase 5C. Local July row needs document/version reconciliation; it is not automatically independent/new |
| New-benzodiazepines row labelled 14 July 2026 locally | Official version 2.0 **5 February 2026**, last update **14 July 2026**; update date is not proof of new issuance | Multiple benzodiazepines, Scotland. [PHS versioned page](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-alert-new-benzodiazepines-in-scotland/rapid-action-drug-alerts-and-response-radar-alert-new-benzodiazepines-in-scotland/recognising-and-responding-to-an-overdose/) | Previously known locally. A broad-group decline can coexist with emerging chemicals; not a validated upward harm warning or independent episode |
| Medetomidine/xylazine-type row labelled 14 July 2026 locally | Official version 2.0 **5 February 2026**, update **14 July 2026**. PHS describes Scottish WEDINOS detections in September-December 2025, not a complete harm-onset series | Medetomidine with xylazine background; Scotland and specified detection areas. [PHS detections page](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-alert-new-xylazine-type-drug-medetomidine/rapid-action-drug-alerts-and-response-radar-alert-new-xylazine-type-drug-medetomidine/what-are-xylazine-type-drugs/detections/) | Topic already present in local extension list; no admitted medetomidine-specific time series or independently dated harm registry. Descriptions do not authenticate historical data availability |

**Chronology conflicts remain unresolved.** The [April 2024 PHS report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-april-2024/) describes initial xylazine hospital/post-mortem detections in July 2023; later PHS detection summaries describe an earlier quarterly testing context. NRS describes its own routine-testing history. These differ by source, definition and vintage and cannot establish one exact first Scottish harm date. No frozen dates were corrected.

Issue evidence establishes communication existence, not complete no-event coverage, unique incidents, first market availability, chemical causation or dissemination equal to occurrence geography. Multiple publications repeating the same testing/intelligence evidence do not constitute independent case ascertainment.

### FOI status

The latest documented status is **pending**, without an admitted real response dataset: `analysis/phase5c/outputs/foi_staging_specification.json` and `analysis/phase5c/foi.py`. This review did not contact PHS or confirm receipt with the team; no local file does not prove that a response has not arrived elsewhere. The validator's external-metric/publication gates remain closed even for syntactically valid staging input. No alert-based sensitivity, specificity, precision, false-warning rate or lead time is calculated. Missing local alerts never establish no official alert.

## 3. Historical availability and as-of classification

An observation period answers *when a measurement refers to*. Publication/availability time answers *when that particular vintage could be used*. Execution/issue time answers *when a research output was actually produced*. These are separate clocks.

| Source | Classification for this warning assessment | Reason / bounded exception |
| --- | --- | --- |
| Frozen Police quarterly series | **Suitable only for retrospective pattern analysis** | Final 2026 release known, historical first-release/revision sequence missing. A 2022 observation label does not establish availability in 2022 |
| Forensic/treatment/naloxone CSVs | **Suitable only for retrospective pattern analysis** | Observation dates exist, but publication/revision/panel histories do not. Weekly frequency alone does not demonstrate timely availability |
| ASSIST percentages | **Suitable only for retrospective descriptive pattern analysis** | Unequal periods, incomplete exact dates/denominators, no availability history; unsuitable for existing count-model warning targets |
| Frozen shares | **Suitable only for retrospective pattern analysis** | Denominator extraction and release lineage unresolved; not independent outcome evidence |
| NRS 2023/2024 national, substance and council editions | **Suitable only for retrospective pattern/outcome analysis in the current warning study** | Two dated editions allow a limited release-vintage comparison after 20 August 2024 / 2 September 2025, conditional on authenticating original editions. Not a complete pre-event stream. A bounded as-of statement must use publication date, not each observation year |
| Official original-issue/news evidence | **Suitable for retrospective as-of evaluation of communication existence only** | Can establish a documented issue date; current content is not necessarily original content. Not adequate for harm onset or complete event-classification evaluation |
| RADAR intelligence export | **Unsuitable for the proposed independent warning target at present** | Date meaning, public availability, selection and outcome confirmation unverified; reports may have generated the alerts themselves. Future reviewed descriptive use is a different task |
| NDRDD/SDMD/programme aggregates | **Unsuitable for timely alert/onset targets** | Delayed, aggregated or different measurements; contextual use does not establish timely independent event labels |
| SAS binary-XLS FOI assets | **Unsuitable until contents and date semantics are verified** | Existing analytical environment did not parse this binary format; no availability timeline inferred here |

No admitted predictor source currently supports a complete genuinely as-of reconstruction for these 2023-2026 events. There are *some* vintage assets, notably NRS 2023/2024 and the earlier Police workbook, but not enough to infer the full historical release sequence. Checksums establish local reproducibility, not original publication availability or immutable historical webpage content.

`analysis/phase3/official_source_review.json` and `REPORT.md` document later Databelt reporting windows incompatible with the frozen calendar-quarter series and an unacquired raw export. Attributed 13-week/monthly figures are not admitted calendar-quarter observations or a separate forecast test set. No acquisition was retried and no later quarter inferred.

## 4. Frozen methods and parameter-preserving assessment

| Method / exact evidence | What can be examined without changing parameters | Limitation |
| --- | --- | --- |
| Original rolling NB2-EWMA: `analysis/group3_indicator_computation.py`, `group3_indicator_results_recomputed.csv` | Saved 8/12/16-quarter outputs; lambda .20, multiplier 2.962, stored bounds retained | Script has historical `/mnt/data` paths and is not executed. `g3-indicator/data/frozen/PARAMETERS.txt` describes a different fixed 2017-2020 baseline; report the mismatch rather than silently harmonising |
| Original opioid-share CUSUM | Fixed 2022-2023 calibration, 2024 monitoring, K=.5 sigma, H=4.77 sigma | Only four monitoring quarters; broad share, denominator lineage unresolved. Calibration contains both 2023 alert dates, so it cannot provide a pre-2023 independent warning evaluation |
| Phase 5 robust screen: `analysis/phase5/outputs/monitoring_configurations.json` | Prior median/MAD/count floor, k=3, 16-quarter / 18-month / 104-week windows; report existing two-window x three-threshold sensitivity grid | Heuristic, not calibrated tail probabilities. Sparsity, seasonality, dependence and exposure remain limitations. No new threshold selection |
| Phase 5C count comparators: `analysis/phase5c/README.md`, `outputs/enhanced_model_results.csv` | Fixed Gamma-Poisson, NB2 moments, seasonal Gamma-Poisson, trend Poisson and original discrete 99% exceedance/eligibility rules | Different conditional assumptions and denominators; no method promoted because it matches a selected event. Conditional coverage is not event validation |
| Phase 2 forecasting: `analysis/outputs/selected_model.json`, `run_manifest.json`, `forecast.json` | Preserve naive selection and original 12-target 2023 Q1-2025 Q4 expanding evaluation | Same targets selected/reported the model, on revised data. Execution 9 November 2026, elapsed target 2026 Q1: not a pre-outcome issued warning |
| Phase 4 trends / Phase 6 council analysis | Stored exact-period changes, complete means and compatible registered-death comparisons | Descriptive, not warning rules. Fifteen annual Inverclyde counts do not justify forced short-term anomaly detection |

### A misleading apparent precursor

The saved configuration-3 2022 Q3 NB2-EWMA statistic is **-1.16480084**, below lower limit **-0.9873333333**, with `signal_flag=true` (`group3_indicator_results_recomputed.csv`; `docs/dashboard-phase-1.md`). This is a **downward mortality residual**, not evidence of rising nitazene harm. Its nominal observation quarter precedes an alert quarter but does not establish chemical specificity, historical availability or warning utility. The original method is two-sided; relabelling that flag an upward warning would change the scientific interpretation.

### Development exposure and frozen-rule inconsistencies

`g3-indicator/data/frozen/FREEZE_RECORD.txt` dates freezing to October 2026, after the candidate outcomes. A note written before a model run is not a prospectively registered pre-outcome protocol. `PARAMETERS.txt` retains references to five alert quarters/14 intelligence reports, whereas `ALERT_RULE_DECISION.txt` describes three confirmed published alerts and incomplete enumeration. Its assignment of all other quarters to zero is not valid no-alert ascertainment under its acknowledged gaps.

These artifacts are preserved, not repaired. The three historical communications were already explicitly selected for the earlier benchmark and reviewed during development. No evidence establishes an untouched event holdout. Conversely, this does **not** prove numerical parameters were optimised directly against those labels; the supported conclusion is development exposure and uncertain independent protocol status.

## 5. Feasible detection questions and saved results

**GO:** Which historical counts deviate from their own complete prior window under the fixed screen, in which direction, and with what already specified parameter sensitivity?

- Saved Phase 5 labels cover **8,034** observations: **5,764 eligible**, **47 flags** (three mortality, 11 forensic, 33 naloxone), 5,717 no detected anomaly, 2,262 insufficient and eight unavailable. Classification fields were read and counted; no screen was rerun.
- Seventeen observations flag in the same direction across six settings. This is bounded internal robustness, including sparse Unknown-geography cases, not 17 verified incidents. Alternatives also flag observations outside the primary 47; selecting whichever setting flags would add post-hoc selection.
- Phase 5C groups the original flags into **44 statistical runs**, including a four-quarter street-benzodiazepine decline, 2024 Q4-2025 Q3. Repeated quarters and overlapping substance categories are not independent incidents.
- Phase 5C stores **2,256** candidate pairs: 646 contextual, 1,592 incompatible, 18 unresolved. Neither original nor NB2 comparison establishes a joint directional contextual signal in the declared pairs. This is not proof of no harm or independent source corroboration.

Evidence: `analysis/phase5/outputs/anomaly_results.csv`, `sensitivity_results.csv`, `analysis/phase5c/outputs/summary.json`, `cross_source_candidates.json`, `cross_source_evidence.json`, `signal_runs.json`.

**CONDITIONAL GO:** A documented communication can provide a separately labelled contextual timeline for a fixed broad-category pattern. This is not confirmation of a chemical-specific emerging threat. No new matching was calculated here.

**GO, descriptive inventory only:** Inspect named chemical labels and sheet definitions in the NRS workbooks. A later historical involvement analysis is **CONDITIONAL GO** after naming, testing, overlap, structural-break and vintage review. Earliest positive year is neither first Scottish use nor earliest analyst availability.

## 6. Feasible warning targets

The anomaly flags require the **current observed value** as well as a prior-only baseline. They therefore detect an unusual observation after it becomes available; they do not predict that same observation before it occurs. Any advance-warning test must define a genuinely later, separately ascertained endpoint. A prior-only reference calculation alone does not establish advance warning.

No current candidate satisfies all advance-warning requirements:

- **First chemical emergence or harm onset:** exact adjudicated onset and pre-onset predictor vintages are absent. All-drug outcomes and broad toxicology do not identify a molecule.
- **Later independent harm episode:** NRS, NDRDD, Police and forensic records may involve the same deaths. Separate publishers are not proof of measurement independence. No compatible independently adjudicated high-frequency episode set and untouched test period is established.
- **Official alert issuance:** some issue dates are verified, but enumeration, versions, negative periods and predictor availability remain unresolved. This would predict a communication, not onset. The FOI metric hold remains.
- **Next-quarter suspected deaths:** a well-defined numerical forecast target exists, but saved scores are revised-vintage development results. No admitted compatible untouched later outcomes plus prior issuance demonstrate warning performance.

## 7. Evaluation design if evidence becomes available

Freeze a protocol **before** new matching: one target (chemical detection, harm episode, numerical outcome or communication), event definition, ascertainment, source/geography/substance mappings, direction, resolution, matching intervals and independent evaluation period. Keep original method parameters; do not select a method/window because it matches the reference events best.

At each decision time t, use only the predictor **vintage released or accessible by t**, including the entire baseline. Track observation period, receipt/laboratory validation, first publication, revision and research execution/issue separately. A quarter containing an alert cannot be treated as pre-alert information simply because the quarter starts earlier: its full observations and release may follow the alert.

For a before-harm claim require: last necessary predictor availability <= decision time < independently adjudicated onset. Overlapping uncertain date intervals make a comparison non-evaluable. For a communication target, explicitly use original issue time instead. A simulated replay is retrospective; prospective validation requires real contemporaneous issue logs.

Predefine repeated-run clustering, overlapping categories, missing/suppressed observations, updates/withdrawals, ambiguous matches and shared-case dependence. Show exclusions, not only matched positives. Establish scoped no-event ascertainment before denominator-dependent metrics. Do not tune a time window to obtain apparent lead time. Already inspected events can be exploratory illustrations, not newly independent confirmation.

**External-alert metrics remain uncomputed and are not authorised by this assessment.** First receive the FOI response, assess completeness, harmonise and approve a protocol. No sensitivity, specificity, precision, warning false-positive rate or lead-time estimate is produced here. Forecast MAE/coverage concern another task and cannot be relabelled warning performance.

## 8. Missing evidence and scientific risks

Minimum missing inputs: authenticated release vintages/revision histories; chemical testing-panel and exposure denominators; adjudicated event/detection/onset versus issue dates; complete scoped original-alert/update/withdrawal enumeration; compatible boundaries/substances; independently ascertained outcomes and shared-case assessment; negative coverage where required; and an untouched evaluation or actual issue-log design.

Risks include revised-vintage leakage despite prior-observation-only code, ecological attribution, sparsity/count-floor effects, nonstationarity and seasonality, serial dependence, multiple comparisons and winner selection, testing expansion mistaken for emergence, unknown exposure, recording changes mistaken for incidence shifts, broad categories masking chemical replacement, retrospective event definition and circular validation against alerts generated from the same source intelligence/testing.

Reproducible code, hashes and six-setting persistence address internal computational/parameter robustness. They do not establish external validity, causation, population toxicity or operational warning performance.

## 9. Recommended minimum viable experiment

**Stage 1 - GO now, using existing outputs only (not executed as a new experiment here):** lock the Phase 5 primary rule and complete eligible source/period universe. Preserve original observation IDs, dates, directions, bounds, insufficient states and Phase 5C run grouping. Demonstrate the saved street-benzodiazepine decline as a **historical broad-category pattern**, with all original flags and method disagreement available. Place official communication dates in a separately labelled context timeline; do not describe that decline as a successful warning of new chemicals. No new models, threshold changes, alert metrics or invented negative periods.

**Stage 2 - CONDITIONAL GO:** audit one narrow event family, preferably the original bromazolam communication and a specifically defined clinical/detection target if obtainable. Obtain authenticated pre-July-2023 substance-specific vintages, testing histories and FOI issue/update coverage. If only broad totals or subsequently released annual data exist, stop the chemical-warning experiment. An already-known development event can illustrate feasibility, not act as a confirmatory holdout.

**Stage 3 - NO-GO until gates are met:** do not announce warning accuracy or lead time. If suitable independent data later arrive, separately approve a frozen retrospective as-of replay on an untouched period. Keep original parameters and distinguish simulated from actual issuance. A genuinely prospective claim needs a separate future issue-log/outcome study.

The minimum defensible experiment demonstrates what the fixed screen measures and why event prediction is not yet identifiable, rather than manufacturing a success score.

## 10. Verification, preservation and exact changes

Inspected actual registry/provenance/gap/FOI JSON, Phase 2 manifests/selection, Phase 3 source review, Phase 4 observation metadata, Phase 5 configuration/classification/sensitivity fields and scientific review, Phase 5C summary/README, Phase 6 provenance, workbook covers/selected sheets/chemical labels, curated alert CSV/frozen rules and the saved negative EWMA record. Intelligence inspection was limited to schema/count, with no narrative or case-description export.

Read-only classification checks confirmed 8,034 original rows and their counts above. The 7,878 sensitivity rows comprise 17 all-choice persistent, 198 choice-sensitive, 6,495 no eligible-choice signal and 1,168 no eligible setting. These are saved-label checks, not recalibration or external evaluation.

The existing guard validated **85 protected earlier-phase hashes**; Phase 6 input/code/output hashes also matched its unchanged manifest. No model, acquisition script, migration, application build/test, monitoring pipeline or forecasting pipeline was run. A full suite rerun was unnecessary for a documentation-only assessment; no scientific result is claimed from tests.

Exact new deliverable: **`analysis/early_warning_feasibility/FEASIBILITY_REPORT.md` only**. Official web references were reviewed on 10 November 2026, not downloaded as new observation datasets. Frozen alert/date inconsistencies were not overwritten. No application, database, RLS, dissertation, deployment or publication changes. Stop for review.
