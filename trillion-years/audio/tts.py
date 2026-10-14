"""Generate the narration track and the master timeline.

Every line in script.json is synthesized separately with Kokoro TTS, then laid
out on a fixed 600-second (10:00) timeline. The gap between scenes is solved
for so the video lands on exactly ten minutes.

Outputs (in build/):
  narration.wav   mono 24 kHz narration, exactly TOTAL seconds long
  timeline.json   scene boundaries + per-line subtitle cues, used by the renderer
"""
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
CACHE = os.path.join(BUILD, "tts_cache")
MODELS = os.environ.get("KOKORO_MODELS", os.path.join(ROOT, "models"))

TOTAL = 600.0        # final length in seconds
LEAD_IN = 5.0        # music-only opening before the first line
TAIL = 9.0           # music-only ending after the last line
LINE_GAP = 0.75      # pause between sentences inside a scene
SPEED = float(os.environ.get("TTS_SPEED", "0.93"))
SR = 24000


def synth(kokoro, text, voice):
    key = hashlib.sha1(f"{voice}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(path):
        samples, sr = kokoro.create(text, voice=voice, speed=SPEED, lang="en-us")
        assert sr == SR
        # trim leading/trailing near-silence so our gaps are what we control
        idx = np.where(np.abs(samples) > 0.01)[0]
        if len(idx):
            samples = samples[max(0, idx[0] - 600): idx[-1] + 2400]
        sf.write(path, samples, SR)
    data, _ = sf.read(path, dtype="float32")
    return data


def main():
    from kokoro_onnx import Kokoro

    os.makedirs(CACHE, exist_ok=True)
    script = json.load(open(os.path.join(ROOT, "script.json")))
    kokoro = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"),
                    os.path.join(MODELS, "voices-v1.0.bin"))
    voice = script["voice"]

    clips = []  # per scene: list of arrays
    for scene in script["scenes"]:
        sc = []
        for line in scene["lines"]:
            audio = synth(kokoro, line.get("say", line["text"]), voice)
            sc.append(audio)
            print(f"  [{scene['id']}] {len(audio)/SR:5.2f}s  {line['text'][:60]}", flush=True)
        clips.append(sc)

    speech = sum(len(a) / SR for sc in clips for a in sc)
    inner_gaps = sum(LINE_GAP * (len(sc) - 1) for sc in clips)
    n_bounds = len(clips) - 1
    scene_gap = (TOTAL - LEAD_IN - TAIL - speech - inner_gaps) / n_bounds
    print(f"speech={speech:.1f}s inner_gaps={inner_gaps:.1f}s -> scene_gap={scene_gap:.2f}s")
    if scene_gap < 1.5:
        sys.exit("Narration too long for 10:00 — raise TTS_SPEED or trim script.")
    if scene_gap > 7.0:
        sys.exit("Narration too short for 10:00 — lower TTS_SPEED or extend script.")

    out = np.zeros(int(TOTAL * SR), dtype=np.float32)
    t = LEAD_IN
    scenes = []
    for si, (scene, sc) in enumerate(zip(script["scenes"], clips)):
        start = 0.0 if si == 0 else t - scene_gap * 0.62
        cues = []
        for li, (line, audio) in enumerate(zip(scene["lines"], sc)):
            s0 = int(round(t * SR))
            out[s0:s0 + len(audio)] += audio
            dur = len(audio) / SR
            cue = {"start": round(t, 3), "end": round(t + dur, 3), "text": line["text"]}
            if "card" in line:
                cue["card"] = line["card"]
            cues.append(cue)
            t += dur + (LINE_GAP if li < len(sc) - 1 else 0)
        scenes.append({"id": scene["id"], "start": round(start, 3), "age": scene["age"], "cues": cues})
        t += scene_gap
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    scenes[-1]["end"] = TOTAL

    peak = np.max(np.abs(out))
    out *= 0.89 / peak
    sf.write(os.path.join(BUILD, "narration.wav"), out, SR)
    json.dump({"duration": TOTAL, "fps": 30, "scenes": scenes},
              open(os.path.join(BUILD, "timeline.json"), "w"), indent=1)
    for s in scenes:
        print(f"{s['id']:10s} {s['start']:7.2f} -> {s['end']:7.2f}  ({s['end']-s['start']:.1f}s)")


if __name__ == "__main__":
    main()
