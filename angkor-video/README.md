# A Trip to Angkor — 3D cartoon short (JavaScript)

A 2-minute, 1080p, 24 fps 3D cartoon about five friends (Sokha, Mia, Leo, Nita and Kai)
visiting the temples of Angkor, Cambodia. Everything — models, animation, titles and
soundtrack — is generated procedurally in JavaScript.

**Story:** title flight over Angkor Wat at dawn → tuk-tuk ride through the rice fields →
walk along the naga causeway → sunrise over the lotus pond and a selfie → Bayon's giant
smiling faces (Leo copies the smile) → Ta Prohm's jungle roots → sunset jump photo →
polaroid "The End".

## How it works

| Part | File |
| --- | --- |
| Renderer, frame compositing | `src/main.js`, `index.html` |
| Shots, cameras, acting, captions | `src/timeline.js` |
| Titles, captions, speech bubbles, iris wipes, polaroid ending | `src/overlay.js` |
| Characters and tuk-tuk | `src/characters.js` |
| Worlds: Angkor Wat, countryside road, Bayon, Ta Prohm | `src/angkor.js`, `src/road.js`, `src/bayon.js`, `src/taprohm.js` |
| Sky, lighting, vegetation, birds | `src/env.js` |
| Procedural stone / grass / bark shaders, geometry helpers | `src/util.js` |
| Synthesized soundtrack (roneat, kong, khloy, skor, chhing + SFX) | `tools/music.js` |
| Frame-by-frame rendering in headless Chromium → H.264 | `tools/render.js` |

Scenes are built with [three.js](https://threejs.org). Each frame is rendered
deterministically from its timestamp in headless Chromium (Playwright, SwiftShader
WebGL), streamed as JPEG into ffmpeg, encoded in resumable 5-second segments, then
concatenated and muxed with the soundtrack.

## Render it yourself

```bash
npm install
npm run render          # writes out/angkor_trip_1080p.mp4 (about 2 h on 4 CPU cores)
node tools/stills.js 12 44 64   # quick preview stills at given seconds -> out/stills/
```
