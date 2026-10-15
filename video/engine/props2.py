"""Additional props for the What If series."""
import math

from .core import (INK, WHITE, PAPER, LIGHT, MID, GRAY, DARK, RED, BLUE, CYAN, YELLOW, GREEN, ORANGE, PURPLE, TAU,
                   FONT_HAND, FONT_BOLD, FONT_TITLE, FONT_SERIF, src, line, circle, ellipse, rrect, rect, polyline, arc,
                   text, glow, lerp, clamp, bezier_pts, xform, rng, star_shape, group)
from .props import LW, crown, coffee

GOLD = (0.98, 0.78, 0.20)
GOLD_D = (0.70, 0.50, 0.10)


def carriage(cr, x, y, s=1.0, t=0.0, roll=0.0):
    """Golden carriage, base at ground."""
    with xform(cr, x, y, s):
        for wx in (-120, 120):
            circle(cr, wx, -50, 50, fill=WHITE, stroke=INK, w=LW)
            for i in range(6):
                a = i / 6 * math.pi - roll
                line(cr, wx, -50, wx + math.cos(a) * 48, -50 + math.sin(a) * 48, 3, INK)
        polyline(cr, bezier_pts([(-170, -100), (-190, -260), (0, -330), (190, -260), (170, -100)], 30) + [(-170, -100)],
                 LW, INK, closed=True, fill=GOLD)
        rrect(cr, -70, -250, 140, 100, 30, fill=(0.85, 0.92, 1.0), stroke=INK, lw=LW)
        crown(cr, 0, -360, 0.5)


def pillow_crown(cr, x, y, s=1.0, glow_a=0.0):
    with xform(cr, x, y, s):
        if glow_a > 0:
            glow(cr, 0, -60, 220, YELLOW, glow_a)
        polyline(cr, bezier_pts([(-110, 0), (-120, -40), (0, -55), (120, -40), (110, 0), (0, 15), (-110, 0)], 30),
                 LW, INK, closed=True, fill=(0.65, 0.08, 0.14))
        for k in (-1, 1):
            line(cr, k * 105, -10, k * 125, 20, 5, YELLOW)
        crown(cr, 0, -80, 0.8)


def press_camera(cr, x, y, s=1.0, flash=0.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rrect(cr, -40, -28, 80, 56, 8, fill=INK)
        circle(cr, 0, 0, 18, fill=GRAY, stroke=WHITE, w=3)
        rect(cr, -30, -42, 26, 14, fill=INK)
        if flash > 0:
            glow(cr, 0, -40, 160, WHITE, 0.9 * flash)
            star_shape(cr, 0, -40, 40 * flash + 1, points=8, inner=0.3, fill=WHITE)


def pie_chart(cr, x, y, r, parts, p=1.0, rot=-math.pi / 2, labels=True, size=30, explode=None):
    """parts: [(fraction, color, label)]"""
    a0 = rot
    total = TAU * clamp(p)
    for i, (frac, col, lab) in enumerate(parts):
        a1 = a0 + TAU * frac
        a1c = min(a1, rot + total)
        if a1c <= a0:
            break
        ox = oy = 0
        if explode is not None and explode == i:
            mid = (a0 + a1) / 2
            ox, oy = math.cos(mid) * 30, math.sin(mid) * 30
        cr.move_to(x + ox, y + oy)
        cr.arc(x + ox, y + oy, r, a0, a1c)
        cr.close_path()
        src(cr, col)
        cr.fill_preserve()
        src(cr, INK)
        cr.set_line_width(5)
        cr.stroke()
        if labels and a1c >= a1 - 1e-6:
            mid = (a0 + a1) / 2
            text(cr, lab, x + ox + math.cos(mid) * r * 0.62, y + oy + math.sin(mid) * r * 0.62, size, face=FONT_BOLD,
                 c=WHITE, outline=INK, ow=5)
        a0 = a1


def ice_cream(cr, x, y, s=1.0, c=(1.0, 0.75, 0.8)):
    with xform(cr, x, y, s):
        polyline(cr, [(-35, -10), (35, -10), (0, 110)], LW, INK, closed=True, fill=(0.9, 0.7, 0.4))
        line(cr, -20, 20, 15, 40, 3, INK)
        line(cr, 18, 15, -10, 60, 3, INK)
        circle(cr, 0, -40, 45, fill=c, stroke=INK, w=LW)
        circle(cr, 12, -95, 32, fill=(0.6, 0.4, 0.25), stroke=INK, w=LW)
        circle(cr, 10, -135, 10, fill=RED, stroke=INK, w=3)


def gauge(cr, x, y, r, value, label=None, colors=(RED, YELLOW, GREEN), t=0.0, size=34):
    """Semicircle meter, value 0..1."""
    for i, c in enumerate(colors):
        a0 = math.pi + i * math.pi / len(colors)
        arc(cr, x, y, r, a0, a0 + math.pi / len(colors), r * 0.22, c)
    a = math.pi + math.pi * clamp(value) + math.sin(t * 25) * 0.01
    line(cr, x, y, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, 8, INK)
    circle(cr, x, y, 14, fill=INK)
    if label:
        text(cr, label, x, y + 50, size, face=FONT_BOLD)


def coin(cr, x, y, r=30, c=GOLD, a=1.0, rot=0.0):
    w = max(2, r * abs(math.cos(rot)))
    ellipse(cr, x, y, w, r, fill=c, stroke=INK, w=4, a=a)
    if w > r * 0.5:
        text(cr, "$", x, y, r * 1.1, face=FONT_TITLE, c=GOLD_D, a=a)


def coin_pile(cr, x, y, s=1.0, rows=6, seed=1):
    """Pyramid of coins with its base on y."""
    g = rng(seed)
    with xform(cr, x, y, s):
        for r in range(rows):
            n = rows - r
            for c in range(n):
                cx_ = (c - (n - 1) / 2) * 50 + g.uniform(-5, 5)
                cy_ = -14 - r * 22
                ellipse(cr, cx_, cy_, 28, 13, fill=GOLD, stroke=INK, w=3)


def money_stack(cr, x, y, s=1.0, n=6, c=(0.55, 0.78, 0.50)):
    with xform(cr, x, y, s):
        for i in range(n):
            yy = -i * 22
            rrect(cr, -90, yy - 20, 180, 22, 4, fill=c, stroke=INK, lw=3)
            rect(cr, -16, yy - 20, 32, 22, fill=(0.85, 0.95, 0.85))
        text(cr, "$", 0, -n * 22 + 11, 22, face=FONT_TITLE, c=(0.2, 0.45, 0.25))


def factory(cr, x, y, s=1.0, t=0.0, smoke=1.0, closed=0.0):
    with xform(cr, x, y, s):
        polyline(cr, [(-200, 0), (-200, -160), (-120, -220), (-120, -160), (-40, -220), (-40, -160), (40, -220),
                      (40, -160), (200, -160), (200, 0)], LW, INK, closed=True, fill=(0.75, 0.72, 0.70))
        rect(cr, 110, -360, 50, 200, fill=(0.6, 0.55, 0.52), stroke=INK, lw=LW)
        for i in range(3):
            rect(cr, -170 + i * 90, -110, 50, 50, fill=(0.85, 0.9, 1.0) if closed < 0.5 else (0.3, 0.3, 0.35),
                 stroke=INK, lw=4)
        if smoke > 0 and closed < 0.5:
            for i in range(4):
                f = (t * 0.4 + i * 0.25) % 1
                circle(cr, 135 + 30 * f + 10 * math.sin(t + i), -380 - 160 * f, 22 + 30 * f, fill=(0.8, 0.8, 0.82),
                       a=smoke * (1 - f) * 0.8)
        if closed > 0:
            with group(cr, closed):
                rect(cr, -60, -90, 120, 90, fill=(0.45, 0.45, 0.48), stroke=INK, lw=4)
                for i in range(5):
                    line(cr, -60, -80 + i * 18, 60, -80 + i * 18, 3, INK)
                rrect(cr, -110, -300, 220, 60, 8, fill=RED, stroke=INK, lw=4)
                text(cr, "CLOSING", 0, -270, 34, face=FONT_TITLE, c=WHITE)


def cracked_ground(cr, x0, x1, y, seed=2, c=(0.80, 0.65, 0.45)):
    rect(cr, x0, y, x1 - x0, 400, fill=c)
    line(cr, x0, y, x1, y, LW, INK)
    g = rng(seed)
    for i in range(18):
        cx_, cy_ = g.uniform(x0, x1), y + g.uniform(20, 180)
        pts = [(cx_, cy_)]
        for k in range(4):
            pts.append((pts[-1][0] + g.uniform(-60, 60), pts[-1][1] + g.uniform(-25, 25)))
        polyline(cr, pts, 3, (0.45, 0.32, 0.2))


def newspaper(cr, x, y, s=1.0, headline="DAILY NEWS", rot=0.0, cartoon=None):
    with xform(cr, x, y, s, rot):
        rect(cr, -170, -220, 340, 440, fill=(0.97, 0.96, 0.92), stroke=INK, lw=LW)
        text(cr, headline, 0, -180, 34, face=FONT_TITLE)
        line(cr, -150, -150, 150, -150, 3, INK)
        if cartoon:
            rect(cr, -150, -130, 300, 190, fill=WHITE, stroke=INK, lw=3)
            cartoon(cr)
        for i in range(6):
            line(cr, -150, 90 + i * 22, 150 - (i % 3) * 30, 90 + i * 22, 3, MID)


def sign(cr, x, y, s=1.0, txt="", c=WHITE, rot=0.0, w=220, h=110, size=34, ink=INK):
    with xform(cr, x, y, s, rot):
        line(cr, 0, 0, 0, 170, 7, (0.55, 0.40, 0.28))
        rrect(cr, -w / 2, -h, w, h, 10, fill=c, stroke=ink, lw=LW)
        rows = txt.split("\n")
        for i, r in enumerate(rows):
            text(cr, r, 0, -h / 2 + (i - (len(rows) - 1) / 2) * size * 1.05, size, face=FONT_HAND, bold=True, c=ink)


def statue(cr, x, y, s=1.0, gold=True, tilt=0.0, pose_fn=None):
    """A stickman statue on a pedestal (base at ground). pose_fn(cr) draws the figure at origin."""
    from . import stickman as sm
    col = GOLD if gold else (0.75, 0.75, 0.72)
    with xform(cr, x, y, s):
        rect(cr, -110, -120, 220, 120, fill=col if gold else (0.85, 0.85, 0.8), stroke=INK, lw=LW)
        with xform(cr, 0, -120, 1.0, tilt):
            p = sm.pose("point_up", x=0, s=1.1, smile=0.5, brow=0.4)
            p = sm.on_ground(p, 0)
            sm.draw(cr, p, ink=GOLD_D if gold else GRAY, fill=col, acc=("tuft", "crown"))


def mirror(cr, x, y, s=1.0, inner=None):
    with xform(cr, x, y, s):
        ellipse(cr, 0, 0, 170, 240, fill=(0.75, 0.82, 0.88), stroke=(0.6, 0.45, 0.2), w=18)
        if inner:
            cr.save()
            cr.translate(0, 0)
            cr.scale(1, 1)
            ellipse_path = None
            cr.arc(0, 0, 1, 0, TAU)
            cr.restore()
            cr.save()
            cr.scale(170, 240)
            cr.arc(0, 0, 0.95, 0, TAU)
            cr.restore()
            cr.save()
            cr.clip()
            inner(cr)
            cr.restore()
            del ellipse_path


def bus(cr, x, y, s=1.0, t=0.0, c=(0.98, 0.78, 0.2), face=1):
    with xform(cr, x, y, s, sx=s * face, sy=s):
        rrect(cr, -300, -230, 600, 200, 30, fill=c, stroke=INK, lw=LW)
        for i in range(5):
            rrect(cr, -260 + i * 105, -200, 85, 70, 8, fill=(0.8, 0.9, 1.0), stroke=INK, lw=4)
        for wx in (-190, 190):
            circle(cr, wx, -30, 38, fill=INK)
            circle(cr, wx, -30, 14, fill=LIGHT)


def market_stall(cr, x, y, s=1.0, awn=RED):
    with xform(cr, x, y, s):
        rect(cr, -180, -110, 360, 110, fill=(0.75, 0.55, 0.35), stroke=INK, lw=LW)
        for i in range(6):
            polyline(cr, [(-200 + i * 66, -300), (-134 + i * 66, -300), (-134 + i * 66, -250), (-200 + i * 66, -250)],
                     3, INK, closed=True, fill=awn if i % 2 == 0 else WHITE)
        for k in (-190, 190):
            line(cr, k, -250, k, 0, 6, INK)
        for i, c in enumerate((RED, ORANGE, YELLOW, GREEN)):
            circle(cr, -120 + i * 80, -130, 26, fill=c, stroke=INK, w=3)


def parchment(cr, x, y, w=520, h=640, title="", lines_=(), t_unroll=1.0, size=34, s=1.0, rot=0.0, seal=False):
    with xform(cr, x, y, s, rot):
        hh = h * clamp(t_unroll)
        rect(cr, -w / 2, -h / 2, w, hh, fill=(0.96, 0.89, 0.72), stroke=INK, lw=LW)
        for k in (-1, 1) if t_unroll < 1 else (-1,):
            pass
        ellipse(cr, 0, -h / 2, w / 2 + 20, 18, fill=(0.90, 0.80, 0.60), stroke=INK, w=LW)
        ellipse(cr, 0, -h / 2 + hh, w / 2 + 20, 18, fill=(0.90, 0.80, 0.60), stroke=INK, w=LW)
        cr.save()
        cr.rectangle(-w / 2, -h / 2, w, hh)
        cr.clip()
        if title:
            text(cr, title, 0, -h / 2 + 70, size * 1.4, face=FONT_SERIF, bold=True)
        for i, ln in enumerate(lines_):
            text(cr, ln, -w / 2 + 50, -h / 2 + 150 + i * size * 1.5, size, face=FONT_HAND, bold=True, align="left")
        if seal:
            circle(cr, w / 2 - 80, h / 2 - 80, 40, fill=RED, stroke=INK, w=4)
        cr.restore()


def gavel(cr, x, y, s=1.0, rot=-0.5):
    with xform(cr, x, y, s, rot):
        line(cr, 0, 0, 0, 160, 12, (0.55, 0.38, 0.22))
        rrect(cr, -70, -40, 140, 60, 14, fill=(0.55, 0.38, 0.22), stroke=INK, lw=LW)


def ballot_box(cr, x, y, s=1.0, t=0.0, drop=0.0):
    with xform(cr, x, y, s):
        rect(cr, -110, -180, 220, 180, fill=WHITE, stroke=INK, lw=LW)
        rect(cr, -60, -186, 120, 12, fill=INK)
        text(cr, "VOTE", 0, -90, 44, face=FONT_TITLE, c=BLUE)
        if drop > 0:
            yy = lerp(-320, -190, clamp(drop))
            rect(cr, -36, yy - 50, 72, 50, fill=WHITE, stroke=INK, lw=3, a=1 - clamp((drop - 1) * 3))
            line(cr, -22, yy - 25, 22, yy - 25, 3, INK)


def museum_case(cr, x, y, s=1.0, inner=None):
    with xform(cr, x, y, s):
        rect(cr, -150, -100, 300, 100, fill=(0.85, 0.82, 0.78), stroke=INK, lw=LW)
        rect(cr, -130, -420, 260, 320, fill=(0.85, 0.95, 1.0), stroke=INK, lw=LW, a=1.0)
        if inner:
            inner(cr)
        line(cr, -100, -400, -40, -320, 4, WHITE, 0.8)
        line(cr, -80, -400, -20, -320, 4, WHITE, 0.5)


def book_big(cr, x, y, s=1.0, title="HISTORY", c=(0.45, 0.25, 0.15)):
    with xform(cr, x, y, s):
        rrect(cr, -160, -220, 320, 440, 14, fill=c, stroke=INK, lw=LW)
        rect(cr, -160, -220, 40, 440, fill=(0.35, 0.18, 0.1))
        rrect(cr, -100, -150, 220, 80, 8, fill=GOLD, stroke=INK, lw=3)
        text(cr, title, 10, -110, 36, face=FONT_TITLE, c=INK)


def hourglass(cr, x, y, s=1.0, p=0.5, t=0.0, c=(0.95, 0.80, 0.45)):
    with xform(cr, x, y, s):
        rect(cr, -90, -170, 180, 20, fill=(0.55, 0.38, 0.22), stroke=INK, lw=4)
        rect(cr, -90, 150, 180, 20, fill=(0.55, 0.38, 0.22), stroke=INK, lw=4)
        top = [(-70, -150), (70, -150), (8, 0), (-8, 0)]
        bot = [(-8, 0), (8, 0), (70, 150), (-70, 150)]
        polyline(cr, top, LW, INK, closed=True, fill=(0.9, 0.95, 1.0))
        polyline(cr, bot, LW, INK, closed=True, fill=(0.9, 0.95, 1.0))
        q = clamp(p)
        ty = lerp(-140, -10, q)
        hw = 70 * (1 - (ty + 150) / 150) + 8
        polyline(cr, [(-hw + 4, ty), (hw - 4, ty), (6, -4), (-6, -4)], 0, INK, closed=True, fill=c)
        by = lerp(146, 40, q)
        polyline(cr, [(-66, 146), (66, 146), (0, by - 20)], 0, INK, closed=True, fill=c)
        if 0 < q < 1:
            line(cr, 0, 0, 0, 146, 3, c)


def horse(cr, x, y, s=1.0, c=GOLD):
    with xform(cr, x, y, s):
        ellipse(cr, 0, -150, 130, 55, fill=c, stroke=INK, w=LW)
        polyline(cr, [(90, -180), (150, -280), (200, -270), (190, -240), (120, -160)], LW, INK, closed=True, fill=c)
        for lx in (-90, -50, 50, 90):
            line(cr, lx, -110, lx, 0, 10, INK)
        line(cr, -130, -160, -180, -100, 8, INK)


def cheese(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        polyline(cr, [(-90, 0), (90, 0), (90, -70), (-90, -20)], LW, INK, closed=True, fill=(1.0, 0.85, 0.3))
        for (hx, hy, r) in ((-40, -18, 10), (20, -30, 14), (60, -15, 8)):
            circle(cr, hx, hy, r, fill=(0.9, 0.7, 0.2))
        for i in range(3):
            f = (i * 0.3)
            arc(cr, 20 + i * 25, -110 - i * 10, 14, 3.5, 5.8, 4, GREEN, 0.7)
            del f


def pigeon(cr, x, y, s=1.0, face=1, flap=0.0, t=0.0, c=(0.62, 0.64, 0.70)):
    """Pigeon standing at (x, y) (feet). flap 0..1 raises the wings."""
    with xform(cr, x, y, s, sx=s * face, sy=s):
        line(cr, -8, 0, -4, -24, 4, ORANGE)
        line(cr, 10, 0, 6, -24, 4, ORANGE)
        ellipse(cr, 0, -50, 46, 30, fill=c, stroke=INK, w=4)
        polyline(cr, [(-40, -56), (-78, -70), (-72, -44)], 4, INK, closed=True, fill=c)
        circle(cr, 36, -84, 20, fill=c, stroke=INK, w=4)
        circle(cr, 42, -88, 4, fill=INK)
        polyline(cr, [(54, -84), (70, -79), (54, -74)], 3, INK, closed=True, fill=ORANGE)
        a = -0.3 - 1.4 * clamp(flap) * (0.6 + 0.4 * math.sin(t * 40))
        with xform(cr, -6, -58, 1.0, a):
            ellipse(cr, -24, 0, 34, 14, fill=(0.50, 0.52, 0.58), stroke=INK, w=3)


def sandwich(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        polyline(cr, [(-50, 10), (50, 10), (0, -50)], 4, INK, closed=True, fill=(0.95, 0.82, 0.55))
        line(cr, -40, 0, 40, 0, 6, GREEN)
        line(cr, -32, -8, 32, -8, 5, RED)


def spreadsheet(cr, x, y, cols=8, rows=5, cw=150, ch=80, k_people=0.0, t=0.0, seed=4):
    """Grid of numbers; k_people 0..1 morphs cells into little faces."""
    r = rng(seed)
    x0, y0 = x - cols * cw / 2, y - rows * ch / 2
    rect(cr, x0, y0 - 50, cols * cw, rows * ch + 50, fill=WHITE, stroke=INK, lw=LW)
    rect(cr, x0, y0 - 50, cols * cw, 50, fill=(0.80, 0.90, 0.80), stroke=INK, lw=3)
    for i in range(1, cols):
        line(cr, x0 + i * cw, y0 - 50, x0 + i * cw, y0 + rows * ch, 2, MID)
    for j in range(rows):
        line(cr, x0, y0 + j * ch, x0 + cols * cw, y0 + j * ch, 2, MID)
    for j in range(rows):
        for i in range(cols):
            v = r.randint(100, 99999)
            cx, cy = x0 + (i + 0.5) * cw, y0 + (j + 0.5) * ch
            kk = clamp(k_people * 2.2 - (i + j) * 0.09)
            if kk < 1:
                text(cr, f"{v:,}", cx, cy, 30, face=FONT_BOLD, c=INK, a=1 - kk)
            if kk > 0:
                with xform(cr, cx, cy + 4, 0.6 + 0.4 * kk):
                    circle(cr, 0, -6, 20, fill=WHITE, stroke=INK, w=4, a=kk)
                    circle(cr, -7, -10, 2.8, fill=INK, a=kk)
                    circle(cr, 7, -10, 2.8, fill=INK, a=kk)
                    arc(cr, 0, -4, 8, 0.4, math.pi - 0.4, 3, INK, a=kk)
                    line(cr, 0, 14, 0, 34, 4, INK, kk)
