// Display transformations only. No statistical methods or observations are calculated.
import {definitionKey,modelKey,periodInfo,periodSlots,valueOf} from './chart-data.js';
import {compatibleSubstances,categoryOf} from './substance-data.js';
export const compatibleAreas=(areas,area,indicator)=>areas.filter(other=>other.available&&other.geography_id!==area?.geography_id&&other.boundary_type===area?.boundary_type&&other.indicators.includes(indicator)).sort((a,b)=>a.name.localeCompare(b.name));
export const periodOf=row=>String(row.period??row.period_label??(row.year&&row.quarter?`${row.year} Q${row.quarter}`:row.year)??'');
export function comparisonTable(rows,options={}){
 verifyDefinitions(rows,options);
 const periods=new Map();
 for(const row of rows){
  if(!['first_area','second_area'].includes(row.comparison_role))throw new Error('Comparison response is missing area roles.');
  const key=periodInfo(row).key;if(!key)throw new Error('Comparison response is missing reporting periods.');
  const item=periods.get(key)??{period:key};
  if(item[row.comparison_role])throw new Error('Multiple measurements share a period. Choose a more specific measure.');
  item[row.comparison_role]=row;periods.set(key,item);
 }
 return (options.slots??periodSlots(rows)).map(slot=>periods.get(slot.key)??{period:slot.label}).map(item=>({...item,left:valueOf(item.first_area),right:valueOf(item.second_area),coverage:!item.first_area||!item.second_area?'missing_period':valueOf(item.first_area)===null||valueOf(item.second_area)===null?'unavailable_value':'paired'}));
}
export function verifyDefinitions(rows,{kind='areas'}={}){
 if(!['areas','substances'].includes(kind))throw new Error('Unsupported comparison type.');
 const signatures=new Set(rows.map(definitionKey));
 if(kind==='areas'&&signatures.size>1)throw new Error('Incompatible reporting definitions, units or boundaries. These series cannot be compared as one measure.');
 if(kind==='substances'){
  compatibleSubstances(rows);
  if(new Set(rows.map(r=>definitionKey({...r,indicator_id:null,substance_category:null}))).size>1)throw new Error('Incompatible source or reporting definitions for substance categories.');
  for(const role of ['first_area','second_area'])if(new Set(rows.filter(r=>r.comparison_role===role).map(r=>JSON.stringify([r.indicator_id,r.substance_category??null]))).size>1)throw new Error('Comparison subject contains multiple category definitions.');
  const subjects=['first_area','second_area'].map(role=>rows.find(r=>r.comparison_role===role)).filter(Boolean);
  if(subjects.length===2&&categoryOf(subjects[0])===categoryOf(subjects[1]))throw new Error('Choose two distinct substance categories.');
 }
 const extra=['sex','age_group','sample_type','population_definition','denominator_definition','standard_population'];
 if(new Set(rows.map(r=>JSON.stringify(extra.map(k=>r[k]??null)))).size>1)throw new Error('Incompatible sample, population or denominator definitions.');
 if(rows.some(r=>/rate|per.?100|standardised/i.test(r.unit??'')))throw new Error('Population-rate comparison is unavailable: compatible denominators and standardisation are not verified by this comparison contract.');
 if(new Set(rows.map(modelKey)).size>1)throw new Error('Incompatible models or monitoring windows. Choose one model and window before comparing.');
 for(const role of ['first_area','second_area'])if(new Set(rows.filter(r=>r.comparison_role===role).map(r=>JSON.stringify([r.geography_id??null,r.geography??null]))).size>1)throw new Error('Comparison role contains multiple geographic definitions.');
 const periods=new Map();
 for(const row of rows){const key=periodInfo(row).key,dates=JSON.stringify([row.period_start??null,row.period_end??null,row.study_period??null,row.ordinal??null]);if(periods.has(key)&&periods.get(key)!==dates)throw new Error('Incompatible reporting period boundaries.');periods.set(key,dates);}
}
export function comparisonCsv(table,left,right,metadata){
 const escape=value=>{let text=value===null||value===undefined?'':String(value);if(/^[\s]*[=+@-]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
 const header=['period','first_subject','first_value','first_status','second_subject','second_value','second_status','unit','first_indicator','second_indicator','source_id','reporting_basis','reporting_definition','coverage','first_record_provenance','second_record_provenance','comparison_metadata'];
 return '\uFEFF'+[header,...table.map(r=>{const record=r.first_area??r.second_area??{};return[r.period,left,r.left,r.left===null?'missing_or_unavailable':'observed',right,r.right,r.right===null?'missing_or_unavailable':'observed',record.unit,r.first_area?.indicator_id,r.second_area?.indicator_id,record.source_id,record.period_basis,record.reporting_definition,r.coverage,JSON.stringify(r.first_area??null),JSON.stringify(r.second_area??null),JSON.stringify(metadata)];})].map(row=>row.map(escape).join(',')).join('\r\n');
}

// Used by both the quick dialog and the dedicated workspace. Partial histories
// fail closed instead of being silently labelled as complete exports.
export async function completeComparison(api,path,params={},isCurrent=()=>true){
 let rows=[],total=null,metadata={};
 do{
  const response=await api(path,{...params,offset:rows.length,limit:1000});
  if(!isCurrent())return null;
  if(!['ready','empty'].includes(response.state))return response;
  if(!Number.isInteger(response.total)||response.total<0||response.total>10000||!Array.isArray(response.data))throw new Error('Comparison exceeds the verified 10,000-observation scope. Choose a narrower range.');
  if(total!==null&&(total!==response.total||metadata.artifact_sha256!==response.metadata?.artifact_sha256))throw new Error('Comparison source changed during pagination; refresh before interpreting or exporting.');
  total=response.total;metadata=response.metadata??{};
  rows.push(...response.data);
  if(rows.length>total||(!response.data.length&&rows.length<total)||response.state==='empty'&&total!==0)throw new Error('Incomplete comparison response; partial pages cannot be exported as complete history.');
 }while(rows.length<total);
 return{state:rows.length?'ready':'empty',data:rows,total,metadata,message:rows.length?'':'No accessible observations for the selected comparison; this is not evidence of zero harm.'};
}
export function comparisonSummary(table){
 return{periods:table.length,shared:table.filter(r=>r.first_area&&r.second_area).length,paired:table.filter(r=>r.coverage==='paired').length,missingPeriods:table.filter(r=>r.coverage==='missing_period').length,unavailableValues:table.filter(r=>r.coverage==='unavailable_value').length};
}
export function comparisonRange(rows,from,to){
 const slots=periodSlots(rows),start=slots.findIndex(p=>p.key===from),end=slots.findIndex(p=>p.key===to);
 if(start<0||end<start)throw new Error('From reporting period must be no later than To reporting period.');
 const selected=slots.slice(start,end+1),keys=new Set(selected.map(p=>p.key));
 return{slots:selected,rows:rows.filter(r=>keys.has(periodInfo(r).key))};
}
export function categoryComparison(rows,first,second){
 if(!first||!second||first===second)throw new Error('Choose two distinct available substance categories.');
 const selected=rows.filter(r=>[first,second].includes(categoryOf(r))).map(r=>({...r,comparison_role:categoryOf(r)===first?'first_area':'second_area'}));
 verifyDefinitions(selected,{kind:'substances'});return selected;
}
export function verifyAreaSubjects(rows,{first,second,indicator}){
 if(!first||!second||first===second)throw new Error('Choose two distinct reporting areas.');
 for(const row of rows){const index=['first_area','second_area'].indexOf(row.comparison_role);if(index<0||row.geography_id!==[first,second][index]||row.indicator_id!==indicator)throw new Error('Comparison response subjects or indicator do not match the requested areas and measure.');}
}
