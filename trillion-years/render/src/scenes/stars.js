// Chapter 4 — a changing sky: the Big Dipper warps, ice ages pass, and
// Betelgeuse explodes, taking Orion's shoulder with it.
import { THREE, starField, nebulaSky, sprite, smooth, ease, rng, NOISE_GLSL } from '../lib.js';

const DEG = Math.PI / 180;

function skyDir(az, el) {
  return new THREE.Vector3(Math.sin(az * DEG) * Math.cos(el * DEG), Math.sin(el * DEG), -Math.cos(az * DEG) * Math.cos(el * DEG));
}

// build a constellation from RA/Dec (deg) around a view direction
function constellation(scene, stars, links, center, R, scale = 1.0) {
  const ra0 = stars.reduce((s, x) => s + x[1], 0) / stars.length;
  const de0 = stars.reduce((s, x) => s + x[2], 0) / stars.length;
  const fwd = center.clone().normalize();
  const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
  const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
  const place = (ra, de) => {
    const x = -(ra - ra0) * Math.cos(de0 * DEG) * scale;
    const y = (de - de0) * scale;
    return fwd.clone().add(right.clone().multiplyScalar(x * DEG)).add(up.clone().multiplyScalar(y * DEG)).normalize().multiplyScalar(R);
  };
  const out = { stars: [], lines: null, place };
  for (const [name, ra, de, mag, col, dra = 0, dde = 0] of stars) {
    const size = (5.4 - mag) * 8.0;
    const core = sprite(col, size, 'core', 1.0);
    const halo = sprite(col, size * 2.6, 'soft', 0.35);
    const p0 = place(ra, de), p1 = place(ra + dra, de + dde);
    core.position.copy(p0); halo.position.copy(p0);
    scene.add(core, halo);
    out.stars.push({ name, core, halo, p0, p1, size });
  }
  const pos = new Float32Array(links.length * 6);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const m = new THREE.LineBasicMaterial({ color: 0x8cc8ff, transparent: true, opacity: 0.45, blending: THREE.AdditiveBlending, depthWrite: false });
  const lines = new THREE.LineSegments(g, m);
  lines.frustumCulled = false;
  scene.add(lines);
  out.lines = lines;
  out.links = links;
  out.update = (k, hide = null, hideA = 1) => {
    out.stars.forEach((s) => {
      s.core.position.lerpVectors(s.p0, s.p1, k);
      s.halo.position.copy(s.core.position);
    });
    links.forEach(([a, b], i) => {
      // shorten lines so they don't touch the stars
      const A = out.stars[a].core.position, B = out.stars[b].core.position;
      const d = B.clone().sub(A);
      const L = d.length();
      const pa = A.clone().add(d.clone().multiplyScalar(Math.min(0.45, 9 / L)));
      const pb = B.clone().sub(d.clone().multiplyScalar(Math.min(0.45, 9 / L)));
      const fade = hide != null && (a === hide || b === hide) ? hideA : 1;
      // collapse a hidden line to a point
      if (fade < 1) { const mid = pa.clone().lerp(pb, 0.5); pa.lerp(mid, 1 - fade); pb.lerp(mid, 1 - fade); }
      pos.set([...pa.toArray(), ...pb.toArray()], i * 6);
    });
    g.attributes.position.needsUpdate = true;
  };
  return out;
}

export default function stars(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, ctx.aspect, 0.1, 5000);
  const sky = nebulaSky({ renderer: ctx.renderer, colA: [0.12, 0.1, 0.22], colB: [0.08, 0.14, 0.26], intensity: 0.5, seed: 6 });
  sky.rotation.z = 0.6;
  scene.add(sky);
  const field = starField({ count: 14000, seed: 51, size: ctx.pix * 1.1, band: 0.55, radius: 900 });
  field.rotation.z = 0.6;
  scene.add(field);

  const dipC = skyDir(-28, 42);
  const dipper = constellation(scene, [
    ['Dubhe', 165.9, 61.75, 1.8, 0xffd9a0, 10, 6.5],
    ['Merak', 165.46, 56.38, 2.3, 0xe8f0ff, 3.0, -1.8],
    ['Phecda', 178.46, 53.69, 2.4, 0xe8f0ff, 3.0, -1.8],
    ['Megrez', 183.86, 57.03, 3.3, 0xe8f0ff, 3.0, -1.8],
    ['Alioth', 193.51, 55.96, 1.8, 0xe8f0ff, 3.0, -1.8],
    ['Mizar', 200.98, 54.93, 2.2, 0xe8f0ff, 3.0, -1.8],
    ['Alkaid', 206.89, 49.31, 1.9, 0xcfe0ff, -5, -13],
  ], [[0, 1], [1, 2], [2, 3], [3, 0], [3, 4], [4, 5], [5, 6]], dipC, 600, 1.3);

  const oriC = skyDir(38, 26);
  const orion = constellation(scene, [
    ['Betelgeuse', 88.79, 7.41, 0.5, 0xff8a4a],
    ['Bellatrix', 81.28, 6.35, 1.6, 0xcfe0ff],
    ['Alnitak', 85.19, -1.94, 1.8, 0xcfe0ff],
    ['Alnilam', 84.05, -1.20, 1.7, 0xcfe0ff],
    ['Mintaka', 83.0, -0.3, 2.2, 0xcfe0ff],
    ['Saiph', 86.94, -9.67, 2.1, 0xcfe0ff],
    ['Rigel', 78.63, -8.2, 0.2, 0xbcd4ff],
    ['Meissa', 83.78, 9.93, 3.3, 0xcfe0ff],
  ], [[7, 0], [7, 1], [0, 1], [0, 2], [1, 4], [2, 3], [3, 4], [2, 5], [4, 6]], oriC, 600, 1.25);
  orion.update(0);
  const betel = orion.stars[0];
  const nova = sprite(0xdfeeff, 40, 'flare', 0);
  const novaGlow = sprite(0xbfd8ff, 400, 'soft', 0);
  nova.position.copy(betel.p0);
  novaGlow.position.copy(betel.p0);
  scene.add(nova, novaGlow);

  // dark rolling hills all around the viewer, with a glowing horizon
  const ground = new THREE.CylinderGeometry(300, 300, 200, 360, 1, true);
  const gp = ground.attributes.position;
  const rr = rng(4);
  const ph = [rr() * 6, rr() * 6, rr() * 6];
  for (let i = 0; i < gp.count; i++) {
    const y = gp.getY(i);
    const a = Math.atan2(gp.getZ(i), gp.getX(i));
    if (y > 0) gp.setY(i, 8 + 10 * Math.sin(a * 3 + ph[0]) * 0.6 + 6 * Math.sin(a * 7 + ph[1]) * 0.6 + 2.5 * Math.sin(a * 23 + ph[2]) + 1.0 * Math.sin(a * 61));
    else gp.setY(i, -200);
  }
  const hills = new THREE.Mesh(ground, new THREE.MeshBasicMaterial({ color: 0x020308, side: THREE.DoubleSide }));
  scene.add(hills);
  const horizonU = { uCol: { value: new THREE.Vector3(0.25, 0.18, 0.32) }, uDay: { value: 0 } };
  const horizon = new THREE.Mesh(
    new THREE.CylinderGeometry(320, 320, 140, 96, 1, true),
    new THREE.ShaderMaterial({
      uniforms: horizonU, side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `varying float vY; void main(){ vY = position.y; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
      fragmentShader: `uniform vec3 uCol; uniform float uDay; varying float vY;
        void main(){ float a = exp(-max(vY,0.0)/14.0) * step(-5.0, vY); gl_FragColor = vec4(uCol*a*0.8 + vec3(0.25,0.35,0.5)*uDay*exp(-max(vY,0.0)/22.0)*step(-5.0, vY), 1.0);} `,
    }),
  );
  horizon.position.y = 70;
  scene.add(horizon);
  // daylight wash for the supernova
  const wash = new THREE.Mesh(new THREE.SphereGeometry(800, 32, 16), new THREE.MeshBasicMaterial({ color: 0x3a5f9a, side: THREE.BackSide, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(wash);

  const look = new THREE.Vector3();
  function update(t, dur) {
    field.material.uniforms.uTime.value = t;
    // proper motion: the Dipper warps
    const k = ease(smooth(info.cue(1) + 1, info.cueEnd(2) + 1.5, t));
    dipper.update(k);
    // ice ages: horizon breathes between warm and icy
    const ice = smooth(info.cue(3), info.cue(3) + 2, t) * (1 - smooth(info.cueEnd(3), info.cueEnd(3) + 3, t));
    const cyc = 0.5 + 0.5 * Math.sin((t - info.cue(3)) * 2.2);
    horizonU.uCol.value.set(0.25 - 0.12 * ice * cyc, 0.18 + 0.1 * ice * cyc, 0.32 + 0.35 * ice * cyc);
    hills.material.color.setRGB(0.008 + 0.05 * ice * cyc, 0.012 + 0.07 * ice * cyc, 0.03 + 0.11 * ice * cyc);

    // supernova
    const tb = info.cueEnd(4) + 0.1;
    const flash = smooth(tb, tb + 0.6, t);
    const decay = smooth(tb + 2, info.cueEnd(5) - 1.0, t);
    const sn = flash * (1 - decay);
    nova.material.opacity = sn;
    nova.scale.setScalar(60 + 260 * sn);
    novaGlow.material.opacity = 0.6 * sn;
    wash.material.opacity = 0.3 * sn;
    horizonU.uDay.value = sn;
    betel.core.material.opacity = 1 - flash;
    betel.halo.material.opacity = 0.35 * (1 - flash);
    const gone = smooth(tb + 1, info.cueEnd(5) + 0.5, t);
    orion.update(0, 0, 1 - gone);

    // camera: Dipper -> down to the horizon -> Orion
    const toH = ease(smooth(info.cue(3) - 1, info.cue(3) + 2.5, t));
    const toO = ease(smooth(info.cue(4) - 2.5, info.cue(4) + 1.5, t));
    const az = -28 + 33 * toH + 33 * toO + 3 * Math.sin(t * 0.05);
    const el = 40 - 32 * toH + 18 * toO;
    look.copy(skyDir(az, el)).multiplyScalar(100);
    camera.position.set(0, 0, 0);
    camera.lookAt(look);
    camera.fov = 55 + 6 * smooth(0, 8, t) - 8 * toO + 4 * sn;
    camera.updateProjectionMatrix();
  }
  return { scene, camera, update };
}
