// Procedural Earth used by several chapters. Continents are built from
// "plates" (spherical caps) plus baked noise, so moving the cap centres makes
// the continents drift, collide and merge.
import { THREE, noiseAtlas, dirLL } from './lib.js';

export const PRESENT = [
  [48, -100, 0.42], // North America
  [-15, -60, 0.33], // South America
  [50, 18, 0.24],   // Europe
  [50, 92, 0.48],   // Asia
  [4, 20, 0.40],    // Africa
  [-25, 134, 0.24], // Australia
  [-86, 0, 0.32],   // Antarctica
  [21, 79, 0.16],   // India
];
// a loose supercontinent ring ("Pangaea Ultima")
export const ULTIMA = [
  [32, -18, 0.42],
  [-18, -12, 0.33],
  [44, 22, 0.24],
  [30, 62, 0.48],
  [6, 24, 0.40],
  [-22, 52, 0.24],
  [-38, 18, 0.32],
  [10, 58, 0.16],
];

export function createEarth(renderer, { segments = 160 } = {}) {
  const noise = noiseAtlas(renderer);
  const plates = Array.from({ length: 8 }, () => new THREE.Vector4());
  const uniforms = {
    uNoise: { value: noise },
    uPlates: { value: plates },
    uSunDir: { value: new THREE.Vector3(1, 0.2, 0.4).normalize() },
    uSea: { value: 0 },
    uDry: { value: 0 },
    uOcean: { value: 1 },
    uBurn: { value: 0 },
    uCity: { value: 0 },
    uCityT: { value: 0 },
    uClouds: { value: 1 },
    uCloudT: { value: 0 },
    uSunBright: { value: 1 },
    uAtmo: { value: new THREE.Vector3(0.35, 0.6, 1.0) },
    uNightGlow: { value: 0 },
  };
  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: /* glsl */`
      varying vec3 vPos; varying vec3 vN; varying vec3 vW;
      void main(){
        vPos = position;
        vN = normalize(mat3(modelMatrix) * normal);
        vec4 w = modelMatrix * vec4(position, 1.0);
        vW = w.xyz;
        gl_Position = projectionMatrix * viewMatrix * w;
      }`,
    fragmentShader: /* glsl */`
      uniform sampler2D uNoise; uniform vec4 uPlates[8]; uniform vec3 uSunDir, uAtmo;
      uniform float uSea, uDry, uOcean, uBurn, uCity, uCityT, uClouds, uCloudT, uSunBright, uNightGlow;
      varying vec3 vPos; varying vec3 vN; varying vec3 vW;
      vec4 nz(vec3 d, float off){
        float lon = atan(d.z, -d.x); float lat = asin(clamp(d.y, -1.0, 1.0));
        return texture2D(uNoise, vec2(lon/6.2831853 + 0.5 + off, lat/3.14159265 + 0.5));
      }
      void main(){
        vec3 d = normalize(vPos);
        vec4 n = nz(d, 0.0);
        float h1 = -9.0, h2 = -9.0;
        for (int i = 0; i < 8; i++) {
          float c = (dot(d, uPlates[i].xyz) - cos(uPlates[i].w)) * 5.0;
          if (c > h1) { h2 = h1; h1 = c; } else if (c > h2) { h2 = c; }
        }
        float h = h1 + (n.r - 0.5) * 2.2 + (n.g - 0.5) * 0.6;
        float coll = smoothstep(-0.12, 0.15, h2 + (n.g-0.5)*0.4);
        float land = smoothstep(uSea - 0.015, uSea + 0.015, h);
        float lat = abs(d.y);

        // ocean
        vec3 deep = vec3(0.01, 0.045, 0.14), shallow = vec3(0.02, 0.2, 0.33);
        vec3 ocean = mix(deep, shallow, smoothstep(uSea - 0.35, uSea, h));
        vec3 seabed = mix(vec3(0.30, 0.22, 0.17), vec3(0.52, 0.42, 0.32), smoothstep(uSea-0.5, uSea, h));
        ocean = mix(seabed, ocean, uOcean);

        // land
        float arid = smoothstep(0.5, 0.7, n.g + 0.2 * (1.0 - smoothstep(0.1, 0.45, abs(lat - 0.3))));
        vec3 green = mix(vec3(0.05, 0.17, 0.05), vec3(0.16, 0.24, 0.08), n.g);
        vec3 desert = mix(vec3(0.55, 0.42, 0.26), vec3(0.62, 0.50, 0.33), n.r);
        vec3 lc = mix(green, desert, clamp(arid * 0.5 + uDry, 0.0, 1.0));
        float mount = clamp((h - uSea) * 1.5, 0.0, 1.0) * 0.5 + coll * 0.8;
        lc = mix(lc, vec3(0.38, 0.33, 0.28), clamp(mount, 0.0, 1.0) * 0.7);
        lc = mix(lc, vec3(0.85, 0.85, 0.85), smoothstep(0.62, 0.95, coll * (1.0 - uDry)) * 0.6);
        // polar ice
        float ice = smoothstep(0.80, 0.86, lat + (n.g - 0.5) * 0.2) * (1.0 - uDry);
        vec3 surf = mix(ocean, lc, land);
        surf = mix(surf, vec3(0.9, 0.93, 0.97), ice);
        // scorched rock
        vec3 rock = mix(vec3(0.16, 0.10, 0.07), vec3(0.32, 0.22, 0.15), n.r);
        surf = mix(surf, rock, uBurn);

        vec3 N = normalize(vN);
        vec3 V = normalize(cameraPosition - vW);
        float ndl = dot(N, uSunDir);
        float diff = max(ndl, 0.0);
        float day = smoothstep(-0.12, 0.2, ndl);
        vec3 col = surf * (0.02 + 1.15 * diff * uSunBright);
        // ocean glint
        vec3 Hh = normalize(uSunDir + V);
        float spec = pow(max(dot(N, Hh), 0.0), 140.0) * (1.0 - land) * uOcean;
        col += vec3(1.0, 0.9, 0.75) * spec * 0.45 * day * uSunBright;
        // clouds
        float cl = smoothstep(0.50, 0.72, nz(d, uCloudT).b) * uClouds;
        col = mix(col, vec3(1.0) * (0.03 + 1.05 * diff * uSunBright), cl * 0.85);
        // city lights on the night side
        float civ = 0.5 + 0.5 * sin(uCityT + n.r * 40.0);
        float lights = smoothstep(0.08, 0.45, n.a * (0.5 + 0.9 * civ)) * land * (1.0 - ice) * uCity;
        col += vec3(1.0, 0.68, 0.32) * lights * (1.0 - day) * (1.0 - cl * 0.6) * 2.2;
        // lava glow
        col += vec3(1.0, 0.28, 0.04) * uBurn * smoothstep(0.6, 0.68, n.g) * 0.9;
        col += vec3(0.6, 0.15, 0.03) * uNightGlow * (1.0 - day) * 0.25;
        // atmosphere rim
        float fr = pow(1.0 - max(dot(N, V), 0.0), 2.5);
        col += uAtmo * fr * (0.15 + 0.85 * smoothstep(-0.3, 0.5, ndl)) * 0.9;
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  const surface = new THREE.Mesh(new THREE.SphereGeometry(1, segments, segments / 2), mat);

  const atmoU = { uSunDir: uniforms.uSunDir, uAtmo: uniforms.uAtmo, uStrength: { value: 1 } };
  const atmo = new THREE.Mesh(
    new THREE.SphereGeometry(1.07, 96, 48),
    new THREE.ShaderMaterial({
      uniforms: atmoU,
      vertexShader: /* glsl */`
        varying vec3 vW; varying vec3 vC; varying float vR;
        void main(){
          vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz;
          vC = (modelMatrix*vec4(0.0,0.0,0.0,1.0)).xyz; vR = length(modelMatrix[0].xyz);
          gl_Position = projectionMatrix*viewMatrix*w; }`,
      fragmentShader: /* glsl */`
        uniform vec3 uSunDir, uAtmo; uniform float uStrength; varying vec3 vW; varying vec3 vC; varying float vR;
        void main(){
          vec3 dir = normalize(vW - cameraPosition);
          vec3 oc = vC - cameraPosition;
          vec3 closest = cameraPosition + dir * dot(oc, dir);
          float b = length(closest - vC) / vR;          // impact parameter in planet radii
          float a = pow(clamp((1.07 - b) / 0.07, 0.0, 1.0), 2.2);
          vec3 nrm = normalize(closest - vC);
          float lit = smoothstep(-0.45, 0.35, dot(nrm, uSunDir));
          gl_FragColor = vec4(uAtmo * a * (0.06 + 0.94 * lit) * uStrength, 1.0);
        }`,
      side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }),
  );
  const group = new THREE.Group();
  group.add(surface);
  group.add(atmo);

  function setPlates(a, b = a, t = 0) {
    for (let i = 0; i < 8; i++) {
      const da = dirLL(a[i][0], a[i][1]);
      const db = dirLL(b[i][0], b[i][1]);
      const ang = da.angleTo(db);
      let d;
      if (ang < 1e-5) d = da;
      else {
        const s = Math.sin(ang);
        d = da.clone().multiplyScalar(Math.sin((1 - t) * ang) / s).add(db.clone().multiplyScalar(Math.sin(t * ang) / s));
      }
      plates[i].set(d.x, d.y, d.z, a[i][2] + (b[i][2] - a[i][2]) * t);
    }
  }
  setPlates(PRESENT);

  return { group, surface, atmo, uniforms, atmoU, setPlates };
}
