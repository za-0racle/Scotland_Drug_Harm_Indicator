import {mkdir} from 'node:fs/promises';
import {test,expect} from '@playwright/test';
import {openSupporting} from './supporting-evidence.js';

const screens=[['overview','#plot-panel'],['comparison','#studio-results > .chart-panel'],['trends','#mortality-trend'],['substance','#substance-trend'],['geography','#geo-trend']];
for(const [route,selector] of screens)test(`Phase 2 ${route}: lead evidence, supporting views and desktop/mobile captures`,async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/#'+route);
 if(route==='comparison'){
  await expect(page.locator('#studio-apply')).toBeEnabled();await page.locator('#studio-apply').click();await expect(page.locator('#studio-status')).toHaveAttribute('data-state','ready');
 }else await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const lead=page.locator(selector).first();await expect(lead.locator('canvas')).toBeVisible();
 if(route==='overview'){
  await expect(page.locator('#summary-grid article')).toHaveCount(2);
  await expect(page.locator('#overview-heatmap').locator('..')).not.toHaveAttribute('open');
  await page.locator('#overview-from-year').selectOption('2024');await expect(page.locator('#data-panel tbody tr')).toHaveCount(8);
  await expect(page.locator('#summary-grid')).toContainText('2025 Q4');await expect(lead).toContainText('not the selected chart years');
 }
 if(route==='trends'){
  await expect(page.locator('#mortality-distribution').locator('..')).not.toHaveAttribute('open');
  await openSupporting(page,'#mortality-heatmap');await expect(page.locator('#mortality-heatmap table')).toBeVisible();
 }
 if(route==='substance'){
  await expect(page.locator('#substance-source option')).toHaveCount(3);
  await page.locator('#substance-source').selectOption('assist');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
  await expect(lead).toContainText('unequal study windows');await expect(lead.locator('[data-chart-note]')).toContainText('Points only');
  await page.locator('#substance-source').selectOption('forensic');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 }
 if(route==='geography'){
  await expect(page.locator('#geo-published')).toContainText('35.6');await expect(page.locator('#geo-published')).toContainText('22.5');
  expect(await page.locator('#geo-published').evaluate(n=>!!(n.compareDocumentPosition(document.querySelector('#geo-history'))&Node.DOCUMENT_POSITION_FOLLOWING))).toBeTruthy();
 }
 await mkdir('docs/images/task08s-phase2',{recursive:true});
 for(const [size,width] of [['desktop',1440],['mobile',390]]){
  await page.setViewportSize({width,height:1000});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  // Full-page capture includes filters, lead analytical evidence and exact-value support.
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:`docs/images/task08s-phase2/${route}-${size}.png`,fullPage:true,animations:'disabled'});
 }
 expect(errors).toEqual([]);
});
