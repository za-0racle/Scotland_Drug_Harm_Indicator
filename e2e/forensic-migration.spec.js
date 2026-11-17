import {openSupporting} from './supporting-evidence.js';
import {readFileSync} from 'node:fs';
import {test, expect} from '@playwright/test';

const legacyScreenExport=readFileSync(new URL('../docs/baselines/task08f/legacy-screen-export.csv',import.meta.url));

test('Substance Intelligence uses the forensic contract and preserves filters, profile, export and navigation',async({page})=>{
 const analyticalRequests=[];
 const legacyRequests=[];
 let phase='initial';
 page.on('request',request=>{
  if(request.url().includes('/api/v1/analytical/v1/forensic-toxicology'))analyticalRequests.push(request.url());
  if(request.url().includes('/api/v1/toxicology/forensic'))legacyRequests.push({phase,url:request.url()});
 });
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto('/#substance');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 expect(analyticalRequests.length).toBeGreaterThan(0);
 expect(legacyRequests).toEqual([]);
 expect(new URL(analyticalRequests[0]).pathname).toBe('/api/v1/analytical/v1/forensic-toxicology');
 await expect(page.locator('#substance-heatmap table tbody tr')).toHaveCount(7);
 await expect(page.locator('#substance-heatmap table thead th')).toHaveCount(31);
 await expect(page.locator('#substance-trend canvas')).toBeVisible();
 await expect(page.locator('#substance-observations table caption')).toContainText('210 eligible');

 const category=page.locator('#substance-category');
 await expect(category.locator('option')).toHaveCount(8);
 await category.selectOption({index:1});
 await expect(page.locator('#substance-heatmap table tbody tr')).toHaveCount(1);
 await expect(page.locator('#substance-observations table caption')).toContainText('30 eligible');
 await category.selectOption('');
 await expect(page.locator('#substance-heatmap table tbody tr')).toHaveCount(7);
 await openSupporting(page,'#substance-heatmap');await openSupporting(page,'#substance-heatmap table tbody button');await page.locator('#substance-heatmap table tbody button').first().click();
 await expect(page.locator('.substance-drawer')).toBeVisible();
 await expect(page.locator('.substance-drawer')).toContainText('does not establish first occurrence');
 await page.keyboard.press('Escape');
 await expect(page.locator('.substance-drawer')).not.toBeVisible();

 const downloadPromise=page.waitForEvent('download');
 await openSupporting(page,'#substance-observations');await page.getByRole('button',{name:'Export all matching observations CSV'}).click();
 const download=await downloadPromise;
 const actual=readFileSync(await download.path());
 expect(actual.equals(legacyScreenExport)).toBe(true);

 const initialForensicRequests=analyticalRequests.length;
 phase='assist-source';
 await page.locator('#substance-source').selectOption('assist');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 expect(legacyRequests,JSON.stringify(legacyRequests)).toEqual([]);
 await expect(page.locator('#substance-area')).toContainText('ASSIST');
 phase='navigate-away';
 await page.goto('/#overview');
 await expect(page.locator('#overview-substances')).toContainText('Forensic substance detections');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 expect(legacyRequests).toHaveLength(1);
 expect(new URL(legacyRequests[0].url).pathname).toBe('/api/v1/toxicology/forensic');
 expect(legacyRequests[0].phase).toBe('navigate-away');
 phase='navigate-back';
 await page.goto('/#substance');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 phase='reset-filters';
 await page.getByRole('button',{name:'Reset substance filters'}).click();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#substance-observations table caption')).toContainText('210 eligible');
 expect(analyticalRequests.length).toBeGreaterThan(initialForensicRequests);
 expect(legacyRequests,JSON.stringify(legacyRequests)).toHaveLength(1);

 await page.setViewportSize({width:390,height:844});
 await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

test('forensic analytical failures show unavailable evidence and recover without legacy fallback',async({page})=>{
 let fail=true;
 const legacyRequests=[];
 await page.route('**/api/v1/analytical/v1/forensic-toxicology**',route=>{
  if(fail)return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({message:'Forensic analytical source unavailable'})});
  return route.continue();
 });
 page.on('request',request=>{
  if(request.url().includes('/api/v1/toxicology/forensic'))legacyRequests.push(request.url());
 });
 await page.goto('/#substance');
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');
 await expect(page.locator('#substance-summary')).toBeEmpty();
 await expect(page.locator('#substance-observations table')).toHaveCount(0);
 expect(legacyRequests).toEqual([]);
 fail=false;
 await page.reload();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#substance-observations table caption')).toContainText('210 eligible');
 expect(legacyRequests).toEqual([]);
});
