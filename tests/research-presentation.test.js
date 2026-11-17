import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {researchColumns,projectionText,forecastFinding} from '../src/platform/research-presentation.js';
test('projection explanation preserves saved origin, target and every interval endpoint',()=>{
 const row=JSON.parse(readFileSync(new URL('../analysis/outputs/forecast.json',import.meta.url),'utf8'));
 const text=projectionText(row);for(const key of ['forecast_origin','target_period','predicted','lower80','upper80','lower95','upper95'])assert.ok(text.includes(String(row[key])));
 assert.match(text,/target period has elapsed/);
});
test('original monitoring columns preserve both CUSUM components and stored limits',()=>{
 for(const field of ['cusum_positive','cusum_negative','lower_limit','upper_limit','signal_flag'])assert.ok(researchColumns.stored.includes(field));
});
test('forecast conclusion follows loaded candidate scores and shared evaluation coverage',()=>{
 const rows=JSON.parse(readFileSync(new URL('../analysis/outputs/model_metrics.json',import.meta.url),'utf8'));
 assert.match(forecastFinding(rows),/21\.58 deaths/);
 assert.doesNotMatch(forecastFinding(rows.filter(row=>row.model!=='naive')),/lowest/);
 assert.doesNotMatch(forecastFinding(rows.map(row=>({...row,evaluated_origins:10}))),/lowest/);
 assert.doesNotMatch(forecastFinding(rows.map(row=>({...row,mae:row.model==='naive'?100:row.mae}))),/lowest/);
});
