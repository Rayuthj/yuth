import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { stoneMat, groundMat, roofGeo, lotusTowerGeo, stairsGeo, mesh, box, rng, prep, merge, mtx, M } from './util.js';
import { Atmos, sugarPalmGeo, broadTreeGeo, farTreeGeo, bushGeo, leafMat, vcMat, scatter, Flock } from './env.js';

export const WaterShader = {
  uniforms: {
    color: { value: null },
    tDiffuse: { value: null },
    textureMatrix: { value: null },
    time: { value: 0 },
    deep: { value: new THREE.Color(0x24424a) },
  },
  vertexShader: /* glsl */ `
    uniform mat4 textureMatrix;
    varying vec4 vUv;
    varying vec3 vWP;
    void main() {
      vUv = textureMatrix * vec4(position, 1.0);
      vWP = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: /* glsl */ `
    uniform vec3 color; uniform vec3 deep; uniform sampler2D tDiffuse; uniform float time;
    varying vec4 vUv; varying vec3 vWP;
    void main() {
      vec2 w = vec2(
        sin(vWP.x * 0.9 + time * 1.4) + sin(vWP.z * 1.7 - time * 1.1) * 0.6 + sin((vWP.x + vWP.z) * 3.1 + time * 2.3) * 0.25,
        cos(vWP.z * 1.1 + time * 1.2) + sin(vWP.x * 1.9 + time * 0.8) * 0.6 + cos((vWP.x - vWP.z) * 2.7 - time * 2.0) * 0.25
      );
      vec3 V = normalize(cameraPosition - vWP);
      float dist = length(cameraPosition - vWP);
      float amp = 0.0035 * clamp(12.0 / dist, 0.15, 1.0);
      vec4 uv = vUv; uv.xy += w * amp * uv.w;
      vec3 refl = texture2DProj(tDiffuse, uv).rgb;
      float fres = 0.35 + 0.65 * pow(1.0 - max(V.y, 0.0), 4.0);
      vec3 col = mix(deep, refl * color, fres);
      float spark = pow(max(0.0, w.x * w.y), 6.0) * 0.02;
      col += spark * refl;
      gl_FragColor = vec4(col, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
};

function rectPath(x0, z0, x1, z1, hole = false) {
  // Shape lives in XY, rotated to XZ with y -> -z
  const p = hole ? new THREE.Path() : new THREE.Shape();
  p.moveTo(x0, -z0);
  if (!hole) {
    p.lineTo(x1, -z0);
    p.lineTo(x1, -z1);
    p.lineTo(x0, -z1);
  } else {
    p.lineTo(x0, -z1);
    p.lineTo(x1, -z1);
    p.lineTo(x1, -z0);
  }
  p.closePath();
  return p;
}

export const LAYOUT = {
  groundY: 0.3,
  island: [-155, -150, 155, 208],
  moatOuter: [-210, -205, 210, 262],
  pondL: [-66, 96, -22, 130],
  pondR: [22, 96, 66, 130],
  causeway: { x: 4.5, z0: 58, z1: 188, top: 1.6 },
  gopuraZ: 190,
  libZ: 152,
  S: 1.5,
};

export function buildAngkor(renderer) {
  const scene = new THREE.Scene();
  const atmos = new Atmos(scene, { seed: 11, clouds: 18 });
  const L = LAYOUT;
  const gy = L.groundY;

  const stone = stoneMat(0xb0a28a, { moss: 0.28, ground: gy });
  const stoneD = stoneMat(0x958a78, { moss: 0.35, ground: gy, flat: true });
  const roofM = stoneMat(0x9a8f7c, { moss: 0.3, ground: gy, bw: 0.6, bh: 0.35 });
  const laterite = stoneMat(0x9a6448, { moss: 0.3, ground: gy, bw: 0.7, bh: 0.4, mossColor: 0x5a6a3a });

  // ---------- water ----------
  const W = window.RENDER_W || 1920;
  const H = window.RENDER_H || 1080;
  const water = new Reflector(new THREE.PlaneGeometry(1600, 1600), {
    textureWidth: Math.round(W * 0.6),
    textureHeight: Math.round(H * 0.6),
    color: 0xc8d4dc,
    multisample: 0,
    shader: WaterShader,
    clipBias: 0.003,
  });
  water.rotation.x = -Math.PI / 2;
  water.position.y = 0;
  scene.add(water);
  const cheapWater = new THREE.Mesh(
    new THREE.PlaneGeometry(1600, 1600),
    new THREE.MeshStandardMaterial({ color: 0x3a5a66, roughness: 0.08, metalness: 0.0, envMapIntensity: 1.4 })
  );
  cheapWater.rotation.x = -Math.PI / 2;
  cheapWater.receiveShadow = true;
  cheapWater.visible = false;
  scene.add(cheapWater);
  const mirrorHidden = [];
  const origBefore = water.onBeforeRender;
  water.onBeforeRender = function (rdr, scn, cam) {
    const vis = mirrorHidden.map((o) => o.visible);
    mirrorHidden.forEach((o) => (o.visible = false));
    origBefore.call(this, rdr, scn, cam);
    mirrorHidden.forEach((o, i) => (o.visible = vis[i]));
  };
  const setMirror = (on) => {
    water.visible = on;
    cheapWater.visible = !on;
  };

  // ---------- land ----------
  const gmat = groundMat({ a: 0x5f9a3a, b: 0x93bf4e, c: 0x7a8a3a, scale: 0.035 });
  const outer = rectPath(-900, -900, 900, 900);
  outer.holes.push(rectPath(...L.moatOuter, true));
  const og = new THREE.ShapeGeometry(outer);
  og.rotateX(-Math.PI / 2);
  const outerM = new THREE.Mesh(og, gmat);
  outerM.position.y = gy;
  outerM.receiveShadow = true;
  scene.add(outerM);

  const isl = rectPath(...L.island);
  isl.holes.push(rectPath(...L.pondL, true));
  isl.holes.push(rectPath(...L.pondR, true));
  const ig = new THREE.ShapeGeometry(isl);
  ig.rotateX(-Math.PI / 2);
  const islM = new THREE.Mesh(ig, gmat);
  islM.position.y = gy;
  islM.receiveShadow = true;
  scene.add(islM);

  // stone embankments around ponds / island / moat
  const rimParts = [];
  const rim = (x0, z0, x1, z1, w = 1.4) => {
    const cx = (x0 + x1) / 2;
    const cz = (z0 + z1) / 2;
    rimParts.push(prep(new THREE.BoxGeometry(x1 - x0 + w, 1.1, w), 0xffffff, mtx([cx, gy - 0.45, z0])));
    rimParts.push(prep(new THREE.BoxGeometry(x1 - x0 + w, 1.1, w), 0xffffff, mtx([cx, gy - 0.45, z1])));
    rimParts.push(prep(new THREE.BoxGeometry(w, 1.1, z1 - z0 + w), 0xffffff, mtx([x0, gy - 0.45, cz])));
    rimParts.push(prep(new THREE.BoxGeometry(w, 1.1, z1 - z0 + w), 0xffffff, mtx([x1, gy - 0.45, cz])));
    // lower step
    rimParts.push(prep(new THREE.BoxGeometry(x1 - x0 - w, 0.6, w), 0xdddddd, mtx([cx, gy - 0.9, z0 + w * 0.9])));
    rimParts.push(prep(new THREE.BoxGeometry(x1 - x0 - w, 0.6, w), 0xdddddd, mtx([cx, gy - 0.9, z1 - w * 0.9])));
  };
  rim(...L.pondL, 1.0);
  rim(...L.pondR, 1.0);
  rim(...L.island, 2.0);
  rim(...L.moatOuter, 2.0);
  const rimM = new THREE.Mesh(merge(rimParts), stoneMat(0xa89a84, { moss: 0.5, ground: -1, vc: true }));
  rimM.receiveShadow = true;
  rimM.castShadow = true;
  scene.add(rimM);

  const T = new THREE.Group();
  scene.add(T);
  const core = new THREE.Group();
  core.scale.setScalar(L.S);
  T.add(core);

  // ---------- temple ----------
  let add = (m) => (core.add(m), m);
  const pillarGeo = new THREE.BoxGeometry(0.55, 1, 0.55);
  const pillarPlacements = [];
  const roofList = [];

  // galleried enclosure on a rectangle at height y
  function gallery(hx, hz, y, h, width, o = {}) {
    // inner wall
    const wallT = 0.9;
    const sides = [
      [0, hz, hx * 2, 'x'],
      [0, -hz, hx * 2, 'x'],
      [hx, 0, hz * 2, 'z'],
      [-hx, 0, hz * 2, 'z'],
    ];
    for (const [cx, cz, len, ax] of sides) {
      const inward = ax === 'x' ? -Math.sign(cz) : -Math.sign(cx);
      const wx = ax === 'x' ? cx : cx + inward * (width / 2 - wallT / 2);
      const wz = ax === 'x' ? cz + inward * (width / 2 - wallT / 2) : cz;
      add(box(ax === 'x' ? len : wallT, h, ax === 'x' ? wallT : len, stone, [wx, y + h / 2, wz]));
      // outer pillars (or outer wall with windows)
      if (o.solidOuter) {
        const ox = ax === 'x' ? cx : cx - inward * (width / 2 - wallT / 2);
        const oz = ax === 'x' ? cz - inward * (width / 2 - wallT / 2) : cz;
        add(box(ax === 'x' ? len : wallT, h * 0.35, ax === 'x' ? wallT : len, stone, [ox, y + h * 0.175, oz]));
        add(box(ax === 'x' ? len : wallT, h * 0.18, ax === 'x' ? wallT : len, stone, [ox, y + h - h * 0.09, oz]));
      }
      const n = Math.floor(len / (o.spacing ?? 2.6));
      for (let i = 0; i <= n; i++) {
        const u = -len / 2 + (i / n) * len;
        const px = ax === 'x' ? cx + u : cx - inward * (width / 2 - 0.4);
        const pz = ax === 'x' ? cz - inward * (width / 2 - 0.4) : cz + u;
        if (o.solidOuter) {
          pillarPlacements.push({ x: px, y: y + h * 0.35, z: pz, sy: h * 0.47, sx: 0.35 });
        } else {
          pillarPlacements.push({ x: px, y, z: pz, sy: h });
        }
      }
      // roof
      const r = roofGeo(len + width * 0.6, width + 1.2, 2.2 + width * 0.12, 2);
      const rm = new THREE.Mesh(r, roofM);
      rm.position.set(cx, y + h, cz);
      if (ax === 'z') rm.rotation.y = Math.PI / 2;
      rm.castShadow = rm.receiveShadow = true;
      add(rm);
      // architrave
      add(box(ax === 'x' ? len + width : width + 0.4, 0.5, ax === 'x' ? width + 0.4 : len + width, stoneD, [cx, y + h - 0.1, cz]));
    }
    // corner pavilions
    if (o.cornerTower) {
      for (const sx of [-1, 1])
        for (const sz of [-1, 1]) {
          add(box(width + 1.4, h + 0.6, width + 1.4, stone, [sx * hx, y + (h + 0.6) / 2, sz * hz]));
          const tg = lotusTowerGeo(o.cornerTower.h, o.cornerTower.r, { trunc: o.cornerTower.trunc ?? 1 });
          const tm = mesh(tg, stoneD, [sx * hx, y + h + 0.6, sz * hz]);
          add(tm);
        }
    }
  }

  // Level 1
  add(box(74, 0.5, 64, stoneD, [0, gy + 0.25, 0]));
  add(box(72, 2.2, 62, stone, [0, gy + 1.1, 0]));
  add(box(72.8, 0.35, 62.8, stoneD, [0, 2.5, 0]));
  gallery(34.5, 29.5, 2.5, 4.2, 4.6, { cornerTower: { h: 5.5, r: 2.2, trunc: 0.55 } });
  // Level 2
  add(box(50, 6.5, 42, stone, [0, 2.5 + 3.25, 0]));
  add(box(50.8, 0.4, 42.8, stoneD, [0, 9.0, 0]));
  gallery(23.5, 19.5, 9.0, 3.8, 3.6, { solidOuter: true, cornerTower: { h: 9, r: 2.0 } });
  // Level 3 (Bakan)
  add(box(33, 1.2, 33, stoneD, [0, 9.6, 0]));
  add(box(31, 11, 31, stone, [0, 9 + 5.5, 0]));
  add(box(29.6, 0.6, 29.6, stoneD, [0, 20.3, 0]));
  add(box(31.8, 0.5, 31.8, stoneD, [0, 20.1, 0]));
  gallery(13.5, 13.5, 20.6, 3.4, 3.2, { solidOuter: true });
  // cruciform inner galleries
  for (const ax of ['x', 'z']) {
    const r = new THREE.Mesh(roofGeo(24, 4.2, 2.6, 2), roofM);
    r.position.set(0, 24, 0);
    if (ax === 'z') r.rotation.y = Math.PI / 2;
    r.castShadow = r.receiveShadow = true;
    add(r);
    add(box(ax === 'x' ? 24 : 3.2, 3.4, ax === 'x' ? 3.2 : 24, stone, [0, 22.3, 0]));
  }
  // corner towers on level 3
  for (const sx of [-1, 1])
    for (const sz of [-1, 1]) {
      add(box(6.5, 4.4, 6.5, stone, [sx * 13.5, 20.6 + 2.2, sz * 13.5]));
      add(box(7.2, 0.5, 7.2, stoneD, [sx * 13.5, 25.0, sz * 13.5]));
      add(mesh(lotusTowerGeo(16, 3.2, { tiers: 8 }), stoneD, [sx * 13.5, 25.2, sz * 13.5]));
    }
  // central tower
  add(box(11, 5, 11, stone, [0, 20.6 + 2.5, 0]));
  add(box(12, 0.6, 12, stoneD, [0, 25.8, 0]));
  add(box(9.5, 3.5, 9.5, stone, [0, 27.8, 0]));
  add(mesh(lotusTowerGeo(20, 4.4, { tiers: 10 }), stoneD, [0, 29.4, 0]));

  // stairs on all 4 sides of each level
  const stairM = stoneD;
  const stairs = (w, h, d, n, x, y, z, ry) => {
    const s = new THREE.Mesh(stairsGeo(w, h, d, n), stairM);
    s.position.set(x, y, z);
    s.rotation.y = ry;
    s.castShadow = s.receiveShadow = true;
    add(s);
  };
  for (let k = 0; k < 4; k++) {
    const ry = (k * Math.PI) / 2;
    const dx = Math.sin(ry);
    const dz = Math.cos(ry);
    stairs(4.2, 11.3, 9, 26, dx * (15.5 + 4.5), 9.3, dz * (15.5 + 4.5), ry);
    // side walls of stairs
    for (const s of [-1, 1]) {
      const sw = box(0.6, 11.3, 9.2, stoneD, [0, 0, 0]);
      sw.geometry = stairsGeo(0.6, 11.6, 9.2, 26);
      sw.position.set(dx * 20 + Math.cos(ry) * s * 2.4, 9.3, dz * 20 - Math.sin(ry) * s * 2.4);
      sw.rotation.y = ry;
      add(sw);
    }
    const l2len = k % 2 === 0 ? 21 : 25;
    stairs(6, 6.5, 5, 14, dx * (l2len + 2.5), 2.5, dz * (l2len + 2.5), ry);
    const l1len = k % 2 === 0 ? 31 : 36;
    stairs(8, 2.2, 3, 6, dx * (l1len + 1.5), gy, dz * (l1len + 1.5), ry);
  }
  // entrance porches (gopura) on gallery 1, all sides
  for (let k = 0; k < 4; k++) {
    const ry = (k * Math.PI) / 2;
    const dx = Math.sin(ry);
    const dz = Math.cos(ry);
    const l1len = k % 2 === 0 ? 29.5 : 34.5;
    const g = new THREE.Group();
    g.position.set(dx * (l1len - 1.2), 2.5, dz * (l1len - 1.2));
    g.rotation.y = ry;
    g.add(box(9, 5.2, 6.5, stone, [0, 2.6, 0]));
    g.add(box(3.2, 3.6, 0.3, M(0x2a2420), [0, 1.8, 3.28]));
    const r = new THREE.Mesh(roofGeo(8, 10, 3.2, 3), roofM);
    r.rotation.y = Math.PI / 2;
    r.position.y = 5.2;
    r.castShadow = r.receiveShadow = true;
    g.add(r);
    const tw = mesh(lotusTowerGeo(7, 2.2, { trunc: 0.6 }), stoneD, [0, 6.3, 0]);
    g.add(tw);
    add(g);
  }

  // pillars of the core (scaled with the core)
  {
    const pim = new THREE.InstancedMesh(pillarGeo, stone, pillarPlacements.length);
    const d = new THREE.Object3D();
    pillarPlacements.forEach((p, i) => {
      d.position.set(p.x, p.y + p.sy / 2, p.z);
      d.scale.set(p.sx ?? 1, p.sy, p.sx ?? 1);
      d.updateMatrix();
      pim.setMatrixAt(i, d.matrix);
    });
    pim.castShadow = pim.receiveShadow = true;
    core.add(pim);
    pillarPlacements.length = 0;
  }
  add = (m) => (T.add(m), m);

  // cruciform terrace in front
  add(box(26, 1.5, 8, stone, [0, gy + 0.75, 53]));
  add(box(10, 1.5, 16, stone, [0, gy + 0.75, 57]));
  add(box(26.6, 0.3, 8.6, stoneD, [0, gy + 1.5, 53]));
  const pillarsT = [];

  // ---------- causeway with naga balustrade ----------
  const C = L.causeway;
  const clen = C.z1 - C.z0;
  add(box(C.x * 2, C.top - gy + 0.3, clen, stone, [0, gy + (C.top - gy) / 2 - 0.15, (C.z0 + C.z1) / 2]));
  const postPlacements = [];
  const nagaM = stoneMat(0xa8987e, { moss: 0.35, ground: gy });
  for (const s of [-1, 1]) {
    const rail = mesh(new THREE.CylinderGeometry(0.34, 0.34, clen - 6, 12), nagaM, [s * (C.x - 0.3), C.top + 0.95, (C.z0 + C.z1) / 2], [Math.PI / 2, 0, 0]);
    add(rail);
    for (let z = C.z0 + 3.5; z < C.z1 - 3; z += 3.3) postPlacements.push({ x: s * (C.x - 0.3), y: C.top, z, sy: 0.9 });
  }
  const naga = nagaGeo();
  for (const [z, dir] of [
    [C.z1 - 2.6, 1],
    [C.z0 + 2.6, -1],
  ])
    for (const s of [-1, 1]) {
      const n = new THREE.Mesh(naga, nagaM);
      n.position.set(s * (C.x - 0.3), C.top, z);
      n.rotation.y = dir > 0 ? 0 : Math.PI;
      n.castShadow = n.receiveShadow = true;
      add(n);
    }
  // outer causeway across moat
  add(box(12, 1.6, L.moatOuter[3] - L.island[3] + 6, stone, [0, 0.5, (L.moatOuter[3] + L.island[3]) / 2]));
  // simple stepped entry platforms at both ends of the inner causeway
  add(box(14, 1.2, 5, stoneD, [0, gy + 0.6, C.z1 - 1]));

  // pillars instanced
  const allPillars = [...postPlacements, ...pillarsT];
  const pim = new THREE.InstancedMesh(pillarGeo, stone, allPillars.length);
  const d = new THREE.Object3D();
  allPillars.forEach((p, i) => {
    d.position.set(p.x, p.y + p.sy / 2, p.z);
    d.scale.set(p.sx ?? 1, p.sy, p.sx ?? 1);
    d.rotation.set(0, 0, 0);
    d.updateMatrix();
    pim.setMatrixAt(i, d.matrix);
  });
  pim.castShadow = pim.receiveShadow = true;
  add(pim);

  // ---------- libraries ----------
  for (const s of [-1, 1]) {
    const g = new THREE.Group();
    g.position.set(s * 28, gy, L.libZ);
    g.add(box(10, 1.8, 7, stone, [0, 0.9, 0]));
    g.add(box(8, 4, 5, stone, [0, 3.8, 0]));
    const r = new THREE.Mesh(roofGeo(8.5, 6.4, 3.2, 2), roofM);
    r.rotation.y = Math.PI / 2;
    r.position.y = 5.8;
    r.castShadow = r.receiveShadow = true;
    g.add(r);
    g.add(box(2.4, 1.8, 5, stone, [s * -5, 0.9, 0]));
    add(g);
  }

  // ---------- west gopura + enclosure wall ----------
  const GZ = L.gopuraZ;
  const wallZ = [GZ, -145];
  for (const z of wallZ) {
    for (const s of [-1, 1]) add(box(104, 4.5, 1.4, laterite, [s * 96, gy + 2.25, z]));
  }
  for (const s of [-1, 1]) add(box(1.4, 4.5, GZ + 145, laterite, [s * 148, gy + 2.25, (GZ - 145) / 2]));
  // gopura gallery with pillars and roof
  const gp = new THREE.Group();
  gp.position.set(0, gy, GZ);
  gp.add(box(80, 1.4, 7, stone, [0, 0.7, 0]));
  gp.add(box(80, 4.2, 1, stone, [0, 3.5, -1.5]));
  const gpillars = [];
  for (let x = -39; x <= 39; x += 2.6) if (Math.abs(x) > 8) gpillars.push({ x, y: gy + 1.4, z: GZ + 2.4, sy: 4.2 });
  const gim = new THREE.InstancedMesh(pillarGeo, stone, gpillars.length);
  gpillars.forEach((p, i) => {
    d.position.set(p.x, p.y + p.sy / 2, p.z);
    d.scale.set(1, p.sy, 1);
    d.updateMatrix();
    gim.setMatrixAt(i, d.matrix);
  });
  gim.castShadow = gim.receiveShadow = true;
  add(gim);
  const gr = new THREE.Mesh(roofGeo(80, 7.4, 2.6, 2), roofM);
  gr.position.y = 5.6;
  gr.castShadow = gr.receiveShadow = true;
  gp.add(gr);
  for (const [x, hs] of [
    [0, 1],
    [-24, 0.75],
    [24, 0.75],
  ]) {
    gp.add(box(11 * hs, 7.5 * hs, 10 * hs, stone, [x, (7.5 * hs) / 2, 0]));
    gp.add(box(4 * hs, 5 * hs, 0.3, M(0x2a2420), [x, 2.5 * hs, 5 * hs + 0.02]));
    gp.add(mesh(lotusTowerGeo(12 * hs, 3.6 * hs, { trunc: 0.5 }), stoneD, [x, 7.5 * hs, 0]));
  }
  add(gp);

  // ---------- vegetation ----------
  const V = new THREE.Group();
  scene.add(V);
  const r = rng(77);
  const palmGeos = [sugarPalmGeo(1), sugarPalmGeo(2), sugarPalmGeo(3)];
  const treeGeos = [broadTreeGeo(4), broadTreeGeo(5, { leaf: 0x3f7f35 }), broadTreeGeo(6, { leaf: 0x5a9a3a, h: 8 })];
  const bigTreeGeos = [farTreeGeo(8, 0x3d7a33), farTreeGeo(9, 0x4a8a38), farTreeGeo(12, 0x55903a)];
  const bushGeos = [bushGeo(10), bushGeo(11, 0x3f7a2f)];
  const blocked = (x, z) => {
    if (Math.abs(x) < 72 && z > -68 && z < 92) return true;
    if (Math.abs(x) < 12 && z > 30 && z < 280) return true;
    if (x > L.pondL[0] - 3 && x < L.pondL[2] + 3 && z > L.pondL[1] - 3 && z < L.pondL[3] + 3) return true;
    if (x > L.pondR[0] - 3 && x < L.pondR[2] + 3 && z > L.pondR[1] - 3 && z < L.pondR[3] + 3) return true;
    if (Math.abs(Math.abs(x) - 28) < 9 && Math.abs(z - L.libZ) < 8) return true;
    if (Math.abs(z - GZ) < 8 && Math.abs(x) < 46) return true;
    return false;
  };
  const inIsland = (x, z) => x > L.island[0] + 3 && x < L.island[2] - 3 && z > L.island[1] + 3 && z < L.island[3] - 3;
  const inMoat = (x, z) => x > L.moatOuter[0] - 4 && x < L.moatOuter[2] + 4 && z > L.moatOuter[1] - 4 && z < L.moatOuter[3] + 4;
  const palms = [];
  // famous palms around the ponds
  for (const pond of [L.pondL, L.pondR]) {
    for (let i = 0; i < 14; i++) {
      const side = i % 4;
      const u = r();
      let x, z;
      if (side === 0) (x = pond[0] + u * (pond[2] - pond[0])), (z = pond[1] - 5 - r() * 6);
      else if (side === 1) (x = pond[0] - 5 - r() * 6), (z = pond[1] + u * (pond[3] - pond[1]));
      else if (side === 2) (x = pond[2] + 5 + r() * 6), (z = pond[1] + u * (pond[3] - pond[1]));
      else (x = pond[0] + u * (pond[2] - pond[0])), (z = pond[1] - 12 - r() * 10);
      if (!blocked(x, z)) palms.push({ x, z, y: gy, s: 0.85 + r() * 0.35 });
    }
  }
  const trees = [];
  const bushes = [];
  for (let i = 0; i < 700; i++) {
    const x = L.island[0] + r() * (L.island[2] - L.island[0]);
    const z = L.island[1] + r() * (L.island[3] - L.island[1]);
    if (!inIsland(x, z) || blocked(x, z)) continue;
    // keep the sunrise view from the south bank of the left pond open
    if (x > -80 && x < 12 && z > 60 && z < 150) continue;
    // lawns: denser near the enclosure walls, sparse in the middle
    const edge = Math.min(x - L.island[0], L.island[2] - x, z - L.island[1], L.island[3] - z);
    if (edge > 30 && r() < 0.75) continue;
    const k = r();
    if (k < 0.18) palms.push({ x, z, y: gy });
    else if (k < 0.62) trees.push({ x, z, y: gy });
    else bushes.push({ x, z, y: gy });
  }
  const bigTrees = [];
  for (let i = 0; i < 1400; i++) {
    const a = r() * Math.PI * 2;
    const dist = 250 + Math.pow(r(), 0.7) * 520;
    const x = Math.cos(a) * dist * 1.1;
    const z = Math.sin(a) * dist;
    if (inMoat(x, z)) continue;
    if (Math.abs(x) < 14 && z > 200) continue;
    bigTrees.push({ x, z, y: gy, s: 0.9 + r() * 0.8 });
    if (r() < 0.12) palms.push({ x: x + 6, z: z + 4, y: gy, s: 1.1 });
  }
  scatter(V, palmGeos, leafMat(), palms, 5);
  scatter(V, treeGeos, vcMat(), trees, 6);
  const far = new THREE.Group();
  scene.add(far);
  scatter(far, bigTreeGeos, vcMat(), bigTrees, 7, false, 120);
  scatter(V, bushGeos, vcMat(), bushes, 8);

  // lotus pads & flowers in the ponds
  const padGeo = new THREE.CircleGeometry(0.55, 12, 0.3, Math.PI * 2 - 0.4);
  padGeo.rotateX(-Math.PI / 2);
  const pads = [];
  for (const pond of [L.pondL, L.pondR])
    for (let i = 0; i < 70; i++) {
      const x = pond[0] + 2 + r() * (pond[2] - pond[0] - 4);
      const z = pond[1] + 2 + r() * (pond[3] - pond[1] - 4);
      if (r() < 0.55 && z < pond[1] + (pond[3] - pond[1]) * 0.5) continue;
      pads.push({ x, z, y: 0.03, s: 0.7 + r() * 0.8 });
    }
  scatter(V, [padGeo], M(0x3f8a3a, { rough: 0.5, side: THREE.DoubleSide }), pads, 9);
  const flowerGeo = merge(
    Array.from({ length: 8 }, (_, i) => {
      const g = new THREE.SphereGeometry(0.16, 8, 6);
      return prep(g, i < 5 ? 0xff9ac0 : 0xffd0e0, mtx([Math.cos(i * 1.3) * 0.12, 0.25 + (i % 3) * 0.05, Math.sin(i * 1.3) * 0.12], [0, 0, 0], [0.6, 1.4, 0.6]));
    })
  );
  scatter(V, [flowerGeo], vcMat(), pads.filter((_, i) => i % 5 === 0).map((p) => ({ ...p, y: 0 })), 10);

  const flock = new Flock(scene, 11, 5, 0x2a2430);
  mirrorHidden.push(far, atmos.clouds);

  scene.traverse((o) => {
    if (o.isMesh && o !== water) {
      if (o.castShadow === undefined) o.castShadow = true;
    }
  });

  return { scene, atmos, water, setMirror, flock, temple: T };
}

function nagaGeo() {
  // Seven-headed naga fan at the end of a balustrade, facing +z
  const parts = [];
  const base = new THREE.CylinderGeometry(0.4, 0.5, 1.4, 10);
  parts.push(prep(base, 0xffffff, mtx([0, 0.7, 0])));
  const neck = new THREE.CylinderGeometry(0.38, 0.45, 2.4, 10);
  parts.push(prep(neck, 0xffffff, mtx([0, 1.9, 0.3], [0.35, 0, 0])));
  // hood plate
  const hood = new THREE.CylinderGeometry(1.9, 1.9, 0.35, 20, 1, false, -Math.PI / 2 - 1.1, 2.2);
  parts.push(prep(hood, 0xffffff, mtx([0, 2.4, 0.2], [Math.PI / 2 - 0.25, 0, 0])));
  for (let i = 0; i < 7; i++) {
    const a = ((i - 3) / 3) * 1.0;
    const x = Math.sin(a) * 1.55;
    const y = 2.4 + Math.cos(a) * 1.55;
    const h = new THREE.SphereGeometry(0.34, 10, 8);
    parts.push(prep(h, 0xffffff, mtx([x, y, 0.55 - Math.abs(i - 3) * 0.05], [0.2, 0, -a * 0.6], [0.85, 1.1, 1.3])));
    const snout = new THREE.SphereGeometry(0.2, 8, 6);
    parts.push(prep(snout, 0xffffff, mtx([x, y + 0.05, 0.9], [0, 0, 0], [0.9, 0.7, 1.2])));
  }
  return merge(parts);
}
