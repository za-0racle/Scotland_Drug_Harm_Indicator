"""Run local Phase 5 screens against hash-verified, saved Phase 4 observations."""
import argparse
import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from analysis.phase3.audit import verify
from analysis.phase5.monitoring import (CONFIGURATIONS, THRESHOLDS, PRIMARY_THRESHOLD, SIGNAL,
                                        screen, unsupported, sensitivity, assess)

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'analysis/phase5'
PHASE4 = ROOT / 'analysis/phase4/outputs'
FIELDS = ('indicator_id', 'source_id', 'source_path', 'source_sha256', 'source_url', 'geography',
          'period', 'ordinal', 'observed_value', 'unit', 'period_basis', 'period_start', 'period_end',
          'quality_status', 'quality_status_detail', 'limitations', 'publication_date', 'publication_lag_days',
          'publication_status', 'source_data_cutoff', 'data_age_days', 'analysis_as_of')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_hashes():
    verify()
    manifest = json.loads((PHASE4 / 'run_manifest.json').read_text())
    for name, expected in manifest['output_hashes'].items():
        if digest(PHASE4 / name) != expected:
            raise ValueError(f'Phase 4 artifact changed: {name}')
    expected_files = dict(manifest['code_hashes'], **manifest['supporting_source_hashes'])
    expected_files.update({name: info['sha256'] for name, info in manifest['sources'].items()})
    for name, expected in expected_files.items():
        if digest(ROOT / name) != expected:
            raise ValueError(f'Phase 4 input/code changed: {name}')
    paths = set(ROOT / name for name in expected_files)
    for directory in ('analysis/outputs', 'analysis/phase3', 'analysis/phase4', 'g3-indicator/data/frozen'):
        for path in (ROOT / directory).rglob('*'):
            if path.is_file() and not any(p.endswith('.local') or p == '__pycache__' for p in path.parts):
                paths.add(path)
    paths.add(ROOT / 'group3_indicator_results_recomputed.csv')
    paths.add(ROOT / 'analysis/group3_indicator_computation.py')
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)}


def load(dataset):
    with (PHASE4 / f'{dataset}.csv').open(newline='', encoding='utf-8') as handle:
        rows = []
        for raw in csv.DictReader(handle):
            row = {key: raw.get(key) or None for key in FIELDS}
            row.update(dataset=dataset, ordinal=int(raw['ordinal']),
                       observed_value=float(raw['observed_value']) if raw['observed_value'] else None,
                       substance_category=raw['indicator_id'].split(':', 1)[1] if ':' in raw['indicator_id'] else None,
                       # Preserve measurement domains: similar drug names are not harmonised outcomes.
                       evidence_domain=raw['indicator_id'])
            rows.append(row)
    return rows


def write_json(directory, name, value):
    (directory / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def write_csv(directory, name, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (directory / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(directory=None):
    directory = Path(directory or HERE / 'outputs').resolve()
    # Do not permit an output target to overwrite preserved research directories.
    if directory != HERE / 'outputs' and not any(p.endswith('.local') for p in directory.parts):
        raise ValueError('Output directory must be phase5/outputs or a .local research scratch directory')
    before = protected_hashes()
    directory.mkdir(parents=True, exist_ok=True)
    primary, stability, frequencies = [], [], []
    for dataset, config in CONFIGURATIONS.items():
        rows = load(dataset)
        if not config['windows']:
            reason = ('Unknown sample denominators, unequal study periods and only 12 observations per series; no binomial or calendar-quarter model'
                      if dataset == 'assist_percentages' else
                      'Only 12 historical quarters, unresolved independent denominator lineage; original CUSUM left unchanged')
            primary.extend(unsupported(rows, reason))
            continue
        variants = []
        for window in config['windows']:
            for threshold in THRESHOLDS:
                results = screen(rows, window, threshold, config['basis'])
                variants.append(results)
                by_geography = defaultdict(list)
                for row in results:
                    by_geography[(row['indicator_id'], row['geography'])].append(row)
                for (indicator, geography), group in sorted(by_geography.items()):
                    eligible = [r for r in group if r['classification'] in (SIGNAL, 'no_detected_anomaly')]
                    flags = sum(r['classification'] == SIGNAL for r in eligible)
                    frequencies.append(dict(dataset=dataset, indicator_id=indicator, geography=geography,
                                            window=window, threshold=threshold, observations=len(group), eligible=len(eligible),
                                            signals=flags, signal_frequency=flags / len(eligible) if eligible else None,
                                            insufficient=sum(r['classification'] == 'insufficient_data' for r in group),
                                            unavailable=sum(r['classification'] == 'unavailable_analysis' for r in group),
                                            scale_floor_active=sum(r.get('scale_floor_active') is True for r in eligible)))
                if window == config['primary_window'] and threshold == PRIMARY_THRESHOLD:
                    selected = results
        primary.extend(selected)
        stability.extend(sensitivity(selected, variants))
    evidence = assess(primary)
    write_csv(directory, 'anomaly_results.csv', primary)
    write_csv(directory, 'sensitivity_results.csv', stability)
    write_json(directory, 'signal_frequencies.json', frequencies)
    write_json(directory, 'monitoring_configurations.json', dict(datasets=CONFIGURATIONS, thresholds=THRESHOLDS,
               primary_threshold=PRIMARY_THRESHOLD, scale='max(1.4826 * prior MAD, sqrt(max(prior median, 1)))',
               limits='[max(0, median - threshold*scale), median + threshold*scale]; strict outside comparison',
               interpretation='Exploratory robust screens; not calibrated p-values, prediction intervals, NB2/EWMA/CUSUM or validated warning rules',
               selection='Pragmatic windows chosen before this run, not optimised against observed flags; all choices reported'))
    write_json(directory, 'evidence_assessments.json', evidence)
    quality = dict(classifications=dict(Counter(r['classification'] for r in primary)),
                   dataset_classifications={d: dict(Counter(r['classification'] for r in primary if r['dataset'] == d)) for d in CONFIGURATIONS},
                   reasons=dict(Counter(r['reason'] for r in primary)),
                   historical_evidence_classes=dict(Counter(r['historical_evidence_class'] for r in evidence)),
                   sensitivity_stability=dict(Counter(r['stability'] for r in stability)),
                   current_assessment='insufficient_evidence: stale cutoffs and unknown publication vintages; no current warning',
                   limitations=['No seasonal/trend adjustment, testing-volume/exposure adjustment or as-published vintages',
                                'Serial correlation, overlapping windows, repeated comparisons and sample changes may produce flags',
                                'Count-scale floor is a pragmatic safeguard, not a fitted count distribution; low-count screens may be conservative',
                                'No reference event set: signal frequency is not false-positive rate, sensitivity, specificity or lead time',
                                'Exact domains/geographies/periods prevent cross-source corroboration in these inputs; absence of support is not absence of harm',
                                'ASSIST and frozen shares are not forced into new statistical models; no private RADAR narratives read',
                                'All findings retrospective; historical flags are not confirmed public health alerts'])
    write_json(directory, 'quality_report.json', quality)
    phase4_manifest = json.loads((PHASE4 / 'run_manifest.json').read_text())
    write_json(directory, 'source_provenance.json', dict(sources=phase4_manifest['sources'],
               phase4_manifest_sha256=digest(PHASE4 / 'run_manifest.json'),
               analysis_as_of='2026-11-10', access='Local saved aggregates only; no network or database',
               radar_context='Not analysed: narrative privacy and non-calendar reporting compatibility unresolved',
               publication='No public output, RLS change, migration, deployment or UI integration'))
    flags = [r for r in primary if r['classification'] == SIGNAL]
    national = [r for r in flags if r['geography'] in ('Scotland', 'Scotland national total')]
    report = ['# Phase 5 execution findings', '',
              f"Primary screens: {len(primary)} observations; {len(flags)} statistical flags. Classifications: {quality['classifications']}.", '',
              f"Historical evidence: {quality['historical_evidence_classes']}.", '',
              f"Sensitivity: {quality['sensitivity_stability']}.", '',
              'All flags are retrospective research screens. See anomaly_results.csv for every flag, threshold, baseline, exact period and source.', '',
              '## National-series flags (all)', '',
              '| Dataset | Geography | Period | Observed | Prior median | Lower | Upper | Direction |',
              '| --- | --- | --- | ---: | ---: | ---: | ---: | --- |']
    for row in national:
        report.append(f"| {row['dataset']} | {row['geography']} | {row['period']} | {row['observed_value']:g} | {row['baseline_estimate']:g} | {row['lower_threshold']:.3f} | {row['upper_threshold']:.3f} | {row['signal_direction']} |")
    report.extend(['', '## Flags by dataset', ''])
    for dataset in CONFIGURATIONS:
        report.append(f"- {dataset}: {sum(r['dataset'] == dataset for r in flags)} flags; {quality['dataset_classifications'][dataset]}.")
    report.extend(['', '## Limits and next decision', '', *['- ' + value for value in quality['limitations']], '',
                   'No compatible multi-source corroboration or current early warning is established. Preserve original historical monitoring independently. Stop after Phase 5; next consider a separately approved methods review and source-vintage/denominator harmonisation, before any publication or interface work.', ''])
    (directory / 'FINDINGS.md').write_text('\n'.join(report), encoding='utf-8')
    after = protected_hashes()
    if before != after:
        raise ValueError('Preserved research artifacts changed during execution')
    outputs = {p.name: digest(p) for p in sorted(directory.iterdir()) if p.is_file() and p.name != 'run_manifest.json'}
    code = list(HERE.glob('*.py')) + [HERE / 'README.md', ROOT / 'analysis/tests/test_phase5.py']
    write_json(directory, 'run_manifest.json', dict(version='phase5-1.0.0', executed_at_utc=datetime.now(timezone.utc).isoformat(),
               python=platform.python_version(), protected_artifact_hashes=before, preserved_artifacts_verified=True,
               source_code_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in code if p.exists()},
               output_hashes=outputs, phase='5 only', deterministic_artifacts='All except execution-timestamped manifest'))
    return quality


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir')
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), indent=2))
