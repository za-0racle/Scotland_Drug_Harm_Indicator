import {definitionKey,periodInfo} from './chart-data.js';
export const mortalitySources={
 police:{label:'Police Scotland — suspected drug deaths',indicator:'suspected_deaths',basis:'quarterly',path:'/exports',params:{resource:'mortality_trends',format:'json'},definition:'Provisional originally suspected deaths, calendar quarters with the source’s legacy ten-day timing adjustment. Police divisions are not councils. These are counts, not population rates or confirmed registered drug misuse deaths.'},
 nrs:{label:'National Records of Scotland — registered drug misuse deaths',indicator:'nrs_registered_drug_misuse_deaths',basis:'annual',path:'/mortality/annual',params:{},definition:'Annual registration-year deaths meeting the NRS drug misuse definition, Persons. Registration year is not necessarily occurrence year. This definition is distinct from Police Scotland suspected deaths and wider drug poisoning. Counts are not population-adjusted rates.'},
};
export const period=row=>periodInfo(row).label;
export async function completeMortality(api,source){
 const spec=mortalitySources[source];if(!spec)throw new Error('Unknown mortality source.');
 let rows=[],offset=0,total=null,metadata=null;
 do{
  const result=await api(spec.path,{...spec.params,offset,limit:1000});
  if(!['ready','empty'].includes(result.state))throw new Error(result.message||'Mortality source unavailable.');
  if(total!==null&&(total!==result.total||metadata?.artifact_sha256!==result.metadata?.artifact_sha256))throw new Error('Mortality source changed during pagination; refresh before interpreting history.');
  total=result.total;metadata=result.metadata;
  if(!Number.isInteger(total)||total<0||total>10000||!Array.isArray(result.data))throw new Error('Mortality result exceeds the verified bounded scope.');
  rows.push(...result.data);offset=rows.length;
  if(offset>total||(!result.data.length&&offset<total))throw new Error('Incomplete mortality response; partial pages are not complete history.');
 }while(offset<total);
 validateMortality(rows,source);
 return{state:rows.length?'ready':'empty',data:rows,total,metadata,message:rows.length?'':'No accessible mortality observations. Empty access does not establish zero deaths.'};
}
export function validateMortality(rows,source){
 const spec=mortalitySources[source];if(!spec)throw new Error('Unknown mortality source.');const keys=new Set();
 for(const row of rows){
  if(row.indicator_id!==spec.indicator||!['count','deaths'].includes(row.unit)||!row.geography_id||!row.geography||!row.boundary_type||!Number.isInteger(row.year))throw new Error('Mortality source, geography or measure could not be verified.');
  if(source==='police'&&(!Number.isInteger(row.quarter)||row.quarter<1||row.quarter>4||periodInfo(row).kind!=='quarter'||period(row)!==`${row.year} Q${row.quarter}`||!String(row.period_basis).includes('calendar_quarter')))throw new Error('Quarterly suspected-death reporting basis is incompatible.');
  if(source==='nrs'&&(row.period_basis!=='calendar_year_of_registration'||row.sex!=='Persons'||row.quarter!=null||periodInfo(row).kind!=='year'))throw new Error('Annual registered-death definition is incompatible.');
  if(row.observed_value!=null&&(!Number.isInteger(row.observed_value)||row.observed_value<0))throw new Error('Invalid mortality observation value.');
  const key=JSON.stringify([row.geography_id,period(row)]);if(keys.has(key))throw new Error('Duplicate mortality observations share an area and period.');keys.add(key);
 }
 for(const boundary of new Set(rows.map(r=>r.boundary_type)))if(new Set(rows.filter(r=>r.boundary_type===boundary).map(definitionKey)).size>1)throw new Error('Multiple source definitions require separate mortality views.');
}
export function mortalityOptions(rows,boundary){
 const boundaries=[...new Set(rows.map(r=>r.boundary_type))].sort();
 const chosen=boundaries.includes(boundary)?boundary:boundaries.includes('country')?'country':boundaries[0]??'';
 const areas=[...new Map(rows.filter(r=>r.boundary_type===chosen).map(r=>[r.geography_id,{id:r.geography_id,name:r.geography}])).values()].sort((a,b)=>a.name.localeCompare(b.name));
 return{boundaries,boundary:chosen,areas,years:[...new Set(rows.map(r=>r.year))].sort((a,b)=>a-b)};
}
export function selectMortality(rows,{boundary,area,start,end}){
 if(Number(start)>Number(end))throw new Error('From year must be no later than To year.');
 return rows.filter(r=>r.boundary_type===boundary&&r.geography_id===area&&r.year>=Number(start)&&r.year<=Number(end)).sort((a,b)=>periodInfo(a).order-periodInfo(b).order);
}
export function mortalityDistribution(rows){
 if(new Set(rows.map(r=>JSON.stringify([definitionKey(r),r.geography_id]))).size>1)throw new Error('A distribution requires one area and one comparable reporting definition.');
 const values=rows.map(r=>r.observed_value).filter(Number.isFinite).sort((a,b)=>a-b),n=values.length;
 if(n<8)return{state:'unavailable',n,message:'At least eight observed, comparable periods are required by this descriptive screen; missing values are excluded and are not zeros.'};
 const quantile=p=>{const h=(n-1)*p,i=Math.floor(h);return values[i]+(h-i)*(values[Math.min(i+1,n-1)]-values[i]);};
 const q1=quantile(.25),median=quantile(.5),q3=quantile(.75),iqr=q3-q1,inside=values.filter(v=>v>=q1-1.5*iqr&&v<=q3+1.5*iqr);
 return{state:'ready',n,q1,median,q3,lower:inside[0],upper:inside.at(-1),min:values[0],max:values.at(-1),outliers:values.filter(v=>v<q1-1.5*iqr||v>q3+1.5*iqr),missing:rows.length-n};
}
export function mortalityRanking(rows,{boundary,start,end},reportingPeriod){
 const eligible=rows.filter(r=>r.boundary_type===boundary&&r.year>=Number(start)&&r.year<=Number(end));
 const latest=reportingPeriod??[...eligible].sort((a,b)=>periodInfo(a).order-periodInfo(b).order).at(-1);
 const target=typeof latest==='string'?latest:latest?period(latest):'';
 const selected=eligible.filter(r=>period(r)===target);
 if(new Set(selected.map(definitionKey)).size>1)throw new Error('Ranking requires the same source, unit and reporting definition.');
 if(new Set(selected.map(r=>JSON.stringify([r.period_start??null,r.period_end??null]))).size>1)throw new Error('Ranking reporting-period boundaries are incompatible.');
 if(new Set(selected.map(r=>r.geography_id)).size!==selected.length)throw new Error('Duplicate geographic observations prevent a ranking.');
 const available=selected.filter(r=>Number.isFinite(r.observed_value)).sort((a,b)=>b.observed_value-a.observed_value||a.geography.localeCompare(b.geography));
 return{state:available.length>=2?'ready':'unavailable',period:target,rows:available,missing:selected.filter(r=>r.observed_value==null),message:'Fewer than two compatible observed areas are available at this boundary and period. National totals, councils and police divisions cannot be substituted for one another.'};
}
export function mortalityTablePage(rows,search='',page=0,size=12){
 const query=search.trim().toLocaleLowerCase(),matched=rows.filter(r=>!query||[period(r),r.geography,r.boundary_type?.replaceAll('_',' '),r.indicator_id?.replaceAll('_',' '),r.observed_value??'Unavailable',r.unit,Object.values(mortalitySources).find(spec=>spec.indicator===r.indicator_id)?.label,r.quality_status,r.limitations,r.small_number_qualification].join(' ').toLocaleLowerCase().includes(query));
 const position=Math.max(0,Math.min(page,Math.max(0,Math.ceil(matched.length/size)-1)));
 return{rows:matched.slice(position*size,(position+1)*size),matched,total:matched.length,page:position,pages:Math.ceil(matched.length/size)};
}
export function mortalityCsv(rows,metadata){
 const quote=value=>{let text=value==null?'':String(value);if(/^\s*[=+@-]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
 const header=['reporting_period','geography','boundary_type','measure','value','unit','source','quality','original_record','provenance_and_filters'];
 return '\uFEFF'+[header,...rows.map(r=>[period(r),r.geography,r.boundary_type,r.indicator_id,r.observed_value,r.unit,r.source_id??r.source_path,r.quality_status,JSON.stringify(r),JSON.stringify(metadata)])].map(row=>row.map(quote).join(',')).join('\r\n');
}
