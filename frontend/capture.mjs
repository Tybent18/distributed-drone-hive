import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

await mkdir('../assets/readme', {recursive: true});
const browser = await chromium.launch({
  headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl',
    '--enable-unsafe-swiftshader', '--disable-gpu-sandbox'],
});
const errors = [];
const ids = ['overview','bridge','multi','comms','energy','recovery'];
try {
  for (const id of ids) {
    const page = await browser.newPage({
      viewport:{width:1680,height:946},deviceScaleFactor:1,
    });
    page.on('pageerror', error=>errors.push(id+': '+error.message));
    await page.goto('http://127.0.0.1:4173/?demo='+id, {waitUntil:'networkidle'});
    await page.waitForTimeout(2700);
    if ((await page.locator('.demo-choice.current').count()) !== 1) {
      throw new Error('Scenario not selected: '+id);
    }
    const png='../assets/readme/colony-'+id+'.png';
    await page.screenshot({path:png, fullPage:false});
    if(id==='bridge') await page.screenshot({
      path:'../assets/readme/threejs-colony-console.png',fullPage:false,
    });
    console.log('Rendered genuine 3D scenario',id,png);
    await page.close();
  }
  if(errors.length)throw new Error(errors.join('; '));
} finally {await browser.close()}
