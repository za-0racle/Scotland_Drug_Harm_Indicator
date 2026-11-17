import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';

test('rolling-origin chart uses verified target quarters, four models and saved intervals',async({page})=>{
 test.setTimeout(240000);
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const responsePromise=page.waitForResponse(r=>r.url().includes('/forecasting/backtest?')&&r.status()===200);
 await page.getByRole('button',{name:'Rolling-origin predictions',exact:true}).click();
 const payload=await (await responsePromise).json();expect(payload.data).toHaveLength(48);
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#chart-context')).toContainText('2023 Q1 to 2025 Q4');
 await expect(page.locator('#plot-panel [data-chart-note]')).not.toContainText('unavailable');
 await expect(page.locator('#plot-panel [data-chart-legend] button')).toHaveCount(4);
 for(const model of ['Last-observation baseline','Same-quarter seasonal baseline','Simple exponential smoothing','Negative binomial trend'])await expect(page.locator('#plot-panel [data-chart-legend]')).toContainText(model);
 await expect(page.locator('#research-chart')).toBeVisible();
 expect(await page.locator('#research-chart').evaluate(c=>Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data).some((v,i)=>i%4===3&&v>0))).toBeTruthy();
 const prepared=await page.evaluate(async rows=>(await import('/src/platform/chart-data.js')).prepareChart(rows),payload.data);
 expect(prepared.labels).toEqual(Array.from({length:12},(_,i)=>`${2023+Math.floor(i/4)} Q${i%4+1}`));
 expect(prepared.datasets).toHaveLength(4);
 for(const series of prepared.datasets)for(const point of series.points){
  const original=payload.data.find(r=>r.model===series.metadata.model&&r.target===point.period);
  expect(point.value).toBe(original.predicted);
  for(const field of ['origin','target','lower80','upper80','lower95','upper95'])expect(point.record[field]).toBe(original[field]);
 }
 await expect(page.locator('#data-panel thead')).toContainText('Target quarter');
 for(const name of ['80% lower bound','80% upper bound','95% lower bound','95% upper bound'])await expect(page.locator('#data-panel thead')).toContainText(name);
 await expect(page.locator('#data-panel tbody tr')).toHaveCount(48);
 const first=payload.data[0];await expect(page.locator('#data-panel tbody tr').first()).toContainText(String(first.lower80));
 await expect(page.locator('#feature-panel')).toContainText('Historical observations and rolling-origin predictions');
 await expect(page.locator('#export-json')).toHaveAttribute('href',/resource=backtest/);
 await mkdir('docs/images/task08s-phase5-forecast-fix',{recursive:true});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.screenshot({path:`docs/images/task08s-phase5-forecast-fix/backtest-${width}.png`,fullPage:true});
 }
 expect(errors).toEqual([]);
});
