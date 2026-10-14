"""Chapter 6 - The Dark Side of Extreme Intelligence (4:50-5:50)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

DARK_TAG = True
ROOM = (0.10, 0.11, 0.15)
ROOM2 = (0.06, 0.065, 0.09)
LAMP = (1.0, 0.86, 0.55)
PALE = (0.86, 0.87, 0.90)
NFILL = (0.12, 0.13, 0.17)


def dark_room(cr, T, lamp_x=760, lamp_y=380, flicker=0.0):
    vgrad(cr, ROOM, ROOM2)
    rect(cr, -300, 880, W + 600, 500, fill=(0.07, 0.07, 0.10))
    line(cr, -300, 880, W + 300, 880, 4, (0.25, 0.26, 0.32))
    f = 1.0 - flicker * (0.5 + 0.5 * math.sin(T * 47) * math.sin(T * 13))
    glow(cr, lamp_x, lamp_y + 120, 650, LAMP, 0.28 * f)
    return f


def lamp(cr, x, y, f=1.0):
    line(cr, x, 0, x, y - 40, 3, (0.3, 0.3, 0.35))
    polyline(cr, [(x - 60, y), (x - 25, y - 45), (x + 25, y - 45), (x + 60, y)], 4, PALE, closed=True, fill=(0.2, 0.2, 0.25))
    ellipse(cr, x, y + 4, 40, 10, fill=LAMP, a=f)


def paper_sheet(cr, x, y, rot, s=1.0, a=1.0, seed=0):
    r = rng(seed)
    with xform(cr, x, y, s, rot):
        rect(cr, -55, -70, 110, 140, fill=(0.92, 0.91, 0.86), stroke=(0.35, 0.35, 0.4), lw=3, a=a)
        syms = ["∫", "Σ", "∂", "π", "√", "λ", "Δ", "∞"]
        for j in range(4):
            text(cr, "".join(r.choice(syms) for _ in range(4)), 0, -40 + j * 28, 20, c=(0.25, 0.25, 0.3), a=a,
                 face=FONT_SERIF)


def alien_glyph(cr, x, y, seed, size=40, c=GREEN, a=1.0):
    r = rng(seed)
    with xform(cr, x, y, size / 40):
        for _ in range(r.randint(2, 4)):
            kind = r.randrange(4)
            if kind == 0:
                line(cr, r.uniform(-16, 16), r.uniform(-18, 18), r.uniform(-16, 16), r.uniform(-18, 18), 4, c, a)
            elif kind == 1:
                circle(cr, r.uniform(-8, 8), r.uniform(-10, 10), r.uniform(4, 9), stroke=c, w=4, a=a)
            elif kind == 2:
                arc(cr, r.uniform(-6, 6), r.uniform(-6, 6), r.uniform(8, 14), r.uniform(0, 3), r.uniform(3.5, 6), 4, c, a)
            else:
                circle(cr, r.uniform(-12, 12), r.uniform(-14, 14), 3.5, fill=c, a=a)


def pale_chair(cr, x, y, face=-1):
    with xform(cr, x, y, 1.0, sx=face, sy=1.0):
        line(cr, -50, -150, 50, -150, 7, PALE)
        line(cr, -45, -150, -45, 0, 5, PALE)
        line(cr, 45, -150, 45, 0, 5, PALE)
        line(cr, -50, -150, -60, -300, 5, PALE)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. a darker side
    t_dark = w("c6_01", "darker")

    @b.shot(0, "fade", 0.5)
    def darken(cr, t, d, T):
        k = ease(prog(T, t_dark - 0.3, 1.2))
        bg = lerpc((0.93, 0.92, 0.89), ROOM, k)
        fill_bg(cr, bg)
        rect(cr, 0, 880, W, 200, fill=lerpc((0.82, 0.78, 0.72), (0.07, 0.07, 0.10), k))
        ink = lerpc(INK, PALE, k)
        line(cr, 0, 880, W, 880, 4, ink)
        if k > 0:
            glow(cr, 960, 500, 650, LAMP, 0.28 * k)
        with ken(cr, t, d, 1.0, 1.08, CX, 600):
            lamp(cr, 960, 380, k)
            P.desk(cr, 960, 880, 520)
            if k < 0.5:
                P.chair(cr, 860, 880, 1.0, face=-1)
            else:
                pale_chair(cr, 860, 880)
            p = sm.pose("sit", x=860, face=1, a1f=60, a2f=50, a1b=55, a2b=55, smile=lerp(0.4, -0.3, k),
                        brow=-0.4 * k, gy=0.6)
            p = sm.on_ground(sm.idle(p, T, 1), 880)
            sm.hero(cr, p, ink=ink, fill=lerpc(WHITE, NFILL, k))
        # shadow sweeping across
        if 0 < k < 1:
            x = lerp(-W * 0.3, W * 1.3, k)
            g = cairo_lg(x - 500, x + 300)
            cr.set_source(g)
            cr.paint()
        vignette(cr, 0.6 * k)

    def cairo_lg(x0, x1):
        import cairo
        g = cairo.LinearGradient(x0, 0, x1, 0)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(0.6, 0, 0, 0, 0.55)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        return g

    b.fx(t_dark - 0.3, "darkwhoosh", -6)

    # ------------------------------------------------------------ 2. this part is fiction
    st2 = s("c6_02") - 0.3
    t_fic, t_res = w("c6_02", "fiction"), w("c6_02", "research")

    @b.shot(st2, "fade", 0.4)
    def fiction(cr, t, d, T):
        dark(cr, T, c1=ROOM, c2=ROOM2, vig=0.6)
        with ken(cr, t, d, 1.0, 1.04):
            # clapperboard
            k = prog(T, t_fic - 0.3, 0.35)
            with xform(cr, 960, 360, 1.0):
                rect(cr, -260, -60, 520, 220, fill=(0.12, 0.12, 0.14), stroke=PALE, lw=6)
                text(cr, "FICTION", 0, 60, 96, face=FONT_TITLE, c=YELLOW)
                ang = lerp(-0.5, 0, eout(k))
                with xform(cr, -260, -60, 1.0, ang):
                    rect(cr, 0, -60, 520, 60, fill=(0.12, 0.12, 0.14), stroke=PALE, lw=6)
                    for i in range(6):
                        polyline(cr, [(20 + i * 90, -60), (60 + i * 90, -60), (40 + i * 90, 0), (0 + i * 90, 0)], 0,
                                 WHITE, closed=True, fill=WHITE)
            kr = prog(T, t_res, 0.5)
            if kr > 0:
                text(cr, "WHAT RESEARCH DOESN'T SHOW:", 960, 660, 44, face=FONT_BOLD, c=PALE, a=kr)
                with group(cr, kr):
                    label_box(cr, "HIGH IQ", 640, 790, 54, c=INK, bg=(0.85, 0.92, 1.0), face=FONT_BOLD, bold=False)
                    arrow(cr, 820, 790, 1080, 790, 10, PALE, head=34)
                    label_box(cr, "UNHAPPY", 1290, 790, 54, c=INK, bg=(1.0, 0.85, 0.85), face=FONT_BOLD, bold=False)
                    cross(cr, 950, 790, 1.8, p=prog(T, t_res + 0.6, 0.4))

    b.fx(t_fic - 0.3, "clap", -4)
    b.fx(t_res + 0.6, "buzz", -12)

    # ------------------------------------------------------------ 3. the room fills up
    st3 = s("c6_03") - 0.3
    t_fill, t_unf = w("c6_03", "fills"), w("c6_03", "unfinished")
    rs = rng(31)
    sheets = [(rs.uniform(80, 1840), rs.uniform(80, 860), rs.uniform(-0.5, 0.5), rs.uniform(0.7, 1.2)) for _ in range(70)]

    @b.shot(st3, "fade", 0.4)
    def clutter(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.10, CX, 560):
            f = dark_room(cr, T, 960, 300, flicker=0.15)
            k = prog(T, t_fill - 0.5, 4.0)
            n = int(len(sheets) * ease(k))
            for i, (x, y, rot, sc) in enumerate(sheets[:n]):
                paper_sheet(cr, x, y, rot + math.sin(T * 0.5 + i) * 0.03, sc * 0.9, 0.9, seed=i)
            lamp(cr, 960, 300, f)
            P.desk(cr, 960, 880, 560)
            ku = prog(T, t_unf, 0.6)
            if ku > 0:
                for i, (bx, lab) in enumerate(((560, "40%"), (1360, "TODO"), (1520, "65%"))):
                    with group(cr, ku):
                        rect(cr, bx - 70, 760, 140, 120, fill=(0.55, 0.42, 0.3), stroke=INK, lw=4)
                        label_box(cr, lab, bx, 730, 30, c=INK, bg=PALE)
                P.gear(cr, 1180, 690, 40, 8, T * 0.2, fill=PALE)
            pale_chair(cr, 880, 880)
            p = sm.pose("sit", x=880, face=1, a1f=35, a2f=135, a1b=50, a2b=60, smile=-0.4, brow=-0.6, gy=0.2)
            p = sm.on_ground(sm.idle(p, T, 2), 880)
            sm.hero(cr, p, ink=PALE, fill=NFILL)
        vignette(cr, 0.55)

    b.fx(t_fill - 0.5, "papers", -10, dur=4.0)

    # ------------------------------------------------------------ 4. simple choices become enormous
    st4 = s("c6_04") - 0.3
    qs = [("GO OUTSIDE?", "should you"), ("WHAT COULD HAPPEN?", "what could"), ("WHAT'S MISSING?", "evidence")]

    @b.shot(st4, "fade", 0.4)
    def choices(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.06, 900, 560):
            f = dark_room(cr, T, 1300, 250)
            P.door(cr, 1450, 880, 1.2, open_=0, frame_fill=(0.25, 0.25, 0.3), ink=PALE)
            p = sm.pose("worried", x=900, face=1, gx=0.4, gy=-0.6)
            p = sm.on_ground(sm.idle(p, T, 3), 880)
            J = sm.hero(cr, p, ink=PALE, fill=NFILL)
            hx, hy = J["head"]
            for i, (q, word) in enumerate(qs):
                k = prog(T, w("c6_04", word), 0.5)
                if k <= 0:
                    continue
                y = hy - 160 - i * 150
                x = hx + (i - 1) * 380
                P.decision_tree(cr, x, y + 70, depth=2 + i, spread=120, dy=50, p=ease(k), ink=lerpc(PALE, RED, i / 2),
                                lw=3, shrink=0.55)
                label_box(cr, q, x, y + 110, 34, c=WHITE, bg=(0.25, 0.08, 0.1), scale=back(k), face=FONT_BOLD, bold=False)
            del f
        vignette(cr, 0.5)

    b.fx(st4 + 0.3, "heartbeat", -6, dur=7.0)
    for q, word in qs:
        b.fx(w("c6_04", word), "blip", -12)

    # ------------------------------------------------------------ 5. ten more... then a hundred
    st5 = s("c6_05") - 0.3
    t_ten, t_hund = w("c6_05", "ten"), w("c6_05", "hundred")

    @b.shot(st5, "cut")
    def explosion(cr, t, d, T):
        fill_bg(cr, ROOM2)
        k = prog(T, st5, d)
        depth = 2 + int(5 * ease(prog(T, t_ten - 0.3, t_hund + 0.6 - t_ten)))
        z = lerp(1.2, 0.75, ease(k))
        with camera(cr, z, CX, 620):
            for j, (x, a0) in enumerate(((CX, 0), (CX - 520, 0.3), (CX + 520, -0.3))):
                P.decision_tree(cr, x, 1000, depth=depth, spread=330 if j == 0 else 200, dy=110, p=1.0,
                                ink=lerpc(PALE, RED, clamp(depth / 7)), lw=3, shrink=0.52)
            p = sm.pose("worried", x=CX, face=1, eye=1.25, s=0.9)
            p = sm.apply(p, a1f=150, a2f=60, a1b=-150, a2b=-60)
            p = sm.on_ground(p, 1110)
            sm.hero(cr, p, ink=PALE, fill=NFILL)
        n = 1 if T < t_ten else (10 if T < t_hund else 100)
        text(cr, str(n), CX, 180, 160, face=FONT_TITLE, c=RED, scale=1.0 + 0.1 * math.sin(T * 12))
        vignette(cr, 0.6)

    b.fx(t_ten, "stinger", -6)
    b.fx(t_hund, "stinger", -4)
    b.fx(st5, "chaos", -10, dur=d_left(tl, st5, 4.0))

    # ------------------------------------------------------------ 6. frustration, alien language
    st6 = s("c6_06") - 0.3
    t_alien = w("c6_06", "explaining")

    @b.shot(st6, "fade", 0.4)
    def alien(cr, t, d, T):
        dark_room(cr, T, 960, 200)
        with ken(cr, t, d, 1.0, 1.05):
            p = sm.pose("present", x=560, face=1, smile=0.7, mo=0.3)
            p = sm.talk(sm.idle(p, T, 4), T, None, 0.8)
            if T > t_alien:
                p = sm.apply(p, a1f=90 + 30 * math.sin(T * 5), a2f=30)
            p = sm.on_ground(p, 880)
            J = sm.hero(cr, p, ink=PALE, fill=NFILL)
            for i, (x, acc) in enumerate(((1260, ("cap",)), (1540, ("ponytail",)))):
                q = sm.pose("listen", x=x, face=-1, smile=-0.1, blink=0.6 if i == 0 else 0.0)
                if i == 0:
                    q = sm.apply(q, a1f=30, a2f=140, head=14, mo=0.6 * max(0, math.sin(T * 1.3)))
                else:
                    q = sm.apply(q, a1f=24, a2f=150, head=10, gy=0.9)
                q = sm.on_ground(sm.idle(q, T, 5 + i), 880)
                Jq = sm.draw(cr, q, acc=acc, ink=PALE, fill=NFILL)
                if i == 1:
                    P.phone(cr, Jq["hand_f"][0], Jq["hand_f"][1] - 20, 0.3, T, lit=1.0)
                text(cr, ["*yawn*", "huh?"][i], x, 380 + i * 30, 40, face=FONT_HAND, bold=True, c=MID,
                     a=prog(T, st6 + 1.0 + i * 0.6, 0.4))
            kb = prog(T, t_alien - 0.2, 0.4)
            if kb > 0:
                speech_bubble(cr, 760, 300, 600, 200, J["head"][0] + 30, J["head"][1] - 50, fill=(0.85, 1.0, 0.85),
                              scale=back(kb))
                base = int(T * 3) * 31
                for row in range(2):
                    for col in range(9):
                        alien_glyph(cr, 760 - 240 + col * 60, 262 + row * 72, base + row * 9 + col, 44, GREEN,
                                    clamp(kb))
        vignette(cr, 0.5)

    b.fx(st6 + 0.5, "murmur", -14, dur=2.0)
    b.fx(t_alien, "alien", -10, dur=2.5)

    # ------------------------------------------------------------ 7. perfection, every time
    st7 = s("c6_07") - 0.3
    t_perf = w("c6_07", "perfection")

    @b.shot(st7, "fade", 0.4)
    def perfect(cr, t, d, T):
        dark_room(cr, T, 960, 200)
        with ken(cr, t, d, 1.0, 1.06):
            rrect(cr, 560, 260, 800, 120, 20, fill=(0.2, 0.2, 0.25), stroke=PALE, lw=5)
            k = ease(prog(t, 0.3, 1.4))
            rrect(cr, 575, 275, 770 * 0.99 * k, 90, 14, fill=GREEN)
            text(cr, f"{int(99 * k)}%", 960, 320, 64, face=FONT_TITLE, c=WHITE)
            stamp(cr, "NOT PERFECT", 780, 560, T - (t_perf + 0.5), 90, c=RED, rot=-0.07)
            p = sm.pose("sad", x=1400, face=-1, s=1.0)
            p = sm.on_ground(sm.idle(p, T, 6), 880)
            sm.hero(cr, p, ink=PALE, fill=NFILL)
            # rising bar of expectations
            by = lerp(700, 620, ease(prog(T, t_perf, 1.5))) - 10 * math.sin(T * 2)
            line(cr, 1240, by - 120, 1560, by - 120, 8, RED, 0.7)
            text(cr, "MY STANDARD", 1580, by - 120, 30, face=FONT_HAND, bold=True, c=RED, align="left")
        vignette(cr, 0.5)

    b.fx(st7 + 0.3, "rise", -12)
    b.fx(t_perf + 0.5, "stamp", -6)

    # ------------------------------------------------------------ 8. intelligence is not wisdom
    st8 = s("c6_08") - 0.3
    t_trap, t_wise = w("c6_08", "trap"), w("c6_08", "wise")

    @b.shot(st8, "fade", 0.4)
    def wisdom(cr, t, d, T):
        dark(cr, T, c1=(0.12, 0.12, 0.17), c2=ROOM2)
        with ken(cr, t, d, 1.0, 1.04):
            label_box(cr, "INTELLIGENCE", 520, 300, 64, c=INK, bg=(0.85, 0.92, 1.0), face=FONT_TITLE, bold=False)
            label_box(cr, "WISDOM", 1400, 300, 64, c=INK, bg=(1.0, 0.95, 0.75), face=FONT_TITLE, bold=False)
            k = prog(T, t_wise - 0.2, 0.5)
            sym = "=" if k < 0.5 else "≠"
            text(cr, sym, 960, 300, 150, face="DejaVu Sans", c=WHITE if k < 0.5 else RED,
                 scale=1 + 0.3 * math.sin(clamp(k) * math.pi))
            if k > 0.4:
                burst(cr, 960, 300, T - t_wise - 0.05, n=10, dist=150, c=RED, dur=0.5)
            kd = prog(T, t_wise + 0.3, 0.6)
            if kd > 0:
                text(cr, "knowing HOW", 520, 420, 48, face=FONT_HAND, bold=True, c=PALE, a=kd)
                text(cr, "knowing WHAT MATTERS", 1400, 420, 48, face=FONT_HAND, bold=True, c=PALE, a=kd)
            # the trap
            kt = prog(T, t_trap, 0.5)
            if kt > 0:
                with group(cr, kt):
                    rect(cr, 760, 860, 400, 30, fill=(0.55, 0.42, 0.3), stroke=PALE, lw=4)
                    for i in range(8):
                        line(cr, 780 + i * 50, 860, 790 + i * 50, 820, 5, PALE)
                    text(cr, "TRAP", 960, 940, 40, face=FONT_TITLE, c=RED)
            p = sm.pose("think", x=560 + 150 * ease(prog(T, t_trap, 1.5)), face=1, smile=0.2, gy=-0.6)
            p = sm.walk(p, T, 0.7, 0.6) if T < t_trap + 1.5 else p
            if T > t_wise:
                p = sm.pose("surprised", x=710, face=1)
            p = sm.on_ground(p, 880)
            sm.hero(cr, p, ink=PALE, fill=NFILL)
        vignette(cr, 0.5)

    b.fx(t_trap, "thud", -10)
    b.fx(t_wise - 0.2, "crack", -6)

    # ------------------------------------------------------------ 9. close the notebook, go outside
    st9 = s("c6_09") - 0.3
    t_close, t_walk, t_call = w("c6_09", "close"), w("c6_09", "walk"), w("c6_09", "call")

    @b.shot(st9, "fade", 0.5)
    def outside(cr, t, d, T):
        k_out = ease(prog(T, t_walk - 0.3, 0.9))
        if k_out < 1:
            with group(cr, 1 - k_out):
                dark_room(cr, T, 760, 330)
                lamp(cr, 760, 330, 1.0)
                op = ease(prog(T, t_close + 0.6, 0.6))
                P.door(cr, 1450, 880, 1.2, open_=op, frame_fill=(0.25, 0.25, 0.3), ink=PALE, light=(1.0, 0.95, 0.8))
                P.desk(cr, 760, 880, 460)
                kc = ease(prog(T, t_close, 0.4))
                with xform(cr, 760, 718, 1.0):
                    rect(cr, -120, -10, 120, 14, fill=PALE, stroke=INK, lw=3)
                    with xform(cr, 0, 0, 1.0, -math.pi * (1 - kc)):
                        rect(cr, 0, -10, 120, 14, fill=(0.55, 0.42, 0.3), stroke=INK, lw=3)
                p = sm.pose("stand", x=lerp(900, 1400, op), face=1, smile=0.3)
                p = sm.walk(p, T, 1.0) if op > 0 else p
                p = sm.on_ground(p, 880)
                sm.hero(cr, p, ink=PALE, fill=NFILL)
        if k_out > 0:
            with group(cr, k_out):
                vgrad(cr, (0.65, 0.83, 0.98), (0.93, 0.97, 0.92))
                P.sun(cr, 1600, 200, 80, T)
                rect(cr, 0, 860, W, 220, fill=(0.62, 0.80, 0.50))
                ground(cr, 860)
                P.tree(cr, 300, 860, 1.3, T)
                P.tree(cr, 1500, 860, 1.1, T + 2)
                P.cloud(cr, 700, 180, 0.9)
                kcall = prog(T, t_call - 0.3, 0.4)
                x = lerp(500, 900, ease(prog(T, t_walk, 2.2)))
                p = sm.walk(sm.pose(x=x, face=1, smile=0.7), T, 0.9)
                if kcall > 0:
                    p = sm.apply(p, a1f=24, a2f=150, head=4, smile=0.9)
                p = sm.on_ground(p, 860)
                J = sm.hero(cr, p)
                if kcall > 0:
                    P.phone(cr, J["hand_f"][0] + 6, J["hand_f"][1] - 18, 0.22, T)
                    speech_bubble(cr, J["head"][0] + 230, J["head"][1] - 150, 260, 90, J["head"][0] + 40,
                                  J["head"][1] - 40, scale=back(kcall))
                    text(cr, "Hey! Walk?", J["head"][0] + 230, J["head"][1] - 150, 40, face=FONT_HAND, bold=True,
                         a=clamp(kcall))
                    for i in range(3):
                        arc(cr, J["hand_f"][0] + 30, J["hand_f"][1] - 30, 20 + i * 14, -0.8, 0.2,
                            4, BLUE, 0.6 * (0.5 + 0.5 * math.sin(T * 8 - i)))

    b.fx(t_close, "thud", -6)
    b.fx(t_close + 0.6, "door", -8)
    b.fx(t_walk - 0.3, "birds", -12, dur=d_left(tl, t_walk, 9.0))
    b.fx(t_call - 0.3, "dial", -10)

    # ------------------------------------------------------------ 10. ordinary human needs
    st10 = s("c6_10") - 0.3
    needs = [("FRESH AIR", "fresh air"), ("SLEEP", "sleep"), ("PEOPLE WHO CARE", "people")]

    def panel_air(cr, T):
        vgrad(cr, (0.7, 0.87, 0.98), (0.9, 0.97, 0.9))
        rect(cr, 0, 380, 520, 200, fill=(0.62, 0.80, 0.50))
        P.tree(cr, 380, 380, 0.7, T)
        p = sm.pose("arms_out", x=200, face=1, smile=0.9, blink=1.0, s=0.7)
        p = sm.on_ground(sm.idle(p, T, 7), 380)
        sm.hero(cr, p)
        for i in range(4):
            f = (T * 0.5 + i * 0.25) % 1
            pts = [(40 + f * 400 + j * 18, 150 + i * 40 + 10 * math.sin(j * 0.8 + T * 3)) for j in range(6)]
            polyline(cr, pts, 4, WHITE, 1 - f)

    def panel_sleep(cr, T):
        vgrad(cr, (0.10, 0.12, 0.25), (0.20, 0.22, 0.38))
        stars(cr, T, n=30, area=(0, 0, 520, 300))
        circle(cr, 420, 90, 40, fill=(0.98, 0.95, 0.8))
        circle(cr, 440, 80, 36, fill=(0.10, 0.12, 0.25))
        rrect(cr, 60, 320, 400, 60, 12, fill=WHITE, stroke=INK, lw=4)
        rrect(cr, 70, 290, 100, 40, 16, fill=WHITE, stroke=INK, lw=4)
        p = sm.pose("front", x=0, s=0.7, blink=1.0, smile=0.5)
        with xform(cr, 210, 300, 1.0, -math.pi / 2):
            p = head_at(p, -40, -40)
            sm.hero(cr, p, ink=WHITE, fill=(0.2, 0.22, 0.38))
        rrect(cr, 200, 290, 260, 50, 16, fill=(0.6, 0.7, 0.95), stroke=INK, lw=4)
        for i in range(3):
            f = (T * 0.6 + i / 3) % 1
            text(cr, "z", 180 + f * 120, 230 - f * 150, 30 + 30 * f, face=FONT_HAND, bold=True, c=WHITE, a=1 - f)

    def panel_people(cr, T):
        vgrad(cr, (1.0, 0.85, 0.65), (1.0, 0.95, 0.85))
        rect(cr, 0, 380, 520, 200, fill=(0.9, 0.78, 0.62))
        for i, (x, acc) in enumerate(((130, ("tuft",)), (260, ("cap",)), (390, ("ponytail",)))):
            p = sm.pose("cheer" if (int(T * 2) + i) % 2 else "wave", x=x, face=1 if i < 1 else -1, s=0.6, smile=1.0, mo=0.5)
            p = sm.on_ground(sm.idle(p, T, i), 380)
            sm.draw(cr, p, acc=acc)
        P.heart(cr, 260, 70, 0.6, beat=max(0, math.sin(T * 6)))

    panels = [panel_air, panel_sleep, panel_people]

    @b.shot(st10, "fade", 0.4)
    def human(cr, t, d, T):
        paper(cr, (0.97, 0.95, 0.90))
        text(cr, "EVEN A BRILLIANT MIND NEEDS...", CX, 150, 54, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
        for i, ((lab, word), fn) in enumerate(zip(needs, panels)):
            k = back(prog(T, w("c6_10", word) - 0.5, 0.45))
            if k <= 0:
                continue
            x0 = 130 + i * 580
            with xform(cr, x0 + 260, 560, max(0.01, k)):
                cr.save()
                cr.translate(-260, -290)
                rrect_path(cr, 0, 0, 520, 580, 24)
                cr.clip()
                fn(cr, T)
                cr.restore()
                rrect(cr, -260, -290, 520, 580, 24, stroke=INK, lw=6)
            text(cr, lab, x0 + 260, 920, 44, face=FONT_BOLD, a=clamp(k))

    for lab, word in needs:
        b.fx(w("c6_10", word) - 0.5, "pop", -8)
    b.fx(st10, "chime", -10)
    return b.result()


def d_left(tl, st, cap):
    return max(0.5, min(cap, tl.dur - st - 0.3))
