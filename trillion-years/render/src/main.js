// Frame compositor. The driver (render.mjs) calls window.renderFrame(t) for
// every frame; we render the active 3D scene(s), crossfade between scenes and
// draw the 2D overlays (titles, age counter, stat cards, subtitles).
import { THREE, clamp, smooth } from './lib.js';
import { SCENES, CHAPTERS } from './scenes/index.js';

const params = new URLSearchParams(location.search);
const W = +(params.get('w') || 1280);
const H = +(params.get('h') || 720);
const S = H / 1080;          // overlay scale
const XF = 1.6;              // crossfade length (s)

const timeline = await fetch('./timeline.json').then((r) => r.json());
await Promise.all([
  document.fonts.load(`700 ${80 * S}px Inter`),
  document.fonts.load(`600 ${40 * S}px Inter`),
  document.fonts.load(`500 ${30 * S}px Inter`),
  document.fonts.load(`300 ${30 * S}px Inter`),
]);

const renderer = new THREE.WebGLRenderer({ antialias: params.get('aa') !== '0', preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setClearColor(0x000000, 1);

const out = document.createElement('canvas');
out.width = W; out.height = H;
document.body.appendChild(out);
const g = out.getContext('2d');

const ctx = { renderer, W, H, aspect: W / H, pix: H / 1080 };
const built = {};
function getScene(i) {
  const sc = timeline.scenes[i];
  if (!built[sc.id]) {
    const info = {
      dur: sc.end - sc.start,
      cue: (k) => sc.cues[k].start - sc.start,
      cueEnd: (k) => sc.cues[k].end - sc.start,
    };
    built[sc.id] = SCENES[sc.id](ctx, info);
  }
  return built[sc.id];
}

function drawScene(i, T, alpha) {
  const sc = timeline.scenes[i];
  const obj = getScene(i);
  const local = T - sc.start;
  obj.update(local, sc.end - sc.start, T);
  renderer.render(obj.scene, obj.camera);
  g.globalAlpha = alpha;
  g.drawImage(renderer.domElement, 0, 0);
  g.globalAlpha = 1;
}

// ---------------- overlay helpers ----------------
function text(str, x, y, { size = 40, weight = 600, color = '#fff', align = 'center', alpha = 1, spacing = 0, glow = 0, shadow = 0.75, baseline = 'alphabetic' } = {}) {
  if (alpha <= 0.001) return;
  g.save();
  g.globalAlpha = clamp(alpha);
  g.font = `${weight} ${size * S}px Inter`;
  g.textAlign = align;
  g.textBaseline = baseline;
  if (spacing) g.letterSpacing = `${spacing * S}px`;
  if (shadow) {
    g.shadowColor = `rgba(0,0,0,${shadow})`;
    g.shadowBlur = 14 * S;
    g.shadowOffsetY = 2 * S;
  }
  if (glow) {
    g.shadowColor = color;
    g.shadowBlur = glow * S;
    g.shadowOffsetY = 0;
    g.fillStyle = color;
    g.fillText(str, x, y);
    g.shadowColor = `rgba(0,0,0,${shadow})`;
    g.shadowBlur = 10 * S;
  }
  g.fillStyle = color;
  g.fillText(str, x, y);
  g.restore();
}

function wrap(str, maxW, font) {
  g.font = font;
  const words = str.split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  if (cur) lines.push(cur);
  return lines;
}

// Split every cue into on-screen chunks of at most two lines.
const SUB_FONT = `500 ${38 * S}px Inter`;
const SUB_MAX = W * 0.74;
const subChunks = [];
for (const sc of timeline.scenes) {
  for (const cue of sc.cues) {
    const lines = wrap(cue.text, SUB_MAX, SUB_FONT);
    const groups = [];
    for (let i = 0; i < lines.length; i += 2) groups.push(lines.slice(i, i + 2));
    // balance a trailing single short line into the previous chunk if possible
    const total = cue.text.length;
    let t = cue.start;
    for (const grp of groups) {
      const share = grp.join(' ').length / total;
      const d = (cue.end - cue.start) * share;
      subChunks.push({ start: t, end: t + d, lines: grp });
      t += d;
    }
  }
}

function drawSubtitles(T) {
  const c = subChunks.find((s) => T >= s.start - 0.05 && T < s.end + 0.35);
  if (!c) return;
  const a = Math.min(smooth(c.start - 0.05, c.start + 0.12, T), 1 - smooth(c.end + 0.15, c.end + 0.35, T));
  const lh = 50 * S;
  const base = H - 70 * S - (c.lines.length - 1) * lh;
  c.lines.forEach((ln, i) => {
    text(ln, W / 2, base + i * lh, { size: 38, weight: 500, alpha: a, shadow: 0.95 });
  });
}

function fmtInt(n) { return Math.round(n).toLocaleString('en-US'); }
function wordy(n) {
  const u = [[1e12, 'trillion'], [1e9, 'billion'], [1e6, 'million'], [1e3, 'thousand']];
  for (const [v, w] of u) if (n >= v) {
    const x = n / v;
    return `${x >= 100 ? Math.round(x) : x >= 10 ? x.toFixed(1).replace(/\.0$/, '') : x.toFixed(2).replace(/\.?0+$/, '')} ${w}`;
  }
  return '';
}

function ageAt(T) {
  const i = sceneIndex(T);
  const sc = timeline.scenes[i];
  const [a0, a1] = sc.age;
  if (a1 === 0) return null;
  if (a0 === a1) return a0;
  const p = smooth(sc.start + 1.0, sc.end - 0.5, T);
  const l = Math.log10(a0) + (Math.log10(a1) - Math.log10(a0)) * p;
  return Math.pow(10, l);
}

function drawAge(T) {
  const age = ageAt(T);
  if (age == null) return;
  const iOut = timeline.scenes.findIndex((s) => s.id === 'outro');
  const iCen = timeline.scenes.findIndex((s) => s.id === 'century');
  let a = smooth(timeline.scenes[iCen].start + 0.5, timeline.scenes[iCen].start + 2.0, T);
  a *= 1 - smooth(timeline.scenes[iOut].start + 3, timeline.scenes[iOut].start + 6, T);
  if (a <= 0) return;
  const x = 64 * S, y = 70 * S;
  text('YOUR AGE', x, y, { size: 18, weight: 600, align: 'left', alpha: a * 0.75, spacing: 4, color: '#9fd8ff' });
  const big = age < 100 ? `${Math.round(age)} years` : `${fmtInt(age)} years`;
  text(big, x, y + 48 * S, { size: 42, weight: 700, align: 'left', alpha: a, glow: 12, color: '#ffffff' });
  const w = wordy(age);
  if (w) text(w, x, y + 82 * S, { size: 22, weight: 400, align: 'left', alpha: a * 0.8, color: '#cfe6ff' });
  // log-scale progress bar, 10^1 .. 10^12
  const bx = x, by = y + 108 * S, bw = 420 * S, bh = 4 * S;
  g.save();
  g.globalAlpha = a;
  g.fillStyle = 'rgba(255,255,255,0.18)';
  g.fillRect(bx, by, bw, bh);
  const p = clamp((Math.log10(Math.max(age, 10)) - 1) / 11);
  const grd = g.createLinearGradient(bx, 0, bx + bw, 0);
  grd.addColorStop(0, '#5fd3ff'); grd.addColorStop(0.5, '#b18cff'); grd.addColorStop(1, '#ff7a59');
  g.fillStyle = grd;
  g.shadowColor = '#8fd8ff'; g.shadowBlur = 10 * S;
  g.fillRect(bx, by, bw * p, bh);
  g.shadowBlur = 0;
  for (let k = 1; k <= 12; k++) {
    const tx = bx + bw * (k - 1) / 11;
    g.fillStyle = k <= 1 + p * 11 + 1e-6 ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.35)';
    g.fillRect(tx - 1 * S, by - 4 * S, 2 * S, bh + 8 * S);
  }
  g.restore();
  const labels = { 1: '10', 3: '1K', 6: '1M', 9: '1B', 12: '1T' };
  for (const [k, l] of Object.entries(labels)) {
    text(l, bx + bw * (k - 1) / 11, by + 28 * S, { size: 15, weight: 500, alpha: a * 0.6, color: '#d8ecff', shadow: 0.6 });
  }
}

function drawCard(T) {
  for (const sc of timeline.scenes) for (const cue of sc.cues) {
    if (!cue.card) continue;
    const t0 = cue.start + 0.15, t1 = cue.end + 1.2;
    if (T < t0 - 0.1 || T > t1 + 0.6) continue;
    const a = Math.min(smooth(t0, t0 + 0.5, T), 1 - smooth(t1, t1 + 0.6, T));
    const [big, small] = cue.card.split('|');
    const rise = (1 - smooth(t0, t0 + 0.8, T)) * 18 * S;
    const yb = H * 0.23 + rise;
    const size = big.length > 20 ? 60 : big.length > 14 ? 76 : 92;
    text(big, W / 2, yb, { size, weight: 700, alpha: a, glow: 26, color: '#ffffff', spacing: 2 });
    if (small) text(small.toUpperCase(), W / 2, yb + 52 * S, { size: 24, weight: 600, alpha: a * 0.9, spacing: 6, color: '#a9dcff' });
  }
}

function drawChapter(T) {
  timeline.scenes.forEach((sc, i) => {
    const name = CHAPTERS[sc.id];
    if (!name) return;
    const t0 = sc.start + 0.9, t1 = sc.start + 6.0;
    if (T < t0 || T > t1 + 0.8) return;
    const a = Math.min(smooth(t0, t0 + 0.7, T), 1 - smooth(t1, t1 + 0.8, T));
    const x = W - 64 * S, y = 70 * S;
    text(`CHAPTER ${String(i).padStart(2, '0')}`, x, y, { size: 18, weight: 600, align: 'right', alpha: a * 0.75, spacing: 5, color: '#ffd59a' });
    g.save(); g.globalAlpha = a * 0.6; g.fillStyle = '#ffd59a';
    const lw = 200 * S * smooth(t0, t0 + 1.2, T);
    g.fillRect(x - lw, y + 12 * S, lw, 2 * S); g.restore();
    text(name, x, y + 52 * S, { size: 34, weight: 700, align: 'right', alpha: a, spacing: 2 });
  });
}

function drawTitle(T) {
  // opening title
  {
    const a = Math.min(smooth(0.8, 2.2, T), 1 - smooth(8.8, 10.2, T));
    if (a > 0) {
      const rise = (1 - smooth(0.8, 3.0, T)) * 20 * S;
      text('WHAT IF YOU LIVED FOR', W / 2, H * 0.2 + rise, { size: 34, weight: 300, alpha: a, spacing: 12, color: '#cfe8ff' });
      text('1 TRILLION YEARS?', W / 2, H * 0.2 + 92 * S + rise, { size: 96, weight: 700, alpha: a, spacing: 6, glow: 30, color: '#ffffff' });
    }
  }
  // closing lines
  const last = timeline.scenes[timeline.scenes.length - 1];
  const cues = last.cues;
  const lastCue = cues[cues.length - 1];
  const tEnd = timeline.duration;
  {
    const t0 = lastCue.end + 0.6;
    const a = Math.min(smooth(t0, t0 + 1.2, T), 1 - smooth(tEnd - 2.6, tEnd - 1.2, T));
    if (a > 0) {
      text('WHAT IF YOU LIVED FOR', W / 2, H * 0.43, { size: 30, weight: 300, alpha: a, spacing: 12, color: '#cfe8ff' });
      text('1 TRILLION YEARS?', W / 2, H * 0.43 + 84 * S, { size: 84, weight: 700, alpha: a, spacing: 6, glow: 30 });
      text('Make it count.', W / 2, H * 0.43 + 150 * S, { size: 30, weight: 400, alpha: a * smooth(t0 + 1.0, t0 + 2.2, T) * 0.85, color: '#ffe2b8' });
    }
  }
}

let vignette;
function drawVignette() {
  if (!vignette) {
    vignette = g.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0);
    vignette.addColorStop(0, 'rgba(0,0,0,0)');
    vignette.addColorStop(1, 'rgba(0,0,0,0.55)');
  }
  g.fillStyle = vignette;
  g.fillRect(0, 0, W, H);
  // soft bottom gradient for subtitle legibility
  const bg = g.createLinearGradient(0, H * 0.78, 0, H);
  bg.addColorStop(0, 'rgba(0,0,0,0)');
  bg.addColorStop(1, 'rgba(0,0,0,0.45)');
  g.fillStyle = bg;
  g.fillRect(0, H * 0.78, W, H * 0.22);
}

function sceneIndex(T) {
  const sc = timeline.scenes;
  for (let i = 0; i < sc.length; i++) if (T < sc[i].end) return i;
  return sc.length - 1;
}

window.renderFrame = (T, quality = 0.92) => {
  g.fillStyle = '#000';
  g.fillRect(0, 0, W, H);
  const i = sceneIndex(T);
  const sc = timeline.scenes;
  const into = T - sc[i].start, left = sc[i].end - T;
  if (i > 0 && into < XF / 2) {
    drawScene(i - 1, T, 1);
    drawScene(i, T, smooth(0, 1, 0.5 + into / XF));
  } else if (i < sc.length - 1 && left < XF / 2) {
    drawScene(i, T, 1);
    drawScene(i + 1, T, smooth(0, 1, 0.5 - left / XF));
  } else {
    drawScene(i, T, 1);
  }
  drawVignette();
  drawTitle(T);
  drawChapter(T);
  drawAge(T);
  drawCard(T);
  drawSubtitles(T);
  // global fade in / out
  const f = Math.min(smooth(0, 1.6, T), 1 - smooth(timeline.duration - 1.4, timeline.duration - 0.05, T));
  if (f < 1) {
    g.fillStyle = `rgba(0,0,0,${1 - f})`;
    g.fillRect(0, 0, W, H);
  }
  return out.toDataURL('image/jpeg', quality);
};
window.timeline = timeline;
window.__built = built;
window.ready = true;
