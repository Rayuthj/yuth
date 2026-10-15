"""Thumbnails for "What If You Became King of a Country?"."""
import math

from video.thumbkit import rays, radial, big_text
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P
from video.engine import props2 as P2
from video.chapters.common import head_at

GOLD = P2.GOLD
GOLD_EDGE = (0.35, 0.20, 0.0)


def crowned_face(cr, cx, cy, s, smile=0.8, brow=0.5, ink=INK, fill=WHITE, crown_s=None):
    p = sm.pose("front", s=s, lw=3.4, fo=0.3, face=1, eye=1.35, gx=0.3, gy=-0.1, smile=smile, mo=0.0, brow=brow,
                browy=0.15)
    p = head_at(p, cx, cy)
    J = sm.draw(cr, p, ink=ink, fill=fill, acc=("tuft",))
    P.crown(cr, cx, cy - 40 * s - 20, crown_s or s * 0.62)
    return J


# A: the crown
def concept_a(cr):
    radial(cr, 620, 560, (0.45, 0.20, 0.45), (0.18, 0.06, 0.22), (0.03, 0.01, 0.05))
    rays(cr, 620, 520, 26, GOLD, 0.10)
    glow(cr, 620, 330, 620, YELLOW, 0.35)
    for i in range(14):
        g = rng(i + 3)
        P2.coin(cr, 620 + g.uniform(-560, 560), 560 + g.uniform(-460, 460), g.uniform(26, 50), rot=g.uniform(-1, 1))
    crowned_face(cr, 620, 640, 6.4)
    big_text(cr, "YOU", 1460, 300, 230, WHITE, INK, ow=26, rot=-0.04)
    big_text(cr, "ARE", 1460, 520, 170, WHITE, INK, ow=22, rot=-0.04)
    big_text(cr, "KING", 1450, 780, 300, GOLD, GOLD_EDGE, ow=30, rot=-0.04)
    pts = bezier_pts([(1180, 1010), (1010, 1030), (930, 900)], 20)
    polyline(cr, pts, 30, RED)
    polyline(cr, [(890, 820), (985, 900), (885, 930)], 0, RED, closed=True, fill=RED)
    vignette(cr, 0.4)


# B: hero or tyrant?
def concept_b(cr):
    fill_bg(cr, (1.0, 0.86, 0.35))
    rays(cr, 480, 600, 22, WHITE, 0.35, spin=0.1)
    cr.save()
    cr.move_to(1040, 0)
    cr.line_to(W, 0)
    cr.line_to(W, H)
    cr.line_to(880, H)
    cr.close_path()
    cr.clip()
    vgrad(cr, (0.40, 0.03, 0.06), (0.10, 0.01, 0.02))
    for i in range(10):
        g = rng(i + 30)
        polyline(cr, [(1100 + g.uniform(0, 800), 0), (1100 + g.uniform(0, 800), H)], 3, RED, 0.25)
    cr.restore()
    polyline(cr, [(1040, 0), (1000, 300), (1060, 520), (960, 760), (880, H)], 26, INK)
    p = sm.pose("cheer", s=2.05, lw=4.6, smile=1.0, mo=0.5, eye=1.25)
    p = sm.on_ground(p, 1200)
    p["x"] = 480
    J = sm.draw(cr, p, acc=("tuft", "cape"))
    P.crown(cr, J["head"][0], J["head"][1] - 110, 1.3)
    q = sm.pose("hips", s=2.05, lw=4.6, face=-1, eye=0.9, smile=0.9, brow=1.0, fo=0.0)
    q = sm.on_ground(q, 1200)
    q["x"] = 1460
    J = sm.draw(cr, q, ink=(1.0, 0.85, 0.85), fill=(0.25, 0.03, 0.05), acc=("tuft", "cape"))
    P.crown(cr, J["head"][0], J["head"][1] - 110, 1.3)
    big_text(cr, "HERO", 480, 170, 190, WHITE, INK, ow=24, rot=-0.03)
    big_text(cr, "OR TYRANT?", 1460, 170, 150, RED, INK, ow=22, rot=-0.03)
    big_text(cr, "YOU DECIDE", CX, 990, 110, YELLOW, INK, ow=18)


# C: the throne
def concept_c(cr):
    radial(cr, CX, 620, (0.75, 0.30, 0.20), (0.40, 0.12, 0.10), (0.10, 0.02, 0.03))
    rays(cr, CX, 560, 24, GOLD, 0.12, spin=0.05)
    rect(cr, -10, 900, W + 20, 200, fill=(0.35, 0.18, 0.12))
    polyline(cr, [(820, 900), (1100, 900), (1400, H + 10), (520, H + 10)], 0, INK, closed=True, fill=(0.75, 0.10, 0.14))
    for x in (380, 1540):
        P2.coin_pile(cr, x, 920, 1.6, rows=7, seed=int(x))
    P.throne(cr, CX, 930, 2.0)
    p = sm.pose("sit", s=1.6, lw=4.4, x=CX, fo=0.0, a1f=60, a2f=40, a1b=-60, a2b=-40, smile=0.9, brow=0.6, eye=1.2)
    p["y"] = 930 - 210
    J = sm.draw(cr, p, acc=("tuft", "cape"))
    P.crown(cr, J["head"][0], J["head"][1] - 85, 1.0)
    big_text(cr, "UNLIMITED", CX, 150, 170, WHITE, INK, ow=24, rot=-0.02)
    big_text(cr, "POWER?", CX, 330, 190, GOLD, GOLD_EDGE, ow=26, rot=-0.02)
    vignette(cr, 0.35)


CONCEPTS = [("a_you_are_king", concept_a), ("b_hero_or_tyrant", concept_b), ("c_unlimited_power", concept_c)]
