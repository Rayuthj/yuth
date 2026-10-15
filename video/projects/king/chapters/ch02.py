"""King - Chapter 2: Day One in the Palace (0:40-1:40)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403


def music_plan(tl):
    return K.music(tl, [(0.6, "discovery", "discovery", 100, 0.8), ("c2_05", "warm", "warm", 84, 0.6),
                        ("c2_08", "uplift", "uplift", 104, 0.7)])


def corridor(cr, T, cam):
    fill_bg(cr, (0.70, 0.45, 0.32))
    with xform(cr, -cam, 0):
        for i in range(-1, 14):
            x = i * 300
            rect(cr, x + 60, 300, 160, 560, fill=(0.55, 0.36, 0.24), stroke=INK, lw=5)
            circle(cr, x + 200, 600, 8, fill=YELLOW)
            label_box(cr, f"{i * 23 % 300 + 1}", x + 140, 260, 26, c=INK, bg=(0.95, 0.85, 0.6))
            P.lightbulb(cr, x + 290, 220, 0.25, on=0.6)
    S.floor(cr, 880, (0.65, 0.12, 0.15))


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    @b.shot(0)
    def title_out(cr, t, d, T):
        TITLE(cr, 2.65 + t)

    # 1. three hundred rooms, lost on the way to breakfast
    @b.shot(0.7, "zoom", 0.6)
    def lost(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            corridor(cr, T, T * 160)
            p = sm.walk(sm.pose(x=CX, face=1, smile=0.2, gx=0.7, brow=-0.3), T, 0.9)
            if T > w("c2_01", "lost"):
                p = sm.apply(sm.pose("think", x=CX, face=-1, gx=-0.8), brow=-0.5, smile=-0.2)
            p = sm.on_ground(p, 880)
            sm.draw(cr, p, acc=KING)
        text(cr, "300 ROOMS", 260, 140, 70, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8,
             a=eout(prog(T, w("c2_01", "three hundred"), 0.4)))
        if T > w("c2_01", "lost"):
            label_box(cr, "BREAKFAST: ???", 1500, 150, 44, c=INK, bg=WHITE, scale=K.pop(T, w("c2_01", "lost")))
    b.fx(0.7, "whoosh", -8)
    b.fx(0.9, "footsteps", -14, dur=3.0)
    b.fx(w("c2_01", "lost"), "boing", -12)

    # 2. a chef, a guard, a giant bed
    st2 = s("c2_02") - 0.15

    def ic_chef(cr, T):
        p = sm.on_ground(sm.pose("hold", x=0, s=0.8, smile=0.8), 110)
        J = sm.draw(cr, p, acc=("chef", "mustache"))
        ellipse(cr, J["hand_f"][0] + 30, J["hand_f"][1] - 6, 70, 14, fill=LIGHT, stroke=INK, w=4)
        arc(cr, J["hand_f"][0] + 30, J["hand_f"][1] - 10, 50, math.pi, TAU, 5, INK)

    def ic_guard(cr, T):
        p = sm.on_ground(sm.pose("stand", x=0, s=0.8, a1f=0, a1b=0, smile=-0.1), 110)
        J = sm.draw(cr, p, acc=GUARD)
        line(cr, J["hand_f"][0] + 10, J["hand_f"][1] + 30, J["hand_f"][0] + 10, J["hand_f"][1] - 180, 6, GRAY)

    def ic_bed(cr, T):
        rrect(cr, -190, -30, 380, 90, 20, fill=WHITE, stroke=INK, lw=5)
        rrect(cr, -190, -60, 380, 50, 20, fill=(0.65, 0.08, 0.14), stroke=INK, lw=5)
        for i in range(6):
            rrect(cr, -180 + i * 60, -90, 50, 30, 12, fill=WHITE, stroke=INK, lw=3)
        p = sm.pose("front", s=0.22, smile=0.9)
        with xform(cr, 0, -50, 1.0, -math.pi / 2):
            sm.draw(cr, head_at(p, 0, 0), acc=("tuft",))

    b.add(st2, K.icons("", [(ic_chef, "A CHEF FOR EVERY MEAL", w("c2_02", "chef")),
                            (ic_guard, "A GUARD AT EVERY DOOR", w("c2_02", "guard")),
                            (ic_bed, "A BED THE SIZE OF A POOL", w("c2_02", "bed"))],
                       bg=(0.97, 0.93, 0.85), y=520, size=1.15, label_size=31), "slide", 0.4)
    for wd in ("chef", "guard", "bed"):
        b.fx(w("c2_02", wd), "pop", -8)

    # 2b. servants bow; someone offers to tie your shoes
    st2b = s("c2_02b") - 0.15
    t_shoe = w("c2_02b", "shoes")

    @b.shot(st2b, "fade", 0.3)
    def servants(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, CX, 640):
            S.palace(cr, T)
            for i, x in enumerate((420, 640, 1280, 1500)):
                K.person(cr, T, x, 880, "stand", face=1 if x < CX else -1, acc=("bowtie",), seed=i,
                         lean=35 * ease(prog(T, st2b + 0.2 + i * 0.1, 0.4)), head=20, a1f=10, a1b=-10)
            k = ease(prog(T, t_shoe - 0.6, 0.6))
            sx = lerp(1100, 1040, k)
            K.person(cr, T, sx, 880, "stand", face=-1, acc=("bowtie", "glasses"), lean=55 * k, head=25 * k,
                     a1f=90 * k, a2f=10, l1f=60 * k, l2f=-90 * k, smile=0.8)
            K.hero(cr, T, 900, 880, "surprised" if T > t_shoe else "stand", acc=KING, face=1, eye=1.2)
            if T > t_shoe:
                text(cr, "uh... thanks?", 900, 420, 46, face=FONT_HAND, bold=True, a=prog(T, t_shoe, 0.3))
    b.fx(t_shoe, "boing", -12)

    # 3-4. the advisor and his endless schedule
    st3 = s("c2_03") - 0.15
    items = [("9:00  BUDGET", "nine"), ("10:00  ARMY", "ten"), ("12:00  LUNCH", "twelve"), ("NO WARS BEFORE LUNCH", "please")]

    @b.shot(st3, "fade", 0.3)
    def schedule(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 540):
            S.palace(cr, T)
            un = ease(prog(T, w("c2_03", "schedule"), 1.4))
            # the scroll unrolls down the steps and across the floor
            rect(cr, 900, 330, 360, 550 * un + 10, fill=(0.96, 0.89, 0.72), stroke=INK, lw=5)
            if un > 0.95:
                polyline(cr, [(900, 880), (1260, 880), (1700, 880 + 30), (1300, 880 + 30)], 5, INK, closed=True,
                         fill=(0.96, 0.89, 0.72))
            ellipse(cr, 1080, 330, 200, 22, fill=(0.9, 0.8, 0.6), stroke=INK, w=5)
            for i, (lab, wd) in enumerate(items):
                if s("c2_04") <= T and T >= w("c2_04", wd) - 0.1:
                    text(cr, lab, 930, 400 + i * 70, 36 if i < 3 else 28, face=FONT_HAND, bold=True,
                         c=RED if i == 3 else INK, align="left", a=prog(T, w("c2_04", wd) - 0.1, 0.3))
            env = tl.env("c2_04", T)
            K.person(cr, T, 760, 880, "present" if env > 0 else "hold", face=1, acc=ADV, talk=env if T > s("c2_04") else None)
            K.hero(cr, T, 1500, 880, "surprised" if T > w("c2_03", "thicker") else "stand", acc=KING, face=-1, eye=1.2)
    b.fx(w("c2_03", "schedule"), "page", -6)
    b.fx(w("c2_03", "schedule") + 0.5, "roll", -12, dur=1.0)

    # 5. reality check
    st5 = s("c2_05") - 0.15

    @b.shot(st5, "cut")
    def honest(cr, t, d, T):
        fill_bg(cr, PAPER2)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 520):
            p = sm.pose("point_up", s=1.9, fo=0.0, smile=0.1, browy=0.4)
            p = head_at(sm.idle(p, T, 5), CX - 120, 360)
            sm.draw(cr, p, acc=KING)
            stamp(cr, "REALITY CHECK", 1360, 330, t - 0.25, 64, c=RED, rot=0.08)
    b.fx(st5, "scratch", -4)
    b.fx(st5 + 0.25, "stamp", -8)

    # 6. symbolic monarchs
    st6 = s("c2_06") - 0.15
    t_sym, t_gov = w("c2_06", "symbol"), w("c2_06", "elected")

    def flag_uk(cr, x, y, s_):
        with xform(cr, x, y, s_):
            rect(cr, -120, -70, 240, 140, fill=(0.0, 0.14, 0.5))
            line(cr, -120, -70, 120, 70, 26, WHITE)
            line(cr, -120, 70, 120, -70, 26, WHITE)
            line(cr, -120, -70, 120, 70, 9, (0.8, 0.1, 0.15))
            line(cr, -120, 70, 120, -70, 9, (0.8, 0.1, 0.15))
            rect(cr, -120, -18, 240, 36, fill=WHITE)
            rect(cr, -20, -70, 40, 140, fill=WHITE)
            rect(cr, -120, -11, 240, 22, fill=(0.8, 0.1, 0.15))
            rect(cr, -12, -70, 24, 140, fill=(0.8, 0.1, 0.15))
            rect(cr, -120, -70, 240, 140, stroke=INK, lw=4)

    def flag_jp(cr, x, y, s_):
        with xform(cr, x, y, s_):
            rect(cr, -120, -70, 240, 140, fill=WHITE, stroke=INK, lw=4)
            circle(cr, 0, 0, 42, fill=(0.75, 0.0, 0.15))

    def flag_se(cr, x, y, s_):
        with xform(cr, x, y, s_):
            rect(cr, -120, -70, 240, 140, fill=(0.0, 0.42, 0.66))
            rect(cr, -55, -70, 32, 140, fill=(1.0, 0.8, 0.0))
            rect(cr, -120, -16, 240, 32, fill=(1.0, 0.8, 0.0))
            rect(cr, -120, -70, 240, 140, stroke=INK, lw=4)

    @b.shot(st6, "fade", 0.3)
    def symbolic(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.03):
            text(cr, "MOST MONARCHS TODAY", CX, 120, 56, face=FONT_TITLE, a=eout(prog(t, 0.05, 0.4)))
            for i, (fn, name, wd) in enumerate(((flag_uk, "UNITED KINGDOM", "united"), (flag_jp, "JAPAN", "japan"),
                                                (flag_se, "SWEDEN", "sweden"))):
                k = K.pop(T, w("c2_06", wd))
                if k > 0:
                    x = 480 + i * 480
                    fn(cr, x, 300, max(0.01, k))
                    text(cr, name, x, 410, 34, face=FONT_BOLD, a=clamp(k))
            ks = K.pop(T, t_sym)
            if ks > 0:
                P.crown(cr, 620, 640, 0.9 * ks + 0.01)
                text(cr, "SYMBOL", 620, 760, 50, face=FONT_TITLE, c=GOLD, a=clamp(ks), outline=INK, ow=5)
            kg = K.pop(T, t_gov)
            if kg > 0:
                with xform(cr, 1300, 660, max(0.01, kg)):
                    polyline(cr, [(-170, 0), (0, -110), (170, 0)], 5, INK, closed=True, fill=LIGHT)
                    for i in range(5):
                        rect(cr, -150 + i * 70, 0, 22, 120, fill=WHITE, stroke=INK, lw=4)
                    rect(cr, -190, 120, 380, 20, fill=LIGHT, stroke=INK, lw=4)
                text(cr, "ELECTED GOVERNMENT DECIDES", 1300, 860, 40, face=FONT_TITLE, c=BLUE, a=clamp(kg))
    for wd in ("united", "japan", "sweden"):
        b.fx(w("c2_06", wd), "pop", -10)
    b.fx(t_gov, "ding", -10)

    # 7. a handful still have near-total power
    st7 = s("c2_07") - 0.15

    @b.shot(st7, "fade", 0.3)
    def handful(cr, t, d, T):
        vgrad(cr, (0.06, 0.08, 0.16), (0.02, 0.02, 0.06))
        stars(cr, T, n=120, alpha=0.6)
        with K.ken(cr, t, d, 1.0, 1.05):
            P.globe(cr, CX, 560, 300, T * 0.6)
            g = rng(9)
            for i in range(5):
                x, y = CX + g.uniform(-200, 200), 560 + g.uniform(-160, 160)
                k = K.pop(T, st7 + 0.6 + i * 0.25)
                if k > 0:
                    glow(cr, x, y, 60, YELLOW, 0.6)
                    P.crown(cr, x, y, 0.25 * k + 0.01)
            text(cr, "ONLY A HANDFUL", CX, 150, 64, face=FONT_TITLE, c=YELLOW, a=eout(prog(t, 0.3, 0.4)))
            text(cr, "STILL HAVE NEAR-TOTAL POWER", CX, 960, 48, face=FONT_TITLE, c=WHITE, a=eout(prog(t, 0.8, 0.4)))
    for i in range(5):
        b.fx(st7 + 0.6 + i * 0.25, "blip", -14)

    # 8. your word is law
    st8 = s("c2_08") - 0.15
    t_law = w("c2_08", "law")

    @b.shot(st8, "fade", 0.3)
    def word_law(cr, t, d, T):
        vgrad(cr, (0.40, 0.12, 0.12), (0.15, 0.04, 0.05))
        radial_lines(cr, CX, 420, T, n=30, c=YELLOW, a=0.12, w=22)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 560):
            P.throne(cr, CX, 900, 1.2)
            k = prog(T, t_law - 0.4, 0.3)
            p = sm.pose("sit", x=CX, fo=0.0, a1f=lerp(60, 150, k), a2f=lerp(40, 0, k), a1b=-60, a2b=-40, smile=0.5,
                        brow=0.5)
            p["y"] = 730
            J = sm.draw(cr, sm.idle(p, T, 3), acc=KING, ink=WHITE, fill=(0.3, 0.06, 0.08))
            P2.gavel(cr, J["hand_f"][0], J["hand_f"][1], 0.6, rot=lerp(-1.6, -0.3, k))
            stamp(cr, "YOUR WORD = LAW", CX, 180, T - t_law, 80, c=YELLOW, rot=-0.04)
    b.fx(t_law, "slam", -4)

    # 9. every decision changes millions of lives
    st9 = s("c2_09") - 0.3
    t_mil = w("c2_09", "millions")

    @b.shot(st9, "fade", 0.5)
    def millions(cr, t, d, T):
        vgrad(cr, (0.98, 0.75, 0.55), (0.55, 0.65, 0.90))
        z = lerp(1.25, 0.85, ease(t / d))
        with camera(cr, z, CX, 640):
            P.skyline(cr, -600, 1000, 3100, 320, seed=33, fill=(0.40, 0.36, 0.48), lit=True, t=T)
            rect(cr, -600, 1000, 3100, 400, fill=(0.30, 0.28, 0.36))
            k = prog(T, t_mil, 1.5)
            g = rng(4)
            for i in range(int(400 * k)):
                x, y = g.uniform(-500, 2400), g.uniform(1010, 1300)
                circle(cr, x, y, 3, fill=YELLOW, a=0.8)
            rect(cr, 760, 700, 400, 400, fill=(0.88, 0.82, 0.70), stroke=INK, lw=6)
            for i in range(9):
                line(cr, 780 + i * 45, 620, 780 + i * 45, 700, 6, INK)
            line(cr, 760, 620, 1160, 620, 8, INK)
            line(cr, 760, 700, 1160, 700, 10, INK)
            K.hero(cr, T, 960, 700, "stand", acc=KING, face=1, fo=0.3, gy=0.6, smile=-0.1, brow=-0.3)
        if k > 0:
            text(cr, "MILLIONS OF LIVES", CX, 150, 70, face=FONT_TITLE, c=WHITE, outline=INK, ow=8, a=clamp(k * 2))
    b.fx(t_mil, "swell", -10, dur=2.0)
    return b.result()
