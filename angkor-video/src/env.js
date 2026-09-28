import * as THREE from 'three';
import { rng, prep, merge, mtx, lerp, clamp } from './util.js';

// ---------- sky presets ----------
export const SKY = {
  predawn: {
    top: '#26346e', mid: '#7a5aa6', horizon: '#ffa47a', bottom: '#3a3456', sun: '#ffc08a',
    glow: 0.9, sunVisible: 0, hemiSky: '#a9b6ff', hemiGround: '#5a4a60', hemiI: 1.6,
    lightColor: '#ffc7a0', lightI: 1.3, fog: '#a898c8', fogNear: 120, fogFar: 1400, stars: 0.7,
    cloud: '#ffb8b0', cloudI: 0.35, env: 0.55,
  },
  sunrise: {
    top: '#3a4fa8', mid: '#d887a0', horizon: '#ff9448', bottom: '#5a4050', sun: '#ffc070',
    glow: 2.2, sunVisible: 1, hemiSky: '#e8c0c8', hemiGround: '#806048', hemiI: 1.3,
    lightColor: '#ffa860', lightI: 3.2, fog: '#e8a080', fogNear: 150, fogFar: 1500, stars: 0.0,
    cloud: '#ffc090', cloudI: 0.45, env: 0.6,
  },
  day: {
    top: '#2f7fe0', mid: '#6fb4f2', horizon: '#c8e4f8', bottom: '#8aa070', sun: '#fff4dc',
    glow: 0.6, sunVisible: 1, hemiSky: '#c8dcff', hemiGround: '#6f7a4a', hemiI: 1.05,
    lightColor: '#ffe8c8', lightI: 2.7, fog: '#c8e0f0', fogNear: 200, fogFar: 1700, stars: 0,
    cloud: '#ffffff', cloudI: 0.25, env: 0.7,
  },
  jungle: {
    top: '#4f93d8', mid: '#9cc8e8', horizon: '#dff0e0', bottom: '#556b3a', sun: '#fff0c8',
    glow: 0.5, sunVisible: 0, hemiSky: '#c8f0c0', hemiGround: '#4a5a2a', hemiI: 1.25,
    lightColor: '#fff0c0', lightI: 3.1, fog: '#9fbf8f', fogNear: 25, fogFar: 180, stars: 0,
    cloud: '#ffffff', cloudI: 0.25, env: 0.6,
  },
  sunset: {
    top: '#3a4a9a', mid: '#e0809a', horizon: '#ffb45a', bottom: '#6a4a40', sun: '#ffcf80',
    glow: 1.4, sunVisible: 1, hemiSky: '#ffc8c0', hemiGround: '#6a4a3a', hemiI: 1.15,
    lightColor: '#ffae5a', lightI: 3.0, fog: '#f0a888', fogNear: 150, fogFar: 1500, stars: 0,
    cloud: '#ffa878', cloudI: 0.5, env: 0.6,
  },
  road: {
    top: '#3a5aa8', mid: '#9d8cc0', horizon: '#ffc49a', bottom: '#5a5060', sun: '#ffd6a0',
    glow: 1.2, sunVisible: 1, hemiSky: '#c0c8ff', hemiGround: '#6a5a48', hemiI: 1.45,
    lightColor: '#ffc690', lightI: 2.4, fog: '#d8b0b0', fogNear: 60, fogFar: 700, stars: 0.15,
    cloud: '#ffc0a0', cloudI: 0.45, env: 0.6,
  },
};

export function blendPreset(a, b, t) {
  const out = {};
  for (const k of Object.keys(a)) {
    const va = a[k];
    const vb = b[k];
    if (typeof va === 'string') out[k] = '#' + new THREE.Color(va).lerp(new THREE.Color(vb), t).getHexString();
    else out[k] = lerp(va, vb, t);
  }
  return out;
}

const skyVert = /* glsl */ `
varying vec3 vDir;
void main(){
  vDir = normalize((modelMatrix * vec4(position,1.0)).xyz - cameraPosition);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
}`;
const skyVertEnv = /* glsl */ `
varying vec3 vDir;
void main(){
  vDir = normalize(position);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
}`;
const skyFrag = /* glsl */ `
uniform vec3 top; uniform vec3 mid; uniform vec3 horizon; uniform vec3 bottom; uniform vec3 sunColor;
uniform vec3 sunDir; uniform float glowAmt; uniform float sunVisible;
varying vec3 vDir;
void main(){
  vec3 d = normalize(vDir);
  float h = d.y;
  vec3 col;
  if (h > 0.0) {
    col = mix(horizon, mid, smoothstep(0.0, 0.28, h));
    col = mix(col, top, smoothstep(0.22, 0.85, h));
  } else {
    col = mix(horizon, bottom, smoothstep(0.0, -0.12, h));
  }
  vec3 sd3 = normalize(sunDir);
  float sd = dot(d, sd3);
  // horizontal glow band around the sun azimuth
  vec2 dh = normalize(d.xz + 1e-5); vec2 sh = normalize(sd3.xz + 1e-5);
  float az = max(dot(dh, sh), 0.0);
  float band = pow(az, 3.0) * exp(-max(h, 0.0) * 6.0) * 0.55;
  col += sunColor * band * glowAmt;
  col += sunColor * (pow(max(sd, 0.0), 12.0) * 0.55 + pow(max(sd, 0.0), 180.0) * 1.2) * glowAmt;
  float disk = smoothstep(0.99955, 0.9997, sd);
  col = mix(col, vec3(1.0, 0.97, 0.88) * 2.6, disk * sunVisible * step(-0.01, h));
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

function skyMaterial(env = false) {
  return new THREE.ShaderMaterial({
    uniforms: {
      top: { value: new THREE.Color() },
      mid: { value: new THREE.Color() },
      horizon: { value: new THREE.Color() },
      bottom: { value: new THREE.Color() },
      sunColor: { value: new THREE.Color() },
      sunDir: { value: new THREE.Vector3(0, 1, 0) },
      glowAmt: { value: 1 },
      sunVisible: { value: 1 },
    },
    vertexShader: env ? skyVertEnv : skyVert,
    fragmentShader: skyFrag,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });
}

function applySkyUniforms(mat, p, sunDir) {
  const u = mat.uniforms;
  u.top.value.set(p.top);
  u.mid.value.set(p.mid);
  u.horizon.value.set(p.horizon);
  u.bottom.value.set(p.bottom);
  u.sunColor.value.set(p.sun);
  u.sunDir.value.copy(sunDir);
  u.glowAmt.value = p.glow;
  u.sunVisible.value = p.sunVisible;
}

export function dirFromAngles(azDeg, elDeg) {
  const az = THREE.MathUtils.degToRad(azDeg);
  const el = THREE.MathUtils.degToRad(elDeg);
  return new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).normalize();
}

// Atmosphere: sky dome + stars + clouds + lights + fog
export class Atmos {
  constructor(scene, o = {}) {
    this.scene = scene;
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), skyMaterial());
    this.sky.frustumCulled = false;
    this.sky.renderOrder = -10;
    scene.add(this.sky);

    const r = rng(o.seed ?? 7);
    const sp = [];
    for (let i = 0; i < 900; i++) {
      const th = r() * Math.PI * 2;
      const y = 0.08 + r() * 0.92;
      const rr = Math.sqrt(1 - y * y);
      sp.push(Math.cos(th) * rr * 1500, y * 1500, Math.sin(th) * rr * 1500);
    }
    const sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
    this.stars = new THREE.Points(
      sg,
      new THREE.PointsMaterial({ color: 0xffffff, size: 2.2, sizeAttenuation: false, transparent: true, opacity: 0, fog: false, depthWrite: false })
    );
    this.stars.frustumCulled = false;
    scene.add(this.stars);

    this.hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
    scene.add(this.hemi);
    this.sun = new THREE.DirectionalLight(0xffffff, 2);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.bias = -0.0004;
    this.sun.shadow.normalBias = 0.04;
    this.sun.shadow.radius = 3;
    scene.add(this.sun);
    scene.add(this.sun.target);
    scene.fog = new THREE.Fog(0xffffff, 100, 1000);

    // cartoon clouds
    this.cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, emissive: 0xffffff, emissiveIntensity: 0.3, fog: false });
    this.clouds = new THREE.Group();
    const nClouds = o.clouds ?? 16;
    for (let i = 0; i < nClouds; i++) {
      const parts = [];
      const nb = 5 + Math.floor(r() * 5);
      for (let j = 0; j < nb; j++) {
        const rad = 14 + r() * 16;
        const g = new THREE.IcosahedronGeometry(rad, 2);
        parts.push(prep(g, 0xffffff, mtx([(j - nb / 2) * 16 + r() * 8, r() * 10 + (j % 2) * 6, r() * 14], [0, 0, 0], [1, 0.72, 0.9])));
      }
      const cg = merge(parts);
      const c = new THREE.Mesh(cg, this.cloudMat);
      const ang = (i / nClouds) * Math.PI * 2 + r() * 0.3;
      const dist = 700 + r() * 500;
      c.position.set(Math.cos(ang) * dist, 110 + r() * 170, Math.sin(ang) * dist);
      c.lookAt(0, c.position.y, 0);
      c.scale.setScalar(0.8 + r() * 0.8);
      this.clouds.add(c);
    }
    scene.add(this.clouds);
    this.sunDir = new THREE.Vector3(0, 1, 0);
    this.preset = SKY.day;
  }

  set(preset, sunDir, lightDir = null) {
    this.preset = preset;
    this.sunDir.copy(sunDir).normalize();
    applySkyUniforms(this.sky.material, preset, this.sunDir);
    this.hemi.color.set(preset.hemiSky);
    this.hemi.groundColor.set(preset.hemiGround);
    this.hemi.intensity = preset.hemiI;
    this.sun.color.set(preset.lightColor);
    this.sun.intensity = preset.lightI;
    this.lightDir = (lightDir ? lightDir.clone() : this.sunDir.clone()).normalize();
    if (this.lightDir.y < 0.18) {
      this.lightDir.y = 0.18;
      this.lightDir.normalize();
    }
    this.scene.fog.color.set(preset.fog);
    this.scene.fog.near = preset.fogNear;
    this.scene.fog.far = preset.fogFar;
    this.stars.material.opacity = preset.stars;
    this.stars.visible = preset.stars > 0.01;
    this.cloudMat.emissive.set(preset.cloud);
    this.cloudMat.emissiveIntensity = preset.cloudI;
    this.scene.environmentIntensity = preset.env;
  }

  // Place shadow camera around a focus point
  focus(center, size = 40, camPos = null) {
    const d = this.lightDir;
    this.sun.target.position.copy(center);
    this.sun.position.copy(center).addScaledVector(d, 300);
    const c = this.sun.shadow.camera;
    c.left = -size;
    c.right = size;
    c.top = size;
    c.bottom = -size;
    c.near = 10;
    c.far = 700;
    c.updateProjectionMatrix();
    if (camPos) {
      this.sky.position.copy(camPos);
      this.stars.position.copy(camPos);
    }
  }

  update(camera) {
    this.sky.position.copy(camera.position);
    this.sky.scale.setScalar(1500);
    this.stars.position.copy(camera.position);
  }
}

// Build a PMREM environment from a preset (for soft IBL reflections)
export function envFromPreset(renderer, preset, sunDir) {
  const s = new THREE.Scene();
  const mat = skyMaterial(true);
  applySkyUniforms(mat, preset, sunDir);
  mat.uniforms.sunVisible.value = 0;
  const m = new THREE.Mesh(new THREE.SphereGeometry(100, 32, 16), mat);
  s.add(m);
  const pm = new THREE.PMREMGenerator(renderer);
  const rt = pm.fromScene(s, 0.02);
  pm.dispose();
  return rt.texture;
}

// ---------- vegetation ----------
export function sugarPalmGeo(seed) {
  const r = rng(seed);
  const parts = [];
  const h = 11 + r() * 5;
  const lean = (r() - 0.5) * 0.08;
  const trunk = new THREE.CylinderGeometry(0.22, 0.34, h, 7, 6);
  // gentle bend
  const pos = trunk.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const y = pos.getY(i) + h / 2;
    pos.setX(i, pos.getX(i) + Math.sin((y / h) * Math.PI * 0.5) * lean * h);
  }
  trunk.translate(0, h / 2, 0);
  parts.push(prep(trunk, 0x6e6258));
  // rough old leaf-bases near top
  const topX = Math.sin(Math.PI * 0.5) * lean * h;
  const top = new THREE.Vector3(topX, h, 0);
  parts.push(prep(new THREE.IcosahedronGeometry(0.55, 1), 0x6a5a40, mtx([top.x, top.y - 0.2, 0], [0, 0, 0], [1, 1.3, 1])));
  const n = 44;
  const up = new THREE.Vector3(0, 1, 0);
  for (let i = 0; i < n; i++) {
    const az = i * 2.39996 + r() * 0.3;
    const u = i / n;
    const el = lerp(1.4, -0.7, u) + (r() - 0.5) * 0.25;
    const dir = new THREE.Vector3(Math.cos(az) * Math.cos(el), Math.sin(el), Math.sin(az) * Math.cos(el));
    const dead = el < -0.4 && r() < 0.6;
    const stalkLen = 0.7 + r() * 0.35;
    // stalk
    const sg = new THREE.CylinderGeometry(0.035, 0.05, stalkLen, 4);
    sg.translate(0, stalkLen / 2, 0);
    const q = new THREE.Quaternion().setFromUnitVectors(up, dir);
    const sm = new THREE.Matrix4().compose(top, q, new THREE.Vector3(1, 1, 1));
    parts.push(prep(sg, 0x7a8a3a, sm));
    // fan leaf
    const rad = 1.05 + r() * 0.35;
    const lg = new THREE.CircleGeometry(rad, 8, Math.PI / 2 - 1.2, 2.4);
    // crinkle: pleats
    const lp = lg.attributes.position;
    for (let k = 0; k < lp.count; k++) {
      const x = lp.getX(k);
      const y = lp.getY(k);
      const a = Math.atan2(y, x);
      lp.setZ(k, Math.sin(a * 18) * 0.08 * Math.hypot(x, y) - Math.hypot(x, y) * 0.12);
    }
    lg.computeVertexNormals();
    const roll = new THREE.Quaternion().setFromAxisAngle(up, r() * Math.PI);
    const q2 = q.clone().multiply(roll);
    const lm = new THREE.Matrix4().compose(top.clone().addScaledVector(dir, stalkLen), q2, new THREE.Vector3(1, 1, 1));
    const g = 0.75 + r() * 0.35;
    const col = dead ? new THREE.Color(0.6, 0.47, 0.25) : new THREE.Color(0.34 * g, 0.62 * g, 0.22 * g);
    parts.push(prep(lg, col, lm));
  }
  return merge(parts);
}

export function broadTreeGeo(seed, o = {}) {
  const r = rng(seed);
  const parts = [];
  const h = (o.h ?? 6) + r() * (o.hv ?? 4);
  const tr = new THREE.CylinderGeometry(0.28, 0.5, h, 7);
  tr.translate(0, h / 2, 0);
  parts.push(prep(tr, o.trunk ?? 0x6b5040));
  const base = new THREE.Color(o.leaf ?? 0x4f8f3a);
  const n = 7 + Math.floor(r() * 4);
  const spread = o.spread ?? 3.2;
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2;
    const d = r() * spread;
    const rad = (o.blob ?? 2.2) + r() * 1.4;
    const c = base.clone().offsetHSL((r() - 0.5) * 0.05, (r() - 0.5) * 0.1, (r() - 0.5) * 0.12);
    parts.push(prep(new THREE.IcosahedronGeometry(rad, 1), c, mtx([Math.cos(a) * d, h + r() * 2.5 - 0.5, Math.sin(a) * d], [r(), r(), r()], [1, 0.85, 1])));
  }
  // branches
  for (let i = 0; i < 3; i++) {
    const b = new THREE.CylinderGeometry(0.08, 0.16, 2.5, 5);
    b.translate(0, 1.25, 0);
    parts.push(prep(b, o.trunk ?? 0x6b5040, mtx([0, h * 0.7, 0], [0.9, i * 2.1, 0])));
  }
  return merge(parts);
}

export function farTreeGeo(seed, leaf = 0x3f7f35) {
  const r = rng(seed);
  const parts = [];
  const h = 9 + r() * 5;
  const tr = new THREE.CylinderGeometry(0.4, 0.7, h, 5);
  tr.translate(0, h / 2, 0);
  parts.push(prep(tr, 0x5a4535));
  const base = new THREE.Color(leaf);
  for (let i = 0; i < 4; i++) {
    const a = (i / 4) * Math.PI * 2 + r();
    const c = base.clone().offsetHSL(0, 0, (r() - 0.5) * 0.12);
    parts.push(prep(new THREE.IcosahedronGeometry(3.6 + r() * 1.5, 1), c, mtx([Math.cos(a) * 3, h + r() * 2, Math.sin(a) * 3], [r(), r(), r()], [1, 0.8, 1])));
  }
  return merge(parts);
}

export function bushGeo(seed, color = 0x4a8a35) {
  const r = rng(seed);
  const parts = [];
  const base = new THREE.Color(color);
  for (let i = 0; i < 4; i++) {
    const c = base.clone().offsetHSL(0, 0, (r() - 0.5) * 0.12);
    parts.push(prep(new THREE.IcosahedronGeometry(0.7 + r() * 0.5, 1), c, mtx([(r() - 0.5) * 1.6, 0.5 + r() * 0.4, (r() - 0.5) * 1.6], [0, 0, 0], [1, 0.8, 1])));
  }
  return merge(parts);
}

export const leafMat = () =>
  new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide });
export const vcMat = () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 });

// Scatter instances of several geometry variants, chunked spatially so that
// off-screen chunks are frustum culled (both in the main and shadow passes).
export function scatter(group, geos, mat, placements, seed = 1, cast = true, cell = 70) {
  const r = rng(seed);
  const buckets = new Map();
  for (const p of placements) {
    const gi = Math.floor(r() * geos.length);
    const key = gi + ':' + Math.floor(p.x / cell) + ':' + Math.floor(p.z / cell);
    if (!buckets.has(key)) buckets.set(key, { gi, list: [] });
    buckets.get(key).list.push({ ...p, ry: p.ry ?? r() * Math.PI * 2, s: p.s ?? 0.85 + r() * 0.35 });
  }
  const dummy = new THREE.Object3D();
  const out = [];
  for (const { gi, list } of buckets.values()) {
    const im = new THREE.InstancedMesh(geos[gi], mat, list.length);
    list.forEach((p, i) => {
      dummy.position.set(p.x, p.y ?? 0, p.z);
      dummy.rotation.set(0, p.ry, 0);
      dummy.scale.setScalar(p.s);
      dummy.updateMatrix();
      im.setMatrixAt(i, dummy.matrix);
    });
    im.computeBoundingSphere();
    im.castShadow = cast;
    im.receiveShadow = true;
    group.add(im);
    out.push(im);
  }
  return out;
}

// ---------- birds ----------
export class Flock {
  constructor(scene, n = 12, seed = 3, color = 0x2a2a35) {
    const r = rng(seed);
    this.birds = [];
    const mat = new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, fog: true });
    const wing = new THREE.BufferGeometry();
    wing.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, -0.18, 0, 0, 0.28, 0.7, 0, 0.12, 0, 0, -0.18, 0.7, 0, 0.12, 0.7, 0, -0.1], 3));
    wing.computeVertexNormals();
    const tip = new THREE.BufferGeometry();
    tip.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, -0.1, 0, 0, 0.12, 0.75, 0, -0.22], 3));
    tip.computeVertexNormals();
    this.group = new THREE.Group();
    for (let i = 0; i < n; i++) {
      const b = new THREE.Group();
      const body = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 4), mat);
      body.scale.set(0.7, 0.7, 2);
      b.add(body);
      const wl = new THREE.Mesh(wing, mat);
      const wr = new THREE.Mesh(wing, mat);
      wr.scale.x = -1;
      const tl = new THREE.Mesh(tip, mat);
      const trr = new THREE.Mesh(tip, mat);
      tl.position.x = 0.7;
      trr.position.x = 0.7;
      wl.add(tl);
      wr.add(trr);
      b.add(wl, wr);
      b.userData.tl = tl;
      b.userData.tr = trr;
      Object.assign(b.userData, { wl, wr, off: [(r() - 0.5) * 30, (r() - 0.5) * 8, (r() - 0.5) * 20], ph: r() * 6, sp: 9 + r() * 2 });
      this.group.add(b);
      this.birds.push(b);
    }
    scene.add(this.group);
  }
  // fly along a line from a to b between t0..t1
  update(t, a, b, t0, t1, scale = 2.5) {
    const u = (t - t0) / (t1 - t0);
    this.group.visible = u > -0.05 && u < 1.05;
    const dir = b.clone().sub(a).normalize();
    for (const bd of this.birds) {
      const d = bd.userData;
      const p = a.clone().lerp(b, u);
      bd.position.set(p.x + d.off[0], p.y + d.off[1] + Math.sin(t * 1.3 + d.ph) * 1.2, p.z + d.off[2]);
      bd.lookAt(bd.position.clone().add(dir));
      bd.scale.setScalar(scale);
      const f = Math.sin(t * d.sp + d.ph) * 0.55;
      d.wl.rotation.z = f;
      d.wr.rotation.z = -f;
      d.tl.rotation.z = f * 0.8 - 0.1;
      d.tr.rotation.z = f * 0.8 - 0.1;
    }
  }
}

export { clamp };
