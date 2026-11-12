import {completeMortality,mortalitySources} from './mortality-data.js';
import {completeSubstances,substanceSources} from './substance-data.js';
import {completeComparison,verifyDefinitions,comparisonRange} from './comparison-data.js';
import {periodInfo,periodSlots,prepareChart,seriesKey} from './chart-data.js';
export const geographicSources={
 nrs:{...mortalitySources.nrs,resource:'annual',unit:'deaths',basis:'calendar_year_of_registration'},
 police:{...mortalitySources.police,resource:'mortality_trends',unit:'count',basis:'calendar_quarter_legacy_10_day_adjustment'},
 naloxone:{label:'Scottish Ambulance Service — naloxone activity',resource:'naloxone',indicator:'ambulance_naloxone_activity',unit:'incident_count',basis:'week_beginning_monday',definition:'Weekly ambulance naloxone activity, not confirmed overdose or toxicity incidence, take-home supply or population-adjusted risk. National, Unknown and health-board observations must not be added together.'},
 ...Object.fromEntries(['forensic','assist','treatment'].map(key=>[key,{...substanceSources[key],resource:key}]))
};
export const boundaryLabel=boundary=>({council:'Local authority / council',police_division:'Police Scotland division',health_board:'NHS health board',country:'Scotland national total',locality:'Locality',national_testing_sample:'National forensic testing sample (not a territorial boundary)',study_sample:'ASSIST study sample (not a territorial boundary)',unknown:'Unassigned geography (not a region)'}[boundary]??boundary);
export const mapState={state:'unavailable',message:'Map unavailable: no verified boundary geometry or geographic crosswalk is integrated with these observations. API geographic identifiers identify evidence scopes; they are not polygons. No decorative or inferred regions are drawn.'};
export function sourcesForBoundary(registry,boundary){return Object.entries(geographicSources).filter(([,spec])=>registry.some(area=>area.boundary_type===boundary&&area.resources?.includes(spec.resource))).map(([id])=>id);}
export function validateGeography(rows,source,registry){
 const spec=geographicSources[source];if(!spec)throw Error('Unknown geographic source.');const seen=new Set();
 for(const row of rows){const area=registry.find(a=>a.geography_id===row.geography_id);
  if(!area||area.boundary_type!==row.boundary_type||area.name!==(row.name??row.geography)||!area.resources?.includes(spec.resource)||!area.indicators?.includes(row.indicator_id)||row.unit!==spec.unit||row.period_basis!==spec.basis||!row.source_sha256||!row.source_path)throw Error('Unverified geographic identity, source, indicator, units or reporting definition.');
  if(spec.indicator&&row.indicator_id!==spec.indicator)throw Error('Incompatible geographic indicator.');
  if(row.observed_value!=null&&(!Number.isFinite(row.observed_value)||row.observed_value<0||(row.unit!=='percent'&&!Number.isInteger(row.observed_value))||(row.unit==='percent'&&row.observed_value>100)))throw Error('Invalid geographic observation.');
  if(source==='naloxone'&&(periodInfo(row).kind!=='week'||row.period!==row.period_start||new Date(row.period_end+'T00:00:00Z').getTime()-new Date(row.period_start+'T00:00:00Z').getTime()!==6*86400000))throw Error('Unverified weekly reporting boundaries.');
  const key=seriesKey(row)+periodInfo(row).key;if(seen.has(key))throw Error('Duplicate geographic observation.');seen.add(key);
 }
 prepareChart(rows);
}
export async function geographicSource(api,source,registry){
 let result;if(['police','nrs'].includes(source))result=await completeMortality(api,source);else if(['forensic','assist','treatment'].includes(source))result=await completeSubstances(api,source);else if(source==='naloxone')result=await completeComparison(api,'/naloxone/activity');else throw Error('Unknown geographic source.');
 if(!['ready','empty'].includes(result.state))throw Error(result.message||'Geographic source unavailable.');validateGeography(result.data,source,registry);return result;
}
export function geographicSelection(rows,{boundary,indicator,area,from,to}){
 const compatible=rows.filter(r=>r.boundary_type===boundary&&r.indicator_id===indicator),range=comparisonRange(compatible,from,to);
 return{...range,areaRows:range.rows.filter(r=>r.geography_id===area).sort((a,b)=>{const x=periodInfo(a).order,y=periodInfo(b).order;return typeof x==='number'&&typeof y==='number'?x-y:String(x).localeCompare(String(y));})};
}
export function geographicRanking(rows,{boundary,indicator,period}){
 const selected=rows.filter(r=>r.boundary_type===boundary&&r.indicator_id===indicator&&periodInfo(r).key===period);verifyDefinitions(selected);
 if(new Set(selected.map(r=>r.geography_id)).size!==selected.length)throw Error('Duplicate geographic ranking rows.');
 const available=selected.filter(r=>Number.isFinite(r.observed_value)).sort((a,b)=>b.observed_value-a.observed_value||a.geography.localeCompare(b.geography));
 return{state:available.length>=2&&!['unknown','locality','study_sample','national_testing_sample','country'].includes(boundary)?'ready':'unavailable',rows:available,missing:selected.filter(r=>r.observed_value==null),period,message:'Fewer than two compatible territorial areas have observed values at this boundary and reporting period. National totals, samples and unassigned records are not peer regions. No boundary substitution or population-risk ranking is made.',label:'Raw source observations; counts are not population-adjusted risk.'};
}
export function geographicProfile(area,results){
 const records=Object.entries(results).flatMap(([source,result])=>(result.data??[]).filter(r=>r.geography_id===area.geography_id).map(record=>({source,record})));
 const indicators=[...new Set(area.indicators??[])].map(indicator=>{const history=records.filter(r=>r.record.indicator_id===indicator),periods=periodSlots(history.map(r=>r.record));return{indicator,observations:history.length,observed:history.filter(r=>r.record.observed_value!=null).length,coverage:periods.length?`${periods[0].label} to ${periods.at(-1).label}`:'Unavailable',units:[...new Set(history.map(r=>r.record.unit))],sources:[...new Set(history.map(r=>geographicSources[r.source].label))]};});
 return{...area,indicators,history:records.map(r=>r.record),limitations:[...new Set([area.limitation,'No wider-area observation establishes Greenock-specific outcomes.',...records.map(r=>r.record.limitations??r.record.small_number_qualification)].filter(Boolean))],provenance:records.map(r=>({source:geographicSources[r.source].label,path:r.record.source_path,sha256:r.record.source_sha256,source_url:r.record.source_url,publication_date:r.record.publication_date,source_data_cutoff:r.record.source_data_cutoff}))};
}
export function geographicCoverage(registry,results,rates={data:[]}){
 const coverage=[];
 for(const area of registry){
  if(!area.available){coverage.push({area:area.name,id:area.geography_id,boundary:area.boundary_type,indicator:'No compatible local outcome series',period:'Unavailable',unit:'Unavailable',source:'No admitted source',status:'Unavailable evidence',notes:area.limitation});continue;}
  for(const[source,spec]of Object.entries(geographicSources))if(area.resources?.includes(spec.resource)){
   const result=results[source],history=(result?.data??[]).filter(r=>r.geography_id===area.geography_id),declared=(area.indicators??[]).filter(id=>spec.indicator?id===spec.indicator:id.startsWith(source+':'));
   for(const indicator of declared){const observations=history.filter(r=>r.indicator_id===indicator),periods=periodSlots(observations),observed=observations.filter(r=>r.observed_value!=null).length;coverage.push({area:area.name,id:area.geography_id,boundary:area.boundary_type,indicator,period:periods.length?`${periods[0].label} to ${periods.at(-1).label}`:'Unavailable',unit:spec.unit,source:spec.label,status:result?.state==='error'?'Source unavailable':observations.length?(observed?'Available source observations':'Unavailable values only'):'No accessible observations',notes:result?.message??`${observations.length} records; ${observed} observed values. Zero values are retained.`});}
  }
  const published=(rates.data??[]).filter(r=>r.geography_id===area.geography_id);if(published.length)coverage.push({area:area.name,id:area.geography_id,boundary:area.boundary_type,indicator:'Published five-year registered mortality ASR',period:`${published[0].period_label} to ${published.at(-1).period_label}`,unit:published[0].unit,source:'National Records of Scotland — Table C4',status:'Published rates available',notes:'Source-provided age-standardised rates, not annual crude rates.'});
  else if(rates.state==='error'&&['Inverclyde','Scotland'].includes(area.name)&&area.resources?.includes('annual'))coverage.push({area:area.name,id:area.geography_id,boundary:area.boundary_type,indicator:'Published five-year registered mortality ASR',period:'Unavailable',unit:'published_age_standardised_deaths_per_100000',source:'National Records of Scotland — Table C4',status:'Source unavailable',notes:rates.message});
 }
 return coverage;
}
export function coveragePage(rows,search='',page=0){const matched=rows.filter(r=>Object.values(r).join(' ').toLowerCase().includes(search.toLowerCase())),pages=Math.ceil(matched.length/12),position=Math.max(0,Math.min(page,pages-1));return{matched,rows:matched.slice(position*12,position*12+12),pages,page:position};}
export function publishedRates(rows,contract){
 const source=contract?.source;if(!source)throw Error('Published rate definitions unavailable.');
 for(const row of rows){if(!['Inverclyde','Scotland'].includes(row.geography)||row.boundary_type!==(row.geography==='Inverclyde'?'council':'country')||row.indicator_id!==source.indicator_id||row.source_sha256!==source.source_sha256||row.period_basis!=='five_year_registration_period'||row.unit!=='published_age_standardised_deaths_per_100000'||row.standard_population!=='2013 European Standard Population'||!row.source_cells||row.rate_origin!=='NRS published; not recalculated or back-solved from total counts')throw Error('Unverified published rate definition or provenance.');
  if(!Number.isInteger(row.start_year)||row.end_year!==row.start_year+4||row.period_label!==`${row.start_year} - ${row.end_year}`||row.period_start!==`${row.start_year}-01-01`||row.period_end!==`${row.end_year}-12-31`||row.quality_status!=='published')throw Error('Unverified published five-year reporting window.');
  if([row.rate,row.lower95,row.upper95].some(v=>v!=null&&(!Number.isFinite(v)||v<0))||row.rate!=null&&row.lower95!=null&&row.lower95>row.rate||row.rate!=null&&row.upper95!=null&&row.upper95<row.rate)throw Error('Invalid published rate interval.');
 }
 const keys=rows.map(r=>r.geography+':'+r.period_label);if(new Set(keys).size!==keys.length)throw Error('Duplicate published rate record.');return rows;
}
