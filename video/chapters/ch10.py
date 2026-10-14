"""Chapter 10 - The Final Revelation (9:00-10:00)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, dark, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

DARK_TAG = True
SKY1 = (0.03, 0.035, 0.08)
SKY2 = (0.08, 0.07, 0.16)
STAR = (0.92, 0.94, 1.0)
NFILL = (0.05, 0.055, 0.10)

# constellation shapes (unit coordinates)
SHAPES = {
    "book": [(-1, -0.6), (0, -0.4), (1, -0.6), (1, 0.6), (0, 0.8), (-1, 0.6), (-1, -0.6), None, (0, -0.4), (0, 0.8)],
    "pattern": [(-1, 0.3), (-0.5, -0.6), (0, 0.1), (0.5, -0.7), (1, 0.2), None, (-0.5, -0.6), (0.5, -0.7), None,
                (0, 0.1), (0, 0.9)],
    "bulb": [(-0.35, 0.5), (-0.6, 0), (-0.6, -0.5), (0, -0.9), (0.6, -0.5), (0.6, 0), (0.35, 0.5), (0.35, 0.9),
             (-0.35, 0.9), (-0.35, 0.5)],
    "question": [(-0.5, -0.5), (-0.3, -0.85), (0.2, -0.95), (0.55, -0.6), (0.4, -0.2), (0, 0.05), (0, 0.4), None,
                 (0, 0.85)],
    "heart": [(0, 0.8), (-0.85, -0.05), (-0.75, -0.6), (-0.35, -0.75), (0, -0.4), (0.35, -0.75), (0.75, -0.6),
              (0.85, -0.05), (0, 0.8)],
    "clock": [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), None,
              (0, 0), (0, -0.6), None, (0, 0), (0.45, 0.2)],
    "path": [(-1, 0.9), (-0.4, 0.4), (-0.1, 0.4), (0.3, -0.2), (0.4, -0.6), (1, -0.9), None, (0.3, -0.2), (0.9, 0.1)],
}


def constellation(cr, shape, cx, cy, size, k, T, c=STAR, a=1.0, label=None, seed=0):
    pts = SHAPES[shape]
    segs, cur = [], []
    for p in pts:
        if p is None:
            segs.append(cur)
            cur = []
        else:
            cur.append((cx + p[0] * size, cy + p[1] * size))
    segs.append(cur)
    total = sum(max(0, len(sg) - 1) for sg in segs)
    done = k * total
    for sg in segs:
        if len(sg) >= 2:
            n = len(sg) - 1
            partial_poly(cr, sg, clamp(done / n), 2.5, c, 0.55 * a)
            done -= n
    seen = set()
    for i, sg in enumerate(segs):
        for j, (x, y) in enumerate(sg):
            key = (round(x), round(y))
            if key in seen:
                continue
            seen.add(key)
            tw = 0.7 + 0.3 * math.sin(T * 2.3 + x * 0.05 + y * 0.03)
            if k > 0:
                glow(cr, x, y, 26, c, 0.35 * a * clamp(k * 3) * tw)
                circle(cr, x, y, 4.5, fill=WHITE, a=a * clamp(k * 3) * tw)
    if label and k > 0.6:
        text(cr, label, cx, cy + size + 50, 34, face=FONT_BOLD, c=c, a=a * clamp((k - 0.6) * 3))


def sky(cr, T, star_a=1.0, galaxies=True, qmarks=0.6):
    vgrad(cr, SKY1, SKY2)
    stars(cr, T, n=380, alpha=star_a, seed=11)
    if galaxies:
        P.galaxy(cr, 1500, 230, 230, T, seed=4, rot=0.4, a=0.8 * star_a)
        P.galaxy(cr, 380, 330, 150, T, seed=8, rot=-0.6, a=0.6 * star_a, c=(1.0, 0.85, 0.8))
    if qmarks > 0:
        r = rng(13)
        for i in range(14):
            x = r.uniform(80, W - 80)
            y = r.uniform(80, 700)
            P.question_mark(cr, x + math.sin(T * 0.3 + i) * 12, y, r.uniform(26, 58), c=(0.7, 0.75, 1.0),
                            a=qmarks * (0.25 + 0.2 * math.sin(T * 0.8 + i)))


def horizon(cr):
    rect(cr, -200, 930, W + 400, 400, fill=(0.02, 0.02, 0.04))
    P.hill(cr, CX, 945, 1600, 70, c=(0.02, 0.02, 0.04))


def small_hero(cr, T, x=CX, gy=-0.9, smile=0.3, **kw):
    p = sm.pose("front", x=x, s=0.8, fo=0.2, gy=gy, smile=smile, **kw)
    p = sm.on_ground(sm.idle(p, T, 3, 0.6), 912)
    return sm.hero(cr, p, ink=(0.9, 0.9, 1.0), fill=NFILL)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. return to the dark
    @b.shot(0, "black", 0.8)
    def universe(cr, t, d, T):
        k = ease(prog(t, 0, 2.0))
        with camera(cr, lerp(1.15, 1.0, k), CX, lerp(760, 560, ease(t / d))):
            sky(cr, T, star_a=k)
            horizon(cr)
            small_hero(cr, T)

    b.fx(0.1, "shimmer", -12)

    # ------------------------------------------------------------ 2. constellations of what you could do
    st2 = s("c10_02") - 0.3
    cons = [("book", "LEARN FASTER", "learn", 480, 380), ("pattern", "SEE PATTERNS", "recognize", 960, 300),
            ("bulb", "IMAGINE SOLUTIONS", "imagine", 1440, 380)]

    @b.shot(st2, "fade", 0.6)
    def constellations(cr, t, d, T):
        with camera(cr, lerp(1.0, 1.04, t / d), CX, 540):
            sky(cr, T, qmarks=0.3)
            for shape, lab, word, x, y in cons:
                k = ease(prog(T, w("c10_02", word), 1.4))
                constellation(cr, shape, x, y, 120, k, T, label=lab, c=(0.85, 0.9, 1.0))
            horizon(cr)
            small_hero(cr, T)

    for shape, lab, word, x, y in cons:
        b.fx(w("c10_02", word), "sparkle", -14)

    # ------------------------------------------------------------ 3. what you wouldn't get
    st3 = s("c10_03") - 0.3
    t_imm = s("c10_04")
    t_life = s("c10_05")
    unknowns = [("heart", "every person happy", 480), ("clock", "future holds", 960), ("path", "your life", 1440)]

    @b.shot(st3, "fade", 0.5)
    def limits(cr, t, d, T):
        with camera(cr, lerp(1.0, 1.05, t / d), CX, 520):
            sky(cr, T, qmarks=0.9)
            k1 = prog(T, s("c10_03"), 0.5) * (1 - prog(T, t_life - 0.3, 0.4))
            k2 = prog(T, t_imm, 0.5) * (1 - prog(T, t_life - 0.3, 0.4))
            if k1 > 0:
                text(cr, "KNOW EVERYTHING", CX, 300, 64, face=FONT_TITLE, c=STAR, a=k1)
                cross(cr, CX + 400, 300, 1.2, p=prog(T, s("c10_03") + 0.8, 0.3), a=k1)
            if k2 > 0:
                text(cr, "IMMUNE TO MISTAKES", CX, 430, 64, face=FONT_TITLE, c=STAR, a=k2)
                cross(cr, CX + 450, 430, 1.2, p=prog(T, t_imm + 0.8, 0.3), a=k2)
            for shape, lab, x in unknowns:
                k = ease(prog(T, w("c10_05", lab.split()[0] if lab != "your life" else "your life"), 1.2))
                if k > 0:
                    constellation(cr, shape, x, 360, 110, k, T, c=(1.0, 0.85, 0.7))
                    P.question_mark(cr, x + 150, 250, 70, c=YELLOW, a=k * 0.8)
            horizon(cr)
            small_hero(cr, T, gy=-0.7, smile=0.1)

    b.fx(s("c10_03") + 0.8, "soft_x", -14)
    b.fx(t_imm + 0.8, "soft_x", -14)
    for shape, lab, x in unknowns:
        b.fx(w("c10_05", lab.split()[0] if lab != "your life" else "your life"), "sparkle", -14)

    # ------------------------------------------------------------ 4. what intelligence can do
    st4 = s("c10_06") - 0.3
    t_ans, t_world, t_fut = w("c10_06", "answer"), s("c10_07"), s("c10_08")

    @b.shot(st4, "fade", 0.5)
    def light(cr, t, d, T):
        with camera(cr, lerp(1.0, 1.04, t / d), CX, 540):
            sky(cr, T, qmarks=0.0)
            J = sm.joints(sm.on_ground(sm.pose("front", x=CX, s=0.8), 912))
            hx, hy = J["head"]
            ka = ease(prog(T, t_ans - 0.2, 0.8))
            r = rng(13)
            for i in range(14):
                x = r.uniform(80, W - 80)
                y = r.uniform(80, 700)
                sz = r.uniform(26, 58)
                lit = clamp(ka * 2 - abs(x - CX) / 900)
                sym = "!" if lit > 0.5 else "?"
                P.question_mark(cr, x, y, sz, c=lerpc((0.7, 0.75, 1.0), YELLOW, lit), a=0.35 + 0.5 * lit) if sym == "?" \
                    else text(cr, "!", x, y, sz, face=FONT_BOLD, c=YELLOW, a=0.9)
            if ka > 0:
                cr.move_to(hx - 20, hy)
                cr.line_to(hx + 20, hy)
                cr.line_to(CX + 700, 60)
                cr.line_to(CX - 700, 60)
                cr.close_path()
                src(cr, YELLOW, 0.08 * ka)
                cr.fill()
            kw_ = ease(prog(T, t_world, 1.0))
            if kw_ > 0:
                P.globe(cr, 1500, 420, 110 * kw_ + 1, T)
                for j in range(3):
                    ellipse(cr, 1500, 420, (170 + j * 50) * kw_, (50 + j * 15) * kw_, stroke=CYAN, w=2, a=0.5 * kw_)
                    a = T * (1.2 - j * 0.3) + j
                    circle(cr, 1500 + math.cos(a) * (170 + j * 50) * kw_, 420 + math.sin(a) * (50 + j * 15) * kw_, 6,
                           fill=CYAN, a=kw_)
            kf = prog(T, t_fut, 1.4)
            if kf > 0:
                pts = bezier_pts([(200, 650), (500, 250), (800, 200), (1000, 180)], 40)
                n = max(2, int(40 * ease(kf)))
                polyline(cr, pts[:n], 4, WHITE, 0.6)
                glow(cr, *pts[n - 1], 60, WHITE, 0.7)
                P.star_shape(cr, *pts[n - 1], 18, fill=YELLOW)
            horizon(cr)
            small_hero(cr, T, smile=0.5)

    b.fx(t_ans - 0.2, "shimmer", -12)
    b.fx(t_world, "sparkle", -14)
    b.fx(t_fut, "whoosh", -14)

    # ------------------------------------------------------------ 5. possible vs. worth doing
    st5 = s("c10_09") - 0.3
    t_worth = w("c10_09", "worth")

    @b.shot(st5, "fade", 0.5)
    def worth(cr, t, d, T):
        vgrad(cr, SKY1, SKY2)
        stars(cr, T, n=120, alpha=0.5, seed=12)
        with camera(cr, lerp(1.0, 1.05, t / d), CX, 520):
            r = rng(3)
            kp = ease(prog(t, 0.2, 0.8))
            for i in range(160):
                a = r.uniform(0, TAU)
                rr = r.uniform(0, 260) ** 1.0
                x, y = 560 + math.cos(a) * rr, 430 + math.sin(a) * rr * 0.8
                circle(cr, x, y, r.uniform(1.5, 4), fill=STAR, a=kp * r.uniform(0.3, 1))
            text(cr, "WHAT'S POSSIBLE", 560, 800, 50, face=FONT_TITLE, c=STAR, a=kp)
            kw_ = ease(prog(T, t_worth - 0.2, 0.8))
            if kw_ > 0:
                glow(cr, 1360, 430, 260, (1.0, 0.75, 0.5), 0.55 * kw_)
                P.star_shape(cr, 1360, 430, 50 * kw_ + 1, fill=(1.0, 0.85, 0.5))
                text(cr, "WHAT'S WORTH DOING", 1360, 800, 50, face=FONT_TITLE, c=(1.0, 0.85, 0.5), a=kw_)
                text(cr, "≠", CX, 450, 140, face="DejaVu Sans", c=WHITE, a=kw_ * 0.8)

    b.fx(t_worth - 0.2, "chime", -12)

    # ------------------------------------------------------------ 6. the intelligence you already have
    st6 = s("c10_10") - 0.3
    t_already = w("c10_11", "already")
    t_choose = w("c10_11", "choose")

    @b.shot(st6, "fade", 0.6)
    def already(cr, t, d, T):
        k_dis = ease(prog(T, s("c10_10") + 1.2, 2.2))
        zoom = lerp(1.0, 1.9, ease(prog(T, s("c10_11"), e("c10_11") - s("c10_11") + 0.4)))
        with camera(cr, zoom, CX, lerp(540, 760, ease(prog(T, s("c10_11"), 3.0)))):
            sky(cr, T, qmarks=0.2, galaxies=False)
            # the giant 500 dissolving into stardust
            if k_dis < 1:
                text(cr, "500", CX, 360, 320, face=FONT_TITLE, c=YELLOW, a=0.5 * (1 - k_dis))
            r = rng(5)
            for i in range(90):
                x0, y0 = CX + r.uniform(-300, 300), 360 + r.uniform(-120, 120)
                ang = r.uniform(0, TAU)
                dd = k_dis * r.uniform(100, 700)
                circle(cr, x0 + math.cos(ang) * dd, y0 + math.sin(ang) * dd - k_dis * 100, 3, fill=YELLOW,
                       a=0.7 * math.sin(k_dis * math.pi))
            horizon(cr)
            ka = prog(T, t_choose - 0.3, 0.8)
            p = sm.pose("front", x=CX, s=0.8, fo=0.2, gy=-0.9 if ka <= 0 else 0.8, smile=0.3)
            if ka > 0:
                p = sm.mix(p, sm.apply(p, a1f=62, a2f=40, a1b=-62, a2b=-40, gy=0.9, gx=0.0, head=8), ease(ka))
            p = sm.on_ground(sm.idle(p, T, 3, 0.5), 912)
            J = sm.hero(cr, p, ink=(0.9, 0.9, 1.0), fill=NFILL)
            kl = prog(T, t_already - 0.4, 0.8)
            if kl > 0:
                mx = (J["hand_f"][0] + J["hand_b"][0]) / 2
                my = (J["hand_f"][1] + J["hand_b"][1]) / 2 - 12
                glow(cr, mx, my, 70, YELLOW, 0.8 * kl)
                circle(cr, mx, my, 9 * kl, fill=WHITE)

    b.fx(s("c10_10") + 1.2, "dissolve", -10, dur=2.0)
    b.fx(t_already - 0.4, "chime", -10)

    # ------------------------------------------------------------ 7. one question remains
    st7 = s("c10_12") - 0.3
    t_puzzle = w("c10_12", "puzzle")
    t_q = s("c10_13")

    @b.shot(st7, "fade", 0.6)
    def puzzle(cr, t, d, T):
        sky(cr, T, qmarks=0.0)
        kq = ease(prog(T, t_q - 0.4, 0.8))
        with camera(cr, lerp(1.0, 1.06, t / d), CX, 520):
            kp = ease(prog(T, t_puzzle - 1.0, 1.6))
            r = rng(21)
            for i in range(4):
                for j in range(3):
                    if (i, j) == (2, 1):
                        continue
                    hx, hy = 660 + i * 150, 270 + j * 150
                    sx, sy = r.uniform(-500, 500), r.uniform(-300, 300)
                    x, y = lerp(hx + sx, hx, kp), lerp(hy + sy, hy, kp)
                    rot = (1 - kp) * r.uniform(-2, 2)
                    with xform(cr, x, y, 1.0, rot):
                        rrect(cr, -70, -70, 140, 140, 14, fill=(0.25, 0.35, 0.65), stroke=STAR, lw=4, a=0.9 * (1 - 0.6 * kq))
                        circle(cr, 70, 0, 18, fill=(0.25, 0.35, 0.65), a=0.9 * (1 - 0.6 * kq))
            # the missing piece glows with a question
            gx_, gy_ = 660 + 2 * 150, 270 + 150
            rrect(cr, gx_ - 70, gy_ - 70, 140, 140, 14, stroke=YELLOW, lw=4, a=kp)
            P.question_mark(cr, gx_, gy_, 110, c=YELLOW, a=kp * (0.6 + 0.4 * math.sin(T * 3)))
        if kq > 0:
            # close-up of the hero looking up at the viewer
            src(cr, SKY1, 0.93 * kq)
            cr.paint()
            p = sm.pose("front", s=3.2, lw=5.0, fo=0.0, gy=lerp(-0.8, 0.0, kq), smile=0.15)
            p = head_at(sm.idle(p, T, 4, 0.3), CX, 560)
            sm.hero(cr, p, ink=(0.92, 0.92, 1.0), fill=NFILL, alpha=kq)

    b.fx(t_puzzle - 1.0, "snap", -12)
    b.fx(t_puzzle - 0.4, "snap", -14)
    b.fx(t_q - 0.4, "swell", -10, dur=2.5)

    # ------------------------------------------------------------ 8. a slight smile, fade, final words
    st8 = e("c10_13") - 0.15
    t_fade = st8 + 0.9
    t_quote = t_fade + 0.55
    t_cta = tl.dur - 4.0

    @b.shot(st8, "cut")
    def ending(cr, t, d, T):
        if T < t_fade + 0.5:
            sky(cr, T, qmarks=0.0)
            src(cr, SKY1, 0.93)
            cr.paint()
            sm_k = ease(prog(T, st8, 0.6))
            p = sm.pose("front", s=3.2, lw=5.0, fo=0.0, gy=0.0, smile=lerp(0.15, 0.7, sm_k), browy=0.25 * sm_k)
            p = head_at(sm.idle(p, T, 4, 0.3), CX, 560)
            sm.hero(cr, p, ink=(0.92, 0.92, 1.0), fill=NFILL)
            fk = ease(prog(T, t_fade, 0.5))
            if fk > 0:
                src(cr, BLACK, fk)
                cr.paint()
            return
        fill_bg(cr, BLACK)
        kq1 = eout(prog(T, t_quote, 0.6))
        kq2 = eout(prog(T, t_quote + 0.8, 0.6))
        up = ease(prog(T, t_cta - 0.2, 0.6))
        y1 = lerp(470, 260, up)
        sc = lerp(1.0, 0.72, up)
        text(cr, "INTELLIGENCE IS POWER.", CX, y1, 92 * sc, face=FONT_TITLE, c=WHITE, a=kq1)
        text(cr, "WISDOM IS HOW YOU USE IT.", CX, y1 + 120 * sc, 92 * sc, face=FONT_TITLE, c=YELLOW, a=kq2)
        kc = eout(prog(T, t_cta, 0.6))
        if kc > 0:
            line(cr, CX - 300 * kc, 470, CX + 300 * kc, 470, 4, MID)
            text(cr, "If you could ask a 500-IQ mind one question,", CX, 600, 54, face=FONT_HAND, bold=True, c=WHITE,
                 a=kc)
            text(cr, "what would it be?", CX, 680, 54, face=FONT_HAND, bold=True, c=WHITE, a=kc)
            kb = back(prog(T, t_cta + 0.5, 0.5))
            speech_bubble(cr, CX + 60, 860, 300, 100, CX - 40, 960, fill=(0.12, 0.12, 0.14), stroke=WHITE, scale=kb)
            text(cr, "comment below", CX + 60, 860, 36, face=FONT_HAND, bold=True, c=YELLOW, a=clamp(kb))
            p = sm.pose("wave", x=CX - 330, s=0.55, smile=0.9)
            p = sm.apply(p, a2f=42 + 22 * math.sin(T * 8))
            p = sm.on_ground(sm.idle(p, T, 5), 1000)
            sm.hero(cr, p, ink=WHITE, fill=BLACK, alpha=kc)

    b.fx(t_quote, "boom_soft", -6)
    b.fx(t_quote + 0.8, "chime", -10)
    b.fx(t_cta, "ding", -12)
    return b.result()
