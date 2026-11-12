"""Prior-only distribution comparisons; no event validation or model reselection."""
import math
import numpy as np
from scipy.stats import nbinom, poisson

METHODS = ('gamma_poisson', 'nb2_moments', 'seasonal_gamma_poisson', 'trend_poisson')


def diagnostics(values, stride=None):
    y = np.asarray(values, dtype=float)
    if len(y) < 2 or not np.isfinite(y).all() or (y < 0).any() or (y != np.floor(y)).any():
        raise ValueError('At least two valid integer counts required')
    mean, variance = float(y.mean()), float(y.var(ddof=1))
    corr = lambda lag: float(np.corrcoef(y[:-lag], y[lag:])[0, 1]) if len(y) > lag + 2 and np.std(y[:-lag]) > 0 and np.std(y[lag:]) > 0 else None
    half = len(y) // 2
    return dict(mean=mean, variance=variance, dispersion=variance / mean if mean else None,
                zero_fraction=float(np.mean(y == 0)), poisson_expected_zero=math.exp(-mean),
                lag1_correlation=corr(1), seasonal_lag_correlation=corr(stride) if stride else None,
                half_window_mean_change=float(y[half:].mean() - y[:half].mean()),
                linear_slope=float(np.polyfit(np.arange(len(y)), y, 1)[0]),
                diagnostic_interpretation='Descriptive prior-window checks, not formal zero-inflation/seasonality/break tests')


def distribution(values, method, stride=None):
    y = np.asarray(values, dtype=float)
    diagnostic = diagnostics(y, stride)
    notes = []
    if method == 'seasonal_gamma_poisson':
        if stride not in (4, 12, 52) or len(y) < 4 * stride:
            return None, 'insufficient_data: require four same-season prior observations', diagnostic
        y = y[np.arange(len(y)) % stride == len(y) % stride]
        notes.append('Same-season stratum only; four or more replicates; no between-season borrowing')
    if method in ('gamma_poisson', 'seasonal_gamma_poisson'):
        # Gamma(shape=.5, rate=.5) prior, unit exposure per period; includes rate uncertainty.
        shape, rate = float(y.sum()) + .5, len(y) + .5
        dist = nbinom(shape, rate / (rate + 1))
        notes.append('Gamma(.5,.5) rate prior; posterior predictive rate uncertainty included; assumes constant rate/exposure within stratum')
    elif method == 'nb2_moments':
        mean, variance = float(y.mean()), float(y.var(ddof=1))
        if mean == 0:
            return None, 'insufficient_data: zero mean cannot estimate NB2 dispersion', diagnostic
        if variance <= mean:
            dist = poisson(mean)
            notes.append('NB2 dispersion at zero boundary; Poisson limiting distribution')
        else:
            shape = mean * mean / (variance - mean)
            dist = nbinom(shape, shape / (shape + mean))
            notes.append('NB2 moment estimates; excludes parameter-estimation uncertainty; not trend/season adjusted')
    elif method == 'trend_poisson':
        if len(y) < 16 or y.sum() == 0:
            return None, 'insufficient_data: trend needs 16 periods and nonzero counts', diagnostic
        import statsmodels.api as sm
        import warnings
        x = np.column_stack([np.ones(len(y)), np.arange(len(y)) / len(y)])
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                fit = sm.GLM(y, x, family=sm.families.Poisson()).fit(maxiter=100)
            if caught or not fit.converged:
                return None, 'fit_unavailable: warning or nonconvergence', diagnostic
            mu = float(fit.predict(np.array([[1., 1.]]))[0])
            if not math.isfinite(mu) or mu <= 0:
                return None, 'fit_unavailable: invalid trend mean', diagnostic
            dist = poisson(mu)
            notes.append('Poisson log-linear trend; plug-in mean, excludes coefficient uncertainty; overdispersion invalidates nominal calibration')
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            return None, 'fit_unavailable: ' + type(error).__name__, diagnostic
    else:
        raise ValueError('Unknown method')
    if diagnostic['dispersion'] is not None and diagnostic['dispersion'] > 1.5:
        notes.append('Observed dispersion >1.5: descriptive assumption warning, not a model-selection test')
    return dist, '; '.join(notes), diagnostic


def predict(values, observed, method, stride=None):
    dist, notes, diagnostic = distribution(values, method, stride)
    result = dict(method=method, status='insufficient_data' if dist is None else 'ok', notes=notes, **diagnostic)
    if dist is None:
        return result
    if not math.isfinite(observed) or observed < 0 or int(observed) != observed:
        raise ValueError('Invalid observed count')
    lower95, upper95 = map(float, dist.ppf([.025, .975]))
    lower99, upper99 = map(float, dist.ppf([.005, .995]))
    score = -float(dist.logpmf(observed))
    if not all(math.isfinite(v) for v in (lower95, upper95, lower99, upper99, score, float(dist.mean()))):
        return dict(result, status='fit_unavailable', notes='Non-finite distribution output')
    direction = 'increase' if observed > upper99 else 'decrease' if observed < lower99 else 'none'
    interval_score = upper95 - lower95 + 40 * max(lower95 - observed, 0) + 40 * max(observed - upper95, 0)
    return dict(result, predicted=float(dist.mean()), lower95=lower95, upper95=upper95, lower99=lower99, upper99=upper99,
                covered95=lower95 <= observed <= upper95, covered99=lower99 <= observed <= upper99,
                negative_log_score=score, interval_score95=interval_score,
                direction=direction, signal=direction != 'none', error=observed - float(dist.mean()))
