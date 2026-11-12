import test from 'node:test';
import assert from 'node:assert/strict';
import {mortalityGrid,overviewKpis,latestForensic,forecastPreview,loadOverview} from '../src/platform/overview-data.js';
test('KPI mapping uses actual latest quarter, complete annual totals, source and period',()=>{
 const data=[...Array.from({length:4},(_,i)=>({year:2024,quarter:i+1,suspected_deaths:10})),...Array.from({length:4},(_,i)=>({year:2025,quarter:i+1,suspected_deaths:12}))];
 const kpis=overviewKpis({state:'ready',data},[{resource:'one'},{resource:'two'}]);assert.equal(kpis[0].value,'12');assert.equal(kpis[0].context,'2025 Q4');assert.equal(kpis[1].value,'48');assert.match(kpis[1].context,/\+20.00%/);assert.match(kpis[0].source,/Police Scotland/);assert.equal(kpis[3].value,'2');
});
test('heatmap distinguishes absent quarters, explicit null and genuine zero without inventing records',()=>{
 const zero={year:2023,quarter:1,suspected_deaths:0},rows=[zero,{year:2023,quarter:3,suspected_deaths:null},{year:2025,quarter:1,suspected_deaths:9}];
 const grid=mortalityGrid(rows);assert.equal(grid.length,3);assert.equal(grid[0].quarters[0].value,0);assert.equal(grid[0].quarters[0].record,zero);assert.equal(grid[0].quarters[1].record,null);assert.equal(grid[0].quarters[2].value,null);assert.ok(grid[1].quarters.every(q=>q.record===null));assert.equal(rows.length,3);
 assert.throws(()=>mortalityGrid([zero,zero]),/Multiple/);assert.throws(()=>mortalityGrid([{year:2025,quarter:5,suspected_deaths:1}]),/periods/);
});
test('unavailable mortality never becomes zero or a complete annual total',()=>{
 const kpis=overviewKpis({state:'error',data:[{year:2025,quarter:1,suspected_deaths:99}]});assert.equal(kpis[0].value,'Unavailable');assert.equal(kpis[1].value,'Unavailable');assert.equal(kpis[2].value,'Unavailable');
 const partial=overviewKpis({state:'ready',data:[{year:2025,quarter:1,suspected_deaths:0}]});assert.equal(partial[0].value,'0');assert.equal(partial[1].value,'Unavailable');
});
test('forensic preview retains source definitions, selects latest complete response and does not pool categories',()=>{
 const row={period:'2025 Q4',indicator_id:'forensic:Opioids',unit:'detection_count',period_basis:'calendar_quarter',source_id:'RADAR',geography:'testing sample',observed_value:10};
 const data=[row,{...row,period:'2026 Q1',observed_value:4},{...row,period:'2026 Q1',indicator_id:'forensic:Other',observed_value:0}];
 const result=latestForensic({state:'ready',total:3,data});assert.equal(result.period,'2026 Q1');assert.equal(result.rows.length,2);assert.equal(result.rows[0].source_id,'RADAR');assert.equal(latestForensic({state:'ready',total:4,data}).state,'unavailable');assert.equal(latestForensic({state:'ready',total:2,data:[row,{...row,source_id:'Other'}]}).state,'unavailable');
});
test('saved forecast labels actual historical origin, target and interval method',()=>{
 const row={model:'naive',horizon_quarters:1,forecast_origin:'2025 Q4',target_period:'2026 Q1',predicted:248,lower95:160,upper95:336,interval_method:'Gaussian one-step random-walk errors; lower bound clipped at zero'};
 const result=forecastPreview({state:'ready',data:[row]});assert.equal(result.row,row);assert.match(result.context,/2025 Q4.*2026 Q1/);assert.match(result.context,/Not a current/);assert.match(result.interval,/Gaussian/);assert.equal(forecastPreview({state:'error',data:[]}).state,'unavailable');assert.equal(forecastPreview({state:'ready',data:[{...row,interval_method:null}]}).state,'unavailable');
});
test('overview resources fail independently without fabricated fallbacks or new endpoints',async()=>{
 const paths=[];const results=await loadOverview(async path=>{paths.push(path);if(path==='/forecasting/results')throw new Error('Forecast unavailable');return{state:'ready',data:[{verified:true}],total:1,metadata:{source_path:'verified.csv'}};});
 assert.equal(results.forecast.state,'error');assert.deepEqual(results.forecast.data,[]);assert.equal(results.geography.state,'ready');assert.equal(results.monitoring.metadata.source_path,'verified.csv');assert.equal(paths.length,6);assert.ok(paths.includes('/overview'));
});
