// Render still frames for inspection: node tools/stills.js 12.5 40 ... [--w 960 --h 540]
const fs = require('fs');
const path = require('path');
const openRenderer = require('./browser');
(async () => {
  const args = process.argv.slice(2);
  let w = 960, h = 540;
  const times = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--w') w = +args[++i];
    else if (args[i] === '--h') h = +args[++i];
    else times.push(+args[i]);
  }
  const t0 = Date.now();
  const r = await openRenderer({ w, h });
  console.log('init ms', Date.now() - t0);
  fs.mkdirSync(path.join(__dirname, '../out/stills'), { recursive: true });
  for (const t of times) {
    const s = Date.now();
    const buf = await r.frame(t, 0.9);
    const f = path.join(__dirname, `../out/stills/t${t.toFixed(2)}.jpg`);
    fs.writeFileSync(f, buf);
    console.log(f, 'ms', Date.now() - s);
  }
  await r.close();
})();
