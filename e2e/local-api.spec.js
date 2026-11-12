import {test,expect} from '@playwright/test';
const localBase=`http://localhost:${process.env.E2E_LOCAL_PORT??5173}`;
test('configured local browser port proxies JSON and renders real police and board observations',async({page,request})=>{
 const health=await request.get(`${localBase}/api/v1/health`);expect(health.status()).toBe(200);expect(health.headers()['content-type']).toContain('application/json');
 await page.goto(`${localBase}/#overview`);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.goto(`${localBase}/#exploration`);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 for(const [boundary,count] of [['police_division',13],['health_board',14]]){
  await page.locator('#boundary').selectOption(boundary);await expect(page.locator('#area option')).toHaveCount(count+1);
  const id=await page.locator('#area option').nth(1).getAttribute('value');
  const network=page.waitForResponse(r=>r.url().includes(`/geographies/${id}/trends?`));
  await page.locator('#area').selectOption(id);const response=await network;expect(response.status()).toBe(200);
  await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#plot-panel')).toBeVisible();
  expect(await page.locator('#data-panel tbody tr').count()).toBeGreaterThan(0);
 }
 await page.reload();await expect(page.locator('#boundary option')).toHaveCount(9);await expect(page.locator('#api-status')).not.toHaveAttribute('data-state','error');
});
test('empty registry gives explicit error and refresh retries full bootstrap',async({page})=>{
 await page.route('**/api/v1/geographies',route=>route.fulfill({json:{state:'empty',kind:'metadata',data:[],total:0,metadata:{}}}));
 await page.route('**/api/v1/geographies?**',route=>route.fulfill({json:{state:'empty',kind:'metadata',data:[],total:0,metadata:{}}}));
 await page.goto('/');await expect(page.locator('#api-status')).toContainText('registry is empty');
 await page.unrouteAll();await page.locator('#refresh-api').click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.goto(`${localBase}/#exploration`);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#boundary option')).toHaveCount(9);
});
