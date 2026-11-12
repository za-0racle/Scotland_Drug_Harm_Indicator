import test from 'node:test';
import assert from 'node:assert/strict';
import {completeMortality,validateMortality,mortalityOptions,selectMortality,mortalityDistribution,mortalityRanking,mortalityTablePage,mortalityCsv,mortalitySources} from '../src/platform/mortality-data.js';
import {prepareChart} from '../src/platform/chart-data.js';
import {mortalityGrid} from '../src/platform/overview-data.js';
const police=(value=1,quarter=1,extra={})=>({geography_id:'a',geography:'Area A',boundary_type:'police_division',indicator_id:'suspected_deaths',unit:'count',period_basis:'calendar_quarter_legacy_10_day_adjustment',source_id:'police',year:2024,quarter,period:`2024 Q${quarter}`,observed_value:value,...extra});
const annual=(year=2024,value=20)=>({geography_id:'c',geography:'Inverclyde',boundary_type:'council',indicator_id:'nrs_registered_drug_misuse_deaths',unit:'deaths',period_basis:'calendar_year_of_registration',sex:'Persons',source_path:'nrs.xlsx',year,observed_value:value});
test('source definitions and dependent geographic/reporting controls cannot silently mix',()=>{
 validateMortality([police()],'police');validateMortality([annual()],'nrs');assert.throws(()=>validateMortality([annual()],'police'),/source/);assert.throws(()=>validateMortality([police()],'nrs'),/source/);
 assert.deepEqual(mortalityOptions([annual()],'police_division').boundaries,['council']);assert.equal(mortalityOptions([annual()],'police_division').boundary,'council');
 assert.match(mortalitySources.nrs.definition,/Registration year/);assert.match(mortalitySources.police.definition,/ten-day/);
});
test('quarterly charts and heatmap preserve missing quarters and zero; annual charts never fabricate quarters',()=>{
 const rows=[police(0,1),police(null,3)];assert.deepEqual(prepareChart(rows).datasets[0].points.map(p=>p.value),[0,null,null]);
 const heat=mortalityGrid(rows.map(r=>({year:r.year,quarter:r.quarter,suspected_deaths:r.observed_value})));assert.deepEqual(heat[0].quarters.map(q=>q.value),[0,null,null,null]);
 const chart=prepareChart([annual(2022),annual(2024)]);assert.deepEqual(chart.labels,['2022','2023','2024']);assert.equal(chart.labels.some(l=>l.includes('Q')),false);
 assert.throws(()=>validateMortality([{...annual(),quarter:1}],'nrs'),/Annual/);
});
test('type-7 quartiles and 1.5-IQR whiskers match independently specified values',()=>{
 const rows=Array.from({length:8},(_,i)=>police(i+1,1,{year:2017+i,period:`${2017+i} Q1`})),before=JSON.stringify(rows),result=mortalityDistribution(rows);
 assert.equal(result.q1,2.75);assert.equal(result.median,4.5);assert.equal(result.q3,6.25);assert.equal(result.lower,1);assert.equal(result.upper,8);assert.deepEqual(result.outliers,[]);assert.equal(JSON.stringify(rows),before);
 const out=mortalityDistribution(rows.map((r,i)=>({...r,observed_value:i===7?100:1})));assert.deepEqual(out.outliers,[100]);assert.equal(out.upper,1);
 assert.equal(mortalityDistribution(rows.slice(0,7)).state,'unavailable');assert.throws(()=>mortalityDistribution([rows[0],annual()]),/one area/);
});
test('ranking uses a single period and boundary, retains zero and reports missing values',()=>{
 const rows=[police(5),police(0,1,{geography_id:'b',geography:'B'}),police(null,1,{geography_id:'c',geography:'C'}),police(999,1,{geography_id:'national',boundary_type:'country'}),police(100,2)];
 const result=mortalityRanking(rows,{boundary:'police_division',start:2024,end:2024},'2024 Q1');assert.deepEqual(result.rows.map(r=>r.observed_value),[5,0]);assert.equal(result.missing.length,1);assert.equal(result.period,'2024 Q1');
 assert.equal(mortalityRanking([annual()],{boundary:'council',start:2024,end:2024}).state,'unavailable');
 assert.throws(()=>mortalityRanking([rows[0],{...rows[1],unit:'rate'}],{boundary:'police_division',start:2024,end:2024}),'Incompatible ranking');
});
test('table-only search and pagination never mutate analytical rows or discard provenance',()=>{
 const rows=Array.from({length:30},(_,i)=>police(i,1,{year:1995+i,period:`${1995+i} Q1`,source_cell:`B${i}`}));const before=JSON.stringify(rows);
 assert.equal(mortalityTablePage(rows,'',1).rows.length,12);assert.equal(mortalityTablePage(rows,'B-not-a-search-field').total,0);assert.equal(mortalityTablePage(rows,'2024').total,1);assert.equal(rows.length,30);assert.equal(JSON.stringify(rows),before);
 const csv=mortalityCsv([rows[0]],{source:'verified',filters:{area:'a'}});assert.match(csv,/source_cell/);assert.match(csv,/verified/);assert.match(csv,/"0"/);
 assert.match(mortalityCsv([{...rows[0],geography:'=unsafe'}],{}),/'=unsafe/);
 const vintageRows=[police(1,1,{year:2017,period:'2017 Q1',source_id:'police_2025.xlsx'}),police(2,1,{source_id:'police_2025.xlsx'})];assert.equal(mortalityTablePage(vintageRows,'2024').total,1);assert.equal(mortalityTablePage(vintageRows,'2025').total,0);assert.equal(mortalityTablePage(vintageRows,'Police Scotland').total,2);
});
test('source history loads all API pages and rejects truncation or changing artifacts',async()=>{
 let calls=0;const result=await completeMortality(async(path,params)=>{calls++;assert.equal(path,'/exports');assert.equal(params.resource,'mortality_trends');return{state:'ready',total:2,data:[police(1,calls)],metadata:{artifact_sha256:'same'}};},'police');assert.equal(calls,2);assert.equal(result.data.length,2);
 await assert.rejects(completeMortality(async()=>({state:'ready',total:2,data:[],metadata:{}}),'police'),/Incomplete/);
 let index=0;await assert.rejects(completeMortality(async()=>({state:'ready',total:2,data:[police(1,++index)],metadata:{artifact_sha256:String(index)}}),'police'),/changed/);
});
test('invalid year ranges, duplicate periods and invalid counts fail closed',()=>{
 assert.throws(()=>selectMortality([police()],{boundary:'police_division',area:'a',start:2025,end:2024}),/From year/);assert.throws(()=>validateMortality([police(),police()],'police'),/Duplicate/);assert.throws(()=>validateMortality([police(-1)],'police'),/value/);
 assert.equal(selectMortality([police()],{boundary:'council',area:'a',start:2024,end:2024}).length,0);
 assert.throws(()=>validateMortality([police(1,1,{period:'2024 Q2'})],'police'),/basis/);
 assert.throws(()=>mortalityRanking([police(1,1,{period_start:'2024-01-01'}),police(2,1,{geography_id:'b',period_start:'2024-02-01'})],{boundary:'police_division',start:2024,end:2024},'2024 Q1'),/boundaries/);
});
