"""On-demand forecasts from verified death and forensic detection series."""
from datetime import datetime, timezone
from functools import lru_cache

from openpyxl import load_workbook

from analysis.data import WORKBOOK, period, validate
from analysis.models import MODELS
from backend.repositories.artifacts import ArtifactRepository
from backend.services.multihorizon import evaluate_horizons, horizon_forecast, horizon_metrics

INDICATOR = 'police_suspected_drug_deaths'
SUBSTANCE = 'all'
SAMPLE_GEOGRAPHY = 'Scotland forensic testing sample'
SUBSTANCES = ('Opioids', 'Prescribable Benzodiazepines', 'Street Benzodiazepines',
              'All Benzodiazepines', 'Dissociatives', 'Gabapentinoids', 'Stimulants')


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
        records = _source_rows(workbook['A - Police Division'])
        result = []
        for record in records:
            name, values = record[0], record[1:37]
            if isinstance(name, str) and all(type(value) is int and value >= 0 for value in values):
                result.append('Scotland' if name.strip() == 'Total' else name.split(':', 1)[-1].strip())
        return result
    finally:
        workbook.close()


def _death_series(geography):
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=True)
    try:
        records = _source_rows(workbook['A - Police Division'])
        match = next((r for r in records if isinstance(r[0], str) and
                      ('Scotland' if r[0].strip() == 'Total' else r[0].split(':', 1)[-1].strip()) == geography), None)
        if match is None or not all(type(value) is int and value >= 0 for value in (match[1:37] if match else [])):
            raise ValueError('This area is unavailable or contains suppressed quarterly values.')
        return validate([dict(year=2017 + i // 4, quarter=i % 4 + 1, suspected_deaths=value)
                         for i, value in enumerate(match[1:37])])
    finally:
        workbook.close()


@lru_cache(maxsize=8)
def _substance_rows(category):
    rows, _ = ArtifactRepository().load('forensic')
    selected = [r for r in rows if r.get('indicator_id') == f'forensic:{category}' and
                r.get('geography') == SAMPLE_GEOGRAPHY]
    selected.sort(key=lambda r: r.get('ordinal', 0))
    if len(selected) != 30 or any(r.get('unit') != 'detection_count' or type(r.get('observed_value')) is not int
                                  or r['observed_value'] < 0 for r in selected):
        raise ValueError('Verified quarterly substance detection data are incomplete; no forecast is produced.')
    parsed = [tuple(map(int, r['period'].replace(' Q', '-').split('-'))) for r in selected]
    indexes = [year * 4 + quarter - 1 for year, quarter in parsed]
    if indexes != list(range(indexes[0], indexes[0] + 30)):
        raise ValueError('Verified quarterly substance detection periods are inconsistent; no forecast is produced.')
    return validate([dict(year=year, quarter=quarter, suspected_deaths=r['observed_value'])
                     for r, (year, quarter) in zip(selected, parsed)])


@lru_cache(maxsize=32)
def _evaluation(geography, category):
    rows = _death_series(geography) if category == SUBSTANCE else _substance_rows(category)
    predictions = evaluate_horizons(rows, horizons=(1, 4, 8, 12), min_train=24 if category == SUBSTANCE else 16)
    return rows, predictions, horizon_metrics(predictions)


@lru_cache(maxsize=512)
def _point_forecast(geography, category, model, horizon):
    rows, _, _ = _evaluation(geography, category)
    return horizon_forecast(model, [row['suspected_deaths'] for row in rows], horizon)


def available_substances():
    return [dict(id='all', label='All suspected drug deaths', outcome='suspected_deaths', unit='deaths')]+[
        dict(id=name, label=f'{name} (forensic detections)', outcome='toxicology_detections', unit='detections') for name in SUBSTANCES]


def generate(geography='Scotland', indicator=INDICATOR, substance=SUBSTANCE, horizon=None,
             model='nb2_trend', year=None, quarter=None):
    if indicator != INDICATOR:
        raise ValueError('Choose drug deaths as the quarterly outcome.')
    if substance not in ('all', *SUBSTANCES):
        raise ValueError('Choose a listed substance category.')
    if substance == SUBSTANCE:
        if geography not in available_geographies():
            raise ValueError('Choose an available geography with 36 complete quarterly observations.')
        display_geography, last_label = geography, '2025 Q4'
        cutoff_note = '2025 Q4'
    else:
        display_geography = SAMPLE_GEOGRAPHY
        last_label = None
        cutoff_note = '2026 Q1'
    if model != 'auto' and model not in MODELS:
        raise ValueError('Unknown forecast model.')
    rows, all_predictions, evaluation = _evaluation(display_geography if substance == SUBSTANCE else 'Scotland', substance)
    last_idx = rows[-1]['year'] * 4 + rows[-1]['quarter'] - 1
    if year is None and quarter is None and horizon is not None:
        if type(horizon) is not int or not 1 <= horizon <= 12:
            raise ValueError('Forecast horizon must be from 1 to 12 quarters.')
        target_idx = last_idx + horizon
    else:
        year = 2028 if year is None else year
        quarter = 4 if quarter is None else quarter
        if type(year) is not int or year not in (2026, 2027, 2028) or type(quarter) is not int or quarter not in (1, 2, 3, 4):
            raise ValueError('Choose a year from 2026 to 2028 and a quarter from Q1 to Q4.')
        target_idx = year * 4 + quarter - 1
    horizon = target_idx - last_idx
    if not 1 <= horizon <= 12:
        raise ValueError(f'The selected quarter must be after the last observation ({period(last_idx)}).')
    horizon_scores = [row for row in evaluation if row['horizon'] == horizon and row['eligible_for_selection']]
    selection_scores = horizon_scores or [row for row in evaluation if row['horizon'] == 1 and row['eligible_for_selection']]
    warnings = []
    if not horizon_scores:
        warnings.append(f'{horizon}-quarter backtesting has too few successful historical origins; model comparison falls back to 1-quarter evaluation. Long-horizon performance is uncertain.')
    if model == 'auto':
        ranked = sorted(selection_scores, key=lambda row: (row['mae'], row['rmse'], MODELS.index(row['model'])))
        candidates = [row['model'] for row in ranked] or ['naive']
    else:
        candidates = [model]
    forecast_geography = display_geography if substance == SUBSTANCE else 'Scotland'
    future = selected = None
    for candidate in candidates:
        try:
            generated = []
            candidate_warnings = []
            predicted = _point_forecast(forecast_geography, substance, candidate, horizon)
            candidate_warnings.extend(predicted.warnings)
            generated.append(dict(target_period=period(target_idx), horizon_quarters=horizon,
                predicted=max(0, int(round(predicted.predicted))), lower80=max(0, int(predicted.lower80)),
                upper80=max(0, int(round(predicted.upper80))), lower95=max(0, int(predicted.lower95)),
                upper95=max(0, int(round(predicted.upper95))), model=candidate,
                interval_method=predicted.interval_method, model_parameters=predicted.diagnostics))
            selected, future = candidate, generated
            warnings.extend(dict.fromkeys(candidate_warnings))
            break
        except Exception:
            continue
    if future is None:
        raise ValueError('No selected model could fit the available history; no forecast was generated.')
    is_death = substance == SUBSTANCE
    unit = 'deaths' if is_death else 'detections'
    outcome = 'Police Scotland suspected drug deaths' if is_death else f'{substance} forensic toxicology detections'
    history = [dict(observation_period=f"{r['year']} Q{r['quarter']}", value=r['suspected_deaths'], status='historical') for r in rows]
    limitations = ['Forecasts are research estimates based on verified historical observations, not operational warnings.',
        'Backtesting is retrospective and does not validate prospective forecast accuracy.',
        'Prediction intervals are approximate observation intervals; NB2 plug-in intervals exclude parameter uncertainty.']
    if is_death:
        limitations += ['Quarterly Police Scotland suspected deaths are distinct from registered drug-related deaths and toxicology detections.',
                        'Substance-specific quarterly histories are not available for the suspected death outcome.']
        source = 'Police Scotland suspected drug deaths by Police Division'
        first = '2017 Q1'
    else:
        limitations += ['These are overlapping toxicology detections in forensic tests, not substance-specific deaths, causal attribution, population prevalence, or unique people.',
                        'The forensic testing sample denominator is unavailable; category counts must not be compared as population rates.']
        source = 'Verified Scotland forensic testing sample quarterly detections'
        first = history[0]['observation_period']
    limitations.append(f'Latest source observation: {cutoff_note}; later elapsed quarters are not treated as refreshed observations.')
    return dict(filters=dict(geography=display_geography, indicator=indicator, substance=substance,
                             year=year, quarter=quarter, horizon_quarters=horizon, model=model),
        historical=history, forecasts=future, selected_model=selected,
        model_evaluation=[r for r in evaluation if r['horizon'] == horizon],
        data_coverage=dict(first=first, last=history[-1]['observation_period'], observations=len(rows), source=source,
                           unit=unit, outcome=outcome, complete_quarters=True),
        generated_at=datetime.now(timezone.utc).isoformat(), warnings=warnings, limitations=limitations,
        interval_note='Point counts and interval bounds are rounded for display; interval bounds are clipped at zero.',
        backtest_method='Expanding-window direct-horizon evaluation; each origin is fitted using observations through that origin only.',
        backtest_horizons=[dict(horizon=h, origins=sum(1 for p in all_predictions if p['horizon']==h and p['model']=='naive' and p['status']=='ok')) for h in (1,4,8,12)])


def generate_many(geography, substances, years, quarters, model='nb2_trend'):
    substances = list(dict.fromkeys(substances))
    years = list(dict.fromkeys(years))
    quarters = list(dict.fromkeys(quarters))
    if not substances or any(value not in ('all', *SUBSTANCES) for value in substances):
        raise ValueError('Select one or more supported substance categories.')
    if not years or any(type(value) is not int or value not in (2026, 2027, 2028) for value in years):
        raise ValueError('Select one or more years from 2026 to 2028.')
    if not quarters or any(type(value) is not int or value not in (1, 2, 3, 4) for value in quarters):
        raise ValueError('Select one or more quarters from Q1 to Q4.')
    if len(substances) * len(years) * len(quarters) > 120:
        raise ValueError('Choose up to 120 category, year and quarter combinations at a time.')
    results, skipped = [], []
    for substance in substances:
        for year in sorted(years):
            for quarter in sorted(quarters):
                try:
                    results.append(generate(geography, substance=substance, year=year, quarter=quarter, model=model))
                except ValueError as error:
                    skipped.append(dict(substance=substance, year=year, quarter=quarter, reason=str(error)))
    return results, skipped
