import {test,expect} from '@playwright/test';

test('white and gold shell, collapse, legacy links, completed screens and comparison focus',async({page})=>{
 await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('html')).toHaveAttribute('data-theme','light');
 await expect(page.locator('#platform-nav a')).toHaveCount(8);
 await expect(page.locator('#page-title')).toHaveText('Forecasting Lab');
 const series=page.locator('[data-chart-legend] button').first();await expect(series).toHaveAttribute('aria-pressed','true');await series.click();await expect(series).toHaveAttribute('aria-pressed','false');await series.click();await expect(series).toHaveAttribute('aria-pressed','true');
 await page.locator('#navigation-toggle').click();await expect(page.locator('#navigation-toggle')).toHaveAttribute('aria-expanded','false');
 await expect(page.locator('#platform-nav a').first()).toHaveAccessibleName('Intelligence Overview');
 await page.locator('#navigation-toggle').click();
 await page.locator('[data-page="anomalies"]').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.locator('[data-page="signals"]').click();await expect(page).toHaveURL(/#signals$/);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#platform-nav [data-page="anomalies"]')).toHaveAttribute('aria-current','page');
 await page.locator('#platform-nav [data-page="reports"]').click();await page.locator('[data-page="methodology"]').click();await expect(page).toHaveURL(/#methodology$/);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.locator('[data-page="substance"]').click();await expect(page.locator('#substance-content')).toBeVisible();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#export-csv')).toBeHidden();
 await page.locator('[data-page="comparison"]').click();await expect(page.locator('#comparison-studio')).toBeVisible();await page.locator('#open-comparison').click();
 await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#comparison-close')).toBeFocused();await page.keyboard.press('Escape');await expect(page.locator('#open-comparison')).toBeFocused();
 await page.screenshot({path:'test-results/task03-shell-desktop.png',fullPage:true});
 await page.goBack();await expect(page.locator('#page-title')).toHaveText('Substance Intelligence');
});

test('mobile drawer contains keyboard focus, closes with Escape, and layout reflows',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/#forecasting');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const trigger=page.locator('#navigation-toggle');await expect(trigger).toHaveAttribute('aria-expanded','false');
 await trigger.click();await expect(trigger).toHaveAttribute('aria-expanded','true');
 await expect(page.locator('#platform-nav [aria-current="page"]')).toBeFocused();
 await page.locator('#platform-nav a').last().focus();await page.keyboard.press('Tab');await expect(page.locator('.drawer-close')).toBeFocused();
 await page.keyboard.press('Escape');await expect(trigger).toHaveAttribute('aria-expanded','false');await expect(trigger).toBeFocused();
 await expect(page.locator('#app-sidebar')).toHaveAttribute('inert','');
 await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:'test-results/task03-shell-mobile.png',fullPage:true});
 await trigger.click();await page.locator('[data-page="geography"]').click();await expect(trigger).toHaveAttribute('aria-expanded','false');await expect(page.locator('#page-title')).toBeFocused();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await expect(page.locator('#geo-boundary')).toBeVisible();
 await page.locator('#geo-profile').click();await expect(page.locator('.geo-drawer')).toBeVisible();await page.keyboard.press('Escape');await expect(page.locator('.geo-drawer')).not.toBeVisible();
});
