import json
from dataclasses import asdict

import numpy as np
import pytest

from analysis.backtesting import evaluate, metrics, rank_models
from analysis.data import integer, load_verified, validate
from analysis.models import ModelFailure, forecast
from analysis.run import run


def observations(n=36):
    return [dict(year=2017 + i // 4, quarter=i % 4 + 1, suspected_deaths=200 + 3 * i + (i % 4) * 2) for i in range(n)]


def test_source_workbook_matches_frozen_series():
    rows, metadata = load_verified()
    assert len(rows) == 36
    assert rows[0] == dict(year=2017, quarter=1, suspected_deaths=222)
    assert rows[-1] == dict(year=2025, quarter=4, suspected_deaths=248)
    assert metadata['data_cutoff'] == '2025 Q4'
    assert len(metadata['sources']) == 2


def test_input_paths_are_repository_relative_not_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows, _ = load_verified()
    assert len(rows) == 36


@pytest.mark.parametrize('bad, message', [
    ([], 'empty'),
    (observations() + [observations()[-1]], 'Duplicate'),
    (list(reversed(observations())), 'chronological'),
    (observations()[:5] + observations()[6:], 'Missing'),
])
def test_bad_series_rejected(bad, message):
    with pytest.raises(ValueError, match=message):
        validate(bad)


@pytest.mark.parametrize('value', [None, True, -1, float('nan'), 222.5, '222'])
def test_non_integer_or_negative_counts_rejected(value):
    rows = observations()
    rows[0]['suspected_deaths'] = value
    with pytest.raises(ValueError):
        validate(rows)


@pytest.mark.parametrize('value', [True, 222.5, None, '222.5', 'NA', ''])
def test_no_silent_input_coercion(value):
    with pytest.raises(ValueError):
        integer(value)


def test_naive_and_seasonal_naive_correct():
    history = [200, 210, 220, 230, 240, 250, 260, 270]
    assert forecast('naive', history).predicted == 270
    assert forecast('seasonal_naive', history).predicted == 240


def test_expanding_origins_alignment_and_training_only():
    rows = observations()
    calls = []

    def spy(model, training):
        calls.append(tuple(training))
        return forecast('naive', training)

    predictions, _ = evaluate(rows, models=('naive',), predictor=spy)
    assert len(predictions) == 12
    assert predictions[0]['origin'] == '2022 Q4'
    assert predictions[0]['target'] == '2023 Q1'
    assert predictions[-1]['origin'] == '2025 Q3'
    assert predictions[-1]['target'] == '2025 Q4'
    for i, training in enumerate(calls, 24):
        assert training == tuple(row['suspected_deaths'] for row in rows[:i])
        assert predictions[i - 24]['training_count'] == i


def test_future_values_do_not_change_earlier_forecasts_or_scales():
    rows = observations()
    before, _ = evaluate(rows, models=('naive', 'seasonal_naive', 'ses'))
    rows[30]['suspected_deaths'] += 1000
    after, _ = evaluate(rows, models=('naive', 'seasonal_naive', 'ses'))
    for a, b in zip(before[:21], after[:21]):  # Includes the prediction for the changed target.
        for key in ('predicted', 'lower95', 'upper95', 'mase_scale', 'training_count'):
            assert a[key] == b[key]


@pytest.mark.parametrize('model', ['naive', 'seasonal_naive', 'ses', 'nb2_trend'])
def test_prediction_intervals_finite_nonnegative_and_nested(model):
    rows, _ = load_verified()
    result = forecast(model, [row['suspected_deaths'] for row in rows])
    assert all(np.isfinite(asdict(result)[key]) for key in ('predicted', 'lower80', 'upper80', 'lower95', 'upper95'))
    assert 0 <= result.lower95 <= result.lower80 <= result.upper80 <= result.upper95
    assert result.predicted >= 0


def test_failures_are_recorded_and_incomplete_models_cannot_win():
    def failing(model, training):
        if model == 'ses':
            raise ModelFailure('Deliberate fitting failure', ['Optimizer diagnostic'])
        return forecast(model, training)
    predictions, diagnostics = evaluate(observations(), models=('naive', 'ses'), predictor=failing)
    evaluation = metrics(predictions, models=('naive', 'ses'))
    assert len(evaluation[1]['failed_origins']) == 12
    assert not evaluation[1]['eligible_for_selection']
    assert rank_models(evaluation)[0]['model'] == 'naive'
    assert any(row.get('warnings') == ['Optimizer diagnostic'] for row in diagnostics)


def test_nb2_nonconvergence_is_a_failure(monkeypatch):
    class BadFit:
        mle_retvals = {'converged': False}
    monkeypatch.setattr('analysis.models.NegativeBinomial.fit', lambda *a, **kw: BadFit())
    with pytest.raises(ModelFailure, match='did not converge'):
        forecast('nb2_trend', [200] * 24)


def test_zero_scaling_denominator_is_not_fabricated():
    rows = observations()
    for row in rows:
        row['suspected_deaths'] = 200
    predictions, _ = evaluate(rows, models=('naive',))
    result = metrics(predictions, models=('naive',))[0]
    assert result['mase'] is None
    assert result['rmsse'] is None
    assert result['scaled_origins'] == 0


def test_metrics_and_interval_coverage_are_calculated_from_actual_errors():
    prediction = dict(model='naive', origin='2024 Q4', status='ok', actual=2., predicted=1.,
                      mase_scale=2., rmsse_scale_squared=4., lower80=0., upper80=3., lower95=0., upper95=4.)
    result = metrics([prediction], models=('naive',))[0]
    assert result['mae'] == 1.
    assert result['rmse'] == 1.
    assert result['mase'] == .5
    assert result['rmsse'] == .5
    assert result['coverage80'] == result['coverage95'] == 1.
    assert result['interval_score95'] == 4.


def test_no_successful_models_means_no_selection():
    with pytest.raises(ValueError, match='No model'):
        rank_models([dict(model='nb2_trend', eligible_for_selection=False)])


def test_output_reproducibility_and_elapsed_label(tmp_path):
    timestamp = '2026-11-09T12:00:00+00:00'
    first, second = tmp_path / 'first', tmp_path / 'second'
    result = run(first, timestamp)
    run(second, timestamp)
    assert sorted(p.name for p in first.iterdir()) == sorted(p.name for p in second.iterdir())
    for path in first.iterdir():
        assert path.read_bytes() == (second / path.name).read_bytes(), path.name
    assert result['forecast']['forecast_origin'] == '2025 Q4'
    assert result['forecast']['target_period'] == '2026 Q1'
    assert 'Elapsed-period' in result['forecast']['interpretation']
    manifest = json.loads((first / 'run_manifest.json').read_text())
    assert manifest['newer_data_review']['newer_official_report_available'] is True
    assert len(manifest['output_hashes']) == 8
