import test from 'node:test';
import assert from 'node:assert/strict';
import { chronological, filterYears, configurationResults, signals, summary, timeline, mortalitySeries, monitoringSeries } from '../src/analytics.js';

test('chronological ordering uses year and quarter without mutating the response', () => {
  const rows = [{ year: 2025, quarter: 2 }, { year: 2024, quarter: 4 }, { year: 2025, quarter: 1 }];
  assert.deepEqual(chronological(rows).map(r => `${r.year}Q${r.quarter}`), ['2024Q4', '2025Q1', '2025Q2']);
  assert.equal(rows[0].quarter, 2);
});

test('year range filtering includes boundaries, respects missing years, and rejects inverted ranges', () => {
  const rows = [{ year: 2025, quarter: 4 }, { year: 2021, quarter: 1 }, { year: 2023, quarter: 2 }];
  assert.deepEqual(filterYears(rows, '2023', '2025').map(r => r.year), [2023, 2025]);
  assert.deepEqual(filterYears(rows, 2024, 2024), []);
  assert.deepEqual(filterYears(rows, 2025, 2021), []);
});

test('mortality chart leaves null gaps and never interpolates missing quarters', () => {
  const rows = [{ year: 2025, quarter: 1, suspected_deaths: 0 }, { year: 2025, quarter: 3, suspected_deaths: 300 }];
  assert.deepEqual(mortalitySeries(rows), { labels: ['2025 Q1', '2025 Q2', '2025 Q3'], values: [0, null, 300] });
  assert.equal(rows.length, 2);
});

test('configuration selection matches actual IDs and orders result quarters', () => {
  const rows = [{ configuration_id: 41, observation_year: 2024, observation_quarter: 3 }, { configuration_id: 9, observation_year: 2024, observation_quarter: 1 }, { configuration_id: 41, observation_year: 2024, observation_quarter: 1 }];
  assert.deepEqual(configurationResults(rows, '41').map(r => r.observation_quarter), [1, 3]);
  assert.deepEqual(configurationResults(rows, 8), []);
});

test('signals follow stored boolean flags, not inferred threshold crossings', () => {
  const rows = [{ signal_flag: false, statistic_value: 20, upper_limit: 1 }, { signal_flag: true, statistic_value: 0, upper_limit: 1 }, { signal_flag: 'true' }];
  assert.deepEqual(signals(rows), [rows[1]]);
});

test('EWMA chart preserves the exact stored retrospective flag and limits', () => {
  const row = { observation_year: 2022, observation_quarter: 3, statistic_value: -1.16480084, lower_limit: -0.9873333333, upper_limit: 0.9873333333, signal_flag: true };
  const data = monitoringSeries([row], { method: 'NB2-EWMA' });
  assert.deepEqual(data.labels, ['2022 Q3']);
  assert.equal(data.series[0].values[0], row.statistic_value);
  assert.equal(data.series[2].values[0], row.lower_limit);
  assert.equal(data.series[3].values[0], row.statistic_value);
});

test('two-sided CUSUM preserves separate components and excludes zero as a lower alarm line', () => {
  const row = { observation_year: 2024, observation_quarter: 1, statistic_value: 0.02169823338104968, cusum_positive: 0.02169823338104968, cusum_negative: 0, upper_limit: 0.15134510354478656, lower_limit: 0, signal_flag: false };
  const data = monitoringSeries([row], { method: 'CUSUM' });
  assert.equal(data.series[0].values[0], row.cusum_positive);
  assert.equal(data.series[1].values[0], 0);
  assert.equal(data.series[2].values[0], row.upper_limit);
  assert.equal(data.series.filter(s => s.limit).length, 1);
  assert.equal(data.series.at(-1).values[0], null);
  assert.ok(!data.labels.some(label => label.startsWith('2022')));
});

test('summary counts live response rows and distinguishes unavailable results from zero flags', () => {
  const states = { mortality: { state: 'ready', rows: [{}, {}] }, configurations: { state: 'ready', rows: [{}] }, results: { state: 'ready', rows: [{ signal_flag: true }, { signal_flag: false }] } };
  assert.deepEqual(summary(states), { quarters: 2, configurations: 1, results: 2, signals: 1 });
  states.results = { state: 'error', rows: [] };
  assert.equal(summary(states).signals, null);
  states.results = { state: 'ready', rows: [{ signal_flag: false }] };
  assert.equal(summary(states).signals, 0);
});

test('empty responses produce no fabricated observations or chart values', () => {
  assert.deepEqual(timeline([]), []);
  assert.deepEqual(mortalitySeries([]), { labels: [], values: [] });
  assert.deepEqual(signals([]), []);
  assert.ok(monitoringSeries([], { method: 'CUSUM' }).series.every(s => s.values.length === 0));
  assert.deepEqual(summary({}), { quarters: null, results: null, configurations: null, signals: null });
});
