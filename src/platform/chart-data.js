// Presentation only: original records remain attached; absent slots are never observations.
export const definitionFields=['source_id','source_path','source_sha256','indicator_id','substance_category','unit','period_basis','reporting_definition','endpoint','outcome','boundary_type'];
export const modelFields=['method','model','configuration_id','window','rolling_window_quarters','forecast_origin','horizon_quarters'];
const signature=(row,fields)=>JSON.stringify(fields.map(key=>row[key]??null));
export const definitionKey=row=>signature(row,definitionFields);
export const modelKey=row=>signature(row,modelFields);
export const seriesKey=row=>signature(row,['geography_id','geography','comparison_role',...definitionFields,...modelFields]);
export const periodLabel=row=>String(row.period??row.period_label??(row.year&&row.quarter?`${row.year} Q${String(row.quarter).replace(/^Q/,'')}`:row.year)??row.target_period??row.start??'');
export function valueOf(row){
 if(!row)return null;
 for(const key of ['observed_value','suspected_deaths','statistic_value','predicted','rate']){
  if(Object.hasOwn(row,key)){
   const value=row[key];
   return value===null||value===undefined||value===''||!Number.isFinite(Number(value))?null:Number(value);
  }
 }
 return null;
}
export function periodInfo(row){
 const label=periodLabel(row),basis=String(row.period_basis??'');
 if(/not_calendar|study|irregular/i.test(basis))return{key:label,label,kind:'irregular',order:row.ordinal??row.study_period??label};
 if(basis==='week_beginning_monday'&&/^\d{4}-\d{2}-\d{2}$/.test(label)){
  const date=new Date(label+'T00:00:00Z');
  if(!Number.isFinite(date.getTime())||date.toISOString().slice(0,10)!==label||date.getUTCDay()!==1)throw new Error('Chart unavailable: weekly period must begin on a verified Monday.');
  return{key:label,label,kind:'week',order:(date.getTime()-Date.UTC(1970,0,5))/604800000};
 }
 const month=label.match(/^(\d{4})-(0[1-9]|1[0-2])$/);
 if(month&&basis==='calendar_month')return{key:label,label,kind:'month',order:Number(month[1])*12+Number(month[2])-1};
 const quarter=label.match(/^(\d{4})\s*Q([1-4])$/i);
 if(quarter)return{key:`${quarter[1]} Q${quarter[2]}`,label:`${quarter[1]} Q${quarter[2]}`,kind:'quarter',order:Number(quarter[1])*4+Number(quarter[2])-1};
 if(/^\d{4}$/.test(label))return{key:label,label,kind:'year',order:Number(label)};
 return{key:label,label,kind:'other',order:row.ordinal??row.period_start??label};
}
export function periodSlots(rows){
 const periods=rows.map(periodInfo);
 if(periods.some(p=>!p.key))throw new Error('Chart unavailable: reporting period is missing.');
 const kinds=new Set(periods.map(p=>p.kind));
 if(kinds.size===1&&['quarter','year','month','week'].includes(periods[0]?.kind)){
  const kind=periods[0].kind,orders=periods.map(p=>p.order),first=Math.min(...orders),last=Math.max(...orders);
  if(last-first>10000)throw new Error('Chart period range exceeds the display limit.');
  return Array.from({length:last-first+1},(_,i)=>{const order=first+i,label=kind==='week'?new Date(Date.UTC(1970,0,5)+order*604800000).toISOString().slice(0,10):kind==='year'?String(order):kind==='month'?`${Math.floor(order/12)}-${String(order%12+1).padStart(2,'0')}`:`${Math.floor(order/4)} Q${order%4+1}`;return{key:label,label,kind,order};});
 }
 return [...new Map(periods.map(p=>[p.key,p])).values()].sort((a,b)=>typeof a.order==='number'&&typeof b.order==='number'?a.order-b.order:String(a.order).localeCompare(String(b.order)));
}
export function prepareChart(rows,{total=rows.length,offset=0}={}){
 const slots=periodSlots(rows),groups=new Map(),warnings=[];
 if(offset>0||total>rows.length)warnings.push('Bounded page only; not complete historical coverage.');
 const regular=slots.length>0&&slots.every(p=>p.kind===slots[0].kind)&&['quarter','year','month','week'].includes(slots[0].kind);
 if(!regular&&rows.length)warnings.push('Points only: source periods are irregular or have no verified regular calendar spacing; horizontal positions do not represent elapsed time.');
 for(const row of rows){
  const key=seriesKey(row),period=periodInfo(row).key;
  if(!groups.has(key))groups.set(key,{key,records:new Map(),metadata:Object.fromEntries([...definitionFields,...modelFields].filter(k=>Object.hasOwn(row,k)).map(k=>[k,row[k]])),label:[row.geography??row.geography_id??row.comparison_role??'Recorded series',...modelFields.map(k=>row[k]===undefined?null:`${k}: ${row[k]}`)].filter(Boolean).join(' · ')});
  const group=groups.get(key);
  if(group.records.has(period))throw new Error('Chart unavailable: multiple observations share a series and period. Select a more specific measure; records remain available in the table.');
  group.records.set(period,row);
 }
 if(new Set(rows.map(definitionKey)).size>1)warnings.push('Separate source or reporting definitions are present; lines are not combined.');
 if(new Set(rows.map(r=>r.unit??null)).size>1)throw new Error('Chart unavailable: incompatible units; inspect the separate records in the table.');
 const differentDefinitions=new Set(rows.map(definitionKey)).size>1;
 const datasets=[...groups.values()].map(group=>({...group,label:group.label+(differentDefinitions?' · '+Object.entries(group.metadata).filter(([key])=>definitionFields.includes(key)).map(([key,value])=>`${key}: ${value}`).join(' · '):''),records:undefined,showLine:regular,points:slots.map(p=>{const record=group.records.get(p.key);return{period:p.label,value:valueOf(record),record:record??null,missingPeriod:!record};})}));
 return{labels:slots.map(p=>p.label),datasets,warnings,regular};
}
