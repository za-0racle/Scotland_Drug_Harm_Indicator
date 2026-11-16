import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {
  categoryOf, compatibleSubstances, selectSubstances, substanceCsv, substanceHeatmap,
  substanceOptions, substanceProfile, substanceRanking,
} from '../../../src/platform/substance-data.js';
import {periodLabel, prepareChart} from '../../../src/platform/chart-data.js';

const directory = new URL('.', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, directory), 'utf8'));
const files = ['legacy-presentation.json', 'legacy-substance-export.csv'];
if (files.some(name => existsSync(new URL(name, directory)))) {
  throw new Error('Task 08F presentation evidence already exists; capture refused without overwriting.');
}

const legacy = read('legacy-response.json');
const rows = legacy.data;
const options = substanceOptions(rows);
const area = options.areas[0][0];
const periods = options.periods;
const filters = {area, category: '', from: periods[0].key, to: periods.at(-1).key};
const selected = selectSubstances(rows, filters);
const chart = prepareChart(selected);
const grid = substanceHeatmap(selected);
const rankings = periods.map(period => ({
  period: period.key,
  rows: substanceRanking(selected, period.key).rows.map(row => ({
    category: categoryOf(row), value: row.observed_value, period: periodLabel(row),
  })),
}));
const profiles = options.categories.map(category => {
  const profile = substanceProfile(selected, category, 'forensic');
  return {
    category: profile.category,
    source: profile.source,
    definition: profile.definition,
    observations: profile.observations,
    periods: profile.periods,
    units: profile.units,
    geographies: profile.geographies,
    denominator: profile.denominator,
    limitations: profile.limitations,
    provenance: profile.provenance,
    note: profile.note,
    values: profile.history.map(row => [periodLabel(row), row.observed_value]),
  };
});
const csv = substanceCsv(selected, {
  ...legacy.metadata,
  filters,
  search: '',
});
const expected = {
  baseline_api_sha256: createHash('sha256').update(readFileSync(new URL('legacy-response.json', directory))).digest('hex'),
  contract_version: 'legacy',
  observation_count: rows.length,
  selected_count: selected.length,
  categories: options.categories,
  periods: periods.map(period => period.key),
  chart: {
    labels: chart.labels,
    regular: chart.regular,
    warnings: chart.warnings,
    datasets: chart.datasets.map(dataset => ({
      label: dataset.label,
      showLine: dataset.showLine,
      metadata: dataset.metadata,
      points: dataset.points.map(point => ({
        period: point.period,
        value: point.value,
        missingPeriod: point.missingPeriod,
      })),
    })),
  },
  heatmap: {
    state: grid.state,
    periods: grid.periods.map(period => period.key),
    rows: grid.rows.map(row => ({category: row.category, values: row.values})),
  },
  rankings,
  profiles,
};
const json = JSON.stringify(expected, null, 2) + '\n';
writeFileSync(new URL('legacy-presentation.json', directory), json, {encoding: 'utf8', flag: 'wx'});
writeFileSync(new URL('legacy-substance-export.csv', directory), csv, {encoding: 'utf8', flag: 'wx'});
const summary = {
  presentation_sha256: createHash('sha256').update(json).digest('hex'),
  csv_sha256: createHash('sha256').update(csv).digest('hex'),
  csv_bytes: Buffer.byteLength(csv),
  chart_series: chart.datasets.length,
  ranking_periods: rankings.length,
  profile_count: profiles.length,
};
writeFileSync(new URL('presentation-capture-summary.json', directory), JSON.stringify(summary, null, 2) + '\n', {encoding: 'utf8', flag: 'wx'});
console.log(JSON.stringify(summary, null, 2));
