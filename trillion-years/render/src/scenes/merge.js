// Chapter 11 — the last island: the Local Group's galaxies fall together,
// blue stars burn out, star-forming gas runs dry and the light reddens.
import { THREE, sprite, smooth, ease, rng, gauss, pointsMaterial } from '../lib.js';
import { makeGalaxy } from '../galaxyfx.js';

export default function merge(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(48, ctx.aspect, 0.05, 5000);

  const main = makeGalaxy({ count: 90000, radius: 7, seed: 15, pix: ctx.pix, elliptical: 0.35, knots: 500, arms: 2, armTight: 0.6 });
  main.points.rotation.x = 0.25;
  scene.add(main.points);
  const core = sprite(0xffd8a8, 9, 'soft', 0.45);
  scene.add(core);

  const r = rng(404);
  const ND = 8, PER = 2600;
  const dwarfs = [];
  const pos = new Float32Array(ND * PER * 3), col = new Float32Array(ND * PER * 3), siz = new Float32Array(ND * PER);
  const off = new Float32Array(ND * PER * 3);
  for (let d = 0; d < ND; d++) {
    const r0 = 16 + r() * 10, th0 = r() * Math.PI * 2, inc = (r() - 0.5) * 1.2;
    const t0 = 2 + d * 2.6 + r() * 2, t1 = t0 + 12 + r() * 6;
    dwarfs.push({ r0, th0, inc, t0, t1, spin: 2.5 + r() * 2.5, sigma: 0.45 + r() * 0.5 });
    for (let i = 0; i < PER; i++) {
      const k = (d * PER + i) * 3;
      off.set([gauss(r), gauss(r) * 0.7, gauss(r)], k);
      const c = r() < 0.6 ? [0.65, 0.78, 1.0] : [1.0, 0.85, 0.65];
      col.set(c, k);
      siz[d * PER + i] = 0.6 + Math.pow(r(), 3) * 1.8;
    }
  }
  const dg = new THREE.BufferGeometry();
  dg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  dg.setAttribute('color', new THREE.BufferAttribute(col, 3));
  dg.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  const dm = pointsMaterial({ sizeScale: 0.06 * ctx.pix });
  const dpts = new THREE.Points(dg, dm);
  dpts.frustumCulled = false;
  scene.add(dpts);
  const dglow = dwarfs.map(() => { const s = sprite(0xcfe0ff, 2.4, 'soft', 0.4); scene.add(s); return s; });

  const tint = new THREE.Vector3();
  function update(t, dur) {
    const age = smooth(info.cue(2) - 2, info.cue(4) + 4, t);
    main.uniforms.uAge.value = age;
    main.uniforms.uRot.value = -t * 0.06;
    main.uniforms.uKnots.value = 1 - smooth(info.cue(4), info.cue(4) + 5, t);
    core.material.color.setRGB(1, 0.85 - 0.3 * age, 0.66 - 0.4 * age);
    tint.set(1, 1 - 0.45 * age, 1 - 0.7 * age);
    dm.uniforms.uTint.value.copy(tint);

    dwarfs.forEach((d, i) => {
      const k = smooth(d.t0, d.t1, t);
      const rad = d.r0 * (1 - ease(k)) + 0.5;
      const th = d.th0 + k * d.spin * Math.PI + t * 0.03;
      const cx = Math.cos(th) * rad, cz = Math.sin(th) * rad, cy = Math.sin(d.inc) * rad * 0.4;
      const spread = d.sigma * (1 + 6 * k * k);
      for (let j = 0; j < PER; j++) {
        const q = (i * PER + j) * 3;
        // tidal stretching along the orbit as the dwarf is shredded
        const ox = off[q] * spread, oy = off[q + 1] * spread * (1 - 0.5 * k), oz = off[q + 2] * spread;
        const a = th + (ox / Math.max(rad, 1.5)) * k * 2.5;
        const rr = rad + oz * (1 - 0.3 * k);
        pos[q] = Math.cos(a) * rr + ox * (1 - k);
        pos[q + 1] = cy * (1 - k) + oy;
        pos[q + 2] = Math.sin(a) * rr;
      }
      dglow[i].position.set(cx, cy * (1 - k), cz);
      dglow[i].material.opacity = 0.4 * (1 - k);
    });
    dg.attributes.position.needsUpdate = true;
    dm.uniforms.uAlpha.value = 1 - 0.5 * smooth(info.cue(3), dur, t);
    main.uniforms.uAlpha.value = 1 - 0.35 * smooth(info.cue(4), dur + 1, t);

    const p = smooth(0, dur, t);
    const ang = 1.0 + p * 0.8;
    const dist = 34 - 10 * ease(p);
    camera.position.set(Math.sin(ang) * dist, dist * 0.42, Math.cos(ang) * dist);
    camera.lookAt(0, 0, 0);
  }
  return { scene, camera, update };
}
