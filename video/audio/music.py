"""Procedural background score.

Each chapter is scored as a list of sections tied to narration beats. A
section has a style (mystery, discovery, playful, uplift, dark, wonder, warm,
reflective), a chord progression, a tempo and an intensity. Sections are
rendered with additive-synthesis instruments, crossfaded, and run through a
convolution reverb.
"""
import math

import numpy as np
from scipy import signal

SR = 48000


def T(d):
    return np.arange(int(d * SR)) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- instruments
def additive(f, d, nh=8, amp=lambda k: 1 / k, db=3.0, dk=1.0, inharm=0.0, att=0.004, rel=0.05):
    t = T(d)
    out = np.zeros_like(t)
    for k in range(1, nh + 1):
        fk = f * k * math.sqrt(1 + inharm * k * k)
        if fk > SR / 2 - 2000:
            break
        out += amp(k) * np.sin(2 * np.pi * fk * t) * np.exp(-t * (db + dk * k))
    n_a, n_r = max(1, int(att * SR)), max(1, int(rel * SR))
    out[:n_a] *= np.linspace(0, 1, n_a)
    if len(out) > n_r:
        out[-n_r:] *= np.linspace(1, 0, n_r)
    return out


def pluck(f, d=0.6):
    return additive(f, d, nh=10, db=4.0, dk=1.8) * 0.5


def piano(f, d=2.0):
    x = additive(f, d, nh=9, amp=lambda k: 1 / k ** 1.3, db=1.1, dk=0.55, inharm=0.0003, att=0.003, rel=0.2)
    return x * 0.55


def marimba(f, d=0.5):
    t = T(d)
    x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 20)) * np.exp(-t * 7)
    x[:120] *= np.linspace(0, 1, 120)
    return x * 0.55


def celesta(f, d=1.5):
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * r) for p, a, r in
            ((1, 1, 2.5), (2, 0.4, 4), (3, 0.15, 6), (4.2, 0.08, 9)))
    x[:100] *= np.linspace(0, 1, 100)
    return x * 0.4


def pad(f, d, att=0.8, rel=1.0, nh=6, bright=1.0):
    t = T(d)
    out = np.zeros_like(t)
    for det in (-0.006, 0.0, 0.0065):
        ff = f * (1 + det)
        for k in range(1, nh + 1):
            out += (1 / k ** (1.6 - 0.4 * bright)) * np.sin(2 * np.pi * ff * k * t + det * 300 * k)
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.25 * t)
    env = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, (d - t) / rel))
    return out * env * lfo * 0.12


def bass(f, d=0.5):
    t = T(d)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t))
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2) * np.minimum(1, np.maximum(0, (d - t) / 0.05))
    return x * env * 0.5


def drone(f, d):
    t = T(d)
    x = sum(np.sin(2 * np.pi * f * k * (1 + 0.002 * k) * t) / k ** 1.4 for k in range(1, 7))
    env = np.minimum(1, t / 2.0) * np.minimum(1, np.maximum(0, (d - t) / 2.0))
    return x * env * (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t)) * 0.18


def kick(d=0.35):
    t = T(d)
    return np.sin(2 * np.pi * np.cumsum(46 + 100 * np.exp(-t * 32)) / SR) * np.exp(-t * 8) * 0.9


def noise(d, seed):
    return np.random.default_rng(seed).standard_normal(int(d * SR))


def bandpass(x, lo, hi):
    sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, f):
    sos = signal.butter(2, f, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


_HAT = highpass(noise(0.05, 1), 7000) * np.exp(-T(0.05) * 90) * 0.25
_SHAKER = bandpass(noise(0.08, 2), 4000, 10000) * np.sin(np.pi * T(0.08) / 0.08) ** 2 * 0.18
_CLAP = bandpass(noise(0.18, 3), 900, 5000) * np.exp(-T(0.18) * 30) * 0.45
_KICK = kick()


# ---------------------------------------------------------------- mixing helpers
class Bus:
    def __init__(self, dur):
        self.L = np.zeros(int(dur * SR) + SR)
        self.R = np.zeros_like(self.L)

    def add(self, x, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i < 0:
            x = x[-i:]
            i = 0
        j = min(len(self.L), i + len(x))
        if j <= i:
            return
        a = (pan + 1) * math.pi / 4
        self.L[i:j] += x[:j - i] * gain * math.cos(a)
        self.R[i:j] += x[:j - i] * gain * math.sin(a)


# chord helpers: chord given as list of MIDI notes; bass = lowest note - 12
def chord(root, quality="maj", octave=0):
    iv = {"maj": (0, 4, 7), "min": (0, 3, 7), "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "sus2": (0, 2, 7),
          "add9": (0, 4, 7, 14), "madd9": (0, 3, 7, 14), "dim": (0, 3, 6), "sus4": (0, 5, 7), "lyd": (0, 4, 6, 11)}[quality]
    return [root + 12 * octave + i for i in iv]


PROGS = {
    "mystery": [chord(57, "madd9"), chord(53, "maj7"), chord(57, "madd9"), chord(52, "sus4")],      # A minor
    "discovery": [chord(60, "add9"), chord(55, "maj"), chord(57, "min7"), chord(53, "maj7")],      # C major
    "discovery_g": [chord(55, "add9"), chord(62, "maj"), chord(52, "min7"), chord(60, "maj7")],    # G major
    "playful": [chord(53, "maj"), chord(50, "min7"), chord(55, "min7"), chord(60, "maj")],         # F major
    "uplift": [chord(59, "min7"), chord(55, "maj7"), chord(50, "add9"), chord(57, "sus4")],         # D major
    "dark": [chord(50, "min"), chord(51, "maj"), chord(50, "min"), chord(46, "maj")],               # D minor + bII
    "wonder": [chord(60, "lyd"), chord(62, "add9"), chord(57, "min7"), chord(65, "maj7")],         # C lydian
    "warm": [chord(51, "add9"), chord(58, "maj"), chord(48, "min7"), chord(56, "maj7")],           # Eb major
    "warm_d": [chord(50, "add9"), chord(55, "maj7"), chord(47, "min7"), chord(57, "sus4")],        # D major
    "reflective": [chord(57, "min7"), chord(53, "maj7"), chord(48, "add9"), chord(55, "sus2")],    # Am F C G
    "playful_g": [chord(55, "maj"), chord(52, "min7"), chord(60, "maj7"), chord(62, "sus4")],     # G major
    "cold": [chord(49, "sus2"), chord(54, "sus2"), chord(52, "sus2"), chord(47, "sus2")],
}


def render_section(bus, t0, t1, style, prog, bpm, inten=1.0, seed=0, fade_in=0.6, fade_out=0.8):
    """Render one musical section into a temporary bus, then fade it into `bus`."""
    dur = t1 - t0
    if dur <= 0.05:
        return
    sb = Bus(dur + 3)
    beat = 60.0 / bpm
    bar = beat * 4
    chords = PROGS[prog]
    rng = np.random.default_rng(seed)
    nbars = int(math.ceil(dur / bar)) + 1
    for b in range(nbars):
        tb = b * bar
        if tb >= dur:
            break
        ch = chords[b % len(chords)]
        root = ch[0]
        L = min(bar, dur - tb) + 0.6
        if style in ("mystery", "dark", "cold"):
            if b % 2 == 0:
                sb.add(drone(midi(root - 24), min(bar * 2, dur - tb) + 2.0), tb, 0.9 * inten)
            for i, n in enumerate(ch):
                sb.add(pad(midi(n - (12 if style == "dark" else 0)), L + 0.8, att=1.5, rel=1.4, bright=0.4),
                       tb, 0.55 * inten, pan=(i - 1) * 0.4)
            if style == "dark":
                sb.add(pad(midi(root + 1 - 12), L + 0.8, att=2.0, rel=1.4, bright=0.3), tb, 0.25 * inten)
                for k in range(4):
                    sb.add(kick(0.4) * 0.5, tb + k * beat, 0.35 * inten)
                if b % 2 == 1:
                    sb.add(celesta(midi(ch[-1] + 12), 2.5), tb + beat * 2, 0.25 * inten, pan=0.5)
            else:
                for k in range(2):
                    if rng.random() < 0.8:
                        n = ch[rng.integers(len(ch))] + 12
                        sb.add(piano(midi(n), 3.0), tb + k * beat * 2 + rng.uniform(0, beat), 0.45 * inten,
                               pan=rng.uniform(-0.5, 0.5))
        elif style in ("discovery", "uplift"):
            for i, n in enumerate(ch):
                sb.add(pad(midi(n), L + 0.6, att=0.4, rel=0.8), tb, 0.35 * inten, pan=(i - 1) * 0.5)
            arp = ch + [ch[1] + 12, ch[2] + 12]
            steps = 16 if style == "uplift" else 8
            for k in range(steps):
                tk = tb + k * bar / steps
                if tk < dur:
                    n = arp[(k * 2 + (k // 4)) % len(arp)] + 12
                    sb.add(pluck(midi(n), 0.5), tk, 0.32 * inten * (1.0 if k % 2 == 0 else 0.7),
                           pan=0.35 * math.sin(k))
            for k in range(4):
                tk = tb + k * beat
                if tk < dur:
                    sb.add(bass(midi(root - 24), beat * 0.9), tk, 0.7 * inten)
                    if style == "uplift" or k % 2 == 0:
                        sb.add(_KICK, tk, 0.55 * inten)
                    if style == "uplift" and k % 2 == 1:
                        sb.add(_CLAP, tk, 0.35 * inten, pan=0.1)
                    sb.add(_SHAKER, tk + beat / 2, 0.5 * inten, pan=0.3)
                    if style == "uplift":
                        sb.add(_HAT, tk + beat / 2, 0.6 * inten, pan=-0.3)
        elif style == "playful":
            for k in range(8):
                tk = tb + k * beat / 2
                if tk < dur:
                    n = ch[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12
                    sb.add(marimba(midi(n), 0.45), tk, 0.42 * inten * (1.0 if k % 2 == 0 else 0.75),
                           pan=0.4 * (1 if k % 2 else -1))
            for k in range(4):
                tk = tb + k * beat
                if tk < dur:
                    if k % 2 == 0:
                        sb.add(bass(midi(root - 24), beat * 0.5), tk, 0.6 * inten)
                    else:
                        sb.add(bass(midi(ch[2] - 24), beat * 0.5), tk, 0.5 * inten)
                        sb.add(_CLAP, tk, 0.25 * inten)
                    sb.add(_HAT, tk + beat / 2, 0.4 * inten)
            for i, n in enumerate(ch):
                sb.add(pad(midi(n), L, att=0.5, rel=0.6, bright=0.5), tb, 0.15 * inten, pan=(i - 1) * 0.5)
        elif style == "wonder":
            for i, n in enumerate(ch):
                sb.add(pad(midi(n), L + 0.8, att=0.8, rel=1.0, bright=0.8), tb, 0.4 * inten, pan=(i - 1) * 0.5)
            arp = ch + [n + 12 for n in ch]
            for k in range(8):
                tk = tb + k * beat / 2
                if tk < dur:
                    n = arp[(k * 3) % len(arp)] + 12
                    sb.add(celesta(midi(n), 1.6), tk, 0.35 * inten, pan=0.5 * math.sin(k * 1.3))
                    sb.add(celesta(midi(n), 1.6), tk + beat * 0.75, 0.12 * inten, pan=-0.5 * math.sin(k * 1.3))
            for k in (0, 2):
                tk = tb + k * beat
                if tk < dur:
                    sb.add(_KICK, tk, 0.3 * inten)
                    sb.add(bass(midi(root - 24), beat * 1.8), tk, 0.45 * inten)
        elif style == "warm":
            for i, n in enumerate(ch):
                sb.add(pad(midi(n), L + 0.8, att=0.8, rel=1.0, bright=0.6), tb, 0.35 * inten, pan=(i - 1) * 0.5)
            for k in range(4):
                tk = tb + k * beat
                if tk < dur:
                    notes = ch if k == 0 else [ch[(k + 1) % len(ch)] + 12]
                    for n in notes:
                        sb.add(piano(midi(n), 2.2), tk + 0.01 * notes.index(n), 0.4 * inten, pan=0.2)
            sb.add(bass(midi(root - 24), bar), tb, 0.55 * inten)
        elif style == "reflective":
            for i, n in enumerate(ch):
                sb.add(pad(midi(n), L + 1.0, att=1.4, rel=1.4, bright=0.4), tb, 0.38 * inten, pan=(i - 1) * 0.5)
            pattern = [0, None, 2, None, 1, None, 3 if len(ch) > 3 else 2, None]
            for k, idx in enumerate(pattern):
                tk = tb + k * beat / 2
                if idx is not None and tk < dur:
                    sb.add(piano(midi(ch[idx] + 12), 3.0), tk, 0.38 * inten, pan=0.3 * math.sin(k))
            sb.add(piano(midi(root - 12), 3.5), tb, 0.3 * inten)
    # fades and transfer
    n = int(dur * SR)
    tail = int(fade_out * SR)
    for ch_ in (sb.L, sb.R):
        fi = int(fade_in * SR)
        if fi > 0:
            ch_[:fi] *= np.linspace(0, 1, fi) ** 1.5
        ch_[n:n + tail] *= np.linspace(1, 0, min(tail, len(ch_) - n))
        ch_[n + tail:] = 0
    i = int(t0 * SR)
    j = min(len(bus.L), i + len(sb.L))
    bus.L[i:j] += sb.L[:j - i]
    bus.R[i:j] += sb.R[:j - i]


def reverb_ir(d=2.4, seed=5):
    t = T(d)
    rng = np.random.default_rng(seed)
    env = np.exp(-t * 6.9 / d)
    irs = []
    for c in range(2):
        x = rng.standard_normal(len(t)) * env
        sos = signal.butter(2, 6000, btype="low", fs=SR, output="sos")
        x = signal.sosfilt(sos, x)
        x[:int(0.012 * SR)] = 0
        irs.append(x / np.sqrt(np.sum(x ** 2)))
    return irs


_IR = None


def apply_reverb(L, R, wet=0.28):
    global _IR
    if _IR is None:
        _IR = reverb_ir()
    wl = signal.fftconvolve(L, _IR[0])[:len(L)]
    wr = signal.fftconvolve(R, _IR[1])[:len(R)]
    return L * (1 - wet * 0.5) + wl * wet, R * (1 - wet * 0.5) + wr * wet


# ---------------------------------------------------------------- chapter scores
def plan(ch, tl):
    """Return a list of (t0, t1, style, prog, bpm, intensity, fade_in, fade_out) in chapter time."""
    s = tl.s
    D = tl.dur
    if ch == 1:
        st10 = tl.e("c1_09") - 0.25
        return [(0.0, s("c1_06"), "mystery", "mystery", 70, 0.55, 2.5, 1.0),
                (s("c1_06") - 0.5, s("c1_08") - 0.2, "dark", "mystery", 96, 0.75, 0.8, 0.6),
                (s("c1_08"), st10, "mystery", "mystery", 70, 0.6, 0.4, 0.3),
                (st10 + 0.45, D + 1.2, "uplift", "mystery", 96, 0.9, 0.05, 1.5)]
    if ch == 2:
        st5 = s("c2_05") - 0.15
        return [(0.6, st5, "discovery", "discovery", 100, 0.85, 0.6, 0.08),
                (s("c2_06") - 0.4, s("c2_10") - 0.4, "warm", "warm", 84, 0.65, 0.8, 1.0),
                (s("c2_10") - 0.6, D + 1.2, "warm", "warm_d", 72, 0.8, 1.0, 1.5)]
    if ch == 3:
        return [(0.0, s("c3_07") - 0.2, "discovery", "discovery_g", 104, 0.85, 1.0, 0.8),
                (s("c3_07") - 0.2, s("c3_09") - 0.3, "warm", "warm", 84, 0.6, 0.6, 1.0),
                (s("c3_09") - 0.5, D + 1.2, "wonder", "wonder", 92, 0.7, 1.0, 1.5)]
    if ch == 4:
        t_right = tl.w("c4_07", "right")
        return [(0.0, s("c4_06") - 0.2, "playful", "playful", 110, 0.75, 1.0, 0.4),
                (s("c4_06") - 0.2, s("c4_07") - 0.1, "wonder", "wonder", 96, 0.8, 0.3, 0.4),
                (s("c4_07"), t_right, "playful", "playful", 128, 0.6, 0.2, 0.05),
                (t_right + 1.0, s("c4_09") - 0.3, "warm", "warm", 84, 0.5, 0.8, 0.8),
                (s("c4_09") - 0.3, D + 1.2, "playful", "playful", 104, 0.55, 0.8, 1.5)]
    if ch == 5:
        t_knock = tl.w("c5_10", "knocks")
        return [(0.0, t_knock - 0.15, "uplift", "uplift", 112, 0.8, 1.0, 0.1),
                (s("c5_11") - 0.3, s("c5_12") - 0.3, "warm", "warm_d", 84, 0.55, 1.0, 0.8),
                (s("c5_12") - 0.4, D + 1.2, "uplift", "uplift", 112, 0.85, 1.5, 1.5)]
    if ch == 6:
        return [(0.0, s("c6_09") - 0.3, "dark", "dark", 60, 0.7, 1.5, 1.2),
                (s("c6_09") - 0.2, D + 1.2, "warm", "warm_d", 76, 0.75, 1.5, 1.5)]
    if ch == 7:
        return [(0.0, s("c7_07") - 0.2, "wonder", "wonder", 96, 0.75, 1.5, 0.8),
                (s("c7_07") - 0.2, s("c7_08") - 0.2, "mystery", "mystery", 70, 0.6, 0.6, 0.6),
                (s("c7_08") - 0.2, s("c7_11") - 0.1, "playful", "playful_g", 104, 0.6, 0.5, 0.3),
                (s("c7_11"), s("c7_12") - 0.2, "uplift", "uplift", 112, 0.75, 0.2, 0.6),
                (s("c7_12") - 0.3, D + 1.2, "warm", "warm", 84, 0.65, 0.8, 1.5)]
    if ch == 8:
        return [(0.0, s("c8_04") - 0.2, "playful", "playful_g", 104, 0.7, 1.0, 0.3),
                (s("c8_04") + 1.0, s("c8_06") - 0.3, "reflective", "reflective", 60, 0.45, 0.6, 0.6),
                (s("c8_06") - 0.3, s("c8_09") - 0.3, "playful", "playful_g", 104, 0.65, 0.5, 0.8),
                (s("c8_09") - 0.3, D + 1.2, "uplift", "uplift", 104, 0.65, 1.0, 1.5)]
    if ch == 9:
        return [(0.0, s("c9_04") - 0.3, "discovery", "discovery", 100, 0.7, 1.0, 1.0),
                (s("c9_04") - 0.3, s("c9_05") - 0.3, "mystery", "reflective", 70, 0.55, 0.8, 0.5),
                (s("c9_05") - 0.3, s("c9_06") - 0.3, "dark", "dark", 70, 0.75, 0.3, 0.5),
                (s("c9_06") - 0.3, s("c9_07") - 0.3, "mystery", "cold", 70, 0.6, 0.4, 0.5),
                (s("c9_07") - 0.3, s("c9_08") - 0.3, "warm", "warm", 84, 0.8, 0.4, 0.6),
                (s("c9_08") - 0.3, s("c9_09") - 0.3, "mystery", "mystery", 70, 0.55, 0.5, 0.6),
                (s("c9_09") - 0.3, s("c9_11") - 0.5, "warm", "warm", 84, 0.75, 0.6, 1.0),
                (s("c9_11") - 0.6, D + 1.2, "reflective", "reflective", 66, 0.6, 1.2, 1.5)]
    if ch == 10:
        return [(0.0, D - 0.4, "reflective", "reflective", 66, 0.65, 2.0, 3.5)]
    raise ValueError(ch)


def chapter_music(ch, tl, seed=0):
    D = tl.dur
    bus = Bus(D + 3)
    for i, (t0, t1, style, prog, bpm, inten, fi, fo) in enumerate(plan(ch, tl)):
        render_section(bus, max(0.0, t0), min(t1, D + 2.0), style, prog, bpm, inten, seed + i * 17, fi, fo)
    L, R = apply_reverb(bus.L, bus.R)
    n = int((D + 1.5) * SR)
    L, R = L[:n], R[:n]
    # loudness normalization per chapter (RMS of the active part)
    rms = np.sqrt(np.mean(np.concatenate([L, R]) ** 2) + 1e-12)
    target = {6: 0.036, 10: 0.036}.get(ch, 0.042)
    g = target / rms
    return (L * g).astype(np.float32), (R * g).astype(np.float32)
