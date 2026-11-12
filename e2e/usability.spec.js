import {test,expect} from '@playwright/test';
test('first-time overview explains mortality without technical records',async({page})=>{
 await page.goto('/');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#summary-grid')).toContainText('1,146');await expect(page.locator('#summary-grid')).toContainText('+7.61%');await expect(page.locator('#summary-grid')).toContainText('248');await expect(page.locator('#summary-grid')).toContainText('2025 Q4');
 await expect(page.locator('#chart-title')).toContainText('Suspected drug deaths');await expect(page.locator('#chart-context')).toContainText('Scotland');
 await expect(page.locator('pre:visible')).toHaveCount(0);await expect(page.locator('.filter-panel')).toBeHidden();await expect(page.locator('#observations-disclosure')).not.toHaveAttribute('open');
 await page.locator('#verification > summary').click();await expect(page.locator('#readable-provenance')).toContainText('Police Scotland');await expect(page.locator('pre:visible')).toHaveCount(0);
 await page.screenshot({path:'analysis/test_scratch.local/usability/after-overview.png',fullPage:true});
});
test('shared dependencies preserve valid choices, reset defaults and explain comparison',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#more-filters')).not.toHaveAttribute('open');await expect(page.locator('#model')).toBeHidden();await expect(page.locator('#category')).toBeHidden();
 await page.locator('#boundary').selectOption('police_division');await expect(page.locator('#area option')).toHaveCount(14);
 const ids=await page.locator('#area option').evaluateAll(items=>items.map(i=>i.value).filter(Boolean));await page.locator('#area').selectOption(ids[0]);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const measure=await page.locator('#indicator').inputValue();await page.locator('#area').selectOption(ids[1]);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');expect(await page.locator('#indicator').inputValue()).toBe(measure);
 await page.getByRole('button',{name:'Compare areas',exact:true}).click();await page.locator('#more-filters > summary').click();await expect(page.locator('#compare')).toBeVisible();
 expect(await page.locator('#compare option').evaluateAll(items=>items.map(i=>i.value))).not.toContain(ids[1]);
 await page.locator('#start-year').fill('2020');await page.locator('#start-year').dispatchEvent('change');
 await page.locator('#reset-filters').click();await expect(page.locator('#boundary')).toHaveValue('country');await expect(page.locator('#start-year')).toHaveValue('');await expect(page.locator('#more-filters')).not.toHaveAttribute('open');
 await page.screenshot({path:'analysis/test_scratch.local/usability/after-filters.png',fullPage:true});
});
test('advanced and verification panels close on Escape without clearing filters',async({page})=>{
 await page.goto('/#anomalies');await expect(page.locator('#api-status')).toContainText('47 records in this view');await page.locator('#more-filters > summary').click();
 await page.locator('#model').selectOption('nb2_moments');await expect(page.locator('#api-status')).toContainText('40 records in this view');await page.locator('#model').focus();await page.keyboard.press('Escape');await expect(page.locator('#more-filters')).not.toHaveAttribute('open');await expect(page.locator('#model')).toHaveValue('nb2_moments');
 await page.locator('#data-panel tbody tr').first().focus();await page.keyboard.press('Enter');await expect(page.locator('#verification')).toHaveAttribute('open');await expect(page.locator('pre:visible')).toHaveCount(0);
 await page.locator('#close-verification').click();await expect(page.locator('#verification')).not.toHaveAttribute('open');await expect(page.locator('#verification > summary')).toBeFocused();
 await page.locator('#more-filters > summary').click();await page.locator('#model').selectOption('');await page.locator('#indicator').selectOption('suspected_deaths');await expect(page.locator('#api-status')).toContainText('3 records in this view');
 const periodColumn=await page.locator('#data-panel thead th').evaluateAll(nodes=>nodes.findIndex(node=>node.textContent.toLowerCase()==='period'));
 const periods=await page.locator('#data-panel tbody tr').evaluateAll((rows,index)=>rows.map(row=>row.cells[index].textContent),periodColumn);expect(periods).toEqual(['2022 Q1','2022 Q2','2023 Q1']);
 const contextRequest=page.waitForRequest(request=>request.url().includes('/anomalies?')&&request.url().includes('signals_only=false'));
 await page.getByRole('button',{name:'All observations',exact:true}).click();await contextRequest;await expect(page.locator('#api-status')).toContainText('records in this view');
 const contextCount=Number((await page.locator('#api-status').textContent()).match(/^\d+/)[0]);expect(contextCount).toBeGreaterThan(3);
 await expect(page.locator('#data-panel tbody')).toContainText('Insufficient historical data');
});
test('forecast, source details and mobile do not imply unsupported controls',async({page})=>{
 await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('.filter-panel')).toBeHidden();await expect(page.locator('#data-panel')).toContainText('2025 Q4');await expect(page.locator('#data-panel')).toContainText('2026 Q1');await expect(page.locator('#feature-panel')).toContainText('Not a current future prediction');
 await page.locator('#platform-nav [data-page="reports"]').click();await page.locator('[data-page="methodology"]').click();await expect(page.locator('pre:visible')).toHaveCount(0);await expect(page.locator('#data-panel')).toContainText('Methods');
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:'analysis/test_scratch.local/usability/after-mobile.png',fullPage:true});
});

test('unequal ASSIST study periods do not offer unsupported calendar filters',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#boundary').selectOption('study_sample');
 const first=await page.locator('#area option').nth(1).getAttribute('value');await page.locator('#area').selectOption(first);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#start-year')).toBeHidden();await expect(page.locator('#end-year')).toBeHidden();await expect(page.locator('#more-filters')).toBeHidden();await expect(page.locator('#filter-help')).toContainText('unequal study periods');
});
