// Launch headless Chromium with software WebGL and open the renderer page
const { chromium } = require('playwright');
const path = require('path');
const serve = require('./server');

module.exports = async function openRenderer({ w = 1920, h = 1080, extra = '' } = {}) {
  const root = path.resolve(__dirname, '..');
  const srv = await serve(root);
  const port = srv.address().port;
  const browser = await chromium.launch({
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-watchdog', '--disable-background-timer-throttling', '--disable-renderer-backgrounding'],
  });
  const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?w=${w}&h=${h}${extra}`);
  await page.waitForFunction(() => window.init !== undefined, null, { timeout: 60000 });
  await page.evaluate(() => window.init());
  return {
    page,
    async frame(t, quality = 0.93) {
      const url = await page.evaluate(([t, q]) => window.renderFrame(t, q), [t, quality]);
      return Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
    },
    async close() { await browser.close(); srv.close(); },
  };
};
