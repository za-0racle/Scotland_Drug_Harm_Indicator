import {completeMortality,mortalitySources,mortalityOptions,selectMortality,mortalityDistribution,mortalityRanking,mortalityTablePage,mortalityCsv,period} from './mortality-data.js';
import {renderChart,clearChart} from './charts.js';
import {mortalityGrid,number} from './overview-data.js';
import {renderMortalityHeatmap,provenance} from './overview.js';
import {label} from './presentation.js';
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!=null)node.textContent=String(text);if(cls)node.className=cls;return node;};
const state=(root,text)=>{const p=el('p',text);p.dataset.state='unavailable';root.append(p);};
const card=(root,id,title)=>{const section=el('section',null,'overview-card');section.id=id;const h=el('h3',title);h.id=id+'-title';section.setAttribute('aria-labelledby',h.id);section.append(h);root.append(section);return section;};
function summaryTable(root,headers,rows,caption){const wrap=el('div',null,'table-scroll');wrap.tabIndex=0;const table=el('table');if(caption)table.append(el('caption',caption));const head=el('thead'),tr=el('tr');for(const title of headers){const th=el('th',title);th.scope='col';tr.append(th);}head.append(tr);table.append(head);const body=el('tbody');for(const values of rows){const row=el('tr');for(const value of values)row.append(el('td',value));body.append(row);}table.append(body);wrap.append(table);root.append(wrap);return body;}
function boxPlot(root,distribution){
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 640 180');svg.setAttribute('role','img');svg.setAttribute('aria-label',`Distribution: median ${number(distribution.median)}, lower quartile ${number(distribution.q1)}, upper quartile ${number(distribution.q3)}; exact summary follows.`);svg.classList.add('mortality-box-svg');
 const max=Math.max(1,distribution.max)*1.08,x=value=>40+value/max*550;
 function shape(tag,attrs,title){const node=document.createElementNS(ns,tag);for(const[key,value]of Object.entries(attrs))node.setAttribute(key,String(value));if(title){const t=document.createElementNS(ns,'title');t.textContent=title;node.append(t);}svg.append(node);return node;}
 shape('line',{x1:40,y1:132,x2:590,y2:132,class:'box-axis'});
 for(let i=0;i<=4;i++){const value=max*i/4;shape('line',{x1:x(value),y1:128,x2:x(value),y2:136,class:'box-axis'});const t=shape('text',{x:x(value),y:155,'text-anchor':'middle'});t.textContent=number(value);}
 shape('line',{x1:x(distribution.lower),y1:65,x2:x(distribution.upper),y2:65,class:'box-whisker'});
 for(const value of [distribution.lower,distribution.upper])shape('line',{x1:x(value),y1:45,x2:x(value),y2:85,class:'box-whisker'},`Whisker ${number(value)}`);
 shape('rect',{x:x(distribution.q1),y:35,width:Math.max(1,x(distribution.q3)-x(distribution.q1)),height:60,class:'box-quartiles'},`Q1 ${number(distribution.q1)}; Q3 ${number(distribution.q3)}`);
 shape('line',{x1:x(distribution.median),y1:35,x2:x(distribution.median),y2:95,class:'box-median'},`Median ${number(distribution.median)}`);
 for(const value of distribution.outliers)shape('circle',{cx:x(value),cy:65,r:4,class:'box-outlier'},`Descriptive outlier: ${number(value)} deaths`);
 const axis=shape('text',{x:315,y:178,'text-anchor':'middle'});axis.textContent='Deaths (count); zero-based axis';const wrap=el('div',null,'mortality-box-wrap');wrap.tabIndex=0;wrap.append(svg);root.append(wrap);
}
export async function mountMortality({root,api,isCurrent,onStatus,onInspect,onScopeChange=()=>{},saved={}}){
 root.hidden=false;root.replaceChildren();root.className='mortality-screen';
 const controls=el('section',null,'filter-panel mortality-controls');controls.setAttribute('aria-label','Mortality source and reporting controls');root.append(controls);
 const fields={};for(const[id,title]of [['source','Mortality source'],['boundary','Geographic boundary'],['area','Reporting area'],['from','From year'],['to','To year']]){const field=el('label',title),select=el('select');select.id='mortality-'+id;field.append(select);controls.append(field);fields[id]=select;}
 for(const[key,spec]of Object.entries(mortalitySources))fields.source.add(new Option(spec.label,key));fields.source.value=saved.source??'police';
 const reset=el('button','Reset mortality filters');reset.type='button';controls.append(reset);
 const definition=el('p',null,'mortality-definition');definition.id='mortality-definition';root.append(definition);const scope=el('p',null,'overview-source-line');scope.id='mortality-scope';root.append(scope);
 const kpis=el('div',null,'summary-grid');kpis.id='mortality-summary';root.append(kpis);const grid=el('div',null,'overview-grid mortality-grid');root.append(grid);
 const trend=card(grid,'mortality-trend','Mortality over reporting periods'),chartContext=el('p',null,'overview-source-line'),plot=el('div',null,'plot-wrap'),canvas=el('canvas');canvas.id='mortality-chart';canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Selected mortality series; equivalent exact observations are in the detailed table below.');plot.append(canvas);trend.append(chartContext,plot);
 const heat=card(grid,'mortality-heatmap','Year-by-quarter suspected deaths'),box=card(grid,'mortality-distribution','Distribution across comparable periods'),ranking=card(grid,'mortality-ranking','Geographic mortality ranking'),tableCard=card(grid,'mortality-observations','Detailed mortality observations'),disclosures=card(grid,'mortality-methods','Sources, definitions & methods');
 const bodies=new Map();for(const section of [heat,box,ranking,tableCard,disclosures]){const body=el('div');section.append(body);bodies.set(section,body);}
 let results={},source=fields.source.value,sourceResult=null,rows=[],tableSearch='',tablePage=0,rankingPeriod='';
 const loading=el('p','Loading complete source-specific mortality histories…');loading.dataset.state='loading';root.append(loading);for(const field of Object.values(fields))field.disabled=true;reset.disabled=true;
 const entries=Object.keys(mortalitySources),settled=await Promise.allSettled(entries.map(key=>completeMortality(api,key)));
 if(!isCurrent())return()=>clearChart(canvas);
 results=Object.fromEntries(entries.map((key,i)=>[key,settled[i].status==='fulfilled'?settled[i].value:{state:'error',data:[],total:0,metadata:{},message:settled[i].reason?.message??'Mortality source unavailable.'}]));loading.remove();fields.source.disabled=false;reset.disabled=false;
 const fill=(select,items,preferred)=>{select.replaceChildren();for(const[value,text]of items)select.add(new Option(String(text),String(value)));if([...select.options].some(o=>o.value===String(preferred)))select.value=String(preferred);};
 function configure(resetYears=false,initial=null){
  source=fields.source.value;sourceResult=results[source];rows=sourceResult.data;const opts=mortalityOptions(rows,initial?.boundary??(resetYears?'country':fields.boundary.value));
  fill(fields.boundary,opts.boundaries.map(v=>[v,label(v)]),opts.boundary);fill(fields.area,opts.areas.map(v=>[v.id,v.name]),initial?.area??(resetYears?'':fields.area.value));
  fill(fields.from,opts.years.map(y=>[y,y]),initial?.start??(resetYears?opts.years[0]:fields.from.value));fill(fields.to,opts.years.map(y=>[y,y]),initial?.end??(resetYears?opts.years.at(-1):fields.to.value));
  for(const id of ['boundary','area','from','to'])fields[id].disabled=!rows.length;
  rankingPeriod='';tableSearch='';tablePage=0;render();
 }
 function body(section){const node=bodies.get(section);node.replaceChildren();return node;}
 function inspect(row){onInspect(row,{...sourceResult.metadata,source_definition:mortalitySources[source].definition,filters:read()});}
 function read(){return{source,boundary:fields.boundary.value,area:fields.area.value,start:fields.from.value,end:fields.to.value};}
 function render(){
  if(!isCurrent())return;
  onScopeChange();clearChart(canvas);for(const section of [heat,box,ranking,tableCard,disclosures])body(section);kpis.replaceChildren();const spec=mortalitySources[source];definition.textContent=spec.label+'. '+spec.definition;
  let selected=[];try{selected=selectMortality(rows,read());}catch(error){onStatus('error',error.message);scope.textContent=chartContext.textContent=error.message;for(const section of [heat,box,ranking,tableCard])state(bodies.get(section),error.message);return;}
  Object.assign(saved,read());
  const latest=selected.at(-1),valid=selected.filter(r=>Number.isFinite(r.observed_value));const coverage=selected.length?`${period(selected[0])} – ${period(latest)}`:'Unavailable';
  scope.textContent=`${spec.label} · ${fields.area.selectedOptions[0]?.textContent??'Area unavailable'} · ${coverage}. Charts use the full matching API history; table search and pagination do not change analytical scope.`;
  for(const[title,value,context]of [['Latest observation',number(latest?.observed_value),latest?period(latest):'Reporting period unavailable'],['Historical coverage',selected.length?String(selected.length)+' periods':'Unavailable',coverage],['Valid observed counts',selected.length?String(valid.length):'Unavailable',`${selected.length-valid.length} unavailable values in returned rows`],['Reporting basis',spec.basis==='quarterly'?'Quarterly':'Annual',spec.basis==='quarterly'?'Suspected-death reporting quarters':'NRS registration years']]){const c=el('article',null,'summary-card overview-kpi');c.append(el('span',title),el('strong',value),el('p',context),el('small',spec.label));kpis.append(c);}
  onStatus(sourceResult.state==='error'?'error':selected.length?'ready':'unavailable',sourceResult.state==='error'?sourceResult.message:`${selected.length} comparable mortality records in selected history; ${valid.length} observed counts.`);
  chartContext.textContent=scope.textContent;renderChart(canvas,selected,'Deaths (count)',{total:selected.length});
  trend.querySelector('h3').textContent=spec.basis==='quarterly'?'Quarterly suspected drug deaths':'Annual registered drug misuse deaths';
  if(!selected.length){for(const section of [heat,box,ranking,tableCard])state(bodies.get(section),sourceResult.message||'No compatible observations for this selection. Missing access is not zero mortality.');}
  else{
   if(spec.basis==='quarterly')renderMortalityHeatmap(bodies.get(heat),mortalityGrid(selected.map(r=>({year:r.year,quarter:r.quarter,suspected_deaths:r.observed_value,original_record:r}))),{geography:latest.geography});
   else state(bodies.get(heat),'Quarterly heatmap is not applicable: NRS provides annual registration-year observations. No quarterly values are inferred.');
   const distribution=mortalityDistribution(selected),boxBody=bodies.get(box);boxBody.append(el('p',`${latest.geography} · ${coverage} · ${spec.basis} counts from one source.`, 'overview-source-line'));
   if(distribution.state==='ready'){boxPlot(boxBody,distribution);summaryTable(boxBody,['Observed n','Q1','Median','Q3','Lower whisker','Upper whisker'],[[distribution.n,number(distribution.q1),number(distribution.median),number(distribution.q3),number(distribution.lower),number(distribution.upper)]],'Exact descriptive distribution summary.');boxBody.append(el('p',`Outliers: ${distribution.outliers.length?distribution.outliers.map(number).join(', '):'none under the displayed convention'}. ${distribution.missing} unavailable returned values excluded.`));}else state(boxBody,distribution.message);
   boxBody.append(el('p','Quartiles: Hyndman–Fan type 7, linear interpolation at zero-based index (n−1)p. Whiskers end at observed values within Q1−1.5×IQR and Q3+1.5×IQR. Minimum eight observed periods is a display rule, not a validation threshold. Temporal dependence, missing periods and changing trends limit interpretation. Outliers are descriptive points, not alerts.','mortality-method-note'));
   renderRanking();renderTable(selected);
  }
  const info=bodies.get(disclosures);info.append(el('p',spec.definition),el('p',latest?.limitations??latest?.small_number_qualification??'No causal conclusions or population-rate claims follow from these descriptive counts.'));
  const other=el('a','Open retained multi-source trends workspace');other.href='#exploration';info.append(other);
  const method=el('p');method.append(document.createTextNode('Quartile reference: '));const ref=el('a','R quantile documentation (type 7)');ref.href='https://stat.ethz.ch/R-manual/R-devel/library/stats/html/quantile.html';ref.target='_blank';ref.rel='noopener noreferrer';method.append(ref,document.createTextNode('. Whiskers use the documented 1.5-IQR convention; type-7 quartiles are not R’s distinct boxplot hinges.'));info.append(method);
  provenance(info,'Source artifact, original definition & record example',sourceResult,selected.length?[selected[0]]:[]);
 }
 function renderRanking(){
  const target=bodies.get(ranking);target.replaceChildren();const eligible=rows.filter(r=>r.boundary_type===fields.boundary.value&&r.year>=Number(fields.from.value)&&r.year<=Number(fields.to.value)),periods=[...new Set(eligible.map(period))].sort();
  if(!periods.includes(rankingPeriod))rankingPeriod=periods.at(-1)??'';const field=el('label','Ranking reporting period'),select=el('select');select.id='mortality-ranking-period';fill(select,periods.map(p=>[p,p]),rankingPeriod);select.onchange=()=>{rankingPeriod=select.value;renderRanking();};field.append(select);target.append(field);
  const result=mortalityRanking(rows,read(),rankingPeriod);target.append(el('p',`${mortalitySources[source].label} · ${label(fields.boundary.value)} · ${result.period||'Period unavailable'}. Death counts, not population-adjusted rates. The selected area does not restrict compatible peer areas.`, 'overview-source-line'));
  if(result.state!=='ready')state(target,result.message);
  else{const max=Math.max(1,...result.rows.map(r=>r.observed_value)),list=el('ol',null,'mortality-bars');list.setAttribute('aria-label','Descending mortality counts at one boundary and reporting period');for(const row of result.rows){const item=el('li'),text=el('div',null,'mortality-bar-label');text.append(el('span',row.geography),el('strong',number(row.observed_value)));const track=el('div',null,'mortality-bar-track'),bar=el('span');bar.style.width=(row.observed_value/max*100)+'%';track.setAttribute('aria-hidden','true');track.append(bar);item.append(text,track);list.append(item);}target.append(list);target.append(el('p',`Zero-based linear bar scale: 0 to ${number(max)} deaths. Counts do not establish comparable population risk.`));}
  if(result.missing.length)target.append(el('p',`Unavailable at this period (${result.missing.length}): ${result.missing.map(r=>r.geography).join('; ')}. These are not zero counts.`));
 }
 function renderTable(selected){
  const target=bodies.get(tableCard);target.replaceChildren();const controls=el('div',null,'mortality-table-controls'),field=el('label','Search observations (table only)'),input=el('input');input.type='search';input.id='mortality-search';input.value=tableSearch;field.append(input);controls.append(field);const download=el('button','Export matching observations CSV');download.type='button';controls.append(download);target.append(controls);
  target.append(el('p','Search displayed periods, areas, measures, source names and notes. Artifact filenames remain in provenance and CSV exports.','overview-source-line'));const tableRoot=el('div');target.append(tableRoot);
  function draw(){const result=mortalityTablePage(selected,tableSearch,tablePage);tablePage=result.page;tableRoot.replaceChildren();const body=summaryTable(tableRoot,['Period','Geography','Boundary','Mortality measure','Count','Source / unit','Quality / notes','Provenance'],result.rows.map(row=>[period(row),row.geography,label(row.boundary_type),label(row.indicator_id),number(row.observed_value),`${mortalitySources[source].label} · ${row.unit}`,`${row.quality_status??'Status unavailable'} · ${row.limitations??row.small_number_qualification??''}`,'']),`${result.total} search matches within ${selected.length} source/area/year observations. Search does not filter the charts.`);
   for(const[index,row]of result.rows.entries()){const button=el('button','Source details');button.type='button';button.onclick=()=>inspect(row);body.children[index].lastElementChild.append(button);}
   const pager=el('div',null,'page-controls'),previous=el('button','Previous observations'),next=el('button','Next observations');previous.type=next.type='button';previous.disabled=result.page===0;next.disabled=!result.pages||result.page+1>=result.pages;previous.onclick=()=>{tablePage--;draw();};next.onclick=()=>{tablePage++;draw();};pager.append(previous,el('span',`Page ${result.pages?result.page+1:0} of ${result.pages} · ${result.total} matching observations`),next);tableRoot.append(pager);download.disabled=!result.total;
   download.onclick=()=>{const blob=new Blob([mortalityCsv(result.matched,{...sourceResult.metadata,filters:read(),search:tableSearch,export_scope:'All matching observations across table pages; charts ignore table search'})],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=`mortality-${source}-observations.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  }
  input.oninput=()=>{tableSearch=input.value;tablePage=0;draw();};draw();
 }
 fields.source.onchange=()=>configure(true);fields.boundary.onchange=()=>{const options=mortalityOptions(rows,fields.boundary.value);fill(fields.area,options.areas.map(a=>[a.id,a.name]));rankingPeriod='';tableSearch='';tablePage=0;render();};
 for(const id of ['area','from','to'])fields[id].onchange=()=>{rankingPeriod='';tableSearch='';tablePage=0;render();};reset.onclick=()=>{fields.source.value='police';configure(true);};configure(true,{...saved});
 return()=>clearChart(canvas);
}
