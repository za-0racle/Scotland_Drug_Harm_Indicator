"""Prior-only, complete-window robust count screens and strict evidence matching.

These are descriptive statistical screens, not calibrated significance tests.
The count-scale floor is a safeguard against tiny/zero MAD, not a Poisson fit.
"""
from collections import defaultdict
from math import isfinite, sqrt
from statistics import median


CONFIGURATIONS = {
    'mortality_quarterly': dict(windows=[12, 16], primary_window=16, basis='calendar_quarter_legacy_10_day_adjustment'),
    'forensic_counts': dict(windows=[12, 16], primary_window=16, basis='calendar_quarter'),
    'treatment_counts': dict(windows=[12, 18], primary_window=18, basis='calendar_month'),
    'naloxone_weekly': dict(windows=[52, 104], primary_window=104, basis='week_beginning_monday'),
    'assist_percentages': dict(windows=[], primary_window=None, basis='source_study_period_not_calendar_quarter'),
    'frozen_forensic_shares': dict(windows=[], primary_window=None, basis='calendar_quarter'),
}
THRESHOLDS = [2.5, 3.0, 3.5]
PRIMARY_THRESHOLD = 3.0
SIGNAL = 'statistically_unusual_observation'
NO_SIGNAL = 'no_detected_anomaly'
METHOD = 'prior_complete_window_median_MAD_count_floor'


def numeric(value):
    if value is None or value in ('', 'x', 'X', ':', 'NA'):
        return None
    if isinstance(value, bool):
        raise ValueError('Boolean count')
    result = float(value)
    if not isfinite(result) or result < 0 or not result.is_integer():
        raise ValueError('Counts must be finite nonnegative integers')
    return result


def screen(rows, window, threshold, basis):
    """Never read descriptive Phase 4 means: derive references from raw prior values."""
    if window < 2 or threshold <= 0 or not isfinite(threshold):
        raise ValueError('Invalid monitoring parameters')
    groups = defaultdict(dict)
    for row in rows:
        key = (row['source_id'], row['indicator_id'], row['geography'], row['period_basis'], row['unit'])
        index = int(row['ordinal'])
        if index in groups[key]:
            raise ValueError('Duplicate monitoring period')
        groups[key][index] = row
    output = []
    for key, indexed in sorted(groups.items()):
        for index, row in sorted(indexed.items()):
            result = dict(row)
            result.update(method=METHOD, window=window, threshold=threshold,
                          classification='insufficient_data', signal_direction='unavailable',
                          baseline_estimate=None, baseline_mad=None, scale=None,
                          lower_threshold=None, upper_threshold=None, robust_score=None,
                          reference_start=None, reference_end=None, reference_observations=0,
                          expected_reference_observations=window,
                          reference_completeness=0, scale_floor_active=None,
                          temporal_status='historical_research_only_not_current_threat')
            if row['period_basis'] != basis or row['unit'] not in ('count', 'detection_count', 'incident_count'):
                result.update(classification='unavailable_analysis', reason='Incompatible period basis or measurement scale')
                output.append(result)
                continue
            current = numeric(row['observed_value'])
            prior = [indexed.get(i) for i in range(index - window, index)]
            values = [numeric(r['observed_value']) if r else None for r in prior]
            available = sum(v is not None for v in values)
            result.update(reference_observations=available, reference_completeness=available / window,
                          reference_start=prior[0]['period'] if prior[0] else None,
                          reference_end=prior[-1]['period'] if prior[-1] else None)
            if current is None:
                result.update(classification='unavailable_analysis', reason='Observation missing or suppressed; never imputed')
            elif available != window:
                result['reason'] = 'Incomplete prior window: missing/suppressed periods or insufficient history'
            else:
                centre = median(values)
                mad = median(abs(v - centre) for v in values)
                floor = sqrt(max(centre, 1.0))
                scale = max(1.4826 * mad, floor)
                lower, upper = max(0.0, centre - threshold * scale), centre + threshold * scale
                direction = 'increase' if current > upper else 'decrease' if current < lower else 'none'
                result.update(classification=SIGNAL if direction != 'none' else NO_SIGNAL,
                              signal_direction=direction, baseline_estimate=centre, baseline_mad=mad,
                              scale=scale, scale_floor_active=floor >= 1.4826 * mad,
                              lower_threshold=lower, upper_threshold=upper,
                              robust_score=(current - centre) / scale,
                              reason='Strict outside-threshold comparison; exploratory count screen, not a p-value or forecast interval')
            output.append(result)
    return output


def unsupported(rows, reason):
    return [dict(row, classification='insufficient_data', signal_direction='unavailable',
                 method='not_estimated', reason=reason, window=None, threshold=None,
                 baseline_estimate=None, lower_threshold=None, upper_threshold=None,
                 reference_start=None, reference_end=None, reference_observations=0,
                 reference_completeness=None, temporal_status='historical_research_only_not_current_threat') for row in rows]


def identity(row):
    return (row['dataset'], row['indicator_id'], row['geography'], row['period_basis'], row['period'])


def sensitivity(primary, variants):
    indexed = defaultdict(list)
    for variant in variants:
        for row in variant:
            indexed[identity(row)].append(row)
    results = []
    for row in primary:
        choices = indexed[identity(row)]
        eligible = [r for r in choices if r['classification'] in (SIGNAL, NO_SIGNAL)]
        flags = [r for r in eligible if r['classification'] == SIGNAL]
        same = [r for r in flags if r['signal_direction'] == row['signal_direction']]
        results.append(dict(zip(('dataset', 'indicator_id', 'geography', 'period_basis', 'period'), identity(row)),
                            primary_classification=row['classification'], primary_direction=row['signal_direction'],
                            attempted_choices=len(choices), eligible_choices=len(eligible), signal_choices=len(flags),
                            signal_fraction=len(flags) / len(eligible) if eligible else None,
                            stability=('all_choices_same_direction_signal' if len(same) == len(choices) and choices else
                                       'choice_sensitive' if flags else 'no_signal_in_eligible_choices' if eligible else 'insufficient_data'),
                            missing_or_short_window_choices=len(choices) - len(eligible)))
    return results


def evidence_class(rows):
    """Caller must supply one strictly compatible evidence domain and period.

    Different categories within one source are not independent corroboration.
    Even different sources may share cases; no independence claim is made.
    """
    keys = {(r['geography'], r['period_basis'], r['period'], r['period_start'], r['period_end'], r['evidence_domain']) for r in rows}
    if len(keys) > 1:
        raise ValueError('Incompatible geography, reporting period or evidence domain')
    eligible = [r for r in rows if r['classification'] in (SIGNAL, NO_SIGNAL)]
    flags = [r for r in eligible if r['classification'] == SIGNAL]
    directions = {r['signal_direction'] for r in flags}
    if len(directions) > 1:
        return 'conflicting_indicators'
    if len({r['source_id'] for r in flags}) > 1:
        return 'multiple_supporting_indicators'
    if flags:
        return 'single_indicator_signal'
    if len(eligible) != len(rows) or not eligible:
        return 'insufficient_evidence'
    return 'no_detected_signal'


def assess(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (row['geography'], row['period_basis'], row['period'], row.get('period_start'), row.get('period_end'), row['evidence_domain'])
        groups[key].append(row)
    results = []
    for key, group in sorted(groups.items(), key=lambda item: str(item[0])):
        flags = [r for r in group if r['classification'] == SIGNAL]
        results.append(dict(geography=key[0], period_basis=key[1], period=key[2], period_start=key[3], period_end=key[4],
                            evidence_domain=key[5], historical_evidence_class=evidence_class(group),
                            supporting_indicators=[dict(dataset=r['dataset'], indicator_id=r['indicator_id'], source_id=r['source_id'],
                                                        direction=r['signal_direction']) for r in flags],
                            assessed_indicators=[r['indicator_id'] for r in group],
                            unavailable_indicators=[r['indicator_id'] for r in group if r['classification'] not in (SIGNAL, NO_SIGNAL)],
                            publication_dates=sorted({r['publication_date'] for r in group if r.get('publication_date')}),
                            publication_timing='Unknown dates retained; retrospective frozen vintage, not as-issued surveillance',
                            current_evidence_class='insufficient_evidence',
                            explanation='Exact geography, period bounds/basis and measurement domain required; no aliases, period aggregation or causal/independence inference. All available cutoffs are historical; no current threat assessment.',
                            contextual_gaps='RADAR narratives not read: privacy review and compatible period mapping unavailable; ASSIST lacks denominators/dates. No confirmed-alert or false-positive reference set.'))
    return results
