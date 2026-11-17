// Reuse existing analytical sections without changing their records or exports.
export function disclose(section,title){
 const details=document.createElement('details');details.className='supporting-analysis';
 const summary=document.createElement('summary');summary.textContent=title??section.querySelector('h3')?.textContent??'Supporting evidence';
 section.before(details);details.append(summary,section);
 const heading=section.querySelector('h3');if(heading)heading.hidden=true;
 return details;
}
export function explanation(panel,text){
 const node=document.createElement('p');node.className='evidence-explanation';node.textContent=text;panel.append(node);return node;
}
export const unitTitle=unit=>({detection_count:'Detections (count)',percent:'Reported percentage (%)',incident_count:'Naloxone activity (incident count)',count:'Deaths (count)',deaths:'Deaths (count)'}[unit]??unit);
