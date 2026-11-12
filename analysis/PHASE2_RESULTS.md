# Phase 2 measured results — 9 November 2026

Local implementation and run only. The web interface, Supabase data, permissions, migrations, original statistical script and frozen inputs were not changed.

## Validation and protocol

All 36 national quarterly observations, 2017 Q1–2025 Q4, passed integer/nonnegative, uniqueness, chronology and completeness checks. All counts and period headers matched the Police Scotland source workbook. Paths and SHA-256 hashes are in `outputs/run_manifest.json`.

The four candidates were evaluated at 12 identical expanding-window origins, with 24–35 training quarters, targeting 2023 Q1–2025 Q4. All 48 attempted backtest fits succeeded. No fitting warnings were recorded. The selected model's full-data forecast also succeeded. Selection used minimum one-step MAE, not in-sample fit.

| Model | MAE | RMSE | MASE | RMSSE | 80% interval coverage | 95% interval coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Last-observation naive | 21.5833 | 31.2343 | 0.4496 | 0.5462 | 11/12 | 12/12 |
| Seasonal naive | 32.1667 | 38.1510 | 0.6635 | 0.6607 | 12/12 | 12/12 |
| Simple exponential smoothing | 25.9926 | 31.3216 | 0.5378 | 0.5467 | 11/12 | 12/12 |
| NB2 linear trend | 25.2644 | 31.9607 | 0.5228 | 0.5589 | 10/12 | 12/12 |

The naive benchmark won; more complex models did not improve its MAE on these origins. This is an exploratory result, not evidence that naive forecasting will remain superior. All 95% intervals covered all 12 outcomes, but this small sample and their substantial widths do not establish reliable 95% calibration. Full precision, mean interval widths, interval scores, benchmark skill and failed-origin lists are in `outputs/model_metrics.json`.

## Selected projection

- Outcome/geography: national quarterly Police Scotland suspected drug deaths, Scotland total.
- Model: last-observation naive, fitted on all 36 observations.
- Forecast origin/data cutoff: **2025 Q4**.
- Target: **2026 Q1**.
- Point projection: **248** suspected deaths.
- Approximate 80% observation interval: **190.48337947455357–305.5166205254464**.
- Approximate 95% observation interval: **160.0359197607262–335.9640802392738**.
- Method: Gaussian one-step random-walk errors estimated from training first differences, with a nonnegative lower bound. These are model-based approximate observation intervals, not clinical risk bounds or EWMA/CUSUM control limits.

**This is an elapsed-period, data-cutoff-based forecast, not a current future prediction.** It is not an observed 2026 Q1 total. No newer counts were fabricated or imported. A newer PHS RADAR release dated 27 October 2026 was verified separately; its data and reporting-method changes need harmonising before extending this frozen series. See `newer_data_review.json` for official links and the decision not to issue a current future-dated forecast.

## Tests and reproducibility

`analysis/.venv/Scripts/python.exe -m pytest analysis/tests -q`: **31 passed**. Tests cover source matching, portable paths, chronology, completeness, duplicate rejection, invalid numeric values, training-only inputs, perturbation of future observations, benchmark correctness, origin/target alignment, interval ordering, metrics, fitting failures, nonconvergence, undefined scaled scores and byte-identical outputs using a fixed timestamp.

`analysis/.venv/Scripts/python.exe -m pip check`: no broken requirements. The run used Python 3.14.7; exact package pins are in `requirements.txt` and the manifest. Code/source/output hashes are recorded; saved output hashes and MAE/RMSE were independently rechecked from the exported CSV. No web build was required or run for this Python-only phase.

## Exact created and modified paths

Created source/configuration/documentation:

- `analysis/__init__.py`
- `analysis/data.py`
- `analysis/models.py`
- `analysis/backtesting.py`
- `analysis/run.py`
- `analysis/requirements.txt`
- `analysis/newer_data_review.json`
- `analysis/tests/test_forecasting.py`
- `analysis/README.md`
- `analysis/PHASE2_RESULTS.md`

Created saved outputs:

- `analysis/outputs/validated_mortality.csv`
- `analysis/outputs/rolling_origin_predictions.csv`
- `analysis/outputs/model_metrics.json`
- `analysis/outputs/model_metrics.csv`
- `analysis/outputs/selected_model.json`
- `analysis/outputs/forecast.json`
- `analysis/outputs/forecast.csv`
- `analysis/outputs/diagnostics.json`
- `analysis/outputs/run_manifest.json`

Created local environment: `analysis/.venv/` (Git-ignored). Modified `.gitignore` to exclude the local Python environment and caches. Earlier unrelated working-tree changes were left intact.

## Limitations and next integration stage

Only 12 test origins are available, and those origins were also used to select the model. There is no independent post-selection evaluation. The backtest uses the current frozen source vintage rather than archived as-published vintages. Gaussian observation intervals assume stable training errors; NB2's plug-in intervals omit parameter uncertainty. No current future forecast, toxicity-specific prediction, geographic prediction, causal claim, or clinical/operational validation is established.

The fixed-baseline versus rolling-baseline discrepancy in the original frozen monitoring work remains documented, not silently resolved. This engine is a separate expanding-window forecasting experiment and does not alter the historical indicator results.

Next steps: review these outputs; harmonise newer official data and publication vintages; obtain unseen forecast origins; then design separate forecast-run, forecast and evaluation tables for reviewed publication. Any migration, public read policy, privileged publisher credentials and dashboard forecast-band integration require a later explicitly scoped phase. Keep existing monitoring tables and private RADAR narratives separate.
