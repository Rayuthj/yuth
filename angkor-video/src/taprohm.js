import * as THREE from 'three';
import { stoneMat, groundMat, barkMat, softDotTexture, lotusTowerGeo, roofGeo, mesh, box, rng, prep, merge, mtx, M } from './util.js';
import { Atmos, dirFromAngles, broadTreeGeo, farTreeGeo, bushGeo, leafMat, vcMat, scatter, Flock } from './env.js';

function taperedTube(points, r0, r1, seg = 40, radial = 10) {
  const path = new THREE.CatmullRomCurve3(points, false, 'centripetal');
  const g = new THREE.TubeGeometry(path, seg, 1, radial, false);
  const pos = g.attributes.position;
  const c = new THREE.Vector3();
  const v = new THREE.Vector3();
  for (let i = 0; i <= seg; i++) {
    const u = i / seg;
    path.getPointAt(u, c);
    const rad = THREE.MathUtils.lerp(r0, r1, Math.pow(u, 0.8)) * (1 + 0.12 * Math.sin(u * 23));
    for (let j = 0; j <= radial; j++) {
      const idx = i * (radial + 1) + j;
      v.fromBufferAttribute(pos, idx).sub(c).multiplyScalar(rad).add(c);
      pos.setXYZ(idx, v.x, v.y, v.z);
    }
  }
  g.computeVertexNormals();
  return g;
}

function fernGeo(seed) {
  const r = rng(seed);
  const parts = [];
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2 + r() * 0.3;
    const len = 1.1 + r() * 0.6;
    const g = new THREE.PlaneGeometry(0.35, len, 1, 4);
    const p = g.attributes.position;
    for (let k = 0; k < p.count; k++) {
      const y = p.getY(k) + len / 2;
      p.setX(k, p.getX(k) * (1 - y / len) * 1.2);
      p.setZ(k, -Math.pow(y / len, 2) * 0.6);
      p.setY(k, y);
    }
    g.computeVertexNormals();
    const c = new THREE.Color(0x4f9a3a).offsetHSL(0, 0, (r() - 0.5) * 0.12);
    parts.push(prep(g, c, mtx([0, 0.05, 0], [-0.7, a, 0])));
  }
  return merge(parts);
}

const beamVert = /* glsl */ `
varying vec3 vN; varying vec3 vV; varying float vY;
void main(){
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vN = normalize(mat3(modelMatrix) * normal);
  vV = normalize(cameraPosition - wp.xyz);
  vY = uv.y;
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;
const beamFrag = /* glsl */ `
uniform vec3 color; uniform float strength;
varying vec3 vN; varying vec3 vV; varying float vY;
void main(){
  float edge = pow(abs(dot(normalize(vN), normalize(vV))), 2.5);
  float fade = smoothstep(0.0, 0.05, vY) * (1.0 - smoothstep(0.25, 0.85, vY));
  gl_FragColor = vec4(color * edge * fade * strength, 1.0);
}`;

export function buildTaProhm() {
  const scene = new THREE.Scene();
  const atmos = new Atmos(scene, { seed: 41, clouds: 8 });
  const gy = 0.3;
  const r = rng(401);

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), groundMat({ a: 0x5a6a2a, b: 0x7a8a3a, c: 0x6a5230, scale: 0.12, key: 'forest' }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = gy;
  ground.receiveShadow = true;
  scene.add(ground);

  const stone = stoneMat(0x8f8a7c, { moss: 0.62, ground: gy, mossColor: 0x5a7a3a, bw: 0.9, bh: 0.45 });
  const stoneD = stoneMat(0x7f7a6c, { moss: 0.7, ground: gy, mossColor: 0x4f6f35, flat: true });
  const T = new THREE.Group();
  scene.add(T);
  const add = (m) => (T.add(m), m);

  // ---- ruined gallery running along x, front face at z = +1.6 ----
  const D = 3.2;
  for (const s of [-1, 1]) {
    // walls either side of the gate
    add(box(13, 5.2, D, stone, [s * 10.5, gy + 2.6, 0]));
    // gallery roof (partly collapsed on the left)
    const rf = new THREE.Mesh(roofGeo(s < 0 ? 7 : 13, D + 0.8, 1.8, 2), stoneD);
    rf.position.set(s < 0 ? -7.5 : 10.5, gy + 5.2, 0);
    rf.castShadow = rf.receiveShadow = true;
    add(rf);
    // window with balusters
    for (let i = 0; i < 5; i++) add(mesh(new THREE.CylinderGeometry(0.12, 0.12, 1.4, 8), stoneD, [s * 9 + i * 0.35 - 0.7, gy + 3.0, D / 2 + 0.05]));
  }
  // cut the window openings by placing dark recesses behind balusters
  for (const s of [-1, 1]) add(box(2.0, 1.5, 0.2, M(0x1a1812), [s * 9, gy + 3.0, D / 2 - 0.05]));

  // gate (gopura) with doorway
  const gx = 0;
  add(box(2.4, 6.5, D + 1.2, stone, [gx - 2.4, gy + 3.25, 0]));
  add(box(2.4, 6.5, D + 1.2, stone, [gx + 2.4, gy + 3.25, 0]));
  add(box(7.2, 2.4, D + 1.2, stone, [gx, gy + 5.3, 0]));
  add(box(7.8, 0.45, D + 1.8, stoneD, [gx, gy + 6.7, 0]));
  add(box(6.2, 1.8, D + 0.6, stone, [gx, gy + 7.8, 0]));
  add(box(1.6, 3.9, 0.35, stoneD, [gx, gy + 5.3, D / 2 + 0.62]));
  // lintel carving
  add(box(2.6, 0.7, 0.3, stoneD, [gx, gy + 4.35, D / 2 + 0.66]));
  // dark passage inside the doorway
  add(box(2.2, 4.0, 0.2, M(0x151410, { rough: 1 }), [gx, gy + 2.0, -D / 2 - 0.3]));
  // truncated tower, broken
  add(mesh(lotusTowerGeo(7, 2.6, { trunc: 0.45, tiers: 7 }), stoneD, [gx, gy + 8.7, 0]));
  // fallen blocks
  const blocks = [];
  for (let i = 0; i < 70; i++) {
    const x = (r() - 0.5) * 34;
    const z = 2.5 + r() * 9 * (r() < 0.5 ? 1 : -1.4);
    if (Math.abs(x) < 3 && z > 0 && z < 14) continue;
    const b = box(0.7 + r() * 1.0, 0.35 + r() * 0.5, 0.5 + r() * 0.7, stone, [x, gy + 0.2 + r() * 0.2, z], [r() * 0.3, r() * 3, r() * 0.3]);
    blocks.push(b);
    add(b);
  }
  // a big stone for climbing
  add(box(1.8, 0.9, 1.4, stone, [-3.8, gy + 0.45, 5.2], [0.05, 0.4, 0.02]));

  // ---- the giant tree (Tetrameles) on the gate ----
  const trunkBase = new THREE.Vector3(1.6, gy + 9.2, -0.6);
  const tg = new THREE.CylinderGeometry(1.0, 1.9, 34, 16, 24, true);
  tg.translate(0, 17, 0);
  const tp = tg.attributes.position;
  for (let i = 0; i < tp.count; i++) {
    const x = tp.getX(i);
    const y = tp.getY(i);
    const z = tp.getZ(i);
    const a = Math.atan2(z, x);
    const k = 1 + 0.07 * Math.sin(a * 7 + y * 0.05) + 0.1 * Math.exp(-y * 0.25) * Math.sin(a * 5);
    tp.setXYZ(i, x * k + Math.sin(y * 0.07) * 0.8, y, z * k);
  }
  tg.computeVertexNormals();
  const barkM = barkMat(0xb4a68e);
  const trunk = mesh(tg, barkM, [trunkBase.x, trunkBase.y - 1.0, trunkBase.z]);
  add(trunk);
  // roots cascading over the gate and walls
  const rootParts = [];
  for (let i = 0; i < 22; i++) {
    const a = (i / 22) * Math.PI * 2 + r() * 0.2;
    const front = Math.cos(a) > -0.2;
    const side = Math.sin(a);
    const zs = front ? 1 : -1;
    const x0 = trunkBase.x + Math.sin(a) * 1.5;
    const x1 = trunkBase.x + side * (2.5 + r() * 3.5);
    const x2 = x1 + side * (0.5 + r() * 2.0);
    const pts = [
      new THREE.Vector3(x0, trunkBase.y + 0.6, trunkBase.z + Math.cos(a) * 1.2),
      new THREE.Vector3(x1 * 0.8 + x0 * 0.2, gy + 8.6 + r() * 0.6, zs * (D / 2 + 0.6)),
      new THREE.Vector3(x1, gy + 6.9, zs * (D / 2 + 1.25)),
      new THREE.Vector3(x2, gy + 3.6 + r(), zs * (D / 2 + 0.9 + r() * 0.4)),
      new THREE.Vector3(x2 + side * r(), gy + 0.5, zs * (D / 2 + 1.4 + r())),
      new THREE.Vector3(x2 + side * (1 + r() * 3), gy + 0.2, zs * (D / 2 + 3.5 + r() * 4)),
    ];
    // keep the doorway clear: push roots that would cross it sideways
    for (const p of pts.slice(3)) if (Math.abs(p.x - gx) < 1.6 && zs > 0) p.x = gx + Math.sign(p.x - gx || 1) * (1.8 + r() * 0.5);
    rootParts.push(prep(taperedTube(pts, 0.55 + r() * 0.3, 0.1, 48, 9), 0xffffff));
  }
  // roots draped over the lintel framing the doorway
  for (const s of [-1, 1]) {
    const pts = [
      new THREE.Vector3(trunkBase.x, trunkBase.y + 0.3, trunkBase.z + 1),
      new THREE.Vector3(gx + s * 1.2, gy + 8.4, D / 2 + 0.9),
      new THREE.Vector3(gx + s * 1.5, gy + 6.2, D / 2 + 1.1),
      new THREE.Vector3(gx + s * 1.5, gy + 4.4, D / 2 + 1.0),
      new THREE.Vector3(gx + s * 1.75, gy + 1.5, D / 2 + 0.95),
      new THREE.Vector3(gx + s * 2.6, gy + 0.2, D / 2 + 2.4),
    ];
    rootParts.push(prep(taperedTube(pts, 0.7, 0.18, 56, 10), 0xffffff));
  }
  const roots = new THREE.Mesh(merge(rootParts), barkM);
  roots.castShadow = roots.receiveShadow = true;
  add(roots);
  // canopy of the big tree
  const can = [];
  for (let i = 0; i < 16; i++) {
    const a = r() * Math.PI * 2;
    const dd = 3 + r() * 10;
    can.push(prep(new THREE.IcosahedronGeometry(4 + r() * 3, 1), new THREE.Color(0x3a7a30).offsetHSL(0, 0, (r() - 0.5) * 0.1), mtx([trunkBase.x + Math.cos(a) * dd, 40 + r() * 6, trunkBase.z + Math.sin(a) * dd])));
  }
  const canopy = new THREE.Mesh(merge(can), vcMat());
  canopy.castShadow = true;
  add(canopy);

  // ---- surrounding jungle ----
  const V = new THREE.Group();
  scene.add(V);
  const tall = [];
  const bushes = [];
  const ferns = [];
  for (let i = 0; i < 380; i++) {
    const x = (r() - 0.5) * 220;
    const z = (r() - 0.5) * 220 - 20;
    if (Math.abs(z) < 4 && Math.abs(x) < 20) continue;
    if (z > 0 && z < 22 && Math.abs(x) < 9) continue;
    const k = r();
    if (k < 0.33) tall.push({ x, z, y: gy, s: 1 + r() * 0.5 });
    else if (k < 0.62) bushes.push({ x, z, y: gy });
    else ferns.push({ x, z, y: gy, s: 0.8 + r() * 0.8 });
  }
  for (let i = 0; i < 90; i++) {
    const x = (r() - 0.5) * 40;
    const z = 2 + r() * 14;
    if (Math.abs(x) < 3.5) continue;
    ferns.push({ x, z, y: gy, s: 0.7 + r() * 0.6 });
  }
  const tallGeo = (seed, leaf) => broadTreeGeo(seed, { h: 22, hv: 10, blob: 4, spread: 6, leaf, trunk: 0xb8ae9a });
  scatter(V, [tallGeo(51, 0x3a7a32), tallGeo(52, 0x2f6a2c), tallGeo(53, 0x4a8a38)], vcMat(), tall, 54, true, 50);
  scatter(V, [bushGeo(55, 0x3f7a2f), bushGeo(56, 0x4f8a35)], vcMat(), bushes, 57, true, 50);
  scatter(V, [fernGeo(58), fernGeo(59)], leafMat(), ferns, 60, false, 40);
  const far = [];
  for (let i = 0; i < 300; i++) {
    const a = r() * Math.PI * 2;
    const dd = 120 + r() * 200;
    far.push({ x: Math.cos(a) * dd, z: Math.sin(a) * dd, y: gy, s: 1.6 + r() * 0.6 });
  }
  scatter(V, [farTreeGeo(61, 0x2f6a2c), farTreeGeo(62, 0x3a7a32)], vcMat(), far, 63, false, 150);

  // ---- light shafts ----
  const beamMat = new THREE.ShaderMaterial({
    uniforms: { color: { value: new THREE.Color(0xfff2c0) }, strength: { value: 0.2 } },
    vertexShader: beamVert,
    fragmentShader: beamFrag,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
    fog: false,
  });
  const beams = new THREE.Group();
  const beamSpots = [
    [-6, 8, 1.3], [3.8, 10, 1.0], [8, 6, 1.6], [-11, 4, 1.2], [0.8, 15, 0.9], [-3.2, 12.5, 0.8], [6.5, 14, 1.1],
  ];
  const beamDir = dirFromAngles(30, 58);
  const beamQ = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), beamDir);
  for (const [x, z, rr] of beamSpots) {
    const bg = new THREE.CylinderGeometry(rr * 1.5, rr, 40, 16, 1, true);
    bg.translate(0, 20, 0);
    const b = new THREE.Mesh(bg, beamMat);
    b.position.set(x, gy, z);
    b.quaternion.copy(beamQ);
    b.renderOrder = 5;
    beams.add(b);
  }
  scene.add(beams);

  // ---- dust motes ----
  const dp = [];
  for (let i = 0; i < 400; i++) dp.push((r() - 0.5) * 26, gy + r() * 9, 1 + r() * 16);
  const dg = new THREE.BufferGeometry();
  dg.setAttribute('position', new THREE.Float32BufferAttribute(dp, 3));
  const dust = new THREE.Points(dg, new THREE.PointsMaterial({ color: 0xfff0c0, map: softDotTexture(), size: 0.07, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(dust);
  const dustBase = dp.slice();

  // ---- butterflies ----
  const flies = [];
  const colors = [0x3aa0ff, 0xffd23a, 0xff7a3a, 0x7a5aff, 0x3aa0ff, 0xffd23a];
  for (let i = 0; i < 6; i++) {
    const g = new THREE.Group();
    const wm = new THREE.MeshStandardMaterial({ color: colors[i], side: THREE.DoubleSide, roughness: 0.5, emissive: colors[i], emissiveIntensity: 0.25 });
    const wg = new THREE.CircleGeometry(0.16, 10);
    wg.translate(0.15, 0.02, 0);
    const wl = new THREE.Mesh(wg, wm);
    const wr = new THREE.Mesh(wg, wm);
    wl.rotation.x = wr.rotation.x = -Math.PI / 2;
    const pl = new THREE.Group();
    const pr = new THREE.Group();
    pl.add(wl);
    pr.add(wr);
    pr.scale.x = -1;
    g.add(pl, pr);
    g.add(new THREE.Mesh(new THREE.CapsuleGeometry(0.025, 0.14, 3, 6), M(0x222222)).rotateX(Math.PI / 2));
    g.userData = { pl, pr, c: new THREE.Vector3((r() - 0.5) * 12, gy + 1.5 + r() * 3, 3 + r() * 10), ph: r() * 6 };
    scene.add(g);
    flies.push(g);
  }

  const flock = new Flock(scene, 6, 21, 0x2a2a30);
  const tick = (t) => {
    const pa = dust.geometry.attributes.position;
    for (let i = 0; i < pa.count; i++) {
      pa.setX(i, dustBase[i * 3] + Math.sin(t * 0.3 + i) * 0.4);
      pa.setY(i, dustBase[i * 3 + 1] + ((t * 0.15 + i * 0.37) % 1.5) - 0.75);
      pa.setZ(i, dustBase[i * 3 + 2] + Math.cos(t * 0.25 + i * 1.3) * 0.4);
    }
    pa.needsUpdate = true;
    for (const f of flies) {
      const { c, ph, pl, pr } = f.userData;
      const p = new THREE.Vector3(c.x + Math.sin(t * 0.7 + ph) * 3, c.y + Math.sin(t * 1.3 + ph * 2) * 0.8, c.z + Math.sin(t * 0.5 + ph * 3) * 2.5);
      const q = new THREE.Vector3(c.x + Math.sin((t + 0.05) * 0.7 + ph) * 3, c.y + Math.sin((t + 0.05) * 1.3 + ph * 2) * 0.8, c.z + Math.sin((t + 0.05) * 0.5 + ph * 3) * 2.5);
      f.position.copy(p);
      f.lookAt(q);
      const flap = Math.sin(t * 22 + ph) * 1.1;
      pl.rotation.z = flap;
      pr.rotation.z = -flap;
    }
  };
  return { scene, atmos, flock, tick, beams, beamMat, gateFront: D / 2, trunkBase };
}
