"""Verify the Phase 2 baseline without overwriting any baseline artifact."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'analysis/outputs'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify():
    manifest = json.loads((BASELINE / 'run_manifest.json').read_text())
    checks = {}
    for name, expected in manifest['output_hashes'].items():
        checks[f'output:{name}'] = digest(BASELINE / name) == expected
    for name, expected in manifest['data']['sources'].items():
        checks[f'input:{name}'] = digest(ROOT / name) == expected
    for name, expected in manifest['source_code_hashes'].items():
        checks[f'code:{name}'] = digest(ROOT / name) == expected
    if not all(checks.values()):
        raise ValueError(f'Baseline hash mismatch: {[key for key, ok in checks.items() if not ok]}')
    predictions = list(csv.DictReader((BASELINE / 'rolling_origin_predictions.csv').open()))
    metrics = json.loads((BASELINE / 'model_metrics.json').read_text())
    for metric in metrics:
        rows = [row for row in predictions if row['model'] == metric['model'] and row['status'] == 'ok']
        errors = [float(row['actual']) - float(row['predicted']) for row in rows]
        computed = dict(mae=sum(map(abs, errors)) / len(errors), rmse=math.sqrt(sum(e * e for e in errors) / len(errors)))
        for level in (80, 95):
            computed[f'coverage{level}'] = sum(float(row[f'lower{level}']) <= float(row['actual']) <= float(row[f'upper{level}']) for row in rows) / len(rows)
        for key, value in computed.items():
            if not math.isclose(value, metric[key], rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(f'Metric mismatch: {metric["model"]}:{key}')
    forecast = json.loads((BASELINE / 'forecast.json').read_text())
    selected = json.loads((BASELINE / 'selected_model.json').read_text())
    if forecast['model'] != selected['selected_model'] or selected != manifest['model_selection']:
        raise ValueError('Model identifier/selection mismatch')
    if forecast['forecast_origin'] != manifest['data']['data_cutoff'] or forecast['target_period'] != '2026 Q1':
        raise ValueError('Forecast cutoff/target mismatch')
    return dict(status='verified', checks=checks, metrics=metrics, forecast=forecast,
                baseline_manifest_sha256=digest(BASELINE / 'run_manifest.json'),
                later_evaluation=dict(status='not_performed', reason='No independently verified compatible calendar-quarter outcome acquired. The 13-week and June-August totals must not be scored as Q1/Q2/Q3 outcomes.'))


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
