import test from 'node:test';
import assert from 'node:assert/strict';
import {compatibleAreas,comparisonTable,comparisonCsv,verifyDefinitions} from '../src/platform/comparison-data.js';
test('comparison options require available same-boundary same-indicator areas',()=>{
 const first={geography_id:'a',boundary_type:'council'};
 const areas=[{geography_id:'b',name:'B',boundary_type:'council',available:true,indicators:['deaths']},{geography_id:'c',name:'C',boundary_type:'health_board',available:true,indicators:['deaths']},{geography_id:'d',name:'D',boundary_type:'council',available:false,indicators:['deaths']}];
 assert.deepEqual(compatibleAreas(areas,first,'deaths').map(a=>a.geography_id),['b']);assert.equal(compatibleAreas(areas,first,'other').length,0);
});
test('comparison alignment preserves zeros, unavailable values and missing periods',()=>{
 const rows=[{year:2024,comparison_role:'first_area',observed_value:0},{year:2023,comparison_role:'second_area',observed_value:null},{year:2023,comparison_role:'first_area',observed_value:7}];
 const table=comparisonTable(rows);assert.deepEqual(table.map(r=>[r.period,r.left,r.right]),[['2023',7,null],['2024',0,null]]);
 assert.throws(()=>comparisonTable([rows[0],rows[0]]),/Multiple measurements/);
 assert.throws(()=>comparisonTable([{year:2024}]),/roles/);
});
test('reporting definitions and measurement units cannot be silently mixed',()=>{
 const row={indicator_id:'deaths',unit:'count',period_basis:'annual',reporting_definition:'registered'};
 verifyDefinitions([row,{...row}]);assert.throws(()=>verifyDefinitions([row,{...row,reporting_definition:'suspected'}]),/Incompatible/);assert.throws(()=>verifyDefinitions([row,{...row,unit:'rate'}]),/Incompatible/);
});
test('CSV exports displayed values, missing states and full provenance safely',()=>{
 const table=comparisonTable([{year:2024,comparison_role:'first_area',observed_value:0,source_cell:'B5'}]);
 const csv=comparisonCsv(table,'=unsafe','Area B',{version:'verified'});
 assert.match(csv,/'=unsafe/);assert.match(csv,/missing_or_unavailable/);assert.match(csv,/source_cell/);assert.match(csv,/verified/);assert.match(csv,/"0"/);
});
