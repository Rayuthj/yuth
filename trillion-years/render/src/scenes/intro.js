// Chapter 0 — a single glowing human floating in space, heart beating.
import { THREE, starField, nebulaSky, humanFigure, pulseRing, heartbeat, sprite, glowTexture, smooth, ease, rng, gauss, mod } from '../lib.js';

export default function intro(ctx) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, ctx.aspect, 0.05, 5000);

  const sky = nebulaSky({ renderer: ctx.renderer, colA: [0.22, 0.08, 0.38], colB: [0.04, 0.18, 0.36], intensity: 0.6, seed: 2 });
  scene.add(sky);
  const stars = starField({ count: 7000, seed: 11, size: ctx.pix, band: 0.5 });
  scene.add(stars);

  const fig = humanFigure({ count: 14000, color: [0.4, 0.78, 1.0] });
  fig.material.uniforms.uPix.value = ctx.pix;
  scene.add(fig);

  const heart = sprite(0xff6a7a, 0.18, 'core', 0.9);
  heart.position.set(-0.03, 0.42, 0.06);
  scene.add(heart);
  const aura = sprite(0x3aa8ff, 3.2, 'soft', 0.35);
  aura.position.set(0, 0.0, 0);
  scene.add(aura);

  const rings = [];
  for (let i = 0; i < 4; i++) {
    const r = pulseRing(0x6fd0ff);
    r.position.copy(heart.position);
    scene.add(r);
    rings.push(r);
  }

  // drifting motes of light around the figure
  const r = rng(5);
  const N = 1500;
  const mp = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) mp.set([gauss(r) * 2.5, gauss(r) * 1.6, gauss(r) * 2.5], i * 3);
  const mg = new THREE.BufferGeometry();
  mg.setAttribute('position', new THREE.BufferAttribute(mp, 3));
  const motes = new THREE.Points(mg, new THREE.PointsMaterial({
    size: 0.018, color: 0x8fd0ff, transparent: true, opacity: 0.55,
    blending: THREE.AdditiveBlending, depthWrite: false, map: glowTexture('soft'),
  }));
  scene.add(motes);

  // glowing disc under the feet
  const disc = sprite(0x2f7dff, 1.6, 'soft', 0.35);
  disc.position.set(0, -0.86, 0);
  scene.add(disc);

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    fig.material.uniforms.uTime.value = t;
    const hb = heartbeat(t, 1.05);
    fig.material.uniforms.uPulse.value = hb;
    heart.material.opacity = 0.35 + 0.65 * hb;
    heart.scale.setScalar(0.12 + 0.12 * hb);
    rings.forEach((ring, i) => {
      const p = mod(t + i * 1.05, 4.2) / 4.2;
      ring.scale.setScalar(0.1 + p * 3.0);
      ring.material.opacity = 0.5 * (1 - p) * (1 - p);
      ring.quaternion.copy(camera.quaternion);
    });
    motes.rotation.y = t * 0.03;

    // camera: slow orbit, rising then pulling far back at the end of the chapter
    const ang = -0.6 + t * 0.045;
    const back = smooth(dur - 12, dur + 1, t);
    const dist = 4.6 - 0.8 * ease(smooth(6, 20, t)) + back * 9;
    const h = 0.25 + 0.2 * Math.sin(t * 0.12) + back * 1.5;
    camera.position.set(Math.sin(ang) * dist, h, Math.cos(ang) * dist);
    camera.lookAt(0, 0.55 - 0.2 * smooth(6, 20, t) + back * 0.2, 0);
  }

  return { scene, camera, update };
}
