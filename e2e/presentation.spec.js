import {test,expect} from '@playwright/test';
test('presentation timings, sampled contrast and accessible controls',async({page},testInfo)=>{
 const started=Date.now();await page.goto('/');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const initialMs=Date.now()-started;
 const contrast=await page.evaluate(()=>{
  const luminance=rgb=>rgb.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  const parse=c=>c.match(/[0-9.]+/g).map(Number);
  return ['.platform-header h1','.platform-header p','.notice','#platform-nav a','#refresh-api','#api-status','.platform-footer'].map(selector=>{
   const node=document.querySelector(selector),fg=parse(getComputedStyle(node).color);let parent=node,bg;
   while(parent){bg=parse(getComputedStyle(parent).backgroundColor);if(bg.length<4||bg[3]>0)break;parent=parent.parentElement;}
   bg=bg&&bg[3]!==0?bg:[255,255,255];const a=luminance(fg),b=luminance(bg);return{selector,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
  });
 });
 for(const sample of contrast)expect(sample.ratio,sample.selector).toBeGreaterThanOrEqual(4.5);
 await page.goto('/#exploration');await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');await page.locator('#boundary').selectOption('health_board');
 const first=await page.locator('#area option').nth(1).getAttribute('value');const selection=Date.now();await page.locator('#area').selectOption(first);
 await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');const areaMs=Date.now()-selection;
 await expect(page.locator('#research-chart')).toHaveAttribute('aria-label',/equivalent values in the table/);
 await expect(page.locator('#data-panel tbody tr')).toHaveCount(100);
 await page.locator('#area').focus();await expect(page.locator('#area')).toBeFocused();
 const focus=await page.locator('#area').evaluate(n=>getComputedStyle(n).outlineStyle);expect(focus).not.toBe('none');
 await page.screenshot({path:'test-results/phase8-desktop.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:'test-results/phase8-mobile.png',fullPage:true});
 const observations={initialMs,areaMs,contrast,note:'Single local warmed-server observations; no service-level or full accessibility certification'};
 console.log('PHASE8_PRESENTATION',JSON.stringify(observations));await testInfo.attach('presentation.json',{body:JSON.stringify(observations,null,2),contentType:'application/json'});
});
