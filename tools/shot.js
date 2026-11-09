// Usage: node tools/shot.js <url> <out.png> <width> <height> [full] [scale]
// Scrolls through the page first so lazy images load, then screenshots.
const { chromium } = require('playwright');
(async () => {
  const [url, out, w = '1440', h = '900', full = '', scale = '1'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  if (full === 'full') {
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
    await page.waitForLoadState('networkidle');
  }
  await page.waitForTimeout(400);
  await page.screenshot({ path: out, fullPage: full === 'full' });
  await browser.close();
  console.log('saved', out);
})();
