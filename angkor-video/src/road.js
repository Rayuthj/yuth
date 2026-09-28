import * as THREE from 'three';
import { groundMat, stoneMat, mesh, box, rng, prep, merge, mtx, M } from './util.js';
import { Atmos, sugarPalmGeo, broadTreeGeo, farTreeGeo, bushGeo, leafMat, vcMat, scatter, Flock } from './env.js';

// Road runs along -Z (travel direction). Road centre x = 0.
export function buildRoad() {
  const scene = new THREE.Scene();
  const atmos = new Atmos(scene, { seed: 21, clouds: 16 });
  const r = rng(99);
  const gy = 0.3;

  // base ground (grass)
  const g = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), groundMat({ a: 0x6a9e3a, b: 0x9cc452, c: 0x7f8a3a, scale: 0.04, key: 'road' }));
  g.rotation.x = -Math.PI / 2;
  g.position.y = gy;
  g.receiveShadow = true;
  scene.add(g);

  // red laterite road
  const roadMat = groundMat({ a: 0xb4583a, b: 0xcf7e52, c: 0x94462e, scale: 0.12, key: 'laterite' });
  const road = new THREE.Mesh(new THREE.PlaneGeometry(7.5, 900, 1, 1), roadMat);
  road.rotation.x = -Math.PI / 2;
  road.position.set(0, gy + 0.03, -250);
  road.receiveShadow = true;
  scene.add(road);
  // soft verges
  for (const s of [-1, 1]) {
    const v = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 900), groundMat({ a: 0x9a8a4a, b: 0x7a8a3a, c: 0xa0663a, scale: 0.2, key: 'verge' }));
    v.rotation.x = -Math.PI / 2;
    v.position.set(s * 4.5, gy + 0.02, -250);
    v.receiveShadow = true;
    scene.add(v);
  }

  // rice paddies with water, dikes and seedlings
  const paddyWater = new THREE.MeshStandardMaterial({ color: 0x6a8a90, roughness: 0.06, metalness: 0, envMapIntensity: 1.6 });
  const lushRice = groundMat({ a: 0x7fc24a, b: 0xa6d85a, c: 0x6aa83a, scale: 0.3, key: 'rice' });
  const dikeParts = [];
  const lushParts = [];
  const waterParts = [];
  const tufts = [];
  const pw = 22;
  const pd = 18;
  for (const side of [-1, 1]) {
    for (let ix = 0; ix < 7; ix++) {
      for (let iz = 0; iz < 36; iz++) {
        const x0 = side * (9 + ix * pw);
        const cx = x0 + side * pw * 0.5;
        const cz = 120 - iz * pd;
        const lush = r() < 0.45;
        (lush ? lushParts : waterParts).push(prep(new THREE.PlaneGeometry(pw - 1.2, pd - 1.2), 0xffffff, mtx([cx, lush ? gy + 0.05 : gy + 0.01, cz], [-Math.PI / 2, 0, 0])));
        dikeParts.push(prep(new THREE.BoxGeometry(pw, 0.35, 1.2), 0xffffff, mtx([cx, gy + 0.08, cz - pd / 2])));
        dikeParts.push(prep(new THREE.BoxGeometry(1.2, 0.35, pd), 0xffffff, mtx([x0, gy + 0.08, cz])));
        if (!lush && ix < 3) {
          for (let k = 0; k < 110; k++) {
            tufts.push({ x: cx + (r() - 0.5) * (pw - 3), z: cz + (r() - 0.5) * (pd - 3), y: gy, s: 0.7 + r() * 0.6 });
          }
        }
      }
    }
  }
  for (const [parts, mat] of [
    [lushParts, lushRice],
    [waterParts, paddyWater],
  ]) {
    const pm = new THREE.Mesh(merge(parts), mat);
    pm.receiveShadow = true;
    scene.add(pm);
  }
  const dikes = new THREE.Mesh(merge(dikeParts), groundMat({ a: 0x7a9a44, b: 0x8a7a4a, c: 0x6a8a3a, scale: 0.3, key: 'dike' }));
  dikes.receiveShadow = true;
  scene.add(dikes);
  const tuftGeo = merge(
    Array.from({ length: 5 }, (_, i) => {
      const cg = new THREE.ConeGeometry(0.05, 0.6, 4);
      cg.translate(0, 0.3, 0);
      return prep(cg, i % 2 ? 0x8fd04a : 0x6fb83a, mtx([Math.cos(i * 1.3) * 0.08, 0, Math.sin(i * 1.3) * 0.08], [Math.cos(i * 2) * 0.35, 0, Math.sin(i * 2) * 0.35]));
    })
  );
  scatter(scene, [tuftGeo], vcMat(), tufts, 31, false, 60);

  // palms and trees
  const palms = [];
  const trees = [];
  const bushes = [];
  for (let i = 0; i < 520; i++) {
    const side = r() < 0.5 ? -1 : 1;
    const x = side * (side > 0 ? 10.5 : 7) + side * Math.pow(r(), 1.3) * 200;
    const z = 140 - r() * 700;
    const k = r();
    if (Math.abs(x) < 12 && k < 0.5) bushes.push({ x, z, y: gy });
    else if (k < 0.55) palms.push({ x, z, y: gy, s: 0.8 + r() * 0.4 });
    else if (k < 0.8) trees.push({ x, z, y: gy });
    else bushes.push({ x, z, y: gy });
  }
  // rows of palms along the road
  for (let z = 120; z > -560; z -= 9 + r() * 14) {
    if (r() < 0.6) palms.push({ x: -(6.5 + r() * 3), z, y: gy });
    if (r() < 0.6) palms.push({ x: 10.5 + r() * 3, z: z - 4, y: gy });
  }
  const farTrees = [];
  for (let i = 0; i < 700; i++) {
    const side = r() < 0.5 ? -1 : 1;
    farTrees.push({ x: side * (170 + r() * 250), z: 200 - r() * 900, y: gy, s: 1 + r() * 0.6 });
  }
  for (let i = 0; i < 160; i++) farTrees.push({ x: (r() - 0.5) * 700, z: -600 - r() * 150, y: gy, s: 1.2 + r() * 0.6 });
  scatter(scene, [sugarPalmGeo(21), sugarPalmGeo(22), sugarPalmGeo(23)], leafMat(), palms, 32, true, 60);
  scatter(scene, [broadTreeGeo(24), broadTreeGeo(25, { leaf: 0x3f7f35 })], vcMat(), trees, 33, true, 60);
  scatter(scene, [bushGeo(26), bushGeo(27, 0x5a9a3a)], vcMat(), bushes, 34, true, 60);
  scatter(scene, [farTreeGeo(28), farTreeGeo(29, 0x4a8a38)], vcMat(), farTrees, 35, false, 150);

  // Khmer stilt houses along the road
  for (let i = 0; i < 9; i++) {
    const side = i % 2 ? 1 : -1;
    const h = stiltHouse(i);
    h.position.set(side * (15 + r() * 6), gy, 60 - i * 58 - r() * 20);
    h.rotation.y = side > 0 ? -Math.PI / 2 : Math.PI / 2;
    scene.add(h);
  }
  // cows grazing
  const cows = [];
  for (let i = 0; i < 5; i++) {
    const c = cow(i);
    c.position.set((i % 2 ? 1 : -1) * (12 + r() * 20), gy, 20 - i * 45);
    c.rotation.y = r() * Math.PI * 2;
    scene.add(c);
    cows.push(c);
  }

  const flock = new Flock(scene, 9, 8, 0x2a2430);
  const tick = (t) => {
    cows.forEach((c, i) => {
      c.userData.head.rotation.x = 0.5 + Math.sin(t * 1.3 + i) * 0.2;
      c.userData.tail.rotation.z = Math.sin(t * 3 + i * 2) * 0.4;
    });
  };
  return { scene, atmos, flock, tick };
}

function stiltHouse(seed) {
  const r = rng(seed + 400);
  const g = new THREE.Group();
  const wood = M([0x8a5a3a, 0x9a6a44, 0x7a4e32][seed % 3], { rough: 0.85 });
  const plank = M([0xb07a4a, 0xc08a58, 0xa06e46][seed % 3], { rough: 0.85 });
  const roofC = [0xb04a36, 0x8a9aa4, 0xc05a3a][seed % 3];
  const roofM = M(roofC, { rough: 0.6, metal: roofC === 0x8a9aa4 ? 0.3 : 0 });
  const W = 7 + r() * 2;
  const D = 5;
  const post = new THREE.CylinderGeometry(0.14, 0.16, 2.6, 6);
  for (const x of [-W / 2 + 0.3, 0, W / 2 - 0.3]) for (const z of [-D / 2 + 0.3, D / 2 - 0.3]) g.add(mesh(post, wood, [x, 1.3, z]));
  g.add(box(W, 0.2, D, wood, [0, 2.6, 0]));
  g.add(box(W - 0.4, 2.4, D - 0.4, plank, [0, 3.9, 0]));
  // windows & door
  const dark = M(0x3a2a20, { rough: 0.9 });
  g.add(box(1.0, 1.7, 0.1, dark, [W * 0.2, 3.7, D / 2 - 0.15]));
  for (const x of [-W * 0.3, -W * 0.05]) {
    g.add(box(0.9, 0.7, 0.1, dark, [x, 4.2, D / 2 - 0.15]));
    g.add(box(0.95, 0.75, 0.06, M(0x3a7ac0), [x - 0.6, 4.2, D / 2 - 0.1], [0, 0.6, 0]));
  }
  // steep gable roof
  const shape = new THREE.Shape();
  shape.moveTo(-D / 2 - 0.9, 0);
  shape.lineTo(D / 2 + 0.9, 0);
  shape.lineTo(0, 2.6);
  shape.closePath();
  const rg = new THREE.ExtrudeGeometry(shape, { depth: W + 1.2, bevelEnabled: false });
  rg.translate(0, 0, -(W + 1.2) / 2);
  const roof = mesh(rg, roofM, [0, 5.05, 0], [0, Math.PI / 2, 0]);
  g.add(roof);
  // ladder
  const lad = new THREE.Group();
  for (let i = 0; i < 6; i++) lad.add(box(1.0, 0.06, 0.25, wood, [0, 0.4 * i + 0.2, 0]));
  lad.add(box(0.08, 2.8, 0.08, wood, [-0.5, 1.3, 0]), box(0.08, 2.8, 0.08, wood, [0.5, 1.3, 0]));
  lad.position.set(W * 0.2, 0, D / 2 + 0.8);
  lad.rotation.x = -0.35;
  g.add(lad);
  // water jars
  g.add(mesh(new THREE.SphereGeometry(0.45, 14, 10), M(0x6a4a3a, { rough: 0.5 }), [-W * 0.35, 0.45, D / 2 + 0.7]));
  g.add(mesh(new THREE.SphereGeometry(0.4, 14, 10), M(0x7a5a3a, { rough: 0.5 }), [-W * 0.35 + 0.9, 0.4, D / 2 + 0.9]));
  g.traverse((c) => c.isMesh && ((c.castShadow = true), (c.receiveShadow = true)));
  return g;
}

function cow(seed) {
  const g = new THREE.Group();
  const white = M(0xf0e8dc, { rough: 0.8 });
  const dark = M(0x3a302a, { rough: 0.7 });
  const body = mesh(new THREE.CapsuleGeometry(0.55, 1.1, 6, 14), white, [0, 1.25, 0], [Math.PI / 2, 0, 0]);
  g.add(body);
  const hump = mesh(new THREE.SphereGeometry(0.35, 12, 8), white, [0, 1.75, 0.55]);
  g.add(hump);
  for (const x of [-0.3, 0.3]) for (const z of [-0.6, 0.6]) g.add(mesh(new THREE.CylinderGeometry(0.1, 0.08, 1.0, 8), white, [x, 0.5, z]), mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.1, 8), dark, [x, 0.05, z]));
  const head = new THREE.Group();
  head.position.set(0, 1.5, 1.05);
  g.add(head);
  const skull = mesh(new THREE.CapsuleGeometry(0.22, 0.4, 6, 12), white, [0, 0, 0.3], [Math.PI / 2 - 0.4, 0, 0]);
  head.add(skull);
  head.add(mesh(new THREE.SphereGeometry(0.2, 10, 8), M(0xe8b8a8), [0, -0.2, 0.58]));
  for (const s of [-1, 1]) {
    head.add(mesh(new THREE.ConeGeometry(0.05, 0.3, 6), dark, [0.15 * s, 0.25, 0.1], [0, 0, -0.5 * s]));
    head.add(mesh(new THREE.SphereGeometry(0.1, 8, 6), white, [0.25 * s, 0.1, 0.15], [0, 0, 0], [1.4, 0.5, 0.7]));
    head.add(mesh(new THREE.SphereGeometry(0.04, 8, 6), dark, [0.13 * s, 0.05, 0.42]));
  }
  const tail = new THREE.Group();
  tail.position.set(0, 1.4, -1.05);
  tail.add(mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.8, 5), white, [0, -0.4, 0]));
  tail.add(mesh(new THREE.SphereGeometry(0.07, 6, 5), dark, [0, -0.8, 0]));
  g.add(tail);
  g.userData = { head, tail };
  g.traverse((c) => c.isMesh && ((c.castShadow = true), (c.receiveShadow = true)));
  g.scale.setScalar(0.9 + (seed % 3) * 0.05);
  return g;
}
