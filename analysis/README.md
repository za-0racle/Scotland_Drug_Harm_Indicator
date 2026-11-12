# Phase 2: offline national mortality forecasting

This package forecasts **national quarterly Police Scotland suspected drug-death counts**, not individual toxicity, clinical risk, or Greenock outcomes. It is independent of the original NB2-EWMA/CUSUM monitoring script. No Supabase client, database writes, web-interface changes or deployment are part of this package.

## Environment and execution

Tested environment and complete dependency versions are recorded in outputs/run_manifest.json and requirements.txt. Use the project-local environment; do not install into the system interpreter.

From the repository root in PowerShell:

```powershell
python -m venv analysis/.venv
.\analysis\.venv\Scripts\python.exe -m pip install -r analysis/requirements.txt
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests -q
.\analysis\.venv\Scripts\python.exe -m analysis.run
```

On Linux/macOS replace the interpreter path with `analysis/.venv/bin/python`. Modules derive input paths from their source location, not the current working directory. Run the `-m analysis.run` command from the repository root. To preserve separate runs, supply `--output-dir analysis/outputs/<run-name>`; the default output filenames are overwritten on a successful rerun. Dependency pins were resolved and installed in the local environment, then frozen including transitive dependencies.

No network connection is used by the forecasting run. `newer_data_review.json` records a separately performed official-source review, including its date and unresolved harmonisation questions. Refresh that review before making a current prediction; the pipeline does not automatically import newer data.

## Input contract

The frozen JSON supplies exactly 36 ordered quarters, 2017 Q1–2025 Q4. Counts must be nonnegative integers. Duplicate quarters, missing quarters, nonchronological data, invalid labels, booleans, fractional values or changed coverage fail validation. Nothing is imputed, interpolated or silently sorted.

The workbook's national Total row and the explicit year/quarter headers must match all 36 JSON observations. Input paths, source publication URL, outcome, geography and SHA-256 hashes are persisted. `load_verified()` never modifies either input. The original `group3_indicator_computation.py` and all frozen files are preserved.

## Candidate models and uncertainty

1. **Naive:** last observed count. One-step Gaussian observation intervals use the standard deviation of training first differences.
2. **Seasonal naive:** corresponding quarter in the preceding year. Gaussian observation intervals use training lag-four differences.
3. **Simple exponential smoothing:** estimated initial level and smoothing coefficient, fitted only on each training prefix. Gaussian additive one-step observation intervals use residual SSE/(n−2).
4. **NB2 trend:** intercept, scaled linear time trend and estimated dispersion. Optimizer nonconvergence, convergence warnings, invalid parameters or covariance warnings invalidate a fit. Prediction bounds use NB2 observation quantiles (Poisson limit for very small dispersion).

Gaussian lower bounds are clipped at zero; they are approximations for a count outcome, not exact discrete distributions. NB2 bounds include observation variability but exclude parameter-estimation uncertainty. SES intervals likewise use plug-in parameter estimates. Coverage is evaluated, not assumed. A zero residual scale is recorded as a warning. No extra ARIMA candidate is added: the short series does not justify expanding the model search in this phase. No random simulation is used.

## Expanding-window evaluation and selection

The fixed minimum training window is 24 quarters: six annual cycles with 12 common one-quarter-ahead targets, 2023 Q1–2025 Q4. This is a pragmatic protocol, not a universal sample-size guarantee. Origins are 2022 Q4–2025 Q3. Each candidate receives only the training-prefix count tuple, never the target or future covariates. Every target is strictly one quarter after its origin.

Each attempted fit is recorded, including failures and captured warnings. MAE and RMSE are computed on successful origins. MASE uses each origin's training mean absolute lag-four difference; RMSSE uses its training mean squared lag-four difference. Zero scaling denominators yield unavailable scaled scores, not made-up values. The reported MASE averages origin-wise scaled absolute errors; RMSSE is the square root of average origin-wise scaled squared errors.

80% and 95% interval coverage, mean 95% width and the 95% interval score are recorded. For actual y and bounds [l,u], the interval score is `(u-l) + 2/0.05*(l-y)` when y<l, or `(u-l) + 2/0.05*(y-u)` when y>u, and width alone otherwise.

Only models completing every common origin are eligible for selection. Selection uses lowest backtest MAE, then RMSE, then predefined model order for exact ties. Skill against both naive benchmarks is reported only for identical successful-origin sets. If a selected candidate's full-data fit fails, the pipeline records that failure and tries the next eligible backtest-ranked model. It never selects using in-sample fit alone.

**Selection and reported accuracy use the same 12 targets.** There is no independent post-selection test set, no robust estimate of long-term performance, and no clinical/operational validation. Current frozen data may include revisions unavailable at historical origins; this is not an as-published-vintage backtest. A production study needs fresh prospective origins or a genuinely untouched evaluation period.

## Output contract

The default `analysis/outputs/` contains:

| File | Contents |
| --- | --- |
| validated_mortality.csv | Verified year, quarter and national count. |
| rolling_origin_predictions.csv | Every attempted model/origin, target, actual, prediction, interval bounds, scale factors and fit status. |
| model_metrics.json / .csv | Point and interval performance, failures, selection eligibility and benchmark skill. |
| selected_model.json | Ranking, selection rule, minimum training justification and limitations. |
| forecast.json / .csv | Selected full-data one-step projection, interval method/bounds, origin, target, issue timestamp and interpretation. |
| diagnostics.json | Warnings, convergence information, failed origins and final-fit diagnostics. |
| run_manifest.json | Execution timestamp, model version, Python/package versions, source/code/output hashes, data cutoff and newer-source review. |

The projection target is **2026 Q1**, conditioned on the verified 2025 Q4 data cutoff. As of the November 2026 implementation it is an **elapsed-period, data-cutoff-based forecast, not a current future prediction**. Newer official reports exist; no newer observations are fabricated or merged here. No current future-dated forecast is attempted.

The manifest is timestamped. With the same frozen inputs, code, dependency versions and supplied test timestamp, output artifacts are byte-reproducible in this environment. Different BLAS/platform implementations may change optimizer results; exact cross-platform byte identity is not promised. File hashes allow review of changes. Tests exercise reproducibility in temporary directories and do not overwrite the saved analytical run.

## Frozen-analysis discrepancies and next steps

The historical frozen design describes a fixed 2017–2020 baseline and a Poisson sensitivity analysis, while the original script uses rolling 8/12/16-quarter NB2 fits. Those unresolved research-method differences are not repaired by this forecasting phase. Its expanding-window NB2 candidate is a **separate forecasting model**, not a reconstruction or replacement of historical indicator outputs. Forecast intervals are separate from EWMA/CUSUM control limits.

Next: review the saved metrics and interval coverage; harmonise newer official mortality publications and reporting-system changes; preserve publication vintages; evaluate on future unseen origins. Only then propose versioned forecast-run/forecast/evaluation tables and separately reviewed public SELECT policies in Supabase. Keep privileged publication credentials outside the browser, publish only reviewed aggregates, and add forecast-origin/cutoff labels plus prediction bands to the existing dashboard in a later phase. No migration or web changes are included here.
