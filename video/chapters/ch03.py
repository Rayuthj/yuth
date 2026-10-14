"""Chapter 3 - Your Brain Becomes a Supercomputer (1:40-2:40)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

CHALK = (0.95, 0.95, 0.92)
BLUEPRINT = (0.07, 0.17, 0.33)
EQ_TOKENS = ["Σ", "1/n²", "+", "∫₀¹", "2x", "dx", "=", "?"]


def school(cr, t):
    vgrad(cr, (0.70, 0.84, 0.97), (0.95, 0.96, 0.98))
    P.cloud(cr, 300, 180, 1.0)
    P.cloud(cr, 1500, 140, 0.8)
    rect(cr, 0, 860, W, 220, fill=(0.80, 0.82, 0.78))
    ground(cr, 860)
    rect(cr, 560, 360, 800, 500, fill=(0.95, 0.88, 0.80), stroke=INK, lw=6)
    polyline(cr, [(520, 370), (960, 190), (1400, 370)], 6, INK, closed=True, fill=(0.75, 0.25, 0.22))
    rrect(cr, 810, 300, 300, 60, 10, fill=WHITE, stroke=INK, lw=5)
    text(cr, "SCHOOL", 960, 330, 44, face=FONT_TITLE)
    for x in (620, 760, 1080, 1220):
        rect(cr, x, 440, 90, 110, fill=(0.8, 0.9, 1.0), stroke=INK, lw=4)
        rect(cr, x, 630, 90, 110, fill=(0.8, 0.9, 1.0), stroke=INK, lw=4)
    rect(cr, 900, 640, 120, 220, fill=(0.55, 0.38, 0.22), stroke=INK, lw=5)
    circle(cr, 960, 245, 28, fill=YELLOW, stroke=INK, w=4)


def classroom(cr, t):
    fill_bg(cr, (0.93, 0.91, 0.86))
    rect(cr, 0, 880, W, 200, fill=(0.78, 0.68, 0.55))
    ground(cr, 880)
    P.chalkboard(cr, 960, 330, 1100, 400)
    P.clock(cr, 1700, 160, 60, t, hours=9, minutes=5)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. day two: school
    @b.shot(0, "fade", 0.3)
    def arrive(cr, t, d, T):
        school(cr, T)
        x = lerp(120, 820, ease(prog(t, 0.2, 2.4)))
        p = sm.walk(sm.pose(x=x, face=1, smile=0.6), t, 1.0) if t < 2.6 else sm.pose("wave", x=x)
        p = sm.on_ground(p, 860)
        J = sm.hero(cr, p)
        rrect(cr, J["sh"][0] - 34, J["sh"][1] - 6, 30, 60, 8, fill=RED, stroke=INK, lw=4)
        pop_text(cr, "DAY 2", 1560, 300, t - 0.15, 110, face=FONT_TITLE, c=INK, rot=0.06)

    b.fx(0.15, "pop", -6)
    b.fx(0.6, "bell", -8)
    b.fx(0.5, "footsteps", -14, dur=2.0)

    # ------------------------------------------------------------ 2. the monster equation
    st2 = s("c3_02") - 0.2
    t_write, t_groan = w("c3_02", "writes"), w("c3_02", "groans")
    eq = "Σ 1/n²  +  ∫₀¹ 2x dx  =  ?"

    def students(cr, T, slump):
        for i, (x, acc) in enumerate(((300, ("cap",)), (1000, ("ponytail",)), (1260, ()))):
            p = sm.pose("sit", x=x, face=-1 if x > 960 else 1)
            if slump > 0:
                p = sm.mix(p, sm.apply(p, lean=24, head=24, a1f=60, a2f=120, smile=-0.6, brow=-0.6), slump)
            p = sm.on_ground(sm.idle(p, T, i), 880)
            sm.draw(cr, p, acc=acc)
            rect(cr, x - 60 if x < 960 else x - 70, 720, 130, 18, fill=WHITE, stroke=INK, lw=4)
            if slump > 0.3:
                text(cr, ["UGH", "NOOO", "WHAT?!"][i], x, 520, 42, face=FONT_HAND, bold=True, c=RED,
                     a=clamp(slump * 2 - 0.6), rot=0.1 * (i - 1))

    @b.shot(st2, "slide", 0.4)
    def board(cr, t, d, T):
        k = prog(T, t_write, 2.2)
        with ken(cr, t, d, 1.0, 1.05, CX, 480):
            classroom(cr, T)
            typewriter(cr, eq, 960 - text_w(cr, eq, FONT_SERIF, 74) / 2, 330, k, 74, c=CHALK, face=FONT_SERIF,
                       cursor=False)
            tp = sm.pose("write", x=1600, face=-1, a2f=-10 + 20 * math.sin(T * 9) * (k < 1))
            tp = sm.on_ground(sm.idle(tp, T, 9), 880)
            sm.draw(cr, tp, acc=("glasses", "mustache"))
            slump = ease(prog(T, t_groan, 0.4))
            students(cr, T, slump)
            p = sm.pose("sit", x=650, face=1, smile=0.6, gx=0.5, gy=-0.6)
            p = sm.on_ground(sm.idle(p, T, 4), 880)
            sm.hero(cr, p)
            rect(cr, 590, 720, 130, 18, fill=WHITE, stroke=INK, lw=4)

    b.fx(t_write, "chalk", -8, dur=2.2)
    b.fx(t_groan, "groan", -6)

    # ------------------------------------------------------------ 3. symbols become shapes
    st3 = s("c3_03") - 0.3
    t_shapes, t_move, t_fit, t_simp = (w("c3_03", "shapes"), w("c3_03", "move"), w("c3_03", "fit"),
                                       w("c3_03", "simplify"))
    colors = [BLUE, RED, YELLOW, GREEN, PURPLE, ORANGE, CYAN, WHITE]
    r = rng(3)
    homes = [(820 + (i % 4) * 95, 420 + (i // 4) * 95) for i in range(8)]
    starts = [(330 + i * 175, 300) for i in range(8)]
    drift = [(r.uniform(250, 1650), r.uniform(220, 860)) for _ in range(8)]

    @b.shot(st3, "zoom", 0.6)
    def mindview(cr, t, d, T):
        fill_bg(cr, BLUEPRINT)
        src(cr, WHITE, 0.06)
        cr.set_line_width(1.5)
        for gx in range(0, W, 48):
            cr.move_to(gx, 0)
            cr.line_to(gx, H)
        for gy in range(0, H, 48):
            cr.move_to(0, gy)
            cr.line_to(W, gy)
        cr.stroke()
        k_sh = ease(prog(T, t_shapes, 0.6))
        k_mv = ease(prog(T, t_move, 1.2))
        k_fit = ease(prog(T, t_fit, 1.0))
        k_simp = ease(prog(T, t_simp, 0.8))
        for i, tok in enumerate(EQ_TOKENS):
            sx, sy = starts[i]
            dx, dy = drift[i]
            hx, hy = homes[i]
            x = lerp(lerp(sx, dx, k_mv), hx, k_fit)
            y = lerp(lerp(sy, dy, k_mv), hy, k_fit)
            x = lerp(x, 960, k_simp)
            y = lerp(y, 520, k_simp)
            rot = (1 - k_fit) * k_mv * math.sin(T * 1.5 + i) * 1.2
            a_tok = 1 - k_sh
            if a_tok > 0:
                text(cr, tok, x, y, 70, c=WHITE, a=a_tok, face=FONT_SERIF)
            if k_sh > 0 and k_simp < 1:
                sz = 44 * k_sh * (1 - k_simp)
                with xform(cr, x, y, 1, rot):
                    shape = i % 3
                    col = colors[i]
                    if shape == 0:
                        rect(cr, -sz, -sz, sz * 2, sz * 2, fill=col, stroke=WHITE, lw=4, a=0.9)
                    elif shape == 1:
                        circle(cr, 0, 0, sz, fill=col, stroke=WHITE, w=4, a=0.9)
                    else:
                        polyline(cr, [(0, -sz * 1.1), (sz, sz * 0.8), (-sz, sz * 0.8)], 4, WHITE, closed=True, fill=col, fa=0.9)
            if k_mv > 0 and k_fit < 1 and k_sh > 0.5:
                for j in range(i + 1, 8, 3):
                    x2 = lerp(lerp(starts[j][0], drift[j][0], k_mv), homes[j][0], k_fit)
                    y2 = lerp(lerp(starts[j][1], drift[j][1], k_mv), homes[j][1], k_fit)
                    line(cr, x, y, x2, y2, 2, CYAN, 0.3 * (1 - k_fit))
        if k_fit > 0.95 and k_simp < 0.5:
            rrect(cr, 760, 360, 400, 210, 10, stroke=YELLOW, lw=5, a=(1 - k_simp * 2))
        if k_simp > 0:
            glow(cr, 960, 520, 300, YELLOW, 0.5 * k_simp)
            pop_text(cr, "= π²/6 + 1", 960, 520, T - t_simp - 0.5, 110, face=FONT_SERIF, c=YELLOW)
        text(cr, "HOW YOU SEE IT", 960, 120, 44, face=FONT_BOLD, c=CYAN, a=eout(prog(t, 0.3, 0.5)))
        p = sm.pose("front", s=1.0, smile=0.7, gx=math.sin(T) * 0.5)
        p = head_at(sm.idle(p, T, 1), 200, 830)
        sm.hero(cr, p, ink=WHITE, fill=BLUEPRINT)

    b.fx(st3, "whoosh", -6)
    b.fx(t_shapes, "shimmer", -8)
    for i in range(4):
        b.fx(t_fit + 0.15 + i * 0.18, "snap", -10)
    b.fx(t_simp + 0.5, "ding", -6)

    # ------------------------------------------------------------ 4. the lab
    st4 = s("c3_04") - 0.2
    t_pat = w("c3_04", "pattern")
    rp = rng(8)
    pts_data = [(x, math.sin(x * 0.012) * 90 + rp.gauss(0, 38)) for x in range(0, 640, 22)]

    @b.shot(st4, "fade", 0.35)
    def lab(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.06, 1100, 520):
            fill_bg(cr, (0.92, 0.95, 0.96))
            rect(cr, -200, 860, W + 400, 420, fill=(0.75, 0.80, 0.82))
            ground(cr, 860, x0=-200, x1=W + 200)
            rect(cr, 120, 700, 820, 30, fill=WHITE, stroke=INK, lw=5)
            for i, (x, c) in enumerate(((220, GREEN), (350, BLUE), (480, PURPLE))):
                P.flask(cr, x, 700, 0.9, c=c, t=T)
            P.tube(cr, 600, 700, 1.0, RED, 0.6)
            P.tube(cr, 650, 700, 1.0, YELLOW, 0.4)
            p = sm.pose("point", x=820, face=1, a1f=70, smile=0.5)
            p = sm.on_ground(sm.idle(p, T, 2), 860)
            sm.draw(cr, p, acc=("tuft", "labcoat"))
            # data screen
            ox, oy = 1000, 200
            rrect(cr, ox, oy, 780, 520, 16, fill=WHITE, stroke=INK, lw=6)
            line(cr, ox + 60, oy + 460, ox + 740, oy + 460, 4, INK)
            line(cr, ox + 60, oy + 460, ox + 60, oy + 40, 4, INK)
            for (x, y) in pts_data:
                circle(cr, ox + 90 + x, oy + 250 - y, 7, fill=MID)
            k = prog(T, t_pat, 1.0)
            if k > 0:
                curve = [(ox + 90 + x, oy + 250 - math.sin(x * 0.012) * 90) for x in range(0, 640, 8)]
                partial_poly(cr, curve, ease(k), 8, RED)
                label_box(cr, "PATTERN!", ox + 600, oy + 90, 38, c=RED, scale=back(prog(T, t_pat + 0.8, 0.4)))
            text(cr, "MESSY DATA", ox + 390, oy + 500, 32, face=FONT_HAND, bold=True)

    b.fx(st4, "bubbles", -14, dur=3.5)
    b.fx(t_pat, "draw", -10, dur=1.0)
    b.fx(t_pat + 0.8, "ding", -8)

    # ------------------------------------------------------------ 5. holding a whole program in your head
    st5 = s("c3_05") - 0.2
    t_head, t_bug = w("c3_05", "in your head"), w("c3_05", "bug")
    rc = rng(5)
    code = [(rc.randrange(0, 4) * 30, rc.uniform(80, 360), rc.choice([CYAN, YELLOW, (0.7, 0.9, 0.5), (0.9, 0.6, 0.9),
                                                                        WHITE])) for _ in range(60)]

    def code_screen(cr, x0, y0, w_, h_, T, bug_k):
        scroll = (T * 60) % 600
        for i, (ind, ln, c) in enumerate(code):
            y = y0 + 20 + i * 26 - scroll
            if y0 < y < y0 + h_ - 10:
                is_bug = i == 31
                if is_bug and bug_k > 0:
                    rect(cr, x0 + 4, y - 9, w_ - 8, 20, fill=RED, a=0.35 * bug_k)
                rrect(cr, x0 + 20 + ind, y - 5, ln, 10, 5, fill=RED if (is_bug and bug_k > 0) else c, a=0.85)

    @b.shot(st5, "slide", 0.4)
    def computer(cr, t, d, T):
        k_head = ease(prog(T, t_head, 0.8))
        k_bug = prog(T, t_bug, 0.4)
        with ken(cr, t, d, 1.0, 1.04, 900, 520):
            fill_bg(cr, (0.90, 0.90, 0.93))
            rect(cr, -200, 860, W + 400, 420, fill=(0.70, 0.70, 0.74))
            ground(cr, 860, x0=-200, x1=W + 200)
            P.desk(cr, 700, 860, 640)
            P.monitor(cr, 700, 520, 520, 330, screen=lambda c, x, y, w_, h_: code_screen(c, x, y, w_, h_, T, k_bug))
            p = sm.pose("type", x=300, face=1, smile=0.5 + 0.3 * k_bug, gy=-0.3)
            p = sm.apply(p, a2f=22 + 12 * math.sin(T * 14), a2b=32 + 12 * math.sin(T * 14 + 1.4))
            p = sm.on_ground(sm.idle(p, T, 3), 860)
            J = sm.hero(cr, p)
            if k_head > 0:
                hx, hy = J["head"]
                thought_bubble(cr, 1380, 330, 560, 400, hx + 40, hy - 40, scale=back(k_head), t=T)
                # the program as a tree structure
                with xform(cr, 1380, 330, max(0.01, k_head)):
                    nodes = [(0, -130), (-160, -40), (0, -40), (160, -40), (-220, 60), (-110, 60), (60, 60), (200, 60),
                             (-40, 140), (110, 140)]
                    edges = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6), (3, 7), (6, 8), (6, 9)]
                    P.node_graph(cr, nodes, edges, p=1.0, t=T, node_r=13, lw=4)
                    if k_bug > 0:
                        circle(cr, -40, 140, 24, stroke=RED, w=6, a=k_bug)
                        bug(cr, -40, 140, 0.5, T, a=k_bug)
            if k_bug > 0:
                P.magnifier(cr, 760, 470, 0.8 * eout(k_bug) + 0.01)
                pop_text(cr, "BUG FOUND", 700, 270, T - t_bug - 0.3, 46, face=FONT_TITLE, c=RED)

    def bug(cr, x, y, s, T, a=1.0):
        with xform(cr, x, y, s):
            for k in (-1, 0, 1):
                line(cr, -30, k * 14, 30, k * 14 + 6 * math.sin(T * 20 + k), 5, INK, a)
            ellipse(cr, 0, 0, 22, 30, fill=RED, stroke=INK, w=4, a=a)
            circle(cr, 0, -30, 12, fill=INK, a=a)

    b.fx(st5, "whoosh", -8)
    b.fx(st5 + 0.3, "typing", -10, dur=t_bug - st5)
    b.fx(t_head, "pop", -8)
    b.fx(t_bug, "alert", -8)

    # ------------------------------------------------------------ 6. a giant web of ideas
    st6 = s("c3_06") - 0.2
    t_bio, t_his = w("c3_06", "biology"), w("c3_06", "history")
    labels = ["BIOLOGY", "MATH", "HISTORY", "TECHNOLOGY", "MUSIC", "PHYSICS", "ART", "LANGUAGE", "ECONOMICS",
              "CHEMISTRY", "PSYCHOLOGY", "ASTRONOMY"]
    rw = rng(12)
    web = []
    for i, lab in enumerate(labels):
        a = i / len(labels) * TAU + rw.uniform(-0.15, 0.15)
        rr = rw.uniform(330, 470)
        web.append((960 + math.cos(a) * rr * 1.45, 540 + math.sin(a) * rr * 0.85, lab))
    extra = [(rw.uniform(-600, 2500), rw.uniform(-400, 1500)) for _ in range(80)]

    @b.shot(st6, "fade", 0.35)
    def web_shot(cr, t, d, T):
        dark(cr, T, star_a=0.3, c1=(0.08, 0.10, 0.18), c2=(0.03, 0.04, 0.08))
        z = lerp(1.15, 0.72, ease(prog(t, 0.5, d - 0.5)))
        with camera(cr, z, 960, 540):
            for i, (x, y) in enumerate(extra):
                j = (i * 7) % len(extra)
                line(cr, x, y, extra[j][0], extra[j][1], 2, CYAN, 0.12)
                circle(cr, x, y, 6, fill=CYAN, a=0.4)
            k = ease(prog(t, 0.0, 1.2))
            for i, (x, y, lab) in enumerate(web):
                for j in range(i + 1, len(web)):
                    if (i + j) % 4 == 0:
                        partial_line(cr, x, y, web[j][0], web[j][1], k, 2.5, WHITE, 0.25)
                partial_line(cr, 960, 540, x, y, k, 2.5, CYAN, 0.35)
            for (a_lab, b_lab, tt, col) in (("BIOLOGY", "MATH", t_bio, GREEN), ("HISTORY", "TECHNOLOGY", t_his, ORANGE)):
                kk = prog(T, tt, 0.6)
                if kk > 0:
                    A = next(v for v in web if v[2] == a_lab)
                    Bv = next(v for v in web if v[2] == b_lab)
                    glow(cr, (A[0] + Bv[0]) / 2, (A[1] + Bv[1]) / 2, 260, col, 0.25 * kk)
                    curve_arrow(cr, [(A[0], A[1]), (960, 540), (Bv[0], Bv[1])], 9, col, head=0, p=ease(kk))
            for (x, y, lab) in web:
                label_box(cr, lab, x, y, 30, c=WHITE, bg=(0.12, 0.15, 0.25), face=FONT_BOLD, bold=False, lw=3,
                          scale=k)
            p = sm.pose("front", s=1.0, smile=0.7, eye=1.1)
            p = head_at(sm.idle(p, T, 5), 960, 540)
            glow(cr, 960, 540, 180, YELLOW, 0.4)
            sm.hero(cr, p, ink=WHITE, fill=(0.08, 0.10, 0.18))

    b.fx(st6 + 0.2, "network", -10, dur=1.2)
    b.fx(t_bio, "zap", -8)
    b.fx(t_his, "zap", -8)

    # ------------------------------------------------------------ 7. still have to study
    st7 = s("c3_06b") - 0.2
    t_days = w("c3_06b", "days")

    @b.shot(st7, "fade", 0.35)
    def study(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.04):
            P.desk(cr, 650, 880, 600)
            for i in range(5):
                P.book(cr, 470 + i * 8, 712 - i * 32, 0.8, c=[RED, BLUE, GREEN, PURPLE, ORANGE][i], rot=math.pi / 2)
            p = sm.pose("sit", x=760, face=1, a1f=70, a2f=40, a1b=60, a2b=50, gy=0.6, smile=0.3)
            p = sm.on_ground(sm.idle(p, T, 6), 880)
            J = sm.hero(cr, p)
            P.chair(cr, 760, 880, 1.0, face=-1)
            P.book(cr, J["hand_f"][0] + 60, J["hand_f"][1] - 10, 0.7, open_=1)
            # calendar
            cx_, cy_ = 1400, 420
            rrect(cr, cx_ - 220, cy_ - 200, 440, 400, 14, fill=WHITE, stroke=INK, lw=6)
            rect(cr, cx_ - 220, cy_ - 200, 440, 70, fill=RED)
            text(cr, "TIME TO LEARN", cx_, cy_ - 165, 36, c=WHITE, face=FONT_BOLD)
            text(cr, "MONTHS", cx_, cy_ - 40, 80, face=FONT_TITLE)
            k = prog(T, t_days, 0.4)
            if k > 0:
                line(cr, cx_ - 170, cy_ - 40, cx_ - 170 + 340 * eout(k), cy_ - 40, 12, RED)
                pop_text(cr, "DAYS", cx_, cy_ + 90, T - t_days - 0.3, 100, face=FONT_TITLE, c=GREEN)
            # a few pages flying
            for i in range(4):
                f = (T * 0.9 + i * 0.25) % 1
                with xform(cr, lerp(900, 1200, f), 700 - 300 * f + 30 * math.sin(f * 9), 0.5, f * 6):
                    rect(cr, -40, -50, 80, 100, fill=WHITE, stroke=INK, lw=4, a=1 - f)

    b.fx(st7 + 0.3, "page", -10)
    b.fx(st7 + 1.4, "page", -12)
    b.fx(t_days, "scratch_out", -10)
    b.fx(t_days + 0.3, "pop", -6)

    # ------------------------------------------------------------ 8. an idea is only a guess
    st8 = s("c3_07") - 0.2
    t_guess, t_test = w("c3_07", "guess"), w("c3_07", "test it")

    @b.shot(st8, "fade", 0.35)
    def guess(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.05):
            p = sm.pose("point_up", x=520, face=1, smile=0.8)
            p = sm.on_ground(sm.idle(p, T, 7), 920)
            sm.hero(cr, p)
            on = ease(prog(t, 0.2, 0.4))
            P.lightbulb(cr, 560, 300, 1.2 * on + 0.01, on=on, t=T)
            k = prog(T, t_guess, 0.4)
            if k > 0:
                text(cr, "?", 560, 276, 90, face=FONT_TITLE, c=INK, a=k)
                label_box(cr, "JUST A GUESS", 840, 200, 40, c=RED, scale=back(k))
            kt = prog(T, t_test, 0.6)
            if kt > 0:
                arrow(cr, 760, 500, 1180, 500, 10, INK, head=36, p=ease(kt))
                with xform(cr, 1420, 560, 1.0):
                    rrect(cr, -170, -230, 340, 420, 20, fill=WHITE, stroke=INK, lw=6, a=kt)
                    text(cr, "TEST", 0, -170, 54, face=FONT_TITLE, a=kt)
                    P.flask(cr, -60, 150, 0.9, c=GREEN, t=T)
                    P.tube(cr, 50, 150, 1.0, BLUE, 0.6)
                    P.tube(cr, 100, 150, 1.0, RED, 0.3)
                    circle(cr, 0, -60, 60, stroke=INK, w=5, a=kt)
                    check(cr, 0, -60, 1.6, p=prog(T, t_test + 0.7, 0.3))

    b.fx(st8 + 0.2, "bulb", -8)
    b.fx(t_guess, "pop", -8)
    b.fx(t_test, "whoosh", -10)
    b.fx(t_test + 0.7, "ding", -8)

    # ------------------------------------------------------------ 9. the scientific method
    st9 = s("c3_08") - 0.2
    steps = [("EXPERIMENTS", "experiments"), ("EVIDENCE", "evidence"), ("DATA", "data"), ("PEER REVIEW", "checking"),
             ("TIME", "time")]
    t_nat = w("c3_08", "nature")

    @b.shot(st9, "fade", 0.35)
    def method(cr, t, d, T):
        paper(cr)
        k_nat = ease(prog(T, t_nat, 0.5))
        cxr, cyr, R = 760, 560, 300
        with ken(cr, t, d, 1.0, 1.03):
            text(cr, "HOW SCIENCE ACTUALLY WORKS", cxr, 110, 50, face=FONT_TITLE)
            arc(cr, cxr, cyr, R, 0, TAU, 5, LIGHT)
            for i, (lab, word) in enumerate(steps):
                a = -math.pi / 2 + i / len(steps) * TAU
                x, y = cxr + math.cos(a) * R, cyr + math.sin(a) * R
                k = back(prog(T, w("c3_08", word), 0.4))
                if k > 0:
                    a2 = -math.pi / 2 + (i + 1) / len(steps) * TAU
                    arc(cr, cxr, cyr, R, a + 0.25, a + (a2 - a) * clamp(k) - 0.25, 7, BLUE)
                    label_box(cr, lab, x, y, 34, c=INK, bg=(1.0, 0.95, 0.7) if i % 2 else (0.85, 0.92, 1.0),
                              face=FONT_BOLD, bold=False, scale=k)
            text(cr, "↻", cxr, cyr, 120, c=BLUE, face="DejaVu Sans", rot=T * 0.8, a=eout(prog(t, 0.3, 0.5)))
            # nature doesn't care: an apple bonks the hero
            hx = 1520
            p = sm.pose("think", x=hx, face=-1, smile=0.4)
            fall = prog(T, t_nat + 0.3, 0.45)
            if fall >= 1:
                p = sm.pose("surprised", x=hx, face=-1, eye=1.2)
            p = sm.on_ground(sm.idle(p, T, 8), 940)
            J = sm.hero(cr, p)
            P.tree(cr, hx + 230, 940, 1.3, T)
            ax, ay = J["head"][0] + 10, lerp(160, J["head"][1] - 55, ein(fall))
            if fall >= 1:
                bt = T - (t_nat + 0.75)
                ax += bt * 260
                ay = J["head"][1] - 55 - 300 * bt + 900 * bt * bt
                for i in range(4):
                    a = T * 4 + i * TAU / 4
                    P.star_shape(cr, J["head"][0] + math.cos(a) * 60, J["head"][1] - 70 + math.sin(a) * 18, 12,
                                 fill=YELLOW, stroke=INK, w=2)
            if k_nat > 0:
                circle(cr, ax, ay, 22, fill=RED, stroke=INK, w=4)
                line(cr, ax, ay - 22, ax + 4, ay - 36, 4, INK)
                label_box(cr, "NATURE DOESN'T CARE", hx - 60, 220, 34, c=INK, bg=(0.85, 1.0, 0.85), scale=k_nat)

    for lab, word in steps:
        b.fx(w("c3_08", word), "pop", -10)
    b.fx(t_nat + 0.75, "bonk", -4)

    # ------------------------------------------------------------ 10. walking home, imagining a machine
    st10 = s("c3_09") - 0.3
    t_mach, t_imp = w("c3_09", "machine"), w("c3_09", "impossible")

    @b.shot(st10, "fade", 0.5)
    def home(cr, t, d, T):
        vgrad(cr, (0.38, 0.40, 0.62), (0.95, 0.70, 0.55))
        off = T * 90
        with camera(cr, 1.0, CX + off * 0.3, CY):
            P.skyline(cr, -400, 880, 3200, 360, seed=41, fill=(0.45, 0.40, 0.55), win=False)
        rect(cr, 0, 880, W, 200, fill=(0.35, 0.32, 0.40))
        ground(cr, 880, (0.15, 0.13, 0.18))
        for i in range(-1, 6):
            x = (i * 420 - off) % (W + 420) - 200
            line(cr, x, 880, x, 520, 8, (0.15, 0.13, 0.18))
            line(cr, x, 520, x + 50, 520, 8, (0.15, 0.13, 0.18))
            glow(cr, x + 50, 535, 90, YELLOW, 0.5)
        p = sm.walk(sm.pose(x=560, face=1, smile=0.5, gy=-0.4), T, 0.85)
        p = sm.on_ground(p, 880)
        J = sm.hero(cr, p, ink=(0.10, 0.09, 0.12), fill=(0.98, 0.85, 0.75))
        k = prog(T, t_mach, 0.5)
        if k > 0:
            hx, hy = J["head"]
            thought_bubble(cr, 1240, 360, 760, 460, hx + 30, hy - 40, scale=back(k), t=T)
            with xform(cr, 1240, 360, max(0.01, k) * 0.95):
                glow_k = prog(T, t_imp, 0.6)
                if glow_k > 0:
                    glow(cr, 0, 0, 300, YELLOW, 0.5 * glow_k)
                rrect(cr, -170, -110, 340, 220, 20, fill=(0.85, 0.9, 1.0), stroke=INK, lw=6)
                P.gear(cr, -70, -10, 60, 10, T * 1.5, fill=(1, 0.85, 0.5))
                P.gear(cr, 30, 30, 45, 8, -T * 2, fill=(0.85, 1, 0.85))
                P.gear(cr, 95, -55, 35, 7, T * 2.6, fill=(1, 0.8, 0.8))
                arrow(cr, -320, 0, -180, 0, 8, INK, head=26)
                arrow(cr, 180, 0, 320, 0, 8, INK, head=26)
                text(cr, "?", -340, 0, 80, face=FONT_TITLE, c=RED)
                text(cr, "!", 345, 0, 80, face=FONT_TITLE, c=GREEN)
                text(cr, "IMPOSSIBLE PROBLEMS IN", -10, 160, 26, face=FONT_HAND, bold=True)

    b.fx(st10 + 0.2, "footsteps", -14, dur=d_safe(tl, st10))
    b.fx(t_mach, "pop", -8)
    b.fx(t_imp, "machine", -10, dur=2.0)
    return b.result()


def d_safe(tl, st):
    return max(1.0, tl.dur - st - 0.5)
