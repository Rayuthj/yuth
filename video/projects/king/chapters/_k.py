"""Shared bits for the King video."""
import math

from video.chapters.common import Builder, head_at  # noqa: F401
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm, props as P, props2 as P2, sets as S, kit as K  # noqa: F401

KING = ("tuft", "crown", "cape")
ADV = ("glasses", "mustache", "bowtie")
GUARD = ("bearskin",)
GOLD = P2.GOLD
CROWN_SYMBOLS = ["LAWS", "GOLD", "ARMY", "TAXES", "PALACE", "POWER", "MAPS", "VOTES", "COURTS", "TRADE", "ROADS",
                 "SCHOOLS"]
TITLE = K.title_card("WHAT IF YOU BECAME", "KING?", symbols=CROWN_SYMBOLS, big_size=300)


def crowd(cr, T, n=24, y0=900, y1=1060, seed=3, cheer=0.0, ink=GRAY, s0=0.5, s1=0.75, x0=-100, x1=2020, signs=None,
          heads_only=False, fill=None):
    """A crowd of stickmen; cheer 0..1 raises arms and makes them bounce."""
    r = rng(seed)
    people = []
    for i in range(n):
        people.append((r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(s0, s1), r.choice([(), ("cap",), ("ponytail",),
                       ("glasses",), ("bun",), ("hat",)]), r.uniform(0, 6)))
    people.sort(key=lambda p: p[1])
    for i, (x, y, s, acc, ph) in enumerate(people):
        g = "cheer" if cheer > 0.5 and (i % 3 != 1 or cheer > 0.8) else "stand"
        p = sm.pose(g, x=x, s=s, face=1 if x < CX else -1, smile=0.4 + 0.5 * cheer)
        if g == "cheer":
            p = sm.apply(p, a1f=150 + 15 * math.sin(T * 8 + ph), a1b=-150 + 15 * math.sin(T * 8 + ph + 1))
        p = sm.idle(p, T, int(ph * 10))
        p = sm.on_ground(p, y)
        if cheer > 0.5:
            p["y"] -= abs(math.sin(T * 6 + ph)) * 18 * s
        if fill is None:
            sm.draw(cr, p, ink=ink, acc=acc)
        else:
            sm.draw(cr, p, ink=ink, fill=fill, acc=acc)
        if signs and i % 5 == 2:
            J = sm.joints(p)
            P2.sign(cr, J["hand_f"][0], J["hand_f"][1] - 20, 0.55 * s / 0.6, signs[i % len(signs)], rot=0.08 * math.sin(T * 3 + ph))


def balcony(cr, T, gy=600, crowd_cheer=0.0, signs=None):
    """Palace balcony over a cheering square."""
    S.city(cr, T, 0, gy=820)
    crowd(cr, T, n=40, y0=860, y1=1080, cheer=crowd_cheer, signs=signs)
    rect(cr, 1150, gy, 900, 700, fill=(0.88, 0.82, 0.70), stroke=INK, lw=6)
    for i in range(10):
        line(cr, 1180 + i * 80, gy - 110, 1180 + i * 80, gy, 8, INK)
    line(cr, 1150, gy - 110, 2050, gy - 110, 10, INK)
    polyline(cr, [(1260, gy + 40), (1340, gy + 40), (1340, gy + 260), (1300, gy + 220), (1260, gy + 260)], 5, INK,
             closed=True, fill=(0.65, 0.08, 0.12))
