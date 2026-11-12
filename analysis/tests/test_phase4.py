from datetime import date, timedelta

import pytest

from analysis.phase4.trends import number, count_number, percentage_change, derive, aggregate_years, assigned_months, rank_groups
from analysis.phase4.run import mortality, toxicology, naloxone
from analysis.phase4.run import run


def record(index, value, unit='count', **extra):
    return dict(indicator_id='test', geography='Test area', source_id='test.csv', ordinal=index,
                period=str(index), observed_value=value, unit=unit, limitations='Test fixture only', **extra)


def test_percentages_and_zero_denominators():
    assert count_number('10') == 10
    assert count_number('x') is None
    with pytest.raises(ValueError):
        count_number('1.5')
    assert percentage_change(120, 100) == 20
    assert percentage_change(80, 100) == -20
    assert percentage_change(0, 100) == -100
    assert percentage_change(1, 0) is None
    assert percentage_change(None, 100) is None
    assert number('NA') is None
    assert number('x') is None
    for value in ('nan', 'inf', '-1', True):
        with pytest.raises(ValueError):
            number(value)


def test_missing_periods_do_not_become_adjacent_changes_or_rolling_means():
    rows = derive([record(1, 10), record(3, 20)], rolling=2, reference=2)
    assert rows[-1]['previous_value'] is None
    assert rows[-1]['period_change_pct'] is None
    assert rows[-1]['rolling_average'] is None
    assert rows[-1]['historical_reference_mean'] is None


def test_duplicates_are_rejected_instead_of_summed():
    with pytest.raises(ValueError, match='Duplicate'):
        derive([record(1, 10), record(1, 10)])


def test_complete_windows_previous_year_and_percentage_points():
    rows = derive([record(i, 10 * i, 'percent') for i in range(1, 6)], year_stride=4, rolling=4, reference=4)
    final = rows[-1]
    assert final['year_reference_value'] == 10
    assert final['year_change_pct'] == 400
    assert final['rolling_average'] == 35
    assert final['historical_reference_mean'] == 25
    assert final['percentage_point_change'] == 10


def test_annual_aggregation_requires_four_unsuppressed_quarters():
    rows = [record(i, i, year=2025, quarter=i) for i in range(1, 5)]
    annual = aggregate_years(rows)
    assert len(annual) == 1 and annual[0]['observed_value'] == 10
    assert aggregate_years(rows[:3]) == []
    rows[1]['observed_value'] = None
    assert aggregate_years(rows) == []


def test_week_start_month_groups_do_not_claim_calendar_month_incidence():
    starts = [date(2026, 2, day) for day in (2, 9, 16, 23)]
    rows = [record(d.toordinal() // 7, 2, period_start=str(d), period_end=str(d + timedelta(days=6))) for d in starts]
    output = assigned_months(rows)
    assert output[0]['observed_value'] == 8
    assert output[0]['period_basis'] == 'month_of_week_start_not_calendar_incidence'
    assert output[0]['expected_weeks'] == 4
    assert 'NOT calendar-month' in output[0]['limitations']
    assert assigned_months(rows[:3])[0]['observed_value'] is None
    with pytest.raises(ValueError, match='Duplicate'):
        assigned_months(rows + [rows[0]])


def test_rankings_are_within_source_period_and_allow_overlapping_shares():
    rows = [record(1, 80, 'percent'), record(1, 70, 'percent')]
    assert [r['within_source_period_dense_rank'] for r in rank_groups(rows)] == [1, 2]
    assert sum(r['observed_value'] for r in rows) == 150  # No forced 100% normalization.


def test_real_mortality_and_regional_totals():
    quarterly, annual = mortality()
    national = [r for r in quarterly if r['geography'] == 'Scotland national total']
    assert len(national) == 36
    assert len({r['geography'] for r in quarterly}) == 14
    national_annual = [r for r in annual if r['geography'] == 'Scotland national total']
    assert len(national_annual) == 9
    assert national_annual[-1]['observed_value'] == sum(r['observed_value'] for r in national[-4:])
    regional = [r for r in annual if 'Renfrewshire and Inverclyde' in r['geography']][-1]
    assert regional['share_of_national_pct'] == 100 * regional['observed_value'] / national_annual[-1]['observed_value']


def test_real_substance_periods_and_denominator_scope():
    forensic, assist, treatment, shares = toxicology()
    assert len(forensic) == 210 and len(assist) == 72 and len(treatment) == 140
    assert len(shares) == 84
    assert all(r['period'][:4] in ('2022', '2023', '2024') for r in shares)
    assert all(abs(r['observed_value'] - r['computed_share_pct']) < .0051 for r in shares)
    assert all(r['period_start'] is None for r in assist)
    assert all(r['rolling_average'] is None for r in assist)
    assert any(r['quality_status_detail'] == 'shortened_Q9' for r in assist)
    assert all(r['sample_type'] == 'Urine' for r in treatment)


def test_real_weekly_naloxone_not_pooled_across_geographies():
    weekly, months = naloxone()
    assert len(weekly) == 7024
    assert len({r['geography'] for r in weekly}) == 16
    assert sum(r['reported_moving_average'] is None for r in weekly) == 32
    assert all(r['year_comparison_basis'] == '52_week_lag_not_calendar_year' for r in weekly)
    assert all(r['period_basis'] == 'month_of_week_start_not_calendar_incidence' for r in months)


def test_saved_outputs_are_reproducible_and_provenance_is_present(tmp_path):
    import json
    from pathlib import Path
    first, second = tmp_path / 'first', tmp_path / 'second'
    run(first)
    run(second)
    for path in first.iterdir():
        if path.name != 'run_manifest.json':
            assert path.read_bytes() == (second / path.name).read_bytes(), path.name
    manifest = json.loads((first / 'run_manifest.json').read_text())
    assert len(manifest['sources']) == 6
    assert all(len(source['sha256']) == 64 for source in manifest['sources'].values())
    quality = json.loads((first / 'quality_report.json').read_text())
    assert len(quality['suppressed_mortality_quarters']) == 8
    assert len(quality['excluded_incomplete_annual_totals']) == 7
    assert quality['missing_source_naloxone_moving_averages'] == 32
