# Phase 5C — versioned local analytical strengthening

This package adds actual cross-source contextual comparisons, conditional count-model comparisons, statistical run grouping, explicit source/geography contracts and a future FOI JSON staging validator. It preserves all earlier phase outputs and does not change Supabase, its schema/RLS, application files, dissertation or dependencies. No current forecast or operational warning is issued.

## Run

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase5c.run
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q -p no:cacheprovider
```

The default destination is `analysis/phase5c/outputs/`; `--output-dir` accepts a `.local` scratch path. Baseline guards verify Phase 2/4 and original Phase 5 manifest hashes, then compare previous-artifact hashes before/after execution. No previous output directory is a permitted destination. Python modules obtain repository paths from their file locations. Outputs, except the execution timestamp in the manifest, are deterministic. There is no network or database access in the pipeline. Review commands never execute migrations.

## Models and prior-only evaluation

For each original count observation, use exact preceding periods, per indicator/geography. Current and later counts never enter the fit. A missing/suppressed reference invalidates that origin; the current missing value remains unavailable. Annual and week-start-month aggregates are not duplicate monitoring targets. ASSIST/frozen shares remain unsupported for these count models. The original Phase 5 robust results are a benchmark, never recalculated or overwritten.

| Candidate | Reference and distribution | Uncertainty / limitations |
| --- | --- | --- |
| `gamma_poisson` | Same complete primary window as Phase 5: 16 quarters, 18 treatment months, 104 naloxone weeks. Gamma(shape=.5, rate=.5) rate prior, posterior shape=sum(y)+.5 and rate=n+.5; one-step predictive NB(shape, rate/(rate+1)). | Includes rate uncertainty conditional on stationary Poisson counts/unit exposure, but not unmodelled rate variation, testing exposure or reporting changes. This is not NB2 population overdispersion. |
| `nb2_moments` | Prior mean m and sample variance v; NB shape=m²/(v−m), p=shape/(shape+m) if v>m. Poisson(m) limiting case if v≤m; zero mean gives insufficient data. | Explicit count-tail alternative; plug-in parameters exclude estimation uncertainty and are not regression coefficients. No fabricated dispersion at all-zero history. |
| `seasonal_gamma_poisson` | Same-phase prior observations only: 16-quarter reference gives four same-quarter values; 208-week reference gives four 52-week-lag values. Minimum four seasonal replicates; treatment 18-month history cannot meet 48-month requirement. | Four replicates are weak; 52-week phase is approximate and not ISO/calendar-year matching. No trend/season interaction or exposure correction. Posterior rate uncertainty included only within the stratum. |
| `trend_poisson` | Poisson log-linear time GLM on complete quarterly or monthly primary references, at least 16 counts; fit only on prior data. Weekly standalone trend deliberately not applied. Warnings/nonconvergence invalidate a fit. | Plug-in mean excludes coefficient uncertainty. Evaluated as an assumption-sensitive comparator, not endorsed for overdispersed data; diagnostic dispersion warning is retained. |

NB parameterisation: [SciPy negative-binomial documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html). These are conditional observation distributions, not event probabilities. Diagnostic fields include prior mean/variance/dispersion, zero fraction versus stationary-Poisson expected zeros, lag-one and seasonal-lag correlations, half-window mean change and linear slope. These are descriptive checks, not formal zero-inflation, break or seasonality tests. Overdispersion >1.5 produces an assumption warning, not a data-tuned model-selection rule.

Results save equal-tailed discrete 95% and 99% intervals, predictive means, negative log predictive scores, 95% interval scores, coverage and errors. Primary enhanced flags are strict outside-99%-interval observations. Integer quantiles can be conservative or degenerate at zero under sparse models; no zero-floor substitution is introduced. Robust k=3 bounds do not have the same nominal coverage as a conditional 99% count interval; differences in flag counts are not improvements in accuracy.

`model_evaluation_metrics.csv` reports both each model's available origins and the intersection of origins among methods with at least one successful result **within each series**. Listed `common_participants` identify the comparison; absence of an unsupported method is explicit. Seasonal weekly origins start later; available-origin rates must not be compared as if evaluation dates were identical. Common-origin results are still retrospective on one revised vintage, not an external holdout. No model is selected by dramatic signals, coverage proximity or log score. No operational false-positive, sensitivity, specificity or alert lead-time metric is calculated.

## Compatibility and actual integration

`compatibility.py` provides explicit national and GG&C spelling aliases, substance-group mappings, geographic boundary types, exact/contained/partial time decisions, measurement differences, dependence and historical availability. National forensic sampling can give national **context**, not an equivalent population estimate or local attribution. Unknown geography and unmapped/undated categories remain unresolved. Broad all-drug naloxone cannot identify a drug. Treatment opioids excluding treatment opioids are not silently mapped to all opioids.

Candidate families actually evaluated are: national mortality quarters versus overlapping national naloxone weeks and forensic quarters; forensic quarters versus overlapping treatment months and frozen forensic shares; latest forensic groups versus source-labelled final ASSIST periods (explicitly undated). Every pairing retains both observation IDs and every compatibility dimension. A contained/overlapping week is not summed or reassigned as a quarter. Local treatment versus national forensic observations are rejected as geographic matches; frozen shares are rejected as independent evidence of the same testing source. Other possible combinations are outside this declared candidate universe, not proven incompatible globally.

Every candidate is assessed using the two original Phase 5 monitoring states, then independently computed NB2-moments states. Distinct collection processes may still share people/cases. Same-direction flags become `supporting_contextual_signals_not_confirmation`, opposite directions `opposing_contextual_signals_not_causal_conflict`, and incompatible/unresolved pairs `no_compatible_cross_source_evidence`. Missing states and single/no-signal contexts are explicit. Actual data need not produce a supporting pair. No pair establishes no harm, independence, causality or prospective availability.

## Runs, source gaps and geographic readiness

`runs.py` groups only consecutive ordinals with the same dataset, indicator, boundary-labelled geography, period basis, method/configuration and direction. Missing/unflagged periods and direction changes break runs. It preserves observation IDs, endpoints, duration and peak deviation with units. Original robust deviations are scaled scores; count-model deviations are observed minus predictive mean. They must not be compared as identical measures. Runs are statistical observations, never confirmed toxicity incidents.

The source registry and gap register retain denominator/period/lag/sample/dependence limits. Official PHS January 2025 continuity documentation identifies a clinical recording-system rollout from April 2024: [report](https://publichealthscotland.scot/publications/rapid-action-drug-alerts-and-response-radar-quarterly-report/rapid-action-drug-alerts-and-response-radar-quarterly-report-january-2025/), reviewed 10 November 2026. This is a potential naloxone measurement break; source-specific rollout effect is unknown. No blocked dataset download was retried. Local SDMD assessments and NDRDD deaths cannot become missing toxicology denominators.

Geographic contracts distinguish Greenock locality, Inverclyde council, Renfrewshire and Inverclyde police division, NHS GG&C and Scotland. No Greenock series is admitted. Local NRS `Table_C1` has an Inverclyde column of annual registered deaths; it is an **unintegrated asset**, not the suspected-death series. Existing health-board population data do not authorise a police-division rate. Dashboard contracts require precise wider-area labels, measurement, cutoff and missing-local-data states. No geographic dashboard or population rate was implemented.

## Future FOI staging

FOI status is **pending**. No actual alert records are generated by this package. `foi_staging_specification.json` describes a JSON adapter contract; PDF/XLS/email extraction remains a separately reviewed upstream step. Keep original attachments unchanged, preserve their hashes and page/row locators, then map only supplied fields to the contract. Raw uncertain date text belongs in field-specific `missingness_notes`; exact ISO dates remain null when unknown. The validator keeps original submitted records, quarantines ambiguity, detects duplicate versions and unresolved revision parents, checks metadata and never silently infers an official identifier, date, boundary or withdrawal status.

Once actual material exists, a local staging command is available:

```powershell
.\analysis\.venv\Scripts\python.exe -m analysis.phase5c.foi path-to-reviewed-response.json path-to-new-local-staging.json
```

It refuses to overwrite its input or an existing output, saves the input hash and never writes Supabase. Staging may contain restricted descriptions and must not be public. Synthetic records exist only in automated tests, labelled `SYNTHETIC TEST DATA ONLY`. Even structurally valid complete input has `external_validation_eligible=false` and `public_export_approved=false`: receipt, completeness, harmonisation, negative-period ascertainment and a predefined evaluation protocol still require explicit scientific review. Missing records never mean no official alert; internal stability remains distinct from external validation.

## Output and traceability contract

All generated files are under `outputs/`: source registry, candidate/evidence JSONs, enhanced model CSV, metrics CSV, diagnostics CSV, run JSON, robustness CSV, zero-baseline review, source gaps, geographic metadata, FOI specification, official source review, local-asset inventory, observation index, summary and execution manifest. Each model/result links to a stable observation ID, original observed value, source path/hash, reference endpoints, method/window and limits. Candidate/run IDs link through the observation index to source provenance. The manifest records code/supporting hashes, previous-artifact hashes and all output hashes.

Computational tests do not establish scientific or operational validity. Remaining work requires appropriate approval for source-vintage/denominator acquisition, modelling calibration, independent events, later evaluation and eventual dashboard publication. Phase 6, deployment, database/RLS changes and dissertation edits remain outside this implementation.
