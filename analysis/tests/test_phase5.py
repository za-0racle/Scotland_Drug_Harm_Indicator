"""Phase 5 tests use synthetic fixtures only for method checks, never published data."""
import csv
import json

import pytest

from analysis.phase5.monitoring import (screen, sensitivity, assess, evidence_class, SIGNAL, NO_SIGNAL,
                                        unsupported, CONFIGURATIONS)
from analysis.phase5.run import run, load, protected_hashes


def row(index, value, **extra):
    return dict(dataset='mortality_quarterly', indicator_id='fixture', source_id='fixture.csv',
                geography='Fixture area', ordinal=index, period=str(index), period_start=str(index),
                period_end=str(index), period_basis='calendar_quarter', unit='count', observed_value=value,
                evidence_domain='fixture', publication_date=None, **extra)


def apply(rows, window=4, threshold=3):
    return screen(rows, window, threshold, 'calendar_quarter')


def test_prior_only_baselines_and_future_invariance():
    rows = [row(i, 10) for i in range(4)] + [row(4, 100)]
    results = apply(rows)
    assert results[-1]['baseline_estimate'] == 10
    assert results[-1]['reference_start'] == '0'
    assert results[-1]['reference_end'] == '3'
    assert results[-1]['classification'] == SIGNAL
    assert apply(rows + [row(5, 999999)])[:5] == results
    changed = apply(rows[:-1] + [row(4, 1)])[-1]
    for field in ('baseline_estimate', 'scale', 'lower_threshold', 'upper_threshold'):
        assert changed[field] == results[-1][field]


def test_exact_thresholds_zero_floor_and_directions():
    # Constant prior count 16 => sqrt floor 4, threshold 3 => [4, 28].
    rows = [row(i, 16) for i in range(4)]
    for value, expected, direction in [(28, NO_SIGNAL, 'none'), (29, SIGNAL, 'increase'),
                                        (4, NO_SIGNAL, 'none'), (3, SIGNAL, 'decrease')]:
        result = apply(rows + [row(4, value)])[-1]
        assert result['lower_threshold'] == 4
        assert result['upper_threshold'] == 28
        assert (result['classification'], result['signal_direction']) == (expected, direction)
    zero = apply([row(i, 0) for i in range(5)])[-1]
    assert zero['classification'] == NO_SIGNAL and zero['scale'] == 1
    assert zero['lower_threshold'] == 0  # Zero is not a lower alarm.


def test_mad_scale_is_computed_from_prior_counts():
    result = apply([row(i, value) for i, value in enumerate([0, 10, 20, 30, 90])])[-1]
    assert result['baseline_estimate'] == 15
    assert result['baseline_mad'] == 10
    assert result['scale'] == pytest.approx(14.826)
    assert not result['scale_floor_active']


def test_short_history_missing_suppressed_and_missing_periods():
    assert apply([row(0, 1)])[-1]['classification'] == 'insufficient_data'
    rows = [row(i, 16) for i in range(5)]
    for missing in (None, 'x', ':'):
        altered = [dict(r) for r in rows]
        altered[1]['observed_value'] = missing
        result = apply(altered)[-1]
        assert result['classification'] == 'insufficient_data'
        assert result['reference_completeness'] == .75
    assert apply(rows[:2] + rows[3:])[-1]['classification'] == 'insufficient_data'
    assert apply(rows[:-1] + [row(4, None)])[-1]['classification'] == 'unavailable_analysis'


def test_geographies_and_measurement_scales_remain_separate():
    rows = [row(i, 10) for i in range(5)]
    other = [dict(r, geography='Other area', observed_value=1000) for r in rows]
    combined = apply(rows + other)
    assert {r['baseline_estimate'] for r in combined if r['ordinal'] == 4} == {10, 1000}
    with pytest.raises(ValueError, match='Duplicate'):
        apply(rows + [rows[0]])
    incompatible = [dict(r, unit='percent') for r in rows]
    assert all(r['classification'] == 'unavailable_analysis' for r in apply(incompatible))
    with pytest.raises(ValueError):
        apply([row(0, -1)])
    with pytest.raises(ValueError):
        apply([row(0, 1.5)])


def test_assist_and_frozen_shares_are_not_forced_into_count_models():
    assist = unsupported(load('assist_percentages'), 'No denominators or compatible periods')
    assert len(assist) == 72
    assert all(r['classification'] == 'insufficient_data' for r in assist)
    assert all(r['period_start'] is None for r in assist)
    assert CONFIGURATIONS['frozen_forensic_shares']['windows'] == []


def evidence_row(source='a', classification=SIGNAL, direction='increase'):
    return dict(row(4, 100), classification=classification, signal_direction=direction, source_id=source)


def test_evidence_classes_do_not_infer_support_from_no_signal():
    signal = evidence_row()
    quiet = evidence_row('b', NO_SIGNAL, 'none')
    assert evidence_class([signal]) == 'single_indicator_signal'
    assert evidence_class([signal, quiet]) == 'single_indicator_signal'
    assert evidence_class([signal, evidence_row('b')]) == 'multiple_supporting_indicators'
    assert evidence_class([signal, evidence_row('b', direction='decrease')]) == 'conflicting_indicators'
    assert evidence_class([quiet]) == 'no_detected_signal'
    insufficient = evidence_row('b', 'insufficient_data', 'unavailable')
    assert evidence_class([quiet, insufficient]) == 'insufficient_evidence'
    assert evidence_class([insufficient]) == 'insufficient_evidence'
    # Multiple categories from one data source are not corroborating sources.
    assert evidence_class([signal, dict(signal, indicator_id='other')]) == 'single_indicator_signal'


@pytest.mark.parametrize('field,value', [('geography', 'Other'), ('period', '2026 Q1'),
                                       ('period_start', 'different'), ('period_end', 'different'),
                                       ('period_basis', 'source_study_period_not_calendar_quarter'),
                                       ('evidence_domain', 'different')])
def test_evidence_rejects_incompatible_periods_geography_and_domain(field, value):
    with pytest.raises(ValueError, match='Incompatible'):
        evidence_class([evidence_row(), dict(evidence_row('b'), **{field: value})])


def test_historical_flags_never_become_current_warnings():
    result = assess([evidence_row()])[0]
    assert result['historical_evidence_class'] == 'single_indicator_signal'
    assert result['current_evidence_class'] == 'insufficient_evidence'
    assert 'RADAR' in result['contextual_gaps']


def test_sensitivity_retains_ineligible_windows_and_direction():
    rows = [row(i, 16) for i in range(4)] + [row(4, 27)]
    primary = apply(rows)
    variants = [apply(rows, threshold=t) for t in (2.5, 3, 3.5)] + [apply(rows, window=6)]
    result = sensitivity(primary, variants)[-1]
    assert result['eligible_choices'] == 3
    assert result['signal_choices'] == 1
    assert result['signal_fraction'] == 1 / 3
    assert result['stability'] == 'choice_sensitive'
    assert result['missing_or_short_window_choices'] == 1
    all_flags = [row(i, 16) for i in range(4)] + [row(4, 100)]
    results = [apply(all_flags, threshold=t) for t in (2.5, 3, 3.5)]
    assert sensitivity(results[1], results)[-1]['stability'] == 'all_choices_same_direction_signal'


def test_reproducibility_preservation_and_real_output_contract(tmp_path):
    before = protected_hashes()
    first, second = tmp_path / 'first', tmp_path / 'second'
    quality = run(first)
    run(second)
    assert protected_hashes() == before
    for path in first.iterdir():
        if path.name != 'run_manifest.json':
            assert path.read_bytes() == (second / path.name).read_bytes(), path.name
    assert sum(quality['classifications'].values()) == 8034
    with (first / 'anomaly_results.csv').open(encoding='utf-8', newline='') as handle:
        records = list(csv.DictReader(handle))
    assert len(records) == 8034
    for record in records:
        assert record['source_sha256'] and record['source_path'] and record['limitations']
        assert record['temporal_status'] == 'historical_research_only_not_current_threat'
    flags = sum(r['classification'] == SIGNAL for r in records)
    assert flags == quality['classifications'].get(SIGNAL, 0)
    frequencies = json.loads((first / 'signal_frequencies.json').read_text())
    assert all(r['signals'] <= r['eligible'] <= r['observations'] for r in frequencies)
    for info in frequencies:
        if info['eligible']:
            assert info['signal_frequency'] == info['signals'] / info['eligible']
    manifest = json.loads((first / 'run_manifest.json').read_text())
    assert manifest['preserved_artifacts_verified']
    assert 'analysis/outputs/run_manifest.json' in manifest['protected_artifact_hashes']
