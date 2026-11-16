// Source-specific contract validation and complete retrieval; no chart code.
import {sha256Canonical,sha256Text,stableJson} from './analytical-integrity.js';

export const mortalityContractVersion='mortality-trends/1.0.0';
export const mortalityContractPath='/analytical/v1/mortality-trends';
export {stableJson};
const fail=message=>{throw new Error('Mortality analytical source unavailable: '+message);};
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const text=x=>typeof x==='string'&&/\S/.test(x);
const count=x=>Number.isSafeInteger(x)&&x>=0;
const hash=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
function shape(value,keys){if(!object(value)||Object.keys(value).length!==keys.length||keys.some(k=>!Object.hasOwn(value,k)))fail('missing or unexpected contract fields.');}
function strings(value,keys){if(keys.some(k=>!text(value[k])))fail('required source metadata is missing.');}
function isoDate(value){if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;const d=new Date(value+'T00:00:00Z');return Number.isFinite(+d)&&d.toISOString().slice(0,10)===value;}
function path(value){return text(value)&&!value.startsWith('/')&&!/[\\:]/.test(value)&&!value.split('/').some(p=>!p||p==='.'||p==='..');}
export async function sha256(value){
 if(!globalThis.crypto?.subtle)fail('secure SHA-256 verification is unavailable.');
 return sha256Canonical(value);
}
export const contextFields=['share_of_national_pct','previous_value','period_change','period_change_pct','year_reference_value','year_change_pct','rolling_average','historical_reference_mean','reference_change_pct','direction','percentage_point_change','comparison_status','publication_lag_days'];
function metadata(page){
 shape(page,['contract_version','source','indicator','artifact','research_metadata','pagination','observations']);
 if(page.contract_version!==mortalityContractVersion)fail('unsupported contract version.');
 const s=page.source,i=page.indicator,a=page.artifact,r=page.research_metadata;
 shape(s,['source_id','source_version','source_path','source_url','publication_date','publication_status','source_data_cutoff']);
 strings(s,['source_id','source_path','source_url','publication_status']);
 if(!hash(s.source_version)||!path(s.source_path)||s.source_path.split('/').at(-1)!==s.source_id)fail('invalid source identity or provenance.');
 let url;try{url=new URL(s.source_url);}catch{fail('invalid source URL.');}
 if(url.protocol!=='https:'||url.username||url.password)fail('invalid source URL.');
 for(const k of ['publication_date','source_data_cutoff'])if(s[k]!==null&&!isoDate(s[k]))fail('invalid source date.');
 shape(i,['indicator_id','definition','unit','period_basis','original_reporting_qualification','scientific_status','calculation_method','year_comparison_basis','rolling_periods','reference_periods']);
 strings(i,['definition','original_reporting_qualification','scientific_status','calculation_method','year_comparison_basis']);
 if(i.indicator_id!=='suspected_deaths'||i.unit!=='count'||i.period_basis!=='calendar_quarter_legacy_10_day_adjustment'||i.definition!=='Police Scotland provisional originally suspected drug deaths; not NRS registered deaths or population-adjusted risk.'||!count(i.rolling_periods)||!i.rolling_periods||!count(i.reference_periods)||!i.reference_periods)fail('incompatible indicator or reporting definition.');
 shape(a,['resource','analytical_version','artifact_sha256','source_path','provenance_manifest','storage','executed_at_utc','limitations']);
 if(a.resource!=='mortality_trends'||!text(a.analytical_version)||!hash(a.artifact_sha256)||a.source_path!=='analysis/phase4/outputs/mortality_quarterly.csv'||a.provenance_manifest!=='analysis/phase4/outputs/run_manifest.json'||a.storage!=='approved_local_artifact'||!text(a.executed_at_utc)||!Number.isFinite(Date.parse(a.executed_at_utc))||!Array.isArray(a.limitations)||a.limitations.some(x=>!text(x)))fail('invalid artifact metadata.');
 shape(r,['analysis_as_of','data_age_days']);if(!isoDate(r.analysis_as_of)||!count(r.data_age_days))fail('invalid research metadata.');
 return {contract_version:page.contract_version,source:s,indicator:i,artifact:a,research_metadata:r};
}
async function observation(row,shared,seen,slots,last){
 shape(row,['observation_id','geography','period','value','availability_status','research_context']);
 const g=row.geography,p=row.period,c=row.research_context;
 shape(g,['geography_id','canonical_name','original_name','boundary_type']);strings(g,['geography_id','canonical_name','original_name']);
 if(!['country','police_division'].includes(g.boundary_type))fail('unsupported geographic boundary.');
 const national=['Scotland','Scotland national total'].includes(g.original_name);
 if((national&&(g.boundary_type!=='country'||g.canonical_name!=='Scotland'))||(!national&&(g.boundary_type!=='police_division'||!g.original_name.includes(': ')||g.canonical_name!==g.original_name)))fail('inconsistent geographic scope.');
 // Geographic IDs use SHA-256 of raw UTF-8 names, not JSON string encoding.
 const actualGid=g.boundary_type+'-'+(await sha256Text(g.canonical_name)).slice(0,12);
 if(g.geography_id!==actualGid)fail('geographic identifier does not match its scope.');
 shape(p,['year','quarter','label','ordinal','period_start','period_end']);
 if(!Number.isSafeInteger(p.year)||p.year<1900||p.year>2100||!Number.isSafeInteger(p.quarter)||p.quarter<1||p.quarter>4||p.label!==`${p.year} Q${p.quarter}`||p.ordinal!==p.year*4+p.quarter-1||!isoDate(p.period_start)||!isoDate(p.period_end))fail('invalid quarterly period.');
 const start=new Date(Date.UTC(p.year,p.quarter*3-3,1)).toISOString().slice(0,10),end=new Date(Date.UTC(p.year,p.quarter*3,0)).toISOString().slice(0,10);
 if(p.period_start!==start||p.period_end!==end)fail('incompatible quarterly dates.');
 if(!['observed','missing_or_suppressed'].includes(row.availability_status)||(row.availability_status==='observed'?!count(row.value):row.value!==null))fail('invalid count/availability combination.');
 shape(c,contextFields);strings(c,['direction','comparison_status']);
 for(const k of contextFields.filter(k=>!['direction','comparison_status'].includes(k)))if(c[k]!==null&&(typeof c[k]!=='number'||!Number.isFinite(c[k])))fail('invalid descriptive context.');
 if(!count(c.publication_lag_days)||['previous_value','year_reference_value'].some(k=>c[k]!==null&&!count(c[k]))||c.period_change!==null&&!Number.isSafeInteger(c.period_change))fail('invalid count reference.');
 const identity='mortality-observation:v1:'+await sha256({contract_version:shared.contract_version,source_id:shared.source.source_id,source_version:shared.source.source_version,indicator:shared.indicator,geography:g,period:p});
 const slot=stableJson([g.geography_id,p.label]);
 if(row.observation_id!==identity||seen.has(identity)||slots.has(slot))fail('invalid or duplicate observation identity.');
 if(last.has(g.geography_id)&&last.get(g.geography_id)>=p.ordinal)fail('quarterly order changed.');
 seen.add(identity);slots.add(slot);last.set(g.geography_id,p.ordinal);
}
export async function collectMortality(api,{pageSize=100}={}){
 if(!Number.isSafeInteger(pageSize)||pageSize<1||pageSize>1000)fail('invalid requested page size.');
 let offset=0,token=null,total=null,shared=null,signature=null;
 const observations=[],seen=new Set(),slots=new Set(),last=new Map();
 do{
  const page=await api(mortalityContractPath,{offset,limit:pageSize,...(token?{expected_collection:token}:{})});
  const current=metadata(page),p=page.pagination;
  shape(p,['total','offset','limit','returned','next_offset','page_is_complete_collection','collection_token','ordering']);
  if(!count(p.total)||p.total===0||p.total>10000||p.offset!==offset||p.limit!==pageSize||!count(p.returned)||p.returned===0||p.returned>pageSize||!Array.isArray(page.observations)||p.returned!==page.observations.length||!hash(p.collection_token)||p.ordering!=='original_artifact_row_order')fail('pagination mismatch or incomplete collection.');
  if(token!==null&&(p.collection_token!==token||p.total!==total||stableJson(current)!==signature))fail('source, artifact or collection version changed during pagination.');
  token=p.collection_token;total=p.total;shared=current;signature=stableJson(current);
  const end=offset+p.returned;
  if(end>total||p.next_offset!==(end<total?end:null)||p.page_is_complete_collection!==(offset===0&&end===total))fail('pagination gap, overlap or incorrect completeness.');
  for(const row of page.observations)await observation(row,shared,seen,slots,last);
  observations.push(...page.observations);offset=end;
 }while(offset<total);
 if(observations.length!==total)fail('partial collection.');
 return {...shared,observations,total,collection_token:token,complete:true};
}
