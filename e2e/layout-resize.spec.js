import {test,expect} from '@playwright/test';
for(const route of ['geography','substance','trends'])test(`${route} canvas and drawing buffer follow repeated exact acceptance viewport changes`,async({page})=>{
 test.setTimeout(180000);
 await page.goto('/#'+route);await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 const canvas=page.locator(route==='geography'?'#geo-chart':route==='substance'?'#substance-trend canvas':'#mortality-chart');
 await expect(canvas).toBeVisible();
 for(let cycle=0;cycle<5;cycle++)for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});
  try{await expect.poll(()=>canvas.evaluate(c=>({
   documentFits:document.documentElement.scrollWidth<=innerWidth,
   canvasFits:c.getBoundingClientRect().right<=c.parentElement.getBoundingClientRect().right+1,
   bufferFits:Math.abs(c.width/devicePixelRatio-c.parentElement.clientWidth)<=2
  }))).toEqual({documentFits:true,canvasFits:true,bufferFits:true});
  await expect.poll(()=>canvas.evaluate(async c=>{
   const url=performance.getEntriesByType('resource').find(r=>r.name.includes('/chart__js_auto.js'))?.name;
   if(!url)return false;
   const {default:Chart}=await import(url);const chart=Chart.getChart(c);if(!chart)return false;
   return chart.data.datasets.every((dataset,index)=>chart.getDatasetMeta(index).data.every((point,i)=>
    dataset.data[i]===null||Math.abs(point.x-chart.scales.x.getPixelForValue(i))<=1&&Math.abs(point.y-chart.scales.y.getPixelForValue(dataset.data[i]))<=1));
  })).toBeTruthy();}catch(error){console.log("CANVAS_GEOMETRY",await canvas.evaluate(c=>({bufferWidth:c.width,dpr:devicePixelRatio,parentWidth:c.parentElement.clientWidth,canvasWidth:c.getBoundingClientRect().width,inlineWidth:c.style.width,viewport:innerWidth})));throw error;}
 }
 await page.getByRole('button',{name:'Refresh data',exact:true}).click();await expect(page.locator('#api-status')).toHaveAttribute('data-state','ready');
 await expect(canvas).toBeVisible();
});
