// Chapter 10 — the great darkness: accelerating expansion carries every other
// galaxy beyond the cosmic horizon until only our Local Group is left.
import { THREE, starField, sprite, smooth, ease, rng, gauss } from '../lib.js';
import { makeGalaxy } from '../galaxyfx.js';

function galaxyAtlas() {
  const S = 128, c = document.createElement('canvas');
  c.width = S * 4; c.height = S * 2;
  const g = c.getContext('2d');
  const r = rng(5);
  for (let v = 0; v < 8; v++) {
    const ox = (v % 4) * S + S / 2, oy = Math.floor(v / 4) * S + S / 2;
    const core = g.createRadialGradient(ox, oy, 0, ox, oy, S * 0.45);
    core.addColorStop(0, 'rgba(255,245,225,1)');
    core.addColorStop(v < 6 ? 0.12 : 0.35, 'rgba(255,225,190,0.55)');
    core.addColorStop(1, 'rgba(255,220,190,0)');
    g.fillStyle = core;
    g.beginPath(); g.arc(ox, oy, S * 0.48, 0, Math.PI * 2); g.fill();
    if (v < 6) {
      const arms = v % 3 === 0 ? 2 : v % 3 === 1 ? 3 : 4;
      for (let i = 0; i < 900; i++) {
        const t = Math.pow(r(), 0.8);
        const arm = Math.floor(r() * arms);
        const ang = arm * Math.PI * 2 / arms + t * 4.2 + gauss(r) * 0.25;
        const rad = t * S * 0.44;
        const x = ox + Math.cos(ang) * rad, y = oy + Math.sin(ang) * rad;
        g.fillStyle = r() < 0.15 ? 'rgba(255,170,210,0.55)' : `rgba(170,200,255,${0.25 + 0.4 * (1 - t)})`;
        g.fillRect(x, y, 1.6, 1.6);
      }
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export default function horizon(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, ctx.aspect, 0.05, 8000);
  const bg = starField({ count: 5000, seed: 111, size: ctx.pix * 0.8 });
  scene.add(bg);

  // cosmic web in comoving coordinates (unit sphere)
  const r = rng(77);
  const nodes = [];
  while (nodes.length < 46) {
    const p = new THREE.Vector3(r() * 2 - 1, r() * 2 - 1, r() * 2 - 1);
    if (p.length() < 1 && p.length() > 0.12) nodes.push(p);
  }
  const fil = [];
  nodes.forEach((a, i) => {
    const ds = nodes.map((b, j) => [a.distanceTo(b), j]).filter(([, j]) => j !== i).sort((x, y) => x[0] - y[0]);
    for (let k = 0; k < 3; k++) if (i < ds[k][1]) fil.push([a, nodes[ds[k][1]]]);
  });
  const NG = 2600;
  const p0 = new Float32Array(NG * 3), col = new Float32Array(NG * 3), siz = new Float32Array(NG), ang = new Float32Array(NG), vari = new Float32Array(NG);
  for (let i = 0; i < NG; i++) {
    let p;
    if (r() < 0.2) { const n = nodes[Math.floor(r() * nodes.length)]; p = n.clone().add(new THREE.Vector3(gauss(r), gauss(r), gauss(r)).multiplyScalar(0.035)); }
    else { const [a, b] = fil[Math.floor(r() * fil.length)]; p = a.clone().lerp(b, r()).add(new THREE.Vector3(gauss(r), gauss(r), gauss(r)).multiplyScalar(0.02)); }
    if (p.length() < 0.1) p.setLength(0.1 + r() * 0.05);
    p0.set(p.toArray(), i * 3);
    const warm = r();
    col.set([0.85 + 0.15 * warm, 0.85, 1.0 - 0.25 * warm], i * 3);
    siz[i] = 0.5 + Math.pow(r(), 3) * 2.5;
    ang[i] = r() * Math.PI * 2;
    vari[i] = Math.floor(r() * 8);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(p0, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  geo.setAttribute('ang', new THREE.BufferAttribute(ang, 1));
  geo.setAttribute('vari', new THREE.BufferAttribute(vari, 1));
  const gu = { uA: { value: 1 }, uS: { value: 60 }, uRH: { value: 120 }, uMap: { value: galaxyAtlas() }, uPix: { value: ctx.pix } };
  const gm = new THREE.ShaderMaterial({
    uniforms: gu,
    vertexShader: /* glsl */`
      attribute float size, ang, vari; attribute vec3 color;
      uniform float uA, uS, uRH, uPix; varying vec3 vC; varying float vAng, vVar, vF;
      void main(){
        vec3 p = position * uS * uA;
        float d = length(p);
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        float red = smoothstep(0.35, 1.0, d / uRH);
        vC = mix(color, vec3(1.0, 0.25, 0.1), red);
        vF = 1.0 - smoothstep(0.7, 1.0, d / uRH);
        gl_PointSize = min(64.0, size * 30.0 * uPix * (60.0 / -mv.z));
        vAng = ang; vVar = vari;
      }`,
    fragmentShader: /* glsl */`
      uniform sampler2D uMap; varying vec3 vC; varying float vAng, vVar, vF;
      void main(){
        vec2 q = gl_PointCoord - 0.5;
        float c = cos(vAng), s = sin(vAng);
        q = vec2(c*q.x - s*q.y, (s*q.x + c*q.y) * 1.8);   // tilt into an ellipse
        if (abs(q.x) > 0.5 || abs(q.y) > 0.5) discard;
        vec2 uv = (vec2(mod(vVar, 4.0), floor(vVar / 4.0)) + q + 0.5) / vec2(4.0, 2.0);
        vec4 t = texture2D(uMap, vec2(uv.x, 1.0 - uv.y));
        gl_FragColor = vec4(t.rgb * vC * t.a * vF * 0.55, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const gals = new THREE.Points(geo, gm);
  gals.frustumCulled = false;
  scene.add(gals);

  // our Local Group stays bound
  const home = makeGalaxy({ count: 30000, radius: 2.2, seed: 8, pix: ctx.pix, knots: 120 });
  home.uniforms.uSize.value = 0.05 * ctx.pix;
  home.points.rotation.x = 0.35;
  scene.add(home.points);
  const homeCore = sprite(0xffe2b0, 2.2, 'soft', 0.6);
  scene.add(homeCore);
  const neighbours = [[5, 1.2, -3, 1.6], [-4, -1.5, 4.5, 1.1], [2.5, 2.5, 6, 0.8]].map(([x, y, z, s]) => {
    const n = sprite(0xd8e4ff, s * 2.2, 'soft', 0.45);
    const c = sprite(0xffffff, s * 0.5, 'core', 0.7);
    n.position.set(x, y, z); c.position.set(x, y, z);
    scene.add(n, c);
    return { n, c, base: new THREE.Vector3(x, y, z) };
  });

  function update(t, dur) {
    bg.material.uniforms.uTime.value = t;
    // scale factor: gentle at first, then runaway expansion
    const a = Math.exp(0.0021 * Math.max(t, 0) * Math.max(t, 0)) * (1 + 0.01 * t);
    gu.uA.value = a;
    bg.material.uniforms.uFade.value = 1 - smooth(info.cue(2), info.cue(4) + 2, t);
    home.uniforms.uRot.value = -t * 0.05;
    neighbours.forEach((o, i) => {
      o.n.position.copy(o.base).applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.02 * t * (i + 1));
      o.c.position.copy(o.n.position);
    });

    // camera: from deep in the web towards home, as the sky empties
    const p = ease(smooth(0, dur, t));
    const ang0 = 0.4 + t * 0.02;
    const dist = 48 - 38 * p;
    camera.position.set(Math.sin(ang0) * dist, dist * 0.35, Math.cos(ang0) * dist);
    camera.lookAt(0, 0, 0);
  }
  return { scene, camera, update };
}
