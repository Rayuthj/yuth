// Shared helpers for every scene: seeded randomness, easing, glow sprites,
// star fields and a procedural nebula sky.
import * as THREE from 'three';

export { THREE };

// ---------- deterministic randomness ----------
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s += 0x6d2b79f5;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function gauss(r) {
  const u = Math.max(1e-9, r());
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r());
}

// ---------- easing ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (a, b, x) => {
  const t = clamp((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};
export const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);

// ---------- textures ----------
const texCache = {};
export function glowTexture(kind = 'soft') {
  if (texCache[kind]) return texCache[kind];
  const s = 256;
  const c = document.createElement('canvas');
  c.width = c.height = s;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  if (kind === 'soft') {
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.15, 'rgba(255,255,255,0.55)');
    grd.addColorStop(0.4, 'rgba(255,255,255,0.12)');
    grd.addColorStop(1, 'rgba(255,255,255,0)');
  } else if (kind === 'core') {
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.08, 'rgba(255,255,255,0.9)');
    grd.addColorStop(0.2, 'rgba(255,255,255,0.25)');
    grd.addColorStop(0.5, 'rgba(255,255,255,0.05)');
    grd.addColorStop(1, 'rgba(255,255,255,0)');
  } else if (kind === 'ring') {
    grd.addColorStop(0, 'rgba(255,255,255,0)');
    grd.addColorStop(0.78, 'rgba(255,255,255,0)');
    grd.addColorStop(0.9, 'rgba(255,255,255,1)');
    grd.addColorStop(1, 'rgba(255,255,255,0)');
  }
  g.fillStyle = grd;
  g.fillRect(0, 0, s, s);
  if (kind === 'flare') {
    g.clearRect(0, 0, s, s);
    const r2 = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
    r2.addColorStop(0, 'rgba(255,255,255,1)');
    r2.addColorStop(0.1, 'rgba(255,255,255,0.6)');
    r2.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r2;
    g.fillRect(0, 0, s, s);
    g.globalCompositeOperation = 'lighter';
    for (const [w, a] of [[3, 0.9], [1.5, 0.5]]) {
      const lg = g.createLinearGradient(0, 0, s, 0);
      lg.addColorStop(0, 'rgba(255,255,255,0)');
      lg.addColorStop(0.5, `rgba(255,255,255,${a})`);
      lg.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = lg;
      g.fillRect(0, s / 2 - w, s, w * 2);
      const lv = g.createLinearGradient(0, 0, 0, s);
      lv.addColorStop(0, 'rgba(255,255,255,0)');
      lv.addColorStop(0.5, `rgba(255,255,255,${a})`);
      lv.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = lv;
      g.fillRect(s / 2 - w, 0, w * 2, s);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  texCache[kind] = t;
  return t;
}

export function sprite(color = 0xffffff, size = 1, kind = 'soft', opacity = 1) {
  const m = new THREE.SpriteMaterial({
    map: glowTexture(kind), color, transparent: true, opacity,
    blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const s = new THREE.Sprite(m);
  s.scale.setScalar(size);
  return s;
}

// ---------- GLSL snippets ----------
export const NOISE_GLSL = /* glsl */`
vec3 hash33(vec3 p){
  p = fract(p * vec3(443.897, 441.423, 437.195));
  p += dot(p, p.yxz + 19.19);
  return fract((p.xxy + p.yxx) * p.zyx) * 2.0 - 1.0;
}
float gnoise(vec3 p){
  vec3 i = floor(p); vec3 f = fract(p);
  vec3 u = f*f*(3.0-2.0*f);
  return mix(mix(mix(dot(hash33(i+vec3(0,0,0)),f-vec3(0,0,0)),dot(hash33(i+vec3(1,0,0)),f-vec3(1,0,0)),u.x),
                 mix(dot(hash33(i+vec3(0,1,0)),f-vec3(0,1,0)),dot(hash33(i+vec3(1,1,0)),f-vec3(1,1,0)),u.x),u.y),
             mix(mix(dot(hash33(i+vec3(0,0,1)),f-vec3(0,0,1)),dot(hash33(i+vec3(1,0,1)),f-vec3(1,0,1)),u.x),
                 mix(dot(hash33(i+vec3(0,1,1)),f-vec3(0,1,1)),dot(hash33(i+vec3(1,1,1)),f-vec3(1,1,1)),u.x),u.y),u.z);
}
float fbm(vec3 p){
  float a = 0.5, s = 0.0;
  for(int i=0;i<5;i++){ s += a*gnoise(p); p = p*2.03 + 1.7; a *= 0.5; }
  return s;
}
float fbm3(vec3 p){
  float a = 0.5, s = 0.0;
  for(int i=0;i<3;i++){ s += a*gnoise(p); p = p*2.03 + 1.7; a *= 0.5; }
  return s;
}
`;

// ---------- star field ----------
// Round, soft points on a big sphere. `uFade` lets scenes dim the sky.
export function starField({ count = 6000, radius = 900, seed = 7, size = 1.0, band = 0.0 } = {}) {
  const r = rng(seed);
  const pos = new Float32Array(count * 3);
  const col = new Float32Array(count * 3);
  const siz = new Float32Array(count);
  const ph = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    let x, y, z;
    // optional concentration towards a galactic band (y ~ 0 plane)
    do {
      x = gauss(r); y = gauss(r); z = gauss(r);
    } while (x * x + y * y + z * z < 1e-6);
    const l = Math.hypot(x, y, z);
    x /= l; y /= l; z /= l;
    if (band > 0 && r() < band) { y *= 0.12; const l2 = Math.hypot(x, y, z); x /= l2; y /= l2; z /= l2; }
    pos.set([x * radius, y * radius, z * radius], i * 3);
    const t = r();
    const c = t < 0.15 ? [1.0, 0.75, 0.55] : t < 0.35 ? [0.7, 0.8, 1.0] : t < 0.4 ? [1, 0.55, 0.45] : [1, 0.97, 0.92];
    col.set(c, i * 3);
    const m = Math.pow(r(), 6);
    siz[i] = (1.2 + m * 5.5) * size;
    ph[i] = r() * 6.283;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  g.setAttribute('phase', new THREE.BufferAttribute(ph, 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uFade: { value: 1 }, uPix: { value: 1 } },
    vertexShader: /* glsl */`
      attribute float size; attribute float phase; attribute vec3 color;
      uniform float uTime; uniform float uPix; varying vec3 vC; varying float vA;
      void main(){
        vec4 mv = modelViewMatrix * vec4(position,1.0);
        gl_Position = projectionMatrix * mv;
        float tw = 0.75 + 0.25*sin(uTime*1.7 + phase*3.0);
        gl_PointSize = size * uPix;
        vC = color; vA = tw;
      }`,
    fragmentShader: /* glsl */`
      uniform float uFade; varying vec3 vC; varying float vA;
      void main(){
        vec2 d = gl_PointCoord - 0.5; float r = length(d)*2.0;
        float a = smoothstep(1.0, 0.0, r); a = a*a;
        gl_FragColor = vec4(vC * a * vA * uFade, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const pts = new THREE.Points(g, mat);
  pts.frustumCulled = false;
  return pts;
}

// ---------- nebula sky ----------
// The fbm nebula is far too expensive to evaluate per pixel per frame in a
// software renderer, so it is baked once into an equirectangular texture.
export function nebulaSky({ renderer, radius = 1000, colA = [0.25, 0.1, 0.45], colB = [0.05, 0.25, 0.45], intensity = 0.55, seed = 0, band = 1.0, res = 2048 } = {}) {
  const rt = new THREE.WebGLRenderTarget(res, res / 2, { colorSpace: THREE.SRGBColorSpace });
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uA: { value: new THREE.Vector3(...colA) }, uB: { value: new THREE.Vector3(...colB) },
      uI: { value: intensity }, uSeed: { value: seed }, uBand: { value: band },
    },
    vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0);} `,
    fragmentShader: NOISE_GLSL + /* glsl */`
      uniform vec3 uA, uB; uniform float uI, uSeed, uBand; varying vec2 vUv;
      void main(){
        float lon = (vUv.x - 0.5) * 6.2831853; float lat = (vUv.y - 0.5) * 3.14159265;
        // match THREE.SphereGeometry's uv layout
        vec3 d = vec3(-cos(lon)*cos(lat), sin(lat), sin(lon)*cos(lat));
        vec3 p = d*2.2 + uSeed;
        float n = fbm(p);
        float m = fbm(p*1.7 - 3.1);
        float band = mix(1.0, exp(-pow(d.y*3.0 + 0.4*n, 2.0)), uBand);
        float dd = smoothstep(-0.15, 0.6, n) * (0.35 + 0.65*band);
        vec3 c = mix(uA, uB, smoothstep(-0.3, 0.4, m)) * dd * uI;
        c += vec3(0.02,0.025,0.05) * band * uI;
        float dust = smoothstep(0.1, 0.5, fbm(p*3.0 + 7.0));
        c *= 1.0 - 0.6*dust*band;
        gl_FragColor = vec4(c, 1.0);
      }`,
    depthTest: false, depthWrite: false,
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat);
  const sc = new THREE.Scene();
  sc.add(quad);
  const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const prev = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  renderer.render(sc, cam);
  renderer.setRenderTarget(prev);
  mat.dispose();
  const skyMat = new THREE.MeshBasicMaterial({ map: rt.texture, side: THREE.BackSide, depthWrite: false, transparent: true, opacity: 1 });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 64, 32), skyMat);
  mesh.renderOrder = -10;
  return mesh;
}

// ---------- particle human figure ----------
// Points sampled on a capsule-built human silhouette. Used as "you".
export function humanFigure({ count = 9000, seed = 3, color = [0.45, 0.8, 1.0] } = {}) {
  const r = rng(seed);
  // parts: [type, params, weight]
  const parts = [
    ['sphere', [0, 1.62, 0, 0.12], 0.07],                 // head
    ['caps', [0, 1.47, 0, 0, 1.43, 0, 0.05], 0.015],      // neck
    ['caps', [0, 1.36, 0, 0, 1.0, 0, 0.17], 0.22],        // chest/torso
    ['caps', [0, 1.02, 0, 0, 0.88, 0, 0.15], 0.07],       // hips
    ['caps', [-0.22, 1.36, 0, -0.29, 1.08, 0.02, 0.05], 0.05], // upper arm L
    ['caps', [-0.29, 1.08, 0.02, -0.31, 0.82, 0.06, 0.042], 0.045],
    ['caps', [0.22, 1.36, 0, 0.29, 1.08, 0.02, 0.05], 0.05],
    ['caps', [0.29, 1.08, 0.02, 0.31, 0.82, 0.06, 0.042], 0.045],
    ['caps', [-0.09, 0.86, 0, -0.11, 0.47, 0.01, 0.075], 0.09], // thigh L
    ['caps', [-0.11, 0.47, 0.01, -0.12, 0.06, -0.01, 0.055], 0.07],
    ['caps', [0.09, 0.86, 0, 0.11, 0.47, 0.01, 0.075], 0.09],
    ['caps', [0.11, 0.47, 0.01, 0.12, 0.06, -0.01, 0.055], 0.07],
  ];
  const tot = parts.reduce((s, p) => s + p[2], 0);
  const pos = new Float32Array(count * 3);
  const rnd = new Float32Array(count);
  let k = 0;
  for (const [type, p, w] of parts) {
    const n = Math.round((w / tot) * count);
    for (let i = 0; i < n && k < count; i++, k++) {
      let x, y, z;
      const dx = gauss(r), dy = gauss(r), dz = gauss(r);
      const l = Math.hypot(dx, dy, dz) || 1;
      const shell = 0.85 + 0.15 * r();
      if (type === 'sphere') {
        x = p[0] + (dx / l) * p[3] * shell; y = p[1] + (dy / l) * p[3] * 1.15 * shell; z = p[2] + (dz / l) * p[3] * shell;
      } else {
        const t = r();
        x = lerp(p[0], p[3], t) + (dx / l) * p[6] * shell;
        y = lerp(p[1], p[4], t) + (dy / l) * p[6] * shell * 0.6;
        z = lerp(p[2], p[5], t) + (dz / l) * p[6] * shell * 0.8;
      }
      pos.set([x, y - 0.85, z], k * 3);
      rnd[k] = r();
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos.slice(0, k * 3), 3));
  g.setAttribute('rnd', new THREE.BufferAttribute(rnd.slice(0, k), 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }, uColor: { value: new THREE.Vector3(...color) },
      uPulse: { value: 0 }, uAlpha: { value: 1 }, uPix: { value: 1 }, uScatter: { value: 0 },
    },
    vertexShader: /* glsl */`
      attribute float rnd; uniform float uTime, uPulse, uPix, uScatter; varying float vR;
      void main(){
        vec3 p = position;
        float a = rnd*6.283 + uTime*0.6;
        p += 0.006*vec3(sin(a), cos(a*1.3), sin(a*0.7));
        vec3 dir = normalize(p - vec3(0.0, 0.4, 0.0) + 0.001);
        p += dir * uScatter * (0.5 + rnd) ;
        p *= 1.0 + 0.02*uPulse;
        vec4 mv = modelViewMatrix*vec4(p,1.0);
        gl_Position = projectionMatrix*mv;
        gl_PointSize = (2.0 + 2.0*rnd) * uPix * (6.0 / -mv.z);
        vR = rnd;
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColor; uniform float uPulse, uAlpha; varying float vR;
      void main(){
        float r = length(gl_PointCoord-0.5)*2.0; float a = smoothstep(1.0,0.0,r);
        vec3 c = mix(uColor, vec3(1.0), 0.25*vR + 0.35*uPulse);
        gl_FragColor = vec4(c*a*(0.55+0.45*uPulse)*uAlpha, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const pts = new THREE.Points(g, mat);
  pts.frustumCulled = false;
  return pts;
}

// Expanding pulse ring (heartbeat)
export function pulseRing(color = 0x66ccff) {
  const m = new THREE.MeshBasicMaterial({
    map: glowTexture('ring'), color, transparent: true, opacity: 0,
    blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
  });
  return new THREE.Mesh(new THREE.PlaneGeometry(1, 1), m);
}

// heartbeat envelope: two beats ("lub-dub") per period
export function heartbeat(t, period = 1.0) {
  const p = (t % period) / period;
  const b1 = Math.exp(-Math.pow((p - 0.05) / 0.035, 2));
  const b2 = 0.6 * Math.exp(-Math.pow((p - 0.2) / 0.035, 2));
  return b1 + b2;
}

// ---------- baked noise atlas ----------
// Equirectangular RGBA texture of fbm noise evaluated on the unit sphere.
// R: continent-scale fbm, G: fine detail, B: clouds, A: city-light speckle.
const atlasCache = {};
export function noiseAtlas(renderer, { res = 2048, seed = 0 } = {}) {
  const key = res + ':' + seed;
  if (atlasCache[key]) return atlasCache[key];
  const rt = new THREE.WebGLRenderTarget(res, res / 2, { wrapS: THREE.RepeatWrapping });
  rt.texture.wrapS = THREE.RepeatWrapping;
  const mat = new THREE.ShaderMaterial({
    uniforms: { uSeed: { value: seed } },
    vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0);} `,
    fragmentShader: NOISE_GLSL + /* glsl */`
      uniform float uSeed; varying vec2 vUv;
      void main(){
        float lon = (vUv.x - 0.5) * 6.2831853; float lat = (vUv.y - 0.5) * 3.14159265;
        vec3 d = vec3(-cos(lon)*cos(lat), sin(lat), sin(lon)*cos(lat));
        float r = fbm(d*2.2 + uSeed) * 0.5 + 0.5;
        float g = fbm(d*7.0 + 3.3 + uSeed) * 0.5 + 0.5;
        vec3 q = d*3.0 + vec3(fbm(d*2.0+9.0), fbm(d*2.0+19.0), 0.0)*1.5;
        float b = fbm(q + 5.0) * 0.5 + 0.5;
        float a = smoothstep(0.58, 0.85, gnoise(d*170.0)*0.5 + 0.5 + 0.12*gnoise(d*40.0));
        a *= smoothstep(0.42, 0.7, gnoise(d*12.0)*0.5 + 0.5 + 0.15);
        gl_FragColor = vec4(r, g, b, a);
      }`,
  });
  const sc = new THREE.Scene();
  sc.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat));
  const prev = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  renderer.render(sc, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1));
  renderer.setRenderTarget(prev);
  mat.dispose();
  atlasCache[key] = rt.texture;
  return rt.texture;
}

// ---------- text sprite ----------
export function textSprite(lines, { size = 0.5, color = '#ffffff', sub = '#9fd8ff', weight = 700 } = {}) {
  const c = document.createElement('canvas');
  const g = c.getContext('2d');
  const fs = 64;
  c.width = 1024; c.height = 64 + lines.length * 84;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  lines.forEach((l, i) => {
    g.font = `${i === 0 ? weight : 500} ${i === 0 ? fs : fs * 0.6}px Inter`;
    g.letterSpacing = i === 0 ? '3px' : '8px';
    g.shadowColor = i === 0 ? color : sub;
    g.shadowBlur = 18;
    g.fillStyle = i === 0 ? color : sub;
    g.fillText(l, c.width / 2, 50 + i * 84);
  });
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, depthTest: false });
  const s = new THREE.Sprite(m);
  s.scale.set(size * c.width / c.height, size, 1);
  s.renderOrder = 10;
  return s;
}

// direction from latitude / longitude in degrees (y up)
export function dirLL(lat, lon) {
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  return new THREE.Vector3(Math.cos(la) * Math.cos(lo), Math.sin(la), -Math.cos(la) * Math.sin(lo));
}

// soft-edged point sprite material helper: per-vertex color + size, additive
export function pointsMaterial({ sizeScale = 1, attenuate = true, opacity = 1 } = {}) {
  return new THREE.ShaderMaterial({
    uniforms: { uSize: { value: sizeScale }, uAlpha: { value: opacity }, uTint: { value: new THREE.Vector3(1, 1, 1) } },
    vertexShader: /* glsl */`
      attribute float size; attribute vec3 color; varying vec3 vC;
      uniform float uSize;
      void main(){
        vec4 mv = modelViewMatrix*vec4(position,1.0);
        gl_Position = projectionMatrix*mv;
        gl_PointSize = ${attenuate ? 'size * uSize * (300.0 / -mv.z)' : 'size * uSize'};
        gl_PointSize = max(gl_PointSize, 1.0);
        vC = color;
      }`,
    fragmentShader: /* glsl */`
      uniform float uAlpha; uniform vec3 uTint; varying vec3 vC;
      void main(){
        float r = length(gl_PointCoord-0.5)*2.0; float a = smoothstep(1.0,0.0,r); a*=a;
        gl_FragColor = vec4(vC*uTint*a*uAlpha, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
}
