import './style.css';
import { getSupabase } from './supabase.js';
import { datasets, loadDataset, describeDataset } from './database.js';

const app = document.querySelector('#app');
app.innerHTML = `<main>
  <header><p class="eyebrow">Research database verification</p>
  <h1>Scotland Drug Harm Indicator</h1>
  <p>Live aggregate observations and research model outputs. Prototype; not a validated warning service.</p></header>
  <p class="notice">Database read policies require manual review and approval. Empty responses do not confirm a successful data load.</p>
  <button id="reload" type="button">Reload data</button>
  <div id="datasets"></div>
</main>`;

const previews = {
  mortality: { title: 'Quarterly mortality', columns: [['year', 'Year'], ['quarter', 'Quarter'], ['suspected_deaths', 'Suspected deaths']] },
  configurations: { title: 'Indicator configurations', columns: [['configuration_label', 'Configuration'], ['method', 'Method'], ['baseline_description', 'Baseline'], ['notes', 'Verification notes']] },
  results: { title: 'Indicator results', columns: [['observation_year', 'Year'], ['observation_quarter', 'Quarter'], ['configuration', 'Configuration'], ['statistic_value', 'Statistic'], ['lower_limit', 'Lower limit'], ['upper_limit', 'Upper limit'], ['signal_flag', 'Signal']] },
};

function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

function render(section, key, result) {
  section.replaceChildren(element('h2', previews[key].title));
  section.dataset.state = result.state;
  section.setAttribute('aria-busy', String(result.state === 'loading'));
  const status = element('p', describeDataset(result));
  status.setAttribute('role', 'status');
  section.append(status);
  if (result.state !== 'ready') return;
  const wrapper = element('div');
  wrapper.className = 'table-scroll';
  wrapper.tabIndex = 0;
  wrapper.setAttribute('role', 'region');
  wrapper.setAttribute('aria-label', `${previews[key].title} preview`);
  const table = element('table');
  table.append(element('caption', `Preview: first ${Math.min(result.rows.length, 8)} of ${result.rows.length} returned records`));
  const head = element('thead');
  const headings = element('tr');
  for (const [, label] of previews[key].columns) {
    const th = element('th', label);
    th.scope = 'col';
    headings.append(th);
  }
  head.append(headings);
  table.append(head);
  const body = element('tbody');
  for (const row of result.rows.slice(0, 8)) {
    const tr = element('tr');
    for (const [column] of previews[key].columns) {
      let value = row[column];
      if (column === 'configuration') value = value?.configuration_label ?? 'Label unavailable';
      if (typeof value === 'boolean') value = value ? 'Yes' : 'No';
      tr.append(element('td', value === null || value === undefined ? '—' : String(value)));
    }
    body.append(tr);
  }
  table.append(body);
  wrapper.append(table);
  section.append(wrapper);
}

async function init() {
  const reload = document.querySelector('#reload');
  reload.disabled = true;
  const container = document.querySelector('#datasets');
  container.replaceChildren();
  let client;
  let setupError;
  try {
    client = getSupabase();
  } catch (error) {
    setupError = error.message;
  }
  await Promise.all(Object.entries(datasets).map(async ([key, definition]) => {
    const section = element('section');
    container.append(section);
    render(section, key, { state: 'loading', rows: [] });
    const result = setupError ? { state: 'error', rows: [], message: setupError } : await loadDataset(client, definition);
    render(section, key, result);
  }));
  reload.disabled = false;
}
document.querySelector('#reload').addEventListener('click', init);
init();
