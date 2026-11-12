import {compatibleAreas,comparisonTable,comparisonCsv,verifyDefinitions,completeComparison,verifyAreaSubjects} from './comparison-data.js';
import {label} from './presentation.js';
import {renderChart,clearChart} from './charts.js';

export function createComparison(root,api,getAreas,getDefaults){
 const dialog=document.createElement('dialog');dialog.className='comparison-modal';
 dialog.setAttribute('aria-labelledby','comparison-title');dialog.setAttribute('aria-describedby','comparison-description');
 dialog.innerHTML=`<div class="modal-heading"><div><p class="eyebrow">GEOGRAPHIC RESEARCH</p><h2 id="comparison-title">Compare Data</h2></div><button type="button" id="comparison-close" aria-label="Close comparison">Close ×</button></div><p id="comparison-description">Compare the same measure within one geographic boundary. Counts are not population rates. Retrospective signals are not confirmed public-health incidents.</p><form class="comparison-form"><label>First reporting area<select id="comparison-area"></select></label><label>Measure<select id="comparison-indicator"></select></label><label>Compatible comparison area<select id="comparison-other"></select></label><label>From year<input id="comparison-start" type="number" min="1900" max="2100" placeholder="All available years"></label><label>To year<input id="comparison-end" type="number" min="1900" max="2100" placeholder="All available years"></label><div class="comparison-actions"><button type="submit" id="comparison-apply">Compare selected data</button><button type="button" id="comparison-reset">Reset</button></div></form><p id="comparison-status" role="status" aria-live="polite"></p><button id="comparison-retry" hidden>Retry comparison</button><div id="comparison-results" hidden><div class="comparison-cards"></div><p id="comparison-context"></p><div class="plot-wrap"><canvas id="comparison-chart" role="img" aria-label="Geographic comparison; equivalent observations in the following table"></canvas></div><div class="table-scroll"><table><caption>Observed values by reporting period. Missing is not zero.</caption><thead></thead><tbody></tbody></table></div><button id="comparison-export">Export displayed comparison CSV</button><details><summary>Sources and reporting definitions</summary><pre id="comparison-provenance"></pre></details></div>`;
 document.body.append(dialog);
 const q=id=>dialog.querySelector('#comparison-'+id);let version=0,opener,scroll='',metadata=[],table=[],responseMeta={},names=[];
 function status(text,state='loading'){q('status').textContent=text;q('status').dataset.state=state;}
 function invalidate(){version++;q('status').setAttribute('aria-busy','false');q('results').hidden=true;q('retry').hidden=true;clearChart(q('chart'));table=[];}
 function options(node,items,preferred){node.replaceChildren();for(const[value,text]of items)node.add(new Option(text,value));if([...node.options].some(o=>o.value===preferred))node.value=preferred;}
 function dependents(invalidateResults=true){
  if(invalidateResults)invalidate();const area=getAreas().find(a=>a.geography_id===q('area').value),indicator=q('indicator').value;
  options(q('other'),compatibleAreas(getAreas(),area,indicator).map(a=>[a.geography_id,a.name]),q('other').value);
  const study=metadata.find(r=>r.indicator_id===indicator)?.period_basis?.includes('not_calendar');
  for(const key of ['start','end']){q(key).disabled=Boolean(study);q(key).closest('label').hidden=Boolean(study);}
  q('apply').disabled=!q('other').value;
  status(!q('other').value?'No compatible second area exists for this measure and boundary. Council, police-division and health-board observations cannot be substituted.':study?'This source uses unequal study periods; calendar-year filtering is unavailable.':'Choose a reporting period, then compare. Changing selections clears previous results.','unavailable');
 }
 async function areaChanged(preferred=''){
  invalidate();metadata=[];q('indicator').replaceChildren();q('other').replaceChildren();const current=version;status('Loading verified measures…');q('indicator').disabled=true;q('other').disabled=true;q('apply').disabled=true;
  try{const result=await api(`/geographies/${q('area').value}/indicators`,{limit:1000});if(current!==version)return;if(result.state==='error')throw new Error(result.message||'Measure metadata unavailable.');metadata=result.data;options(q('indicator'),metadata.map(r=>[r.indicator_id,label(r.indicator_id)]),preferred);dependents(false);}
  catch(error){if(current===version){status(error.message,'error');q('retry').hidden=false;}}
  finally{if(current===version){q('indicator').disabled=false;q('other').disabled=false;}}
 }
 async function compare(){
  if(!q('other').value)return;
  if(!dialog.querySelector('form').reportValidity())return;
  invalidate();const current=version;status('Loading comparison observations…');q('status').setAttribute('aria-busy','true');q('apply').disabled=true;
  const start=q('start').disabled?'':q('start').value,end=q('end').disabled?'':q('end').value;
  try{
   if(start&&end&&Number(start)>Number(end))throw new Error('From year must be no later than To year.');
   const result=await completeComparison(api,`/geographies/${q('area').value}/comparisons`,{indicator:q('indicator').value,compare_to:q('other').value,start_year:start,end_year:end},()=>current===version&&dialog.open);
   if(!result)return;
   if(result.state!=='ready'){status(result.message||'No accessible observations for this comparison.',result.state);if(result.state==='error')q('retry').hidden=false;return;}
   const rows=result.data;
   if(!rows.length){status('No observations for the selected reporting period.','empty');return;}
   verifyAreaSubjects(rows,{first:q('area').value,second:q('other').value,indicator:q('indicator').value});verifyDefinitions(rows);table=comparisonTable(rows);responseMeta={...result.metadata,coverage:{returned:rows.length,total:result.total,scope:'Complete API result for selected filters; not necessarily complete source history',unpairedPeriods:table.filter(r=>r.coverage!=='paired').length}};
   names=[q('area').selectedOptions[0].textContent,q('other').selectedOptions[0].textContent];
   const cards=dialog.querySelector('.comparison-cards');cards.replaceChildren();
   for(const[role,name]of [['first_area',names[0]],['second_area',names[1]]]){const card=document.createElement('article');card.className='summary-card';const title=document.createElement('h3');title.textContent=name;const detail=document.createElement('p');const selected=rows.filter(r=>r.comparison_role===role);detail.textContent=`${selected.length} observations returned · ${selected.filter(r=>r.observed_value===null).length} explicitly unavailable values`;card.append(title,detail);cards.append(card);}
   q('context').textContent=`${label(q('indicator').value)} · ${rows[0].unit??'source units'} · ${rows[0].period_basis??'source reporting periods'}. ${result.metadata?.comparison??'Same dataset and boundary.'} Missing periods and suppressed values are not replaced.`;
   const head=dialog.querySelector('thead'),body=dialog.querySelector('tbody');head.replaceChildren();body.replaceChildren();const tr=document.createElement('tr');for(const text of ['Period',...names]){const th=document.createElement('th');th.scope='col';th.textContent=text;tr.append(th);}head.append(tr);
   for(const row of table){const tr=document.createElement('tr');for(const value of [row.period,row.left??'Missing / unavailable',row.right??'Missing / unavailable']){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}body.append(tr);}
   q('provenance').textContent=JSON.stringify({metadata:responseMeta,definition:{indicator:rows[0].indicator_id,unit:rows[0].unit,period_basis:rows[0].period_basis,reporting_definition:rows[0].reporting_definition},note:'Full original row provenance is retained in CSV export.'},null,2);
   q('results').hidden=false;renderChart(q('chart'),rows,rows[0].unit??'Recorded value',{total:result.total});status(`${rows.length} observations across ${table.length} reporting periods. ${table.filter(r=>r.coverage!=='paired').length} periods have missing or unavailable paired values. Complete API result for selected filters; source history may be incomplete. No statistical significance or population-rate comparison is inferred.`,'ready');
  }catch(error){if(current===version){status(error.message,'error');q('retry').hidden=false;}}
  finally{if(current===version){q('apply').disabled=!q('other').value;q('status').setAttribute('aria-busy','false');}}
 }
 function reset(){const areas=getAreas().filter(a=>a.available).sort((a,b)=>a.name.localeCompare(b.name)),defaults=getDefaults();options(q('area'),areas.map(a=>[a.geography_id,`${a.name} — ${label(a.boundary_type)}`]),defaults.area);q('start').value=defaults['start-year']??'';q('end').value=defaults['end-year']??'';return areaChanged(defaults.indicator);}
 q('area').onchange=()=>areaChanged(q('indicator').value);q('indicator').onchange=dependents;
 for(const key of ['other','start','end'])q(key).onchange=()=>{invalidate();status('Selections changed. Compare to load the selected data.','unavailable');q('apply').disabled=!q('other').value;};
 dialog.querySelector('form').onsubmit=e=>{e.preventDefault();compare();};q('reset').onclick=reset;q('retry').onclick=()=>metadata.length&&q('other').value?compare():areaChanged();q('close').onclick=()=>dialog.close();
 dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
 dialog.addEventListener('close',()=>{invalidate();document.body.style.overflow=scroll;opener?.focus();});
 dialog.addEventListener('keydown',event=>{
  if(event.key!=='Tab')return;
  const stops=[...dialog.querySelectorAll('button:not([disabled]),input:not([disabled]),select:not([disabled]),a[href],summary,[tabindex="0"]')].filter(node=>node.getClientRects().length&&!node.closest('[hidden]'));
  const first=stops[0],last=stops.at(-1);
  if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}
  else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
 });
 q('export').onclick=()=>{const blob=new Blob([comparisonCsv(table,...names,responseMeta)],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='geographic-comparison.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 return{open(){opener=document.activeElement;scroll=document.body.style.overflow;dialog.showModal();document.body.style.overflow='hidden';q('close').focus();reset();}};
}
