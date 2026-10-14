// Chapter 8 — collision of galaxies: a restricted N-body simulation. Two
// galaxy cores fall together (softened gravity + dynamical friction) and the
// star particles respond, throwing out tidal tails before merging.
import { THREE, starField, sprite, smooth, ease, rng, gauss } from '../lib.js';

const M1 = 1.0, M2 = 1.2, EPS_C = 0.6, DRAG = 0.6, EPS_P = 0.45;
const SIM_RATE = 1.27;          // sim time units per second of video
const DTC = 0.002;              // core step
const DTP = 0.02;               // particle step

export default function andromeda(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(48, ctx.aspect, 0.05, 5000);
  const stars = starField({ count: 6000, seed: 91, size: ctx.pix });
  scene.add(stars);

  const r = rng(2024);
  const N1 = 26000, N2 = 30000, N = N1 + N2;
  const pos = new Float32Array(N * 3), vel = new Float32Array(N * 3);
  const col = new Float32Array(N * 3), siz = new Float32Array(N);
  const init = { pos: null, vel: null };

  // initial cores
  const D0 = 10, VT = 0.35, VR = 0.3;
  const c0 = {
    p1: [-M2 / (M1 + M2) * D0, 0, 0], p2: [M1 / (M1 + M2) * D0, 0, 0],
    v1: [VR * M2 / (M1 + M2), 0, -VT * M2 / (M1 + M2)], v2: [-VR * M1 / (M1 + M2), 0, VT * M1 / (M1 + M2)],
  };

  function addDisk(start, n, R, center, v, M, tiltX, tiltZ, palette) {
    const m = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(tiltX, 0, tiltZ));
    const p = new THREE.Vector3(), q = new THREE.Vector3();
    for (let i = start; i < start + n; i++) {
      const bulge = r() < 0.16;
      let rad, th, y;
      if (bulge) { rad = Math.abs(gauss(r)) * R * 0.12 + 0.05; th = r() * Math.PI * 2; y = gauss(r) * R * 0.05; }
      else {
        rad = R * (0.08 + Math.pow(r(), 0.85) * 0.92);
        const arm = Math.floor(r() * 2);
        th = arm * Math.PI + Math.log(rad / (R * 0.1)) / Math.tan(0.3) + gauss(r) * 0.35;
        y = gauss(r) * 0.04;
      }
      p.set(Math.cos(th) * rad, y, Math.sin(th) * rad);
      const vc = Math.sqrt(M * rad * rad / Math.pow(rad * rad + EPS_P * EPS_P, 1.5));
      q.set(-Math.sin(th) * vc, 0, Math.cos(th) * vc);
      p.applyMatrix4(m); q.applyMatrix4(m);
      pos.set([p.x + center[0], p.y + center[1], p.z + center[2]], i * 3);
      vel.set([q.x + v[0], q.y + v[1], q.z + v[2]], i * 3);
      const c = bulge ? palette[1] : palette[0];
      const k = 0.75 + 0.25 * r();
      col.set([c[0] * k, c[1] * k, c[2] * k], i * 3);
      siz[i] = (bulge ? 1.2 : 0.8) + Math.pow(r(), 3) * 2.0;
    }
  }
  addDisk(0, N1, 3.0, c0.p1, c0.v1, M1, 0.25, 0.15, [[0.6, 0.75, 1.0], [1.0, 0.85, 0.6]]);
  addDisk(N1, N2, 3.6, c0.p2, c0.v2, M2, 1.05, -0.5, [[1.0, 0.85, 0.7], [1.0, 0.75, 0.5]]);
  init.pos = pos.slice(); init.vel = vel.slice();

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: { uSize: { value: 0.055 * ctx.pix } },
    vertexShader: /* glsl */`
      attribute float size; attribute vec3 color; uniform float uSize; varying vec3 vC;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); gl_Position = projectionMatrix*mv;
        gl_PointSize = max(1.0, size*uSize*(300.0 / -mv.z)); vC = color; }`,
    fragmentShader: /* glsl */`
      varying vec3 vC; void main(){ float r = length(gl_PointCoord-0.5)*2.0; float a = smoothstep(1.0,0.0,r); a*=a;
        gl_FragColor = vec4(vC*a*0.85, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  scene.add(pts);
  const g1 = sprite(0xbcd4ff, 3.0, 'soft', 0.55), g2 = sprite(0xffd9b0, 3.6, 'soft', 0.55);
  const k1 = sprite(0xffffff, 0.8, 'core', 0.9), k2 = sprite(0xffffff, 0.9, 'core', 0.9);
  scene.add(g1, g2, k1, k2);

  // ---- simulation state ----
  let simT = 0;
  const cs = { p1: [], p2: [], v1: [], v2: [] };
  function reset() {
    simT = 0;
    pos.set(init.pos); vel.set(init.vel);
    for (const k of ['p1', 'p2', 'v1', 'v2']) cs[k] = c0[k].slice();
  }
  reset();
  function stepCores(dt) {
    const d = [cs.p2[0] - cs.p1[0], cs.p2[1] - cs.p1[1], cs.p2[2] - cs.p1[2]];
    const r2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
    const f = 1 / Math.pow(r2 + EPS_C * EPS_C, 1.5);
    const drag = DRAG * Math.exp(-r2 / 4.0);
    for (let a = 0; a < 3; a++) {
      const vrel = cs.v2[a] - cs.v1[a];
      cs.v1[a] += (M2 * f * d[a] + drag * vrel * M2 / (M1 + M2)) * dt;
      cs.v2[a] += (-M1 * f * d[a] - drag * vrel * M1 / (M1 + M2)) * dt;
    }
    for (let a = 0; a < 3; a++) { cs.p1[a] += cs.v1[a] * dt; cs.p2[a] += cs.v2[a] * dt; }
  }
  function stepParticles(dt) {
    const e2 = EPS_P * EPS_P;
    const [ax1, ay1, az1] = cs.p1, [ax2, ay2, az2] = cs.p2;
    for (let i = 0; i < N; i++) {
      const j = i * 3;
      const x = pos[j], y = pos[j + 1], z = pos[j + 2];
      let dx = ax1 - x, dy = ay1 - y, dz = az1 - z;
      let f = M1 / Math.pow(dx * dx + dy * dy + dz * dz + e2, 1.5);
      let fx = dx * f, fy = dy * f, fz = dz * f;
      dx = ax2 - x; dy = ay2 - y; dz = az2 - z;
      f = M2 / Math.pow(dx * dx + dy * dy + dz * dz + e2, 1.5);
      fx += dx * f; fy += dy * f; fz += dz * f;
      vel[j] += fx * dt; vel[j + 1] += fy * dt; vel[j + 2] += fz * dt;
      pos[j] += vel[j] * dt; pos[j + 1] += vel[j + 1] * dt; pos[j + 2] += vel[j + 2] * dt;
    }
  }
  function advanceTo(target) {
    if (target < simT - 1e-9) reset();
    while (simT + DTP <= target) {
      for (let k = 0; k < DTP / DTC; k++) stepCores(DTC);
      stepParticles(DTP);
      simT += DTP;
    }
  }

  const com = new THREE.Vector3();
  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    const tt = Math.min(Math.max(t, 0), dur + 1);
    advanceTo(tt * SIM_RATE);
    geo.attributes.position.needsUpdate = true;
    g1.position.fromArray(cs.p1); k1.position.fromArray(cs.p1);
    g2.position.fromArray(cs.p2); k2.position.fromArray(cs.p2);
    const merged = smooth(info.cue(4) - 2, info.cue(4) + 4, t);
    g2.scale.setScalar(3.6 + 4 * merged);
    g2.material.opacity = 0.55 + 0.2 * merged;
    com.set(0, 0, 0).addScaledVector(g1.position, M1 / (M1 + M2)).addScaledVector(g2.position, M2 / (M1 + M2));

    // camera: wide oblique view that slowly orbits and tightens
    const p = smooth(0, dur, t);
    const ang = 0.6 + p * 0.9;
    const dist = 15.5 - 3.5 * ease(p);
    camera.position.set(com.x + Math.sin(ang) * dist, com.y + 8.5 - 2 * p, com.z + Math.cos(ang) * dist);
    camera.lookAt(com);
  }
  return { scene, camera, update };
}
