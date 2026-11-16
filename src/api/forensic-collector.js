// Strict, source-specific collection validation; no presentation or chart logic.
import {sha256Canonical,sha256Text,stableJson} from './analytical-integrity.js';

export const forensicContractVersion='forensic-toxicology/1.0.0';
export const forensicContractPath='/analytical/v1/forensic-toxicology';
export const forensicSourceVersion='ccba2a3158b69e38194cafb415dba8834cf080c9174721299977037c4a8bb0df';
export const forensicArtifactVersion='phase4-1.0.0';
export const forensicArtifactSha256='6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063';
export const forensicArtifactExecutedAt='2026-11-10T01:13:49.285090+00:00';
export const forensicCategories=[
 'Opioids','Prescribable Benzodiazepines','Street Benzodiazepines','All Benzodiazepines',
 'Dissociatives','Gabapentinoids','Stimulants',
];
const fail=message=>{throw new Error('Forensic analytical source unavailable: '+message);};
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const text=value=>typeof value==='string'&&/\S/.test(value);
const count=value=>Number.isSafeInteger(value)&&value>=0;
const hash=value=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
function shape(value,keys){
 if(!object(value)||Object.keys(value).length!==keys.length||keys.some(key=>!Object.hasOwn(value,key)))fail('missing or unexpected contract fields.');
}
function strings(value,keys){if(keys.some(key=>!text(value[key])))fail('required forensic metadata is missing.');}
function isoDate(value){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
 const date=new Date(value+'T00:00:00Z');
 return Number.isFinite(+date)&&date.toISOString().slice(0,10)===value;
}
function path(value){
 return text(value)&&!value.startsWith('/')&&!/[\\:]/.test(value)&&!value.split('/').some(part=>!part||part==='.'||part==='..');
}
async function digest(value){
 if(!globalThis.crypto?.subtle)fail('secure SHA-256 verification is unavailable.');
 return sha256Canonical(value);
}
async function rawDigest(value){
 if(!globalThis.crypto?.subtle)fail('secure SHA-256 verification is unavailable.');
 return sha256Text(value);
}
function validateSource(source){
 shape(source,['source_id','source_version','source_path','source_url','publisher','publication_date','publication_status','source_data_cutoff']);
 if(source.source_id!=='radar_toxicology_forensic_2018-2026.csv'
  ||source.source_path!=='datasets/Group3_Item2_Data/radar_toxicology_forensic_2018-2026.csv'
  ||source.source_version!==forensicSourceVersion||!path(source.source_path)
  ||source.source_path.split('/').at(-1)!==source.source_id
  ||source.publisher!=='Public Health Scotland'||source.publication_date!==null
  ||source.publication_status!=='unknown_publication_date'||source.source_data_cutoff!=='2026-03-31')fail('invalid source identity or provenance.');
 let url;try{url=new URL(source.source_url);}catch{fail('invalid source URL.');}
 if(url.protocol!=='https:'||url.username||url.password||url.hostname!=='scotland.shinyapps.io'
  ||url.pathname!=='/phs-drugs-radar-dashboard/')fail('invalid forensic source URL.');
}
function validateArtifact(artifact){
 shape(artifact,['resource','analytical_version','artifact_sha256','source_path','provenance_manifest','storage','executed_at_utc','limitations']);
 if(artifact.resource!=='forensic'||artifact.analytical_version!==forensicArtifactVersion
  ||artifact.artifact_sha256!==forensicArtifactSha256||artifact.source_path!=='analysis/phase4/outputs/forensic_counts.csv'
  ||artifact.provenance_manifest!=='analysis/phase4/outputs/run_manifest.json'
  ||artifact.storage!=='approved_local_artifact'||artifact.executed_at_utc!==forensicArtifactExecutedAt
  ||!Array.isArray(artifact.limitations)||artifact.limitations.length!==2
  ||artifact.limitations.some(item=>!text(item)))fail('invalid artifact identity or provenance.');
}
function validateMeasure(measure){
 shape(measure,['definition','source_measure','unit','period_basis','calculation_method','year_comparison_basis',
  'rolling_periods','reference_periods','scientific_status','sample_or_testing_definition',
  'sample_definition_status','sample_denominator']);
 if(measure.definition!=='Source-reported Number of forensic toxicology detections by original category and calendar quarter; categories overlap and do not represent unique deaths or people.'
  ||measure.source_measure!=='Number'||measure.unit!=='detection_count'||measure.period_basis!=='calendar_quarter'
  ||!text(measure.calculation_method)||measure.year_comparison_basis!=='same_calendar_period_previous_year'
  ||!count(measure.rolling_periods)||measure.rolling_periods===0||!count(measure.reference_periods)||measure.reference_periods===0
  ||measure.scientific_status!=='descriptive_research_only_not_anomaly_or_alert'
  ||measure.sample_or_testing_definition!==null||measure.sample_definition_status!=='not_provided_by_source'
  ||measure.sample_denominator!==null)fail('incompatible forensic measure or reporting definition.');
}
async function validateCategories(categories,source){
 if(!Array.isArray(categories)||categories.length!==forensicCategories.length)fail('missing or duplicate category definitions.');
 const seen=new Set();
 for(let index=0;index<categories.length;index++){
  const category=categories[index];
  shape(category,['category_id','original_label','source_definition','definition_status','relationship','additive']);
  const label=forensicCategories[index];
  if(category.original_label!==label||category.source_definition!==null
   ||category.definition_status!=='source_label_only'||category.relationship!=='overlapping_source_groups'
   ||category.additive!==false||!category.category_id.startsWith('forensic-category:v1:')
   ||!hash(category.category_id.slice('forensic-category:v1:'.length))
   ||category.category_id!=='forensic-category:v1:'+await digest({
    contract_version:forensicContractVersion,source_id:source.source_id,
    source_version:source.source_version,original_label:label,
   })||seen.has(category.category_id))fail('invalid or inconsistent source category definition.');
  seen.add(category.category_id);
 }
 return new Map(categories.map(category=>[category.original_label,category]));
}
function validateResearchMetadata(research){
 shape(research,['analysis_as_of','data_age_days']);
 if(!isoDate(research.analysis_as_of)||!count(research.data_age_days))fail('invalid research metadata.');
}
function validateGeography(geography){
 shape(geography,['geography_id','canonical_name','original_name','boundary_type']);
 if(geography.canonical_name!=='Scotland forensic testing sample'
  ||geography.original_name!=='Scotland forensic testing sample'
  ||geography.boundary_type!=='national_testing_sample')fail('incompatible forensic sample geography.');
}
function validatePeriod(period){
 shape(period,['year','quarter','label','original_label','ordinal','period_start','period_end']);
 if(!Number.isSafeInteger(period.year)||period.year<1900||period.year>2100
  ||!Number.isSafeInteger(period.quarter)||period.quarter<1||period.quarter>4
  ||period.label!==`${period.year} Q${period.quarter}`
  ||period.original_label!==`Q${period.quarter} ${period.year}`
  ||period.ordinal!==period.year*4+period.quarter-1
  ||!isoDate(period.period_start)||!isoDate(period.period_end))fail('invalid forensic reporting quarter.');
 const start=new Date(Date.UTC(period.year,period.quarter*3-3,1)).toISOString().slice(0,10);
 const end=new Date(Date.UTC(period.year,period.quarter*3,0)).toISOString().slice(0,10);
 if(period.period_start!==start||period.period_end!==end)fail('inconsistent forensic quarter dates.');
}
const contextFields=[
 'previous_value','period_change','period_change_pct','year_reference_value','year_change_pct','rolling_average',
 'rolling_periods','historical_reference_mean','reference_periods','reference_change_pct','direction',
 'percentage_point_change','comparison_status','within_source_period_dense_rank','publication_lag_days',
];
function validateContext(context){
 shape(context,contextFields);
 for(const key of ['period_change_pct','year_change_pct','rolling_average','historical_reference_mean','reference_change_pct']){
  if(context[key]!==null&&(typeof context[key]!=='number'||!Number.isFinite(context[key])))fail('invalid nonfinite forensic descriptive value.');
 }
 for(const key of ['previous_value','year_reference_value','within_source_period_dense_rank']){
  if(context[key]!==null&&!count(context[key]))fail('invalid forensic count context.');
 }
 if(context.period_change!==null&&!Number.isSafeInteger(context.period_change))fail('invalid forensic period change.');
 if(!count(context.rolling_periods)||context.rolling_periods===0||!count(context.reference_periods)
  ||context.reference_periods===0||context.percentage_point_change!==null||context.publication_lag_days!==null
  ||!['unavailable','increase','decrease','unchanged'].includes(context.direction)
  ||!['missing_reference','zero_reference_pct_undefined','descriptive_only'].includes(context.comparison_status))fail('incompatible forensic descriptive context.');
}
async function validateObservation(row,shared,categories,seen,periodsByCategory,previous){
 shape(row,['observation_id','indicator_id','category_id','geography','period','value','availability_status','limitations','research_context']);
 if(!text(row.indicator_id)||!row.indicator_id.startsWith('forensic:'))fail('invalid forensic indicator identity.');
 const label=row.indicator_id.slice('forensic:'.length),category=categories.get(label);
 if(!category||category.category_id!==row.category_id)fail('observation category identity is inconsistent.');
 validateGeography(row.geography);validatePeriod(row.period);validateContext(row.research_context);
 if(!text(row.limitations)||!['observed','missing_or_suppressed'].includes(row.availability_status)
  ||(row.availability_status==='observed'?!count(row.value):row.value!==null))fail('invalid forensic value or availability status.');
 const ordinal=row.period.ordinal;
 if(previous.has(label)&&ordinal<=previous.get(label))fail('forensic source observation ordering changed.');
 previous.set(label,ordinal);
 const slot=JSON.stringify([row.category_id,ordinal]);
 if(seen.has(slot))fail('duplicate or overlapping category-period observations.');
 seen.add(slot);periodsByCategory.get(label).add(ordinal);
 const expected='forensic-observation:v1:'+await digest({
  contract_version:shared.contract_version,
  source:shared.source,
  artifact:{analytical_version:shared.artifact.analytical_version,artifact_sha256:shared.artifact.artifact_sha256},
  measure:shared.measure,
  category,
  indicator_id:row.indicator_id,
  geography:row.geography,
  period:row.period,
 });
 if(row.observation_id!==expected)fail('forensic observation identity does not match its source definition.');
 const geoId='national_testing_sample-'+(await rawDigest(row.geography.canonical_name)).slice(0,12);
 if(row.geography.geography_id!==geoId)fail('forensic sample identifier does not match its scope.');
}
export async function collectForensic(api,{pageSize=100}={}){
 if(!Number.isSafeInteger(pageSize)||pageSize<1||pageSize>1000)fail('invalid requested page size.');
 let offset=0,token=null,total=null,shared=null,signature=null;
 const observations=[],seen=new Set(),periodsByCategory=new Map(),previous=new Map();
 let lastCategoryIndex=-1;
 const completedCategories=new Set();
 do{
  const page=await api(forensicContractPath,{offset,limit:pageSize,...(token?{expected_collection:token}:{})});
  shape(page,['contract_version','source','artifact','measure','categories','research_metadata','pagination','observations']);
  if(page.contract_version!==forensicContractVersion)fail('unsupported contract version.');
  validateSource(page.source);validateArtifact(page.artifact);validateMeasure(page.measure);validateResearchMetadata(page.research_metadata);
  const categories=await validateCategories(page.categories,page.source);
  const p=page.pagination;
  shape(p,['total','offset','limit','returned','next_offset','page_is_complete_collection','collection_token','ordering']);
  if(!count(p.total)||p.total!==210||p.offset!==offset||p.limit!==pageSize
   ||!count(p.returned)||p.returned===0||p.returned>pageSize||!Array.isArray(page.observations)
   ||p.returned!==page.observations.length||!hash(p.collection_token)||p.ordering!=='original_artifact_row_order')fail('pagination mismatch or incomplete forensic collection.');
  if(token!==null&&(p.collection_token!==token||p.total!==total||stableJson(page.source)!==signature.source
   ||stableJson(page.artifact)!==signature.artifact||stableJson(page.measure)!==signature.measure
   ||stableJson(page.categories)!==signature.categories||stableJson(page.research_metadata)!==signature.research))fail('source, artifact, category or collection version changed during pagination.');
  if(token===null){
   shared={contract_version:page.contract_version,source:page.source,artifact:page.artifact,measure:page.measure,
    categories:page.categories,research_metadata:page.research_metadata};
   signature={source:stableJson(page.source),artifact:stableJson(page.artifact),measure:stableJson(page.measure),
    categories:stableJson(page.categories),research:stableJson(page.research_metadata)};
   token=p.collection_token;total=p.total;
   for(const category of page.categories)periodsByCategory.set(category.original_label,new Set());
  }
  const end=offset+p.returned;
  if(end>total||p.next_offset!==(end<total?end:null)
   ||p.page_is_complete_collection!==(offset===0&&end===total))fail('forensic pagination gap or incorrect completeness.');
  for(const row of page.observations){
   const label=row.indicator_id?.startsWith('forensic:')?row.indicator_id.slice('forensic:'.length):'';
   const categoryIndex=forensicCategories.indexOf(label);
   if(categoryIndex<0||categoryIndex<lastCategoryIndex||completedCategories.has(categoryIndex))fail('source observation ordering changed.');
   if(lastCategoryIndex>=0&&categoryIndex>lastCategoryIndex)completedCategories.add(lastCategoryIndex);
   lastCategoryIndex=categoryIndex;
   await validateObservation(row,shared,categories,seen,periodsByCategory,previous);
  }
  observations.push(...page.observations);offset=end;
 }while(offset<total);
 if(observations.length!==total||seen.size!==210)fail('partial forensic observation collection.');
 const periods=[...new Set(observations.map(row=>row.period.ordinal))].sort((a,b)=>a-b);
 if(periods.length!==30||periods.at(-1)-periods[0]!==29
  ||[...periodsByCategory.values()].some(values=>values.size!==30||periods.some(period=>!values.has(period))))fail('incomplete category-quarter coverage.');
 return {...shared,observations,total,collection_token:token,complete:true};
}
