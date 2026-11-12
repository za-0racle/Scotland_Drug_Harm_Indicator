import Chart from 'chart.js/auto';
import {prepareChart} from './chart-data.js';
import {comparisonTable} from './comparison-data.js';
const charts=new Map();
export function clearChart(canvas){if(canvas){charts.get(canvas)?.destroy();charts.delete(canvas);canvas.parentElement?.parentElement?.querySelector('[data-chart-legend]')?.replaceChildren();}else{for(const [node,chart] of charts){chart.destroy();node.parentElement?.parentElement?.querySelector('[data-chart-legend]')?.replaceChildren();}charts.clear();}}
export function renderChart(canvas,rows,label='Recorded value',coverage={}){
 clearChart(canvas);
 let legend=canvas.parentElement.parentElement.querySelector('[data-chart-legend]');
 if(!legend){legend=document.createElement('div');legend.dataset.chartLegend='';legend.className='chart-legend';legend.setAttribute('role','group');legend.setAttribute('aria-label','Chart series visibility');canvas.parentElement.after(legend);}
 let note=canvas.parentElement.parentElement.querySelector('[data-chart-note]');
 if(!note){note=document.createElement('p');note.dataset.chartNote='';note.setAttribute('role','status');canvas.parentElement.before(note);}
 let prepared;
 try{prepared=prepareChart(rows,coverage);if(rows.some(r=>r.comparison_role)){const table=comparisonTable(rows,{kind:coverage.comparisonKind??'areas'});prepared.warnings.push(`${table.filter(r=>r.coverage!=='paired').length} reporting periods have missing or unavailable paired values within the returned coverage.`);}}catch(error){note.textContent=error.message;return;}
 note.textContent=prepared.warnings.join(' ');
 const style=getComputedStyle(canvas),colors=[1,2,3,4,5].map(i=>style.getPropertyValue('--series-'+i).trim());
 const datasets=prepared.datasets.map((series,i)=>({label:coverage.seriesLabel?.(series)??series.label,seriesId:series.key,metadata:series.metadata,records:series.points.map(p=>p.record),data:series.points.map(p=>p.value),showLine:series.showLine,borderColor:colors[i%colors.length],backgroundColor:colors[i%colors.length],pointRadius:series.showLine?2:5,tension:0,spanGaps:false}));
 if(rows.length===1&&rows[0].predicted!==undefined){for(const key of ['lower95','upper95'])if(rows[0][key]!==undefined&&rows[0][key]!==null)datasets.push({label:key==='lower95'?'95% lower uncertainty bound':'95% upper uncertainty bound',data:[rows[0][key]],records:[rows[0]],showLine:false,borderColor:'#7a8492',pointRadius:5});}
 if(!datasets.some(s=>s.data.some(v=>v!==null&&Number.isFinite(v))))return;
 const reduced=globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
 const ink=style.getPropertyValue('--ink').trim()||'#252525',grid=style.getPropertyValue('--chart-grid').trim()||'#E9E5DC';
 const chart=new Chart(canvas,{type:'line',data:{labels:prepared.labels,datasets},options:{color:ink,responsive:true,maintainAspectRatio:false,animation:reduced?false:{duration:250},plugins:{legend:{display:false},tooltip:{backgroundColor:style.getPropertyValue('--surface').trim(),titleColor:ink,bodyColor:ink,borderColor:grid,borderWidth:1,padding:12,callbacks:{afterLabel(context){const record=context.dataset.records?.[context.dataIndex];return record?Object.entries(record).filter(([key])=>['source_id','indicator_id','unit','period_basis','reporting_definition','method','model','window','observation_id','result_id','lower_limit','upper_limit','lower_threshold','upper_threshold','lower95','upper95'].includes(key)).map(([key,value])=>`${key}: ${value}`):[];}}}},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:14,color:ink},title:{display:true,text:prepared.regular?'Source observation period':'Source periods (categorical; elapsed time not represented)',color:ink}},y:{grid:{color:grid},ticks:{color:ink},title:{display:true,text:label,color:ink}}}}});charts.set(canvas,chart);
 for(const[ index,dataset]of datasets.entries()){const button=document.createElement('button');button.type='button';button.setAttribute('aria-pressed','true');button.setAttribute('aria-label',dataset.label);const swatch=document.createElement('span');swatch.className='legend-swatch';swatch.style.backgroundColor=dataset.borderColor;swatch.setAttribute('aria-hidden','true');const text=document.createElement('span');text.textContent=dataset.label;button.append(swatch,text);button.onclick=()=>{const visible=!chart.isDatasetVisible(index);chart.setDatasetVisibility(index,visible);button.setAttribute('aria-pressed',String(visible));chart.update();};legend.append(button);}

}
