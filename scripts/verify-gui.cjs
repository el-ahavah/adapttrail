// Optional browser check: install Playwright separately, then provide GUI_TEST_URL.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({headless:true, ...(process.env.GUI_BROWSER_PATH ? {executablePath:process.env.GUI_BROWSER_PATH} : {}), args:['--no-sandbox']});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const base = process.env.GUI_TEST_URL || 'http://127.0.0.1:5055';
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if(message.type()==='error') errors.push(message.text()); });
  await page.goto(base);
  if(!(await page.locator('h1').innerText()).includes('Small actions')) throw Error('Homepage missing');
  if(process.env.GUI_SCREENSHOT_DIR) await page.screenshot({path:process.env.GUI_SCREENSHOT_DIR+'/desktop.png',fullPage:true});
  await page.goto(base+'/discover');
  await page.locator('[data-project-search]').fill('Nigeria');
  if(await page.locator('[data-search-group] .card:visible').count()!==1) throw Error('Search mismatch');
  await page.locator('[data-project-search]').fill('no-such-project');
  if(await page.locator('[data-search-group] .card:visible').count()!==0) throw Error('Empty search mismatch');
  await page.locator('[data-clear-search]').click();
  if(await page.locator('[data-search-group] .card:visible').count()<6) throw Error('Clear mismatch');
  await page.setViewportSize({width:390,height:844});
  await page.goto(base);
  if(await page.locator('#main-navigation').isVisible()) throw Error('Mobile menu initially open');
  await page.locator('[data-nav-toggle]').click();
  if(!(await page.locator('#main-navigation').isVisible())) throw Error('Menu did not open');
  await page.keyboard.press('Escape');
  if(await page.locator('#main-navigation').isVisible()) throw Error('Escape did not close menu');
  if(process.env.GUI_SCREENSHOT_DIR) await page.screenshot({path:process.env.GUI_SCREENSHOT_DIR+'/mobile.png',fullPage:true});
  for(const route of ['/','/discover','/register','/how-to-use','/projects/niger-tahoua']) {
    await page.goto(base+route);
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)) throw Error('Horizontal overflow: '+route);
  }
  const nojs = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const plain = await nojs.newPage(); await plain.goto(base+'/discover');
  if(!(await plain.locator('#main-navigation').isVisible())) throw Error('No-JS navigation missing');
  if(errors.length) throw Error(errors.join('\n'));
  await browser.close();
  console.log('PASS: desktop/mobile rendering, search/clear/empty state, mobile menu/Escape, overflow, no-JavaScript navigation; no console errors.');
})().catch(error=>{console.error(error);process.exit(1)});
