"""Helpers shared by the chapter modules."""
import math
from contextlib import contextmanager

from video.engine.core import *  # noqa: F401,F403
from video.engine.core import (W, H, CX, CY, PAPER, PAPER2, DARK, DARK2, INK, WHITE, YELLOW, RED, BLUE, LIGHT, MID,
                               FONT_TITLE, FONT_BOLD, FONT_HAND, FONT_SERIF, TAU, camera, clamp, lerp, ease, eout,
                               prog, vgrad, vignette, stars, glow, text, fill_bg, radial_lines, floating_symbols,
                               burst, shake, group, xform, line, rect, back)
from video.engine.scene import Shot
from video.engine import stickman as sm

MATH_SYMBOLS = ["π", "∑", "√2", "n!", "x²", "∞", "Δ", "∫", "φ", "1,1,2,3,5,8", "E=mc²", "f(x)", "λ", "θ",
                "ℏ", "≈", "∂y/∂x", "a²+b²=c²", "log n", "σ"]


class Builder:
    """Collects shots and sound cues for a chapter."""

    def __init__(self, tl):
        self.tl = tl
        self.shots = []
        self.sfx = []

    def shot(self, start, trans="cut", tdur=0.5):
        def deco(fn):
            st = start

            def draw(cr, t, d, fn=fn, st=st):
                fn(cr, t, d, st + t)
            self.shots.append(Shot(st, draw, trans, tdur, fn.__name__))
            return fn
        return deco

    def fx(self, T, name, gain=0.0, **kw):
        self.sfx.append((round(T, 3), name, gain, kw))

    def result(self):
        return self.shots, self.sfx


def paper(cr, c=PAPER, vig=0.18):
    fill_bg(cr, c)
    if vig:
        vignette(cr, vig)


def dark(cr, t=0.0, star_a=0.0, c1=DARK2, c2=DARK, vig=0.5):
    vgrad(cr, c1, c2)
    if star_a > 0:
        stars(cr, t, n=220, alpha=star_a)
    if vig:
        vignette(cr, vig)


def ground(cr, y, c=INK, w=5, x0=0, x1=W, a=1.0):
    line(cr, x0, y, x1, y, w, c, a)


@contextmanager
def ken(cr, t, d, z0=1.0, z1=1.06, fx=CX, fy=CY, fx1=None, fy1=None, sx=0.0, sy=0.0):
    """Slow 'Ken Burns' camera move over a shot of duration d."""
    k = ease(t / d) if d > 0 else 0
    z = lerp(z0, z1, k)
    fxx = lerp(fx, fx1 if fx1 is not None else fx, k)
    fyy = lerp(fy, fy1 if fy1 is not None else fy, k)
    with camera(cr, z, fxx + sx, fyy + sy):
        yield


def head_at(p, hx, hy):
    """Return pose positioned so its head centre lands on (hx, hy)."""
    q = dict(p)
    J = sm.joints(q)
    q["x"] += hx - J["head"][0]
    q["y"] += hy - J["head"][1]
    return q


def title_card(cr, t, a=1.0, zoom=1.0):
    """'WHAT IF YOU HAD 500 IQ?' animated title. t = seconds since the reveal started."""
    dark(cr, t, star_a=0.6, c1=(0.07, 0.07, 0.12), c2=(0.02, 0.02, 0.04))
    sx, sy = shake(t, 14 * max(0.0, 1 - (t - 0.55) * 3) if t > 0.55 else 0, seed=3)
    with camera(cr, zoom * (1 + 0.03 * t), CX - sx, CY - sy):
        radial_lines(cr, CX, CY + 40, t, n=40, r0=260, c=YELLOW, a=0.07 * clamp(t * 2), w=14, spin=0.04)
        floating_symbols(cr, t, MATH_SYMBOLS, CX, CY + 20, 820, 380, size=46, c=WHITE, a=0.22 * clamp(t * 2),
                         seed=8, speed=0.18)
        glow(cr, CX, CY + 80, 520, YELLOW, 0.22 * clamp((t - 0.5) * 2))
        words = ["WHAT", "IF", "YOU", "HAD"]
        from video.engine.core import text_w
        ws = [text_w(cr, wd, FONT_TITLE, 96) for wd in words]
        gap = 34
        x = CX - (sum(ws) + gap * (len(ws) - 1)) / 2
        for i, wd in enumerate(words):
            k = prog(t, i * 0.09, 0.22)
            if k > 0:
                sc = lerp(2.6, 1.0, eout(k))
                text(cr, wd, x + ws[i] / 2, CY - 120, 96, c=WHITE, a=a * clamp(k * 2), face=FONT_TITLE,
                     scale=sc)
            x += ws[i] + gap
        k = prog(t, 0.5, 0.35)
        if k > 0:
            sc = lerp(3.5, 1.0, back(k, 1.4))
            text(cr, "500 IQ?", CX, CY + 70, 250, c=YELLOW, a=a * clamp(k * 3), face=FONT_TITLE, scale=sc,
                 outline=(0.35, 0.22, 0.0), ow=10)
        burst(cr, CX, CY + 70, t - 0.62, n=26, dist=700, size=10, c=YELLOW, dur=1.1, seed=5)
        burst(cr, CX, CY + 70, t - 0.62, n=18, dist=520, size=12, c=WHITE, dur=0.9, seed=9, shape="line")
        k2 = prog(t, 1.1, 0.5)
        if k2 > 0:
            line(cr, CX - 360 * eout(k2), CY + 215, CX + 360 * eout(k2), CY + 215, 6, WHITE, 0.6 * a)
    if a < 1:
        pass
