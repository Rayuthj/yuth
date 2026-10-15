"""Shared bits for "What If You Could Stop Time?".

Frozen-time language (used in every chapter):
  * the world is drawn with a *world clock* `wt = wtime(T, t_freeze, t_unfreeze)` that decelerates to a stop,
    so rain, birds, walkers and clock hands simply stop where they are;
  * `freeze_wave()` washes everything drawn so far in a cool, desaturated blue (`frost`) inside a ring that expands
    from the snapping hand (and a thaw ring that removes it again);
  * the hero is drawn *after* the frost, in plain black and white with a faint warm "bubble" glow: he is the only
    thing still moving;
  * `frozen_hud()` adds a pause badge (top right) and a frosty vignette while time is stopped;
  * sound: "snap" + "slowmo" when time stops (a ticking clock goes silent), "snap" + "whoosh" when it restarts.
"""
import math

import cairo

from video.chapters.common import Builder, head_at  # noqa: F401
from video.engine.core import *  # noqa: F401,F403
from video.engine.core import text_w, font  # noqa: F401
from video.engine import stickman as sm, props as P, props2 as P2, sets as S, kit as K  # noqa: F401

HERO = ("tuft",)
FRIEND = ("cap",)
SCI = ("labcoat", "glasses")
GOLD = P2.GOLD

ICE = (0.62, 0.86, 1.0)          # accent for frozen things / the title
ICE_D = (0.06, 0.24, 0.45)       # dark outline for ICE text
FROST = (0.55, 0.70, 0.92)       # wash colour of frozen time
WARM = (1.0, 0.85, 0.55)         # the hero's bubble of normal time
DROP = (0.70, 0.86, 1.0)         # raindrops / water
NIGHT_INK = (0.90, 0.90, 1.0)
NIGHT_FILL = (0.05, 0.055, 0.10)

SNAP_KW = dict(a1f=95, a2f=75)   # pose kw: hand raised beside the head to snap
SLOW = 0.32                      # seconds the world takes to decelerate / speed back up


# ---------------------------------------------------------------- world clock
def wtime(T, tf=None, tu=None, slow=SLOW):
    """World time: equals T, decelerates to a stop after tf, stays frozen, and speeds back up after tu."""
    if tf is None or T <= tf:
        return T
    if tu is not None and tu < tf + slow:
        tu = tf + slow
    if tu is None or T < tu:
        dt = min(T - tf, slow)
        return tf + dt - dt * dt / (2 * slow)
    base = tf + slow / 2
    dt = T - tu
    if dt < slow:
        return base + dt * dt / (2 * slow)
    return base + slow / 2 + (dt - slow)


def wvel(T, tf=None, tu=None, slow=SLOW):
    """Speed of the world clock (1 = normal, 0 = frozen)."""
    if tf is None or T <= tf:
        return 1.0
    if tu is not None and tu < tf + slow:
        tu = tf + slow
    if tu is None or T < tu:
        return clamp(1 - (T - tf) / slow)
    return clamp((T - tu) / slow)


def fk(T, tf, tu=None, dur=0.4):
    """0..1 amount of 'frozen look' (for HUD / overlays)."""
    k = ease(prog(T, tf, dur))
    if tu is not None:
        k *= 1 - ease(prog(T, tu, dur))
    return k


# ---------------------------------------------------------------- frozen look
def frost(cr, k=1.0):
    """Cool, desaturating wash over everything drawn so far (k up to ~1.5 for a stronger freeze)."""
    if k <= 0.003:
        return
    src(cr, FROST, 0.25 * min(k, 1.6))
    cr.paint()
    cr.save()
    cr.set_operator(cairo.OPERATOR_MULTIPLY)
    src(cr, (0.78, 0.86, 1.0), clamp(k))
    cr.paint()
    cr.restore()


def _ring(cr, x, y, r, R):
    a = clamp(1 - r / R)
    if a <= 0.01 or r <= 1:
        return
    circle(cr, x, y, r, stroke=ICE, w=46, a=0.18 * a)
    circle(cr, x, y, r, stroke=WHITE, w=9, a=0.85 * a)
    circle(cr, x, y, r * 0.93, stroke=WHITE, w=3, a=0.4 * a)


def freeze_wave(cr, T, t0, x, y, t1=None, speed=3000, R=2600, ring=True):
    """Frozen look expanding as a ring from (x, y) at t0; a thaw ring from t1 removes it.
    Call after drawing the world, before drawing the hero (current coordinates, e.g. inside the camera).
    Returns the amount of frozen look (0..1)."""
    if t0 is None or T < t0:
        return 0.0
    if t1 is not None and T >= t1:
        r2 = (T - t1) * speed
        if r2 >= R:
            return 0.0
        cr.save()
        cr.new_path()
        cr.rectangle(-4000, -4000, 10000, 10000)
        cr.new_sub_path()
        cr.arc(x, y, max(1.0, r2), 0, TAU)
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.clip()
        frost(cr, 1.0)
        cr.restore()
        cr.new_path()
        if ring:
            _ring(cr, x, y, r2, R)
        return clamp(1 - r2 / R)
    r = (T - t0) * speed
    if r < R:
        cr.save()
        cr.new_path()
        cr.arc(x, y, max(1.0, r), 0, TAU)
        cr.clip()
        frost(cr, 1.0)
        cr.restore()
        cr.new_path()
        if ring:
            _ring(cr, x, y, r, R)
        return clamp(r / R)
    frost(cr, 1.0)
    return 1.0


def frozen_hud(cr, k, T=0.0, badge=True, vig=True):
    """Screen-space: frosty vignette + a small pause badge top-right while time is stopped."""
    if k <= 0.01:
        return
    if vig:
        vignette(cr, 0.30 * k, color=(0.85, 0.93, 1.0), inner=0.35)
    if badge:
        kk = back(clamp(k), 2.0)
        with xform(cr, 1832, 86, max(0.01, kk)):
            circle(cr, 0, 0, 44, fill=WHITE, stroke=ICE_D, w=5, a=0.9 * k)
            rrect(cr, -17, -20, 12, 40, 3, fill=ICE_D, a=k)
            rrect(cr, 5, -20, 12, 40, 3, fill=ICE_D, a=k)


def bubble(cr, x, y, r, T, k=1.0, glow_a=0.22):
    """The hero's bubble of normal time: warm glow + a faint shimmering soap-bubble rim."""
    if k <= 0.01:
        return
    glow(cr, x, y, r * 1.15, WARM, glow_a * k)
    for i in range(3):
        hue = [(1.0, 0.75, 0.85), (0.70, 0.95, 1.0), (1.0, 0.95, 0.6)][i]
        a0 = T * (0.6 + 0.2 * i) + i * 2.1
        arc(cr, x, y, r * (1 - 0.012 * i), a0, a0 + 2.2, 4, hue, 0.45 * k)
    circle(cr, x, y, r, stroke=WHITE, w=3, a=0.35 * k)
    arc(cr, x, y, r * 0.86, math.pi * 1.12, math.pi * 1.38, 7, WHITE, 0.45 * k)


def hero_bubble(cr, J, T, k=1.0, s=1.0, glow_a=0.2):
    """Bubble centred on a drawn stickman (joints J)."""
    cx = (J["head"][0] + J["hip"][0]) / 2
    cy = (J["head"][1] + J["hip"][1]) / 2 + 30 * s
    bubble(cr, cx, cy, 230 * s, T, k, glow_a)


def snap_fx(cr, x, y, ts, c=YELLOW, label=True, size=1.0):
    """Finger snap at (x, y): spark lines, a ring and a 'SNAP!' pop. ts = seconds since the snap."""
    if ts < 0 or ts > 1.0:
        return
    burst(cr, x, y, ts, n=10, dist=110 * size, size=12 * size, c=c, dur=0.45, seed=3, shape="line")
    if ts < 0.5:
        circle(cr, x, y, 20 + 140 * eout(ts / 0.5) * size, stroke=WHITE, w=5, a=0.8 * (1 - ts / 0.5))
    if label and ts < 0.9:
        k = back(prog(ts, 0, 0.25), 2.2)
        a = clamp((0.9 - ts) * 4)
        text(cr, "SNAP!", x + 70 * size, y - 70 * size, 52 * size, face=FONT_TITLE, c=c, outline=INK, ow=7, a=a,
             scale=max(0.01, k), rot=-0.12)


# ---------------------------------------------------------------- particles & small props
def drop(cr, x, y, sz=1.0, a=1.0, c=DROP):
    """A single glassy raindrop bead hanging in the air."""
    if a <= 0.01:
        return
    pts = [(x, y - 13 * sz)]
    for i in range(13):
        ang = -0.25 * math.pi + i / 12 * 1.5 * math.pi
        pts.append((x + math.cos(ang) * 7 * sz, y + 3 * sz + math.sin(ang) * 7 * sz))
    polyline(cr, pts, 2.2 * sz, (0.30, 0.48, 0.70), a, closed=True, fill=c, fa=0.85 * a)
    circle(cr, x - 2.5 * sz, y + 1 * sz, 2.2 * sz, fill=WHITE, a=0.95 * a)


def rain(cr, T, tf=None, tu=None, n=110, seed=1, x0=-300, x1=W + 300, y0=-120, y1=1000, speed=1500, s=1.0,
         wave=None, wave_speed=3000, c=DROP, streak_c=(0.45, 0.60, 0.80), slant=0.12):
    """Falling rain that hangs as beads when the world clock stops. wave=(x, y): drops freeze as the ring reaches them."""
    r = rng(seed)
    hgt = y1 - y0
    for i in range(n):
        x = r.uniform(x0, x1)
        ph = r.uniform(0, hgt)
        sz = r.uniform(0.6, 1.25) * s
        sp = speed * r.uniform(0.85, 1.15)
        tfi = tf
        if tf is not None and wave is not None:
            yy = y0 + (ph + tf * sp) % hgt
            tfi = tf + math.hypot(x - wave[0], yy - wave[1]) / wave_speed
        wt = wtime(T, tfi, tu)
        v = wvel(T, tfi, tu)
        y = y0 + (ph + wt * sp) % hgt
        xx = x + (y - y0) * slant
        if v > 0.02:
            ln = (14 + 46 * v) * sz
            line(cr, xx - ln * slant, y - ln, xx, y, 3 * sz, streak_c, 0.65 * v)
        if v < 0.98:
            drop(cr, xx, y, sz, 1 - v, c)


def snow_flour(cr, T, tf=None, n=160, seed=4, x0=0, x1=W, y0=0, y1=H, c=WHITE, size=(2, 6), speed=40, a=0.9):
    """Gentle drifting flakes (flour / snow); they hang still after tf."""
    r = rng(seed)
    wt = wtime(T, tf)
    for i in range(n):
        x = r.uniform(x0, x1)
        ph = r.uniform(0, y1 - y0)
        sz = r.uniform(*size)
        y = y0 + (ph + wt * speed * r.uniform(0.6, 1.4)) % (y1 - y0)
        xx = x + 14 * math.sin(wt * 1.3 + i)
        circle(cr, xx, y, sz, fill=c, a=a * r.uniform(0.6, 1.0))


def bird(cr, x, y, s=1.0, ph=0.0, c=(0.20, 0.22, 0.28), face=1):
    """Flying gull silhouette; ph = wing phase (freeze it to freeze the bird)."""
    f = math.sin(ph)
    with xform(cr, x, y, s, sx=s * face, sy=s):
        for k in (-1, 1):
            pts = bezier_pts([(0, 0), (k * 28, -18 - 26 * f), (k * 62, -8 - 34 * f)], 10)
            polyline(cr, pts, 6, c)
        ellipse(cr, 4, 2, 14, 7, fill=c)
        circle(cr, 16, -1, 5, fill=c)


def flock(cr, wt, n=6, x0=300, y0=200, seed=2, s=1.0, speed=120, c=(0.20, 0.22, 0.28)):
    r = rng(seed)
    for i in range(n):
        bx = x0 + r.uniform(-260, 260) + wt * speed
        by = y0 + r.uniform(-90, 90) + 8 * math.sin(wt * 2 + i)
        bird(cr, bx, by, s * r.uniform(0.7, 1.2), wt * 9 + i * 1.7, c)


def dog(cr, x, y, s=1.0, face=1, leap=0.0, ph=0.0, c=(0.86, 0.66, 0.42), tongue=True):
    """Dog with feet at (x, y). leap 0..1 stretches it into a flying pose."""
    lp = clamp(leap)
    with xform(cr, x, y, s, sx=s * face, sy=s):
        rot = -0.18 * lp
        with xform(cr, 0, -70, 1.0, rot):
            # tail
            polyline(cr, bezier_pts([(-62, -8), (-92, -30 - 10 * math.sin(ph * 6)), (-108, -58)], 8), 9, INK)
            # legs
            sw = math.sin(ph * 8) * 18 * (1 - lp)
            for lx, ang_st, ang_lp in ((40, 0.15, 1.15), (25, -0.1, 1.0), (-38, 0.1, -1.1), (-52, -0.15, -1.25)):
                a = lerp(ang_st, ang_lp, lp) + math.radians(sw) * (1 if lx > 0 else -1)
                line(cr, lx, 10, lx + math.sin(a) * 68, 10 + math.cos(a) * 68, 9, INK)
            ellipse(cr, 0, 0, 72, 30, fill=c, stroke=INK, w=5)
            ellipse(cr, -18, -6, 22, 14, fill=(0.65, 0.45, 0.28))
            # head
            circle(cr, 78, -34, 30, fill=c, stroke=INK, w=5)
            ellipse(cr, 108, -24, 20, 13, fill=c, stroke=INK, w=4)
            circle(cr, 124, -28, 6, fill=INK)
            polyline(cr, [(64, -58), (56, -92), (80, -66)], 4, INK, closed=True, fill=(0.65, 0.45, 0.28))
            circle(cr, 86, -42, 5, fill=INK)
            circle(cr, 87.5, -43.5, 1.6, fill=WHITE)
            if tongue:
                ellipse(cr, 112, -6, 7, 11, fill=(0.95, 0.45, 0.50), stroke=INK, w=2.5)


def ball(cr, x, y, r=20, c=(0.80, 0.92, 0.25)):
    circle(cr, x, y, r, fill=c, stroke=INK, w=4)
    arc(cr, x - r * 1.1, y, r * 0.9, -0.9, 0.9, 3, WHITE)
    arc(cr, x + r * 1.1, y, r * 0.9, math.pi - 0.9, math.pi + 0.9, 3, WHITE)


def coffee_spill(cr, x, y, s=1.0, k=0.5, fall=330):
    """Mug tipping over a table edge at (x, y); the coffee pours down, its front a fraction k of the way down."""
    with xform(cr, x, y, s):
        brown = (0.45, 0.27, 0.12)
        k = clamp(k)
        front = 10 + fall * k
        spine = bezier_pts([(46, -40), (86, -26), (98, front * 0.45), (104, front)], 18)
        left, right = [], []
        for i, (px, py) in enumerate(spine):
            wdt = lerp(15, 7, i / 18)
            left.append((px - wdt, py))
            right.append((px + wdt, py))
        polyline(cr, left + right[::-1], 3, (0.25, 0.14, 0.06), closed=True, fill=brown)
        polyline(cr, [(px + 3, py) for px, py in spine[2:12]], 3, (0.75, 0.55, 0.35), 0.8)
        r = rng(7)
        for i in range(10):
            dx, dy, rr = r.uniform(-40, 46), r.uniform(-20, 60), r.uniform(4, 10)
            circle(cr, 104 + dx, front + dy, rr, fill=brown, stroke=(0.25, 0.14, 0.06), w=2)
        with xform(cr, 6, -46, 1.0, 1.95):
            polyline(cr, [(-40, -52), (-32, 36), (32, 36), (40, -52)], 6, INK, closed=True, fill=WHITE)
            arc(cr, 46, -10, 20, -1.4, 1.4, 6, INK)
            line(cr, -36, -50, 36, -50, 10, brown)


def stopwatch(cr, x, y, r=100, sec=0.0, glow_a=0.0, body=(0.86, 0.88, 0.92), face=WHITE, ink=INK, hand=RED,
              rot=0.0, a=1.0):
    """Chrome stopwatch centred at (x, y); sec = hand position in seconds (60 = one turn)."""
    with group(cr, a):
        with xform(cr, x, y, 1.0, rot):
            if glow_a > 0:
                glow(cr, 0, 0, r * 2.4, ICE, glow_a)
            rect(cr, -r * 0.16, -r * 1.32, r * 0.32, r * 0.26, fill=body, stroke=ink, lw=r * 0.05)
            rrect(cr, -r * 0.28, -r * 1.46, r * 0.56, r * 0.16, r * 0.05, fill=body, stroke=ink, lw=r * 0.05)
            with xform(cr, 0, 0, 1.0, 0.75):
                rect(cr, -r * 0.1, -r * 1.2, r * 0.2, r * 0.22, fill=body, stroke=ink, lw=r * 0.05)
            circle(cr, 0, 0, r * 1.1, fill=body, stroke=ink, w=r * 0.07)
            circle(cr, 0, 0, r * 0.92, fill=face, stroke=ink, w=r * 0.04)
            for i in range(60):
                ang = i / 60 * TAU
                l0 = r * (0.70 if i % 5 == 0 else 0.80)
                line(cr, math.sin(ang) * l0, -math.cos(ang) * l0, math.sin(ang) * r * 0.86, -math.cos(ang) * r * 0.86,
                     r * (0.035 if i % 5 == 0 else 0.015), ink)
            ang = sec / 60 * TAU
            line(cr, -math.sin(ang) * r * 0.18, math.cos(ang) * r * 0.18, math.sin(ang) * r * 0.78,
                 -math.cos(ang) * r * 0.78, r * 0.05, hand)
            circle(cr, 0, 0, r * 0.08, fill=ink)
            arc(cr, 0, 0, r * 1.0, math.pi * 1.15, math.pi * 1.45, r * 0.06, WHITE, 0.6)


def tick_sec(T, tf=None, tu=None):
    """Second-hand position (seconds) that ticks once per second and stops with the world clock."""
    wt = wtime(T, tf, tu)
    return math.floor(wt) + clamp((wt % 1) * 6) ** 2


def umbrella(cr, x, y, s=1.0, c=RED, rot=0.0):
    """Umbrella whose handle end is at (x, y)."""
    with xform(cr, x, y, s, rot):
        line(cr, 0, 0, 0, -150, 5, INK)
        arc(cr, 10, 0, 10, 0, math.pi, 5, INK)
        pts = [(-110, -140)]
        for i in range(21):
            a = math.pi + i / 20 * math.pi
            pts.append((math.cos(a) * 110, -140 + math.sin(a) * 70))
        for i in range(4):
            cx_ = 82 - i * 55
            pts += [(cx_ - 27, -132)]
        pts.append((-110, -140))
        polyline(cr, pts, 5, INK, closed=True, fill=c)
        line(cr, 0, -210, 0, -228, 5, INK)


def clock_tower(cr, x, gy, s=1.0, T=0.0, hours=3, minutes=10, c=(0.80, 0.74, 0.66)):
    """Street clock tower (base at gy) whose seconds hand follows T (pass the world clock)."""
    with xform(cr, x, gy, s):
        rect(cr, -60, -520, 120, 520, fill=c, stroke=INK, lw=5)
        polyline(cr, [(-80, -520), (0, -620), (80, -520)], 5, INK, closed=True, fill=(0.45, 0.30, 0.25))
        P.clock(cr, 0, -430, 52, T, hours=hours, minutes=minutes, speed=1.0)
        rect(cr, -24, -80, 48, 80, fill=(0.45, 0.30, 0.20), stroke=INK, lw=4)


def sunglasses(cr, J, s=1.0, face=1, a=1.0):
    hx, hy = J["head"]
    with group(cr, a):
        for k in (-1, 1):
            ellipse(cr, hx + (11 * face + k * 9) * s, hy - 4 * s, 10 * s, 8 * s, fill=INK)
        line(cr, hx + (11 * face - 9) * s, hy - 6 * s, hx + (11 * face + 9) * s, hy - 6 * s, 3 * s, INK)


def old_marks(cr, J, s=1.0, k=1.0, face=1, ink=INK):
    """Ageing: forehead wrinkles and gray streaks (k 0..1)."""
    if k <= 0.02:
        return
    hx, hy = J["head"]
    for i in range(2):
        yy = hy - (24 - i * 6) * s
        arc(cr, hx + 6 * face * s, yy + 30 * s, 30 * s, -math.pi / 2 - 0.35, -math.pi / 2 + 0.35, 2.4 * s, ink, 0.7 * k)
    for dx in (-14, 0, 12):
        line(cr, hx + dx * s * face, hy - 38 * s, hx + (dx - 4) * s * face, hy - 52 * s, 3 * s, (0.75, 0.75, 0.75), k)


def pause_icon(cr, x, y, s=1.0, c=WHITE, a=1.0, ring=True):
    with xform(cr, x, y, s):
        if ring:
            circle(cr, 0, 0, 90, stroke=c, w=10, a=a)
        rrect(cr, -38, -48, 26, 96, 6, fill=c, a=a)
        rrect(cr, 12, -48, 26, 96, 6, fill=c, a=a)


def play_icon(cr, x, y, s=1.0, c=WHITE, a=1.0):
    with xform(cr, x, y, s):
        circle(cr, 0, 0, 90, stroke=c, w=10, a=a)
        polyline(cr, [(-28, -48), (48, 0), (-28, 48)], 0, c, closed=True, fill=c, fa=a)


def x_out(cr, x, y, k, size=120, c=RED, w=16):
    """Red X drawn over (x, y), k 0..1."""
    if k <= 0:
        return
    partial_line(cr, x - size, y - size, x + size, y + size, clamp(k * 2), w, c)
    partial_line(cr, x + size, y - size, x - size, y + size, clamp(k * 2 - 1), w, c)


def callout(cr, s_, x, y, tx, ty, k, size=44, c=INK, bg=YELLOW):
    """Label box at (x, y) with an arrow to (tx, ty); k = pop amount."""
    if k <= 0:
        return
    arrow(cr, x, y + (34 if ty > y else -34), tx, ty, 6, c, a=clamp(k), head=24, p=clamp(k))
    label_box(cr, s_, x, y, size, c=c, bg=bg, face=FONT_TITLE, bold=False, scale=max(0.01, k))


def frozen_people(cr, wt, n=10, y0=900, y1=1010, seed=3, x0=-100, x1=2020, s0=0.75, s1=0.95, ink=INK, fill=WHITE,
                  skip=(), walk=0.8):
    """Pedestrians walking left/right; they stop dead when the world clock wt stops."""
    r = rng(seed)
    people = []
    accs = [(), ("cap",), ("ponytail",), ("glasses",), ("bun",), ("hat",), ("hair",), ("beard", "glasses")]
    for i in range(n):
        f = r.choice([-1, 1])
        people.append((r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(s0, s1), accs[r.randrange(len(accs))], f,
                       r.uniform(0, 5), i))
    people.sort(key=lambda p: p[1])
    out = []
    for (x, y, s, acc, f, ph, i) in people:
        if i in skip:
            continue
        xx = x + f * sm.stride(walk, s) * wt
        p = sm.pose("stand", x=xx, s=s, face=f, smile=0.3)
        p = sm.walk(p, wt + ph, walk)
        p = sm.on_ground(p, y)
        J = sm.draw(cr, p, ink=ink, fill=fill, acc=acc)
        out.append(J)
    return out


# ---------------------------------------------------------------- the title card
TITLE_TOP = "WHAT IF YOU COULD"
TITLE_BIG = "STOP TIME?"
TITLE_SYMBOLS = ["TICK", "TOCK", "12:00", "PAUSE", "FREEZE", "SNAP", "NOW", "∞", "SECONDS", "HOURS", "WAIT",
                 "STOP", "00:00:00", "FOREVER"]


def TITLE(cr, t, a=1.0):
    """Animated title. t = seconds since the reveal started. Everything freezes when STOP TIME? lands (t = 0.55)."""
    tf = 0.55
    ft = min(t, tf + 0.15 * clamp((t - tf) / 0.15))      # frozen title clock
    vgrad(cr, (0.04, 0.07, 0.14), (0.01, 0.02, 0.05))
    stars(cr, ft, n=220, alpha=0.6)
    sx, sy = shake(t, 14 * max(0.0, 1 - (t - tf) * 3) if t > tf else 0, seed=3)
    with camera(cr, 1 + 0.03 * t, CX - sx, CY - sy):
        # giant clock face behind, its second hand sweeps and stops dead
        cr_r = 430
        circle(cr, CX, CY + 30, cr_r, stroke=ICE, w=6, a=0.16)
        for i in range(60):
            ang = i / 60 * TAU
            l0 = cr_r * (0.86 if i % 5 == 0 else 0.92)
            line(cr, CX + math.sin(ang) * l0, CY + 30 - math.cos(ang) * l0, CX + math.sin(ang) * cr_r * 0.97,
                 CY + 30 - math.cos(ang) * cr_r * 0.97, 6 if i % 5 == 0 else 3, ICE, 0.18)
        ang = (ft * 1.6 + 0.2) * TAU / 6
        line(cr, CX, CY + 30, CX + math.sin(ang) * cr_r * 0.85, CY + 30 - math.cos(ang) * cr_r * 0.85, 6, RED, 0.45)
        radial_lines(cr, CX, CY + 40, ft, n=40, r0=260, c=ICE, a=0.06 * clamp(t * 2), w=14, spin=0.04)
        floating_symbols(cr, ft, TITLE_SYMBOLS, CX, CY + 20, 820, 380, size=44, c=WHITE, a=0.22 * clamp(t * 2),
                         seed=8, speed=0.18, face=FONT_BOLD, italic=False)
        # rain that hangs in the air once the title lands
        r = rng(21)
        for i in range(70):
            x = r.uniform(0, W)
            ph = r.uniform(0, H)
            sz = r.uniform(0.7, 1.5)
            y = (ph + ft * 1300 * r.uniform(0.8, 1.2)) % (H + 100) - 50
            if t < tf:
                line(cr, x, y - 40 * sz, x, y, 3 * sz, ICE, 0.35)
            else:
                drop(cr, x, y, sz, 0.75)
        glow(cr, CX, CY + 80, 520, ICE, 0.22 * clamp((t - 0.5) * 2))
        words = TITLE_TOP.split()
        ws = [text_w(cr, wd, FONT_TITLE, 96) for wd in words]
        gap = 34
        x = CX - (sum(ws) + gap * (len(ws) - 1)) / 2
        for i, wd in enumerate(words):
            k = prog(t, i * 0.08, 0.22)
            if k > 0:
                text(cr, wd, x + ws[i] / 2, CY - 140, 96, c=WHITE, a=a * clamp(k * 2), face=FONT_TITLE,
                     scale=lerp(2.6, 1.0, eout(k)))
            x += ws[i] + gap
        k = prog(t, 0.45, 0.3)
        if k > 0:
            size = 250
            tw = text_w(cr, TITLE_BIG, FONT_TITLE, size)
            if tw > 1700:
                size *= 1700 / tw
            text(cr, TITLE_BIG, CX, CY + 70, size, c=ICE, a=a * clamp(k * 3), face=FONT_TITLE,
                 scale=lerp(3.0, 1.0, back(k, 1.4)), outline=ICE_D, ow=12)
        if t > tf:
            rr = (t - tf) * 2600
            _ring(cr, CX, CY + 70, rr, 2400)
        burst(cr, CX, CY + 70, t - tf - 0.05, n=26, dist=700, size=10, c=ICE, dur=1.1, seed=5)
        burst(cr, CX, CY + 70, t - tf - 0.05, n=18, dist=520, size=12, c=WHITE, dur=0.9, seed=9, shape="line")
        k2 = prog(t, 1.1, 0.5)
        if k2 > 0:
            line(cr, CX - 380 * eout(k2), CY + 230, CX + 380 * eout(k2), CY + 230, 6, WHITE, 0.6 * a)
        if t > tf + 0.2:
            pause_icon(cr, CX, CY + 330, 0.42, c=WHITE, a=0.75 * a * clamp((t - tf - 0.2) * 3))


def night_sky(cr, T, star_a=1.0, hill=True):
    S.night_sky(cr, T, star_a=star_a, hill=hill)


# ---------------------------------------------------------------- posing helpers
def hpose(T, x, gy, g="stand", face=1, s=1.0, idle=True, walk=0.0, talk=None, seed=0, y=None, **kw):
    """Build (don't draw) a stickman pose standing on gy -> use sm.joints(p) before drawing, sm.draw(cr, p) after."""
    p = sm.pose(g, x=x, face=face, s=s, **kw)
    if walk:
        p = sm.walk(p, T + seed, walk)
    elif idle:
        p = sm.idle(p, T, seed)
    if talk is not None:
        p = sm.talk(p, T, talk)
    if y is not None:
        p["y"] = y
    else:
        p = sm.on_ground(p, gy)
    return p


def statue(cr, wt, x, gy, g="stand", face=1, s=1.0, acc=(), seed=0, walk=0.0, **kw):
    """A frozen bystander: posed with the world clock, no idle sway once frozen."""
    p = sm.pose(g, x=x, face=face, s=s, **kw)
    if walk:
        p = sm.walk(p, wt + seed, walk)
    else:
        p = sm.idle(p, wt, seed)
    p = sm.on_ground(p, gy)
    return sm.draw(cr, p, acc=acc)


def frost_outside(cr, x, y, r, k=1.0):
    """Frozen look everywhere except inside the circle (x, y, r): the bubble of normal time."""
    if k <= 0.003:
        return
    cr.save()
    cr.new_path()
    cr.rectangle(-4000, -4000, 10000, 10000)
    cr.new_sub_path()
    cr.arc(x, y, max(1.0, r), 0, TAU)
    cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    cr.clip()
    frost(cr, k)
    cr.restore()
    cr.new_path()


def molecule(cr, x, y, s=1.0, c=(0.55, 0.80, 1.0), a=1.0, rot=0.0):
    """An O2-style air molecule (two joined balls)."""
    with xform(cr, x, y, s, rot):
        circle(cr, -9, 0, 12, fill=c, stroke=INK, w=3, a=a)
        circle(cr, 9, 0, 12, fill=c, stroke=INK, w=3, a=a)


def air(cr, wt, n=60, x0=0, x1=W, y0=0, y1=H, seed=5, s=1.0, c=(0.55, 0.80, 1.0), amp=40, a=1.0, skip=None):
    """Jiggling air molecules driven by world time wt (they freeze when wt stops)."""
    r = rng(seed)
    for i in range(n):
        bx, by = r.uniform(x0, x1), r.uniform(y0, y1)
        f1, f2, p1, p2 = r.uniform(1.5, 3.5), r.uniform(1.5, 3.5), r.uniform(0, 6), r.uniform(0, 6)
        x = bx + amp * math.sin(wt * f1 + p1)
        y = by + amp * math.cos(wt * f2 + p2)
        if skip and skip(x, y):
            continue
        molecule(cr, x, y, s * r.uniform(0.8, 1.1), c, a, rot=wt * r.uniform(-2, 2) + p1)


def photon(cr, x, y, a=1.0, c=YELLOW, s=1.0, ang=0.0, moving=1.0):
    """A packet of light: glowing dot with a short motion streak."""
    if moving > 0.02:
        line(cr, x - math.cos(ang) * 34 * s * moving, y - math.sin(ang) * 34 * s * moving, x, y, 6 * s, c, 0.5 * a)
    glow(cr, x, y, 22 * s, c, 0.6 * a)
    circle(cr, x, y, 7 * s, fill=c if moving > 0.5 else ICE, stroke=INK, w=2, a=a)


def cake(cr, x, y, s=1.0, candles=5, lit=1.0, T=0.0, frozen=False, fire=0.0):
    """Birthday cake with its base at (x, y). fire 0..1 makes the candle flames merge into a blaze."""
    with xform(cr, x, y, s):
        ellipse(cr, 0, 0, 170, 26, fill=WHITE, stroke=INK, w=5)
        rect(cr, -150, -150, 300, 150, fill=(0.95, 0.70, 0.78), stroke=INK, lw=5)
        rect(cr, -150, -78, 300, 18, fill=WHITE)
        for i in range(8):
            circle(cr, -131 + i * 37.5, -150, 14, fill=WHITE)
        ellipse(cr, 0, -150, 150, 22, fill=(0.98, 0.85, 0.88), stroke=INK, w=5)
        r = rng(candles)
        for i in range(candles):
            cx = -120 + 240 * (i + 0.5) / candles + r.uniform(-6, 6)
            cy = -158 + r.uniform(-8, 8)
            rect(cr, cx - 6, cy - 60, 12, 60, fill=[BLUE, YELLOW, GREEN, RED][i % 4], stroke=INK, lw=2.5)
            if lit > 0:
                fl = 1.0 if frozen else 1 + 0.15 * math.sin(T * 17 + i)
                ellipse(cr, cx, cy - 78, 9 * fl, 16 * fl, fill=ORANGE, stroke=None, a=lit)
                ellipse(cr, cx, cy - 74, 4.5, 8, fill=YELLOW, a=lit)
        if fire > 0:
            glow(cr, 0, -260, 260 * fire, ORANGE, 0.6 * fire)
            for i in range(9):
                fl = 1.0 if frozen else 1 + 0.2 * math.sin(T * 13 + i * 1.3)
                hgt = (80 + 60 * math.sin(i * 2.1) ** 2) * fire * fl
                bx = -120 + i * 30
                polyline(cr, [(bx - 26, -200), (bx, -200 - hgt), (bx + 26, -200)], 0, ORANGE, closed=True, fill=ORANGE,
                         fa=0.85)
                polyline(cr, [(bx - 12, -200), (bx, -200 - hgt * 0.6), (bx + 12, -200)], 0, YELLOW, closed=True,
                         fill=YELLOW)


def party_hat(cr, J, s=1.0, c=PURPLE, face=1):
    hx, hy = J["head"]
    polyline(cr, [(hx - 26 * s, hy - 30 * s), (hx + 4 * s * face, hy - 100 * s), (hx + 28 * s, hy - 28 * s)], 3 * s, INK,
             closed=True, fill=c)
    circle(cr, hx + 4 * s * face, hy - 104 * s, 9 * s, fill=YELLOW, stroke=INK, w=2.5 * s)


def school(cr, x, gy, s=1.0, T=0.0, hours=7, minutes=59):
    with xform(cr, x, gy, s):
        rect(cr, -420, -420, 840, 420, fill=(0.88, 0.62, 0.45), stroke=INK, lw=6)
        polyline(cr, [(-460, -420), (0, -600), (460, -420)], 6, INK, closed=True, fill=(0.55, 0.25, 0.20))
        P.clock(cr, 0, -500, 55, T, hours=hours, minutes=minutes)
        rect(cr, -200, -400, 400, 70, fill=WHITE, stroke=INK, lw=5)
        text(cr, "SCHOOL", 0, -365, 50, face=FONT_TITLE)
        for i in range(4):
            for j in range(2):
                if i in (1, 2) and j == 1:
                    continue
                rect(cr, -360 + i * 200, -300 + j * 150, 120, 100, fill=(0.85, 0.93, 1.0), stroke=INK, lw=4)
        rect(cr, -90, -200, 180, 200, fill=(0.45, 0.30, 0.20), stroke=INK, lw=5)


def guitar(cr, x, y, s=1.0, rot=-0.6):
    with xform(cr, x, y, s, rot):
        rect(cr, -9, -170, 18, 140, fill=(0.45, 0.28, 0.15), stroke=INK, lw=4)
        rrect(cr, -18, -205, 36, 40, 8, fill=(0.30, 0.18, 0.10), stroke=INK, lw=4)
        circle(cr, 0, 20, 62, fill=(0.85, 0.45, 0.20), stroke=INK, w=5)
        circle(cr, 0, -30, 46, fill=(0.85, 0.45, 0.20), stroke=INK, w=5)
        circle(cr, 0, 20, 58, fill=(0.85, 0.45, 0.20))
        circle(cr, 0, -10, 18, fill=INK)
        for k in (-4, 4):
            line(cr, k, -200, k, 50, 1.5, LIGHT)


def controller(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        rrect(cr, -110, -50, 220, 100, 50, fill=(0.30, 0.32, 0.40), stroke=INK, lw=5)
        rect(cr, -75, -8, 50, 16, fill=WHITE)
        rect(cr, -58, -25, 16, 50, fill=WHITE)
        for (bx, by, c) in ((60, -18, GREEN), (82, 4, RED), (38, 4, BLUE), (60, 26, YELLOW)):
            circle(cr, bx, by, 10, fill=c, stroke=INK, w=2)
