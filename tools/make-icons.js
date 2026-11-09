// Makes every small logo file from the one wolf symbol (docs/images/brand/stray-wolf-symbol-color.svg):
//   docs/favicon.svg            browser tab. The plain wolf on light tabs, the wolf on a paper tile on dark tabs.
//   docs/favicon.ico            16, 32 and 48 px, for older browsers and search engines that ask for /favicon.ico
//   docs/images/apple-touch-icon.png   iPhone and iPad home screen, iMessage and Safari favourites (180 px, no see-through corners)
//   docs/images/favicon-192.png, favicon-512.png, favicon-512-maskable.png   Android home screen (site.webmanifest)
//   docs/images/favicon-16.png, favicon-32.png, favicon-48.png, favicon-96.png   the same tab icon as plain files
//   docs/images/stray-wolf-logo-512.png   the logo Google is pointed to in the page's structured data
// Run from the project folder:  node tools/make-icons.js   (needs Node and Playwright; Claude runs it)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const DOCS = path.join(ROOT, 'docs');
const IMG = path.join(DOCS, 'images');
const PAPER = '#F4F2EE';

const symbol = fs.readFileSync(path.join(IMG, 'brand', 'stray-wolf-symbol-color.svg'), 'utf8');
const wolf = symbol.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '').trim();

// The wolf, scaled about the centre of its 200 x 200 box.
const scaled = (s) => s === 1 ? wolf : `<g transform="translate(${(200 - 200 * s) / 2} ${(200 - 200 * s) / 2}) scale(${s})">${wolf}</g>`;
const svg = (inner) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">${inner}</svg>`;

const designs = {
  // a paper tile with the wolf filling it, so it reads on dark tabs and dark search pages
  tab: svg(`<rect width="200" height="200" rx="40" fill="${PAPER}"/>${scaled(1)}`),
  // the home-screen tile: square and solid (phones round the corners themselves)
  home: svg(`<rect width="200" height="200" fill="${PAPER}"/>${scaled(0.72)}`),
  // Android's own icon: a rounded tile, wolf a touch smaller
  app: svg(`<rect width="200" height="200" rx="44" fill="${PAPER}"/>${scaled(0.86)}`),
  // Android "maskable": full bleed, wolf inside the middle circle that every phone shape keeps
  maskable: svg(`<rect width="200" height="200" fill="${PAPER}"/>${scaled(0.6)}`),
  // the logo for search engines: the plain wolf with a little room around it
  logo: svg(scaled(0.88)),
};

const outputs = [
  ['tab', 16, 'images/favicon-16.png'],
  ['tab', 32, 'images/favicon-32.png'],
  ['tab', 48, 'images/favicon-48.png'],
  ['tab', 96, 'images/favicon-96.png'],
  ['home', 180, 'images/apple-touch-icon.png'],
  ['app', 192, 'images/favicon-192.png'],
  ['app', 512, 'images/favicon-512.png'],
  ['maskable', 512, 'images/favicon-512-maskable.png'],
  ['logo', 512, 'images/stray-wolf-logo-512.png'],
];

// favicon.ico: an icon directory holding three PNGs
function ico(pngs) {
  const head = Buffer.alloc(6 + 16 * pngs.length);
  head.writeUInt16LE(0, 0); head.writeUInt16LE(1, 2); head.writeUInt16LE(pngs.length, 4);
  let offset = head.length;
  pngs.forEach(([size, buf], i) => {
    const e = 6 + 16 * i;
    head.writeUInt8(size >= 256 ? 0 : size, e); head.writeUInt8(size >= 256 ? 0 : size, e + 1);
    head.writeUInt8(0, e + 2); head.writeUInt8(0, e + 3);
    head.writeUInt16LE(1, e + 4); head.writeUInt16LE(32, e + 6);
    head.writeUInt32LE(buf.length, e + 8); head.writeUInt32LE(offset, e + 12);
    offset += buf.length;
  });
  return Buffer.concat([head, ...pngs.map(([, b]) => b)]);
}

(async () => {
  // favicon.svg: plain wolf when the browser is light, tiled wolf when it's dark
  const tabSvg = svg(`<style>@media (prefers-color-scheme: light) { .tile { display: none } }</style><rect class="tile" width="200" height="200" rx="40" fill="${PAPER}"/>${wolf}`);
  fs.writeFileSync(path.join(DOCS, 'favicon.svg'), tabSvg + '\n');
  console.log('wrote favicon.svg');

  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  const made = {};
  for (const [name, size, file] of outputs) {
    await page.setViewportSize({ width: size, height: size });
    await page.setContent(`<html><body style="margin:0;background:transparent">${designs[name].replace('<svg ', `<svg width="${size}" height="${size}" `)}</body></html>`);
    const buf = await page.screenshot({ omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
    fs.writeFileSync(path.join(DOCS, file), buf);
    made[`${name}-${size}`] = buf;
    console.log('wrote', file);
  }
  await browser.close();
  fs.writeFileSync(path.join(DOCS, 'favicon.ico'), ico([[16, made['tab-16']], [32, made['tab-32']], [48, made['tab-48']]]));
  console.log('wrote favicon.ico');
})();
