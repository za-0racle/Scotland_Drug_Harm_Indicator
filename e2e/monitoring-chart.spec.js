import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
test('approved S08 charts preserve each configuration, quarters, components and stored flags',async({page,request})=>{
 test.setTimeout(240000);
 const configurations=(await(await request.get('/api/v1/monitoring/configurations?limit=100')).json()).data;
 const rows=(await(await request.get('/api/v1/monitoring/results?limit=100')).json()).data;
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/#anomalies');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#plot-panel')).toBeHidden();
 for(const configuration of configurations){
  await page.locator('#original-configuration').selectOption(String(configuration.configuration_id));
  await expect(page.locator('#plot-panel')).toBeVisible();
  const expected=rows.filter(r=>r.configuration_id===configuration.configuration_id);
  await expect(page.locator('#data-panel tbody tr')).toHaveCount(expected.length);
  const prepared=await page.evaluate(async({rows,configuration})=>(await import('/src/platform/monitoring-chart.js')).prepareMonitoring(rows,configuration),{rows,configuration});
  for(const series of prepared.datasets)for(const point of series.points){
   if(!point.record){expect(point.value).toBeNull();continue;}
   expect(point.value).toBe(point.record[series.key]??null);
  }
  await expect(page.locator('#plot-panel [data-chart-legend] button')).toHaveCount(3);
  await expect(page.locator('#chart-context')).toContainText(configuration.configuration_label);
  await expect(page.locator('#plot-panel [data-chart-note]')).toContainText('current API page only');
  expect(await page.locator('#research-chart').evaluate(c=>Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data).some((v,i)=>i%4===3&&v>0))).toBeTruthy();
  if(configuration.method==='CUSUM'){
   await expect(page.locator('#plot-panel')).toContainText('Positive CUSUM component');
   await expect(page.locator('#plot-panel')).toContainText('Negative CUSUM component');
   await expect(page.locator('#plot-panel')).not.toContainText('Stored lower limit');
  }
  await mkdir('test-results/task08s-s08',{recursive:true});
  for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:`test-results/task08s-s08/config-${configuration.configuration_id}-${width}.png`,fullPage:true,animations:'disabled'});}
 }
 await page.locator('#original-configuration').selectOption('');await expect(page.locator('#plot-panel')).toBeHidden();
 await page.route('**/api/v1/monitoring/results?**',route=>route.fulfill({status:503,json:{message:'TEST ONLY'}}));
 await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');await expect(page.locator('#plot-panel')).toBeHidden();
 await page.unroute('**/api/v1/monitoring/results?**');await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 expect(errors).toEqual([]);
});
