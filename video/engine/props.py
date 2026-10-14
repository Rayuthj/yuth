"""Reusable props and diagram pieces, drawn in a consistent line style.

Convention: (x, y) is the visual centre unless the docstring says 'base'
(bottom centre). `s` scales everything, `t` animates where relevant.
"""
import math

from .core import (INK, WHITE, PAPER, PAPER2, LIGHT, MID, GRAY, DARK, RED, BLUE, CYAN, YELLOW, GREEN,
                   ORANGE, PURPLE, BOARD, TAU, W, H, FONT_HAND, FONT_SERIF, FONT_BOLD, FONT_UI,
                   src, line, circle, ellipse, rrect, rect, polyline, arc, text, glow, lerp, clamp,
                   bezier_pts, xform, star_shape, rng, ease, eout, prog, partial_line, arrow, group)

LW = 5


# ---------------------------------------------------------------- household
def clock(cr, x, y, r=80, t=0.0, hours=7.0, minutes=0.0, speed=1.0, ring=0.0, face=WHITE, ink=INK, lw=LW,
          seconds=True):
    """Analog clock. `speed` scales how fast the second hand moves; `ring` shakes it."""
    sx = math.sin(t * 60) * 6 * ring
    rot = math.sin(t * 55) * 0.12 * ring
    with xform(cr, x + sx, y, 1.0, rot):
        if ring > 0:
            for k in (-1, 1):
                circle(cr, k * r * 0.55, -r * 0.95, r * 0.24, fill=ink)
        circle(cr, 0, 0, r, fill=face, stroke=ink, w=lw * 1.2)
        for i in range(12):
            a = i / 12 * TAU
            l1 = r * (0.78 if i % 3 else 0.7)
            line(cr, math.sin(a) * l1, -math.cos(a) * l1, math.sin(a) * r * 0.88, -math.cos(a) * r * 0.88,
                 lw * (0.9 if i % 3 else 1.3), ink)
        sec = t * speed
        mins = minutes + sec / 60
        hrs = hours + mins / 60
        ah, am = hrs / 12 * TAU, mins / 60 * TAU
        line(cr, 0, 0, math.sin(ah) * r * 0.45, -math.cos(ah) * r * 0.45, lw * 1.4, ink)
        line(cr, 0, 0, math.sin(am) * r * 0.68, -math.cos(am) * r * 0.68, lw, ink)
        if seconds:
            a_s = math.floor(sec) / 60 * TAU + (sec % 1) ** 8 / 60 * TAU
            line(cr, 0, 0, math.sin(a_s) * r * 0.78, -math.cos(a_s) * r * 0.78, lw * 0.5, RED)
        circle(cr, 0, 0, lw * 1.1, fill=ink)


def alarm_clock(cr, x, y, s=1.0, t=0.0, ring=0.0):
    with xform(cr, x, y, s):
        line(cr, -40, 60, -55, 80, LW, INK)
        line(cr, 40, 60, 55, 80, LW, INK)
        clock(cr, 0, 0, 70, t, hours=7, minutes=0, speed=1, ring=ring)
        if ring > 0:
            for k in (-1, 1):
                for j in range(3):
                    rr = 95 + j * 22
                    a0 = (-0.5 if k > 0 else math.pi - 0.3) + (0.15 * math.sin(t * 30))
                    arc(cr, 0, 0, rr, a0 - 0.3, a0 + 0.3 + 0.2, 4, INK, ring * (1 - j * 0.25))


def bed(cr, x, y, s=1.0, ink=INK):
    """Base at (x, y) (floor), headboard on the left."""
    with xform(cr, x, y, s):
        rect(cr, -260, -150, 24, 150, fill=WHITE, stroke=ink, lw=LW)
        rrect(cr, -240, -95, 500, 55, 10, fill=WHITE, stroke=ink, lw=LW)
        line(cr, -230, -40, -230, 0, LW, ink)
        line(cr, 250, -40, 250, 0, LW, ink)
        rrect(cr, -225, -130, 110, 40, 18, fill=WHITE, stroke=ink, lw=LW)
        # blanket
        rrect(cr, -100, -110, 340, 30, 12, fill=LIGHT, stroke=ink, lw=LW)


def window(cr, x, y, w=360, h=280, t=0.0, sky=(0.75, 0.86, 0.98), sky2=None, city=True, night=False, frame=INK):
    import cairo
    rect(cr, x - w / 2, y - h / 2, w, h, fill=None)
    cr.save()
    cr.rectangle(x - w / 2, y - h / 2, w, h)
    cr.clip()
    g = cairo.LinearGradient(0, y - h / 2, 0, y + h / 2)
    g.add_color_stop_rgb(0, *sky)
    g.add_color_stop_rgb(1, *(sky2 or sky))
    cr.set_source(g)
    cr.paint()
    if night:
        from .core import stars
        stars(cr, t, n=40, seed=3, area=(x - w / 2, y - h / 2, x + w / 2, y))
    if city:
        skyline(cr, x - w / 2, y + h / 2, w, h * 0.55, seed=4, fill=(0.35, 0.38, 0.45) if not night else (0.12, 0.13, 0.18),
                lit=night, t=t)
    cr.restore()
    rect(cr, x - w / 2, y - h / 2, w, h, stroke=frame, lw=LW * 1.4)
    line(cr, x, y - h / 2, x, y + h / 2, LW, frame)
    line(cr, x - w / 2, y, x + w / 2, y, LW, frame)
    rect(cr, x - w / 2 - 14, y + h / 2, w + 28, 14, fill=WHITE, stroke=frame, lw=LW)


def skyline(cr, x0, base, w, h, seed=1, fill=(0.3, 0.32, 0.38), lit=False, t=0.0, win=True, outline=None):
    r = rng(seed)
    x = x0
    while x < x0 + w:
        bw = r.uniform(0.07, 0.16) * w
        bh = r.uniform(0.35, 1.0) * h
        rect(cr, x, base - bh, bw, bh, fill=fill, stroke=outline, lw=3)
        if win:
            for wy in range(int(base - bh + 14), int(base - 10), 22):
                for wx in range(int(x + 8), int(x + bw - 12), 18):
                    on = r.random() < (0.45 if lit else 0.25)
                    if lit and on:
                        flick = 0.7 + 0.3 * math.sin(t * r.uniform(0.2, 1.2) + wx)
                        rect(cr, wx, wy, 8, 10, fill=(1.0, 0.85, 0.45), a=flick)
                    elif not lit and on:
                        rect(cr, wx, wy, 8, 10, fill=WHITE, a=0.35)
        x += bw + r.uniform(0, 0.02) * w


def nightstand(cr, x, y, s=1.0):
    """Base at floor."""
    with xform(cr, x, y, s):
        rect(cr, -70, -110, 140, 110, fill=WHITE, stroke=INK, lw=LW)
        line(cr, -70, -55, 70, -55, LW, INK)
        circle(cr, 0, -82, 6, fill=INK)
        circle(cr, 0, -28, 6, fill=INK)


def bookshelf(cr, x, y, s=1.0, highlight=0.0, t=0.0):
    """Base at bottom-centre."""
    with xform(cr, x, y, s):
        rect(cr, -120, -300, 240, 300, fill=WHITE, stroke=INK, lw=LW)
        cols = [BLUE, RED, YELLOW, GREEN, INK, PURPLE, ORANGE, MID]
        r = rng(11)
        for row, yy in enumerate((-300, -200, -100)):
            line(cr, -120, yy + 100, 120, yy + 100, LW, INK)
            bx = -110
            while bx < 95:
                bw = r.uniform(14, 26)
                bh = r.uniform(60, 88)
                c = cols[r.randrange(len(cols))] if highlight > 0 else MID
                c = tuple(lerp(a, b, highlight) for a, b in zip(LIGHT, c))
                rect(cr, bx, yy + 100 - bh, bw, bh, fill=c, stroke=INK, lw=3)
                bx += bw + 2


def phone(cr, x, y, s=1.0, t=0.0, lit=1.0, content=None, rot=0.0):
    with xform(cr, x, y, s, rot):
        rrect(cr, -45, -85, 90, 170, 16, fill=INK)
        rrect(cr, -38, -72, 76, 140, 6, fill=lerpc3(DARK, (0.85, 0.93, 1.0), lit))
        if content:
            content(cr)
        else:
            for i in range(4):
                rrect(cr, -30, -60 + i * 32, 60, 22, 6, fill=WHITE, a=0.85 * lit)
                circle(cr, -20, -49 + i * 32, 6, fill=[BLUE, RED, GREEN, YELLOW][i], a=lit)


def lerpc3(a, b, t):
    return tuple(lerp(x, y, t) for x, y in zip(a, b))


def book(cr, x, y, s=1.0, open_=0.0, c=BLUE, rot=0.0, title=None):
    with xform(cr, x, y, s, rot):
        if open_ < 0.5:
            rrect(cr, -55, -75, 110, 150, 8, fill=c, stroke=INK, lw=LW)
            line(cr, -40, -75, -40, 75, LW * 0.8, INK)
            if title:
                text(cr, title, 8, 0, 22, c=WHITE, face=FONT_HAND, bold=True, rot=-math.pi / 2)
        else:
            polyline(cr, [(0, -60), (-120, -75), (-120, 70), (0, 85)], LW, INK, closed=True, fill=WHITE)
            polyline(cr, [(0, -60), (120, -75), (120, 70), (0, 85)], LW, INK, closed=True, fill=WHITE)
            for k in (-1, 1):
                for i in range(5):
                    yy = -40 + i * 22
                    line(cr, k * 20, yy, k * 100, yy - 8, 3, MID)


def toaster(cr, x, y, s=1.0, pop=0.0):
    """Base at bottom. pop 0..1 launches the toast."""
    with xform(cr, x, y, s):
        h = -pop * 120
        for k in (-1, 1):
            rrect(cr, k * 32 - 22, -150 + h, 44, 70, 10, fill=(0.85, 0.65, 0.35), stroke=INK, lw=LW)
        rrect(cr, -90, -110, 180, 110, 26, fill=WHITE, stroke=INK, lw=LW)
        line(cr, -60, -110, -10, -110, LW * 1.6, INK)
        line(cr, 10, -110, 60, -110, LW * 1.6, INK)
        rect(cr, 90, -70, 18, 10, fill=INK)


def desk(cr, x, y, w=420, s=1.0):
    """Base at floor."""
    with xform(cr, x, y, s):
        rect(cr, -w / 2, -150, w, 22, fill=WHITE, stroke=INK, lw=LW)
        line(cr, -w / 2 + 20, -128, -w / 2 + 20, 0, LW, INK)
        line(cr, w / 2 - 20, -128, w / 2 - 20, 0, LW, INK)


def chair(cr, x, y, s=1.0, face=1):
    """Base at floor; seat height ~ 158 (so a sitting stickman's hip rests on it)."""
    with xform(cr, x, y, s, sx=face * s, sy=s):
        line(cr, -50, -150, 50, -150, LW * 1.3, INK)
        line(cr, -45, -150, -45, 0, LW, INK)
        line(cr, 45, -150, 45, 0, LW, INK)
        line(cr, -50, -150, -60, -300, LW, INK)


def monitor(cr, x, y, w=420, h=270, s=1.0, screen=None, lit=1.0, bg=(0.10, 0.12, 0.16)):
    with xform(cr, x, y, s):
        rrect(cr, -w / 2, -h / 2, w, h, 14, fill=INK)
        rrect(cr, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 6, fill=bg)
        if screen:
            cr.save()
            cr.rectangle(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24)
            cr.clip()
            screen(cr, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24)
            cr.restore()
        rect(cr, -16, h / 2, 32, 40, fill=INK)
        rrect(cr, -80, h / 2 + 36, 160, 14, 6, fill=INK)


def chalkboard(cr, x, y, w=900, h=420, c=BOARD):
    rrect(cr, x - w / 2 - 16, y - h / 2 - 16, w + 32, h + 32, 10, fill=(0.55, 0.38, 0.22), stroke=INK, lw=LW)
    rect(cr, x - w / 2, y - h / 2, w, h, fill=c)
    rect(cr, x - w / 2 + 40, y + h / 2 + 8, 160, 12, fill=WHITE)


def flask(cr, x, y, s=1.0, c=GREEN, level=0.6, t=0.0, bubbles=True):
    """Erlenmeyer flask, base at bottom."""
    with xform(cr, x, y, s):
        pts = [(-18, -130), (-18, -80), (-60, 0), (60, 0), (18, -80), (18, -130)]
        lv = -80 * level
        cr.save()
        polyline(cr, pts, 0, INK, closed=True, fill=WHITE)
        cr.move_to(*pts[0])
        for p in pts[1:]:
            cr.line_to(*p)
        cr.close_path()
        cr.clip()
        rect(cr, -70, lv, 140, -lv + 2, fill=c, a=0.8)
        if bubbles:
            r = rng(int(x) % 97)
            for i in range(6):
                by = -((t * 40 * r.uniform(0.6, 1.4) + r.uniform(0, 80)) % max(10, -lv))
                circle(cr, r.uniform(-30, 30) * (1 + by / 120), by, r.uniform(3, 6), stroke=WHITE, w=2)
        cr.restore()
        polyline(cr, pts, LW, INK)
        line(cr, -26, -130, 26, -130, LW, INK)


def tube(cr, x, y, s=1.0, c=BLUE, level=0.5):
    with xform(cr, x, y, s):
        rrect(cr, -14, -120, 28, 120, 14, fill=WHITE, stroke=INK, lw=LW)
        rrect(cr, -10, -120 * level, 20, 120 * level - 4, 10, fill=c, a=0.85)


def lightbulb(cr, x, y, s=1.0, on=1.0, t=0.0, c=YELLOW):
    with xform(cr, x, y, s):
        if on > 0:
            glow(cr, 0, -10, 150, c, 0.55 * on)
            for i in range(10):
                a = i / 10 * TAU + t * 0.4
                l0, l1 = 85, 110 + 10 * math.sin(t * 6 + i)
                line(cr, math.cos(a) * l0, -10 + math.sin(a) * l0, math.cos(a) * l1, -10 + math.sin(a) * l1,
                     6, c, on)
        circle(cr, 0, -20, 55, fill=lerpc3(WHITE, c, on), stroke=INK, w=LW)
        rect(cr, -26, 30, 52, 40, fill=MID, stroke=INK, lw=LW)
        line(cr, -26, 44, 26, 44, 3, INK)
        line(cr, -26, 56, 26, 56, 3, INK)
        polyline(cr, [(-12, 30), (-12, -10), (0, -25), (12, -10), (12, 30)], 3, INK)


def gear(cr, x, y, r=60, teeth=10, rot=0.0, fill=WHITE, ink=INK, lw=LW):
    pts = []
    for i in range(teeth * 4):
        a = rot + i / (teeth * 4) * TAU
        rr = r if (i % 4) in (1, 2) else r * 0.78
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    polyline(cr, pts, lw, ink, closed=True, fill=fill)
    circle(cr, x, y, r * 0.28, fill=PAPER, stroke=ink, w=lw)


def atom(cr, x, y, s=1.0, t=0.0, c=BLUE, ink=INK):
    with xform(cr, x, y, s):
        for k in range(3):
            ellipse(cr, 0, 0, 80, 28, stroke=ink, w=LW * 0.8, rot=k * TAU / 6 + t * 0.2)
        circle(cr, 0, 0, 14, fill=c, stroke=ink, w=3)
        for k in range(3):
            a = t * 2.4 + k * 2.1
            rot = k * TAU / 6 + t * 0.2
            ex, ey = math.cos(a) * 80, math.sin(a) * 28
            circle(cr, ex * math.cos(rot) - ey * math.sin(rot), ex * math.sin(rot) + ey * math.cos(rot), 8, fill=c)


def brain(cr, x, y, s=1.0, c=(1.0, 0.72, 0.78), ink=INK, glow_a=0.0, t=0.0):
    with xform(cr, x, y, s):
        if glow_a > 0:
            glow(cr, 0, 0, 200, YELLOW, glow_a)
        lobes = [(-45, -25, 48), (5, -45, 50), (50, -20, 45), (40, 25, 42), (-10, 28, 46), (-55, 18, 38)]
        for lx, ly, lr in lobes:
            circle(cr, lx, ly, lr, stroke=ink, w=LW * 2)
        for lx, ly, lr in lobes:
            circle(cr, lx, ly, lr, fill=c)
        for pts in ([(-60, -20), (-30, -5), (-45, 20)], [(0, -60), (10, -25), (-10, 0), (5, 30)],
                    [(40, -40), (30, -10), (55, 10)], [(-20, 40), (10, 45), (30, 30)]):
            polyline(cr, bezier_pts(pts, 12), LW * 0.8, ink)
        line(cr, -5, 70, 10, 100, LW * 1.4, ink)


def chip(cr, x, y, s=1.0, c=GREEN, ink=INK):
    with xform(cr, x, y, s):
        for i in range(5):
            o = -48 + i * 24
            for (a, b, cc, d) in ((o, -70, o, -90), (o, 70, o, 90), (-70, o, -90, o), (70, o, 90, o)):
                line(cr, a, b, cc, d, LW, ink)
        rrect(cr, -70, -70, 140, 140, 12, fill=c, stroke=ink, lw=LW)
        rrect(cr, -35, -35, 70, 70, 6, fill=WHITE, stroke=ink, lw=LW * 0.8)


def scroll(cr, x, y, s=1.0, c=(0.96, 0.88, 0.70), ink=INK):
    with xform(cr, x, y, s):
        rect(cr, -60, -75, 120, 150, fill=c, stroke=ink, lw=LW)
        for k in (-1, 1):
            ellipse(cr, 0, k * 80, 75, 14, fill=c, stroke=ink, w=LW)
        for i in range(5):
            line(cr, -40, -45 + i * 22, 40, -45 + i * 22, 3, MID)


def globe(cr, x, y, r=110, t=0.0, c=(0.55, 0.78, 0.95), land=GREEN, ink=INK, heat=0.0):
    circle(cr, x, y, r, fill=c, stroke=ink, w=LW)
    cr.save()
    cr.arc(x, y, r - 2, 0, TAU)
    cr.clip()
    rr = rng(5)
    blobs = [(rr.uniform(-1, 1), rr.uniform(-0.8, 0.8), rr.uniform(0.18, 0.4)) for _ in range(9)]
    for bx, by, br in blobs:
        px = ((bx + t * 0.15 + 1) % 2.4 - 1.2) * r
        lc = lerpc3(land, ORANGE, heat) if heat else land
        ellipse(cr, x + px, y + by * r, br * r * 1.2, br * r * 0.8, fill=lc)
    for k in (-0.5, 0, 0.5):
        ellipse(cr, x, y + k * r, r * math.sqrt(1 - k * k), r * 0.12 * (1 - abs(k)), stroke=ink, w=2, a=0.35)
    for k in range(4):
        ph = (t * 0.15 * 1.3 + k / 4) % 1
        ellipse(cr, x, y, max(1, r * abs(math.cos(ph * math.pi))), r, stroke=ink, w=2, a=0.3)
    cr.restore()
    circle(cr, x, y, r, stroke=ink, w=LW)


def solar_panel(cr, x, y, s=1.0, shine=0.0, t=0.0):
    """Base at ground."""
    with xform(cr, x, y, s):
        line(cr, 0, 0, 0, -80, LW, INK)
        pts = [(-110, -70), (90, -70), (130, -170), (-70, -170)]
        polyline(cr, pts, LW, INK, closed=True, fill=(0.2, 0.35, 0.7))
        for i in range(1, 4):
            f = i / 4
            line(cr, lerp(-110, -70, f), lerp(-70, -170, f), lerp(90, 130, f), lerp(-70, -170, f), 2.5, WHITE, 0.7)
        for i in range(1, 5):
            f = i / 5
            line(cr, lerp(-110, 90, f), -70, lerp(-70, 130, f), -170, 2.5, WHITE, 0.7)
        if shine > 0:
            k = (t * 0.6) % 1.6 - 0.3
            cr.save()
            cr.move_to(*pts[0])
            for p in pts[1:]:
                cr.line_to(*p)
            cr.close_path()
            cr.clip()
            polyline(cr, [(lerp(-160, 160, k), -60), (lerp(-160, 160, k) + 40, -60),
                          (lerp(-160, 160, k) + 100, -180), (lerp(-160, 160, k) + 60, -180)], 0, INK,
                     closed=True, fill=WHITE, fa=0.5 * shine)
            cr.restore()


def wind_turbine(cr, x, y, s=1.0, t=0.0, speed=1.0):
    with xform(cr, x, y, s):
        polyline(cr, [(-8, 0), (-3, -260), (3, -260), (8, 0)], LW * 0.6, INK, closed=True, fill=WHITE)
        for k in range(3):
            a = t * speed * 2 + k * TAU / 3
            with xform(cr, 0, -260, 1, a):
                polyline(cr, [(0, -6), (120, -10), (130, 0), (0, 6)], LW * 0.6, INK, closed=True, fill=WHITE)
        circle(cr, 0, -260, 10, fill=INK)


def battery(cr, x, y, s=1.0, level=0.5, c=GREEN, t=0.0):
    with xform(cr, x, y, s):
        rrect(cr, -60, -110, 120, 220, 16, fill=WHITE, stroke=INK, lw=LW * 1.2)
        rect(cr, -24, -128, 48, 18, fill=INK)
        lv = clamp(level)
        if lv > 0:
            rrect(cr, -46, 96 - 192 * lv, 92, 192 * lv, 8, fill=c)
        polyline(cr, [(8, -50), (-18, 6), (2, 6), (-8, 50), (22, -8), (2, -8)], 3, INK, closed=True,
                 fill=YELLOW)


def drone(cr, x, y, s=1.0, t=0.0, rot=0.0, version=1, spin=1.0):
    with xform(cr, x, y, s, rot):
        line(cr, -110, -10, 110, -10, LW * 1.2, INK)
        for k in (-1, 1):
            line(cr, k * 110, -10, k * 110, -30, LW, INK)
            w_ = 70 * abs(math.cos(t * 40 * spin + k))
            line(cr, k * 110 - w_, -32, k * 110 + w_, -32, LW * 0.9, INK)
            ellipse(cr, k * 110, -32, 75, 8, stroke=INK, w=2, a=0.25 * spin)
        rrect(cr, -50, -30, 100, 50, 14, fill=WHITE if version < 3 else YELLOW, stroke=INK, lw=LW)
        circle(cr, 22, -5, 9, fill=INK)
        if version >= 2:
            line(cr, -30, 20, -40, 45, LW * 0.8, INK)
            line(cr, 30, 20, 40, 45, LW * 0.8, INK)
        if version >= 3:
            rrect(cr, -28, 46, 56, 40, 6, fill=(0.85, 0.65, 0.35), stroke=INK, lw=LW * 0.8)
            line(cr, 0, 20, 0, 46, 3, INK)


def tree(cr, x, y, s=1.0, t=0.0, c=GREEN, ink=INK):
    """Base at ground."""
    with xform(cr, x, y, s):
        polyline(cr, [(-14, 0), (-10, -120), (10, -120), (14, 0)], LW, ink, closed=True, fill=(0.55, 0.40, 0.28))
        sway = math.sin(t * 1.2) * 4
        for (bx, by, br) in ((0, -200, 80), (-60, -160, 60), (60, -160, 60), (-30, -240, 55), (35, -240, 55)):
            circle(cr, bx + sway, by, br, stroke=ink, w=LW * 2)
        for (bx, by, br) in ((0, -200, 80), (-60, -160, 60), (60, -160, 60), (-30, -240, 55), (35, -240, 55)):
            circle(cr, bx + sway, by, br, fill=c)


def bush(cr, x, y, s=1.0, c=GREEN, shake=0.0, t=0.0):
    with xform(cr, x + math.sin(t * 40) * 6 * shake, y, s):
        for (bx, by, br) in ((-60, -40, 50), (0, -60, 62), (60, -40, 50)):
            circle(cr, bx, by, br, stroke=INK, w=LW * 2)
        for (bx, by, br) in ((-60, -40, 50), (0, -60, 62), (60, -40, 50)):
            circle(cr, bx, by, br, fill=c)
        rect(cr, -110, -20, 220, 20, fill=c)


def sun(cr, x, y, r=70, t=0.0, c=YELLOW, rays=True, a=1.0):
    glow(cr, x, y, r * 3, c, 0.45 * a)
    if rays:
        for i in range(12):
            ang = i / 12 * TAU + t * 0.2
            line(cr, x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3,
                 x + math.cos(ang) * r * 1.7, y + math.sin(ang) * r * 1.7, 7, c, a)
    circle(cr, x, y, r, fill=c, stroke=INK, w=LW, a=a)


def cloud(cr, x, y, s=1.0, c=WHITE, ink=INK, a=1.0):
    with xform(cr, x, y, s):
        parts = ((-60, 10, 40), (-20, -15, 50), (30, -5, 45), (65, 15, 32), (0, 20, 40))
        for px, py, pr in parts:
            circle(cr, px, py, pr, stroke=ink, w=LW * 2, a=a)
        for px, py, pr in parts:
            circle(cr, px, py, pr, fill=c, a=a)


def door(cr, x, y, s=1.0, open_=0.0, light=YELLOW, ink=INK, frame_fill=WHITE):
    """Base at floor. open_ 0..1 swings the door and spills light."""
    with xform(cr, x, y, s):
        rect(cr, -80, -300, 160, 300, fill=light if open_ > 0 else frame_fill)
        if open_ > 0:
            glow(cr, 0, -150, 300, light, 0.5 * open_)
        w_ = 160 * (1 - open_ * 0.85)
        rect(cr, -80, -300, w_, 300, fill=frame_fill, stroke=ink, lw=LW)
        circle(cr, -80 + w_ - 22, -150, 8, fill=ink)
        rect(cr, -80, -300, 160, 300, stroke=ink, lw=LW * 1.3)


def coffee(cr, x, y, s=1.0, t=0.0, steam=True, level=1.0):
    """Base at bottom."""
    with xform(cr, x, y, s):
        polyline(cr, [(-40, -90), (-32, 0), (32, 0), (40, -90)], LW, INK, closed=True, fill=WHITE)
        arc(cr, 44, -50, 20, -1.4, 1.4, LW, INK)
        if level > 0:
            polyline(cr, [(-38, -90 + 80 * (1 - level)), (38, -90 + 80 * (1 - level)), (32, -4), (-32, -4)], 0, INK,
                     closed=True, fill=(0.45, 0.28, 0.15))
        if steam:
            for k in (-15, 10):
                pts = [(k + 8 * math.sin(t * 3 + i * 0.8 + k), -100 - i * 14) for i in range(6)]
                polyline(cr, pts, 3.5, MID, 0.7)


def notebook(cr, x, y, s=1.0, pages=0.0, t=0.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rrect(cr, -150, -100, 300, 200, 8, fill=WHITE, stroke=INK, lw=LW)
        line(cr, 0, -100, 0, 100, LW * 0.8, INK)
        r = rng(3)
        n = int(16 * clamp(pages))
        for i in range(n):
            side = -1 if i < 8 else 1
            yy = -75 + (i % 8) * 20
            ln = r.uniform(60, 120)
            line(cr, side * 15 if side > 0 else -15 - ln, yy, (side * 15 + ln) if side > 0 else -15, yy, 3, BLUE)


def crown(cr, x, y, s=1.0, c=YELLOW):
    with xform(cr, x, y, s):
        pts = [(-60, 30), (-70, -40), (-30, 0), (0, -55), (30, 0), (70, -40), (60, 30)]
        polyline(cr, pts, LW, INK, closed=True, fill=c)
        for px in (-35, 0, 35):
            circle(cr, px, 15, 7, fill=RED)


def house(cr, x, y, s=1.0, lit=0.0, c=WHITE, roof=RED):
    """Base at ground."""
    with xform(cr, x, y, s):
        rect(cr, -70, -110, 140, 110, fill=c, stroke=INK, lw=LW)
        polyline(cr, [(-90, -105), (0, -180), (90, -105)], LW, INK, closed=True, fill=roof)
        rect(cr, -20, -60, 40, 60, fill=INK)
        rect(cr, -55, -90, 28, 28, fill=lerpc3(WHITE, YELLOW, lit), stroke=INK, lw=3)
        rect(cr, 27, -90, 28, 28, fill=lerpc3(WHITE, YELLOW, lit), stroke=INK, lw=3)


def tower(cr, x, y, s=1.0, c=LIGHT, ink=INK, lit=0.0):
    """Base at ground."""
    with xform(cr, x, y, s):
        polyline(cr, [(-70, 0), (-55, -420), (55, -420), (70, 0)], LW, ink, closed=True, fill=c)
        for i in range(5):
            rx = -80 + i * 34
            rect(cr, rx, -460, 24, 40, fill=c, stroke=ink, lw=LW)
        rect(cr, -70, -425, 140, 12, fill=c, stroke=ink, lw=LW)
        rect(cr, -14, -360, 28, 44, fill=lerpc3(INK, YELLOW, lit))
        rect(cr, -20, -60, 40, 60, fill=ink)


def question_mark(cr, x, y, size=80, c=INK, a=1.0, rot=0.0, face=FONT_BOLD):
    text(cr, "?", x, y, size, c=c, a=a, face=face, rot=rot)


def penguin(cr, x, y, s=1.0, t=0.0, xray=0.0):
    """Base at bottom. xray reveals the (surprisingly long) legs with knees."""
    with xform(cr, x, y, s):
        ellipse(cr, 0, -110, 70, 105, fill=INK)
        ellipse(cr, 8, -95, 48, 82, fill=WHITE)
        circle(cr, 0, -200, 48, fill=INK)
        ellipse(cr, 14, -200, 28, 30, fill=WHITE)
        circle(cr, 22, -205, 7, fill=INK)
        polyline(cr, [(36, -195), (66, -188), (36, -180)], 3, INK, closed=True, fill=ORANGE)
        for k in (-1, 1):
            ellipse(cr, k * 28 + 6, -4, 22, 8, fill=ORANGE, stroke=INK, w=3)
        ellipse(cr, -60, -110, 18, 55, fill=INK, rot=0.25)
        if xray > 0:
            with group(cr, xray):
                ellipse(cr, 0, -110, 72, 107, fill=(0.15, 0.3, 0.45))
                for k in (-1, 1):
                    pts = [(k * 22, -120), (k * 26 - 6, -60), (k * 30 + 4, -30), (k * 28 + 6, -8)]
                    polyline(cr, pts, 7, WHITE)
                    circle(cr, *pts[1], 9, fill=YELLOW)
                text(cr, "KNEES!", 0, -260, 34, c=RED, face=FONT_HAND, bold=True)


def magnifier(cr, x, y, s=1.0, rot=0.6, lens=(0.85, 0.93, 1.0)):
    with xform(cr, x, y, s, rot):
        line(cr, 0, 60, 0, 160, LW * 2.4, INK)
        circle(cr, 0, 0, 60, fill=lens, stroke=INK, w=LW * 1.4, fa=0.5)


def heart(cr, x, y, s=1.0, c=RED, a=1.0, beat=0.0):
    if s <= 1e-3:
        return
    k = s * (1 + 0.12 * beat)
    with xform(cr, x, y, k):
        cr.move_to(0, 30)
        cr.curve_to(-70, -20, -40, -70, 0, -35)
        cr.curve_to(40, -70, 70, -20, 0, 30)
        cr.close_path()
        src(cr, c, a)
        cr.fill_preserve()
        src(cr, INK, a)
        cr.set_line_width(LW / k * s)
        cr.stroke()


def dna(cr, x, y, s=1.0, t=0.0, h=300, c1=BLUE, c2=RED):
    with xform(cr, x, y, s):
        n = 14
        for i in range(n):
            yy = -h / 2 + i * h / (n - 1)
            ph = t * 2 + i * 0.55
            x1, x2 = math.sin(ph) * 60, -math.sin(ph) * 60
            line(cr, x1, yy, x2, yy, 3, MID)
            circle(cr, x1, yy, 9, fill=c1, stroke=INK, w=2)
            circle(cr, x2, yy, 9, fill=c2, stroke=INK, w=2)


def car(cr, x, y, s=1.0, c=RED, t=0.0, face=1):
    """Base at road level."""
    with xform(cr, x, y, s, sx=s * face, sy=s):
        polyline(cr, [(-90, -20), (-90, -50), (-50, -55), (-25, -90), (40, -90), (65, -55), (95, -50), (95, -20)],
                 LW, INK, closed=True, fill=c)
        rect(cr, -15, -82, 30, 24, fill=(0.8, 0.9, 1.0), stroke=INK, lw=3)
        rect(cr, 22, -82, 30, 24, fill=(0.8, 0.9, 1.0), stroke=INK, lw=3)
        for k in (-55, 60):
            circle(cr, k, -18, 20, fill=INK)
            circle(cr, k, -18, 8, fill=LIGHT)
            a = -t * 8
            line(cr, k, -18, k + math.cos(a) * 8, -18 + math.sin(a) * 8, 3, INK)


def telescope(cr, x, y, s=1.0, rot=-0.5):
    """Base at ground."""
    with xform(cr, x, y, s):
        for k in (-1, 0, 1):
            line(cr, 0, -110, k * 60, 0, LW, INK)
        with xform(cr, 0, -120, 1, rot):
            rrect(cr, -90, -22, 180, 44, 10, fill=WHITE, stroke=INK, lw=LW)
            rect(cr, 90, -28, 26, 56, fill=INK)


def probe(cr, x, y, s=1.0, t=0.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        for k in (-1, 1):
            rect(cr, k * 50 - (60 if k < 0 else 0) + (0 if k < 0 else 10), -18, 60, 36, fill=(0.2, 0.35, 0.7),
                 stroke=INK, lw=3)
        rrect(cr, -30, -30, 60, 60, 8, fill=YELLOW, stroke=INK, lw=LW)
        arc(cr, 0, -48, 30, math.pi * 1.15, math.pi * 1.85, LW, INK)
        line(cr, 0, -30, 0, -60, 3, INK)


def robot(cr, x, y, s=1.0, t=0.0, c=LIGHT, eye_c=CYAN, smile=0.5):
    """Friendly robot, base at bottom."""
    with xform(cr, x, y, s):
        rrect(cr, -60, -190, 120, 130, 20, fill=c, stroke=INK, lw=LW)
        rrect(cr, -70, -320, 140, 110, 26, fill=c, stroke=INK, lw=LW)
        line(cr, 0, -320, 0, -355, LW, INK)
        circle(cr, 0, -362, 10, fill=RED)
        for k in (-1, 1):
            circle(cr, k * 30, -272, 15, fill=eye_c, stroke=INK, w=3)
        polyline(cr, bezier_pts([(-25, -240), (0, -240 + 18 * smile), (25, -240)], 8), 4, INK)
        line(cr, -60, -150, -95, -95 + 10 * math.sin(t * 3), LW, INK)
        line(cr, 60, -150, 95, -95 - 10 * math.sin(t * 3), LW, INK)
        line(cr, -30, -60, -30, 0, LW, INK)
        line(cr, 30, -60, 30, 0, LW, INK)
        rrect(cr, -30, -160, 60, 50, 8, fill=WHITE, stroke=INK, lw=3)
        for i in range(3):
            circle(cr, -15 + i * 15, -135, 5, fill=[GREEN, YELLOW, RED][i])


def rubiks(cr, x, y, s=1.0, solved=1.0, t=0.0, rot=0.0):
    """Isometric Rubik's cube; solved 0..1 blends scrambled colors to solved faces."""
    cols = [RED, BLUE, YELLOW, GREEN, ORANGE, WHITE]
    r = rng(17)
    with xform(cr, x, y, s, rot):
        faces = {
            "top": ((0, -100), (87, -50), (0, 0), (-87, -50)),
            "left": ((-87, -50), (0, 0), (0, 100), (-87, 50)),
            "right": ((0, 0), (87, -50), (87, 50), (0, 100)),
        }
        solved_col = {"top": YELLOW, "left": RED, "right": BLUE}
        for name, (a, b, c, d) in faces.items():
            for i in range(3):
                for j in range(3):
                    def P(u, v):
                        return (a[0] + (b[0] - a[0]) * u + (d[0] - a[0]) * v,
                                a[1] + (b[1] - a[1]) * u + (d[1] - a[1]) * v)
                    sc = cols[r.randrange(6)]
                    k = clamp(solved * 1.6 - (i + j) * 0.12)
                    col = lerpc3(sc, solved_col[name], k)
                    pts = [P(i / 3, j / 3), P((i + 1) / 3, j / 3), P((i + 1) / 3, (j + 1) / 3), P(i / 3, (j + 1) / 3)]
                    polyline(cr, pts, 4, INK, closed=True, fill=col)


def sudoku(cr, x, y, size=360, fill=1.0, seed=2, c=INK, highlight=BLUE):
    cell = size / 9
    x0, y0 = x - size / 2, y - size / 2
    rect(cr, x0, y0, size, size, fill=WHITE, stroke=c, lw=6)
    for i in range(1, 9):
        w_ = 5 if i % 3 == 0 else 2
        line(cr, x0 + i * cell, y0, x0 + i * cell, y0 + size, w_, c)
        line(cr, x0, y0 + i * cell, x0 + size, y0 + i * cell, w_, c)
    base = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
    r = rng(seed)
    given = [[r.random() < 0.35 for _ in range(9)] for _ in range(9)]
    order = [(i, j) for i in range(9) for j in range(9) if not given[i][j]]
    r.shuffle(order)
    nfill = int(len(order) * clamp(fill))
    filled = set(order[:nfill])
    for i in range(9):
        for j in range(9):
            if given[i][j]:
                text(cr, str(base[i][j]), x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell, cell * 0.62, c=c,
                     face=FONT_UI, bold=True)
            elif (i, j) in filled:
                text(cr, str(base[i][j]), x0 + (j + 0.5) * cell, y0 + (i + 0.55) * cell, cell * 0.66,
                     c=highlight, face=FONT_HAND, bold=True)


def bell_curve(cr, x, y, w=900, h=360, p=1.0, ink=INK, fill=BLUE, mean_label=True, a=1.0):
    """IQ-style bell curve. (x, y) is the centre of the baseline."""
    pts = []
    n = 120
    for i in range(n + 1):
        u = -4 + 8 * i / n
        pts.append((x + u * w / 8, y - h * math.exp(-u * u / 2)))
    k = max(2, int(len(pts) * clamp(p)))
    poly = pts[:k]
    polyline(cr, poly + [(poly[-1][0], y), (poly[0][0], y)], 0, ink, closed=True, fill=fill, fa=0.25 * a)
    polyline(cr, poly, LW, ink, a)
    line(cr, x - w / 2 - 20, y, x + w / 2 + 20, y, LW, ink, a)


def node_graph(cr, nodes, edges, p=1.0, ink=INK, a=1.0, lw=4, node_r=14, t=0.0, pulse=True, c=BLUE):
    """Draw edges then nodes; nodes is a list of (x, y)."""
    for i, (u, v) in enumerate(edges):
        k = clamp(p * len(edges) * 0.6 - i * 0.6 + 0.6)
        if k > 0:
            (x1, y1), (x2, y2) = nodes[u], nodes[v]
            partial_line(cr, x1, y1, x2, y2, k, lw, ink, a * 0.8)
            if pulse and k >= 1:
                f = (t * 0.7 + i * 0.37) % 1
                circle(cr, lerp(x1, x2, f), lerp(y1, y2, f), lw * 1.2, fill=c, a=a)
    for i, (x, y) in enumerate(nodes):
        k = clamp(p * len(nodes) * 0.5 - i * 0.5 + 1)
        if k > 0:
            circle(cr, x, y, node_r * eout(k), fill=WHITE, stroke=ink, w=lw, a=a)


def decision_tree(cr, x, y, depth=3, spread=150, dy=60, p=1.0, ink=INK, a=1.0, lw=3.5, highlight=None, hc=BLUE,
                  shrink=0.55, seed=0):
    """Branching tree growing upward from (x, y). `highlight` = list of 0/1 choices to colour."""
    def rec(x0, y0, d, sp, path, start):
        if d == 0:
            return
        for k, side in enumerate((-1, 1)):
            x1, y1 = x0 + side * sp, y0 - dy
            seg = clamp(p * depth - start)
            if seg <= 0:
                continue
            hp = highlight is not None and path + [k] == highlight[:len(path) + 1]
            partial_line(cr, x0, y0, x1, y1, seg, lw * (1.4 if hp else 1), hc if hp else ink, a)
            if seg >= 1:
                circle(cr, x1, y1, lw * 1.6, fill=hc if hp else ink, a=a)
                rec(x1, y1, d - 1, sp * shrink, path + [k], start + 1)
    circle(cr, x, y, lw * 1.8, fill=ink, a=a)
    rec(x, y, depth, spread, [], 0)


def checklist(cr, x, y, items, p=1.0, size=40, ink=INK, done_c=GREEN, gap=62, a=1.0, face=FONT_HAND):
    for i, it in enumerate(items):
        k = clamp(p * len(items) - i)
        if k <= 0:
            continue
        yy = y + i * gap
        rrect(cr, x, yy - size * 0.45, size * 0.9, size * 0.9, 6, fill=WHITE, stroke=ink, lw=4, a=a * eout(k))
        text(cr, it, x + size * 1.3, yy, size, c=ink, a=a * eout(k), face=face, bold=True, align="left")
        if k > 0.5:
            from .core import check
            check(cr, x + size * 0.45, yy, s=size / 46, c=done_c, w=9, p=clamp((k - 0.5) * 2), a=a)


def bar_chart(cr, x, y, values, labels=None, w=600, h=400, p=1.0, colors=None, ink=INK, a=1.0, maxv=None,
              size=30):
    """Bars grow upward from baseline y."""
    n = len(values)
    maxv = maxv or max(values)
    bw = w / n * 0.6
    line(cr, x - w / 2, y, x + w / 2, y, LW, ink, a)
    for i, v in enumerate(values):
        k = eout(clamp(p * n * 0.7 - i * 0.7 + 0.7))
        bh = h * v / maxv * k
        bx = x - w / 2 + (i + 0.5) * w / n - bw / 2
        c = colors[i] if colors else BLUE
        rect(cr, bx, y - bh, bw, bh, fill=c, stroke=ink, lw=4, a=a)
        if labels:
            text(cr, labels[i], bx + bw / 2, y + size, size, c=ink, a=a, face=FONT_HAND, bold=True)


def galaxy(cr, x, y, r=200, t=0.0, arms=3, c=(0.75, 0.8, 1.0), n=420, seed=1, a=1.0, tilt=0.45, rot=0.0):
    rr = rng(seed)
    glow(cr, x, y, r * 0.7, c, 0.35 * a)
    for i in range(n):
        arm = i % arms
        d = rr.random() ** 0.7
        ang = rot + t * 0.04 + arm * TAU / arms + d * 4.2 + rr.gauss(0, 0.25)
        px = math.cos(ang) * d * r
        py = math.sin(ang) * d * r * tilt
        sz = rr.uniform(0.8, 2.6) * (1.2 - d * 0.6)
        src(cr, c, a * rr.uniform(0.3, 1.0))
        cr.arc(x + px, y + py, sz, 0, TAU)
        cr.fill()
    glow(cr, x, y, r * 0.18, WHITE, 0.8 * a)


def road(cr, y, t=0.0, speed=0.0, c=(0.35, 0.36, 0.4)):
    rect(cr, 0, y, W, 120, fill=c)
    off = (t * speed) % 160
    for i in range(-1, 14):
        rect(cr, i * 160 - off, y + 55, 80, 10, fill=WHITE)


def scale_balance(cr, x, y, s=1.0, tilt=0.0, left=None, right=None):
    """Balance scale; tilt in radians (positive = right side down)."""
    with xform(cr, x, y, s):
        polyline(cr, [(-60, 0), (0, -20), (60, 0)], LW, INK, closed=True, fill=WHITE)
        line(cr, 0, -20, 0, -260, LW * 1.2, INK)
        with xform(cr, 0, -260, 1, tilt):
            line(cr, -200, 0, 200, 0, LW * 1.2, INK)
            for k, fn in ((-1, left), (1, right)):
                with xform(cr, k * 200, 0, 1, -tilt):
                    line(cr, 0, 0, -50, 90, 3, INK)
                    line(cr, 0, 0, 50, 90, 3, INK)
                    polyline(cr, [(-70, 90), (70, 90), (50, 110), (-50, 110)], LW, INK, closed=True, fill=WHITE)
                    if fn:
                        fn(cr)
        circle(cr, 0, -260, 10, fill=INK)


def water_pump(cr, x, y, s=1.0, t=0.0, flow=0.0, broken=0.0):
    with xform(cr, x, y, s):
        rect(cr, -30, -200, 60, 200, fill=(0.4, 0.55, 0.65), stroke=INK, lw=LW)
        line(cr, 30, -150, 90, -150, LW * 2, INK)
        line(cr, 90, -150, 90, -125, LW * 2, INK)
        ang = -0.4 + 0.5 * math.sin(t * 4) * (1 - broken)
        with xform(cr, 0, -200, 1, ang):
            line(cr, 0, 0, -120, 0, LW * 1.5, INK)
        circle(cr, 0, -200, 10, fill=INK)
        if flow > 0:
            for i in range(8):
                yy = -120 + ((t * 300 + i * 30) % 120)
                circle(cr, 90 + math.sin(i) * 4, yy, 7, fill=BLUE, a=flow)
        if broken > 0:
            text(cr, "!", 70, -250, 70, c=RED, a=broken, face=FONT_BOLD)


def shop(cr, x, y, s=1.0, sign="SHOP", lit=0.0, awn=RED):
    with xform(cr, x, y, s):
        rect(cr, -140, -220, 280, 220, fill=WHITE, stroke=INK, lw=LW)
        for i in range(7):
            polyline(cr, [(-140 + i * 40, -220), (-100 + i * 40, -220), (-100 + i * 40, -180), (-140 + i * 40, -180)],
                     3, INK, closed=True, fill=awn if i % 2 == 0 else WHITE)
        rect(cr, -110, -150, 120, 90, fill=lerpc3((0.8, 0.9, 1.0), YELLOW, lit), stroke=INK, lw=4)
        rect(cr, 40, -140, 70, 140, fill=INK)
        rrect(cr, -90, -270, 180, 44, 8, fill=WHITE, stroke=INK, lw=4)
        text(cr, sign, 0, -248, 30, face=FONT_HAND, bold=True)


def throne(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        polyline(cr, [(-70, 0), (-70, -150), (-90, -340), (-30, -300), (0, -360), (30, -300), (90, -340), (70, -150),
                      (70, 0)], LW, INK, closed=True, fill=(0.6, 0.1, 0.15))
        rect(cr, -80, -160, 160, 30, fill=YELLOW, stroke=INK, lw=LW)


def hill(cr, x, y, w=900, h=220, c=(0.2, 0.22, 0.28), ink=None):
    pts = bezier_pts([(x - w / 2, y), (x - w / 4, y - h * 1.3), (x + w / 4, y - h * 1.3), (x + w / 2, y)], 40)
    polyline(cr, pts, LW if ink else 0, ink or INK, closed=False, fill=c)
