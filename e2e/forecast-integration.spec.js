import {test,expect} from '@playwright/test';

test('forecast page generates filter-specific numerical estimates and exports them',async({page})=>{
 test.setTimeout(240000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto('/#forecasting');
 await expect(page.locator('.forecast-output tbody tr')).toHaveCount(1,{timeout:120000});
 await expect(page.locator('#api-status')).toContainText('1 forecast generated');
 const form=page.locator('.forecast-filters');
 await expect(form.getByLabel('Geographical area')).toHaveValue('Scotland');
 await expect(form.locator('.forecast-multi-field').nth(0).locator('input:checked')).toHaveValue('all');
 await expect(form.locator('.forecast-multi-field').nth(1).locator('input:checked')).toHaveValue('2028');
 await expect(form.locator('.forecast-multi-field').nth(2).locator('input:checked')).toHaveValue('4');
 await expect(page.locator('.forecast-output tbody tr')).toHaveCount(1);
 await expect(page.locator('.forecast-output tbody tr').first()).toContainText('2028 Q4');
 await expect(page.locator('.forecast-output thead')).toContainText('95% upper');
 await expect(page.locator('.forecast-chart-group canvas')).toBeVisible();
 await expect(page.locator('.forecast-output tbody')).toContainText('Scotland');

 await form.getByLabel('Geographical area').selectOption({label:'Greater Glasgow'});
 const categories=form.locator('.forecast-multi-field').nth(0),years=form.locator('.forecast-multi-field').nth(1),quarters=form.locator('.forecast-multi-field').nth(2);
 await categories.locator('summary').click();await categories.locator('input[value="Opioids"]').check();await categories.getByRole('button',{name:'Done'}).click();
 await years.locator('summary').click();await years.locator('input[value="2027"]').check();await years.getByRole('button',{name:'Done'}).click();
 await quarters.locator('summary').click();await quarters.locator('input[value="3"]').check();await quarters.getByRole('button',{name:'Done'}).click();
 await form.getByLabel('Forecast model').selectOption('naive');
 await form.getByRole('button',{name:'Apply forecast'}).click();
 await expect(page.locator('#api-status')).toContainText('8 forecasts generated',{timeout:120000});
 await expect(page.locator('.forecast-output tbody')).toContainText('Greater Glasgow');
 await expect(page.locator('.forecast-output tbody tr')).toHaveCount(8);
 await expect(page.locator('.forecast-output tbody')).toContainText('2027 Q3');
 await expect(page.locator('.forecast-output tbody')).toContainText('2028 Q4');
 await expect(page.locator('.forecast-chart-group')).toHaveCount(2);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export forecasts CSV'}).click();
 expect((await download).suggestedFilename()).toBe('sdhi-quarterly-forecasts.csv');
 expect(errors).toEqual([]);
});
