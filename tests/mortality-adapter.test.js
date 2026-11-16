import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {collectMortality,mortalityContractPath} from '../src/api/mortality-collector.js';
import {mortalityPresentation} from '../src/platform/mortality-adapter.js';
import {geographicSource,geographicRanking,geographicSelection,geographicProfile} from '../src/platform/geography-data.js';
import {completeMortality,mortalityCsv} from '../src/platform/mortality-data.js';
import {prepareChart} from '../src/platform/chart-data.js';
import {request} from '../src/api/client.js';
const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
const contract=read('../docs/baselines/task08d/contract-response.json');
const legacy=read('../docs/baselines/task08d/legacy-response.json');
const immutable=read('../docs/baselines/task08b/resource-contracts.json').find(r=>r.resource==='mortality_trends');
const clone=x=>structuredClone(x);
function page(params){const result=clone(contract),end=Math.min(params.offset+params.limit,504);result.observations=result.observations.slice(params.offset,end);Object.assign(result.pagination,{offset:params.offset,limit:params.limit,returned:result.observations.length,next_offset:end<504?end:null,page_is_complete_collection:params.offset===0&&end===504});return result;}
const registry=[...new Map(legacy.data.map(r=>[r.geography_id,{geography_id:r.geography_id,name:r.name,boundary_type:r.boundary_type,resources:['mortality_trends'],indicators:['suspected_deaths'],available:true}])).values()];

test('complete collector pins every page and retains original order and 504 unique identities',async()=>{
 for(const pageSize of [73,1000]){let calls=0;const result=await collectMortality(async(path,params)=>{calls++;assert.equal(path,mortalityContractPath);if(params.offset)assert.equal(params.expected_collection,contract.pagination.collection_token);return page(params);},{pageSize});assert.equal(calls,Math.ceil(504/pageSize));assert.deepEqual(result.observations,contract.observations);assert.equal(new Set(result.observations.map(o=>o.observation_id)).size,504);assert.equal(result.complete,true);}
});
test('mapped values and metadata match the baseline-verified fixture and unchanged original CSV',async()=>{
 const mapped=mortalityPresentation(await collectMortality(async(_path,params)=>page(params)));
 const verified=read('../docs/baselines/task08d/fixture-verification.json');
 assert.equal(verified.ordered_response_fingerprint,immutable.ordered_response_fingerprint);
 for(const [file,key] of [['legacy-response.json','legacy_response_file_sha256'],['contract-response.json','contract_response_file_sha256']])assert.equal(createHash('sha256').update(readFileSync(new URL('../docs/baselines/task08d/'+file,import.meta.url))).digest('hex'),verified[key]);
 assert.deepEqual(mapped.data,legacy.data);assert.deepEqual(mapped.metadata,immutable.metadata);
 const inventory=read('../docs/baselines/task08b/file-inventory.json').find(r=>r.path==='analysis/phase4/outputs/mortality_quarterly.csv');
 const strings=mapped.data.map(row=>Object.fromEntries(inventory.fields.map(k=>[k,row[k]===null?'':String(row[k])])));
 // JS formatting of some integer-valued floats differs from Python; original
 // string lexemes are compared via the unchanged CSV file hash, and every value
 // is independently compared to the baseline-verified legacy fixture above.
 assert.equal(strings.length,inventory.records);
 const bytes=readFileSync(new URL('../analysis/phase4/outputs/mortality_quarterly.csv',import.meta.url));
 assert.equal(createHash('sha256').update(bytes).digest('hex'),inventory.sha256);
 assert.equal(mapped.data.filter(r=>r.observed_value===null).length,8);
 assert.equal(mapped.data.filter(r=>r.quality_status==='missing_or_suppressed').length,8);
 assert.equal(mapped.data[0].analyticalIdentity.observation_id,contract.observations[0].observation_id);
 assert.equal(Object.keys(mapped.data[0]).includes('analyticalIdentity'),false);
});
test('selected-area history, gaps, ranking, profiles and complete CSV/JSON exports are unchanged',async()=>{
 const mapped=mortalityPresentation(await collectMortality(async(_path,params)=>page(params)));
 const area=registry.find(a=>a.name==='L: Argyll & West Dunbartonshire');
 const options={boundary:'police_division',indicator:'suspected_deaths',area:area.geography_id,from:'2017 Q1',to:'2025 Q4'};
 const selected=geographicSelection(mapped.data,options).areaRows,oldSelected=geographicSelection(legacy.data,options).areaRows;
 assert.equal(selected.length,36);assert.deepEqual(prepareChart(selected),prepareChart(oldSelected));
 assert.equal(prepareChart(selected).datasets[0].points.filter(p=>p.value===null).length,oldSelected.filter(r=>r.observed_value===null).length);
 assert.ok(selected.some(r=>r.observed_value===null));
 assert.deepEqual(geographicRanking(mapped.data,{...options,period:'2025 Q4'}),geographicRanking(legacy.data,{...options,period:'2025 Q4'}));
 assert.deepEqual(geographicProfile(area,{police:mapped}),geographicProfile(area,{police:legacy}));
 const metadata={...mapped.metadata,filters:options,export_scope:'Complete eligible selected-area history across API and table pages; not necessarily complete source history.'};
 assert.equal(mortalityCsv(selected,metadata),mortalityCsv(oldSelected,metadata));
 assert.equal(JSON.stringify({data:selected,metadata},null,2),JSON.stringify({data:oldSelected,metadata},null,2));
});
test('explicit rollback uses only legacy and other mortality consumers retain their endpoint',async()=>{
 let paths=[];const api=async(path,params)=>{paths.push(path);return path==='/exports'?{...legacy,data:legacy.data.slice(params.offset,params.offset+params.limit)}:page(params);};
 const result=await geographicSource(api,'police',registry);assert.ok(paths.every(p=>p===mortalityContractPath));assert.equal(result.total,504);
 paths=[];const old=await geographicSource(api,'police',registry,{policeContract:'legacy'});assert.deepEqual(old.data,result.data);assert.deepEqual(paths,['/exports']);
 paths=[];await completeMortality(api,'police');assert.deepEqual(paths,['/exports']);
 await assert.rejects(geographicSource(api,'police',registry,{policeContract:'invalid'}));
 paths=[];await assert.rejects(geographicSource(async path=>{paths.push(path);throw Error('Backend unavailable');},'police',registry));assert.deepEqual(paths,[mortalityContractPath]);
});
test('invalid contract, metadata, periods, scope and availability fail without producing partial history',async()=>{
 const changes=[
  p=>{p.contract_version='mortality-trends/2.0.0';},p=>{delete p.source.source_version;},p=>{p.artifact.artifact_sha256='bad';},
  p=>{p.source.source_path='../file.xlsx';},p=>{p.observations[0].value=null;},p=>{p.observations[0].value=-1;},
  p=>{p.observations[0].value=1.2;},p=>{p.observations[0].value=true;},p=>{p.observations[0].availability_status='zero';},
  p=>{p.observations[0].geography.boundary_type='council';},p=>{p.observations[0].period.quarter=5;},p=>{p.observations[0].period.period_end='2017-03-30';},
  p=>{p.observations[0].observation_id='mortality-observation:v1:'+'0'.repeat(64);},p=>{p.observations[1]=clone(p.observations[0]);}
 ];
 for(const change of changes)await assert.rejects(collectMortality(async(_path,params)=>{const p=page(params);change(p);return p;}));
});
test('page gaps, overlap, truncation, changed token/source/artifact and partial backend failure reject collection',async()=>{
 const changes=[p=>{p.pagination.offset++;},p=>{p.pagination.returned--;},p=>{p.pagination.next_offset++;},p=>{p.pagination.total--;},
  p=>{p.pagination.collection_token='0'.repeat(64);},p=>{p.source.source_version='0'.repeat(64);},p=>{p.artifact.analytical_version='changed';},
  p=>{p.observations=[];p.pagination.returned=0;},p=>{p.observations[0]=clone(contract.observations[0]);}];
 for(const change of changes)await assert.rejects(collectMortality(async(_path,params)=>{const p=page(params);if(params.offset)change(p);return p;}));
 await assert.rejects(collectMortality(async(_path,params)=>{if(params.offset)throw Error('HTTP 409 stale token');return page(params);}));
});
test('zero semantics are preserved without changing identity in a synthetic value fixture',async()=>{
 const collection=await collectMortality(async(_path,params)=>{const p=page(params);if(!params.offset)p.observations[0].value=0;return p;});
 assert.equal(mortalityPresentation(collection).data[0].observed_value,0);
});
test('API transport accepts only the separate analytical shape and scoped continuation token',async()=>{
 let url;const fetcher=async value=>{url=value;return{ok:true,status:200,headers:new Headers({'content-type':'application/json'}),json:async()=>page({offset:0,limit:100})};};
 assert.equal((await request(mortalityContractPath,{expected_collection:'a'.repeat(64)},{fetcher})).contract_version,contract.contract_version);assert.match(url,/expected_collection=/);
 await assert.rejects(request('/health',{expected_collection:'x'},{fetcher}));
 await assert.rejects(request('/health',{},{fetcher}),e=>e.code==='schema');
});
