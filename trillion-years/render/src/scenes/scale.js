// Chapter 1 — how big is a trillion? 72 glowing cubes, each one the whole
// 13.8-billion-year history of the universe.
import { THREE, starField, nebulaSky, textSprite, smooth, ease, easeOut, rng, gauss, heartbeat, pointsMaterial, sprite } from '../lib.js';

export default function scale(ctx, info) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, ctx.aspect, 0.05, 5000);
  scene.add(nebulaSky({ renderer: ctx.renderer, colA: [0.1, 0.12, 0.35], colB: [0.3, 0.08, 0.3], intensity: 0.4, seed: 8 }));
  const stars = starField({ count: 5000, seed: 31, size: ctx.pix });
  scene.add(stars);

  // one mini spiral galaxy shared by all cubes
  const r = rng(12);
  const NG = 420;
  const gp = new Float32Array(NG * 3), gc = new Float32Array(NG * 3), gs = new Float32Array(NG);
  for (let i = 0; i < NG; i++) {
    const arm = i % 2;
    const d = Math.pow(r(), 0.7) * 0.36;
    const a = arm * Math.PI + d * 9 + gauss(r) * 0.25;
    gp.set([Math.cos(a) * d, gauss(r) * 0.015, Math.sin(a) * d], i * 3);
    const warm = Math.max(0, 1 - d * 5);
    gc.set([0.6 + 0.4 * warm, 0.7 + 0.2 * warm, 1.0 - 0.3 * warm], i * 3);
    gs[i] = 0.6 + r() * 1.2;
  }
  const gGeo = new THREE.BufferGeometry();
  gGeo.setAttribute('position', new THREE.BufferAttribute(gp, 3));
  gGeo.setAttribute('color', new THREE.BufferAttribute(gc, 3));
  gGeo.setAttribute('size', new THREE.BufferAttribute(gs, 1));
  const gMat = pointsMaterial({ sizeScale: 0.012 * ctx.pix });

  const edgeGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));
  const boxGeo = new THREE.BoxGeometry(1, 1, 1);
  const cubes = [];
  const NX = 6, NY = 4, NZ = 3, SP = 1.55;
  for (let x = 0; x < NX; x++) for (let y = 0; y < NY; y++) for (let z = 0; z < NZ; z++) {
    const g = new THREE.Group();
    g.position.set((x - (NX - 1) / 2) * SP, (y - (NY - 1) / 2) * SP, (z - (NZ - 1) / 2) * SP);
    const em = new THREE.LineBasicMaterial({ color: 0x7fd4ff, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false });
    g.add(new THREE.LineSegments(edgeGeo, em));
    const fm = new THREE.MeshBasicMaterial({ color: 0x1a4a8a, transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    g.add(new THREE.Mesh(boxGeo, fm));
    const gal = new THREE.Points(gGeo, gMat);
    gal.rotation.x = r() * 0.8 - 0.4;
    gal.rotation.z = r() * 0.8 - 0.4;
    g.add(gal);
    const core = sprite(0xfff0d0, 0.22, 'soft', 0.8);
    g.add(core);
    g.userData = { em, fm, gal, spin: 0.2 + r() * 0.3, dist: g.position.length() + r() * 0.6 };
    scene.add(g);
    cubes.push(g);
  }
  // the "first" cube is the one closest to the centre-front
  cubes.sort((a, b) => a.userData.dist - b.userData.dist);
  const maxDist = cubes[cubes.length - 1].userData.dist;

  const label1 = textSprite(['13.8 BILLION YEARS', 'THE AGE OF THE UNIVERSE'], { size: 0.32 });
  scene.add(label1);
  const label2 = textSprite(['× 72', 'ONE TRILLION YEARS'], { size: 1.1 });
  label2.position.set(SP * 3 + 2.6, -0.4, 0);
  scene.add(label2);

  function update(t, dur) {
    stars.material.uniforms.uTime.value = t;
    const tGrow0 = info.cue(1) - 1.0, tGrow1 = tGrow0 + 8;
    const hbOn = smooth(info.cue(5), info.cue(5) + 1, t);
    const hb = heartbeat(t, 0.9) * hbOn;
    cubes.forEach((c, i) => {
      const u = c.userData;
      const delay = i === 0 ? -10 : tGrow0 + (u.dist / maxDist) * (tGrow1 - tGrow0);
      const k = i === 0 ? smooth(0.2, 2.2, t) : smooth(delay, delay + 0.9, t);
      const back = k < 1 ? 1 + 0.35 * Math.sin(k * Math.PI) : 1;
      c.scale.setScalar(Math.max(0.0001, easeOut(k) * back) * (1 + 0.06 * hb));
      c.visible = k > 0.001;
      c.rotation.y = t * u.spin * 0.25;
      c.rotation.x = Math.sin(t * 0.2 + u.dist) * 0.1;
      u.gal.rotation.y = t * u.spin;
      u.em.opacity = 0.55 + 0.4 * hb + 0.3 * (1 - k);
      u.fm.opacity = 0.1 + 0.12 * hb;
    });
    label1.position.set(0, -0.95, cubes[0].position.z + 0.6);
    label1.material.opacity = smooth(1.5, 3, t) * (1 - smooth(tGrow0 - 0.5, tGrow0 + 0.5, t));
    label2.material.opacity = smooth(tGrow1, tGrow1 + 1.5, t) * (1 - smooth(info.cue(2) - 1, info.cue(2) + 0.5, t));

    // camera: close on the first cube, then pull back and orbit the block
    const pull = ease(smooth(tGrow0, tGrow1 + 2, t));
    const c0 = cubes[0].position;
    const ang = 0.35 + t * 0.03;
    const dist = 2.6 + pull * 12.5;
    const target = new THREE.Vector3().copy(c0).multiplyScalar(1 - pull);
    target.y += 1.3 * pull;
    camera.position.set(target.x + Math.sin(ang) * dist, target.y + 0.5 + pull * 3.5, target.z + Math.cos(ang) * dist);
    camera.lookAt(target);
  }
  return { scene, camera, update };
}
