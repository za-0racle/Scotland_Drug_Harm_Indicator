"""Four small forecasting candidates; intervals are approximate and backtested."""
import warnings
from dataclasses import dataclass, field

import numpy as np
from scipy.stats import norm, nbinom, poisson
from statsmodels.discrete.discrete_model import NegativeBinomial
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

MODELS = ('naive', 'seasonal_naive', 'ses', 'nb2_trend')


class ModelFailure(RuntimeError):
    def __init__(self, message, notes=()):
        super().__init__(message)
        self.notes = list(notes)


@dataclass
class Prediction:
    predicted: float
    lower80: float
    upper80: float
    lower95: float
    upper95: float
    interval_method: str
    diagnostics: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


def normal_prediction(point, scale, method, diagnostics=None):
    if not np.isfinite(point) or point < 0 or not np.isfinite(scale) or scale < 0:
        raise ModelFailure('Non-finite or negative forecast/scale')
    bounds = []
    for level in (.8, .95):
        width = float(norm.ppf((1 + level) / 2) * scale)
        bounds.extend((max(0., float(point) - width), float(point) + width))
    notes = ['Zero residual scale: degenerate intervals; coverage is not assured'] if scale == 0 else []
    return Prediction(float(point), *bounds, method, diagnostics or {}, notes)


def forecast(model, training):
    y = np.asarray(training, dtype=float).copy()
    if len(y) < 8 or not np.all(np.isfinite(y)) or np.any(y < 0) or np.any(y != np.floor(y)):
        raise ModelFailure('At least eight finite, nonnegative integer observations required')
    if model == 'naive':
        return normal_prediction(y[-1], np.std(np.diff(y), ddof=1), 'Gaussian one-step random-walk errors; training differences; lower bound clipped at zero')
    if model == 'seasonal_naive':
        return normal_prediction(y[-4], np.std(y[4:] - y[:-4], ddof=1), 'Gaussian one-step seasonal errors; training lag-4 differences; lower bound clipped at zero')
    if model not in ('ses', 'nb2_trend'):
        raise ModelFailure(f'Unknown model: {model}')

    captured = []
    try:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            if model == 'ses':
                fit = SimpleExpSmoothing(y, initialization_method='estimated').fit(optimized=True)
                optimizer = fit.mle_retvals
                if optimizer is not None and not optimizer.get('success', True):
                    raise ModelFailure('SES optimizer did not converge')
                if any('ConvergenceWarning' in w.category.__name__ for w in captured):
                    raise ModelFailure('SES convergence warning')
                residual_scale = np.sqrt(np.sum(np.asarray(fit.resid) ** 2) / (len(y) - 2))
                result = normal_prediction(float(fit.forecast(1)[0]), residual_scale,
                    'Gaussian additive one-step SES errors; SSE/(n-2); plug-in parameters; lower bound clipped at zero',
                    {'converged': True, 'smoothing_level': float(fit.params['smoothing_level']), 'residual_scale': float(residual_scale)})
            else:
                # Intercept + scaled linear time trend + NB2 dispersion, no seasonality.
                x = np.column_stack((np.ones(len(y)), np.arange(len(y)) / len(y)))
                fit = NegativeBinomial(y, x, loglike_method='nb2').fit(method='bfgs', maxiter=1000, disp=False)
                if not fit.mle_retvals.get('converged', False):
                    raise ModelFailure('NB2 optimizer did not converge')
                if any(w.category.__name__ in ('ConvergenceWarning', 'HessianInversionWarning') for w in captured):
                    raise ModelFailure('NB2 convergence/covariance warning')
                intercept, slope, alpha = map(float, fit.params)
                mu = float(np.exp(intercept + slope))
                if not np.all(np.isfinite([mu, alpha, intercept, slope])) or mu <= 0 or alpha <= 0:
                    raise ModelFailure('Invalid NB2 mean or dispersion')
                dist = nbinom(1 / alpha, 1 / (1 + alpha * mu)) if alpha > 1e-8 else poisson(mu)
                bounds = [float(dist.ppf(q)) for q in (.1, .9, .025, .975)]
                if not np.all(np.isfinite(bounds)):
                    raise ModelFailure('Invalid NB2 prediction bounds')
                result = Prediction(mu, *bounds, 'Plug-in NB2 observation quantiles (Poisson limit at alpha <= 1e-8); parameter uncertainty excluded',
                    {'converged': True, 'intercept': intercept, 'scaled_trend': slope, 'dispersion': alpha})
        result.warnings.extend(f'{w.category.__name__}: {w.message}' for w in captured)
        return result
    except Exception as error:
        notes = [f'{w.category.__name__}: {w.message}' for w in captured]
        raise ModelFailure(str(error), notes) from error
