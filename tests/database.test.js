import test from 'node:test';
import assert from 'node:assert/strict';
import { datasets, readDataset, loadDataset, describeDataset } from '../src/database.js';

function fakeClient(responses) {
  const calls = [];
  return {
    calls,
    from(table) {
      calls.push(['from', table]);
      return {
        select(columns, options) { calls.push(['select', columns, options]); return this; },
        order(column, options) { calls.push(['order', column, options]); return this; },
        async range(start, end) { calls.push(['range', start, end]); return responses.shift(); },
      };
    },
  };
}

test('reader requests only reviewed tables and explicit columns', () => {
  assert.deepEqual(Object.values(datasets).map(d => d.table), ['mortality_quarterly', 'indicator_configurations', 'indicator_results']);
  for (const d of Object.values(datasets)) assert.ok(!d.columns.includes('*'));
  assert.match(datasets.results.columns, /indicator_results_configuration_id_fkey\(configuration_label\)/);
});

test('mortality pagination preserves chronological query ordering and fetches all pages', async () => {
  const rows = [{ year: 2024, quarter: 4 }, { year: 2025, quarter: 1 }, { year: 2025, quarter: 2 }];
  const client = fakeClient([{ data: rows.slice(0, 2), count: 3 }, { data: rows.slice(2), count: 3 }]);
  assert.deepEqual(await readDataset(client, datasets.mortality, 2), rows);
  assert.deepEqual(client.calls.filter(c => c[0] === 'range'), [['range', 0, 1], ['range', 2, 3]]);
  assert.deepEqual(client.calls.filter(c => c[0] === 'order').slice(0, 2), [['order', 'year', { ascending: true }], ['order', 'quarter', { ascending: true }]]);
});

test('result query orders quarters and retains associated configuration labels', async () => {
  const row = { configuration: { configuration_label: 'Reviewed model' } };
  const client = fakeClient([{ data: [row], count: 1 }]);
  const result = await loadDataset(client, datasets.results);
  assert.equal(result.state, 'ready');
  assert.equal(result.rows[0].configuration.configuration_label, 'Reviewed model');
  assert.deepEqual(client.calls.filter(c => c[0] === 'order').map(c => c[1]), datasets.results.order);
});

test('RLS-style empty responses are empty, never successful loads', async () => {
  const result = await loadDataset(fakeClient([{ data: [], count: 0 }]), datasets.mortality);
  assert.equal(result.state, 'empty');
  assert.match(describeDataset(result), /0 accessible records.*RLS/);
  assert.doesNotMatch(describeDataset(result), /success|loaded/i);
});

test('permission errors retain useful diagnostics', async () => {
  const result = await loadDataset(fakeClient([{ error: { message: 'permission denied', code: '42501' }, data: null }]), datasets.results);
  assert.equal(result.state, 'error');
  assert.match(describeDataset(result), /indicator_results: permission denied \(42501\)/);
});

test('missing configuration and network errors become error states', async () => {
  assert.equal((await loadDataset(null, datasets.mortality)).state, 'error');
  const client = { from() { throw new Error('Network unavailable'); } };
  assert.match((await loadDataset(client, datasets.mortality)).message, /Network unavailable/);
});

test('loading and missing related labels have distinct messages', () => {
  assert.equal(describeDataset({ state: 'loading' }), 'Loading records…');
  assert.match(describeDataset({ state: 'ready', rows: [{ configuration: null }] }), /1 configuration labels are unavailable/);
});

test('incomplete server-capped responses fail rather than claim a full load', async () => {
  const client = fakeClient([{ data: [{ year: 2025 }], count: 3 }]);
  await assert.rejects(readDataset(client, datasets.mortality, 2), /incomplete response/);
});

test('empty page before the reported count is reached cannot report a successful partial load', async () => {
  const client = fakeClient([{ data: [], count: 3 }]);
  await assert.rejects(readDataset(client, datasets.mortality), /incomplete response/);
});

test('malformed responses and invalid pagination are rejected', async () => {
  await assert.rejects(readDataset(fakeClient([{ data: null }]), datasets.mortality), /invalid database response/);
  await assert.rejects(readDataset(fakeClient([]), datasets.mortality, 0), /Invalid page size/);
});
