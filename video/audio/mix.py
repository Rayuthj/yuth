"""Assemble the full soundtrack: narration + sound effects + ducked music.

    python3 video/audio/mix.py        -> build/mix.wav (48 kHz stereo) + build/soundtrack.m4a
"""
import importlib
import json
import os
import subprocess
import sys
import zlib

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from video.audio import sfx as SFX  # noqa: E402
from video.audio import music as MUSIC  # noqa: E402
from video.engine.scene import TL  # noqa: E402
from video import project as PROJECT  # noqa: E402

SR = 48000
TOTAL = 600.0

VOICE_RMS = 0.085        # target RMS per narration line
SFX_MASTER = 0.55        # overall level of sound effects relative to their own peak (0.8)
DUCK_DB = 9.0            # music reduction while someone is speaking


def place(buf, x, at, gain=1.0):
    i = int(round(at * SR))
    if i >= buf.shape[-1]:
        return
    if i < 0:
        x = x[..., -i:]
        i = 0
    j = min(buf.shape[-1], i + x.shape[-1])
    buf[..., i:j] += x[..., :j - i] * gain


def load_voice(path):
    x, sr = sf.read(path, dtype="float64")
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = signal.resample_poly(x, SR, sr)
    # loudness-match every line (speech-weighted RMS ignoring silences)
    win = int(0.05 * SR)
    frames = x[:len(x) // win * win].reshape(-1, win)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    active = rms[rms > rms.max() * 0.1]
    level = np.sqrt(np.mean(active ** 2)) if len(active) else 1e-3
    return x * (VOICE_RMS / level)


def envelope(x, attack=0.03, release=0.35, hop=0.01):
    h = int(hop * SR)
    n = len(x) // h
    rms = np.sqrt(np.mean(x[:n * h].reshape(n, h) ** 2, axis=1))
    out = np.zeros(n)
    a_up = 1 - np.exp(-hop / attack)
    a_dn = 1 - np.exp(-hop / release)
    v = 0.0
    for i in range(n):
        k = a_up if rms[i] > v else a_dn
        v += (rms[i] - v) * k
        out[i] = v
    return np.interp(np.arange(len(x)) / h, np.arange(n), out)


def build():
    BUILD = PROJECT.get().build
    tl_all = json.load(open(PROJECT.get().timeline))
    N = int(TOTAL * SR)
    voice = np.zeros(N)
    fx = np.zeros((2, N))
    mus = np.zeros((2, N))
    cues = []
    for ch in range(1, 11):
        data = tl_all[str(ch)]
        tl = TL(data)
        t0 = data["start"]
        # narration
        for b in data["beats"]:
            place(voice, load_voice(b["path"]), t0 + b["start"])
        # sound effects
        mod = PROJECT.get().chapter(ch)
        _, cue_list = mod.build(tl)
        for (T, name, gain, kw) in cue_list:
            seed = zlib.crc32(f"{ch}:{T}:{name}".encode()) & 0xFFFF
            x = SFX.make(name, kw.get("dur"), seed).astype(np.float64)
            pan = ((seed % 100) / 100 - 0.5) * 0.5
            g = 10 ** (gain / 20) * SFX_MASTER
            st = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
            place(fx, st, t0 + T, g)
            cues.append((round(t0 + T, 2), name))
        # music, with a master fade across the chapter boundary
        L, R = MUSIC.chapter_music(ch, tl, seed=ch * 101, mod=mod)
        D = tl.dur
        tt = np.arange(len(L)) / SR
        g = np.clip((D + 1.5 - tt) / 1.7, 0, 1)
        if ch == 10:
            g = np.clip((D - tt) / 3.0, 0, 1)
        place(mus, np.stack([L * g, R * g]), t0)
        print(f"chapter {ch}: {len(data['beats'])} lines, {len(cue_list)} sfx cues", flush=True)

    env = envelope(voice)
    thr = VOICE_RMS * 0.35
    duck = 10 ** (-DUCK_DB / 20 * np.clip(env / thr, 0, 1))
    mix = np.stack([voice, voice]) + mus * duck + fx
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    out_wav = os.path.join(BUILD, "mix.wav")
    sf.write(out_wav, mix.T.astype(np.float32), SR, subtype="FLOAT")
    # stems for QC
    sf.write(os.path.join(BUILD, "stem_voice.wav"), voice.astype(np.float32), SR, subtype="FLOAT")
    with open(os.path.join(BUILD, "sfx_cues.json"), "w") as f:
        json.dump(cues, f)
    print(f"mix written: peak {peak:.3f}", flush=True)
    return out_wav


def loudnorm(src, dst, I=-14.0, TP=-1.5, LRA=11.0):
    """Two-pass EBU R128 normalization with ffmpeg, encoded to AAC."""
    cmd1 = ["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af",
            f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd1, capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    m = json.loads(txt)
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true,aresample=48000")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-af", af, "-c:a", "aac",
                    "-b:a", "160k", "-ar", "48000", dst], check=True)
    print("loudness before:", m["input_i"], "LUFS ->", I, flush=True)
    return dst


if __name__ == "__main__":
    PROJECT.pop_project_arg(sys.argv)
    wav = build()
    loudnorm(wav, os.path.join(PROJECT.get().build, "soundtrack.m4a"))
