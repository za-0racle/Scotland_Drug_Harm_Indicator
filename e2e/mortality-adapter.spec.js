import {openSupporting} from './supporting-evidence.js';
import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';
import {mortalityCsv} from '../src/platform/mortality-data.js';
const path='/api/v1/analytical/v1/mortality-trends';
const legacy=JSON.parse(await readFile(new URL('../docs/baselines/task08d/legacy-response.json',import.meta.url),'utf8'));
const ready=page=>expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');

test('Geographic police feed pins full history and preserves exact JSON/CSV exports and mobile profile focus',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});
 const requests=[];page.on('request',request=>{if(request.url().includes(path+'?'))requests.push(new URL(request.url()));});
 await page.goto('/#geography');await ready(page);await page.locator('#geo-boundary').selectOption('police_division');await ready(page);
 expect(requests).toHaveLength(6);expect(requests.map(u=>u.searchParams.get('offset'))).toEqual(['0','100','200','300','400','500']);
 const tokens=requests.slice(1).map(u=>u.searchParams.get('expected_collection'));expect(new Set(tokens).size).toBe(1);expect(tokens[0]).toMatch(/^[a-f0-9]{64}$/);
 await expect(page.locator('#geo-ranking .mortality-bars li')).toHaveCount(13);
 const area=await page.locator('#geo-area').inputValue();const expected=legacy.data.filter(r=>r.geography_id===area);
 const jsonDownload=page.waitForEvent('download');await openSupporting(page,'#geo-history');await page.getByRole('button',{name:'Export area history JSON',exact:true}).click();const json=JSON.parse(await readFile(await(await jsonDownload).path(),'utf8'));
 expect(json.data).toEqual(expected);expect(json.data).toHaveLength(36);expect(json.metadata.artifact_sha256).toBe(legacy.metadata.artifact_sha256);
 const csvDownload=page.waitForEvent('download');await openSupporting(page,'#geo-history');await page.getByRole('button',{name:'Export area history CSV',exact:true}).click();const csv=await readFile(await(await csvDownload).path(),'utf8');expect(csv).toBe(mortalityCsv(expected,json.metadata));
 await page.locator('#geo-from').selectOption('2023 Q1');await expect(page.locator('#geo-trend')).toContainText('2023 Q1');
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.locator('#geo-profile').click();await expect(page.locator('.geo-drawer')).toBeVisible();await page.keyboard.press('Escape');await expect(page.locator('#geo-profile')).toBeFocused();
 await page.screenshot({path:'test-results/task08d-police-mobile.png',fullPage:true});
});

test('invalid analytical contract is unavailable without legacy fallback; independent sources and retry survive',async({page})=>{
 let legacyRequests=0;page.on('request',request=>{const u=new URL(request.url());if(u.pathname.endsWith('/exports')&&u.searchParams.get('resource')==='mortality_trends')legacyRequests++;});
 await page.route('**/analytical/v1/mortality-trends?**',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({contract_version:'invalid'})}));
 await page.goto('/#geography');await ready(page);await page.locator('#geo-boundary').selectOption('police_division');await expect(page.locator('#api-status')).toHaveAttribute('data-state','error');await expect(page.locator('#geo-summary')).toBeEmpty();await expect(page.getByRole('button',{name:'Export area history JSON',exact:true})).toHaveCount(0);expect(legacyRequests).toBe(0);
 await page.locator('#geo-boundary').selectOption('council');await ready(page);
 await page.unroute('**/analytical/v1/mortality-trends?**');await page.locator('#refresh-api').click();await ready(page);await page.locator('#geo-boundary').selectOption('police_division');await ready(page);await expect(page.locator('#geo-ranking .mortality-bars li')).toHaveCount(13);
});

test('Mortality Analytics remains legacy and late Geographic responses cannot replace another screen',async({page})=>{
 let analytical=0,old=0;page.on('request',request=>{const u=new URL(request.url());if(u.pathname===path)analytical++;if(u.pathname.endsWith('/exports')&&u.searchParams.get('resource')==='mortality_trends')old++;});
 await page.goto('/#trends');await ready(page);expect(old).toBeGreaterThan(0);expect(analytical).toBe(0);
 await page.route('**/analytical/v1/mortality-trends?**',async route=>{await new Promise(resolve=>setTimeout(resolve,250));await route.continue().catch(()=>{});});
 await page.goto('/#geography');await expect(page.locator('#api-status')).toHaveAttribute('data-state','loading');await page.locator('#platform-nav a[href="#trends"]').click();await ready(page);await expect(page.locator('#mortality-source')).toBeVisible();await expect(page.locator('#geo-boundary')).toHaveCount(0);
});
