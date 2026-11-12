import {loadOverview,mortalityGrid,overviewKpis,latestForensic,forecastPreview,mortalitySource,number} from './overview-data.js';
import {label} from './presentation.js';
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!=null)node.textContent=String(text);if(cls)node.className=cls;return node;};
const link=(text,route)=>{const node=el('a',text,'overview-link');node.href='#'+route;return node;};
function unavailable(container,result,message){const node=el('p',message||result?.message||'Verified observations unavailable. Missing access does not mean zero harm.','overview-state');node.dataset.state=result?.state==='error'?'error':'unavailable';container.append(node);}
export function provenance(container,title,result,records=[]){
 const details=el('details',null,'overview-provenance');details.append(el('summary',title));
 const metadata=result?.metadata??{};
 if(metadata.source_path)details.append(el('p',`Artifact: ${metadata.source_path}`));
 for(const record of records){
  const info=[record.source_id,record.source_sheet,record.source_cell,record.publication_date?`Published ${record.publication_date}`:null,record.source_data_cutoff?`Cutoff ${record.source_data_cutoff}`:null].filter(Boolean);
  if(info.length)details.append(el('p',info.join(' · ')));
  if(record.source_url&&/^https?:\/\//.test(record.source_url)){const a=el('a','Source publication');a.href=record.source_url;a.target='_blank';a.rel='noopener noreferrer';details.append(a);}
 }
 const raw=el('details');raw.append(el('summary','Complete provenance and record metadata'),el('pre',JSON.stringify({metadata,records},null,2)));details.append(raw);container.append(details);
}
function card(root,id,kicker,title,route){const section=el('section',null,'overview-card');section.id=id;section.setAttribute('aria-labelledby',id+'-title');const head=el('div',null,'overview-card-heading'),copy=el('div');copy.append(el('p',kicker,'eyebrow'));const heading=el('h3',title);heading.id=id+'-title';copy.append(heading);head.append(copy);if(route)head.append(link('Explore →',route));section.append(head);root.append(section);return section;}
export function renderMortalityHeatmap(container,grid,{geography='Scotland'}={}){
 container.replaceChildren();const values=grid.flatMap(r=>r.quarters.map(q=>q.value)).filter(v=>v!==null),max=values.length?Math.max(...values):null;
 if(!grid.length){unavailable(container,null,'Quarterly mortality observations are unavailable.');return;}
 const wrap=el('div',null,'table-scroll heatmap-scroll');wrap.tabIndex=0;const table=el('table',null,'mortality-heatmap');
 table.append(el('caption',`Police Scotland suspected deaths, ${geography}. Gold intensity represents count magnitude within the selected years; it is not a risk or alert threshold. Missing observations are labelled unavailable.`));
 const head=el('thead'),header=el('tr');for(const text of ['Year','Q1','Q2','Q3','Q4']){const th=el('th',text);th.scope='col';header.append(th);}head.append(header);table.append(head);const body=el('tbody');
 for(const row of grid){const tr=el('tr'),year=el('th',row.year);year.scope='row';tr.append(year);for(const q of row.quarters){const td=el('td',q.value===null?'Unavailable':number(q.value));td.dataset.level=q.value===null?'missing':String(max?Math.ceil(q.value/max*4):0);td.setAttribute('aria-label',`${q.year} Q${q.quarter}: ${q.value===null?'unavailable observation':`${q.value} suspected deaths`}`);td.title=td.getAttribute('aria-label');tr.append(td);}body.append(tr);}table.append(body);wrap.append(table);container.append(wrap);
 const legend=el('p',max===null?'No observed counts for a colour scale.':`Sequential count scale: 0 to ${number(max)} suspected deaths. Zero is a recorded count; “Unavailable” is not zero.`,'heatmap-key');container.append(legend);
}

export async function mountOverview({api,summary,before,after,isCurrent,onMortality}){
 summary.replaceChildren();for(let i=0;i<4;i++){const loading=el('article','Loading verified indicator…','summary-card');loading.dataset.state='loading';summary.append(loading);}
 before.append(el('p','Historical surveillance research across mortality, toxicology and ambulance activity. Source periods and definitions remain separate. This is retrospective analysis, not real-time public-health monitoring.','overview-research-summary'));
 after.hidden=false;after.className='overview-grid';after.replaceChildren();
 const heat=card(after,'overview-heatmap','TEMPORAL PATTERNS','Mortality by year & quarter','trends'),heatBody=el('div');heat.append(heatBody);
 const geo=card(after,'overview-geography','GEOGRAPHIC CONTEXT','Inverclyde, in context','geography');
 const forensic=card(after,'overview-substances','TOXICOLOGY SNAPSHOT','Forensic substance detections','substance');
 const monitoring=card(after,'overview-monitoring','RESEARCH SIGNALS','Historical statistical monitoring','anomalies');
 const forecast=card(after,'overview-forecast','FROZEN PROJECTION','Forecasting preview','forecasting');
 const coverage=card(after,'overview-coverage','EVIDENCE COVERAGE','Sources, periods & next steps','reports');
 for(const section of [heatBody,geo,forensic,monitoring,forecast,coverage]){const loading=el('p','Loading verified research…','overview-loading');loading.dataset.state='loading';section.append(loading);}
 const results=await loadOverview(api);if(!isCurrent())return;
 for(const section of [geo,forensic,monitoring,forecast,coverage])section.querySelector('.overview-loading')?.remove();
 const overview=results.overview.state==='ready'?results.overview.data[0]:null;
 let database=overview?.database??{state:results.overview.state,data:[],total:0,metadata:{},message:results.overview.message||'Mortality observations unavailable.'};
 try{if(database.state==='ready'&&database.total!==database.data.length)throw new Error('Incomplete mortality response; historical coverage cannot be verified.');mortalityGrid(database.state==='ready'?database.data:[]);}catch(error){database={state:'unavailable',data:[],total:0,metadata:database.metadata,message:error.message};}
 const sources=Array.isArray(overview?.sources)?overview.sources:[];
 summary.replaceChildren();for(const item of overviewKpis(database,sources)){const article=el('article',null,'summary-card overview-kpi');article.append(el('span',item.title),el('strong',item.value),el('p',item.context),el('small',item.source));summary.append(article);}
 const allRows=database.state==='ready'?database.data:[],years=[...new Set(allRows.map(r=>r.year))].sort((a,b)=>a-b);
 const controls=el('div',null,'overview-period-controls');controls.setAttribute('role','group');controls.setAttribute('aria-label','Mortality reporting years');const selects=[];
 for(const [id,title]of [['overview-from-year','Mortality from year'],['overview-to-year','Mortality to year']]){const field=el('label',title),select=el('select');select.id=id;for(const year of years)select.add(new Option(String(year),String(year)));select.disabled=!years.length;field.append(select);controls.append(field);selects.push(select);}
 selects[1].value=String(years.at(-1)??'');const reset=el('button','All available years');reset.type='button';reset.disabled=!years.length;controls.append(reset);before.append(controls,el('p','Year controls apply to the mortality line, heatmap and observations table. KPI cards describe the full returned historical coverage.','overview-filter-note'));
 function draw(){if(!isCurrent())return;const start=Number(selects[0].value),end=Number(selects[1].value);if(start>end){onMortality({state:'unavailable',data:[],total:0,metadata:database.metadata,message:'From year must be no later than To year.'});renderMortalityHeatmap(heatBody,[]);return;}const rows=allRows.filter(r=>r.year>=start&&r.year<=end);onMortality({...database,data:rows,total:rows.length,metadata:{...database.metadata,source:mortalitySource}});renderMortalityHeatmap(heatBody,mortalityGrid(rows));}
 for(const select of selects)select.onchange=draw;reset.onclick=()=>{selects[0].value=String(years[0]);selects[1].value=String(years.at(-1));draw();};draw();
 provenance(heat,'Mortality source & definition',database,[{source_id:mortalitySource,reporting_definition:'Provisional suspected deaths, calendar quarters; distinct from NRS registered drug misuse deaths.',...database.metadata}]);
 const caseStudy=results.geography.state==='ready'?results.geography.data[0]:null,latest=caseStudy?.findings?.latest,rate=caseStudy?.findings?.latest_published_rate_comparison;
 if(latest&&latest.boundary_type==='council'&&latest.indicator_id==='nrs_registered_drug_misuse_deaths'){
  geo.append(el('p',`${latest.geography} council · ${latest.year} registration year`,'overview-source-line'),el('strong',`${number(latest.observed_value)} registered drug misuse deaths`,'overview-stat'),el('p','NRS registered counts are separate from Police Scotland suspected deaths. Annual council crude rates are unavailable without a compatible denominator.'));
  if(rate&&[rate.inverclyde_rate,rate.scotland_rate].every(Number.isFinite))geo.append(el('p',`${rate.period_label} · published five-year age-standardised rates per 100,000`,'overview-source-line'),el('p',`Inverclyde ${number(rate.inverclyde_rate)} (95% CI ${number(rate.inverclyde_lower95)}–${number(rate.inverclyde_upper95)}); Scotland ${number(rate.scotland_rate)} (${number(rate.scotland_lower95)}–${number(rate.scotland_upper95)}).`),el('p',rate.interpretation));
  geo.append(el('p',caseStudy.greenock?.message??'No Greenock-specific outcome is inferred.','overview-caveat'));provenance(geo,'NRS source, boundary & denominator',results.geography,[caseStudy.source,latest,rate].filter(Boolean));
 }else unavailable(geo,results.geography);
 const toxicology=latestForensic(results.forensic);
 if(toxicology.state==='ready'){
  forensic.append(el('p',`${toxicology.period} · ${toxicology.rows[0].geography}`,'overview-source-line'),el('p','Overlapping broad categories in a forensic testing sample. Detection counts are not causal deaths, mutually exclusive shares or population prevalence. Individual-substance rankings are not available through the current API.'));
  const list=el('dl',null,'substance-preview');for(const row of toxicology.rows)list.append(el('dt',label(row.indicator_id.split(':').slice(1).join(':'))),el('dd',number(row.observed_value)));forensic.append(list);provenance(forensic,'Toxicology source & reporting definition',results.forensic,toxicology.rows);
 }else unavailable(forensic,toxicology);
 if(results.monitoring.state==='ready'&&Number.isInteger(results.monitoring.total)){
  monitoring.append(el('strong',`${number(results.monitoring.total)} historical statistical flags`,'overview-stat'),el('p','Prior-only robust median/MAD count screen across the frozen source observations. Flags are correlated research measurements, not independent incidents or confirmed public-health alerts.'),el('p','Mixed source periods; review the full monitoring view for each observation’s geography, source and reporting period.','overview-source-line'));
  if(Number.isInteger(overview?.original_runs))monitoring.append(el('p',`${number(overview.original_runs)} saved historical runs; consecutive flags do not establish independent events.`));provenance(monitoring,'Monitoring method & provenance',results.monitoring,results.monitoring.data);
 }else unavailable(monitoring,results.monitoring,'Historical flag count unavailable; missing results do not establish no signals.');
 const validation=results.validation.state==='ready'?results.validation.data[0]:null;
 monitoring.append(el('p',validation?`External alert metrics: ${validation.external_alert_metrics??'unavailable'}. FOI status: ${validation.foi_status??'unavailable'}. No operational warning service.`:'External validation status unavailable; no confirmed-alert count is inferred.','overview-caveat'));
 provenance(monitoring,'External validation status',results.validation,results.validation.data??[]);
 const projection=forecastPreview(results.forecast);
 if(projection.state==='ready'){const row=projection.row;forecast.append(el('p',projection.context,'overview-source-line'),el('strong',`${number(row.predicted)} projected suspected deaths`,'overview-stat'),el('p','Saved one-quarter naïve-model projection for Scotland. This target period has elapsed; no new forecast is generated.'));
  if(Number.isFinite(row.lower95)&&Number.isFinite(row.upper95))forecast.append(el('p',`95% model interval: ${number(row.lower95)}–${number(row.upper95)}. These are model-based bounds, not a guarantee.`, 'overview-interval'));
  forecast.append(el('p',`Interval method: ${projection.interval}.`));provenance(forecast,'Forecast source, origin & interval method',results.forecast,[row]);
 }else unavailable(forecast,projection);
 if(sources.length){const wrap=el('div',null,'table-scroll');wrap.tabIndex=0;const table=el('table');table.append(el('caption','Frozen analytical resource families. Cutoffs use each source’s own reporting basis; records overlap and must not be summed into people or events.'));const head=el('thead'),tr=el('tr');for(const text of ['Source series','Records','Source cutoff']){const th=el('th',text);th.scope='col';tr.append(th);}head.append(tr);table.append(head);const body=el('tbody');for(const source of sources){const row=el('tr');row.append(el('td',label(source.resource)),el('td',number(source.records)),el('td',source.cutoff||'Unavailable'));body.append(row);}table.append(body);wrap.append(table);coverage.append(wrap);provenance(coverage,'Coverage manifests & source identifiers',results.overview,sources.map(s=>({resource:s.resource,...s.provenance})));
 }else unavailable(coverage,results.overview,'Source coverage could not be loaded; no source count is inferred.');
 const nav=el('nav',null,'overview-research-links');nav.setAttribute('aria-label','Explore research evidence');for(const [route,title]of [['geography','Explore geographic trends'],['comparison','Compare compatible areas'],['signals','Review surveillance signals'],['methodology','Sources & methodology']])nav.append(link(title,route));coverage.append(nav);
 return results;
}
