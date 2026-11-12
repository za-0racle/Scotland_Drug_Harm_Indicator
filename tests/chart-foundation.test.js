import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareChart,valueOf} from '../src/platform/chart-data.js';
import {comparisonTable,verifyDefinitions} from '../src/platform/comparison-data.js';
const base={geography:'Scotland',indicator_id:'deaths',unit:'count',period_basis:'calendar_quarter',period:'2024 Q1',observed_value:0};
test('models and windows preserve separate values, limits, identities and records',()=>{
 const rows=[{...base,method:'nb2',window:8,observation_id:'a',upper99:10},{...base,method:'nb2',window:12,observed_value:3},{...base,method:'poisson',window:8,observed_value:4}];
 const result=prepareChart(rows);assert.equal(result.datasets.length,3);assert.equal(new Set(result.datasets.map(s=>s.key)).size,3);
 assert.deepEqual(result.datasets.map(s=>s.points[0].value),[0,3,4]);assert.equal(result.datasets[0].points[0].record,rows[0]);assert.equal(result.datasets[0].points[0].record.upper99,10);
 assert.throws(()=>prepareChart([base,{...base,observation_id:'different'}]),/multiple observations/);
 assert.equal(prepareChart([{...base,source_path:'one.csv'},{...base,source_path:'two.csv'}]).datasets.length,2);
 assert.equal(prepareChart([{...base,forecast_origin:'2023 Q4'},{...base,forecast_origin:'2023 Q3'}]).datasets.length,2);
});
test('missing intermediate quarters and years become null display slots without fabricated records',()=>{
 const r=prepareChart([base,{...base,period:'2024 Q3',observed_value:7}]);assert.deepEqual(r.labels,['2024 Q1','2024 Q2','2024 Q3']);assert.deepEqual(r.datasets[0].points.map(p=>p.value),[0,null,7]);assert.equal(r.datasets[0].points[1].record,null);
 const annual=prepareChart([{year:2022,observed_value:1},{year:2024,observed_value:2}]);assert.deepEqual(annual.labels,['2022','2023','2024']);
});
test('explicit null and missing values never fall back to predictions or become zero',()=>{
 assert.equal(valueOf({observed_value:null,predicted:10}),null);assert.equal(valueOf({observed_value:0}),0);assert.equal(valueOf({observed_value:''}),null);assert.equal(valueOf({observed_value:'invalid'}),null);
});
test('definitions stay separate and incompatible comparison definitions and models fail',()=>{
 const other={...base,reporting_definition:'registered'};
 assert.equal(prepareChart([base,other]).datasets.length,2);assert.throws(()=>verifyDefinitions([base,other]),/Incompatible/);
 assert.throws(()=>verifyDefinitions([{...base,model:'a'},{...base,model:'b'}]),/models/);
 assert.throws(()=>verifyDefinitions([{...base,period_start:'2024-01-01'},{...base,period_start:'2024-02-01'}]),/period boundaries/);
 assert.throws(()=>prepareChart([base,{...base,unit:'percent'}]),/incompatible units/);
});
test('comparison aligns absent periods and reports incomplete coverage with genuine zeros',()=>{
 const rows=[{...base,comparison_role:'first_area'},{...base,geography:'Other',comparison_role:'second_area'},{...base,period:'2024 Q3',comparison_role:'first_area',observed_value:9}];
 const table=comparisonTable(rows);assert.deepEqual(table.map(r=>[r.period,r.left,r.right,r.coverage]),[['2024 Q1',0,0,'paired'],['2024 Q2',null,null,'missing_period'],['2024 Q3',9,null,'missing_period']]);
 assert.match(prepareChart(rows,{total:100,offset:10}).warnings.join(' '),/Bounded page/);
});
test('irregular ASSIST periods use ordinal ordering and unconnected categorical points',()=>{
 const rows=[{...base,period_basis:'source_study_period_not_calendar_quarter',period:'Q10 study',ordinal:10},{...base,period_basis:'source_study_period_not_calendar_quarter',period:'Q4 study',ordinal:4}];
 const result=prepareChart(rows);assert.deepEqual(result.labels,['Q4 study','Q10 study']);assert.equal(result.datasets[0].showLine,false);assert.match(result.warnings.join(' '),/elapsed time/);
});
test('supported regular series sort immutably; forecasts retain bounds; empty inputs work',()=>{
 const rows=[{...base,period:'2024 Q2',observed_value:2},base];const before=JSON.stringify(rows);assert.deepEqual(prepareChart(rows).datasets[0].points.map(p=>p.value),[0,2]);assert.equal(JSON.stringify(rows),before);
 const forecast={target_period:'2026 Q1',predicted:248,lower95:160,upper95:336,model:'naive'};assert.equal(prepareChart([forecast]).datasets[0].points[0].record,forecast);assert.deepEqual(prepareChart([]).datasets,[]);
});
