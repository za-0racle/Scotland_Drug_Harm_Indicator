import { chronological, filterYears, configurationResults, signals, summary, isCusum, quarterIndex, quarterLabel } from './analytics.js';
import { describeDataset } from './database.js';
import { drawMortality, drawMonitoring, destroyCharts, destroyChart } from './charts.js';

const rowsOf = state => state?.state === 'ready' ? state.rows : [];
const labelOf = row => quarterLabel(quarterIndex(row.observation_year, row.observation_quarter));
const text = value => value === null || value === undefined ? 'Not stored' : String(value);
function node(tag, content, className) {
  const result = document.createElement(tag);
  if (content !== undefined) result.textContent = text(content);
  if (className) result.className = className;
  return result;
}

function table(target, rows, columns, caption) {
  target.replaceChildren();
  if (!rows.length) return;
  target.className = 'table-scroll';
  target.tabIndex = 0;
  target.setAttribute('role', 'region');
  target.setAttribute('aria-label', caption);
  const result = node('table');
  result.append(node('caption', caption));
  const head = node('thead');
  const headings = node('tr');
  for (const [heading] of columns) {
    const cell = node('th', heading);
    cell.scope = 'col';
    headings.append(cell);
  }
  head.append(headings);
  const body = node('tbody');
  for (const row of rows) {
    const tr = node('tr');
    if (row.signal_flag === true) tr.className = 'signal-row';
    for (const [, getter] of columns) tr.append(node('td', getter(row)));
    body.append(tr);
  }
  result.append(head, body);
  target.append(result);
}

export function mountDashboard(root, refresh) {
  root.innerHTML = `
    <a class="skip-link" href="#mortality">Skip to analysis</a>
    <header class="masthead"><div class="header-inner">
      <div><p class="eyebrow">SCOTLAND · RESEARCH ANALYTICS</p><h1>Scotland Drug Harm Indicator</h1>
      <p class="subtitle">Quarterly mortality and retrospective statistical monitoring</p></div>
      <div class="refresh"><button id="reload" type="button">Refresh data</button><p id="refresh-time" role="status">Not yet refreshed</p></div>
    </div></header>
    <main><aside class="disclaimer"><strong>Research prototype</strong><p>Statistical signals are retrospective model flags, not validated public health warnings or confirmed clinical alerts. This dashboard does not provide operational advice.</p></aside>
    <nav aria-label="Dashboard sections"><a href="#mortality">Mortality</a><a href="#monitoring">Statistical monitoring</a><a href="#methodology">Methodology & provenance</a></nav>
    <section aria-label="Dataset summary" id="summary" class="summary-grid"></section>
    <section class="panel" id="mortality" aria-labelledby="mortality-title">
      <div class="section-heading"><div><p class="eyebrow">01 / MORTALITY</p><h2 id="mortality-title">Quarterly suspected drug deaths</h2></div>
      <div class="filters"><label>From year<select id="year-start"></select></label><label>To year<select id="year-end"></select></label></div></div>
      <p id="mortality-status" role="status"></p><p class="muted">Observed counts only. Missing quarters remain gaps; no values are interpolated. Year filters apply to mortality only.</p>
      <div class="chart-wrap" id="mortality-chart-wrap"><canvas id="mortality-chart" role="img" aria-label="Quarterly suspected drug deaths; exact values in the observations table below"></canvas></div>
      <details><summary>View mortality observations and exact values</summary><div id="mortality-table"></div></details>
    </section>
    <section class="panel" id="monitoring" aria-labelledby="monitoring-title">
      <div class="section-heading"><div><p class="eyebrow">02 / STATISTICAL MONITORING</p><h2 id="monitoring-title">Retrospective model outputs</h2></div>
      <label class="model-control">Model configuration<select id="configuration"></select></label></div>
      <p id="monitoring-status" role="status"></p><p id="monitoring-context" class="context"></p>
      <div id="model-notes" class="model-notes"></div>
      <div class="chart-wrap" id="monitoring-chart-wrap"><canvas id="monitoring-chart" role="img" aria-label="Stored model statistics and limits; exact values and recorded flags in the results table below"></canvas></div>
      <div id="selected-signals" aria-live="polite"></div>
      <details><summary>View all selected model results and exact values</summary><div id="results-table"></div></details>
    </section>
    <section class="panel" id="recorded-signals" aria-labelledby="signals-title"><p class="eyebrow">03 / RECORDED FLAGS</p><h2 id="signals-title">Statistical signals across models</h2>
      <p>Only stored <code>signal_flag = true</code> records appear here. Flags are not recomputed from the plotted limits.</p><div id="signals-list" aria-live="polite"></div></section>
    <section class="panel" id="methodology" aria-labelledby="methodology-title"><p class="eyebrow">04 / METHODS & SOURCES</p><h2 id="methodology-title">Interpretation and data provenance</h2>
      <div class="method-grid"><article><h3>Mortality observations</h3><p>Police Scotland suspected drug deaths, January 2017–December 2025, published by the Scottish Government. Suspected deaths are provisional and distinct from registered drug-related deaths; this is not a clinical case dataset.</p>
      <a href="https://www.gov.scot/publications/suspected-drug-deaths-scotland-october-december-2025/" target="_blank" rel="noreferrer">Mortality source publication</a>
      <p class="muted">Source identified through the mortality source_id relationship during read-only review. The browser does not query the unapproved data_sources table.</p></article>
      <article><h3>Models and interpretation</h3><p>Rolling NB2-EWMA configurations use preceding quarters as a model baseline. The two-sided opioid-share CUSUM uses 2022–2023 calibration and 2024 monitoring. Statistics, limits, component values and parameters are displayed as stored, with no new fitting, threshold calculations or signal generation.</p>
      <p>Published RADAR alerts, RADAR intelligence reports and model-generated signals are different evidence types. Neither alerts nor intelligence are retrieved or represented by this dashboard.</p></article></div>
      <h3>Selected configuration parameters</h3><dl id="parameters" class="parameters"></dl><div id="computation-references" class="muted"></div>
      <p class="limitation">Limitations: retrospective analysis, a short monitoring series for CUSUM, possible revisions to source data and unverified model assumptions. Stored verification notes are retained. A recorded signal is not evidence of a confirmed public health event or causation.</p>
      <details><summary>Database integration verification</summary><ul id="verification"></ul></details>
    </section><footer>Scotland Drug Harm Indicator · Academic research prototype · Live, read-only Supabase data</footer></main>`;

  const byId = id => root.querySelector(`#${id}`);
  let states = {};
  let selectedId = '';
  let start = '';
  let end = '';
  let loading = false;
  const mortalityCanvas = byId('mortality-chart');
  const monitoringCanvas = byId('monitoring-chart');

  function status(id, state) {
    const result = state ?? { state: 'loading', rows: [] };
    byId(id).textContent = describeDataset(result);
    byId(id).dataset.state = result.state;
  }

  function populate(select, options, value) {
    select.replaceChildren(...options.map(([id, label]) => {
      const option = node('option', label);
      option.value = String(id);
      return option;
    }));
    select.value = String(value);
    select.disabled = loading || !options.length;
  }

  function renderSummary() {
    const totals = summary(states);
    byId('summary').replaceChildren(...[
      ['Mortality quarters', totals.quarters], ['Indicator results', totals.results],
      ['Model configurations', totals.configurations], ['Recorded statistical signals', totals.signals],
    ].map(([label, value]) => {
      const card = node('article', undefined, 'summary-card');
      card.append(node('p', label), node('strong', value === null ? '—' : value), node('small', value === null ? (loading ? 'Loading live data' : 'No accessible data') : 'All retrieved records · unfiltered'));
      return card;
    }));
  }

  function renderMortality() {
    destroyChart(mortalityCanvas);
    const state = states.mortality;
    status('mortality-status', state);
    byId('mortality').setAttribute('aria-busy', String(state?.state === 'loading'));
    const rows = filterYears(rowsOf(state), start, end);
    const visible = state?.state === 'ready' && rows.length > 0;
    byId('mortality-chart-wrap').hidden = !visible;
    if (state?.state === 'ready') byId('mortality-status').textContent = start > end ? 'Invalid year range: choose a start year no later than the end year.' : `${rows.length} observed quarters in the selected range; ${state.rows.length} retrieved in total.${rows.length ? ` ${rows[0].year} Q${rows[0].quarter} to ${rows.at(-1).year} Q${rows.at(-1).quarter}.` : ' No observations in this year range.'}`;
    table(byId('mortality-table'), rows, [['Quarter', row => `${row.year} Q${row.quarter}`], ['Suspected deaths', row => row.suspected_deaths]], 'Actual mortality observations in the selected year range');
    if (visible) drawMortality(mortalityCanvas, rows);
  }

  function renderMonitoring() {
    destroyChart(monitoringCanvas);
    const configurations = rowsOf(states.configurations);
    const config = configurations.find(row => String(row.configuration_id) === selectedId);
    const rows = config ? configurationResults(rowsOf(states.results), config.configuration_id) : [];
    const cusum = isCusum(config);
    status('monitoring-status', states.results);
    if (states.configurations?.state !== 'ready') byId('monitoring-status').textContent = `Configurations: ${describeDataset(states.configurations ?? { state: 'loading' })}`;
    else if (states.results?.state === 'ready') byId('monitoring-status').textContent = `${rows.length} stored results for ${config?.configuration_label ?? 'the selected configuration'}.${rows.length ? '' : ' No accessible results for this model.'}`;
    byId('monitoring').setAttribute('aria-busy', String(loading));
    byId('monitoring-chart-wrap').hidden = !rows.length;
    byId('monitoring-context').textContent = config ? (cusum ? 'Two-sided CUSUM · Calibration: 2022 Q1–2023 Q4 · Monitoring: 2024 Q1–Q4. Positive and negative components are separate stored series. Zero is the reset baseline, not a lower alarm threshold. The upper decision limit is shown on the stored scale.' : 'NB2-EWMA · Statistic and per-quarter limits are read directly from the database. Triangle markers identify stored retrospective flags; gaps indicate missing observations.') : '';
    byId('model-notes').replaceChildren();
    if (config) byId('model-notes').append(node('strong', config.configuration_label), node('p', config.baseline_description), node('p', config.notes));
    const flagged = signals(rows);
    byId('selected-signals').replaceChildren(node('p', rows.length ? (flagged.length ? `${flagged.length} recorded retrospective flag(s): ${flagged.map(labelOf).join(', ')}. These are not confirmed clinical or public health alerts.` : 'No recorded statistical signals for this configuration in the retrieved results.') : ''));
    const columns = [['Quarter', labelOf], ['Stored statistic', row => row.statistic_value]];
    if (cusum) columns.push(['Positive CUSUM', row => row.cusum_positive], ['Negative CUSUM', row => row.cusum_negative]);
    columns.push([cusum ? 'Reset baseline (stored lower limit)' : 'Lower limit', row => row.lower_limit], [cusum ? 'Upper decision limit' : 'Upper limit', row => row.upper_limit], ['Recorded flag', row => row.signal_flag === true ? 'Yes — retrospective' : 'No']);
    table(byId('results-table'), rows, columns, `${config?.configuration_label ?? 'Model'} — exact stored result values`);
    const parameters = byId('parameters');
    parameters.replaceChildren();
    if (config) for (const [field, label] of [['configuration_id', 'Configuration ID'], ['method', 'Method'], ['rolling_window_quarters', 'Rolling window (quarters)'], ['lambda_value', 'EWMA lambda'], ['limit_multiplier', 'Limit multiplier'], ['lower_limit', 'Configuration lower limit'], ['upper_limit', 'Configuration upper limit'], ['cusum_k_sigma', 'CUSUM K (SD)'], ['cusum_h_sigma', 'CUSUM H (SD)']]) parameters.append(node('dt', label), node('dd', config[field]));
    byId('computation-references').replaceChildren(...[...new Set(rows.map(row => row.computation_reference).filter(Boolean))].map(reference => node('p', `Stored computation reference: ${reference}`)));
    if (rows.length) drawMonitoring(monitoringCanvas, rows, config);
  }

  function renderSignals() {
    const target = byId('signals-list');
    target.replaceChildren();
    if (states.results?.state !== 'ready') { target.append(node('p', describeDataset(states.results ?? { state: 'loading' }))); return; }
    const flagged = chronological(signals(states.results.rows), 'observation_year', 'observation_quarter');
    if (!flagged.length) { target.append(node('p', 'No recorded statistical signals in the retrieved results.')); return; }
    for (const row of flagged) {
      const config = rowsOf(states.configurations).find(item => item.configuration_id === row.configuration_id);
      const card = node('article', undefined, 'flag-card');
      card.append(node('h3', `${labelOf(row)} · ${config?.configuration_label ?? row.configuration?.configuration_label ?? `Configuration ${row.configuration_id}`}`), node('p', `Stored statistic: ${row.statistic_value}; lower limit: ${text(row.lower_limit)}; upper limit: ${text(row.upper_limit)}.`), node('p', 'Retrospective model flag only. This is not a confirmed clinical alert or validated public health warning.'));
      target.append(card);
    }
  }

  byId('reload').addEventListener('click', refresh);
  byId('year-start').addEventListener('change', event => { start = event.target.value; renderMortality(); });
  byId('year-end').addEventListener('change', event => { end = event.target.value; renderMortality(); });
  byId('configuration').addEventListener('change', event => { selectedId = event.target.value; renderMonitoring(); });

  return {
    loading() {
      destroyCharts();
      loading = true;
      states = Object.fromEntries(['mortality', 'configurations', 'results'].map(key => [key, { state: 'loading', rows: [] }]));
      byId('reload').disabled = true;
      for (const id of ['year-start', 'year-end', 'configuration']) byId(id).disabled = true;
      byId('refresh-time').textContent = 'Refreshing live data…';
      byId('verification').replaceChildren();
      renderSummary(); renderMortality(); renderMonitoring(); renderSignals();
    },
    update(nextStates) {
      states = nextStates;
      loading = false;
      const years = [...new Set(rowsOf(states.mortality).map(row => row.year))].sort((a, b) => a - b);
      if (!years.some(year => String(year) === start)) start = String(years[0] ?? '');
      if (!years.some(year => String(year) === end)) end = String(years.at(-1) ?? '');
      populate(byId('year-start'), years.map(year => [year, year]), start);
      populate(byId('year-end'), years.map(year => [year, year]), end);
      const configs = rowsOf(states.configurations);
      if (!configs.some(config => String(config.configuration_id) === selectedId)) selectedId = String(signals(rowsOf(states.results))[0]?.configuration_id ?? configs[0]?.configuration_id ?? '');
      populate(byId('configuration'), configs.map(config => [config.configuration_id, config.configuration_label]), selectedId);
      byId('reload').disabled = false;
      const allReady = Object.values(states).every(state => state.state === 'ready');
      byId('refresh-time').textContent = `${allReady ? 'Data refreshed' : 'Refresh completed with unavailable datasets'} · ${new Date().toLocaleString()}`;
      byId('verification').replaceChildren(...Object.entries(states).map(([key, state]) => node('li', `${key}: ${describeDataset(state)}`)));
      renderSummary(); renderMortality(); renderMonitoring(); renderSignals();
    },
  };
}
