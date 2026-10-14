// Chapter 2 — the first 10,000 years: Earth at night, civilisations flicker.
import { THREE, starField, nebulaSky, sprite, smooth, ease, rng, gauss, pointsMaterial } from '../lib.js';
import { createEarth } from '../earth.js';

export default function century(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, ctx.aspect, 0.01, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, intensity: 0.28, seed: 4 }));
  const stars = starField({ count: 6000, seed: 21, size: ctx.pix });
  scene.add(stars);

  const earth = createEarth(ctx.renderer);
  earth.group.rotation.z = 0.41;
  scene.add(earth.group);
  const sunDir = new THREE.Vector3(1, 0.18, 0.2).normalize();
  earth.uniforms.uSunDir.value.copy(sunDir);
  earth.uniforms.uCity.value = 1;


  // a swarm of satellites = technology
  const r = rng(9);
  const N = 900;
  const pos = new Float32Array(N * 3), col = new Float32Array(N * 3), siz = new Float32Array(N);
  const orb = [];
  for (let i = 0; i < N; i++) {
    const rad = 1.08 + Math.pow(r(), 2) * 0.5;
    const ax = new THREE.Vector3(gauss(r), gauss(r), gauss(r)).normalize();
    const v0 = new THREE.Vector3(gauss(r), gauss(r), gauss(r)).cross(ax).normalize();
    orb.push({ rad, ax, v0, w: 0.25 / Math.pow(rad, 1.5), ph: r() * 6.28 });
    col.set([0.7, 0.85, 1.0], i * 3);
    siz[i] = 0.9 + r();
  }
  const sg = new THREE.BufferGeometry();
  sg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  sg.setAttribute('color', new THREE.BufferAttribute(col, 3));
  sg.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  const sm = pointsMaterial({ sizeScale: 0.012 * ctx.pix });
  const sats = new THREE.Points(sg, sm);
  sats.frustumCulled = false;
  scene.add(sats);
  const tmp = new THREE.Vector3();

  const moon = new THREE.Mesh(new THREE.SphereGeometry(0.27, 48, 24), new THREE.MeshStandardMaterial({ color: 0x9a968f, roughness: 1 }));
  moon.position.set(-9, 2.2, -14);
  scene.add(moon);
  const light = new THREE.DirectionalLight(0xffffff, 2.2);
  light.position.copy(sunDir);
  scene.add(light);
  scene.add(new THREE.AmbientLight(0x223344, 0.15));

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    earth.group.rotation.y = 1.6 + t * 0.035;
    earth.uniforms.uCloudT.value = t * 0.0015;
    // civilisations rise and fall faster and faster as the centuries blur
    const k = smooth(info.cue(2), info.cue(4) + 3, t);
    earth.uniforms.uCityT.value = t * (0.05 + 1.2 * k * k);
    earth.uniforms.uCity.value = 0.6 + 0.4 * smooth(0, 6, t) - 0.25 * smooth(info.cue(5), dur, t);
    // satellites: appear with technology, vanish as nations fall
    const sa = smooth(info.cue(1), info.cue(1) + 3, t) * (1 - smooth(info.cue(3), info.cue(4) + 2, t));
    sm.uniforms.uAlpha.value = sa;
    sats.visible = sa > 0.01;
    if (sats.visible) {
      for (let i = 0; i < N; i++) {
        const o = orb[i];
        tmp.copy(o.v0).applyAxisAngle(o.ax, o.ph + t * o.w).multiplyScalar(o.rad);
        pos[i * 3] = tmp.x; pos[i * 3 + 1] = tmp.y; pos[i * 3 + 2] = tmp.z;
      }
      sg.attributes.position.needsUpdate = true;
    }
    moon.rotation.y = t * 0.02;

    const p = ease(smooth(0, dur, t));
    const ang = -0.15 + p * 0.45;
    const dist = 3.7 - 0.8 * p;
    camera.position.set(Math.sin(ang) * dist, 0.6 - 0.3 * p, Math.cos(ang) * dist);
    camera.lookAt(0.15, 0.05, 0);
  }
  return { scene, camera, update };
}
