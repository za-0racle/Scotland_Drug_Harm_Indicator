import {test,expect} from '@playwright/test';

test('verified overview, mortality year selection, source disclosures and responsive screenshots',async({page})=>{
 const errors=[];page.on('pageerror',error=>errors.push(error.message));await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/#overview');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#summary-grid')).toContainText('248');await expect(page.locator('#summary-grid')).toContainText('2025 Q4');await expect(page.locator('#summary-grid')).toContainText('Police Scotland');
 await expect(page.locator('#overview-heatmap tbody tr')).toHaveCount(9);await expect(page.locator('#overview-forecast')).toContainText('2025 Q4');await expect(page.locator('#overview-forecast')).toContainText('2026 Q1');await expect(page.locator('#overview-forecast')).toContainText('Gaussian');
 await expect(page.locator('#overview-substances')).toContainText('Overlapping broad categories');await expect(page.locator('#overview-geography')).toContainText('25 registered');await expect(page.locator('#overview-monitoring')).toContainText('47 historical statistical flags');
 await page.locator('#overview-from-year').selectOption('2024');await expect(page.locator('#overview-heatmap tbody tr')).toHaveCount(2);await expect(page.locator('#data-panel tbody tr')).toHaveCount(8);
 await page.getByRole('button',{name:'All available years',exact:true}).click();await expect(page.locator('#overview-heatmap tbody tr')).toHaveCount(9);
 await page.locator('#overview-forecast > details > summary').click();await expect(page.locator('#overview-forecast')).toContainText('analysis/outputs/forecast.json');await page.locator('#overview-forecast > details > summary').click();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task04-overview-desktop.png',fullPage:true});
 await page.setViewportSize({width:900,height:1000});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task04-overview-tablet.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await expect(page.locator('#research-chart')).toBeVisible();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task04-overview-mobile.png',fullPage:true});
 await page.locator('#navigation-toggle').click();await page.keyboard.press('Escape');await expect(page.locator('#navigation-toggle')).toBeFocused();expect(errors).toEqual([]);
});

test('forecast failure is explicit while independently verified overview sections remain usable',async({page})=>{
 await page.route('**/forecasting/results?**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({message:'Saved forecast temporarily unavailable'})}));
 await page.goto('/#overview');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#overview-forecast')).toContainText('Saved forecast temporarily unavailable');await expect(page.locator('#overview-heatmap tbody tr')).toHaveCount(9);await expect(page.locator('#overview-geography')).toContainText('registered drug misuse deaths');
 await page.locator('#overview-coverage').getByRole('link',{name:'Explore geographic trends',exact:true}).click();await expect(page).toHaveURL(/#geography$/);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#overview-content')).toBeHidden();
});

test('mortality failure does not fabricate zero counts or hide the saved forecast',async({page})=>{
 await page.route('**/overview?**',async route=>{const response=await route.fetch();const data=await response.json();data.data[0].database={state:'error',data:[],total:0,metadata:{},message:'Mortality source unavailable'};await route.fulfill({response,json:data});});
 await page.goto('/#overview');await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');await expect(page.locator('#summary-grid .summary-card').first()).toContainText('Unavailable');await expect(page.locator('#research-chart')).toBeHidden();await expect(page.locator('#overview-heatmap')).toContainText('unavailable');await expect(page.locator('#overview-forecast')).toContainText('248 projected suspected deaths');
});
