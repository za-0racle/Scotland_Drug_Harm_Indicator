import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {collectMortality} from '../../../src/api/mortality-collector.js';
import {collectForensic} from '../../../src/api/forensic-collector.js';
import {mortalityPresentation} from '../../../src/platform/mortality-adapter.js';
import {forensicPresentation} from '../../../src/platform/forensic-adapter.js';
import {mortalityCsv} from '../../../src/platform/mortality-data.js';
import {substanceCsv,substanceOptions,selectSubstances} from '../../../src/platform/substance-data.js';

const directory=new URL('.',import.meta.url);
const read=(path)=>JSON.parse(readFileSync(new URL(path,directory),'utf8'));
const sha=value=>createHash('sha256').update(value).digest('hex');
const mortalityContract=read('../task08d/contract-response.json');
const mortalityLegacy=read('../task08d/legacy-response.json');
const forensicContract=read('../task08f/analytical-response.json');
const forensicLegacy=read('../task08f/legacy-response.json');
const forensicCsv=readFileSync(new URL('../task08f/legacy-screen-export.csv',directory));

function pages(resource){
 const source=resource==='mortality'?mortalityContract:forensicContract;
 return async(_path,params)=>{
  const body=structuredClone(source),start=params.offset,end=Math.min(start+params.limit,source.pagination.total);
  body.observations=body.observations.slice(start,end);
  Object.assign(body.pagination,{offset:start,limit:params.limit,returned:body.observations.length,
   next_offset:end<source.pagination.total?end:null,
   page_is_complete_collection:start===0&&end===source.pagination.total});
  return body;
 };
}

const mortality=mortalityPresentation(await collectMortality(pages('mortality'),{pageSize:73}));
const forensic=forensicPresentation(await collectForensic(pages('forensic'),{pageSize:73}));
if(JSON.stringify({data:mortality.data,metadata:mortality.metadata})!==JSON.stringify({
 data:mortalityLegacy.data,metadata:mortalityLegacy.metadata,
}))throw new Error('Pre-change mortality presentation does not match the baseline fixture.');
if(JSON.stringify({data:forensic.data,metadata:forensic.metadata})!==JSON.stringify({
 data:forensicLegacy.data,metadata:forensicLegacy.metadata,
}))throw new Error('Pre-change forensic presentation does not match the baseline fixture.');

const mortalityFilters={boundary:'police_division',indicator:'suspected_deaths',
 area:'police_division-122fb6ace418',from:'2017 Q1',to:'2025 Q4'};
const mortalitySelected=mortality.data.filter(row=>row.boundary_type===mortalityFilters.boundary
 &&row.indicator_id===mortalityFilters.indicator&&row.geography_id===mortalityFilters.area);
const mortalityJson=JSON.stringify({data:mortalitySelected,metadata:mortality.metadata},null,2);
const forensicOptions=substanceOptions(forensic.data),firstArea=forensicOptions.areas[0][0];
const forensicFilters={source:'forensic',area:firstArea,category:'',
 from:forensicOptions.periods[0].key,to:forensicOptions.periods.at(-1).key};
const forensicSelected=selectSubstances(forensic.data,forensicFilters);
const forensicExport=substanceCsv(forensicSelected,{...forensic.metadata,filters:forensicFilters,search:''});
if(!Buffer.from(forensicExport).equals(forensicCsv))throw new Error('Pre-change forensic export does not match immutable screen CSV.');

const summary={
 capture:'pre-Task-08H frontend adapters evaluated against Task 08D/08F fixtures',
 mortality:{
  observations:mortality.data.length,null_values:mortality.data.filter(row=>row.observed_value===null).length,
  observation_ids_sha256:sha(JSON.stringify(mortality.data.map(row=>row.analyticalIdentity.observation_id))),
  presentation_sha256:sha(JSON.stringify({data:mortality.data,metadata:mortality.metadata})),
  selected_area_json_sha256:sha(mortalityJson),selected_area_json_bytes:Buffer.byteLength(mortalityJson),
  source_artifact_sha256:mortality.metadata.artifact_sha256,
  fixture_response_sha256:sha(readFileSync(new URL('../task08d/contract-response.json',directory))),
 },
 forensic:{
  observations:forensic.data.length,null_values:forensic.data.filter(row=>row.observed_value===null).length,
  zero_values:forensic.data.filter(row=>row.observed_value===0).length,
  observation_ids_sha256:sha(JSON.stringify(forensic.data.map(row=>row.analyticalIdentity.observation_id))),
  category_ids_sha256:sha(JSON.stringify(forensic.data.map(row=>row.analyticalIdentity.category_id))),
  presentation_sha256:sha(JSON.stringify({data:forensic.data,metadata:forensic.metadata})),
  screen_csv_sha256:sha(forensicExport),screen_csv_bytes:Buffer.byteLength(forensicExport),
  source_sha256:forensic.analytical.source.source_version,
  artifact_sha256:forensic.metadata.artifact_sha256,
  fixture_response_sha256:sha(readFileSync(new URL('../task08f/analytical-response.json',directory))),
 },
 independent_expected:{
  mortality_ordered_fingerprint:'ebb982939b748578caec331bd3edf3849e8e0867202e594c4b86d69deb655174',
  forensic_ordered_fingerprint:'279211b429f4a2827f0722673fd45874ba0bff2fed41a31de1855ad2c5c79cc0',
  forensic_screen_csv_sha256:'ee91fd04a1f8caf0963053cc2eb16b7f6cec576daaccccb669fc0af72e2bc1f7',
 },
};
const output=new URL('frontend-baseline-summary.json',directory);
writeFileSync(output,JSON.stringify(summary,null,2)+'\n',{encoding:'utf8',flag:'wx'});
console.log(JSON.stringify(summary,null,2));
