import {test,expect} from '@playwright/test';
test('backend-connected navigation, real geographic coverage and historical evidence',async({page})=>{
 await page.goto('/');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#platform-nav a')).toHaveCount(8);
 await page.locator('#platform-nav a[data-page="geography"]').click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#geo-boundary').selectOption('police_division');
 await expect(page.locator('#geo-area option')).toHaveCount(13);
 await page.locator('#geo-boundary').selectOption('health_board');
 await expect(page.locator('#geo-area option')).toHaveCount(14);
 await page.locator('#geo-reset').click();
 await page.locator('#platform-nav a[data-page="anomalies"]').click();
 await expect(page.locator('#api-status')).toContainText('47 records in this view');
 await page.locator('#more-filters').evaluate(n=>n.open=true);
 await page.locator('#model').selectOption('nb2_moments');
 await expect(page.locator('#api-status')).toContainText('40 records in this view',{timeout:60000});
 await page.locator('#platform-nav a[data-page="geography"]').click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#geo-reset').click();
 await expect(page.locator('#geo-summary')).toContainText('25');await expect(page.locator('#geo-published')).toContainText('35.6');await expect(page.locator('#api-status')).toContainText('15 selected-area records');
 await page.locator('#geo-from').selectOption('2020');await expect(page.locator('#api-status')).toContainText('5 selected-area records');
 await page.screenshot({path:'test-results/phase7-geography-desktop.png',fullPage:true});
 await page.locator('#platform-nav a[data-page="forecasting"]').click();
 await expect(page.locator('#feature-panel')).toContainText('Not a current future prediction');
 await page.locator('#platform-nav a[data-page="anomalies"]').click();await page.locator('#section-links a[data-page="signals"]').click();
 await page.getByRole('button',{name:'External validation',exact:true}).click();
 await expect(page.locator('#data-panel')).toContainText('pending');
});
test('mobile layout and backend errors remain explicit',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.screenshot({path:'test-results/phase7-mobile.png',fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.route('**/api/v1/overview?**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Test-only unavailable backend'})}));
 await page.locator('#refresh-api').click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');
});

test('API changes alter visible observations, without application mock data',async({page})=>{
 await page.goto('/#forecasting');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#data-panel')).toContainText('248');
 const before=await page.locator('#research-chart').evaluate(c=>c.toDataURL());
 await page.route('**/api/v1/forecasting/results?**',async route=>{
   const response=await route.fetch();const body=await response.json();
   body.data[0].predicted=999; // Explicit synthetic test-only transport substitution.
   await route.fulfill({response,json:body});
 });
 await page.locator('#refresh-api').click();
 await expect(page.locator('#data-panel')).toContainText('999');
 await expect(page.locator('#plot-panel')).toBeVisible();
 await expect.poll(()=>page.locator('#research-chart').evaluate(c=>c.toDataURL())).not.toBe(before);
});
