import * as THREE from 'three';
import { stoneMat, groundMat, lotusTowerGeo, stairsGeo, roofGeo, mesh, box, rng, prep, merge, mtx, M } from './util.js';
import { Atmos, sugarPalmGeo, broadTreeGeo, farTreeGeo, bushGeo, leafMat, vcMat, scatter, Flock } from './env.js';

const CREASE = 0x8a8070;

// One serene Bayon face on the +z side of a block of width w, centred at (0, yc)
function faceParts(w, yc) {
  const f = w;
  const z0 = w / 2;
  const P = [];
  const S = (r, pos, scl, color = 0xffffff, seg = [12, 8]) => P.push(prep(new THREE.SphereGeometry(r, seg[0], seg[1]), color, mtx(pos, [0, 0, 0], scl)));
  const CAP = (r, len, pos, rot, color = 0xffffff) => P.push(prep(new THREE.CapsuleGeometry(r, len, 3, 8), color, mtx(pos, rot)));
  const ARC = (R, tube, arc, pos, color = CREASE, rotX = 0) =>
    P.push(prep(new THREE.TorusGeometry(R, tube, 4, 12, arc), color, mtx(pos, [rotX, 0, -Math.PI / 2 - arc / 2])));

  // diadem band with jewels
  P.push(prep(new THREE.BoxGeometry(f * 0.98, f * 0.12, f * 0.07), 0xf2eee6, mtx([0, yc + f * 0.37, z0 + f * 0.03])));
  for (let i = -3; i <= 3; i++) S(f * 0.04, [i * f * 0.13, yc + f * 0.37, z0 + f * 0.07], [1, 1, 0.6], 0xffffff, [8, 6]);
  P.push(prep(new THREE.BoxGeometry(f * 0.98, f * 0.05, f * 0.05), 0xe8e2d8, mtx([0, yc + f * 0.45, z0 + f * 0.02])));
  // forehead
  S(f * 0.4, [0, yc + f * 0.2, z0 - f * 0.1], [1.1, 0.4, 0.35]);
  // brows (gentle arches meeting at the nose)
  for (const s of [-1, 1]) {
    P.push(prep(new THREE.TorusGeometry(f * 0.15, f * 0.028, 5, 12, 2.0), 0xffffff, mtx([s * f * 0.19, yc + f * 0.1, z0 + f * 0.03], [0, 0, Math.PI / 2 - 1.0])));
  }
  // eyes: downcast lids with a dark slit
  for (const s of [-1, 1]) {
    S(f * 0.1, [s * f * 0.19, yc + f * 0.12, z0 + f * 0.01], [1.25, 0.42, 0.45]);
    ARC(f * 0.13, f * 0.011, 1.1, [s * f * 0.19, yc + f * 0.235, z0 + f * 0.052]);
  }
  // nose
  S(f * 0.1, [0, yc + f * 0.02, z0 + f * 0.03], [0.62, 1.55, 0.72]);
  S(f * 0.1, [0, yc - f * 0.11, z0 + f * 0.05], [1.05, 0.62, 0.72]);
  for (const s of [-1, 1]) S(f * 0.04, [s * f * 0.065, yc - f * 0.13, z0 + f * 0.07], [1, 0.75, 0.5], 0xf0ece4, [8, 6]);
  // cheeks
  for (const s of [-1, 1]) S(f * 0.2, [s * f * 0.27, yc - f * 0.1, z0 - f * 0.05], [1, 1.05, 0.45]);
  // smiling lips
  CAP(f * 0.042, f * 0.2, [0, yc - f * 0.225, z0 + f * 0.035], [0, 0, Math.PI / 2]);
  CAP(f * 0.048, f * 0.16, [0, yc - f * 0.3, z0 + f * 0.03], [0, 0, Math.PI / 2]);
  for (const s of [-1, 1]) S(f * 0.035, [s * f * 0.15, yc - f * 0.225, z0 + f * 0.03], [1, 1, 0.8]);
  ARC(f * 0.24, f * 0.012, 1.05, [0, yc - f * 0.26 + f * 0.24 * 1.0 - f * 0.0, z0 + f * 0.075], CREASE);
  // chin
  S(f * 0.14, [0, yc - f * 0.4, z0 - f * 0.02], [1.1, 0.7, 0.45]);
  // long earlobes
  for (const s of [-1, 1]) {
    CAP(f * 0.055, f * 0.32, [s * f * 0.47, yc - f * 0.02, z0 - f * 0.01], [0, 0, 0]);
    S(f * 0.06, [s * f * 0.47, yc - f * 0.22, z0 + f * 0.0], [1, 1.3, 0.8]);
  }
  return P;
}

// A complete face tower (4 faces). Returns merged geometry with base at y = 0.
export function faceTowerGeo(w, o = {}) {
  const P = [];
  const plinth = o.plinth ?? 1.2;
  const body = o.body ?? 1.5;
  P.push(prep(new THREE.BoxGeometry(w + 1.8, plinth, w + 1.8), 0xffffff, mtx([0, plinth / 2, 0])));
  P.push(prep(new THREE.BoxGeometry(w + 2.0, 0.25, w + 2.0), 0xe8e4dc, mtx([0, plinth, 0])));
  if (body > 0) P.push(prep(new THREE.BoxGeometry(w + 0.7, body, w + 0.7), 0xffffff, mtx([0, plinth + body / 2, 0])));
  const band = plinth + body;
  P.push(prep(new THREE.BoxGeometry(w + 1.0, 0.35, w + 1.0), 0xe8e4dc, mtx([0, band + 0.17, 0])));
  const f0 = band + 0.35;
  const fh = w * 1.08;
  P.push(prep(new THREE.BoxGeometry(w, fh, w), 0xffffff, mtx([0, f0 + fh / 2, 0])));
  const yc = f0 + fh * 0.5;
  const faces = faceParts(w, yc);
  for (let k = 0; k < 4; k++) {
    const rot = new THREE.Matrix4().makeRotationY((k * Math.PI) / 2);
    for (const g of faces) P.push(g.clone().applyMatrix4(rot));
  }
  // corbelled tiers above
  let y = f0 + fh;
  let tw = w + 0.7;
  for (let i = 0; i < 4; i++) {
    const th = 0.7 - i * 0.08;
    P.push(prep(new THREE.BoxGeometry(tw, th, tw), i % 2 ? 0xe8e4dc : 0xffffff, mtx([0, y + th / 2, 0])));
    y += th;
    tw *= 0.84;
  }
  const crown = lotusTowerGeo(w * 0.9, tw * 0.5, { trunc: 0.7, tiers: 6 });
  P.push(prep(crown, 0xffffff, mtx([0, y, 0])));
  const geo = merge(P);
  geo.userData = { faceCenter: yc, faceZ: w / 2 };
  return geo;
}

export function buildBayon() {
  const scene = new THREE.Scene();
  const atmos = new Atmos(scene, { seed: 31, clouds: 20 });
  const gy = 0.3;
  const r = rng(301);

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), groundMat({ a: 0x62993a, b: 0x8fbb4a, c: 0x8a7a44, scale: 0.05, key: 'bayon' }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = gy;
  ground.receiveShadow = true;
  scene.add(ground);

  const stone = stoneMat(0x9a8a76, { moss: 0.38, ground: gy, mossColor: 0x5a6240, vc: true });
  const stoneP = stoneMat(0x9a8a76, { moss: 0.35, ground: gy, mossColor: 0x5a6240 });
  const T = new THREE.Group();
  scene.add(T);
  const add = (m) => (T.add(m), m);

  // platforms
  add(box(70, 0.6, 70, stoneP, [0, gy + 0.3, 0]));
  add(box(66, 3.0, 66, stoneP, [0, gy + 1.5, 0]));
  add(box(67, 0.35, 67, stoneP, [0, gy + 3.0, 0]));
  const L1 = gy + 3.2;
  add(box(46, 4.0, 46, stoneP, [0, L1 + 2.0, 0]));
  add(box(47, 0.35, 47, stoneP, [0, L1 + 4.0, 0]));
  const L2 = L1 + 4.15;
  // outer low gallery on level 1 (pillars + roof), front side broken
  const pillarGeo = new THREE.BoxGeometry(0.6, 3.2, 0.6);
  const pills = [];
  for (let k = 0; k < 4; k++) {
    const ry = (k * Math.PI) / 2;
    for (let u = -30; u <= 30; u += 2.8) {
      if (Math.abs(u) < 5) continue;
      if (k === 0 && u > 8 && u < 20) continue; // ruined section
      const x = Math.cos(ry) * u + Math.sin(ry) * 31;
      const z = -Math.sin(ry) * u + Math.cos(ry) * 31;
      pills.push([x, z]);
    }
    const g = new THREE.Group();
    g.rotation.y = ry;
    const rf = new THREE.Mesh(roofGeo(60, 3.6, 1.6, 2), stoneP);
    rf.position.set(0, L1 + 3.2, 30);
    rf.castShadow = rf.receiveShadow = true;
    if (k !== 0) g.add(rf);
    g.add(box(60, 3.2, 0.8, stoneP, [0, L1 + 1.6, 29]));
    T.add(g);
  }
  const pim = new THREE.InstancedMesh(pillarGeo, stoneP, pills.length);
  const d = new THREE.Object3D();
  pills.forEach(([x, z], i) => {
    d.position.set(x, L1 + 1.6, z);
    d.updateMatrix();
    pim.setMatrixAt(i, d.matrix);
  });
  pim.castShadow = pim.receiveShadow = true;
  add(pim);
  // stairs
  for (let k = 0; k < 4; k++) {
    const ry = (k * Math.PI) / 2;
    const s1 = mesh(stairsGeo(7, 3.2, 4, 8), stoneP, [Math.sin(ry) * 35, gy, Math.cos(ry) * 35], [0, ry, 0]);
    const s2 = mesh(stairsGeo(6, 4.1, 5, 10), stoneP, [Math.sin(ry) * 25.5, L1, Math.cos(ry) * 25.5], [0, ry, 0]);
    add(s1);
    add(s2);
  }

  // central massif
  add(mesh(new THREE.CylinderGeometry(12, 13, 7, 16), stoneP, [0, L2 + 3.5, 0]));
  add(mesh(new THREE.CylinderGeometry(13.4, 13.4, 0.5, 16), stoneP, [0, L2 + 7.0, 0]));
  const big = faceTowerGeo(7.5, { plinth: 1.0, body: 1.0 });
  add(mesh(big, stone, [0, L2 + 7.2, 0], [0, Math.PI / 8, 0]));

  // ring of face towers on level 2
  const tw = faceTowerGeo(4.6, { plinth: 1.2, body: 0.4 });
  const towers = [];
  const ring2 = [
    [-15, -15], [15, -15], [-15, 15], [15, 15],
    [0, -17], [-17, 0], [17, 0],
    [8.5, 16.5],
  ];
  for (const [x, z] of ring2) {
    const m = mesh(tw, stone, [x, L2, z], [0, 0, 0]);
    add(m);
    towers.push(m);
  }
  const tw2 = faceTowerGeo(4.2, { plinth: 1.0, body: 1.8 });
  for (const [x, z] of [
    [-27, -27], [27, -27], [-27, 27], [27, 27], [-10, -27], [10, -27], [-27, 10], [27, -10],
  ]) {
    add(mesh(tw2, stone, [x, L1, z], [0, 0, 0]));
  }
  // the "hero" tower for close ups: the one at (8.5, 16.5), facing +z
  const hero = towers[towers.length - 1];
  const heroFace = new THREE.Vector3(8.5, L2 + tw.userData.faceCenter, 16.5 + tw.userData.faceZ);

  // fallen stones on level 2 terrace + a block for Leo to stand on
  const rubble = [];
  for (let i = 0; i < 26; i++) {
    const x = (r() - 0.5) * 40;
    const z = 18 + r() * 3.5;
    if (Math.abs(x - 8.5) < 5) continue;
    rubble.push(mesh(new THREE.BoxGeometry(0.8 + r() * 1.2, 0.4 + r() * 0.6, 0.6 + r() * 0.8), stoneP, [x, L2 + 0.25, z], [0, r(), r() * 0.2]));
  }
  rubble.forEach(add);
  const block = add(box(1.4, 2.0, 1.2, stoneP, [11.3, L2 + 1.0, 20.2]));
  add(box(1.2, 1.0, 1.0, stoneP, [12.5, L2 + 0.5, 20.6], [0, 0.3, 0]));

  // jungle around
  const V = new THREE.Group();
  scene.add(V);
  const trees = [];
  const palms = [];
  const far = [];
  for (let i = 0; i < 600; i++) {
    const a = r() * Math.PI * 2;
    const dd = 48 + Math.pow(r(), 0.8) * 180;
    const x = Math.cos(a) * dd;
    const z = Math.sin(a) * dd;
    if (Math.abs(x) < 6 && z > 30) continue;
    if (z > 20 && Math.abs(x) < 75 && dd < 105) continue;
    if (dd > 115) far.push({ x, z, y: gy, s: 1.0 + r() * 0.4 });
    else (r() < 0.15 ? palms : trees).push({ x, z, y: gy, s: 1.0 + r() * 0.5 });
  }
  scatter(V, [broadTreeGeo(41, { h: 10, hv: 6, blob: 3, spread: 4.5, leaf: 0x3f7f35 }), broadTreeGeo(42, { h: 9, hv: 6, blob: 3.2, spread: 4, leaf: 0x4f8f3a }), broadTreeGeo(43, { h: 12, hv: 4, blob: 3.5, spread: 5, leaf: 0x5a9a3a })], vcMat(), trees, 44, true, 60);
  scatter(V, [sugarPalmGeo(45), sugarPalmGeo(46)], leafMat(), palms, 47, true, 60);
  for (let i = 0; i < 500; i++) {
    const a = r() * Math.PI * 2;
    const dd = 230 + r() * 400;
    far.push({ x: Math.cos(a) * dd, z: Math.sin(a) * dd, y: gy, s: 1.2 + r() * 0.6 });
  }
  scatter(V, [farTreeGeo(48), farTreeGeo(49, 0x4a8a38)], vcMat(), far, 50, false, 150);

  const flock = new Flock(scene, 7, 12, 0x2a2a30);
  return { scene, atmos, flock, L2, heroFace, block, stone };
}
