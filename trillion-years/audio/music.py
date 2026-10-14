"""Procedural ambient score + sound design, mixed under the narration.

Everything is synthesized with numpy (no samples): evolving pad chords, a sub
drone, sparse bell tones, heartbeat thumps synced to the visuals, and a few
effects (supernova boom, ship launch, galaxy collision rumble). The music is
ducked under the narration and the result is written to build/soundtrack.wav.
"""
import json
import os
import subprocess

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
SR = 48000
RNG = np.random.default_rng(1234)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# chords per chapter (MIDI notes); every chapter's span is split evenly
CHORDS = {
    "intro":     [[50, 57, 60, 64], [46, 53, 57, 62], [41, 48, 57, 60], [45, 52, 57, 61]],
    "scale":     [[50, 57, 62, 64], [43, 50, 58, 62], [46, 53, 57, 62], [45, 52, 57, 64]],
    "century":   [[46, 53, 57, 62], [41, 48, 53, 57], [48, 55, 60, 64], [50, 57, 60, 65]],
    "memory":    [[50, 57, 60, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 55, 61]],
    "stars":     [[50, 57, 62, 64], [46, 53, 58, 65], [41, 48, 57, 64], [45, 52, 57, 61]],
    "drift":     [[43, 50, 55, 58], [46, 53, 58, 62], [48, 55, 60, 64], [50, 57, 62, 65]],
    "galaxy":    [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]],
    "oceans":    [[50, 57, 60, 65], [46, 53, 57, 62], [44, 51, 56, 60], [45, 52, 55, 61]],
    "andromeda": [[43, 50, 58, 62], [46, 53, 57, 64], [48, 55, 60, 67], [50, 57, 62, 69]],
    "sun":       [[50, 57, 60, 65], [44, 51, 56, 60], [46, 53, 58, 61], [49, 56, 61, 64]],
    "horizon":   [[38, 45, 53, 57], [34, 41, 50, 53], [36, 43, 50, 55], [38, 45, 50, 53]],
    "merge":     [[38, 45, 50, 53], [41, 48, 53, 57], [36, 43, 52, 55], [37, 44, 52, 57]],
    "trillion":  [[38, 45, 53, 57], [46, 53, 57, 62], [41, 48, 57, 60], [43, 50, 57, 62]],
    "outro":     [[46, 53, 57, 62], [41, 48, 57, 60], [48, 55, 60, 64], [50, 57, 62, 66]],
}
INTENSITY = {
    "intro": 0.55, "scale": 0.6, "century": 0.6, "memory": 0.5, "stars": 0.55, "drift": 0.62,
    "galaxy": 0.75, "oceans": 0.68, "andromeda": 0.85, "sun": 0.82, "horizon": 0.45,
    "merge": 0.4, "trillion": 0.7, "outro": 0.78,
}


def env_adsr(n, a, r):
    e = np.ones(n, dtype=np.float32)
    na, nr = int(a * SR), int(r * SR)
    na, nr = min(na, n // 2), min(nr, n // 2)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[n - nr:] = np.linspace(1, 0, nr) ** 2
    return e


def pad_chord(notes, dur, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    L = np.zeros(n, np.float32)
    R = np.zeros(n, np.float32)
    for note in notes:
        f0 = midi(note)
        for h in range(1, 7):
            amp = (1.0 / h ** 1.6) * (bright if h > 2 else 1.0)
            if f0 * h > 6000:
                break
            for det, pan in ((-0.0025, 0.2), (0.0, 0.5), (0.0031, 0.8)):
                ph = RNG.uniform(0, 2 * np.pi)
                lfo = 1 + 0.0015 * np.sin(2 * np.pi * RNG.uniform(0.05, 0.15) * t + ph)
                s = np.sin(2 * np.pi * f0 * h * (1 + det) * t * lfo + ph).astype(np.float32) * amp
                trem = 0.8 + 0.2 * np.sin(2 * np.pi * RNG.uniform(0.04, 0.1) * t + ph)
                s *= trem
                L += s * (1 - pan)
                R += s * pan
    e = env_adsr(n, min(4.0, dur * 0.35), min(4.0, dur * 0.35))
    k = 1.0 / (len(notes) * 3)
    return L * e * k, R * e * k


def bell(f, dur=3.5):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
         + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    s *= np.exp(-t * 1.4) * np.minimum(1, t * 200)
    return s.astype(np.float32)


def thump(dur=0.5, f0=58):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = f0 * (1 + 0.8 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 11) * np.minimum(1, t * 400)
    return s.astype(np.float32)


def noise_burst(dur, lp_hz, decay):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    x = RNG.standard_normal(n).astype(np.float32)
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / (1 + (fr / lp_hz) ** 4)
    x = np.fft.irfft(X, n).astype(np.float32)
    x /= np.max(np.abs(x)) + 1e-9
    return x * np.exp(-t * decay) * np.minimum(1, t * 20)


def add(buf, sig, t0, gain=1.0, pan=0.5):
    i = int(t0 * SR)
    if i >= buf.shape[1]:
        return
    j = min(buf.shape[1], i + len(sig))
    buf[0, i:j] += sig[: j - i] * gain * (1 - pan) * 2 ** 0.5
    buf[1, i:j] += sig[: j - i] * gain * pan * 2 ** 0.5


def reverb(x, seconds=3.2, mix=0.35):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = RNG.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(x.shape[1] + n)))
        y = np.fft.irfft(np.fft.rfft(x[c], size) * np.fft.rfft(ir, size), size)[: x.shape[1]]
        out[c] = (1 - mix) * x[c] + mix * y.astype(np.float32) * 0.9
    return out


def lowpass(x, hz):
    X = np.fft.rfft(x, axis=1)
    fr = np.fft.rfftfreq(x.shape[1], 1 / SR)
    X *= 1 / np.sqrt(1 + (fr / hz) ** 4)
    return np.fft.irfft(X, x.shape[1], axis=1).astype(np.float32)


def main():
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    total = tl["duration"]
    N = int(total * SR)
    music = np.zeros((2, N), np.float32)
    sfx = np.zeros((2, N), np.float32)
    scenes = {s["id"]: s for s in tl["scenes"]}

    def cue(sid, k, end=False):
        s = scenes[sid]
        return s["cues"][k]["end" if end else "start"]

    # ---- pads, drone, bells ----
    for s in tl["scenes"]:
        chords = CHORDS[s["id"]]
        span = s["end"] - s["start"]
        cd = span / len(chords)
        inten = INTENSITY[s["id"]]
        for k, ch in enumerate(chords):
            t0 = s["start"] + k * cd - 2.0
            dur = cd + 4.0
            L, R = pad_chord(ch, dur, bright=0.6 + 0.6 * inten)
            add(music, L, max(t0, 0), gain=0.55 + 0.5 * inten, pan=0.0)
            add(music, R, max(t0, 0), gain=0.55 + 0.5 * inten, pan=1.0)
            # sub drone on the root
            n = int(dur * SR)
            tt = np.arange(n, dtype=np.float32) / SR
            sub = np.sin(2 * np.pi * midi(ch[0] - 12) * tt).astype(np.float32) * env_adsr(n, 3, 3)
            add(music, sub, max(t0, 0), gain=0.18 * inten)
            # bells from the chord, upper octaves
            rate = 0.25 + 0.5 * inten
            tb = t0 + 2.0
            while tb < t0 + dur - 2.5:
                tb += RNG.exponential(1 / rate)
                note = RNG.choice(ch) + 12 * RNG.choice([1, 2])
                add(music, bell(midi(note)), tb, gain=0.05 + 0.05 * inten, pan=RNG.uniform(0.2, 0.8))

    # ---- heartbeat synced to the visuals ----
    for sid, period, vol in (("intro", 1.05, 0.55), ("trillion", 1.6, 0.4)):
        s = scenes[sid]
        k = 0
        while True:
            for off, g in ((0.05, 1.0), (0.2, 0.6)):
                tb = s["start"] + (k + off) * period
                if tb < s["end"] - 1.0:
                    fade = min(1.0, (s["end"] - 1.0 - tb) / 4.0)
                    add(sfx, thump(), tb, gain=vol * g * fade)
            k += 1
            if s["start"] + k * period > s["end"]:
                break

    # ---- one-off effects ----
    tsn = cue("stars", 4, end=True) + 0.1
    add(sfx, noise_burst(7.0, 180, 0.6), tsn, gain=0.55)
    n = int(6 * SR)
    tt = np.arange(n) / SR
    add(sfx, (np.sin(2 * np.pi * (40 - 15 * tt / 6) * tt) * np.exp(-tt * 0.6)).astype(np.float32), tsn, gain=0.5)
    tship = cue("oceans", 5) - 0.5
    w = noise_burst(9.0, 900, 0.35)
    w *= np.minimum(1, np.arange(len(w)) / (1.2 * SR))
    add(sfx, w, tship, gain=0.22, pan=0.45)
    ta = scenes["andromeda"]["start"] + 14
    add(sfx, noise_burst(14.0, 120, 0.25) * np.minimum(1, np.arange(int(14 * SR)) / (4 * SR)).astype(np.float32), ta, gain=0.4)
    tg = scenes["sun"]["start"] + 8
    add(sfx, noise_burst(16.0, 90, 0.18) * np.minimum(1, np.arange(int(16 * SR)) / (6 * SR)).astype(np.float32), tg, gain=0.35)
    tb = cue("sun", 4) + 0.5
    add(sfx, noise_burst(8.0, 400, 0.5), tb, gain=0.3)

    music = lowpass(music, 5200)
    music = reverb(music + sfx * 0.6, seconds=3.6, mix=0.4) + sfx * 0.4

    # ---- narration + ducking ----
    nar48 = os.path.join(BUILD, "narration48.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(BUILD, "narration.wav"),
                    "-ar", str(SR), "-ac", "1", nar48], check=True)
    voice, _ = sf.read(nar48, dtype="float32")
    voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
    win = int(0.05 * SR)
    rms = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
    active = (rms > 0.01).astype(np.float32)
    # smooth the gate: fast attack, slow release
    k = int(0.6 * SR)
    gate = np.convolve(active, np.ones(k) / k, mode="same")
    gate = np.clip(gate * 3, 0, 1)
    duck = 1.0 - 0.55 * gate
    music *= duck

    # master: fade in/out, normalize
    fade = np.ones(N, np.float32)
    fi, fo = int(1.5 * SR), int(4 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    music *= fade
    music *= 0.32 / (np.percentile(np.abs(music), 99.9) + 1e-9)
    mix = music + voice[None, :] * 0.92
    peak = np.max(np.abs(mix))
    if peak > 0.97:
        mix *= 0.97 / peak
    sf.write(os.path.join(BUILD, "soundtrack.wav"), mix.T, SR, subtype="PCM_16")
    sf.write(os.path.join(BUILD, "music_only.wav"), (music.T / max(1e-9, np.max(np.abs(music)))) * 0.9, SR, subtype="PCM_16")
    print(f"soundtrack: {N / SR:.2f}s, voice peak {np.max(np.abs(voice)):.2f}, music rms {np.sqrt(np.mean(music ** 2)):.3f}")


if __name__ == "__main__":
    main()
