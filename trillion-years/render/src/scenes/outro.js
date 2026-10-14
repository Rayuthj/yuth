// Chapter 13 — back to now: sunrise over the Earth's limb.
import { THREE, starField, sprite, smooth, ease } from '../lib.js';
import { createEarth } from '../earth.js';

export default function outro(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, ctx.aspect, 0.005, 5000);
  const stars = starField({ count: 7000, seed: 131, size: ctx.pix });
  scene.add(stars);

  const earth = createEarth(ctx.renderer);
  earth.group.rotation.z = 0.25;
  scene.add(earth.group);
  earth.uniforms.uCity.value = 1;
  earth.uniforms.uClouds.value = 0.85;

  const sunCore = sprite(0xfff6e8, 40, 'core', 1);
  const sunFlare = sprite(0xfff0d0, 170, 'flare', 0.8);
  const sunGlow = sprite(0xffc890, 300, 'soft', 0.5);
  scene.add(sunGlow, sunFlare, sunCore);
  const sunDir = new THREE.Vector3();

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    // the Sun climbs over the limb during "maybe a sunrise feels beautiful"
    const rise = ease(smooth(info.cue(2) + 1, info.cue(3) + 3, t));
    const th = 0.17 + 0.17 * rise + 0.025 * smooth(info.cueEnd(3), dur, t);
    sunDir.set(0.12, Math.sin(th), -Math.cos(th)).normalize();
    earth.uniforms.uSunDir.value.copy(sunDir);
    const sp = sunDir.clone().multiplyScalar(1200);
    sunCore.position.copy(sp); sunFlare.position.copy(sp); sunGlow.position.copy(sp);
    sunFlare.material.opacity = 0.8 * smooth(0.24, 0.3, th);
    earth.atmoU.uStrength.value = 1.2;
    earth.uniforms.uCloudT.value = t * 0.0015;
    earth.group.rotation.y = 2.3 + t * 0.01;

    const p = smooth(0, dur, t);
    camera.position.set(0.05 * p, 0.42 - 0.06 * p, 2.35 - 0.25 * ease(p));
    camera.lookAt(0, 1.12 + 0.04 * p, -0.2);
  }
  return { scene, camera, update };
}
