// Production renderer: renders the whole film into resumable 5-second H.264
// segments, then concatenates them and muxes the soundtrack.
//   node tools/render.js [--fps 24] [--w 1920] [--h 1080] [--workers 2] [--out out/angkor_trip.mp4]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const ffmpeg = require('ffmpeg-static');
const openRenderer = require('./browser');

const args = Object.fromEntries(
  process.argv
    .slice(2)
    .join(' ')
    .split('--')
    .filter(Boolean)
    .map((s) => s.trim().split(/\s+/))
);
const FPS = +(args.fps || 24);
const W = +(args.w || 1920);
const H = +(args.h || 1080);
const WORKERS = +(args.workers || 2);
const DURATION = 120;
const SEG = FPS * 5;
const ROOT = path.resolve(__dirname, '..');
const SEGDIR = path.join(ROOT, 'out', `seg_${W}x${H}_${FPS}`);
const OUT = path.resolve(ROOT, args.out || 'out/angkor_trip.mp4');
fs.mkdirSync(SEGDIR, { recursive: true });

const total = DURATION * FPS;
const segs = [];
for (let s = 0; s * SEG < total; s++) segs.push({ i: s, f0: s * SEG, f1: Math.min(total, (s + 1) * SEG) });
const segFile = (s) => path.join(SEGDIR, `seg_${String(s.i).padStart(3, '0')}.mp4`);
const todo = segs.filter((s) => !fs.existsSync(segFile(s)));
const t0 = Date.now();
let framesDone = 0;
const framesTodo = todo.reduce((a, s) => a + s.f1 - s.f0, 0);
const log = (...m) => {
  const line = `[${new Date().toISOString().slice(11, 19)}] ${m.join(' ')}`;
  console.log(line);
  fs.appendFileSync(path.join(ROOT, 'out', 'render.log'), line + '\n');
};
log(`render ${W}x${H}@${FPS} segments ${segs.length} todo ${todo.length} frames ${framesTodo}`);

function encodeSegment(file) {
  const tmp = file + '.part.mp4';
  const p = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-r', String(FPS), tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => p.on('close', (c) => (c === 0 ? (fs.renameSync(tmp, file), res()) : rej(new Error('ffmpeg ' + c)))));
  return {
    write: (buf) => new Promise((res) => (p.stdin.write(buf) ? res() : p.stdin.once('drain', res))),
    end: () => (p.stdin.end(), done),
  };
}

async function worker(id) {
  const r = await openRenderer({ w: W, h: H });
  while (todo.length) {
    const s = todo.shift();
    const enc = encodeSegment(segFile(s));
    const st = Date.now();
    for (let f = s.f0; f < s.f1; f++) {
      const buf = await r.frame(f / FPS, 0.95);
      await enc.write(buf);
      framesDone++;
    }
    await enc.end();
    const el = (Date.now() - t0) / 1000;
    const eta = (el / framesDone) * (framesTodo - framesDone);
    log(`w${id} seg ${s.i} done in ${((Date.now() - st) / 1000).toFixed(0)}s | ${framesDone}/${framesTodo} frames | elapsed ${(el / 60).toFixed(1)}m | eta ${(eta / 60).toFixed(1)}m`);
  }
  await r.close();
}

function run(argv) {
  return new Promise((res, rej) => {
    const p = spawn(ffmpeg, argv, { stdio: 'inherit' });
    p.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  });
}

(async () => {
  await Promise.all(Array.from({ length: Math.min(WORKERS, todo.length) }, (_, i) => worker(i)));
  const list = path.join(SEGDIR, 'list.txt');
  fs.writeFileSync(list, segs.map((s) => `file '${segFile(s)}'`).join('\n'));
  const video = path.join(SEGDIR, 'video.mp4');
  await run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);
  const music = path.join(ROOT, 'out', 'music.wav');
  await run(['-y', '-loglevel', 'error', '-i', video, '-i', music, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', OUT]);
  log('wrote', OUT, (fs.statSync(OUT).size / 1e6).toFixed(1) + ' MB', 'total', ((Date.now() - t0) / 60000).toFixed(1) + 'm');
})().catch((e) => {
  log('ERROR', e.stack || e);
  process.exit(1);
});
