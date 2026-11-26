import {test,expect} from '@playwright/test';

test('forecast page generates filter-specific numerical estimates and exports them',async({page})=>{
 test.setTimeout(240000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto('/#forecasting');
 await expect(page.getByRole('heading',{name:'Quarterly forecast estimates'})).toBeVisible({timeout:120000});
 await expect(page.locator('#api-status')).toContainText('Forecast for 2028 Q4 generated at a 12-quarter horizon');
 const form=page.locator('.forecast-filters');
 await expect(form.getByLabel('Geographical area')).toHaveValue('Scotland');
 await expect(form.getByLabel('Year')).toHaveValue('2028');
 await expect(form.getByLabel('Quarter')).toHaveValue('4');
 await expect(form.getByLabel('Substance category')).toHaveValue('all');
 await expect(page.locator('.forecast-output tbody tr')).toHaveCount(1);
 await expect(page.locator('.forecast-output tbody tr').first()).toContainText('2028 Q4');
 await expect(page.locator('.forecast-output thead')).toContainText('95% upper');
 await expect(page.locator('.forecast-chart-panel canvas')).toBeVisible();
 await expect(page.locator('.forecast-summary')).toContainText('Scotland');

 await form.getByLabel('Geographical area').selectOption({label:'Greater Glasgow'});
 await form.getByLabel('Year').selectOption('2026');
 await form.getByLabel('Quarter').selectOption('4');
 await form.getByLabel('Forecast model').selectOption('naive');
 await form.getByRole('button',{name:'Apply forecast'}).click();
 await expect(page.locator('#api-status')).toContainText('Forecast for 2026 Q4 generated at a 4-quarter horizon',{timeout:120000});
 await expect(page.locator('.forecast-summary')).toContainText('Greater Glasgow');
 await expect(page.locator('.forecast-output tbody tr')).toHaveCount(1);
 await expect(page.locator('.forecast-output tbody tr').last()).toContainText('2026 Q4');
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export forecasts CSV'}).click();
 expect((await download).suggestedFilename()).toBe('sdhi-quarterly-forecasts.csv');
 expect(errors).toEqual([]);
});
