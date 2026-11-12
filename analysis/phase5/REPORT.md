# Phase 5 implementation report — 10 November 2026

Phase 5 is implemented and executed locally. No later phase is started. The web interface, database, permissions, dissertation, frozen datasets, historical NB2-EWMA/CUSUM and saved Phase 2/3/4 outputs were not changed. No network acquisition, private RADAR narrative analysis, model retraining, migration, publication or deployment occurred. Existing unrelated working-tree changes remain intact.

## Methods and actual classifications

The implemented method is a prior-only robust count screen, with median centre, MAD scale and a count-scale floor. Complete exact-period history is required; no interpolation or suppression substitution is allowed. Primary windows are 16 quarters for mortality/forensic counts, 18 months for treatment and 104 weeks for naloxone. Sensitivity compares two windows and three threshold multipliers per eligible dataset. The floor and thresholds are transparent pragmatic research choices, not calibrated probabilistic control limits. Full formulas and assumptions are in `README.md` and the saved configuration file.

| Dataset | Observations | Eligible | Primary flags | Insufficient | Unavailable |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mortality quarters | 504 | 256 | 3 | 240 | 8 |
| Forensic detections | 210 | 98 | 11 | 112 | 0 |
| Treatment detections | 140 | 50 | 0 | 90 | 0 |
| Weekly naloxone | 7,024 | 5,360 | 33 | 1,664 | 0 |
| ASSIST percentages | 72 | 0 | Not estimated | 72 | 0 |
| Frozen forensic shares | 84 | 0 | Not estimated | 84 | 0 |
| Total | 8,034 | 5,764 | 47 | 2,262 | 8 |

Eligible includes flagged and unflagged screens. Of those eligible, 5,717 had no detected anomaly. The 47 flags are historical statistically unusual observations under the specified screen; they are neither confirmed alerts nor validated emerging threats. Neither the national mortality series nor the national naloxone series exceeded the primary screen. This does not invalidate or replace any original NB2-EWMA/CUSUM result: these are different methods.

All three mortality flags, with original division geography:

| Police division | Quarter | Count | Prior median | Screen bounds | Direction |
| --- | --- | ---: | ---: | --- | --- |
| E: Edinburgh City | 2023 Q1 | 46 | 23 | 7.433–38.567 | Increase |
| G: Greater Glasgow | 2022 Q1 | 50 | 84 | 52.865–115.135 | Decrease |
| K: Renfrewshire and Inverclyde | 2022 Q2 | 7 | 21 | 7.252–34.748 | Decrease |

These are police divisions, not councils or Greenock-specific findings.

All 11 forensic flags refer to detections in the Scotland forensic testing sample:

| Substance | Period(s) | Count(s), in matching order | Direction |
| --- | --- | --- | --- |
| Dissociatives | 2023 Q1; 2023 Q3; 2024 Q1 | 22; 40; 27 | Increase |
| Prescribable Benzodiazepines | 2022 Q4; 2023 Q2 | 290; 286 | Increase |
| Stimulants | 2023 Q2 | 250 | Increase |
| Street Benzodiazepines | 2024 Q4; 2025 Q1; 2025 Q2; 2025 Q3 | 117; 104; 98; 91 | Decrease |
| Opioids | 2026 Q1 | 328 | Decrease |

The opioid count of 328 is below the screen's lower bound 337.201, against a prior median 439.5. Counts have unknown testing exposure; these are not prevalence, causal-death or toxicity-severity estimates. The descriptive 2026 Q1 street-benzodiazepine increase reported in Phase 4 does **not** become a primary statistical anomaly here.

Naloxone flags comprise 27 board-specific observations and six `Unknown` geography observations, spanning weeks beginning 6 January 2020 to 6 April 2026. For example, NHS Lanarkshire has 21 incidents in the week beginning 9 March 2026, compared with a prior median 7 and an upper screen bound 15.896. The two 2026 Unknown-geography flags are seven incidents on 23 February and four on 6 April, with a prior median zero and upper bound three. Unknown geography must not be interpreted as a local hotspot. Every one of the 33 exact weeks/areas, original values and bounds is listed in `outputs/anomaly_results.csv`; there is no direct overdose-incidence inference.

## Evidence and methodological stability

There are 47 `single_indicator_signal`, 5,717 `no_detected_signal` and 2,270 `insufficient_evidence` historical assessments. No compatible multi-source supporting or conflicting assessment is established. Exact geographies, periods and measurement definitions differ; no cross-boundary aliases, sample-to-population joins or ASSIST calendar reassignment were invented. The evidence engine can represent multiple supporting/conflicting indicators when compatible inputs exist, and those branches are tested, but these saved inputs do not establish them. Lack of corroboration is not evidence that harm is absent.

Every current assessment remains `insufficient_evidence`. Mortality ends December 2025, forensic/treatment March 2026, naloxone May 2026 and shares December 2024. ASSIST ends at source-labelled Q15 Feb–May 2026 without exact dates. Most publication dates and as-published vintages are unknown. RADAR intelligence is recorded as unavailable context pending privacy review and compatible period mapping; no narratives are exposed. Published alerts, RADAR intelligence reports and model-generated statistical flags remain distinct.

Of the 47 primary flags, **17 persist in the same direction across all six choices; 30 are choice-sensitive**. Across all 7,878 count observations, 198 are choice-sensitive, 17 consistently flag, 6,495 have no flag among eligible choices and 1,168 have no eligible choice. The 198 include observations flagged only by an alternative setting; this is not the number of primary flags. Thirteen primary flags use the count-scale floor, indicating sensitivity to low or flat reference counts. Missing/suppressed or short windows are excluded rather than counted as agreement. Per-indicator/geography/window/threshold signal frequencies, eligible denominators and floor usage are saved separately.

Observed flag frequency is not a false-positive rate. No complete reference-event dataset supports validated sensitivity, specificity or lead time. No null simulation or operational false-alarm calibration was performed. Seasonality, trends, serial correlation, overlapping windows, repeated comparisons, changing testing volume and source revisions remain unresolved. Treat persistent flags as research priorities for source/method review, not confirmed health warnings.

## Exact files created

No pre-existing file was edited during this phase.

- `analysis/phase5/__init__.py`
- `analysis/phase5/monitoring.py`
- `analysis/phase5/run.py`
- `analysis/phase5/README.md`
- `analysis/phase5/REPORT.md`
- `analysis/tests/test_phase5.py`
- `analysis/phase5/outputs/anomaly_results.csv`
- `analysis/phase5/outputs/monitoring_configurations.json`
- `analysis/phase5/outputs/evidence_assessments.json`
- `analysis/phase5/outputs/sensitivity_results.csv`
- `analysis/phase5/outputs/signal_frequencies.json`
- `analysis/phase5/outputs/quality_report.json`
- `analysis/phase5/outputs/source_provenance.json`
- `analysis/phase5/outputs/FINDINGS.md`
- `analysis/phase5/outputs/run_manifest.json`

Test scratch artifacts are under the existing ignored `analysis/test_scratch.local/`. The execution manifest hashes 44 protected research artifacts and all eight non-manifest Phase 5 outputs. The Phase 2 audit also verifies its recorded input/code/output hashes; Phase 4 sources/code/outputs are checked against their saved manifest. Before/after protected hashes agree.

## Verification and next decision

Commands:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase5.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
git diff --check
```

New tests cover prior-only windows and future invariance, exact thresholds/directions/zero floors/MAD, short/missing/suppressed history, invalid/duplicate counts, geographic/measurement separation, unsupported percentages, reporting-period compatibility, evidence classes, historical/current distinction, sensitivity denominators and repeated-run byte reproducibility. Existing tests additionally reproduce Phase 2 and Phase 4 outputs.

Actual results: **61 passed in 129.17 seconds**, including all 45 existing tests and 16 Phase 5 tests. The focused Phase 5 suite separately passed all 16 tests in 26.81 seconds. Non-timestamped Phase 5 artifacts reproduced byte-for-byte in two scratch runs. `git diff --check` passed; Git emitted only pre-existing working-tree line-ending notices. JavaScript tests/build were not rerun because no application or dependency file changed in this Python-only phase.

The next recommended step is a separately approved scientific review and source harmonisation: obtain verified publication vintages, testing denominators and compatible event definitions; examine seasonality/trend and low-count alternatives; review the 17 persistent observations against contextual evidence. Phase 6, geographic dashboard development, database publication and UI integration remain pending separate approval. Stop after Phase 5.
