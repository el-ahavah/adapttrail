// Run against a local AdaptTrail instance. Requires Playwright.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.GUI_BROWSER_PATH ? {executablePath: process.env.GUI_BROWSER_PATH} : {})});
  try {
    const base = process.env.GUI_TEST_URL || 'http://127.0.0.1:5055';
    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const width of [320, 390, 768, 1440]) {
      await page.setViewportSize({width, height: 844});
      for (const route of ['/', '/discover', '/register', '/how-to-use', '/accessibility']) {
        await page.goto(base + route);
        assert.equal(await page.evaluate(() =>
          document.documentElement.scrollWidth > innerWidth), false, width + ': ' + route);
      }
    }
    await page.setViewportSize({width: 320, height: 844});
    await page.goto(base);
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('.skip').evaluate(el => el === document.activeElement), true);
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#main').evaluate(el => el === document.activeElement), true);
    await page.locator('[data-nav-toggle]').click();
    assert.equal(await page.locator('#main-navigation').isVisible(), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#main-navigation').isVisible(), false);
    assert.equal(await page.locator('[data-nav-toggle]').evaluate(el => el === document.activeElement), true);
    await page.locator('[data-theme-toggle]').click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    const plainContext = await browser.newContext({javaScriptEnabled: false,
      viewport: {width: 320, height: 844}});
    const plain = await plainContext.newPage();
    await plain.goto(base + '/accessibility');
    await plain.locator('input[value="low"]').check();
    await Promise.all([plain.waitForURL('**/accessibility?saved=1'),
      plain.getByRole('button', {name: 'Save display preference'}).click()]);
    const requests = [];
    plain.on('request', req => requests.push(new URL(req.url()).pathname));
    await plain.goto(base);
    assert.equal(await plain.locator('#main-navigation').isVisible(), true);
    assert.equal(await plain.locator('.hero-art').count(), 0);
    assert.equal(requests.includes('/static/app.js'), false);
    assert.equal(requests.includes('/static/landscape.svg'), false);
    assert.equal(await plain.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await plain.goto(base + '/accessibility');
    await plain.locator('input[value="standard"]').check();
    await Promise.all([plain.waitForURL('**/accessibility?saved=1'),
      plain.getByRole('button', {name: 'Save display preference'}).click()]);
    await plain.goto(base);
    assert.equal(await plain.locator('.hero-art').count(), 1);
    assert.equal(await plain.locator('#main-navigation').isVisible(), true);
    assert.deepEqual(errors, []);
    console.log('PASS: public-page reflow, skip link, menu keyboard control, low-data/no-JS preferences and omitted assets.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
