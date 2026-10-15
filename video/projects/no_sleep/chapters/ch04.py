"""No Sleep - Chapter 4: The Productivity Machine (2:40-3:40)."""
from video.projects.no_sleep.chapters._n import *  # noqa: F401,F403

CHALK = (0.95, 0.95, 0.90)


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 104, 0.6), ("c4_03", "uplift", "uplift", 104, 0.7),
                        ("c4_06", "playful", "playful_g", 108, 0.65), ("c4_08", "mystery", "mystery", 72, 0.5),
                        ("c4_09", "cold", "cold", 68, 0.5), ("c4_10", "mystery", "mystery", 70, 0.55)])


def classroom(cr, T):
    S.room(cr, T, wall=(0.93, 0.90, 0.82), floor_c=(0.70, 0.58, 0.45), fy=900)
    P.chalkboard(cr, 1080, 450, 1360, 560)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. let's do the math
    t_math = w("c4_01", "math")

    @b.shot(0, "fade", 0.3)
    def math_intro(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            classroom(cr, T)
            k = prog(T, 0.6, 1.2)
            J = K.hero(cr, T, 260, 920, "write" if k < 1 else "point", face=1, smile=0.6, a1f=120 + 10 * math.sin(T * 9))
            typewriter(cr, "LET'S DO THE MATH", 560, 330, k, 92, face=FONT_HAND, bold=True, c=CHALK, cursor=False)
            if k >= 1:
                text(cr, "8 h × ?", 1080, 520, 70, face=FONT_HAND, bold=True, c=CHALK, a=prog(T, t_math + 0.2, 0.4))
            del J
    b.fx(0.6, "chalk", -8, dur=1.2)

    # 2. 8 hours a night, age 20 to 80 -> around 20 years asleep
    st2 = s("c4_02") - 0.15
    t_8, t_ages, t_20 = w("c4_02", "eight hours"), w("c4_02", "twenty to eighty"), w("c4_02", "twenty years")
    lines = [("8 HOURS A NIGHT = 1/3 OF A DAY", t_8), ("AGE 20 TO 80 = 60 YEARS", t_ages),
             ("60 × 1/3 ≈ 20 YEARS ASLEEP", t_20)]

    @b.shot(st2, "cut")
    def board(cr, t, d, T):
        fill_bg(cr, (0.55, 0.38, 0.22))
        rect(cr, 30, 30, W - 60, H - 60, fill=(0.16, 0.24, 0.21))
        with K.ken(cr, t, d, 1.0, 1.03, CX, 540):
            text(cr, "SLEEP MATH", 1560, 120, 50, face=FONT_HAND, bold=True, c=(0.7, 0.85, 0.75), a=eout(prog(t, 0.0, 0.3)))
            line(cr, 1420, 150, 1700, 150, 4, (0.7, 0.85, 0.75), eout(prog(t, 0.2, 0.3)))
            for i, (ln, ta) in enumerate(lines):
                k = prog(T, min(ta - 0.1, st2 + 0.15) if i == 0 else ta - 0.1, 0.9)
                typewriter(cr, ln, 180, 240 + i * 150, k, 76, face=FONT_HAND, bold=True, c=YELLOW if i == 2 else CHALK,
                           cursor=False)
            k20 = prog(T, t_20 + 0.8, 0.5)
            if k20 > 0:
                tw = text_w(cr, lines[2][0], FONT_HAND, 76, True)
                ellipse(cr, 180 + tw * 0.83, 540, 320, 70, stroke=YELLOW, w=6, a=k20)
            kb = prog(T, t_ages + 0.3, 1.0)
            if kb > 0:
                x0, x1, y = 200, 1720, 850
                partial_line(cr, x0, y, x1, y, ease(kb), 8, CHALK)
                for i in range(7):
                    xx = x0 + (x1 - x0) * i / 6
                    if kb * 7 > i:
                        line(cr, xx, y - 20, xx, y + 20, 6, CHALK)
                        text(cr, str(20 + i * 10), xx, y + 55, 36, face=FONT_HAND, bold=True, c=CHALK)
                ks = ease(prog(T, t_20, 1.2))
                if ks > 0:
                    rect(cr, x0, y - 70, (x1 - x0) / 3 * ks, 50, fill=SLEEP_BLUE, stroke=CHALK, lw=3)
                    rect(cr, x0 + (x1 - x0) / 3 * ks, y - 70, (x1 - x0) * (1 - ks / 3), 50, fill=(0.85, 0.75, 0.35),
                         stroke=CHALK, lw=3)
                    text(cr, "ASLEEP", x0 + (x1 - x0) / 6 * ks, y - 45, 30, face=FONT_TITLE, c=WHITE, a=ks)
                    text(cr, "AWAKE", x0 + (x1 - x0) * (1 / 3 + 1 / 3) * 1.0, y - 45, 30, face=FONT_TITLE, c=INK, a=ks)
                    text(cr, "(all the nights added together)", 960, 960, 34, face=FONT_HAND, bold=True, c=CHALK, a=ks)
    for ta in (t_8, t_ages, t_20):
        b.fx(ta, "chalk", -10, dur=0.8)

    # 3. twenty extra years awake: a second adulthood for free
    st3 = s("c4_03") - 0.15
    t_sec, t_free = w("c4_03", "second adulthood"), w("c4_03", "free")

    @b.shot(st3, "fade", 0.3)
    def bonus_life(cr, t, d, T):
        fill_bg(cr, (1.0, 0.88, 0.40))
        radial_lines(cr, CX, 600, T, n=30, c=WHITE, a=0.35, w=30, spin=0.05)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.floor(cr, 920, (0.95, 0.75, 0.30))
            k = K.pop(T, st3 + 0.15)
            text(cr, "+20 YEARS AWAKE", CX, 230, 110, face=FONT_TITLE, c=WHITE, outline=INK, ow=10, scale=max(0.01, k))
            K.hero(cr, T, 720, 940, "present" if T > t_sec else "confident", face=1, s=1.15, smile=0.9)
            kc = K.pop(T, t_sec)
            if kc > 0:
                glow(cr, 1180, 700, 260, WHITE, 0.6 * clamp(kc))
                with xform(cr, 1180, 940, max(0.01, kc)):
                    K.hero(cr, T, 0, 0, "cheer", face=-1, s=1.15, smile=1.0, seed=4, alpha=0.95)
                text(cr, "ADULTHOOD #2", 1180, 1000, 48, face=FONT_TITLE, c=INK, a=clamp(kc))
            kf = K.pop(T, t_free)
            if kf > 0:
                with xform(cr, 1480, 470, max(0.01, kf), 0.25 + 0.08 * math.sin(T * 4)):
                    polyline(cr, [(-120, -60), (90, -60), (140, 0), (90, 60), (-120, 60)], 6, INK, closed=True, fill=RED)
                    circle(cr, 85, 0, 12, fill=WHITE, stroke=INK, w=4)
                    text(cr, "FREE!", -20, 0, 64, face=FONT_TITLE, c=WHITE)
    b.fx(st3 + 0.15, "pop", -8)
    b.fx(t_sec, "sparkle", -10)
    b.fx(t_free, "coins", -10)

    # 4. three languages, two instruments, that stack of books
    st4 = s("c4_04") - 0.15
    t_lang, t_inst, t_books, t_pre = (w("c4_04", "three languages"), w("c4_04", "two instruments"),
                                      w("c4_04", "stack of books"), w("c4_04", "pretending"))

    @b.shot(st4, "slide", 0.4)
    def hobbies(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.03, CX, 600):
            S.room(cr, T, wall=(0.90, 0.93, 0.96), floor_c=(0.75, 0.68, 0.58), fy=900)
            K.hero(cr, T, 420, 920, "present" if T < t_inst else "point", face=1, smile=0.8,
                   gx=1.0 if T > t_books else 0.0)
            for i, (wd, x, y) in enumerate((("HOLA!", 250, 400), ("BONJOUR!", 470, 300), ("CIAO!", 680, 420))):
                k = K.pop(T, t_lang + i * 0.2)
                if k > 0:
                    speech_bubble(cr, x, y, 220, 90, 420, 560, scale=k, fill=[(1.0, 0.92, 0.8), (0.85, 0.92, 1.0),
                                                                             (0.88, 1.0, 0.88)][i])
                    text(cr, wd, x, y, 40, face=FONT_HAND, bold=True, a=clamp(k))
            ki = K.pop(T, t_inst)
            if ki > 0:
                guitar(cr, 900, 660, 0.9 * max(0.01, ki), rot=0.25)
                trumpet(cr, 1100, 560, 1.0 * max(0.01, K.pop(T, t_inst + 0.25)), rot=-0.3)
                for j in range(3):
                    ph = (T * 0.7 + j / 3) % 1
                    text(cr, "♪", 1000 + ph * 60, 450 - ph * 120, 50, face=FONT_BOLD, c=BLUE, a=(1 - ph) * clamp(ki))
            kb = prog(T, t_books - 0.3, 0.6)
            if kb > 0:
                book_stack(cr, 1500, 900, 1.1, n=int(3 + 11 * ease(kb)), T=T, dust=prog(T, t_pre, 0.4))
                if T > t_pre:
                    for j in range(3):
                        a = T + j * 2
                        circle(cr, 1500 + 160 * math.cos(a), 330 + 40 * math.sin(a * 1.3), 4, fill=MID)
                    label_box(cr, "STARTING... SOMEDAY", 1500, 230, 40, c=INK, bg=WHITE, scale=K.pop(T, t_pre))
            for (lab, x, ta) in (("3 LANGUAGES", 460, t_lang), ("2 INSTRUMENTS", 1000, t_inst)):
                k = K.pop(T, ta)
                if k > 0:
                    chip(cr, lab, x, 170, 46, bg=YELLOW, scale=k)
    for i in range(3):
        b.fx(t_lang + i * 0.2, "pop", -12)
    b.fx(t_inst, "ding", -12)
    b.fx(t_books, "thud", -10)

    # 5. a business at night, medicine, a midnight marathon
    st5 = s("c4_05") - 0.15
    t_bus, t_med, t_mar = w("c4_05", "business"), w("c4_05", "medicine"), w("c4_05", "marathon")

    def p_business(cr, T):
        vgrad(cr, (0.10, 0.12, 0.25), (0.20, 0.18, 0.35), 0, 0, 520, 600)
        stars(cr, T, n=30, area=(0, 0, 520, 250))
        building(cr, 260, 520, 360, 330, c=(0.35, 0.30, 0.45), sign="OPEN 24/7", sign_c=(1.0, 0.45, 0.6), lit=1.0,
                 T=T, win_rows=1, seed=2, sign_size=36)
        P.monitor(cr, 260, 345, 150, 90, screen=lambda c, x, y, w_, h_: (fill_bg(c, (0.2, 0.5, 0.9)),
                                                                           text(c, "$", x + w_ / 2, y + h_ / 2, 50,
                                                                                face=FONT_TITLE, c=WHITE)))
        rect(cr, -10, 520, 540, 100, fill=(0.12, 0.12, 0.16))

    def p_medicine(cr, T):
        fill_bg(cr, (0.88, 0.94, 0.96))
        rect(cr, 0, 470, 520, 130, fill=(0.75, 0.80, 0.85))
        P.desk(cr, 300, 500, 300)
        for i in range(4):
            rrect(cr, 210 + i * 10, 300 - i * 28, 170, 26, 5, fill=[RED, BLUE, GREEN, ORANGE][i], stroke=INK, lw=3)
        text(cr, "ANATOMY", 300, 260, 22, face=FONT_TITLE)
        p = sm.pose("write", x=130, face=1, s=0.75, smile=0.4)
        sm.draw(cr, sm.on_ground(sm.idle(p, T, 2), 520), acc=SCI)

    def p_marathon(cr, T):
        vgrad(cr, (0.06, 0.07, 0.16), (0.16, 0.14, 0.30), 0, 0, 520, 600)
        stars(cr, T, n=40, area=(0, 0, 520, 300))
        moon(cr, 400, 120, 45)
        rect(cr, 0, 470, 520, 130, fill=(0.22, 0.22, 0.28))
        for i in range(-1, 5):
            rect(cr, (i * 140 - T * 300) % 700 - 100, 530, 70, 8, fill=WHITE, a=0.7)
        p = sm.run(sm.pose("stand", x=260, face=1, s=0.8, smile=0.7), T, 1.0)
        sm.draw(cr, sm.on_ground(p, 500), ink=NI, fill=NF, acc=("tuft",))
        text(cr, "12:00 AM", 120, 80, 34, face=FONT_TITLE, c=WHITE)

    b.add(st5, K.three_paths([("NIGHT BUSINESS", (0.55, 0.35, 0.75), p_business, t_bus),
                              ("STUDY MEDICINE", (0.20, 0.55, 0.70), p_medicine, t_med),
                              ("MARATHON", (0.85, 0.45, 0.20), p_marathon, t_mar)],
                             title="SOME PEOPLE WOULD..."), "fade", 0.3)
    for ta in (t_bus, t_med, t_mar):
        b.fx(ta, "pop", -10)

    # 6. "I'm going to be so productive."
    st6 = s("c4_06") - 0.15

    def office_night(cr, T):
        S.room(cr, T, wall=(0.88, 0.90, 0.95), floor_c=(0.70, 0.65, 0.60), fy=900)
        window2(cr, 420, 360, 360, 300, T)
        todo_list(cr, 1500, 480, ["LANGUAGES", "GUITAR", "BUSINESS", "MARATHON"], k_items=1.0, k_checks=0.0,
                  title="THE PLAN", w=440, size=40)
        P.desk(cr, 560, 900, 360)
        P.coffee(cr, 640, 750, 0.6, T)

    b.add(st6, K.dialogue(tl, office_night, [dict(x=900, gy=900, acc=HERO, face=1, g="confident", talk_g="cheer",
                                                  kw=dict(smile=1.0, eye=1.15))],
                          [(0, "I'm going to be so productive.", "c4_06", (930, 300))], zoom=(1.0, 1.06),
                          focus=(CX, 560)), "fade", 0.3)
    b.fx(st6 + 0.1, "pop", -12)

    # 7. and for a while, you are
    st7 = s("c4_07") - 0.15
    t_todo, t_gr, t_pl = w("c4_07", "to-do"), w("c4_07", "grades"), w("c4_07", "houseplants")

    @b.shot(st7, "fade", 0.3)
    def thriving(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.03, CX, 600):
            S.room(cr, T, wall=(0.95, 0.96, 0.90), floor_c=(0.72, 0.62, 0.50), fy=900)
            text(cr, "AND FOR A WHILE... YOU ARE!", CX, 200, 60, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
            kd = prog(T, t_todo, 1.2)
            kfly = ease(prog(T, t_todo + 1.3, 0.6))
            if kfly < 1:
                todo_list(cr, 420, 560 - 500 * kfly, ["LANGUAGES", "GUITAR", "BUSINESS", "MARATHON"], k_checks=kd,
                          title="THE PLAN", w=420, size=38, rot=kfly * 0.6)
            else:
                chip(cr, "TO-DO: DONE!", 420, 560, 50, bg=GREEN, c=WHITE, scale=K.pop(T, t_todo + 1.9))
            kg = K.pop(T, t_gr)
            if kg > 0:
                with xform(cr, 960, 560, max(0.01, kg)):
                    rrect(cr, -170, -210, 340, 420, 14, fill=WHITE, stroke=INK, lw=5)
                    text(cr, "REPORT CARD", 0, -165, 32, face=FONT_TITLE)
                    for i, subj in enumerate(("MATH", "ART", "SCIENCE")):
                        text(cr, subj, -130, -80 + i * 90, 34, face=FONT_HAND, bold=True, align="left")
                        g = "A+" if T > t_gr + 0.4 + i * 0.25 else "C"
                        text(cr, g, 110, -80 + i * 90, 46, face=FONT_TITLE, c=RED if g == "A+" else GRAY)
                arrow(cr, 1180, 720, 1180, 720 - 280 * ease(prog(T, t_gr + 0.3, 0.8)), 14, GREEN, head=40)
            kp = prog(T, t_pl - 0.2, 0.3)
            if kp > 0:
                hl = ease(prog(T, t_pl, 1.2))
                houseplant(cr, 1460, 900, 1.25, T, health=0.3 + 0.7 * hl, sparkle=hl, seed=1)
                houseplant(cr, 1700, 900, 1.0, T, health=0.3 + 0.7 * hl, sparkle=hl, seed=3)
                chip(cr, "NEVER LOOKED BETTER", 1580, 360, 40, bg=WHITE, scale=K.pop(T, t_pl + 0.6))
    for i in range(4):
        b.fx(t_todo + i * 0.3, "check", -14)
    b.fx(t_todo + 1.3, "whoosh", -12)
    b.fx(t_gr + 0.4, "ding", -12)
    b.fx(t_pl + 0.3, "sparkle", -12)

    # 8. the extra time starts filling up with more work
    st8 = s("c4_08") - 0.15
    t_fill, t_work = w("c4_08", "filling up"), w("c4_08", "more work")
    blocks = ["EMAIL", "MEETING", "REPORT", "TASK", "EMAIL", "CALL", "MEETING", "SLIDES", "TASK", "EMAIL", "REVIEW",
              "TASK"]

    @b.shot(st8, "fade", 0.4)
    def jar(cr, t, d, T):
        fill_bg(cr, (0.80, 0.82, 0.86))
        vignette(cr, 0.3)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            S.floor(cr, 920, (0.62, 0.64, 0.70))
            text(cr, "SOMETHING STRANGE...", CX, 190, 60, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
            x0, x1, y0, y1 = 760, 1160, 380, 900
            kf = prog(T, t_fill - 0.3, (t_work - t_fill) + 1.2)
            n = int(len(blocks) * kf)
            for i in range(len(blocks)):
                row, col = divmod(i, 2)
                tx, ty = x0 + 105 + col * 190, y1 - 45 - row * 82
                land = clamp(kf * len(blocks) - i)
                if land <= 0:
                    continue
                yy = lerp(-120, ty, ein(clamp(land * 1.6)))
                rrect(cr, tx - 85, yy - 36, 170, 72, 10, fill=[(0.95, 0.55, 0.45), (0.55, 0.70, 0.95),
                                                               (0.95, 0.85, 0.45)][i % 3], stroke=INK, lw=4)
                text(cr, blocks[i], tx, yy, 30, face=FONT_TITLE)
            del n
            polyline(cr, [(x0, y0), (x0, y1), (x1, y1), (x1, y0)], 8, INK)
            rect(cr, x0 - 20, y0 - 30, x1 - x0 + 40, 30, fill=(0.85, 0.88, 0.92), stroke=INK, lw=5)
            label_box(cr, "YOUR 8 EXTRA HOURS", CX, 970, 40, c=INK, bg=WHITE)
            K.hero(cr, T, 450, 920, "worried" if T > t_fill else "stand", face=1, s=1.0, gx=0.8)
            if T > t_work:
                chip(cr, "MORE WORK", 1500, 450, 60, c=WHITE, bg=RED, scale=K.pop(T, t_work))
    b.fx(st8, "darkwhoosh", -12)
    for i in range(6):
        b.fx(t_fill - 0.3 + i * 0.5, "thud", -16)

    # 9. Parkinson, 1955
    st9 = s("c4_09") - 0.15
    t_hist, t_quote, t_law = w("c4_09", "historian"), w("c4_09", "work expands"), w("c4_09", "parkinson's law")

    @b.shot(st9, "fade", 0.4)
    def parkinson(cr, t, d, T):
        fill_bg(cr, (0.93, 0.89, 0.80))
        vignette(cr, 0.3, color=(0.3, 0.2, 0.1))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            text(cr, "1955", 560, 260, 150, face=FONT_SERIF, bold=True, c=(0.35, 0.25, 0.15), a=eout(prog(t, 0.1, 0.5)))
            with xform(cr, 1250, 520, 1.0, 0.03):
                rect(cr, -230, -280, 460, 560, fill=(0.62, 0.45, 0.28), stroke=INK, lw=6)
                rect(cr, -195, -245, 390, 490, fill=(0.96, 0.92, 0.82), stroke=INK, lw=4)
                p = sm.pose("front", s=2.1, smile=0.3, brow=0.2)
                cr.save()
                cr.rectangle(-195, -245, 390, 490)
                cr.clip()
                sm.draw(cr, head_at(sm.idle(p, T, 1, 0.4), 0, -40), acc=("glasses", "mustache", "tie"))
                cr.restore()
                cr.new_path()
            if T > t_hist - 0.2:
                text(cr, "C. NORTHCOTE PARKINSON", 1250, 870, 44, face=FONT_TITLE, c=INK, a=eout(prog(T, t_hist - 0.2, 0.4)))
                chip(cr, "HISTORIAN", 560, 450, 50, bg=WHITE, scale=K.pop(T, t_hist))
            K.person(cr, T, 560, 900, "write", face=1, acc=("glasses", "mustache"), s=0.9, smile=0.3)
            P.desk(cr, 680, 900, 260)
    b.fx(st9 + 0.2, "page", -12)
    b.fx(t_hist, "pop", -12)

    @b.shot(t_quote - 0.25, "fade", 0.4)
    def law(cr, t, d, T):
        vgrad(cr, (0.08, 0.08, 0.13), (0.03, 0.03, 0.06))
        with K.ken(cr, t, d, 1.0, 1.03, CX, 540):
            ql = ["“WORK EXPANDS TO FILL", "THE TIME AVAILABLE", "FOR ITS COMPLETION.”"]
            for i, ln in enumerate(ql):
                k = eout(prog(T, t_quote + i * 0.7, 0.5))
                text(cr, ln, CX, 210 + i * 95 + (1 - k) * 25, 74, face=FONT_TITLE, c=WHITE, a=k)
            text(cr, "— C. Northcote Parkinson, 1955", CX, 500, 40, face=FONT_HAND, bold=True, c=YELLOW,
                 a=eout(prog(T, t_quote + 2.2, 0.5)))
            bx, by, bw, bh = CX - 340, 600, 680, 330
            cr.push_group()
            rect(cr, bx, by, bw, bh, stroke=WHITE, lw=6)
            text(cr, "TIME AVAILABLE", CX, by + bh + 40, 34, face=FONT_TITLE, c=(0.7, 0.7, 0.8))
            kx = ease(prog(T, t_quote + 0.5, 4.0))
            ww, hh = lerp(140, bw - 16, kx), lerp(100, bh - 16, kx)
            wob = 8 * math.sin(T * 5) * (1 - kx)
            rrect(cr, CX - ww / 2, by + bh - 8 - hh, ww, hh, 30 * (1 - kx) + 8, fill=(0.95, 0.45, 0.35), stroke=INK, lw=5)
            text(cr, "WORK", CX, by + bh - 8 - hh / 2 + wob, 60 + 30 * kx, face=FONT_TITLE, c=WHITE)
            cr.pop_group_to_source()
            cr.paint_with_alpha(1 - 0.75 * prog(T, t_law, 0.3))
        if T > t_law:
            stamp(cr, "PARKINSON'S LAW", CX, 760, T - t_law, 90, c=YELLOW, rot=-0.06)
        vignette(cr, 0.4)
    b.fx(t_quote, "chime", -12)
    b.fx(t_quote + 0.5, "strain", -14, dur=3.0)
    b.fx(t_law, "stamp", -6)

    # 10. you're about to learn what he meant
    st10 = s("c4_10") - 0.15

    @b.shot(st10, "fade", 0.3)
    def buried(cr, t, d, T):
        with K.ken(cr, t, d, 1.05, 1.15, CX, 600):
            S.room(cr, T, wall=(0.86, 0.86, 0.90), floor_c=(0.62, 0.60, 0.62), fy=900)
            P.desk(cr, 960, 900, 600)
            K.hero(cr, T, 960, 900, "worried", face=1, fo=0.0, smile=-0.5, eye=1.25, mo=0.2)
            g = rng(5)
            for i in range(70):
                px = 960 + g.uniform(-420, 420)
                top = 900 - 275 + abs(px - 960) * 0.5
                py = g.uniform(top, 900)
                with xform(cr, px, py, 1.0, g.uniform(-0.6, 0.6)):
                    rect(cr, -55, -38, 110, 76, fill=(0.98, 0.98, 0.96), stroke=INK, lw=3)
                    line(cr, -35, -10, 35, -10, 3, MID)
                    line(cr, -35, 10, 25, 10, 3, MID)
            for i in range(4):
                f = (T * 0.9 + i * 0.25) % 1
                with xform(cr, 600 + i * 240, lerp(-60, 520, f), 1.0, f * 4 + i):
                    rect(cr, -55, -38, 110, 76, fill=WHITE, stroke=INK, lw=3)
            text(cr, "gulp.", 1220, 470, 54, face=FONT_HAND, bold=True, c=INK, a=prog(T, st10 + 0.8, 0.3))
    b.fx(st10, "papers", -10)
    b.fx(st10 + 0.8, "gulp", -8)
    return b.result()
