import {mortalitySummary} from './presentation.js';

export const mortalitySource='Police Scotland · suspected drug deaths';
export const number=value=>Number.isFinite(value)?new Intl.NumberFormat('en-GB',{maximumFractionDigits:2}).format(value):'Unavailable';
export function mortalityGrid(rows){
 const records=new Map();
 for(const row of rows){
  if(!Number.isInteger(row.year)||!Number.isInteger(row.quarter)||row.quarter<1||row.quarter>4)throw new Error('Mortality reporting periods could not be verified.');
  if(row.suspected_deaths!=null&&(!Number.isInteger(row.suspected_deaths)||row.suspected_deaths<0))throw new Error('Mortality count could not be verified.');
  const key=`${row.year} Q${row.quarter}`;
  if(records.has(key))throw new Error('Multiple mortality observations share a quarter; overview withheld.');
  records.set(key,row);
 }
 const years=[...new Set(rows.map(r=>r.year))].sort((a,b)=>a-b);
 if(!years.length)return[];
 if(years.at(-1)-years[0]>200)throw new Error('Mortality reporting range exceeds the overview scope.');
 return Array.from({length:years.at(-1)-years[0]+1},(_,i)=>{const year=years[0]+i;return{year,quarters:[1,2,3,4].map(quarter=>{const record=records.get(`${year} Q${quarter}`);return{year,quarter,value:record?.suspected_deaths??null,record:record??null};})};});
}
export function overviewKpis(database,sources=[]){
 const rows=database?.state==='ready'?database.data:[];mortalityGrid(rows);
 const stats=mortalitySummary(rows),latest=stats.latestQuarter;
 const ordered=[...rows].sort((a,b)=>a.year-b.year||a.quarter-b.quarter),first=ordered[0];
 const period=latest?`${latest.year} Q${latest.quarter}`:'Period unavailable';
 return[
  {title:'Latest quarterly suspected deaths',value:number(latest?.suspected_deaths),context:period,source:mortalitySource},
  {title:'Latest complete annual total',value:number(stats.annual?.total),context:stats.annual?`${stats.annual.year} · ${stats.change===null?'Previous-year comparison unavailable':`${stats.change>0?'+':''}${stats.change.toFixed(2)}% from preceding complete year`}`:'Four observed quarters required',source:mortalitySource},
  {title:'Mortality reporting coverage',value:rows.length?`${rows.length} quarters`:'Unavailable',context:first?`${first.year} Q${first.quarter} – ${period}; ${rows.filter(r=>r.suspected_deaths==null).length} unavailable values`:'No verified accessible coverage',source:mortalitySource},
  {title:'Analytical source series',value:sources.length?String(sources.length):'Unavailable',context:'Frozen resource families · individual cutoffs below',source:'Research API · artifact coverage; not independent sources'},
 ];
}
export function latestForensic(result){
 if(result?.state!=='ready'||!result.data?.length)return{state:result?.state??'unavailable',rows:[],message:result?.message||'Forensic observations unavailable.'};
 if(result.total!==result.data.length)return{state:'unavailable',rows:[],message:'Incomplete forensic response; a latest-period preview cannot be established.'};
 const rows=result.data;
 if(rows.some(r=>!/^\d{4} Q[1-4]$/.test(r.period)||r.unit!=='detection_count'))return{state:'unavailable',rows:[],message:'Compatible quarterly forensic detection definitions could not be verified.'};
 const definitions=new Set(rows.map(r=>JSON.stringify([r.source_id,r.geography,r.unit,r.period_basis,r.reporting_definition??null])));
 if(definitions.size!==1)return{state:'unavailable',rows:[],message:'Multiple forensic source definitions require separate exploration.'};
 const period=rows.map(r=>r.period).sort().at(-1),latest=rows.filter(r=>r.period===period);
 if(new Set(latest.map(r=>r.indicator_id)).size!==latest.length)return{state:'unavailable',rows:[],message:'Duplicate forensic categories prevent a verified preview.'};
 return{state:'ready',period,rows:latest.sort((a,b)=>a.indicator_id.localeCompare(b.indicator_id))};
}
export function forecastPreview(result){
 const row=result?.state==='ready'?result.data?.[0]:null;
 if(!row||result.data.length!==1||row.model!=='naive'||row.horizon_quarters!==1||!row.forecast_origin||!row.target_period||!row.interval_method||!Number.isFinite(row.predicted))return{state:'unavailable',message:result?.message||'A verified saved one-quarter naïve forecast is unavailable.'};
 return{state:'ready',row,title:'Saved historical-origin projection',context:`Origin ${row.forecast_origin} → target ${row.target_period}. Not a current future forecast.`,interval:row.interval_method};
}
export async function loadOverview(api){
 const definitions={overview:['/overview',{}],geography:['/geography/inverclyde',{}],forensic:['/toxicology/forensic',{limit:1000}],monitoring:['/anomalies',{limit:1,signals_only:true}],forecast:['/forecasting/results',{}],validation:['/validation/status',{}]};
 const entries=Object.entries(definitions),results=await Promise.allSettled(entries.map(([, [path,params]])=>api(path,params)));
 return Object.fromEntries(entries.map(([key],i)=>[key,results[i].status==='fulfilled'?results[i].value:{state:'error',data:[],total:0,metadata:{},message:results[i].reason?.message||'Research API resource unavailable.'}]));
}
