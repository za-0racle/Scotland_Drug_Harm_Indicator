import {label} from './presentation.js';
import {areasFor,boundaries} from './data.js';
import {compatibleAreas} from './comparison-data.js';
export function createFilters(root,api,areas,onChange){
 const q=id=>root.querySelector('#'+id),ids=['boundary','area','indicator','category','start-year','end-year','model','compare'];
 let metadata=[],page='',view='',busy=false,sequence=0,resetting=false;const saved=new Map();
 const read=()=>Object.fromEntries(ids.map(id=>[id,q(id).value]));
 function options(id,items,blank,preferred=''){
  const node=q(id);node.replaceChildren();if(blank){const o=new Option(blank,'');node.add(o);}
  for(const[value,text]of items)node.add(new Option(text,value));
  if([...node.options].some(o=>o.value===preferred))node.value=preferred;
 }
 options('boundary',boundaries(areas).map(v=>[v,label(v)]),'All geographic scopes');
 function visibility(){
  const scoped=['geography','exploration','anomalies','signals'].includes(page);
  const hiddenView=page==='anomalies'&&['models','zero'].includes(view)||page==='signals'&&['validation','stored','configurations'].includes(view);
  root.querySelector('.filter-panel').hidden=!scoped||hiddenView;
  const hasModel=page==='anomalies'&&!['sensitivity','models','zero'].includes(view)||page==='signals'&&['','runs','evidence'].includes(view);
  const compare=['geography','exploration'].includes(page)&&view==='comparison';
  for(const id of ids)q(id).closest('label').hidden=false;
  q('model').closest('label').hidden=!hasModel;q('compare').closest('label').hidden=!compare;
  const selected=metadata.find(i=>i.indicator_id===q('indicator').value);
  const study=selected?.period_basis?.includes('not_calendar');for(const id of ['start-year','end-year'])q(id).closest('label').hidden=Boolean(study);
  q('category').closest('label').hidden=!(selected?.categories?.length>1);
  if(page==='signals'&&view==='evidence')q('indicator').closest('label').hidden=true;
  q('model').disabled=busy||!hasModel;q('compare').disabled=busy||!compare||q('compare').options.length<2;
  root.querySelector('#more-filters').hidden=['start-year','end-year','model','compare','category'].every(id=>q(id).closest('label').hidden);
  const active=['start-year','end-year','model','compare','category'].filter(id=>!q(id).closest('label').hidden&&q(id).value).length;root.querySelector('#more-filters > summary').textContent=active?`More filters (${active} active)`:'More filters';
  q('filter-help').textContent=study?'This source uses unequal study periods. Verified calendar-year filters are unavailable.':compare&&q('compare').options.length<2?'No other area has this measure within the same geographic boundary.':'Selections update results immediately. More filters contains the time range and applicable analytical options.';
 }
 function categories(previous=''){
  const selected=metadata.find(i=>i.indicator_id===q('indicator').value);
  options('category',(selected?.categories??[]).map(v=>[v,label(v)]),'All supported categories',previous);
  const area=areas.find(a=>a.geography_id===q('area').value);
  const candidates=compatibleAreas(areas,area,q('indicator').value);
  options('compare',candidates.sort((a,b)=>a.name.localeCompare(b.name)).map(a=>[a.geography_id,a.name]),'Choose a compatible area',q('compare').value);
  visibility();
 }
 async function methods(){
  const previous=q('model').value;
  let rows=[];
  if(['anomalies','signals'].includes(page)&&!(page==='anomalies'&&['sensitivity','models','zero'].includes(view))){
   const result=await api('/anomalies/models',{geography_id:q('area').value,indicator:q('indicator').value,limit:1000});
   rows=result.data.filter(row=>Number(row.evaluated)>0);
  }
  const supported=[...new Set(rows.map(row=>row.method))].filter(method=>page!=='signals'||view!=='evidence'||method==='nb2_moments');
  options('model',supported.sort().map(method=>[method,label(method)]),'Historical robust screen',previous);
 }
 async function indicators(previous=''){
  const result=await api(q('area').value?`/geographies/${q('area').value}/indicators`:'/indicators',{limit:1000});metadata=result.data;
  metadata.sort((a,b)=>label(a.indicator_id).localeCompare(label(b.indicator_id)));
  const specific=['geography','exploration'].includes(page);
  options('indicator',metadata.map(r=>[r.indicator_id,label(r.indicator_id)]),specific?null:'All measures',previous);
  if(specific&&!previous){const preferred=metadata.find(r=>r.indicator_id.includes('suspected'));if(preferred)q('indicator').value=preferred.indicator_id;}
  categories();await methods();
 }
 async function areaOptions(previous='',indicator=''){
  const list=areasFor(areas,q('boundary').value).sort((a,b)=>a.name.localeCompare(b.name));
  options('area',list.map(a=>[a.geography_id,a.name]),['geography','exploration'].includes(page)?'Choose a reporting area':'All reporting areas',previous);
  await indicators(indicator);
 }
 async function change(id){
  if(resetting)return;
  const current=++sequence,old=read();busy=true;q('reset-filters').disabled=true;for(const key of ids)q(key).disabled=true;
  root.setAttribute('aria-busy','true');root.querySelector('#api-status').textContent='Updating available filters...';
  try{
   if(id==='boundary')await areaOptions(old.area,old.indicator);
   else if(id==='area')await indicators(old.indicator);
   else if(id==='indicator'){categories(old.category);await methods();}
   if(current!==sequence)return;
  }catch(error){root.querySelector('#api-status').textContent=error.message;root.querySelector('#api-status').dataset.state='error';return;}
  finally{if(current===sequence){busy=false;q('reset-filters').disabled=false;for(const key of ids)q(key).disabled=false;root.setAttribute('aria-busy','false');visibility();}}
  onChange();
 }
 for(const id of ids)q(id).onchange=()=>change(id);
 async function configure(nextPage,nextView='',reset=false){
  if(nextPage!==page||reset){
   root.querySelector('#more-filters').open=false;
   if(page&&!reset)saved.set(page,read());page=nextPage;view=nextView;
   if(!['geography','exploration','anomalies','signals'].includes(page)){visibility();return;}
   const state=reset?{}:saved.get(page)??{};
   const national=areas.find(a=>a.name==='Scotland'&&a.boundary_type==='country');
   const specific=['geography','exploration'].includes(page);
   q('boundary').value=state.boundary??(specific?'country':'');
   for(const id of ['start-year','end-year','model'])q(id).value=state[id]??'';
   await areaOptions(state.area??(specific?national?.geography_id:''),state.indicator??'');
   categories(state.category);q('compare').value=[...q('compare').options].some(o=>o.value===state.compare)?state.compare:'';
  }else if(view!==nextView){view=nextView;await methods();}
  visibility();
 }
 // Preserve the edited field's focus until activation: a blur-triggered change
 // must not disable or move Reset between pointer-down and click.
 q('reset-filters').onpointerdown=event=>event.preventDefault();
 q('reset-filters').onclick=async()=>{
  resetting=true;sequence++;
  try{await configure(page,view,true);root.querySelector('#more-filters').open=false;q('boundary').focus();}
  finally{resetting=false;}
  onChange();
 };
 return{configure,metadata:()=>metadata,params(){
  if(root.querySelector('.filter-panel').hidden)return{};
  const f={geography_id:q('area').value,boundary_type:q('boundary').value,indicator:q('indicator').value,start_year:q('start-year').value,end_year:q('end-year').value};
  for(const [id,key]of [['start-year','start_year'],['end-year','end_year']])if(q(id).closest('label').hidden)delete f[key];
  if(!q('category').closest('label').hidden)f.category=q('category').value;
  if(!q('model').closest('label').hidden)f.model=q('model').value;
  if(!q('compare').closest('label').hidden)f.compare_to=q('compare').value;
  if(page==='signals'&&view==='evidence')delete f.indicator;
  return f;
 },async selectArea(area){q('boundary').value=area.boundary_type;await areaOptions(area.geography_id);},values:read};
}
