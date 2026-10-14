// Chapter 12 — one trillion years: a cold, red, quiet universe. You, a dim
// white dwarf that was once the Sun, and a galaxy of red dwarfs.
import { THREE, nebulaSky, sprite, humanFigure, pulseRing, heartbeat, smooth, ease, rng, gauss, pointsMaterial } from '../lib.js';
import { makeGalaxy } from '../galaxyfx.js';

export default function trillion(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, ctx.aspect, 0.05, 6000);
  // the last afterglow of the Big Bang
  const cmb = nebulaSky({ renderer: ctx.renderer, colA: [0.45, 0.12, 0.05], colB: [0.25, 0.05, 0.12], intensity: 0.5, seed: 31, band: 0, radius: 3000 });
  scene.add(cmb);

  const gal = makeGalaxy({ count: 80000, radius: 14, seed: 44, pix: ctx.pix, elliptical: 0.7, knots: 0, arms: 2 });
  gal.uniforms.uAge.value = 1;
  gal.points.position.set(-6, -4, -70);
  gal.points.rotation.x = 0.6;
  scene.add(gal.points);
  const galCore = sprite(0xff7a40, 26, 'soft', 0.35);
  galCore.position.copy(gal.points.position);
  scene.add(galCore);

  // red dwarfs scattered nearby
  const r = rng(808);
  const NR = 500;
  const rp = new Float32Array(NR * 3), rc = new Float32Array(NR * 3), rs = new Float32Array(NR), ph = [];
  for (let i = 0; i < NR; i++) {
    rp.set([gauss(r) * 30, gauss(r) * 14, -10 - r() * 60], i * 3);
    rc.set([1.0, 0.32 + 0.15 * r(), 0.12], i * 3);
    rs[i] = 1 + r() * 3; ph.push(r() * 6.28);
  }
  const rg = new THREE.BufferGeometry();
  rg.setAttribute('position', new THREE.BufferAttribute(rp, 3));
  rg.setAttribute('color', new THREE.BufferAttribute(rc, 3));
  rg.setAttribute('size', new THREE.BufferAttribute(rs, 1));
  const rm = pointsMaterial({ sizeScale: 0.12 * ctx.pix });
  const reds = new THREE.Points(rg, rm);
  reds.frustumCulled = false;
  scene.add(reds);

  // the Sun's cold remnant
  const wd = new THREE.Mesh(new THREE.SphereGeometry(0.22, 48, 24), new THREE.MeshBasicMaterial({ color: 0xffc9a0 }));
  wd.position.set(2.6, 0.9, -3.5);
  const wdGlow = sprite(0xff9a60, 1.6, 'soft', 0.45);
  wdGlow.position.copy(wd.position);
  scene.add(wd, wdGlow);
  const rd = sprite(0xff4a20, 3.2, 'core', 0.9);
  rd.position.set(-7, 2.5, -14);
  const rdGlow = sprite(0xff3010, 9, 'soft', 0.4);
  rdGlow.position.copy(rd.position);
  scene.add(rd, rdGlow);

  const you = humanFigure({ count: 14000, seed: 3, color: [1.0, 0.62, 0.35] });
  you.material.uniforms.uPix.value = ctx.pix;
  scene.add(you);
  const aura = sprite(0xff8a50, 3.0, 'soft', 0.25);
  scene.add(aura);
  const ring = pulseRing(0xffa070);
  ring.position.set(-0.03, 0.42, 0.06);
  scene.add(ring);

  function update(t, dur) {
    cmb.material.opacity = 1 - smooth(info.cue(3) + 1, info.cue(3) + 6, t);
    cmb.visible = cmb.material.opacity > 0.002;
    const hb = heartbeat(t, 1.6);
    you.material.uniforms.uTime.value = t;
    you.material.uniforms.uPulse.value = hb;
    const p = ((t % 4.8) / 4.8);
    ring.scale.setScalar(0.1 + p * 3.5);
    ring.material.opacity = 0.35 * (1 - p) * (1 - p);
    ring.quaternion.copy(camera.quaternion);
    gal.uniforms.uRot.value = -t * 0.02;
    // "still early": red dwarfs brighten, the view opens up
    const hope = smooth(info.cue(5) - 1, info.cue(5) + 4, t);
    rm.uniforms.uAlpha.value = 0.35 + 0.65 * hope;
    for (let i = 0; i < NR; i++) rs[i] = (1 + (i % 7) * 0.45) * (0.85 + 0.15 * Math.sin(t * 1.3 + ph[i]));
    rg.attributes.size.needsUpdate = true;
    gal.uniforms.uAlpha.value = 0.55 + 0.45 * hope;

    const back = ease(smooth(info.cue(4), dur + 2, t));
    const ang = -0.35 + t * 0.012;
    const dist = 3.3 + 9 * back;
    camera.position.set(Math.sin(ang) * dist, 0.25 + 2.2 * back, Math.cos(ang) * dist);
    camera.lookAt(0, 0.1 + 0.6 * back, -4 * back);
  }
  return { scene, camera, update };
}
