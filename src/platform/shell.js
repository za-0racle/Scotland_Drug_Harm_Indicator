export const screens=[
 ['overview','Intelligence Overview','overview'],
 ['comparison','Comparison Studio','compare'],
 ['trends','Mortality Analytics','mortality'],
 ['substance','Substance Intelligence','substance'],
 ['geography','Geographic Explorer','geography'],
 ['anomalies','Anomaly Detection & Surveillance Signals','signals'],
 ['forecasting','Forecasting Lab','forecast'],
 ['reports','Research, Data & Exports','research'],
];
export const legacyRoutes={compare:{screen:'comparison',title:'Comparison Studio'},signals:{screen:'anomalies',title:'Surveillance Signals'},methodology:{screen:'reports',title:'Data & Methodology'},exploration:{screen:'trends',title:'Source Trends & Patterns'}};
export const isRoute=id=>screens.some(([key])=>key===id)||Object.hasOwn(legacyRoutes,id);
export const screenFor=id=>legacyRoutes[id]?.screen??id;
export const routeTitle=id=>legacyRoutes[id]?.title??screens.find(([key])=>key===id)?.[1]??screens[0][1];
const paths={overview:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',compare:'M4 4v16 M20 4v16 M7 8h10 M14 5l3 3-3 3 M17 16H7 M10 13l-3 3 3 3',mortality:'M3 12h4l3-8 4 16 3-8h4',substance:'M9 3h6 M10 3v6L4 19q-1 2 2 2h12q3 0 2-2L14 9V3 M8 14h8',geography:'M12 22s8-8 8-14a8 8 0 0 0-16 0c0 6 8 14 8 14 M15 8a3 3 0 1 1-6 0 3 3 0 1 1 6 0',signals:'M3 20V4 M3 20h18 M6 15l4-4 4 2 6-9',forecast:'M3 20V4 M3 20h18 M6 15l4-4 4 1 M14 12l6-7 M17 5h3v3',research:'M5 3h10l4 4v14H5z M14 3v5h5 M8 12h8 M8 16h6'};
export const icon=name=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[name]}"/></svg>`;

export function mountShell(root,navigate){
 const nav=root.querySelector('#platform-nav'),header=root.querySelector('.platform-header');
 const sidebar=document.createElement('aside');sidebar.id='app-sidebar';sidebar.className='app-sidebar';
 sidebar.innerHTML='<a class="sdhi-brand" href="#overview" aria-label="SDHI — Intelligence Overview"><span class="brand-mark">S<span>·</span></span><span class="brand-copy"><strong>SDHI</strong><small>SCOTLAND DRUG HARM<br>INTELLIGENCE PLATFORM</small></span></a><p class="sidebar-label">RESEARCH WORKSPACE</p>';
 nav.before(sidebar);sidebar.append(nav);
 const sidebarFoot=document.createElement('div');sidebarFoot.className='sidebar-foot';sidebarFoot.innerHTML='<span class="research-dot" aria-hidden="true"></span><span class="nav-label">Historical research<br><small>Evidence before inference</small></span>';sidebar.append(sidebarFoot);
 nav.replaceChildren();
 for(const[id,title,shape]of screens){const a=document.createElement('a');a.href='#'+id;a.dataset.page=id;a.setAttribute('aria-label',title);a.title=title;a.innerHTML=`${icon(shape)}<span class="nav-label">${title}</span>`;nav.append(a);}
 const toggle=document.createElement('button');toggle.id='navigation-toggle';toggle.className='icon-button';toggle.setAttribute('aria-controls','app-sidebar');toggle.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
 header.prepend(toggle);header.classList.add('top-toolbar');
 const breadcrumb=document.createElement('p');breadcrumb.id='toolbar-context';breadcrumb.className='toolbar-context';header.querySelector('div').append(breadcrumb);
 const backdrop=document.createElement('button');backdrop.id='navigation-backdrop';backdrop.tabIndex=-1;backdrop.setAttribute('aria-label','Close navigation');backdrop.hidden=true;root.append(backdrop);
 const mobile=matchMedia('(max-width: 900px)');let collapsed=false,drawer=false,priorOverflow='';
 const close=document.createElement('button');close.className='drawer-close';close.textContent='Close navigation';close.onclick=()=>closeDrawer();sidebar.prepend(close);
 function sync(){
  root.classList.toggle('sidebar-collapsed',!mobile.matches&&collapsed);root.classList.toggle('navigation-open',mobile.matches&&drawer);
  const expanded=mobile.matches?drawer:!collapsed;toggle.setAttribute('aria-expanded',String(expanded));toggle.setAttribute('aria-label',mobile.matches?(drawer?'Close navigation':'Open navigation'):(collapsed?'Expand sidebar':'Collapse sidebar'));toggle.title=toggle.getAttribute('aria-label');
  sidebar.inert=mobile.matches&&!drawer;backdrop.hidden=!mobile.matches||!drawer;
  root.querySelector('#workspace').inert=mobile.matches&&drawer;
  root.querySelector('.workspace-actions').inert=mobile.matches&&drawer;
  root.querySelector('.platform-footer').inert=mobile.matches&&drawer;
  if(mobile.matches&&drawer){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');sidebar.setAttribute('aria-label','Research navigation');}else{sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');sidebar.removeAttribute('aria-label');}
 }
 function closeDrawer(restore=true){if(!drawer)return;drawer=false;document.body.style.overflow=priorOverflow;sync();if(restore)toggle.focus();}
 toggle.onclick=()=>{if(mobile.matches){if(drawer)closeDrawer();else{drawer=true;priorOverflow=document.body.style.overflow;document.body.style.overflow='hidden';sync();nav.querySelector('[aria-current="page"]')?.focus();}}else{collapsed=!collapsed;sync();}};
 backdrop.onclick=()=>closeDrawer();mobile.addEventListener('change',()=>{closeDrawer(false);sync();});
 root.addEventListener('keydown',event=>{
  if(!mobile.matches||!drawer)return;
  if(event.key==='Escape'){event.preventDefault();closeDrawer();}
  if(event.key==='Tab'){
   const stops=[...sidebar.querySelectorAll('a[href],button:not([disabled])')],first=stops[0],last=stops.at(-1);
   if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
  }
 });
 root.addEventListener('click',event=>{const a=event.target.closest('a[href^="#"]');if(!a||!isRoute(a.hash.slice(1)))return;event.preventDefault();closeDrawer(false);navigate(a.hash.slice(1));root.querySelector('#page-title').focus();});
 const links=document.createElement('nav');links.id='section-links';links.setAttribute('aria-label','Related research views');root.querySelector('.workspace-heading').after(links);
 sync();
 return{update(page){
  breadcrumb.textContent=routeTitle(page);
  for(const a of nav.children){if(a.dataset.page===screenFor(page))a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
  links.replaceChildren();
  const related=screenFor(page)==='anomalies'?[['anomalies','Anomaly detection'],['signals','Surveillance signals']]:screenFor(page)==='reports'?[['reports','Reports & exports'],['methodology','Data & methodology']]:screenFor(page)==='trends'?[['trends','Mortality analytics'],['exploration','Other source trends']]:[];
  for(const[id,title]of related){const a=document.createElement('a');a.href='#'+id;a.dataset.page=id;a.textContent=title;if(page===id)a.setAttribute('aria-current','page');links.append(a);}
 }};
}
