"""On-demand forecasts from the verified Police Scotland quarterly workbook."""
from datetime import datetime, timezone
from functools import lru_cache

from openpyxl import load_workbook

from analysis.data import WORKBOOK, period, validate
from analysis.models import MODELS
from backend.services.multihorizon import evaluate_horizons, horizon_forecast, horizon_metrics

INDICATOR = 'police_suspected_drug_deaths'
SUBSTANCE = 'all'


def _source_rows(sheet):
    if sheet.max_column != 37:
        raise ValueError('The verified workbook does not contain the expected 36 quarterly columns.')
    previous_year = None
    quarter_names = ['January to March', 'April to June', 'July to September', 'October to December']
    for offset in range(36):
        column = offset + 2
        previous_year = sheet.cell(3, column).value or previous_year
        if type(previous_year) is not int or previous_year != 2017 + offset // 4 or sheet.cell(4, column).value != quarter_names[offset % 4]:
            raise ValueError('The workbook quarter headers are inconsistent; no forecast is produced.')
    records = list(sheet.iter_rows(min_row=5, max_row=18, values_only=True))
    names = [row[0].strip() for row in records if isinstance(row[0], str)]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate geographical rows in the workbook; no forecast is produced.')
    return records


def available_geographies():
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    try:
        sheet = workbook['A - Police Division']
        records = _source_rows(sheet)
        result = []
        for record in records:
            name = record[0]
            values = record[1:37]
            if not isinstance(name, str) or not all(type(value) is int and value >= 0 for value in values):
                continue
            key = 'Scotland' if name.strip() == 'Total' else name.split(':', 1)[-1].strip()
            result.append(key)
        return result
    finally:
        workbook.close()


def _series(geography):
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    try:
        sheet = workbook['A - Police Division']
        records = _source_rows(sheet)
        match = next((r for r in records if isinstance(r[0], str) and
                      ('Scotland' if r[0].strip() == 'Total' else r[0].split(':', 1)[-1].strip()) == geography), None)
        if match is None:
            raise ValueError('This area is unavailable or contains suppressed quarterly values.')
        if not all(type(value) is int and value >= 0 for value in match[1:37]):
            raise ValueError('This area has suppressed or missing quarters; no forecast is produced.')
        return [dict(year=2017 + i // 4, quarter=i % 4 + 1,
                     suspected_deaths=value) for i, value in enumerate(match[1:37])]
    finally:
        workbook.close()


@lru_cache(maxsize=16)
def _evaluation(geography):
    rows = validate(_series(geography))
    predictions = evaluate_horizons(rows, horizons=(1, 4, 8, 12), min_train=24)
    return rows, predictions, horizon_metrics(predictions)


def generate(geography='Scotland', indicator=INDICATOR, substance=SUBSTANCE,
             horizon=12, model='auto'):
    if geography not in available_geographies():
        raise ValueError('Choose an available geography with 36 complete quarterly observations.')
    if indicator != INDICATOR:
        raise ValueError('Only Police Scotland suspected drug deaths are available as a quarterly forecasting indicator.')
    if substance != SUBSTANCE:
        raise ValueError('Substance-specific quarterly counts are not present in this dataset.')
    if type(horizon) is not int or not 1 <= horizon <= 12:
        raise ValueError('Forecast horizon must be from 1 to 12 quarters.')
    if model != 'auto' and model not in MODELS:
        raise ValueError('Unknown forecast model.')

    rows, all_predictions, evaluation = _evaluation(geography)
    horizon_scores = [row for row in evaluation if row['horizon'] == horizon and row['eligible_for_selection']]
    warnings = [f'{horizon}-quarter backtesting has fewer than two successful historical origins; selection uses the 1-quarter expanding-window evaluation. Long-horizon performance is uncertain.'] if not horizon_scores else []
    selection_scores = horizon_scores or [row for row in evaluation if row['horizon'] == 1 and row['eligible_for_selection']]
    if model == 'auto':
        ranked = sorted(selection_scores, key=lambda row: (row['mae'], row['rmse'], MODELS.index(row['model'])))
        candidates = [row['model'] for row in ranked] or ['naive']
        if not selection_scores:
            warnings.append('There are too few successful backtests to select a model reliably; the transparent naïve baseline is shown.')
    else:
        candidates = [model]
    training = [row['suspected_deaths'] for row in rows]
    future = None
    selected = None
    last = rows[-1]['year'] * 4 + rows[-1]['quarter'] - 1
    for candidate in candidates:
        try:
            candidate_forecasts = []
            candidate_warnings = []
            for step in range(1, horizon + 1):
                predicted = horizon_forecast(candidate, training, step)
                candidate_warnings.extend(predicted.warnings)
                candidate_forecasts.append(dict(target_period=period(last + step), horizon_quarters=step,
                    predicted=max(0, int(round(predicted.predicted))),
                    lower80=max(0, int(predicted.lower80)), upper80=max(0, int(round(predicted.upper80))),
                    lower95=max(0, int(predicted.lower95)), upper95=max(0, int(round(predicted.upper95))),
                    model=candidate, interval_method=predicted.interval_method, model_parameters=predicted.diagnostics))
            selected, future = candidate, candidate_forecasts
            warnings.extend(dict.fromkeys(candidate_warnings))
            if model == 'auto' and candidate != candidates[0]:
                warnings.append(f'The highest-ranked model did not fit the full series; {candidate} was used as the next eligible model.')
            break
        except Exception:
            continue
    if future is None:
        raise ValueError('No selected model could fit the available history; no forecast was generated.')
    history = [dict(observation_period=f"{row['year']} Q{row['quarter']}", value=row['suspected_deaths'], status='historical') for row in rows]
    selected_metrics = [row for row in evaluation if row['horizon'] == horizon]
    return dict(filters=dict(geography=geography, indicator=indicator, substance=substance,
                             horizon_quarters=horizon, model=model),
        historical=history, forecasts=future, selected_model=selected,
        model_evaluation=selected_metrics, data_coverage=dict(first='2017 Q1', last='2025 Q4', observations=len(rows),
            source='Police Scotland suspected drug deaths by Police Division', unit='deaths', complete_quarters=True),
        generated_at=datetime.now(timezone.utc).isoformat(), warnings=warnings,
        limitations=['Research estimate based only on data through 2025 Q4; elapsed 2026 quarters are not refreshed observations.',
            'Quarterly Police Scotland suspected deaths are distinct from registered drug-related deaths and toxicology detections.',
            'Historical backtesting is retrospective and does not validate forecast accuracy; 2026–2028 outcomes have not been prospectively validated.',
            'Prediction intervals are approximate observation intervals; Gaussian bounds use square-root horizon scaling, and NB2 plug-in intervals exclude parameter uncertainty.',
            'Substance-specific quarterly histories are not available in the selected source.'],
        interval_note='Point counts and interval bounds are rounded for display; interval bounds are clipped at zero.',
        backtest_method='Expanding-window direct-horizon evaluation; each origin is fitted using observations through that origin only.',
        backtest_horizons=[dict(horizon=h, origins=sum(1 for p in all_predictions if p['horizon']==h and p['model']=='naive' and p['status']=='ok')) for h in (1,4,8,12)])
