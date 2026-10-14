// Chapter 5 — moving continents: plates slide together into Pangaea Ultima.
import { THREE, starField, nebulaSky, smooth, ease } from '../lib.js';
import { createEarth, PRESENT, ULTIMA } from '../earth.js';

export default function drift(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, ctx.aspect, 0.01, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, intensity: 0.25, seed: 9, colA: [0.1, 0.12, 0.3], colB: [0.2, 0.08, 0.25] }));
  const stars = starField({ count: 6000, seed: 61, size: ctx.pix });
  scene.add(stars);

  const earth = createEarth(ctx.renderer);
  earth.group.rotation.z = 0.3;
  scene.add(earth.group);
  earth.uniforms.uSunDir.value.set(0.55, 0.35, 0.75).normalize();
  earth.uniforms.uClouds.value = 0.55;
  earth.uniforms.uSea.value = 0.1;

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    // drift begins with "the ground beneath your feet is moving"
    const k = ease(smooth(info.cue(2), info.cueEnd(5) - 2, t));
    earth.setPlates(PRESENT, ULTIMA, k);
    earth.uniforms.uCloudT.value = t * 0.004;
    earth.uniforms.uClouds.value = 0.5 - 0.25 * Math.sin(t * 0.5) * smooth(info.cue(2), info.cue(3), t);
    // keep the Africa/Europe side in view, slowly turning
    earth.group.rotation.y = -Math.PI / 2 - 0.45 + t * 0.012;
    const p = smooth(0, dur, t);
    const dist = 3.9 - 0.6 * ease(p);
    const ang = 0.15 + 0.25 * p;
    camera.position.set(Math.sin(ang) * dist, 0.9 - 0.4 * p, Math.cos(ang) * dist);
    camera.lookAt(0, 0, 0);
  }
  return { scene, camera, update };
}
