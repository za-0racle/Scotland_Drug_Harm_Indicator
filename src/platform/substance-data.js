import {periodInfo,periodSlots,periodLabel,seriesKey,prepareChart} from './chart-data.js';
import {mortalityCsv} from './mortality-data.js';
export const substanceSources={
 forensic:{label:'Forensic toxicology',unit:'detection_count',basis:'calendar_quarter',definition:'Quarterly detections in the Scotland forensic testing sample. Overlapping categories are not causal death counts. Testing selection and volume may change; sample denominators are unavailable.'},
 assist:{label:'ASSIST toxicology',unit:'percent',basis:'source_study_period_not_calendar_quarter',definition:'Reported percentages in the selected participating emergency-department cohort. Unequal study periods are categorical points, not calendar quarters. Q9 recruitment was shortened; denominators are unavailable. No pooled percentages or population prevalence.'},
 treatment:{label:'Treatment toxicology',unit:'detection_count',basis:'calendar_month',definition:'Monthly urine-sample detections in NHS Greater Glasgow and Clyde treatment services. The source opioid category excludes treatment opioids. Testing selection and volume may change; overlapping categories are not community prevalence.'},
 radar:{label:'RADAR contextual intelligence',pending:'Raw RADAR intelligence is not exposed by the approved API. Existing cross-source contextual research is available in Surveillance Signals; it is not a comparable substance series.'},
 phase9:{label:'NRS individual substances — pending integration',pending:'Phase 9 artifacts exist locally but are not integrated into the active API. Separate approval is required for backend routes and frozen research scope. No Phase 9 results are loaded here.'}
};
export const categoryOf=r=>r.substance_category??r.indicator_id?.split(':').slice(1).join(':');
export function validateSubstances(rows,source){
 const spec=substanceSources[source],seen=new Set();if(!spec||spec.pending)throw Error('Source pending integration.');
 for(const r of rows){
  if(!r.indicator_id?.startsWith(source+':')||!categoryOf(r)||r.unit!==spec.unit||r.period_basis!==spec.basis||!r.geography_id||!r.source_id||!r.source_sha256||!periodLabel(r))throw Error('Unverified substance source, identity, units or reporting definition.');
  if(source!=='assist'&&periodInfo(r).kind!==(source==='forensic'?'quarter':'month'))throw Error('Unverified calendar reporting period.');
  if(r.observed_value!=null&&(!Number.isFinite(r.observed_value)||r.observed_value<0||(spec.unit==='detection_count'&&!Number.isInteger(r.observed_value))||(spec.unit==='percent'&&r.observed_value>100)))throw Error('Invalid observation value.');
  const key=seriesKey(r)+periodLabel(r);if(seen.has(key))throw Error('Duplicate substance observation.');seen.add(key);
 }
 prepareChart(rows);
}
export async function completeSubstances(api,source){
 if(substanceSources[source]?.pending)return{state:'unavailable',data:[],total:0,metadata:{},message:substanceSources[source].pending};
 let data=[],total=null,metadata={};
 do{const result=await api('/toxicology/'+source,{offset:data.length,limit:1000});
  if(!['ready','empty'].includes(result.state))throw Error(result.message||'Source unavailable.');
  if(total!==null&&(total!==result.total||metadata.artifact_sha256!==result.metadata?.artifact_sha256))throw Error('Source changed during pagination.');
  total=result.total;metadata=result.metadata??{};if(!Number.isInteger(total)||total<0||total>20000)throw Error('Source exceeds verified scope.');
  data.push(...result.data);if(data.length>total||(!result.data.length&&data.length<total))throw Error('Incomplete source history.');
 }while(data.length<total);
 validateSubstances(data,source);return{state:data.length?'ready':'empty',data,total,metadata};
}
export function substanceOptions(rows){return{areas:[...new Map(rows.map(r=>[r.geography_id,r.geography])).entries()],categories:[...new Set(rows.map(categoryOf))].sort(),periods:periodSlots(rows)};}
export function selectSubstances(rows,{area,category='',from,to}){
 const slots=periodSlots(rows),a=slots.findIndex(p=>p.key===from),b=slots.findIndex(p=>p.key===to);if(a<0||b<a)throw Error('Select an ordered reporting-period range.');
 const allowed=new Set(slots.slice(a,b+1).map(p=>p.key));return rows.filter(r=>r.geography_id===area&&(!category||categoryOf(r)===category)&&allowed.has(periodLabel(r)));
}
const compatibility=r=>JSON.stringify([r.source_id,r.source_sha256,r.unit,r.period_basis,r.reporting_definition??null,r.geography_id,r.boundary_type,r.sample_type??null]);
export function compatibleSubstances(rows){
 if(new Set(rows.map(compatibility)).size>1)throw Error('Comparison requires one source, unit, reporting definition and geography.');
 prepareChart(rows);return rows;
}
export function substanceHeatmap(rows){
 compatibleSubstances(rows);if(rows.some(r=>periodInfo(r).kind==='irregular'))return{state:'unavailable',message:'Heatmap unavailable: unequal ASSIST study periods and unavailable denominators prevent a comparable calendar grid. Use the labelled observations and point chart.'};
 const periods=periodSlots(rows),categories=[...new Set(rows.map(categoryOf))].sort();
 return{state:rows.length?'ready':'unavailable',periods,rows:categories.map(category=>({category,values:periods.map(p=>rows.find(r=>categoryOf(r)===category&&periodLabel(r)===p.key)?.observed_value??null)}))};
}
export function substanceRanking(rows,period){
 const chosen=rows.filter(r=>periodLabel(r)===period);compatibleSubstances(chosen);
 if(new Set(chosen.map(r=>JSON.stringify([r.period_start??null,r.period_end??null,r.study_period??null]))).size>1)throw Error('Incompatible reporting windows.');
 return{rows:chosen.filter(r=>Number.isFinite(r.observed_value)).sort((a,b)=>b.observed_value-a.observed_value),missing:chosen.filter(r=>r.observed_value==null)};
}
export function substanceProfile(rows,category,source){
 const history=rows.filter(r=>categoryOf(r)===category),spec=substanceSources[source];return{category,source:spec.label,definition:spec.definition,observations:history.length,periods:periodSlots(history).map(p=>p.label),units:[...new Set(history.map(r=>r.unit))],geographies:[...new Set(history.map(r=>r.geography))],denominator:'Unavailable in the approved observations; no prevalence estimate.',limitations:[...new Set(history.map(r=>r.limitations).filter(Boolean))],provenance:history.map(r=>({source_id:r.source_id,source_sha256:r.source_sha256,source_path:r.source_path,source_url:r.source_url,publication_date:r.publication_date,source_data_cutoff:r.source_data_cutoff})),history,note:'First recorded dataset appearance does not establish first occurrence in Scotland.'};
}
export function substanceTable(rows,search='',page=0){const matched=rows.filter(r=>[categoryOf(r),periodLabel(r),r.geography,r.unit,r.source_id,r.quality_status,r.limitations].join(' ').toLowerCase().includes(search.toLowerCase()));const pages=Math.ceil(matched.length/12),position=Math.max(0,Math.min(page,pages-1));return{matched,rows:matched.slice(position*12,position*12+12),page:position,pages};}
export const exportScope='Complete eligible dataset: all search matches across table pages; charts ignore table search.';
export const substanceCsv=(rows,metadata)=>mortalityCsv(rows,{...metadata,export_scope:exportScope});
