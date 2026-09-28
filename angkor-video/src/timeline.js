import * as THREE from 'three';
import { SKY, dirFromAngles, blendPreset } from './env.js';
import { pose, spinWheels } from './characters.js';
import { clamp, lerp, smooth, easeInOut, easeOut, v3, lerpV } from './util.js';

export const DURATION = 120;
const NAMES = ['sokha', 'mia', 'leo', 'nita', 'kai'];

// ---------- helpers ----------
function cam(c, pos, look, fov = 40) {
  c.cam.position.copy(pos);
  c.cam.lookAt(look);
  c.cam.fov = fov;
}
function sky(c, preset, az, el, focus, size, env, lightDir) {
  c.W.atmos.set(preset, dirFromAngles(az, el), lightDir || null);
  c.W.atmos.focus(focus, size);
  if (env) c.W.scene.environment = env;
}
function place(p, x, y, z, ry = 0) {
  p.root.position.set(x, y, z);
  p.root.rotation.set(0, ry, 0);
}
function walkState(p, t, t0, t1, a, b, stepLen = 0.6) {
  const u = clamp((t - t0) / (t1 - t0));
  p.root.position.copy(a).lerp(b, u);
  const dir = b.clone().sub(a);
  p.root.rotation.set(0, Math.atan2(dir.x, dir.z), 0);
  const dist = u * a.distanceTo(b);
  const active = smooth(t0 - 0.05, t0 + 0.35, t) * (1 - smooth(t1 - 0.35, t1 + 0.05, t));
  return { walkPhase: (dist / stepLen) * Math.PI, walk: active };
}
function headPos(p, up = 0.62) {
  const v = new THREE.Vector3();
  p.head.getWorldPosition(v);
  return v.add(new THREE.Vector3(0, up * p.root.scale.y, 0));
}
function bubble(c, p, text, t0, t1, o = {}) {
  if (c.t < t0 || c.t > t1) return;
  c.info.bubbles = c.info.bubbles || [];
  c.info.bubbles.push({ text, pos: headPos(p, o.up ?? 0.62), age: c.t - t0, left: t1 - c.t, big: o.big, dx: o.dx ?? 0 });
}
function caption(c, title, sub, t0, t1, emoji = '', where = 'bottom') {
  if (c.t < t0 || c.t > t1) return;
  c.info.captions.push({ title, sub, age: c.t - t0, left: t1 - c.t, emoji, top: where === 'top' });
}
const win = (t, a, b, ramp = 0.3) => smooth(a - ramp, a, t) * (1 - smooth(b, b + ramp, t));

// ---------- tuk-tuk ----------
const TUK_Z0 = 40;
const TUK_V = 8.5;
const tukZ = (t) => TUK_Z0 - TUK_V * (t - 9);
function tukRide(c, st = {}) {
  const T = c.tuk;
  const t = c.t;
  const z = tukZ(t);
  T.root.position.set(1.6, Math.sin(t * 17) * 0.012 + Math.abs(Math.sin(t * 5.3)) * 0.018, z);
  T.root.rotation.set(Math.sin(t * 3.1) * 0.008, Math.PI, Math.sin(t * 4.3) * 0.012);
  spinWheels(T, TUK_Z0 - z);
  c.use(NAMES);
  const so = c.cast.sokha;
  T.root.add(so.root);
  so.root.position.set(0, 0.86, 1.5);
  so.root.rotation.set(0, 0, 0);
  pose(so, t, { sit: 1, seatH: 0.2, drive: 1, bounce: 0.012, spread: 1, ...(st.sokha || {}) });
  so.torso.rotation.x += 0.2;
  const seats = [
    ['kai', -0.34, -0.95, 0],
    ['leo', 0.34, -0.95, 0],
    ['mia', -0.34, 0.28, Math.PI],
    ['nita', 0.34, 0.28, Math.PI],
  ];
  for (const [n, x, zz, ry] of seats) {
    const p = c.cast[n];
    T.root.add(p.root);
    p.root.position.set(x, 0.9, zz);
    p.root.rotation.set(0, ry + (st[n]?.turn ?? 0), 0);
    pose(p, t, { sit: 1, seatH: 0.14, bounce: 0.02, bounceF: 8, legSwing: true, ...(st[n] || {}) });
  }
  c.W.flock.update(t, v3(-120, 40, z - 150), v3(140, 55, z - 90), 9, 24, 3);
  return z;
}

// ---------- Angkor group helpers ----------
const FORM = {
  sokha: [0.9, -1.6],
  mia: [-1.3, 0],
  leo: [0.35, 0.4],
  nita: [-0.45, 1.5],
  kai: [1.9, 0.9],
};

// ---------- Jump photo (used by two shots) ----------
const JUMP_T = 105.6;
const FREEZE_T = 107.0;
function jumpShot(c) {
  const A = c.W;
  const t = c.t;
  A.setMirror(false);
  sky(c, SKY.sunset, 12, 9, v3(0, 0, 100), 18, A.envs.sunset, dirFromAngles(20, 14));
  cam(c, v3(0, 2.55, 109.5), v3(0, 9.5, 60), 46);
  c.use(NAMES);
  const order = ['kai', 'mia', 'sokha', 'nita', 'leo'];
  order.forEach((n, i) => {
    const p = c.cast[n];
    place(p, (i - 2) * 1.25, 1.6, 102 + Math.abs(i - 2) * 0.35, -(i - 2) * 0.08);
    const d = [0, 0.05, 0.02, 0.07, 0.03][i];
    const j0 = JUMP_T + d;
    let jump = 0;
    if (t > j0) jump = 0.5 * easeOut((t - j0) / (FREEZE_T - j0)) + Math.max(0, t - FREEZE_T) * 0.4;
    const crouch = win(t, JUMP_T - 0.45, j0, 0.2) * (t < j0 ? 1 : 0);
    const st = {
      wave: n !== 'sokha' ? win(t, 102.2, 104.2, 0.3) : 0,
      bigSmile: 1,
      laugh: t > j0 ? 0.9 : 0,
      jump: jump > 0 ? Math.min(jump, 0.999) : undefined,
      jumpH: [1.0, 0.85, 0.95, 0.9, 1.05][i],
      crouch,
      tilt: [0.12, -0.1, 0, 0.1, -0.12][i],
      talk: n === 'sokha' ? win(t, 102.8, 105.6, 0.1) : 0,
    };
    pose(p, t, st);
    if (jump > 0) {
      p.shL.rotation.z += Math.sin(i * 1.7) * 0.3;
      p.thighR.rotation.x -= 0.4 * Math.sin(i + 1);
    }
  });
  const so = c.cast.sokha;
  bubble(c, so, '1...', 102.9, 103.7);
  bubble(c, so, '2...', 103.7, 104.5);
  bubble(c, so, '3...', 104.5, 105.25);
  bubble(c, so, 'JUMP!', 105.25, 106.6, { big: true });
}

// ---------- shot list ----------
export const SHOTS = [
  // 1. Title: aerial approach at dawn
  {
    start: 0, end: 9, world: 'angkor',
    run(c) {
      const A = c.W;
      A.setMirror(false);
      const pre = blendPreset(SKY.predawn, SKY.sunrise, 0.12 + 0.1 * c.p);
      sky(c, pre, 172, -2.5, v3(0, 0, 60), 170, A.envs.predawn, dirFromAngles(150, 24));
      const u = easeInOut(c.p * 0.85 + 0.05);
      cam(c, v3(lerp(-40, 0, u), lerp(125, 62, u), lerp(480, 300, u)), v3(0, lerp(94, 64, u), 0), 38);
      c.use([]);
      A.flock.update(c.t, v3(-200, 110, 300), v3(200, 125, 240), 0, 9, 2.2);
    },
  },
  // 2. Tuk-tuk from the front
  {
    start: 9, end: 17, world: 'road',
    run(c) {
      const t = c.t;
      sky(c, SKY.road, 200, 5, v3(1.6, 0, tukZ(t)), 18);
      const z = tukRide(c, {
        kai: { wave: win(t, 10.4, 14.2), lookYaw: 0.1, laugh: win(t, 11, 13) * 0.6 },
        leo: { wave: win(t, 11.2, 15.5), bigSmile: 1 },
        mia: { turn: -1.2, lookYaw: -0.3, talk: win(t, 13, 16) },
        nita: { turn: 1.2, lookYaw: 0.4, laugh: win(t, 14, 16.5) },
        sokha: { lookYaw: Math.sin(t * 0.8) * 0.15, talk: 0 },
      });
      const u = easeInOut(c.p);
      cam(c, v3(lerp(0.7, 0.2, u), lerp(1.3, 1.6, u), z - lerp(8.2, 5.4, u)), v3(1.5, 1.6, z), 40);
      bubble(c, c.cast.kai, 'Good morning, Angkor!', 11.2, 14.0);
      caption(c, 'Siem Reap, Cambodia', '5:00 AM  -  off to Angkor by tuk-tuk!', 10.0, 15.6, 'pin');
    },
  },
  // 3. Tuk-tuk tracking from the side
  {
    start: 17, end: 24, world: 'road',
    run(c) {
      const t = c.t;
      sky(c, SKY.road, 200, 5.5, v3(1.6, 0, tukZ(t)), 18);
      const z = tukRide(c, {
        leo: { point: win(t, 18.2, 21.6), pointUp: 1.35, lookYaw: -0.5, talk: win(t, 18.4, 20.8) },
        kai: { lookYaw: -0.7, bigSmile: 0.6 },
        mia: { photo: win(t, 20.0, 23.2), phone: t > 19.8 && t < 23.4, turn: -0.9, lookYaw: -0.4 },
        nita: { laugh: win(t, 19.5, 21.5), turn: 0.3 },
        sokha: { lookYaw: win(t, 21.6, 23.8) * -0.6, talk: win(t, 21.7, 23.6) },
      });
      const u = easeInOut(c.p);
      cam(c, v3(1.6 + lerp(6.8, 5.6, u), lerp(1.65, 1.9, u), z + lerp(2.0, -1.2, u)), v3(1.6, 1.5, z - 0.4), 42);
      bubble(c, c.cast.leo, 'Look! Sugar palms!', 18.4, 20.8);
      bubble(c, c.cast.sokha, 'Almost there!', 21.7, 23.7);
    },
  },
  // 4. Walking the causeway, crane up to reveal Angkor Wat
  {
    start: 24, end: 32, world: 'angkor',
    run(c) {
      const A = c.W;
      const t = c.t;
      A.setMirror(false);
      const pre = blendPreset(SKY.predawn, SKY.sunrise, 0.22 + 0.18 * c.p);
      sky(c, pre, 183, -1.5, v3(0, 0, 150), 40, A.envs.predawn, dirFromAngles(205, 22));
      c.use(NAMES);
      const zc0 = 171;
      const zc1 = 159;
      for (const n of NAMES) {
        const [ox, oz] = FORM[n];
        const a = v3(ox, 1.6, zc0 + oz);
        const b = v3(ox * 0.9, 1.6, zc1 + oz);
        const st = walkState(c.cast[n], t, 24, 32.5, a, b);
        if (n === 'sokha') Object.assign(st, { point: win(t, 25.8, 28.4), pointUp: 1.7, talk: win(t, 26, 28.2) });
        else st.lookYaw = Math.sin(t * 0.7 + ox) * 0.5;
        st.lookUp = 0.15;
        pose(c.cast[n], t, st);
      }
      const zc = lerp(zc0, zc1, clamp((t - 24) / 8.5));
      const u = easeInOut(smooth(25.5, 32, t));
      cam(c, v3(lerp(1.2, 0, u), lerp(3.3, 15, u), lerp(zc + 6.2, zc + 12, u)), lerpV(v3(0.2, 4.2, zc - 25), v3(0, 27, 0), u), lerp(44, 42, u));
      caption(c, 'Angkor Wat', 'The largest religious monument in the world', 26.2, 31.6, 'temple');
      bubble(c, c.cast.sokha, "Follow me, friends!", 25.4, 27.8);
    },
  },
  // 5. Faces: walking toward camera, amazed
  {
    start: 32, end: 38, world: 'angkor',
    run(c) {
      const A = c.W;
      const t = c.t;
      A.setMirror(false);
      const pre = blendPreset(SKY.predawn, SKY.sunrise, 0.42 + 0.1 * c.p);
      sky(c, pre, 175, 0, v3(0, 0, 140), 25, A.envs.predawn, dirFromAngles(185, 20));
      c.use(NAMES);
      const zc0 = 150;
      const zc1 = 144;
      for (const n of NAMES) {
        const [ox, oz] = FORM[n];
        const st = walkState(c.cast[n], t, 31.5, 38.5, v3(ox, 1.6, zc0 + oz), v3(ox, 1.6, zc1 + oz), 0.55);
        st.lookUp = 0.32;
        st.lookYaw = Math.sin(t * 0.6 + oz * 3) * 0.25;
        if (n === 'mia') Object.assign(st, { laugh: win(t, 32.6, 35.2) * 0.9 });
        if (n === 'leo') Object.assign(st, { talk: win(t, 35.4, 37.6), point: win(t, 35.3, 37.8), pointUp: 1.9 });
        if (n === 'kai') st.bigSmile = 1;
        pose(c.cast[n], t, st);
      }
      const zc = lerp(zc0, zc1, clamp((t - 31.5) / 7));
      const u = easeInOut(c.p);
      cam(c, v3(lerp(-0.4, 0.4, u), lerp(2.75, 2.95, u), zc - lerp(6.3, 5.3, u)), v3(0.2, 3.3, zc + 2), 42);
      bubble(c, c.cast.mia, 'Wooow!', 32.6, 35.0, { big: true });
      bubble(c, c.cast.leo, "It's HUGE!", 35.4, 37.8);
    },
  },
  // 6. Sunrise over the lotus pond (wide, with reflection)
  {
    start: 38, end: 49, world: 'angkor',
    run(c) {
      const A = c.W;
      const t = c.t;
      const k = smooth(38, 49, t);
      A.setMirror(true);
      const pre = blendPreset(SKY.predawn, SKY.sunrise, 0.6 + 0.4 * k);
      const el = lerp(18.5, 26, k);
      sky(c, pre, 161.6, el, v3(-42, 0, 128), 16, A.envs.sunrise, dirFromAngles(161.6, el));
      c.use(NAMES);
      const order = ['kai', 'nita', 'mia', 'leo', 'sokha'];
      order.forEach((n, i) => {
        place(c.cast[n], -45.2 + i * 1.18, 0.4, 130.0, Math.PI);
        pose(c.cast[n], t, { sit: 1, seatH: 0.14, legSwing: true, lookUp: 0.18, tilt: n === 'mia' ? -0.2 : n === 'nita' ? 0.12 : 0, lookYaw: n === 'sokha' ? win(t, 43, 47) * 0.8 : 0, talk: n === 'sokha' ? win(t, 43.2, 46.6) : 0 });
      });
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(-40.4, 2.8, 144.5), v3(-41.4, 2.35, 141.3), u), v3(-6.5, 21, 0), 44);
      A.flock.update(t, v3(-170, 62, -30), v3(160, 75, -10), 40, 49, 2.2);
      caption(c, 'Sunrise at Angkor Wat', 'Reflections in the lotus pond', 39.2, 45.8, 'sun', 'top');
    },
  },
  // 7. Close-up faces in golden light + selfie
  {
    start: 49, end: 55, world: 'angkor',
    run(c) {
      const A = c.W;
      const t = c.t;
      A.setMirror(true);
      sky(c, SKY.sunrise, 161.3, 26, v3(-45, 0, 130), 8, A.envs.sunrise, dirFromAngles(161.3, 20));
      c.use(NAMES);
      const order = ['kai', 'nita', 'mia', 'leo', 'sokha'];
      const lean = win(t, 51.0, 54.2, 0.4);
      order.forEach((n, i) => {
        const p = c.cast[n];
        place(p, -45.2 + i * 1.18 + (2 - i) * 0.12 * lean, 0.4, 130.0, Math.PI);
        const st = { sit: 1, seatH: 0.14, legSwing: true, eyesClosed: 0.25 * (1 - lean), bigSmile: 0.5 + 0.5 * lean, tilt: (i - 2) * -0.12 * lean };
        if (n === 'mia') Object.assign(st, { point: lean, pointUp: 2.25, phone: lean > 0.05, talk: win(t, 51.2, 52.6) });
        if (t > 53.25) st.laugh = win(t, 53.3, 55.2) * 0.9;
        pose(p, t, st);
      });
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(-43.0, 1.3, 126.2), v3(-42.8, 1.35, 126.8), u), v3(-42.9, 1.25, 130), 40);
      bubble(c, c.cast.mia, 'Say cheese!', 51.3, 53.1);
      if (t > 53.2 && t < 53.7) c.info.flash = 1 - (t - 53.2) / 0.5;
      c.info.shutter = 53.2;
    },
  },
  // 8. Bayon: giant stone face close-up, pull back
  {
    start: 55, end: 61, world: 'bayon',
    run(c) {
      const B = c.W;
      const t = c.t;
      sky(c, SKY.day, 35, 38, v3(9, B.L2, 20), 22);
      const F = B.heroFace;
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(F.x + 0.25, F.y + 0.2, F.z + 4.6), v3(F.x - 4.2, F.y - 2.6, F.z + 15.5), u), lerpV(v3(F.x, F.y - 0.05, F.z), v3(F.x + 1.2, F.y + 0.6, F.z), u), lerp(40, 50, u));
      c.use(NAMES);
      const spots = { sokha: [6.2, 22.6], mia: [8.0, 23.4], leo: [9.6, 22.9], nita: [11.2, 23.6], kai: [12.9, 22.8] };
      for (const n of NAMES) {
        const [x, z] = spots[n];
        place(c.cast[n], x, B.L2, z, Math.PI + (x - 9.5) * 0.08);
        pose(c.cast[n], t, { lookUp: 0.55, laugh: n === 'mia' ? win(t, 58, 60.5) * 0.6 : 0, point: n === 'kai' ? win(t, 58.5, 61) : 0, pointUp: 2.3 });
      }
      B.flock.update(t, v3(-60, 40, -30), v3(60, 45, 40), 55, 61, 2.5);
      caption(c, 'Bayon Temple', 'Home of the giant smiling stone faces', 56.0, 60.8, 'smile');
    },
  },
  // 9. Leo copies the famous smile
  {
    start: 61, end: 68, world: 'bayon',
    run(c) {
      const B = c.W;
      const t = c.t;
      sky(c, SKY.day, 35, 38, v3(10, B.L2, 21), 12);
      c.use(NAMES);
      const leo = c.cast.leo;
      place(leo, 11.3, B.L2 + 2.0, 20.2, -0.12);
      const smile = smooth(61.6, 62.4, t);
      pose(leo, t, { eyesClosed: 0.88 * smile, bigSmile: smile, tilt: -0.1 * smile, lookYaw: -0.1 * smile, laugh: win(t, 65.8, 68, 0.3) * 0.5 });
      leo.shL.rotation.z -= 0.2 * smile;
      leo.shR.rotation.z += 0.2 * smile;
      const others = { sokha: [6.6, 22.8, 0.55], mia: [8.3, 23.7, 0.3], nita: [13.6, 23.6, -0.4], kai: [15.2, 22.6, -0.65] };
      for (const [n, [x, z, ry]] of Object.entries(others)) {
        place(c.cast[n], x, B.L2, z, Math.PI + ry);
        const laugh = win(t, 64.3, 68, 0.3);
        pose(c.cast[n], t, { laugh, bounce: laugh * 0.03, bounceF: 14, clap: n === 'mia' || n === 'sokha' ? laugh : 0, lookUp: 0.25, lookYaw: -ry * 0.5 });
      }
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(11.0, 10.3, 29.5), v3(10.8, 10.6, 27.6), u), v3(10.1, 11.0, 19.5), 44);
      bubble(c, leo, 'Same smile?', 62.2, 64.6);
      bubble(c, c.cast.nita, 'Hahaha!', 64.6, 66.8);
      bubble(c, c.cast.kai, 'Twins!', 65.4, 67.8);
    },
  },
  // 10. Bayon wide orbit
  {
    start: 68, end: 75, world: 'bayon',
    run(c) {
      const B = c.W;
      const t = c.t;
      sky(c, SKY.day, 35, 40, v3(0, 0, 0), 55);
      const ang = lerp(0.55, -0.1, easeInOut(c.p));
      cam(c, v3(Math.sin(ang) * 54, lerp(24, 16, easeInOut(c.p)), Math.cos(ang) * 54), v3(2, 13, 0), 46);
      c.use(NAMES);
      const spots = { sokha: [6.2, 22.6], mia: [8.0, 23.4], leo: [9.6, 22.9], nita: [11.2, 23.6], kai: [12.9, 22.8] };
      for (const n of NAMES) {
        const [x, z] = spots[n];
        place(c.cast[n], x, B.L2, z, 0.5);
        pose(c.cast[n], t, { wave: 1, bounce: 0.03, bounceF: 7 });
      }
      B.flock.update(t, v3(-120, 50, 60), v3(100, 60, -60), 68, 75, 3);
    },
  },
  // 11. Ta Prohm: glide toward the root-covered gate
  {
    start: 75, end: 82, world: 'taprohm',
    run(c) {
      const t = c.t;
      sky(c, SKY.jungle, 30, 58, v3(0, 0, 4), 24);
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(-7.5, 3.6, 27), v3(-1.9, 2.3, 13.2), u), lerpV(v3(0.3, 6, 0), v3(0.4, 4.3, 0), u), 44);
      c.use([]);
      caption(c, 'Ta Prohm', 'The temple swallowed by the jungle', 76.0, 81.6, 'tree');
    },
  },
  // 12. Friends explore the gate
  {
    start: 82, end: 89, world: 'taprohm',
    run(c) {
      const t = c.t;
      sky(c, SKY.jungle, 30, 58, v3(0, 0, 6), 18);
      c.use(NAMES);
      const paths = {
        sokha: [v3(-0.8, 0.3, 15.5), v3(-0.6, 0.3, 7.2)],
        mia: [v3(1.4, 0.3, 16.5), v3(1.3, 0.3, 8.0)],
        leo: [v3(0.3, 0.3, 17.3), v3(0.4, 0.3, 8.8)],
        nita: [v3(-1.9, 0.3, 17.8), v3(-1.9, 0.3, 9.2)],
        kai: [v3(-2.8, 0.3, 16.4), v3(-3.6, 0.3, 6.6)],
      };
      for (const n of NAMES) {
        const [a, b] = paths[n];
        const p = c.cast[n];
        const st = walkState(p, t, 81.6, 85.8, a, b, 0.55);
        st.lookUp = 0.3 * smooth(84, 86, t);
        st.lookYaw = Math.sin(t * 0.8 + a.x) * 0.4;
        if (n === 'sokha') Object.assign(st, { talk: win(t, 83.4, 86.4), point: win(t, 85.4, 88.6), pointUp: 2.1 });
        if (n === 'mia') Object.assign(st, { photo: win(t, 86.2, 89), phone: t > 86 });
        if (t > 85.8) p.root.rotation.y = Math.PI + (n === 'mia' ? 0.2 : 0);
        if (n === 'kai') {
          // hop onto the big stone
          const hop = smooth(86.0, 86.8, t);
          if (t > 85.9) {
            p.root.position.set(lerp(-3.6, -3.8, hop), 0.3 + Math.sin(hop * Math.PI) * 0.8 + hop * 0.9, lerp(6.6, 5.3, hop));
            p.root.rotation.y = lerp(Math.PI, 0.3, hop);
            st.walk = 0;
            st.jump = hop > 0 && hop < 1 ? hop : undefined;
            st.jumpH = 0.001;
            st.armsUp = win(t, 87.0, 89, 0.3);
            st.laugh = win(t, 87, 89, 0.3);
          }
        }
        pose(p, t, st);
      }
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(6.8, 2.1, 14.5), v3(5.6, 1.9, 11.4), u), lerpV(v3(-0.3, 2.4, 8), v3(-0.9, 2.9, 4.5), u), 46);
      bubble(c, c.cast.sokha, 'These roots are hundreds of years old!', 83.4, 86.4);
      bubble(c, c.cast.kai, 'Look at me!', 87.1, 89.0);
    },
  },
  // 13. Looking up at the giant tree
  {
    start: 89, end: 95, world: 'taprohm',
    run(c) {
      const t = c.t;
      sky(c, SKY.jungle, 30, 58, v3(0, 0, 4), 20);
      c.use(NAMES);
      const spots = { sokha: [-0.6, 7.2, 3.3], mia: [1.3, 8.0, 3.0], leo: [0.4, 8.8, 3.1], nita: [-1.9, 9.2, 3.4], kai: [-3.8, 5.3, 2.8] };
      for (const n of NAMES) {
        const [x, z, ry] = spots[n];
        const p = c.cast[n];
        place(p, x, n === 'kai' ? 1.2 : 0.3, z, ry);
        pose(p, t, { lookUp: 0.75, point: n === 'leo' ? win(t, 89.5, 94.5) : 0, pointUp: 2.5, laugh: n === 'nita' ? win(t, 91.5, 93.5) * 0.7 : 0, photo: n === 'mia' ? 1 : 0, phone: n === 'mia' });
      }
      const u = easeInOut(smooth(89.3, 94.6, t));
      cam(c, lerpV(v3(2.6, 0.9, 12.2), v3(2.4, 0.85, 11.8), u), lerpV(v3(0.2, 2.3, 5), v3(1.2, 10.5, -1), u), 52);
      bubble(c, c.cast.leo, 'Up there!', 89.8, 92.0);
    },
  },
  // 14. Sunset: golden Angkor Wat reflected in the pond
  {
    start: 95, end: 102, world: 'angkor',
    run(c) {
      const A = c.W;
      const t = c.t;
      A.setMirror(true);
      sky(c, SKY.sunset, 16, lerp(10, 6, c.p), v3(20, 0, 60), 90, A.envs.sunset, dirFromAngles(18, 13));
      const u = easeInOut(c.p);
      cam(c, lerpV(v3(47.5, 2.5, 136), v3(43, 3.2, 133.5), u), v3(9, 25, 0), 45);
      c.use([]);
      A.flock.update(t, v3(160, 60, 20), v3(-160, 75, -10), 95, 102, 2.2);
      caption(c, 'Sunset at Angkor Wat', 'One last photo together!', 96.0, 101.6, 'camera');
    },
  },
  // 15. The jump photo
  { start: 102, end: FREEZE_T, world: 'angkor', run: jumpShot },
  // 16. Freeze frame -> polaroid -> The End
  {
    start: FREEZE_T, end: DURATION + 1, world: 'angkor',
    run(c) {
      const real = c.t;
      c.t = FREEZE_T - 0.0001;
      jumpShot(c);
      c.t = real;
      c.info.bubbles = [];
      c.info.freezeT = FREEZE_T;
      c.info.polaroid = real - FREEZE_T;
    },
  },
];

// transitions at world changes (handled by the overlay)
export const TRANSITIONS = [
  { t: 9.0, type: 'fade', d: 0.55 },
  { t: 24.0, type: 'iris', d: 0.55, cx: 0.5, cy: 0.45 },
  { t: 55.0, type: 'iris', d: 0.55, cx: 0.5, cy: 0.42 },
  { t: 75.0, type: 'iris', d: 0.55, cx: 0.5, cy: 0.5 },
  { t: 95.0, type: 'fade', d: 0.7 },
];
export { FREEZE_T };
