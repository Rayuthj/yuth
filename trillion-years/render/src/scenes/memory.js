// Chapter 3 — the problem of memory: a glowing neural network where memories
// light up and are overwritten, while named memories dissolve.
import { THREE, nebulaSky, starField, textSprite, humanFigure, smooth, ease, rng, gauss, pointsMaterial, sprite, mod } from '../lib.js';

export default function memory(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, ctx.aspect, 0.05, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, colA: [0.25, 0.08, 0.25], colB: [0.08, 0.1, 0.3], intensity: 0.32, seed: 14 }));
  const stars = starField({ count: 3500, seed: 41, size: ctx.pix * 0.8 });
  scene.add(stars);

  const r = rng(77);
  // nodes inside two hemispheres, biased to the outer "cortex"
  const nodes = [];
  while (nodes.length < 950) {
    const p = new THREE.Vector3(r() * 2 - 1, r() * 2 - 1, r() * 2 - 1);
    const side = p.x > 0 ? 1 : -1;
    const q = new THREE.Vector3((p.x - side * 0.5) / 0.55, p.y / 0.78, p.z / 1.0);
    const l = q.length();
    if (l > 1 || l < 0.55 || Math.abs(p.x) < 0.06) continue;
    if (p.y < -0.55 && Math.abs(p.z) > 0.6) continue;
    nodes.push({ p: p.multiplyScalar(1.25), phase: (p.x * 0.35 + p.y * 0.25 + p.z * 0.15 + r() * 0.35 + 10) % 1, rate: 0.85 + r() * 0.3, b: 0, s: 0 });
  }
  const NN = nodes.length;
  // connect to nearest neighbours
  const edges = [];
  for (let i = 0; i < NN; i++) {
    const ds = [];
    for (let j = 0; j < NN; j++) if (j !== i) ds.push([nodes[i].p.distanceToSquared(nodes[j].p), j]);
    ds.sort((a, b) => a[0] - b[0]);
    for (let k = 0; k < 2; k++) { const j = ds[k][1]; if (i < j) edges.push([i, j]); }
    if (r() < 0.15) { const j = ds[3 + Math.floor(r() * 6)][1]; if (i < j) edges.push([i, j]); }
  }
  const NE = edges.length;

  const np = new Float32Array(NN * 3), nc = new Float32Array(NN * 3), ns = new Float32Array(NN);
  nodes.forEach((n, i) => { np.set([n.p.x, n.p.y, n.p.z], i * 3); n.s = 1.6 + r() * 2.2; ns[i] = n.s; });
  const ng = new THREE.BufferGeometry();
  ng.setAttribute('position', new THREE.BufferAttribute(np, 3));
  ng.setAttribute('color', new THREE.BufferAttribute(nc, 3));
  ng.setAttribute('size', new THREE.BufferAttribute(ns, 1));
  const nodePts = new THREE.Points(ng, pointsMaterial({ sizeScale: 0.045 * ctx.pix }));
  nodePts.frustumCulled = false;

  const ep = new Float32Array(NE * 6), ec = new Float32Array(NE * 6);
  edges.forEach(([a, b], k) => { ep.set([...nodes[a].p.toArray(), ...nodes[b].p.toArray()], k * 6); });
  const eg = new THREE.BufferGeometry();
  eg.setAttribute('position', new THREE.BufferAttribute(ep, 3));
  eg.setAttribute('color', new THREE.BufferAttribute(ec, 3));
  const lines = new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  lines.frustumCulled = false;

  // signals travelling along edges
  const NS = 420;
  const sigs = Array.from({ length: NS }, () => ({ e: Math.floor(r() * NE), ph: r(), sp: 0.5 + r() }));
  const sp = new Float32Array(NS * 3), sc = new Float32Array(NS * 3), ss = new Float32Array(NS);
  for (let i = 0; i < NS; i++) { sc.set([1.0, 0.85, 0.55], i * 3); ss[i] = 2.2; }
  const sgeo = new THREE.BufferGeometry();
  sgeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  sgeo.setAttribute('color', new THREE.BufferAttribute(sc, 3));
  sgeo.setAttribute('size', new THREE.BufferAttribute(ss, 1));
  const sigPts = new THREE.Points(sgeo, pointsMaterial({ sizeScale: 0.025 * ctx.pix }));
  sigPts.frustumCulled = false;

  const brain = new THREE.Group();
  brain.add(lines, nodePts, sigPts);
  const glow = sprite(0x6a5cff, 5, 'soft', 0.25);
  brain.add(glow);
  scene.add(brain);

  // named memories that dissolve
  const words = [
    ['your first steps', -1.5, 1.0, 0.6],
    ['a summer evening', 1.5, 1.2, 0.6],
    ['your childhood home', -1.6, -0.5, 0.8],
    ['your first friend', 1.6, -0.5, 0.8],
    ['the face of your mother', 0.0, 1.55, 0.9],
  ].map(([w, x, y, z]) => {
    const s = textSprite([w], { size: 0.3, color: '#ffe3b0' });
    s.position.set(x, y, z);
    s.userData = { base: s.scale.clone(), y };
    scene.add(s);
    return s;
  });
  // timings: first two drift by early, the last three follow the narration
  const wt = [info.cue(1) + 0.3, info.cue(2) + 0.2, info.cue(3) - 0.2, info.cue(3) + 1.6, info.cue(3) + 3.0];

  const you = humanFigure({ count: 6000, seed: 9, color: [1.0, 0.75, 0.45] });
  you.material.uniforms.uPix.value = ctx.pix;
  you.position.set(2.6, -0.2, 0.6);
  you.scale.setScalar(1.1);
  scene.add(you);

  const tmp = new THREE.Vector3();
  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    // memories get overwritten faster as time goes on
    const speed = 0.16 + 0.45 * smooth(info.cue(2), info.cue(4), t);
    const fade = 1 - 0.55 * smooth(info.cue(3), dur, t);
    for (let i = 0; i < NN; i++) {
      const n = nodes[i];
      const age = mod(t * speed * n.rate + n.phase, 1);
      const flash = Math.exp(-age * 7) * fade;
      const base = 0.22 + 0.15 * (1 - age);
      nc[i * 3] = base * 0.45 + flash * 1.3;
      nc[i * 3 + 1] = base * 0.6 + flash * 0.95;
      nc[i * 3 + 2] = base * 1.0 + flash * 0.45;
      ns[i] = n.s * (1 + 1.8 * flash);
      n.b = flash;
    }
    ng.attributes.color.needsUpdate = true;
    ng.attributes.size.needsUpdate = true;
    for (let k = 0; k < NE; k++) {
      const [a, b] = edges[k];
      const f = (nodes[a].b + nodes[b].b) * 0.5;
      for (let v = 0; v < 2; v++) {
        ec[k * 6 + v * 3] = 0.04 + f * 0.9;
        ec[k * 6 + v * 3 + 1] = 0.06 + f * 0.65;
        ec[k * 6 + v * 3 + 2] = 0.16 + f * 0.25;
      }
    }
    eg.attributes.color.needsUpdate = true;
    for (let i = 0; i < NS; i++) {
      const s = sigs[i];
      const u = mod(s.ph + t * s.sp * 0.6, 1);
      const cyc = Math.floor(s.ph + t * s.sp * 0.6);
      const e = edges[mod(s.e + cyc * 131, NE)];
      tmp.copy(nodes[e[0]].p).lerp(nodes[e[1]].p, u);
      sp[i * 3] = tmp.x; sp[i * 3 + 1] = tmp.y; sp[i * 3 + 2] = tmp.z;
    }
    sgeo.attributes.position.needsUpdate = true;
    brain.rotation.y = t * 0.08;

    words.forEach((w, i) => {
      const t0 = wt[i];
      const a = smooth(t0, t0 + 0.8, t) * (1 - smooth(t0 + 2.6, t0 + 4.6, t));
      w.material.opacity = a;
      w.visible = a > 0.001;
      const k = smooth(t0 + 2.6, t0 + 4.6, t);
      w.scale.copy(w.userData.base).multiplyScalar(1 + k * 0.5);
      w.position.y = w.userData.y + k * 0.35;
    });

    // "the person you were at twenty" fades in, then scatters into dust
    const ya = smooth(info.cue(4) - 0.5, info.cue(4) + 1.5, t);
    const ys = smooth(info.cue(4) + 2.5, info.cue(5) + 3, t);
    you.visible = ya > 0.001;
    you.material.uniforms.uTime.value = t;
    you.material.uniforms.uAlpha.value = ya * (1 - ys * 0.85);
    you.material.uniforms.uScatter.value = ys * ys * 2.5;

    const p = ease(smooth(0, dur, t));
    const ang = -0.5 + p * 0.7;
    const dist = 5.6 - 1.2 * p + 1.2 * smooth(info.cue(4) - 1, info.cue(4) + 3, t);
    camera.position.set(Math.sin(ang) * dist + 0.6 * smooth(info.cue(4) - 1, info.cue(4) + 3, t), 0.9 - 0.5 * p, Math.cos(ang) * dist);
    camera.lookAt(0.5 * smooth(info.cue(4) - 1, info.cue(4) + 3, t), 0, 0);
  }
  return { scene, camera, update };
}
