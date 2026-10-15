"""Shared bits for "What If You Never Needed to Sleep?"."""
import math

import cairo

from video.chapters.common import Builder, head_at  # noqa: F401
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm, props as P, props2 as P2, sets as S, kit as K  # noqa: F401

# ---------------------------------------------------------------- cast & palette
HERO = ("tuft",)
MOM = ("hair",)
DAD = ("glasses", "mustache")
SIS = ("bun",)
MIA = ("ponytail",)
SAM = ("cap",)
BAKER = ("chef", "mustache")
NURSE = ("badge", "bun")
SCI = ("labcoat", "glasses")

NI = (0.88, 0.89, 0.95)          # stickman ink at night
NF = (0.11, 0.12, 0.18)          # head fill at night
MOON = (1.0, 0.94, 0.72)
NIGHT_SKY = ((0.04, 0.05, 0.12), (0.12, 0.12, 0.26))
SLEEP_BLUE = (0.20, 0.26, 0.55)
BONUS = (0.35, 0.92, 0.70)
WOOD = (0.62, 0.44, 0.30)
BLANKET = (0.36, 0.48, 0.80)
DREAM = ((0.30, 0.18, 0.48), (0.62, 0.42, 0.72))
GOLD = P2.GOLD

SLEEP_SYMBOLS = ["ZZZ", "8 HOURS", "3 AM", "DREAMS", "REM", "ALARM", "NIGHT SHIFT", "BED", "STARS", "2,920 HOURS",
                 "MOON", "YAWN"]
TITLE = K.title_card("WHAT IF YOU NEVER NEEDED TO", "SLEEP?", color=(1.0, 0.84, 0.30), symbols=SLEEP_SYMBOLS,
                     big_size=300)
# chapter 1's title card starts at e("c1_07") - 0.2 = 37.2 s, so it has run 2.8 s when chapter 2 begins
TITLE_T_END = 2.8


def nhero(cr, T, x, ground_y, g="stand", **kw):
    """The hero drawn in pale ink for dark scenes."""
    kw.setdefault("ink", NI)
    kw.setdefault("fill", NF)
    return K.hero(cr, T, x, ground_y, g, **kw)


def nperson(cr, T, x, ground_y, g="stand", **kw):
    kw.setdefault("ink", NI)
    kw.setdefault("fill", NF)
    return K.person(cr, T, x, ground_y, g, **kw)


def night_bg(cr, T, star_a=0.8, top=NIGHT_SKY[0], bottom=NIGHT_SKY[1]):
    S.vgrad(cr, top, bottom)
    if star_a > 0:
        stars(cr, T, n=200, alpha=star_a, seed=21, area=(-200, -200, W + 200, 700))


def sky_dawn(cr, k, T=0.0):
    """Night (k=0) to sunrise (k=1) sky gradient."""
    top = lerpc((0.05, 0.06, 0.15), (0.40, 0.55, 0.85), k)
    bot = lerpc((0.13, 0.13, 0.28), (1.00, 0.72, 0.45), k)
    S.vgrad(cr, top, bot)
    if k < 1:
        stars(cr, T, n=160, alpha=0.8 * (1 - k), seed=21, area=(-200, -200, W + 200, 650))


# ---------------------------------------------------------------- small helpers
def moon(cr, x, y, r, c=MOON, a=1.0, glow_a=0.35, off=0.45):
    """Crescent moon that works on any background."""
    if glow_a > 0:
        glow(cr, x, y, r * 3.2, c, glow_a * a)
    cr.push_group()
    circle(cr, x, y, r, fill=c)
    cr.set_operator(cairo.OPERATOR_CLEAR)
    circle(cr, x + r * off * 1.25, y - r * off * 0.7, r * 0.9, fill=BLACK)
    cr.set_operator(cairo.OPERATOR_OVER)
    cr.pop_group_to_source()
    cr.paint_with_alpha(a)


def zzz(cr, x, y, T, s=1.0, c=INK, a=1.0, seed=0, n=3):
    """Floating Z's rising from (x, y)."""
    for i in range(n):
        ph = (T * 0.55 + i / n + seed * 0.137) % 1.0
        al = a * math.sin(ph * math.pi)
        if al <= 0.02:
            continue
        text(cr, "Z", x + ph * 70 * s + 8 * math.sin(T * 2 + i) * s, y - ph * 120 * s, (22 + ph * 30) * s, c=c, a=al,
             face=FONT_TITLE, rot=-0.15)


def digital_clock(cr, x, y, txt, s=1.0, c=(1.0, 0.28, 0.22), body=INK, a=1.0):
    with group(cr, a):
        with xform(cr, x, y, s):
            rrect(cr, -150, -62, 300, 124, 22, fill=body, stroke=(0.35, 0.35, 0.4), lw=5)
            rrect(cr, -128, -44, 256, 88, 10, fill=(0.05, 0.03, 0.03))
            glow(cr, 0, 0, 120, c, 0.25)
            text(cr, txt, 0, 2, 62 if len(txt) <= 5 else 50, c=c, face=FONT_BOLD)


def label_dark(cr, s, x, y, size=40, c=WHITE, bg=(0.10, 0.10, 0.16), scale=1.0, a=1.0):
    return label_box(cr, s, x, y, size, c=c, bg=bg, face=FONT_BOLD, bold=False, scale=scale, a=a)


def chip(cr, s, x, y, size=40, c=INK, bg=YELLOW, scale=1.0, a=1.0):
    """Bold title-font chip (for pop-in key words)."""
    return label_box(cr, s, x, y, size, c=c, bg=bg, face=FONT_TITLE, bold=False, scale=max(0.01, scale), a=a)


def version_tag(cr, n, name, col, a=1.0):
    rrect(cr, CX - 120, 60, 240, 64, 14, fill=col, stroke=INK, lw=4, a=a)
    text(cr, f"VERSION {n}", CX, 92, 36, face=FONT_TITLE, c=WHITE, a=a)
    text(cr, name, CX, 180, 70, face=FONT_TITLE, c=WHITE, a=a, outline=INK, ow=9)


def cross_out(cr, x, y, r, k, w=16, c=RED):
    if k <= 0:
        return
    partial_line(cr, x - r, y - r, x + r, y + r, clamp(k * 2), w, c)
    partial_line(cr, x + r, y - r, x - r, y + r, clamp(k * 2 - 1), w, c)


def big_word(cr, s, x, y, size, c=WHITE, edge=INK, ow=10, a=1.0, scale=1.0, rot=0.0):
    text(cr, s, x, y, size, c=c, face=FONT_TITLE, outline=edge, ow=ow, a=a, scale=max(0.01, scale), rot=rot)


# ---------------------------------------------------------------- furniture & rooms
def bed2(cr, T, x, gy, s=1.0, who=None, acc=HERO, ink=INK, fill=WHITE, blanket=BLANKET, frame=WOOD, sheet=WHITE,
         z=True, z_c=None, seed=0, two=None, kw=None, messy=0.0):
    """Bed with its base on the floor at (x, gy), headboard on the left.
    who: None (made bed), "sleep" (lying, eyes shut), "sit" (sitting up awake), "empty" (thrown-back blanket)."""
    kw = kw or {}
    with xform(cr, x, gy, s):
        rrect(cr, -272, -215, 36, 215, 10, fill=frame, stroke=ink, lw=5)
        rrect(cr, 236, -135, 28, 135, 8, fill=frame, stroke=ink, lw=5)
        rect(cr, -240, -72, 480, 42, fill=frame, stroke=ink, lw=5)
        line(cr, -225, -30, -225, 0, 8, ink)
        line(cr, 225, -30, 225, 0, 8, ink)
        rrect(cr, -240, -106, 480, 40, 10, fill=sheet, stroke=ink, lw=5)
        rrect(cr, -230, -142, 112, 44, 18, fill=sheet, stroke=ink, lw=5)
        breath = 3 * math.sin(T * 1.6 + seed)
        if who == "sleep":
            heads = [(-168, -146)] + ([(-112, -142)] if two else [])
            accs = [acc] + ([two] if two else [])
            for i, ((hx, hy), a_) in enumerate(zip(heads, accs)):
                p = sm.pose("front", s=0.85, head=-14 + i * 8, smile=0.35, blink=1.0)
                p = head_at(p, hx, hy)
                cr.save()
                cr.arc(hx, hy, 37, 0, TAU)
                cr.new_sub_path()
                cr.rectangle(hx - 70, hy - 110, 140, 90)
                cr.clip()
                sm.draw(cr, p, ink=ink, fill=fill, acc=a_)
                cr.restore()
                cr.new_path()
            bx0 = -126 if not two else -78
            polyline(cr, bezier_pts([(bx0, -112 + breath), (bx0 + 40, -150 + breath), (150, -140 + breath * 0.5),
                                     (236, -120)], 20) + [(236, -66), (bx0, -66)], 5, ink, closed=True, fill=blanket)
            for i in range(3):
                line(cr, -40 + i * 90, -130 + breath, -20 + i * 90, -72, 3, ink, 0.25)
        elif who == "sit":
            kw2 = dict(a1f=48, a2f=52, a1b=40, a2b=60, smile=0.6)
            kw2.update(kw)
            p = sm.pose("stand", x=-150, s=0.85, l1f=88, l2f=0, l1b=84, l2b=0, **kw2)
            p = sm.idle(p, T, seed, 0.6)
            p["y"] = -104
            sm.draw(cr, p, ink=ink, fill=fill, acc=acc)
            rrect(cr, -120, -128 + breath * 0.5, 356, 64, 22, fill=blanket, stroke=ink, lw=5)
        elif who == "empty":
            polyline(cr, [(40, -128), (236, -128), (236, -64), (60, -64)], 5, ink, closed=True, fill=blanket)
            polyline(cr, bezier_pts([(40, -128), (-10, -150), (20, -90), (60, -64)], 12), 5, ink, closed=True,
                     fill=lerpc(blanket, WHITE, 0.25))
        else:
            rrect(cr, -110, -126, 346, 60, 20, fill=blanket, stroke=ink, lw=5)
            line(cr, -110, -104, 236, -104, 4, lerpc(blanket, WHITE, 0.5))
    if who == "sleep" and z:
        zzz(cr, x - 150 * s, gy - 200 * s, T, s * 1.1, c=z_c or ink, seed=seed)


def nightstand_lamp(cr, x, gy, s=1.0, on=1.0, ink=INK, c=(0.95, 0.85, 0.6)):
    with xform(cr, x, gy, s):
        rect(cr, -70, -120, 140, 120, fill=WOOD, stroke=ink, lw=5)
        line(cr, -70, -60, 70, -60, 4, ink)
        circle(cr, 0, -90, 6, fill=ink)
        line(cr, 0, -120, 0, -200, 6, ink)
        if on > 0:
            glow(cr, 0, -210, 260, (1.0, 0.85, 0.5), 0.45 * on)
        polyline(cr, [(-50, -195), (-30, -250), (30, -250), (50, -195)], 5, ink, closed=True,
                 fill=lerpc((0.45, 0.42, 0.40), c, on))


def window2(cr, x, y, w=360, h=300, T=0.0, k_day=0.0, moon_on=True, frame=WOOD, ink=INK, city=True, sun_on=False):
    """Window showing a night sky (k_day=0) up to a sunrise (k_day=1)."""
    cr.save()
    cr.rectangle(x - w / 2, y - h / 2, w, h)
    cr.clip()
    top = lerpc((0.04, 0.05, 0.13), (0.45, 0.62, 0.90), k_day)
    bot = lerpc((0.14, 0.14, 0.30), (1.0, 0.75, 0.50), k_day)
    vgrad(cr, top, bot, x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    if k_day < 1:
        stars(cr, T, n=30, seed=3, alpha=1 - k_day, area=(x - w / 2, y - h / 2, x + w / 2, y + h * 0.2))
    if moon_on and k_day < 0.8:
        moon(cr, x + w * 0.22, y - h * 0.22, h * 0.11, a=1 - k_day / 0.8, glow_a=0.3)
    if sun_on:
        P.sun(cr, x - w * 0.15, y + h * 0.25 - 60 * k_day, h * 0.1, T, rays=False)
    if city:
        P.skyline(cr, x - w / 2, y + h / 2, w, h * 0.45, seed=4, fill=lerpc((0.10, 0.11, 0.17), (0.45, 0.42, 0.50), k_day),
                  lit=k_day < 0.5, t=T)
    cr.restore()
    cr.new_path()
    rect(cr, x - w / 2, y - h / 2, w, h, stroke=frame, lw=14)
    line(cr, x, y - h / 2, x, y + h / 2, 8, frame)
    line(cr, x - w / 2, y, x + w / 2, y, 8, frame)
    rect(cr, x - w / 2 - 18, y + h / 2, w + 36, 16, fill=frame, stroke=ink, lw=4)


def night_room(cr, T, lamp=0.0, fy=880, wall=((0.17, 0.18, 0.28), (0.10, 0.11, 0.17)), floor_c=(0.13, 0.12, 0.16),
               win=(1450, 380), k_day=0.0):
    """A bedroom at night (dark walls, a window); lamp 0..1 warms it up."""
    S.vgrad(cr, lerpc(wall[0], (0.42, 0.34, 0.30), lamp * 0.5), lerpc(wall[1], (0.25, 0.20, 0.18), lamp * 0.5))
    if win:
        window2(cr, win[0], win[1], 380, 320, T, k_day=k_day)
    S.floor(cr, fy, floor_c, (0.30, 0.30, 0.36), 4)


def couch(cr, x, gy, s=1.0, c=(0.55, 0.30, 0.32), ink=INK):
    """Base at floor; seat top at gy - 150*s."""
    with xform(cr, x, gy, s):
        rrect(cr, -260, -260, 520, 150, 30, fill=lerpc(c, BLACK, 0.12), stroke=ink, lw=5)
        rrect(cr, -290, -170, 580, 120, 26, fill=c, stroke=ink, lw=5)
        for k in (-1, 1):
            rrect(cr, k * 270 - 40, -210, 80, 160, 30, fill=lerpc(c, BLACK, 0.06), stroke=ink, lw=5)
        line(cr, 0, -165, 0, -60, 3, ink, 0.4)
        line(cr, -240, -50, -240, 0, 8, ink)
        line(cr, 240, -50, 240, 0, 8, ink)


def fridge(cr, x, gy, s=1.0, T=0.0, hum=0.0, open_=0.0, ink=INK, c=(0.92, 0.94, 0.96)):
    """Base at floor."""
    jx = math.sin(T * 90) * 2.5 * hum
    with xform(cr, x + jx, gy, s):
        if open_ > 0:
            rect(cr, -110, -440, 220, 430, fill=(1.0, 0.97, 0.80))
            glow(cr, 0, -250, 420, (1.0, 0.95, 0.75), 0.6 * open_)
        rrect(cr, -110, -440, 220, 430, 22, fill=c, stroke=ink, lw=6)
        line(cr, -110, -300, 110, -300, 5, ink)
        line(cr, 80, -400, 80, -330, 9, ink)
        line(cr, 80, -270, 80, -170, 9, ink)
        for (mx, my, mc) in ((-60, -380, RED), (-20, -360, BLUE), (-50, -220, YELLOW)):
            circle(cr, mx, my, 12, fill=mc, stroke=ink, w=3)
        rect(cr, -40, -250, 70, 90, fill=WHITE, stroke=ink, lw=3)
        line(cr, -90, -10, -90, 0, 8, ink)
        line(cr, 90, -10, 90, 0, 8, ink)
    if hum > 0:
        for i in range(3):
            ph = (T * 1.2 + i / 3) % 1
            arc(cr, x + 140 * s, gy - 300 * s, (40 + 90 * ph) * s, -0.6, 0.6, 5, (0.6, 0.85, 1.0), hum * (1 - ph))
            arc(cr, x - 140 * s, gy - 300 * s, (40 + 90 * ph) * s, math.pi - 0.6, math.pi + 0.6, 5, (0.6, 0.85, 1.0),
                hum * (1 - ph))


def tv(cr, x, gy, s=1.0, T=0.0, ch=0, ink=INK, glow_a=0.5):
    """Old TV on a stand, base at floor; ch: 0 static, 1 infomercial, 2 color bars, 3 fishing show, -1 off."""
    with xform(cr, x, gy, s):
        rect(cr, -200, -120, 400, 120, fill=WOOD, stroke=ink, lw=5)
        line(cr, -200, -60, 200, -60, 4, ink)
        rrect(cr, -210, -420, 420, 300, 24, fill=(0.25, 0.25, 0.28), stroke=ink, lw=6)
        sx, sy, sw, sh = -180, -395, 300, 250
        if ch >= 0 and glow_a > 0:
            glow(cr, sx + sw / 2, sy + sh / 2, 520, (0.6, 0.75, 1.0), glow_a * 0.5)
        cr.save()
        rrect_path(cr, sx, sy, sw, sh, 16)
        cr.clip()
        tv_screen(cr, sx, sy, sw, sh, T, ch)
        cr.restore()
        cr.new_path()
        rrect(cr, sx, sy, sw, sh, 16, stroke=ink, lw=5)
        for i in range(2):
            circle(cr, 160, -350 + i * 60, 14, fill=LIGHT, stroke=ink, w=4)
        line(cr, -60, -420, -120, -500, 4, ink)
        line(cr, 60, -420, 120, -500, 4, ink)


def tv_screen(cr, x, y, w, h, T, ch):
    if ch < 0:
        rect(cr, x, y, w, h, fill=(0.08, 0.09, 0.10))
        return
    if ch == 0:
        rect(cr, x, y, w, h, fill=(0.5, 0.5, 0.5))
        g = rng(int(T * 30))
        for i in range(160):
            v = g.random()
            rect(cr, x + g.uniform(0, w), y + g.uniform(0, h), g.uniform(6, 26), 4, fill=(v, v, v))
    elif ch == 1:
        rect(cr, x, y, w, h, fill=(1.0, 0.85, 0.30))
        p = sm.pose("point", x=x + 70, s=0.42, smile=1.0, mo=0.5 * (0.5 + 0.5 * math.sin(T * 18)), face=1)
        sm.draw(cr, sm.on_ground(p, y + h + 20), acc=("tie", "glasses"))
        with xform(cr, x + 190, y + 90, 1.0, 0.12 * math.sin(T * 6)):
            polyline(cr, [(-70, 0), (60, -12), (70, 0), (60, 12)], 4, INK, closed=True, fill=(0.85, 0.88, 0.92))
            rect(cr, -110, -12, 45, 24, fill=(0.2, 0.2, 0.2))
        text(cr, "CALL NOW!", x + w / 2 + 40, y + 34, 32, face=FONT_TITLE, c=RED)
        text(cr, "ONLY $19.99", x + 200, y + h - 40, 26, face=FONT_TITLE, c=INK)
    elif ch == 2:
        cols = [WHITE, YELLOW, CYAN, GREEN, PURPLE, RED, BLUE]
        for i, c in enumerate(cols):
            rect(cr, x + i * w / 7, y, w / 7 + 1, h * 0.72, fill=c)
        rect(cr, x, y + h * 0.72, w, h * 0.28, fill=(0.1, 0.1, 0.12))
        text(cr, "PLEASE STAND BY", x + w / 2, y + h * 0.86, 24, face=FONT_TITLE, c=WHITE)
    elif ch == 3:
        rect(cr, x, y, w, h * 0.45, fill=(0.6, 0.8, 0.95))
        rect(cr, x, y + h * 0.45, w, h * 0.55, fill=(0.2, 0.45, 0.65))
        p = sm.pose("hold", x=x + 70, s=0.35, smile=0.0, face=1)
        J = sm.draw(cr, sm.on_ground(p, y + h * 0.48), acc=("hat",))
        line(cr, J["hand_f"][0], J["hand_f"][1], x + 200, y + 30, 3, INK)
        line(cr, x + 200, y + 30, x + 200, y + h * 0.7, 1.5, INK)
        text(cr, "zzz", x + 120, y + 40, 26, face=FONT_HAND, bold=True, c=INK)
        text(cr, "FISHING LIVE: HOUR 6", x + w / 2, y + h - 22, 22, face=FONT_TITLE, c=WHITE)


def houseplant(cr, x, gy, s=1.0, T=0.0, health=1.0, sparkle=0.0, ink=INK, pot=(0.80, 0.45, 0.28), seed=0):
    """Potted plant, base at floor. health 0 (droopy, brown) .. 1 (lush)."""
    leaf = lerpc((0.55, 0.45, 0.25), (0.25, 0.72, 0.35), health)
    with xform(cr, x, gy, s):
        r = rng(seed + 5)
        n = 5 + int(4 * health)
        for i in range(n):
            a0 = -1.1 + 2.2 * i / max(1, n - 1)
            droop = (1 - health) * 1.2
            ln = 120 + r.uniform(-20, 40) * (0.5 + health)
            sway = 0.04 * math.sin(T * 1.5 + i)
            ang = a0 * (1 + droop * 0.6) + sway
            bx, by = math.sin(ang) * ln * 0.6, -110 - math.cos(ang) * ln * (1 - droop * 0.5)
            tipx = bx + math.sin(ang) * 40 * (1 + droop)
            tipy = by + droop * 60
            polyline(cr, bezier_pts([(0, -110), (bx * 0.5, by - 20), (bx, by)], 10), 4, ink)
            with xform(cr, (bx + tipx) / 2, (by + tipy) / 2, 1.0, ang + droop * 1.2):
                ellipse(cr, 0, 0, 20, 42, fill=leaf, stroke=ink, w=4)
                line(cr, 0, -30, 0, 30, 2, ink, 0.5)
        polyline(cr, [(-70, -120), (70, -120), (52, 0), (-52, 0)], 5, ink, closed=True, fill=pot)
        rect(cr, -78, -132, 156, 26, fill=lerpc(pot, BLACK, 0.1), stroke=ink, lw=5)
    if sparkle > 0:
        for i in range(5):
            a = T * 1.5 + i * 1.25
            star_shape(cr, x + math.cos(a) * 130 * s, gy - 220 * s + math.sin(a) * 90 * s, 14 * s, fill=YELLOW,
                       a=sparkle * (0.5 + 0.5 * math.sin(T * 6 + i)))


def todo_list(cr, x, y, items, k_items=1.0, k_checks=0.0, title="TO DO", w=420, size=38, ink=INK, rot=0.0,
              strike=True, paper=(1.0, 0.98, 0.82)):
    """Notepad; items appear with k_items (0..1) and get ticked with k_checks (0..1)."""
    n = len(items)
    h = 120 + n * size * 1.45
    with xform(cr, x, y, 1.0, rot):
        rrect(cr, -w / 2, -h / 2, w, h, 12, fill=paper, stroke=ink, lw=5)
        rect(cr, -w / 2, -h / 2, w, 60, fill=RED, stroke=ink, lw=5)
        text(cr, title, 0, -h / 2 + 30, 34, face=FONT_TITLE, c=WHITE)
        for i, it in enumerate(items):
            ka = clamp(k_items * n - i)
            if ka <= 0:
                continue
            yy = -h / 2 + 100 + i * size * 1.45
            rrect(cr, -w / 2 + 24, yy - 16, 32, 32, 6, fill=WHITE, stroke=ink, lw=3, a=ka)
            text(cr, it, -w / 2 + 72, yy, size, face=FONT_HAND, bold=True, align="left", c=ink, a=ka)
            kc = clamp(k_checks * n - i)
            if kc > 0:
                check(cr, -w / 2 + 40, yy, 0.8, p=kc)
                if strike:
                    tw = text_w(cr, it, FONT_HAND, size, True)
                    partial_line(cr, -w / 2 + 68, yy + 2, -w / 2 + 76 + tw, yy + 2, kc, 4, ink, 0.7)


def phone_big(cr, x, y, s=1.0, content=None, rot=0.0, lit=1.0, ink=INK):
    """Big phone; content(cr) draws inside a 290x520 screen centred on the origin."""
    with xform(cr, x, y, s, rot):
        if lit > 0:
            glow(cr, 0, 0, 420, (0.55, 0.75, 1.0), 0.35 * lit)
        rrect(cr, -162, -300, 324, 600, 40, fill=ink, stroke=(0.35, 0.35, 0.4), lw=4)
        cr.save()
        rrect_path(cr, -145, -265, 290, 520, 18)
        cr.clip()
        fill_bg(cr, lerpc((0.06, 0.07, 0.10), (0.93, 0.95, 1.0), lit))
        if content:
            content(cr)
        cr.restore()
        cr.new_path()
        rrect(cr, -40, -288, 80, 12, 6, fill=(0.3, 0.3, 0.34))


def contacts(cr, names, title="ONLINE: 0", T=0.0, k=1.0):
    """Phone content: a contact list where everyone is asleep."""
    rect(cr, -145, -265, 290, 70, fill=(0.25, 0.45, 0.85))
    text(cr, title, 0, -230, 30, face=FONT_TITLE, c=WHITE)
    for i, nm in enumerate(names):
        kk = clamp(k * len(names) - i)
        if kk <= 0:
            continue
        yy = -150 + i * 92
        circle(cr, -95, yy, 30, fill=LIGHT, stroke=INK, w=3, a=kk)
        p = sm.pose("front", s=0.32, smile=0.2, blink=1.0)
        cr.save()
        cr.arc(-95, yy, 28, 0, TAU)
        cr.clip()
        sm.draw(cr, head_at(p, -95, yy + 4), acc=[("cap",), ("ponytail",), ("glasses",), ("bun",), ()][i % 5])
        cr.restore()
        cr.new_path()
        text(cr, nm, -50, yy - 12, 28, face=FONT_BOLD, align="left", a=kk)
        text(cr, "asleep  zzz", -50, yy + 20, 22, face=FONT_HAND, bold=True, c=MID, align="left", a=kk)
        circle(cr, 115, yy, 9, fill=MID, a=kk)


def traffic_light(cr, x, gy, s=1.0, T=0.0, ink=INK):
    with xform(cr, x, gy, s):
        line(cr, 0, 0, 0, -380, 12, (0.25, 0.25, 0.3))
        rrect(cr, -45, -560, 90, 200, 16, fill=(0.15, 0.15, 0.18), stroke=ink, lw=5)
        on = 0.5 + 0.5 * math.copysign(1, math.sin(T * math.pi * 1.6))
        for i, c in enumerate(((0.35, 0.10, 0.10), YELLOW, (0.10, 0.30, 0.15))):
            cc = c if i != 1 else lerpc((0.35, 0.28, 0.08), YELLOW, on)
            if i == 1 and on > 0.5:
                glow(cr, 0, -460, 160, YELLOW, 0.55)
            circle(cr, 0, -520 + i * 60, 22, fill=cc, stroke=ink, w=3)


def streetlamp(cr, x, gy, s=1.0, on=1.0, ink=INK, c=(1.0, 0.85, 0.5), face=1):
    with xform(cr, x, gy, s, sx=s * face, sy=s):
        line(cr, 0, 0, 0, -420, 10, (0.25, 0.25, 0.3))
        polyline(cr, bezier_pts([(0, -420), (0, -470), (60, -470)], 10), 10, (0.25, 0.25, 0.3))
        if on > 0:
            cr.move_to(45, -455)
            cr.line_to(95, -455)
            cr.line_to(190, 0)
            cr.line_to(-50, 0)
            cr.close_path()
            g = cairo.LinearGradient(0, -455, 0, 0)
            g.add_color_stop_rgba(0, *c, 0.30 * on)
            g.add_color_stop_rgba(1, *c, 0.04 * on)
            cr.set_source(g)
            cr.fill()
            glow(cr, 70, -450, 120, c, 0.6 * on)
        polyline(cr, [(35, -475), (105, -475), (95, -450), (45, -450)], 4, ink, closed=True, fill=(0.3, 0.3, 0.35))
        ellipse(cr, 70, -450, 25, 6, fill=lerpc((0.4, 0.4, 0.4), c, on))


def building(cr, x, gy, w, h, c=(0.30, 0.32, 0.42), sign=None, sign_c=(1.0, 0.85, 0.3), lit=1.0, T=0.0, ink=INK,
             awn=None, door=True, seed=1, sign_size=40, win_rows=None):
    """Simple storefront/building, base at floor, centred on x."""
    rect(cr, x - w / 2, gy - h, w, h, fill=c, stroke=ink, lw=5)
    g = rng(seed)
    rows = win_rows if win_rows is not None else max(1, int((h - 200) / 90))
    for j in range(rows):
        for i in range(max(1, int(w / 110))):
            n = max(1, int(w / 110))
            wx = x - w / 2 + (i + 0.5) * w / n
            wy = gy - h + 50 + j * 90
            on = g.random() < 0.8
            rect(cr, wx - 28, wy, 56, 56, fill=lerpc((0.15, 0.16, 0.22), (1.0, 0.86, 0.5), lit if on else 0.0),
                 stroke=ink, lw=3)
    if awn:
        n = int(w / 50)
        for i in range(n):
            polyline(cr, [(x - w / 2 + i * w / n, gy - 190), (x - w / 2 + (i + 1) * w / n, gy - 190),
                          (x - w / 2 + (i + 1) * w / n, gy - 150), (x - w / 2 + i * w / n, gy - 150)], 3, ink,
                     closed=True, fill=awn if i % 2 == 0 else WHITE)
    if door:
        rect(cr, x - 40, gy - 130, 80, 130, fill=lerpc((0.12, 0.12, 0.16), (1.0, 0.9, 0.6), lit * 0.8), stroke=ink,
             lw=4)
    if sign:
        tw = text_w(cr, sign, FONT_TITLE, sign_size)
        sy = gy - h - 10
        rrect(cr, x - tw / 2 - 20, sy - sign_size * 0.75, tw + 40, sign_size * 1.5, 10, fill=(0.10, 0.10, 0.14),
              stroke=ink, lw=4)
        if lit > 0:
            glow(cr, x, sy, tw * 0.7, sign_c, 0.25 * lit)
        text(cr, sign, x, sy, sign_size, face=FONT_TITLE, c=lerpc((0.4, 0.4, 0.45), sign_c, lit))


def night_street(cr, T, cam=0.0, gy=880):
    S.city(cr, T, cam, gy=gy, night=True, sky=NIGHT_SKY)


# ---------------------------------------------------------------- house cutaway
def house_cutaway(cr, T, x=CX, gy=1000, s=1.0, lights=(1, 1, 1, 1), fam_sleep=1.0, hero_g="stand", hero_kw=None,
                  sky=True, k_day=0.0):
    """Two-storey house in cross-section. Upstairs: parents, sister, hero. Downstairs: living room.
    lights: (parents, sister, hero, downstairs) 0..1; fam_sleep 0 = standing & yawning, 1 = asleep in bed."""
    hero_kw = hero_kw or {}
    if sky:
        sky_dawn(cr, k_day, T)
        moon(cr, 1700, 160, 55, a=1 - k_day)
        S.floor(cr, gy, (0.10, 0.12, 0.10), (0.25, 0.28, 0.25), 4)
    rooms = [(-750, -250), (-250, 250), (250, 750)]
    with xform(cr, x, gy, s):
        polyline(cr, [(-820, -640), (0, -880), (820, -640)], 6, INK, closed=True, fill=(0.45, 0.20, 0.20))
        rect(cr, 120, -880, 80, 160, fill=(0.50, 0.30, 0.25), stroke=INK, lw=5)
        rect(cr, -770, -640, 1540, 640, fill=(0.40, 0.38, 0.42), stroke=INK, lw=6)
        for i, (x0, x1) in enumerate(rooms):
            lt = lights[i]
            rect(cr, x0, -620, x1 - x0, 290, fill=lerpc((0.10, 0.11, 0.18), (0.98, 0.88, 0.62), lt))
            if lt > 0:
                glow(cr, (x0 + x1) / 2, -560, 300, (1.0, 0.9, 0.6), 0.3 * lt)
        lt = lights[3]
        rect(cr, -750, -310, 1500, 290, fill=lerpc((0.10, 0.11, 0.18), (0.98, 0.88, 0.62), lt))
        rect(cr, -770, -330, 1540, 20, fill=(0.40, 0.38, 0.42), stroke=INK, lw=4)
        for xx in (-250, 250):
            rect(cr, xx - 10, -620, 20, 290, fill=(0.40, 0.38, 0.42), stroke=INK, lw=4)
        night = [lights[i] < 0.5 for i in range(4)]
        # parents
        ink0, fill0 = (NI, NF) if night[0] else (INK, WHITE)
        if fam_sleep > 0.5:
            bed2(cr, T, -500, -330, 0.55, who="sleep", acc=DAD, two=MOM, ink=ink0, fill=fill0, z_c=NI if night[0] else INK,
                 seed=1)
        else:
            bed2(cr, T, -500, -330, 0.55, ink=ink0)
            K.person(cr, T, -660, -330, "stand", s=0.62, acc=DAD, face=1, ink=ink0, fill=fill0, mo=0.6, blink=0.8,
                     a1f=140, a2f=40, seed=1)
            K.person(cr, T, -340, -330, "stand", s=0.6, acc=MOM, face=-1, ink=ink0, fill=fill0, mo=0.6, blink=0.8,
                     a1f=140, a2f=40, seed=2)
        # sister
        ink1, fill1 = (NI, NF) if night[1] else (INK, WHITE)
        if fam_sleep > 0.5:
            bed2(cr, T, 0, -330, 0.55, who="sleep", acc=SIS, ink=ink1, fill=fill1, blanket=(0.80, 0.45, 0.60),
                 z_c=NI if night[1] else INK, seed=2)
        else:
            bed2(cr, T, 0, -330, 0.55, ink=ink1, blanket=(0.80, 0.45, 0.60))
            K.person(cr, T, -150, -330, "stand", s=0.55, acc=SIS, face=1, ink=ink1, fill=fill1, mo=0.6, blink=0.8,
                     a1f=140, a2f=40, seed=3)
        # hero's room
        ink2, fill2 = (NI, NF) if night[2] else (INK, WHITE)
        P.desk(cr, 560, -330, 260, 0.9)
        nightstand_lamp(cr, 640, -460, 0.45, on=lights[2])
        P.book(cr, 520, -480, 0.4, c=RED)
        hk = dict(s=0.6, face=1, ink=ink2, fill=fill2)
        hk.update(hero_kw)
        K.hero(cr, T, 400, -330, hero_g, **hk)
        # downstairs
        ink3 = NI if night[3] else INK
        couch(cr, -380, -20, 0.6, c=(0.40, 0.25, 0.30) if night[3] else (0.65, 0.35, 0.38), ink=ink3)
        tv(cr, 120, -20, 0.5, T, ch=-1, ink=ink3, glow_a=0.0)
        fridge(cr, 560, -20, 0.6, T, ink=ink3, c=(0.30, 0.32, 0.38) if night[3] else (0.92, 0.94, 0.96))
        polyline(cr, [(-770, -640), (0, -880), (770, -640)], 6, INK)


# ---------------------------------------------------------------- animals
def cat_sleep(cr, x, y, s=1.0, T=0.0, c=(0.95, 0.65, 0.30), ink=INK):
    with xform(cr, x, y, s):
        br = 1 + 0.03 * math.sin(T * 1.6)
        ellipse(cr, 0, 0, 110 * br, 60 * br, fill=c, stroke=ink, w=5)
        polyline(cr, bezier_pts([(100, 10), (130, 60), (20, 75), (-90, 50)], 16), 14, ink)
        polyline(cr, bezier_pts([(100, 10), (130, 60), (20, 75), (-90, 50)], 16), 8, c)
        circle(cr, -85, -20, 48, fill=c, stroke=ink, w=5)
        for k in (-1, 1):
            polyline(cr, [(-85 + k * 8, -62), (-85 + k * 30, -94), (-85 + k * 40, -40)], 5, ink, closed=True, fill=c)
        for k in (-1, 1):
            arc(cr, -85 + k * 18, -22, 9, 0.2, math.pi - 0.2, 4, ink)
        circle(cr, -85, -5, 5, fill=(0.9, 0.5, 0.5))


def bat_hang(cr, x, y, s=1.0, T=0.0, c=(0.30, 0.22, 0.38), ink=INK):
    """Upside-down bat; (x, y) is the branch grip point."""
    with xform(cr, x, y + 4 * math.sin(T * 1.3), s):
        line(cr, -120, 0, 120, 0, 10, (0.45, 0.32, 0.22))
        line(cr, -10, 0, -10, 18, 5, ink)
        line(cr, 10, 0, 10, 18, 5, ink)
        ellipse(cr, 0, 75, 48, 64, fill=c, stroke=ink, w=5)
        polyline(cr, [(-48, 60), (-30, 140), (0, 125), (30, 140), (48, 60)], 5, ink, fill=lerpc(c, BLACK, 0.2))
        circle(cr, 0, 145, 32, fill=c, stroke=ink, w=5)
        for k in (-1, 1):
            polyline(cr, [(k * 12, 172), (k * 26, 205), (k * 30, 165)], 4, ink, closed=True, fill=c)
            arc(cr, k * 12, 142, 7, math.pi + 0.3, TAU - 0.3, 3, WHITE)


def fish(cr, x, y, s=1.0, T=0.0, c=(1.0, 0.55, 0.25), ink=INK, face=1, sleep=True):
    with xform(cr, x, y + 5 * math.sin(T * 1.2), s, sx=s * face, sy=s):
        polyline(cr, [(-70, 0), (-115, -40), (-110, 40)], 5, ink, closed=True, fill=c)
        ellipse(cr, 0, 0, 85, 50, fill=c, stroke=ink, w=5)
        polyline(cr, bezier_pts([(-10, -48), (10, -80), (40, -42)], 8), 5, ink, fill=c)
        if sleep:
            line(cr, 38, -10, 58, -10, 4, ink)
        else:
            circle(cr, 48, -10, 8, fill=ink)
        arc(cr, 10, 0, 30, -0.9, 0.9, 3, ink, 0.6)


def bird_sleep(cr, x, y, s=1.0, T=0.0, c=(0.62, 0.64, 0.72), ink=INK, branch=True, face=1):
    """Round sleeping bird perched at (x, y)."""
    with xform(cr, x, y, s, sx=s * face, sy=s):
        if branch:
            line(cr, -110, 0, 110, 0, 8, (0.45, 0.32, 0.22))
        line(cr, -8, 0, -8, -16, 4, ORANGE)
        line(cr, 8, 0, 8, -16, 4, ORANGE)
        b = 1 + 0.03 * math.sin(T * 1.8)
        ellipse(cr, 0, -50, 46 * b, 38 * b, fill=c, stroke=ink, w=4)
        polyline(cr, [(-40, -60), (-75, -50), (-40, -38)], 4, ink, closed=True, fill=c)
        circle(cr, 28, -82, 22, fill=c, stroke=ink, w=4)
        arc(cr, 34, -84, 6, 0.2, math.pi - 0.2, 3, ink)
        polyline(cr, [(48, -80), (62, -76), (48, -70)], 3, ink, closed=True, fill=ORANGE)
        ellipse(cr, -8, -50, 28, 16, fill=lerpc(c, BLACK, 0.15), stroke=ink, w=3)


def mouse_lab(cr, x, y, s=1.0, ink=INK, c=(0.85, 0.85, 0.88)):
    with xform(cr, x, y, s):
        polyline(cr, bezier_pts([(-60, 10), (-120, 30), (-140, -20)], 12), 4, (0.85, 0.6, 0.6))
        ellipse(cr, 0, 0, 65, 40, fill=c, stroke=ink, w=4)
        circle(cr, 55, -20, 30, fill=c, stroke=ink, w=4)
        circle(cr, 45, -52, 18, fill=(1.0, 0.8, 0.85), stroke=ink, w=4)
        circle(cr, 64, -18, 4, fill=ink)
        circle(cr, 86, -12, 6, fill=(0.9, 0.5, 0.55))


def dolphin(cr, x, y, s=1.0, T=0.0, face=1, c=(0.52, 0.66, 0.86), ink=INK, eye_closed=0.0, rot=0.0):
    belly_c = (0.88, 0.92, 0.97)
    flap = 14 * math.sin(T * 4)
    with xform(cr, x, y, s, rot, sx=s * face, sy=s):
        polyline(cr, [(-150, 0), (-215, -38 + flap), (-190, 2), (-215, 42 + flap)], 5, ink, closed=True, fill=c)
        top = bezier_pts([(-160, 0), (-60, -62), (90, -66), (150, -22)], 24)
        beak = [(170, -14), (215, -4), (214, 6), (165, 10)]
        bot = bezier_pts([(150, 22), (60, 50), (-80, 40), (-160, 4)], 24)
        polyline(cr, top + beak + bot, 5, ink, closed=True, fill=c)
        polyline(cr, bezier_pts([(165, 10), (90, 44), (-40, 42), (-120, 14)], 16) +
                 bezier_pts([(-120, 14), (-20, 22), (100, 18), (165, 10)], 16), 0, ink, closed=True, fill=belly_c)
        polyline(cr, bezier_pts([(-40, -56), (-10, -78), (10, -120), (40, -58)], 16), 5, ink, closed=True, fill=c)
        polyline(cr, [(30, 22), (0, 70), (-20, 28)], 4, ink, closed=True, fill=c)
        polyline(cr, bezier_pts([(214, 4), (190, 12), (170, 8)], 8), 3, ink)
        if eye_closed > 0.5:
            arc(cr, 128, -16, 9, 0.2, math.pi - 0.2, 4, ink)
        else:
            circle(cr, 128, -18, 7, fill=ink)
            circle(cr, 130, -20, 2.4, fill=WHITE)
        circle(cr, 60, -60, 5, fill=ink)


def frigatebird(cr, x, y, s=1.0, T=0.0, face=1, nap=0.0, ink=INK):
    flap = 0.08 * math.sin(T * 1.5)
    with xform(cr, x, y, s, sx=s * face, sy=s):
        c = (0.10, 0.10, 0.13)
        for k in (-1, 1):
            pts = [(0, -5), (k * 120, -60 + flap * 300), (k * 260, -20 + flap * 200), (k * 330, 30 + flap * 150),
                   (k * 230, 0), (k * 110, 15), (0, 15)]
            polyline(cr, pts, 4, (0.35, 0.35, 0.4), closed=True, fill=c)
        ellipse(cr, 0, 10, 95, 26, fill=c, stroke=(0.35, 0.35, 0.4), w=4)
        polyline(cr, [(-90, 10), (-170, -20), (-120, 12), (-170, 40)], 4, (0.35, 0.35, 0.4), closed=True, fill=c)
        circle(cr, 110, 0, 26, fill=c, stroke=(0.35, 0.35, 0.4), w=4)
        ellipse(cr, 86, 36, 34, 30, fill=(0.95, 0.15, 0.15), stroke=ink, w=3)
        polyline(cr, [(130, -6), (190, 2), (186, 14), (130, 8)], 3, ink, closed=True, fill=(0.55, 0.55, 0.6))
        if nap > 0.5:
            arc(cr, 116, -4, 7, 0.2, math.pi - 0.2, 3, WHITE)
        else:
            circle(cr, 116, -6, 5, fill=WHITE)


def fur_seal(cr, x, y, s=1.0, T=0.0, ink=INK, c=(0.50, 0.38, 0.28)):
    """Seal floating on its back, (x, y) at the waterline centre."""
    bob = 6 * math.sin(T * 1.4)
    with xform(cr, x, y + bob, s):
        ellipse(cr, 0, -10, 150, 45, fill=c, stroke=ink, w=5)
        circle(cr, 150, -30, 42, fill=c, stroke=ink, w=5)
        ellipse(cr, 185, -22, 18, 14, fill=lerpc(c, WHITE, 0.3), stroke=ink, w=3)
        arc(cr, 150, -38, 8, 0.2, math.pi - 0.2, 4, ink)
        arc(cr, 168, -40, 8, 0.2, math.pi - 0.2, 4, ink)
        for k in (-1, 1):
            line(cr, 190, -20, 220, -20 + k * 10, 2, ink)
        w_ = 10 * math.sin(T * 3)
        polyline(cr, [(40, -40), (70, -95 + w_), (95, -90 + w_), (75, -38)], 5, ink, closed=True, fill=c)
        polyline(cr, [(-140, -20), (-205, -60), (-200, 10)], 5, ink, closed=True, fill=c)


def sea_turtle(cr, x, y, s=1.0, T=0.0, face=1, ink=INK):
    with xform(cr, x, y, s, sx=s * face, sy=s):
        f = 10 * math.sin(T * 6)
        for k in (-1, 1):
            polyline(cr, [(30, k * 20), (60, k * (60 + f)), (10, k * 40)], 4, ink, closed=True, fill=(0.45, 0.65, 0.35))
            polyline(cr, [(-40, k * 20), (-55, k * 45), (-25, k * 30)], 4, ink, closed=True, fill=(0.45, 0.65, 0.35))
        circle(cr, 70, 0, 18, fill=(0.45, 0.65, 0.35), stroke=ink, w=4)
        circle(cr, 78, -6, 3, fill=ink)
        ellipse(cr, 0, 0, 55, 40, fill=(0.30, 0.50, 0.30), stroke=ink, w=4)
        for (px, py) in ((0, 0), (-25, -15), (25, -15), (-25, 15), (25, 15)):
            circle(cr, px, py, 9, stroke=(0.2, 0.35, 0.2), w=3)


def moth(cr, x, y, s=1.0, T=0.0, c=(0.85, 0.80, 0.65), ink=INK):
    f = 0.5 + 0.5 * math.sin(T * 30 + x)
    with xform(cr, x, y, s):
        for k in (-1, 1):
            ellipse(cr, k * 16, -6, 18, 12 + 6 * f, fill=c, stroke=ink, w=2, rot=k * 0.5)
        ellipse(cr, 0, 0, 5, 12, fill=ink)


def owl(cr, x, y, s=1.0, T=0.0, squint=0.0, shades=0.0, ink=INK, c=(0.62, 0.45, 0.30)):
    """Owl perched at (x, y)."""
    with xform(cr, x, y, s):
        line(cr, -120, 0, 120, 0, 10, (0.45, 0.32, 0.22))
        ellipse(cr, 0, -90, 70, 90, fill=c, stroke=ink, w=5)
        ellipse(cr, 0, -70, 45, 55, fill=lerpc(c, WHITE, 0.45))
        for k in (-1, 1):
            polyline(cr, [(k * 30, -160), (k * 55, -200), (k * 62, -150)], 5, ink, closed=True, fill=c)
            circle(cr, k * 30, -125, 26, fill=WHITE, stroke=ink, w=4)
            if squint > 0.5:
                line(cr, k * 30 - 16, -125, k * 30 + 16, -125 + k * 4, 5, ink)
            else:
                circle(cr, k * 30, -125, 11, fill=ink)
        polyline(cr, [(-10, -105), (10, -105), (0, -85)], 3, ink, closed=True, fill=ORANGE)
        if shades > 0:
            with group(cr, shades):
                for k in (-1, 1):
                    rrect(cr, k * 30 - 30, -142, 60, 34, 10, fill=INK)
                line(cr, -5, -132, 5, -132, 6, INK)


# ---------------------------------------------------------------- brain & body
def brain_big(cr, x, y, s=1.0, T=0.0, c=(1.0, 0.72, 0.78), glow_a=0.0):
    P.brain(cr, x, y, s, c=c, glow_a=glow_a, t=T)


def half_brain(cr, x, y, s=1.0, T=0.0, sleep_side=-1, label=True, dark=True):
    """Brain icon with one hemisphere asleep (dim, Z's) and one awake (bright)."""
    with xform(cr, x, y, s):
        for side in (-1, 1):
            asleep = side == sleep_side
            col = (0.45, 0.45, 0.70) if asleep else (1.0, 0.72, 0.78)
            cr.save()
            cr.rectangle(-200 if side < 0 else 0, -200, 200, 400)
            cr.clip()
            if not asleep:
                glow(cr, side * 50, 0, 170, YELLOW, 0.35)
            P.brain(cr, 0, 0, 1.0, c=col)
            cr.restore()
            cr.new_path()
        line(cr, 0, -100, 0, 80, 5, INK)
    zzz(cr, x + sleep_side * 70 * s, y - 70 * s, T, s, c=NI if dark else INK)
    if label:
        text(cr, "ASLEEP", x + sleep_side * 85 * s, y + 140 * s, 30 * s, face=FONT_TITLE, c=(0.6, 0.65, 1.0))
        text(cr, "AWAKE", x - sleep_side * 85 * s, y + 140 * s, 30 * s, face=FONT_TITLE, c=YELLOW)


def janitor(cr, T, x, gy, s=1.0, face=1, ink=INK, fill=WHITE, tool="mop", seed=0, a=1.0):
    """Tiny cleaning-crew stickman scrubbing with a mop (or carrying a bucket)."""
    sw = math.sin(T * 6 + seed)
    p = sm.pose("hold", x=x, face=face, s=s, a1f=60 + 15 * sw, a2f=30, a1b=50 + 15 * sw, a2b=40, smile=0.7)
    p = sm.on_ground(sm.idle(p, T, seed), gy)
    J = sm.draw(cr, p, ink=ink, fill=fill, acc=("cap",), alpha=a)
    hx, hy = J["hand_f"]
    if tool == "mop":
        mx = hx + face * 70 * s + sw * 20 * s
        line(cr, hx - face * 30 * s, hy - 40 * s, mx, gy - 6 * s, 6 * s, (0.6, 0.45, 0.3), a)
        for i in range(5):
            line(cr, mx, gy - 8 * s, mx + (i - 2) * 9 * s, gy + 2 * s, 5 * s, (0.75, 0.85, 1.0), a)
    else:
        polyline(cr, [(hx - 22 * s, hy + 10 * s), (hx + 22 * s, hy + 10 * s), (hx + 16 * s, hy + 50 * s),
                      (hx - 16 * s, hy + 50 * s)], 4 * s, ink, a, closed=True, fill=(0.35, 0.55, 0.90), fa=a)
    return J


def filing_cabinet(cr, x, gy, s=1.0, open_k=0.0, ink=INK, labels=("SCHOOL", "FRIENDS", "SKILLS")):
    with xform(cr, x, gy, s):
        rect(cr, -110, -420, 220, 420, fill=(0.62, 0.66, 0.72), stroke=ink, lw=5)
        for i, lab in enumerate(labels):
            dy = -400 + i * 135
            ox = 60 * open_k if i == 1 else 0
            rect(cr, -95 + ox, dy, 190, 120, fill=(0.72, 0.76, 0.82), stroke=ink, lw=4)
            rrect(cr, -55 + ox, dy + 18, 110, 34, 6, fill=WHITE, stroke=ink, lw=3)
            text(cr, lab, ox, dy + 35, 22, face=FONT_TITLE)
            line(cr, -30 + ox, dy + 80, 30 + ox, dy + 80, 8, ink)


MEM_COLORS = [(0.95, 0.55, 0.35), (0.45, 0.70, 0.95), (0.55, 0.85, 0.50), (0.95, 0.80, 0.30), (0.80, 0.55, 0.90)]


def mem_icon(cr, kind, s=1.0):
    """Tiny icons for memory cards (drawn at origin, ~ +-40 px)."""
    with xform(cr, 0, 0, s):
        if kind == "ball":
            circle(cr, 0, 0, 34, fill=WHITE, stroke=INK, w=4)
            polyline(cr, [(-12, -10), (12, -10), (18, 12), (0, 24), (-18, 12)], 3, INK, closed=True, fill=INK)
        elif kind == "star":
            star_shape(cr, 0, 0, 38, fill=YELLOW, stroke=INK, w=4)
        elif kind == "book":
            P.book(cr, 0, 0, 0.45, open_=1.0)
        elif kind == "heart":
            P.heart(cr, 0, 4, 0.7)
        elif kind == "pizza":
            polyline(cr, [(-34, -26), (34, -26), (0, 36)], 4, INK, closed=True, fill=(1.0, 0.82, 0.35))
            for (px, py) in ((-10, -12), (10, -4), (0, 12)):
                circle(cr, px, py, 6, fill=RED)
        elif kind == "cat":
            circle(cr, 0, 6, 28, fill=(0.95, 0.65, 0.30), stroke=INK, w=4)
            for k in (-1, 1):
                polyline(cr, [(k * 10, -16), (k * 24, -40), (k * 28, -8)], 4, INK, closed=True, fill=(0.95, 0.65, 0.30))
                circle(cr, k * 10, 2, 4, fill=INK)
        elif kind == "rocket":
            polyline(cr, [(0, -40), (16, -10), (16, 24), (-16, 24), (-16, -10)], 4, INK, closed=True, fill=WHITE)
            polyline(cr, [(-16, 10), (-30, 30), (-16, 24)], 3, INK, closed=True, fill=RED)
            polyline(cr, [(16, 10), (30, 30), (16, 24)], 3, INK, closed=True, fill=RED)
            circle(cr, 0, -6, 7, fill=CYAN, stroke=INK, w=3)
        elif kind == "test":
            rect(cr, -26, -34, 52, 68, fill=WHITE, stroke=INK, lw=4)
            text(cr, "A+", 0, 0, 30, face=FONT_TITLE, c=RED)
        elif kind == "face":
            circle(cr, 0, 0, 30, fill=WHITE, stroke=INK, w=4)
            circle(cr, -10, -6, 4, fill=INK)
            circle(cr, 10, -6, 4, fill=INK)
            arc(cr, 0, 2, 14, 0.3, math.pi - 0.3, 4, INK)
        elif kind == "storm":
            P.cloud(cr, 0, -6, 0.42, c=(0.6, 0.62, 0.7))
            polyline(cr, [(4, 10), (-8, 28), (4, 28), (-6, 44)], 4, YELLOW)


def mem_card(cr, x, y, kind, s=1.0, ci=0, glow_a=0.0, rot=0.0, a=1.0):
    with group(cr, a):
        with xform(cr, x, y, s, rot):
            if glow_a > 0:
                glow(cr, 0, 0, 140, YELLOW, glow_a)
            rrect(cr, -55, -55, 110, 110, 14, fill=MEM_COLORS[ci % len(MEM_COLORS)], stroke=INK, lw=5)
            mem_icon(cr, kind, 1.0)


def muscle_icon(cr, T=0.0):
    skin = (1.0, 0.84, 0.72)
    arm = [(-110, 50), (10, 50), (40, -70)]
    polyline(cr, arm, 46, INK)
    polyline(cr, arm, 36, skin)
    ellipse(cr, -45, 22, 56, 40, fill=skin, stroke=INK, w=5)
    circle(cr, 44, -84, 30, fill=skin, stroke=INK, w=5)
    with xform(cr, -45, 22, 1.0, -0.25):
        rrect(cr, -16, -36, 32, 72, 8, fill=WHITE, stroke=INK, lw=3)
        line(cr, -7, 0, 7, 0, 4, RED)
        line(cr, 0, -7, 0, 7, 4, RED)
    with xform(cr, 95, 10, 1.0, 0.5 + 0.25 * math.sin(T * 5)):
        line(cr, 0, 0, 0, 80, 14, (0.55, 0.55, 0.6))
        arc(cr, 0, -12, 22, math.pi * 0.25, math.pi * 1.75, 12, (0.55, 0.55, 0.6))


def hormone_icon(cr, T=0.0):
    tilt = 0.12 * math.sin(T * 2)

    def l(c):
        circle(c, -20, 70, 16, fill=PURPLE, stroke=INK, w=3)
        circle(c, 16, 74, 12, fill=ORANGE, stroke=INK, w=3)

    def r(c):
        circle(c, 0, 70, 16, fill=CYAN, stroke=INK, w=3)
        circle(c, 30, 74, 12, fill=GREEN, stroke=INK, w=3)
    P.scale_balance(cr, 0, 110, 0.55, tilt=tilt, left=l, right=r)


def shield_icon(cr, T=0.0):
    pts = [(0, -100), (80, -70), (70, 30), (0, 100), (-70, 30), (-80, -70)]
    polyline(cr, pts, 6, INK, closed=True, fill=(0.40, 0.65, 0.95))
    circle(cr, 0, -5, 38, fill=WHITE, stroke=INK, w=5)
    for i in range(6):
        a = i / 6 * TAU + T
        line(cr, math.cos(a) * 38, -5 + math.sin(a) * 38, math.cos(a) * 52, -5 + math.sin(a) * 52, 5, INK)
    circle(cr, -10, -12, 6, fill=INK)
    circle(cr, 12, -12, 6, fill=INK)
    arc(cr, 0, 0, 14, 0.3, math.pi - 0.3, 4, INK)


def light_switch(cr, x, y, s=1.0, on=False, ink=INK):
    with xform(cr, x, y, s):
        rrect(cr, -70, -110, 140, 220, 18, fill=WHITE, stroke=ink, lw=6)
        rrect(cr, -28, -60, 56, 120, 10, fill=LIGHT, stroke=ink, lw=4)
        rrect(cr, -22, -54 if on else 4, 44, 50, 8, fill=WHITE, stroke=ink, lw=4)
        text(cr, "ON" if on else "OFF", 0, 85, 26, face=FONT_TITLE)


def brain_factory(cr, x, y, s=1.0, T=0.0, lit=1.0):
    """A brain-shaped factory working the night shift."""
    with xform(cr, x, y, s):
        rect(cr, 40, -260, 50, 130, fill=(0.55, 0.50, 0.55), stroke=INK, lw=5)
        for i in range(4):
            f = (T * 0.35 + i * 0.25) % 1
            circle(cr, 65 + 25 * f, -270 - 140 * f, 18 + 26 * f, fill=(0.75, 0.75, 0.82), a=0.7 * (1 - f))
        P.brain(cr, 0, 0, 1.9, c=(1.0, 0.72, 0.78))
        for (wx, wy) in ((-80, -40), (-10, -70), (60, -30), (-40, 30), (40, 40)):
            rect(cr, wx - 18, wy - 16, 36, 32, fill=lerpc((0.3, 0.3, 0.4), (1.0, 0.88, 0.45), lit), stroke=INK, lw=3)
        g1 = T * 1.5
        P.gear(cr, -120, 80, 34, 8, g1, fill=(0.85, 0.85, 0.9))
        P.gear(cr, -70, 110, 24, 7, -g1 * 1.4, fill=(0.85, 0.85, 0.9))


def eeg(cr, x, y, w, h, T, busy=1.0, c=GREEN, rows=3):
    for r in range(rows):
        yy = y + (r + 0.5) * h / rows
        pts = []
        for i in range(120):
            u = i / 119
            px = x + u * w
            amp = h / rows * 0.35 * busy
            v = math.sin(u * 40 + T * 9 + r * 2) * 0.6 + math.sin(u * 97 - T * 13 + r) * 0.4
            pts.append((px, yy + v * amp))
        polyline(cr, pts, 3, c)


# ---------------------------------------------------------------- misc props
def gift_box(cr, x, y, s=1.0, k_open=0.0, c=(0.18, 0.20, 0.45), rib=GOLD, T=0.0, inner=None):
    """Gift box with its base at (x, y); k_open lifts the lid. inner(cr) draws what spills out (at the box mouth)."""
    with xform(cr, x, y, s):
        if k_open > 0 and inner:
            inner(cr)
        rect(cr, -150, -220, 300, 220, fill=c, stroke=INK, lw=6)
        for i in range(9):
            g = rng(i + 30)
            star_shape(cr, g.uniform(-130, 130), g.uniform(-200, -20), g.uniform(6, 12), fill=(1.0, 1.0, 0.85))
        rect(cr, -22, -220, 44, 220, fill=rib, stroke=INK, lw=4)
        ko = ease(k_open)
        with xform(cr, -170 - 330 * ko, -220 - 160 * math.sin(ko * math.pi) + 150 * ko, 1.0, -1.1 * ko):
            rect(cr, 0, -50, 340, 50, fill=lerpc(c, WHITE, 0.08), stroke=INK, lw=6)
            rect(cr, 148, -50, 44, 50, fill=rib, stroke=INK, lw=4)
            for k in (-1, 1):
                ellipse(cr, 170 + k * 40, -70, 42, 22, fill=rib, stroke=INK, w=4, rot=k * 0.4)


def calendar_page(cr, x, y, s=1.0, top="TUESDAY", big="14", top_c=RED, rot=0.0, a=1.0, melt=0.0, T=0.0, size=None):
    with group(cr, a):
        with xform(cr, x, y, s, rot):
            if melt > 0:
                pts = [(-130, -150), (130, -150)]
                for i in range(41):
                    u = i / 40
                    drip = melt * (30 + 110 * max(0.0, math.sin(u * TAU * 2.2 + 0.6)) ** 3 + 15 * math.sin(u * 9))
                    pts.append((130 - 260 * u + melt * 20 * math.sin(u * 3 + T), 150 + drip))
                polyline(cr, pts, 6, INK, closed=True, fill=WHITE)
            else:
                rrect(cr, -130, -150, 260, 300, 14, fill=WHITE, stroke=INK, lw=6)
            rect(cr, -130, -150, 260, 80, fill=top_c, stroke=INK, lw=6)
            text(cr, top, 0, -110, size or (34 if len(top) < 9 else 28), face=FONT_TITLE, c=WHITE)
            text(cr, big, 0, 30 + melt * 30, 120, face=FONT_TITLE, c=INK, scale=1.0)


def guitar(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rect(cr, -10, -230, 20, 170, fill=(0.45, 0.30, 0.2), stroke=INK, lw=4)
        rrect(cr, -18, -270, 36, 46, 8, fill=(0.35, 0.22, 0.15), stroke=INK, lw=4)
        circle(cr, 0, 40, 72, fill=(0.85, 0.50, 0.20), stroke=INK, w=5)
        circle(cr, 0, -40, 54, fill=(0.85, 0.50, 0.20), stroke=INK, w=5)
        rect(cr, -50, -10, 100, 40, fill=(0.85, 0.50, 0.20))
        circle(cr, 0, -10, 20, fill=INK)
        for k in (-6, 0, 6):
            line(cr, k, -260, k, 60, 1.5, (0.9, 0.9, 0.9))


def trumpet(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        line(cr, -110, 0, 60, 0, 14, INK)
        line(cr, -110, 0, 60, 0, 8, GOLD)
        polyline(cr, [(60, -8), (130, -45), (130, 45), (60, 8)], 4, INK, closed=True, fill=GOLD)
        rrect(cr, -40, -36, 80, 30, 10, stroke=INK, lw=4)
        for k in (-20, 0, 20):
            line(cr, k, -36, k, -54, 6, INK)


def book_stack(cr, x, gy, s=1.0, n=9, T=0.0, dust=0.0, seed=4):
    cols = [RED, BLUE, GREEN, ORANGE, PURPLE, (0.3, 0.6, 0.6), YELLOW]
    g = rng(seed)
    with xform(cr, x, gy, s):
        y = 0
        for i in range(n):
            h = g.uniform(30, 46)
            w = g.uniform(190, 250)
            ox = g.uniform(-18, 18) + math.sin(T * 1.5) * i * 0.6
            rrect(cr, ox - w / 2, y - h, w, h, 6, fill=cols[i % len(cols)], stroke=INK, lw=4)
            line(cr, ox - w / 2 + 18, y - h / 2, ox + w / 2 - 18, y - h / 2, 3, WHITE, 0.5)
            y -= h
        if dust > 0:
            polyline(cr, [(-60, y), (-20, y - 40), (30, y - 10), (70, y - 50)], 2, MID, dust)
            line(cr, -20, y - 40, -20, y, 1.5, MID, dust)
            line(cr, 30, y - 10, 70, y - 50, 1.5, MID, dust)


def pizza_scooter(cr, T, x, gy, s=1.0, face=1, ink=INK, fill=WHITE):
    with xform(cr, x, gy, s, sx=s * face, sy=s):
        for wx in (-90, 90):
            circle(cr, wx, -34, 32, fill=INK)
            circle(cr, wx, -34, 12, fill=LIGHT)
        polyline(cr, [(-120, -60), (60, -60), (110, -150), (130, -150), (100, -60), (120, -40), (-120, -40)], 4, ink,
                 closed=True, fill=RED)
        for i in range(4):
            rect(cr, -140, -95 - i * 22, 90, 20, fill=(0.95, 0.85, 0.65), stroke=INK, lw=3)
        p = sm.pose("sit", x=-10, s=0.6, face=1, a1f=80, a2f=10, a1b=70, a2b=20, smile=0.8)
        p["y"] = -100
        sm.draw(cr, sm.idle(p, T, 3), ink=ink, fill=fill, acc=("cap",))


def snake_ring(cr, x, y, r, T=0.0, k=1.0, c=(0.35, 0.65, 0.30), a=1.0):
    """A snake biting its own tail (ouroboros), drawn around (x, y)."""
    rot = T * 0.6
    n = 60
    span = TAU * 0.92 * clamp(k)
    pts = [(x + math.cos(rot + u * span / n) * r, y + math.sin(rot + u * span / n) * r) for u in range(n + 1)]
    polyline(cr, pts, r * 0.24 + 6, INK, a)
    polyline(cr, pts, r * 0.24, c, a)
    for i in range(0, n, 4):
        circle(cr, pts[i][0], pts[i][1], r * 0.04, fill=lerpc(c, BLACK, 0.3), a=a)
    if k > 0.05:
        hx, hy = pts[-1]
        ang = rot + span + math.pi / 2
        with xform(cr, hx, hy, 1.0, ang):
            ellipse(cr, 0, 0, r * 0.2, r * 0.15, fill=c, stroke=INK, w=4, a=a)
            circle(cr, -r * 0.05, -r * 0.06, r * 0.035, fill=INK, a=a)


def benzene(cr, x, y, r, k=1.0, c=INK, a=1.0, label=True):
    pts = [(x + math.cos(math.pi / 6 + i * TAU / 6) * r, y + math.sin(math.pi / 6 + i * TAU / 6) * r) for i in range(7)]
    partial_poly(cr, pts, k, 8, c, a)
    if k >= 1:
        for i in (0, 2, 4):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ix, iy = lerp(mx, x, 0.18), lerp(my, y, 0.18)
            line(cr, lerp(x1, x2, 0.2) + (ix - mx), lerp(y1, y2, 0.2) + (iy - my), lerp(x1, x2, 0.8) + (ix - mx),
                 lerp(y1, y2, 0.8) + (iy - my), 6, c, a)
        if label:
            for (px, py) in pts[:6]:
                circle(cr, px, py, 20, fill=WHITE, stroke=c, w=4, a=a)
                text(cr, "C", px, py, 24, face=FONT_TITLE, c=c, a=a)


def nightcap(cr, J, s=1.0, c=(0.35, 0.45, 0.85), face=1):
    hx, hy = J["head"]
    r = 40 * s
    tip = (hx - face * 70 * s, hy - 10 * s)
    polyline(cr, [(hx - r * 1.0, hy - r * 0.45), (hx - face * 10 * s, hy - r * 1.7), tip, (hx + r * 1.0, hy - r * 0.45)],
             3 * s, INK, closed=True, fill=c)
    rrect(cr, hx - r * 1.05, hy - r * 0.62, r * 2.1, r * 0.34, 6 * s, fill=WHITE, stroke=INK, lw=3 * s)
    circle(cr, tip[0], tip[1], 10 * s, fill=WHITE, stroke=INK, w=3 * s)


def pajama_item(c=(0.40, 0.55, 0.90)):
    """`item` callback for sm.draw: striped pajama top over the torso."""
    def fn(cr, J):
        nx, ny = J["neck"]
        hx, hy = J["hip"]
        s = math.dist((nx, ny), (hx, hy)) / 118
        ang = math.atan2(hy - ny, hx - nx) - math.pi / 2
        with xform(cr, nx, ny, 1.0, ang):
            L = math.dist((nx, ny), (hx, hy))
            rrect(cr, -26 * s, 2, 52 * s, L + 6 * s, 10 * s, fill=c, stroke=INK, lw=3 * s)
            for i in range(1, 5):
                line(cr, -24 * s, i * L / 5, 24 * s, i * L / 5, 4 * s, WHITE, 0.8)
    return fn


def globe_sleepy(cr, x, y, r, T=0.0, cap=True):
    P.globe(cr, x, y, r, T * 0.5)
    for k in (-1, 1):
        arc(cr, x + k * r * 0.32, y - r * 0.1, r * 0.12, 0.2, math.pi - 0.2, max(3, r * 0.04), INK)
    ellipse(cr, x, y + r * 0.35, r * 0.12, r * 0.08 + r * 0.04 * math.sin(T * 2), fill=INK)
    if cap:
        tip = (x + r * 1.15, y - r * 0.55)
        polyline(cr, [(x - r * 0.75, y - r * 0.62), (x + r * 0.2, y - r * 1.55), tip, (x + r * 0.8, y - r * 0.55)],
                 5, INK, closed=True, fill=(0.35, 0.45, 0.85))
        rrect(cr, x - r * 0.82, y - r * 0.72, r * 1.68, r * 0.22, 10, fill=WHITE, stroke=INK, lw=5)
        circle(cr, tip[0], tip[1], r * 0.12, fill=WHITE, stroke=INK, w=5)
    zzz(cr, x + r * 0.9, y - r * 0.9, T, r / 160, c=WHITE)


def polaroid(cr, x, y, s=1.0, rot=0.0, inner=None, caption="", k=1.0, bg=(0.85, 0.92, 1.0)):
    """Photo with a white frame; inner(cr) draws in a 300x240 area centred at (0, -30)."""
    if k <= 0:
        return
    with xform(cr, x, y, max(0.01, k) * s, rot):
        rect(cr, -175, -190, 350, 380, fill=(0, 0, 0, 0.25))
        rect(cr, -180, -200, 360, 380, fill=WHITE, stroke=INK, lw=5)
        cr.save()
        cr.rectangle(-150, -170, 300, 260)
        cr.clip()
        fill_bg(cr, bg)
        if inner:
            inner(cr)
        cr.restore()
        cr.new_path()
        rect(cr, -150, -170, 300, 260, stroke=INK, lw=3)
        if caption:
            text(cr, caption, 0, 135, 34, face=FONT_HAND, bold=True)
        circle(cr, 0, -188, 12, fill=RED, stroke=INK, w=3)


def chalk(cr, s, x, y, size=56, a=1.0, c=WHITE, align="center"):
    text(cr, s, x, y, size, face=FONT_HAND, bold=True, c=c, a=a, align=align)


def ocean(cr, T, y, w0=-400, w1=W + 400, c=(0.15, 0.35, 0.60), c2=(0.05, 0.15, 0.30), night=False):
    if night:
        c, c2 = (0.08, 0.16, 0.30), (0.02, 0.05, 0.12)
    vgrad(cr, c, c2, w0, y, w1, H + 400)
    for j in range(3):
        pts = [(x, y + j * 40 + 6 * math.sin(x * 0.02 + T * 2 + j)) for x in range(int(w0), int(w1) + 1, 20)]
        polyline(cr, pts, 3, WHITE, 0.25 - j * 0.06)


# ---------------------------------------------------------------- custom constellations
SHAPES = {
    "eye": [[(-1, 0), (-0.5, -0.45), (0.5, -0.45), (1, 0), (0.5, 0.45), (-0.5, 0.45), (-1, 0)],
            [(0, -0.25), (0.25, 0), (0, 0.25), (-0.25, 0), (0, -0.25)]],
    "cloud": [[(-0.9, 0.3), (-0.95, -0.1), (-0.6, -0.3), (-0.35, -0.65), (0.1, -0.7), (0.4, -0.4), (0.8, -0.35),
               (0.95, 0.05), (0.8, 0.3), (-0.9, 0.3)]],
    "z": [[(-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6)]],
    "sun": [[(0, -0.45), (0.32, -0.32), (0.45, 0), (0.32, 0.32), (0, 0.45), (-0.32, 0.32), (-0.45, 0), (-0.32, -0.32),
             (0, -0.45)], [(0, -0.65), (0, -1)], [(0.65, 0), (1, 0)], [(0, 0.65), (0, 1)], [(-0.65, 0), (-1, 0)]],
    "bed": [[(-1, -0.5), (-1, 0.5)], [(-1, 0.1), (1, 0.1), (1, 0.5)], [(-0.75, -0.1), (-0.5, -0.1)],
            [(-0.35, -0.1), (0.9, -0.1), (0.9, 0.1)]],
    "hero": [[(0, -0.9), (0.22, -0.68), (0, -0.46), (-0.22, -0.68), (0, -0.9)], [(-0.05, -0.9), (-0.15, -1.1)],
             [(0, -0.46), (0, 0.25)], [(-0.45, -0.05), (0, -0.25), (0.45, -0.05)], [(-0.35, 0.95), (0, 0.25), (0.35, 0.95)]],
    "two": [[(-0.55, -0.85), (-0.35, -0.65), (-0.55, -0.45), (-0.75, -0.65), (-0.55, -0.85)], [(-0.55, -0.45), (-0.55, 0.2)],
            [(-0.85, 0.9), (-0.55, 0.2), (-0.25, 0.9)], [(-0.55, -0.25), (0.55, -0.25)],
            [(0.55, -0.85), (0.75, -0.65), (0.55, -0.45), (0.35, -0.65), (0.55, -0.85)], [(0.55, -0.45), (0.55, 0.2)],
            [(0.25, 0.9), (0.55, 0.2), (0.85, 0.9)]],
    "pie": [[(0, -1), (0.71, -0.71), (1, 0), (0.71, 0.71), (0, 1), (-0.71, 0.71), (-1, 0), (-0.71, -0.71), (0, -1)],
            [(0, -1), (0, 0), (0.87, 0.5)]],
}


def constellation2(cr, shape, cx, cy, size, k, T, c=(0.92, 0.94, 1.0), a=1.0, label=None, label_size=34):
    """Like kit.constellation, but for the custom SHAPES above (or kit's own names)."""
    if shape not in SHAPES:
        K.constellation(cr, shape, cx, cy, size, k, T, c=c, a=a, label=label)
        return
    segs = [[(cx + px * size, cy + py * size) for (px, py) in sg] for sg in SHAPES[shape]]
    total = sum(max(0, len(sg) - 1) for sg in segs)
    done = k * total
    for sg in segs:
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
        text(cr, label, cx, cy + size + 50, label_size, face=FONT_BOLD, c=c, a=a * clamp((k - 0.6) * 3))


# ---------------------------------------------------------------- the 24-hour day ring
def day_ring(cr, cx, cy, r, T, k_bonus=0.0, k_in=1.0, dark=True, labels=True, center=None, center_c=None,
             center_size=64, sleep_from=23, sleep_hours=8):
    """24 segments (midnight at the top). Sleep hours are navy; k_bonus turns them bright one by one."""
    ink = NI if dark else INK
    width = r * 0.30
    for i in range(24):
        kk = clamp(k_in * 24 - i)
        if kk <= 0:
            continue
        a0 = -math.pi / 2 + i / 24 * TAU + 0.012
        a1 = a0 + TAU / 24 * kk - 0.024
        hour = i
        asleep = ((hour - sleep_from) % 24) < sleep_hours
        if asleep:
            idx = (hour - sleep_from) % 24
            kb = clamp(k_bonus * sleep_hours - idx)
            col = lerpc(SLEEP_BLUE, BONUS, kb)
            if kb > 0:
                mid = (a0 + a1) / 2
                glow(cr, cx + math.cos(mid) * r, cy + math.sin(mid) * r, width * 1.4, BONUS, 0.35 * kb)
        else:
            col = (1.0, 0.82, 0.35)
        cr.new_path()
        cr.arc(cx, cy, r + width / 2, a0, a1)
        cr.arc_negative(cx, cy, r - width / 2, a1, a0)
        cr.close_path()
        src(cr, col)
        cr.fill_preserve()
        src(cr, INK)
        cr.set_line_width(3)
        cr.stroke()
    if labels and k_in >= 1:
        for lab, ang in (("MIDNIGHT", -math.pi / 2), ("6 AM", 0), ("NOON", math.pi / 2), ("6 PM", math.pi)):
            rr = r + width / 2 + 46
            rr2 = rr + (34 if lab in ("6 AM", "6 PM") else 0)
            text(cr, lab, cx + math.cos(ang) * rr2, cy + math.sin(ang) * rr, 30, face=FONT_BOLD, c=ink)
    if center:
        text(cr, center, cx, cy, center_size, face=FONT_TITLE, c=center_c or ink)
