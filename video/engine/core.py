"""Core 2D drawing toolkit on top of Cairo.

Every animation in the film is a pure function of time, so any frame can be
rendered independently (which lets chapters render in parallel).
"""
import math
import random
from contextlib import contextmanager

import cairo

W, H, FPS = 1920, 1080, 30
CX, CY = W / 2, H / 2
TAU = math.tau

# ---------------------------------------------------------------- palette
INK = (0.075, 0.075, 0.09)
PAPER = (0.965, 0.962, 0.945)
PAPER2 = (0.915, 0.912, 0.895)
LIGHT = (0.86, 0.86, 0.85)
MID = (0.55, 0.55, 0.56)
GRAY = (0.35, 0.35, 0.37)
DARK = (0.055, 0.06, 0.085)
DARK2 = (0.10, 0.11, 0.15)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
RED = (0.90, 0.20, 0.20)
BLUE = (0.18, 0.50, 0.96)
CYAN = (0.25, 0.80, 0.95)
YELLOW = (1.00, 0.78, 0.12)
GREEN = (0.20, 0.72, 0.38)
ORANGE = (0.98, 0.55, 0.15)
PURPLE = (0.55, 0.35, 0.90)
BOARD = (0.16, 0.24, 0.21)

FONT_TITLE = "Inter Display Black"
FONT_BOLD = "Inter Display ExtraBold"
FONT_UI = "Inter"
FONT_HAND = "Kalam"
FONT_HAND2 = "Patrick Hand"
FONT_SERIF = "DejaVu Serif"


# ---------------------------------------------------------------- maths
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def prog(t, start, dur):
    """0..1 progress of t through [start, start+dur]."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def eout(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ein(t):
    t = clamp(t)
    return t ** 3


def back(t, s=1.70158):
    t = clamp(t)
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def elastic(t):
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (TAU / 3)) + 1


def bounce(t):
    t = clamp(t)
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def inout(t, start, end, fade=0.4):
    """1 inside [start, end] with eased ramps of `fade` seconds."""
    return ease(prog(t, start, fade)) * (1 - ease(prog(t, end - fade, fade)))


def wobble(t, seed=0, freq=1.0, amp=1.0):
    """Smooth pseudo-noise in [-amp, amp]."""
    return amp * (0.55 * math.sin(t * freq * 2.1 + seed * 1.7)
                  + 0.30 * math.sin(t * freq * 3.7 + seed * 4.1)
                  + 0.15 * math.sin(t * freq * 6.3 + seed * 2.3))


def rng(seed):
    return random.Random(seed)


# ---------------------------------------------------------------- surfaces
def new_surface():
    return cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def new_ctx(surf):
    cr = cairo.Context(surf)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    return cr


def src(cr, c, a=1.0):
    if len(c) == 4:
        cr.set_source_rgba(c[0], c[1], c[2], c[3] * a)
    else:
        cr.set_source_rgba(c[0], c[1], c[2], a)


@contextmanager
def saved(cr):
    cr.save()
    try:
        yield
    finally:
        cr.restore()


@contextmanager
def group(cr, alpha=1.0):
    """Draw a compound element with uniform opacity."""
    if alpha >= 0.999:
        yield
        return
    cr.push_group()
    try:
        yield
    finally:
        cr.pop_group_to_source()
        cr.paint_with_alpha(max(0.0, alpha))


@contextmanager
def xform(cr, x=0, y=0, s=1.0, rot=0.0, sx=None, sy=None):
    """Translate to (x, y), rotate (radians) and scale."""
    cr.save()
    cr.translate(x, y)
    if rot:
        cr.rotate(rot)
    kx = sx if sx is not None else s
    ky = sy if sy is not None else s
    cr.scale(kx if abs(kx) > 1e-4 else 1e-4, ky if abs(ky) > 1e-4 else 1e-4)
    try:
        yield
    finally:
        cr.restore()


@contextmanager
def camera(cr, zoom=1.0, fx=CX, fy=CY, rot=0.0, sx=CX, sy=CY):
    """World point (fx, fy) is shown at screen point (sx, sy) with zoom."""
    cr.save()
    cr.translate(sx, sy)
    if rot:
        cr.rotate(rot)
    cr.scale(zoom, zoom)
    cr.translate(-fx, -fy)
    try:
        yield
    finally:
        cr.restore()


def shake(t, amp, freq=22.0, seed=0):
    return (wobble(t, seed, freq, amp), wobble(t, seed + 9, freq, amp))


# ---------------------------------------------------------------- backgrounds
def fill_bg(cr, c):
    src(cr, c)
    cr.paint()


def vgrad(cr, top, bottom, x0=0, y0=0, x1=W, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top[:3])
    g.add_color_stop_rgb(1, *bottom[:3])
    cr.set_source(g)
    cr.rectangle(x0, y0, x1 - x0, y1 - y0)
    cr.fill()


def paper_bg(cr, c=PAPER, grid=False, t=0.0):
    fill_bg(cr, c)
    if grid:
        src(cr, INK, 0.035)
        cr.set_line_width(1.5)
        for x in range(0, W + 1, 60):
            cr.move_to(x, 0)
            cr.line_to(x, H)
        for y in range(0, H + 1, 60):
            cr.move_to(0, y)
            cr.line_to(W, y)
        cr.stroke()


def vignette(cr, strength=0.35, color=BLACK, inner=0.45):
    g = cairo.RadialGradient(CX, CY, H * inner, CX, CY, W * 0.75)
    g.add_color_stop_rgba(0, *color[:3], 0)
    g.add_color_stop_rgba(1, *color[:3], strength)
    cr.set_source(g)
    cr.paint()


def spotlight(cr, x, y, r, strength=0.85, color=BLACK):
    """Darken everything except a soft circle around (x, y)."""
    g = cairo.RadialGradient(x, y, r * 0.35, x, y, r)
    g.add_color_stop_rgba(0, *color[:3], 0)
    g.add_color_stop_rgba(1, *color[:3], strength)
    cr.set_source(g)
    cr.paint()


def glow(cr, x, y, r, c, a=0.6):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *c[:3], a)
    g.add_color_stop_rgba(0.4, *c[:3], a * 0.35)
    g.add_color_stop_rgba(1, *c[:3], 0)
    cr.set_source(g)
    cr.arc(x, y, r, 0, TAU)
    cr.fill()


def stars(cr, t, n=260, seed=7, alpha=1.0, color=WHITE, drift=0.0, area=(0, 0, W, H)):
    r = rng(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        x = r.uniform(x0, x1)
        y = r.uniform(y0, y1)
        x = x0 + ((x - x0 + drift * t * r.uniform(0.3, 1.0)) % (x1 - x0))
        size = r.choice([1.0, 1.2, 1.5, 1.8, 2.4, 3.2])
        tw = 0.55 + 0.45 * math.sin(t * r.uniform(0.6, 2.4) + r.uniform(0, 6))
        src(cr, color, alpha * tw * r.uniform(0.35, 1.0))
        cr.arc(x, y, size, 0, TAU)
        cr.fill()


# ---------------------------------------------------------------- primitives
def line(cr, x1, y1, x2, y2, w=6, c=INK, a=1.0, dash=None):
    src(cr, c, a)
    cr.set_line_width(w)
    if dash:
        cr.set_dash(dash)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()
    if dash:
        cr.set_dash([])


def partial_line(cr, x1, y1, x2, y2, p, w=6, c=INK, a=1.0):
    if p <= 0:
        return
    line(cr, x1, y1, lerp(x1, x2, p), lerp(y1, y2, p), w, c, a)


def polyline(cr, pts, w=6, c=INK, a=1.0, closed=False, fill=None, fa=1.0, dash=None):
    if len(pts) < 2:
        return
    cr.move_to(*pts[0])
    for p in pts[1:]:
        cr.line_to(*p)
    if closed:
        cr.close_path()
    if fill is not None:
        src(cr, fill, fa)
        cr.fill_preserve() if w else cr.fill()
    if w:
        src(cr, c, a)
        cr.set_line_width(w)
        if dash:
            cr.set_dash(dash)
        cr.stroke()
        if dash:
            cr.set_dash([])
    else:
        cr.new_path()


def partial_poly(cr, pts, p, w=6, c=INK, a=1.0):
    """Draw the first fraction p of a polyline (by length)."""
    if p <= 0 or len(pts) < 2:
        return
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(segs) * clamp(p)
    out = [pts[0]]
    for i, sl in enumerate(segs):
        if total >= sl:
            out.append(pts[i + 1])
            total -= sl
        else:
            f = total / sl if sl else 0
            out.append((lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)))
            break
    polyline(cr, out, w, c, a)


def circle(cr, x, y, r, fill=None, stroke=None, w=6, a=1.0, fa=None):
    if r <= 0:
        return
    cr.new_sub_path()
    cr.arc(x, y, r, 0, TAU)
    if fill is not None:
        src(cr, fill, a if fa is None else fa)
        if stroke is not None:
            cr.fill_preserve()
        else:
            cr.fill()
    if stroke is not None:
        src(cr, stroke, a)
        cr.set_line_width(w)
        cr.stroke()
    cr.new_path()


def arc(cr, x, y, r, a1, a2, w=6, c=INK, a=1.0):
    src(cr, c, a)
    cr.set_line_width(w)
    cr.new_sub_path()
    cr.arc(x, y, r, a1, a2)
    cr.stroke()


def ellipse(cr, x, y, rx, ry, fill=None, stroke=None, w=5, a=1.0, rot=0.0):
    if rx <= 0 or ry <= 0:
        return
    cr.save()
    cr.translate(x, y)
    if rot:
        cr.rotate(rot)
    cr.scale(rx, ry)
    cr.arc(0, 0, 1, 0, TAU)
    cr.restore()
    if fill is not None:
        src(cr, fill, a)
        if stroke is not None:
            cr.fill_preserve()
        else:
            cr.fill()
    if stroke is not None:
        src(cr, stroke, a)
        cr.set_line_width(w)
        cr.stroke()
    cr.new_path()


def rrect_path(cr, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -TAU / 4, 0)
    cr.arc(x + w - r, y + h - r, r, 0, TAU / 4)
    cr.arc(x + r, y + h - r, r, TAU / 4, TAU / 2)
    cr.arc(x + r, y + r, r, TAU / 2, 3 * TAU / 4)
    cr.close_path()


def rrect(cr, x, y, w, h, r=12, fill=None, stroke=None, lw=5, a=1.0, fa=None):
    rrect_path(cr, x, y, w, h, r)
    if fill is not None:
        src(cr, fill, a if fa is None else fa)
        if stroke is not None:
            cr.fill_preserve()
        else:
            cr.fill()
    if stroke is not None:
        src(cr, stroke, a)
        cr.set_line_width(lw)
        cr.stroke()
    cr.new_path()


def rect(cr, x, y, w, h, fill=None, stroke=None, lw=5, a=1.0):
    rrect(cr, x, y, w, h, 0, fill, stroke, lw, a)


def arrow(cr, x1, y1, x2, y2, w=6, c=INK, a=1.0, head=22, p=1.0, dash=None):
    if p <= 0:
        return
    x2, y2 = lerp(x1, x2, p), lerp(y1, y2, p)
    ang = math.atan2(y2 - y1, x2 - x1)
    line(cr, x1, y1, x2 - math.cos(ang) * head * 0.4, y2 - math.sin(ang) * head * 0.4, w, c, a, dash)
    polyline(cr, [(x2, y2),
                  (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45)),
                  (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))],
             w=max(2, w * 0.5), c=c, a=a, closed=True, fill=c, fa=a)


def curve_arrow(cr, pts, w=6, c=INK, a=1.0, head=22, p=1.0):
    """Arrow along a quadratic-ish polyline sampled from control points."""
    samp = bezier_pts(pts, 40)
    n = max(2, int(len(samp) * clamp(p)))
    part = samp[:n]
    polyline(cr, part, w, c, a)
    if len(part) >= 2:
        (xa, ya), (xb, yb) = part[-2], part[-1]
        ang = math.atan2(yb - ya, xb - xa)
        polyline(cr, [(xb, yb),
                      (xb - head * math.cos(ang - 0.45), yb - head * math.sin(ang - 0.45)),
                      (xb - head * math.cos(ang + 0.45), yb - head * math.sin(ang + 0.45))],
                 w=max(2, w * 0.5), c=c, a=a, closed=True, fill=c, fa=a)


def bezier_pts(ctrl, n=30):
    """Sample a Bezier curve of arbitrary degree."""
    out = []
    for i in range(n + 1):
        t = i / n
        pts = list(ctrl)
        while len(pts) > 1:
            pts = [(lerp(pts[j][0], pts[j + 1][0], t), lerp(pts[j][1], pts[j + 1][1], t))
                   for j in range(len(pts) - 1)]
        out.append(pts[0])
    return out


def star_shape(cr, x, y, r, points=5, inner=0.45, rot=-TAU / 4, fill=YELLOW, stroke=None, w=4, a=1.0):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        ang = rot + i * TAU / (points * 2)
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    polyline(cr, pts, w if stroke else 0, stroke or INK, a, closed=True, fill=fill, fa=a)


def check(cr, x, y, s=1.0, c=GREEN, w=10, p=1.0, a=1.0):
    pts = [(x - 22 * s, y), (x - 6 * s, y + 18 * s), (x + 26 * s, y - 20 * s)]
    partial_poly(cr, pts, p, w * s, c, a)


def cross(cr, x, y, s=1.0, c=RED, w=12, p=1.0, a=1.0):
    d = 26 * s
    partial_line(cr, x - d, y - d, x + d, y + d, clamp(p * 2), w * s, c, a)
    partial_line(cr, x + d, y - d, x - d, y + d, clamp(p * 2 - 1), w * s, c, a)


# ---------------------------------------------------------------- text
def font(cr, face=FONT_UI, size=40, bold=False, italic=False):
    cr.select_font_face(face,
                        cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)


def text_w(cr, s, face=FONT_UI, size=40, bold=False, italic=False):
    font(cr, face, size, bold, italic)
    return cr.text_extents(s)[4]


def text(cr, s, x, y, size=40, c=INK, a=1.0, face=FONT_UI, align="center",
         valign="middle", bold=False, italic=False, outline=None, ow=6, rot=0.0, scale=1.0):
    """Draw a single line of text. valign: 'middle', 'baseline', 'top'."""
    if a <= 0 or not s:
        return 0
    font(cr, face, size, bold, italic)
    xb, yb, tw, th, xa, ya = cr.text_extents(s)
    fe = cr.font_extents()  # ascent, descent, height, ...
    if align == "center":
        dx = -xa / 2
    elif align == "right":
        dx = -xa
    else:
        dx = 0
    if valign == "middle":
        dy = (fe[0] - fe[1]) / 2 * 0.92
    elif valign == "top":
        dy = fe[0]
    else:
        dy = 0
    cr.save()
    cr.translate(x, y)
    if rot:
        cr.rotate(rot)
    if scale != 1.0:
        sc = scale if abs(scale) > 1e-4 else 1e-4
        cr.scale(sc, sc)
    cr.move_to(dx, dy)
    if outline is not None:
        cr.text_path(s)
        src(cr, outline, a)
        cr.set_line_width(ow)
        cr.stroke_preserve()
        src(cr, c, a)
        cr.fill()
    else:
        src(cr, c, a)
        cr.show_text(s)
    cr.restore()
    return xa


def text_lines(cr, lines, x, y, size=40, lh=1.25, **kw):
    n = len(lines)
    for i, ln in enumerate(lines):
        text(cr, ln, x, y + (i - (n - 1) / 2) * size * lh, size, **kw)


def wrap(cr, s, maxw, face=FONT_UI, size=40, bold=False):
    font(cr, face, size, bold)
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if cr.text_extents(trial)[4] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def typewriter(cr, s, x, y, p, size=40, cursor=True, **kw):
    n = int(round(len(s) * clamp(p)))
    shown = s[:n]
    kw.setdefault("align", "left")
    w = text(cr, shown, x, y, size, **kw)
    if cursor and p < 1.0:
        c = kw.get("c", INK)
        rect(cr, x + (w if kw["align"] == "left" else w / 2) + 4, y - size * 0.42, size * 0.08, size * 0.8, fill=c)


def pop_text(cr, s, x, y, t, size=60, dur=0.45, **kw):
    """Text that pops in with an overshoot at t=0."""
    if t < 0:
        return
    k = back(prog(t, 0, dur), 2.4)
    a = kw.pop("a", 1.0) * clamp(t / (dur * 0.5))
    text(cr, s, x, y, size, a=a, scale=max(0.001, k), **kw)


def words_reveal(cr, s, x, y, t, size=50, per=0.12, dur=0.35, rise=24, align="center", **kw):
    """Words fade and rise in one after another starting at t=0."""
    words = s.split()
    face = kw.get("face", FONT_UI)
    bold = kw.get("bold", False)
    font(cr, face, size, bold)
    space = cr.text_extents(" ")[4]
    widths = [cr.text_extents(wd)[4] for wd in words]
    total = sum(widths) + space * (len(words) - 1)
    cx = x - total / 2 if align == "center" else x
    base_a = kw.pop("a", 1.0)
    for i, wd in enumerate(words):
        p = eout(prog(t, i * per, dur))
        if p > 0:
            text(cr, wd, cx, y + rise * (1 - p), size, a=base_a * p, align="left", **kw)
        cx += widths[i] + space


def label_box(cr, s, x, y, size=34, c=INK, bg=WHITE, pad=16, face=FONT_HAND, bold=True, a=1.0, lw=4, r=12, scale=1.0):
    font(cr, face, size, bold)
    tw = cr.text_extents(s)[4]
    w, h = tw + pad * 2, size * 1.35
    with xform(cr, x, y, scale):
        rrect(cr, -w / 2, -h / 2, w, h, r, fill=bg, stroke=c, lw=lw, a=a)
        text(cr, s, 0, 0, size, c=c, a=a, face=face, bold=bold)
    return w, h


def stamp(cr, s, x, y, t, size=80, c=RED, rot=-0.12, dur=0.35, a=1.0, face=FONT_TITLE):
    """Rubber-stamp style text that slams down at t=0."""
    if t < 0:
        return
    p = prog(t, 0, dur)
    sc = lerp(2.2, 1.0, eout(p))
    al = a * clamp(p * 3)
    font(cr, face, size)
    tw = cr.text_extents(s)[4]
    with xform(cr, x, y, sc, rot):
        rrect(cr, -tw / 2 - 26, -size * 0.75, tw + 52, size * 1.5, 14, stroke=c, lw=8, a=al)
        text(cr, s, 0, 0, size, c=c, a=al, face=face)


# ---------------------------------------------------------------- bubbles
def speech_bubble(cr, x, y, w, h, tx, ty, fill=WHITE, stroke=INK, lw=5, a=1.0, scale=1.0, r=28):
    """Rounded speech bubble centred at (x, y) with a tail pointing at (tx, ty)."""
    if scale <= 0.01:
        return
    with xform(cr, x, y, scale):
        lx, ly = (tx - x) / scale, (ty - y) / scale
        bx = clamp(lx, -w / 2 + r + 10, w / 2 - r - 30)
        base_y = h / 2 if ly > 0 else -h / 2
        rrect_path(cr, -w / 2, -h / 2, w, h, r)
        src(cr, fill, a)
        cr.fill()
        cr.move_to(bx, base_y - (4 if ly > 0 else -4))
        cr.line_to(lx, ly)
        cr.line_to(bx + 34, base_y - (4 if ly > 0 else -4))
        cr.close_path()
        cr.fill()
        # outline
        rrect_path(cr, -w / 2, -h / 2, w, h, r)
        src(cr, stroke, a)
        cr.set_line_width(lw)
        cr.stroke()
        src(cr, fill, a)
        cr.rectangle(bx + 3, base_y - lw - 2 if ly > 0 else base_y - 3, 28, lw + 6)
        cr.fill()
        polyline(cr, [(bx + 1, base_y), (lx, ly), (bx + 33, base_y)], lw, stroke, a)


def thought_bubble(cr, x, y, w, h, tx, ty, fill=WHITE, stroke=INK, lw=5, a=1.0, scale=1.0, t=0.0):
    if scale <= 0.01:
        return
    with xform(cr, x, y, scale):
        n = 11
        pts = []
        for i in range(n):
            ang = i / n * TAU
            pts.append((math.cos(ang) * w / 2 * 0.86, math.sin(ang) * h / 2 * 0.80))
        for (px, py) in pts:
            circle(cr, px, py, min(w, h) * 0.2 + 3 * math.sin(t * 2 + px), stroke=stroke, w=lw * 2, a=a)
        for (px, py) in pts:
            circle(cr, px, py, min(w, h) * 0.2 + 3 * math.sin(t * 2 + px), fill=fill, a=a)
        ellipse(cr, 0, 0, w / 2 * 0.86, h / 2 * 0.8, fill=fill, a=a)
        lx, ly = (tx - x) / scale, (ty - y) / scale
        for k, rr in ((0.62, 16), (0.80, 11), (0.93, 7)):
            bx = lerp(0, lx, k)
            by = lerp(h * 0.42 if ly > 0 else -h * 0.42, ly, k)
            circle(cr, bx, by, rr, fill=fill, stroke=stroke, w=lw, a=a)


# ---------------------------------------------------------------- particles
def burst(cr, x, y, t, n=14, dist=160, size=8, c=YELLOW, dur=0.7, seed=1, a=1.0, shape="dot"):
    """Radial particle burst starting at t=0."""
    if t < 0 or t > dur:
        return
    r = rng(seed)
    p = eout(t / dur)
    for i in range(n):
        ang = i / n * TAU + r.uniform(-0.2, 0.2)
        d = dist * p * r.uniform(0.6, 1.1)
        px, py = x + math.cos(ang) * d, y + math.sin(ang) * d
        al = a * (1 - t / dur)
        if shape == "line":
            d2 = d - 30 * (1 - p)
            line(cr, x + math.cos(ang) * d2 * 0.7, y + math.sin(ang) * d2 * 0.7, px, py, size * 0.6, c, al)
        else:
            circle(cr, px, py, size * (1 - 0.5 * p), fill=c, a=al)


def speed_lines(cr, t, n=26, c=INK, a=0.25, seed=3, horizontal=True):
    r = rng(seed)
    for i in range(n):
        y = r.uniform(0, H)
        ln = r.uniform(200, 600)
        x = (r.uniform(0, W + ln) - t * r.uniform(1800, 3200)) % (W + ln) - ln
        if horizontal:
            line(cr, x, y, x + ln, y, r.uniform(2, 5), c, a)
        else:
            line(cr, y * W / H, x, y * W / H, x + ln, r.uniform(2, 5), c, a)


def radial_lines(cr, x, y, t, n=36, r0=300, r1=1400, c=INK, a=0.12, w=10, spin=0.05):
    for i in range(n):
        ang = i / n * TAU + t * spin
        line(cr, x + math.cos(ang) * r0, y + math.sin(ang) * r0,
             x + math.cos(ang) * r1, y + math.sin(ang) * r1, w, c, a)


def floating_symbols(cr, t, symbols, cx, cy, rx, ry, size=40, c=INK, a=1.0, seed=5, face=FONT_SERIF, speed=0.25, italic=True):
    """Symbols orbiting an ellipse around (cx, cy) - used for 'thinking' effects."""
    r = rng(seed)
    n = len(symbols)
    for i, s in enumerate(symbols):
        ph = i / n * TAU + r.uniform(-0.3, 0.3)
        sp = speed * r.uniform(0.7, 1.3) * (1 if i % 2 else -1)
        ang = ph + t * sp
        rr = r.uniform(0.75, 1.15)
        x = cx + math.cos(ang) * rx * rr
        y = cy + math.sin(ang) * ry * rr + math.sin(t * 1.3 + i) * 10
        depth = 0.6 + 0.4 * math.sin(ang)
        text(cr, s, x, y, size * (0.75 + 0.35 * depth), c=c, a=a * (0.35 + 0.65 * depth),
             face=face, italic=italic)
