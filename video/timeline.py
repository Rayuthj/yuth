"""Fit narration beats into the fixed chapter slots.

For every chapter:
  1. synthesize at speed 1.0 and measure,
  2. pick a speaking speed so the average pause between lines is close to a
     per-chapter target (dramatic chapters breathe more),
  3. re-synthesize at that speed and distribute the remaining slack across
     the pauses according to each beat's `gap` weight.

Writes build/timeline.json, the single source of truth for animation, SFX
and audio placement.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video import tts  # noqa: E402
from video import project as PROJECT  # noqa: E402

TARGET_GAP = {1: 0.20, 2: 0.70, 3: 0.70, 4: 0.75, 5: 0.65, 6: 0.95, 7: 0.70, 8: 0.70, 9: 0.75, 10: 0.45}
SPEED_RANGE = (0.88, 1.22)
MIN_GAP = 0.12


def fit_chapter(ch):
    S = PROJECT.get().script
    _, title, start, end = next(c for c in S.CHAPTER_SLOTS if c[0] == ch)
    lead, tail = S.CHAPTER_TIMING[ch]["lead"], S.CHAPTER_TIMING[ch]["tail"]
    beats = S.BEATS[ch]
    target_gap = getattr(S, "TARGET_GAP", TARGET_GAP)
    avail = (end - start) - lead - tail
    n_gaps = len(beats) - 1

    speech_target = avail - n_gaps * target_gap[ch]
    speed = 1.0
    res = tts.synth_chapter(ch, speed)
    speech = sum(v["dur"] for v in res.values())
    # duration is only roughly proportional to 1/speed, so iterate
    for _ in range(4):
        if abs(speech - speech_target) < 0.6:
            break
        new = round(min(max(speed * speech / speech_target, SPEED_RANGE[0]), SPEED_RANGE[1]), 2)
        if abs(new - speed) < 0.005:
            break
        speed = new
        res = tts.synth_chapter(ch, speed)
        speech = sum(v["dur"] for v in res.values())

    slack = avail - speech
    if slack < n_gaps * MIN_GAP:
        raise SystemExit(f"chapter {ch}: narration too long by {n_gaps * MIN_GAP - slack:.2f}s")
    weights = [b["gap"] for b in beats[1:]]
    # every gap gets a minimum, the rest is shared by weight
    spare = slack - n_gaps * MIN_GAP
    gaps = [MIN_GAP + spare * w / sum(weights) for w in weights] if n_gaps else []

    t = lead
    out = []
    for i, b in enumerate(beats):
        if i > 0:
            t += gaps[i - 1]
        r = res[b["id"]]
        out.append(dict(id=b["id"], start=round(t, 4), end=round(t + r["dur"], 4),
                        path=r["path"], voice=b["voice"], text=b["text"]))
        t += r["dur"]
    assert abs((t + tail) - (end - start)) < 1e-6, (t, tail, end - start)
    print(f"chapter {ch:2d}: speed x{speed:.2f}  speech {speech:5.1f}s  avg gap {slack / max(1, n_gaps):.2f}s")
    return dict(title=title, start=start, end=end, speed=speed, lead=lead, tail=tail, beats=out)


def envelope(path, fps=30):
    """Per-frame loudness (0..1) used for lip-sync of dialogue."""
    sig, sr = sf.read(path, dtype="float32")
    hop = sr // fps
    n = len(sig) // hop + 1
    env = np.array([np.sqrt(np.mean(sig[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    env = env / (env.max() + 1e-9)
    return [round(float(x), 3) for x in env]


def build(chs=None):
    TIMELINE = PROJECT.get().timeline
    tl = {}
    if os.path.exists(TIMELINE):
        with open(TIMELINE) as f:
            tl = json.load(f)
    for ch in chs or sorted(PROJECT.get().script.BEATS):
        data = fit_chapter(ch)
        for b in data["beats"]:
            b["env"] = envelope(b["path"])
        tl[str(ch)] = data
    with open(TIMELINE, "w") as f:
        json.dump(tl, f, indent=1)
    return tl


def load():
    with open(PROJECT.get().timeline) as f:
        return json.load(f)


if __name__ == "__main__":
    PROJECT.pop_project_arg(sys.argv)
    build([int(a) for a in sys.argv[1:]] or None)
