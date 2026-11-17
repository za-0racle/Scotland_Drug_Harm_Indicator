import {mkdir} from 'node:fs/promises';
import {test,expect} from '@playwright/test';

test('initial HTTP HTML and production assets expose metadata without JavaScript',async({request})=>{
 const response=await request.get('/');expect(response.ok()).toBeTruthy();const html=await response.text();
 expect(html).toContain('<title>Scotland Drug Harm Intelligence | Research Dashboard</title>');
 expect(html).toContain('rel="canonical" href="https://sdhi.cc/"');
 expect(html).toContain('property="og:image" content="https://sdhi.cc/og-image.png"');
 for(const path of ['/favicon.svg','/favicon.ico','/apple-touch-icon.png','/brand/sdhi-logo.svg','/brand/sdhi-logo-dark.svg','/brand/sdhi-icon.svg','/brand/sdhi-icon-192.png','/brand/sdhi-icon-512.png','/og-image.png']){
  const asset=await request.get(path);expect(asset.ok(),path).toBeTruthy();expect(asset.headers()['content-type'],path).not.toContain('text/html');
 }
});

test('shared shell remains readable across widths, themes and the comparison workflows',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('/');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(page.locator('#research-chart')).toBeVisible();
 await expect(page.locator('.brand-logo').first()).toBeVisible();
 await expect(page.locator('#platform-nav a')).toHaveCount(8);
 await mkdir('docs/images/task08s-phase1',{recursive:true});
 for(const width of [1440,1024,768,390,320]){
  await page.setViewportSize({width,height:900});
  await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),{message:`Page overflow at ${width}px`}).toBeTruthy();
  if(width===1440)await page.screenshot({path:'docs/images/task08s-phase1/shell-desktop.png',animations:'disabled'});
  if(width===390)await page.screenshot({path:'docs/images/task08s-phase1/shell-mobile.png',animations:'disabled'});
  if(width<=900){
   await page.locator('#navigation-toggle').click();await expect(page.locator('#platform-nav [aria-current]')).toBeFocused();
   const geometry=await page.locator('#app-sidebar').evaluate(n=>({top:n.getBoundingClientRect().top,header:document.querySelector('.platform-header').getBoundingClientRect().bottom}));
   expect(Math.abs(geometry.top-geometry.header)).toBeLessThan(2);
   if(width===390)await page.screenshot({path:'docs/images/task08s-phase1/shell-mobile-navigation.png',animations:'disabled'});
   await page.keyboard.press('Escape');await expect(page.locator('#navigation-toggle')).toBeFocused();
  }
 }
 await page.setViewportSize({width:1440,height:1100});
 await page.locator('#theme-toggle').click();await expect(page.locator('html')).toHaveAttribute('data-theme','dark');await expect(page.locator('.brand-logo-dark')).toBeVisible();
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await page.locator('#navigation-toggle').click();await expect(page.locator('.brand-icon')).toBeVisible();await expect(page.locator('.brand-logo-dark')).toBeHidden();
 await page.locator('#navigation-toggle').click();await page.locator('#theme-toggle').click();
 await page.locator('#open-comparison').click();await expect(page).toHaveURL(/#comparison$/);await expect(page.locator('#page-title')).toBeFocused();await expect(page.locator('#comparison-studio')).toBeVisible();
 await page.locator('#quick-comparison').click();await expect(page.locator('#comparison-close')).toBeFocused();await page.keyboard.press('Escape');await expect(page.locator('#quick-comparison')).toBeFocused();
 expect(errors).toEqual([]);
});
