"""King - Chapter 3: The Power to Change Everything (1:40-2:40)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 110, 0.75), ("c3_05", "warm", "warm", 84, 0.6),
                        ("c3_08", "discovery", "discovery_g", 100, 0.7)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. the first royal decree
    @b.shot(0, "fade", 0.3)
    def decree(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 520):
            S.palace(cr, T)
            un = ease(prog(t, 0.2, 1.2))
            P2.parchment(cr, 1150, 470, 460, 560, title="ROYAL DECREE", lines_=["~ ~ ~", "By order of", "the King:"],
                         t_unroll=un, size=34)
            K.hero(cr, T, 600, 880, "write", acc=KING, face=1, a2f=-10 + 15 * math.sin(T * 8))
    b.fx(0.3, "page", -8)

    # 2-3. free ice cream! the crowd goes wild
    st2 = s("c3_02") - 0.2
    t_wild = w("c3_03", "wild")
    t_rate = w("c3_03", "approval")

    @b.shot(st2, "slide", 0.4)
    def icecream(cr, t, d, T):
        cheer = ease(prog(T, t_wild - 0.2, 0.5))
        with K.ken(cr, t, d, 1.04, 1.0, 1200, 600):
            balcony(cr, T, crowd_cheer=cheer, signs=["WE LOVE\nYOU!", "ICE\nCREAM!", "LONG LIVE\nTHE KING"])
            env = tl.env("c3_02", T)
            K.person(cr, T, 1500, 600, "point_up" if env > 0 else "cheer", acc=KING, face=-1, talk=env, smile=0.9)
            for i in range(6):
                f = (T * 0.5 + i / 6) % 1
                P2.ice_cream(cr, 300 + i * 180, 900 - 300 * f, 0.4, c=[(1, 0.75, 0.8), (0.75, 0.9, 1), (1, 0.95, 0.6)][i % 3])
            if T > s("c3_02") - 0.1:
                kb = back(prog(T, s("c3_02") - 0.1, 0.3))
                speech_bubble(cr, 1200, 300, 560, 110, 1470, 420, scale=kb)
                text(cr, "Free ice cream every Friday!", 1200, 300, 40, face=FONT_HAND, bold=True, a=clamp(kb))
        kg = prog(T, t_rate - 0.2, 1.0)
        if kg > 0:
            rrect(cr, 60, 60, 440, 200, 20, fill=WHITE, stroke=INK, lw=5)
            P2.gauge(cr, 280, 220, 130, lerp(0.35, 0.98, ease(kg)), t=T)
            text(cr, "APPROVAL", 280, 100, 34, face=FONT_TITLE)
    b.fx(s("c3_02"), "pop", -10)
    b.fx(t_wild - 0.2, "cheer", -6, dur=3.0)
    b.fx(t_rate, "rise", -8)

    # 4. the bill
    st4 = s("c3_04") - 0.15
    t_bill = w("c3_04", "bill")

    @b.shot(st4, "cut")
    def bill(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            S.palace(cr, T)
            K.person(cr, T, 640, 880, "hold", face=1, acc=("glasses", "tie"), a1f=80, a2f=10)
            un = ease(prog(T, t_bill, 1.6))
            rect(cr, 760, 420, 260, 460 * un + 2, fill=WHITE, stroke=INK, lw=4)
            for i in range(int(14 * un)):
                text(cr, "ICE CREAM .... $$$", 780, 450 + i * 32, 22, face=FONT_HAND, bold=True, align="left")
            if un > 0.9:
                polyline(cr, [(760, 880), (1020, 880), (1500, 900), (1240, 900)], 4, INK, closed=True, fill=WHITE)
                text(cr, "TOTAL: $90,000,000", 1300, 960, 44, face=FONT_TITLE, c=RED, a=prog(T, t_bill + 1.6, 0.4))
            K.hero(cr, T, 1400, 880, "surprised" if un > 0.5 else "stand", acc=KING, face=-1, eye=1.3, mo=0.6 * un)
    b.fx(t_bill, "roll", -10, dur=1.6)
    b.fx(t_bill + 1.6, "thud", -8)

    # 5. money comes from taxes; every coin has a cost
    st5 = s("c3_05") - 0.15
    t_tax, t_else = w("c3_05", "taxes"), w("c3_05", "something else")

    @b.shot(st5, "fade", 0.3)
    def taxes(cr, t, d, T):
        fill_bg(cr, (0.97, 0.95, 0.90))
        vignette(cr, 0.15)
        with K.ken(cr, t, d, 1.0, 1.03):
            text(cr, "LESSON #1: MONEY COMES FROM SOMEWHERE", CX, 110, 50, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
            for i, x in enumerate((180, 340, 500)):
                K.person(cr, T, x, 860, "hold", face=1, s=0.8, acc=[("cap",), ("ponytail",), ("glasses",)][i], seed=i)
            S.castle(cr, CX, 860, 0.55, t=T)
            text(cr, "TREASURY", CX, 900, 40, face=FONT_TITLE)
            kt = prog(T, t_tax, 3.0)
            if kt > 0:
                for i in range(12):
                    f = (kt * 4 + i / 12) % 1
                    P2.coin(cr, lerp(380, CX - 80, f), 650 - 160 * math.sin(f * math.pi), 20, rot=T * 5 + i)
                text(cr, "TAXES", 560, 420, 44, face=FONT_TITLE, c=GREEN, a=clamp(kt * 3))
            ke = prog(T, t_else - 0.6, 1.2)
            if ke > 0:
                for j, (lab, x, col) in enumerate((("SCHOOLS", 1450, BLUE), ("ROADS", 1750, ORANGE))):
                    rrect(cr, x - 110, 640, 220, 220, 16, fill=WHITE, stroke=col, lw=6)
                    text(cr, lab, x, 900, 36, face=FONT_TITLE, c=col)
                f = ease(ke)
                P2.coin(cr, lerp(CX + 120, 1450, f), 560 - 200 * math.sin(f * math.pi), 34, rot=T * 6)
                if ke >= 1:
                    text(cr, "EMPTY", 1750, 750, 44, face=FONT_TITLE, c=RED, rot=-0.15)
    b.fx(t_tax, "coins", -8, dur=1.5)
    b.fx(t_else, "coins", -10, dur=0.6)

    # 6. schools or roads? trade-offs pie
    st6 = s("c3_06") - 0.15
    pairs = [("schools", 0), ("roads", 1), ("hospitals", 2), ("army", 3), ("taxes", 4), ("services", 5)]

    @b.shot(st6, "fade", 0.3)
    def pie(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "THE ROYAL BUDGET", 700, 120, 60, face=FONT_TITLE)
            focus = 0
            for i, (wd, idx) in enumerate(pairs):
                if T >= w("c3_06", wd) - 0.1:
                    focus = idx
            grow = 0.06 * math.sin(T * 3)
            base = [0.24, 0.18, 0.20, 0.18, 0.10, 0.10]
            labels = ["SCHOOLS", "ROADS", "HEALTH", "ARMY", "TAX CUTS", "SERVICES"]
            cols = [BLUE, ORANGE, RED, GRAY, GREEN, PURPLE]
            fr = list(base)
            fr[focus] += 0.08 + grow
            tot = sum(fr)
            parts = [(f / tot, c, lab) for f, c, lab in zip(fr, cols, labels)]
            P2.pie_chart(cr, 700, 580, 340, parts, p=ease(prog(t, 0.2, 1.0)), explode=focus, size=26)
            K.hero(cr, T, 1500, 980, "shrug" if (int(T * 1.2) % 2) else "think", acc=KING, face=-1)
            text(cr, "?", 1500, 420, 160, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, rot=math.sin(T * 2) * 0.2)
    for wd, _ in pairs:
        b.fx(w("c3_06", wd), "blip", -12)

    # 6b. every ruler faced these trade-offs
    st6b = s("c3_06b") - 0.15

    @b.shot(st6b, "fade", 0.3)
    def rulers(cr, t, d, T):
        fill_bg(cr, (0.95, 0.92, 0.86))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "EVERY RULER IN HISTORY", CX, 130, 60, face=FONT_TITLE)
            for i in range(6):
                x = 220 + i * 296
                k = K.pop(T, st6b + 0.2 + i * 0.25)
                if k <= 0:
                    continue
                rrect(cr, x - 120, 260, 240, 320, 12, fill=(0.85, 0.75, 0.55), stroke=(0.55, 0.40, 0.2), lw=10)
                p = sm.pose("front", s=0.75 * k + 0.01, smile=-0.2 + 0.1 * i % 2, brow=-0.4)
                acc = [("crown", "beard"), ("crown",), ("crown", "mustache"), ("crown", "ponytail"), ("crown", "glasses"),
                       ("crown", "bun")][i]
                sm.draw(cr, head_at(p, x, 400), acc=acc)
                P.scale_balance(cr, x, 820, 0.45 * k + 0.01, tilt=0.25 * math.sin(T * 2 + i))
            text(cr, "...AND NONE GOT IT PERFECT", CX, 990, 48, face=FONT_TITLE, c=RED,
                 a=eout(prog(T, w("c3_06b", "none"), 0.4)))
    for i in range(6):
        b.fx(st6b + 0.2 + i * 0.25, "pop", -14)

    # 7. opportunity cost vs headache
    st7 = s("c3_07") - 0.15
    t_head = w("c3_07", "headache")

    @b.shot(st7, "fade", 0.3)
    def headache(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04):
            P2.book_big(cr, 520, 520, 0.9, title="ECONOMICS", c=(0.2, 0.35, 0.6))
            label_box(cr, "OPPORTUNITY COST", 520, 860, 50, c=BLUE, scale=K.pop(T, w("c3_07", "opportunity")))
            kh = prog(T, t_head - 0.3, 0.4)
            K.hero(cr, T, 1350, 960, "facepalm" if kh > 0 else "think", acc=KING, face=-1)
            if kh > 0:
                label_box(cr, "HEADACHE", 1350, 280, 60, c=RED, scale=back(kh))
                for i in range(4):
                    a = T * 3 + i * TAU / 4
                    P.star_shape(cr, 1350 + math.cos(a) * 80, 470 + math.sin(a) * 20, 14, fill=YELLOW, stroke=INK, w=2)
    b.fx(t_head - 0.3, "boing", -10)

    # 8. something smarter: schools, water, roads
    st8 = s("c3_08") - 0.15

    def ic_school(cr, T):
        rect(cr, -120, -60, 240, 140, fill=(0.95, 0.88, 0.80), stroke=INK, lw=5)
        polyline(cr, [(-140, -55), (0, -140), (140, -55)], 5, INK, closed=True, fill=RED)
        rect(cr, -25, 20, 50, 60, fill=(0.55, 0.38, 0.22), stroke=INK, lw=4)
        text(cr, "SCHOOL", 0, -10, 26, face=FONT_TITLE)

    def ic_water(cr, T):
        line(cr, -80, -80, 40, -80, 22, MID)
        line(cr, 40, -80, 40, -30, 22, MID)
        rect(cr, -110, -110, 40, 60, fill=GRAY, stroke=INK, lw=4)
        for i in range(5):
            f = (T * 2 + i * 0.2) % 1
            ellipse(cr, 40, -10 + f * 130, 9, 14, fill=CYAN, stroke=INK, w=2)
        ellipse(cr, 40, 110, 80, 20, fill=(0.6, 0.85, 1.0), stroke=INK, w=4)

    def ic_road(cr, T):
        polyline(cr, [(-140, 100), (140, 100), (60, -100), (-60, -100)], 5, INK, closed=True, fill=(0.35, 0.36, 0.4))
        for i in range(4):
            y = -80 + i * 50
            rect(cr, -6, y, 12, 26, fill=WHITE)

    b.add(st8, K.icons("SOMETHING SMARTER", [(ic_school, "NEW SCHOOLS", w("c3_08", "schools")),
                                             (ic_water, "CLEAN WATER", w("c3_08", "water")),
                                             (ic_road, "ROADS THAT WORK", w("c3_08", "roads"))],
                       bg=PAPER, y=520, size=1.2, hero_at=(1800, 1000, "present", -1)), "fade", 0.3)
    for wd in ("schools", "water", "roads"):
        b.fx(w("c3_08", wd), "pop", -8)

    # 9. nobody throws a parade for plumbing
    st9 = s("c3_09") - 0.15
    t_par = w("c3_09", "parade")

    @b.shot(st9, "fade", 0.3)
    def plumbing(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.city(cr, T, 0, gy=880, sky=((0.70, 0.74, 0.82), (0.88, 0.88, 0.9)))
            kp = prog(T, t_par - 0.3, 0.5)
            if kp > 0:
                J = K.person(cr, T, 900, 900, "cheer", acc=("cap",), smile=1.0, seed=3)
                P2.sign(cr, J["hand_f"][0], J["hand_f"][1] - 10, 0.9, "YAY\nPIPES!", c=(0.85, 0.95, 1.0), rot=0.1)
                P.cloud(cr, 1400, 260, 0.7, c=(0.8, 0.8, 0.84))
            rrect(cr, 1340, 80, 440, 200, 20, fill=WHITE, stroke=INK, lw=5)
            P2.gauge(cr, 1560, 240, 130, lerp(0.95, 0.55, ease(prog(T, st9 + 0.3, 1.2))), t=T)
            text(cr, "APPROVAL", 1560, 120, 34, face=FONT_TITLE)
    b.fx(st9 + 0.3, "slowmo", -12)
    b.fx(t_par, "boing", -14)

    # 10. years from now
    st10 = s("c3_10") - 0.3

    @b.shot(st10, "fade", 0.5)
    def years(cr, t, d, T):
        k = ease(prog(t, 0.3, d - 0.6))
        sky = lerpc((0.75, 0.86, 0.98), (1.0, 0.85, 0.6), k)
        vgrad(cr, sky, (0.95, 0.96, 0.95))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.floor(cr, 880, (0.62, 0.80, 0.50))
            for i in range(6):
                hk = clamp(k * 6 - i)
                if hk > 0:
                    x = 200 + i * 300
                    P.house(cr, x, 880, 0.8 * eout(hk) + 0.01, lit=0.5)
            for i in range(5):
                kk = clamp(k * 5 - i)
                if kk > 0:
                    K.person(cr, T, 350 + i * 300, 960, "cheer" if i % 2 else "wave", s=0.7, seed=i,
                             acc=[("cap",), ("ponytail",), ("glasses",), ("bun",), ()][i], alpha=kk)
            label_box(cr, f"YEAR {1 + int(k * 20)}", CX, 140, 56, c=INK, face=FONT_TITLE, bold=False)
    b.fx(st10, "chime", -10)
    return b.result()
