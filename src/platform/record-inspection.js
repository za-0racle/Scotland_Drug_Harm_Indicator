import {headings,label} from './presentation.js';
const fieldNames={source_id:'Source identifier',source_sha256:'Source checksum',artifact_sha256:'Research output checksum',source_path:'Research file',configuration_id:'Configuration identifier',result_id:'Result identifier',observation_id:'Observation identifier',lower80:'80% lower bound',upper80:'80% upper bound'};
const text=value=>value==null?'Unavailable':typeof value==='boolean'?(value?'Yes':'No'):String(value);
// Values are always text nodes. Nested records are built only when requested,
// so complete provenance remains inspectable without serialising it into prose.
export function recordView(value){
 const root=document.createElement('div');root.className='record-inspection';
 if(value===null||typeof value!=='object'){root.textContent=text(value);return root;}
 const list=document.createElement('dl');list.className='record-list';
 for(const [key,item]of Object.entries(value)){
  const term=document.createElement('dt');term.textContent=Array.isArray(value)?`Entry ${Number(key)+1}`:fieldNames[key]??headings[key]??label(key);
  const description=document.createElement('dd');
  if(item!==null&&typeof item==='object'){
   const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent=Array.isArray(item)?`${item.length} entries`:'Inspect supporting record';details.append(summary);
   details.addEventListener('toggle',()=>{if(details.open&&!details.dataset.rendered){details.dataset.rendered='true';details.append(recordView(item));}});description.append(details);
  }else description.textContent=text(item);
  list.append(term,description);
 }
 root.append(list);return root;
}
