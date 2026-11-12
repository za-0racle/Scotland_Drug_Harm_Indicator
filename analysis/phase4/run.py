"""Offline descriptive trends. Run: python -m analysis.phase4.run."""
import argparse
import calendar
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from openpyxl import load_workbook

from analysis.data import load_verified, WORKBOOK, FROZEN
from analysis.phase3.audit import verify
from analysis.phase4.trends import number, count_number, derive, aggregate_years, assigned_months, rank_groups

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'datasets/Group3_Item2_Data'
AS_OF = date(2026, 11, 10)  # Explicit reproducible analysis date, not a live warning date.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def month_end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1]).isoformat()


def observation(path, indicator, geography, period, ordinal, value, unit, basis, start, end, limitations, **extra):
    return dict(indicator_id=indicator, source_id=path.name, source_path=path.relative_to(ROOT).as_posix(),
                geography=geography, period=period, ordinal=ordinal, observed_value=value, unit=unit,
                period_basis=basis, period_start=start, period_end=end,
                quality_status='missing_or_suppressed' if value is None else 'observed',
                limitations=limitations, **extra)


def mortality():
    verified, _ = load_verified()
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    rows = []
    try:
        sheet = workbook['A - Police Division']
        for source in sheet.iter_rows(min_row=5, max_row=18, values_only=True):
            geography = 'Scotland national total' if source[0] == 'Total' else source[0].strip()
            for i, target in enumerate(verified):
                year, quarter = target['year'], target['quarter']
                value = count_number(source[i + 1])
                start_month = 3 * quarter - 2
                rows.append(observation(WORKBOOK, 'suspected_deaths', geography, f'{year} Q{quarter}', year * 4 + quarter - 1,
                    value, 'count', 'calendar_quarter_legacy_10_day_adjustment', f'{year}-{start_month:02}-01', month_end(year, start_month + 2),
                    'Provisional originally suspected deaths, legacy ten-day timing adjustment; police divisions are not councils or Greenock; x suppression retained; no significance test.',
                    year=year, quarter=quarter, publication_date='2026-03-17'))
    finally:
        workbook.close()
    national = {row['ordinal']: row['observed_value'] for row in rows if row['geography'] == 'Scotland national total'}
    for row in rows:
        total = national[row['ordinal']]
        row['share_of_national_pct'] = 100 * row['observed_value'] / total if row['observed_value'] is not None and total and row['geography'] != 'Scotland national total' else None
    annual = aggregate_years(rows)
    annual_national = {row['year']: row['observed_value'] for row in annual if row['geography'] == 'Scotland national total'}
    for row in annual:
        total = annual_national.get(row['year'])
        row['share_of_national_pct'] = 100 * row['observed_value'] / total if total and row['geography'] != 'Scotland national total' else None
    return derive(rows, year_stride=4, rolling=4, reference=8), annual


def toxicology():
    forensic_path = DATA / 'radar_toxicology_forensic_2018-2026.csv'
    forensic = []
    for item in csv_rows(forensic_path):
        match = re.fullmatch(r'Q([1-4]) (\d{4})', item['Quarter'])
        if not match or item['measure'] != 'Number':
            raise ValueError('Unexpected forensic period or unit')
        quarter, year = map(int, match.groups())
        month = 3 * quarter - 2
        forensic.append(observation(forensic_path, 'forensic:' + item['drug_name'], 'Scotland forensic testing sample', f'{year} Q{quarter}', year * 4 + quarter - 1,
            count_number(item['value']), 'detection_count', 'calendar_quarter', f'{year}-{month:02}-01', month_end(year, month + 2),
            'Overlapping substance categories; detections are not causal deaths; testing/sample changes and absent denominators preclude prevalence estimates.'))
    forensic = rank_groups(derive(forensic, year_stride=4, rolling=4, reference=8))

    assist_path = DATA / 'radar_toxicology_assist.csv'
    assist = []
    for item in csv_rows(assist_path):
        value = number(item['Percentage'])
        if value is not None and value > 100:
            raise ValueError('ASSIST percentage outside [0,100]')
        sequence = int(item['quarter'])
        assist.append(observation(assist_path, 'assist:' + item['drug_name'], 'ASSIST participating emergency-department sample',
            ' '.join(item['chart_label'].split()), sequence, value, 'percent', 'source_study_period_not_calendar_quarter', None, None,
            'Selected emergency-department cohort, not population prevalence; categories overlap; sample denominators unavailable; Q9 recruitment shortened; no pooled percentages or calendar-quarter reassignment.',
            study_period=sequence, quality_status_detail='shortened_Q9' if sequence == 9 else 'study_period_and_denominator_caveat'))
    assist = rank_groups(derive(assist, rolling=None, reference=None))

    treatment_path = DATA / 'radar_toxicology_treatment_glasgow.csv'
    treatment = []
    for item in csv_rows(treatment_path):
        start = date.fromisoformat(item['month'])
        if start.day != 1 or item['measure'] != 'Number':
            raise ValueError('Unexpected treatment period or measure')
        treatment.append(observation(treatment_path, 'treatment:' + item['drug'], item['region'], start.strftime('%Y-%m'), start.year * 12 + start.month - 1,
            count_number(item['value']), 'detection_count', 'calendar_month', start.isoformat(), month_end(start.year, start.month),
            'Treatment urine samples, not community prevalence; testing volume/selection may change; categories overlap and exclude treatment opioids in the source opioid category.', sample_type=item['sample_type']))
    treatment = rank_groups(derive(treatment, year_stride=12, rolling=3, reference=12))

    mapping = dict(opioids='Opioids', all_benzodiazepines='All Benzodiazepines', street_benzodiazepines='Street Benzodiazepines',
                   prescribable_benzodiazepines='Prescribable Benzodiazepines', stimulants='Stimulants', dissociatives='Dissociatives', gabapentinoids='Gabapentinoids')
    shares = []
    for item in json.loads(FROZEN.read_text()):
        denominator = number(item['table1_positive_deaths'])
        if not denominator:
            continue
        year, quarter = int(item['year']), int(item['quarter'][1:])
        for key, name in mapping.items():
            numerator, share = number(item['n_' + key]), number(item['share_' + key])
            if numerator is None or share is None:
                continue
            if numerator > denominator or abs(numerator / denominator - share) > .000051:
                raise ValueError('Inconsistent frozen detection share')
            shares.append(observation(FROZEN, 'frozen_forensic_share:' + name, 'Scotland forensic testing sample', item['calendar_quarter'], year * 4 + quarter - 1,
                share * 100, 'percent', 'calendar_quarter', f'{year}-{3*quarter-2:02}-01', month_end(year, 3 * quarter),
                'Frozen 2022-2024 Table 1 denominator only; arithmetic verified, independent extraction lineage unresolved; rounded original shares retained; overlapping substance detections, not mutually exclusive proportions.',
                numerator=numerator, denominator=denominator, computed_share_pct=100 * numerator / denominator,
                quality_status_detail='frozen_denominator_lineage_caveat'))
    shares = rank_groups(derive(shares, year_stride=4, rolling=None, reference=None))
    return forensic, assist, treatment, shares


def naloxone():
    path = DATA / 'radar_sas_naloxone_weekly_by_board.csv'
    rows = []
    for item in csv_rows(path):
        start = date.fromisoformat(item['weekbeginning'])
        if start.weekday() != 0:
            raise ValueError('Expected Monday week-beginning')
        moving = number(item['moving_average'])
        rows.append(observation(path, 'ambulance_naloxone_activity', item['Board'], start.isoformat(), start.toordinal() // 7,
            count_number(item['Number']), 'incident_count', 'week_beginning_monday', start.isoformat(), (start + timedelta(days=6)).isoformat(),
            'Ambulance naloxone activity, not take-home supply or direct overdose/toxicity incidence; national/Unknown/board rows must not be summed together; 52-week change is not exact calendar-year matching.',
            reported_moving_average=moving, quality_status_detail='source_moving_average_missing' if moving is None else 'source_moving_average_available'))
    return derive(rows, year_stride=52, rolling=4, reference=52), assigned_months(rows)


def enrich(outputs):
    registry = {row['dataset_name']: row for row in csv_rows(ROOT / 'group3_data_sources_import.csv')}
    manifest_sources = {}
    for records in outputs.values():
        for row in records:
            filename = row['source_path']
            if filename not in manifest_sources:
                match = registry.get(row['source_id'], {})
                url = re.match(r'https?://[^\s]+', match.get('source_url', ''))
                manifest_sources[filename] = dict(sha256=sha(ROOT / filename), publisher=match.get('publisher'), url=url.group(0) if url else None)
    for records in outputs.values():
        cutoffs = {}
        for row in records:
            key = row['source_id']
            cutoffs[key] = max(cutoffs.get(key, ''), row['period_end'] or '')
        for row in records:
            source = manifest_sources[row['source_path']]
            cutoff = cutoffs[row['source_id']] or None
            cutoff_label = max((r for r in records if r['source_id'] == row['source_id']), key=lambda r: r['ordinal'])['period'] if not cutoff else cutoff
            publication = row.get('publication_date')
            row.update(source_sha256=source['sha256'], source_url=source['url'], publication_date=publication,
                       source_data_cutoff=cutoff_label, analysis_as_of=AS_OF.isoformat(),
                       data_age_days=(AS_OF - date.fromisoformat(cutoff)).days if cutoff else None,
                       publication_lag_days=(date.fromisoformat(publication) - date.fromisoformat(row['period_end'])).days if publication and row['period_end'] else None,
                       publication_status='verified_vintage_date_not_first_release' if publication else 'unknown_publication_date',
                       scientific_status='descriptive_research_only_not_anomaly_or_alert')
    return manifest_sources


def write_csv(path, records):
    fields = list(dict.fromkeys(key for row in records for key in row))
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def run(directory=None):
    baseline = verify()
    quarterly, annual = mortality()
    forensic, assist, treatment, shares = toxicology()
    weekly, months = naloxone()
    outputs = dict(mortality_quarterly=quarterly, mortality_annual=annual, forensic_counts=forensic,
                   frozen_forensic_shares=shares, assist_percentages=assist, treatment_counts=treatment,
                   naloxone_weekly=weekly, naloxone_week_start_month=months)
    provenance = enrich(outputs)
    findings = {}
    for name, rows in outputs.items():
        groups = defaultdict(list)
        for row in rows:
            groups[(row['indicator_id'], row['geography'])].append(row)
        findings[name] = dict(records=len(rows), groups=len(groups), missing_observations=sum(row['observed_value'] is None for row in rows),
            latest=[max(items, key=lambda row: row['ordinal']) for items in groups.values()])
    directory = Path(directory) if directory else ROOT / 'analysis/phase4/outputs'
    directory.mkdir(parents=True, exist_ok=True)
    for name, rows in outputs.items():
        write_csv(directory / f'{name}.csv', rows)
    (directory / 'findings.json').write_text(json.dumps(findings, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    expected_annual = {(r['geography'], r['year']) for r in quarterly}
    available_annual = {(r['geography'], r['year']) for r in annual}
    quality = dict(
        suppressed_mortality_quarters=[{'geography': r['geography'], 'period': r['period']} for r in quarterly if r['observed_value'] is None],
        excluded_incomplete_annual_totals=[{'geography': geography, 'year': year, 'reason': 'At least one quarter missing/suppressed; no total inferred'} for geography, year in sorted(expected_annual - available_annual)],
        missing_source_naloxone_moving_averages=sum(r['reported_moving_average'] is None for r in weekly),
        incomplete_naloxone_week_start_months=sum(r['observed_value'] is None for r in months),
        assist_exact_dates_unavailable=True, assist_shortened_period='Q9',
        frozen_share_denominator_review='84 arithmetic checks passed; independent original Table 1 extraction lineage remains unresolved',
        calendar_month_naloxone_incidence='Not calculated; weekly counts cannot be split into exact calendar months',
        new_anomaly_or_alert_results='Not implemented or generated in Phase 4')
    (directory / 'quality_report.json').write_text(json.dumps(quality, indent=2) + '\n', encoding='utf-8')
    manifest = dict(version='phase4-1.0.0', executed_at_utc=datetime.now(timezone.utc).isoformat(), analysis_as_of=AS_OF.isoformat(),
        baseline_manifest_sha256=baseline['baseline_manifest_sha256'], sources=provenance,
        supporting_source_hashes={'group3_data_sources_import.csv': sha(ROOT / 'group3_data_sources_import.csv')},
        code_hashes={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / 'analysis/phase4').glob('*.py'))},
        methods='Descriptive exact-period changes and full-window means; no p-values, anomaly thresholds, risk scores, cross-source pooling or model reselection.',
        publication='Local outputs only; not approved for Supabase publication or public UI.',
        output_hashes={p.name: sha(p) for p in sorted(directory.iterdir()) if p.is_file() and p.name != 'run_manifest.json'})
    (directory / 'run_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    verify()  # Original research baseline must remain untouched.
    print(json.dumps({key: {k: v for k, v in value.items() if k != 'latest'} for key, value in findings.items()}, indent=2))
    return findings


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    run(parser.parse_args().output_dir)
