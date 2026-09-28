import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// ---------- math helpers ----------
export function rng(seed) {
  let s = seed | 0;
  return () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (e0, e1, x) => {
  const t = clamp((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};
export const easeInOut = (t) => {
  t = clamp(t);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};
export const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
export const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
export const lerpV = (a, b, t) => new THREE.Vector3().lerpVectors(a, b, t);

// Catmull-Rom through key points, parameter 0..1
export function pathAt(points, t) {
  const c = new THREE.CatmullRomCurve3(points, false, 'centripetal');
  return c.getPoint(clamp(t));
}

// ---------- materials ----------
const matCache = new Map();
export function M(color, o = {}) {
  const key = color + JSON.stringify(o);
  if (matCache.has(key)) return matCache.get(key);
  const m = new THREE.MeshStandardMaterial({
    color,
    roughness: o.rough ?? 0.75,
    metalness: o.metal ?? 0,
    flatShading: o.flat ?? false,
    emissive: o.emissive ?? 0x000000,
    emissiveIntensity: o.ei ?? 1,
    transparent: o.opacity !== undefined,
    opacity: o.opacity ?? 1,
    side: o.side ?? THREE.FrontSide,
    vertexColors: o.vc ?? false,
    depthWrite: o.depthWrite ?? true,
  });
  matCache.set(key, m);
  return m;
}

const GLSL_NOISE = /* glsl */ `
float h21(vec2 p){ p = fract(p*vec2(123.34, 456.21)); p += dot(p, p+45.32); return fract(p.x*p.y); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h21(i),h21(i+vec2(1,0)),f.x), mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x), f.y); }
float fbm(vec2 p){ float s=0., a=.5; for(int i=0;i<3;i++){ s+=a*vnoise(p); p=p*2.03+17.1; a*=.5;} return s*1.14; }
`;

export function patchWorld(mat, key, uniforms, fragBody) {
  mat.customProgramCacheKey = () => key;
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, uniforms);
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWPos;\nvarying vec3 vWNrm;')
      .replace(
        '#include <project_vertex>',
        `#include <project_vertex>
        {
          vec4 wp4 = vec4(transformed, 1.0);
          vec3 wn = objectNormal;
          #ifdef USE_INSTANCING
            wp4 = instanceMatrix * wp4;
            wn = mat3(instanceMatrix) * wn;
          #endif
          wp4 = modelMatrix * wp4;
          vWPos = wp4.xyz;
          vWNrm = normalize(mat3(modelMatrix) * wn);
        }`
      );
    const decl = Object.keys(uniforms)
      .map((k) => {
        const v = uniforms[k].value;
        const type = typeof v === 'number' ? 'float' : v.isVector2 ? 'vec2' : v.isColor ? 'vec3' : 'vec3';
        return `uniform ${type} ${k};`;
      })
      .join('\n');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>\nvarying vec3 vWPos;\nvarying vec3 vWNrm;\n${decl}\n${GLSL_NOISE}`)
      .replace('#include <color_fragment>', `#include <color_fragment>\n${fragBody}`);
  };
  return mat;
}

// Procedural sandstone blocks, projected in world space. Works on any geometry.
export function stoneMat(color = 0x9c8f7a, o = {}) {
  const m = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.92,
    metalness: 0,
    flatShading: o.flat ?? false,
    vertexColors: o.vc ?? false,
  });
  const uniforms = {
    uBlock: { value: new THREE.Vector2(o.bw ?? 1.1, o.bh ?? 0.5) },
    uMoss: { value: o.moss ?? 0.35 },
    uGround: { value: o.ground ?? 0.3 },
    uMossCol: { value: new THREE.Color(o.mossColor ?? 0x6f8a4a) },
  };
  return patchWorld(
    m,
    'stone' + (o.vc ? 'vc' : '') + (o.flat ? 'f' : ''),
    uniforms,
    /* glsl */ `
    {
      vec3 an = abs(normalize(vWNrm));
      vec2 uv = an.y > max(an.x, an.z) ? vWPos.xz : (an.x > an.z ? vWPos.zy : vWPos.xy);
      vec2 b = uv / uBlock;
      float row = floor(b.y);
      b.x += mod(row, 2.0) * 0.5;
      vec2 id = floor(b); vec2 f = fract(b);
      float edge = min(min(f.x, 1.0 - f.x) * uBlock.x, min(f.y, 1.0 - f.y) * uBlock.y);
      float mortar = smoothstep(0.0, 0.035, edge);
      float tint = 0.86 + 0.24 * h21(id + 3.7);
      float grime = fbm(uv * 0.45 + vWPos.y * 0.05);
      vec3 col = diffuseColor.rgb * tint * mix(0.62, 1.0, mortar);
      col *= mix(0.72, 1.12, grime);
      float streak = vnoise(vec2(uv.x * 2.0, vWPos.y * 0.15));
      col *= mix(1.0, 0.82, smoothstep(0.55, 0.85, streak) * (1.0 - an.y));
      float moss = uMoss * smoothstep(0.5, 0.78, fbm(uv * 0.3 + 11.0));
      moss += uMoss * 0.8 * (1.0 - smoothstep(0.0, 1.6, vWPos.y - uGround));
      col = mix(col, uMossCol * (0.7 + 0.5 * grime), clamp(moss, 0.0, 0.85));
      col *= mix(0.55, 1.0, smoothstep(0.0, 2.2, vWPos.y - uGround));
      diffuseColor.rgb = col;
    }`
  );
}

// Grass / earth ground with world-space colour variation
export function groundMat(o = {}) {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, metalness: 0 });
  const uniforms = {
    uA: { value: new THREE.Color(o.a ?? 0x5f9a3a) },
    uB: { value: new THREE.Color(o.b ?? 0x8dbb4a) },
    uC: { value: new THREE.Color(o.c ?? 0x6b7f35) },
    uScale: { value: o.scale ?? 0.05 },
  };
  return patchWorld(
    m,
    'ground' + (o.key ?? ''),
    uniforms,
    /* glsl */ `
    {
      vec2 p = vWPos.xz * uScale;
      float n = fbm(p);
      float n2 = vnoise(p * 6.0 + 3.0);
      vec3 col = mix(uA, uB, smoothstep(0.3, 0.7, n));
      col = mix(col, uC, smoothstep(0.55, 0.75, n2) * 0.6);
      col *= 0.85 + 0.3 * vnoise(vWPos.xz * 3.0);
      diffuseColor.rgb *= col;
    }`
  );
}

// Pale tree bark / roots with vertical streaks and mossy tops
export function barkMat(color = 0xb0a28a) {
  const m = new THREE.MeshStandardMaterial({ color, roughness: 0.88, metalness: 0 });
  return patchWorld(
    m,
    'bark',
    { uMoss: { value: new THREE.Color(0x6a8a45) } },
    /* glsl */ `
    {
      float a = fbm(vec2((vWPos.x + vWPos.z) * 2.2, vWPos.y * 0.35));
      float b = vnoise(vWPos.xz * 3.0 + vWPos.y * 1.7);
      vec3 col = diffuseColor.rgb * (0.78 + 0.35 * a) * (0.92 + 0.12 * b);
      float up = smoothstep(0.35, 0.9, normalize(vWNrm).y);
      float moss = up * smoothstep(0.45, 0.7, fbm(vWPos.xz * 0.8 + 5.0));
      col = mix(col, uMoss * (0.8 + 0.4 * a), moss * 0.75);
      col *= mix(0.6, 1.0, smoothstep(0.0, 1.5, vWPos.y - 0.3));
      diffuseColor.rgb = col;
    }`
  );
}

export function softDotTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.6)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g;
  x.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------- geometry helpers ----------
const KEEP = new Set(['position', 'normal']);
export function prep(geo, color, matrix) {
  let g = geo.index ? geo.toNonIndexed() : geo.clone();
  for (const k of Object.keys(g.attributes)) if (!KEEP.has(k)) g.deleteAttribute(k);
  if (!g.attributes.normal) g.computeVertexNormals();
  if (matrix) g.applyMatrix4(matrix);
  const c = new THREE.Color(color);
  const n = g.attributes.position.count;
  const arr = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    arr[i * 3] = c.r;
    arr[i * 3 + 1] = c.g;
    arr[i * 3 + 2] = c.b;
  }
  g.setAttribute('color', new THREE.BufferAttribute(arr, 3));
  return g;
}
export function merge(list) {
  return mergeGeometries(list, false);
}
export function mtx(pos = [0, 0, 0], rot = [0, 0, 0], scl = [1, 1, 1]) {
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(rot[0], rot[1], rot[2]));
  const s = typeof scl === 'number' ? new THREE.Vector3(scl, scl, scl) : new THREE.Vector3(...scl);
  m.compose(new THREE.Vector3(...pos), q, s);
  return m;
}

export function mesh(geo, mat, pos, rot, scl) {
  const m = new THREE.Mesh(geo, mat);
  if (pos) m.position.set(...pos);
  if (rot) m.rotation.set(...rot);
  if (scl !== undefined) typeof scl === 'number' ? m.scale.setScalar(scl) : m.scale.set(...scl);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

export function box(w, h, d, mat, pos, rot) {
  return mesh(new THREE.BoxGeometry(w, h, d), mat, pos, rot);
}

// Triangular prism roof along X, base width w, height h
export function roofGeo(len, w, h, tiers = 2) {
  const parts = [];
  for (let i = 0; i < tiers; i++) {
    const s = 1 - i * 0.28;
    const shape = new THREE.Shape();
    shape.moveTo(-w * 0.5 * s, 0);
    shape.lineTo(w * 0.5 * s, 0);
    shape.lineTo(0, h * s);
    shape.lineTo(-w * 0.5 * s, 0);
    const g = new THREE.ExtrudeGeometry(shape, { depth: len * (1 - i * 0.04), bevelEnabled: false });
    g.translate(0, i * h * 0.55, -len * (1 - i * 0.04) * 0.5);
    g.rotateY(Math.PI / 2);
    parts.push(prep(g, 0xffffff));
  }
  return merge(parts);
}

// Khmer lotus-bud tower (lathe), height h, base radius r
export function lotusTowerGeo(h, r, o = {}) {
  const pts = [];
  const tiers = o.tiers ?? 9;
  const trunc = o.trunc ?? 1;
  pts.push(new THREE.Vector2(0.0001, 0));
  pts.push(new THREE.Vector2(r * 1.12, 0));
  pts.push(new THREE.Vector2(r * 1.12, h * 0.04));
  pts.push(new THREE.Vector2(r * 1.0, h * 0.05));
  pts.push(new THREE.Vector2(r * 1.0, h * 0.2));
  pts.push(new THREE.Vector2(r * 1.1, h * 0.21));
  pts.push(new THREE.Vector2(r * 1.1, h * 0.25));
  const start = 0.25;
  const profile = (u) => {
    // bud: slight bulge then taper to a point
    const bulge = Math.sin(Math.min(1, u * 1.6) * Math.PI * 0.5) * 0.08;
    return r * (1.02 + bulge) * Math.pow(1 - u, 0.75);
  };
  for (let i = 0; i < tiers; i++) {
    const u0 = i / tiers;
    const u1 = (i + 1) / tiers;
    if (u0 > trunc) break;
    const y0 = h * (start + (1 - start) * u0);
    const y1 = h * (start + (1 - start) * Math.min(u1, trunc));
    const r0 = profile(u0);
    const r1 = profile(Math.min(u1, trunc));
    pts.push(new THREE.Vector2(r0 * 0.9, y0));
    pts.push(new THREE.Vector2(r0 * 1.02, y0 + (y1 - y0) * 0.18));
    pts.push(new THREE.Vector2(r1 * 1.05, y1 - (y1 - y0) * 0.1));
    pts.push(new THREE.Vector2(r1 * 0.88, y1));
  }
  if (trunc >= 1) {
    pts.push(new THREE.Vector2(r * 0.07, h * 1.0));
    pts.push(new THREE.Vector2(r * 0.03, h * 1.06));
    pts.push(new THREE.Vector2(0.0001, h * 1.07));
  } else {
    const yTop = h * (start + (1 - start) * trunc);
    pts.push(new THREE.Vector2(0.0001, yTop));
  }
  const g = new THREE.LatheGeometry(pts, o.segments ?? 8);
  g.rotateY(Math.PI / 8);
  return g;
}

export function stairsGeo(width, height, depth, n) {
  const parts = [];
  for (let i = 0; i < n; i++) {
    const sh = height / n;
    const sd = depth / n;
    const g = new THREE.BoxGeometry(width, sh * (i + 1), sd);
    g.translate(0, (sh * (i + 1)) / 2, depth / 2 - sd * (i + 0.5));
    parts.push(prep(g, 0xffffff));
  }
  return merge(parts);
}

// ---------- canvas textures ----------
export function kramaTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const x = c.getContext('2d');
  x.fillStyle = '#f4f1ea';
  x.fillRect(0, 0, 128, 128);
  x.fillStyle = 'rgba(200,30,40,0.85)';
  for (let i = 0; i < 128; i += 32) {
    x.fillRect(i, 0, 16, 128);
    x.fillRect(0, i, 128, 16);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 1);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
