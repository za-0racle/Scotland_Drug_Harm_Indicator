import {completeMortality,mortalitySources,validateMortality} from './mortality-data.js';
import {completeSubstances,substanceSources,substanceOptions,categoryOf} from './substance-data.js';
import {completeComparison,comparisonTable,comparisonCsv,comparisonSummary,comparisonRange,categoryComparison,verifyDefinitions,verifyAreaSubjects} from './comparison-data.js';
import {periodSlots,periodInfo} from './chart-data.js';
import {renderChart,clearChart} from './charts.js';
import {label} from './presentation.js';

const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!=null)node.textContent=String(text);if(cls)node.className=cls;return node;};
const roles=['first_area','second_area'];
const number=value=>value==null?'Missing / unavailable':new Intl.NumberFormat('en-GB',{maximumFractionDigits:2}).format(value);
export async function mountComparisonStudio({root,api,isCurrent,onStatus,saved={}}){
 let rows=[],sourceResult=null,version=0,disposed=false,last=null,tablePage=0;
 const live=()=>!disposed&&isCurrent();
 root.replaceChildren();root.setAttribute('aria-label','Comparison Studio');
 const introduction=el('article',null,'case-feature');introduction.append(el('p','DESCRIPTIVE RESEARCH · TWO SUBJECTS','eyebrow'),el('h3','Compare compatible historical evidence'),el('p','Align two reporting areas or two substance categories within a verified source. Compare observations in their original units, with gaps visible and original records retained. Descriptive differences do not establish statistical significance, causation or operational alerts.'));root.append(introduction);
 const form=el('form',null,'filter-panel studio-form'),fields={};
 const titles={kind:'Comparison type',source:'Evidence source',indicator:'Indicator',boundary:'Geographic boundary',geography:'Reporting geography',first:'First comparison subject',second:'Second comparison subject',from:'From reporting period',to:'To reporting period'};
 for(const[id,title]of Object.entries(titles)){const field=el('label',title),select=el('select');select.id='studio-'+id;field.htmlFor=select.id;field.append(select);fields[id]=select;form.append(field);}
 const actions=el('div',null,'comparison-actions'),apply=el('button','Compare selected subjects'),reset=el('button','Reset comparison'),retry=el('button','Retry comparison');apply.type='submit';apply.id='studio-apply';reset.type=retry.type='button';retry.hidden=true;retry.id='studio-retry';actions.append(apply,reset,retry);form.append(actions);root.append(form);
 const support=el('p','Available types: two compatible areas and two same-source substance categories. Separate-period contrasts and different-indicator comparisons are not enabled: equivalent windows and interchangeable definitions are not established. Population-rate comparisons, model-output comparisons, raw RADAR intelligence and Phase 9 individual substances are outside this verified comparison contract.','studio-support');root.append(support);
 const definition=el('p',null,'overview-source-line'),status=el('p');status.id='studio-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');root.append(definition,status);
 const results=el('div');results.id='studio-results';results.hidden=true;root.append(results);
 const summaries=el('div',null,'summary-grid');summaries.id='studio-summary';results.append(summaries);
 const plot=el('section',null,'chart-panel');plot.append(el('h3','Aligned historical observations'));const context=el('p');context.id='studio-context';plot.append(context);const wrap=el('div',null,'plot-wrap'),canvas=el('canvas');canvas.id='studio-chart';canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Aligned comparison observations; exact values and missing states in the following table');wrap.append(canvas);plot.append(wrap);results.append(plot);
 const observations=el('section',null,'chart-panel');observations.append(el('h3','Aligned observations'));const exportButton=el('button','Export complete aligned comparison CSV');exportButton.type='button';exportButton.id='studio-export';const exportLabel=el('p');exportLabel.id='studio-export-scope';observations.append(exportLabel,exportButton);const tableRoot=el('div');tableRoot.id='studio-table';observations.append(tableRoot);results.append(observations);
 const methods=el('section',null,'chart-panel');methods.id='studio-methodology';methods.append(el('h3','Source definitions and methodology'));const methodBody=el('div');methods.append(methodBody);results.append(methods);
 const options=(select,items,preferred)=>{select.replaceChildren();for(const[value,text]of items)select.add(new Option(String(text),String(value)));if([...select.options].some(o=>o.value===preferred))select.value=preferred;};
 options(fields.kind,[['areas','Two compatible geographic areas'],['substances','Two same-source substance categories'],['periods','Two reporting periods — unavailable'],['indicators','Different indicators — unavailable']],saved.kind??'areas');for(const option of fields.kind.options)if(['periods','indicators'].includes(option.value))option.disabled=true;
 const read=()=>Object.fromEntries(Object.entries(fields).map(([id,field])=>[id,field.value]));
 const save=()=>Object.assign(saved,read());
 const spec=()=>fields.kind.value==='areas'?mortalitySources[fields.source.value]:substanceSources[fields.source.value];
 function setStatus(state,message){if(!live())return;status.dataset.state=state;status.textContent=message;onStatus(state,message);}
 function invalidate(){version++;last=null;results.hidden=true;exportButton.disabled=true;clearChart(canvas);summaries.replaceChildren();tableRoot.replaceChildren();methodBody.replaceChildren();plot.querySelector('[data-chart-note]')?.replaceChildren();retry.hidden=true;}
 function changed(){invalidate();save();apply.disabled=!fields.first.value||!fields.second.value;setStatus('unavailable',apply.disabled?'No compatible second subject is available for this source and boundary.':'Selections changed. Compare to load the selected evidence.');}
 function chosenRows(){return fields.kind.value==='areas'?rows.filter(r=>[fields.first.value,fields.second.value].includes(r.geography_id)):rows.filter(r=>r.geography_id===fields.geography.value&&[fields.first.value,fields.second.value].includes(categoryOf(r)));}
 function periods(preferred={}){const slots=periodSlots(chosenRows());options(fields.from,slots.map(p=>[p.key,p.label]),slots.some(p=>p.key===preferred.from)?preferred.from:slots[0]?.key);options(fields.to,slots.map(p=>[p.key,p.label]),slots.some(p=>p.key===preferred.to)?preferred.to:slots.at(-1)?.key);fields.from.disabled=fields.to.disabled=!slots.length;}
 function subjects(preferred={}){
  const areas=fields.kind.value==='areas';const available=rows.filter(r=>r.boundary_type===fields.boundary.value);fields.geography.disabled=areas||!available.length;
  if(areas){const choices=[...new Map(available.map(r=>[r.geography_id,r.geography])).entries()].sort((a,b)=>a[1].localeCompare(b[1]));options(fields.first,choices,preferred.first);options(fields.second,choices.filter(([id])=>id!==fields.first.value),preferred.second);}
  else{options(fields.geography,[...new Map(available.map(r=>[r.geography_id,r.geography])).entries()],preferred.geography);const categories=substanceOptions(available.filter(r=>r.geography_id===fields.geography.value)).categories;options(fields.first,categories.map(c=>[c,c]),preferred.first);options(fields.second,categories.filter(c=>c!==fields.first.value).map(c=>[c,c]),preferred.second);}
  for(const id of ['first','second'])fields[id].disabled=!fields[id].options.length;periods(preferred);changed();
 }
 function configure(preferred={}){
  const areas=fields.kind.value==='areas',boundaries=[...new Set(rows.map(r=>r.boundary_type))].sort();
  const defaultBoundary=areas?boundaries.find(boundary=>new Set(rows.filter(r=>r.boundary_type===boundary).map(r=>r.geography_id)).size>=2):boundaries[0];
  options(fields.boundary,boundaries.map(b=>[b,label(b)]),preferred.boundary??defaultBoundary);fields.boundary.disabled=!boundaries.length;
  fields.geography.closest('label').hidden=areas;fields.indicator.closest('label').hidden=!areas;
  const s=spec();options(fields.indicator,areas?[[s.indicator,label(s.indicator)]]:[]);fields.indicator.disabled=!rows.length;
  definition.textContent=s.label+' · '+s.definition;
  subjects(preferred);
 }
 function sources(preferred){const list=fields.kind.value==='areas'?Object.entries(mortalitySources):Object.entries(substanceSources).filter(([,s])=>!s.pending);options(fields.source,list.map(([id,s])=>[id,s.label]),preferred);}
 async function loadSource(preferred={}){
  invalidate();const current=version,kind=fields.kind.value,source=fields.source.value;rows=[];sourceResult=null;apply.disabled=true;definition.textContent=spec().label+' · '+spec().definition;
  for(const id of ['indicator','boundary','geography','first','second','from','to']){fields[id].disabled=true;fields[id].replaceChildren();}
  setStatus('loading','Loading complete verified source history and compatible subjects…');
  try{
   const response=kind==='areas'?await completeMortality(api,source):await completeSubstances(api,source);
   if(!live()||current!==version)return;sourceResult=response;rows=response.data;configure(preferred);
   if(!rows.length)setStatus('empty',response.message||'No accessible observations; empty access does not establish zero harm.');
  }catch(error){if(live()&&current===version){setStatus('error',error.message);retry.hidden=false;}}
 }
 function renderTable(){
  tableRoot.replaceChildren();if(!last)return;const {table,names}=last,pages=Math.ceil(table.length/12);tablePage=Math.max(0,Math.min(tablePage,pages-1));
  const scroll=el('div',null,'table-scroll');scroll.tabIndex=0;const t=el('table');t.append(el('caption',`${last.source} · ${last.unit}. Missing periods and unavailable values are shown separately. Pagination does not change the comparison or export.`));
  const head=el('thead'),header=el('tr');for(const title of ['Reporting period',names[0],names[1],'Pair coverage','Original records']){const th=el('th',title);th.scope='col';header.append(th);}head.append(header);t.append(head);const body=el('tbody');
  for(const row of table.slice(tablePage*12,tablePage*12+12)){const tr=el('tr');for(const v of [row.period,number(row.left),number(row.right),row.coverage==='paired'?'Paired observations':row.coverage==='missing_period'?'Missing reporting period':'Unavailable observation value'])tr.append(el('td',v));const cell=el('td'),detail=el('details');detail.append(el('summary','View source records'),el('pre',JSON.stringify({first:row.first_area??null,second:row.second_area??null},null,2)));cell.append(detail);tr.append(cell);body.append(tr);}t.append(body);scroll.append(t);tableRoot.append(scroll);
  const controls=el('div',null,'page-controls'),prev=el('button','Previous aligned periods'),next=el('button','Next aligned periods');prev.type=next.type='button';prev.disabled=tablePage===0;next.disabled=tablePage+1>=pages;prev.onclick=()=>{tablePage--;renderTable();};next.onclick=()=>{tablePage++;renderTable();};controls.append(prev,el('span',`Page ${pages?tablePage+1:0} of ${pages} · ${table.length} aligned periods`),next);tableRoot.append(controls);
 }
 async function compare(){
  if(!form.reportValidity())return;invalidate();const current=version,selection=read(),s=spec();apply.disabled=true;setStatus('loading','Validating compatibility and aligning complete eligible observations…');
  try{
   if(!selection.first||!selection.second||selection.first===selection.second)throw new Error('Choose two distinct compatible subjects.');
   const range=comparisonRange(chosenRows(),selection.from,selection.to);let compared,metadata;
   if(selection.kind==='areas'){
    const first=rows.find(r=>r.geography_id===selection.first),second=rows.find(r=>r.geography_id===selection.second);
    if(!first||!second||first.boundary_type!==selection.boundary||second.boundary_type!==selection.boundary)throw new Error('Incompatible geographic boundaries.');
    const params={indicator:s.indicator,compare_to:selection.second,start_year:Number(selection.from.slice(0,4)),end_year:Number(selection.to.slice(0,4))};
    const response=await completeComparison(api,`/geographies/${selection.first}/comparisons`,params,()=>live()&&current===version);
    if(!response)return;if(response.state!=='ready'){setStatus(response.state,response.message||'Comparison evidence unavailable.');retry.hidden=response.state!=='error';return;}
    if(response.metadata?.artifact_sha256!==sourceResult.metadata?.artifact_sha256)throw new Error('Source artifact changed since selection. Refresh the source before comparing.');
    validateMortality(response.data,selection.source);
    verifyAreaSubjects(response.data,{first:selection.first,second:selection.second,indicator:s.indicator});
    compared=response.data.filter(r=>range.slots.some(p=>p.key===periodInfo(r).key));metadata=response.metadata;
   }else{compared=categoryComparison(range.rows,selection.first,selection.second);metadata=sourceResult.metadata;}
   if(!live()||current!==version)return;
   verifyDefinitions(compared,{kind:selection.kind});const table=comparisonTable(compared,{kind:selection.kind,slots:range.slots});
   if(!compared.length){setStatus('empty','No accessible observations for the selected subjects and reporting window.');return;}
   const names=[fields.first.selectedOptions[0].textContent,fields.second.selectedOptions[0].textContent],summary=comparisonSummary(table),unit=compared[0].unit;
   const exportMetadata={...metadata,comparison_type:selection.kind,subjects:names,filters:selection,definition:s.definition,coverage:{returned:compared.length,alignedPeriods:table.length,...summary,scope:'Complete eligible comparison for selected filters, across all API and table pages; not necessarily complete source history.'},limitations:[...new Set(compared.map(r=>r.limitations).filter(Boolean))]};
   last={table,names,source:s.label,unit,metadata:exportMetadata};results.hidden=false;
   for(const[title,v,note]of [['First subject',names[0],`${compared.filter(r=>r.comparison_role===roles[0]).length} returned records`],['Second subject',names[1],`${compared.filter(r=>r.comparison_role===roles[1]).length} returned records`],['Shared reporting periods',summary.shared,'Both source records exist; values may be unavailable'],['Paired observed values',summary.paired,`${summary.missingPeriods} missing periods · ${summary.unavailableValues} periods with unavailable values`]]){const c=el('article',null,'summary-card');c.append(el('span',title),el('strong',v),el('p',note),el('small',s.label));summaries.append(c);}
   context.textContent=`${s.label} · ${selection.from} to ${selection.to} · ${unit} · ${compared[0].period_basis}. ${selection.kind==='areas'?'Same indicator and geographic boundary. Counts are not population-adjusted risk.':'Same source and geography. Categories overlap; no pooled percentages or additive composition.'} No percentage changes or statistical significance are calculated.`;
   renderChart(canvas,compared,unit,{total:compared.length,comparisonKind:selection.kind,seriesLabel:series=>{const row=series.points.find(p=>p.record)?.record;return row?names[roles.indexOf(row.comparison_role)]:series.label;}});
   exportLabel.textContent=`${exportMetadata.coverage.scope} ${table.length} aligned periods; ${compared.length} original records. Gaps remain missing; no bounded page is presented as full history.`;exportButton.disabled=false;tablePage=0;renderTable();
   methodBody.append(el('p',s.definition),el('p',`Measurement unit: ${unit}. Reporting basis: ${compared[0].period_basis}. Geographic boundary: ${label(compared[0].boundary_type)}. Source identifiers: ${[...new Set(compared.map(r=>r.source_id))].join('; ')}.`),el('p','Calendar gaps are alignment slots, not fabricated observations. ASSIST uses unconnected categorical points in original study-period order; unequal periods do not represent equal elapsed time. Missing values never become zero. Substance detection does not establish causation or independent death counts; no population prevalence or operational warning follows from this comparison.'));
   for(const limitation of exportMetadata.limitations)methodBody.append(el('p',limitation));const provenance=el('details');provenance.append(el('summary','Verify original definitions, source hashes and export scope'),el('pre',JSON.stringify({metadata:exportMetadata,original_subject_definitions:names.map((name,i)=>({name,record:compared.find(r=>r.comparison_role===roles[i])??null}))},null,2)));methodBody.append(provenance);
   setStatus('ready',`${summary.paired} paired observed periods; ${summary.missingPeriods} missing reporting periods and ${summary.unavailableValues} periods with unavailable values. ${unit}. Complete eligible API result; source history may be incomplete.`);save();
  }catch(error){if(live()&&current===version){invalidate();setStatus('error',error.message);retry.hidden=false;}}
  finally{if(live()&&status.dataset.state!=='loading'){apply.disabled=!fields.first.value||!fields.second.value;}}
 }
 exportButton.onclick=()=>{if(!last)return;const url=URL.createObjectURL(new Blob([comparisonCsv(last.table,...last.names,last.metadata)],{type:'text/csv;charset=utf-8'})),a=el('a');a.href=url;a.download=`comparison-${fields.kind.value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 form.onsubmit=event=>{event.preventDefault();compare();};
 fields.kind.onchange=()=>{sources();loadSource();};fields.source.onchange=()=>loadSource();fields.boundary.onchange=()=>subjects();
 fields.geography.onchange=()=>subjects({geography:fields.geography.value});
 fields.first.onchange=()=>{const previous=read();subjects(previous);};
 fields.second.onchange=()=>{periods(read());changed();};fields.from.onchange=fields.to.onchange=changed;
 reset.onclick=()=>{fields.kind.value='areas';sources('police');loadSource();};retry.onclick=()=>rows.length?compare():loadSource();
 sources(saved.source);await loadSource({...saved});return()=>{disposed=true;version++;clearChart(canvas);};
}
