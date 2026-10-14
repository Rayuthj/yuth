"""Narration synthesis with Kokoro-82M (ONNX).

Each beat is rendered to build/tts/<hash>.wav (24 kHz mono float32) and cached
by (text, voice, speed). Leading/trailing silence is trimmed so the timeline
has full control over pauses.

Model files (from https://github.com/thewh1teagle/kokoro-onnx/releases,
tag model-files-v1.0) are looked up in $KOKORO_DIR (default /tmp/claude-0/models).
"""
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video.script import BEATS, VOICES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
TTS_DIR = os.path.join(BUILD, "tts")
KOKORO_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/models")
SR = 24000

_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"),
                         os.path.join(KOKORO_DIR, "voices-v1.0.bin"))
    return _kokoro


def beat_key(text, voice, speed):
    h = hashlib.sha1(f"{voice}|{speed:.3f}|{text}".encode()).hexdigest()[:16]
    return h


def trim(sig, thresh_db=-42.0, pad=0.035):
    if len(sig) == 0:
        return sig
    peak = np.max(np.abs(sig)) + 1e-9
    win = int(0.01 * SR)
    env = np.sqrt(np.convolve(sig ** 2, np.ones(win) / win, mode="same"))
    on = np.where(env > peak * 10 ** (thresh_db / 20))[0]
    if len(on) == 0:
        return sig
    a = max(0, on[0] - int(pad * SR))
    b = min(len(sig), on[-1] + int(pad * SR))
    out = sig[a:b].copy()
    f = int(0.008 * SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-f:] *= np.linspace(1, 0, f)
    return out


def synth(text, voice_key, speed):
    voice = VOICES[voice_key]
    os.makedirs(TTS_DIR, exist_ok=True)
    path = os.path.join(TTS_DIR, beat_key(text, voice, speed) + ".wav")
    if not os.path.exists(path):
        samples, sr = kokoro().create(text, voice=voice, speed=speed, lang="en-us")
        assert sr == SR
        sig = trim(np.asarray(samples, dtype=np.float32))
        sf.write(path, sig, SR, subtype="FLOAT")
    info = sf.info(path)
    return path, info.frames / info.samplerate


def synth_chapter(ch, speed):
    """Synthesize every beat of a chapter; returns {beat_id: {path, dur, ...}}."""
    out = {}
    for b in BEATS[ch]:
        # Character dialogue keeps a natural pace regardless of narrator speed.
        sp = speed if b["voice"] == "narrator" else min(speed, 1.05)
        path, dur = synth(b["text"], b["voice"], round(sp, 3))
        out[b["id"]] = dict(path=path, dur=dur, voice=b["voice"], speed=sp)
        print(f"  {b['id']:7s} {dur:6.2f}s  ({b['voice']}, x{sp:.2f})", flush=True)
    return out


if __name__ == "__main__":
    chs = [int(a) for a in sys.argv[1:]] or sorted(BEATS)
    res = {}
    for ch in chs:
        print("chapter", ch)
        res[ch] = synth_chapter(ch, 1.0)
    print(json.dumps({c: round(sum(v["dur"] for v in r.values()), 2) for c, r in res.items()}))
