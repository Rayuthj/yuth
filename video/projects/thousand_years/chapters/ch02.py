"""Thousand Years - Chapter 2: The First Hundred Years (0:40-1:40)."""
from video.projects.thousand_years.chapters._t import *  # noqa: F401,F403

T1 = title_elapsed()


def music_plan(tl):
    return K.music(tl, [(0.6, "playful", "playful", 108, 0.7), ("c2_04", "discovery", "discovery", 96, 0.6),
                        ("c2_06", "wonder", "wonder", 80, 0.6), ("c2_07", "playful", "playful_g", 104, 0.65)])


def school(cr, x, gy, s=1.0):
    with xform(cr, x, gy, s):
        rect(cr, -380, -460, 760, 460, fill=(0.95, 0.88, 0.78), stroke=INK, lw=6)
        polyline(cr, [(-420, -460), (0, -620), (420, -460)], 6, INK, closed=True, fill=RED)
        rrect(cr, -150, -580, 300, 60, 10, fill=WHITE, stroke=INK, lw=4)
        text(cr, "SCHOOL", 0, -550, 40, face=FONT_TITLE)
        for i in range(3):
            rect(cr, -320 + i * 230, -400, 150, 130, fill=(0.85, 0.93, 1.0), stroke=INK, lw=5)
        rect(cr, -60, -180, 120, 180, fill=(0.45, 0.30, 0.2), stroke=INK, lw=5)


def party_hat(cr, J, s=1.0, c=PURPLE):
    hx, hy = J["head"]
    polyline(cr, [(hx - 26 * s, hy - 32 * s), (hx + 4 * s, hy - 110 * s), (hx + 30 * s, hy - 30 * s)], 3 * s, INK,
             closed=True, fill=c)
    circle(cr, hx + 4 * s, hy - 112 * s, 9 * s, fill=YELLOW, stroke=INK, w=2.5 * s)
    for k in range(3):
        circle(cr, hx - 6 * s + k * 10 * s, hy - 52 * s - k * 16 * s, 4 * s, fill=YELLOW)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    @b.shot(0)
    def title_out(cr, t, d, T):
        TITLE(cr, T1 + t)

    # 1. school, friends, pizza
    t_fr, t_piz = w("c2_01", "friends"), w("c2_01", "love") - 0.1

    @b.shot(0.7, "zoom", 0.6)
    def kids(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, 900, 600):
            S.park(cr, T, gy=900)
            school(cr, 1420, 900, 0.95)
            K.hero(cr, T, 640, 900, "hold" if T > t_piz else "stand", s=0.72, face=1, smile=1.0 if T > t_piz else 0.5)
            for i, (x, acc, f) in enumerate(((420, ("cap",), 1), (860, ("ponytail",), -1))):
                g = "wave" if t_fr < T < t_fr + 1.6 else "stand"
                kid(cr, T, x, 900, g, face=f, acc=acc, seed=i, s=0.72, smile=0.8)
            if T > t_piz:
                J = sm.joints(sm.on_ground(sm.pose("hold", x=640, s=0.72, face=1), 900))
                pizza(cr, J["hand_f"][0] + 20, J["hand_f"][1] - 40, 0.8, -0.3)
                for i in range(4):
                    f = (T - t_piz) * 0.6 + i * 0.25
                    if f % 1 < 0.95 and T - t_piz > i * 0.25:
                        ff = f % 1
                        P.heart(cr, 640 + 60 * math.sin(i * 2 + ff * 4), 560 - 260 * ff, 0.45, a=1 - ff)
        age_badge(cr, 10, k=K.pop(T, 1.0))
    b.fx(0.7, "whoosh", -8)
    b.fx(t_fr, "laugh", -16)
    b.fx(t_piz, "boing", -12)

    # 2. by forty: you look great for your age
    st2 = s("c2_02") - 0.15
    t_say = w("c2_02", "people say")

    @b.shot(st2, "slide", 0.4)
    def forty(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.office(cr, T, fy=900)
            J = K.person(cr, T, 1250, 900, "point" if T > t_say else "stand", face=-1, acc=("glasses", "mustache"),
                         seed=2, talk=0.6 if T > t_say else None, brow=0.2)
            gray_hair(cr, J, 1.0, "puffs", c=(0.6, 0.6, 0.62))
            K.hero(cr, T, 760, 900, "confident" if T > t_say + 0.5 else "stand", face=1, acc=("tuft", "tie"))
            say(cr, "You look great for your age!", 1180, 330, 1210, 520, K.pop(T, t_say), size=42)
        age_badge(cr, 40)
    b.fx(st2, "whoosh", -10)
    b.fx(t_say, "pop", -12)

    # 3. by seventy: gray hair, bad knees - you still look 25
    st3 = s("c2_03") - 0.15
    t_gray, t_knee, t_25 = w("c2_03", "gray hair"), w("c2_03", "bad knees"), w("c2_03", "twenty-five")

    @b.shot(st3, "slide", 0.4)
    def seventy(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.park(cr, T, gy=900)
            Js = []
            for i, (x, acc, st_) in enumerate(((330, ("glasses",), "puffs"), (580, (), "bun"), (830, ("cap",), "puffs"))):
                Js.append(oldie(cr, T, x, 900, face=1, acc=acc, style=st_, seed=i, bend=1.2))
            K.hero(cr, T, 1380, 900, "confident" if T > t_25 else "stand", face=-1, smile=0.9)
            kg = K.pop(T, t_gray)
            if kg > 0:
                label_box(cr, "GRAY HAIR", 580, 330, 44, c=INK, scale=kg)
                arrow(cr, 580, 365, Js[1]["head"][0], Js[1]["head"][1] - 55, 6, INK, head=20, p=clamp(kg))
            kk = K.pop(T, t_knee)
            if kk > 0:
                for J in Js:
                    kx, ky = J["knee_f"]
                    for j in range(2):
                        ph = (T * 3 + j * 0.5) % 1
                        polyline(cr, [(kx + 18 + j * 6, ky - 22), (kx + 34 + j * 6, ky - 8), (kx + 22 + j * 6, ky + 2),
                                      (kx + 40 + j * 6, ky + 18)], 4, RED, a=clamp(kk) * (1 - ph * 0.5))
                label_box(cr, "BAD KNEES", 580, 990, 44, c=RED, scale=kk)
            k25 = K.pop(T, t_25)
            if k25 > 0:
                label_box(cr, "STILL LOOKS 25", 1380, 420, 50, c=WHITE, bg=GREEN, face=FONT_TITLE, bold=False, scale=k25)
                sparkles(cr, T, 1380, 700, 160, 180, n=7, seed=5)
        age_badge(cr, 70)
    b.fx(st3, "whoosh", -10)
    b.fx(t_gray, "pop", -12)
    b.fx(t_knee, "crack", -12)
    b.fx(t_25, "sparkle", -10)

    # 3b. 50th reunion: are you somebody's grandchild?
    st4 = s("c2_03b") - 0.15
    t_ask = w("c2_03b", "someone asks")

    @b.shot(st4, "fade", 0.3)
    def reunion(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 620):
            S.room(cr, T, wall=(0.92, 0.88, 0.96), floor_c=(0.62, 0.50, 0.42), fy=900)
            for i, x in enumerate((140, 260, 1680, 1800)):
                yy = 330 + 20 * math.sin(T * 1.5 + i)
                line(cr, x, yy + 60, x + 10, 900, 2, GRAY)
                ellipse(cr, x, yy, 44, 56, fill=[RED, YELLOW, BLUE, GREEN][i], stroke=INK, w=4)
            rrect(cr, 460, 140, 1000, 120, 16, fill=(0.25, 0.35, 0.65), stroke=INK, lw=5)
            text(cr, "50TH CLASS REUNION", CX, 200, 64, face=FONT_TITLE, c=WHITE)
            for i, (x, acc, st_) in enumerate(((330, ("glasses",), "puffs"), (520, ("cap",), "puffs"),
                                               (1500, (), "bun"), (1700, ("glasses",), "puffs"))):
                oldie(cr, T, x, 900, face=1 if x < CX else -1, acc=acc, style=st_, seed=i, cane=i % 2 == 0, s=0.92)
            ka = ease(prog(T, t_ask - 0.4, 0.5))
            J = oldie(cr, T, 1120, 900, "stand", face=-1, acc=("glasses",), style="bun", seed=7, cane=False,
                      lean=14 + 22 * ka, head=8 + 12 * ka, a1f=70 * ka, a2f=20, smile=0.7, talk=0.5 if T > t_ask else None)
            awk = T > t_ask + 1.4
            K.hero(cr, T, 830, 900, "facepalm" if awk else "stand", face=1, smile=0.2 if awk else 0.5, eye=1.15)
            say(cr, "Are you somebody's grandchild?", 1280, 400, J["head"][0], J["head"][1] - 40, K.pop(T, t_ask), size=40,
                maxw=440)
    b.fx(st4, "murmur", -16, dur=3.0)
    b.fx(t_ask, "pop", -12)
    b.fx(t_ask + 1.4, "bonk", -14)

    # 4. reality check
    st5 = s("c2_04") - 0.15
    t_old = w("c2_04", "the oldest")

    @b.shot(st5, "cut")
    def reality(cr, t, d, T):
        fill_bg(cr, PAPER2)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 520):
            p = sm.pose("point_up", s=1.9, fo=0.0, smile=0.1, browy=0.4)
            p = head_at(sm.idle(p, T, 5), CX - 160, 400)
            sm.draw(cr, p, acc=HERO)
            stamp(cr, "REALITY CHECK", 1300, 360, t - 0.25, 72, c=RED, rot=0.08)
    b.fx(st5, "scratch", -4)
    b.fx(st5 + 0.25, "stamp", -8)

    # 4b. Jeanne Calment, 122
    t_name, t_fr2, t_122 = w("c2_04", "jeanne"), w("c2_04", "france"), w("c2_04", "one hundred")

    @b.shot(t_old - 0.15, "slide", 0.4)
    def record(cr, t, d, T):
        vgrad(cr, (0.16, 0.18, 0.32), (0.05, 0.05, 0.12))
        glow(cr, 560, 560, 520, YELLOW, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            title_text(cr, "OLDEST PERSON EVER VERIFIED", 140, 62, c=YELLOW, k=eout(prog(t, 0.05, 0.4)))
            with xform(cr, 560, 580, 1.0, -0.03):
                rect(cr, -230, -280, 460, 560, fill=(0.62, 0.45, 0.25), stroke=INK, lw=6)
                rect(cr, -195, -245, 390, 490, fill=SEPIA, stroke=INK, lw=4)
                cr.save()
                cr.rectangle(-195, -245, 390, 490)
                cr.clip()
                p = sm.pose("front", s=1.5, fo=0.0, smile=0.7, eye=0.9)
                p = head_at(p, 0, -40)
                J = sm.draw(cr, p, ink=SEPIA_D, fill=(0.95, 0.88, 0.72), acc=("glasses",))
                gray_hair(cr, J, 1.5, "bun", c=(0.97, 0.95, 0.90))
                cr.restore()
                cr.new_path()
            kn = eout(prog(T, t_name, 0.4))
            text(cr, "JEANNE CALMENT", 1320, 360, 72, face=FONT_TITLE, c=WHITE, a=kn)
            kf = K.pop(T, t_fr2)
            if kf > 0:
                flag(cr, 1130, 500, 0.55 * kf + 0.01, "fr")
                text(cr, "FRANCE", 1220, 500, 52, face=FONT_TITLE, c=WHITE, a=clamp(kf), align="left")
                text(cr, "1875 - 1997", 1320, 600, 44, face=FONT_BOLD, c=(0.75, 0.78, 0.9), a=clamp(kf))
            k1 = prog(T, t_122, 0.35)
            if k1 > 0:
                glow(cr, 1320, 800, 360, YELLOW, 0.3 * k1)
                text(cr, "122 YEARS", 1320, 800, 150, face=FONT_TITLE, c=YELLOW, outline=(0.3, 0.2, 0.0), ow=10,
                     scale=lerp(2.2, 1.0, eout(k1)), a=clamp(k1 * 3))
                burst(cr, 1320, 800, T - t_122 - 0.2, n=22, dist=420, size=9, c=YELLOW, dur=0.8)
        vignette(cr, 0.35)
    b.fx(t_old - 0.1, "whoosh", -10)
    b.fx(t_fr2, "pop", -12)
    b.fx(t_122 + 0.2, "boom_soft", -6)

    # 5. nobody knows how to stop aging: science fiction
    st6 = s("c2_05") - 0.15
    t_stop, t_sf = w("c2_05", "stop"), w("c2_05", "science fiction")

    @b.shot(st6, "fade", 0.3)
    def lab(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.room(cr, T, wall=(0.88, 0.92, 0.94), floor_c=(0.72, 0.74, 0.78), fy=900)
            P.chalkboard(cr, 1140, 400, 1000, 400)
            text(cr, "HOW TO STOP AGING:", 1140, 300, 64, face=FONT_HAND, bold=True, c=WHITE, a=eout(prog(t, 0.0, 0.3)))
            if T > t_stop:
                for i in range(3):
                    k = K.pop(T, t_stop + 0.2 + i * 0.25)
                    text(cr, "?", 940 + i * 200, 470, 130, face=FONT_TITLE, c=YELLOW, scale=max(0.01, k))
            P.desk(cr, 1500, 900, 380)
            P.flask(cr, 1420, 750, 0.8, c=GREEN, t=T)
            P.flask(cr, 1560, 750, 0.6, c=PURPLE, t=T + 1)
            K.person(cr, T, 420, 900, "shrug" if T > t_stop + 0.3 else "think", face=1, acc=("labcoat", "glasses"),
                     seed=3, smile=0.0)
            if T > t_sf:
                stamp(cr, "PURE SCIENCE FICTION", 1140, 790, T - t_sf, 64, c=PURPLE, rot=-0.06)
    b.fx(t_stop + 0.2, "blips", -14)
    b.fx(t_sf, "stamp", -6)

    # 6. Greenland sharks
    st7 = s("c2_06") - 0.15
    t_gs, t_400, t_bc, t_5k = (w("c2_06", "greenland"), w("c2_06", "four hundred"), w("c2_06", "bristlecone"),
                               w("c2_06", "five thousand"))

    @b.shot(st7, "fade", 0.4)
    def shark_shot(cr, t, d, T):
        vgrad(cr, (0.20, 0.42, 0.55), (0.03, 0.10, 0.18))
        for i in range(6):
            x = 200 + i * 320 + 40 * math.sin(T * 0.3 + i)
            polyline(cr, [(x, 0), (x + 120, 0), (x + 260, H), (x + 60, H)], 0, INK, closed=True, fill=WHITE, fa=0.05)
        g = rng(2)
        for i in range(10):
            w_ = g.uniform(160, 340)
            x = g.uniform(-100, W)
            polyline(cr, [(x, 0), (x + w_, 0), (x + w_ - 30, 40 + g.uniform(0, 30)), (x + 30, 50)], 4, (0.5, 0.65, 0.75),
                     closed=True, fill=(0.92, 0.97, 1.0))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            for i in range(30):
                gg = rng(i + 10)
                circle(cr, gg.uniform(0, W), (gg.uniform(0, H) - T * 20 * gg.uniform(0.5, 1.5)) % H, gg.uniform(2, 5),
                       fill=WHITE, a=0.25)
            x = lerp(1450, 650, t / max(d, 1))
            shark(cr, x, 560, 1.25, T, face=-1)
            for i in range(3):
                f = (T * 0.8 + i * 0.33) % 1
                circle(cr, x - 330 + 20 * math.sin(i + T), 520 - 260 * f, 8 + 6 * f, stroke=WHITE, w=3, a=1 - f)
        title_text(cr, "NATURE'S SURPRISES", 160, 64, c=WHITE, k=eout(prog(t, 0.0, 0.3)))
        kg = K.pop(T, t_gs)
        if kg > 0:
            label_box(cr, "GREENLAND SHARK", CX, 850, 54, c=INK, bg=WHITE, face=FONT_TITLE, bold=False, scale=kg)
        k4 = K.pop(T, t_400)
        if k4 > 0:
            text(cr, "~400 YEARS", CX - 120, 970, 78, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, scale=k4)
            text(cr, "(ESTIMATED)", CX + 250, 975, 40, face=FONT_HAND, bold=True, c=WHITE, a=clamp(k4))
        vignette(cr, 0.35)
    b.fx(st7, "bubbles", -12, dur=3.0)
    b.fx(t_gs, "pop", -12)
    b.fx(t_400, "ding", -10)

    # 6b. bristlecone pines
    @b.shot(t_bc - 0.15, "fade", 0.4)
    def pine(cr, t, d, T):
        vgrad(cr, (0.98, 0.72, 0.50), (0.70, 0.78, 0.95))
        with K.ken(cr, t, d, 1.0, 1.06, 900, 600):
            P.sun(cr, 1600, 300, 80, T, c=(1.0, 0.85, 0.5))
            polyline(cr, [(-400, 760), (300, 600), (700, 520), (1100, 470), (1500, 560), (2300, 700), (2300, 1500),
                          (-400, 1500)], 0, INK, closed=True, fill=(0.72, 0.65, 0.58))
            polyline(cr, [(-400, 900), (500, 820), (1300, 790), (2300, 860), (2300, 1500), (-400, 1500)], 5, INK,
                     closed=True, fill=(0.82, 0.74, 0.62))
            for i in range(9):
                g = rng(i + 3)
                ellipse(cr, g.uniform(0, W), g.uniform(860, 1060), g.uniform(30, 70), g.uniform(14, 26),
                        fill=(0.66, 0.60, 0.55), stroke=INK, w=3)
            bristlecone(cr, 850, 830, 1.3, T)
            K.hero(cr, T, 1420, 850, "surprised" if T > t_5k else "point_up", face=-1, s=0.62, gy=-0.6)
        kb = K.pop(T, t_bc + 0.1)
        if kb > 0:
            label_box(cr, "BRISTLECONE PINE", CX, 160, 54, c=INK, bg=WHITE, face=FONT_TITLE, bold=False, scale=kb)
        k5 = K.pop(T, t_5k)
        if k5 > 0:
            text(cr, "NEARLY 5,000 YEARS OLD", CX, 990, 72, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, scale=k5)
    b.fx(t_bc - 0.1, "wind", -14, dur=3.0)
    b.fx(t_5k, "ding", -8)

    # 7. 100th birthday at the doctor's office
    st8 = s("c2_07") - 0.15
    t_look = w("c2_07", "strange looks")

    @b.shot(st8, "fade", 0.3)
    def doctor(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.room(cr, T, wall=(0.86, 0.94, 0.92), floor_c=(0.70, 0.76, 0.76), fy=900)
            rrect(cr, 300, 220, 220, 300, 10, fill=WHITE, stroke=INK, lw=5)
            for i, (txt, sz) in enumerate((("E", 90), ("F P", 56), ("T O Z", 40), ("L P E D", 28))):
                text(cr, txt, 410, 290 + i * 62, sz, face=FONT_BOLD)
            rect(cr, 1580, 260, 120, 120, fill=WHITE, stroke=INK, lw=5)
            rect(cr, 1625, 280, 30, 80, fill=RED)
            rect(cr, 1600, 305, 80, 30, fill=RED)
            rrect(cr, 700, 700, 420, 60, 12, fill=(0.75, 0.88, 0.95), stroke=INK, lw=5)
            line(cr, 740, 760, 740, 900, 8, INK)
            line(cr, 1080, 760, 1080, 900, 8, INK)
            p = sm.pose("sit", x=880, face=1, a1f=20, a2f=30, a1b=10, a2b=30, smile=0.8)
            p["y"] = 700
            J = sm.draw(cr, sm.idle(p, T, 2), acc=HERO)
            party_hat(cr, J)
            kl = T > t_look
            Jd = K.person(cr, T, 1380, 900, "hold", face=-1, acc=("labcoat", "glasses", "mustache"), seed=4,
                          eye=1.5 if kl else 1.0, browy=1.0 if kl else 0.0, mo=0.5 if kl else 0.0,
                          gx=0.8 if (int(T * 2.5) % 2 and kl) else 0.0, gy=0.6 if not kl else 0.0)
            with xform(cr, Jd["hand_f"][0] - 10, Jd["hand_f"][1] - 30, 1.0, 0.15):
                rect(cr, -60, -80, 120, 160, fill=(0.75, 0.55, 0.35), stroke=INK, lw=4)
                rect(cr, -48, -66, 96, 136, fill=WHITE)
                text(cr, "AGE:", 0, -36, 26, face=FONT_BOLD)
                text(cr, "100", 0, 10, 44, face=FONT_TITLE, c=RED)
            if kl:
                text(cr, "?!", Jd["head"][0], Jd["head"][1] - 110, 90, face=FONT_TITLE, c=RED, scale=K.pop(T, t_look))
        age_badge(cr, 100, c=RED, k=K.pop(T, st8 + 0.3))
    b.fx(st8 + 0.3, "ding", -12)
    b.fx(t_look, "boing", -10)

    # 7b. certificate says 100, face says college student
    st9 = s("c2_07b") - 0.15
    t_cert, t_100, t_face, t_col = (w("c2_07b", "certificate"), w("c2_07b", "one hundred"), w("c2_07b", "face"),
                                    w("c2_07b", "college"))

    @b.shot(st9, "fade", 0.3)
    def cert(cr, t, d, T):
        fill_bg(cr, (0.96, 0.92, 0.84))
        rect(cr, CX, 0, W / 2, H, fill=(0.80, 0.88, 0.98))
        line(cr, CX, 0, CX, H, 8, INK)
        with K.ken(cr, t, d, 1.0, 1.03, CX, 560):
            kc = K.pop(T, t_cert - 0.3)
            if kc > 0:
                certificate(cr, 480, 560, 0.95 * max(0.01, kc), rows=(("NAME", "YOU"), ("BORN", "100 YEARS AGO")),
                            big="100" if T > t_100 else None, rot=-0.03)
            p = sm.pose("front", s=2.6, fo=0.0, smile=0.8, eye=1.1)
            p = head_at(sm.idle(p, T, 3), 1440, 560)
            J = sm.draw(cr, p, acc=HERO)
            if T > t_col:
                mortarboard(cr, J, 2.6 * clamp(K.pop(T, t_col)) + 0.01)
        kf = eout(prog(T, t_face, 0.3))
        text(cr, "BIRTH CERTIFICATE", 480, 120, 54, face=FONT_TITLE, a=eout(prog(t, 0.0, 0.3)))
        text(cr, "YOUR FACE", 1440, 120, 54, face=FONT_TITLE, a=kf)
        if T > t_col:
            label_box(cr, "COLLEGE STUDENT", 1440, 960, 54, c=WHITE, bg=BLUE, face=FONT_TITLE, bold=False,
                      scale=K.pop(T, t_col))
    b.fx(t_cert - 0.3, "page", -8)
    b.fx(t_100, "stamp", -8)
    b.fx(t_col, "pop", -10)

    # 8. still nine hundred years to go
    st10 = s("c2_08") - 0.15
    t_900 = w("c2_08", "nine hundred")
    x0, x1, ly = 150, 1770, 720

    @b.shot(st10, "fade", 0.3)
    def to_go(cr, t, d, T):
        vgrad(cr, (0.98, 0.94, 0.84), (0.92, 0.86, 0.74))
        k = ease(prog(T, t_900 - 0.8, 1.3))
        z = lerp(2.4, 1.0, k)
        hx = x0 + 0.1 * (x1 - x0)
        with camera(cr, z, lerp(hx + 120, CX, k), lerp(ly - 120, 560, k)):
            line(cr, x0, ly, x1, ly, 14, INK)
            for i in range(11):
                x = x0 + i * (x1 - x0) / 10
                line(cr, x, ly - 20, x, ly + 20, 6, INK)
                text(cr, f"{i * 100}", x, ly + 60, 34, face=FONT_BOLD)
            line(cr, x0, ly, hx, ly, 18, GREEN)
            kh = prog(T, t_900, 0.8)
            if kh > 0:
                line(cr, hx, ly, lerp(hx, x1, ease(kh)), ly, 18, YELLOW)
            K.hero(cr, T, hx, ly - 8, "worried" if T > t_900 else "stand", face=1, s=0.5, gx=0.8)
            text(cr, "YOU", hx, ly - 210, 30, face=FONT_TITLE, c=GREEN)
        text(cr, "YEARS", CX, 880, 40, face=FONT_BOLD, c=GRAY, a=k)
        if T > t_900:
            k9 = K.pop(T, t_900 + 0.5)
            text(cr, "900 YEARS TO GO", 1150, 380, 110, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10, scale=max(0.01, k9))
    b.fx(t_900 - 0.8, "whoosh", -10)
    b.fx(t_900 + 0.5, "gulp", -8)
    return b.result()
