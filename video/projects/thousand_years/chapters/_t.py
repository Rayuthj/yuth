"""Shared bits for "What If You Lived for 1,000 Years?"."""
import math

from video.chapters.common import Builder, head_at  # noqa: F401
from video.engine.core import *  # noqa: F401,F403
from video.engine.core import text_w, font, star_shape  # noqa: F401
from video.engine import stickman as sm, props as P, props2 as P2, sets as S, kit as K  # noqa: F401

HERO = ("tuft",)
GOLD = P2.GOLD
SEPIA = (0.86, 0.76, 0.58)
SEPIA_D = (0.45, 0.34, 0.22)
HAIR = (0.80, 0.80, 0.82)
STAR = (0.92, 0.94, 1.0)
PALE = (0.9, 0.9, 1.0)
NF = (0.05, 0.055, 0.10)
NIGHT_INK = (0.86, 0.87, 0.92)

TITLE_SYMBOLS = ["BIRTHDAYS", "CENTURIES", "EMPIRES", "LANGUAGES", "SKILLS", "MEMORIES", "FRIENDS", "SUMMERS",
                 "BOOKS", "HISTORY", "FUTURE", "GOODBYES"]
TITLE = K.title_card("WHAT IF YOU LIVED", "1,000 YEARS?", symbols=TITLE_SYMBOLS, big_size=260)


def title_elapsed():
    """Seconds of the title animation already shown when chapter 1 ends (ch02 continues from there)."""
    try:
        from video import timeline as tm
        d = tm.load()["1"]
        end = next(b["end"] for b in d["beats"] if b["id"] == "c1_07")
        return (d["end"] - d["start"]) - (end - 0.2)
    except Exception:  # noqa: BLE001
        return 2.8


# ---------------------------------------------------------------- characters
def gray_hair(cr, J, s=1.0, style="puffs", c=HAIR):
    """Gray hair on a drawn stickman head (puffs on the sides, or a bun)."""
    hc, ang = J["head"], J["ha"]
    r = 40 * s

    def rot(dx, dy):
        cc, ss = math.cos(ang), math.sin(ang)
        return hc[0] + dx * cc - dy * ss, hc[1] + dx * ss + dy * cc

    if style == "bun":
        pts = [rot(math.cos(a) * r * 1.06, math.sin(a) * r * 1.06) for a in
               [math.pi * 1.0 + i * math.pi / 14 for i in range(15)]]
        pts += [rot(r * 0.6, -r * 0.55), rot(0, -r * 0.75), rot(-r * 0.6, -r * 0.55)]
        polyline(cr, pts, 2.5 * s, INK, closed=True, fill=c)
        circle(cr, *rot(0, -r * 1.22), r * 0.36, fill=c, stroke=INK, w=2.5 * s)
    else:
        for k in (-1, 1):
            for (dx, dy, rr) in ((0.98, -0.30, 0.30), (0.90, -0.62, 0.26), (1.02, 0.02, 0.22)):
                circle(cr, *rot(k * dx * r, dy * r), rr * r, fill=c, stroke=INK, w=2.2 * s)
        arc(cr, hc[0], hc[1], r * 0.9, -math.pi / 2 - 0.5 + ang, -math.pi / 2 + 0.5 + ang, 3 * s, (0.6, 0.6, 0.62))


def oldie(cr, T, x, gy, g="stand", face=1, s=1.0, acc=(), style="puffs", cane=True, seed=0, ink=INK, fill=WHITE,
          bend=1.0, alpha=1.0, **kw):
    """An old friend: bent back, gray hair, a cane."""
    kw.setdefault("lean", 14 * bend)
    kw.setdefault("head", 8 * bend)
    if cane and g == "stand":
        kw.setdefault("a1f", 28)
        kw.setdefault("a2f", -8)
    kw.setdefault("l1f", 10)
    kw.setdefault("l2f", -12 * bend)
    kw.setdefault("smile", 0.4)
    J = K.person(cr, T, x, gy, g, face=face, s=s, acc=acc, seed=seed, ink=ink, fill=fill, alpha=alpha, **kw)
    if alpha > 0.01:
        with group(cr, alpha):
            gray_hair(cr, J, s, style)
            if cane:
                hx, hy = J["hand_f"]
                line(cr, hx, hy - 4 * s, hx + 10 * s * face, gy, 6 * s, (0.45, 0.30, 0.18))
                arc(cr, hx - 8 * s * face, hy - 4 * s, 9 * s, math.pi, TAU, 6 * s, (0.45, 0.30, 0.18))
    return J


def kid(cr, T, x, gy, g="stand", face=1, acc=("cap",), seed=0, s=0.62, **kw):
    return K.person(cr, T, x, gy, g, face=face, s=s, acc=acc, seed=seed, **kw)


def crowd(cr, T, n=24, y0=900, y1=1060, seed=3, cheer=0.0, ink=GRAY, s0=0.5, s1=0.75, x0=-100, x1=2020, fill=None,
          old=0.0, face_to=None):
    """A crowd of stickmen; cheer 0..1 raises arms and makes them bounce; old 0..1 adds gray hair."""
    r = rng(seed)
    people = []
    for i in range(n):
        people.append((r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(s0, s1), r.choice([(), ("cap",), ("ponytail",),
                       ("glasses",), ("bun",), ("hat",)]), r.uniform(0, 6), r.random()))
    people.sort(key=lambda p: p[1])
    for i, (x, y, s, acc, ph, ro) in enumerate(people):
        g = "cheer" if cheer > 0.5 and (i % 3 != 1 or cheer > 0.8) else "stand"
        fc = (1 if x < CX else -1) if face_to is None else (1 if x < face_to else -1)
        p = sm.pose(g, x=x, s=s, face=fc, smile=0.4 + 0.5 * cheer)
        if g == "cheer":
            p = sm.apply(p, a1f=150 + 15 * math.sin(T * 8 + ph), a1b=-150 + 15 * math.sin(T * 8 + ph + 1))
        p = sm.idle(p, T, int(ph * 10))
        p = sm.on_ground(p, y)
        if cheer > 0.5:
            p["y"] -= abs(math.sin(T * 6 + ph)) * 18 * s
        J = sm.draw(cr, p, ink=ink, fill=fill or WHITE, acc=acc)
        if ro < old:
            gray_hair(cr, J, s, "bun" if "bun" in acc or "ponytail" in acc else "puffs")


# ---------------------------------------------------------------- small UI pieces
def age_badge(cr, num, x=1740, y=110, k=1.0, label="AGE", c=YELLOW):
    if k <= 0:
        return
    with xform(cr, x, y, max(0.01, k)):
        rrect(cr, -130, -62, 260, 124, 22, fill=INK, stroke=WHITE, lw=5)
        text(cr, label, 0, -32, 28, face=FONT_BOLD, c=(0.8, 0.8, 0.82))
        text(cr, str(num), 0, 18, 66, face=FONT_TITLE, c=c)


def say(cr, txt, x, y, tx, ty, k=1.0, size=40, c=INK, fill=WHITE, face=FONT_HAND, maxw=620, bold=True):
    """Speech bubble that sizes itself to its (wrapped) text."""
    if k <= 0.01:
        return
    rows = wrap(cr, txt, maxw, face, size, bold)
    bw = max(text_w(cr, r_, face, size, bold) for r_ in rows) + 70
    bh = size * 1.2 * len(rows) + 48
    with xform(cr, x, y, max(0.01, k)):
        speech_bubble(cr, 0, 0, bw, bh, (tx - x) / max(0.01, k), (ty - y) / max(0.01, k), fill=fill)
        for i, r_ in enumerate(rows):
            text(cr, r_, 0, (i - (len(rows) - 1) / 2) * size * 1.2, size, face=face, bold=bold, c=c)


def title_text(cr, s, y=200, size=64, c=WHITE, k=1.0, outline=INK, ow=9, x=CX):
    if k > 0:
        text(cr, s, x, y, size, face=FONT_TITLE, c=c, a=clamp(k), outline=outline, ow=ow)


def sparkle(cr, x, y, r, c=WHITE, a=1.0, rot=0.0):
    if r <= 0:
        return
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.22
        ang = rot + i * TAU / 8
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    polyline(cr, pts, 0, c, closed=True, fill=c, fa=a)


def sparkles(cr, T, x, y, rx, ry, n=8, c=YELLOW, a=1.0, seed=1, size=18):
    g = rng(seed)
    for i in range(n):
        px, py = x + g.uniform(-rx, rx), y + g.uniform(-ry, ry)
        tw = 0.5 + 0.5 * math.sin(T * g.uniform(3, 6) + g.uniform(0, 6))
        sparkle(cr, px, py, size * tw, c, a * tw)


def xmark(cr, x, y, size, k, c=RED, w=16):
    """Big red X drawn over something (k 0..1)."""
    if k <= 0:
        return
    partial_line(cr, x - size, y - size, x + size, y + size, clamp(k * 2), w, c)
    partial_line(cr, x + size, y - size, x - size, y + size, clamp(k * 2 - 1), w, c)


def rain(cr, T, x0=-200, x1=2120, y0=-50, y1=1100, n=140, c=(0.7, 0.75, 0.85), a=0.6, seed=4):
    g = rng(seed)
    for i in range(n):
        x = g.uniform(x0, x1)
        sp = g.uniform(900, 1300)
        y = y0 + (g.uniform(0, y1 - y0) + T * sp) % (y1 - y0)
        line(cr, x, y, x - 8, y + 34, 3, c, a)


# ---------------------------------------------------------------- props
def cake(cr, x, y, s=1.0, candles=5, t=0.0, lit=1.0, top_c=(1.0, 0.75, 0.82), base_c=(0.98, 0.92, 0.80),
         number=None):
    """Two-tier birthday cake, base at bottom. number='1000' puts number candles on top."""
    with xform(cr, x, y, s):
        ellipse(cr, 0, 2, 200, 22, fill=LIGHT, stroke=INK, w=4)
        rrect(cr, -170, -120, 340, 120, 18, fill=base_c, stroke=INK, lw=5)
        rrect(cr, -110, -210, 220, 95, 16, fill=top_c, stroke=INK, lw=5)
        for k in range(7):
            xx = -150 + k * 50
            polyline(cr, bezier_pts([(xx - 20, -120), (xx, -84 - (k % 2) * 14), (xx + 20, -120)], 8), 0, INK, closed=True,
                     fill=(1.0, 1.0, 1.0))
        for k in range(5):
            circle(cr, -90 + k * 45, -60, 8, fill=[RED, BLUE, GREEN, ORANGE, PURPLE][k])
        if number:
            n = len(number)
            for i, ch in enumerate(number):
                cx_ = (i - (n - 1) / 2) * 52
                rrect(cr, cx_ - 22, -290, 44, 80, 8, fill=[BLUE, RED, GREEN, ORANGE][i % 4], stroke=INK, lw=3)
                text(cr, ch, cx_, -250, 52, face=FONT_TITLE, c=WHITE)
                if lit > 0:
                    fl = 1 + 0.15 * math.sin(t * 17 + i * 2)
                    glow(cr, cx_, -312, 40, YELLOW, 0.5 * lit)
                    ellipse(cr, cx_, -312, 9 * fl, 15 * fl, fill=ORANGE, a=lit)
                    ellipse(cr, cx_, -309, 4, 8, fill=YELLOW, a=lit)
        else:
            n = max(1, candles)
            for i in range(n):
                cx_ = -90 + 180 * (i + 0.5) / n
                rect(cr, cx_ - 6, -262, 12, 52, fill=[BLUE, RED, GREEN, YELLOW, PURPLE][i % 5], stroke=INK, lw=2.5)
                if lit > 0:
                    fl = 1 + 0.15 * math.sin(t * 17 + i * 2)
                    glow(cr, cx_, -278, 30, YELLOW, 0.45 * lit)
                    ellipse(cr, cx_, -278, 7 * fl, 12 * fl, fill=ORANGE, a=lit)
                    ellipse(cr, cx_, -275, 3, 6, fill=YELLOW, a=lit)


def pizza(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        polyline(cr, [(-50, -40), (50, -40), (0, 80)], 4, INK, closed=True, fill=(1.0, 0.82, 0.35))
        rrect(cr, -58, -54, 116, 22, 10, fill=(0.85, 0.55, 0.25), stroke=INK, lw=4)
        for (px, py) in ((-18, -14), (16, -6), (0, 30)):
            circle(cr, px, py, 10, fill=RED, stroke=INK, w=2)


def shark(cr, x, y, s=1.0, t=0.0, face=1, c=(0.45, 0.47, 0.50), belly=(0.70, 0.71, 0.72)):
    """Greenland shark: a chunky, slow, gray giant."""
    sw = math.sin(t * 1.6)
    with xform(cr, x, y, s, sx=s * face, sy=s):
        tail = [(-300, 0), (-420, -90 + 10 * sw), (-395, 0), (-430, 80 + 10 * sw)]
        polyline(cr, tail, 5, INK, closed=True, fill=c)
        polyline(cr, [(-60, -70), (-20, -140), (50, -80)], 5, INK, closed=True, fill=c)
        polyline(cr, [(-210, -40), (-185, -85), (-150, -50)], 4, INK, closed=True, fill=c)
        polyline(cr, [(30, 40), (-10, 120 + 8 * sw), (110, 50)], 5, INK, closed=True, fill=c)
        body = bezier_pts([(-320, 0), (-200, -95), (80, -110), (230, -40), (260, 10)], 30) + \
            bezier_pts([(260, 10), (200, 70), (-120, 75), (-320, 0)], 30)
        polyline(cr, body, 5, INK, closed=True, fill=c)
        polyline(cr, bezier_pts([(-200, 30), (0, 75), (200, 40)], 20) + [(150, 55), (-120, 60)], 0, INK, closed=True,
                 fill=belly)
        for k in range(4):
            line(cr, 120 + k * 16, -30, 116 + k * 16, 20, 3, INK, 0.6)
        circle(cr, 200, -30, 7, fill=INK)
        circle(cr, 202, -32, 2, fill=WHITE)
        arc(cr, 238, 18, 18, 1.8, 2.9, 4, INK)
        g = rng(3)
        for i in range(14):
            circle(cr, g.uniform(-250, 150), g.uniform(-70, 20), g.uniform(4, 8), fill=(0.38, 0.40, 0.43))


def bristlecone(cr, x, y, s=1.0, t=0.0):
    """Gnarled, twisted bristlecone pine, base at ground."""
    wood = (0.80, 0.70, 0.55)
    wood_d = (0.55, 0.42, 0.30)
    needle = (0.20, 0.45, 0.30)
    with xform(cr, x, y, s):
        trunk = bezier_pts([(-110, 0), (-60, -80), (-120, -170), (-40, -260), (-80, -340)], 24) + \
            bezier_pts([(-30, -360), (20, -260), (-20, -170), (60, -90), (90, 0)], 24)
        polyline(cr, trunk, 6, INK, closed=True, fill=wood)
        for (a, b_, c_) in (((-70, -40), (-50, -150), (-60, -240)), ((10, -30), (-10, -140), (-40, -290)),
                            ((40, -40), (0, -120), (10, -200))):
            polyline(cr, bezier_pts([a, b_, c_], 12), 4, wood_d)
        branches = [[(-60, -250), (-170, -300), (-240, -280)], [(-50, -320), (-20, -420), (40, -450)],
                    [(0, -200), (110, -250), (180, -240)], [(-90, -160), (-200, -170), (-230, -210)]]
        for br in branches:
            polyline(cr, bezier_pts(br, 12), 16, INK)
            polyline(cr, bezier_pts(br, 12), 9, wood)
        sw = math.sin(t * 1.1) * 3
        for (bx, by, r_) in ((-240, -285, 46), (40, -455, 52), (185, -245, 48), (-235, -215, 36), (80, -430, 34),
                             (-200, -305, 34)):
            for k in range(7):
                a = k / 7 * TAU
                ellipse(cr, bx + sw + math.cos(a) * r_ * 0.45, by + math.sin(a) * r_ * 0.35, r_ * 0.55, r_ * 0.28,
                        fill=needle, stroke=INK, w=2.5, rot=a)
        rect(cr, -200, -6, 360, 14, fill=(0.62, 0.55, 0.48))


def certificate(cr, x, y, s=1.0, title="BIRTH CERTIFICATE", rows=(), big=None, rot=0.0, stamp_k=0.0):
    with xform(cr, x, y, s, rot):
        rect(cr, -280, -340, 560, 680, fill=(0.98, 0.96, 0.88), stroke=INK, lw=6)
        rect(cr, -250, -310, 500, 620, stroke=(0.75, 0.62, 0.35), lw=5)
        text(cr, title, 0, -250, 40, face=FONT_SERIF, bold=True)
        line(cr, -200, -210, 200, -210, 3, MID)
        for i, (lab, val) in enumerate(rows):
            yy = -150 + i * 70
            text(cr, lab, -220, yy, 30, face=FONT_BOLD, c=GRAY, align="left")
            text(cr, val, 220, yy, 34, face=FONT_HAND, bold=True, align="right")
            line(cr, -220, yy + 26, 220, yy + 26, 2, LIGHT)
        if big:
            text(cr, big, 0, 200, 120, face=FONT_TITLE, c=RED)
        if stamp_k > 0:
            circle(cr, 170, 250, 50, stroke=RED, w=6, a=stamp_k)


def gravestone(cr, x, y, s=1.0, txt="R.I.P.", sub=None, c=(0.72, 0.73, 0.76), a=1.0, flowers=False):
    """Base at ground."""
    with group(cr, a):
        with xform(cr, x, y, s):
            pts = [(-80, 0), (-80, -150)] + [(math.cos(an) * 80, -150 + math.sin(an) * 80)
                                             for an in [math.pi + i * math.pi / 16 for i in range(17)]] + [(80, 0)]
            polyline(cr, pts, 5, INK, closed=True, fill=c)
            text(cr, txt, 0, -150, 30 if len(txt) <= 5 else 22, face=FONT_TITLE, c=(0.30, 0.30, 0.34))
            if sub:
                text(cr, sub, 0, -100, 24, face=FONT_BOLD, c=(0.35, 0.35, 0.40))
            if flowers:
                for k, cc in ((-40, RED), (-20, YELLOW), (30, (1.0, 0.6, 0.75))):
                    line(cr, k, 0, k + 4, -34, 3, GREEN)
                    circle(cr, k + 4, -38, 9, fill=cc, stroke=INK, w=2)


def journal(cr, x, y, s=1.0, c=(0.55, 0.25, 0.20), rot=0.0, label=None):
    with xform(cr, x, y, s, rot):
        rrect(cr, -50, -70, 100, 140, 6, fill=c, stroke=INK, lw=4)
        rect(cr, -50, -70, 16, 140, fill=tuple(v * 0.7 for v in c))
        rect(cr, -20, -40, 56, 24, fill=(0.95, 0.90, 0.75), stroke=INK, lw=2)
        if label:
            text(cr, label, 8, -28, 16, face=FONT_BOLD)


JOURNAL_C = [(0.55, 0.25, 0.20), (0.20, 0.35, 0.55), (0.25, 0.45, 0.30), (0.50, 0.40, 0.20), (0.40, 0.25, 0.45),
             (0.60, 0.45, 0.30)]


def journal_stack(cr, x, y, s=1.0, n=8, seed=1):
    """Stack of journals lying flat, base at bottom."""
    g = rng(seed)
    with xform(cr, x, y, s):
        for i in range(n):
            c = JOURNAL_C[g.randrange(len(JOURNAL_C))]
            w_ = g.uniform(120, 150)
            dx = g.uniform(-10, 10)
            rrect(cr, -w_ / 2 + dx, -(i + 1) * 30, w_, 28, 4, fill=c, stroke=INK, lw=3)
            line(cr, -w_ / 2 + dx + 8, -(i + 1) * 30 + 14, w_ / 2 + dx - 8, -(i + 1) * 30 + 14, 2,
                 (0.95, 0.90, 0.75), 0.7)


def photo(cr, x, y, w=220, h=180, rot=0.0, inner=None, sepia=True, s=1.0, a=1.0, fade=0.0):
    """Old photograph with white border; inner(cr, w, h) draws the picture centred at the origin."""
    with group(cr, a):
        with xform(cr, x, y, s, rot):
            rect(cr, -w / 2 - 14, -h / 2 - 14, w + 28, h + 44, fill=(0.97, 0.95, 0.90), stroke=INK, lw=4)
            rect(cr, -w / 2, -h / 2, w, h, fill=SEPIA if sepia else (0.80, 0.90, 1.0))
            if inner:
                cr.save()
                cr.rectangle(-w / 2, -h / 2, w, h)
                cr.clip()
                inner(cr, w, h)
                cr.restore()
                cr.new_path()
            if fade > 0:
                rect(cr, -w / 2, -h / 2, w, h, fill=(0.97, 0.95, 0.90), a=fade)
            rect(cr, -w / 2, -h / 2, w, h, stroke=INK, lw=3)


def portrait(acc=(), old=False, ink=SEPIA_D, n=1, seed=0, hat=None):
    """inner() for photo(): one or more little figures in sepia ink."""
    def inner(cr, w, h):
        for i in range(n):
            dx = (i - (n - 1) / 2) * (w / max(1, n)) * 0.9
            ss = 0.42 * h / 180 * (1.0 if n == 1 else 0.85)
            p = sm.pose("front", x=dx, s=ss, smile=0.5, fo=0.0)
            p = sm.on_ground(p, h / 2 + 30 * ss)
            a_ = acc[i % len(acc)] if acc and isinstance(acc[0], tuple) else acc
            J = sm.draw(cr, p, ink=ink, fill=(0.93, 0.86, 0.70), acc=a_)
            if old:
                gray_hair(cr, J, ss, "puffs", c=(0.95, 0.92, 0.85))
    return inner


def photo_box(cr, x, y, s=1.0, open_=1.0):
    """Cardboard box of old photos, base at bottom."""
    with xform(cr, x, y, s):
        for i, (dx, rot) in enumerate(((-60, -0.2), (10, 0.1), (60, -0.05), (-20, 0.25))):
            if open_ > 0.3:
                photo(cr, dx, -150 - i * 6, 90, 70, rot, inner=portrait(n=1 + i % 2, acc=[("hat",), ("bun",)]), s=1.0)
        rect(cr, -150, -140, 300, 140, fill=(0.75, 0.58, 0.38), stroke=INK, lw=5)
        polyline(cr, [(-150, -140), (-190, -190 * open_ - 120 * (1 - open_)), (-40, -190 * open_ - 120 * (1 - open_)),
                      (0, -140)], 4, INK, closed=True, fill=(0.68, 0.50, 0.32))
        rrect(cr, -70, -95, 140, 50, 6, fill=(0.95, 0.92, 0.85), stroke=INK, lw=3)
        text(cr, "PHOTOS", 0, -70, 26, face=FONT_HAND, bold=True)


def tv(cr, x, y, w=560, h=380, screen=None, s=1.0, legs=True):
    """Retro TV; screen(cr, w, h) draws centred at the origin, clipped."""
    with xform(cr, x, y, s):
        rrect(cr, -w / 2 - 30, -h / 2 - 30, w + 60, h + 60, 30, fill=(0.55, 0.38, 0.25), stroke=INK, lw=6)
        rrect(cr, -w / 2, -h / 2, w, h, 26, fill=(0.12, 0.14, 0.18))
        if screen:
            cr.save()
            rrect_path(cr, -w / 2, -h / 2, w, h, 26)
            cr.clip()
            screen(cr, w, h)
            cr.restore()
            cr.new_path()
        rrect(cr, -w / 2, -h / 2, w, h, 26, stroke=INK, lw=5)
        line(cr, -60, -h / 2 - 30, -120, -h / 2 - 120, 5, INK)
        line(cr, 60, -h / 2 - 30, 120, -h / 2 - 120, 5, INK)
        if legs:
            line(cr, -w / 2 + 30, h / 2 + 30, -w / 2 + 10, h / 2 + 90, 8, INK)
            line(cr, w / 2 - 30, h / 2 + 30, w / 2 - 10, h / 2 + 90, 8, INK)


def couch(cr, x, y, s=1.0, c=(0.35, 0.50, 0.70)):
    """Base at floor; seat top ~ y-150."""
    with xform(cr, x, y, s):
        rrect(cr, -260, -300, 520, 170, 30, fill=c, stroke=INK, lw=5)
        rrect(cr, -290, -170, 580, 110, 24, fill=c, stroke=INK, lw=5)
        rrect(cr, -320, -230, 70, 170, 24, fill=c, stroke=INK, lw=5)
        rrect(cr, 250, -230, 70, 170, 24, fill=c, stroke=INK, lw=5)
        line(cr, -250, -60, -250, 0, 8, INK)
        line(cr, 250, -60, 250, 0, 8, INK)


def steam_train(cr, x, y, s=1.0, t=0.0, face=-1, cars=2, smoke=1.0):
    """Base at rails."""
    with xform(cr, x, y, s, sx=s * face, sy=s):
        for i in range(cars):
            cx0 = -380 - i * 330
            rrect(cr, cx0 - 140, -230, 280, 170, 14, fill=(0.55, 0.15, 0.15), stroke=INK, lw=5)
            for k in range(3):
                rect(cr, cx0 - 110 + k * 80, -200, 60, 60, fill=(0.95, 0.85, 0.55), stroke=INK, lw=3)
            for wx in (-90, 90):
                circle(cr, cx0 + wx, -45, 38, fill=INK)
                circle(cr, cx0 + wx, -45, 14, fill=MID)
        rrect(cr, -200, -300, 150, 240, 10, fill=(0.20, 0.22, 0.26), stroke=INK, lw=5)
        rect(cr, -180, -270, 110, 70, fill=(0.95, 0.85, 0.55), stroke=INK, lw=3)
        rrect(cr, -60, -200, 280, 140, 60, fill=(0.25, 0.27, 0.32), stroke=INK, lw=5)
        rect(cr, 120, -300, 50, 110, fill=(0.20, 0.22, 0.26), stroke=INK, lw=5)
        rect(cr, 105, -320, 80, 26, fill=(0.20, 0.22, 0.26), stroke=INK, lw=5)
        polyline(cr, [(220, -60), (290, -10), (220, -10)], 5, INK, closed=True, fill=RED)
        circle(cr, 215, -150, 22, fill=YELLOW, stroke=INK, w=4)
        for wx, r_ in ((-130, 50), (20, 50), (150, 38)):
            circle(cr, wx, -50, r_, fill=INK)
            circle(cr, wx, -50, r_ * 0.4, fill=RED)
            a = -t * 9
            line(cr, wx, -50, wx + math.cos(a) * r_ * 0.8, -50 + math.sin(a) * r_ * 0.8, 6, MID)
        line(cr, -130 + math.cos(-t * 9) * 40, -50 + math.sin(-t * 9) * 40, 150 + math.cos(-t * 9) * 30,
             -50 + math.sin(-t * 9) * 30, 8, (0.7, 0.7, 0.72))
        if smoke > 0:
            for i in range(7):
                f = (t * 0.9 + i / 7) % 1
                circle(cr, 145 - 380 * f, -340 - 140 * f + 20 * math.sin(i * 2 + t), 30 + 60 * f, fill=(0.85, 0.85, 0.87),
                       a=smoke * (1 - f) * 0.9)


def candlestick_phone(cr, x, y, s=1.0):
    """Base at bottom."""
    with xform(cr, x, y, s):
        ellipse(cr, 0, -10, 70, 18, fill=INK)
        rect(cr, -12, -200, 24, 190, fill=INK)
        polyline(cr, [(-40, -260), (40, -260), (25, -200), (-25, -200)], 4, INK, closed=True, fill=INK)
        circle(cr, 0, -262, 36, fill=(0.25, 0.25, 0.28), stroke=INK, w=4)
        line(cr, 70, -170, 110, -120, 6, INK)
        rrect(cr, 60, -200, 30, 90, 12, fill=INK)


def biplane(cr, x, y, s=1.0, t=0.0, rot=0.0, c=(0.85, 0.30, 0.25)):
    with xform(cr, x, y, s, rot):
        rrect(cr, -150, -18, 260, 40, 18, fill=c, stroke=INK, lw=5)
        polyline(cr, [(-150, 0), (-200, -50), (-180, 10)], 5, INK, closed=True, fill=c)
        for yy in (-70, 40):
            rrect(cr, -70, yy, 150, 20, 8, fill=(0.95, 0.85, 0.5), stroke=INK, lw=4)
        line(cr, -40, -50, -40, 40, 4, INK)
        line(cr, 50, -50, 50, 40, 4, INK)
        w_ = 70 * abs(math.cos(t * 30))
        line(cr, 118, -w_, 118, w_, 6, INK)
        circle(cr, 112, 2, 9, fill=INK)


def jet(cr, x, y, s=1.0, rot=0.0, c=WHITE):
    with xform(cr, x, y, s, rot):
        polyline(cr, [(-60, -10), (60, -100), (95, -100), (40, -10)], 4, INK, closed=True, fill=LIGHT)
        rrect(cr, -200, -30, 400, 60, 30, fill=c, stroke=INK, lw=5)
        polyline(cr, [(-190, -20), (-230, -90), (-180, -90), (-130, -25)], 4, INK, closed=True, fill=RED)
        for i in range(6):
            circle(cr, -90 + i * 40, -6, 8, fill=(0.6, 0.8, 1.0), stroke=INK, w=2)
        polyline(cr, [(-40, 15), (60, 90), (95, 90), (40, 15)], 4, INK, closed=True, fill=LIGHT)


def rocket(cr, x, y, s=1.0, t=0.0, flame=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        if flame > 0:
            fl = 1 + 0.2 * math.sin(t * 30)
            polyline(cr, [(-30, 100), (0, 100 + 110 * fl * flame), (30, 100)], 0, INK, closed=True, fill=ORANGE)
            polyline(cr, [(-16, 100), (0, 100 + 60 * fl * flame), (16, 100)], 0, INK, closed=True, fill=YELLOW)
        polyline(cr, [(-50, 60), (-90, 110), (-45, 100)], 4, INK, closed=True, fill=RED)
        polyline(cr, [(50, 60), (90, 110), (45, 100)], 4, INK, closed=True, fill=RED)
        polyline(cr, bezier_pts([(-50, 100), (-60, -60), (0, -170)], 16) + bezier_pts([(0, -170), (60, -60), (50, 100)], 16),
                 5, INK, closed=True, fill=WHITE)
        circle(cr, 0, -40, 24, fill=(0.6, 0.85, 1.0), stroke=INK, w=5)


def dome_city(cr, x, y, s=1.0, t=0.0):
    """Mars base: glass domes; base at ground."""
    with xform(cr, x, y, s):
        for (dx, r_) in ((-170, 110), (60, 160), (250, 90)):
            cr.new_path()
            cr.arc(dx, 0, r_, math.pi, 0)
            cr.close_path()
            src(cr, (0.75, 0.90, 1.0), 0.55)
            cr.fill()
            P.skyline(cr, dx - r_ * 0.7, 0, r_ * 1.4, r_ * 0.75, seed=int(dx) % 7 + 2, fill=(0.55, 0.60, 0.70),
                      lit=True, t=t)
            arc(cr, dx, 0, r_, math.pi, TAU, 5, INK)
            arc(cr, dx - r_ * 0.3, -r_ * 0.2, r_ * 0.6, math.pi * 1.2, math.pi * 1.45, 4, WHITE, 0.7)
        line(cr, -300, 0, 360, 0, 5, INK)


def piggy(cr, x, y, s=1.0, c=(1.0, 0.70, 0.78), rot=0.0):
    """Piggy bank, base at bottom."""
    with xform(cr, x, y, s, rot):
        for lx in (-60, -25, 30, 65):
            rrect(cr, lx - 14, -40, 28, 42, 8, fill=c, stroke=INK, lw=4)
        ellipse(cr, 0, -100, 130, 85, fill=c, stroke=INK, w=5)
        ellipse(cr, 130, -95, 26, 32, fill=c, stroke=INK, w=5)
        circle(cr, 124, -100, 5, fill=INK)
        circle(cr, 138, -90, 5, fill=INK)
        polyline(cr, [(55, -170), (75, -215), (95, -160)], 5, INK, closed=True, fill=c)
        circle(cr, 70, -125, 9, fill=INK)
        rrect(cr, -40, -186, 80, 12, 6, fill=INK)
        polyline(cr, bezier_pts([(-128, -110), (-165, -140), (-150, -90), (-175, -100)], 12), 5, INK)


def banknote(cr, x, y, s=1.0, rot=0.0, c=(0.55, 0.78, 0.50), a=1.0, label="$"):
    with group(cr, a):
        with xform(cr, x, y, s, rot):
            rrect(cr, -90, -45, 180, 90, 6, fill=c, stroke=INK, lw=4)
            rrect(cr, -76, -33, 152, 66, 4, stroke=(0.25, 0.45, 0.28), lw=3)
            circle(cr, 0, 0, 24, fill=(0.80, 0.92, 0.78), stroke=(0.25, 0.45, 0.28), w=3)
            text(cr, label, 0, 0, 30, face=FONT_TITLE, c=(0.20, 0.42, 0.25))


def money_pile(cr, x, y, s=1.0, seed=2, c=(0.55, 0.78, 0.50)):
    """Heap of bill bundles; base at bottom, about 600 wide and 330 tall at s=1."""
    g = rng(seed)
    with xform(cr, x, y, s):
        rows = 7
        for r_ in range(rows):
            n = rows - r_
            for k in range(n):
                cx_ = (k - (n - 1) / 2) * 86 + g.uniform(-8, 8)
                cy_ = -24 - r_ * 44 + g.uniform(-4, 4)
                rrect(cr, cx_ - 42, cy_ - 20, 84, 40, 5, fill=c, stroke=INK, lw=3)
                rect(cr, cx_ - 9, cy_ - 20, 18, 40, fill=(0.88, 0.95, 0.85))
        text(cr, "$", 0, -rows * 44 - 10, 44, face=FONT_TITLE, c=(0.2, 0.45, 0.25))


def bank(cr, x, y, s=1.0, crack=0.0, t=0.0, label="BANK"):
    """Classical bank, base at ground. crack 0..1 collapses it."""
    with xform(cr, x, y, s):
        c = (0.88, 0.86, 0.80)
        rect(cr, -300, -40, 600, 40, fill=c, stroke=INK, lw=5)
        for i in range(6):
            fall = clamp(crack * 1.6 - (i % 3) * 0.25)
            rx = -250 + i * 100
            with xform(cr, rx, -40, 1.0, (0.5 if i % 2 else -0.6) * ease(fall)):
                rect(cr, -22, -260 + 200 * ease(fall) * 0.0, 44, 260 - 0, fill=c, stroke=INK, lw=4)
        dy = 220 * ease(crack)
        with xform(cr, 0, dy, 1.0, 0.12 * ease(crack)):
            rect(cr, -320, -330, 640, 40, fill=c, stroke=INK, lw=5)
            polyline(cr, [(-330, -330), (0, -450), (330, -330)], 5, INK, closed=True, fill=c)
            text(cr, label, 0, -372, 44, face=FONT_TITLE, c=(0.35, 0.35, 0.38))
        if 0 < crack < 1:
            for i in range(6):
                g = rng(i)
                circle(cr, g.uniform(-300, 300), -g.uniform(0, 200) * (1 - crack), 30 + 60 * crack, fill=(0.75, 0.72, 0.65),
                       a=0.6 * (1 - crack))


def mortarboard(cr, J, s=1.0, c=INK):
    hx, hy = J["head"]
    polyline(cr, [(hx - 62 * s, hy - 46 * s), (hx, hy - 70 * s), (hx + 62 * s, hy - 46 * s), (hx, hy - 24 * s)],
             3 * s, INK, closed=True, fill=c)
    rect(cr, hx - 26 * s, hy - 44 * s, 52 * s, 18 * s, fill=c)
    line(cr, hx, hy - 48 * s, hx + 52 * s, hy - 30 * s, 3 * s, YELLOW)
    line(cr, hx + 52 * s, hy - 30 * s, hx + 54 * s, hy + 6 * s, 4 * s, YELLOW)


def name_tag(cr, J, txt, s=1.0, k=1.0):
    if k <= 0:
        return
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    x, y = lerp(nx, hx, 0.35), lerp(ny, hy, 0.35)
    with xform(cr, x, y, max(0.01, k) * s):
        rrect(cr, -60, -36, 120, 72, 8, fill=WHITE, stroke=INK, lw=3)
        rrect(cr, -60, -36, 120, 22, 6, fill=RED)
        text(cr, "HELLO, I'M", 0, -25, 12, face=FONT_BOLD, c=WHITE)
        text(cr, txt, 0, 12, 26, face=FONT_HAND, bold=True)


def suitcase(cr, x, y, s=1.0, c=(0.62, 0.38, 0.22)):
    with xform(cr, x, y, s):
        rrect(cr, -55, -80, 110, 80, 10, fill=c, stroke=INK, lw=4)
        arc(cr, 0, -80, 18, math.pi, TAU, 5, INK)
        line(cr, -55, -50, 55, -50, 3, INK)


def guitar(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rect(cr, -8, -170, 16, 120, fill=(0.45, 0.30, 0.18), stroke=INK, lw=3)
        rrect(cr, -16, -200, 32, 34, 6, fill=(0.35, 0.22, 0.12), stroke=INK, lw=3)
        circle(cr, 0, -20, 48, fill=(0.85, 0.50, 0.20), stroke=INK, w=4)
        circle(cr, 0, 30, 58, fill=(0.85, 0.50, 0.20), stroke=INK, w=4)
        rect(cr, -40, 0, 80, 40, fill=(0.85, 0.50, 0.20))
        circle(cr, 0, -5, 16, fill=INK)
        line(cr, -24, 50, 24, 50, 5, INK)


def pan(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        line(cr, 40, 0, 140, 0, 12, INK)
        ellipse(cr, 0, 0, 60, 22, fill=(0.3, 0.3, 0.34), stroke=INK, w=4)
        ellipse(cr, 0, -3, 22, 10, fill=YELLOW)
        circle(cr, 0, -3, 7, fill=ORANGE)


def blueprint_roll(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rect(cr, -120, -80, 240, 160, fill=(0.25, 0.45, 0.80), stroke=INK, lw=4)
        for k in range(5):
            line(cr, -100, -60 + k * 30, 100, -60 + k * 30, 2, WHITE, 0.6)
        polyline(cr, [(-60, 50), (-60, -20), (0, -55), (60, -20), (60, 50)], 4, WHITE)
        ellipse(cr, -120, 0, 14, 80, fill=(0.85, 0.90, 1.0), stroke=INK, w=3)


def stethoscope(cr, J, s=1.0):
    nx, ny = J["neck"]
    polyline(cr, bezier_pts([(nx - 18 * s, ny + 4 * s), (nx - 26 * s, ny + 60 * s), (nx + 4 * s, ny + 70 * s)], 12),
             4 * s, GRAY)
    polyline(cr, bezier_pts([(nx + 18 * s, ny + 4 * s), (nx + 26 * s, ny + 50 * s), (nx + 4 * s, ny + 70 * s)], 12),
             4 * s, GRAY)
    circle(cr, nx + 4 * s, ny + 76 * s, 9 * s, fill=LIGHT, stroke=INK, w=3 * s)


def flag(cr, x, y, s=1.0, kind="fr", wave=0.0):
    cols = {"fr": ("v", [(0.0, 0.2, 0.6), WHITE, (0.9, 0.15, 0.2)]),
            "it": ("v", [(0.0, 0.55, 0.3), WHITE, (0.85, 0.15, 0.2)]),
            "es": ("h3", [(0.75, 0.05, 0.1), (1.0, 0.77, 0.0), (0.75, 0.05, 0.1)])}
    mode, cs = cols[kind]
    with xform(cr, x, y, s, wave * 0.05):
        if mode == "v":
            for i, c in enumerate(cs):
                rect(cr, -90 + i * 60, -60, 60, 120, fill=c)
        else:
            rect(cr, -90, -60, 180, 30, fill=cs[0])
            rect(cr, -90, -30, 180, 60, fill=cs[1])
            rect(cr, -90, 30, 180, 30, fill=cs[2])
        rect(cr, -90, -60, 180, 120, stroke=INK, lw=5)


def campfire(cr, x, y, s=1.0, t=0.0):
    with xform(cr, x, y, s):
        glow(cr, 0, -40, 380, ORANGE, 0.35)
        for k in (-1, 1):
            rrect(cr, -80, -20, 160, 26, 12, fill=(0.45, 0.28, 0.15), stroke=INK, lw=4)
            del k
        for i, (c, h, w_) in enumerate(((RED, 150, 60), (ORANGE, 115, 45), (YELLOW, 70, 28))):
            f = 1 + 0.12 * math.sin(t * 14 + i * 2)
            pts = bezier_pts([(-w_, -10), (-w_ * 0.8, -h * 0.5 * f), (0, -h * f)], 10) + \
                bezier_pts([(0, -h * f), (w_ * 0.8, -h * 0.5 * f), (w_, -10)], 10)
            polyline(cr, pts, 0, INK, closed=True, fill=c)


def plague_mask(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        polyline(cr, [(-20, -60), (-75, -40), (-75, 30), (-20, 60), (40, 30)], 0, INK, closed=True, fill=INK)
        ellipse(cr, -15, 0, 60, 70, fill=(0.25, 0.25, 0.28), stroke=INK, w=4)
        polyline(cr, [(20, -15), (140, 40), (20, 30)], 4, INK, closed=True, fill=(0.85, 0.80, 0.70))
        circle(cr, -10, -18, 16, fill=(0.85, 0.9, 1.0), stroke=INK, w=4)
        rect(cr, -80, -95, 120, 40, fill=INK)
        rect(cr, -110, -60, 180, 14, fill=INK)


def revolution(cr, x, y, s=1.0, t=0.0):
    with xform(cr, x, y, s):
        line(cr, -60, 100, -60, -110, 8, (0.45, 0.30, 0.18))
        pts = [(-60 + i * 22, -110 + 10 * math.sin(t * 5 + i)) for i in range(8)]
        pts += [(-60 + i * 22, -20 + 10 * math.sin(t * 5 + i)) for i in range(7, -1, -1)]
        polyline(cr, pts, 4, INK, closed=True, fill=RED)
        p = sm.pose("cheer", x=40, s=0.45, smile=0.8)
        sm.draw(cr, sm.on_ground(p, 100), acc=("cap",))


def moon_icon(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        circle(cr, 0, 0, 100, fill=(0.85, 0.85, 0.88), stroke=INK, w=5)
        for (cx_, cy_, r_) in ((-40, -30, 18), (30, 30, 22), (40, -40, 12), (-30, 45, 10)):
            circle(cr, cx_, cy_, r_, fill=(0.70, 0.70, 0.74), stroke=INK, w=3)
        line(cr, -10, -100, -10, -190, 5, INK)
        rect(cr, -10, -190, 70, 44, fill=WHITE, stroke=INK, lw=4)
        for k in range(3):
            line(cr, -10, -182 + k * 14, 60, -182 + k * 14, 3, RED)
        rect(cr, -10, -190, 28, 22, fill=BLUE)


def printing_press(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        rect(cr, -90, -110, 30, 210, fill=(0.50, 0.33, 0.20), stroke=INK, lw=4)
        rect(cr, 60, -110, 30, 210, fill=(0.50, 0.33, 0.20), stroke=INK, lw=4)
        rect(cr, -100, -130, 200, 30, fill=(0.50, 0.33, 0.20), stroke=INK, lw=4)
        line(cr, 0, -100, 0, -20, 10, INK)
        rect(cr, -60, -20, 120, 26, fill=(0.40, 0.40, 0.44), stroke=INK, lw=4)
        rect(cr, -70, 30, 140, 20, fill=WHITE, stroke=INK, lw=3)
        line(cr, -10, -60, 80, -70, 6, INK)
        circle(cr, 82, -70, 10, fill=INK)


def skill_icon(cr, i, T=0.0):
    """Small icons (about +-60 px) for the 'dozens of skills' grid."""
    i = i % 20
    if i == 0:
        guitar(cr, 0, 10, 0.45, 0.4)
    elif i == 1:
        P.flask(cr, 0, 50, 0.65, c=GREEN, t=T)
    elif i == 2:
        pan(cr, -20, 0, 0.7)
    elif i == 3:
        P.book(cr, 0, 0, 0.6, c=BLUE)
    elif i == 4:
        P.gear(cr, 0, 0, 48, rot=T)
    elif i == 5:
        P.globe(cr, 0, 0, 50, T)
    elif i == 6:
        with xform(cr, 0, 0, 1.0):
            ellipse(cr, 0, 0, 60, 46, fill=(0.95, 0.88, 0.70), stroke=INK, w=4)
            for k, c in enumerate((RED, BLUE, YELLOW, GREEN)):
                circle(cr, -30 + k * 18, -14 + (k % 2) * 12, 9, fill=c)
            circle(cr, 22, 18, 10, fill=(0.95, 0.88, 0.70), stroke=INK, w=3)
    elif i == 7:
        P2.press_camera(cr, 0, 0, 1.0)
    elif i == 8:
        P.atom(cr, 0, 0, 0.6, t=T)
    elif i == 9:
        with xform(cr, 0, 0, 1.0):
            rect(cr, -40, 30, 80, 20, fill=INK)
            polyline(cr, [(-26, 30), (-20, -10), (-36, -30), (-14, -60), (10, -50), (20, -10), (26, 30)], 4, INK,
                     closed=True, fill=WHITE)
    elif i == 10:
        P.telescope(cr, 0, 60, 0.5)
    elif i == 11:
        P.brain(cr, 0, 0, 0.55)
    elif i == 12:
        with xform(cr, 0, 0, 1.0):
            circle(cr, 0, 0, 50, fill=WHITE, stroke=INK, w=4)
            polyline(cr, [(0, -20), (19, -6), (12, 16), (-12, 16), (-19, -6)], 0, INK, closed=True, fill=INK)
    elif i == 13:
        with xform(cr, 0, 0, 1.0):
            line(cr, -10, -50, -10, 30, 6, INK)
            line(cr, 30, -60, 30, 20, 6, INK)
            line(cr, -10, -50, 30, -60, 10, INK)
            ellipse(cr, -24, 32, 18, 13, fill=INK, rot=-0.3)
            ellipse(cr, 16, 22, 18, 13, fill=INK, rot=-0.3)
    elif i == 14:
        P.lightbulb(cr, 0, 0, 0.5, on=0.5, t=T)
    elif i == 15:
        P.heart(cr, 0, 10, 1.1)
    elif i == 16:
        blueprint_roll(cr, 0, 0, 0.42)
    elif i == 17:
        P.chip(cr, 0, 0, 0.5)
    elif i == 18:
        P.rubiks(cr, 0, 0, 0.5)
    else:
        P.magnifier(cr, -10, -10, 0.6)


def medieval_village(cr, T, gy=860, sky=((0.80, 0.86, 0.95), (0.96, 0.92, 0.82)), cam=0.0):
    S.vgrad(cr, *sky)
    P.hill(cr, 500, gy + 10, 1400, 160, c=(0.55, 0.70, 0.45))
    P.hill(cr, 1500, gy + 10, 1300, 130, c=(0.50, 0.66, 0.42))
    S.floor(cr, gy, (0.60, 0.74, 0.46))
    polyline(cr, [(820, gy), (1100, gy), (1400, H + 300), (500, H + 300)], 0, INK, closed=True, fill=(0.75, 0.62, 0.45))
    for i, (x, sc) in enumerate(((240, 1.0), (520, 0.85), (1430, 0.95), (1700, 1.05))):
        thatched_hut(cr, x - cam, gy, sc)
    for i in range(6):
        x = 120 + i * 330
        line(cr, x, gy + 40, x + 60, gy + 40, 4, (0.45, 0.32, 0.2), 0.5)


def thatched_hut(cr, x, gy, s=1.0):
    with xform(cr, x, gy, s):
        rect(cr, -90, -120, 180, 120, fill=(0.88, 0.80, 0.65), stroke=INK, lw=5)
        line(cr, -90, -60, 90, -60, 4, (0.5, 0.35, 0.2))
        line(cr, -30, -120, -30, 0, 4, (0.5, 0.35, 0.2))
        polyline(cr, [(-120, -110), (0, -220), (120, -110)], 5, INK, closed=True, fill=(0.80, 0.65, 0.30))
        for k in range(5):
            line(cr, -90 + k * 40, -118, -40 + k * 20, -190, 3, (0.55, 0.42, 0.18))
        rect(cr, 20, -70, 40, 70, fill=(0.40, 0.26, 0.15), stroke=INK, lw=4)


def classroom(cr, T, board_lines=(), fy=860):
    S.room(cr, T, wall=(0.93, 0.90, 0.80), floor_c=(0.70, 0.55, 0.40), fy=fy)
    P.chalkboard(cr, 1060, 360, 1100, 420)
    for i, (ln, a) in enumerate(board_lines):
        if a > 0:
            text(cr, ln, 1060, 270 + i * 110, 66, face=FONT_HAND, bold=True, c=WHITE, a=a)


def desk_kid(cr, T, x, gy, acc=("cap",), seed=0, g="sit", face=-1, s=0.62, **kw):
    """A kid sitting at a school desk (desk drawn in front)."""
    p = sm.pose(g, x=x, face=face, s=s, **kw)
    p = sm.idle(p, T, seed)
    hip = gy - 84 * s
    p["y"] = hip
    line(cr, x - 30 * s, hip + 6, x + 30 * s, hip + 6, 7 * s, (0.45, 0.30, 0.18))
    line(cr, x - face * 26 * s, hip + 6, x - face * 26 * s, gy, 5 * s, (0.45, 0.30, 0.18))
    line(cr, x - face * 30 * s, hip + 6, x - face * 40 * s, hip - 90 * s, 5 * s, (0.45, 0.30, 0.18))
    J = sm.draw(cr, p, acc=acc)
    dx = x + face * 105 * s
    rect(cr, dx - 60 * s, hip - 40 * s, 120 * s, 16 * s, fill=(0.75, 0.55, 0.35), stroke=INK, lw=4)
    line(cr, dx, hip - 24 * s, dx, gy, 6 * s, INK)
    return J


# ---------------------------------------------------------------- night-sky pieces (ch10)
EXTRA_SHAPES = {
    "bubble": [(-1, -0.7), (1, -0.7), (1, 0.4), (-0.2, 0.4), (-0.6, 0.9), (-0.5, 0.4), (-1, 0.4), (-1, -0.7)],
    "globe": [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), None,
              (-1, 0), (1, 0), None, (0, -1), (-0.4, 0), (0, 1), None, (0, -1), (0.4, 0), (0, 1)],
    "castle": [(-1, 0.8), (-1, -0.5), (-0.7, -0.5), (-0.7, -0.2), (-0.35, -0.2), (-0.35, -0.5), (0, -0.9), (0.35, -0.5),
               (0.35, -0.2), (0.7, -0.2), (0.7, -0.5), (1, -0.5), (1, 0.8), (-1, 0.8)],
    "cake": [(-0.9, 0.7), (-0.9, 0.0), (0.9, 0.0), (0.9, 0.7), (-0.9, 0.7), None, (-0.4, 0.0), (-0.4, -0.5), None,
             (0, 0.0), (0, -0.6), None, (0.4, 0.0), (0.4, -0.5)],
    "replay": [(0.8, 0.0), (0.57, 0.57), (0, 0.8), (-0.57, 0.57), (-0.8, 0), (-0.57, -0.57), (0, -0.8), (0.45, -0.66),
               None, (0.2, -0.95), (0.45, -0.66), (0.1, -0.45), None, (-0.15, -0.3), (0.35, 0.0), (-0.15, 0.3),
               (-0.15, -0.3)],
    "glass": [(-0.5, -0.9), (-0.4, 0.9), (0.4, 0.9), (0.5, -0.9)],
    "rocket": [(0, -1), (0.35, -0.4), (0.35, 0.5), (0.7, 0.9), (-0.7, 0.9), (-0.35, 0.5), (-0.35, -0.4), (0, -1)],
    "sun": [(0, -0.5), (0.35, -0.35), (0.5, 0), (0.35, 0.35), (0, 0.5), (-0.35, 0.35), (-0.5, 0), (-0.35, -0.35),
            (0, -0.5), None, (0, -0.7), (0, -1), None, (0.7, 0), (1, 0), None, (0, 0.7), (0, 1), None, (-0.7, 0), (-1, 0)],
}


def const(cr, shape, cx, cy, size, k, T, c=STAR, a=1.0, label=None, label_dy=None, label_size=34):
    """Constellation with extra shapes (or a list of points) on top of the engine's K.constellation."""
    if isinstance(shape, str) and shape in K.CONSTELLATIONS:
        K.constellation(cr, shape, cx, cy, size, k, T, c=c, a=a, label=None)
    else:
        pts = EXTRA_SHAPES[shape] if isinstance(shape, str) else shape
        segs, cur = [], []
        for p in pts:
            if p is None:
                segs.append(cur)
                cur = []
            else:
                cur.append((cx + p[0] * size, cy + p[1] * size))
        segs.append(cur)
        total = sum(max(0, len(sg) - 1) for sg in segs)
        done = k * total
        for sg in segs:
            if len(sg) >= 2:
                n = len(sg) - 1
                partial_poly(cr, sg, clamp(done / n), 2.5, c, 0.55 * a)
                done -= n
        seen = set()
        for sg in segs:
            for (x, y) in sg:
                key = (round(x), round(y))
                if key in seen or k <= 0:
                    continue
                seen.add(key)
                tw = 0.7 + 0.3 * math.sin(T * 2.3 + x * 0.05 + y * 0.03)
                glow(cr, x, y, 26, c, 0.35 * a * clamp(k * 3) * tw)
                circle(cr, x, y, 4.5, fill=WHITE, a=a * clamp(k * 3) * tw)
    if label and k > 0.6:
        text(cr, label, cx, cy + (label_dy if label_dy is not None else size + 50), label_size, face=FONT_BOLD, c=c,
             a=a * clamp((k - 0.6) * 3))


def night(cr, T, star_a=1.0):
    S.night_sky(cr, T, star_a=star_a)


def note(cr, x, y, s=1.0, c=INK, a=1.0, double=False):
    """Music note (drawn, so no font glyph is needed)."""
    with group(cr, a):
        with xform(cr, x, y, s):
            ellipse(cr, -14, 22, 16, 11, fill=c, rot=-0.4)
            line(cr, 0, 20, 0, -40, 5, c)
            if double:
                ellipse(cr, 36, 12, 16, 11, fill=c, rot=-0.4)
                line(cr, 50, 10, 50, -50, 5, c)
                line(cr, 0, -40, 50, -50, 9, c)
            else:
                polyline(cr, bezier_pts([(0, -40), (24, -26), (22, -6)], 8), 5, c)


def pilot_cap(cr, J, s=1.0, c=(0.12, 0.18, 0.35)):
    hx, hy = J["head"]
    f = 1
    ellipse(cr, hx, hy - 52 * s, 50 * s, 16 * s, fill=c, stroke=INK, w=3 * s)
    polyline(cr, [(hx - 40 * s, hy - 50 * s), (hx - 36 * s, hy - 30 * s), (hx + 36 * s, hy - 30 * s),
                  (hx + 40 * s, hy - 50 * s)], 3 * s, INK, closed=True, fill=c)
    line(cr, hx - 36 * s, hy - 34 * s, hx + 36 * s, hy - 34 * s, 4 * s, YELLOW)
    polyline(cr, [(hx + 10 * s * f, hy - 30 * s), (hx + 58 * s * f, hy - 24 * s), (hx + 36 * s * f, hy - 34 * s)],
             3 * s, INK, closed=True, fill=INK)
    circle(cr, hx, hy - 44 * s, 6 * s, fill=YELLOW)
