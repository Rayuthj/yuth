"""Chapter 9 - What Would Happen to Your Life? (7:50-9:00)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

GROUND = 900


def age_tag(cr, t, age):
    k = back(prog(t, 0.2, 0.4))
    if k > 0:
        label_box(cr, f"AGE {age}", W - 170, 120, 44, c=WHITE, bg=INK, face=FONT_TITLE, bold=False, scale=k, lw=0)


def path_label(cr, t, num, title, col):
    k = eout(prog(t, 0.1, 0.4))
    x = lerp(-700, 80, k)
    rrect(cr, x, 60, 190, 70, 12, fill=col)
    text(cr, f"PATH {num}", x + 95, 95, 38, face=FONT_TITLE, c=WHITE)
    text(cr, title, x + 215, 95, 46, face=FONT_TITLE, align="left", c=WHITE, outline=INK, ow=6)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. fast forward
    @b.shot(0, "fade", 0.4)
    def ff(cr, t, d, T):
        paper(cr, (0.95, 0.94, 0.90))
        with ken(cr, t, d, 1.0, 1.04):
            k = ease(prog(t, 0.3, 3.2))
            line(cr, 260, 760, 1660, 760, 10, INK)
            for i, age in enumerate((16, 20, 30, 40, 60, 80)):
                x = 260 + i * 280
                line(cr, x, 740, x, 780, 6, INK)
                text(cr, str(age), x, 820, 40, face=FONT_BOLD)
            px = lerp(260, 1100, k)
            polyline(cr, [(px, 740), (px - 22, 700), (px + 22, 700)], 4, INK, closed=True, fill=RED)
            p = sm.run(sm.pose(x=px, face=1, s=0.8, smile=0.7), T, 1.2)
            p = sm.on_ground(p, 690)
            sm.hero(cr, p)
            speed_lines(cr, T, n=16, a=0.2)
            # VHS style overlay
            text(cr, "▶▶", 560, 330, 110, face="DejaVu Sans", c=RED, outline=INK, ow=6, align="left",
                 a=0.6 + 0.4 * math.sin(T * 10))
            text(cr, "FAST FORWARD", 770, 330, 80, face=FONT_TITLE, align="left")
            for i in range(5):
                f = (T * 1.4 + i * 0.2) % 1
                with xform(cr, 1500 + i * 30 - f * 200, 300 + f * 300, 0.7, f * 3):
                    rect(cr, -60, -70, 120, 140, fill=WHITE, stroke=INK, lw=4, a=1 - f)
                    rect(cr, -60, -70, 120, 30, fill=RED, a=1 - f)

    b.fx(0.2, "fastforward", -8, dur=2.8)

    # ------------------------------------------------------------ 2. obsessed with learning
    st2 = s("c9_02") - 0.25
    subjects = [("BOOKS", "books", "book"), ("LANGUAGES", "languages", "lang"), ("PHYSICS", "physics", "atom"),
                ("MUSIC", "music", "music")]
    t_dev = w("c9_02", "devour")

    @b.shot(st2, "fade", 0.35)
    def learning(cr, t, d, T):
        paper(cr)
        age_tag(cr, t, 17)
        with ken(cr, t, d, 1.0, 1.05, CX, 560):
            ground(cr, GROUND)
            n_books = 3 + int(ease(prog(T, st2, d)) * 12)
            for i in range(n_books):
                P.book(cr, 760 + (i % 2) * 10, GROUND - 22 - i * 34, 0.9, c=[RED, BLUE, GREEN, PURPLE, ORANGE, YELLOW][i % 6],
                       rot=math.pi / 2)
            top = GROUND - n_books * 34
            p = sm.pose("sit", x=770, face=1, a1f=60, a2f=50, a1b=55, a2b=55, gy=0.4, smile=0.8)
            p = sm.on_ground(sm.idle(p, T, 1), top + 160)
            p["y"] = top - 6
            J = sm.hero(cr, p)
            P.book(cr, J["hand_f"][0] + 50, J["hand_f"][1] - 10, 0.55, open_=1.0, rot=-0.2)
            hx, hy = J["head"]
            for i, (lab, word, kind) in enumerate(subjects):
                tw0 = w("c9_02", word)
                k = prog(T, tw0, 0.5)
                if k <= 0:
                    continue
                x0, y0 = 1250 + (i % 2) * 330, 330 + (i // 2) * 300
                if T > t_dev:
                    f = clamp((T - t_dev - i * 0.15) * 1.2)
                    x0, y0 = lerp(x0, hx, ein(f)), lerp(y0, hy, ein(f))
                    sc = 1 - f * 0.8
                else:
                    sc = back(k)
                with xform(cr, x0, y0, max(0.01, sc) * 1.4):
                    if kind == "book":
                        P.book(cr, 0, 0, 0.8, c=BLUE)
                    elif kind == "lang":
                        speech_bubble(cr, 0, 0, 200, 100, -60, 90)
                        text(cr, "¡Hola!", 0, 0, 40, face=FONT_HAND, bold=True)
                    elif kind == "atom":
                        P.atom(cr, 0, 0, 0.9, T)
                    else:
                        text(cr, "♪♫", 0, 0, 110, face="DejaVu Sans", c=PURPLE)
                    if T <= t_dev:
                        text(cr, lab, 0, 120, 34, face=FONT_BOLD)

    for lab, word, kind in subjects:
        b.fx(w("c9_02", word), "pop", -10)
    b.fx(t_dev, "gulp", -6)

    # ------------------------------------------------------------ 3. helping people
    st3 = s("c9_03") - 0.25
    t_pump = min(w("c9_03", "water pump") - 0.5, s("c9_03") + 1.2)
    t_stud = min(w("c9_03", "student") - 0.5, t_pump + 2.0)
    t_biz = min(w("c9_03", "business") - 0.5, t_stud + 2.0)

    @b.shot(st3, "fade", 0.35)
    def helping(cr, t, d, T):
        paper(cr, (0.97, 0.95, 0.90))
        age_tag(cr, t, 25)
        text(cr, "SOLVING REAL PROBLEMS", CX, 120, 56, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
        scenes = [(t_pump, 330), (t_stud, 960), (t_biz, 1590)]
        for i, (ts, cx_) in enumerate(scenes):
            k = back(prog(T, ts, 0.45))
            if k <= 0:
                continue
            with xform(cr, cx_, 620, max(0.01, k)):
                rrect(cr, -280, -380, 560, 640, 26, fill=WHITE, stroke=INK, lw=6)
                cr.save()
                rrect_path(cr, -274, -374, 548, 628, 22)
                cr.clip()
                fixed = prog(T, ts + 1.2, 0.6)
                if i == 0:
                    vgrad(cr, (0.80, 0.92, 1.0), (1.0, 0.95, 0.85), -280, -380, 280, 260)
                    rect(cr, -280, 160, 560, 100, fill=(0.85, 0.75, 0.55))
                    P.water_pump(cr, 40, 160, 0.9, T, flow=fixed, broken=1 - fixed)
                    p = sm.pose("hold", x=-150, face=1, s=0.7, smile=0.4 + 0.5 * fixed)
                    p = sm.on_ground(sm.idle(p, T, 2), 160)
                    sm.hero(cr, p)
                    for j in range(3):
                        q = sm.pose("cheer" if fixed > 0.5 else "worried", x=150 + j * 50, face=-1, s=0.45)
                        q = sm.on_ground(q, 160)
                        sm.draw(cr, q, acc=[("cap",), ("ponytail",), ("bun",)][j], alpha=0.0 if j else 0.0)
                    text(cr, "WATER PUMP", 0, -320, 32, face=FONT_BOLD)
                elif i == 1:
                    fill_bg(cr, (0.95, 0.95, 0.98))
                    rect(cr, -200, 40, 400, 18, fill=(0.6, 0.45, 0.3), stroke=INK, lw=4)
                    p = sm.pose("present", x=-130, face=1, s=0.7, smile=0.7)
                    p = sm.on_ground(sm.idle(p, T, 3), 200)
                    sm.hero(cr, p)
                    q = sm.pose("sit", x=110, face=-1, s=0.6, smile=lerp(-0.5, 0.9, fixed), brow=-0.5 * (1 - fixed))
                    q = sm.on_ground(q, 200)
                    q["y"] = 200 - 98
                    J = sm.draw(cr, q, acc=("cap",))
                    if fixed > 0:
                        P.lightbulb(cr, J["head"][0], J["head"][1] - 80, 0.35 * fixed + 0.01, on=1.0, t=T)
                    else:
                        P.question_mark(cr, J["head"][0], J["head"][1] - 70, 50, c=RED)
                    text(cr, "STUDENT", 0, -320, 32, face=FONT_BOLD)
                else:
                    fill_bg(cr, (0.98, 0.95, 0.92))
                    P.shop(cr, -60, 140, 0.75, sign="BAKERY", lit=fixed)
                    gx, gy = 80, -230
                    pts = []
                    for j in range(12):
                        v = (1 - j / 11) if j < 6 else 0.0
                        v = 0.8 - j * 0.06 if fixed <= 0 else (0.8 - min(j, 5) * 0.06 + max(0, j - 5) * 0.12 * fixed)
                        pts.append((gx + j * 15, gy + 120 - v * 120))
                    rect(cr, gx - 10, gy - 20, 200, 160, fill=WHITE, stroke=INK, lw=3)
                    polyline(cr, pts, 5, GREEN if fixed > 0.5 else RED)
                    p = sm.pose("point", x=150, face=-1, s=0.6, smile=0.7)
                    p = sm.on_ground(sm.idle(p, T, 4), 160)
                    sm.hero(cr, p)
                    text(cr, "SMALL BUSINESS", 0, -320, 32, face=FONT_BOLD)
                cr.restore()
                if fixed > 0.9:
                    check(cr, 220, -320, 1.2, p=prog(T, ts + 1.8, 0.3))

    for ts in (t_pump, t_stud, t_biz):
        b.fx(ts, "pop", -8)
        b.fx(ts + 1.8, "ding", -10)

    # ------------------------------------------------------------ 4. three paths
    st4 = s("c9_04") - 0.25
    t_three = w("c9_04", "three paths")
    PATH_COL = [RED, (0.35, 0.45, 0.65), YELLOW]

    def fork(cr, T, k):
        vgrad(cr, (0.75, 0.86, 0.98), (0.97, 0.95, 0.90))
        rect(cr, 0, 560, W, H - 560, fill=(0.70, 0.82, 0.55))
        line(cr, 0, 560, W, 560, 3, MID)
        for i, (tx, col) in enumerate(((330, PATH_COL[0]), (960, PATH_COL[1]), (1590, PATH_COL[2]))):
            kk = clamp(k * 3 - i)
            if kk <= 0:
                continue
            top_x = lerp(960, tx, kk)
            polyline(cr, [(900, H), (1020, H), (top_x + 40, 560), (top_x - 40, 560)], 4, INK, closed=True,
                     fill=lerpc((0.85, 0.80, 0.70), col, 0.35))
            with xform(cr, lerp(960, tx, 0.55 * kk), lerp(H, 560, 0.55), 1.0):
                line(cr, 0, 0, 0, -160, 8, (0.45, 0.32, 0.2))
                rrect(cr, -60, -210, 120, 70, 10, fill=col, stroke=INK, lw=5)
                text(cr, str(i + 1), 0, -175, 50, face=FONT_TITLE, c=WHITE, outline=INK, ow=4)

    @b.shot(st4, "fade", 0.4)
    def crossroads(cr, t, d, T):
        k = ease(prog(T, t_three - 0.3, 1.2))
        age_tag(cr, t, 30)
        with ken(cr, t, d, 1.0, 1.06, CX, 640):
            fork(cr, T, k)
            p = sm.pose("think", x=960, face=1, fo=0.3, gx=math.sin(T * 1.5), smile=0.0, brow=-0.3)
            p = sm.on_ground(sm.idle(p, T, 5), 1040)
            sm.hero(cr, p)
        age_tag(cr, t, 30)

    b.fx(t_three - 0.3, "whoosh", -10)
    for i in range(3):
        b.fx(t_three - 0.3 + i * 0.4, "thud", -12)

    # ------------------------------------------------------------ 5. path one: status and control
    st5 = s("c9_05") - 0.25

    @b.shot(st5, "zoom", 0.5)
    def path_one(cr, t, d, T):
        vgrad(cr, (0.35, 0.05, 0.08), (0.12, 0.02, 0.04))
        with ken(cr, t, d, 1.0, 1.06, CX, 560):
            radial_lines(cr, CX, 420, T, n=24, c=RED, a=0.18, w=20)
            P.throne(cr, CX, 760, 1.2)
            p = sm.pose("sit", x=CX, face=1, fo=0.0, a1f=70, a2f=40, a1b=-70, a2b=-40, smile=0.4, brow=0.7)
            p = sm.on_ground(sm.idle(p, T, 6), 760)
            p["y"] = 760 - 170
            J = sm.draw(cr, p, acc=("tuft", "crown"), ink=WHITE, fill=(0.3, 0.05, 0.07))
            for i, x in enumerate((360, 620, 1300, 1560)):
                hy = 860 + 10 * math.sin(T * 3 + i)
                hand = J["hand_f"] if x > CX else J["hand_b"]
                line(cr, hand[0], hand[1], x, hy - 200, 2, (1, 0.8, 0.8), 0.7)
                q = sm.pose("arms_out", x=x, face=1 if x < CX else -1, s=0.6, smile=-0.3,
                            a1f=95 + 25 * math.sin(T * 3 + i), a1b=-95 + 25 * math.sin(T * 3 + i + 1))
                q = sm.on_ground(q, hy + 120)
                sm.draw(cr, q, acc=(), ink=(1, 0.8, 0.8), fill=(0.3, 0.05, 0.07))
        path_label(cr, t, 1, "STATUS & CONTROL", PATH_COL[0])

    b.fx(st5, "darkwhoosh", -8)
    b.fx(st5 + 0.4, "stinger", -10)

    # ------------------------------------------------------------ 6. path two: knowledge alone
    st6 = s("c9_06") - 0.25
    t_aff = w("c9_06", "affect")

    @b.shot(st6, "slide", 0.4)
    def path_two(cr, t, d, T):
        vgrad(cr, (0.08, 0.10, 0.18), (0.20, 0.24, 0.34))
        stars(cr, T, n=120, alpha=0.7, area=(0, 0, W, 600))
        with ken(cr, t, d, 1.0, 1.05, CX, 560):
            rect(cr, 0, 900, W, 180, fill=(0.12, 0.14, 0.2))
            P.tower(cr, 560, 900, 1.3, c=(0.45, 0.48, 0.58), lit=1.0)
            p = sm.pose("think", x=560, face=1, s=0.35)
            p = sm.on_ground(p, 900 - 420 * 1.3 + 30)
            sm.hero(cr, p, ink=YELLOW, fill=(0.2, 0.2, 0.25))
            P.telescope(cr, 640, 900 - 600, 0.5, rot=-0.6)
            # houses below, affected by something they never agreed to
            for i, x in enumerate((1150, 1350, 1550, 1750)):
                P.house(cr, x, 900, 0.7, lit=0.6, c=(0.6, 0.62, 0.7), roof=(0.35, 0.37, 0.45))
            ka = prog(T, t_aff - 0.6, 1.2)
            if ka > 0:
                for j in range(6):
                    f = (T * 0.6 + j / 6) % 1
                    x = lerp(640, 1450, f)
                    y = lerp(330, 760, f) - 120 * math.sin(f * math.pi)
                    circle(cr, x, y, 18 + 18 * f, fill=PURPLE, a=0.45 * ka * (1 - f * 0.5))
                for i, x in enumerate((1250, 1650)):
                    q = sm.pose("worried", x=x, face=-1, s=0.55)
                    q = sm.on_ground(q, 900)
                    sm.draw(cr, q, acc=(), ink=WHITE, fill=(0.12, 0.14, 0.2), alpha=ka)
                    P.question_mark(cr, x, 640, 50, c=WHITE, a=ka)
        path_label(cr, t, 2, "KNOWLEDGE ALONE", PATH_COL[1])

    b.fx(st6, "wind", -12, dur=5.0)
    b.fx(t_aff - 0.6, "alien", -14, dur=1.5)

    # ------------------------------------------------------------ 7. path three: a better life
    st7 = s("c9_07") - 0.25

    @b.shot(st7, "slide", 0.4)
    def path_three(cr, t, d, T):
        vgrad(cr, (1.0, 0.86, 0.55), (0.80, 0.92, 0.98))
        P.sun(cr, 1560, 230, 90, T)
        with ken(cr, t, d, 1.0, 1.05, CX, 600):
            rect(cr, 0, 880, W, 200, fill=(0.62, 0.80, 0.50))
            ground(cr, 880)
            for i, x in enumerate((240, 1680)):
                P.house(cr, x, 880, 1.0, lit=1.0)
            P.tree(cr, 480, 880, 1.0, T)
            P.solar_panel(cr, 1440, 880, 0.7, shine=1.0, t=T)
            people = [(720, ("cap",), "wave"), (880, ("tuft",), "present"), (1040, ("ponytail",), "cheer"),
                      (1200, ("bun", "glasses"), "wave")]
            for i, (x, acc, g) in enumerate(people):
                q = sm.pose(g, x=x, face=1 if x < 960 else -1, smile=0.9, s=0.9)
                q = sm.apply(q, a2f=40 + 20 * math.sin(T * 6 + i)) if g == "wave" else q
                q = sm.on_ground(sm.idle(q, T, i), 880)
                sm.draw(cr, q, acc=acc)
            for i in range(10):
                x = 600 + i * 80
                circle(cr, x, 900 + (i % 2) * 20, 9, fill=[RED, YELLOW, PURPLE][i % 3])
        path_label(cr, t, 3, "A BETTER LIFE", PATH_COL[2])

    b.fx(st7, "chime", -8)
    b.fx(st7 + 0.3, "birds", -14, dur=4.0)

    # ------------------------------------------------------------ 8. no equation tells you what you value
    st8 = s("c9_08") - 0.25
    t_trade, t_value = w("c9_08", "trade-offs"), w("c9_08", "value")

    @b.shot(st8, "fade", 0.4)
    def calculate(cr, t, d, T):
        fill_bg(cr, (0.10, 0.12, 0.20))
        r = rng(9)
        for i in range(40):
            x = r.uniform(0, W)
            y = (r.uniform(0, H) + T * r.uniform(30, 90)) % H
            text(cr, r.choice(["Σ", "∫", "P(x)", "≈", "Δ", "→", "f(x)", "%", "√"]), x, y, r.uniform(26, 60),
                 c=CYAN, a=0.25, face=FONT_SERIF)
        with ken(cr, t, d, 1.0, 1.04):
            kt = prog(T, t_trade, 0.5)
            if kt > 0:
                tilt = 0.18 * math.sin(T * 1.6)

                def lp(c):
                    P.crown(c, 0, 55, 0.4)

                def rp(c):
                    P.heart(c, 0, 60, 0.45)
                with group(cr, kt):
                    P.scale_balance(cr, 560, 800, 1.2, tilt=tilt, left=lp, right=rp)
                    text(cr, "TRADE-OFFS", 560, 880, 40, face=FONT_TITLE, c=WHITE)
            rrect(cr, 1000, 300, 760, 300, 20, fill=(0.06, 0.07, 0.10), stroke=CYAN, lw=5)
            text(cr, "WHAT DO I VALUE?", 1380, 370, 46, face=FONT_TITLE, c=CYAN)
            kv = prog(T, t_value - 0.4, 0.4)
            if kv > 0:
                gl = math.sin(T * 50) * 4
                text(cr, "= UNDEFINED", 1380 + gl, 480, 70, face=FONT_TITLE, c=RED, a=kv)
            else:
                r2 = rng(int(T * 12))
                text(cr, "= " + "".join(str(r2.randrange(10)) for _ in range(8)), 1380, 480, 70, face=FONT_TITLE,
                     c=WHITE)
            p = sm.pose("think", x=1380, face=-1, smile=0.0, brow=-0.3, s=0.8)
            p = sm.on_ground(sm.idle(p, T, 7), 1000)
            if kv > 0:
                p = sm.apply(p, smile=0.3, gy=0.6, gx=-0.3, browy=0.4)
            J = sm.hero(cr, p, ink=WHITE, fill=(0.10, 0.12, 0.20))
            if kv > 0:
                P.heart(cr, J["sh"][0] - 4, J["sh"][1] + 26, 0.32, beat=max(0, math.sin(T * 6)))
                glow(cr, J["sh"][0], J["sh"][1] + 26, 120, RED, 0.4 * kv)

    b.fx(st8 + 0.2, "data", -14, dur=2.0)
    b.fx(t_value - 0.4, "glitch", -8)
    b.fx(t_value, "heartbeat", -8, dur=2.0)

    # ------------------------------------------------------------ 9. a tool; you decide
    st9 = s("c9_09") - 0.25
    t_char, t_you = w("c9_09", "character"), w("c9_09", "you do")

    @b.shot(st9, "fade", 0.35)
    def tool(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.06):
            k = back(prog(t, 0.2, 0.5))
            with xform(cr, 700, 470, max(0.01, k), -0.4 + 0.1 * math.sin(T * 2)):
                rect(cr, -20, -40, 40, 300, fill=(0.6, 0.42, 0.28), stroke=INK, lw=6)
                rrect(cr, -110, -120, 220, 100, 14, fill=MID, stroke=INK, lw=6)
            label_box(cr, "INTELLIGENCE = A TOOL", 700, 820, 48, c=INK, scale=k)
            kc = prog(T, t_char, 0.4)
            if kc > 0:
                text(cr, "CHARACTER?", 1350, 360, 64, face=FONT_TITLE, a=kc)
            ky = prog(T, t_you, 0.35)
            if ky > 0:
                p = sm.pose("front", x=1350, s=1.1, smile=0.6, brow=0.4)
                p = sm.apply(p, a1f=40, a2f=120)
                p = sm.on_ground(sm.idle(p, T, 8), 980)
                sm.hero(cr, p, alpha=ky)
                text(cr, "YOU DECIDE.", 1350, 470, 80, face=FONT_TITLE, c=BLUE, a=ky, scale=lerp(1.4, 1.0, eout(ky)))

    b.fx(st9 + 0.2, "clank", -10)
    b.fx(t_you, "stinger", -10)

    # ------------------------------------------------------------ 10. hospital or weapon
    st10 = s("c9_09b") - 0.25
    t_hosp, t_weap, t_choice = w("c9_09b", "hospital"), w("c9_09b", "weapon"), w("c9_09b", "choice")

    @b.shot(st10, "fade", 0.35)
    def choice(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.03):
            P.brain(cr, CX, 300, 1.1, glow_a=0.3)
            text(cr, "THE SAME MIND", CX, 140, 48, face=FONT_TITLE)
            kh = prog(T, t_hosp - 0.2, 0.5)
            if kh > 0:
                arrow(cr, CX - 80, 420, 560, 600, 9, GREEN, head=34, p=ease(kh))
                with group(cr, kh):
                    rect(cr, 360, 640, 400, 260, fill=WHITE, stroke=INK, lw=6)
                    rect(cr, 520, 560, 80, 80, fill=WHITE, stroke=INK, lw=6)
                    line(cr, 560, 575, 560, 625, 14, RED)
                    line(cr, 535, 600, 585, 600, 14, RED)
                    for i in range(3):
                        rect(cr, 400 + i * 120, 700, 80, 70, fill=(0.8, 0.9, 1.0), stroke=INK, lw=4)
                    text(cr, "HOSPITAL", 560, 950, 44, face=FONT_TITLE, c=GREEN)
            kw_ = prog(T, t_weap - 0.2, 0.5)
            if kw_ > 0:
                arrow(cr, CX + 80, 420, 1360, 600, 9, (0.3, 0.3, 0.32), head=34, p=ease(kw_))
                with group(cr, kw_):
                    with xform(cr, 1360, 760, 1.0, -0.5):
                        rrect(cr, -180, -50, 360, 100, 50, fill=(0.3, 0.3, 0.32), stroke=INK, lw=6)
                        polyline(cr, [(180, -50), (260, 0), (180, 50)], 6, INK, closed=True, fill=(0.3, 0.3, 0.32))
                        polyline(cr, [(-180, -50), (-250, -100), (-250, 100), (-180, 50)], 6, INK, closed=True,
                                 fill=(0.45, 0.45, 0.48))
                    text(cr, "WEAPON", 1360, 950, 44, face=FONT_TITLE, c=(0.3, 0.3, 0.32))
            kc = prog(T, t_choice - 0.2, 0.4)
            if kc > 0:
                label_box(cr, "YOUR CHOICE", CX, 560, 50, c=WHITE, bg=INK, face=FONT_TITLE, bold=False, scale=back(kc))

    b.fx(t_hosp - 0.2, "pop", -8)
    b.fx(t_weap - 0.2, "pop", -8)
    b.fx(t_choice - 0.2, "stinger", -10)

    # ------------------------------------------------------------ 11. a project, and people, that matter
    st11 = s("c9_10") - 0.3
    t_people = w("c9_10", "make time")

    @b.shot(st11, "fade", 0.4)
    def matters(cr, t, d, T):
        kp = ease(prog(T, t_people - 0.3, 0.6))
        if kp < 1:
            with group(cr, 1 - kp):
                vgrad(cr, (0.80, 0.90, 0.98), (0.97, 0.95, 0.90))
                rect(cr, 0, 880, W, 200, fill=(0.80, 0.75, 0.62))
                ground(cr, 880)
                kb = ease(prog(T, st11 + 0.3, 3.0))
                # a school being built together
                rect(cr, 700, 880 - 360 * kb, 520, 360 * kb, fill=(0.95, 0.88, 0.80), stroke=INK, lw=6)
                if kb > 0.95:
                    polyline(cr, [(660, 525), (960, 380), (1260, 525)], 6, INK, closed=True, fill=(0.75, 0.25, 0.22))
                    text(cr, "SCHOOL", 960, 600, 44, face=FONT_TITLE)
                for i, (x, acc, g) in enumerate(((560, ("hardhat",), "hold"), (1360, ("tuft",), "hold"),
                                                 (1500, ("headset",), "point"))):
                    q = sm.pose(g, x=x, face=1 if x < 960 else -1, smile=0.8)
                    q = sm.apply(q, a2f=45 + 25 * math.sin(T * 7 + i))
                    q = sm.on_ground(sm.idle(q, T, i), 880)
                    sm.draw(cr, q, acc=acc)
                text(cr, "A PROJECT THAT MATTERS", CX, 150, 56, face=FONT_TITLE)
        if kp > 0:
            with group(cr, kp):
                vgrad(cr, (0.18, 0.14, 0.25), (0.42, 0.28, 0.30))
                for i in range(14):
                    x = 200 + i * 115
                    line(cr, x, 150 + 30 * math.sin(i * 0.9), x + 115, 150 + 30 * math.sin((i + 1) * 0.9), 2, MID)
                    glow(cr, x, 150 + 30 * math.sin(i * 0.9), 50, YELLOW, 0.6)
                    circle(cr, x, 150 + 30 * math.sin(i * 0.9), 8, fill=YELLOW)
                rect(cr, 0, 900, W, 180, fill=(0.25, 0.18, 0.2))
                rect(cr, 560, 690, 800, 30, fill=(0.6, 0.42, 0.28), stroke=INK, lw=5)
                for x in (600, 1320):
                    line(cr, x, 720, x, 900, 6, INK)
                for i, x in enumerate((720, 900, 1060, 1220)):
                    P.coffee(cr, x, 690, 0.4, T, steam=False)
                diners = [(500, ("tuft",), 1), (700, ("cap",), 1), (1240, ("ponytail",), -1), (1420, ("glasses",), -1)]
                for i, (x, acc, f) in enumerate(diners):
                    laugh = max(0, math.sin(T * 5 + i * 1.3))
                    q = sm.pose("sit", x=x, face=f, smile=1.0, mo=0.5 * laugh, a1f=50, a2f=40, head=-6 * laugh)
                    q["y"] = 900 - 98
                    sm.draw(cr, sm.idle(q, T, i), acc=acc, ink=(0.95, 0.9, 0.85), fill=(0.42, 0.28, 0.30))
                text(cr, "...AND PEOPLE WHO MATTER", CX, 300, 56, face=FONT_TITLE, c=WHITE)

    b.fx(st11 + 0.3, "hammer", -12, dur=3.0)
    b.fx(t_people - 0.3, "laugh", -14, dur=4.0)

    # ------------------------------------------------------------ 12. a hill above the city lights
    st12 = s("c9_11") - 0.4

    @b.shot(st12, "fade", 0.7)
    def hilltop(cr, t, d, T):
        vgrad(cr, (0.03, 0.04, 0.10), (0.16, 0.14, 0.30))
        stars(cr, T, n=260, alpha=0.9, area=(0, 0, W, 700))
        with ken(cr, t, d, 1.0, 1.12, 700, 620):
            circle(cr, 1500, 220, 60, fill=(0.98, 0.95, 0.82))
            glow(cr, 1500, 220, 200, (0.98, 0.95, 0.82), 0.25)
            P.skyline(cr, 700, 860, 1300, 300, seed=61, fill=(0.08, 0.08, 0.14), lit=True, t=T)
            glow(cr, 1350, 860, 600, YELLOW, 0.12)
            rect(cr, 0, 860, W, 300, fill=(0.05, 0.05, 0.09))
            P.hill(cr, 380, 900, 1100, 260, c=(0.04, 0.04, 0.07))
            p = sm.pose("sit", x=420, face=1, a1f=-20, a2f=10, a1b=-30, a2b=10, gy=-0.3, gx=0.8, smile=0.3)
            p = sm.idle(p, T, 9, 0.5)
            p["y"] = 900 - 330 + 56
            sm.hero(cr, p, ink=(0.85, 0.85, 0.95), fill=(0.04, 0.04, 0.07))
            kq = prog(T, w("c9_11", "worthwhile") - 0.8, 1.5)
            if kq > 0:
                P.question_mark(cr, 470 + 20 * math.sin(T), 380 - 60 * kq, 70, c=YELLOW, a=kq * 0.85)

    b.fx(st12, "night", -12, dur=tl.dur - st12)
    return b.result()
