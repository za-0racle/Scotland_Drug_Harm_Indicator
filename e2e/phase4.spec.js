import {test,expect} from '@playwright/test';
import {mkdir,readFile} from 'node:fs/promises';

test('research explains adopted objectives, source distinctions and saved geographic findings',async({page})=>{
 await page.goto('/#reports');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#research-about')).toContainText('To develop a data analytics system for examining emerging illicit drug toxicity patterns.');
 await expect(page.locator('#research-objectives > ol > li')).toHaveCount(5);
 await expect(page.locator('#research-objectives')).toContainText('not verified verbatim quotations');
 await expect(page.locator('#research-findings')).toContainText('25 registered drug misuse deaths in 2024');
 await expect(page.locator('#research-findings')).toContainText('35.6');await expect(page.locator('#research-findings')).toContainText('22.5');await expect(page.locator('#research-findings')).toContainText('95% confidence interval');
 await expect(page.locator('#research-findings')).toContainText('do not describe Greenock separately');
 await expect(page.locator('.research-source')).toHaveCount(7);
 const forensic=page.locator('.research-source').filter({has:page.locator('summary', {hasText:'forensic toxicology'})});
 await forensic.locator(':scope > summary').click();await expect(forensic).toContainText('cannot be added');await expect(forensic).toContainText('2018 Q4');await expect(forensic).toContainText('2026 Q1');
 const treatment=page.locator('.research-source').filter({has:page.locator('summary', {hasText:'treatment samples'})});await treatment.locator(':scope > summary').click();await expect(treatment).toContainText('source opioid category excludes treatment opioids');
 await expect(page.locator('pre:visible')).toHaveCount(0);
 await page.locator('#research-study-methods > details > summary').click();await expect(page.locator('#research-study-methods')).toContainText('2017–2020');await expect(page.locator('#research-study-methods')).toContainText('not no-alert periods');
 await page.locator('#research-documentation > summary').click();await expect(page.locator('#research-documentation a')).toHaveCount(7);
 for(const a of await page.locator('#research-documentation a').all())expect(await a.getAttribute('href')).toMatch(/^https:\/\/github.com\/za-0racle\/Scotland_Drug_Harm_Indicator\/blob\/main\//);
 await page.locator('#research-technical > summary').click();await page.getByRole('button',{name:'Source inventory',exact:true}).click();await expect(page.locator('#api-status')).toContainText('6 records');await expect(page.locator('#data-panel')).toBeVisible();
});

test('saved download links retain real page bounds, exact scores and provenance',async({page})=>{
 await page.goto('/#reports');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.getByText('Saved analytical result downloads',{exact:true}).click();
 const a=page.locator('#research-downloads a[href*="resource=forecast_models"][href*="format=json"]');const href=await a.getAttribute('href');expect(href).toContain('limit=100');expect(href).toContain('offset=0');
 const response=await page.request.get(href);expect(response.ok()).toBeTruthy();const actual=await response.json();
 const expected=JSON.parse(await readFile('analysis/outputs/model_metrics.json','utf8'));
 expect(actual.data.map(row=>[row.model,row.mae])).toEqual(expected.map(row=>[row.model,row.mae]));expect(actual.metadata.artifact_sha256).toBeTruthy();
 const csv=await page.request.get(await page.locator('#research-downloads a[href*="resource=forecast_models"][href*="format=csv"]').getAttribute('href'));expect(csv.ok()).toBeTruthy();expect(await csv.text()).toContain('_artifact_sha256');
 await expect(page.locator('#research-downloads')).toContainText('first page only');await expect(page.locator('#research-downloads')).toContainText('complete aligned comparison');
});

test('unavailable research evidence stays separate and refresh restores verified findings',async({page})=>{
 await page.route('**/api/v1/geography/inverclyde?**',route=>route.fulfill({status:503,json:{detail:'Test-only unavailable case study'}}));
 await page.goto('/#reports');await expect(page.locator('#api-status')).toHaveAttribute('data-state','unavailable');await expect(page.locator('#research-findings')).toContainText('could not be loaded or verified');await expect(page.locator('#research-findings')).not.toContainText('25 registered');await expect(page.locator('.research-source')).toHaveCount(6);
 await page.unroute('**/api/v1/geography/inverclyde?**');await page.route('**/api/v1/sources?**',route=>route.fulfill({status:503,json:{detail:'Test-only unavailable source inventory'}}));
 await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','unavailable');await expect(page.locator('#research-sources')).toContainText('Source definitions could not be loaded');await expect(page.locator('#research-findings')).toContainText('25 registered');
 await page.unroute('**/api/v1/sources?**');await page.locator('#refresh-api').click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
});

test('research desktop and mobile captures include evidence and accessible supporting sections',async({page})=>{
 const errors=[];page.on('pageerror',error=>errors.push(error.message));await mkdir('docs/images/task08s-phase4',{recursive:true});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto('/#reports');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
  await expect(page.locator('#research-findings')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.locator('#research-study-methods > details > summary').focus();await page.keyboard.press('Enter');await expect(page.locator('#research-study-methods > details')).toHaveAttribute('open');await page.keyboard.press('Escape');await expect(page.locator('#research-study-methods > details')).not.toHaveAttribute('open');
  await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});await page.screenshot({path:`docs/images/task08s-phase4/research-${width===1440?'desktop':'mobile'}.png`,fullPage:true});
 }
 expect(errors).toEqual([]);
});

test('all eight primary headings use public language and scientific qualifications remain accessible',async({page})=>{
 test.setTimeout(300000);
 for(const route of ['overview','comparison','trends','substance','geography','anomalies','forecasting','reports']){
  await page.goto('/#'+route);if(route==='comparison'){await expect(page.locator('#studio-apply')).toBeEnabled();await page.locator('#studio-apply').click();}await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
  const headings=await page.locator('main h2,main h3').allTextContents();expect(headings.join(' ')).not.toMatch(/frozen|artifact|manifest|TASK\d|Phase \d/i);
 }
 await expect(page.locator('#research-study-methods')).toContainText('Missing values remain missing');
 await expect(page.locator('#research-study-methods')).toContainText('not a current forecast');
 await expect(page.locator('.platform-footer')).toContainText('No PHS endorsement');
});
