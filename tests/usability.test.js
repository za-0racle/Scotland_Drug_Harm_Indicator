import {chartSeries} from '../src/platform/data.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import {mortalitySummary,label} from '../src/platform/presentation.js';
test('overview descriptive totals use only complete live calendar years',()=>{
 const rows=[...Array.from({length:4},(_,i)=>({year:2024,quarter:i+1,suspected_deaths:10})),...Array.from({length:4},(_,i)=>({year:2025,quarter:i+1,suspected_deaths:12})),{year:2026,quarter:1,suspected_deaths:3}];
 const result=mortalitySummary(rows);assert.deepEqual(result.annual,{year:2025,total:48});assert.equal(result.change,20);assert.equal(result.latestQuarter.year,2026);
 assert.equal(mortalitySummary([]).annual,undefined);assert.equal(mortalitySummary([]).change,null);
 rows[4].suspected_deaths=null;assert.equal(mortalitySummary(rows).annual.year,2024);
});
test('zero values retained and incomplete previous year gives unavailable change',()=>{
 const rows=Array.from({length:4},(_,i)=>({year:2024,quarter:i+1,suspected_deaths:0}));assert.equal(mortalitySummary(rows).annual.total,0);assert.equal(mortalitySummary(rows).change,null);
 assert.equal(label('nrs_registered_drug_misuse_deaths'),'Registered drug misuse deaths');
});

test('source study ordinals preserve non-calendar period ordering',()=>{
 assert.deepEqual(chartSeries([{period:'Q10 study',ordinal:10,observed_value:2},{period:'Q4 study',ordinal:4,observed_value:1}]).labels,['Q4 study','Q10 study']);
});
