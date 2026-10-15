# What If You Had 500 IQ? — 10-minute 2D stickman video

**Final video:** [`output/what_if_you_had_500_iq.mp4`](output/what_if_you_had_500_iq.mp4)
(1920×1080, 16:9, 30 fps, 18,000 frames, H.264 + AAC 48 kHz stereo, exactly 10:00, ~95 MiB)

Other deliverables in `output/`:
- `what_if_you_had_500_iq.srt`: subtitles timed from the narration (112 cues)
- `narration_script.md`: the full narration (1,405 words) with timestamps
- `preview_frames_1.jpg`, `preview_frames_2.jpg`: 40 frames sampled from the final MP4 (4 per chapter)
- `thumbnail.png` (1280×720) plus two alternates in `thumbnails/`, made by `video/thumbnail.py`
- `youtube_metadata.md`: title options, description with chapter timestamps, tags and upload settings

Everything in the film is generated from code in this repository: the animation, narration,
music and sound effects. It uses no stock footage, stock audio or image assets.

| Component | How it is made |
|---|---|
| Animation | Procedural 2D vector animation with **Cairo** (`video/engine/`): a rigged stickman with forward kinematics, foot planting, walk/run cycles, gestures, blinking, eyebrows, mouth shapes and lip-sync from the voice track; props, diagrams, camera moves and transitions |
| Narration | **Kokoro-82M** neural TTS (ONNX, runs locally). The narrator is `af_heart`; character dialogue uses `am_michael` (hero), `am_puck` (Sam) and `bf_emma` (Mia) |
| Music | Synthesized score (`video/audio/music.py`): additive-synthesis piano, plucks, marimba, celesta, pads, bass and drums, with a separate mood per chapter section and convolution reverb |
| Sound effects | 94 procedurally synthesized effects (`video/audio/sfx.py`) |
| Mix | Music ducks under speech; two-pass EBU R128 loudness normalization to −14 LUFS (`video/audio/mix.py`) |

## Structure (exact chapter timing)

| # | Chapter | Time |
|---|---|---|
| 1 | The Hook | 0:00–0:40 |
| 2 | The First 24 Hours | 0:40–1:40 |
| 3 | Your Brain Becomes a Supercomputer | 1:40–2:40 |
| 4 | You Can Predict People | 2:40–3:40 |
| 5 | You Could Change the World | 3:40–4:50 |
| 6 | The Dark Side of Extreme Intelligence | 4:50–5:50 |
| 7 | Could You Invent the Future? | 5:50–6:50 |
| 8 | The Biggest Problem: Other People | 6:50–7:50 |
| 9 | What Would Happen to Your Life? | 7:50–9:00 |
| 10 | The Final Revelation | 9:00–10:00 |

The full narration script (about 1,400 words) is in [`video/script.py`](video/script.py).

## How the timing works

1. `video/script.py` splits the narration into sentence-level *beats*.
2. `video/timeline.py` synthesizes every beat, picks a speaking speed per chapter, and spreads the
   pauses so each chapter lands exactly on its time slot. It writes `build/timeline.json`.
3. Each chapter module (`video/chapters/chNN.py`) anchors its shots and sound cues to beat IDs or
   individual words (`tl.w(beat, "word")`), so picture and sound stay in sync with the narration.

## Rebuilding

Requirements: Python 3.11+, ffmpeg with libx264, and
`pip install pycairo numpy scipy soundfile pillow kokoro-onnx`.
The Kokoro model files `kokoro-v1.0.onnx` and `voices-v1.0.bin` come from the
[kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
Put them in `$KOKORO_DIR` (default `/tmp/claude-0/models`). The fonts are Inter (system),
plus Kalam and Patrick Hand from Google Fonts (OFL) installed in `~/.fonts`.

```bash
python3 video/build.py                  # narration -> soundtrack -> render 10 chapters -> MP4 -> checks
python3 video/render.py 4 --sheet       # 16-frame contact sheet of chapter 4 for review
python3 video/render.py 4 --at 12.5     # one full-size frame at 12.5 s into chapter 4
```

A full rebuild takes about 10 minutes on 4 CPU cores.
