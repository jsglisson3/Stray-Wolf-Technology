// Runs axe-core (WCAG 2.2 AA rules) on each page at phone and desktop widths.
// Usage: node tools/a11y-check.js http://localhost:8500  (serve the docs folder first)
const { chromium } = require('playwright');
const axePath = require.resolve('axe-core', { paths: [process.cwd(), ...(process.env.NODE_PATH || '').split(':').filter(Boolean)] });
const fs = require('fs');
(async () => {
  const base = process.argv[2] || 'http://localhost:8500';
  const pages = ['index.html', 'work.html', 'pricing.html', 'reviews.html', 'about.html', 'start.html', 'privacy.html', 'terms.html', '404.html', 'thanks.html'];
  const b = await chromium.launch();
  let total = 0;
  for (const [w, h] of [[390, 844], [1440, 900]]) {
    for (const pg of pages) {
      // bypassCSP: the pages carry a Content-Security-Policy that (rightly) blocks injected scripts like axe
      const p = await b.newPage({ viewport: { width: w, height: h }, bypassCSP: true });
      await p.goto(`${base}/${pg}`, { waitUntil: 'networkidle' });
      await p.waitForTimeout(2500);   // let the hero finish so nothing is mid-fade
      if (w < 600 && pg === 'index.html') { await p.click('[data-menu-toggle]'); await p.waitForTimeout(900); }   // check the open phone menu too, once its links have settled
      // Show every scroll-reveal block (hidden ones are skipped by axe), and for the contrast rule hide the decorative
      // layers (paper grain, stone facets) and flatten the sand gradient to its darker end; otherwise axe can't work out
      // the background and silently skips the contrast check on most of the text.
      await p.evaluate(() => document.querySelectorAll('[data-reveal]').forEach((e) => e.classList.add('is-in')));
      await p.addStyleTag({ content: '*::before,*::after{display:none!important} .on-stone{background:#E4DCCC!important} .hero{background:#F1E2D1!important}' });
      await p.waitForTimeout(900);
      await p.addScriptTag({ content: fs.readFileSync(axePath, 'utf8') });
      const res = await p.evaluate(async () => await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } }));
      const v = res.violations;
      total += v.length;
      console.log(`${w}px ${pg}: ${v.length} issue(s)`);
      for (const x of v) console.log(`   - [${x.impact}] ${x.id}: ${x.help} (${x.nodes.length}) e.g. ${x.nodes[0].target.join(' ')}`);
      await p.close();
    }
  }
  await b.close();
  console.log('TOTAL', total);
})();
