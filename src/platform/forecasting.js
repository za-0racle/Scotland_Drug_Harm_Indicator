import Chart from 'chart.js/auto';
import './forecasting.css';

const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(cls)node.className=cls;return node;};
const fmt=value=>new Intl.NumberFormat('en-GB').format(value);

export async function mountForecasting({root,api,onStatus=()=>{},isCurrent=()=>true}){
 root.replaceChildren();
 const form=el('form',undefined,'filter-panel forecast-filters');form.setAttribute('aria-label','Forecast filters');
 const fields={};
 for(const [key,title] of [['geography','Geographical area'],['category','Substance category'],['year','Year'],['quarter','Quarter'],['model','Forecast model']]){
  const label=el('label',title),select=el('select');select.name=key;select.required=true;fields[key]=select;label.append(select);form.append(label);
 }
 const note=el('p','Drug deaths are the outcome when “All suspected drug deaths” is selected. Substance categories use forensic toxicology detections, which are not substance-specific deaths.','forecast-source-note');
 const actions=el('div',undefined,'filter-actions'),applyButton=el('button','Apply forecast'),reset=el('button','Reset'),csv=el('button','Export forecasts CSV');applyButton.type='submit';reset.type='button';csv.type='button';csv.disabled=true;actions.append(applyButton,reset,csv);form.append(note,actions);root.append(form);
 const status=el('p','Loading supported forecasting options…');status.setAttribute('role','status');status.setAttribute('aria-live','polite');root.append(status);
 const summary=el('section',undefined,'summary-grid forecast-summary');summary.setAttribute('aria-label','Forecast summary');root.append(summary);
 const chartPanel=el('section',undefined,'chart-panel forecast-chart-panel'),heading=el('h3','Historical observations and future estimates'),context=el('p'),wrap=el('div',undefined,'plot-wrap'),canvas=el('canvas');canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Historical observations and forecast estimates with prediction intervals');wrap.append(canvas);chartPanel.append(heading,context,wrap);root.append(chartPanel);
 const tablePanel=el('section',undefined,'forecast-output'),tableTitle=el('h3','Quarterly forecast estimates'),tableWrap=el('div',undefined,'table-scroll');tablePanel.append(tableTitle,tableWrap);root.append(tablePanel);
 const evaluation=el('details',undefined,'supporting-analysis'),summaryText=el('summary','Model performance and evaluation limits'),evaluationBody=el('div');evaluation.append(summaryText,evaluationBody);root.append(evaluation);
 const limitations=el('details',undefined,'supporting-analysis'),limitSummary=el('summary','Data, intervals and interpretation'),limitBody=el('div');limitations.append(limitSummary,limitBody);root.append(limitations);
 let chart=null,lastResult=null,options=null;
 const setStatus=(message,state='ready')=>{status.textContent=message;status.dataset.state=state;onStatus(state,message);};
 const fill=(select,items,key,label)=>select.replaceChildren(...items.map(item=>{const option=el('option',label(item));option.value=key(item);return option;}));
 const updateControls=()=>{
  if(!options)return;
  const toxic=fields.category.value!=='all';
  fields.geography.disabled=toxic;
  if(toxic){if(![...fields.geography.options].some(o=>o.value===options.substance_geography)){const option=el('option',options.substance_geography);option.value=options.substance_geography;fields.geography.append(option);}fields.geography.value=options.substance_geography;}
  else if(fields.geography.value===options.substance_geography)fields.geography.value='Scotland';
  [...fields.quarter.options].forEach(option=>{option.disabled=toxic&&fields.year.value==='2026'&&option.value==='1';});
  if(toxic&&fields.year.value==='2026'&&fields.quarter.value==='1')fields.quarter.value='2';
 };
 const showSummary=result=>{
  const meta=result.data_coverage,forecasts=result.forecasts;
  const cards=[['Geographical area',result.filters.geography],['Outcome',meta.outcome],['Last observation',`${meta.last}: ${fmt(result.historical.at(-1).value)}`],['Selected model',result.selected_model.replaceAll('_',' ')],['Forecast horizon',`${forecasts.length} quarters`],['Sum of quarterly expected counts',fmt(forecasts.reduce((sum,row)=>sum+row.predicted,0))]];
  summary.replaceChildren(...cards.map(([title,value])=>{const card=el('article',undefined,'summary-card');card.append(el('span',title),el('strong',value));return card;}));
 };
 const renderTable=result=>{
  const table=el('table');table.append(el('caption','Model-generated future quarterly estimates; values are not observed outcomes.'));
  const headers=['Quarter','Status','Predicted value','80% lower','80% upper','95% lower','95% upper','Selected model'];
  const thead=el('thead'),tr=el('tr');for(const title of headers){const th=el('th',title);th.scope='col';tr.append(th);}thead.append(tr);table.append(thead);
  const tbody=el('tbody');for(const row of result.forecasts){const tr=el('tr');for(const value of [row.target_period,'Forecast',fmt(row.predicted),fmt(row.lower80),fmt(row.upper80),fmt(row.lower95),fmt(row.upper95),row.model.replaceAll('_',' ')])tr.append(el('td',value));tbody.append(tr);}table.append(tbody);tableWrap.replaceChildren(table);
 };
 const renderChart=result=>{
  chart?.destroy();chart=null;const history=result.historical,forecast=result.forecasts,labels=[...history.map(row=>row.observation_period),...forecast.map(row=>row.target_period)],n=history.length;
  const style=getComputedStyle(canvas),ink=style.getPropertyValue('--ink').trim()||'#222',grid=style.getPropertyValue('--chart-grid').trim()||'#ddd';
  const band=(name,key,color,fill)=>({label:name,data:[...Array(n).fill(null),...forecast.map(row=>row[key])],borderColor:'transparent',backgroundColor:color,pointRadius:0,borderWidth:0,fill,spanGaps:false});
  const datasets=[{label:'Historical observed values',data:[...history.map(row=>row.value),...Array(forecast.length).fill(null)],borderColor:'#496c7b',backgroundColor:'#496c7b',pointRadius:2,borderWidth:2,spanGaps:false},band('95% lower bound','lower95','transparent',false),band('95% prediction interval','upper95','rgba(179,157,120,.14)','-1'),band('80% lower bound','lower80','transparent',false),band('80% prediction interval','upper80','rgba(179,157,120,.27)','-1'),{label:'Forecast point estimate',data:[...Array(n).fill(null),...forecast.map(row=>row.predicted)],borderColor:'#ad6f26',backgroundColor:'#ad6f26',borderDash:[6,4],pointRadius:3,borderWidth:2,spanGaps:false}];
  chart=new Chart(canvas,{type:'line',data:{labels,datasets},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{position:'bottom',labels:{color:ink,usePointStyle:true,filter:item=>!item.text.includes('lower bound')}},tooltip:{callbacks:{label:item=>`${item.dataset.label}: ${item.formattedValue}`}}},scales:{x:{grid:{display:false},ticks:{color:ink,maxTicksLimit:12,maxRotation:0},title:{display:true,text:'Quarter',color:ink}},y:{beginAtZero:true,grid:{color:grid},ticks:{color:ink},title:{display:true,text:`${result.data_coverage.unit} (count)`,color:ink}}}}});
  context.textContent=`Observed: ${result.data_coverage.first}–${result.data_coverage.last}. Forecast starts after the source cutoff. Source: ${result.data_coverage.source}.`;
 };
 const renderEvaluation=result=>{
  const selection=result.filters.model==='auto'?`Historical backtests selected ${result.selected_model.replaceAll('_',' ')} using horizon-specific errors.`:`You selected ${result.selected_model.replaceAll('_',' ')}. It is fitted to the historical series; this is a model forecast, not a copied forward trend.`;
  evaluationBody.replaceChildren(el('p',`${selection} Expanding-window backtesting uses only observations available at each origin. It does not establish prospective accuracy.`));
  const table=el('table'),head=el('thead'),row=el('tr');for(const name of ['Horizon','Model','Origins',`MAE (${result.data_coverage.unit})`,`RMSE (${result.data_coverage.unit})`,'Bias']){const th=el('th',name);th.scope='col';row.append(th);}head.append(row);table.append(head);const body=el('tbody');
  for(const metric of result.model_evaluation){const tr=el('tr');for(const value of [`${metric.horizon} quarters`,metric.model.replaceAll('_',' '),metric.evaluated_origins,metric.mae===null?'Unavailable':metric.mae.toFixed(2),metric.rmse===null?'Unavailable':metric.rmse.toFixed(2),metric.bias===null?'Unavailable':metric.bias.toFixed(2)])tr.append(el('td',value));body.append(tr);}table.append(body);evaluationBody.append(table);
  for(const h of result.backtest_horizons)evaluationBody.append(el('p',`${h.horizon}-quarter evaluation: ${h.origins} successful expanding-window origins.`));for(const warning of result.warnings)evaluationBody.append(el('p',warning));
 };
 const renderLimitations=result=>limitBody.replaceChildren(el('p',result.interval_note),...result.limitations.map(text=>el('p',text)));
 const download=()=>{if(!lastResult)return;const headings=['quarter','status','predicted','lower80','upper80','lower95','upper95','model'];const rows=lastResult.forecasts.map(row=>[row.target_period,'forecast',row.predicted,row.lower80,row.upper80,row.lower95,row.upper95,row.model]);const csvText=[headings,...rows].map(row=>row.map(value=>`"${String(value).replaceAll('"','""')}"`).join(',')).join('\r\n');const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([csvText],{type:'text/csv;charset=utf-8'}));link.download='sdhi-quarterly-forecasts.csv';link.click();URL.revokeObjectURL(link.href);};
 const runForecast=async event=>{event?.preventDefault();updateControls();chart?.destroy();chart=null;lastResult=null;tableWrap.replaceChildren();summary.replaceChildren();setStatus('Generating a forecast from the selected historical series…','loading');for(const control of Object.values(fields))control.disabled=true;applyButton.disabled=true;csv.disabled=true;
  try{const result=await api('/forecasting/generate',{geography:fields.geography.value,category:fields.category.value,year:fields.year.value,quarter:fields.quarter.value,model:fields.model.value});if(!isCurrent())return;if(result.state!=='ready'||!result.data?.[0])throw new Error(result.message||'No forecast is available for this selection.');lastResult=result.data[0];showSummary(lastResult);renderChart(lastResult);renderTable(lastResult);renderEvaluation(lastResult);renderLimitations(lastResult);setStatus(`${lastResult.forecasts.length} quarterly ${lastResult.data_coverage.unit} estimates generated from ${lastResult.data_coverage.observations} historical observations.`);csv.disabled=false;
  }catch(error){if(isCurrent())setStatus(error.message||'Forecast could not be generated.','error');}
  finally{for(const control of Object.values(fields))control.disabled=false;updateControls();applyButton.disabled=false;}
 };
 form.addEventListener('submit',runForecast);csv.addEventListener('click',download);
 for(const select of Object.values(fields))select.addEventListener('change',()=>{updateControls();csv.disabled=true;setStatus('Filters changed. Apply forecast to refresh the results.','pending');});
 reset.addEventListener('click',()=>{if(!options)return;fields.category.value='all';fields.geography.value='Scotland';fields.year.value='2028';fields.quarter.value='4';fields.model.value='nb2_trend';updateControls();runForecast();});
 try{const result=await api('/forecasting/options',{});if(!isCurrent())return;if(result.state!=='ready'||!result.data?.[0])throw new Error('Forecast options are unavailable.');options=result.data[0];fill(fields.geography,options.geographies,value=>value,value=>value);fill(fields.category,options.substances,item=>item.id,item=>item.label);fill(fields.year,options.years,item=>item.id,item=>item.label);fill(fields.quarter,options.quarters,item=>item.id,item=>item.label);fill(fields.model,options.models,item=>item.id,item=>item.label);fields.geography.value='Scotland';fields.category.value='all';fields.year.value='2028';fields.quarter.value='4';fields.model.value='nb2_trend';updateControls();await runForecast();}
 catch(error){setStatus(error.message||'Forecast options could not be loaded.','error');}
 return()=>chart?.destroy();
}
