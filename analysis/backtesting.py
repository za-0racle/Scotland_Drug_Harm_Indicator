"""Expanding-window one-step evaluation. Models receive training values only."""
from dataclasses import asdict

import numpy as np

from .data import validate, period
from .models import MODELS, forecast

MIN_TRAIN = 24  # Six annual cycles, leaving 12 common test origins in this dataset.


def evaluate(rows, min_train=MIN_TRAIN, models=MODELS, predictor=forecast):
    validate(rows)
    if min_train < 8 or min_train >= len(rows):
        raise ValueError('Training window must be >=8 and leave at least one test observation')
    predictions, diagnostics = [], []
    for target in range(min_train, len(rows)):
        training = tuple(row['suspected_deaths'] for row in rows[:target])
        history = np.asarray(training, dtype=float)
        scale_mae = float(np.mean(np.abs(history[4:] - history[:-4])))
        scale_mse = float(np.mean((history[4:] - history[:-4]) ** 2))
        origin = rows[target - 1]['year'] * 4 + rows[target - 1]['quarter'] - 1
        for model in models:
            record = dict(model=model, origin=period(origin), target=period(origin + 1), horizon=1,
                          training_count=len(training), actual=rows[target]['suspected_deaths'],
                          mase_scale=scale_mae, rmsse_scale_squared=scale_mse)
            try:
                prediction = predictor(model, training)
                record.update(asdict(prediction))
                record['status'] = 'ok'
                diagnostics.append(dict(model=model, origin=record['origin'], status='ok',
                                        diagnostics=prediction.diagnostics, warnings=prediction.warnings))
            except Exception as error:
                record.update(status='failed', error=str(error))
                diagnostics.append(dict(model=model, origin=record['origin'], status='failed',
                                        error=str(error), warnings=getattr(error, 'notes', [])))
            predictions.append(record)
    return predictions, diagnostics


def interval_score(actual, lower, upper, alpha):
    return upper - lower + 2 / alpha * max(lower - actual, 0) + 2 / alpha * max(actual - upper, 0)


def metrics(predictions, models=MODELS):
    output = []
    for model in models:
        attempted = [row for row in predictions if row['model'] == model]
        valid = [row for row in attempted if row['status'] == 'ok']
        failures = [row['origin'] for row in attempted if row['status'] != 'ok']
        result = dict(model=model, evaluated_origins=len(valid), failed_origins=failures,
                      eligible_for_selection=bool(valid) and not failures,
                      mae=None, rmse=None, mase=None, rmsse=None, coverage80=None, coverage95=None,
                      mean_width95=None, interval_score95=None)
        if valid:
            errors = np.array([row['actual'] - row['predicted'] for row in valid])
            scaled = [abs(row['actual'] - row['predicted']) / row['mase_scale'] for row in valid if row['mase_scale'] > 0]
            squared = [(row['actual'] - row['predicted']) ** 2 / row['rmsse_scale_squared'] for row in valid if row['rmsse_scale_squared'] > 0]
            result.update(mae=float(np.mean(np.abs(errors))), rmse=float(np.sqrt(np.mean(errors ** 2))),
                          mase=float(np.mean(scaled)) if scaled else None,
                          rmsse=float(np.sqrt(np.mean(squared))) if squared else None,
                          scaled_origins=len(scaled),
                          coverage80=sum(row['lower80'] <= row['actual'] <= row['upper80'] for row in valid) / len(valid),
                          coverage95=sum(row['lower95'] <= row['actual'] <= row['upper95'] for row in valid) / len(valid),
                          mean_width95=float(np.mean([row['upper95'] - row['lower95'] for row in valid])),
                          interval_score95=float(np.mean([interval_score(row['actual'], row['lower95'], row['upper95'], .05) for row in valid])))
        output.append(result)
    # A skill comparison is supplied only when the origin sets match exactly.
    for result in output:
        origins = {row['origin'] for row in predictions if row['model'] == result['model'] and row['status'] == 'ok'}
        for benchmark in ('naive', 'seasonal_naive'):
            base = next((row for row in output if row['model'] == benchmark), None)
            base_origins = {row['origin'] for row in predictions if row['model'] == benchmark and row['status'] == 'ok'}
            result[f'mae_skill_vs_{benchmark}'] = 1 - result['mae'] / base['mae'] if base and base['mae'] and result['mae'] is not None and origins == base_origins else None
    return output


def rank_models(evaluation):
    eligible = [row for row in evaluation if row['eligible_for_selection']]
    if not eligible:
        raise ValueError('No model completed all evaluation origins; no model selected')
    return sorted(eligible, key=lambda row: (row['mae'], row['rmse'], MODELS.index(row['model'])))
