"""Period-aware descriptive changes; missing and zero denominators stay explicit."""
import math
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean


def number(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a numeric observation')
    if value is None or str(value).strip() in ('', 'NA', ':', 'x', 'X'):
        return None
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError('Expected a finite nonnegative observation')
    return result


def percentage_change(current, reference):
    if current is None or reference is None or reference == 0:
        return None
    return 100 * (current - reference) / reference


def count_number(value):
    result = number(value)
    if result is not None and result != int(result):
        raise ValueError('Count must be an integer')
    return int(result) if result is not None else None


def derive(records, *, year_stride=None, rolling=4, reference=8):
    """A group must represent one outcome, unit, source and geography."""
    groups = defaultdict(list)
    for record in records:
        groups[(record['indicator_id'], record['geography'])].append(dict(record))
    output = []
    for rows in groups.values():
        rows.sort(key=lambda row: row['ordinal'])
        by_period = {}
        for row in rows:
            if row['ordinal'] in by_period:
                raise ValueError(f'Duplicate observation: {row["indicator_id"]}/{row["geography"]}/{row["period"]}')
            by_period[row['ordinal']] = row
        for row in rows:
            index, value = row['ordinal'], row['observed_value']
            previous = by_period.get(index - 1, {}).get('observed_value')
            last_year = by_period.get(index - year_stride, {}).get('observed_value') if year_stride else None
            recent = [by_period.get(i, {}).get('observed_value') for i in range(index - rolling + 1, index + 1)] if rolling else []
            baseline = [by_period.get(i, {}).get('observed_value') for i in range(index - reference, index)] if reference else []
            baseline_mean = mean(baseline) if baseline and all(v is not None for v in baseline) else None
            change = value - previous if value is not None and previous is not None else None
            row.update(previous_value=previous, period_change=change,
                       period_change_pct=percentage_change(value, previous),
                       year_reference_value=last_year, year_change_pct=percentage_change(value, last_year),
                       rolling_average=mean(recent) if recent and all(v is not None for v in recent) else None,
                       rolling_periods=rolling, historical_reference_mean=baseline_mean,
                       reference_periods=reference, reference_change_pct=percentage_change(value, baseline_mean),
                       direction='unavailable' if change is None else 'increase' if change > 0 else 'decrease' if change < 0 else 'unchanged',
                       percentage_point_change=change if row['unit'] == 'percent' else None,
                       year_comparison_basis='52_week_lag_not_calendar_year' if year_stride == 52 else 'same_calendar_period_previous_year' if year_stride else 'not_available',
                       calculation_method='Adjacent exact-period differences; percent change only for nonzero reference; complete-window arithmetic means; no inference or significance test',
                       comparison_status='missing_reference' if previous is None else 'zero_reference_pct_undefined' if previous == 0 else 'descriptive_only')
            output.append(row)
    return output


def aggregate_years(records):
    groups = defaultdict(list)
    for row in records:
        groups[(row['indicator_id'], row['geography'], int(row['year']))].append(row)
    result = []
    for (_, _, year), rows in groups.items():
        if len({r['ordinal'] for r in rows}) != len(rows):
            raise ValueError('Duplicate quarterly input to annual aggregation')
        if len(rows) != 4 or {row['quarter'] for row in rows} != {1, 2, 3, 4} or any(row['observed_value'] is None for row in rows):
            continue  # Never present incomplete annual counts as full-year totals.
        row = dict(rows[0])
        row.pop('share_of_national_pct', None)
        row.update(period=str(year), ordinal=year, period_basis='calendar_year', quarter=None,
                   observed_value=sum(row['observed_value'] for row in rows),
                   period_start=f'{year}-01-01', period_end=f'{year}-12-31')
        result.append(row)
    return derive(result, year_stride=1, rolling=None, reference=3)


def assigned_months(records):
    """Group whole weekly totals by week-start month, NOT calendar incidence."""
    groups = defaultdict(list)
    for row in records:
        start = date.fromisoformat(row['period_start'])
        groups[(row['indicator_id'], row['geography'], start.year, start.month)].append(row)
    result = []
    for (_, _, year, month), rows in groups.items():
        if len({r['ordinal'] for r in rows}) != len(rows):
            raise ValueError('Duplicate weekly input to month grouping')
        first = date(year, month, 1)
        next_month = date(year + (month == 12), month % 12 + 1, 1)
        expected = sum((first + timedelta(days=i)).weekday() == 0 for i in range((next_month - first).days))
        complete = len(rows) == expected and all(r['observed_value'] is not None for r in rows)
        row = dict(rows[0])
        row.pop('reported_moving_average', None)
        row.pop('quality_status_detail', None)
        row.update(indicator_id=row['indicator_id'] + '_week_start_month', period=f'{year}-{month:02}',
                   ordinal=year * 12 + month - 1, period_start=str(first), period_end=str(next_month - timedelta(days=1)),
                   period_basis='month_of_week_start_not_calendar_incidence',
                   observed_value=sum(r['observed_value'] for r in rows) if complete else None,
                   quality_status='complete_week_start_group' if complete else 'incomplete_week_start_group',
                   expected_weeks=expected, observed_weeks=len(rows),
                   missing_source_moving_average_weeks=sum(r.get('reported_moving_average') is None for r in rows),
                   limitations=row['limitations'] + '; Whole weeks assigned by Monday; NOT calendar-month incidents. No prorating across boundaries.')
        result.append(row)
    return derive(result, year_stride=12, rolling=3, reference=12)


def rank_groups(records):
    groups = defaultdict(list)
    for row in records:
        groups[(row['source_id'], row['geography'], row['period'], row['unit'])].append(row)
    for rows in groups.values():
        values = sorted({row['observed_value'] for row in rows if row['observed_value'] is not None}, reverse=True)
        for row in rows:
            row['within_source_period_dense_rank'] = values.index(row['observed_value']) + 1 if row['observed_value'] is not None else None
    return records
