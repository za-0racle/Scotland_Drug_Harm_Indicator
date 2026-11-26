// Display saved statistics only; no thresholds or flags are calculated here.
export function prepareMonitoring(rows,configuration){
 if(!['EWMA','NB2-EWMA','CUSUM'].includes(configuration?.method?.toUpperCase()))throw new Error('Chart unavailable: unsupported monitoring method.');
 const selected=rows.filter(r=>String(r.configuration_id)===String(configuration.configuration_id));
 const indexed=new Map();
 for(const row of selected){
  if(!Number.isInteger(row.observation_year)||!Number.isInteger(row.observation_quarter)||row.observation_quarter<1||row.observation_quarter>4)throw new Error('Chart unavailable: reporting quarter is missing.');
  const key=row.observation_year*4+row.observation_quarter-1;
  if(indexed.has(key))throw new Error('Chart unavailable: duplicate configuration quarter.');
  indexed.set(key,row);
 }
 const keys=[...indexed.keys()].sort((a,b)=>a-b),slots=keys.length?Array.from({length:keys.at(-1)-keys[0]+1},(_,i)=>keys[0]+i):[];
 const labels=slots.map(k=>`${Math.floor(k/4)} Q${k%4+1}`),cusum=configuration.method.toUpperCase()==='CUSUM';
 const fields=cusum?[['cusum_positive','Positive CUSUM component'],['cusum_negative','Negative CUSUM component'],['upper_limit','Stored upper decision limit']]:[['statistic_value','Stored EWMA statistic'],['lower_limit','Stored lower limit'],['upper_limit','Stored upper limit']];
 const datasets=fields.map(([field,label])=>({key:field,label,limit:field.includes('limit'),metadata:configuration,showLine:true,points:slots.map((key,i)=>{const record=indexed.get(key);return{period:labels[i],value:Number.isFinite(record?.[field])?record[field]:null,record};})}));
 const flagged=slots.filter(key=>indexed.get(key)?.signal_flag===true).map(key=>labels[slots.indexOf(key)]);
 return{labels,datasets,regular:true,warnings:[`Charted quarters from the current API page. Recorded flagged quarters: ${flagged.join(', ')||'none in these returned records'}. Flags are saved classifications under this method and reference period.${cusum?' CUSUM components and decision limits are shown in their original scale. Zero is the reset baseline.':''} Missing quarters and statistics display as gaps; calibration periods remain identified separately.`]};
}
