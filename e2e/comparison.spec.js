import {test,expect} from '@playwright/test';
test('comparison modal uses actual API data, exports both areas and restores focus',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#area option')).not.toHaveCount(0);
 await page.getByRole('button',{name:'Compare Data',exact:true}).click();
 const modal=page.getByRole('dialog');await expect(modal).toBeVisible();await expect(page.locator('#comparison-close')).toBeFocused();
 const area=await page.locator('#comparison-area option').evaluateAll(options=>options.find(o=>o.textContent.toLowerCase().includes('police division'))?.value);
 expect(area).toBeTruthy();await page.locator('#comparison-area').selectOption(area);
 await expect(page.locator('#comparison-other option')).not.toHaveCount(0);await expect(page.locator('#comparison-apply')).toBeEnabled();
 await page.locator('#comparison-start').fill('2023');await page.locator('#comparison-end').fill('2024');
 const response=page.waitForResponse(r=>r.url().includes('/comparisons?')&&r.url().includes('start_year=2023'));
 await page.locator('#comparison-apply').click();expect((await response).ok()).toBeTruthy();
 await expect(page.locator('#comparison-status')).toHaveAttribute('data-state','ready');await expect(modal.locator('tbody tr').first()).toBeVisible();
 await expect(page.locator('#comparison-chart')).toBeVisible();await expect(page.locator('#research-chart')).toBeVisible();
 await page.locator('#comparison-close').focus();await page.keyboard.press('Shift+Tab');expect(await modal.evaluate(node=>node.contains(document.activeElement))).toBeTruthy();
 await page.screenshot({path:'test-results/comparison-desktop.png',fullPage:true});
 const download=page.waitForEvent('download');await page.locator('#comparison-export').click();expect((await download).suggestedFilename()).toBe('geographic-comparison.csv');
 await page.keyboard.press('Escape');await expect(modal).not.toBeVisible();await expect(page.locator('#open-comparison')).toBeFocused();expect(await page.evaluate(()=>document.body.style.overflow)).not.toBe('hidden');
});
test('comparison errors support retry and changed selections clear stale results',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#area option')).not.toHaveCount(0);await page.locator('#open-comparison').click();
 const id=await page.locator('#comparison-area option').evaluateAll(options=>options.find(o=>o.textContent.toLowerCase().includes('police division'))?.value);await page.locator('#comparison-area').selectOption(id);await expect(page.locator('#comparison-apply')).toBeEnabled();
 await page.route('**/comparisons?**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({message:'Comparison temporarily unavailable'})}));
 await page.locator('#comparison-apply').click();await expect(page.locator('#comparison-status')).toHaveAttribute('data-state','error');await expect(page.locator('#comparison-retry')).toBeVisible();
 await page.unroute('**/comparisons?**');await page.locator('#comparison-retry').click();await expect(page.locator('#comparison-results')).toBeVisible();
 await page.locator('#comparison-end').fill('2022');await page.locator('#comparison-end').dispatchEvent('change');await expect(page.locator('#comparison-results')).toBeHidden();
 await page.setViewportSize({width:390,height:844});expect(await page.locator('dialog').evaluate(el=>el.scrollWidth<=el.clientWidth+1)).toBeTruthy();await page.screenshot({path:'test-results/comparison-mobile.png'});
 await page.keyboard.press('Escape');await page.locator('#theme-toggle').click();await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
});
test('single-area scopes explain incompatibility; empty comparison has no chart or export',async({page})=>{
 await page.goto('/#exploration');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#open-comparison').click();
 const council=await page.locator('#comparison-area option').evaluateAll(options=>options.find(o=>o.textContent.includes('Inverclyde')&&o.textContent.includes('Council'))?.value);await page.locator('#comparison-area').selectOption(council);
 await expect(page.locator('#comparison-status')).toContainText('No compatible second area');await expect(page.locator('#comparison-apply')).toBeDisabled();
 const police=await page.locator('#comparison-area option').evaluateAll(options=>options.find(o=>o.textContent.toLowerCase().includes('police division'))?.value);await page.locator('#comparison-area').selectOption(police);await expect(page.locator('#comparison-apply')).toBeEnabled();
 await page.route('**/comparisons?**',route=>route.fulfill({contentType:'application/json',body:JSON.stringify({state:'empty',data:[],total:0,message:'No observations in this test-only response'})}));
 await page.locator('#comparison-apply').click();await expect(page.locator('#comparison-status')).toHaveAttribute('data-state','empty');await expect(page.locator('#comparison-results')).toBeHidden();
 await page.locator('#comparison-close').click();await expect(page.getByRole('dialog')).not.toBeVisible();
});
