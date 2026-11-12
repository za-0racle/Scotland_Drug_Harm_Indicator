import {test,expect} from '@playwright/test';

test('quarterly mortality, source controls, ranking, table search, export and responsive layouts',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/#trends');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#mortality-definition')).toContainText('suspected');await expect(page.locator('#mortality-summary')).toContainText('248');await expect(page.locator('#mortality-heatmap tbody tr')).toHaveCount(9);await expect(page.locator('#mortality-distribution svg')).toBeVisible();
 await expect(page.locator('#mortality-observations tbody tr')).toHaveCount(12);const n=await page.locator('#mortality-distribution table').textContent();await page.locator('#mortality-search').fill('2025');await expect(page.locator('#mortality-observations tbody tr')).toHaveCount(4);expect(await page.locator('#mortality-distribution table').textContent()).toBe(n);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export matching observations CSV'}).click();expect((await download).suggestedFilename()).toBe('mortality-police-observations.csv');
 await page.locator('#mortality-search').fill('');await page.getByRole('button',{name:'Next observations',exact:true}).click();await expect(page.locator('#mortality-observations')).toContainText('Page 2 of 3');
 await page.locator('#mortality-boundary').selectOption('police_division');await expect(page.locator('.mortality-bars li')).toHaveCount(13);await expect(page.locator('#mortality-ranking')).toContainText('2025 Q4');
 await page.locator('#mortality-observations').getByRole('button',{name:'Source details',exact:true}).first().click();await expect(page.locator('#verification')).toHaveAttribute('open');await page.locator('#close-verification').click();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task05-mortality-desktop.png',fullPage:true});
 await page.setViewportSize({width:900,height:1000});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task05-mortality-tablet.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'test-results/task05-mortality-mobile.png',fullPage:true});
});

test('registered source resets incompatible boundaries and never invents quarters or geographic peers',async({page})=>{
 await page.goto('/#trends');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#mortality-boundary').selectOption('police_division');
 await page.locator('#mortality-source').selectOption('nrs');await expect(page.locator('#mortality-boundary')).toHaveValue('country');await expect(page.locator('#mortality-boundary option')).toHaveCount(2);await expect(page.locator('#mortality-definition')).toContainText('Registration year');
 await expect(page.locator('#mortality-heatmap')).toContainText('not applicable');await expect(page.locator('#mortality-heatmap table')).toHaveCount(0);await expect(page.locator('#mortality-ranking')).toContainText('Fewer than two');
 await page.locator('#mortality-boundary').selectOption('council');await expect(page.locator('#mortality-area option')).toHaveCount(1);await expect(page.locator('#mortality-summary')).toContainText('25');await expect(page.locator('#mortality-scope')).toContainText('Inverclyde');
 await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#mortality-source')).toHaveValue('nrs');await expect(page.locator('#mortality-boundary')).toHaveValue('council');
 await page.locator('#mortality-from').selectOption('2024');await expect(page.locator('#mortality-distribution')).toContainText('At least eight');await page.getByRole('button',{name:'Reset mortality filters'}).click();await expect(page.locator('#mortality-source')).toHaveValue('police');
 await page.locator('#section-links a[href="#exploration"]').click();await expect(page.locator('#boundary')).toBeVisible();await expect(page.locator('#mortality-content')).toBeHidden();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
});

test('unavailable quarterly source remains explicit while annual source is independently accessible',async({page})=>{
 await page.route('**/exports?**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({message:'Quarterly mortality unavailable'})}));await page.goto('/#trends');await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');await expect(page.locator('#mortality-summary')).toContainText('Unavailable');
 await page.locator('#mortality-source').selectOption('nrs');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#mortality-trend')).toContainText('Annual registered');
});
