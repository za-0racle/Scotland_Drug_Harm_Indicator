import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {collectMortality} from '../../../src/api/mortality-collector.js';
import {collectForensic} from '../../../src/api/forensic-collector.js';
import {mortalityPresentation} from '../../../src/platform/mortality-adapter.js';
import {forensicPresentation} from '../../../src/platform/forensic-adapter.js';
import {mortalityCsv} from '../../../src/platform/mortality-data.js';
import {substanceCsv,substanceOptions,selectSubstances} from '../../../src/platform/substance-data.js';
import {sha256Bytes,sha256Canonical,sha256Text,stableJson} from '../../../src/api/analytical-integrity.js';

const directory=new URL('.',import.meta.url);
const read=path=>JSON.parse(readFileSync(new URL(path,directory),'utf8'));
const bytes=path=>readFileSync(new URL(path,directory));
const digest=value=>createHash('sha256').update(value).digest('hex');
const before=read('frontend-baseline-summary.json');
const capture=read('capture-summary.json');
const mortalityContract=read('../task08d/contract-response.json');
const mortalityLegacy=read('../task08d/legacy-response.json');
const forensicContract=read('../task08f/analytical-response.json');
const forensicLegacy=read('../task08f/legacy-response.json');

function page(resource){
 const source=resource==='mortality'?mortalityContract:forensicContract;
 return async(_path,params)=>{
  const result=structuredClone(source),start=params.offset,end=Math.min(start+params.limit,source.pagination.total);
  result.observations=result.observations.slice(start,end);
  Object.assign(result.pagination,{offset:start,limit:params.limit,returned:result.observations.length,
   next_offset:end<source.pagination.total?end:null,
   page_is_complete_collection:start===0&&end===source.pagination.total});
  return result;
 };
}

const mortality=mortalityPresentation(await collectMortality(page('mortality'),{pageSize:73}));
const forensic=forensicPresentation(await collectForensic(page('forensic'),{pageSize:73}));
assert.deepEqual({data:mortality.data,metadata:mortality.metadata},
 {data:mortalityLegacy.data,metadata:mortalityLegacy.metadata});
assert.deepEqual({data:forensic.data,metadata:forensic.metadata},
 {data:forensicLegacy.data,metadata:forensicLegacy.metadata});
assert.equal(mortality.data.length,before.mortality.observations);
assert.equal(mortality.data.filter(row=>row.observed_value===null).length,8);
assert.equal(forensic.data.length,before.forensic.observations);
assert.equal(forensic.data.filter(row=>row.observed_value===0).length,1);
assert.equal(forensic.data.filter(row=>row.observed_value===null).length,0);
assert.equal(digest(JSON.stringify(mortality.data.map(row=>row.analyticalIdentity.observation_id))),
 before.mortality.observation_ids_sha256);
assert.equal(digest(JSON.stringify(forensic.data.map(row=>row.analyticalIdentity.observation_id))),
 before.forensic.observation_ids_sha256);
assert.equal(digest(JSON.stringify(forensic.data.map(row=>row.analyticalIdentity.category_id))),
 before.forensic.category_ids_sha256);
assert.equal(digest(JSON.stringify({data:mortality.data,metadata:mortality.metadata})),
 before.mortality.presentation_sha256);
assert.equal(digest(JSON.stringify({data:forensic.data,metadata:forensic.metadata})),
 before.forensic.presentation_sha256);

const mortalityFirst=mortality.data.find(row=>row.geography==='L: Argyll & West Dunbartonshire');
const mortalityFilters={boundary:'police_division',indicator:'suspected_deaths',
 area:mortalityFirst.geography_id,from:'2017 Q1',to:'2025 Q4'};
const mortalityRows=mortality.data.filter(row=>row.boundary_type===mortalityFilters.boundary
 &&row.indicator_id===mortalityFilters.indicator&&row.geography_id===mortalityFilters.area);
const mortalityMetadata={...mortality.metadata,filters:mortalityFilters,
 export_scope:'Complete eligible selected-area history across API and table pages; not necessarily complete source history.'};
const mortalityCsvBytes=Buffer.from(mortalityCsv(mortalityRows,mortalityMetadata));
assert.deepEqual(mortalityCsvBytes,bytes('mortality-legacy-export.csv'));
const mortalityExport=read('mortality-export-summary.json');
assert.equal(digest(mortalityCsvBytes),mortalityExport.sha256);
assert.equal(mortalityCsvBytes.length,mortalityExport.bytes);

const options=substanceOptions(forensic.data),area=options.areas[0][0];
const forensicFilters={source:'forensic',area,category:'',
 from:options.periods[0].key,to:options.periods.at(-1).key};
const forensicCsvBytes=Buffer.from(substanceCsv(selectSubstances(forensic.data,forensicFilters),
 {...forensic.metadata,filters:forensicFilters,search:''}));
assert.deepEqual(forensicCsvBytes,bytes('../task08f/legacy-screen-export.csv'));
assert.equal(digest(forensicCsvBytes),before.forensic.screen_csv_sha256);

const canonical='{"a":{"\u03b2":[1,1,0,null,true]},"n":1e-7,"z":"\u00e9"}';
assert.equal(stableJson({z:'\u00e9',a:{'\u03b2':[1,1.0,-0.0,null,true]},n:1e-7}),canonical);
assert.equal(await sha256Canonical({b:2,a:1}),'43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777');
assert.equal(await sha256Text('é'),await sha256Bytes(new TextEncoder().encode('é')));

assert.equal(capture.contracts.mortality.collection_token,mortalityContract.pagination.collection_token);
assert.equal(capture.contracts.forensic.collection_token,forensicContract.pagination.collection_token);
console.log('Frontend identities, record projections, null/zero states, and both CSV exports match pre-change evidence.');
