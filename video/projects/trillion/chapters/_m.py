"""Shared bits for the Trillion video: title card, characters, money props and big-ticket purchases."""
import math

from video.chapters.common import Builder, head_at  # noqa: F401
from video.engine.core import *  # noqa: F401,F403
from video.engine.core import text_w, font, rrect_path, star_shape, bezier_pts, curve_arrow, src  # noqa: F401
from video.engine import stickman as sm, props as P, props2 as P2, sets as S, kit as K  # noqa: F401

HERO = ("tuft",)
SAM = ("cap",)
MIA = ("ponytail",)
GOLD = P2.GOLD
GOLD_D = P2.GOLD_D
CASH = (0.62, 0.82, 0.55)
CASH_D = (0.16, 0.40, 0.20)
CASH_L = (0.86, 0.95, 0.82)
MONEY_G = (0.40, 0.90, 0.42)
WATER = (0.40, 0.72, 0.92)
WATER_D = (0.22, 0.50, 0.75)
NIGHT_INK = (0.88, 0.88, 0.93)
NIGHT_FILL = (0.10, 0.10, 0.14)

MONEY_SYMBOLS = ["$", "YACHTS", "JETS", "ISLANDS", "1,000,000,000,000", "MANSIONS", "$$$", "BILLIONS", "GOLD",
                 "POWER", "ROCKETS", "INTEREST", "$", "CASTLES"]
TITLE = K.title_card("WHAT IF YOU HAD", "$1 TRILLION?", color=MONEY_G, edge=(0.03, 0.22, 0.06), symbols=MONEY_SYMBOLS,
                     big_size=260)


def money_str(nz):
    """'$1' followed by nz zeros, grouped with commas."""
    return "${:,}".format(int("1" + "0" * nz))


# ---------------------------------------------------------------- characters
def dude(cr, T, x, ground_y, g="stand", face=1, s=1.0, acc=HERO, seed=0, ink=INK, fill=WHITE, walk=0.0, talk=None,
         alpha=1.0, y=None, under=None, over=None, **kw):
    """Like K.person, but with hooks: under(cr, J, p) draws before the figure (jerseys), over(cr, J, p) after (hats)."""
    p = sm.pose(g, x=x, face=face, s=s, **kw)
    if walk:
        p = sm.walk(p, T + seed, walk)
    else:
        p = sm.idle(p, T, seed)
    if talk is not None:
        p = sm.talk(p, T, talk)
    if y is not None:
        p["y"] = y
    else:
        p = sm.on_ground(p, ground_y)
    J = sm.joints(p)
    with group(cr, alpha):
        if under:
            under(cr, J, p)
        sm.draw(cr, p, ink=ink, fill=fill, acc=acc)
        if over:
            over(cr, J, p)
    return J


def hrot(J, dx, dy):
    hc, ang = J["head"], J["ha"]
    c, s_ = math.cos(ang), math.sin(ang)
    return hc[0] + dx * c - dy * s_, hc[1] + dx * s_ + dy * c


def eye_pts(J, p):
    s, f, fo = p["s"], p["face"], p.get("fo", 1.0)
    off = 11 * fo * f
    sep = 9.5 * s * (1 - 0.18 * fo)
    ey = (-4 + p["gy"] * 3.5) * s
    return [hrot(J, off * s + k * sep, ey) for k in (-1, 1)]


def shades(cr, J, p, c=INK):
    s = p["s"]
    (x1, y1), (x2, y2) = eye_pts(J, p)
    for (x, y) in ((x1, y1), (x2, y2)):
        ellipse(cr, x, y, 10 * s, 7.5 * s, fill=c, rot=J["ha"])
    line(cr, x1, y1, x2, y2, 3 * s, c)


def dollar_eyes(cr, J, p, k=1.0, c=(0.10, 0.55, 0.20), fill=WHITE):
    if k <= 0:
        return
    s = p["s"]
    for (x, y) in eye_pts(J, p):
        circle(cr, x, y, 10 * s, fill=fill)
        text(cr, "$", x, y, 24 * s * k, c=c, face=FONT_TITLE)


def party_hat(cr, J, p, c=RED):
    s = p["s"]
    a = hrot(J, -16 * s, -34 * s)
    b = hrot(J, 16 * s, -34 * s)
    tip = hrot(J, 4 * s, -86 * s)
    polyline(cr, [a, tip, b], 3 * s, INK, closed=True, fill=c)
    circle(cr, tip[0], tip[1], 6 * s, fill=YELLOW, stroke=INK, w=2 * s)


def jersey(c=RED, num=None):
    def under(cr, J, p):
        s = p["s"]
        nx, ny = J["neck"]
        hx, hy = J["hip"]
        pts = [(nx - 30 * s, ny + 6 * s), (nx + 30 * s, ny + 6 * s), (hx + 24 * s, hy + 6 * s), (hx - 24 * s, hy + 6 * s)]
        polyline(cr, pts, 3 * s, INK, closed=True, fill=c)
        if num is not None:
            text(cr, str(num), (nx + hx) / 2, (ny + hy) / 2 + 6 * s, 30 * s, c=WHITE, face=FONT_TITLE)
    return under


def crowd(cr, T, n=20, y0=900, y1=1060, seed=3, cheer=0.0, ink=GRAY, s0=0.5, s1=0.75, x0=-100, x1=2020, fill=WHITE):
    r = rng(seed)
    people = []
    for i in range(n):
        people.append((r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(s0, s1),
                       r.choice([(), ("cap",), ("ponytail",), ("glasses",), ("bun",), ("hat",)]), r.uniform(0, 6)))
    people.sort(key=lambda q: q[1])
    for i, (x, y, s, acc, ph) in enumerate(people):
        g = "cheer" if cheer > 0.5 and (i % 3 != 1 or cheer > 0.8) else "stand"
        p = sm.pose(g, x=x, s=s, face=1 if x < CX else -1, smile=0.4 + 0.5 * cheer)
        if g == "cheer":
            p = sm.apply(p, a1f=150 + 15 * math.sin(T * 8 + ph), a1b=-150 + 15 * math.sin(T * 8 + ph + 1))
        p = sm.on_ground(sm.idle(p, T, int(ph * 10)), y)
        if cheer > 0.5:
            p["y"] -= abs(math.sin(T * 6 + ph)) * 18 * s
        sm.draw(cr, p, ink=ink, fill=fill, acc=acc)


# ---------------------------------------------------------------- money
def bill(cr, x, y, s=1.0, rot=0.0, a=1.0, flip=1.0, val="100"):
    """A banknote, 240x110 at s=1, centred."""
    with xform(cr, x, y, rot=rot, sx=s, sy=s * flip):
        rrect(cr, -120, -55, 240, 110, 8, fill=CASH, stroke=CASH_D, lw=4, a=a)
        rrect(cr, -106, -42, 212, 84, 6, stroke=CASH_D, lw=2, a=a * 0.7)
        ellipse(cr, 0, 0, 30, 36, fill=CASH_L, stroke=CASH_D, w=2.5, a=a)
        circle(cr, 0, -6, 11, stroke=CASH_D, w=2.5, a=a)
        line(cr, 0, 5, 0, 28, 2.5, CASH_D, a)
        if val:
            text(cr, val, -76, -22, 22, c=CASH_D, face=FONT_TITLE, a=a)
            text(cr, val, 76, 22, 22, c=CASH_D, face=FONT_TITLE, a=a)
        text(cr, "$", 76, -20, 26, c=CASH_D, face=FONT_TITLE, a=a)
        text(cr, "$", -76, 20, 26, c=CASH_D, face=FONT_TITLE, a=a)


def brick(cr, x, y, s=1.0, c=CASH):
    """A strapped bundle of notes in 3/4 view, base centre at (x, y)."""
    with xform(cr, x, y, s):
        top = [(-100, -60), (100, -60), (130, -84), (-70, -84)]
        polyline(cr, top, 4, CASH_D, closed=True, fill=lerpc(c, WHITE, 0.25))
        polyline(cr, [(100, -60), (130, -84), (130, -24), (100, 0)], 4, CASH_D, closed=True, fill=lerpc(c, INK, 0.15))
        rect(cr, -100, -60, 200, 60, fill=c, stroke=CASH_D, lw=4)
        for i in range(1, 6):
            line(cr, -96, -60 + i * 10, 96, -60 + i * 10, 1.5, CASH_D, 0.5)
        rect(cr, -20, -60, 40, 60, fill=(0.97, 0.93, 0.80), stroke=CASH_D, lw=2)
        polyline(cr, [(-20, -60), (20, -60), (50, -84), (10, -84)], 2, CASH_D, closed=True, fill=(0.97, 0.93, 0.80))
        text(cr, "$", 0, -30, 30, c=CASH_D, face=FONT_TITLE)


def cash_pile(cr, x, y, s=1.0, rows=5, seed=1):
    """Pyramid of cash bricks with its base on y."""
    g = rng(seed)
    with xform(cr, x, y, s):
        for r in range(rows):
            n = rows - r
            for c in range(n):
                brick(cr, (c - (n - 1) / 2) * 205 + g.uniform(-8, 8) + r * 12, -r * 58, 1.0)


def money_rain(cr, T, n=30, seed=1, x0=-100, x1=W + 100, y0=-160, y1=H + 160, speed=240, s=0.45, a=1.0):
    r = rng(seed)
    for i in range(n):
        bx = r.uniform(x0, x1)
        off = r.uniform(0, y1 - y0)
        sp = r.uniform(0.7, 1.3)
        ph = r.uniform(0, 6.3)
        y = y0 + (T * speed * sp + off) % (y1 - y0)
        x = bx + 50 * math.sin(T * 1.7 + ph)
        bill(cr, x, y, s * r.uniform(0.8, 1.15), 0.5 * math.sin(T * 2.3 + ph), a=a, flip=math.cos(T * 3.1 + ph),
             val="100")


def coin_rain(cr, T, n=20, seed=2, x0=0, x1=W, speed=420, r0=18, r1=30, a=1.0):
    g = rng(seed)
    for i in range(n):
        x = g.uniform(x0, x1)
        off = g.uniform(0, H + 200)
        y = -100 + (T * speed * g.uniform(0.8, 1.2) + off) % (H + 200)
        P2.coin(cr, x, y, g.uniform(r0, r1), a=a, rot=T * 5 + i)


def money_bag(cr, x, y, s=1.0, label="$", c=(0.80, 0.68, 0.45)):
    """Sack of money, base at (x, y)."""
    with xform(cr, x, y, s):
        pts = bezier_pts([(-30, -150), (-150, -120), (-140, 0), (0, 4), (140, 0), (150, -120), (30, -150)], 30)
        polyline(cr, pts, 5, INK, closed=True, fill=c)
        polyline(cr, [(-30, -150), (-55, -190), (0, -175), (55, -190), (30, -150)], 5, INK, closed=True, fill=c)
        line(cr, -38, -152, 38, -152, 9, INK)
        text(cr, label, 0, -65, 90 if len(label) < 2 else 60, c=CASH_D, face=FONT_TITLE)


# ---------------------------------------------------------------- phone & bank app
def big_phone(cr, x, y, s=1.0, rot=0.0, screen=None, bg=WHITE):
    """Large phone, 380x760 at s=1, centred. screen(cr) draws in a clipped area x -172..172, y -350..350."""
    with xform(cr, x, y, s, rot):
        rrect(cr, -190, -380, 380, 760, 54, fill=INK)
        rect(cr, 186, -230, 10, 90, fill=INK)
        rrect(cr, -172, -352, 344, 704, 34, fill=bg)
        if screen:
            cr.save()
            rrect_path(cr, -172, -352, 344, 704, 34)
            cr.clip()
            screen(cr)
            cr.restore()
            cr.new_path()
        rrect(cr, -55, -364, 110, 22, 11, fill=INK)


def fit_size(cr, s, maxw, size, face=FONT_TITLE):
    w_ = text_w(cr, s, face, size)
    return size if w_ <= maxw else size * maxw / w_


def bank_screen(amount, hello="Good morning!", k_glow=0.0, sub="Available balance", bar=None):
    """Screen content for big_phone: a friendly banking app showing `amount`."""
    def scr(cr):
        fill_bg(cr, (0.96, 0.97, 0.96))
        rect(cr, -172, -352, 344, 130, fill=CASH_D)
        circle(cr, -120, -268, 22, fill=GOLD, stroke=WHITE, w=3)
        text(cr, "$", -120, -268, 26, c=CASH_D, face=FONT_TITLE)
        text(cr, "MY BANK", -86, -268, 34, c=WHITE, face=FONT_TITLE, align="left")
        text(cr, hello, 0, -180, 32, face=FONT_HAND, bold=True, c=GRAY)
        rrect(cr, -150, -130, 300, 190, 18, fill=WHITE, stroke=LIGHT, lw=3)
        text(cr, sub, 0, -95, 24, face=FONT_BOLD, c=MID)
        if k_glow > 0:
            glow(cr, 0, -20, 200, MONEY_G, 0.5 * k_glow)
        sz = fit_size(cr, amount, 280, 64)
        text(cr, amount, 0, -25, sz, c=CASH_D, face=FONT_TITLE)
        if bar is not None:
            rrect(cr, -130, 20, 260, 18, 9, fill=LIGHT)
            rrect(cr, -130, 20, 260 * clamp(bar), 18, 9, fill=GREEN)
        for i, (lab, c) in enumerate((("SEND", BLUE), ("PAY", GREEN), ("SAVE", ORANGE))):
            xx = -110 + i * 110
            circle(cr, xx, 130, 34, fill=c)
            text(cr, lab, xx, 190, 22, face=FONT_BOLD, c=GRAY)
        for i in range(3):
            rrect(cr, -150, 240 + i * 34, 300, 24, 8, fill=(0.90, 0.91, 0.90))
    return scr


def notif(cr, x, y, w, title, body, c=GREEN, s=1.0, a=1.0):
    """A phone notification card centred at (x, y)."""
    with xform(cr, x, y, s):
        rrect(cr, -w / 2, -48, w, 96, 20, fill=WHITE, stroke=LIGHT, lw=3, a=a)
        circle(cr, -w / 2 + 44, 0, 26, fill=c, a=a)
        text(cr, title, -w / 2 + 84, -16, 26, face=FONT_BOLD, align="left", a=a)
        text(cr, body, -w / 2 + 84, 18, 24, face=FONT_HAND, bold=True, c=GRAY, align="left", a=a)


# ---------------------------------------------------------------- big-ticket purchases
def mansion(cr, x, y, s=1.0, wall=(0.97, 0.93, 0.84), roof=(0.55, 0.26, 0.22), lit=0.0):
    """Base at ground, ~620 wide, ~400 tall at s=1."""
    win = lerpc((0.75, 0.86, 0.98), (1.0, 0.86, 0.45), lit)
    with xform(cr, x, y, s):
        for sx_ in (-1, 1):
            rect(cr, sx_ * 210 - 100, -220, 200, 220, fill=wall, stroke=INK, lw=5)
            polyline(cr, [(sx_ * 210 - 115, -220), (sx_ * 210, -290), (sx_ * 210 + 115, -220)], 5, INK, closed=True,
                     fill=roof)
            for i in range(2):
                for j in range(2):
                    rect(cr, sx_ * 210 - 70 + i * 90, -190 + j * 95, 50, 60, fill=win, stroke=INK, lw=4)
        rect(cr, -110, -300, 220, 300, fill=wall, stroke=INK, lw=5)
        polyline(cr, [(-140, -300), (0, -400), (140, -300)], 5, INK, closed=True, fill=roof)
        circle(cr, 0, -335, 18, fill=win, stroke=INK, w=4)
        for i in range(4):
            rect(cr, -96 + i * 58, -250, 18, 250, fill=WHITE, stroke=INK, lw=3)
        rrect(cr, -28, -120, 56, 120, 26, fill=(0.50, 0.32, 0.20), stroke=INK, lw=4)
        rect(cr, -130, -14, 260, 14, fill=LIGHT, stroke=INK, lw=3)


def palm(cr, x, y, s=1.0, t=0.0):
    """Palm tree, base at (x, y)."""
    with xform(cr, x, y, s):
        pts = bezier_pts([(0, 0), (35, -150), (10, -300)], 16)
        polyline(cr, pts, 22, INK)
        polyline(cr, pts, 14, (0.62, 0.45, 0.25))
        for i in range(1, 8):
            px, py = pts[i * 2]
            line(cr, px - 8, py, px + 8, py - 4, 3, (0.40, 0.28, 0.15))
        tx, ty = pts[-1]
        for k, ang in enumerate((-2.7, -2.1, -1.4, -0.7, -0.15)):
            a = ang + 0.06 * math.sin(t * 2 + k)
            ln = 170
            ex, ey = tx + math.cos(a) * ln, ty + math.sin(a) * ln * 0.75 + 60
            mx, my = tx + math.cos(a) * ln * 0.5, ty + math.sin(a) * ln * 0.5 - 30
            top = bezier_pts([(tx, ty), (mx, my - 26), (ex, ey)], 12)
            bot = bezier_pts([(ex, ey), (mx, my + 16), (tx, ty)], 12)
            polyline(cr, top + bot, 4, INK, closed=True, fill=(0.30, 0.68, 0.32))
        for dx in (-14, 8):
            circle(cr, tx + dx, ty + 12, 13, fill=(0.45, 0.30, 0.15), stroke=INK, w=3)


def island(cr, x, y, s=1.0, t=0.0, sand=(0.96, 0.86, 0.60)):
    """Tropical island; y = waterline."""
    with xform(cr, x, y, s):
        pts = bezier_pts([(-280, 12), (-180, -95), (180, -95), (280, 12)], 30)
        polyline(cr, pts, 5, INK, closed=True, fill=sand)
        palm(cr, -50, -70, 1.0, t)
        palm(cr, 90, -60, 0.7, t + 1)


def waves(cr, T, y, x0=-400, x1=W + 400, c=WATER, top=None, h=600, a=1.0):
    """Sea surface with little wave arcs, from y downward."""
    rect(cr, x0, y, x1 - x0, h, fill=c, a=a)
    line(cr, x0, y, x1, y, 4, WATER_D, a)
    g = rng(5)
    for i in range(40):
        wx = x0 + ((i * 97 + T * 30 * (1 + i % 3)) % (x1 - x0))
        wy = y + 30 + (i * 53) % 260
        arc(cr, wx, wy, 18, math.pi * 1.15, math.pi * 1.85, 3, WHITE, 0.55 * a)
    del g


def yacht(cr, x, y, s=1.0, t=0.0, mini=0.0, hull=WHITE, stripe=(0.12, 0.22, 0.42)):
    """Superyacht facing right; y = waterline; ~760 wide at s=1. mini 0..1 opens the stern garage and launches
    a smaller yacht."""
    with xform(cr, x, y, s):
        bob = 4 * math.sin(t * 2)
        with xform(cr, 0, bob):
            if mini > 0:
                k = ease(clamp(mini * 1.3))
                mx = lerp(-300, -620, ease(clamp(mini * 1.6 - 0.4)))
                if k > 0.05:
                    yacht(cr, mx, -6 - bob, 0.26, t + 2, 0.0, hull, stripe)
            polyline(cr, [(-370, -100), (400, -110), (320, 12), (-345, 12)], 5, INK, closed=True, fill=hull)
            line(cr, -362, -62, 376, -72, 9, stripe)
            for i in range(9):
                circle(cr, -250 + i * 62, -36, 9, fill=(0.75, 0.86, 0.98), stroke=INK, w=3)
            polyline(cr, [(-290, -100), (230, -100), (180, -175), (-280, -175)], 5, INK, closed=True, fill=hull)
            for i in range(7):
                rrect(cr, -255 + i * 62, -160, 46, 36, 6, fill=(0.20, 0.28, 0.40), stroke=INK, lw=3)
            polyline(cr, [(-210, -175), (120, -175), (80, -235), (-200, -235)], 5, INK, closed=True, fill=hull)
            rrect(cr, -170, -222, 230, 30, 8, fill=(0.20, 0.28, 0.40), stroke=INK, lw=3)
            line(cr, -60, -235, -60, -300, 5, INK)
            line(cr, -95, -285, -25, -285, 5, INK)
            circle(cr, -60, -305, 8, fill=WHITE, stroke=INK, w=3)
            # stern garage
            o = ease(clamp(mini * 3))
            rect(cr, -360, -92, 80, 70, fill=(0.25, 0.25, 0.30) if o > 0 else hull, stroke=INK, lw=4)
            if o > 0:
                polyline(cr, [(-360, -22), (-280, -22), (-280 - 60 * o, -22 + 40 * o), (-360 - 60 * o, -22 + 40 * o)],
                         4, INK, closed=True, fill=hull)


def jet(cr, x, y, s=1.0, face=1, rot=0.0, body=WHITE, accent=GOLD):
    """Private jet in profile, centred, ~560 wide at s=1."""
    with xform(cr, x, y, rot=rot, sx=s * face, sy=s):
        polyline(cr, [(-60, 6), (60, 6), (-40, 96), (-100, 96)], 4, INK, closed=True, fill=lerpc(body, INK, 0.12))
        top = bezier_pts([(-260, -6), (-230, -46), (140, -46), (250, -30), (300, 4)], 30)
        bot = bezier_pts([(300, 4), (260, 40), (-200, 42), (-260, 8)], 30)
        polyline(cr, top + bot, 5, INK, closed=True, fill=body)
        polyline(cr, [(-200, -40), (-262, -140), (-215, -140), (-130, -42)], 5, INK, closed=True, fill=body)
        line(cr, -250, 0, 280, 0, 6, accent)
        rrect(cr, -205, -78, 100, 34, 17, fill=LIGHT, stroke=INK, lw=4)
        for i in range(6):
            circle(cr, -80 + i * 38, -16, 8, fill=(0.75, 0.86, 0.98), stroke=INK, w=2.5)
        polyline(cr, [(205, -34), (262, -22), (250, -8), (200, -14)], 3, INK, closed=True, fill=(0.20, 0.28, 0.40))
        polyline(cr, [(-60, 0), (60, 0), (-30, 70), (-80, 70)], 4, INK, closed=True, fill=body)


def rocket(cr, x, y, s=1.0, t=0.0, flame=1.0, body=WHITE, accent=RED):
    """Rocket, base (fin bottoms) at (x, y), ~340 tall at s=1."""
    with xform(cr, x, y, s):
        if flame > 0:
            fl = 1 + 0.15 * math.sin(t * 40) + 0.1 * math.sin(t * 23)
            polyline(cr, [(-26, -18), (26, -18), (0, (60 + 70 * flame) * fl)], 0, INK, closed=True, fill=ORANGE)
            polyline(cr, [(-14, -18), (14, -18), (0, (25 + 40 * flame) * fl)], 0, INK, closed=True, fill=YELLOW)
        rect(cr, -30, -42, 60, 26, fill=GRAY, stroke=INK, lw=4)
        for k in (-1, 1):
            polyline(cr, [(k * 50, -130), (k * 98, -30), (k * 98, 0), (k * 50, -44)], 4, INK, closed=True, fill=accent)
        body_pts = ([(-50, -42), (-52, -200)] + bezier_pts([(-52, -200), (-50, -290), (0, -345)], 12) +
                    bezier_pts([(0, -345), (50, -290), (52, -200)], 12) + [(50, -42)])
        polyline(cr, body_pts, 5, INK, closed=True, fill=body)
        cr.save()
        cr.move_to(*body_pts[0])
        for p_ in body_pts[1:]:
            cr.line_to(*p_)
        cr.close_path()
        cr.clip()
        rect(cr, -70, -360, 140, 105, fill=accent)
        cr.restore()
        cr.new_path()
        polyline(cr, body_pts, 5, INK, closed=True)
        circle(cr, 0, -190, 24, fill=(0.75, 0.86, 0.98), stroke=INK, w=5)
        line(cr, 0, -42, 0, -120, 4, INK, 0.3)


def hospital(cr, x, y, s=1.0, sign="HOSPITAL", wall=(0.95, 0.96, 0.98), lit=0.0, sign_size=30):
    """Base at ground, 440x320 at s=1."""
    win = lerpc((0.75, 0.86, 0.98), (1.0, 0.86, 0.45), lit)
    with xform(cr, x, y, s):
        rect(cr, -220, -300, 440, 300, fill=wall, stroke=INK, lw=5)
        rect(cr, -230, -318, 460, 22, fill=LIGHT, stroke=INK, lw=4)
        rect(cr, -40, -390, 80, 76, fill=WHITE, stroke=INK, lw=4)
        rect(cr, -10, -380, 20, 56, fill=RED)
        rect(cr, -28, -362, 56, 20, fill=RED)
        for r in range(2):
            for c in range(6):
                if c in (2, 3) and r == 1:
                    continue
                rect(cr, -195 + c * 66, -270 + r * 100, 46, 60, fill=win, stroke=INK, lw=3)
        rect(cr, -50, -100, 100, 100, fill=(0.65, 0.85, 0.95), stroke=INK, lw=4)
        line(cr, 0, -100, 0, 0, 3, INK)
        rrect(cr, -110, -150, 220, 42, 8, fill=WHITE, stroke=INK, lw=3)
        text(cr, sign, 0, -129, fit_size(cr, sign, 200, sign_size, FONT_BOLD), face=FONT_BOLD, c=RED)


def school(cr, x, y, s=1.0, sign="SCHOOL", wall=(0.88, 0.55, 0.42), lit=0.0):
    """Base at ground, ~460x380 at s=1."""
    win = lerpc((0.75, 0.86, 0.98), (1.0, 0.86, 0.45), lit)
    with xform(cr, x, y, s):
        rect(cr, -220, -220, 440, 220, fill=wall, stroke=INK, lw=5)
        polyline(cr, [(-240, -220), (0, -320), (240, -220)], 5, INK, closed=True, fill=(0.95, 0.90, 0.80))
        rect(cr, -36, -380, 72, 80, fill=(0.95, 0.90, 0.80), stroke=INK, lw=4)
        polyline(cr, [(-46, -380), (0, -420), (46, -380)], 4, INK, closed=True, fill=RED)
        arc(cr, 0, -330, 16, math.pi, TAU, 5, GOLD_D)
        line(cr, 0, -420, 0, -470, 4, INK)
        polyline(cr, [(0, -470), (44, -458), (0, -446)], 3, INK, closed=True, fill=BLUE)
        for c in range(4):
            if c in (1, 2):
                continue
            for r in range(2):
                rect(cr, -190 + c * 105, -190 + r * 85, 64, 56, fill=win, stroke=INK, lw=3)
        rect(cr, -40, -110, 80, 110, fill=(0.50, 0.32, 0.20), stroke=INK, lw=4)
        text(cr, sign, 0, -262, fit_size(cr, sign, 240, 30, FONT_BOLD), face=FONT_BOLD)


def library(cr, x, y, s=1.0, sign="LIBRARY", wall=(0.93, 0.90, 0.82), lit=0.0):
    """Classical library, base at ground, ~480x360 at s=1."""
    win = lerpc((0.30, 0.25, 0.20), (1.0, 0.86, 0.45), lit)
    with xform(cr, x, y, s):
        rect(cr, -240, -28, 480, 28, fill=wall, stroke=INK, lw=4)
        rect(cr, -215, -50, 430, 22, fill=wall, stroke=INK, lw=4)
        rect(cr, -200, -250, 400, 200, fill=lerpc(wall, INK, 0.08), stroke=INK, lw=4)
        rect(cr, -45, -170, 90, 120, fill=win, stroke=INK, lw=4)
        for i in range(6):
            cx_ = -175 + i * 70
            if abs(cx_) < 40:
                continue
            rect(cr, cx_ - 14, -250, 28, 200, fill=wall, stroke=INK, lw=3)
        rect(cr, -225, -290, 450, 40, fill=wall, stroke=INK, lw=4)
        polyline(cr, [(-235, -290), (0, -370), (235, -290)], 4, INK, closed=True, fill=wall)
        text(cr, sign, 0, -270, fit_size(cr, sign, 400, 28, FONT_TITLE), face=FONT_TITLE)
        for i, c in enumerate((RED, BLUE, GREEN)):
            rect(cr, -24 + i * 16, -340, 12, 34, fill=c, stroke=INK, lw=2)


def stadium_ball(cr, x, y, r=40, rot=0.0):
    """Football (soccer ball)."""
    circle(cr, x, y, r, fill=WHITE, stroke=INK, w=4)
    for i in range(5):
        a = rot + i * TAU / 5
        star_shape(cr, x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.22, points=5, inner=0.8,
                   fill=INK)
    star_shape(cr, x, y, r * 0.3, points=5, inner=0.8, rot=rot - TAU / 4, fill=INK)


def toilet(cr, x, y, s=1.0, c=GOLD, t=0.0):
    """Golden toilet, base at floor, faces right."""
    edge = GOLD_D if c == GOLD else INK
    with xform(cr, x, y, s):
        rrect(cr, -110, -280, 70, 170, 14, fill=c, stroke=edge, lw=5)
        polyline(cr, [(-60, -130), (90, -130), (80, -90), (30, -60), (20, 0), (-40, 0), (-50, -60)], 5, edge,
                 closed=True, fill=c)
        ellipse(cr, 15, -138, 82, 16, fill=lerpc(c, WHITE, 0.3), stroke=edge, w=5)
        line(cr, -96, -250, -60, -250, 6, edge)
        for i in range(3):
            ph = t * 2 + i * 2.1
            k = 0.5 + 0.5 * math.sin(ph)
            star_shape(cr, -150 + i * 120, -300 + (i % 2) * 120, 6 + 12 * k, points=4, inner=0.3, fill=WHITE)


def diamond(cr, x, y, r=40, c=(0.75, 0.93, 1.0)):
    pts = [(-r, -r * 0.3), (-r * 0.55, -r * 0.75), (r * 0.55, -r * 0.75), (r, -r * 0.3), (0, r)]
    polyline(cr, [(x + a, y + b) for a, b in pts], max(2, r * 0.08), INK, closed=True, fill=c)
    line(cr, x - r, y - r * 0.3, x + r, y - r * 0.3, max(1.5, r * 0.05), INK)
    for a, b in ((-r * 0.55, -r * 0.75), (r * 0.55, -r * 0.75)):
        line(cr, x + a, y + b, x + a * 0.4, y - r * 0.3, max(1.5, r * 0.05), INK)
    line(cr, x - r * 0.22, y - r * 0.3, x, y + r, max(1.5, r * 0.05), INK)
    line(cr, x + r * 0.22, y - r * 0.3, x, y + r, max(1.5, r * 0.05), INK)


def diamond_phone(cr, x, y, s=1.0, t=0.0):
    with xform(cr, x, y, s):
        rrect(cr, -100, -190, 200, 380, 34, fill=(0.85, 0.92, 1.0), stroke=INK, lw=6)
        for r in range(6):
            for c in range(3):
                diamond(cr, -55 + c * 55 + (r % 2) * 27 - 13, -140 + r * 56, 18)
        circle(cr, -55, -150, 18, fill=INK)
        for i in range(3):
            k = 0.5 + 0.5 * math.sin(t * 3 + i * 2)
            star_shape(cr, -90 + i * 90, -200 + i * 150, 6 + 14 * k, points=4, inner=0.3, fill=WHITE, stroke=None)


def face_pool(cr, x, y, s=1.0, t=0.0):
    """A swimming pool shaped like the hero's face (top view)."""
    with xform(cr, x, y, s):
        rrect(cr, -230, -250, 460, 470, 30, fill=(0.88, 0.82, 0.70), stroke=INK, lw=5)
        for i in range(-3, 4):
            line(cr, i * 60, -250, i * 60, 220, 2, (0.70, 0.62, 0.50))
        for c in ([(-6, -150), (-30, -215), (6, -238)], [(14, -150), (22, -200), (60, -210)]):
            polyline(cr, bezier_pts(c, 14), 34, WHITE)
            polyline(cr, bezier_pts(c, 14), 22, WATER)
        circle(cr, 0, -10, 150, fill=WATER, stroke=WHITE, w=12)
        circle(cr, 0, -10, 156, stroke=INK, w=3)
        for k in (-1, 1):
            ellipse(cr, k * 50, -40, 20, 30, fill=WATER_D)
        polyline(cr, bezier_pts([(-60, 40), (0, 90), (60, 40)], 14), 12, WATER_D)
        for i in range(5):
            a = t * 0.8 + i * 1.3
            arc(cr, -60 + i * 30, 10 + (i % 2) * 40, 14, a, a + 1.6, 3, WHITE, 0.7)
        sx_ = 60 * math.sin(t * 0.7)
        circle(cr, sx_, 100, 13, fill=WHITE, stroke=INK, w=3)
        line(cr, sx_ - 26, 100 + 8 * math.sin(t * 6), sx_ + 26, 100 - 8 * math.sin(t * 6), 4, INK)


def price_tag(cr, x, y, s=1.0, txt="$9.99", rot=0.0, c=(1.0, 0.95, 0.75), ink=INK, size=36, a=1.0):
    font(cr, FONT_BOLD, size)
    w_ = cr.text_extents(txt)[4] + 70
    h_ = size * 1.6
    with xform(cr, x, y, s, rot):
        pts = [(-w_ / 2 + 32, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2 + 32, h_ / 2), (-w_ / 2, 0)]
        polyline(cr, pts, 4, ink, a, closed=True, fill=c, fa=a)
        circle(cr, -w_ / 2 + 26, 0, 7, fill=WHITE, stroke=ink, w=3, a=a)
        text(cr, txt, 14, 0, size, c=ink, face=FONT_BOLD, a=a)
    return w_


def gold_card(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rrect(cr, -110, -70, 220, 140, 14, fill=GOLD, stroke=GOLD_D, lw=5)
        rrect(cr, -80, -30, 46, 36, 6, fill=(0.95, 0.90, 0.60), stroke=GOLD_D, lw=3)
        for i in range(4):
            rrect(cr, -80 + i * 44, 22, 36, 10, 4, fill=GOLD_D)
        text(cr, "VIP", 60, -40, 28, face=FONT_TITLE, c=GOLD_D)


def shopping_bag(cr, x, y, s=1.0, c=(0.90, 0.30, 0.45), label=None):
    """Base at bottom."""
    with xform(cr, x, y, s):
        arc(cr, 0, -100, 28, math.pi, TAU, 6, INK)
        polyline(cr, [(-55, -100), (55, -100), (62, 0), (-62, 0)], 4, INK, closed=True, fill=c)
        if label:
            text(cr, label, 0, -50, 26, face=FONT_TITLE, c=WHITE)


def cart(cr, x, y, s=1.0, items=0.0, t=0.0, seed=4):
    """Shopping cart, base at floor, faces right; items 0..1 fill."""
    g = rng(seed)
    with xform(cr, x, y, s):
        n = int(14 * items)
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CASH]
        for i in range(n):
            ix, iy = -100 + (i % 5) * 50 + g.uniform(-6, 6), -150 - (i // 5) * 42 + g.uniform(-6, 6)
            rrect(cr, ix - 24, iy - 30, 48, 60, 8, fill=cols[i % len(cols)], stroke=INK, lw=3)
        polyline(cr, [(-170, -170), (-140, -60), (110, -60), (140, -170)], 5, INK, closed=True, fill=WHITE, fa=0.35)
        for i in range(1, 6):
            xx = lerp(-160, 130, i / 6)
            line(cr, xx, -170, lerp(-140, 110, i / 6), -60, 2.5, INK)
        line(cr, -150, -120, 125, -120, 2.5, INK)
        polyline(cr, [(-140, -60), (-130, -30), (110, -30)], 5, INK)
        polyline(cr, [(140, -170), (175, -200), (205, -200)], 6, INK)
        for wx in (-110, 90):
            circle(cr, wx, -14, 14, fill=WHITE, stroke=INK, w=5)


def eiffel(cr, x, y, s=1.0, c=(0.55, 0.42, 0.30)):
    """Eiffel Tower silhouette in line art, base at ground, ~620 tall at s=1."""
    with xform(cr, x, y, s):
        left = bezier_pts([(-170, 0), (-60, -180), (-30, -420), (-8, -600)], 24)
        right = [(-a, b) for a, b in left]
        polyline(cr, left + right[::-1], 5, INK, closed=True, fill=c)
        cr.save()
        polyline(cr, left + right[::-1], 0, INK, closed=True)
        cr.move_to(*left[0])
        for p_ in left[1:] + right[::-1]:
            cr.line_to(*p_)
        cr.close_path()
        cr.clip()
        for i in range(24):
            yy = -i * 26
            line(cr, -200, yy, 200, yy - 26, 2, INK, 0.45)
            line(cr, 200, yy, -200, yy - 26, 2, INK, 0.45)
        cr.restore()
        cr.new_path()
        arc_pts = bezier_pts([(-110, 0), (0, -150), (110, 0)], 16)
        polyline(cr, arc_pts + [(110, 2), (-110, 2)], 4, INK, closed=True, fill=PAPER)
        for (yy, ww) in ((-180, 120), (-400, 60)):
            rect(cr, -ww, yy - 14, 2 * ww, 18, fill=c, stroke=INK, lw=4)
        line(cr, 0, -600, 0, -660, 5, INK)


def iss(cr, x, y, s=1.0, t=0.0):
    """International Space Station."""
    with xform(cr, x, y, s, 0.05 * math.sin(t * 0.5)):
        rect(cr, -230, -6, 460, 12, fill=LIGHT, stroke=INK, lw=3)
        for sx_ in (-1, 1):
            for k in (0, 1):
                px = sx_ * (120 + k * 70)
                for sy_ in (-1, 1):
                    rect(cr, px - 26, (8 if sy_ > 0 else -128), 52, 120, fill=(0.20, 0.35, 0.70), stroke=INK, lw=3)
                    for j in range(1, 4):
                        yy = (8 if sy_ > 0 else -128) + j * 30
                        line(cr, px - 26, yy, px + 26, yy, 1.5, (0.6, 0.7, 0.9))
        rrect(cr, -70, -22, 140, 44, 18, fill=WHITE, stroke=INK, lw=4)
        rrect(cr, -22, -60, 44, 120, 18, fill=WHITE, stroke=INK, lw=4)


def calendar(cr, x, y, s=1.0, top="DAY", big="1", c=RED, big_size=110):
    with xform(cr, x, y, s):
        rrect(cr, -120, -130, 240, 260, 16, fill=WHITE, stroke=INK, lw=5)
        cr.save()
        rrect_path(cr, -120, -130, 240, 260, 16)
        cr.clip()
        rect(cr, -120, -130, 240, 70, fill=c)
        cr.restore()
        cr.new_path()
        rrect(cr, -120, -130, 240, 260, 16, stroke=INK, lw=5)
        for k in (-1, 1):
            rrect(cr, k * 60 - 8, -150, 16, 40, 8, fill=GRAY, stroke=INK, lw=3)
        text(cr, top, 0, -95, fit_size(cr, top, 210, 34, FONT_TITLE), face=FONT_TITLE, c=WHITE)
        text(cr, big, 0, 30, fit_size(cr, big, 210, big_size, FONT_TITLE), face=FONT_TITLE)


def gravestone(cr, x, y, s=1.0, lines_=("R.I.P.",), c=(0.75, 0.76, 0.78)):
    with xform(cr, x, y, s):
        pts = [(-110, 0), (-110, -200)] + [(math.cos(a) * 110, -200 + math.sin(a) * 110)
                                           for a in [math.pi + i * math.pi / 16 for i in range(17)]] + [(110, 0)]
        polyline(cr, pts, 5, INK, closed=True, fill=c)
        for i, ln in enumerate(lines_):
            text(cr, ln, 0, -220 + i * 56, 44 if i == 0 else 36, face=FONT_TITLE, c=GRAY)
        for gx in (-120, -60, 50, 120):
            polyline(cr, [(gx - 14, 0), (gx - 4, -26), (gx, 0), (gx + 6, -22), (gx + 12, 0)], 3, (0.25, 0.55, 0.25))


def envelope(cr, x, y, s=1.0, rot=0.0, c=WHITE, seal=None):
    with xform(cr, x, y, s, rot):
        rect(cr, -80, -50, 160, 100, fill=c, stroke=INK, lw=4)
        polyline(cr, [(-80, -50), (0, 10), (80, -50)], 4, INK)
        if seal:
            circle(cr, 0, 8, 14, fill=seal, stroke=INK, w=3)


def briefcase(cr, x, y, s=1.0, c=(0.40, 0.25, 0.15)):
    with xform(cr, x, y, s):
        rrect(cr, -50, -22, 100, 16, 6, stroke=INK, lw=5)
        rrect(cr, -70, -8, 140, 90, 10, fill=c, stroke=INK, lw=5)
        rect(cr, -8, 10, 16, 14, fill=GOLD, stroke=INK, lw=2)


def calculator(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        rrect(cr, -45, -65, 90, 130, 10, fill=GRAY, stroke=INK, lw=4)
        rect(cr, -34, -54, 68, 30, fill=(0.75, 0.88, 0.70), stroke=INK, lw=2)
        for r in range(3):
            for c in range(3):
                rrect(cr, -32 + c * 24, -14 + r * 24, 18, 18, 4, fill=WHITE)


def money_printer(cr, x, y, s=1.0, t=0.0, run=1.0, sign=None):
    """Printing press, base at floor; notes fly out to the right while run > 0."""
    with xform(cr, x, y, s):
        rect(cr, -200, -300, 340, 300, fill=(0.62, 0.66, 0.72), stroke=INK, lw=6)
        rect(cr, -220, -330, 380, 40, fill=(0.50, 0.54, 0.60), stroke=INK, lw=5)
        for i, gx in enumerate((-120, -10)):
            rot = t * 6 * run * (1 if i else -1)
            P.gear(cr, gx, -180, 55, 10, rot, fill=(0.80, 0.82, 0.86))
        circle(cr, 90, -240, 26, fill=WHITE, stroke=INK, w=4)
        line(cr, 90, -240, 90 + 18 * math.cos(t * 3), -240 + 18 * math.sin(t * 3), 4, RED)
        rect(cr, 140, -110, 40, 50, fill=INK)
        if sign:
            text(cr, sign, -30, -310, 30, face=FONT_TITLE, c=WHITE)
        if run > 0:
            for i in range(6):
                f = (t * 1.6 * run + i / 6) % 1
                bill(cr, 180 + f * 380, -86 + 220 * f * f, 0.45, f * 2.5, a=1.0, flip=math.cos(f * 9 + i))


def big_note(cr, x, y, s=1.0, amount="100 000 000 000 000", words="ONE HUNDRED TRILLION DOLLARS", c=(0.80, 0.86, 0.62),
             rot=0.0):
    """A huge banknote (~900x400 at s=1)."""
    edge = (0.30, 0.38, 0.20)
    with xform(cr, x, y, s, rot):
        rrect(cr, -450, -200, 900, 400, 14, fill=c, stroke=edge, lw=6)
        rrect(cr, -425, -175, 850, 350, 10, stroke=edge, lw=3)
        text(cr, amount, -400, -120, 58, face=FONT_TITLE, c=edge, align="left")
        text(cr, words, 0, 120, 44, face=FONT_TITLE, c=edge)
        for i, (rx, ry, w_) in enumerate(((300, 30, 60), (290, -40, 44), (310, -95, 36))):
            ellipse(cr, rx, ry, w_, 28, fill=lerpc(c, edge, 0.35), stroke=edge, w=3)
        text(cr, "100", -330, 30, 80, face=FONT_TITLE, c=lerpc(c, edge, 0.4))


def stove(cr, x, y, s=1.0, t=0.0, fire=1.0):
    """Cast-iron stove with a fire window, base at floor."""
    with xform(cr, x, y, s):
        rect(cr, -24, -560, 48, 340, fill=(0.25, 0.25, 0.28), stroke=INK, lw=4)
        rrect(cr, -130, -230, 260, 210, 16, fill=(0.22, 0.22, 0.25), stroke=INK, lw=5)
        for k in (-1, 1):
            rect(cr, k * 100 - 10, -22, 20, 22, fill=INK)
        rrect(cr, -80, -180, 160, 110, 10, fill=(0.10, 0.08, 0.06), stroke=(0.5, 0.5, 0.5), lw=4)
        if fire > 0:
            glow(cr, 0, -120, 220, ORANGE, 0.45 * fire)
            for i in range(5):
                fx = -50 + i * 25
                hh = (40 + 25 * math.sin(t * 9 + i * 1.7)) * fire
                polyline(cr, [(fx - 14, -80), (fx, -80 - hh), (fx + 14, -80)], 0, INK, closed=True,
                         fill=YELLOW if i % 2 else ORANGE)


def tv(cr, x, y, s=1.0, screen=None, c=(0.30, 0.30, 0.34)):
    """Old-school TV centred; screen(cr) gets a clipped area x -150..150, y -100..100."""
    with xform(cr, x, y, s):
        line(cr, -20, -150, -70, -220, 4, INK)
        line(cr, 20, -150, 70, -220, 4, INK)
        rrect(cr, -200, -150, 400, 300, 30, fill=c, stroke=INK, lw=6)
        rrect(cr, -160, -110, 320, 220, 20, fill=(0.12, 0.14, 0.18))
        if screen:
            cr.save()
            rrect_path(cr, -160, -110, 320, 220, 20)
            cr.clip()
            screen(cr)
            cr.restore()
            cr.new_path()
        line(cr, -120, 150, -150, 200, 6, INK)
        line(cr, 120, 150, 150, 200, 6, INK)


def browser(cr, x, y, w=420, h=300, title="NEWS", content=None, s=1.0):
    with xform(cr, x, y, s):
        rrect(cr, -w / 2, -h / 2, w, h, 14, fill=WHITE, stroke=INK, lw=5)
        cr.save()
        rrect_path(cr, -w / 2, -h / 2, w, h, 14)
        cr.clip()
        rect(cr, -w / 2, -h / 2, w, 44, fill=LIGHT)
        cr.restore()
        cr.new_path()
        for i, c in enumerate((RED, YELLOW, GREEN)):
            circle(cr, -w / 2 + 26 + i * 24, -h / 2 + 22, 8, fill=c)
        rrect(cr, -w / 2 + 110, -h / 2 + 10, w - 130, 24, 12, fill=WHITE, stroke=MID, lw=2)
        text(cr, title, -w / 2 + 124, -h / 2 + 22, 18, face=FONT_BOLD, c=GRAY, align="left")
        line(cr, -w / 2, -h / 2 + 44, w / 2, -h / 2 + 44, 4, INK)
        if content:
            content(cr)


def chart_line(cr, x0, y0, w, h, fn, p=1.0, c=GREEN, lw=8, n=80, axes=True, ink=INK, fill=None):
    """Plot fn(u) for u in 0..1 (returns 0..1) inside a box whose bottom-left is (x0, y0)."""
    if axes:
        arrow(cr, x0, y0, x0, y0 - h - 40, 5, ink, head=20)
        arrow(cr, x0, y0, x0 + w + 40, y0, 5, ink, head=20)
    m = max(2, int(n * clamp(p)))
    pts = [(x0 + w * i / n, y0 - h * fn(i / n)) for i in range(m + 1)]
    if fill is not None and len(pts) > 1:
        polyline(cr, pts + [(pts[-1][0], y0), (x0, y0)], 0, ink, closed=True, fill=fill, fa=0.35)
    polyline(cr, pts, lw, c)
    return pts[-1]


def pizza(cr, x, y, s=1.0, rot=0.0, bites=0.0):
    with xform(cr, x, y, s, rot):
        pts = [(0, 110), (-70, -60), (70, -60)]
        polyline(cr, pts, 5, INK, closed=True, fill=(1.0, 0.82, 0.35))
        rrect(cr, -82, -86, 164, 34, 16, fill=(0.85, 0.55, 0.25), stroke=INK, lw=5)
        for (px, py) in ((-20, -20), (24, -10), (0, 40), (-30, 10) if bites < 0.5 else (10, 70)):
            circle(cr, px, py, 13, fill=(0.80, 0.18, 0.15), stroke=INK, w=3)


def cake(cr, x, y, s=1.0, t=0.0, candles=5):
    """Birthday cake, base at table."""
    with xform(cr, x, y, s):
        rrect(cr, -130, -100, 260, 100, 14, fill=(1.0, 0.80, 0.85), stroke=INK, lw=5)
        rrect(cr, -90, -180, 180, 80, 12, fill=(1.0, 0.92, 0.80), stroke=INK, lw=5)
        polyline(cr, [(-130, -70)] + [(-130 + i * 26, -70 + (12 if i % 2 else 0)) for i in range(11)], 4, (0.9, 0.4, 0.5))
        for i in range(candles):
            cx_ = -60 + i * 30
            rect(cr, cx_ - 5, -230, 10, 50, fill=[BLUE, YELLOW, GREEN, RED, PURPLE][i % 5], stroke=INK, lw=2)
            fl = 1 + 0.2 * math.sin(t * 13 + i)
            ellipse(cr, cx_, -244, 7, 13 * fl, fill=ORANGE)
            ellipse(cr, cx_, -242, 3.5, 7 * fl, fill=YELLOW)


def balloon(cr, x, y, s=1.0, c=RED, t=0.0, seed=0):
    bx = x + 8 * math.sin(t * 1.3 + seed)
    by = y + 6 * math.sin(t * 1.7 + seed)
    pts = bezier_pts([(bx, by + 60 * s), (bx - 30 * s, by + 120 * s), (bx + 20 * s, by + 180 * s), (bx, by + 240 * s)], 16)
    polyline(cr, pts, 2.5, INK)
    ellipse(cr, bx, by, 46 * s, 58 * s, fill=c, stroke=INK, w=4)
    ellipse(cr, bx - 16 * s, by - 22 * s, 9 * s, 14 * s, fill=WHITE, a=0.6)
    polyline(cr, [(bx - 8 * s, by + 66 * s), (bx + 8 * s, by + 66 * s), (bx, by + 56 * s)], 2, INK, closed=True, fill=c)


def firework(cr, x, y, t, c=YELLOW, n=18, r=180, seed=1, dur=1.6, w=6):
    """Firework burst; t = seconds since it exploded."""
    if t < 0 or t > dur:
        return
    g = rng(seed)
    k = eout(t / (dur * 0.6))
    fade = 1 - clamp((t - dur * 0.4) / (dur * 0.6))
    drop = 40 * (t / dur) ** 2
    for i in range(n):
        a = i / n * TAU + g.uniform(-0.1, 0.1)
        rr = r * k * g.uniform(0.85, 1.05)
        x2, y2 = x + math.cos(a) * rr, y + math.sin(a) * rr + drop
        x1, y1 = x + math.cos(a) * rr * 0.6, y + math.sin(a) * rr * 0.6 + drop * 0.6
        line(cr, x1, y1, x2, y2, w, c, fade)
        circle(cr, x2, y2, w * 0.9, fill=WHITE, a=fade)
    glow(cr, x, y, r * 1.2, c, 0.25 * fade)


def firework_shell(cr, x0, y0, x1, y1, k, c=YELLOW):
    """Rising shell trail, k 0..1."""
    if k <= 0 or k >= 1:
        return
    xx, yy = lerp(x0, x1, eout(k)), lerp(y0, y1, eout(k))
    line(cr, lerp(x0, x1, eout(max(0, k - 0.15))), lerp(y0, y1, eout(max(0, k - 0.15))), xx, yy, 4, c, 0.7)
    circle(cr, xx, yy, 6, fill=WHITE)


def dragon_parts(cr, J, p, t=0.0, c=(0.25, 0.62, 0.35)):
    """Dragon costume (wings, horns, tail) around a stickman; call as `under` then `horns` as over."""
    s = p["s"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    f = p["face"]
    flap = 0.08 * math.sin(t * 2.5)
    for k in (-1, 1):
        bx, by = nx - 6 * s * f, ny + 20 * s
        tip = (bx + k * 230 * s, by - 150 * s - 40 * s * flap * k)
        pts = [(bx, by), tip, (bx + k * 200 * s, by - 40 * s), (bx + k * 150 * s, by + 10 * s),
               (bx + k * 100 * s, by - 10 * s), (bx + k * 60 * s, by + 40 * s)]
        polyline(cr, pts, 4 * s, INK, closed=True, fill=c)
        line(cr, bx, by, tip[0], tip[1], 3 * s, INK)
    tail = bezier_pts([(hx, hy), (hx - 120 * s * f, hy + 60 * s), (hx - 220 * s * f, hy - 10 * s),
                       (hx - 260 * s * f, hy + 40 * s)], 20)
    polyline(cr, tail, 12 * s, INK)
    polyline(cr, tail, 7 * s, c)
    ex, ey = tail[-1]
    polyline(cr, [(ex - 18 * s, ey - 4 * s), (ex - 40 * s * f, ey + 20 * s), (ex + 6 * s, ey + 22 * s)], 3 * s, INK,
             closed=True, fill=c)


def horns(cr, J, p, c=(0.25, 0.62, 0.35)):
    s = p["s"]
    for k in (-1, 1):
        a = hrot(J, k * 18 * s, -32 * s)
        b = hrot(J, k * 34 * s, -66 * s)
        m = hrot(J, k * 6 * s, -36 * s)
        polyline(cr, [a, b, m], 3 * s, INK, closed=True, fill=(0.95, 0.90, 0.75))


def crane(cr, x, y, s=1.0, t=0.0, load=None):
    """Tower crane, base at ground."""
    with xform(cr, x, y, s):
        for k in (-1, 1):
            line(cr, k * 22, 0, k * 22, -520, 6, INK)
        for i in range(13):
            yy = -i * 40
            line(cr, -22, yy, 22, yy - 40, 3, INK)
            line(cr, 22, yy, -22, yy - 40, 3, INK)
        polyline(cr, [(-160, -520), (420, -520), (420, -500), (-160, -500)], 5, INK, closed=True, fill=YELLOW)
        rect(cr, -180, -500, 70, 50, fill=GRAY, stroke=INK, lw=4)
        rect(cr, 20, -560, 60, 40, fill=YELLOW, stroke=INK, lw=4)
        hx = 300 + 40 * math.sin(t * 0.8)
        hy = -260 + 30 * math.sin(t * 1.1)
        line(cr, hx, -500, hx, hy, 3, INK)
        polyline(cr, [(hx - 8, hy), (hx, hy + 18), (hx + 10, hy + 8)], 4, INK)
        if load:
            load(cr, hx, hy + 30)


def fuel_can(cr, x, y, s=1.0, label="MONEY", c=(0.25, 0.65, 0.30)):
    """Jerry can, base at (x, y)."""
    with xform(cr, x, y, s):
        polyline(cr, [(-110, 0), (-110, -230), (-60, -280), (110, -280), (110, 0)], 6, INK, closed=True, fill=c)
        rrect(cr, -70, -270, 90, 40, 12, stroke=INK, lw=6)
        rect(cr, 60, -320, 36, 44, fill=GRAY, stroke=INK, lw=4)
        polyline(cr, [(-90, -40), (90, -200)], 3, INK, 0.25)
        polyline(cr, [(-90, -200), (90, -40)], 3, INK, 0.25)
        circle(cr, 0, -120, 58, fill=WHITE, stroke=INK, w=4)
        text(cr, "$", 0, -120, 80, face=FONT_TITLE, c=CASH_D)
        text(cr, label, 0, 40, 42, face=FONT_TITLE)


def barricade(cr, x, y, s=1.0):
    with xform(cr, x, y, s):
        for k in (-1, 1):
            line(cr, k * 120, 0, k * 100, -110, 8, INK)
        rect(cr, -160, -120, 320, 50, fill=WHITE, stroke=INK, lw=5)
        cr.save()
        cr.rectangle(-160, -120, 320, 50)
        cr.clip()
        for i in range(-2, 10):
            polyline(cr, [(-160 + i * 50, -70), (-130 + i * 50, -120), (-105 + i * 50, -120), (-135 + i * 50, -70)], 0,
                     INK, closed=True, fill=RED)
        cr.restore()
        cr.new_path()
        rect(cr, -160, -120, 320, 50, stroke=INK, lw=5)


def truck(cr, x, y, s=1.0, c=WHITE, label="FOOD", face=1, t=0.0, roll=0.0):
    """Delivery truck, base at ground."""
    with xform(cr, x, y, sx=s * face, sy=s):
        rect(cr, -230, -230, 300, 190, fill=c, stroke=INK, lw=5)
        polyline(cr, [(70, -40), (70, -180), (150, -180), (200, -110), (200, -40)], 5, INK, closed=True,
                 fill=(0.85, 0.25, 0.25))
        polyline(cr, [(90, -165), (145, -165), (180, -115), (90, -115)], 4, INK, closed=True, fill=(0.75, 0.86, 0.98))
        with xform(cr, -80, -135, sx=face, sy=1):
            text(cr, label, 0, 0, 52, face=FONT_TITLE, c=GREEN)
        for wx in (-150, 120):
            circle(cr, wx, -30, 34, fill=INK)
            circle(cr, wx, -30, 13, fill=LIGHT)
            line(cr, wx, -30, wx + 13 * math.cos(roll), -30 + 13 * math.sin(roll), 3, INK)


def syringe(cr, x, y, s=1.0, rot=-0.6):
    with xform(cr, x, y, s, rot):
        rect(cr, -90, -20, 140, 40, fill=(0.85, 0.95, 1.0), stroke=INK, lw=4)
        rect(cr, -90, -20, 80, 40, fill=(0.55, 0.85, 0.95))
        rect(cr, 50, -6, 70, 12, fill=LIGHT, stroke=INK, lw=3)
        line(cr, 120, 0, 175, 0, 3, INK)
        rect(cr, -130, -6, 40, 12, fill=LIGHT, stroke=INK, lw=3)
        rect(cr, -140, -30, 12, 60, fill=LIGHT, stroke=INK, lw=3)
        for i in range(4):
            line(cr, -70 + i * 26, -20, -70 + i * 26, -6, 2, INK)


def grad_cap(cr, x, y, s=1.0, c=INK):
    with xform(cr, x, y, s):
        polyline(cr, [(-90, 0), (0, -40), (90, 0), (0, 40)], 3, INK, closed=True, fill=c)
        polyline(cr, [(-50, 18), (-50, 60), (50, 60), (50, 18)], 3, INK, fill=c)
        line(cr, 0, 0, 70, 20, 3, GOLD)
        line(cr, 70, 20, 70, 70, 4, GOLD)


def diploma(cr, x, y, s=1.0, rot=-0.2):
    with xform(cr, x, y, s, rot):
        rrect(cr, -90, -22, 180, 44, 20, fill=(0.98, 0.95, 0.85), stroke=INK, lw=4)
        rect(cr, -10, -22, 20, 44, fill=RED)


def microscope(cr, x, y, s=1.0):
    """Base at bottom."""
    with xform(cr, x, y, s):
        rrect(cr, -80, -24, 160, 24, 8, fill=GRAY, stroke=INK, lw=4)
        arc(cr, -10, -110, 80, -0.3, 1.6, 14, INK)
        rect(cr, -60, -110, 80, 12, fill=LIGHT, stroke=INK, lw=3)
        with xform(cr, 20, -190, 1, 0.45):
            rrect(cr, -18, -70, 36, 120, 8, fill=WHITE, stroke=INK, lw=4)
            rect(cr, -12, -90, 24, 22, fill=GRAY, stroke=INK, lw=3)


def door_frame(cr, x, y, s=1.0, open_=0.0, light=(1.0, 0.92, 0.6), c=(0.55, 0.38, 0.22)):
    """Door in a frame (base at floor, ~150x300), opening toward the viewer with light behind it."""
    with xform(cr, x, y, s):
        rect(cr, -85, -310, 170, 310, fill=(0.35, 0.30, 0.28), stroke=INK, lw=6)
        if open_ > 0:
            glow(cr, 0, -150, 260, light, 0.7 * open_)
            rect(cr, -75, -300, 150, 300, fill=light, a=open_)
        w_ = 150 * math.cos(open_ * 1.3)
        polyline(cr, [(-75, -300), (-75 + w_, -300 - 20 * open_), (-75 + w_, 20 * open_), (-75, 0)], 5, INK,
                 closed=True, fill=c)
        circle(cr, -75 + w_ * 0.85, -150, 7, fill=GOLD)


def gear_people(cr, x, y, s, T, k=1.0, n=3):
    """A big gear turned by small stickmen pushing on spokes (people = engine)."""
    with xform(cr, x, y, s):
        rot = T * 0.8 * k
        P.gear(cr, 0, 0, 160, 14, rot, fill=(0.85, 0.85, 0.88))
        circle(cr, 0, 0, 40, fill=GRAY, stroke=INK, w=5)


# ---------------------------------------------------------------- constellations (custom shapes)
SHAPES = dict(K.CONSTELLATIONS)
SHAPES.update({
    "plane": [(-1, 0), (1, 0), None, (-0.2, 0), (-0.5, -0.7), None, (-0.2, 0), (-0.5, 0.7), None, (-0.9, 0),
              (-1, -0.35)],
    "city": [(-1, 0.8), (-1, -0.2), (-0.6, -0.2), (-0.6, -0.7), (-0.2, -0.7), (-0.2, 0.0), (0.2, 0.0), (0.2, -1.0),
             (0.6, -1.0), (0.6, -0.3), (1, -0.3), (1, 0.8), (-1, 0.8)],
    "cross": [(-0.3, -1), (0.3, -1), (0.3, -0.3), (1, -0.3), (1, 0.3), (0.3, 0.3), (0.3, 1), (-0.3, 1), (-0.3, 0.3),
              (-1, 0.3), (-1, -0.3), (-0.3, -0.3), (-0.3, -1)],
    "building": [(-0.7, 0.9), (-0.7, -0.6), (0, -1), (0.7, -0.6), (0.7, 0.9), (-0.7, 0.9), None, (-0.4, 0.9),
                 (-0.4, -0.4), None, (0, 0.9), (0, -0.4), None, (0.4, 0.9), (0.4, -0.4)],
    "wrench": [(-0.9, 0.9), (0.3, -0.3), None, (0.1, -0.5), (0.3, -1), (0.7, -0.9), (0.5, -0.5), (0.9, -0.3),
               (1, -0.7), None, (0.3, -0.3), (0.6, -0.1), (1, -0.3)],
    "mansion": [(-1, 0.8), (-1, -0.1), (-0.4, -0.1), (-0.4, -0.5), (0, -0.9), (0.4, -0.5), (0.4, -0.1), (1, -0.1),
                (1, 0.8), (-1, 0.8)],
    "wall": [(-1, 0.6), (-1, -0.4), (1, -0.4), (1, 0.6), (-1, 0.6), None, (-1, 0.1), (1, 0.1), None, (-0.5, -0.4),
             (-0.5, 0.1), None, (0.5, -0.4), (0.5, 0.1), None, (0, 0.1), (0, 0.6)],
    "bridge": [(-1, 0.6), (-1, 0.1), (1, 0.1), (1, 0.6), None, (-1, 0.1), (-0.5, -0.3), (0, -0.45), (0.5, -0.3),
               (1, 0.1), None, (-0.5, -0.3), (-0.5, 0.1), None, (0, -0.45), (0, 0.1), None, (0.5, -0.3), (0.5, 0.1)],
    "dollar": [(0.5, -0.6), (0, -0.8), (-0.5, -0.6), (-0.5, -0.2), (0.5, 0.2), (0.5, 0.6), (0, 0.8), (-0.5, 0.6),
               None, (0, -1), (0, 1)],
    "hands": [(-1, 0.2), (-0.4, 0.4), (0.4, 0.4), (1, 0.2), None, (-0.4, 0.4), (-0.2, -0.1), None, (0.4, 0.4),
              (0.2, -0.1), None, (-0.2, -0.4), (0, -0.7), (0.2, -0.4), (0, -0.2), (-0.2, -0.4)],
    "globe": [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), None,
              (-1, 0), (1, 0), None, (0, -1), (-0.35, 0), (0, 1), None, (0, -1), (0.35, 0), (0, 1)],
})


def constellation(cr, shape, cx, cy, size, k, T, c=(0.92, 0.94, 1.0), a=1.0, label=None, label_size=34):
    pts = SHAPES[shape]
    segs, cur = [], []
    for p_ in pts:
        if p_ is None:
            segs.append(cur)
            cur = []
        else:
            cur.append((cx + p_[0] * size, cy + p_[1] * size))
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
        text(cr, label, cx, cy + size + 50, label_size, face=FONT_BOLD, c=c, a=a * clamp((k - 0.6) * 3))


# ---------------------------------------------------------------- small layout helpers
def title_text(cr, s, y=150, size=60, c=INK, a=1.0, outline=None, x=CX):
    text(cr, s, x, y, size, face=FONT_TITLE, c=c, a=a, outline=outline, ow=8)


def card_panel(cr, x, y, w, h, fill=WHITE, stroke=INK, lw=6, r=24, a=1.0):
    rrect(cr, x - w / 2, y - h / 2, w, h, r, fill=fill, stroke=stroke, lw=lw, a=a)


def meter(cr, x, y, w, label, v, c=GREEN, size=34, h=36, label_w=None, a=1.0):
    """Horizontal bar meter: label on the left, bar to the right."""
    text(cr, label, x, y, size, face=FONT_TITLE, align="right", a=a)
    rrect(cr, x + 24, y - h / 2, w, h, h / 2, fill=LIGHT, stroke=INK, lw=4, a=a)
    if v > 0.01:
        rrect(cr, x + 24, y - h / 2, max(h, w * clamp(v)), h, h / 2, fill=c, a=a)
        rrect(cr, x + 24, y - h / 2, w, h, h / 2, stroke=INK, lw=4, a=a)


# ---------------------------------------------------------------- timing
def wt(tl, bid, word, occ=0, lead=0.08):
    """Like tl.w, but maps the character offset onto voiced time only (skips pauses longer than 0.2 s),
    which is much closer for beats with '...' or sentence breaks."""
    b = tl.beats[bid]
    txt = b["text"]
    low = txt.lower()
    i = -1
    for _ in range(occ + 1):
        i = low.find(word.lower(), i + 1)
    if i < 0:
        raise KeyError(f"{word!r} not in {bid}")
    e = b.get("env") or []
    n = len(e)
    if n == 0:
        return tl.w(bid, word, occ, lead)
    quiet = [v < 0.05 for v in e]
    active = [True] * n
    j = 0
    while j < n:
        if quiet[j]:
            k = j
            while k < n and quiet[k]:
                k += 1
            if k - j >= 6 or j == 0:
                for m in range(j, k):
                    active[m] = False
            j = k
        else:
            j += 1
    total = sum(active)
    if total == 0:
        return tl.w(bid, word, occ, lead)
    target = total * i / max(1, len(txt))
    acc = 0
    for f in range(n):
        if active[f]:
            acc += 1
            if acc >= target:
                return b["start"] + f / 30.0 - lead
    return b["end"] - lead


def timing(tl):
    """Return (s, e, w) helpers for a chapter; w uses voiced-time word estimates."""
    return tl.s, tl.e, (lambda bid, word, occ=0: wt(tl, bid, word, occ))


# ---------------------------------------------------------------- icon row with two-line labels
def icons2(title, items, bg=PAPER, title_c=INK, label_c=INK, y=520, size=1.0, label_size=38, zoom=(1.0, 1.04),
           dark=False, title_y=200, extra=None):
    """Like K.icons, but labels may contain '\\n' for two rows; extra(cr, t, d, T) draws on top (in camera)."""
    n = len(items)

    def fn(cr, t, d, T):
        if callable(bg):
            bg(cr, T)
        else:
            rect(cr, -20, -20, W + 40, H + 40, fill=bg)
            vignette(cr, 0.18 if not dark else 0.5)
        with K.ken(cr, t, d, *zoom):
            if title:
                text(cr, title, CX, title_y, 60, face=FONT_TITLE, c=title_c, a=eout(prog(t, 0.05, 0.4)))
            span = 1560 if n > 2 else 1000
            for i, (draw, label, ta) in enumerate(items):
                x = CX - span / 2 + span * (i + 0.5) / n if n > 1 else CX
                k = K.pop(T, ta)
                if k <= 0:
                    continue
                with xform(cr, x, y, max(0.01, k) * size):
                    draw(cr, T)
                if label:
                    rows = label.split("\n")
                    for r, row in enumerate(rows):
                        text(cr, row, x, y + 165 * size + r * label_size * 1.15, label_size, face=FONT_BOLD,
                             c=label_c, a=clamp(k))
            if extra:
                extra(cr, t, d, T)
    return fn
