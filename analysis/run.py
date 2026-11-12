"""Run with: python -m analysis.run. No network or Supabase access."""
import argparse
import csv
import importlib.metadata
import json
import platform
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .backtesting import MIN_TRAIN, evaluate, metrics, rank_models
from .data import ROOT, load_verified, sha256, period
from .models import forecast

VERSION = 'phase2-1.0.0'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) else value for key, value in row.items()})


def run(output_dir=None, timestamp=None):
    output_dir = Path(output_dir) if output_dir else ROOT / 'analysis/outputs'
    timestamp = timestamp or datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows, source = load_verified()
    predictions, diagnostics = evaluate(rows)
    evaluation = metrics(predictions)
    ranked = rank_models(evaluation)
    values = [row['suspected_deaths'] for row in rows]
    final = None
    for candidate in ranked:
        try:
            final = forecast(candidate['model'], values)
            selected = candidate
            diagnostics.append(dict(model=selected['model'], stage='full_data_fit', status='ok',
                                    diagnostics=final.diagnostics, warnings=final.warnings))
            break
        except Exception as error:
            diagnostics.append(dict(model=candidate['model'], stage='full_data_fit', status='failed',
                                    error=str(error), warnings=getattr(error, 'notes', [])))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'diagnostics.json', diagnostics)
    if final is None:
        raise RuntimeError('All final fits failed; diagnostics saved, no forecast published')
    last = rows[-1]['year'] * 4 + rows[-1]['quarter'] - 1
    projection = dict(model=selected['model'], forecast_origin=period(last), target_period=period(last + 1),
                      horizon_quarters=1, issued_at_utc=timestamp,
                      interpretation='Elapsed-period, data-cutoff-based forecast; not a current future prediction',
                      geography=source['geography'], outcome=source['outcome'], **asdict(final))
    selection = dict(selected_model=selected['model'], selection_rule='Lowest expanding-window one-step MAE among models completing every common origin; RMSE then predefined model order break ties; final-fit failure falls back in that order',
                     min_training_quarters=MIN_TRAIN, training_window_reason='24 quarters provide six annual cycles, with 12 common test origins. This pragmatic choice limits parameter estimation risk; it is not evidence of adequacy or validation.',
                     ranking=[row['model'] for row in ranked], selected_metrics=selected,
                     limitation='Model selection and reported performance use the same 12 origins; no independent post-selection test set. Scores are exploratory, not clinical or operational validation.')
    write_csv(output_dir / 'validated_mortality.csv', rows)
    write_csv(output_dir / 'rolling_origin_predictions.csv', predictions)
    write_json(output_dir / 'model_metrics.json', evaluation)
    write_csv(output_dir / 'model_metrics.csv', evaluation)
    write_json(output_dir / 'selected_model.json', selection)
    write_json(output_dir / 'forecast.json', projection)
    write_csv(output_dir / 'forecast.csv', [projection])
    review = ROOT / 'analysis/newer_data_review.json'
    code_files = sorted((ROOT / 'analysis').glob('*.py'))
    requirements = ROOT / 'analysis/requirements.txt'
    manifest = dict(model_version=VERSION, executed_at_utc=timestamp, python=platform.python_version(),
                    packages={name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'pandas', 'statsmodels', 'openpyxl', 'pytest')},
                    data=source, model_selection=selection,
                    evaluation_start=predictions[0]['target'], evaluation_end=predictions[-1]['target'],
                    evaluation_kind='Retrospective rolling-origin evaluation on the current frozen vintage; historical publication vintages unavailable',
                    uncertainty='Approximate model-specific one-step observation intervals; NB2 excludes parameter uncertainty; Gaussian baselines/SES assume stable errors. Evaluate empirical coverage; do not interpret control limits as forecast intervals.',
                    newer_data_review=json.loads(review.read_text(encoding='utf-8')),
                    source_code_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in code_files + [requirements, review]},
                    output_hashes={p.name: sha256(p) for p in sorted(output_dir.iterdir()) if p.is_file() and p.name != 'run_manifest.json'})
    write_json(output_dir / 'run_manifest.json', manifest)
    return dict(evaluation=evaluation, forecast=projection, selection=selection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'analysis/outputs')
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
