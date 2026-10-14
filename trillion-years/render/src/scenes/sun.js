// Chapter 9 — death of the Sun: red giant swallows the inner planets, then
// blows off a planetary nebula and leaves a white dwarf.
import { THREE, starField, nebulaSky, sprite, smooth, ease, rng, gauss, noiseAtlas, lerp } from '../lib.js';

export default function sun(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, ctx.aspect, 0.05, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, intensity: 0.2, seed: 21, colA: [0.3, 0.08, 0.1], colB: [0.1, 0.08, 0.25] }));
  const stars = starField({ count: 6000, seed: 101, size: ctx.pix });
  scene.add(stars);

  const su = {
    uNoise: { value: noiseAtlas(ctx.renderer) }, uTime: { value: 0 },
    uCol: { value: new THREE.Color(1, 0.85, 0.55) }, uTurb: { value: 0.5 },
  };
  const sunMat = new THREE.ShaderMaterial({
    uniforms: su,
    vertexShader: /* glsl */`
      varying vec3 vPos; varying vec3 vN; varying vec3 vW;
      void main(){ vPos = position; vN = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`,
    fragmentShader: /* glsl */`
      uniform sampler2D uNoise; uniform float uTime, uTurb; uniform vec3 uCol;
      varying vec3 vPos; varying vec3 vN; varying vec3 vW;
      vec4 nz(vec3 d, vec2 off){ float lon = atan(d.z, -d.x); float lat = asin(clamp(d.y,-1.0,1.0));
        return texture2D(uNoise, vec2(lon/6.2831853 + 0.5, lat/3.14159265 + 0.5) + off); }
      void main(){
        vec3 d = normalize(vPos);
        float a = nz(d, vec2(uTime*0.004, 0.0)).g;
        float b = nz(d.zyx, vec2(-uTime*0.006, 0.0)).g;
        float c = nz(d.yxz, vec2(uTime*0.002, 0.0)).r;
        float gran = (a + b) * 0.5 + (c - 0.5) * 0.6;
        vec3 V = normalize(cameraPosition - vW);
        float mu = max(dot(normalize(vN), V), 0.0);
        vec3 col = uCol * (0.7 + (gran - 0.5) * 2.2 * uTurb);
        col *= 0.35 + 0.75 * pow(mu, 0.45);
        col += uCol * pow(1.0 - mu, 3.0) * 0.6;
        gl_FragColor = vec4(col * 1.25, 1.0);
      }`,
  });
  const sunMesh = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 48), sunMat);
  scene.add(sunMesh);
  const corona = sprite(0xffc070, 4, 'soft', 0.7);
  const corona2 = sprite(0xff9040, 8, 'soft', 0.3);
  scene.add(corona, corona2);
  const light = new THREE.PointLight(0xffe0b0, 60, 0, 1.2);
  scene.add(light);
  scene.add(new THREE.AmbientLight(0x404050, 0.25));

  const planets = [
    { name: 'mercury', r: 2.2, size: 0.11, color: 0x9c8f86, speed: 0.30, ph: 0.4 },
    { name: 'venus', r: 3.2, size: 0.19, color: 0xe3c58d, speed: 0.20, ph: 2.1 },
    { name: 'earth', r: 4.4, size: 0.2, color: 0x3d78c8, speed: 0.14, ph: 4.0 },
    { name: 'mars', r: 6.0, size: 0.14, color: 0xc0583a, speed: 0.1, ph: 1.0 },
  ].map((p) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(p.size, 40, 20), new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.85, emissive: 0x000000 }));
    scene.add(m);
    const pts = [];
    for (let i = 0; i <= 200; i++) { const a = i / 200 * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(a) * p.r, 0, Math.sin(a) * p.r)); }
    const orbit = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0x6fa8ff, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending, depthWrite: false }));
    scene.add(orbit);
    return { ...p, m, orbit };
  });

  // planetary nebula shell
  const r = rng(33);
  const NN = 36000;
  const dir = new Float32Array(NN * 3), spd = new Float32Array(NN);
  const pos = new Float32Array(NN * 3), col = new Float32Array(NN * 3), siz = new Float32Array(NN);
  for (let i = 0; i < NN; i++) {
    let x = gauss(r), y = gauss(r), z = gauss(r);
    const l = Math.hypot(x, y, z); x /= l; y /= l; z /= l;
    // bipolar, clumpy shell
    const lobe = 1 + 0.6 * Math.abs(y);
    dir.set([x, y * 1.15, z], i * 3);
    spd[i] = lobe * (0.85 + 0.3 * r()) * (r() < 0.25 ? 0.7 : 1);
    const inner = r();
    const c = inner < 0.45 ? [0.25, 0.9, 0.85] : inner < 0.8 ? [1.0, 0.35, 0.45] : [0.6, 0.45, 1.0];
    col.set(c, i * 3);
    siz[i] = 0.8 + r() * 2.2;
  }
  const ng = new THREE.BufferGeometry();
  ng.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  ng.setAttribute('color', new THREE.BufferAttribute(col, 3));
  ng.setAttribute('size', new THREE.BufferAttribute(siz, 1));
  const nm = new THREE.ShaderMaterial({
    uniforms: { uSize: { value: 0.12 * ctx.pix }, uAlpha: { value: 0 } },
    vertexShader: /* glsl */`attribute float size; attribute vec3 color; uniform float uSize; varying vec3 vC;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); gl_Position = projectionMatrix*mv; gl_PointSize = max(1.0, size*uSize*(300.0/-mv.z)); vC = color; }`,
    fragmentShader: /* glsl */`uniform float uAlpha; varying vec3 vC;
      void main(){ float r = length(gl_PointCoord-0.5)*2.0; float a = smoothstep(1.0,0.0,r); a*=a; gl_FragColor = vec4(vC*a*uAlpha*0.5, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const nebula = new THREE.Points(ng, nm);
  nebula.frustumCulled = false;
  scene.add(nebula);
  // big soft clouds give the shell its glow
  const clouds = [];
  for (let i = 0; i < 260; i++) {
    let x = gauss(r), y = gauss(r), z = gauss(r);
    const l = Math.hypot(x, y, z); x /= l; y /= l; z /= l;
    const k = r();
    const c = k < 0.45 ? 0x30d0c0 : k < 0.8 ? 0xff4a6a : 0x8a60ff;
    const s = sprite(c, 1, 'soft', 0);
    s.userData = { d: new THREE.Vector3(x, y * 1.15, z), sp: (1 + 0.6 * Math.abs(y)) * (0.8 + 0.35 * r()), sz: 1.2 + r() * 2.2, op: 0.08 + r() * 0.1 };
    scene.add(s);
    clouds.push(s);
  }
  const wd = sprite(0xe8f0ff, 0.6, 'core', 0);
  const wdGlow = sprite(0x9fc0ff, 3.5, 'soft', 0);
  scene.add(wd, wdGlow);

  const cYellow = new THREE.Color(1, 0.86, 0.55), cOrange = new THREE.Color(1, 0.5, 0.18), cRed = new THREE.Color(0.95, 0.22, 0.07);
  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    su.uTime.value = t;
    const tBlow = info.cue(4) + 0.5;
    // radius over time
    const g1 = smooth(info.cue(1) + 2, info.cue(2) + 1.2, t);
    const g2 = smooth(info.cue(2) + 1.2, info.cue(3) - 0.2, t);
    const g3 = smooth(info.cue(3) + 1, info.cue(3) + 6, t);
    let R = 0.7 + 1.75 * g1 + 1.0 * g2 + 1.35 * g3 + 0.08 * Math.sin(t * 0.7) * g1;
    const blow = smooth(tBlow, tBlow + 3, t);
    const Rg = R;                 // giant radius before the collapse
    R *= 1 - 0.97 * blow;
    sunMesh.scale.setScalar(Math.max(R, 0.02));
    sunMesh.visible = R > 0.05;
    const col = cYellow.clone().lerp(cOrange, g1).lerp(cRed, Math.max(g2 * 0.6, g3));
    su.uCol.value.copy(col);
    su.uTurb.value = 0.45 + 0.4 * g1;
    corona.scale.setScalar(R * 3.6); corona.material.color.copy(col); corona.material.opacity = 0.7 * (1 - blow);
    corona2.scale.setScalar(R * 7); corona2.material.color.copy(col); corona2.material.opacity = 0.28 * (1 - blow);
    light.color.copy(col);
    light.intensity = 60 + 80 * g1 - 120 * blow;

    planets.forEach((p) => {
      const a = p.ph + t * p.speed;
      p.m.position.set(Math.cos(a) * p.r, 0, Math.sin(a) * p.r);
      const heat = smooth(p.r * 0.55, p.r - p.size, Rg);
      p.m.material.emissive.setRGB(heat * 0.9, heat * 0.25, heat * 0.05);
      if (p.name === 'earth') p.m.material.color.setRGB(0.24 * (1 - heat) + 0.35 * heat, 0.47 * (1 - heat) + 0.18 * heat, 0.78 * (1 - heat) + 0.1 * heat);
      p.m.visible = Rg < p.r - p.size * 0.3;
      p.orbit.material.opacity = 0.22 * (1 - smooth(p.r - 0.6, p.r, Rg));
    });

    // nebula
    const nk = Math.max(0, t - tBlow);
    const Rmax = 4.75;
    if (nk > 0) {
      const ex = Rmax + nk * 0.38;
      for (let i = 0; i < NN; i++) {
        const s = spd[i];
        pos[i * 3] = dir[i * 3] * ex * s;
        pos[i * 3 + 1] = dir[i * 3 + 1] * ex * s;
        pos[i * 3 + 2] = dir[i * 3 + 2] * ex * s;
      }
      ng.attributes.position.needsUpdate = true;
    }
    const na = smooth(tBlow, tBlow + 1.5, t) * (1 - 0.35 * smooth(tBlow + 8, dur + 2, t));
    nm.uniforms.uAlpha.value = 1.2 * na;
    const ex2 = Rmax + nk * 0.38;
    clouds.forEach((c) => {
      const u = c.userData;
      c.visible = nk > 0;
      c.position.copy(u.d).multiplyScalar(ex2 * u.sp);
      c.scale.setScalar(u.sz * (1 + nk * 0.12));
      c.material.opacity = u.op * na;
    });
    nebula.visible = nk > 0;
    wd.material.opacity = smooth(tBlow + 1.5, tBlow + 3.5, t);
    wdGlow.material.opacity = 0.55 * wd.material.opacity;
    wd.scale.setScalar(0.5 + 0.08 * Math.sin(t * 2));

    // camera
    const p = smooth(0, dur, t);
    const ang = 0.3 + p * 0.6;
    const dist = 10 + 6 * smooth(info.cue(1), info.cue(3) + 6, t) + 5 * smooth(tBlow, dur, t);
    camera.position.set(Math.sin(ang) * dist, dist * 0.38, Math.cos(ang) * dist);
    camera.lookAt(0, -0.6 + 0.6 * smooth(tBlow, dur, t), 0);
  }
  return { scene, camera, update };
}
