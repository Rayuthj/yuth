"""King - Chapter 5: The Weight of the Crown (3:40-4:50)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 70, 0.6), ("c5_07", "dark", "dark", 60, 0.6),
                        ("c5_10", "warm", "warm", 84, 0.7)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. storm clouds over the palace
    @b.shot(0, "fade", 0.3)
    def storm(cr, t, d, T):
        k = ease(prog(t, 0.0, d))
        vgrad(cr, lerpc((0.62, 0.78, 0.95), (0.25, 0.27, 0.35), k), lerpc((0.92, 0.95, 0.98), (0.45, 0.45, 0.50), k))
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            S.floor(cr, 900, (0.55, 0.65, 0.45))
            S.castle(cr, CX, 900, 1.0, t=T)
            for i in range(6):
                P.cloud(cr, lerp(-300, 200 + i * 300, k), 160 + (i % 2) * 70, 1.1, c=(0.45, 0.46, 0.52))
        text(cr, "THE HARD DECISIONS", CX, 200, 60, face=FONT_TITLE, c=WHITE, outline=INK, ow=8, a=eout(prog(t, 0.4, 0.4)))
    b.fx(0.2, "darkwhoosh", -8)

    # 2. drought in the south
    st2 = s("c5_02") - 0.15
    t_price = w("c5_02", "prices")

    @b.shot(st2, "slide", 0.4)
    def drought(cr, t, d, T):
        vgrad(cr, (1.0, 0.80, 0.50), (1.0, 0.92, 0.75))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            P.sun(cr, 1500, 220, 110, T)
            P2.cracked_ground(cr, -400, W + 400, 760)
            for i in range(8):
                x = 200 + i * 200
                line(cr, x, 760, x + 10 * math.sin(i), 680, 5, (0.55, 0.45, 0.2))
                ellipse(cr, x + 20, 690, 20, 8, fill=(0.75, 0.65, 0.3), rot=0.8)
            K.person(cr, T, 400, 900, "sad", face=1, acc=("hat",))
            kp = prog(T, t_price - 0.2, 1.5)
            if kp > 0:
                rrect(cr, 1150, 420, 420, 200, 16, fill=WHITE, stroke=INK, lw=5)
                text(cr, "BREAD", 1250, 470, 36, face=FONT_TITLE)
                text(cr, f"${2 + 3 * ease(kp):.2f}", 1450, 470, 44, face=FONT_TITLE, c=RED)
                arrow(cr, 1360, 590, 1360, 590 - 100 * ease(kp), 10, RED, head=30)
        text(cr, "SOUTH: DROUGHT", 340, 110, 50, face=FONT_TITLE, c=INK)
    b.fx(st2, "wind", -12, dur=4.0)
    b.fx(t_price, "rise", -10)

    # 3. a factory closing in the north
    st3 = s("c5_03") - 0.15
    t_close = w("c5_03", "close")

    @b.shot(st3, "slide", 0.4)
    def factory(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.city(cr, T, 0, gy=880, sky=((0.70, 0.75, 0.85), (0.88, 0.88, 0.9)))
            kc = ease(prog(T, t_close, 0.6))
            P2.factory(cr, 760, 880, 1.3, T, closed=kc)
            for i, x in enumerate((1260, 1400, 1540, 1680)):
                K.person(cr, T, x, 900, "worried" if kc > 0.5 else "stand", face=-1, s=0.85, acc=("hardhat",), seed=i)
            kj = prog(T, w("c5_03", "thousands"), 0.5)
            if kj > 0:
                text(cr, "THOUSANDS OF JOBS", 1460, 420, 50, face=FONT_TITLE, c=RED, a=kj)
        text(cr, "NORTH: FACTORY", 330, 110, 50, face=FONT_TITLE)
    b.fx(t_close, "thud", -6)

    # 4-5. money for one problem; farmers or factory?
    st4 = s("c5_04") - 0.15
    t_help, t_save = w("c5_05", "help"), w("c5_05", "save")

    def farm(c):
        line(c, -40, 80, 40, 80, 4, INK)
        for k in (-30, 0, 30):
            line(c, k, 80, k, 40, 4, (0.6, 0.5, 0.2))
        text(c, "FARMS", 0, 130, 26, face=FONT_TITLE)

    def fac(c):
        rect(c, -40, 40, 80, 50, fill=LIGHT, stroke=INK, lw=3)
        rect(c, 10, 10, 15, 30, fill=MID, stroke=INK, lw=3)
        text(c, "FACTORY", 0, 130, 26, face=FONT_TITLE)

    @b.shot(st4, "fade", 0.3)
    def choose(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "ONE BAG OF GOLD. TWO PROBLEMS.", CX, 120, 54, face=FONT_TITLE)
            tilt = 0.0
            if T > t_help:
                tilt = -0.28
            if T > t_save:
                tilt = 0.28
            tilt += 0.04 * math.sin(T * 3)
            P.scale_balance(cr, CX, 900, 1.6, tilt=tilt, left=farm, right=fac)
            with xform(cr, CX, 380 + 10 * math.sin(T * 2), 1.0):
                ellipse(cr, 0, 40, 90, 70, fill=(0.75, 0.6, 0.35), stroke=INK, w=5)
                text(cr, "$", 0, 45, 70, face=FONT_TITLE, c=GOLD)
            if T > t_help:
                text(cr, "WORKERS SUFFER", 1450, 300, 36, face=FONT_TITLE, c=RED, a=prog(T, t_help, 0.3) * (1 if T < t_save else 0.3))
            if T > t_save:
                text(cr, "FAMILIES STRUGGLE", 470, 300, 36, face=FONT_TITLE, c=RED, a=prog(T, t_save, 0.3))
    b.fx(t_help, "clank", -10)
    b.fx(t_save, "clank", -10)

    # 6. no perfect answer
    st6 = s("c5_06") - 0.15
    b.add(st6, K.big_number("NO PERFECT", s("c5_06") + 0.1, label="ANSWER", sub="Every choice helps some people and hurts others",
                            t_sub=w("c5_06", "every"), color=WHITE, glow_c=RED), "fade", 0.3)
    b.fx(s("c5_06") + 0.1, "stinger", -8)

    # 6b. behind every number is a family
    st6b = s("c5_06b") - 0.15

    @b.shot(st6b, "fade", 0.3)
    def families(cr, t, d, T):
        fill_bg(cr, (0.95, 0.93, 0.88))
        vignette(cr, 0.2)
        k = ease(prog(t, 0.2, 1.4))
        z = lerp(1.0, 1.0, k)
        with camera(cr, z, CX, CY):
            t_far, t_fam = w("c5_06b", "farmer"), w("c5_06b", "real family")
            k0 = 1 - clamp(prog(T, t_far - 0.35, 0.3))
            if k0 > 0:
                with group(cr, k0):
                    for j, (num, lab, y) in enumerate((("-4,000", "JOBS", 330), ("-30%", "HARVEST", 520))):
                        kn = eout(prog(T, st6b + 0.15 + j * 0.3, 0.4))
                        text(cr, num, CX - 40, y, 120, face=FONT_TITLE, c=RED, align="right", a=kn)
                        text(cr, lab, CX + 10, y, 80, face=FONT_TITLE, c=GRAY, align="left", a=kn)
                    kf = K.pop(T, t_fam)
                    if kf > 0:
                        with xform(cr, CX, 900, max(0.01, kf)):
                            for j, (dx, s_, a2) in enumerate(((-90, 0.75, ("hat",)), (30, 0.65, ("ponytail",)),
                                                              (120, 0.42, ("cap",)))):
                                p = sm.pose("front", x=dx, s=s_, smile=-0.1, brow=-0.3)
                                sm.draw(cr, sm.on_ground(sm.idle(p, T, j), 60), acc=a2)
                        text(cr, "= A REAL FAMILY", CX, 1010, 44, face=FONT_TITLE, a=clamp(kf))
            for i, (lab, x, acc, bgc) in enumerate((("A FARMER", 520, ("hat",), (1.0, 0.85, 0.6)),
                                                    ("A WORKER", 1400, ("hardhat",), (0.75, 0.80, 0.90)))):
                kk = K.pop(T, w("c5_06b", ["farmer", "worker"][i]))
                if kk <= 0:
                    continue
                with xform(cr, x, 520, max(0.01, kk)):
                    rrect(cr, -330, -330, 660, 620, 24, fill=bgc, stroke=INK, lw=8)
                    for j, (dx, s_, a2) in enumerate(((-130, 1.0, acc), (40, 0.85, ("ponytail",)), (170, 0.55, ("cap",)))):
                        p = sm.pose("front", x=dx, s=s_, smile=-0.1 if i else 0.0, brow=-0.4)
                        p = sm.on_ground(sm.idle(p, T, j + i * 3), 260)
                        sm.draw(cr, p, acc=a2)
                text(cr, lab, x, 930, 50, face=FONT_TITLE, a=clamp(kk))
            text(cr, "BEHIND EVERY NUMBER", CX, 110, 56, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
    b.fx(w("c5_06b", "farmer"), "pop", -10)
    b.fx(w("c5_06b", "worker"), "pop", -10)
    b.fx(w("c5_06b", "real family"), "pop", -14)

    # 7. up all night
    st7 = s("c5_07") - 0.15

    @b.shot(st7, "fade", 0.4)
    def night(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, 900, 560):
            S.dark_room(cr, T, 900, 280, flicker=0.1)
            P.desk(cr, 900, 880, 700)
            for i in range(9):
                g = rng(i)
                with xform(cr, 650 + i * 60, 700 + g.uniform(-10, 10), 0.5, g.uniform(-0.4, 0.4)):
                    rect(cr, -60, -40, 120, 80, fill=(0.92, 0.90, 0.84), stroke=(0.3, 0.3, 0.35), lw=3)
            P.clock(cr, 1500, 300, 70, T * 300, hours=2, minutes=0, speed=60, face=(0.85, 0.85, 0.8), ink=INK)
            p = sm.pose("sit", x=760, face=1, a1f=35, a2f=135, a1b=50, a2b=60, smile=-0.4, brow=-0.6, gy=0.3)
            p = sm.on_ground(sm.idle(p, T, 4), 880)
            sm.draw(cr, p, acc=KING, ink=(0.86, 0.87, 0.90), fill=(0.12, 0.13, 0.17))
        vignette(cr, 0.5)
    b.fx(st7, "tick", -10)
    b.fx(st7 + 1.0, "tock", -10)
    b.fx(st7 + 2.0, "tick", -12)

    # 8. Shakespeare
    st8 = s("c5_08") - 0.15
    b.add(st8, K.quote(["UNEASY LIES THE HEAD", "THAT WEARS A CROWN."], w("c5_08", "uneasy"), author="William Shakespeare"),
          "fade", 0.4)
    b.fx(w("c5_08", "uneasy"), "chime", -12)

    # 9. the crown gets heavier
    st9 = s("c5_09") - 0.15

    @b.shot(st9, "fade", 0.3)
    def heavy(cr, t, d, T):
        k = ease(prog(t, 0.2, d - 0.4))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.palace(cr, T)
            p = sm.pose("stand", x=CX, face=1, lean=lerp(0, 25, k), head=lerp(0, 25, k), smile=lerp(0.1, -0.6, k),
                        brow=-0.6 * k, a1f=10, a1b=-10)
            p = sm.on_ground(sm.walk(p, T, 0.4, 0.4), 900)
            J = sm.draw(cr, p, acc=("tuft", "cape"))
            P.crown(cr, J["head"][0], J["head"][1] - 50 - 30 * k, 0.55 + 0.9 * k)
            label_box(cr, f"{int(1 + 99 * k)} KG", J["head"][0] + 200, J["head"][1] - 160, 40, c=RED)
    b.fx(st9 + 0.3, "strain", -10, dur=2.5)

    # 10. experts, evidence, honest explanation
    st10 = s("c5_10") - 0.15
    t_exp, t_evi, t_exp2 = w("c5_10", "experts"), w("c5_10", "evidence"), w("c5_10", "explain")

    @b.shot(st10, "fade", 0.4)
    def experts(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.palace(cr, T, warm=0.6)
            ke = prog(T, t_exp2 - 0.3, 0.6)
            if ke < 1:
                with group(cr, 1 - ke):
                    K.hero(cr, T, CX, 800, "think", acc=KING, face=1, s=0.8)
                    ellipse(cr, CX, 800, 520, 90, fill=(0.55, 0.38, 0.22), stroke=INK, w=6)
                    rect(cr, CX - 380, 800, 20, 100, fill=(0.45, 0.30, 0.18), stroke=INK, lw=4)
                    rect(cr, CX + 360, 800, 20, 100, fill=(0.45, 0.30, 0.18), stroke=INK, lw=4)
                    for i, (x, acc) in enumerate(((520, ("labcoat", "glasses")), (760, ("hardhat",)), (1160, ("glasses", "tie")),
                                                 (1400, ("hat",)))):
                        k = K.pop(T, t_exp + i * 0.2)
                        if k > 0:
                            K.person(cr, T, x, 900, "present" if i % 2 else "point", face=1 if x < CX else -1, s=0.9,
                                     acc=acc, seed=i, alpha=clamp(k))
                    kv = prog(T, t_evi - 0.2, 0.5)
                    if kv > 0:
                        P.bar_chart(cr, CX, 360, [3, 5, 4, 7], None, w=360, h=200, p=kv, size=24)
            if ke > 0:
                with group(cr, ke):
                    rect(cr, CX - 120, 640, 240, 260, fill=(0.55, 0.38, 0.22), stroke=INK, lw=6)
                    line(cr, CX + 60, 640, CX + 120, 520, 6, INK)
                    circle(cr, CX + 125, 510, 16, fill=INK)
                    J = K.hero(cr, T, CX - 10, 900, "present", acc=KING, face=1, talk=0.5 + 0.5 * math.sin(T * 9))
                    text(cr, "HERE'S WHAT WE KNOW...", CX, 300, 56, face=FONT_TITLE, c=WHITE, outline=INK, ow=8)
                    del J
    for i in range(4):
        b.fx(t_exp + i * 0.2, "pop", -12)
    b.fx(t_exp2 - 0.3, "whoosh", -12)

    # 11. trust rises
    st11 = s("c5_11") - 0.3
    t_truth = w("c5_11", "truth")

    @b.shot(st11, "fade", 0.4)
    def trust(cr, t, d, T):
        with K.ken(cr, t, d, 1.04, 1.0, 1200, 600):
            balcony(cr, T, crowd_cheer=0.3)
            K.hero(cr, T, 1500, 600, "present", acc=KING, face=-1, smile=0.6)
        kt = prog(T, st11 + 0.4, d - 0.6)
        rrect(cr, 60, 60, 520, 120, 20, fill=WHITE, stroke=INK, lw=5)
        text(cr, "TRUST", 140, 120, 40, face=FONT_TITLE)
        rrect(cr, 230, 100, 320, 40, 18, fill=LIGHT)
        rrect(cr, 230, 100, 320 * lerp(0.3, 0.75, ease(kt)), 40, 18, fill=GREEN)
        if T > t_truth:
            label_box(cr, "YOU TOLD THE TRUTH", CX, 1000, 44, c=INK, scale=K.pop(T, t_truth))
    b.fx(st11 + 0.4, "rise", -12)
    return b.result()
