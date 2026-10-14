"""Chapter 5 - You Could Change the World (3:40-4:50)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

BP = (0.93, 0.96, 1.0)
BPL = (0.55, 0.70, 0.92)


def card(cr, t, num, title, T):
    """Blueprint-paper background with a project header."""
    fill_bg(cr, BP)
    src(cr, BPL, 0.25)
    cr.set_line_width(1.5)
    for x in range(0, W, 40):
        cr.move_to(x, 0)
        cr.line_to(x, H)
    for y in range(0, H, 40):
        cr.move_to(0, y)
        cr.line_to(W, y)
    cr.stroke()
    k = eout(prog(t, 0.05, 0.35))
    x = lerp(-600, 70, k)
    rrect(cr, x, 60, 140, 60, 10, fill=INK)
    text(cr, f"#{num:02d}", x + 70, 90, 34, c=YELLOW, face=FONT_BOLD)
    text(cr, title, x + 165, 90, 46, face=FONT_TITLE, align="left")


def mini_hero(cr, T, x, y, pose="present", face=-1, s=0.9, **kw):
    p = sm.pose(pose, x=x, face=face, s=s, **kw)
    p = sm.on_ground(sm.idle(p, T, int(x) % 7), y)
    return sm.hero(cr, p)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. aim higher
    t_much = w("c5_01", "much higher")

    @b.shot(0, "fade", 0.4)
    def aim(cr, t, d, T):
        k = ease(prog(T, t_much, 1.2))
        cam_y = lerp(CY, -1400, k)
        sky = lerpc((0.97, 0.96, 0.93), (0.05, 0.06, 0.14), clamp(k * 1.3))
        fill_bg(cr, sky)
        if k > 0.3:
            stars(cr, T, n=180, alpha=clamp((k - 0.3) * 2))
        with camera(cr, 1.0, CX, cam_y):
            rect(cr, 0, 880, W, 300, fill=(0.85, 0.82, 0.76))
            ground(cr, 880)
            # target on the wall... then on the moon
            if k < 0.5:
                for i, (rr, c) in enumerate(((110, RED), (80, WHITE), (50, RED), (20, WHITE))):
                    circle(cr, 1250, 470, rr, fill=c, stroke=INK, w=4)
            circle(cr, 1250, -1900, 220, fill=(0.92, 0.92, 0.88), stroke=INK, w=6)
            for (mx, my, mr) in ((-60, -40, 40), (70, 50, 30), (20, -110, 22)):
                circle(cr, 1250 + mx, -1900 + my, mr, fill=(0.8, 0.8, 0.76))
            for i, (rr, c) in enumerate(((90, RED), (60, WHITE), (30, RED))):
                circle(cr, 1250, -1900, rr, fill=c, stroke=INK, w=4, a=clamp(k * 2 - 0.6))
            p = sm.pose("point_up" if k > 0.05 else "point", x=600, face=1, smile=0.7, brow=0.5)
            p = sm.on_ground(sm.idle(p, T, 1), 880)
            sm.hero(cr, p)
            dart_k = prog(T, 0.4, 0.6)
            if dart_k < 1 and k < 0.1:
                pass
            label_box(cr, "GOAL", 1250, 300 if k < 0.5 else -2160, 40, c=INK, scale=1.0)

    b.fx(t_much, "riser", -8, dur=1.2)
    b.fx(t_much + 1.1, "ding", -10)

    # ------------------------------------------------------------ 2. clean energy
    st2 = s("c5_02") - 0.2
    t_grid, t_waste = w("c5_02", "power grids"), w("c5_02", "waste")

    @b.shot(st2, "slide", 0.4)
    def energy(cr, t, d, T):
        card(cr, t, 1, "CLEANER ENERGY", T)
        with ken(cr, t, d, 1.0, 1.04, CX, 600):
            P.sun(cr, 300, 260, 70, T)
            for i, x in enumerate((240, 470)):
                P.solar_panel(cr, x, 800, 1.0, shine=1.0, t=T + i)
            for i, x in enumerate((700, 860)):
                P.wind_turbine(cr, x, 800, 0.9, T + i * 0.5)
            ground(cr, 800, BLUE, 4)
            houses = [(1250, 800), (1450, 800), (1650, 800)]
            for (hx, hy) in houses:
                P.house(cr, hx, hy, 0.9, lit=prog(T, t_grid, 0.6))
            kg = prog(T, t_grid - 0.4, 0.8)
            if kg > 0:
                poles = [(560, 560), (1000, 560), (1250, 560), (1450, 560), (1650, 560)]
                for (x1, y1), (x2, y2) in zip(poles, poles[1:]):
                    pts = bezier_pts([(x1, y1), ((x1 + x2) / 2, y1 + 50), (x2, y2)], 16)
                    partial_poly(cr, pts, kg, 4, INK)
                    for j in range(3):
                        f = (T * 1.2 + j / 3) % 1
                        px, py = pts[int(f * 16)]
                        circle(cr, px, py, 8, fill=YELLOW, stroke=INK, w=2, a=kg)
                for (x, y) in poles:
                    line(cr, x, y, x, 800, 6, INK)
            kw_ = prog(T, t_waste, 0.6)
            if kw_ > 0:
                bar_chart(cr, 1500, 390, [100, 55], ["WASTE BEFORE", "AFTER"], w=420, h=170, p=kw_,
                          colors=[RED, GREEN], size=24)
        mini_hero(cr, T, 1840, 1000, "present", face=-1, s=0.75)

    def bar_chart(cr, *a, **k):
        P.bar_chart(cr, *a, **k)

    b.fx(st2, "whoosh", -8)
    b.fx(t_grid - 0.4, "hum", -14, dur=4.0)
    b.fx(t_waste, "rise", -12)

    # ------------------------------------------------------------ 3. medicine
    st3 = s("c5_03") - 0.2
    t_treat = w("c5_03", "treatments")
    rv = rng(4)
    viruses = [(rv.uniform(-300, 300), rv.uniform(-300, 300), rv.uniform(0, 6)) for _ in range(9)]

    @b.shot(st3, "slide", 0.4)
    def medicine(cr, t, d, T):
        card(cr, t, 2, "MEDICAL RESEARCH", T)
        cx_, cy_ = 820, 580
        with ken(cr, t, d, 1.0, 1.05, cx_, cy_):
            circle(cr, cx_, cy_, 380, fill=(0.98, 0.94, 0.96), stroke=INK, w=10)
            cr.save()
            cr.arc(cx_, cy_, 372, 0, TAU)
            cr.clip()
            kt = prog(T, t_treat, 1.5)
            for i, (vx, vy, ph) in enumerate(viruses):
                x = cx_ + vx + math.sin(T * 0.8 + ph) * 25
                y = cy_ + vy + math.cos(T * 0.7 + ph) * 25
                dead = clamp(kt * 2.2 - i * 0.2)
                if dead < 1:
                    with xform(cr, x, y, 1 - 0.6 * dead, T * 0.5 + ph):
                        for j in range(10):
                            a = j / 10 * TAU
                            line(cr, math.cos(a) * 34, math.sin(a) * 34, math.cos(a) * 50, math.sin(a) * 50, 5, PURPLE, 1 - dead)
                            circle(cr, math.cos(a) * 52, math.sin(a) * 52, 6, fill=PURPLE, a=1 - dead)
                        circle(cr, 0, 0, 36, fill=(0.75, 0.55, 0.95), stroke=INK, w=4, a=1 - dead)
                if kt > 0 and dead < 1:
                    f = clamp(kt * 2.2 - i * 0.2 + 0.4)
                    px, py = lerp(cx_ - 420, x, f), lerp(cy_ + 300, y, f)
                    with xform(cr, px, py, 1, 0.6):
                        rrect(cr, -30, -14, 60, 28, 14, fill=WHITE, stroke=INK, lw=3)
                        rrect(cr, 0, -14, 30, 28, 14, fill=RED, stroke=INK, lw=3)
            cr.restore()
            P.dna(cr, 1450, 560, 1.2, T)
            text(cr, "MICROSCOPE VIEW", cx_, cy_ + 430, 30, face=FONT_HAND, bold=True)
        mini_hero(cr, T, 1780, 1000, "think", face=-1, s=0.75)

    b.fx(st3, "whoosh", -8)
    b.fx(st3 + 0.4, "bubbles", -14, dur=3.0)
    b.fx(t_treat, "zap", -10)

    # ------------------------------------------------------------ 4. transportation
    st4 = s("c5_04") - 0.2
    t_routes = w("c5_04", "better routes")

    @b.shot(st4, "slide", 0.4)
    def transport(cr, t, d, T):
        card(cr, t, 3, "SMARTER TRANSPORT", T)
        x0, y0, cell = 360, 200, 150
        k = ease(prog(T, t_routes, 1.0))
        with ken(cr, t, d, 1.0, 1.04, 840, 560):
            for i in range(9):
                for j in range(6):
                    rrect(cr, x0 + i * cell + 22, y0 + j * cell + 22, cell - 44, cell - 44, 8, fill=WHITE, stroke=BPL, lw=3)
            r = rng(9)
            for n in range(46):
                horiz = n % 2 == 0
                lane = r.randrange(0, 7 if horiz else 10)
                spd = r.uniform(60, 140)
                jam = (1 - k) * (1 if lane in (2, 3, 4) else 0.2)
                pos = (r.uniform(0, 1300) + T * spd * (1 - 0.85 * jam)) % 1350
                if horiz:
                    x, y = x0 + pos, y0 + lane * cell
                    if jam > 0.5:
                        x = x0 + 600 + (pos % 300) * 0.3
                else:
                    x, y = x0 + lane * cell, y0 + (pos % 900)
                col = lerpc(RED, GREEN, k) if jam > 0.3 else BLUE
                rrect(cr, x - 14, y - 9, 28, 18, 5, fill=col, stroke=INK, lw=2)
            if k > 0:
                route = [(x0, y0 + 5 * cell), (x0 + 3 * cell, y0 + 5 * cell), (x0 + 3 * cell, y0 + cell),
                         (x0 + 8 * cell, y0 + cell)]
                partial_poly(cr, route, k, 12, GREEN, 0.7)
                label_box(cr, "-38% TRAFFIC", 1500, 900, 36, c=GREEN, scale=back(prog(T, t_routes + 0.8, 0.4)))
            text(cr, "JAM", x0 + 680, y0 + 3 * cell - 40, 40, face=FONT_BOLD, c=RED, a=1 - k)
        mini_hero(cr, T, 1820, 1000, "point", face=-1, s=0.75)

    b.fx(st4, "whoosh", -8)
    b.fx(st4 + 0.3, "traffic", -16, dur=2.5)
    b.fx(t_routes, "rise", -10)

    # ------------------------------------------------------------ 5. climate models
    st5 = s("c5_05") - 0.2

    @b.shot(st5, "slide", 0.4)
    def climate(cr, t, d, T):
        card(cr, t, 4, "CLIMATE MODELS", T)
        with ken(cr, t, d, 1.0, 1.05, CX, 580):
            P.globe(cr, 640, 580, 300, T, heat=0.4 + 0.3 * math.sin(T))
            # simulation grid overlay
            cr.save()
            cr.arc(640, 580, 298, 0, TAU)
            cr.clip()
            r = rng(2)
            for i in range(-6, 7):
                for j in range(-6, 7):
                    v = 0.5 + 0.5 * math.sin(i * 0.7 + j * 0.4 + T * 1.5)
                    rect(cr, 640 + i * 50, 580 + j * 50, 50, 50, fill=lerpc(BLUE, RED, v), a=0.22)
            cr.restore()
            # model line chart
            gx, gy = 1060, 820
            line(cr, gx, gy, gx + 700, gy, 4, INK)
            line(cr, gx, gy, gx, gy - 420, 4, INK)
            pts = [(gx + i * 7, gy - 80 - i * 2.2 - 25 * math.sin(i * 0.3) * (1 - i / 100)) for i in range(100)]
            partial_poly(cr, pts, ease(prog(t, 0.3, 2.2)), 6, RED)
            text(cr, "SIMULATED YEARS →", gx + 350, gy + 40, 30, face=FONT_HAND, bold=True)
        mini_hero(cr, T, 1840, 1000, "think", face=-1, s=0.7)

    b.fx(st5, "whoosh", -8)
    b.fx(st5 + 0.3, "data", -14, dur=2.0)

    # ------------------------------------------------------------ 6. learning tools
    st6 = s("c5_06") - 0.2

    @b.shot(st6, "slide", 0.4)
    def learning(cr, t, d, T):
        card(cr, t, 5, "LEARNING TOOLS", T)
        with ken(cr, t, d, 1.0, 1.04, CX, 580):
            rrect(cr, 360, 200, 1200, 760, 40, fill=INK)
            rrect(cr, 390, 230, 1140, 700, 20, fill=WHITE)
            for i, (acc, col) in enumerate(((("cap",), BLUE), (("ponytail",), GREEN), (("glasses",), ORANGE))):
                y = 360 + i * 220
                p = sm.pose("front", x=500, s=0.45, smile=0.6)
                p = head_at(sm.idle(p, T, i), 500, y - 20)
                sm.draw(cr, p, acc=acc)
                path = [(580, y)]
                r = rng(i + 3)
                for j in range(1, 6):
                    path.append((580 + j * 170, y + r.uniform(-60, 60)))
                partial_poly(cr, path, ease(prog(t, 0.2 + i * 0.25, 1.6)), 6, col)
                for j, (px, py) in enumerate(path[1:]):
                    if ease(prog(t, 0.2 + i * 0.25, 1.6)) * 5 >= j + 1:
                        circle(cr, px, py, 16, fill=col, stroke=INK, w=3)
                text(cr, ["VISUAL", "HANDS-ON", "STEP BY STEP"][i], 1440, y - 50, 26, face=FONT_HAND, bold=True, c=col)
        mini_hero(cr, T, 1820, 1000, "present", face=-1, s=0.7)

    b.fx(st6, "whoosh", -8)
    b.fx(st6 + 0.5, "blips", -12, dur=2.0)

    # ------------------------------------------------------------ 7. AI safety
    st7 = s("c5_07") - 0.2
    t_int = w("c5_07", "intend")

    @b.shot(st7, "slide", 0.4)
    def ai_safety(cr, t, d, T):
        card(cr, t, 6, "AI SAFETY", T)
        with ken(cr, t, d, 1.0, 1.04, CX, 600):
            P.robot(cr, 520, 900, 1.2, T)
            tx, ty = 1480, 520
            for rr, c in ((150, RED), (105, WHITE), (60, RED), (22, WHITE)):
                circle(cr, tx, ty, rr, fill=c, stroke=INK, w=4)
            text(cr, "WHAT PEOPLE", tx, ty + 210, 34, face=FONT_HAND, bold=True)
            text(cr, "ACTUALLY WANT", tx, ty + 250, 34, face=FONT_HAND, bold=True)
            k = ease(prog(T, s("c5_07") + 0.8, 2.0))
            off = lerp(260, 0, k) * math.cos(T * 2 * (1 - k))
            arrow(cr, 640, 560, tx - 20, ty + off, 9, BLUE, head=34, dash=[18, 12])
            if k >= 0.99:
                check(cr, tx, ty - 200, 2.0, p=prog(T, s("c5_07") + 2.8, 0.3))
            # the hero tuning the dial
            P.gear(cr, 1000, 860, 60, 10, T * (1 - k) * 2)
            p = sm.pose("type", x=1130, face=-1, smile=0.4 + 0.4 * k, brow=0.3)
            p = sm.on_ground(sm.idle(p, T, 3), 1000)
            sm.hero(cr, p)
            if T > t_int - 0.3:
                label_box(cr, "ALIGNED", tx, 260, 40, c=GREEN, scale=back(prog(T, t_int - 0.3, 0.4)))

    b.fx(st7, "whoosh", -8)
    b.fx(st7 + 0.8, "servo", -12, dur=2.0)
    b.fx(t_int - 0.3, "ding", -8)

    # ------------------------------------------------------------ 8. famous math problems
    st8 = s("c5_08") - 0.2
    probs = [("P = NP ?", 360), ("Riemann Hypothesis ?", 480), ("Twin primes: infinite ?", 600)]

    @b.shot(st8, "slide", 0.4)
    def math_probs(cr, t, d, T):
        card(cr, t, 7, "UNSOLVED MATH", T)
        with ken(cr, t, d, 1.0, 1.04):
            P.chalkboard(cr, 820, 520, 1100, 560)
            for i, (pr, y) in enumerate(probs):
                typewriter(cr, pr, 330, y, prog(t, 0.3 + i * 0.6, 0.8), 64, c=(0.95, 0.95, 0.92), face=FONT_HAND,
                           cursor=False)
            k = prog(T, w("c5_08", "fun"), 0.4)
            stamp(cr, "JUST FOR FUN", 1050, 730, T - w("c5_08", "fun"), 56, c=YELLOW, rot=-0.08)
            p = sm.pose("write", x=1500, face=-1, smile=0.8, a2f=-10 + 15 * math.sin(T * 8))
            p = sm.on_ground(sm.idle(p, T, 4), 1000)
            sm.hero(cr, p)
            del k

    b.fx(st8, "whoosh", -8)
    b.fx(st8 + 0.3, "chalk", -10, dur=2.0)
    b.fx(w("c5_08", "fun"), "stamp", -8)

    # ------------------------------------------------------------ 9. notebook and coffee
    st9 = s("c5_09") - 0.2
    t_mug = w("c5_09", "coffee")

    @b.shot(st9, "fade", 0.35)
    def notebook(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.05):
            P.desk(cr, 860, 920, 900)
            pg = (T * 3) % 1
            P.notebook(cr, 760, 660, 1.3, pages=pg, t=T)
            cnt = 1 + int(max(0, T - t_mug) * 4)
            P.coffee(cr, 1180, 770, 1.1, T, level=1 - ((T * 2) % 1) * 0.8)
            for i in range(min(cnt, 9)):
                P.coffee(cr, 1350 + (i % 3) * 70, 770 - (i // 3) * 0, 0.45, T, steam=False, level=0)
            if T > t_mug:
                label_box(cr, f"COFFEE #{cnt + 3}", 1290, 520, 40, c=ORANGE, scale=1.0)
            p = sm.pose("write", x=480, face=1, a1f=75, a2f=20, eye=1.25, smile=0.9, brow=0.4)
            p = sm.apply(p, a2f=20 + 20 * math.sin(T * 16))
            p = sm.on_ground(sm.idle(p, T, 5), 920)
            p["x"] += math.sin(T * 50) * 1.5
            sm.hero(cr, p)
            text(cr, "RECORD TIME!", 760, 300, 64, face=FONT_TITLE, c=BLUE, rot=-0.04, a=eout(prog(t, 0.2, 0.4)))

    b.fx(st9, "page", -10)
    b.fx(st9 + 0.4, "scribble", -10, dur=2.5)
    b.fx(t_mug, "pour", -8)

    # ------------------------------------------------------------ 10. reality knocks
    st10 = s("c5_10") - 0.25
    t_knock = w("c5_10", "knocks")
    t_open = e("c5_10") + 0.1

    def reality(cr, x, y, T, a=1.0):
        p = sm.pose("hips", x=x, face=-1, s=1.2, smile=-0.2, brow=0.6)
        p = sm.on_ground(sm.idle(p, T, 6), y)
        J = sm.draw(cr, p, acc=("tie", "glasses"), ink=(0.25, 0.25, 0.28), alpha=a)
        label_box(cr, "REALITY", x, y - 470, 40, c=WHITE, bg=(0.25, 0.25, 0.28), a=a)
        return J

    @b.shot(st10, "fade", 0.3)
    def knock(cr, t, d, T):
        paper(cr, (0.93, 0.92, 0.89))
        op = ease(prog(T, t_open, 0.5))
        shk = sum(max(0, 1 - abs(T - (t_knock + i * 0.28)) * 8) for i in range(3))
        with ken(cr, t, d, 1.0, 1.06, 1100, 560):
            rect(cr, -300, 900, W + 600, 480, fill=(0.82, 0.78, 0.72))
            ground(cr, 900, x0=-300, x1=W + 300)
            if op > 0:
                reality(cr, 1250, 900, T, op)
            P.door(cr, 1250 + math.sin(T * 80) * 4 * shk, 900, 1.3, open_=op, light=(1.0, 0.95, 0.8))
            for i in range(3):
                kk = prog(T, t_knock + i * 0.28, 0.3)
                if 0 < kk < 1:
                    text(cr, "KNOCK", 1250 + (i - 1) * 170, 420 - i * 30, 54, face=FONT_TITLE, c=RED, a=1 - kk,
                         scale=lerp(0.8, 1.2, kk))
            p = sm.pose("surprised" if T > t_knock else "write", x=600, face=1, eye=1.2)
            p = sm.on_ground(sm.idle(p, T, 7), 900)
            sm.hero(cr, p)
            P.notebook(cr, 380, 820, 0.6, pages=1.0)

    for i in range(3):
        b.fx(t_knock + i * 0.28, "knock", -2)
    b.fx(t_open, "door", -8)

    # ------------------------------------------------------------ 11. what ideas need
    st11 = s("c5_11") - 0.2
    t_plant, t_med = w("c5_11", "power plant"), w("c5_11", "medicine")
    t_list = w("c5_11", "ideas have")
    items = [("TESTED", "tested"), ("FUNDED", "funded"), ("BUILT", "built"), ("SAFE & ETHICAL", "safety"),
             ("EXPLAINED", "explained")]

    @b.shot(st11, "fade", 0.35)
    def needs(cr, t, d, T):
        paper(cr)
        k_list = ease(prog(T, t_list - 0.2, 0.5))
        with ken(cr, t, d, 1.0, 1.03):
            if k_list < 1:
                with group(cr, 1 - k_list):
                    # idea != power plant ; formula != medicine
                    P.lightbulb(cr, 420, 380, 0.9, on=1, t=T)
                    text(cr, "≠", 700, 380, 140, face="DejaVu Sans", c=RED, a=prog(T, t_plant - 0.5, 0.3))
                    if T > t_plant - 0.5:
                        with xform(cr, 1000, 470, 1.0):
                            rect(cr, -150, -160, 300, 160, fill=LIGHT, stroke=INK, lw=5)
                            for k in (-1, 1):
                                polyline(cr, [(k * 60 - 40, -160), (k * 60 - 25, -330), (k * 60 + 25, -330),
                                              (k * 60 + 40, -160)], 5, INK, closed=True, fill=WHITE)
                                P.cloud(cr, k * 60, -370 - 20 * math.sin(T * 2 + k), 0.4, c=LIGHT)
                        text(cr, "POWER PLANT", 1000, 540, 34, face=FONT_HAND, bold=True)
                    if T > t_med - 0.5:
                        text(cr, "E = f(x, y)", 420, 760, 64, face=FONT_SERIF, italic=True)
                        text(cr, "≠", 700, 760, 140, face="DejaVu Sans", c=RED)
                        rrect(cr, 930, 690, 140, 170, 16, fill=WHITE, stroke=INK, lw=5)
                        rect(cr, 920, 660, 160, 40, fill=RED, stroke=INK, lw=5)
                        text(cr, "MEDICINE", 1000, 900, 34, face=FONT_HAND, bold=True)
            if k_list > 0:
                with group(cr, k_list):
                    text(cr, "EVERY IDEA STILL NEEDS TO BE...", 820, 170, 54, face=FONT_TITLE)
                    for i, (lab, word) in enumerate(items):
                        kk = prog(T, w("c5_11", word), 0.35)
                        y = 330 + i * 120
                        rrect(cr, 360, y - 40, 80, 80, 12, fill=WHITE, stroke=INK, lw=5, a=1)
                        text(cr, lab, 480, y, 60, face=FONT_TITLE, align="left", a=0.25 + 0.75 * clamp(kk * 2))
                        if kk > 0:
                            check(cr, 400, y, 1.7, p=kk)
                    J = reality(cr, 1500, 980, T)
                    hx, hy = J["hand_f"]
                    rrect(cr, hx - 20, hy - 70, 100, 130, 8, fill=(0.75, 0.6, 0.45), stroke=INK, lw=4)
                    rect(cr, hx - 5, hy - 55, 70, 100, fill=WHITE)

    b.fx(t_plant - 0.5, "pop", -10)
    b.fx(t_med - 0.5, "pop", -10)
    for lab, word in items:
        b.fx(w("c5_11", word), "check", -8)

    # ------------------------------------------------------------ 12. others join you
    st12 = s("c5_12") - 0.2
    team = [("ENGINEER", "engineer", ("hardhat",), 560), ("DOCTOR", "doctor", ("labcoat", "badge"), 1360),
            ("TEACHER", "teacher", ("bun", "glasses"), 320), ("PROGRAMMER", "programmer", ("headset",), 1600)]

    @b.shot(st12, "fade", 0.35)
    def join(cr, t, d, T):
        paper(cr, (0.96, 0.95, 0.91))
        with ken(cr, t, d, 1.05, 1.0, CX, 600):
            ground(cr, 900, x0=-300, x1=W + 300)
            for i, (lab, word, acc, x) in enumerate(team):
                tj = w("c5_12", word) - 0.6
                k = ease(prog(T, tj, 0.9))
                if k <= 0:
                    continue
                side = -1 if x < CX else 1
                xx = lerp(x + side * 900, x, k)
                p = sm.walk(sm.pose(x=xx, face=-side), T, 1.0) if k < 1 else sm.pose("wave", x=xx, face=-side, smile=0.9)
                if k >= 1:
                    p = sm.apply(p, a2f=42 + 20 * math.sin(T * 9 + i))
                p = sm.on_ground(p, 900)
                sm.draw(cr, p, acc=acc)
                label_box(cr, lab, xx, 480, 32, c=INK, scale=back(prog(T, tj + 0.7, 0.3)))
            p = sm.pose("cheer" if T > w("c5_12", "programmer") else "present", x=CX, face=1, smile=0.9)
            p = sm.on_ground(sm.idle(p, T, 8), 900)
            sm.hero(cr, p)

    for lab, word, acc, x in team:
        b.fx(w("c5_12", word) - 0.6, "footsteps", -14, dur=0.9)
        b.fx(w("c5_12", word) + 0.1, "pop", -10)

    # ------------------------------------------------------------ 13. nobody builds a better world alone
    st13 = s("c5_13") - 0.3

    @b.shot(st13, "fade", 0.5)
    def together(cr, t, d, T):
        vgrad(cr, (0.98, 0.80, 0.55), (0.62, 0.80, 0.98))
        P.sun(cr, CX, 520, 120, T, rays=True)
        with ken(cr, t, d, 1.0, 0.9, CX, 560):
            P.globe(cr, CX, 1250, 620, T * 0.3)
            r = rng(5)
            accs = [("tuft",), ("hardhat",), ("labcoat", "badge"), ("bun", "glasses"), ("headset",), ("cap",),
                    ("ponytail",), ("beret",)]
            for i in range(8):
                a = -math.pi / 2 + (i - 3.5) * 0.17
                x = CX + math.cos(a) * 620
                y = 1250 + math.sin(a) * 620
                p = sm.pose("cheer" if (i + int(T * 2)) % 3 == 0 else "wave", x=0, face=1 if i < 4 else -1, s=0.7)
                p = sm.apply(p, a2f=40 + 20 * math.sin(T * 6 + i))
                with xform(cr, x, y, 1.0, a + math.pi / 2):
                    p = sm.on_ground(p, 0)
                    sm.draw(cr, p, acc=accs[i])
            text(cr, "NOBODY BUILDS IT ALONE", CX, 200, 70, face=FONT_TITLE, a=eout(prog(T, w("c5_13", "alone") - 0.5, 0.5)),
                 outline=WHITE, ow=8)
            del r

    b.fx(st13, "swell", -8, dur=3.0)
    b.fx(w("c5_13", "alone") - 0.5, "chime", -8)
    return b.result()
