// Particle spiral / elliptical galaxy with differential rotation done in the
// vertex shader. uRot is the rotation angle (radians) at radius uRref.
import { THREE, rng, gauss } from './lib.js';

export function makeGalaxy({
  count = 90000, radius = 10, arms = 4, pitch = 18, seed = 1, bulge = 0.18, thickness = 0.12,
  armTight = 0.75, elliptical = 0, pix = 1, size = 1, diff = 0.12, armColor = [0.62, 0.75, 1.0], coreColor = [1.0, 0.82, 0.55], knots = 400,
} = {}) {
  const r = rng(seed);
  const N = count + knots;
  const aR = new Float32Array(N), aT = new Float32Array(N), aY = new Float32Array(N);
  const col = new Float32Array(N * 3), siz = new Float32Array(N), red = new Float32Array(N);
  const tanP = Math.tan(pitch * Math.PI / 180);
  for (let i = 0; i < N; i++) {
    let rad, th, y, c, s, rd;
    const knot = i >= count;
    if (!knot && r() < bulge + elliptical) {
      // bulge / elliptical component (with a short bar)
      const sc = elliptical > 0 ? radius * 0.45 : radius * 0.13;
      let x = gauss(r) * sc * 1.6, z = gauss(r) * sc * 0.9;
      y = gauss(r) * sc * (elliptical > 0 ? 0.75 : 0.6);
      rad = Math.hypot(x, z); th = Math.atan2(z, x);
      const w = Math.min(1, rad / (radius * 0.5));
      c = coreColor.map((v, k) => v * (1 - 0.25 * w) + armColor[k] * 0.25 * w);
      s = 0.8 + r() * 1.4; rd = 0.6 + 0.4 * r();
    } else {
      rad = -Math.log(1 - r() * 0.985) * radius * 0.3 + radius * 0.06;
      if (rad > radius * 1.25) rad = radius * (0.2 + r());
      const arm = Math.floor(r() * arms);
      const base = arm * (2 * Math.PI / arms) + Math.log(rad / (radius * 0.12)) / tanP;
      const inArm = knot || r() < armTight;
      const spread = inArm ? 0.18 + 0.1 * r() : Math.PI;
      th = base + gauss(r) * spread * (inArm ? 1 : 0.6);
      y = gauss(r) * thickness * (1 - 0.5 * Math.min(1, rad / radius)) * radius * 0.1;
      const young = inArm ? 1 : 0.35;
      c = armColor.map((v, k) => v * young + coreColor[k] * (1 - young) * 0.8);
      s = 0.6 + Math.pow(r(), 3) * 2.2;
      rd = r();
      if (knot) { c = [1.0, 0.45, 0.7]; s = 3 + r() * 4; rd = 2; }
    }
    aR[i] = rad; aT[i] = th; aY[i] = y;
    col.set(c, i * 3); siz[i] = s * size; red[i] = rd;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
  g.setAttribute('aR', new THREE.BufferAttribute(aR, 1));
  g.setAttribute('aT', new THREE.BufferAttribute(aT, 1));
  g.setAttribute('aY', new THREE.BufferAttribute(aY, 1));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  g.setAttribute('red', new THREE.BufferAttribute(red, 1));
  const uniforms = {
    uRot: { value: 0 }, uRref: { value: radius * 0.55 }, uDiff: { value: diff },
    uSize: { value: 0.07 * pix }, uAlpha: { value: 1 }, uAge: { value: 0 }, uKnots: { value: 1 },
    uRmin: { value: radius * 0.15 },
  };
  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: /* glsl */`
      attribute float aR, aT, aY, size, red; attribute vec3 color;
      uniform float uRot, uRref, uDiff, uSize, uAge, uKnots, uRmin;
      varying vec3 vC; varying float vA;
      void main(){
        float w = 1.0 + uDiff * (uRref / max(aR, uRmin) - 1.0);
        float th = aT + uRot * w;
        vec3 p = vec3(cos(th) * aR, aY, sin(th) * aR);
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        // ageing: blue stars die first, survivors redden
        vec3 oldC = vec3(1.0, 0.45, 0.22) * (0.55 + 0.45 * red);
        float dies = smoothstep(red - 0.15, red + 0.15, uAge * 1.15);
        vec3 c = mix(color, oldC, smoothstep(0.0, 0.8, uAge));
        float a = 1.0 - 0.75 * dies;
        if (red > 1.5) a = uKnots;
        vC = c; vA = a;
        gl_PointSize = max(1.0, size * uSize * (300.0 / -mv.z));
      }`,
    fragmentShader: /* glsl */`
      uniform float uAlpha; varying vec3 vC; varying float vA;
      void main(){
        float r = length(gl_PointCoord - 0.5) * 2.0; float a = smoothstep(1.0, 0.0, r); a *= a;
        gl_FragColor = vec4(vC * a * vA * uAlpha, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const points = new THREE.Points(g, mat);
  points.frustumCulled = false;
  return { points, uniforms };
}
