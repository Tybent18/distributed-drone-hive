import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

await mkdir('../assets/readme', {recursive:true});
await mkdir('../demos/webgl-frames', {recursive:true});
const browser = await chromium.launch({
 headless:true,args:['--use-gl=angle','--use-angle=swiftshader',
 '--enable-webgl','--enable-unsafe-swiftshader','--disable-gpu-sandbox']
});
const ids=['overview','bridge','multi','comms','energy','recovery'];
const errors=[];
try {
 for(const id of ids){
  const page=await browser.newPage({viewport:{width:1440,height:810},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(id+': '+e.message));
  await page.goto('http://127.0.0.1:4173/?demo='+id+'&step=0',{waitUntil:'networkidle'});
  await page.waitForTimeout(1300);
  for(let step=0;step<6;step++){
   if(step>0){
    await page.getByTestId('demo-next').click();
    await page.waitForTimeout(650);
   }
   const label=await page.locator('.timeline-copy b').innerText();
   if(!label.includes('STAGE '+(step+1)+'/6'))throw new Error(id+': incorrect '+label);
   await page.screenshot({path:'../demos/webgl-frames/'+id+'-'+step+'.png'});
   if(step===3){
    await page.screenshot({path:'../assets/readme/colony-'+id+'.png'});
    if(id==='bridge')await page.screenshot({
      path:'../assets/readme/threejs-colony-console.png'
    });
   }
  }
  console.log('Captured six DISTINCT interactive event frames:',id);
  await page.close();
 }
 if(errors.length)throw new Error(errors.join('; '));
} finally {await browser.close()}
