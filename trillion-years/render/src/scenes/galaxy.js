// Chapter 6 — the galactic year: the Sun (and you) orbit the Milky Way.
import { THREE, starField, sprite, textSprite, smooth, ease } from '../lib.js';
import { makeGalaxy } from '../galaxyfx.js';

export default function galaxy(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, ctx.aspect, 0.05, 5000);
  const stars = starField({ count: 4000, seed: 71, size: ctx.pix * 0.8 });
  scene.add(stars);

  const R = 10;
  const gal = makeGalaxy({ count: 110000, radius: R, seed: 3, pix: ctx.pix, pitch: 19, diff: 0.06 });
  scene.add(gal.points);
  const core = sprite(0xffd9a0, 7, 'soft', 0.55);
  const core2 = sprite(0xfff0d0, 2.2, 'core', 0.8);
  scene.add(core, core2);
  const halo = sprite(0x4060a0, 34, 'soft', 0.18);
  scene.add(halo);

  // the Sun's orbit
  const RS = R * 0.55;
  const ringPts = [];
  for (let i = 0; i <= 256; i++) { const a = i / 256 * Math.PI * 2; ringPts.push(new THREE.Vector3(Math.cos(a) * RS, 0, Math.sin(a) * RS)); }
  const ring = new THREE.Line(new THREE.BufferGeometry().setFromPoints(ringPts), new THREE.LineDashedMaterial({ color: 0xffd38a, dashSize: 0.25, gapSize: 0.18, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false }));
  ring.computeLineDistances();
  scene.add(ring);
  const sun = sprite(0xffe08a, 0.9, 'core', 1);
  const sunGlow = sprite(0xffc060, 2.4, 'soft', 0.6);
  scene.add(sun, sunGlow);
  // trail behind the Sun
  const TN = 120;
  const trailPos = new Float32Array(TN * 3);
  const trailCol = new Float32Array(TN * 3);
  const tg = new THREE.BufferGeometry();
  tg.setAttribute('position', new THREE.BufferAttribute(trailPos, 3));
  tg.setAttribute('color', new THREE.BufferAttribute(trailCol, 3));
  const trail = new THREE.Line(tg, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  trail.frustumCulled = false;
  scene.add(trail);
  const label = textSprite(['YOU ARE HERE'], { size: 0.38, color: '#ffe3a0' });
  label.userData.aspect = label.scale.x / label.scale.y;
  scene.add(label);

  const phi0 = 2.2;
  // number of laps the Sun has made at local time t
  const laps = (t) => 0.012 * t + 1.0 * ease(smooth(info.cue(1) + 1, info.cueEnd(2) + 1, t)) + 3.0 * Math.pow(smooth(info.cue(4), info.dur + 1, t), 2);

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    const L = laps(t);
    const rot = -L * Math.PI * 2;
    gal.uniforms.uRot.value = rot;
    const phi = phi0 + rot;
    const sp = new THREE.Vector3(Math.cos(phi) * RS, 0.05, Math.sin(phi) * RS);
    sun.position.copy(sp); sunGlow.position.copy(sp);
    sun.scale.setScalar(0.6 + 0.15 * Math.sin(t * 3));
    const showL = smooth(1.5, 3.5, t) * (1 - smooth(info.cue(4) + 1, info.cue(4) + 3, t));
    label.material.opacity = showL;
    ring.material.opacity = 0.55 * smooth(info.cue(1), info.cue(1) + 3, t);
    const trailLen = 0.35 + 0.6 * smooth(info.cue(2), info.cue(3), t);
    for (let i = 0; i < TN; i++) {
      const a = phi + (i / (TN - 1)) * trailLen * Math.PI * 2;
      trailPos.set([Math.cos(a) * RS, 0.05, Math.sin(a) * RS], i * 3);
      const f = Math.pow(1 - i / (TN - 1), 1.5) * smooth(info.cue(1), info.cue(1) + 2, t);
      trailCol.set([1.0 * f, 0.8 * f, 0.4 * f], i * 3);
    }
    tg.attributes.position.needsUpdate = true;
    tg.attributes.color.needsUpdate = true;

    // camera: start near the Sun inside the disc, rise to a wide tilted view
    const up = ease(smooth(0, info.cue(2), t));
    const orbit = t * 0.025;
    const near = sp.clone().multiplyScalar(1.35).add(new THREE.Vector3(0, 0.9, 0));
    const far = new THREE.Vector3(Math.cos(orbit + 0.9) * 11.5, 9.5, Math.sin(orbit + 0.9) * 11.5);
    camera.position.lerpVectors(near, far, up);
    const target = sp.clone().multiplyScalar(0.5 * (1 - up));
    camera.lookAt(target);
    const ls = 0.38 * Math.max(1, camera.position.distanceTo(sp) / 3.5);
    label.scale.set(ls * label.userData.aspect, ls, 1);
    label.position.copy(sp).add(new THREE.Vector3(0, 0.55 + ls * 0.9, 0));
  }
  return { scene, camera, update };
}
