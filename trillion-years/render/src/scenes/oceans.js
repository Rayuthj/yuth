// Chapter 7 — leaving Earth: the Sun brightens, the Moon drifts off, oceans
// boil away, and a ship leaves the scorched planet.
import { THREE, starField, nebulaSky, sprite, smooth, ease, clamp } from '../lib.js';
import { createEarth, ULTIMA } from '../earth.js';

function makeShip() {
  const g = new THREE.Group();
  const hull = new THREE.MeshStandardMaterial({ color: 0xdfe6ee, metalness: 0.6, roughness: 0.35 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x39424d, metalness: 0.7, roughness: 0.4 });
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.13, 0.9, 24), hull);
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.35, 24), hull);
  nose.position.y = 0.62;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.035, 10, 32), dark);
  ring.rotation.x = Math.PI / 2;
  ring.position.y = 0.05;
  g.add(body, nose, ring);
  for (let i = 0; i < 3; i++) {
    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.28, 0.2), dark);
    const a = i / 3 * Math.PI * 2;
    fin.position.set(Math.cos(a) * 0.15, -0.35, Math.sin(a) * 0.15);
    fin.rotation.y = -a;
    g.add(fin);
  }
  const engine = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 0.12, 20), dark);
  engine.position.y = -0.5;
  g.add(engine);
  const flame = sprite(0x9fd8ff, 0.9, 'core', 1);
  flame.position.y = -0.62;
  const flame2 = sprite(0x4f8dff, 1.8, 'soft', 0.7);
  flame2.position.y = -0.7;
  g.add(flame, flame2);
  g.userData = { flame, flame2 };
  return g;
}

export default function oceans(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, ctx.aspect, 0.005, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, intensity: 0.22, seed: 12 }));
  const stars = starField({ count: 6000, seed: 81, size: ctx.pix });
  scene.add(stars);

  const earth = createEarth(ctx.renderer);
  earth.setPlates(ULTIMA);
  earth.group.rotation.z = 0.3;
  scene.add(earth.group);
  const sunDir = new THREE.Vector3(1, 0.25, 0.35).normalize();
  earth.uniforms.uSunDir.value.copy(sunDir);
  earth.uniforms.uClouds.value = 0.6;

  const sunCore = sprite(0xfff4e0, 60, 'core', 1);
  const sunGlow = sprite(0xffd28a, 220, 'soft', 0.5);
  const sunPos = sunDir.clone().multiplyScalar(400);
  sunCore.position.copy(sunPos); sunGlow.position.copy(sunPos);
  scene.add(sunCore, sunGlow);

  const moon = new THREE.Mesh(new THREE.SphereGeometry(0.27, 48, 24), new THREE.MeshStandardMaterial({ color: 0x9a968f, roughness: 1 }));
  scene.add(moon);
  const light = new THREE.DirectionalLight(0xffffff, 2.4);
  light.position.copy(sunDir);
  scene.add(light);
  scene.add(new THREE.AmbientLight(0x334455, 0.35));

  const ship = makeShip();
  ship.scale.setScalar(0.12);
  scene.add(ship);
  // exhaust trail
  const TN = 40;
  const trail = Array.from({ length: TN }, (_, i) => {
    const s = sprite(0x7fb8ff, 0.1, 'soft', 0);
    scene.add(s);
    return s;
  });

  const launch0 = new THREE.Vector3();
  const tmp = new THREE.Vector3();
  function shipPath(u, out) {
    // from just above the surface towards (and past) the camera side
    const a = ease(clamp(u));
    out.copy(launch0).multiplyScalar(1.03 + a * 3.2);
    out.x += Math.sin(a * 2.0) * 0.5 * a;
    out.y += 0.4 * a * a;
    return out;
  }

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    const u = earth.uniforms;
    const bright = smooth(info.cue(1), info.cue(3) + 4, t);
    const plants = smooth(info.cue(2) + 3, info.cue(3), t);
    const boil = smooth(info.cue(3) + 1, info.cue(4) + 1, t);
    const desert = smooth(info.cue(4) - 1, info.cue(5), t);
    u.uSunBright.value = 1 + 0.5 * bright;
    u.uDry.value = 0.35 * plants + 0.65 * boil;
    u.uSea.value = 0.55 * boil;
    u.uOcean.value = 1 - smooth(info.cue(3) + 3, info.cue(4) + 2, t);
    // steam first thickens the clouds, then everything clears
    u.uClouds.value = 0.6 + 0.5 * Math.sin(Math.PI * smooth(info.cue(3), info.cue(4) + 1, t)) - 0.6 * smooth(info.cue(4), info.cue(4) + 3, t);
    u.uBurn.value = 0.35 * desert;
    u.uNightGlow.value = desert;
    u.uAtmo.value.set(0.35 + 0.6 * boil, 0.6 - 0.15 * boil, 1.0 - 0.75 * boil).multiplyScalar(1 - 0.5 * desert);
    earth.atmoU.uStrength.value = 1 - 0.55 * desert;
    u.uCloudT.value = t * 0.003;
    earth.group.rotation.y = -Math.PI / 2 - 0.3 + t * 0.01;

    sunCore.scale.setScalar(60 + 50 * bright);
    sunGlow.scale.setScalar(220 + 260 * bright);
    sunGlow.material.opacity = 0.45 + 0.3 * bright;

    // the Moon slowly drifts away
    const md = 3.2 + 4.5 * smooth(info.cue(2) - 2, info.cue(3), t);
    const ma = 2.4 + t * 0.012;
    moon.position.set(Math.cos(ma) * md, 0.5 + md * 0.08, Math.sin(ma) * md);

    // ship launch
    const tl = info.cue(5) - 0.5;
    const su = (t - tl) / 8.5;
    ship.visible = su > 0;
    trail.forEach((s) => { s.visible = su > 0; });
    if (su > 0) {
      launch0.set(0.25, 0.35, 1).normalize();
      shipPath(su, ship.position);
      shipPath(su + 0.01, tmp);
      ship.up.set(0, 1, 0);
      const dir = tmp.clone().sub(ship.position).normalize();
      ship.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      const f = 0.85 + 0.15 * Math.sin(t * 40);
      ship.userData.flame.scale.setScalar(0.9 * f);
      ship.userData.flame2.scale.setScalar(1.8 * f);
      trail.forEach((s, i) => {
        const uu = su - (i + 1) * 0.012;
        shipPath(Math.max(uu, 0), s.position);
        const k = 1 - i / TN;
        s.material.opacity = uu > 0 ? 0.55 * k * k : 0;
        s.scale.setScalar(0.04 + 0.12 * (1 - k));
      });
    }

    // camera: wide on the planet, then follows the ship out
    const p = smooth(0, dur, t);
    const base = new THREE.Vector3(Math.sin(0.35 + 0.2 * p) * 3.8, 0.8 - 0.3 * p, Math.cos(0.35 + 0.2 * p) * 3.8);
    const follow = smooth(tl + 1, tl + 6, t);
    if (follow > 0) {
      const sp = ship.position;
      const chase = sp.clone().add(new THREE.Vector3(0.55, 0.12, 0.85));
      camera.position.lerpVectors(base, chase, ease(follow));
      const look = new THREE.Vector3(0, 0, 0).lerp(sp, ease(follow) * 0.75);
      camera.lookAt(look);
    } else {
      camera.position.copy(base);
      camera.lookAt(0, 0, 0);
    }
  }
  return { scene, camera, update };
}
