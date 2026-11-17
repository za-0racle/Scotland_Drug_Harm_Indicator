import {test,expect} from '@playwright/test';
import {mkdir} from 'node:fs/promises';

test('monitoring retains original records, separate components, settings and historical screens',async({page})=>{
 await page.goto('/#anomalies');await page.getByRole('button',{name:'Statistical flags',exact:true}).click();await expect(page.locator('#api-status')).toContainText('47 records');
 await page.getByRole('button',{name:'Original monitoring results',exact:true}).click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#data-panel')).toContainText('Positive CUSUM component');
 await expect(page.locator('#data-panel')).toContainText('Negative CUSUM component');
 await expect(page.locator('#data-panel tbody tr')).not.toHaveCount(0);await page.locator('#original-configuration').selectOption({index:1});await expect(page.locator('#data-panel tbody tr')).not.toHaveCount(0);await page.locator('#original-configuration').selectOption('');
 await expect(page.locator('#plot-panel')).toBeHidden();
 await page.locator('#data-panel tbody tr').first().press('Enter');await expect(page.locator('#verification')).toHaveAttribute('open');await page.locator('#close-verification').click();
 await page.getByRole('button',{name:'Original method settings',exact:true}).click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#data-panel')).toContainText('Rolling window quarters');
 await page.getByRole('button',{name:'Six-setting sensitivity',exact:true}).click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#feature-panel')).toContainText('not sensitivity for detecting');await expect(page.locator('#export-csv')).toHaveAttribute('href',/sensitivity/);
 await page.goto('/#signals');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#data-panel thead')).toContainText('Direction');
 await page.getByRole('button',{name:'External validation',exact:true}).click();await expect(page.locator('#data-panel')).toContainText('pending');
});

test('evaluation leads, saved values remain exact and analytical layouts fit desktop and mobile',async({page})=>{
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await mkdir('docs/images/task08s-phase3',{recursive:true});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
  await expect(page.locator('#data-panel tbody tr')).toHaveCount(4);
  for(const score of ['21.58','25.26','32.17','25.99'])await expect(page.locator('#data-panel')).toContainText(score);
  await expect(page.locator('#feature-panel')).toContainText('not an independent test');
  await expect(page.locator('#saved-projection')).toContainText('248 deaths');
  expect(await page.locator('#data-panel').evaluate(n=>Boolean(n.compareDocumentPosition(document.querySelector('#saved-projection'))&Node.DOCUMENT_POSITION_FOLLOWING))).toBeTruthy();
  await expect(page.locator('#export-csv')).toHaveAttribute('href',/forecast_models/);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
  await page.screenshot({path:`docs/images/task08s-phase3/forecast-${width===1440?'desktop':'mobile'}.png`,fullPage:true});
  await page.goto('/#anomalies');await page.getByRole('button',{name:'Statistical flags',exact:true}).click();await expect(page.locator('#api-status')).toContainText('47 records');
  await page.getByRole('button',{name:'Original monitoring results',exact:true}).click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
  await page.screenshot({path:`docs/images/task08s-phase3/monitoring-${width===1440?'desktop':'mobile'}.png`,fullPage:true});
 }
 expect(errors).toEqual([]);
});
