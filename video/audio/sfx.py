"""Procedural sound effects (48 kHz mono float32).

Every effect is synthesized from scratch with numpy/scipy, so the film has no
external audio dependencies. `make(name, dur=None, seed=0)` returns a signal.
"""
import numpy as np
from scipy import signal

SR = 48000


# ---------------------------------------------------------------- building blocks
def T(d):
    return np.arange(int(d * SR)) / SR


def rng(seed):
    return np.random.default_rng(seed)


def noise(d, seed=0):
    return rng(seed).standard_normal(int(d * SR)).astype(np.float64)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR / 2 - 100)], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    sos = signal.butter(order, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    sos = signal.butter(order, f, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def expdec(d, rate):
    return np.exp(-T(d) * rate)


def adsr(n, a=0.01, dcy=0.1, s=0.7, r=0.2):
    a_n, d_n, r_n = int(a * SR), int(dcy * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    env = np.concatenate([np.linspace(0, 1, a_n, endpoint=False), np.linspace(1, s, d_n, endpoint=False),
                          np.full(s_n, s), np.linspace(s, 0, r_n)])
    return np.pad(env, (0, max(0, n - len(env))))[:n]


def sweep(f0, f1, d, curve="exp"):
    t = T(d)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / d)
    else:
        f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def tone(f, d, kind="sine"):
    t = T(d)
    if kind == "square":
        return np.sign(np.sin(2 * np.pi * f * t)) * 0.6
    if kind == "saw":
        return 2 * ((f * t) % 1) - 1
    if kind == "tri":
        return 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
    return np.sin(2 * np.pi * f * t)


def bell(f, d=1.2, partials=((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)), rate=4.0):
    t = T(d)
    out = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * rate * (1 + p * 0.4)) for p, a in partials)
    return out


def place(dst, src, at):
    i = int(at * SR)
    if i >= len(dst) or i + len(src) <= 0:
        return dst
    s0 = max(0, -i)
    j = min(len(dst), i + len(src))
    dst[max(0, i):j] += src[s0:s0 + j - max(0, i)]
    return dst


def fade(x, fi=0.005, fo=0.02):
    n = len(x)
    a, b = min(n // 2, int(fi * SR)), min(n // 2, int(fo * SR))
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def click(d=0.004, seed=0, lo=2000, hi=9000):
    return bp(noise(d, seed), lo, hi) * expdec(d, 900)


# ---------------------------------------------------------------- effects
def fx_tick(dur, s, f=2400):
    d = 0.07
    x = click(0.006, s) * 0.6
    x = np.pad(x, (0, int(d * SR) - len(x)))
    x += np.sin(2 * np.pi * f * T(d)) * expdec(d, 90) * 0.5
    return x


def fx_tock(dur, s):
    return fx_tick(dur, s, 1700)


def fx_blink(dur, s):
    return np.sin(2 * np.pi * 900 * T(0.03)) * expdec(0.03, 150) * 0.3


def fx_whoosh(dur, s, d=0.65, lo=300, hi=2600, peak=0.55):
    d = dur or d
    n = noise(d, s)
    t = T(d)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * np.exp(-((t / d - peak) ** 2) * 3)
    # moving band: split into chunks
    out = np.zeros_like(n)
    k = 12
    for i in range(k):
        f = lo * (hi / lo) ** np.sin(np.pi * (i + 0.5) / k)
        seg = bp(n, f * 0.7, f * 1.4)
        w = np.clip(1 - np.abs(t / d * k - i - 0.5), 0, 1)
        out += seg * w
    return out * env


def fx_swoosh(dur, s):
    return fx_whoosh(0.32, s, lo=800, hi=4500)


def fx_darkwhoosh(dur, s):
    d = 1.3
    x = fx_whoosh(d, s, lo=120, hi=900) * 1.2
    x += lp(noise(d, s + 1), 120) * np.sin(np.pi * T(d) / d) * 2.0
    return x


def fx_pop(dur, s):
    d = 0.09
    x = sweep(700, 180, d) * expdec(d, 45)
    x[:200] += click(200 / SR, s)[:200] * 0.5
    return x


def fx_ding(dur, s):
    return bell(1318.5, 1.3) * 0.6


def fx_check(dur, s):
    return (bell(1760, 0.35, rate=10) + bell(2637, 0.35, rate=12) * 0.5) * 0.5


def fx_chime(dur, s):
    out = np.zeros(int(2.0 * SR))
    for i, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
        place(out, bell(f, 1.6, rate=2.5) * (0.5 - i * 0.07), i * 0.09)
    return out


def fx_boom(dur, s):
    d = 2.2
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
    x += lp(noise(d, s), 200) * np.exp(-t * 4) * 3
    x += hp(noise(d, s + 2), 2000) * np.exp(-t * 18) * 0.4
    return x


def fx_boom_soft(dur, s):
    d = 3.0
    t = T(d)
    env = np.minimum(t / 0.08, 1) * np.exp(-t * 0.9)
    x = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t)) * env
    x += lp(noise(d, s), 400) * env * 1.5
    return x * 0.7


def fx_thud(dur, s):
    d = 0.3
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)
    x += lp(noise(d, s), 600) * np.exp(-t * 30) * 1.5
    return x


def fx_stamp(dur, s):
    x = fx_thud(dur, s)
    x[:300] += click(300 / SR, s, 1000, 6000) * 0.8
    return x


def fx_slam(dur, s):
    x = np.zeros(int(1.4 * SR))
    place(x, fx_thud(dur, s) * 1.5, 0)
    place(x, fx_boom(dur, s)[:int(1.4 * SR)] * 0.5, 0)
    return x


def fx_bump(dur, s):
    return fx_thud(dur, s) * 0.6


def fx_riser(dur, s):
    d = dur or 1.5
    t = T(d)
    env = (t / d) ** 2
    x = bp(noise(d, s), 800, 7000) * env * 0.6
    x += sweep(200, 1600, d) * env * 0.35
    return fade(x, 0.01, 0.03)


def fx_rise(dur, s):
    d = dur or 0.6
    return sweep(300, 1400, d) * adsr(int(d * SR), 0.02, 0.1, 0.6, 0.2) * 0.4


def fx_shimmer(dur, s):
    d = dur or 1.6
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(28):
        f = r.uniform(2500, 7000)
        place(out, np.sin(2 * np.pi * f * T(0.25)) * expdec(0.25, 14) * r.uniform(0.1, 0.25), r.uniform(0, d - 0.25))
    return out


def fx_sparkle(dur, s):
    r = rng(s)
    out = np.zeros(int(0.8 * SR))
    for i in range(6):
        f = r.choice([2093, 2637, 3136, 3520, 4186])
        place(out, bell(f, 0.4, rate=9) * 0.25, i * 0.07)
    return out


def fx_zap(dur, s):
    d = 0.22
    x = sweep(2400, 150, d)
    x = np.tanh(x * 3) * expdec(d, 12) * 0.5
    return x


def fx_alarm(dur, s):
    d = dur or 1.5
    t = T(d)
    strikes = (np.sin(2 * np.pi * 22 * t) > 0).astype(float)
    metal = bell(2200, d, rate=0.5) + bell(2650, d, rate=0.5) * 0.7
    x = metal * (0.4 + 0.6 * strikes) * 0.6
    return fade(x, 0.005, 0.05)


def fx_bell(dur, s):
    d = 1.8
    t = T(d)
    strikes = (np.sin(2 * np.pi * 14 * t) > 0).astype(float)
    x = (bell(880, d, rate=0.8) + bell(1180, d, rate=0.8) * 0.6) * (0.5 + 0.5 * strikes) * np.exp(-t * 1.2)
    return x * 0.6


def fx_ping(dur, s):
    out = np.zeros(int(0.6 * SR))
    place(out, bell(1318.5, 0.4, rate=8), 0)
    place(out, bell(1760, 0.5, rate=7), 0.1)
    return out * 0.5


def fx_honk(dur, s):
    d = 0.35
    x = lp(tone(392, d, "saw") + tone(494, d, "saw"), 1800) * adsr(int(d * SR), 0.01, 0.05, 0.9, 0.05)
    return x * 0.35


def fx_scribble(dur, s):
    d = dur or 1.0
    r = rng(s)
    n = bp(noise(d, s), 2500, 7000)
    t = T(d)
    env = np.abs(np.sin(2 * np.pi * r.uniform(5, 8) * t + np.sin(2 * np.pi * 1.3 * t) * 2))
    return n * env * 0.35


def fx_clicks(dur, s):
    d = dur or 1.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 9)):
        place(out, click(0.01, s + i, 1500, 6000) * r.uniform(0.4, 1.0) +
              np.pad(fx_thud(0, s)[:200] * 0.1, (0, 280)), r.uniform(0, d - 0.02))
    return out


def fx_toaster(dur, s):
    out = np.zeros(int(1.4 * SR))
    place(out, fx_boing(0, s) * 0.8, 0)
    place(out, fx_ding(0, s) * 0.8, 0.15)
    return out


def fx_boing(dur, s):
    d = 0.6
    t = T(d)
    f = 260 * (1 + 0.35 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 5))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * expdec(d, 5) * 0.5


def fx_scratch(dur, s):
    d = 0.55
    t = T(d)
    n = noise(d, s)
    f = 800 + 700 * np.sin(2 * np.pi * 3.5 * t) * np.exp(-t * 2)
    out = np.zeros_like(n)
    for c in (500, 1000, 1500):
        out += bp(n, c * 0.8, c * 1.3) * np.clip(1 - np.abs(f - c) / 600, 0, 1)
    out += sweep(900, 200, d) * 0.3
    return out * np.exp(-t * 2.5) * 0.8


def fx_draw(dur, s):
    d = dur or 1.0
    t = T(d)
    return bp(noise(d, s), 3000, 8000) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t)) * 0.2


def fx_marker(dur, s):
    d = dur or 1.0
    t = T(d)
    x = fx_draw(d, s)
    squeak = np.sin(2 * np.pi * np.cumsum(2400 + 300 * np.sin(2 * np.pi * 2.2 * t)) / SR)
    x += squeak * (np.sin(2 * np.pi * 1.7 * t) > 0.6) * 0.05
    return x


def fx_chalk(dur, s):
    d = dur or 1.5
    r = rng(s)
    out = fx_scribble(d, s) * 0.8
    for i in range(int(d * 4)):
        place(out, click(0.01, s + i, 1500, 5000) * 0.6, r.uniform(0, d - 0.02))
    return out


def fx_groan(dur, s):
    notes = [233.1, 220.0, 207.7, 196.0]
    lens = [0.32, 0.32, 0.32, 0.9]
    out = np.zeros(int(2.2 * SR))
    at = 0
    for f, ln in zip(notes, lens):
        t = T(ln)
        vib = 1 + (0.012 * np.sin(2 * np.pi * 6 * t) if ln > 0.5 else 0)
        x = lp(2 * ((np.cumsum(f * vib) / SR) % 1) - 1, 1500) * adsr(len(t), 0.03, 0.05, 0.85, 0.1)
        place(out, x * 0.45, at)
        at += ln
    return out


def fx_footsteps(dur, s):
    d = dur or 1.0
    out = np.zeros(int(d * SR))
    k = 0
    tt = 0.05
    while tt < d - 0.1:
        step = lp(noise(0.08, s + k), 900) * expdec(0.08, 50)
        step += np.sin(2 * np.pi * (90 + 15 * (k % 2)) * T(0.08)) * expdec(0.08, 40) * 0.5
        place(out, step * 0.5, tt)
        tt += 0.42
        k += 1
    return out


def fx_bubbles(dur, s):
    d = dur or 2.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 10)):
        bd = r.uniform(0.04, 0.09)
        f0 = r.uniform(400, 1200)
        place(out, sweep(f0, f0 * 2.2, bd) * expdec(bd, 30) * r.uniform(0.1, 0.25), r.uniform(0, d - bd))
    return out


def fx_typing(dur, s):
    d = dur or 2.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    tt = 0
    while tt < d - 0.05:
        place(out, click(0.012, int(tt * 1000) + s, 1200, 7000) * r.uniform(0.3, 0.7), tt)
        tt += r.uniform(0.06, 0.16)
    return out


def fx_alert(dur, s):
    out = np.zeros(int(0.7 * SR))
    for i, f in enumerate((988, 740, 988, 740)):
        place(out, lp(tone(f, 0.13, "square"), 4000) * adsr(int(0.13 * SR), 0.005, 0.02, 0.8, 0.02) * 0.25, i * 0.15)
    return out


def fx_blip(dur, s):
    return np.sin(2 * np.pi * 1250 * T(0.07)) * adsr(int(0.07 * SR), 0.003, 0.02, 0.5, 0.03) * 0.35


def fx_blips(dur, s):
    d = dur or 1.5
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 7)):
        f = r.choice([880, 1046, 1318, 1568])
        place(out, np.sin(2 * np.pi * f * T(0.06)) * expdec(0.06, 40) * 0.25, i / 7)
    return out


def fx_data(dur, s):
    d = dur or 1.5
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 22)):
        f = r.uniform(1500, 4000)
        place(out, lp(tone(f, 0.025, "square"), 6000) * 0.08, r.uniform(0, d - 0.03))
    return out


def fx_network(dur, s):
    d = dur or 1.2
    out = fx_data(d, s)
    place(out, fx_whoosh(d, s, lo=1000, hi=5000) * 0.5, 0)
    return out


def fx_predict(dur, s):
    out = np.zeros(int(0.45 * SR))
    place(out, np.sin(2 * np.pi * 1046 * T(0.1)) * expdec(0.1, 25) * 0.35, 0)
    place(out, np.sin(2 * np.pi * 1568 * T(0.25)) * expdec(0.25, 12) * 0.35, 0.1)
    return out


def fx_page(dur, s):
    d = 0.35
    return fx_whoosh(d, s, lo=1500, hi=6000) * 1.2


def fx_scratch_out(dur, s):
    d = 0.28
    return bp(noise(d, s), 2000, 7000) * np.sin(np.pi * T(d) / d) * 0.5


def fx_bulb(dur, s):
    out = np.zeros(int(1.0 * SR))
    place(out, bell(2093, 0.8, rate=6) * 0.4, 0)
    place(out, np.sin(2 * np.pi * 120 * T(0.8)) * adsr(int(0.8 * SR), 0.05, 0.1, 0.3, 0.4) * 0.08, 0)
    return out


def fx_bonk(dur, s):
    d = 0.35
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(520 * np.exp(-t * 4)) / SR) * expdec(d, 16)
    x[:300] += click(300 / SR, s, 800, 4000)
    return x * 0.6


def fx_crowd(dur, s):
    d = dur or 10
    t = T(d)
    x = bp(noise(d, s), 150, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t) * np.sin(2 * np.pi * 0.31 * t))
    x += lp(noise(d, s + 1), 120) * 0.8
    return fade(x * 0.15, 1.0, 1.5)


def fx_murmur(dur, s):
    d = dur or 2.0
    t = T(d)
    syl = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 1.7 * t + 1))
    return fade(bp(noise(d, s), 250, 1600) * syl * 0.25, 0.3, 0.4)


def fx_laugh(dur, s):
    d = dur or 3.0
    r = rng(s)
    t = T(d)
    syl = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 4.5 * t) * np.sin(2 * np.pi * 0.9 * t))
    x = bp(noise(d, s), 400, 2400) * syl * 0.22
    for i in range(4):
        place(x, bell(r.uniform(2500, 3500), 0.4, rate=10) * 0.08, r.uniform(0, d - 0.4))
    return fade(x, 0.4, 0.6)


def fx_scan(dur, s):
    d = 1.0
    t = T(d)
    f = 600 + 900 * np.sin(np.pi * t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t))
    return x * np.sin(np.pi * t / d) * 0.25


def fx_slowmo(dur, s):
    d = 0.9
    x = sweep(400, 70, d) * adsr(int(d * SR), 0.05, 0.2, 0.7, 0.3)
    x += fx_whoosh(d, s, lo=150, hi=800) * 0.6
    return x * 0.6


def fx_dance(dur, s):
    d = dur or 2.0
    out = np.zeros(int(d * SR))
    beat = 60 / 128
    bass = [110, 110, 146.8, 130.8]
    i = 0
    tt = 0
    while tt < d - 0.05:
        if i % 2 == 0:
            place(out, fx_kick() * 0.5, tt)
        place(out, hp(noise(0.03, i), 6000) * expdec(0.03, 120) * 0.25, tt + beat / 2)
        bd = beat * 0.45
        place(out, lp(tone(bass[(i // 2) % 4], bd, "saw"), 700) * adsr(int(bd * SR), 0.005, 0.05, 0.7, 0.05) * 0.3, tt)
        tt += beat / 2 * 2 / 2
        i += 1
    return out


def fx_kick():
    d = 0.3
    t = T(d)
    return np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-t * 35)) / SR) * np.exp(-t * 9)


def fx_glitch(dur, s):
    d = 0.45
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(10):
        ln = r.uniform(0.01, 0.05)
        seg = tone(r.uniform(100, 2000), ln, "square") * 0.25 if r.random() < 0.6 else noise(ln, s + i) * 0.2
        place(out, seg, r.uniform(0, d - ln))
    return np.round(out * 8) / 8


def fx_static(dur, s):
    d = dur or 2.0
    r = rng(s)
    x = bp(noise(d, s), 1500, 6000) * 0.12
    for i in range(int(d * 15)):
        place(x, click(0.003, s + i) * r.uniform(0.2, 0.6), r.uniform(0, d - 0.01))
    return fade(x, 0.1, 0.2)


def fx_birds(dur, s):
    d = dur or 4.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    tt = r.uniform(0, 0.6)
    while tt < d - 0.5:
        for j in range(r.integers(2, 5)):
            cd = r.uniform(0.05, 0.1)
            f0 = r.uniform(2500, 3800)
            place(out, sweep(f0, f0 * r.uniform(1.2, 1.6), cd) * np.sin(np.pi * T(cd) / cd) * 0.12, tt + j * 0.12)
        tt += r.uniform(0.7, 1.8)
    return out


def fx_hum(dur, s):
    d = dur or 3.0
    t = T(d)
    x = sum(np.sin(2 * np.pi * 60 * k * t) / k for k in (1, 2, 3, 5)) * 0.15
    x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t)
    return fade(x, 0.4, 0.6)


def fx_traffic(dur, s):
    d = dur or 3.0
    x = lp(noise(d, s), 300) * 0.4
    r = rng(s)
    for i in range(int(d / 1.2)):
        place(x, fx_whoosh(1.2, s + i, lo=150, hi=900) * 0.4, r.uniform(0, max(0.01, d - 1.2)))
    return fade(x * 0.5, 0.3, 0.5)


def fx_servo(dur, s):
    d = dur or 1.5
    t = T(d)
    f = 300 + 200 * np.sin(2 * np.pi * 0.8 * t)
    x = lp(2 * ((np.cumsum(f) / SR) % 1) - 1, 2500) * 0.12
    return fade(x, 0.05, 0.1)


def fx_knock(dur, s):
    d = 0.16
    t = T(d)
    x = lp(noise(d, s), 1500) * np.exp(-t * 40) * 1.4
    x += np.sin(2 * np.pi * 180 * t) * np.exp(-t * 35)
    return x * 0.8


def fx_door(dur, s):
    d = 1.0
    t = T(d)
    f = 340 + 120 * np.sin(2 * np.pi * 0.9 * t) + 25 * np.sin(2 * np.pi * 31 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 * np.sin(np.pi * t / d)
    x += bp(noise(d, s), 300, 1200) * 0.1 * np.sin(np.pi * t / d)
    return x


def fx_pour(dur, s):
    d = 1.2
    x = bp(noise(d, s), 600, 3000) * np.sin(np.pi * T(d) / d) * 0.25
    place(x, fx_bubbles(d, s) * 0.8, 0)
    return x


def fx_clank(dur, s):
    d = 0.5
    x = bell(820, d, partials=((1, 1), (1.55, 0.7), (2.6, 0.5), (3.9, 0.3)), rate=9)
    x[:300] += click(300 / SR, s, 1500, 8000)
    return x * 0.5


def fx_charge(dur, s):
    d = dur or 1.5
    t = T(d)
    x = sweep(150, 900, d) * 0.3 + lp(tone(1, d, "saw") * 0, 100)
    x += bp(noise(d, s), 2000, 6000) * (t / d) * 0.15
    return fade(x * (0.3 + 0.7 * t / d), 0.02, 0.05)


def fx_space(dur, s):
    d = dur or 4.0
    t = T(d)
    x = lp(noise(d, s), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t)) * 0.6
    x += np.sin(2 * np.pi * 55 * t) * 0.1
    return fade(x * 0.5, 0.8, 1.0)


def fx_strain(dur, s):
    d = dur or 1.5
    t = T(d)
    x = lp(noise(d, s), 200) * 0.8 + np.sin(2 * np.pi * np.cumsum(90 + 10 * np.sin(2 * np.pi * 7 * t)) / SR) * 0.2
    return fade(x * 0.5, 0.1, 0.2)


def fx_drone(dur, s):
    d = dur or 2.0
    t = T(d)
    f = 190 * (1 + 0.03 * np.sin(2 * np.pi * 3 * t))
    x = lp(2 * ((np.cumsum(f) / SR) % 1) - 1, 2200) * (0.7 + 0.3 * np.sin(2 * np.pi * 47 * t))
    x += lp(2 * ((np.cumsum(f * 1.5) / SR) % 1) - 1, 2200) * 0.4
    return fade(x * 0.18, 0.15, 0.25)


def fx_crash(dur, s):
    d = 1.0
    t = T(d)
    x = bp(noise(d, s), 800, 6000) * np.exp(-t * 4) * 0.6
    place(x, fx_thud(0, s) * 1.2, 0)
    r = rng(s)
    for i in range(8):
        place(x, click(0.006, s + i, 1500, 6000) * 0.8, r.uniform(0, 0.5))
    return x


def fx_buzz(dur, s):
    d = 0.4
    return lp(tone(110, d, "square") + tone(116, d, "square"), 3000) * adsr(int(d * SR), 0.005, 0.05, 0.8, 0.05) * 0.3


def fx_success(dur, s):
    out = np.zeros(int(1.4 * SR))
    for i, f in enumerate((523.3, 659.3, 784.0, 1046.5)):
        tt = T(0.6)
        note = sum(np.sin(2 * np.pi * f * k * tt) / k * np.exp(-tt * (5 + 3 * k)) for k in range(1, 6))
        place(out, note * 0.35, i * 0.09)
    return out


def fx_shatter(dur, s):
    d = 0.7
    t = T(d)
    x = hp(noise(d, s), 3000) * np.exp(-t * 9) * 0.6
    r = rng(s)
    for i in range(10):
        place(x, bell(r.uniform(3000, 7000), 0.3, rate=14) * 0.12, r.uniform(0, 0.3))
    return x


def fx_clap(dur, s):
    d = 0.25
    t = T(d)
    x = bp(noise(d, s), 800, 5000) * np.exp(-t * 40)
    x += np.sin(2 * np.pi * 300 * t) * np.exp(-t * 30) * 0.5
    return x


def fx_papers(dur, s):
    d = dur or 3.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 4)):
        place(out, fx_page(0, s + i) * r.uniform(0.3, 0.7), r.uniform(0, d - 0.35))
    return out


def fx_heartbeat(dur, s):
    d = dur or 4.0
    out = np.zeros(int(d * SR))
    tt = 0.1
    while tt < d - 0.4:
        for off, a in ((0, 1.0), (0.22, 0.7)):
            beat = np.sin(2 * np.pi * 55 * T(0.15)) * expdec(0.15, 25) * a
            place(out, lp(beat, 200) * 0.9, tt + off)
        tt += 0.85
    return out


def fx_stinger(dur, s):
    d = 1.6
    t = T(d)
    x = np.zeros(int(d * SR))
    place(x, fx_thud(0, s) * 1.2, 0)
    cluster = sum(lp(2 * ((f * t) % 1) - 1, 1500) for f in (146.8, 155.6, 220.0, 233.1))
    x += cluster * np.minimum(t / 0.05, 1) * np.exp(-t * 2.2) * 0.12
    return x


def fx_chaos(dur, s):
    d = dur or 3.0
    t = T(d)
    out = fx_data(d, s) * 1.5
    out += bp(noise(d, s), 500, 4000) * (t / d) * 0.25
    return fade(out, 0.05, 0.3)


def fx_alien(dur, s):
    d = dur or 2.0
    t = T(d)
    f = 700 + 300 * np.sin(2 * np.pi * 1.3 * t) + 40 * np.sin(2 * np.pi * 7 * t)
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.18, 0.1, 0.2)


def fx_ufo(dur, s):
    d = dur or 2.0
    t = T(d)
    f = 900 + 250 * np.sin(2 * np.pi * 9 * t)
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15, 0.2, 0.4)


def fx_crack(dur, s):
    d = 0.4
    t = T(d)
    x = hp(noise(d, s), 1500) * np.exp(-t * 30) * 0.9
    place(x, fx_thud(0, s) * 0.7, 0)
    return x


def fx_dial(dur, s):
    out = np.zeros(int(2.4 * SR))
    for k in range(2):
        d = 0.8
        x = (np.sin(2 * np.pi * 440 * T(d)) + np.sin(2 * np.pi * 480 * T(d))) * 0.1
        place(out, fade(x, 0.01, 0.02), k * 1.3)
    return out


def fx_fastforward(dur, s):
    d = dur or 1.5
    t = T(d)
    f = 1800 + 800 * np.sin(2 * np.pi * 11 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.08
    x += bp(noise(d, s), 2000, 8000) * 0.12
    return fade(x, 0.05, 0.1)


def fx_snore(dur, s):
    d = dur or 2.5
    t = T(d)
    cyc = np.clip(np.sin(2 * np.pi * 0.55 * t), 0, 1)
    x = lp(noise(d, s), 500) * cyc * 0.5
    x += lp(tone(70, d, "saw"), 300) * cyc ** 3 * 0.25
    return fade(x, 0.1, 0.3)


def fx_erase(dur, s):
    return fx_whoosh(0.6, s, lo=800, hi=3500) * 1.1


def fx_roll(dur, s):
    d = dur or 2.0
    t = T(d)
    x = lp(noise(d, s), 250) * (0.3 + 0.7 * t / d) * 0.9
    return fade(x, 0.1, 0.2)


def fx_gulp(dur, s):
    d = 0.3
    t = T(d)
    f = 400 - 250 * np.sin(np.pi * t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.45


def fx_hammer(dur, s):
    d = dur or 2.0
    out = np.zeros(int(d * SR))
    tt = 0.1
    k = 0
    while tt < d - 0.3:
        place(out, fx_clank(0, s + k) * 0.5 + np.pad(fx_knock(0, s + k), (0, int(0.34 * SR))) * 0.6, tt)
        tt += 0.5
        k += 1
    return out


def fx_wind(dur, s):
    d = dur or 4.0
    t = T(d)
    x = bp(noise(d, s), 200, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t)) * 0.3
    return fade(x, 0.6, 0.8)


def fx_night(dur, s):
    d = dur or 6.0
    r = rng(s)
    out = fx_wind(d, s) * 0.3
    tt = 0.3
    while tt < d - 0.5:
        for j in range(3):
            place(out, np.sin(2 * np.pi * 4300 * T(0.04)) * np.sin(np.pi * T(0.04) / 0.04) * 0.05, tt + j * 0.07)
        tt += r.uniform(0.6, 1.3)
    return out


def fx_xray(dur, s):
    d = 1.0
    t = T(d)
    x = sweep(200, 800, d) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * np.sin(np.pi * t / d) * 0.25
    return x


def fx_machine(dur, s):
    d = dur or 2.0
    t = T(d)
    x = lp(tone(80, d, "saw"), 400) * 0.15 * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * t))
    place(x, fx_shimmer(d, s) * 0.8, 0)
    return fade(x, 0.2, 0.3)


def fx_dissolve(dur, s):
    d = dur or 2.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(30):
        f = 4000 * (1 - i / 40)
        place(out, bell(f, 0.3, rate=10) * 0.08, i * d / 32)
    return out


def fx_swell(dur, s):
    d = dur or 2.0
    t = T(d)
    x = hp(noise(d, s), 1500) * (t / d) ** 3 * 0.4
    x += (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 330 * t)) * (t / d) ** 2 * 0.08
    return fade(x, 0.01, 0.08)


def fx_snap(dur, s):
    d = 0.12
    x = click(0.008, s, 800, 5000)
    x = np.pad(x, (0, int(d * SR) - len(x)))
    x += np.sin(2 * np.pi * 700 * T(d)) * expdec(d, 50) * 0.3
    return x


def fx_soft_x(dur, s):
    d = 0.3
    return sweep(330, 200, d) * expdec(d, 10) * 0.3


def fx_camera(dur, s):
    d = 0.18
    x = click(0.006, s, 1500, 9000) * 0.9
    x = np.pad(x, (0, int(d * SR) - len(x)))
    place(x, click(0.01, s + 1, 800, 5000) * 0.6, 0.06)
    place(x, hp(noise(0.08, s + 2), 3000) * expdec(0.08, 40) * 0.3, 0.02)
    return x


def fx_cheer(dur, s):
    d = dur or 2.5
    t = T(d)
    x = bp(noise(d, s), 300, 3000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 5.3 * t) * np.sin(2 * np.pi * 1.1 * t)))
    r = rng(s)
    for i in range(int(d * 6)):
        f0 = r.uniform(500, 1100)
        place(x, sweep(f0, f0 * 1.5, 0.18) * np.sin(np.pi * T(0.18) / 0.18) * 0.15, r.uniform(0, d - 0.2))
    return fade(x * 0.6, 0.15, 0.6)


def fx_applause(dur, s):
    d = dur or 2.5
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 60)):
        place(out, bp(noise(0.02, s + i), 1000, 6000) * expdec(0.02, 150) * r.uniform(0.2, 0.6), r.uniform(0, d - 0.03))
    return fade(out, 0.2, 0.6)


def fx_coins(dur, s):
    d = dur or 1.0
    r = rng(s)
    out = np.zeros(int(d * SR))
    for i in range(int(d * 14)):
        place(out, bell(r.uniform(2500, 4500), 0.25, rate=16) * r.uniform(0.15, 0.35), r.uniform(0, d - 0.25))
    return out


def fx_swish(dur, s):
    return fx_whoosh(0.4, s, lo=1200, hi=5000) * 0.9


def fx_hit(dur, s):
    return fx_thud(dur, s)


def fx_flutter(dur, s):
    """Wing flaps: a burst of short band-passed noise puffs."""
    d = dur or 0.9
    n = noise(d, s)
    t = T(d)
    rate = 14.0
    puffs = np.clip(np.sin(2 * np.pi * rate * t), 0, 1) ** 6
    env = np.clip(1 - t / d, 0, 1) ** 0.7
    return bp(n, 500, 2400) * puffs * env


REGISTRY = {k[3:]: v for k, v in globals().items() if k.startswith("fx_") and callable(v) and k != "fx_kick"}


def make(name, dur=None, seed=0):
    fn = REGISTRY.get(name)
    if fn is None:
        raise KeyError(f"unknown sfx {name!r}")
    x = np.asarray(fn(dur, seed), dtype=np.float64)
    x = np.nan_to_num(x)
    x = fade(x, 0.002, 0.02)
    return norm(x, 0.8).astype(np.float32) if np.max(np.abs(x)) > 0 else x.astype(np.float32)
