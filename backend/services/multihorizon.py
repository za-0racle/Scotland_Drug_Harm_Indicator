"""Multi-quarter research forecasting, kept separate from frozen Phase 2 code."""
from dataclasses import asdict
import warnings

import numpy as np
from scipy.stats import norm, nbinom, poisson
from statsmodels.discrete.discrete_model import NegativeBinomial
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

from analysis.data import period, validate
from analysis.models import MODELS, ModelFailure, Prediction


def horizon_forecast(model, training, horizon):
    if type(horizon) is not int or not 1 <= horizon <= 12:
        raise ModelFailure('Forecast horizon must be an integer from 1 to 12 quarters')
    y = np.asarray(training, dtype=float)
    if len(y) < 8 or not np.all(np.isfinite(y)) or np.any(y < 0) or np.any(y != np.floor(y)):
        raise ModelFailure('At least eight finite, nonnegative integer observations required')
    diagnostics, notes, captured = {}, [], []
    if model == 'naive':
        point = float(y[-1]); scale = float(np.std(np.diff(y), ddof=1) * np.sqrt(horizon))
        method = 'Gaussian random-walk errors; training differences; sqrt(horizon) variance scaling'
    elif model == 'seasonal_naive':
        point = float(y[-4 + (horizon - 1) % 4])
        scale = float(np.std(y[4:] - y[:-4], ddof=1) * np.sqrt((horizon + 3) // 4))
        method = 'Gaussian seasonal errors; training lag-4 differences; annual variance scaling'
    elif model in ('ses', 'nb2_trend'):
        try:
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter('always')
                if model == 'ses':
                    fit = SimpleExpSmoothing(y, initialization_method='estimated').fit(optimized=True)
                    if fit.mle_retvals is not None and not fit.mle_retvals.get('success', True):
                        raise ModelFailure('SES optimizer did not converge')
                    if any('ConvergenceWarning' in warning.category.__name__ for warning in captured):
                        raise ModelFailure('SES convergence warning')
                    residual_scale = float(np.sqrt(np.sum(np.asarray(fit.resid) ** 2) / (len(y) - 2)))
                    point = float(fit.forecast(horizon)[-1]); scale = residual_scale * np.sqrt(horizon)
                    diagnostics = {'converged': True, 'smoothing_level': float(fit.params['smoothing_level']),
                                   'residual_scale': residual_scale, 'horizon': horizon}
                    method = 'Gaussian additive SES errors; SSE/(n-2); sqrt(horizon) variance scaling; plug-in parameters'
                else:
                    x = np.column_stack((np.ones(len(y)), np.arange(len(y)) / len(y)))
                    fit = NegativeBinomial(y, x, loglike_method='nb2').fit(method='bfgs', maxiter=1000, disp=False)
                    if not fit.mle_retvals.get('converged', False):
                        raise ModelFailure('NB2 optimizer did not converge')
                    if any(warning.category.__name__ in ('ConvergenceWarning', 'HessianInversionWarning') for warning in captured):
                        raise ModelFailure('NB2 convergence/covariance warning')
                    intercept, slope, alpha = map(float, fit.params)
                    point = float(np.exp(intercept + slope * (len(y) - 1 + horizon) / len(y)))
                    if not np.all(np.isfinite([point, alpha, intercept, slope])) or point <= 0 or alpha <= 0:
                        raise ModelFailure('Invalid NB2 mean or dispersion')
                    dist = nbinom(1 / alpha, 1 / (1 + alpha * point)) if alpha > 1e-8 else poisson(point)
                    lower80, upper80, lower95, upper95 = [float(dist.ppf(q)) for q in (.1, .9, .025, .975)]
                    if not np.all(np.isfinite([lower80, upper80, lower95, upper95])):
                        raise ModelFailure('Invalid NB2 prediction bounds')
                    notes = [f'{warning.category.__name__}: {warning.message}' for warning in captured]
                    return Prediction(point, max(0., lower80), max(0., upper80), max(0., lower95), max(0., upper95),
                        'Plug-in NB2 observation quantiles; Poisson limit at alpha <= 1e-8; parameter uncertainty excluded',
                        {'converged': True, 'intercept': intercept, 'scaled_trend': slope, 'dispersion': alpha,
                         'forecast_mean': point, 'horizon': horizon}, notes)
                notes = [f'{warning.category.__name__}: {warning.message}' for warning in captured]
        except Exception as error:
            raise ModelFailure(str(error), [f'{warning.category.__name__}: {warning.message}' for warning in captured]) from error
        method += '; lower bound clipped at zero'
    else:
        raise ModelFailure(f'Unknown model: {model}')
    if not np.isfinite(point) or point < 0 or not np.isfinite(scale) or scale < 0:
        raise ModelFailure('Non-finite or negative forecast/scale')
    bounds = []
    for level in (.8, .95):
        width = float(norm.ppf((1 + level) / 2) * scale)
        bounds.extend((max(0., point - width), point + width))
    if scale == 0:
        notes.append('Zero residual scale: degenerate intervals; coverage is not assured')
    diagnostics.update({'horizon': horizon, 'prediction_scale': scale})
    return Prediction(point, *bounds, method, diagnostics, notes)


def evaluate_horizons(rows, horizons=(1, 4, 8, 12), min_train=24, models=MODELS):
    validate(rows)
    if type(min_train) is not int or min_train < 8 or min_train >= len(rows):
        raise ValueError('Training window must be >=8 and leave at least one test observation')
    if not horizons or any(type(h) is not int or not 1 <= h <= 12 for h in horizons):
        raise ValueError('Evaluation horizons must be integers from 1 to 12 quarters')
    if any(model not in MODELS for model in models):
        raise ValueError('Unknown forecast model')
    predictions = []
    for horizon in horizons:
        for target in range(min_train + horizon - 1, len(rows)):
            training = tuple(row['suspected_deaths'] for row in rows[:target - horizon + 1])
            origin = rows[target - horizon]['year'] * 4 + rows[target - horizon]['quarter'] - 1
            for model in models:
                item = dict(model=model, origin=period(origin), target=period(origin + horizon), horizon=horizon,
                            training_count=len(training), actual=rows[target]['suspected_deaths'])
                try:
                    result = horizon_forecast(model, training, horizon)
                    item.update(asdict(result)); item['status'] = 'ok'
                except Exception as error:
                    item.update(status='failed', error=str(error))
                predictions.append(item)
    return predictions


def horizon_metrics(predictions, models=MODELS):
    output = []
    for horizon in sorted({item['horizon'] for item in predictions}):
        for model in models:
            attempted = [item for item in predictions if item['horizon'] == horizon and item['model'] == model]
            valid = [item for item in attempted if item['status'] == 'ok']
            errors = [item['actual'] - item['predicted'] for item in valid]
            actual = [item['actual'] for item in valid]
            output.append(dict(horizon=horizon, model=model, evaluated_origins=len(valid),
                failed_origins=len(attempted)-len(valid), mae=float(np.mean(np.abs(errors))) if errors else None,
                rmse=float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
                bias=float(np.mean(errors)) if errors else None,
                mape=float(np.mean([abs(e)/y for e,y in zip(errors,actual)])*100)
                    if errors and all(y != 0 for y in actual) else None,
                eligible_for_selection=bool(valid) and len(valid) >= 3 and len(valid) == len(attempted)))
    return output
