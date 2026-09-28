import { TRANSITIONS, DURATION } from './timeline.js';
import { rng, clamp, smooth, easeOut } from './util.js';

const EMOJI = { pin: '📍', temple: '🛕', sun: '🌅', smile: '😊', tree: '🌳', camera: '📸' };
const easeOutBack = (x) => {
  x = clamp(x);
  const c1 = 1.9;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function vignette(ctx, W, H, k = 0.32) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.0);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, `rgba(20,10,30,${k})`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

function outlinedText(ctx, text, x, y, fill, stroke, lw, shadow = true) {
  ctx.lineJoin = 'round';
  if (shadow) {
    ctx.save();
    ctx.fillStyle = 'rgba(30,10,40,0.35)';
    ctx.fillText(text, x + lw * 0.5, y + lw * 0.9);
    ctx.restore();
  }
  if (lw > 0) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lw;
    ctx.strokeText(text, x, y);
  }
  ctx.fillStyle = fill;
  ctx.fillText(text, x, y);
}

function titleCard(ctx, W, H, t, s) {
  if (t < 0.6 || t > 8.9) return;
  const out = 1 - smooth(7.9, 8.7, t);
  ctx.save();
  ctx.globalAlpha = out;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  // soft band behind the title
  const g = ctx.createLinearGradient(0, H * 0.06, 0, H * 0.66);
  g.addColorStop(0, 'rgba(30,20,60,0)');
  g.addColorStop(0.5, `rgba(30,20,60,${0.26 * smooth(0.6, 1.6, t)})`);
  g.addColorStop(1, 'rgba(30,20,60,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, H * 0.06, W, H * 0.6);

  const a1 = easeOutBack((t - 0.9) / 0.6);
  ctx.font = `600 ${64 * s}px Fredoka`;
  ctx.globalAlpha = out * clamp((t - 0.9) / 0.3);
  outlinedText(ctx, 'A Trip to', W / 2, H * 0.2 + (1 - a1) * 40 * s, '#ffffff', '#3a2456', 10 * s);

  // ANGKOR with bouncing letters
  const word = 'ANGKOR';
  ctx.font = `700 ${200 * s}px Fredoka`;
  const widths = [...word].map((ch) => ctx.measureText(ch).width + 6 * s);
  const total = widths.reduce((a, b) => a + b, 0);
  let x = W / 2 - total / 2;
  const grad = ctx.createLinearGradient(0, H * 0.26, 0, H * 0.42);
  grad.addColorStop(0, '#ffe38a');
  grad.addColorStop(0.55, '#ffb63a');
  grad.addColorStop(1, '#ff7a3a');
  [...word].forEach((ch, i) => {
    const ti = t - 1.3 - i * 0.09;
    const k = easeOutBack(ti / 0.55);
    const bob = Math.sin(t * 2.2 + i * 0.7) * 6 * s * smooth(2.5, 3.2, t);
    ctx.save();
    ctx.globalAlpha = out * clamp(ti / 0.15);
    const cx = x + widths[i] / 2;
    const cy = H * 0.39 + bob;
    ctx.translate(cx, cy);
    ctx.scale(k, k);
    ctx.rotate((1 - clamp(ti / 0.55)) * (i % 2 ? 0.3 : -0.3));
    ctx.textAlign = 'center';
    ctx.lineJoin = 'round';
    ctx.fillStyle = 'rgba(40,10,50,0.45)';
    ctx.fillText(ch, 8 * s, 14 * s);
    ctx.strokeStyle = '#3a2456';
    ctx.lineWidth = 18 * s;
    ctx.strokeText(ch, 0, 0);
    ctx.fillStyle = grad;
    ctx.fillText(ch, 0, 0);
    ctx.restore();
    x += widths[i];
  });

  // Khmer subtitle
  const a3 = clamp((t - 2.4) / 0.6);
  ctx.globalAlpha = out * a3;
  ctx.font = `400 ${50 * s}px Moul`;
  outlinedText(ctx, 'ដំណើរកម្សាន្តទៅអង្គរ', W / 2, H * 0.505 + (1 - a3) * 20 * s, '#fff4d8', '#3a2456', 8 * s);
  const a4 = clamp((t - 3.1) / 0.6);
  ctx.globalAlpha = out * a4;
  ctx.font = `500 ${36 * s}px Fredoka`;
  outlinedText(ctx, 'a 3D cartoon adventure in Cambodia', W / 2, H * 0.58, '#ffffff', '#3a2456', 7 * s, false);
  ctx.restore();
}

function drawCaption(ctx, W, H, s, cap) {
  const inK = easeOutBack(cap.age / 0.6);
  const outK = smooth(0.45, 0, cap.left);
  const x0 = 70 * s - (1 - inK) * 700 * s - outK * 700 * s;
  const y0 = cap.top ? 60 * s : H - 210 * s;
  ctx.save();
  ctx.font = `700 ${46 * s}px Fredoka`;
  const tw = ctx.measureText(cap.title).width;
  ctx.font = `400 ${29 * s}px Fredoka`;
  const sw = ctx.measureText(cap.sub).width;
  const w = Math.max(tw, sw) + 175 * s;
  const h = 128 * s;
  ctx.shadowColor = 'rgba(20,10,40,0.35)';
  ctx.shadowBlur = 24 * s;
  ctx.shadowOffsetY = 8 * s;
  roundRect(ctx, x0, y0, w, h, h / 2);
  ctx.fillStyle = 'rgba(255,255,255,0.94)';
  ctx.fill();
  ctx.shadowColor = 'transparent';
  // icon disc
  const cx = x0 + h / 2;
  const cy = y0 + h / 2;
  const g = ctx.createLinearGradient(cx, cy - 50 * s, cx, cy + 50 * s);
  g.addColorStop(0, '#ffcf5a');
  g.addColorStop(1, '#ff8a4a');
  ctx.beginPath();
  ctx.arc(cx, cy, h / 2 - 12 * s, 0, Math.PI * 2);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.font = `${52 * s}px "Noto Color Emoji"`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(EMOJI[cap.emoji] || '✨', cx, cy + 3 * s);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = '#2d2448';
  ctx.font = `700 ${46 * s}px Fredoka`;
  ctx.fillText(cap.title, x0 + h + 10 * s, y0 + 60 * s);
  ctx.fillStyle = '#6a5e86';
  ctx.font = `400 ${29 * s}px Fredoka`;
  ctx.fillText(cap.sub, x0 + h + 10 * s, y0 + 100 * s);
  ctx.restore();
}

function drawBubble(ctx, W, H, s, b) {
  if (b.behind) return;
  const k = easeOutBack(b.age / 0.28);
  const a = clamp(b.left / 0.18);
  const fs = (b.big ? 54 : 38) * s;
  ctx.save();
  ctx.font = `600 ${fs}px Fredoka`;
  const tw = ctx.measureText(b.text).width;
  const pw = tw + 56 * s;
  const ph = fs + 40 * s;
  let bx = b.sx + b.dx * s - pw / 2;
  let by = b.sy - ph - 58 * s;
  bx = clamp(bx, 24 * s, W - pw - 24 * s);
  by = clamp(by, 24 * s, H - ph - 24 * s);
  const ax = b.sx;
  const ay = b.sy - 12 * s;
  ctx.globalAlpha = a;
  ctx.translate(ax, ay);
  ctx.scale(k, k);
  ctx.translate(-ax, -ay);
  ctx.shadowColor = 'rgba(20,10,40,0.3)';
  ctx.shadowBlur = 16 * s;
  ctx.shadowOffsetY = 6 * s;
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#2d2448';
  ctx.lineWidth = 5 * s;
  // tail
  const tx = clamp(ax, bx + ph * 0.5, bx + pw - ph * 0.5);
  roundRect(ctx, bx, by, pw, ph, ph / 2);
  ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.beginPath();
  ctx.moveTo(tx - 18 * s, by + ph - 3 * s);
  ctx.lineTo(ax, ay);
  ctx.lineTo(tx + 18 * s, by + ph - 3 * s);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  roundRect(ctx, bx, by, pw, ph, ph / 2);
  ctx.stroke();
  // cover the seam between tail and bubble
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(tx - 15 * s, by + ph - 8 * s, 30 * s, 9 * s);
  ctx.fillStyle = b.big ? '#ff5a3a' : '#2d2448';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(b.text, bx + pw / 2, by + ph / 2 + 2 * s);
  ctx.restore();
}

function transitions(ctx, W, H, t) {
  for (const tr of TRANSITIONS) {
    const dt = t - tr.t;
    if (Math.abs(dt) > tr.d) continue;
    if (tr.type === 'fade') {
      ctx.fillStyle = `rgba(10,6,20,${1 - Math.abs(dt) / tr.d})`;
      ctx.fillRect(0, 0, W, H);
    } else {
      const maxR = Math.hypot(W, H) * 0.62;
      const k = dt < 0 ? 1 - (dt + tr.d) / tr.d : dt / tr.d;
      const r = maxR * (dt < 0 ? Math.pow(k, 2) : easeOut(k));
      const r2 = dt < 0 ? maxR * Math.pow(1 - clamp((dt + tr.d) / tr.d), 2) : r;
      ctx.beginPath();
      ctx.rect(0, 0, W, H);
      ctx.arc(tr.cx * W, tr.cy * H, Math.max(0.01, r2), 0, Math.PI * 2, true);
      ctx.fillStyle = '#120a1e';
      ctx.fill('evenodd');
    }
  }
}

// ---------- ending: polaroid + confetti + The End ----------
const CONF = (() => {
  const r = rng(2026);
  const cols = ['#ff5a7a', '#ffd23a', '#3ad0ff', '#7aff8a', '#b07aff', '#ff9a3a'];
  return Array.from({ length: 140 }, () => ({ x: r(), d: r() * 2.5, sp: 0.12 + r() * 0.12, sw: r() * 6, w: 10 + r() * 12, h: 6 + r() * 8, c: cols[Math.floor(r() * cols.length)], rot: r() * 6 }));
})();

function ending(ctx, W, H, s, e, t, glCanvas) {
  // e = seconds since freeze frame
  const shrink = easeInOut2(clamp((e - 0.55) / 1.1));
  if (e > 0.5) {
    // blurred, warm background
    ctx.save();
    ctx.filter = `blur(${18 * s}px) brightness(0.62) saturate(1.2)`;
    ctx.drawImage(glCanvas, -40 * s, -40 * s, W + 80 * s, H + 80 * s);
    ctx.restore();
    const g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, 'rgba(255,140,90,0.25)');
    g.addColorStop(1, 'rgba(90,40,140,0.35)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    // bokeh
    const r = rng(7);
    for (let i = 0; i < 26; i++) {
      const bx = r() * W;
      const by = ((r() * H - e * 12 * s * (0.5 + r())) % H + H) % H;
      const br = (18 + r() * 60) * s;
      ctx.beginPath();
      ctx.arc(bx, by, br, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,${200 + Math.floor(r() * 55)},160,${0.06 + r() * 0.08})`;
      ctx.fill();
    }
    // polaroid
    const endMove = easeInOut2(clamp((e - 4.6) / 1.2));
    const scale = 1 - shrink * 0.4 - endMove * 0.1;
    const cx = W / 2 - endMove * W * 0.17;
    const cy = H / 2 - shrink * 0.02 * H;
    const rot = (-3.5 * shrink - 2.5 * endMove) * (Math.PI / 180);
    const iw = W * scale;
    const ih = H * scale;
    const pad = 28 * s * shrink;
    const padB = 150 * s * shrink;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);
    ctx.shadowColor = 'rgba(20,10,30,0.5)';
    ctx.shadowBlur = 50 * s * shrink;
    ctx.shadowOffsetY = 18 * s * shrink;
    ctx.fillStyle = '#fbf8f1';
    ctx.fillRect(-iw / 2 - pad, -ih / 2 - pad, iw + pad * 2, ih + pad + padB);
    ctx.shadowColor = 'transparent';
    ctx.drawImage(glCanvas, -iw / 2, -ih / 2, iw, ih);
    // tape
    ctx.fillStyle = 'rgba(255,230,160,0.8)';
    ctx.save();
    ctx.translate(0, -ih / 2 - pad);
    ctx.rotate(0.04);
    ctx.fillRect(-90 * s * shrink, -22 * s, 180 * s * shrink, 44 * s * shrink);
    ctx.restore();
    // handwriting caption
    const ca = clamp((e - 1.8) / 0.8);
    ctx.globalAlpha = ca;
    ctx.fillStyle = '#3a3050';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = `600 ${58 * s * Math.max(scale, 0.5)}px Fredoka`;
    ctx.fillText('Angkor, Cambodia  ♥  Best trip ever!', 0, ih / 2 + padB * 0.52);
    ctx.restore();
  }
  // confetti
  if (e > 1.0) {
    for (const p of CONF) {
      const age = e - 1.0 - p.d;
      if (age < 0) continue;
      const y = -30 * s + age * p.sp * H * 1.1;
      if (y > H + 40 * s) continue;
      const x = p.x * W + Math.sin(age * 2 + p.sw) * 40 * s;
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(p.rot + age * 3);
      ctx.scale(1, Math.cos(age * 5 + p.sw));
      ctx.fillStyle = p.c;
      ctx.fillRect((-p.w / 2) * s, (-p.h / 2) * s, p.w * s, p.h * s);
      ctx.restore();
    }
  }
  // The End
  if (e > 5.2) {
    const x = W * 0.8;
    ctx.save();
    ctx.textAlign = 'center';
    const k1 = easeOutBack((e - 5.2) / 0.7);
    ctx.globalAlpha = clamp((e - 5.2) / 0.2);
    ctx.translate(x, H * 0.4);
    ctx.scale(k1, k1);
    ctx.rotate(Math.sin(e * 2) * 0.03);
    ctx.font = `700 ${128 * s}px Fredoka`;
    const g = ctx.createLinearGradient(0, -90 * s, 0, 20 * s);
    g.addColorStop(0, '#fff09a');
    g.addColorStop(1, '#ff9a3a');
    outlinedText(ctx, 'The End', 0, 0, g, '#3a2456', 16 * s);
    ctx.restore();
    const k2 = clamp((e - 6.0) / 0.6);
    ctx.save();
    ctx.textAlign = 'center';
    ctx.globalAlpha = k2;
    ctx.font = `400 ${60 * s}px Moul`;
    outlinedText(ctx, 'អរគុណ!', x, H * 0.55 + (1 - k2) * 20 * s, '#ffffff', '#3a2456', 9 * s);
    const k3 = clamp((e - 6.7) / 0.6);
    ctx.globalAlpha = k3;
    ctx.font = `600 ${44 * s}px Fredoka`;
    outlinedText(ctx, 'Thanks for watching!', x, H * 0.64 + (1 - k3) * 20 * s, '#ffffff', '#3a2456', 8 * s);
    const k4 = clamp((e - 7.6) / 0.8);
    ctx.globalAlpha = k4 * 0.9;
    ctx.font = `400 ${28 * s}px Fredoka`;
    outlinedText(ctx, 'Sokha  ·  Mia  ·  Leo  ·  Nita  ·  Kai', x, H * 0.72, '#fff4e0', '#3a2456', 6 * s, false);
    ctx.restore();
  }
}
const easeInOut2 = (x) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);

export function drawOverlay(ctx, W, H, t, shot, info, glCanvas) {
  const s = H / 1080;
  if (info.polaroid !== undefined) {
    ending(ctx, W, H, s, info.polaroid, t, glCanvas);
  }
  vignette(ctx, W, H, info.polaroid !== undefined ? 0.2 : 0.3);
  titleCard(ctx, W, H, t, s);
  for (const c of info.captions) drawCaption(ctx, W, H, s, c);
  for (const b of info.bubbles || []) drawBubble(ctx, W, H, s, b);
  // camera flashes
  let flash = info.flash || 0;
  if (info.polaroid !== undefined) {
    const e = info.polaroid;
    flash = Math.max(flash, e < 0.1 ? e / 0.1 : 1 - clamp((e - 0.1) / 0.55));
  }
  if (flash > 0) {
    ctx.fillStyle = `rgba(255,255,255,${clamp(flash)})`;
    ctx.fillRect(0, 0, W, H);
  }
  transitions(ctx, W, H, t);
  // final fade out
  if (t > DURATION - 1.3) {
    ctx.fillStyle = `rgba(0,0,0,${clamp((t - (DURATION - 1.3)) / 1.1)})`;
    ctx.fillRect(0, 0, W, H);
  }
  if (t < 0.6) {
    ctx.fillStyle = `rgba(0,0,0,${1 - t / 0.6})`;
    ctx.fillRect(0, 0, W, H);
  }
}
