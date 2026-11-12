import test from 'node:test';
import assert from 'node:assert/strict';
import {request,queryString} from '../src/api/client.js';
import {chartSeries,sections,boundaries,areasFor} from '../src/platform/data.js';
test('central API client validates parameters, response contracts and structured errors',async()=>{
 assert.throws(()=>queryString({raw_sql:'x'}));
 const fetcher=async url=>({ok:true,status:200,headers:new Headers({'Content-Type':'application/json'}),json:async()=>({state:'empty',data:[],total:0,metadata:{url}})});
 assert.equal((await request('/anomalies',{geography_id:'test',start_year:2024},{fetcher})).state,'empty');
 await assert.rejects(request('/bad',{},{fetcher:async()=>({ok:false,status:503,headers:new Headers({'Content-Type':'application/json'}),json:async()=>({message:'Unavailable source'})})}),/Unavailable source/);
 await assert.rejects(request('/bad',{},{fetcher:async()=>({ok:true,headers:new Headers({'Content-Type':'application/json'}),json:async()=>({data:[]})})}),/schema/);
 await assert.rejects(request('/bad',{},{fetcher:async()=>{throw new Error('network');}}),/Cannot reach/);
});
test('chart inputs respond to API changes and retain missing values',()=>{
 const first=chartSeries([{year:2024,observed_value:25},{year:2023,observed_value:null}]);
 assert.deepEqual(first.values,[null,25]);
 assert.deepEqual(chartSeries([{year:2024,observed_value:31}]).values,[31]);
 assert.deepEqual(chartSeries([]),{labels:[],values:[]});
});
test('navigation has eight sections and geographic choices follow API data',()=>{
 assert.equal(sections.length,8);
 const fixture=[{name:'TEST DIVISION',boundary_type:'police_division'},{name:'TEST BOARD',boundary_type:'health_board'}];
 assert.equal(boundaries(fixture).length,2);assert.equal(areasFor(fixture,'police_division')[0].name,'TEST DIVISION');
});

test('slow requests time out without fallback values',async()=>{
 const fetcher=(_url,{signal})=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError'))));
 await assert.rejects(request('/forecasting/results',{},{fetcher,timeout:5}),/timed out/);
});
