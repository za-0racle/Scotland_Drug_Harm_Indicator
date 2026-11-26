import {recordView} from './record-inspection.js';
import {disclose} from './analytical-layout.js';
import {loadOverview,mortalityGrid,overviewKpis,latestForensic,forecastPreview,mortalitySource,number} from './overview-data.js';
import {label} from './presentation.js';
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!=null)node.textContent=String(text);if(cls)node.className=cls;return node;};
const link=(text,route)=>{const node=el('a',text,'overview-link');node.href='#'+route;return node;};
function unavailable(container,result,message){const node=el('p',message||result?.message||'Research observations could not be loaded. Refresh data to try again.','overview-state');node.dataset.state=result?.state==='error'?'error':'unavailable';container.append(node);}
export function provenance(container,title,result,records=[]){
 const details=el('details',null,'overview-provenance');details.append(el('summary',title));
 const metadata=result?.metadata??{};
 const overview=container.id.startsWith('overview-')||Boolean(container.closest('#overview-content'));
 for(const record of records){
  const info=[record.publication_date?`Published ${record.publication_date}`:null,record.source_data_cutoff?`Observation cutoff ${record.source_data_cutoff}`:null].filter(Boolean);
  if(info.length)details.append(el('p',info.join(' / ')));
  if(record.source_url&&/^https?:\/\//.test(record.source_url)){const a=el('a','Source publication');a.href=record.source_url;a.target='_blank';a.rel='noopener noreferrer';details.append(a);}
 }
 if(overview)details.append(link('Detailed sources and research records','reports'));
 else{const raw=el('details');raw.append(el('summary','Complete source records'),recordView({metadata,records}));details.append(raw);}
 container.append(details);
}
function card(root,id,kicker,title,route){const section=el('section',null,'overview-card');section.id=id;section.setAttribute('aria-labelledby',id+'-title');const head=el('div',null,'overview-card-heading'),copy=el('div');copy.append(el('p',kicker,'eyebrow'));const heading=el('h3',title);heading.id=id+'-title';copy.append(heading);head.append(copy);if(route)head.append(link('Explore →',route));section.append(head);root.append(section);return section;}
export function renderMortalityHeatmap(container,grid,{geography='Scotland'}={}){
 container.replaceChildren();const values=grid.flatMap(r=>r.quarters.map(q=>q.value)).filter(v=>v!==null),max=values.length?Math.max(...values):null;
 if(!grid.length){unavailable(container,null,'Quarterly mortality observations are unavailable.');return;}
 const wrap=el('div',null,'table-scroll heatmap-scroll');wrap.tabIndex=0;const table=el('table',null,'mortality-heatmap');
 table.append(el('caption',`Police Scotland suspected deaths, ${geography}. Gold intensity scales with count magnitude within the selected years. Missing observations are labelled separately.`));
 const head=el('thead'),header=el('tr');for(const text of ['Year','Q1','Q2','Q3','Q4']){const th=el('th',text);th.scope='col';header.append(th);}head.append(header);table.append(head);const body=el('tbody');
 for(const row of grid){const tr=el('tr'),year=el('th',row.year);year.scope='row';tr.append(year);for(const q of row.quarters){const td=el('td',q.value===null?'Unavailable':number(q.value));td.dataset.level=q.value===null?'missing':String(max?Math.ceil(q.value/max*4):0);td.setAttribute('aria-label',`${q.year} Q${q.quarter}: ${q.value===null?'unavailable observation':`${q.value} suspected deaths`}`);td.title=td.getAttribute('aria-label');tr.append(td);}body.append(tr);}table.append(body);wrap.append(table);container.append(wrap);
 const legend=el('p',max===null?'No observed counts for a colour scale.':`Sequential count scale: 0 to ${number(max)} suspected deaths. Recorded zeros and missing observations are shown separately.`,'heatmap-key');container.append(legend);
}

export async function mountOverview({api,summary,before,after,isCurrent,onMortality}){
 summary.replaceChildren();for(let i=0;i<4;i++){const loading=el('article','Loading verified indicator…','summary-card');loading.dataset.state='loading';summary.append(loading);}

 after.hidden=false;after.className='overview-grid findings-overview';after.replaceChildren();
 const heat=card(after,'overview-heatmap','TEMPORAL PATTERNS','Mortality by year & quarter','trends'),heatBody=el('div');heat.append(heatBody);
 const geo=card(after,'overview-geography','GEOGRAPHIC EVIDENCE','Inverclyde: registered deaths and published rates','geography');
 const forensic=card(after,'overview-substances','TOXICOLOGY SNAPSHOT','Forensic substance detections','substance');
 const monitoring=card(after,'overview-monitoring','RESEARCH SIGNALS','Historical statistical monitoring','anomalies');
 const forecast=card(after,'overview-forecast','FORECASTING ANALYSIS','Forecast evaluation','forecasting');
 const coverage=card(after,'overview-coverage','EVIDENCE COVERAGE','Sources, periods & next steps','reports');
 for(const section of [heatBody,geo,forensic,monitoring,forecast,coverage]){const loading=el('p','Loading verified research…','overview-loading');loading.dataset.state='loading';section.append(loading);}
 const results=await loadOverview(api);if(!isCurrent())return;
 for(const section of [geo,forensic,monitoring,forecast,coverage])section.querySelector('.overview-loading')?.remove();
 const overview=results.overview.state==='ready'?results.overview.data[0]:null;
 let database=overview?.database??{state:results.overview.state,data:[],total:0,metadata:{},message:results.overview.message||'Mortality observations unavailable.'};
 try{if(database.state==='ready'&&database.total!==database.data.length)throw new Error('Incomplete mortality response; historical coverage cannot be verified.');mortalityGrid(database.state==='ready'?database.data:[]);}catch(error){database={state:'unavailable',data:[],total:0,metadata:database.metadata,message:error.message};}
 const sources=Array.isArray(overview?.sources)?overview.sources:[];
 summary.replaceChildren();for(const item of overviewKpis(database,sources).slice(0,2)){const article=el('article',null,'summary-card overview-kpi');article.append(el('span',item.title),el('strong',item.value),el('p',item.context),el('small',item.source));summary.append(article);}
 const allRows=database.state==='ready'?database.data:[],years=[...new Set(allRows.map(r=>r.year))].sort((a,b)=>a-b);
 const controls=el('div',null,'overview-period-controls');controls.setAttribute('role','group');controls.setAttribute('aria-label','Mortality reporting years');const selects=[];
 for(const [id,title]of [['overview-from-year','Mortality from year'],['overview-to-year','Mortality to year']]){const field=el('label',title),select=el('select');select.id=id;for(const year of years)select.add(new Option(String(year),String(year)));select.disabled=!years.length;field.append(select);controls.append(field);selects.push(select);}
 selects[1].value=String(years.at(-1)??'');const reset=el('button','All available years');reset.type='button';reset.disabled=!years.length;controls.append(reset);before.append(controls,el('p','Year controls apply to the mortality line, heatmap and observations table. Headline values describe the full returned dataset, not the selected chart years.','overview-filter-note'));
 function draw(){if(!isCurrent())return;const start=Number(selects[0].value),end=Number(selects[1].value);if(start>end){onMortality({state:'unavailable',data:[],total:0,metadata:database.metadata,message:'From year must be no later than To year.'});renderMortalityHeatmap(heatBody,[]);return;}const rows=allRows.filter(r=>r.year>=start&&r.year<=end);onMortality({...database,data:rows,total:rows.length,metadata:{...database.metadata,source:mortalitySource}});renderMortalityHeatmap(heatBody,mortalityGrid(rows));}
 for(const select of selects)select.onchange=draw;reset.onclick=()=>{selects[0].value=String(years[0]);selects[1].value=String(years.at(-1));draw();};draw();
 provenance(heat,'Mortality source & definition',database,[{source_id:mortalitySource,reporting_definition:'Provisional suspected deaths, calendar quarters; distinct from NRS registered drug misuse deaths.',...database.metadata}]);
 const caseStudy=results.geography.state==='ready'?results.geography.data[0]:null,latest=caseStudy?.findings?.latest,rate=caseStudy?.findings?.latest_published_rate_comparison;
 if(latest&&latest.boundary_type==='council'&&latest.indicator_id==='nrs_registered_drug_misuse_deaths'){
  geo.append(el('p',`${latest.geography} council · ${latest.year} registration year`,'overview-source-line'),el('strong',`${number(latest.observed_value)} registered drug misuse deaths`,'overview-stat'),el('p','NRS reports registered deaths annually; Police Scotland reports suspected deaths quarterly. Published age-standardised council rates use five-year periods.'));
  if(rate&&[rate.inverclyde_rate,rate.scotland_rate].every(Number.isFinite))geo.append(el('p',`${rate.period_label} · published five-year age-standardised rates per 100,000`,'overview-source-line'),el('p',`Inverclyde ${number(rate.inverclyde_rate)} (95% CI ${number(rate.inverclyde_lower95)}–${number(rate.inverclyde_upper95)}); Scotland ${number(rate.scotland_rate)} (${number(rate.scotland_lower95)}–${number(rate.scotland_upper95)}).`),el('p','Scotland includes Inverclyde; adjacent five-year periods overlap. These published rates and annual counts are distinct measures.'));
  geo.append(el('p','This result is reported at Inverclyde council level. Greenock-specific estimates require a locality-level source.','overview-caveat'));provenance(geo,'NRS source, boundary & denominator',results.geography,[caseStudy.source,latest,rate].filter(Boolean));
 }else unavailable(geo,results.geography);
 const toxicology=latestForensic(results.forensic);
 if(toxicology.state==='ready'){
  forensic.append(el('p',`${toxicology.period} · ${toxicology.rows[0].geography}`,'overview-source-line'),el('p','Forensic testing detections are sample counts. Categories can overlap, and the current API reports the source-defined groups.'));
  const list=el('dl',null,'substance-preview');for(const row of toxicology.rows)list.append(el('dt',label(row.indicator_id.split(':').slice(1).join(':'))),el('dd',number(row.observed_value)));forensic.append(list);provenance(forensic,'Toxicology source & reporting definition',results.forensic,toxicology.rows);
 }else unavailable(forensic,toxicology);
 if(results.monitoring.state==='ready'&&Number.isInteger(results.monitoring.total)){
  monitoring.append(el('strong',`${number(results.monitoring.total)} historical statistical flags`,'overview-stat'),el('p','Prior-observation median and median absolute deviation (MAD) screen. Review each flag with its source, geography, direction and reference period.'),el('p','The monitoring view keeps source reporting periods separate.','overview-source-line'));
  if(Number.isInteger(overview?.original_runs))monitoring.append(el('p',`${number(overview.original_runs)} saved runs grouped by source series, method and direction.`));provenance(monitoring,'Monitoring method & provenance',results.monitoring,results.monitoring.data);
 }else unavailable(monitoring,results.monitoring,'Historical monitoring results could not be loaded. Refresh data to view the saved flags.');
 const validation=results.validation.state==='ready'?results.validation.data[0]:null;
 monitoring.append(el('p',validation?`PHS alert archive: ${validation.foi_status==='received_archived_publications'?'received and stored':'status unavailable'}. Live alert feed sync: ${validation.live_alert_sync===false?'off':'status unavailable'}.`:'PHS alert archive status unavailable.','overview-caveat'));
 provenance(monitoring,'External validation status',results.validation,results.validation.data??[]);
 const projection=forecastPreview(results.forecast);
 if(projection.state==='ready'){const row=projection.row;forecast.append(el('p',projection.context,'overview-source-line'),el('strong',`${number(row.predicted)} projected suspected deaths`,'overview-stat'),el('p','Saved one-quarter naïve-model projection for Scotland. This target period has elapsed; no new forecast is generated.'));
  if(Number.isFinite(row.lower95)&&Number.isFinite(row.upper95))forecast.append(el('p',`95% model interval: ${number(row.lower95)}–${number(row.upper95)}. These are model-based bounds, not a guarantee.`, 'overview-interval'));
  forecast.append(el('p',`Interval method: ${projection.interval}.`));provenance(forecast,'Forecast source, origin & interval method',results.forecast,[row]);
 }else unavailable(forecast,projection);
 if(sources.length){const wrap=el('div',null,'table-scroll');wrap.tabIndex=0;const table=el('table');table.append(el('caption','Saved research datasets. Cutoffs use each source’s own reporting basis; records overlap and must not be summed into people or events.'));const head=el('thead'),tr=el('tr');for(const text of ['Source series','Records','Source cutoff']){const th=el('th',text);th.scope='col';tr.append(th);}head.append(tr);table.append(head);const body=el('tbody');for(const source of sources){const row=el('tr');row.append(el('td',label(source.resource)),el('td',number(source.records)),el('td',source.cutoff||'Unavailable'));body.append(row);}table.append(body);wrap.append(table);coverage.append(wrap);provenance(coverage,'Sources and analysis details',results.overview,sources.map(s=>({resource:s.resource,...s.provenance})));
 }else unavailable(coverage,results.overview,'Refresh data to load the saved source coverage.');
 const nav=el('nav',null,'overview-research-links');nav.setAttribute('aria-label','Explore research evidence');for(const [route,title]of [['substance','Explore toxicology patterns'],['comparison','Compare areas and substances'],['anomalies','Review statistical monitoring'],['forecasting','Evaluate historical forecasts'],['methodology','Sources and methods']])nav.append(link(title,route));after.prepend(nav);nav.classList.add('research-shortcuts');
 geo.after(heat);after.prepend(geo);geo.after(nav);
 for(const panel of [heat,forensic,monitoring,forecast,coverage])disclose(panel);
 return results;
}
