"""No Sleep - Chapter 3: What Sleep Actually Does (1:40-2:40)."""
from video.projects.no_sleep.chapters._n import *  # noqa: F401,F403

SEPIA = (0.93, 0.86, 0.72)
BROWN = (0.30, 0.20, 0.12)


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "discovery", 92, 0.5), ("c3_02", "discovery", "discovery", 100, 0.6),
                        ("c3_05", "wonder", "wonder", 84, 0.55), ("c3_06", "discovery", "discovery_g", 100, 0.6),
                        ("c3_07", "mystery", "mystery", 70, 0.5), ("c3_08", "dark", "dark", 62, 0.5),
                        ("c3_09", "uplift", "uplift", 100, 0.7)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. but wait: why do nearly all animals sleep?
    t_wait, t_use, t_ani, t_some = (w("c3_01", "wait"), w("c3_01", "useless"), w("c3_01", "animals"),
                                    w("c3_01", "some way"))

    @b.shot(0, "fade", 0.3)
    def animals(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.floor(cr, 900, (0.88, 0.85, 0.78))
            K.hero(cr, T, 260, 920, "point_up" if T < t_ani + 0.5 else "think", face=1, brow=-0.3, smile=0.0)
            kw_ = K.pop(T, max(0.35, t_wait))
            if kw_ > 0 and T < t_ani:
                speech_bubble(cr, 470, 420, 300, 110, 300, 560, scale=kw_)
                text(cr, "WAIT...", 470, 420, 54, face=FONT_TITLE, a=clamp(kw_))
            if t_use < T < t_ani + 0.3:
                chip(cr, "SLEEP = USELESS?", 1150, 420, 56, bg=WHITE, scale=K.pop(T, t_use),
                     a=1 - prog(T, t_ani, 0.3))
            for i, (fn, x, y, sc) in enumerate(((cat_sleep, 720, 840, 1.0), (bat_hang, 1040, 440, 1.0),
                                                (bird_sleep, 1340, 880, 1.2), (fish, 1660, 760, 1.1))):
                k = K.pop(T, t_ani + i * 0.18)
                if k <= 0:
                    continue
                if fn is fish:
                    with xform(cr, x, y, 1.0):
                        circle(cr, 0, 0, 150 * max(0.01, k), fill=(0.75, 0.88, 1.0), stroke=INK, w=5)
                        cr.save()
                        cr.arc(0, 0, 148 * max(0.01, k), 0, TAU)
                        cr.clip()
                        fn(cr, 0, 10, sc * max(0.01, k), T)
                        cr.restore()
                        cr.new_path()
                else:
                    fn(cr, x, y, sc * max(0.01, k), T)
                zzz(cr, x + (110 if fn is bat_hang else 40), y + (170 if fn is bat_hang else -150), T, 1.0, seed=i,
                    a=clamp(k))
            if T > t_ani:
                text(cr, "NEARLY ALL ANIMALS SLEEP", 1190, 230, 64, face=FONT_TITLE, a=eout(prog(T, t_ani, 0.4)))
            if T > t_some:
                text(cr, "(in some way)", 1190, 310, 44, face=FONT_HAND, bold=True, c=GRAY, a=eout(prog(T, t_some, 0.4)))
    b.fx(max(0.35, t_wait), "pop", -10)
    b.fx(t_use, "boing", -14)
    for i in range(4):
        b.fx(t_ani + i * 0.18, "pop", -12)
    b.fx(t_ani + 0.6, "snore", -16, dur=1.5)

    # 2. scientists: sleep is incredibly busy
    st2 = s("c3_02") - 0.15
    t_busy = w("c3_02", "busy")

    @b.shot(st2, "fade", 0.3)
    def lab(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.room(cr, T, wall=(0.86, 0.90, 0.94), floor_c=(0.72, 0.76, 0.80), fy=880)
            bed2(cr, T, 560, 900, 1.2, who="sleep", z=True, seed=3)
            for i in range(3):
                polyline(cr, bezier_pts([(370 + i * 14, 700), (520 + i * 40, 520), (900, 470 + i * 20)], 16), 3,
                         [RED, BLUE, GREEN][i])
            busy = 0.3 + 0.7 * ease(prog(T, t_busy - 0.4, 0.6))
            P.monitor(cr, 1100, 470, 440, 280, screen=lambda c, x, y, w_, h_: eeg(c, x + 10, y + 10, w_ - 20, h_ - 20,
                                                                                  T, busy=busy))
            K.person(cr, T, 1500, 900, "hold", face=-1, acc=SCI, smile=0.3, eye=1.2 if T > t_busy else 1.0,
                     browy=0.6 if T > t_busy else 0.0)
            rect(cr, 1380, 640, 70, 90, fill=WHITE, stroke=INK, lw=4)
            text(cr, "SLEEP LAB", 300, 200, 50, face=FONT_TITLE, c=BLUE)
        if T > t_busy:
            stamp(cr, "INCREDIBLY BUSY!", 1150, 190, T - t_busy, 64, c=RED, rot=-0.05)
    b.fx(st2 + 0.3, "data", -14, dur=2.0)
    b.fx(t_busy, "stamp", -8)

    # 2b. not switching off: a factory on the night shift
    st2b = s("c3_02b") - 0.15
    t_more = w("c3_02b", "more like")

    def switch_off(cr, cx, T):
        light_switch(cr, cx, 560, 1.6, on=False)
        if T > t_more:
            cross_out(cr, cx, 560, 200, prog(T, t_more, 0.3), 22)

    def factory(cr, cx, T):
        stars(cr, T, n=80, alpha=0.7, area=(cx - 480, 200, cx + 480, 500))
        moon(cr, cx + 330, 290, 46)
        brain_factory(cr, cx, 640, 1.25, T)
        for i in range(3):
            janitor(cr, T, cx - 200 + i * 200, 1000, 0.42, face=1 if i % 2 else -1, ink=NI, fill=NF, tool="bucket",
                    seed=i)

    b.add(st2b, K.split(dict(title="SWITCHING OFF?", bg=(0.88, 0.88, 0.90), draw=switch_off),
                        dict(title="NIGHT-SHIFT FACTORY", bg=(0.07, 0.08, 0.18), draw=factory), t_more), "fade", 0.3)
    b.fx(t_more, "machine", -12, dur=2.5)
    b.fx(t_more, "scratch", -14)

    # 3. sorting the day, strengthening memories, filing them away
    st3 = s("c3_03") - 0.15
    t_sort, t_str, t_file = w("c3_03", "sorts"), w("c3_03", "strengthening"), w("c3_03", "filing")
    kinds = ["star", "ball", "heart", "pizza", "test", "cat", "face", "rocket"]
    important = {"star", "heart", "test", "face"}

    @b.shot(st3, "fade", 0.4)
    def sorting(cr, t, d, T):
        S.vgrad(cr, (0.30, 0.22, 0.40), (0.14, 0.10, 0.22))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            with group(cr, 0.35):
                P.brain(cr, CX, 560, 6.0, c=(1.0, 0.72, 0.78))
            moon(cr, 1760, 150, 40)
            rrect(cr, 120, 740, 1260, 40, 20, fill=(0.40, 0.40, 0.46), stroke=INK, lw=5)
            for i in range(14):
                circle(cr, 150 + i * 92, 760, 14, fill=(0.65, 0.65, 0.7), stroke=INK, w=3)
            filing_cabinet(cr, 1600, 900, 0.95, open_k=ease(prog(T, t_file - 0.3, 0.5)),
                           labels=("SCHOOL", "FRIENDS", "SKILLS"))
            v = 150
            for i in range(9):
                kind = kinds[i % len(kinds)]
                x = ((i * 190 + (T - st3) * v) % 1710) - 250
                imp = kind in important
                ks = ease(prog(T, t_str, 0.6))
                kf = ease(prog(T, t_file, 0.5))
                y = 680
                sc = 0.9
                a = 1.0
                if imp:
                    sc += 0.25 * ks
                    if x > 1250 and kf > 0:
                        f = clamp((x - 1250) / 200)
                        x = lerp(1250, 1640, f)
                        y = lerp(680, 600, f)
                        sc *= 1 - 0.6 * f
                else:
                    a = 1 - 0.65 * ks
                if x < 1460:
                    mem_card(cr, x, y, kind, sc, i, glow_a=0.6 * ks if imp else 0.0, a=a)
            K.person(cr, T, 760, 1040, "point" if (T * 1.3) % 2 < 1 else "present", face=1, acc=("hardhat",),
                     s=0.75, ink=NI, fill=NF, smile=0.7)
            for (lab, x, ta) in (("SORTING", 480, t_sort), ("STRENGTHENING", 960, t_str), ("FILING", 1460, t_file)):
                k = K.pop(T, ta)
                if k > 0:
                    chip(cr, lab, x, 250, 50, bg=YELLOW, scale=k)
        text(cr, "YOUR BRAIN AT NIGHT", 960, 140, 44, face=FONT_TITLE, c=WHITE, a=eout(prog(t, 0.1, 0.4)))
    b.fx(st3, "roll", -16, dur=4.0)
    b.fx(t_sort, "pop", -12)
    b.fx(t_str, "shimmer", -10)
    b.fx(t_file, "papers", -10)

    # 4. studies in mice suggest a nighttime cleaning crew
    st4 = s("c3_04") - 0.15
    t_mice, t_flush, t_crew = w("c3_04", "mice"), w("c3_04", "flushes"), w("c3_04", "cleaning crew")

    @b.shot(st4, "fade", 0.4)
    def cleaning(cr, t, d, T):
        night_bg(cr, T, 0.7)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.floor(cr, 930, (0.12, 0.12, 0.18), (0.3, 0.3, 0.38), 4)
            kf = prog(T, t_flush, 2.5)
            brain_big(cr, CX, 560, 3.0, T)
            g = rng(7)
            for i in range(26):
                a0 = g.uniform(0, TAU)
                r0 = g.uniform(30, 190)
                px, py = CX + math.cos(a0) * r0, 540 + math.sin(a0) * r0 * 0.8
                if kf > 0:
                    out = ease(clamp(kf * 1.4 - g.uniform(0, 0.4)))
                    px += math.cos(a0) * 500 * out
                    py += 300 * out
                    al = 1 - out
                else:
                    al = 1.0
                if al > 0.02:
                    circle(cr, px, py, g.uniform(6, 13), fill=[(0.55, 0.45, 0.20), (0.45, 0.55, 0.25)][i % 2],
                           stroke=INK, w=2, a=al)
            if kf > 0:
                for j in range(3):
                    ph = (T * 0.7 + j / 3) % 1
                    arc(cr, CX, 560, 200 + 260 * ph, 0.2, math.pi - 0.2, 10, (0.45, 0.75, 1.0), 0.7 * (1 - ph) * clamp(kf * 4))
            kc = prog(T, t_crew - 0.2, 0.5)
            if kc > 0:
                for i, (x, tool) in enumerate(((560, "mop"), (760, "bucket"), (1160, "bucket"), (1360, "mop"))):
                    janitor(cr, T, x, 940, 0.6, face=1 if x < CX else -1, ink=NI, fill=NF, tool=tool, seed=i,
                            a=clamp(kc * 2 - i * 0.3))
        km = K.pop(T, t_mice)
        if km > 0:
            with xform(cr, 330, 230, max(0.01, km)):
                rrect(cr, -250, -70, 500, 140, 18, fill=WHITE, stroke=INK, lw=5)
                mouse_lab(cr, -170, 20, 0.7)
                text(cr, "STUDIES IN MICE", 50, -18, 38, face=FONT_TITLE)
                text(cr, "suggest...", 30, 30, 36, face=FONT_HAND, bold=True, c=GRAY)
        if T > t_flush:
            chip(cr, "FLUSHING OUT WASTE", 1500, 230, 46, bg=(0.55, 0.80, 1.0), scale=K.pop(T, t_flush))
        if T > t_crew:
            chip(cr, "NIGHTTIME CLEANING CREW", CX, 1010, 50, bg=YELLOW, scale=K.pop(T, t_crew))
    b.fx(t_mice, "pop", -10)
    b.fx(t_flush, "pour", -10, dur=2.0)
    b.fx(t_crew, "bubbles", -12, dur=2.0)

    # 5. dreams seem to mix memories in new ways
    st5 = s("c3_05") - 0.15
    t_mix, t_new = w("c3_05", "mix"), w("c3_05", "unexpected")

    @b.shot(st5, "fade", 0.4)
    def mixing(cr, t, d, T):
        S.vgrad(cr, *DREAM)
        stars(cr, T, n=120, alpha=0.6)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.floor(cr, 930, (0.22, 0.14, 0.32), (0.4, 0.3, 0.5), 4)
            bed2(cr, T, 360, 950, 1.0, who="sleep", ink=NI, fill=NF, z=False, seed=1)
            kb = K.pop(T, st5 + 0.2)
            thought_bubble(cr, 1150, 560, 900, 500, 330, 760, scale=kb, t=T)
            if kb > 0.5:
                km = ease(prog(T, t_mix, 1.0))
                pairs = [("cat", "rocket", -250), ("pizza", "book", 250)]
                for j, (a_, b2, ox) in enumerate(pairs):
                    cx_ = 1150 + ox
                    sep = 150 * (1 - km)
                    rot = T * 1.5 + j
                    if km < 1:
                        for k_, kind in enumerate((a_, b2)):
                            ang = rot + k_ * math.pi
                            mem_card(cr, cx_ + math.cos(ang) * sep, 540 + math.sin(ang) * sep * 0.6, kind, 0.95, j * 2 + k_)
                    kn = K.pop(T, t_new + j * 0.25)
                    if km >= 1 and kn > 0:
                        with xform(cr, cx_, 530, 1.3 * max(0.01, kn), 0.1 * math.sin(T * 2)):
                            rrect(cr, -70, -70, 140, 140, 18, fill=(0.98, 0.90, 0.55), stroke=INK, lw=5)
                            if j == 0:
                                mem_icon(cr, "rocket", 1.1)
                                with xform(cr, 0, -48, 0.6):
                                    mem_icon(cr, "cat")
                            else:
                                mem_icon(cr, "book", 1.2)
                                with xform(cr, 18, -8, 0.55):
                                    mem_icon(cr, "pizza")
                        text(cr, ["SPACE CAT?!", "PIZZA BOOK?!"][j], cx_, 670, 38, face=FONT_TITLE, c=INK, a=clamp(kn))
                    if km >= 1 and kn <= 0:
                        burst(cr, cx_, 540, T - (t_mix + 1.0), n=14, dist=160, c=YELLOW, dur=0.6)
        text(cr, "DREAMS SEEM TO MIX MEMORIES", CX, 120, 52, face=FONT_TITLE, c=WHITE, a=eout(prog(T, t_mix - 0.3, 0.4)))
    b.fx(st5 + 0.2, "bubbles", -14)
    b.fx(t_mix, "whoosh", -12)
    b.fx(t_new, "boing", -10)

    # 6. repairs muscles, balances hormones, supports immunity
    st6 = s("c3_06") - 0.15
    b.add(st6, K.icons("MEANWHILE, YOUR BODY...", [(muscle_icon, "REPAIRS MUSCLES", w("c3_06", "repairs")),
                                                    (hormone_icon, "BALANCES HORMONES", w("c3_06", "balances")),
                                                    (shield_icon, "SUPPORTS IMMUNE SYSTEM", w("c3_06", "supports"))],
                       bg=(0.95, 0.96, 0.92), y=540, size=1.15, label_size=36), "slide", 0.4)
    for wd in ("repairs", "balances", "supports"):
        b.fx(w("c3_06", wd), "pop", -10)

    # 7. 1964: Randy Gardner, about eleven days awake
    st7 = s("c3_07") - 0.15
    t_randy, t_days = w("c3_07", "randy"), w("c3_07", "eleven days")
    t_conc, t_mood, t_hall = w("c3_07", "concentrating"), w("c3_07", "mood"), w("c3_07", "hallucinations")

    @b.shot(st7, "fade", 0.5)
    def randy(cr, t, d, T):
        fill_bg(cr, SEPIA)
        vignette(cr, 0.35, color=(0.3, 0.2, 0.1))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.floor(cr, 880, (0.80, 0.70, 0.52), BROWN, 5)
            kd = prog(T, t_randy + 0.8, t_days - t_randy - 0.6)
            day = 1 + int(10 * kd)
            window2(cr, 1500, 380, 380, 300, T, k_day=0.5 + 0.5 * math.sin(T * 8) if kd > 0 else 0.6, moon_on=True,
                    frame=BROWN)
            calendar_page(cr, 1050, 470, 0.9, top="DAYS AWAKE", big=str(day), top_c=(0.6, 0.25, 0.2), size=30)
            K.person(cr, T, 600, 900, "stand", face=1, acc=(), ink=BROWN, fill=(0.98, 0.94, 0.85), eye=1.3, smile=0.2,
                     blink=0.0)
            if T > t_randy:
                label_box(cr, "RANDY GARDNER (TEEN)", 600, 960, 40, c=BROWN, bg=(0.98, 0.94, 0.85),
                          scale=K.pop(T, t_randy))
        text(cr, "1964", 300, 230, 120, face=FONT_SERIF, bold=True, c=BROWN, a=eout(prog(t, 0.1, 0.5)))
        if kd > 0.95:
            chip(cr, "ABOUT 11 DAYS AWAKE", 1250, 820, 50, c=WHITE, bg=(0.6, 0.25, 0.2), scale=K.pop(T, t_days))
    for i in range(4):
        b.fx(t_randy + 0.8 + i * (t_days - t_randy - 0.6) / 4, "page", -13)
    b.fx(t_days, "pop", -10)

    @b.shot(w("c3_07", "trouble") - 0.6, "cut")
    def symptoms(cr, t, d, T):
        fill_bg(cr, SEPIA)
        vignette(cr, 0.35, color=(0.3, 0.2, 0.1))
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            S.floor(cr, 880, (0.80, 0.70, 0.52), BROWN, 5)
            mood = math.sin(T * 5) if T > t_mood else 0.0
            J = K.person(cr, T, 560, 900, "worried" if T < t_mood else "stand", face=1, acc=(), ink=BROWN,
                         fill=(0.98, 0.94, 0.85), eye=0.8, blink=0.45, smile=-0.3 + mood * 1.1, brow=-mood * 0.9,
                         lean=6 * math.sin(T * 2.2), head=10 * math.sin(T * 1.7))
            hx, hy = J["head"]
            if T > t_conc:
                for i in range(4):
                    a = T * 2 + i * TAU / 4
                    text(cr, "?", hx + math.cos(a) * 90, hy - 30 + math.sin(a) * 40, 50, face=FONT_TITLE,
                         c=(0.6, 0.25, 0.2), a=prog(T, t_conc, 0.4))
            if T > t_hall:
                kh = prog(T, t_hall, 0.6)
                for i in range(3):
                    pts = [(250 + i * 30 + 40 * math.sin(T * 3 + j * 0.5 + i), 300 + j * 18) for j in range(30)]
                    polyline(cr, pts, 6, [PURPLE, GREEN, ORANGE][i], 0.6 * kh)
                with xform(cr, 300, 520, kh, 0.2 * math.sin(T * 2)):
                    circle(cr, 0, 0, 50, fill=(0.85, 0.75, 0.95), stroke=BROWN, w=4, a=0.6)
                    circle(cr, -15, -8, 8, fill=BROWN, a=0.6)
                    circle(cr, 15, -8, 8, fill=BROWN, a=0.6)
        for i, (lab, ta) in enumerate((("TROUBLE CONCENTRATING", t_conc), ("MOOD SWINGS", t_mood),
                                       ("HALLUCINATIONS", t_hall))):
            k = K.pop(T, ta)
            if k > 0:
                chip(cr, lab, 1330, 360 + i * 150, 52, c=WHITE, bg=(0.6, 0.25, 0.2), scale=k)
        text(cr, "BY THE END...", 1330, 220, 56, face=FONT_TITLE, c=BROWN, a=eout(prog(t, 0.05, 0.3)))
    for ta in (t_conc, t_mood, t_hall):
        b.fx(ta, "alert", -14)
    b.fx(t_hall, "glitch", -14)

    # 8. please don't try that
    st8 = s("c3_08") - 0.15
    t_dont, t_dang = w("c3_08", "don't"), w("c3_08", "dangerous")

    @b.shot(st8, "cut")
    def warning(cr, t, d, T):
        fill_bg(cr, (1.0, 0.86, 0.30))
        for i in range(-2, 30):
            for (y0, y1) in ((0, 70), (H - 70, H)):
                polyline(cr, [(i * 120, y1), (i * 120 + 60, y0), (i * 120 + 120, y0), (i * 120 + 60, y1)], 0, INK,
                         closed=True, fill=INK)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            K.hero(cr, T, 420, 940, "point_up", face=1, smile=-0.2, brow=0.6, s=1.15)
            stamp(cr, "DON'T TRY THIS", 1180, 420, T - t_dont, 110, c=RED, rot=-0.06)
            if T > t_dang - 0.2:
                text(cr, "REAL SLEEP LOSS IS DANGEROUS", 1180, 700, 54, face=FONT_TITLE, c=INK,
                     a=eout(prog(T, t_dang - 0.2, 0.4)))
    b.fx(st8, "alert", -10)
    b.fx(t_dont, "stamp", -4)

    # 9. in our story: your body has been upgraded
    st9 = s("c3_09") - 0.15
    t_up, t_rep = w("c3_09", "upgraded"), w("c3_09", "repair")

    @b.shot(st9, "fade", 0.4)
    def upgrade(cr, t, d, T):
        S.blueprint(cr, bg=(0.10, 0.16, 0.30), grid=(0.35, 0.55, 0.85), a=0.35)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            ku = ease(prog(T, t_up - 0.6, 1.4))
            for k_ in (-1, 1):
                rrect(cr, CX + k_ * 230 - 30, 300, 60, 600, 20, fill=(0.25, 0.30, 0.40), stroke=CYAN, lw=4)
            glow(cr, CX, 600, 380, CYAN, 0.25 + 0.2 * ku)
            sy = 320 + (math.sin(T * 3) * 0.5 + 0.5) * 560
            line(cr, CX - 200, sy, CX + 200, sy, 6, CYAN, 0.8 * (1 - prog(T, t_rep - 0.3, 0.3)))
            J = nhero(cr, T, CX, 900, "cheer" if T > t_rep else "front", face=1, ink=(0.85, 0.95, 1.0), fill=NF,
                      smile=0.9, eye=1.15)
            if T > t_rep:
                for i in range(5):
                    a = T * 1.6 + i * TAU / 5
                    with xform(cr, CX + math.cos(a) * 170, 640 + math.sin(a) * 230, 0.5, a):
                        line(cr, 0, 0, 0, 70, 12, (0.75, 0.80, 0.9))
                        arc(cr, 0, -12, 22, math.pi * 0.25, math.pi * 1.75, 12, (0.75, 0.80, 0.9))
                    star_shape(cr, CX + math.cos(a + 0.6) * 220, 600 + math.sin(a + 0.6) * 260, 12, fill=YELLOW,
                               a=prog(T, t_rep, 0.4))
            del J
            rrect(cr, 1340, 420, 460, 70, 16, fill=(0.06, 0.08, 0.15), stroke=CYAN, lw=4)
            rrect(cr, 1350, 430, 440 * ku, 50, 12, fill=BONUS)
            text(cr, "BODY UPGRADE", 1570, 380, 40, face=FONT_TITLE, c=WHITE)
            text(cr, f"{int(100 * ku)}%", 1570, 455, 40, face=FONT_TITLE, c=WHITE)
            if T > t_rep:
                chip(cr, "REPAIRS WHILE AWAKE", 1570, 620, 44, bg=YELLOW, scale=K.pop(T, t_rep))
        label_dark(cr, "STORY MODE: FICTION", 330, 230, 40, c=YELLOW, bg=(0.06, 0.08, 0.15), scale=K.pop(T, st9 + 0.2))
    b.fx(st9 + 0.2, "servo", -12)
    b.fx(t_up - 0.6, "charge", -10, dur=1.4)
    b.fx(t_up + 0.8, "success", -10)
    b.fx(t_rep, "sparkle", -12)
    return b.result()
