// Synthesizes the 2-minute soundtrack (Khmer-flavoured pentatonic score + SFX)
// Output: out/music.wav (44.1 kHz, 16-bit stereo)
const fs = require('fs');
const path = require('path');

const SR = 44100;
const DUR = 120;
const N = SR * DUR;
const L = new Float32Array(N);
const R = new Float32Array(N);
const RV = new Float32Array(N); // reverb send (mono)

let seed = 12345;
const rnd = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
};
const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
const TAU = Math.PI * 2;

function put(i, v, pan, send) {
  if (i < 0 || i >= N) return;
  const gl = Math.cos((pan + 1) * Math.PI * 0.25);
  const gr = Math.sin((pan + 1) * Math.PI * 0.25);
  L[i] += v * gl;
  R[i] += v * gr;
  RV[i] += v * send;
}

// generic partial-based struck instrument
function struck(t, f, amp, partials, pan = 0, send = 0.25, maxDur = 3) {
  const i0 = Math.floor(t * SR);
  const n = Math.floor(maxDur * SR);
  const ph = partials.map(() => rnd() * TAU);
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const att = Math.min(1, tt / 0.003);
    let v = 0;
    for (let p = 0; p < partials.length; p++) {
      const [mul, a, tau] = partials[p];
      v += a * Math.exp(-tt / tau) * Math.sin(TAU * f * mul * tt + ph[p]);
    }
    put(i0 + k, v * amp * att, pan, send);
  }
}
const roneat = (t, m, amp = 0.22, pan = 0.15) =>
  struck(t, mtof(m), amp, [[1, 1, 0.32], [3.93, 0.28, 0.07], [9.3, 0.08, 0.025], [2.0, 0.08, 0.15]], pan, 0.22, 1.4);
const kong = (t, m, amp = 0.18, pan = -0.2) =>
  struck(t, mtof(m), amp, [[1, 1, 1.3], [1.004, 0.5, 1.1], [2.76, 0.4, 0.55], [5.4, 0.2, 0.3], [8.93, 0.08, 0.18]], pan, 0.35, 3.5);
const chime = (t, m, amp = 0.12, pan = 0) =>
  struck(t, mtof(m), amp, [[1, 1, 0.9], [2.76, 0.25, 0.3], [5.4, 0.1, 0.12]], pan, 0.45, 2.5);
const gong = (t, amp = 0.5) =>
  struck(t, 72, amp, [[1, 1, 3.2], [1.51, 0.6, 2.4], [2.03, 0.4, 1.8], [2.71, 0.35, 1.2], [3.8, 0.2, 0.8], [5.1, 0.12, 0.5]], 0, 0.5, 7);
const bass = (t, m, amp = 0.3, dur = 0.6) =>
  struck(t, mtof(m), amp, [[1, 1, 0.35], [2, 0.25, 0.18], [3, 0.08, 0.1]], 0, 0.05, dur + 0.4);

function flute(t, m, dur, amp = 0.13, pan = 0.25) {
  const f = mtof(m);
  const i0 = Math.floor(t * SR);
  const n = Math.floor((dur + 0.15) * SR);
  let lp = 0;
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const env = Math.min(1, tt / 0.08) * (tt > dur ? Math.exp(-(tt - dur) / 0.06) : 1);
    const vib = 1 + 0.006 * Math.sin(TAU * 5.4 * tt) * Math.min(1, Math.max(0, (tt - 0.2) / 0.3));
    const ph = TAU * f * vib * tt;
    lp += 0.08 * (rnd() * 2 - 1 - lp);
    const v = Math.sin(ph) + 0.18 * Math.sin(2 * ph) + 0.06 * Math.sin(3 * ph) + lp * 0.35;
    put(i0 + k, v * env * amp, pan, 0.4);
  }
}

function pad(t, notes, dur, amp = 0.05, pan = 0) {
  const i0 = Math.floor(t * SR);
  const n = Math.floor((dur + 1.0) * SR);
  const oscs = [];
  for (const m of notes) for (const d of [-0.004, 0.004]) oscs.push({ f: mtof(m) * (1 + d), ph: rnd() * TAU });
  let lp = 0;
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const env = Math.min(1, tt / 0.7) * (tt > dur ? Math.exp(-(tt - dur) / 0.35) : 1);
    let v = 0;
    for (const o of oscs) {
      const p = TAU * o.f * tt + o.ph;
      for (let h = 1; h <= 6; h++) v += Math.sin(p * h) / h;
    }
    lp += 0.06 * (v - lp);
    put(i0 + k, lp * env * amp, pan + 0.2 * Math.sin(tt * 0.5), 0.5);
  }
}

function noiseBurst(t, dur, amp, tau, hp = 0.0, pan = 0, send = 0.1, lpCoef = 1) {
  const i0 = Math.floor(t * SR);
  const n = Math.floor(dur * SR);
  let prev = 0;
  let lp = 0;
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const w = rnd() * 2 - 1;
    const h = w - hp * prev;
    prev = w;
    lp += lpCoef * (h - lp);
    put(i0 + k, lp * amp * Math.exp(-tt / tau), pan, send);
  }
}
function skor(t, amp = 0.5) {
  const i0 = Math.floor(t * SR);
  const n = Math.floor(0.6 * SR);
  let ph = 0;
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const f = 55 + 70 * Math.exp(-tt / 0.04);
    ph += (TAU * f) / SR;
    put(i0 + k, Math.sin(ph) * amp * Math.exp(-tt / 0.22), 0, 0.08);
  }
  noiseBurst(t, 0.02, amp * 0.25, 0.005, 0.5);
}
function tak(t, amp = 0.22, pan = 0.3) {
  struck(t, 240, amp, [[1, 1, 0.05], [1.6, 0.6, 0.03]], pan, 0.1, 0.2);
  noiseBurst(t, 0.05, amp * 0.8, 0.012, 0.9, pan, 0.1);
}
function chhing(t, open = true, amp = 0.07, pan = -0.35) {
  struck(t, 1000, amp, [[3.15, 1, open ? 0.3 : 0.04], [4.27, 0.8, open ? 0.25 : 0.035], [5.62, 0.6, open ? 0.2 : 0.03], [7.21, 0.4, open ? 0.15 : 0.02]], pan, 0.2, open ? 1.0 : 0.15);
}
function crash(t, amp = 0.2) {
  noiseBurst(t, 2.2, amp, 0.7, 0.95, 0, 0.3);
}
function shutter(t) {
  noiseBurst(t, 0.02, 0.35, 0.004, 0.8, 0.1, 0.05);
  noiseBurst(t + 0.075, 0.03, 0.3, 0.006, 0.8, 0.1, 0.05);
  struck(t, 2200, 0.05, [[1, 1, 0.01]], 0.1, 0, 0.05);
}
function whoosh(tCenter, dur = 1.0, amp = 0.22) {
  const t0 = tCenter - dur * 0.6;
  const i0 = Math.floor(t0 * SR);
  const n = Math.floor(dur * SR);
  let lp = 0;
  for (let k = 0; k < n; k++) {
    const u = k / n;
    const env = Math.sin(Math.PI * u) ** 2;
    const coef = 0.02 + 0.25 * Math.sin(Math.PI * u);
    lp += coef * (rnd() * 2 - 1 - lp);
    put(i0 + k, lp * env * amp * 2.2, (u - 0.5) * 1.4, 0.3);
  }
}
function slide(t, f0, f1, dur, amp = 0.12, wobble = 0) {
  const i0 = Math.floor(t * SR);
  const n = Math.floor(dur * SR);
  let ph = 0;
  for (let k = 0; k < n; k++) {
    const u = k / n;
    const f = f0 * Math.pow(f1 / f0, u) * (1 + wobble * Math.sin(TAU * 7 * u * dur));
    ph += (TAU * f) / SR;
    const env = Math.min(1, u * 20) * Math.min(1, (1 - u) * 8);
    put(i0 + k, (Math.sin(ph) + 0.2 * Math.sin(2 * ph)) * env * amp, 0.2, 0.3);
  }
}
function bird(t, pan) {
  const reps = 2 + Math.floor(rnd() * 3);
  const base = 2600 + rnd() * 1400;
  for (let r = 0; r < reps; r++) {
    const t0 = t + r * (0.11 + rnd() * 0.05);
    const i0 = Math.floor(t0 * SR);
    const n = Math.floor(0.075 * SR);
    let ph = 0;
    for (let k = 0; k < n; k++) {
      const u = k / n;
      const f = base * (1 + 0.45 * u - 0.2 * u * u);
      ph += (TAU * f) / SR;
      put(i0 + k, Math.sin(ph) * Math.sin(Math.PI * u) * 0.045, pan, 0.35);
    }
  }
}
function horn(t) {
  for (const [dt, f] of [[0, 415], [0.18, 415]]) {
    const i0 = Math.floor((t + dt) * SR);
    const n = Math.floor(0.12 * SR);
    for (let k = 0; k < n; k++) {
      const tt = k / SR;
      let v = 0;
      for (let h = 1; h <= 9; h += 2) v += Math.sin(TAU * f * h * tt) / h;
      put(i0 + k, v * 0.07 * Math.min(1, tt / 0.005) * Math.min(1, (0.12 - tt) / 0.01), 0.1, 0.1);
    }
  }
}
function engine(t0, t1, amp = 0.12) {
  // two-stroke putt-putt of the tuk-tuk
  const i0 = Math.floor(t0 * SR);
  const n = Math.floor((t1 - t0) * SR);
  let lp = 0;
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const fade = Math.min(1, tt / 0.6) * Math.min(1, (t1 - t0 - tt) / 0.6);
    const rate = 13.5 + Math.sin(tt * 0.7) * 0.8;
    const puls = Math.pow(0.5 + 0.5 * Math.sin(TAU * rate * tt), 6);
    lp += 0.05 * (rnd() * 2 - 1 - lp);
    const v = (lp * 3 + Math.sin(TAU * 58 * tt) * 0.6 + Math.sin(TAU * 29 * tt) * 0.4) * puls;
    put(i0 + k, v * amp * fade, -0.1, 0.05);
  }
}
function crickets(t0, t1, amp = 0.012) {
  const i0 = Math.floor(t0 * SR);
  const n = Math.floor((t1 - t0) * SR);
  for (let k = 0; k < n; k++) {
    const tt = k / SR;
    const fade = Math.min(1, tt / 1.5) * Math.min(1, (t1 - t0 - tt) / 1.5);
    const chirp = Math.pow(Math.max(0, Math.sin(TAU * 3.1 * tt)), 8) * (0.5 + 0.5 * Math.sin(TAU * 38 * tt));
    put(i0 + k, Math.sin(TAU * 4700 * tt) * chirp * amp * fade, 0.5 * Math.sin(tt * 0.3), 0.3);
  }
}

// ---------- score helpers ----------
const G = { G3: 55, A3: 57, B3: 59, C4: 60, D4: 62, E4: 64, G4: 67, A4: 69, B4: 71, C5: 72, D5: 74, E5: 76, G5: 79, A5: 81, B5: 83, D6: 86, E6: 88, G6: 91 };
const CHORDS = {
  G: [55, 62, 67, 71],
  D: [50, 57, 62, 66],
  Em: [52, 59, 64, 67],
  C: [48, 55, 64, 67],
  Am: [45, 52, 60, 64],
  Bm: [47, 54, 62, 66],
};
const ROOT = { G: 43, D: 38, Em: 40, C: 36, Am: 45, Bm: 47 };

// main theme [midi|null, beats]
const THEME_A = [
  [74, 1], [71, 0.5], [74, 0.5], [76, 1], [74, 1],
  [71, 0.5], [69, 0.5], [67, 1], [69, 1], [71, 1],
  [74, 1], [76, 0.5], [79, 0.5], [81, 1], [79, 0.5], [76, 0.5],
  [74, 2], [null, 1], [71, 0.5], [74, 0.5],
];
const THEME_B = [
  [76, 1], [74, 0.5], [76, 0.5], [79, 1], [76, 1],
  [74, 0.5], [71, 0.5], [69, 1], [71, 1], [67, 1],
  [69, 1], [71, 0.5], [74, 0.5], [76, 1], [71, 1],
  [67, 3], [null, 1],
];
function playMelody(t0, bpm, notes, inst, tEnd = 1e9, transpose = 0, tremolo = false) {
  const b = 60 / bpm;
  let t = t0;
  for (const [m, d] of notes) {
    if (t >= tEnd) break;
    if (m !== null) {
      if (inst === 'flute') flute(t, m + transpose, Math.min(d * b * 0.95, tEnd - t));
      else if (tremolo && d >= 1) {
        for (let k = 0; k < d * 4; k++) if (t + k * b * 0.25 < tEnd) roneat(t + k * b * 0.25, m + transpose, k === 0 ? 0.22 : 0.12);
      } else if (inst === 'kong') kong(t, m + transpose);
      else roneat(t, m + transpose);
    }
    t += d * b;
  }
  return t;
}
function groove(t0, t1, bpm, o = {}) {
  const b = 60 / bpm;
  for (let k = 0; t0 + k * b * 0.5 < t1; k++) {
    const t = t0 + k * b * 0.5;
    const beat = k / 2;
    const inBar = beat % 4;
    if (o.skor !== false && (inBar === 0 || inBar === 2.5)) skor(t, (o.skorAmp ?? 0.45) * (inBar === 0 ? 1 : 0.7));
    if (o.tak !== false && (inBar === 1 || inBar === 3 || (o.busy && inBar === 3.5))) tak(t, o.takAmp ?? 0.18);
    if (o.chhing !== false && k % 2 === 1) chhing(t, (k / 2) % 2 < 1, o.chAmp ?? 0.06);
  }
}
function chordTrack(t0, t1, bpm, prog, beatsPer = 4, o = {}) {
  const b = 60 / bpm;
  let i = 0;
  for (let t = t0; t < t1 - 0.05; t += beatsPer * b, i++) {
    const ch = prog[i % prog.length];
    const dur = Math.min(beatsPer * b, t1 - t);
    if (o.pad !== false) pad(t, CHORDS[ch].map((m) => m + 12), dur, o.padAmp ?? 0.035);
    if (o.bass !== false)
      for (let k = 0; k < beatsPer; k += o.bassStep ?? 2) {
        if (t + k * b < t1) bass(t + k * b, ROOT[ch] + ((k / (o.bassStep ?? 2)) % 2 ? 7 : 0), o.bassAmp ?? 0.28);
      }
  }
}

// ---------- the score ----------
console.log('composing...');
// 1. Intro 0-9: pad swell, twinkles, title chimes
gong(0.15, 0.25);
pad(0.2, [55, 62, 67, 71, 74], 8.6, 0.04);
bass(0.2, 43, 0.25, 3);
for (let i = 0; i < 6; i++) chime(1.3 + i * 0.09, [79, 83, 86, 91, 95, 98][i], 0.1, -0.5 + i * 0.2);
{
  const tw = [74, 79, 81, 83, 86, 88, 91];
  for (let t = 3.2; t < 8.5; t += 0.3) roneat(t, tw[Math.floor(rnd() * tw.length)], 0.07 + 0.05 * rnd(), rnd() - 0.5);
}
playMelody(4.0, 100, [[67, 1], [71, 1], [74, 2], [76, 1], [74, 1], [79, 2]], 'kong');
whoosh(9.0, 1.0, 0.16);

// 2. Tuk-tuk ride 9-24: upbeat
engine(9.0, 24.1, 0.1);
horn(10.6);
groove(9.0, 24.0, 104, { busy: true });
chordTrack(9.0, 24.0, 104, ['G', 'D', 'Em', 'C', 'G', 'D', 'C', 'G'], 4, { padAmp: 0.022, bassStep: 1, bassAmp: 0.22 });
{
  const tEnd = playMelody(9.0 + 2 * (60 / 104), 104, THEME_A, 'roneat', 24.0);
  playMelody(tEnd, 104, THEME_B, 'roneat', 24.0);
}
for (let t = 12; t < 23; t += 2.5 + rnd() * 2) bird(t, rnd() * 1.6 - 0.8);
whoosh(24.0, 1.0, 0.24);

// 3. Arrival walk 24-38
groove(24.0, 36.0, 100, { skorAmp: 0.32, takAmp: 0.13, chAmp: 0.045 });
chordTrack(24.0, 38.0, 100, ['G', 'Em', 'C', 'D'], 4, { padAmp: 0.035, bassAmp: 0.2 });
playMelody(25.2, 100, THEME_A, 'kong', 35.5, 0);
for (let k = 0; k < 16; k++) roneat(36.0 + k * 0.125, [74, 76, 79, 81][k % 4], 0.05 + k * 0.009);
gong(37.95, 0.45);

// 4. Sunrise 38-49: majestic, flute
chordTrack(38.0, 49.0, 60, ['G', 'Em', 'C', 'D'], 2.75, { padAmp: 0.05, bassStep: 2.75, bassAmp: 0.22 });
playMelody(39.0, 60, [[74, 2], [76, 1], [79, 1.5], [76, 0.5], [74, 2], [71, 1], [74, 1]], 'flute', 48.6);
for (let t = 38.4; t < 48.5; t += 0.18) roneat(t, [79, 83, 86][Math.floor(t * 7) % 3], 0.02 + 0.02 * Math.sin((t - 38) * 0.6) ** 2, 0.5);
for (let t = 40; t < 48; t += 1.6 + rnd() * 1.8) bird(t, rnd() * 1.6 - 0.8);

// 5. Selfie 49-55: playful plucks
chordTrack(49.0, 55.0, 100, ['G', 'C', 'D', 'G'], 2.5, { padAmp: 0.045, bassAmp: 0.26 });
for (let k = 0; k < 16; k++) if (49.2 + k * 0.3 < 53.1) roneat(49.2 + k * 0.3, [67, 71, 74, 71, 76, 74, 71, 74][k % 8], 0.19);
shutter(53.2);
for (let i = 0; i < 4; i++) chime(53.35 + i * 0.07, [86, 91, 95, 98][i], 0.07, 0.3);
for (let k = 0; k < 6; k++) roneat(53.8 + k * 0.18, [79, 76, 74, 71, 74, 79][k], 0.12);
whoosh(55.0, 1.0, 0.24);

// 6. Bayon 55-75: playful, a little mysterious
groove(55.3, 74.5, 100, { skorAmp: 0.35, takAmp: 0.17, chAmp: 0.05 });
chordTrack(55.3, 75.0, 100, ['Em', 'C', 'G', 'D'], 4, { padAmp: 0.03, bassAmp: 0.22 });
{
  const motif = [[76, 0.5], [79, 0.5], [76, 0.5], [74, 0.5], [71, 1], [null, 1]];
  const answer = [[69, 0.5], [71, 0.5], [74, 0.5], [71, 0.5], [67, 1], [null, 1]];
  let t = 56.0;
  for (let r = 0; r < 4 && t < 74; r++) {
    t = playMelody(t, 100, motif, 'roneat', 74.5);
    t = playMelody(t, 100, answer, 'kong', 74.5, 0);
  }
}
slide(62.2, 520, 260, 0.35, 0.1, 0.12); // "boing": Leo copies the smile
slide(62.55, 260, 700, 0.3, 0.09, 0.08);
for (let k = 0; k < 14; k++) roneat(64.6 + k * 0.07, [79, 81, 83, 86, 83, 81, 79][k % 7], 0.1, 0.4); // giggles
whoosh(75.0, 1.0, 0.24);

// 7. Ta Prohm 75-95: jungle mystery
pad(75.2, [40, 47, 52, 59], 19.5, 0.035);
crickets(75.0, 95.0);
for (let t = 75.5; t < 94.5; t += 1.5) skor(t, 0.18);
{
  const em = [64, 67, 69, 71, 74, 76];
  const seq = [2, 3, 4, 3, 1, 2, 0, 1, 3, 5, 4, 3, 2, 1, 2, 0];
  seq.forEach((d, i) => kong(76.0 + i * 1.12, em[d] + 0, 0.15, (i % 2 ? 0.3 : -0.3)));
}
flute(84.0, 71, 2.0, 0.08);
flute(86.4, 74, 1.2, 0.08);
flute(87.8, 76, 2.4, 0.08);
for (let t = 76; t < 94; t += 1.2 + rnd() * 2.2) bird(t, rnd() * 1.6 - 0.8);
slide(86.0, 300, 600, 0.5, 0.05, 0); // Kai hops onto the stone
chime(87.1, 91, 0.06);

// 8. Sunset 95-107: warm reprise, drum roll, jump
gong(95.0, 0.35);
chordTrack(95.2, 104.6, 100, ['G', 'D', 'Em', 'C'], 4, { padAmp: 0.045, bassAmp: 0.24 });
groove(97.6, 104.6, 100, { skorAmp: 0.38, takAmp: 0.15, chAmp: 0.05 });
playMelody(95.6, 100, THEME_A, 'roneat', 104.5, 0, true);
playMelody(97.4, 100, [[67, 2], [71, 2], [74, 2], [72, 2]], 'flute', 104.4);
for (let k = 0; k < 24; k++) {
  const t = 104.6 + k * (1.0 / 24);
  skor(t, 0.12 + k * 0.012);
  if (k % 2) tak(t, 0.08 + k * 0.006);
}
slide(105.6, 400, 1600, 0.9, 0.09);
crash(105.62, 0.16);
skor(105.62, 0.55);

// 9. Freeze + finale 107-120
shutter(107.0);
crash(107.05, 0.12);
{
  const hits = [[107.6, 'G'], [108.8, 'C'], [110.0, 'D'], [111.2, 'G']];
  for (const [t, ch] of hits) {
    pad(t, CHORDS[ch].map((m) => m + 12), 1.2, 0.045);
    bass(t, ROOT[ch], 0.3, 1.0);
    for (let i = 0; i < 4; i++) roneat(t + i * 0.09, CHORDS[ch][i] + 12, 0.12, -0.3 + i * 0.2);
  }
}
playMelody(111.2, 100, THEME_B, 'roneat', 118.4);
pad(111.2, [55, 62, 67, 71], 7.0, 0.04);
for (let i = 0; i < 7; i++) chime(112.2 + i * 0.08, [79, 83, 86, 91, 95, 98, 103][i], 0.08, -0.6 + i * 0.2);
bass(111.2, 43, 0.3, 4);
gong(116.6, 0.4);

// ---------- reverb (Schroeder) ----------
console.log('reverb...');
function comb(inp, delay, fb, damp) {
  const out = new Float32Array(N);
  const buf = new Float32Array(delay);
  let idx = 0;
  let lp = 0;
  for (let i = 0; i < N; i++) {
    const y = buf[idx];
    lp = y * (1 - damp) + lp * damp;
    buf[idx] = inp[i] + lp * fb;
    out[i] = y;
    idx = (idx + 1) % delay;
  }
  return out;
}
function allpass(inp, delay, g) {
  const out = new Float32Array(N);
  const buf = new Float32Array(delay);
  let idx = 0;
  for (let i = 0; i < N; i++) {
    const b = buf[idx];
    const y = -inp[i] + b;
    buf[idx] = inp[i] + b * g;
    out[i] = y;
    idx = (idx + 1) % delay;
  }
  return out;
}
function reverb(delays) {
  const sum = new Float32Array(N);
  for (const d of delays) {
    const c = comb(RV, d, 0.82, 0.3);
    for (let i = 0; i < N; i++) sum[i] += c[i] * 0.25;
  }
  return allpass(allpass(sum, 556, 0.5), 441, 0.5);
}
const revL = reverb([1557, 1617, 1491, 1422]);
const revR = reverb([1580, 1640, 1514, 1445]);
for (let i = 0; i < N; i++) {
  L[i] += revL[i] * 0.55;
  R[i] += revR[i] * 0.55;
}

// ---------- master: fade, normalise, soft clip ----------
let peak = 0;
for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
const gain = 0.89 / peak;
const out = Buffer.alloc(44 + N * 4);
out.write('RIFF', 0);
out.writeUInt32LE(36 + N * 4, 4);
out.write('WAVE', 8);
out.write('fmt ', 12);
out.writeUInt32LE(16, 16);
out.writeUInt16LE(1, 20);
out.writeUInt16LE(2, 22);
out.writeUInt32LE(SR, 24);
out.writeUInt32LE(SR * 4, 28);
out.writeUInt16LE(4, 32);
out.writeUInt16LE(16, 34);
out.write('data', 36);
out.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const fade = Math.min(1, t / 0.3) * Math.min(1, Math.max(0, (DUR - t) / 1.4));
  const l = Math.tanh(L[i] * gain * 1.1) * fade;
  const r = Math.tanh(R[i] * gain * 1.1) * fade;
  out.writeInt16LE(Math.round(l * 32767), 44 + i * 4);
  out.writeInt16LE(Math.round(r * 32767), 44 + i * 4 + 2);
}
const file = path.join(__dirname, '../out/music.wav');
fs.mkdirSync(path.dirname(file), { recursive: true });
fs.writeFileSync(file, out);
console.log('wrote', file, 'peak', peak.toFixed(3));
