"""Reusable backgrounds ("sets"). Draw them inside the camera transform so that
characters and floors move together. Floors extend past the frame edges so
camera zooms never reveal gaps."""
import math

from .core import (W, H, CX, CY, INK, WHITE, PAPER, PAPER2, LIGHT, MID, GRAY, DARK, DARK2, RED, BLUE, YELLOW, GREEN,
                   ORANGE, PURPLE, CYAN, TAU, fill_bg, vgrad as _vgrad, rect, rrect, line, circle, ellipse, polyline, glow, stars,
                   text, lerp, rng, bezier_pts, xform, FONT_HAND, FONT_TITLE)
from . import props as P

X0, X1 = -400, W + 400          # floor extents



def vgrad(cr, top, bottom):
    """Sky/wall gradient padded past the frame so zoomed-out cameras never show black."""
    _vgrad(cr, top, bottom, pad=500)

def floor(cr, y, c, ink=INK, lw=5):
    rect(cr, X0, y, X1 - X0, H - y + 500, fill=c)
    line(cr, X0, y, X1, y, lw, ink)


def room(cr, T, wall=(0.94, 0.92, 0.88), floor_c=(0.82, 0.76, 0.68), fy=880, window=None, frame=True):
    fill_bg(cr, wall)
    if window:
        P.window(cr, window[0], window[1], 380, 300, T, sky=(0.75, 0.86, 0.98))
    floor(cr, fy, floor_c)


def city(cr, T, cam_x=0.0, sky=((0.80, 0.88, 0.97), (0.96, 0.96, 0.97)), gy=760, night=False):
    vgrad(cr, *sky)
    if night:
        stars(cr, T, n=120, alpha=0.7, area=(0, 0, W, 500))
    with xform(cr, -cam_x * 0.3, 0):
        P.skyline(cr, X0 - 800, gy - 40, 3600, 420, seed=51, fill=(0.80, 0.82, 0.86) if not night else (0.14, 0.15, 0.22),
                  win=night, lit=night, t=T)
    with xform(cr, -cam_x * 0.6, 0):
        P.skyline(cr, X0 - 800, gy, 3600, 360, seed=52, fill=(0.62, 0.65, 0.72) if not night else (0.09, 0.10, 0.15),
                  win=True, lit=night, t=T)
    floor(cr, gy, (0.86, 0.85, 0.82) if not night else (0.12, 0.12, 0.16), MID if not night else (0.3, 0.3, 0.35), 3)
    for i in range(-3, 14):
        x = (i * 240 - cam_x) % (W + 720) - 480
        line(cr, x, gy, x - 120, H + 200, 3, MID, 0.4)


def park(cr, T, gy=860):
    vgrad(cr, (0.75, 0.88, 0.98), (0.92, 0.97, 0.92))
    P.cloud(cr, 400, 170, 1.0)
    P.cloud(cr, 1500, 130, 0.8)
    floor(cr, gy, (0.62, 0.80, 0.50))
    P.tree(cr, 220, gy, 1.3, T)
    P.tree(cr, 1750, gy, 1.1, T + 1)


def field(cr, T, gy=880, sky=((0.62, 0.82, 0.98), (0.92, 0.96, 0.98)), grass=(0.62, 0.80, 0.50)):
    vgrad(cr, *sky)
    P.cloud(cr, 500, 200, 0.9)
    P.cloud(cr, 1400, 160, 0.7)
    floor(cr, gy, grass)


def dark_room(cr, T, lamp_x=960, lamp_y=300, wall=(0.10, 0.11, 0.15), wall2=(0.06, 0.065, 0.09), fy=880,
              lamp=True, flicker=0.0):
    vgrad(cr, wall, wall2)
    f = 1.0 - flicker * (0.5 + 0.5 * math.sin(T * 47) * math.sin(T * 13))
    glow(cr, lamp_x, lamp_y + 120, 650, (1.0, 0.86, 0.55), 0.28 * f)
    rect(cr, X0, fy, X1 - X0, 700, fill=(0.07, 0.07, 0.10))
    line(cr, X0, fy, X1, fy, 4, (0.25, 0.26, 0.32))
    if lamp:
        line(cr, lamp_x, -10, lamp_x, lamp_y - 40, 3, (0.3, 0.3, 0.35))
        polyline(cr, [(lamp_x - 60, lamp_y), (lamp_x - 25, lamp_y - 45), (lamp_x + 25, lamp_y - 45), (lamp_x + 60, lamp_y)],
                 4, (0.86, 0.87, 0.90), closed=True, fill=(0.2, 0.2, 0.25))
        ellipse(cr, lamp_x, lamp_y + 4, 40, 10, fill=(1.0, 0.86, 0.55), a=f)
    return f


def night_sky(cr, T, gy=930, star_a=1.0, hill=True, top=(0.03, 0.035, 0.08), bottom=(0.08, 0.07, 0.16)):
    vgrad(cr, top, bottom)
    stars(cr, T, n=360, alpha=star_a, seed=11)
    if hill:
        rect(cr, X0, gy, X1 - X0, 700, fill=(0.02, 0.02, 0.04))
        P.hill(cr, CX, gy + 15, 1600, 70, c=(0.02, 0.02, 0.04))


def palace(cr, T, fy=880, warm=1.0):
    """Throne room: columns, banners, red carpet."""
    vgrad(cr, (0.55, 0.30, 0.22), (0.30, 0.14, 0.12))
    for x in (160, 520, 1400, 1760):
        rect(cr, x - 50, 80, 100, fy - 80, fill=(0.85, 0.78, 0.62), stroke=INK, lw=5)
        rect(cr, x - 70, 60, 140, 40, fill=(0.85, 0.78, 0.62), stroke=INK, lw=5)
        rect(cr, x - 70, fy - 40, 140, 40, fill=(0.85, 0.78, 0.62), stroke=INK, lw=5)
    for x in (340, 1580):
        polyline(cr, [(x - 70, 120), (x + 70, 120), (x + 70, 520), (x, 470), (x - 70, 520)], 5, INK, closed=True,
                 fill=(0.65, 0.08, 0.12))
        P.crown(cr, x, 280, 0.6)
    floor(cr, fy, (0.55, 0.42, 0.30))
    polyline(cr, [(840, fy), (1080, fy), (1300, H + 300), (620, H + 300)], 0, INK, closed=True, fill=(0.75, 0.10, 0.14))
    glow(cr, CX, 300, 600, YELLOW, 0.12 * warm)


def castle(cr, x, gy, s=1.0, c=(0.82, 0.80, 0.76), flag_c=RED, t=0.0):
    with xform(cr, x, gy, s):
        rect(cr, -260, -300, 520, 300, fill=c, stroke=INK, lw=6)
        for tx in (-300, 230):
            rect(cr, tx, -460, 70, 460, fill=c, stroke=INK, lw=6)
            polyline(cr, [(tx - 15, -460), (tx + 35, -560), (tx + 85, -460)], 6, INK, closed=True, fill=(0.35, 0.40, 0.65))
        for i in range(9):
            rect(cr, -250 + i * 58, -340, 34, 40, fill=c, stroke=INK, lw=5)
        rect(cr, -60, -200, 120, 200, fill=(0.45, 0.30, 0.2), stroke=INK, lw=6)
        circle(cr, 0, -200, 60, fill=(0.45, 0.30, 0.2), stroke=INK, w=6)
        rect(cr, -58, -200, 116, 10, fill=(0.45, 0.30, 0.2))
        for tx in (-265, 265):
            line(cr, tx, -560, tx, -650, 5, INK)
            wv = [(tx + i * 12, -650 + 8 * math.sin(t * 4 + i * 0.9)) for i in range(8)]
            polyline(cr, wv + [(tx + 84, -610 + 8 * math.sin(t * 4 + 6.3)), (tx, -610)], 4, INK, closed=True, fill=flag_c)


def village(cr, T, gy=880, warm=True):
    vgrad(cr, (1.0, 0.86, 0.60) if warm else (0.75, 0.86, 0.98), (0.85, 0.93, 0.98))
    P.sun(cr, 1600, 220, 80, T)
    floor(cr, gy, (0.62, 0.80, 0.50))
    for i, x in enumerate((180, 420, 1500, 1740)):
        P.house(cr, x, gy, 0.9, lit=0.3, roof=[RED, BLUE, ORANGE, GREEN][i])


def space(cr, T, drift=4):
    vgrad(cr, (0.02, 0.02, 0.06), (0.06, 0.05, 0.14))
    stars(cr, T, n=320, drift=drift)


def blueprint(cr, bg=(0.93, 0.96, 1.0), grid=(0.55, 0.70, 0.92), step=40, a=0.25):
    fill_bg(cr, bg)
    from .core import src
    src(cr, grid, a)
    cr.set_line_width(1.5)
    for x in range(0, W, step):
        cr.move_to(x, 0)
        cr.line_to(x, H)
    for y in range(0, H, step):
        cr.move_to(0, y)
        cr.line_to(W, y)
    cr.stroke()


def office(cr, T, fy=880):
    room(cr, T, wall=(0.90, 0.92, 0.94), floor_c=(0.70, 0.72, 0.76), fy=fy)
    for x in (300, 700, 1100, 1500):
        rect(cr, x - 120, 140, 240, 300, fill=(0.75, 0.86, 0.98), stroke=INK, lw=5)
        line(cr, x, 140, x, 440, 4, INK)
