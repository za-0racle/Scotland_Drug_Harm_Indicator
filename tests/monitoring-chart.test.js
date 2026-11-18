import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareMonitoring} from '../src/platform/monitoring-chart.js';
const config={configuration_id:1,method:'NB2-EWMA'};
const row=(quarter,extra={})=>({configuration_id:1,observation_year:2024,observation_quarter:quarter,statistic_value:0,lower_limit:-1,upper_limit:1,signal_flag:false,...extra});
test('monitoring uses one configuration, sorts saved quarters and preserves gaps, zeros and exact limits',()=>{
 const rows=[row(3,{statistic_value:-1.16480084,lower_limit:-0.9873333333,signal_flag:true}),row(1),row(2,{configuration_id:2})],before=structuredClone(rows);
 const chart=prepareMonitoring(rows,config);
 assert.deepEqual(chart.labels,['2024 Q1','2024 Q2','2024 Q3']);
 assert.deepEqual(chart.datasets[0].points.map(p=>p.value),[0,null,-1.16480084]);
 assert.equal(chart.datasets[1].points[2].value,-0.9873333333);
 assert.match(chart.warnings[0],/2024 Q3/);assert.deepEqual(rows,before);
});
test('CUSUM keeps separate saved components, no lower alarm and no inferred crossing attribution',()=>{
 const chart=prepareMonitoring([row(1,{cusum_positive:2,cusum_negative:null,signal_flag:true})],{...config,method:'CUSUM'});
 assert.deepEqual(chart.datasets.map(s=>s.key),['cusum_positive','cusum_negative','upper_limit']);
 assert.equal(chart.datasets[1].points[0].value,null);
 assert.match(chart.warnings[0],/does not identify which component/);
 const crossing=prepareMonitoring([row(1,{statistic_value:999})],config);
 assert.match(crossing.warnings[0],/none in these returned records/);
});
test('monitoring rejects ambiguous or unsupported periods and keeps empty evidence empty',()=>{
 assert.throws(()=>prepareMonitoring([row(1),row(1)],config),/duplicate/);
 assert.throws(()=>prepareMonitoring([row(5)],config),/quarter/);
 assert.throws(()=>prepareMonitoring([],{...config,method:'other'}),/unsupported/);
 assert.deepEqual(prepareMonitoring([],config).labels,[]);
});
