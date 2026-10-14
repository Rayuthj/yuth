"""Chapter 2 - The First 24 Hours (0:40-1:40)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at, title_card
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

FLOOR = 870
WALL = (0.93, 0.92, 0.89)
SKY_DAWN = ((1.0, 0.80, 0.62), (0.75, 0.86, 0.98))


def rotated(cr, p, ang, px, py, **kw):
    """Draw a stickman rotated by `ang` around the pivot (px, py)."""
    with saved(cr):
        cr.translate(px, py)
        cr.rotate(ang)
        cr.translate(-px, -py)
        return sm.hero(cr, p, **kw)


def bedroom(cr, t, window_sky=SKY_DAWN, traffic=0.0, books=0.0):
    fill_bg(cr, WALL)
    rect(cr, -300, FLOOR, W + 600, H - FLOOR + 300, fill=(0.84, 0.80, 0.74))
    ground(cr, FLOOR, x0=-300, x1=W + 300)
    P.window(cr, 1450, 380, 420, 320, t, sky=window_sky[0], sky2=window_sky[1])
    if traffic > 0:
        cr.save()
        cr.rectangle(1240, 220, 420, 320)
        cr.clip()
        for i in range(3):
            x = 1240 + ((t * 160 + i * 170) % 600) - 90
            P.car(cr, x, 532, 0.45, c=[RED, BLUE, YELLOW][i], t=t)
        cr.restore()
    P.bookshelf(cr, 1830, FLOOR, 0.9, highlight=books, t=t)
    rect(cr, 120, 200, 180, 130, fill=WHITE, stroke=INK, lw=5)   # poster
    P.star_shape(cr, 210, 265, 40, fill=YELLOW, stroke=INK)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 0. title carries over
    @b.shot(0)
    def title_out(cr, t, d, T):
        title_card(cr, 2.65 + t)

    # ------------------------------------------------------------ 1. waking up
    t_ring = w("c2_01", "alarm")
    t_sit = w("c2_01", "rings") + 0.5
    t_diff = w("c2_01", "different")

    @b.shot(0.75, "zoom", 0.6)
    def wake(cr, t, d, T):
        ring = inout(T, t_ring, t_sit + 0.4, 0.15)
        with ken(cr, t, d, 1.08, 1.0, 760, 600):
            bedroom(cr, T)
            P.nightstand(cr, 1040, FLOOR)
            P.alarm_clock(cr, 1040, FLOOR - 190, 0.75, T, ring=ring)
            P.bed(cr, 560, FLOOR)
            k = ease(prog(T, t_sit, 0.6))
            p = sm.pose("stand", x=560, y=FLOOR - 112, face=1, a1f=lerp(0, 40, k), a2f=lerp(0, 30, k),
                        a1b=lerp(0, -10, k), smile=lerp(0.0, 0.2, k), l1f=lerp(0, 86, k), l1b=lerp(0, 82, k),
                        l2f=0.0, l2b=0.0)
            p["blink"] = 1.0 if T < t_ring + 0.2 else (sm.blink(T, 1) if T < t_diff else 0)
            if T >= t_diff:
                kd = ease(prog(T, t_diff, 0.3))
                p = sm.apply(p, eye=1 + 0.3 * kd, browy=0.8 * kd, smile=0.0, mo=0.3 * kd)
            rotated(cr, p, lerp(-math.pi / 2 + 0.06, 0, k), 560, FLOOR - 112)
            # blanket over legs
            rrect(cr, 540, FLOOR - 150, 260, 50, 16, fill=LIGHT, stroke=INK, lw=5)
            if T > t_diff:
                kd = prog(T, t_diff, 0.6)
                J = sm.joints(p)
                for i in range(8):
                    a = i / 8 * TAU
                    rr = 70 + 60 * eout(kd)
                    line(cr, 560 + math.cos(a) * rr, FLOOR - 112 - 170 + math.sin(a) * rr,
                         560 + math.cos(a) * (rr + 30), FLOOR - 112 - 170 + math.sin(a) * (rr + 30), 6, YELLOW,
                         1 - kd)
                del J

    b.fx(0.75, "whoosh", -8)
    b.fx(t_ring, "alarm", -8, dur=t_sit + 0.4 - t_ring)
    b.fx(t_sit, "swoosh", -12)
    b.fx(t_diff, "sparkle", -8)

    # ------------------------------------------------------------ 2. the clock's hidden rhythm
    st2 = s("c2_02") - 0.25
    t_rhythm = w("c2_02", "rhythm")
    t_inside = w("c2_02", "inside")

    @b.shot(st2, "fade", 0.35)
    def clock_close(cr, t, d, T):
        paper(cr, WALL)
        with ken(cr, t, d, 1.0, 1.08, 820, 540):
            k_r = prog(T, t_rhythm, 0.6)
            # rhythm waves pulse with every tick
            if k_r > 0:
                for j in range(4):
                    pts = []
                    for i in range(140):
                        x = i * 14
                        amp = 40 * (1 - j * 0.2) * math.exp(-((T % 1.0) * 3)) + 8
                        pts.append((x, 540 + (j - 1.5) * 120 + math.sin(x * 0.02 * (j + 1) - T * 4) * amp))
                    polyline(cr, pts, 4, [BLUE, CYAN, PURPLE, RED][j], 0.35 * k_r)
            k_in = ease(prog(T, t_inside, 1.0))
            cx, cy, R = 760, 540, 300
            P.clock(cr, cx, cy, R, T, hours=7, minutes=2, speed=1)
            if k_in > 0:
                # cut-away: gears inside, and smaller clocks inside those
                cr.save()
                cr.arc(cx, cy, R * 0.82 * k_in, 0, TAU)
                cr.clip()
                fill_bg(cr, (0.97, 0.94, 0.85))
                P.gear(cr, cx - 90, cy - 40, 110, 12, T * 0.6, fill=(1, 0.85, 0.5))
                P.gear(cr, cx + 105, cy + 30, 85, 10, -T * 0.6 * 12 / 10 + 0.15, fill=(0.8, 0.9, 1.0))
                P.gear(cr, cx - 10, cy + 160, 60, 8, T * 1.2, fill=(0.85, 1.0, 0.85))
                P.clock(cr, cx + 120, cy - 150, 60, T * 4, speed=1, seconds=True)
                P.clock(cr, cx - 160, cy + 140, 40, T * 8, speed=1)
                cr.restore()
                circle(cr, cx, cy, R * 0.82 * k_in, stroke=INK, w=5)
            # the hero leaning into frame, fascinated
            p = sm.pose("front", s=2.6, lw=5.5, face=-1, fo=0.7, eye=1.15, gx=-0.9, smile=0.55, browy=0.4)
            p = head_at(sm.idle(p, T, 2), 1500 - 40 * ease(t / d), 520)
            sm.hero(cr, p)

    for k in range(int(st2) + 1, int(s("c2_03"))):
        b.fx(k, "tick" if k % 2 else "tock", -6)

    # ------------------------------------------------------------ 3. everything is connected
    st3 = s("c2_03") - 0.25
    t_phone, t_traf, t_book, t_conn = (w("c2_03", "phone"), w("c2_03", "traffic"), w("c2_03", "books"),
                                       w("c2_03", "connected") - 0.4)

    @b.shot(st3, "fade", 0.35)
    def connected(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.05, CX, 560):
            bedroom(cr, T, traffic=prog(T, t_traf, 0.3), books=prog(T, t_book, 0.5))
            P.nightstand(cr, 760, FLOOR)
            P.alarm_clock(cr, 700, FLOOR - 190, 0.6, T)
            lit = prog(T, t_phone, 0.2)
            if lit > 0:
                glow(cr, 815, FLOOR - 140, 120, CYAN, 0.6 * lit)
            P.phone(cr, 815, FLOOR - 145, 0.35, T, lit=0.3 + 0.7 * lit, rot=-1.3)
            p = sm.pose("think", x=1030, face=1, gx=math.sin(T * 1.7), smile=0.5)
            p = sm.on_ground(sm.idle(p, T, 3), FLOOR)
            J = sm.hero(cr, p)
            k = prog(T, t_conn, 0.8)
            if k > 0:
                pts = [(815, FLOOR - 145), (700, FLOOR - 190), (1450, 380), (1830, FLOOR - 160), (210, 265)]
                hx, hy = J["head"]
                for i, (x, y) in enumerate(pts):
                    curve_arrow(cr, [(hx, hy), ((hx + x) / 2, min(hy, y) - 160), (x, y)], 5, YELLOW, head=0,
                                p=clamp(k * 1.5 - i * 0.1))
                    circle(cr, x, y, 22 * eout(k), stroke=YELLOW, w=6)
                glow(cr, hx, hy, 200, YELLOW, 0.5 * k)

    b.fx(t_phone, "ping", -8)
    b.fx(t_traf, "honk", -16)
    b.fx(t_conn, "sparkle", -6)
    b.fx(t_conn + 0.2, "zap", -12)

    # ------------------------------------------------------------ 4. puzzles before breakfast
    st4 = s("c2_04") - 0.2
    t_sud, t_rub, t_toast = w("c2_04", "sudoku"), w("c2_04", "rubik"), w("c2_04", "pops", lead=0.0)

    @b.shot(st4, "slide", 0.4)
    def puzzles(cr, t, d, T):
        fill_bg(cr, (0.97, 0.95, 0.90))
        rect(cr, 0, 780, W, 300, fill=(0.88, 0.84, 0.78))
        ground(cr, 780)
        P.clock(cr, 1700, 190, 80, T, hours=12, minutes=0, speed=60)
        text(cr, "LUNCH", 1700, 300, 32, face=FONT_HAND, bold=True)
        P.sudoku(cr, 450, 470, 420, fill=ease(prog(T, t_sud - 0.2, 1.1)))
        if T > t_sud + 0.9:
            check(cr, 680, 280, 1.6, p=prog(T, t_sud + 0.9, 0.3))
        k_c = prog(T, t_rub, 1.2)
        P.rubiks(cr, 1000, 560, 0.85, solved=ease(k_c), rot=math.sin(T * 9) * 0.25 * (1 - k_c) if k_c > 0 else 0)
        if k_c >= 1:
            check(cr, 1100, 420, 1.4, p=prog(T, t_rub + 1.2, 0.3))
        P.toaster(cr, 1450, 780, 1.0, pop=bounce(prog(T, t_toast, 0.5)) * (1 if T < t_toast + 1.4 else 1))
        p = sm.pose("type", x=880, face=1, smile=0.7, gx=0.6)
        p = sm.apply(p, a2f=22 + 15 * math.sin(T * 12), a2b=32 + 15 * math.sin(T * 12 + 1))
        p = sm.on_ground(sm.idle(p, T, 4), 1000)
        sm.hero(cr, p)
        rect(cr, 620, 780, 900, 30, fill=WHITE, stroke=INK, lw=5)

    b.fx(st4, "whoosh", -8)
    b.fx(t_sud - 0.2, "scribble", -10, dur=1.1)
    b.fx(t_rub, "clicks", -10, dur=1.2)
    b.fx(t_toast, "toaster", -6)

    # ------------------------------------------------------------ 5. real talk
    st5 = s("c2_05") - 0.15

    @b.shot(st5, "cut")
    def honest(cr, t, d, T):
        paper(cr, PAPER2)
        with ken(cr, t, d, 1.0, 1.06, CX, 520):
            p = sm.pose("front", s=1.9, smile=0.0, brow=-0.2, browy=0.3)
            p = sm.mix(p, sm.pose("point_up", s=1.9, fo=0.0, smile=0.1, browy=0.4), ease(prog(t, 0.1, 0.35)))
            p = head_at(sm.idle(p, T, 5), CX - 120, 360)
            sm.hero(cr, p)
            stamp(cr, "REAL TALK", 1350, 330, t - 0.25, 70, c=RED, rot=0.08)

    b.fx(st5, "scratch", -4)
    b.fx(st5 + 0.25, "stamp", -8)

    # ------------------------------------------------------------ 6. what IQ tests measure
    st6 = s("c2_06") - 0.2
    t_avg, t_160 = w("c2_06", "100", lead=0.2), w("c2_06", "160", lead=0.25)
    base_y, cx0, unit = 780, 760, 9.0   # 1 IQ point = 9 px

    def iq_x(v):
        return cx0 + (v - 100) * unit

    def axis(cr, T, k_draw):
        P.bell_curve(cr, cx0, base_y, w=unit * 15 * 8, h=420, p=k_draw)
        for v in (40, 70, 100, 130, 160):
            text(cr, str(v), iq_x(v), base_y + 40, 34, face=FONT_HAND, bold=True, a=k_draw)

    @b.shot(st6, "fade", 0.35)
    def curve(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.04, CX, 560):
            text(cr, "IQ SCORES", 300, 160, 54, face=FONT_TITLE, align="left", a=eout(prog(t, 0, 0.4)))
            axis(cr, T, eout(prog(t, 0.1, 1.4)))
            k = prog(T, t_avg, 0.5)
            if k > 0:
                line(cr, iq_x(100), base_y, iq_x(100), base_y - 440 * eout(k), 6, BLUE, dash=[14, 10])
                label_box(cr, "AVERAGE = 100", iq_x(100), base_y - 480, 36, c=BLUE, scale=back(k))
            k2 = prog(T, t_160, 0.5)
            if k2 > 0:
                x160 = iq_x(160)
                rect(cr, x160, base_y - 460, 20, 460 * eout(k2), fill=INK)
                text(cr, "MOST TESTS", x160 + 30, base_y - 250, 36, face=FONT_HAND, bold=True, a=k2, align="left")
                text(cr, "STOP HERE", x160 + 30, base_y - 208, 36, face=FONT_HAND, bold=True, a=k2, align="left")
            p = sm.pose("point", x=1640, face=-1, smile=0.4)
            p = sm.on_ground(sm.idle(p, T, 6), 940)
            sm.hero(cr, p)

    b.fx(st6 + 0.1, "draw", -10, dur=1.4)
    b.fx(t_avg, "pop", -8)
    b.fx(t_160, "thud", -6)

    # ------------------------------------------------------------ 7. 500 is science fiction
    st7 = s("c2_07") - 0.2
    t_fun = w("c2_07", "fun")

    @b.shot(st7, "cut")
    def scifi(cr, t, d, T):
        k = ease(prog(t, 0.0, 2.6))
        cam_x = lerp(cx0 + 300, iq_x(500), k)
        night = clamp((k - 0.3) * 1.6)
        fill_bg(cr, lerpc(PAPER, (0.05, 0.05, 0.12), night))
        if night > 0:
            stars(cr, T, n=200, alpha=night)
        with camera(cr, lerp(1.0, 0.9, k), cam_x, 560):
            axis(cr, T, 1.0)
            line(cr, iq_x(165), base_y, iq_x(520), base_y, 6, lerpc(INK, WHITE, night), dash=[20, 18])
            for v in (200, 300, 400):
                text(cr, str(v), iq_x(v), base_y + 40, 34, face=FONT_HAND, bold=True, c=lerpc(INK, WHITE, night))
            x5 = iq_x(500)
            line(cr, x5, base_y, x5, base_y - 260, 6, WHITE)
            polyline(cr, [(x5, base_y - 260), (x5 + 110, base_y - 230), (x5, base_y - 200)], 4, INK, closed=True,
                     fill=YELLOW)
            text(cr, "500", x5, base_y + 46, 54, face=FONT_TITLE, c=YELLOW)
            # a little UFO for the hero
            uy = base_y - 420 + math.sin(T * 2) * 14
            ux = x5 - 260
            glow(cr, ux, uy + 40, 140, CYAN, 0.35)
            polyline(cr, [(ux - 60, uy + 120), (ux + 60, uy + 120), (ux + 25, uy + 30), (ux - 25, uy + 30)], 0, INK,
                     closed=True, fill=CYAN, fa=0.25)
            p = sm.pose("wave", x=ux, s=0.45, smile=0.9)
            p = sm.apply(p, a2f=42 + 25 * math.sin(T * 10))
            p = sm.on_ground(p, uy + 8)
            sm.hero(cr, p, ink=WHITE, fill=(0.1, 0.1, 0.15))
            ellipse(cr, ux, uy + 10, 120, 26, fill=(0.75, 0.78, 0.85), stroke=WHITE, w=4)
            arc(cr, ux, uy + 4, 60, math.pi, TAU, 4, WHITE, 0.8)
        kf = prog(T, t_fun - 0.6, 0.5)
        if kf > 0:
            text(cr, "PURE SCIENCE FICTION", CX, 170, 80, face=FONT_TITLE, c=YELLOW, a=kf, scale=lerp(1.3, 1, eout(kf)),
                 outline=(0.2, 0.1, 0.3), ow=8)

    b.fx(st7, "whoosh", -6)
    b.fx(st7 + 1.4, "ufo", -12, dur=2.5)
    b.fx(t_fun - 0.6, "shimmer", -8)

    # ------------------------------------------------------------ 8. what it doesn't give you
    st8 = s("c2_08") - 0.2
    items = [("PERFECT MEMORY", "memory", 420), ("INSTANT KNOWLEDGE", "instant", 960), ("SUPERPOWERS", "superpowers", 1500)]
    t_book = w("c2_08", "you still")

    def icon(cr, i, x, y, T):
        if i == 0:
            P.brain(cr, x, y, 0.9)
            rrect(cr, x + 50, y + 30, 70, 40, 6, fill=LIGHT, stroke=INK, lw=4)
            text(cr, "∞ GB", x + 85, y + 50, 22, face=FONT_BOLD)
        elif i == 1:
            circle(cr, x, y - 20, 70, fill=WHITE, stroke=INK, w=5)
            arrow(cr, x, y - 230, x, y - 100, 10, BLUE, head=34)
            rrect(cr, x - 100, y + 80, 200, 30, 10, stroke=INK, lw=4)
            rrect(cr, x - 96, y + 84, 192 * ((T * 0.8) % 1), 22, 8, fill=GREEN)
        else:
            polyline(cr, [(x + 20, y - 130), (x - 50, y + 10), (x, y + 10), (x - 30, y + 130), (x + 60, y - 20),
                          (x + 10, y - 20)], 5, INK, closed=True, fill=YELLOW)

    @b.shot(st8, "fade", 0.35)
    def limits(cr, t, d, T):
        paper(cr)
        k_out = ease(prog(T, t_book - 0.3, 0.5))
        with ken(cr, t, d, 1.0, 1.03):
            with group(cr, 1 - k_out):
                text(cr, "A POWERFUL BRAIN IS NOT...", CX, 150, 60, face=FONT_TITLE, a=eout(prog(t, 0, 0.4)))
                for i, (lab, word, x) in enumerate(items):
                    tw0 = w("c2_08", word)
                    k = back(prog(T, tw0, 0.4))
                    if k > 0:
                        with xform(cr, x, 500, max(0.01, k)):
                            icon(cr, i, 0, 0, T)
                        text(cr, lab, x, 720, 40, face=FONT_BOLD, a=clamp(k))
                        cross(cr, x, 480, 4.2, p=prog(T, tw0 + 0.35, 0.3), w=14)
            if k_out > 0:
                with group(cr, k_out):
                    p = sm.pose("sit", x=820, face=1, a1f=60, a2f=50, a1b=50, a2b=60, gy=0.7, smile=-0.1, brow=-0.3)
                    p = sm.on_ground(sm.idle(p, T, 7, 0.5), 880)
                    J = sm.hero(cr, p)
                    hx, hy = J["hand_f"]
                    P.book(cr, hx + 105, hy - 10, 0.8, open_=1.0, rot=-0.15)
                    ground(cr, 880, x0=500, x1=1400)
                    # pile of books still to read
                    for i in range(6):
                        P.book(cr, 1250, 850 - i * 34, 0.9, c=[RED, BLUE, GREEN, PURPLE, YELLOW, ORANGE][i],
                               rot=math.pi / 2 + (i % 2) * 0.06)
                    text(cr, "STILL HAVE TO READ THE BOOK", CX, 160, 56, face=FONT_TITLE)
                    circle(cr, J["head"][0] + 50, J["head"][1] - 30, 9, fill=CYAN)

    for lab, word, x in items:
        b.fx(w("c2_08", word), "pop", -8)
        b.fx(w("c2_08", word) + 0.35, "buzz", -12)
    b.fx(t_book, "page", -6)
    b.fx(t_book + 1.0, "page", -8)

    # ------------------------------------------------------------ 9. what actually changes
    st9 = s("c2_09") - 0.2
    gauges = [("REASONING", "reason", 480), ("LEARNING", "learn", 960), ("CONNECTING", "connect", 1440)]

    @b.shot(st9, "fade", 0.35)
    def change(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.05):
            text(cr, "WHAT CHANGES", CX, 170, 60, face=FONT_TITLE)
            for lab, word, x in gauges:
                k = ease(prog(T, w("c2_09", word), 0.6))
                y = 560
                arc(cr, x, y, 170, math.pi, TAU, 28, LIGHT)
                arc(cr, x, y, 170, math.pi, math.pi + math.pi * 0.98 * k, 28, [BLUE, GREEN, YELLOW][gauges.index((lab, word, x))])
                a = math.pi + math.pi * (0.05 + 0.93 * k) + math.sin(T * 30) * 0.02 * k
                line(cr, x, y, x + math.cos(a) * 150, y + math.sin(a) * 150, 8, INK)
                circle(cr, x, y, 16, fill=INK)
                text(cr, lab, x, y + 80, 40, face=FONT_BOLD)
                if k > 0.9:
                    text(cr, "MAX", x, y - 60, 30, face=FONT_HAND, bold=True, c=RED)

    for lab, word, x in gauges:
        b.fx(w("c2_09", word), "rise", -10)

    # ------------------------------------------------------------ 10. sunset full of questions
    st10 = s("c2_10") - 0.4
    t_q = w("c2_10", "questions")

    @b.shot(st10, "fade", 0.6)
    def sunset(cr, t, d, T):
        vgrad(cr, (0.30, 0.25, 0.50), (1.0, 0.62, 0.35))
        P.sun(cr, 1300, 760, 110, T, c=(1.0, 0.82, 0.45), rays=False)
        with ken(cr, t, d, 1.0, 1.06, CX, 600):
            P.skyline(cr, -40, 900, W + 80, 420, seed=31, fill=(0.17, 0.13, 0.22), lit=True, t=T)
            k = prog(T, t_q, 3.0)
            r = rng(9)
            n = int(60 * k)
            for i in range(n):
                x = r.uniform(80, W - 80)
                y0 = r.uniform(700, 880)
                rise = (T - t_q) * r.uniform(40, 90)
                y = y0 - rise - i * 3
                if y < -50:
                    continue
                P.question_mark(cr, x + math.sin(T + i) * 10, y, r.uniform(26, 64), c=(1.0, 0.9, 0.6),
                                a=clamp((T - t_q - i * 0.04) * 2) * 0.85)
            rect(cr, 0, 900, W, 180, fill=(0.10, 0.08, 0.13))
            p = sm.pose("front", x=520, fo=0.6, face=1, gy=-0.6, smile=0.4, a1f=8, a1b=-8)
            p = sm.on_ground(sm.idle(p, T, 8), 900)
            sm.hero(cr, p, ink=(0.08, 0.06, 0.1), fill=(0.98, 0.72, 0.45))

    b.fx(t_q, "shimmer", -8)
    b.fx(t_q + 0.8, "chime", -12)
    return b.result()
