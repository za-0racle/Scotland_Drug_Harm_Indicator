import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {substanceCsv, substanceOptions} from '../../../src/platform/substance-data.js';

const directory = new URL('.', import.meta.url);
const output = new URL('legacy-screen-export.csv', directory);
const summaryOutput = new URL('screen-export-capture-summary.json', directory);
if (existsSync(output) || existsSync(summaryOutput)) {
  throw new Error('Task 08F screen export evidence exists; capture refused without overwriting.');
}
const legacy = JSON.parse(readFileSync(new URL('legacy-response.json', directory), 'utf8'));
const options = substanceOptions(legacy.data);
const periods = options.periods;
const filters = {
  source: 'forensic',
  area: options.areas[0][0],
  category: '',
  from: periods[0].key,
  to: periods.at(-1).key,
};
const csv = substanceCsv(legacy.data, {...legacy.metadata, filters, search: ''});
writeFileSync(output, csv, {encoding: 'utf8', flag: 'wx'});
const summary = {
  sha256: createHash('sha256').update(csv).digest('hex'),
  bytes: Buffer.byteLength(csv),
  source_response_sha256: createHash('sha256').update(readFileSync(new URL('legacy-response.json', directory))).digest('hex'),
  selected_rows: legacy.data.length,
};
writeFileSync(summaryOutput, JSON.stringify(summary, null, 2) + '\n', {encoding: 'utf8', flag: 'wx'});
console.log(JSON.stringify(summary, null, 2));
