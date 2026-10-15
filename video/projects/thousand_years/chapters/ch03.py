"""Thousand Years - Chapter 3: Time to Master Everything (1:40-2:40)."""
from video.projects.thousand_years.chapters._t import *  # noqa: F401,F403

TODO = ["LEARN PIANO", "CLIMB EVEREST", "WRITE A NOVEL", "LEARN JAPANESE", "BUILD A HOUSE", "SAIL THE WORLD",
        "PAINT", "LEARN TO JUGGLE", "STUDY STARS", "COOK EVERYTHING", "DANCE TANGO", "LEARN CHESS", "FLY A PLANE",
        "GROW A GARDEN", "LEARN PHYSICS", "MAKE A FILM"]


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 110, 0.7), ("c3_03", "discovery", "discovery_g", 100, 0.6),
                        ("c3_05", "playful", "playful_g", 108, 0.65), ("c3_07", "reflective", "reflective", 76, 0.55)])


def todo_scroll(cr, x, y0, y1, T, n_show, offset=0.0, checks=0, w=520):
    """A hand-written to-do list from y0 to y1 (items scroll up by `offset` rows)."""
    rect(cr, x - w / 2, y0, w, y1 - y0, fill=(0.98, 0.95, 0.85), stroke=INK, lw=5)
    cr.save()
    cr.rectangle(x - w / 2, y0 + 70, w, y1 - y0 - 70)
    cr.clip()
    for i in range(int(offset), int(offset) + 14):
        if i >= n_show:
            break
        yy = y0 + 110 + (i - offset) * 62
        lab = TODO[i % len(TODO)]
        rrect(cr, x - w / 2 + 30, yy - 18, 36, 36, 6, fill=WHITE, stroke=INK, lw=3)
        text(cr, lab, x - w / 2 + 84, yy, 34, face=FONT_HAND, bold=True, align="left")
        if i < checks:
            check(cr, x - w / 2 + 48, yy, 1.0, w=8)
    cr.restore()
    cr.new_path()
    rect(cr, x - w / 2, y0, w, 70, fill=(0.98, 0.95, 0.85), stroke=INK, lw=5)
    text(cr, "THINGS TO DO", x, y0 + 36, 40, face=FONT_TITLE, c=RED)
    ellipse(cr, x, y0, w / 2 + 20, 18, fill=(0.92, 0.85, 0.65), stroke=INK, w=5)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. what do you do with all that time? everything.
    t_ev = w("c3_01", "everything")

    @b.shot(0, "fade", 0.3)
    def everything(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, 1000, 560):
            S.room(cr, T, wall=(0.92, 0.94, 0.98), floor_c=(0.72, 0.66, 0.60), fy=900)
            n = 2 + int(14 * ease(prog(T, 0.3, t_ev - 0.3)))
            todo_scroll(cr, 1150, 200, 900, T, n)
            K.hero(cr, T, 640, 900, "cheer" if T > t_ev else "point", face=1, smile=0.9, eye=1.1)
            if T > t_ev:
                stamp(cr, "EVERYTHING!", 1150, 560, T - t_ev, 100, c=RED, rot=-0.1)
    b.fx(0.4, "scribble", -12, dur=2.0)
    b.fx(t_ev, "stamp", -6)

    # 2. doctor, pilot, chef, architect, musician
    st2 = s("c3_02") - 0.15
    jobs = [("doctor", "DOCTOR", "2ND CENTURY", (0.80, 0.94, 0.88)), ("pilot", "PILOT", "3RD CENTURY", (0.72, 0.86, 0.98)),
            ("chef", "CHEF", "4TH CENTURY", (1.0, 0.88, 0.70)), ("architect", "ARCHITECT", "THEN...", (0.86, 0.88, 0.95)),
            ("musician", "MUSICIAN", "THEN...", (0.90, 0.82, 0.98))]
    t_jobs = [w("c3_02", j[0]) - 0.2 for j in jobs]

    @b.shot(st2, "slide", 0.4)
    def careers(cr, t, d, T):
        i = -1
        for k, tt in enumerate(t_jobs):
            if T >= tt:
                i = k
        key, lab, cent, bg = jobs[max(0, i)]
        if i < 0:
            key, lab, bg = "none", "", (0.95, 0.93, 0.88)
        k_in = K.pop(T, t_jobs[max(0, i)])
        fill_bg(cr, bg)
        radial_lines(cr, CX, 560, T, n=24, c=WHITE, a=0.4, w=28)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.floor(cr, 880, lerpc(bg, (0.4, 0.4, 0.45), 0.35))
            acc = {"doctor": ("tuft", "labcoat"), "pilot": ("tie",), "chef": ("chef",), "none": ("tuft",),
                   "architect": ("hardhat",), "musician": ("tuft", "beret")}[key]
            g = {"doctor": "present", "pilot": "point", "chef": "hold", "architect": "hold", "musician": "hold",
                 "none": "think"}[key]
            if key == "pilot":
                jet(cr, lerp(1900, 1300, ease(prog(T, t_jobs[1], 1.0))), 360, 0.9, rot=-0.08)
            if key == "doctor":
                rect(cr, 1340, 300, 160, 160, fill=WHITE, stroke=INK, lw=5)
                rect(cr, 1395, 320, 50, 120, fill=RED)
                rect(cr, 1360, 355, 120, 50, fill=RED)
            if key == "architect":
                for j in range(3):
                    rect(cr, 1280, 880 - (j + 1) * 120, 260, 120, fill=(0.85, 0.80, 0.72), stroke=INK, lw=5)
                    rect(cr, 1320, 880 - (j + 1) * 120 + 30, 60, 60, fill=(0.8, 0.9, 1.0), stroke=INK, lw=3)
                    rect(cr, 1440, 880 - (j + 1) * 120 + 30, 60, 60, fill=(0.8, 0.9, 1.0), stroke=INK, lw=3)
                line(cr, 1600, 880, 1600, 260, 8, ORANGE)
                line(cr, 1400, 270, 1700, 270, 8, ORANGE)
            if key == "musician":
                for j in range(5):
                    f = (T * 0.5 + j * 0.2) % 1
                    note(cr, 1150 + j * 90 + 30 * math.sin(T + j), 560 - 300 * f, 1.1, PURPLE, 1 - f, double=j % 2 == 1)
            J = K.hero(cr, T, CX - 120, 880, g, face=1, s=1.1, acc=acc, smile=0.9)
            if key == "doctor":
                stethoscope(cr, J, 1.1)
            if key == "pilot":
                pilot_cap(cr, J, 1.1)
            if key == "chef":
                pan(cr, J["hand_f"][0] + 60, J["hand_f"][1] - 10, 1.0, 0.1 * math.sin(T * 6))
            if key == "architect":
                blueprint_roll(cr, J["hand_f"][0] + 80, J["hand_f"][1] - 40, 0.6, -0.2)
            if key == "musician":
                guitar(cr, J["hand_f"][0] - 20, J["hand_f"][1] - 10, 0.9, 0.9)
            if i >= 0:
                burst(cr, CX - 120, 700, T - t_jobs[i], n=16, dist=300, size=10, c=WHITE, dur=0.5, seed=i)
        text(cr, cent, CX, 140, 50, face=FONT_TITLE, c=INK, a=0.8)
        if lab:
            text(cr, lab, CX, 225, 92, face=FONT_TITLE, c=WHITE, outline=INK, ow=10, scale=max(0.01, k_in))
        for k in range(5):
            if T >= t_jobs[k]:
                x = 260 + k * 350
                kk = K.pop(T, t_jobs[k])
                label_box(cr, jobs[k][1], x, 1010, 36, c=INK, bg=WHITE if k != i else YELLOW, face=FONT_TITLE, bold=False,
                          scale=kk)
    for tt in t_jobs:
        b.fx(tt, "pop", -8)
    b.fx(t_jobs[1], "whoosh", -12)

    # 2b. fifty-year careers vs a whole working life
    st3 = s("c3_02b") - 0.15
    t_50, t_long = w("c3_02b", "fifty"), w("c3_02b", "longer")

    @b.shot(st3, "fade", 0.3)
    def fifty(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.15)
        with K.ken(cr, t, d, 1.0, 1.03):
            text(cr, "HOW LONG IS A CAREER?", CX, 150, 60, face=FONT_TITLE, a=eout(prog(t, 0.0, 0.3)))
            px = 24
            x0 = 300
            for i, (lab, yrs, tt, c, sub) in enumerate((("ONE OF YOUR CAREERS", 50, t_50, GREEN, "50 YEARS"),
                                                        ("MOST PEOPLE'S WHOLE WORKING LIFE", 40, t_long, MID, "~40 YEARS"))):
                y = 400 + i * 300
                text(cr, lab, x0, y - 70, 42, face=FONT_BOLD, align="left", a=eout(prog(T, tt - 0.3, 0.3)))
                k = ease(prog(T, tt, 1.0))
                if k > 0:
                    rrect(cr, x0, y - 40, px * yrs * k, 80, 16, fill=c, stroke=INK, lw=5)
                    for j in range(1, int(yrs * k / 10) + 1):
                        line(cr, x0 + j * 10 * px, y - 40, x0 + j * 10 * px, y + 40, 3, WHITE, 0.7)
                    text(cr, sub, x0 + px * yrs * k + 30, y, 54, face=FONT_TITLE, c=c if i == 0 else GRAY, align="left",
                         a=clamp(k * 2))
            K.hero(cr, T, 1760, 980, "confident" if T > t_long + 1.0 else "stand", face=-1, s=0.7, acc=("tuft", "labcoat"))
    b.fx(t_50, "rise", -12)
    b.fx(t_long, "rise", -14)

    # 3. the 10,000-hour idea
    st4 = s("c3_03") - 0.15
    t_idea, t_10k, t_var, t_doz = (w("c3_03", "popular idea"), w("c3_03", "ten thousand"), w("c3_03", "varies"),
                                   w("c3_03", "dozens"))

    @b.shot(st4, "fade", 0.3)
    def practice(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.room(cr, T, wall=(0.95, 0.90, 0.84), floor_c=(0.62, 0.46, 0.34), fy=900)
            P.clock(cr, 1500, 300, 120, T * 900, hours=3, speed=900)
            P.chair(cr, 560, 900, 1.0)
            p = sm.pose("sit", x=580, face=1, a1f=60, a2f=50, a1b=40, a2b=80, gy=0.4, smile=0.5)
            p["y"] = 742
            J = sm.draw(cr, sm.idle(p, T, 2), acc=HERO)
            guitar(cr, J["hand_f"][0] - 20, J["hand_f"][1] - 10, 0.9, 0.9 + 0.03 * math.sin(T * 12))
            for j in range(4):
                f = (T * 0.6 + j * 0.25) % 1
                note(cr, 760 + j * 60, 520 - 260 * f, 0.9, BLUE, 1 - f, double=j % 2 == 1)
            k = ease(prog(T, t_10k - 0.8, 1.6))
            n = int(10000 * k)
            if T > t_10k - 0.8:
                wob = 6 * math.sin(T * 30) * clamp(prog(T, t_var, 0.3)) * (1 - clamp(prog(T, t_var + 2.5, 0.4)))
                text(cr, f"{n:,} HOURS", 1250 + wob, 620, 110, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10)
            if T > t_var:
                stamp(cr, "IT VARIES A LOT", 1250, 790, T - t_var, 60, c=RED, rot=-0.05)
        if T > t_idea:
            label_box(cr, "A POPULAR IDEA:", 1250, 470, 46, c=INK, scale=K.pop(T, t_idea))
    b.fx(t_10k - 0.8, "tick", -12)
    b.fx(t_10k + 0.8, "ding", -10)
    b.fx(t_var, "stamp", -8)

    # 3b. dozens of skills
    @b.shot(t_doz - 0.25, "fade", 0.3)
    def dozens(cr, t, d, T):
        vgrad(cr, (0.98, 0.95, 0.85), (0.95, 0.85, 0.70))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            for i in range(24):
                r_, c_ = divmod(i, 8)
                x, y = 260 + c_ * 200, 330 + r_ * 180
                k = K.pop(T, t_doz - 0.2 + i * 0.05, 0.3)
                if k > 0:
                    with xform(cr, x, y, max(0.01, k) * 0.85):
                        circle(cr, 0, 0, 78, fill=WHITE, stroke=INK, w=5)
                        skill_icon(cr, i, T)
            K.hero(cr, T, CX, 1075, "cheer", s=0.75, smile=1.0)
        title_text(cr, "DOZENS OF SKILLS", 150, 74, c=WHITE, k=eout(prog(t, 0.0, 0.3)))
    for i in range(0, 24, 4):
        b.fx(t_doz - 0.2 + i * 0.05, "pop", -16)

    # 4. 7,000 languages; one every five years = 200
    st5 = s("c3_04") - 0.15
    t_7k, t_five, t_200 = w("c3_04", "seven thousand"), w("c3_04", "every five"), w("c3_04", "two hundred")
    hellos = ["HELLO", "HOLA", "BONJOUR", "CIAO", "HALLO", "OLA", "NAMASTE", "JAMBO", "MERHABA", "SALAM", "AHOJ",
              "KONNICHIWA", "NI HAO", "SAWUBONA"]

    @b.shot(st5, "fade", 0.3)
    def languages(cr, t, d, T):
        vgrad(cr, (0.82, 0.92, 1.0), (0.95, 0.97, 1.0))
        with K.ken(cr, t, d, 1.0, 1.03, CX, 560):
            P.globe(cr, 560, 600, 230, T * 0.8)
            for i, hw in enumerate(hellos):
                k = K.pop(T, st5 + 0.15 + i * 0.22, 0.3)
                if k <= 0:
                    continue
                a = i / len(hellos) * TAU + 0.3
                bx, by = 560 + math.cos(a) * 380, 600 + math.sin(a) * 330
                tw = text_w(cr, hw, FONT_BOLD, 30) + 30
                with xform(cr, bx, by + 6 * math.sin(T * 2 + i), max(0.01, k)):
                    rrect(cr, -tw / 2, -26, tw, 52, 16, fill=[WHITE, (1, 0.95, 0.8), (0.9, 1, 0.9)][i % 3], stroke=INK, lw=3)
                    text(cr, hw, 0, 0, 30, face=FONT_BOLD)
            k7 = K.pop(T, t_7k)
            if k7 > 0:
                text(cr, "~7,000", 1400, 300, 150, face=FONT_TITLE, c=BLUE, outline=INK, ow=10, scale=k7)
                text(cr, "LANGUAGES", 1400, 410, 60, face=FONT_TITLE, a=clamp(k7))
            kf = eout(prog(T, t_five, 0.4))
            if kf > 0:
                rrect(cr, 1110, 500, 580, 100, 20, fill=WHITE, stroke=INK, lw=5, a=kf)
                text(cr, "1 NEW LANGUAGE / 5 YEARS", 1400, 550, 40, face=FONT_BOLD, a=kf)
                text(cr, "1,000 YEARS ÷ 5", 1400, 680, 64, face=FONT_TITLE, a=eout(prog(T, t_five + 1.0, 0.4)))
            k2 = K.pop(T, t_200)
            if k2 > 0:
                text(cr, "= 200 LANGUAGES", 1400, 820, 84, face=FONT_TITLE, c=GREEN, outline=INK, ow=8, scale=k2)
    for i in range(0, len(hellos), 3):
        b.fx(st5 + 0.15 + i * 0.22, "blip", -16)
    b.fx(t_7k, "pop", -8)
    b.fx(t_200, "ding", -8)

    # 5. hero: bonjour, hola, ciao, and... I forgot
    st6 = s("c3_05") - 0.15
    t_bj, t_ho, t_ci, t_fg = w("c3_05", "bonjour"), w("c3_05", "hola"), w("c3_05", "ciao"), w("c3_05", "forgot")

    def stage(cr, T):
        S.room(cr, T, wall=(0.98, 0.92, 0.80), floor_c=(0.62, 0.46, 0.34), fy=900)
        for (tt, kind, x) in ((t_bj, "fr", 1080), (t_ho, "es", 1340), (t_ci, "it", 1600)):
            k = K.pop(T, tt)
            if k > 0:
                flag(cr, x, 700, 0.75 * max(0.01, k), kind, wave=math.sin(T * 3 + x))

    dlg = K.dialogue(tl, stage, [dict(x=700, gy=900, acc=HERO, face=1, g="stand", talk_g="present", s=1.1,
                                      kw=dict(smile=0.8))],
                     [(0, "Bonjour, hola, ciao, and... I forgot what I was saying.", "c3_05", (1250, 330))],
                     zoom=(1.0, 1.05), focus=(CX, 600))

    @b.shot(st6, "fade", 0.3)
    def forgot(cr, t, d, T):
        dlg(cr, t, d, T)
        kq = prog(T, t_fg, 0.4)
        if kq > 0:
            for i in range(5):
                a = T * 2.5 + i * TAU / 5
                text(cr, "?", 700 + math.cos(a) * 120, 470 + math.sin(a) * 36, 64, face=FONT_TITLE, c=RED, a=kq)
    b.fx(t_bj, "pop", -12)
    b.fx(t_ho, "pop", -12)
    b.fx(t_ci, "pop", -12)
    b.fx(t_fg + 0.3, "boing", -10)

    # 6. read every great book, then again
    st7 = s("c3_06") - 0.15
    t_again = w("c3_06", "again")

    @b.shot(st7, "fade", 0.3)
    def library(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.room(cr, T, wall=(0.55, 0.38, 0.28), floor_c=(0.40, 0.26, 0.18), fy=900)
            for x in range(-40, 2000, 260):
                P.bookshelf(cr, x, 900, 1.9, highlight=1.0)
            src(cr, (0.0, 0.0, 0.0), 0.25)
            cr.paint()
            glow(cr, CX, 600, 500, YELLOW, 0.3)
            k = ease(prog(T, st7 + 0.2, t_again - st7 - 0.2))
            for side in (-1, 1):
                n = int(14 * k)
                for i in range(n):
                    P.book(cr, CX + side * 330 + (i % 2) * 8, 880 - i * 24, 0.45, c=[BLUE, RED, GREEN, ORANGE, PURPLE][i % 5],
                           rot=math.pi / 2)
            P.chair(cr, CX - 40, 900, 1.0)
            p = sm.pose("sit", x=CX - 20, face=1, a1f=60, a2f=60, a1b=50, a2b=70, gy=0.5, smile=0.7)
            p["y"] = 742
            J = sm.draw(cr, sm.idle(p, T, 4), acc=HERO)
            P.book(cr, J["hand_f"][0] + 20, J["hand_f"][1] - 20, 0.6, open_=1.0)
        title_text(cr, "EVERY GREAT BOOK", 150, 70, c=WHITE)
        if T > t_again:
            ka = K.pop(T, t_again)
            with xform(cr, 1520, 450, max(0.01, ka), T * 2):
                arc(cr, 0, 0, 90, 0.3, TAU - 0.4, 16, YELLOW)
                polyline(cr, [(80, -60), (110, 10), (40, 0)], 0, INK, closed=True, fill=YELLOW)
            text(cr, "AGAIN!", 1520, 450, 50, face=FONT_TITLE, c=WHITE, outline=INK, ow=6, scale=max(0.01, ka))
    b.fx(st7 + 0.3, "page", -10)
    b.fx(t_again, "swoosh", -8)

    # 7. you still can't do everything
    st8 = s("c3_07") - 0.15
    t_cant = w("c3_07", "still can't")

    @b.shot(st8, "fade", 0.3)
    def endless(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, 1000, 560):
            S.room(cr, T, wall=(0.92, 0.94, 0.98), floor_c=(0.72, 0.66, 0.60), fy=900)
            off = (T - st8) * 1.6
            todo_scroll(cr, 1150, 180, 1100, T, 99, offset=off, checks=int(off) + 5)
            K.hero(cr, T, 600, 900, "slump" if T > t_cant else "worried", face=1, s=1.0)
            g = rng(2)
            for i in range(6):
                f = (T * 0.8 + g.random()) % 1
                ellipse(cr, 600 + g.uniform(-60, 60), 560 + 120 * f, 6, 10, fill=(0.5, 0.75, 1.0), a=1 - f)
        if T > t_cant:
            stamp(cr, "YOU STILL CAN'T DO EVERYTHING", CX, 330, T - t_cant, 64, c=RED, rot=-0.05)
    b.fx(st8, "scribble", -14, dur=3.0)
    b.fx(t_cant, "stamp", -6)

    # 8. more to learn than time to learn it
    st9 = s("c3_08") - 0.15

    @b.shot(st9, "fade", 0.4)
    def horizon(cr, t, d, T):
        vgrad(cr, (0.98, 0.80, 0.55), (0.70, 0.75, 0.95))
        with K.ken(cr, t, d, 1.0, 1.08, CX, 640):
            S.floor(cr, 600, (0.62, 0.50, 0.40))
            for row in range(9, 0, -1):
                sc = 1.0 / (1 + row * 0.55)
                y = 600 + 520 * sc
                for side in (-1, 1):
                    for k in range(3):
                        x = CX + side * (260 + k * 260) * sc * 2.2
                        P.bookshelf(cr, x, y, 2.2 * sc, highlight=0.8)
            K.hero(cr, T, CX, 1000, "shrug", face=1, s=0.8, smile=0.6, fo=0.3)
            P2.hourglass(cr, CX + 200, 930, 0.4, p=prog(T, st9, d), t=T)
        title_text(cr, "MORE TO LEARN", 160, 76, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
        title_text(cr, "THAN TIME TO LEARN IT", 260, 60, c=YELLOW, k=eout(prog(T, w("c3_08", "than time"), 0.4)))
    b.fx(st9 + 0.2, "chime", -12)
    return b.result()
