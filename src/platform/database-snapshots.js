const resources={
 naloxone_activity:{
  label:'Naloxone activity — live database snapshot',
  path:'/database/v1/naloxone-activity',
  columns:[['week_beginning','Reporting week'],['geography_display','Geography'],['geography_class','Geography class'],['administrations','Administrations (count)'],['moving_average','Source-reported moving average'],['source_dataset','Source dataset']],
  note:'This is a live database representation, separate from the frozen Phase 4 analytical series. Administrations match the frozen source; 14 first-week board moving averages are populated here but remain missing in the frozen source. The moving average is source-reported, not recalculated by this application.'
 },
 geographic_areas:{
  label:'Geographic registry — live database snapshot',
  path:'/database/v1/geographic-areas',
  columns:[['area_code','Area code'],['area_name','Area name'],['geography_class','Geography class'],['area_type','Source area type'],['valid_from','Valid from'],['valid_to','Valid to'],['source_dataset','Source dataset']],
  note:'Validity dates are the current database values. Frozen research outputs and their geographic identities are not changed by this registry view.'
 },
 data_sources:{
  label:'Source catalog — live database snapshot',
  path:'/database/v1/data-sources',
  columns:[['dataset_name','Dataset'],['publisher','Publisher'],['source_url','Source URL'],['source_sha256','Source SHA-256'],['source_id','Source ID'],['notes','Source notes']],
  note:'This database source catalog is metadata only. URLs and checksums do not alter or replace frozen source files.'
 }
};
const pageSize=100;
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined&&text!==null)node.textContent=String(text);if(cls)node.className=cls;return node;};
const csvValue=value=>{let text=value===null||value===undefined?'':String(value);if(/^[\s]*[=+@-]/.test(text))text="'"+text;return'"'+text.replaceAll('"','""')+'"';};
export const databaseSnapshotResources=Object.freeze(Object.fromEntries(Object.entries(resources).map(([key,{label,path}])=>[key,{label,path}])));
export function databaseSnapshotCsv(resource,rows){
 const spec=resources[resource];if(!spec)throw new Error('Unsupported database snapshot export.');
 return'\uFEFF'+[spec.columns.map(([,label])=>label),...rows.map(row=>spec.columns.map(([key])=>row[key]))].map(row=>row.map(csvValue).join(',')).join('\r\n');
}
function validatePage(resource,response,offset){
 const spec=resources[resource];
 if(!spec||!response||!['ready','empty'].includes(response.state)||!Array.isArray(response.data)||!Number.isInteger(response.total)||response.total<0||response.offset!==offset||!Number.isInteger(response.limit)||response.limit<1||!response.metadata||response.metadata.resource!==resource)
  throw new Error('Database snapshot response could not be verified.');
 const expected=Math.min(pageSize,Math.max(response.total-offset,0));
 if(response.data.length!==expected||(response.state==='empty'&&response.total!==0&&offset<response.total))
  throw new Error('Database snapshot page is incomplete; refresh before interpreting or exporting.');
 for(const row of response.data)if(!row||typeof row!=='object'||Array.isArray(row)||spec.columns.some(([key])=>!Object.hasOwn(row,key)))
  throw new Error('Database snapshot record is missing required fields.');
 if(resource==='naloxone_activity'&&response.data.some(row=>!['nhs_board','national','unknown'].includes(row.geography_class)||!row.geography_id||!row.boundary_type))
  throw new Error('Database naloxone geography is not classified by the approved registry.');
 return response;
}
export async function mountDatabaseSnapshots({root,api,onStatus=()=>{},isCurrent=()=>true}){
 let resource='naloxone_activity',offset=0,requestId=0,disposed=false,previousTotal=null,previousSourceHash=null,last=null;
 const live=()=>!disposed&&isCurrent();
 root.replaceChildren();root.setAttribute('aria-label','Live database snapshots');
 root.append(el('p','LIVE DATABASE · VERSIONED SEPARATELY FROM FROZEN RESEARCH','eyebrow'));
 root.append(el('h3','Approved live database snapshots'));
 root.append(el('p','These read-only pages show selected live Supabase tables through explicit API allowlists. They do not update or replace frozen analytical artifacts. Empty, unavailable and missing values are distinct from zero.'));
 const controls=el('div',null,'filter-panel database-snapshot-controls');
 const label=el('label','Database resource'),select=el('select');select.id='database-resource';
 for(const[id,spec]of Object.entries(resources))select.add(new Option(spec.label,id));
 label.append(select);controls.append(label);root.append(controls);
 const note=el('p',resources[resource].note);note.id='database-snapshot-note';root.append(note);
 const provenance=el('div');provenance.id='database-snapshot-provenance';root.append(provenance);
 const status=el('p');status.id='database-snapshot-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');root.append(status);
 const exportButton=el('button','Export this database page as CSV');exportButton.id='database-snapshot-export';exportButton.type='button';exportButton.disabled=true;root.append(exportButton);
 const tableRoot=el('div');tableRoot.id='database-snapshot-table';root.append(tableRoot);
 const pager=el('div',null,'page-controls'),previous=el('button','Previous database page'),pageLabel=el('span',''),next=el('button','Next database page'),retry=el('button','Retry database request');pageLabel.id='database-snapshot-page-count';previous.type=next.type=retry.type='button';retry.hidden=true;pager.append(previous,pageLabel,next,retry);root.append(pager);
 function setStatus(state,message){if(!live())return;status.dataset.state=state;status.textContent=message;onStatus(state,message);}
 function downloadCsv(){
  if(!last||!last.data.length)return;
  const blob=new Blob([databaseSnapshotCsv(resource,last.data)],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),anchor=el('a');
  anchor.href=url;anchor.download=`${resource}-database-page-${Math.floor(offset/pageSize)+1}.csv`;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 function renderTable(spec,rows){
  tableRoot.replaceChildren();
  if(!rows.length){tableRoot.append(el('p','No records are visible in this database page. This is not evidence that the underlying source has no observations.'));return;}
  const scroll=el('div',null,'table-scroll');scroll.tabIndex=0;
  const table=el('table');table.setAttribute('aria-label',spec.label);table.append(el('caption',`Database page ${Math.floor(offset/pageSize)+1}; missing values are shown explicitly and zeros are preserved.`));
  const head=el('thead'),header=el('tr');
  for(const[,title]of spec.columns){const th=el('th',title);th.scope='col';header.append(th);}head.append(header);table.append(head);
  const body=el('tbody');
  for(const row of rows){const tr=el('tr');for(const[key]of spec.columns){const td=el('td'),value=row[key];
   if(key==='source_url'&&typeof value==='string'&&value){try{const url=new URL(value);if(url.protocol==='https:'){const link=el('a',value);link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';td.append(link);}else td.textContent=value;}catch{td.textContent=value;}}
   else td.textContent=value===null||value===undefined?'Missing / unavailable':String(value);
   tr.append(td);}body.append(tr);}table.append(body);scroll.append(table);tableRoot.append(scroll);
 }
 async function load(){
  const current=++requestId,spec=resources[resource];last=null;tableRoot.replaceChildren();provenance.replaceChildren();exportButton.disabled=true;retry.hidden=true;
  previous.disabled=next.disabled=true;pageLabel.textContent='';note.textContent=spec.note;
  setStatus('loading',`Loading ${spec.label.toLowerCase()}…`);
  try{
   const response=validatePage(resource,await api(spec.path,{offset,limit:pageSize}),offset);
   if(!live()||current!==requestId)return;
   if(previousTotal!==null&&(previousTotal!==response.total||previousSourceHash!==response.metadata.source_sha256))
    throw new Error('Database rows or source version changed during paging; refresh the resource before continuing.');
   previousTotal=response.total;previousSourceHash=response.metadata.source_sha256??null;last=response;
   renderTable(spec,response.data);
   const version=el('p',`Live database contract ${response.metadata.database_contract_version??'unversioned'} · ${response.total} visible rows · page ${Math.floor(offset/pageSize)+1} of ${Math.max(1,Math.ceil(response.total/pageSize))}.`);
   provenance.append(version);
   for(const[key,title]of [['source_dataset','Source dataset'],['source_id','Source ID'],['source_sha256','Source SHA-256'],['source_url','Source URL']]){
    const value=response.metadata[key];if(value===undefined||value===null)continue;
    const p=el('p',`${title}: `);if(key==='source_url'&&typeof value==='string'){try{const url=new URL(value);if(url.protocol==='https:'){const link=el('a',value);link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';p.append(link);}else p.append(document.createTextNode(value));}catch{p.append(document.createTextNode(value));}}else p.append(document.createTextNode(String(value)));provenance.append(p);
   }
   exportButton.disabled=!response.data.length;previous.disabled=offset===0;next.disabled=offset+response.data.length>=response.total;
   pageLabel.textContent=`${response.total?offset+1:0}–${Math.min(offset+response.data.length,response.total)} of ${response.total}`;
   setStatus(response.state,response.state==='empty'?response.message||'No accessible rows were returned.':`${response.data.length} live database records loaded. Export includes this page only.`);
  }catch(error){if(!live()||current!==requestId)return;last=null;renderTable(spec,[]);setStatus('error',error.message||'Live database snapshot unavailable.');retry.hidden=false;}
 }
 select.onchange=()=>{resource=select.value;offset=0;previousTotal=null;previousSourceHash=null;load();};
 previous.onclick=()=>{offset=Math.max(0,offset-pageSize);load();};
 next.onclick=()=>{offset+=pageSize;load();};
 retry.onclick=load;exportButton.onclick=downloadCsv;
 await load();
 return()=>{disposed=true;requestId++;};
}
