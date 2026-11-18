import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
const folder='test-results/task08s-phase5';
const routes=['overview','comparison','trends','substance','geography','anomalies','forecasting','reports'];
for(const route of routes)test(`Phase 5 ${route}: clean content, real evidence and desktop/mobile acceptance`,async({page})=>{
 test.setTimeout(240000);const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await mkdir(folder,{recursive:true});await page.goto('/#'+route);
 if(route==='comparison'){await expect(page.locator('#studio-apply')).toBeEnabled();await page.locator('#studio-apply').click();}
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('main pre,main code')).toHaveCount(0);
 expect(await page.locator('main').innerText()).not.toMatch(/"(?:source_path|artifact_sha256|configuration_id)"\s*:/);
 if(route==='overview'){
  await expect(page.locator('#page-introduction')).toContainText('To develop a data analytics system');
  await expect(page.locator('#summary-grid')).toContainText('1,146');
  await expect(page.locator('#overview-content .record-inspection')).toHaveCount(0);
  await expect(page.locator('#overview-content')).not.toContainText('Complete provenance and record metadata');
 }
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.waitForTimeout(500);await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  if(width===1440){await expect(page.locator('#navigation-toggle')).toBeHidden();await expect(page.locator('#app-sidebar')).toBeVisible();}
  else await expect(page.locator('#navigation-toggle')).toBeVisible();
  await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});await page.screenshot({path:`${folder}/${route}-${width===1440?'desktop':'mobile'}.png`,fullPage:true});
 }
 if(route==='anomalies'){
  await page.locator('#data-panel tbody tr').first().press('Enter');await expect(page.locator('#verification')).toHaveAttribute('open');await expect(page.locator('#readable-record .record-inspection')).toBeVisible();await expect(page.locator('#readable-record')).toContainText('Configuration identifier');await page.screenshot({path:`${folder}/monitoring-inspection-mobile.png`,fullPage:true});await page.locator('#close-verification').click();
 }
 if(route==='reports'){
  await page.locator('#research-findings > details > summary').click();await expect(page.locator('#research-findings .record-inspection')).toBeVisible();await expect(page.locator('main pre')).toHaveCount(0);await page.screenshot({path:`${folder}/research-inspection-mobile.png`,fullPage:true});
 }
 expect(errors).toEqual([]);
});

test('navigation modes agree at the breakpoint, preserve focus and have no page overflow',async({page})=>{
 await mkdir(folder,{recursive:true});await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 for(const width of [320,390,768,900,901,1024,1440]){
  await page.setViewportSize({width,height:900});const menu=page.locator('#navigation-toggle');
  await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  if(width<=900){await expect(menu).toBeVisible();await menu.click();await expect(page.locator('#platform-nav [aria-current]')).toBeFocused();await page.keyboard.press('Escape');await expect(menu).toBeFocused();}
  else{await expect(menu).toBeHidden();await expect(page.locator('#app-sidebar')).not.toHaveAttribute('inert');}
 }
 await page.setViewportSize({width:900,height:900});await page.locator('#navigation-toggle').click();await page.setViewportSize({width:901,height:900});await expect(page.locator('#navigation-toggle')).toBeHidden();await expect(page.locator('#platform-nav [aria-current]')).toBeFocused();await expect(page.locator('#workspace')).not.toHaveAttribute('inert');
 await page.setViewportSize({width:390,height:900});await page.locator('#navigation-toggle').click();await page.screenshot({path:`${folder}/navigation-mobile-open.png`,fullPage:true});await page.keyboard.press('Escape');
});

test('structured inspection preserves exact values and escapes code-like input without execution',async({page})=>{
 await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const result=await page.evaluate(async()=>{
  const {recordView}=await import('/src/platform/record-inspection.js');const node=recordView({observed_value:0,missing:null,signal_flag:false,nested:{precision:160.0359197607262,unsafe:'<img src=x onerror="window.unintendedCode=true">'}});node.id='test-only-record';document.querySelector('main').append(node);return node.textContent;
 });
 expect(result).toContain('0');expect(result).toContain('Unavailable');expect(result).toContain('No');await page.locator('#test-only-record summary').click();await expect(page.locator('#test-only-record')).toContainText('160.0359197607262');await expect(page.locator('#test-only-record')).toContainText('<img');await expect(page.locator('#test-only-record img')).toHaveCount(0);expect(await page.evaluate(()=>window.unintendedCode)).toBeUndefined();await page.locator('#test-only-record').evaluate(n=>n.remove());
});
