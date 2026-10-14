// Headless frame renderer.
//   node render.mjs --start 0 --end 18000 [--w 1920 --h 1080] [--out ../build/frames]
// Serves this folder over HTTP, opens index.html in headless Chromium and
// writes one JPEG per frame (frame_000000.jpg ...). Frames that already exist
// are skipped, so an interrupted render can simply be restarted.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith('--') ? [...a, [v.slice(2), arr[i + 1]]] : a), []));
const W = +(args.w || 1280), H = +(args.h || 720), FPS = +(args.fps || 30);
const outDir = path.resolve(args.out || path.join(here, '../build/frames'));
const timelinePath = path.join(here, '../build/timeline.json');
const total = Math.round(JSON.parse(fs.readFileSync(timelinePath, 'utf8')).duration * FPS);
const start = +(args.start || 0), end = Math.min(+(args.end || total), total);
const step = +(args.step || 1);
fs.mkdirSync(outDir, { recursive: true });

const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  const file = p === '/timeline.json' ? timelinePath : path.join(here, p === '/' ? 'index.html' : p);
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(data);
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'],
});
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
page.on('pageerror', (e) => { console.error('[pageerror]', e); process.exit(1); });
await page.goto(`http://127.0.0.1:${port}/?w=${W}&h=${H}&aa=${args.aa ?? 1}`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 120000 });

const t0 = Date.now();
let done = 0;
if (args.times) {
  // preview mode: --times 12.5,40,61  -> preview_012.50.jpg ...
  for (const ts of args.times.split(',')) {
    const t = +ts;
    const url = await page.evaluate((x) => window.renderFrame(x), t);
    fs.writeFileSync(path.join(outDir, `preview_${t.toFixed(2).padStart(7, '0')}.jpg`), Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
  }
  await browser.close();
  server.close();
  process.exit(0);
}
for (let f = start; f < end; f += step) {
  const file = path.join(outDir, `frame_${String(f).padStart(6, '0')}.jpg`);
  if (fs.existsSync(file)) continue;
  const url = await page.evaluate((t) => window.renderFrame(t), f / FPS);
  fs.writeFileSync(file + '.tmp', Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
  fs.renameSync(file + '.tmp', file);
  done++;
  if (done % 60 === 0) {
    const el = (Date.now() - t0) / 1000;
    const left = Math.ceil((end - f) / step);
    console.log(`frame ${f}/${end}  ${(done / el).toFixed(2)} fps  eta ${(left / (done / el) / 60).toFixed(1)} min`);
  }
}
console.log(`done ${done} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
await browser.close();
server.close();
