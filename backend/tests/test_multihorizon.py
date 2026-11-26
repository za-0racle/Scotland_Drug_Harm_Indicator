import numpy as np
import pytest

from analysis.data import load_verified
from analysis.models import MODELS, ModelFailure
from backend.services.multihorizon import evaluate_horizons, horizon_forecast, horizon_metrics


@pytest.mark.parametrize('model', MODELS)
@pytest.mark.parametrize('horizon', [1, 4, 8, 12])
def test_models_generate_finite_nonnegative_multistep_intervals(model, horizon):
    rows, _ = load_verified()
    result = horizon_forecast(model, [row['suspected_deaths'] for row in rows], horizon)
    assert np.isfinite(result.predicted) and result.predicted >= 0
    assert 0 <= result.lower95 <= result.lower80 <= result.upper80 <= result.upper95
    assert result.diagnostics['horizon'] == horizon


def test_direct_horizon_backtest_uses_only_data_available_at_origin():
    rows, _ = load_verified()
    observed_prefixes = []

    # The evaluation helper takes its predictor from the module for straightforward leakage inspection.
    from backend.services import multihorizon
    original_predictor = multihorizon.horizon_forecast
    monkey = pytest.MonkeyPatch()
    def record_prefix(model, training, horizon):
        observed_prefixes.append(tuple(training))
        return original_predictor(model, training, horizon)
    monkey.setattr(multihorizon, 'horizon_forecast', record_prefix)
    try:
        predictions = evaluate_horizons(rows, horizons=(4,), min_train=24, models=('naive',))
    finally:
        monkey.undo()
    assert predictions[0]['origin'] == '2022 Q4'
    assert predictions[0]['target'] == '2023 Q4'
    assert observed_prefixes[0] == tuple(row['suspected_deaths'] for row in rows[:24])
    assert predictions[0]['training_count'] == 24


def test_insufficient_model_input_and_invalid_horizon_fail_clearly():
    with pytest.raises(ModelFailure, match='horizon'):
        horizon_forecast('naive', [1, 2, 3, 4, 5, 6, 7, 8], 13)
    with pytest.raises(ModelFailure, match='eight'):
        horizon_forecast('naive', [1, 2, 3], 4)


def test_horizon_metrics_report_zero_mape_as_unavailable():
    rows = [dict(horizon=4, model='naive', status='ok', actual=0, predicted=1)]
    metric = horizon_metrics(rows, models=('naive',))[0]
    assert metric['mae'] == 1
    assert metric['mape'] is None
