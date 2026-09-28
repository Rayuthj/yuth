import * as THREE from 'three';
import { M, mesh, kramaTexture, clamp, lerp } from './util.js';

const cap = (r, l, mat, seg = 12) => mesh(new THREE.CapsuleGeometry(r, l, 6, seg), mat);
const sph = (r, mat, w = 24, h = 16) => mesh(new THREE.SphereGeometry(r, w, h), mat);

let kramaTex = null;

export const CAST = {
  sokha: {
    name: 'Sokha', skin: 0xb07850, shirt: 0xf5f2ea, pants: 0x2f3548, long: true, hair: 0x2e2420,
    hairStyle: 'short', shoes: 0x3a2a20, krama: true, hat: null, scale: 1.02,
  },
  mia: {
    name: 'Mia', skin: 0xf2c6a0, shirt: 0xffc93c, pants: 0x4a78c0, long: false, hair: 0x7a4a2a,
    hairStyle: 'ponytail', shoes: 0xffffff, hat: 'sun', hatColor: 0xf2dfb0, band: 0xe0506a, camera: true, scale: 0.95,
  },
  leo: {
    name: 'Leo', skin: 0xf0c09a, shirt: 0x3a8ee6, pants: 0xc8b48a, long: false, hair: 0xf0c050,
    hairStyle: 'spiky', shoes: 0xe04a3a, backpack: 0xff8a2a, scale: 1.0,
  },
  nita: {
    name: 'Nita', skin: 0xd8a47a, shirt: 0xff7a8a, pants: 0xf4efe6, long: true, hair: 0x2a201e,
    hairStyle: 'bun', shoes: 0x7a5aa0, glasses: true, scale: 0.93,
  },
  kai: {
    name: 'Kai', skin: 0x8a5a3a, shirt: 0x3fb87a, pants: 0x3a3a48, long: false, hair: 0x2c201a,
    hairStyle: 'curly', shoes: 0xf2f2f2, hat: 'cap', hatColor: 0xf04a4a, backpack: 0x3a6ad0, scale: 1.04,
  },
};

export function makePerson(o) {
  const root = new THREE.Group();
  const P = { root, o };
  const skin = M(o.skin, { rough: 0.55 });
  const shirt = M(o.shirt, { rough: 0.8 });
  const pants = M(o.pants, { rough: 0.85 });
  const shoe = M(o.shoes, { rough: 0.6 });
  const hairM = M(o.hair, { rough: 0.55 });

  const hips = new THREE.Group();
  hips.position.y = 0.72;
  root.add(hips);
  P.hips = hips;

  // legs with knees
  for (const s of [-1, 1]) {
    const thigh = new THREE.Group();
    thigh.position.set(0.1 * s, -0.02, 0);
    hips.add(thigh);
    const tm = cap(0.088, 0.22, o.long ? pants : skin);
    tm.position.y = -0.17;
    thigh.add(tm);
    if (!o.long) {
      const shorts = cap(0.108, 0.1, pants);
      shorts.position.y = -0.08;
      thigh.add(shorts);
    }
    const knee = new THREE.Group();
    knee.position.y = -0.33;
    thigh.add(knee);
    const sm = cap(0.08, 0.22, o.long ? pants : skin);
    sm.position.y = -0.17;
    knee.add(sm);
    const sh = sph(0.1, shoe, 16, 12);
    sh.scale.set(0.95, 0.62, 1.55);
    sh.position.set(0, -0.36, 0.05);
    knee.add(sh);
    P[s < 0 ? 'thighL' : 'thighR'] = thigh;
    P[s < 0 ? 'kneeL' : 'kneeR'] = knee;
  }

  // torso
  const torso = new THREE.Group();
  hips.add(torso);
  P.torso = torso;
  const pelvis = sph(0.2, pants, 20, 14);
  pelvis.scale.set(1.0, 0.62, 0.82);
  pelvis.position.y = 0.02;
  torso.add(pelvis);
  const chest = cap(0.205, 0.2, shirt, 18);
  chest.scale.set(1, 1, 0.82);
  chest.position.y = 0.27;
  torso.add(chest);
  const neck = mesh(new THREE.CylinderGeometry(0.06, 0.07, 0.1, 10), skin, [0, 0.5, 0]);
  torso.add(neck);

  if (o.krama) {
    kramaTex = kramaTex || kramaTexture();
    const km = new THREE.MeshStandardMaterial({ map: kramaTex, roughness: 0.9 });
    const k = mesh(new THREE.TorusGeometry(0.12, 0.045, 10, 20), km, [0, 0.47, 0], [Math.PI / 2 + 0.15, 0, 0]);
    torso.add(k);
    const tail = mesh(new THREE.BoxGeometry(0.1, 0.28, 0.03), km, [0.07, 0.33, 0.165], [0.15, 0, 0.12]);
    torso.add(tail);
  }
  if (o.backpack) {
    const bm = M(o.backpack, { rough: 0.7 });
    const bp = cap(0.15, 0.14, bm);
    bp.scale.set(1.1, 1, 0.6);
    bp.position.set(0, 0.27, -0.2);
    torso.add(bp);
    const pocket = cap(0.08, 0.04, M(new THREE.Color(o.backpack).multiplyScalar(0.75).getHex()));
    pocket.scale.set(1.2, 1, 0.5);
    pocket.position.set(0, 0.18, -0.29);
    torso.add(pocket);
    for (const s of [-1, 1]) {
      const strap = mesh(new THREE.TorusGeometry(0.13, 0.018, 6, 16, Math.PI), bm, [0.1 * s, 0.33, -0.02], [0, Math.PI / 2, 0]);
      torso.add(strap);
    }
  }
  if (o.camera) {
    const cm = M(0x222228, { rough: 0.4 });
    const body = mesh(new THREE.BoxGeometry(0.14, 0.09, 0.06), cm, [0, 0.22, 0.2]);
    torso.add(body);
    const lens = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.05, 14), M(0x111111, { rough: 0.2 }), [0, 0.22, 0.245], [Math.PI / 2, 0, 0]);
    torso.add(lens);
    const strap = mesh(new THREE.TorusGeometry(0.19, 0.01, 4, 20, Math.PI), cm, [0, 0.29, 0.06], [-0.35, 0, Math.PI]);
    torso.add(strap);
  }

  // arms with elbows
  for (const s of [-1, 1]) {
    const sh = new THREE.Group();
    sh.position.set(0.25 * s, 0.4, 0);
    torso.add(sh);
    const sleeve = cap(0.078, 0.08, shirt);
    sleeve.position.y = -0.06;
    sh.add(sleeve);
    const ua = cap(0.058, 0.14, skin);
    ua.position.y = -0.13;
    sh.add(ua);
    const el = new THREE.Group();
    el.position.y = -0.23;
    sh.add(el);
    const fa = cap(0.055, 0.14, skin);
    fa.position.y = -0.1;
    el.add(fa);
    const hand = sph(0.068, skin, 14, 10);
    hand.position.y = -0.22;
    el.add(hand);
    P[s < 0 ? 'shL' : 'shR'] = sh;
    P[s < 0 ? 'elL' : 'elR'] = el;
    P[s < 0 ? 'handL' : 'handR'] = hand;
  }
  const phone = mesh(new THREE.BoxGeometry(0.09, 0.17, 0.02), M(0x1a1a24, { rough: 0.3 }), [0, -0.27, 0.05]);
  const screen = mesh(new THREE.PlaneGeometry(0.075, 0.14), M(0x8ad0ff, { emissive: 0x6ab8ff, ei: 0.8 }), [0, 0, -0.011], [0, Math.PI, 0]);
  phone.add(screen);
  phone.visible = false;
  P.elR.add(phone);
  P.phone = phone;

  // head
  const head = new THREE.Group();
  head.position.y = 0.62;
  torso.add(head);
  P.head = head;
  const skull = sph(0.27, skin, 32, 24);
  skull.position.y = 0.2;
  skull.scale.set(1, 0.97, 0.95);
  head.add(skull);
  for (const s of [-1, 1]) {
    const ear = sph(0.055, skin, 12, 8);
    ear.scale.set(0.5, 1, 0.8);
    ear.position.set(0.265 * s, 0.19, 0);
    head.add(ear);
  }
  const face = new THREE.Group();
  face.position.y = 0.2;
  head.add(face);
  const white = M(0xffffff, { rough: 0.3 });
  const pupilM = M(0x2a1a14, { rough: 0.2 });
  const shine = M(0xffffff, { emissive: 0xffffff, ei: 0.8 });
  P.eyes = [];
  for (const s of [-1, 1]) {
    const eye = new THREE.Group();
    eye.position.set(0.095 * s, 0.03, 0.225);
    face.add(eye);
    const ew = sph(0.062, white, 16, 12);
    ew.scale.set(0.9, 1.1, 0.55);
    eye.add(ew);
    const pu = sph(0.038, pupilM, 14, 10);
    pu.position.set(0, -0.005, 0.03);
    pu.scale.set(1, 1.1, 0.6);
    eye.add(pu);
    const hl = sph(0.012, shine, 8, 6);
    hl.position.set(0.013, 0.018, 0.052);
    eye.add(hl);
    P.eyes.push(eye);
    const brow = cap(0.013, 0.07, hairM, 6);
    brow.rotation.z = Math.PI / 2 + 0.15 * s;
    brow.position.set(0.1 * s, 0.13, 0.235);
    face.add(brow);
    const cheek = sph(0.045, M(0xff8a8a, { opacity: 0.35, depthWrite: false }), 12, 8);
    cheek.scale.set(1, 0.6, 0.3);
    cheek.position.set(0.16 * s, -0.06, 0.2);
    cheek.castShadow = false;
    face.add(cheek);
  }
  const nose = sph(0.034, M(new THREE.Color(o.skin).multiplyScalar(0.92).getHex(), { rough: 0.5 }), 12, 8);
  nose.position.set(0, -0.02, 0.262);
  face.add(nose);
  // smile: lower half torus
  const mouthM = M(0x8a2a2a, { rough: 0.5 });
  const mouth = mesh(new THREE.TorusGeometry(0.055, 0.013, 8, 18, Math.PI), mouthM, [0, -0.085, 0.235], [0.25, 0, Math.PI]);
  face.add(mouth);
  P.mouth = mouth;
  const open = sph(0.05, M(0x6a1a20, { rough: 0.6 }), 14, 10);
  open.scale.set(1, 0.6, 0.35);
  open.position.set(0, -0.1, 0.228);
  open.visible = false;
  face.add(open);
  P.mouthOpen = open;

  if (o.glasses) {
    const gm = M(0x3a2a3a, { rough: 0.4 });
    for (const s of [-1, 1]) {
      const ring = mesh(new THREE.TorusGeometry(0.068, 0.01, 6, 20), gm, [0.095 * s, 0.03, 0.262]);
      face.add(ring);
    }
    const bridge = mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.06, 5), gm, [0, 0.04, 0.268], [0, 0, Math.PI / 2]);
    face.add(bridge);
  }

  // hair
  const hairCap = mesh(new THREE.SphereGeometry(0.285, 28, 18, 0, Math.PI * 2, 0, Math.PI * 0.52), hairM, [0, 0.215, -0.012], [-0.32, 0, 0]);
  head.add(hairCap);
  const back = sph(0.27, hairM, 24, 16);
  back.scale.set(1.02, 0.9, 0.7);
  back.position.set(0, 0.17, -0.07);
  head.add(back);
  if (o.hairStyle === 'ponytail') {
    const pt = sph(0.1, hairM);
    pt.position.set(0, 0.3, -0.29);
    head.add(pt);
    const tail = cap(0.075, 0.22, hairM);
    tail.position.set(0, 0.12, -0.34);
    tail.rotation.x = 0.35;
    head.add(tail);
    P.tail = tail;
    for (const s of [-1, 1]) {
      const side = cap(0.06, 0.12, hairM);
      side.position.set(0.24 * s, 0.14, 0.08);
      head.add(side);
    }
  } else if (o.hairStyle === 'bun') {
    const bun = sph(0.12, hairM);
    bun.position.set(0, 0.5, -0.06);
    head.add(bun);
    const fr = sph(0.14, hairM);
    fr.scale.set(1.6, 0.45, 0.7);
    fr.position.set(0.05, 0.36, 0.17);
    fr.rotation.z = -0.2;
    head.add(fr);
  } else if (o.hairStyle === 'spiky') {
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * Math.PI * 2;
      const sp = mesh(new THREE.ConeGeometry(0.07, 0.2, 7), hairM);
      sp.position.set(Math.cos(a) * 0.14, 0.44, Math.sin(a) * 0.14 - 0.02);
      sp.rotation.set(Math.sin(a) * 0.6, 0, -Math.cos(a) * 0.6);
      head.add(sp);
    }
    const fr = mesh(new THREE.ConeGeometry(0.09, 0.22, 7), hairM, [0.03, 0.4, 0.2], [1.1, 0, -0.2]);
    head.add(fr);
  } else if (o.hairStyle === 'curly') {
    for (let i = 0; i < 11; i++) {
      const a = Math.PI * 0.15 + (i / 10) * Math.PI * 0.7;
      const c = sph(0.075, hairM, 12, 8);
      c.position.set(Math.cos(a) * 0.25, 0.24 + Math.sin(i * 1.7) * 0.02, -Math.sin(a) * 0.19);
      head.add(c);
    }
  } else {
    const fr = sph(0.14, hairM);
    fr.scale.set(1.5, 0.45, 0.75);
    fr.position.set(-0.04, 0.37, 0.16);
    fr.rotation.z = 0.25;
    head.add(fr);
  }

  if (o.hat === 'sun') {
    const hm = M(o.hatColor, { rough: 0.9 });
    const brim = mesh(new THREE.CylinderGeometry(0.46, 0.5, 0.025, 32), hm, [0, 0.4, 0], [-0.12, 0, 0]);
    head.add(brim);
    const dome = mesh(new THREE.SphereGeometry(0.27, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), hm, [0, 0.39, -0.01], [-0.12, 0, 0]);
    dome.scale.set(1.02, 0.85, 1.02);
    head.add(dome);
    const band = mesh(new THREE.CylinderGeometry(0.278, 0.278, 0.06, 28, 1, true), M(o.band), [0, 0.43, -0.013], [-0.12, 0, 0]);
    head.add(band);
    hairCap.visible = true;
  } else if (o.hat === 'cap') {
    const hm = M(o.hatColor, { rough: 0.7 });
    const dome = mesh(new THREE.SphereGeometry(0.29, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), hm, [0, 0.29, 0], [-0.08, 0, 0]);
    head.add(dome);
    const visor = mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.02, 24, 1, false, -Math.PI / 2, Math.PI), hm, [0, 0.3, 0.22], [0.12, 0, 0]);
    visor.scale.set(1, 1, 0.9);
    head.add(visor);
    const btn = sph(0.03, M(0xffffff), 8, 6);
    btn.position.set(0, 0.58, 0);
    head.add(btn);
  }

  root.scale.setScalar(o.scale ?? 1);
  root.traverse((c) => {
    if (c.isMesh && c.castShadow !== false) {
      c.castShadow = true;
      c.receiveShadow = true;
    }
  });
  return P;
}

// Pose a person. s = state object, t = global time
export function pose(P, t, s = {}) {
  const ph = s.walkPhase ?? 0;
  const walk = s.walk ?? 0;
  const sit = s.sit ?? 0;
  const seed = P.o.name.length * 1.7;

  // reset
  for (const k of ['thighL', 'thighR', 'kneeL', 'kneeR', 'shL', 'shR', 'elL', 'elR', 'torso', 'head']) P[k].rotation.set(0, 0, 0);
  P.hips.position.set(0, 0.72, 0);
  P.hips.rotation.set(0, 0, 0);

  // breathing / idle sway
  const br = Math.sin(t * 2.2 + seed);
  P.torso.rotation.z = Math.sin(t * 0.9 + seed) * 0.025;
  P.torso.position.y = br * 0.004;

  // walking
  const sw = Math.sin(ph);
  P.thighL.rotation.x = -sw * 0.55 * walk;
  P.thighR.rotation.x = sw * 0.55 * walk;
  P.kneeL.rotation.x = Math.max(0, Math.sin(ph + 1.6)) * 0.9 * walk;
  P.kneeR.rotation.x = Math.max(0, Math.sin(ph + 1.6 + Math.PI)) * 0.9 * walk;
  P.hips.position.y += Math.abs(Math.cos(ph)) * 0.045 * walk - 0.02 * walk;
  P.hips.rotation.y = sw * 0.08 * walk;
  P.torso.rotation.y = -sw * 0.12 * walk;
  P.torso.rotation.x = 0.05 * walk;
  P.shL.rotation.x = sw * 0.5 * walk;
  P.shR.rotation.x = -sw * 0.5 * walk;
  P.elL.rotation.x = -0.35 * walk;
  P.elR.rotation.x = -0.35 * walk;

  // arms relax outward
  P.shL.rotation.z = -0.1;
  P.shR.rotation.z = 0.1;

  // sitting
  if (sit > 0) {
    P.hips.position.y = lerp(P.hips.position.y, s.seatH ?? 0.45, sit);
    P.thighL.rotation.x = lerp(P.thighL.rotation.x, -1.45, sit);
    P.thighR.rotation.x = lerp(P.thighR.rotation.x, -1.45, sit);
    P.kneeL.rotation.x = lerp(P.kneeL.rotation.x, 1.45 + (s.legSwing ? Math.sin(t * 3 + seed) * 0.15 : 0), sit);
    P.kneeR.rotation.x = lerp(P.kneeR.rotation.x, 1.45 + (s.legSwing ? Math.sin(t * 3 + seed + 1) * 0.15 : 0), sit);
    P.thighL.rotation.z = -(0.08 + 0.2 * (s.spread ?? 0)) * sit;
    P.thighR.rotation.z = (0.08 + 0.2 * (s.spread ?? 0)) * sit;
    P.shL.rotation.x = lerp(P.shL.rotation.x, -0.35, sit);
    P.shR.rotation.x = lerp(P.shR.rotation.x, -0.35, sit);
    P.elL.rotation.x = -0.7 * sit;
    P.elR.rotation.x = -0.7 * sit;
  }

  // bounce (in vehicle / laughing)
  if (s.bounce) P.hips.position.y += Math.abs(Math.sin(t * (s.bounceF ?? 9) + seed)) * s.bounce;

  // jump: 0..1 phase of an arc
  if (s.jump !== undefined && s.jump > 0 && s.jump < 1) {
    const j = s.jump;
    const hgt = Math.sin(j * Math.PI) * (s.jumpH ?? 0.9);
    P.hips.position.y += hgt;
    const tuck = Math.sin(j * Math.PI);
    P.thighL.rotation.x = -0.7 * tuck;
    P.thighR.rotation.x = -0.5 * tuck;
    P.kneeL.rotation.x = 1.3 * tuck;
    P.kneeR.rotation.x = 1.1 * tuck;
    s.armsUp = Math.max(s.armsUp ?? 0, tuck);
  }
  if (s.crouch) {
    P.hips.position.y -= 0.15 * s.crouch;
    P.thighL.rotation.x += -0.6 * s.crouch;
    P.thighR.rotation.x += -0.6 * s.crouch;
    P.kneeL.rotation.x += 1.1 * s.crouch;
    P.kneeR.rotation.x += 1.1 * s.crouch;
    P.torso.rotation.x += 0.35 * s.crouch;
  }

  if (s.armsUp) {
    const a = s.armsUp;
    P.shL.rotation.z = lerp(P.shL.rotation.z, -2.6, a);
    P.shR.rotation.z = lerp(P.shR.rotation.z, 2.6, a);
    P.shL.rotation.x = lerp(P.shL.rotation.x, 0, a);
    P.shR.rotation.x = lerp(P.shR.rotation.x, 0, a);
    P.elL.rotation.x = lerp(P.elL.rotation.x, 0, a);
    P.elR.rotation.x = lerp(P.elR.rotation.x, 0, a);
  }

  // wave with right arm
  if (s.wave) {
    const a = s.wave;
    P.shR.rotation.z = lerp(P.shR.rotation.z, 2.5, a);
    P.shR.rotation.x = lerp(P.shR.rotation.x, 0, a);
    P.elR.rotation.z = Math.sin(t * 10 + seed) * 0.5 * a;
    P.elR.rotation.x = 0;
  }
  // point with right arm, forward/up
  if (s.point) {
    const a = s.point;
    P.shR.rotation.x = lerp(P.shR.rotation.x, -(s.pointUp ?? 1.5), a);
    P.shR.rotation.z = lerp(P.shR.rotation.z, 0.25, a);
    P.elR.rotation.x = lerp(P.elR.rotation.x, -0.1, a);
  }
  // hold phone / camera up to face
  if (s.photo) {
    const a = s.photo;
    for (const k of ['L', 'R']) {
      P['sh' + k].rotation.x = lerp(P['sh' + k].rotation.x, -1.25, a);
      P['sh' + k].rotation.z = lerp(P['sh' + k].rotation.z, k === 'L' ? 0.5 : -0.5, a);
      P['el' + k].rotation.x = lerp(P['el' + k].rotation.x, -1.2, a);
    }
  }
  if (s.drive) {
    for (const k of ['L', 'R']) {
      P['sh' + k].rotation.x = -1.05;
      P['sh' + k].rotation.z = k === 'L' ? -0.25 : 0.25;
      P['el' + k].rotation.x = -0.35;
    }
  }
  P.phone.visible = !!s.phone;
  // hands on hips / clap
  if (s.clap) {
    const a = s.clap;
    const c = Math.sin(t * 14) * 0.12;
    P.shL.rotation.x = lerp(P.shL.rotation.x, -1.0, a);
    P.shR.rotation.x = lerp(P.shR.rotation.x, -1.0, a);
    P.shL.rotation.z = lerp(P.shL.rotation.z, 0.45 + c, a);
    P.shR.rotation.z = lerp(P.shR.rotation.z, -0.45 - c, a);
    P.elL.rotation.x = -0.6 * a;
    P.elR.rotation.x = -0.6 * a;
  }

  // head look
  P.head.rotation.y = (s.lookYaw ?? 0) + Math.sin(t * 0.7 + seed) * 0.05;
  P.head.rotation.x = -(s.lookUp ?? 0) + Math.sin(t * 0.5 + seed * 2) * 0.03;
  P.head.rotation.z = s.tilt ?? 0;
  if (s.lookUp) P.torso.rotation.x -= s.lookUp * 0.15;

  // blink every ~3.5s
  const bt = (t + seed * 0.37) % 3.7;
  const blink = bt < 0.12 ? Math.sin((bt / 0.12) * Math.PI) : 0;
  const closed = s.eyesClosed ?? 0;
  for (const e of P.eyes) e.scale.y = Math.max(0.08, 1 - Math.max(blink, closed) * 0.92);

  // mouth
  const talk = s.talk ? Math.max(0, Math.sin(t * 13 + seed)) * s.talk : 0;
  const laugh = s.laugh ?? 0;
  P.mouthOpen.visible = talk > 0.15 || laugh > 0.1;
  P.mouthOpen.scale.set(1 + laugh * 0.5, 0.6 * Math.max(talk, laugh), 0.35);
  P.mouth.scale.setScalar(1 + (s.bigSmile ?? 0) * 0.6 + laugh * 0.3);
  if (laugh) P.hips.position.y += Math.abs(Math.sin(t * 16)) * 0.02 * laugh;

  if (P.tail) P.tail.rotation.z = Math.sin(t * 3 + seed) * 0.15 * (0.3 + walk + (s.bounce ? 2 : 0));
}

// ---------- Tuk-tuk ----------
export function makeTukTuk() {
  const g = new THREE.Group();
  const body = M(0x2a6fd0, { rough: 0.35, metal: 0.1 });
  const red = M(0xe03a3a, { rough: 0.5 });
  const dark = M(0x222226, { rough: 0.6 });
  const chrome = M(0xcfd4dc, { rough: 0.2, metal: 0.9 });
  const seatM = M(0x8a2a2a, { rough: 0.6 });
  const wood = M(0x9a6a40, { rough: 0.8 });
  const wheels = [];
  const wheel = (x, z, r = 0.34) => {
    const w = new THREE.Group();
    const tire = mesh(new THREE.TorusGeometry(r * 0.78, r * 0.24, 10, 24), dark);
    const hub = mesh(new THREE.CylinderGeometry(r * 0.5, r * 0.5, 0.1, 16), chrome, [0, 0, 0], [Math.PI / 2, 0, 0]);
    w.add(tire, hub);
    for (let i = 0; i < 5; i++) {
      const sp = mesh(new THREE.BoxGeometry(0.03, r * 1.3, 0.04), chrome, [0, 0, 0], [0, 0, (i / 5) * Math.PI]);
      w.add(sp);
    }
    w.rotation.y = Math.PI / 2;
    w.position.set(x, r, z);
    g.add(w);
    wheels.push({ w, r });
    return w;
  };
  // carriage (rear), faces +z (forward)
  const floor = box(1.5, 0.12, 1.7, wood, [0, 0.62, -0.35]);
  g.add(floor);
  const skirt = box(1.56, 0.35, 1.76, body, [0, 0.45, -0.35]);
  g.add(skirt);
  for (const s of [-1, 1]) {
    const side = box(0.06, 0.35, 1.7, body, [0.75 * s, 0.82, -0.35]);
    g.add(side);
    const trim = box(0.08, 0.06, 1.72, red, [0.76 * s, 1.0, -0.35]);
    g.add(trim);
  }
  const backW = box(1.5, 0.6, 0.06, body, [0, 0.95, -1.2]);
  g.add(backW);
  // benches: rear bench faces forward, front bench faces backward
  const b1 = box(1.36, 0.14, 0.45, seatM, [0, 0.95, -0.95]);
  const b1b = box(1.36, 0.55, 0.1, seatM, [0, 1.25, -1.13]);
  const b2 = box(1.36, 0.14, 0.4, seatM, [0, 0.95, 0.28]);
  const b2b = box(1.36, 0.5, 0.1, seatM, [0, 1.22, 0.45]);
  g.add(b1, b1b, b2, b2b);
  // posts & canopy
  for (const x of [-0.72, 0.72]) for (const z of [-1.18, 0.5]) g.add(mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.5, 8), chrome, [x, 1.45, z]));
  const canopy = box(1.7, 0.08, 2.0, M(0x1f5fb8, { rough: 0.6 }), [0, 2.22, -0.35]);
  g.add(canopy);
  // valance around the roof so it reads from the side
  for (const s of [-1, 1]) {
    g.add(box(0.04, 0.2, 2.04, M(0x1f5fb8, { rough: 0.6 }), [0.86 * s, 2.3, -0.35]));
    g.add(box(1.74, 0.2, 0.04, M(0x1f5fb8, { rough: 0.6 }), [0, 2.3, -0.35 + 1.01 * s]));
  }
  g.add(box(1.74, 0.05, 2.04, M(0xf2d03a, { rough: 0.5 }), [0, 2.41, -0.35]));
  const canopyTop = mesh(new THREE.CylinderGeometry(0.9, 0.9, 1.98, 24, 1, false, -Math.PI / 2, Math.PI), M(0x1f5fb8, { rough: 0.6 }), [0, 2.24, -0.35], [Math.PI / 2, 0, 0]);
  canopyTop.scale.set(0.95, 1, 0.22);
  g.add(canopyTop);
  // scalloped fringe
  for (let i = 0; i < 14; i++) {
    for (const s of [-1, 1]) {
      const f = mesh(new THREE.SphereGeometry(0.07, 8, 6, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), red, [0.86 * s, 2.18, -1.3 + i * 0.145]);
      g.add(f);
    }
  }
  wheel(-0.86, -0.55, 0.36);
  wheel(0.86, -0.55, 0.36);
  // hitch
  g.add(box(0.1, 0.1, 1.0, dark, [0, 0.55, 0.9]));
  // motorbike in front
  const moto = new THREE.Group();
  moto.position.set(0, 0, 1.75);
  g.add(moto);
  const tank = mesh(new THREE.CapsuleGeometry(0.16, 0.5, 6, 12), M(0xd83a3a, { rough: 0.3, metal: 0.2 }), [0, 0.78, 0], [Math.PI / 2, 0, 0]);
  moto.add(tank);
  const seat = mesh(new THREE.CapsuleGeometry(0.13, 0.4, 6, 12), dark, [0, 0.93, -0.3], [Math.PI / 2, 0, 0]);
  seat.scale.set(1.2, 1, 0.5);
  moto.add(seat);
  const engine = box(0.3, 0.3, 0.4, chrome, [0, 0.5, -0.1]);
  moto.add(engine);
  const fork = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.9, 8), chrome, [0, 0.72, 0.5], [0.35, 0, 0]);
  moto.add(fork);
  const bar = mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.7, 8), chrome, [0, 1.15, 0.38], [0, 0, Math.PI / 2]);
  moto.add(bar);
  const lamp = mesh(new THREE.SphereGeometry(0.1, 16, 12), M(0xfff4c0, { emissive: 0xffe8a0, ei: 1.5 }), [0, 1.02, 0.55]);
  moto.add(lamp);
  const w = wheel(0, 0, 0.32);
  g.remove(w);
  w.position.set(0, 0.32, 1.95);
  g.add(w);
  g.traverse((c) => {
    if (c.isMesh) {
      c.castShadow = true;
      c.receiveShadow = true;
    }
  });
  return { root: g, wheels, driverPos: new THREE.Vector3(0, 0, 1.45), seats: [
    // [x, z, facing(ry)] relative to tuk-tuk
    { x: -0.34, z: -0.95, ry: 0 },
    { x: 0.34, z: -0.95, ry: 0 },
    { x: -0.34, z: 0.28, ry: Math.PI },
    { x: 0.34, z: 0.28, ry: Math.PI },
  ] };
}

function box(w, h, d, mat, pos) {
  return mesh(new THREE.BoxGeometry(w, h, d), mat, pos);
}

export function spinWheels(tt, dist) {
  for (const { w, r } of tt.wheels) w.rotation.z = dist / r;
}
