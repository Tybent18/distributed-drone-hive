import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

await mkdir('../assets/readme', { recursive: true });
const browser = await chromium.launch({
  headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl',
    '--enable-unsafe-swiftshader', '--disable-gpu-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1680, height: 946 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', (error) => errors.push(error.message));
await page.goto('http://127.0.0.1:4173/?demo=bridge', { waitUntil: 'networkidle' });
await page.waitForTimeout(5000);
await page.screenshot({ path: '../assets/readme/threejs-colony-console.png', fullPage: false });
const title = await page.title();
if (!title.includes('Drone Hive')) throw new Error('Unexpected page: ' + title);
if (errors.length) throw new Error('Frontend runtime errors: ' + errors.join('; '));
console.log('Captured real 3D frontend viewport:', title);
await browser.close();
