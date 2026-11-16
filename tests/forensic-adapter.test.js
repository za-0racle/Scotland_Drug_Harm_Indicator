import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {collectForensic,forensicContractPath} from '../src/api/forensic-collector.js';
import {forensicPresentation} from '../src/platform/forensic-adapter.js';
import {loadSubstanceSource,substanceForensicContract} from '../src/platform/substance.js';
import {completeSubstances,categoryOf,selectSubstances,substanceCsv,substanceHeatmap,substanceOptions,substanceProfile,substanceRanking} from '../src/platform/substance-data.js';
import {periodLabel,prepareChart} from '../src/platform/chart-data.js';

const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
const legacy=read('../docs/baselines/task08f/legacy-response.json');
const analytical=read('../docs/baselines/task08f/analytical-response.json');
const presentation=read('../docs/baselines/task08f/legacy-presentation.json');
const exportBytes=readFileSync(new URL('../docs/baselines/task08f/legacy-substance-export.csv',import.meta.url));
const screenExportBytes=readFileSync(new URL('../docs/baselines/task08f/legacy-screen-export.csv',import.meta.url));
const capture=read('../docs/baselines/task08f/capture-summary.json');
const exportCapture=read('../docs/baselines/task08f/presentation-capture-summary.json');
const screenExportCapture=read('../docs/baselines/task08f/screen-export-capture-summary.json');
const clone=value=>structuredClone(value);

function page(params,source=analytical){
 const result=clone(source),start=params.offset,end=Math.min(start+params.limit,source.pagination.total);
 result.observations=result.observations.slice(start,end);
 Object.assign(result.pagination,{
  offset:start,limit:params.limit,returned:result.observations.length,
  next_offset:end<source.pagination.total?end:null,
  page_is_complete_collection:start===0&&end===source.pagination.total,
 });
 return result;
}

function chartPresentation(rows){
 const chart=prepareChart(rows);
 return {
  labels:chart.labels,regular:chart.regular,warnings:chart.warnings,
  datasets:chart.datasets.map(dataset=>({
   label:dataset.label,showLine:dataset.showLine,metadata:dataset.metadata,
   points:dataset.points.map(point=>({period:point.period,value:point.value,missingPeriod:point.missingPeriod})),
  })),
 };
}
function baselineFilters(rows){
 const options=substanceOptions(rows);
 return {area:options.areas[0][0],category:'',from:options.periods[0].key,to:options.periods.at(-1).key};
}

test('complete collector pins pages and retains all ordered, source-scoped observations',async()=>{
 for(const pageSize of [1,73,1000]){
  let calls=0;
  const result=await collectForensic(async(path,params)=>{
   calls++;assert.equal(path,forensicContractPath);
   if(params.offset)assert.equal(params.expected_collection,analytical.pagination.collection_token);
   return page(params);
  },{pageSize});
  assert.equal(calls,Math.ceil(210/pageSize));
  assert.deepEqual(result.observations,analytical.observations);
  assert.equal(result.total,210);
  assert.equal(new Set(result.observations.map(row=>row.observation_id)).size,210);
  assert.equal(result.complete,true);
  assert.equal(result.observations.filter(row=>row.value===0).length,1);
  assert.equal(result.observations.filter(row=>row.value===null).length,0);
 }
});

test('lossless adapter matches immutable legacy row, metadata and JSON output byte-for-byte',async()=>{
 const mapped=forensicPresentation(await collectForensic(async(_path,params)=>page(params)));
 assert.equal(mapped.data.length,210);
 assert.equal(JSON.stringify(mapped.data),JSON.stringify(legacy.data));
 assert.equal(JSON.stringify(mapped.metadata),JSON.stringify(legacy.metadata));
 assert.equal(JSON.stringify({data:mapped.data,metadata:mapped.metadata}),
  JSON.stringify({data:legacy.data,metadata:legacy.metadata}));
 assert.equal(Object.keys(mapped.data[0]).includes('analyticalIdentity'),false);
 assert.equal(mapped.data[0].analyticalIdentity.observation_id,analytical.observations[0].observation_id);
 assert.equal(mapped.data[0].analyticalIdentity.category_id,analytical.observations[0].category_id);
 assert.equal(mapped.data.filter(row=>row.observed_value===0).length,1);
 assert.equal(mapped.data.filter(row=>row.observed_value===null).length,0);
 assert.equal(capture.legacy_ordered_response_fingerprint,'279211b429f4a2827f0722673fd45874ba0bff2fed41a31de1855ad2c5c79cc0');
 assert.equal(createHash('sha256').update(JSON.stringify({data:legacy.data,metadata:legacy.metadata})).digest('hex'),
  createHash('sha256').update(JSON.stringify({data:mapped.data,metadata:mapped.metadata})).digest('hex'));
});

test('chart gaps, heatmap, category ranking and all profiles match pre-migration results',async()=>{
 const mapped=forensicPresentation(await collectForensic(async(_path,params)=>page(params)));
 const filters=baselineFilters(legacy.data);
 const selected=selectSubstances(mapped.data,filters);
 assert.deepEqual(chartPresentation(selected),presentation.chart);
 const heatmap=substanceHeatmap(selected);
 assert.equal(heatmap.state,presentation.heatmap.state);
 assert.deepEqual(heatmap.periods.map(period=>period.label),presentation.heatmap.periods);
 assert.deepEqual(heatmap.rows,presentation.heatmap.rows);
 for(const expected of presentation.rankings){
  const actual=substanceRanking(selected,expected.period).rows.map(row=>({
   category:categoryOf(row),value:row.observed_value,period:periodLabel(row),
  }));
  assert.deepEqual(actual,expected.rows);
 }
 for(const expected of presentation.profiles){
  const profile=substanceProfile(selected,expected.category,'forensic');
  const actual={
   category:profile.category,source:profile.source,definition:profile.definition,
   observations:profile.observations,periods:profile.periods,units:profile.units,
   geographies:profile.geographies,denominator:profile.denominator,limitations:profile.limitations,
   provenance:profile.provenance,note:profile.note,
   values:profile.history.map(row=>[periodLabel(row),row.observed_value]),
  };
  assert.deepEqual(actual,expected);
 }
});

test('existing CSV export remains byte-identical to the pre-migration export',async()=>{
 const mapped=forensicPresentation(await collectForensic(async(_path,params)=>page(params)));
 const filters=baselineFilters(legacy.data);
 const selected=selectSubstances(mapped.data,filters);
 const csv=substanceCsv(selected,{...mapped.metadata,filters,search:''});
 assert.equal(Buffer.byteLength(csv),exportCapture.csv_bytes);
 assert.equal(createHash('sha256').update(csv).digest('hex'),exportCapture.csv_sha256);
 assert.deepEqual(Buffer.from(csv),exportBytes);
});

test('Substance Intelligence CSV remains byte-identical with its original screen filters',async()=>{
 const mapped=forensicPresentation(await collectForensic(async(_path,params)=>page(params)));
 const options=substanceOptions(legacy.data);
 const filters={
  source:'forensic',area:options.areas[0][0],category:'',
  from:options.periods[0].key,to:options.periods.at(-1).key,
 };
 const csv=substanceCsv(selectSubstances(mapped.data,filters),{...mapped.metadata,filters,search:''});
 assert.equal(Buffer.byteLength(csv),screenExportCapture.bytes);
 assert.equal(createHash('sha256').update(csv).digest('hex'),screenExportCapture.sha256);
 assert.deepEqual(Buffer.from(csv),screenExportBytes);
});

test('only Substance Intelligence selects the versioned route and explicit rollback selects legacy',async()=>{
 assert.equal(substanceForensicContract,'v1');
 const paths=[];
 const result=await loadSubstanceSource(async(path,params)=>{
  paths.push([path,params]);
  return page(params);
 },'forensic');
 assert.equal(result.total,210);
 assert.ok(paths.every(([path])=>path===forensicContractPath));
 assert.ok(paths.slice(1).every(([,params])=>params.expected_collection===analytical.pagination.collection_token));

 const rollbackPaths=[];
 const rollback=await loadSubstanceSource(async(path,params)=>{
  rollbackPaths.push(path);
  const start=params.offset,end=Math.min(start+params.limit,legacy.total);
  return {...legacy,data:legacy.data.slice(start,end),offset:start,limit:params.limit};
 },'forensic','legacy');
 assert.equal(rollback.total,210);
 assert.deepEqual(rollbackPaths,['/toxicology/forensic']);
 assert.deepEqual(rollback.data,legacy.data);
 await assert.rejects(loadSubstanceSource(async()=>{},'forensic','invalid'),/Unknown forensic contract/);
 await assert.rejects(loadSubstanceSource(async()=>{},'assist','invalid'),/Unknown forensic contract/);
});

test('ASSIST, treatment and comparison-studio forensic loaders retain legacy route',async()=>{
 const paths=[];
 const legacyApi=async(path,params)=>{
  paths.push(path);
  if(path==='/toxicology/forensic'){
   const start=params.offset??0,end=Math.min(start+(params.limit??1000),legacy.total);
   return {...legacy,data:legacy.data.slice(start,end),offset:start,limit:params.limit??1000};
  }
  return {state:'ready',data:[],total:0,metadata:{artifact_sha256:'unchanged'},offset:0,limit:1000};
 };
 await completeSubstances(legacyApi,'forensic');
 assert.deepEqual(paths,['/toxicology/forensic']);
 paths.length=0;
 await loadSubstanceSource(legacyApi,'assist');
 await loadSubstanceSource(legacyApi,'treatment');
 assert.deepEqual(paths,['/toxicology/assist','/toxicology/treatment']);
});

test('invalid contract, source/artifact metadata and observation semantics fail closed',async()=>{
 const mutations=[
  body=>{body.contract_version='forensic-toxicology/2.0.0';},
  body=>{body.source.source_version='0'.repeat(64);},
  body=>{body.artifact.artifact_sha256='0'.repeat(64);},
  body=>{body.artifact.analytical_version='changed';},
  body=>{body.source.source_url='https://invalid.example/';},
  body=>{delete body.source.publisher;},
  body=>{body.measure.unit='count';},
  body=>{body.categories[0].original_label='Benzodiazepines';},
  body=>{body.categories[0].category_id='forensic-category:v1:'+'0'.repeat(64);},
  body=>{body.observations[0].value=null;},
  body=>{body.observations[0].value=-1;},
  body=>{body.observations[0].availability_status='zero';},
  body=>{body.observations[0].geography.boundary_type='country';},
  body=>{body.observations[0].period.original_label='Q3 2018';},
  body=>{body.observations[0].research_context.rolling_average=Infinity;},
 ];
 for(const mutate of mutations){
  await assert.rejects(collectForensic(async(_path,params)=>{
   const result=page(params);mutate(result);return result;
  }));
 }
});

test('changed tokens, missing pages, overlaps and incomplete pagination reject the collection',async()=>{
 let changedToken=false;
 await assert.rejects(collectForensic(async(_path,params)=>{
  const result=page(params);
  if(params.offset){result.pagination.collection_token='0'.repeat(64);changedToken=true;}
  return result;
 },{pageSize:73}));
 assert.equal(changedToken,true);

 await assert.rejects(collectForensic(async(_path,params)=>{
  if(params.offset)return page({...params,offset:params.offset+73});
  return page(params);
 },{pageSize:73}));
 await assert.rejects(collectForensic(async(_path,params)=>{
  const result=page(params);
  if(params.offset)result.observations[0]=clone(analytical.observations[0]);
  return result;
 },{pageSize:73}));
 await assert.rejects(collectForensic(async(_path,params)=>{
  const result=page(params);
  if(params.offset){result.pagination.returned--;result.observations.pop();}
  return result;
 },{pageSize:73}));
 await assert.rejects(collectForensic(async(_path,params)=>{
  if(params.offset)throw new Error('Backend unavailable');
  return page(params);
 },{pageSize:73}));
});

test('backend failure never invokes legacy fallback',async()=>{
 const paths=[];
 await assert.rejects(loadSubstanceSource(async path=>{
  paths.push(path);throw new Error('backend unavailable');
 },'forensic'));
 assert.deepEqual(paths,[forensicContractPath]);
});
