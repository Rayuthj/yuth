import * as THREE from 'three';
import { buildAngkor } from './angkor.js';
import { buildRoad } from './road.js';
import { buildBayon } from './bayon.js';
import { buildTaProhm } from './taprohm.js';
import { makePerson, makeTukTuk, CAST } from './characters.js';
import { envFromPreset, SKY, dirFromAngles } from './env.js';
import { SHOTS } from './timeline.js';
import { drawOverlay } from './overlay.js';

const W = window.RENDER_W;
const H = window.RENDER_H;

const Q = new URLSearchParams(location.search);
const renderer = new THREE.WebGLRenderer({ antialias: Q.get('aa') !== '0', preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 4000);
window.__r = renderer;
window.__worlds = null;
const out = document.createElement('canvas');
out.width = W;
out.height = H;
const ctx2d = out.getContext('2d');

const worlds = {};
const cast = {};
let freezeCache = null;
let tuk = null;

function inScene(o, scene) {
  for (let p = o.parent; p; p = p.parent) if (p === scene) return true;
  return false;
}
function useCast(scene, names) {
  for (const [k, p] of Object.entries(cast)) {
    const on = names.includes(k);
    p.root.visible = on;
    if (on && !inScene(p.root, scene)) scene.add(p.root);
  }
}

window.init = async () => {
  worlds.angkor = buildAngkor(renderer);
  worlds.road = buildRoad(renderer);
  worlds.bayon = buildBayon(renderer);
  worlds.taprohm = buildTaProhm(renderer);
  window.__worlds = worlds;
  // image based lighting per sky mood
  const envs = {};
  const envFor = (name, sun) => (envs[name] = envs[name] || envFromPreset(renderer, SKY[name], sun));
  worlds.angkor.envs = {
    predawn: envFor('predawn', dirFromAngles(160, -4)),
    sunrise: envFor('sunrise', dirFromAngles(160, 8)),
    sunset: envFor('sunset', dirFromAngles(10, 8)),
  };
  worlds.road.scene.environment = envFor('road', dirFromAngles(200, 6));
  worlds.bayon.scene.environment = envFor('day', dirFromAngles(140, 50));
  worlds.taprohm.scene.environment = envFor('jungle', dirFromAngles(140, 60));

  for (const [k, o] of Object.entries(CAST)) cast[k] = makePerson(o);
  tuk = makeTukTuk();
  worlds.road.scene.add(tuk.root);

  await document.fonts.load('700 60px Fredoka');
  await document.fonts.load('600 40px Fredoka');
  await document.fonts.load('400 40px Fredoka');
  await document.fonts.load('400 60px Moul', 'អង្គរ');
  await document.fonts.load('700 40px "Noto Sans Khmer"', 'អរគុណ');
  await document.fonts.ready;

  // warm up shader compilation for every world
  for (const w of Object.values(worlds)) {
    useCast(w.scene, Object.keys(cast));
    renderer.compile(w.scene, camera);
  }
  return true;
};

window.renderFrame = (t, quality = 0.93) => {
  const shot = SHOTS.find((s) => t >= s.start && t < s.end) || SHOTS[SHOTS.length - 1];
  const w = worlds[shot.world];
  const info = { captions: [] };
  const c = {
    t,
    u: t - shot.start,
    d: shot.end - shot.start,
    p: (t - shot.start) / (shot.end - shot.start),
    W: w,
    cam: camera,
    cast,
    tuk,
    info,
    use: (names) => useCast(w.scene, names),
  };
  camera.fov = 40;
  camera.up.set(0, 1, 0);
  if (w.flock) w.flock.group.visible = false;
  shot.run(c);
  const at = info.freezeT ?? t;
  camera.aspect = W / H;
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
  w.atmos.update(camera);
  if (w.water) w.water.material.uniforms.time.value = at;
  if (w.tick) w.tick(at, camera);
  w.scene.updateMatrixWorld();
  for (const b of info.bubbles || []) {
    const v = b.pos.clone().project(camera);
    b.sx = (v.x * 0.5 + 0.5) * W;
    b.sy = (-v.y * 0.5 + 0.5) * H;
    b.behind = v.z > 1;
  }
  // the polaroid ending shows a frozen 3D frame: render it once and reuse it
  let src = renderer.domElement;
  if (info.freezeT !== undefined) {
    if (!freezeCache || freezeCache.key !== info.freezeT) {
      renderer.render(w.scene, camera);
      const cv = document.createElement('canvas');
      cv.width = W;
      cv.height = H;
      cv.getContext('2d').drawImage(renderer.domElement, 0, 0);
      freezeCache = { key: info.freezeT, cv };
    }
    src = freezeCache.cv;
  } else {
    renderer.render(w.scene, camera);
  }
  ctx2d.drawImage(src, 0, 0);
  drawOverlay(ctx2d, W, H, t, shot, info, src);
  return out.toDataURL('image/jpeg', quality);
};
