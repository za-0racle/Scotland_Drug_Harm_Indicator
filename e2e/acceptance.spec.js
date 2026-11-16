import {mkdir,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {test,expect} from '@playwright/test';

test('all eight sections, keyboard access and no direct database requests',async({page})=>{
 test.setTimeout(300000);
 const bypass=[],browserErrors=[];page.on('request',r=>{if(r.url().includes('.supabase.co'))bypass.push(r.url());});
 page.on('pageerror',error=>browserErrors.push(error.message));
 page.on('console',message=>{if(message.type()==='error')browserErrors.push(message.text());});
 await page.goto('/');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:'Skip to analysis'})).toBeFocused();
 const screenshots='test-results/final-screenshots';
 await mkdir(screenshots,{recursive:true});
 const screens=[
  ['overview','Intelligence Overview'],
  ['comparison','Comparison Studio'],
  ['trends','Mortality Analytics'],
  ['substance','Substance Intelligence'],
  ['geography','Geographic Explorer'],
  ['anomalies','Anomaly Detection & Surveillance Signals'],
  ['forecasting','Forecasting Lab'],
  ['reports','Research, Data & Exports'],
 ];
 const terminalState=/^(ready|empty|unavailable)$/;
 for(const[index,[id,title]]of screens.entries()){
   if(index)await page.locator(`[data-page="${id}"]`).click();
   await expect(page.locator('#page-title')).toHaveText(title);
   await expect(page.locator('#api-status')).toHaveAttribute('data-state',terminalState,{timeout:60000});
   await page.screenshot({path:join(screenshots,`${id}.png`),fullPage:true,animations:'disabled'});
 }
 expect(bypass).toEqual([]);expect(browserErrors).toEqual([]);
 await page.getByRole('button',{name:'Source-quality gaps'}).click();
 await expect(page.locator('#api-status')).toContainText('10 records in this view');
 await page.locator('[data-page="methodology"]').click();await page.getByRole('button',{name:'Source inventory',exact:true}).click();
 await expect(page.locator('#api-status')).toContainText('6 records in this view');
});

test('same-boundary comparison retains two areas and bounded pagination',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.locator('#boundary').selectOption('health_board');
 const options=await page.locator('#area option').evaluateAll(items=>items.map(i=>i.value).filter(Boolean));
 await page.locator('#area').selectOption(options[0]);
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.getByRole('button',{name:'Compare areas',exact:true}).click();
 await page.locator('#more-filters').evaluate(n=>n.open=true);
 await page.locator('#compare').selectOption(options[1]);
 await page.getByRole('button',{name:'Compare areas',exact:true}).click();
 await expect(page.locator('#api-status')).toContainText('878 records in this view');
 await expect(page.locator('#next-page')).toBeEnabled();
 await expect(page.locator('#data-panel tbody tr')).toHaveCount(100);
 const first=await page.locator('#data-panel tbody').textContent();await page.locator('#next-page').click();
 await expect(page.locator('#page-count')).toContainText('101');
 expect(await page.locator('#data-panel tbody').textContent()).not.toBe(first);
});

test('Inverclyde exports match selected scope and dates; failure clears stale export',async({page})=>{
 await page.goto('/#geography');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.locator('#geo-from').selectOption('2020');await expect(page.locator('#api-status')).toContainText('5 selected-area records');
 const pending=page.waitForEvent('download');await page.getByRole('button',{name:'Export area history JSON',exact:true}).click();const exported=JSON.parse(await readFile(await (await pending).path(),'utf8'));
 expect(exported.data.length).toBe(5);expect(exported.data.every(r=>r.geography==='Inverclyde'&&r.year>=2020)).toBeTruthy();expect(exported.metadata.export_scope).toContain('Complete eligible');
 await page.route('**/api/v1/mortality/annual?**',route=>route.abort());await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');await expect(page.getByRole('button',{name:'Export area history JSON',exact:true})).toHaveCount(0);
});

test('empty, malformed, unavailable and slow transport responses have explicit states',async({page})=>{
 await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 for(const body of [{state:'empty',kind:'research_result',data:[],total:0,metadata:{},message:'No accessible research records'}, {bad:'TEST ONLY'}, {state:'unavailable',kind:'unavailable_evidence',data:[],total:0,metadata:{},message:'Verified source unavailable'}]){
   await page.route('**/api/v1/forecasting/results?**',async route=>{await new Promise(resolve=>setTimeout(resolve,500));await route.fulfill({json:body});});
   await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','loading');
   await expect(page.locator('#api-status')).toHaveAttribute('data-state',body.state??'error');
   await expect(page.locator('#data-panel tbody tr')).toHaveCount(0);
   await page.unroute('**/api/v1/forecasting/results?**');
 }
});

test('Supabase outage is visible independently of available research artifacts',async({page})=>{
 await page.route('**/api/v1/overview?**',async route=>{
   const response=await route.fetch();const body=await response.json();
   body.data[0].database={state:'error',total:0,data:[],message:'TEST ONLY: approved database unavailable'};
   await route.fulfill({response,json:body});
 });
 await page.goto('/');await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');
 await expect(page.locator('#summary-grid article').first()).toContainText('Unavailable');
 await expect(page.locator('#api-status')).toContainText('approved database unavailable');await expect(page.locator('#overview-heatmap')).toContainText('Quarterly mortality observations are unavailable');
 await expect(page.locator('#data-panel tbody tr')).toHaveCount(0);
});

test('live database snapshots are paged, classified and remain separate from frozen reports',async({page})=>{
 const browserErrors=[];page.on('pageerror',error=>browserErrors.push(error.message));
 await page.goto('/#reports');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.getByRole('button',{name:'Live database snapshots'}).click();
 await expect(page.locator('#database-snapshot-status')).toHaveAttribute('data-state','ready',{timeout:60000});
 await expect(page.locator('#database-snapshot-status')).toContainText('Export includes this page only');
 await expect(page.locator('#database-snapshot-table tbody tr')).toHaveCount(100);
 await expect(page.locator('#database-snapshot-table')).toContainText('National Aggregate — Scotland');
 await expect(page.locator('#database-snapshot-table')).toContainText('Unknown');
 await expect(page.locator('#database-snapshot-note')).toContainText('separate from the frozen Phase 4');
 const firstPage=await page.locator('#database-snapshot-table tbody').textContent();
 await page.getByRole('button',{name:'Next database page'}).click();
 await expect(page.locator('#database-snapshot-status')).toContainText('100 live database records loaded');
 expect(await page.locator('#database-snapshot-table tbody').textContent()).not.toBe(firstPage);
 await expect(page.locator('#database-snapshot-page-count')).toHaveText('101–200 of 7024');

 const download=page.waitForEvent('download');
 await page.getByRole('button',{name:'Export this database page as CSV'}).click();
 const csv=await readFile(await (await download).path(),'utf8');
 expect(csv).toContain('Source-reported moving average');

 await page.locator('#database-resource').selectOption('geographic_areas');
 await expect(page.locator('#database-snapshot-table tbody tr')).toHaveCount(18);
 await expect(page.locator('#database-snapshot-table')).toContainText('nhs_board');
 await page.locator('#database-resource').selectOption('data_sources');
 await expect(page.locator('#database-snapshot-table tbody tr')).toHaveCount(18);
 await expect(page.locator('#database-snapshot-table')).toContainText('Source SHA-256');

 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 expect(browserErrors).toEqual([]);
});

test('browser history during backend bootstrap does not use uninitialized filters',async({page})=>{
 let releaseGeographies,markRequestStarted;
 const pending=new Promise(resolve=>{releaseGeographies=resolve;});
 const requestStarted=new Promise(resolve=>{markRequestStarted=resolve;});
 await page.route('**/api/v1/geographies*',async route=>{
  markRequestStarted();
  await pending;
  await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({
   state:'error',kind:'unavailable_evidence',data:[],total:0,metadata:{},message:'TEST ONLY: geographic registry unavailable',
  })});
 });
 await page.goto('/#overview');
 await requestStarted;
 await expect(page.locator('#api-status')).toHaveText('Connecting to research backend...');
 await page.locator('[data-page="comparison"]').click();
 await expect(page.locator('#page-title')).toHaveText('Comparison Studio');
 await page.goBack();
 await expect(page.locator('#page-title')).toHaveText('Intelligence Overview');
 await expect(page.locator('#api-status')).toHaveText('Connecting to research backend...');
 releaseGeographies();
 await expect(page.locator('#api-status')).toContainText('TEST ONLY: geographic registry unavailable');
});
