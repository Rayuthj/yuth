"""Thousand Years - Chapter 1: The Hook (0:00-0:40)."""
from video.projects.thousand_years.chapters._t import *  # noqa: F401,F403

DARK_TAG = True


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 72, 0.5), ("c1_02", "wonder", "wonder", 90, 0.6),
                        ("c1_05", "uplift", "uplift", 104, 0.7), ("c1_06", "mystery", "mystery", 70, 0.55),
                        (tl.e("c1_07") + 0.2, "uplift", "mystery", 96, 0.9)])


def flex_pose(x, s=1.0, **kw):
    return sm.pose("front", x=x, s=s, a1f=90, a2f=80, a1b=-90, a2b=-80, smile=0.9, brow=0.4, **kw)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. imagine a thousand years: the counter runs up while the hero stays the same
    t_th = w("c1_01", "thousand")

    @b.shot(0, "fade", 0.4)
    def counter(cr, t, d, T):
        vgrad(cr, (0.08, 0.09, 0.18), (0.02, 0.02, 0.05))
        stars(cr, T, n=160, alpha=0.5)
        with K.ken(cr, t, d, 1.08, 1.0, CX, 600):
            glow(cr, CX, 520, 520, (0.5, 0.6, 1.0), 0.18 + 0.1 * clamp(prog(T, t_th, 0.6)))
            k = ease(prog(T, t_th - 0.7, 1.4))
            P2.hourglass(cr, CX, 380, 1.1, p=0.15 + 0.7 * k, t=T)
            for i in range(10):
                a = T * 0.35 + i * TAU / 10
                r_ = 520
                x, y = CX + math.cos(a) * r_, 470 + math.sin(a) * 250
                depth = 0.55 + 0.45 * math.sin(a)
                with xform(cr, x, y, 0.55 + 0.25 * depth, 0.15 * math.sin(a * 2)):
                    rect(cr, -60, -46, 120, 92, fill=WHITE, stroke=INK, lw=4, a=0.25 + 0.55 * depth)
                    rect(cr, -60, -46, 120, 26, fill=RED, a=0.25 + 0.55 * depth)
                    text(cr, f"{(i * 100 + int(k * 1000)) % 1000 + 1}", 0, 14, 34, face=FONT_TITLE,
                         a=0.25 + 0.55 * depth)
            K.hero(cr, T, CX, 1062, "front", s=0.55, ink=NIGHT_INK, fill=NF, gy=-0.8, smile=0.3)
            n = int(1000 * k)
            if T > t_th - 0.7:
                text(cr, f"{n:,}", CX, 650, 140, face=FONT_TITLE, c=YELLOW, outline=(0.3, 0.2, 0.0), ow=10)
                text(cr, "YEARS", CX, 750, 56, face=FONT_TITLE, c=WHITE, a=clamp(k * 3))
        burst(cr, CX, 650, T - (t_th + 0.7), n=24, dist=420, size=9, c=YELLOW, dur=0.8)
        vignette(cr, 0.45)
    b.fx(0.3, "drone", -16, dur=3.5)
    b.fx(t_th - 0.7, "fastforward", -10)
    b.fx(t_th + 0.7, "shimmer", -8)

    # 2. not frail and old: healthy, strong, young
    st2 = s("c1_02") - 0.15
    t_frail, t_but = w("c1_02", "frail"), w("c1_02", "but healthy")
    t_h, t_s, t_y, t_ent = w("c1_02", "healthy"), w("c1_02", "strong"), w("c1_02", "young"), w("c1_02", "entire")

    @b.shot(st2, "fade", 0.4)
    def young(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 620):
            S.park(cr, T, gy=900)
            ko = ease(prog(T, t_but + 0.35, 0.5))
            if ko < 1:
                x = lerp(CX, -300, ko)
                shake_x = 3 * math.sin(T * 40)
                oldie(cr, T, x + shake_x, 900, face=1, s=1.1, acc=("tuft",), bend=1.7, smile=-0.3, brow=-0.5)
                if T > t_frail and ko < 0.2:
                    label_box(cr, "FRAIL & OLD?", x, 380, 44, c=INK, scale=K.pop(T, t_frail))
                xmark(cr, x, 680, 170, prog(T, t_but - 0.1, 0.3) * (1 - ko))
            if T > t_but + 0.4:
                kh = back(prog(T, t_but + 0.4, 0.5))
                p = flex_pose(CX, 1.25, eye=1.1)
                p = sm.on_ground(sm.idle(p, T, 2), 900)
                p["y"] -= 60 * (1 - ease(prog(T, t_but + 0.4, 0.45)))
                with xform(cr, CX, 900, max(0.01, kh), sx=None):
                    cr.translate(-CX, -900)
                    sm.draw(cr, p, acc=HERO)
                sparkles(cr, T, CX, 640, 260, 200, n=10, c=YELLOW, seed=3)
            for (lab, tt, x, y, c) in (("HEALTHY", t_h, 560, 330, GREEN), ("STRONG", t_s, CX, 250, BLUE),
                                       ("YOUNG", t_y, 1360, 330, ORANGE)):
                k = K.pop(T, tt)
                if k > 0:
                    label_box(cr, lab, x, y, 58, c=WHITE, bg=c, face=FONT_TITLE, bold=False, scale=k, lw=5)
        if T > t_ent:
            text(cr, "...THE ENTIRE TIME", CX, 1010, 54, face=FONT_TITLE, c=WHITE, outline=INK, ow=8,
                 a=eout(prog(T, t_ent, 0.4)))
    b.fx(t_frail, "pop", -12)
    b.fx(t_but - 0.1, "scratch_out", -10)
    b.fx(t_but + 0.4, "sparkle", -8)
    for tt in (t_h, t_s, t_y):
        b.fx(tt, "pop", -10)

    # 2b. a thousand birthdays, summers, ten centuries
    st3 = s("c1_02b") - 0.15

    def ic_cake(cr, T):
        cake(cr, 0, 110, 0.6, candles=9, t=T)

    def ic_summer(cr, T):
        P.sun(cr, 60, -60, 46, T)
        rect(cr, -140, 60, 280, 50, fill=(0.98, 0.88, 0.60), stroke=INK, lw=4)
        polyline(cr, [(-140, 60)] + [(-140 + i * 20, 52 + 6 * math.sin(T * 3 + i)) for i in range(15)] + [(140, 60)],
                 0, INK, closed=True, fill=(0.35, 0.65, 0.95))
        line(cr, -50, 110, -60, -40, 6, INK)
        cr.new_path()
        cr.arc(-60, -40, 90, math.pi, TAU)
        cr.close_path()
        src(cr, RED)
        cr.fill_preserve()
        src(cr, INK)
        cr.set_line_width(5)
        cr.stroke()
        for k in (-1, 1):
            polyline(cr, [(-60, -130), (-60 + k * 45, -40), (-60 + k * 20, -40)], 0, INK, closed=True, fill=WHITE)

    def ic_cent(cr, T):
        P2.hourglass(cr, 0, 0, 0.62, p=(T * 0.25) % 1, t=T)
        label_box(cr, "x10", 95, -100, 40, c=WHITE, bg=PURPLE, face=FONT_TITLE, bold=False)

    def bg3(cr, T):
        vgrad(cr, (1.0, 0.93, 0.78), (0.98, 0.84, 0.66))
        radial_lines(cr, CX, 520, T, n=28, c=WHITE, a=0.25, w=30)

    b.add(st3, K.icons("A LIFE OF 1,000 YEARS", [(ic_cake, "1,000 BIRTHDAYS", w("c1_02b", "birthdays") - 0.25),
                                                 (ic_summer, "1,000 SUMMERS", w("c1_02b", "summers") - 0.25),
                                                 (ic_cent, "10 CENTURIES", w("c1_02b", "centuries") - 0.25)],
                       bg=bg3, y=560, size=1.25, label_size=46), "slide", 0.4)
    for wd in ("birthdays", "summers", "centuries"):
        b.fx(w("c1_02b", wd) - 0.25, "pop", -8)

    # 3. empires rise and fall
    st4 = s("c1_03") - 0.15
    t_rise, t_fall = w("c1_03", "rise"), w("c1_03", "fall")

    @b.shot(st4, "fade", 0.3)
    def empires(cr, t, d, T):
        kd = prog(T, st4, 3.0)
        vgrad(cr, lerpc((1.0, 0.80, 0.55), (0.55, 0.45, 0.70), kd), (0.98, 0.90, 0.78))
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            P.sun(cr, lerp(300, 1650, kd), 260 - 120 * math.sin(kd * math.pi), 70, T)
            S.floor(cr, 880, (0.70, 0.62, 0.45))
            kr = ease(prog(T, st4, t_rise - st4 + 0.4))
            kf = ease(prog(T, t_fall, 0.6))
            cr.save()
            cr.rectangle(-500, -500, W + 1000, 880 + 500)
            cr.clip()
            with xform(cr, 1150, 880 + 560 * (1 - kr) + 260 * kf, 1.0, 0.18 * kf):
                S.castle(cr, 0, 0, 1.0, t=T, flag_c=PURPLE)
            cr.restore()
            cr.new_path()
            if kf > 0:
                g = rng(5)
                for i in range(18):
                    rx = 1150 + g.uniform(-380, 380)
                    ry = 880 - 40 * g.random() - 140 * math.sin(math.pi * clamp(kf * 1.2 - g.random() * 0.2))
                    rect(cr, rx - 20, ry - 16, 40, 32, fill=(0.82, 0.80, 0.76), stroke=INK, lw=3)
                for i in range(6):
                    circle(cr, 1150 + (i - 2.5) * 140, 860 - 60 * kf, 70 + 80 * kf, fill=(0.80, 0.75, 0.68),
                           a=0.55 * (1 - kf))
            K.hero(cr, T, 380, 900, "surprised" if T > t_fall else "point", face=1, s=0.95)
            for (lab, tt, c, up) in (("RISE", t_rise, GREEN, True), ("FALL", t_fall, RED, False)):
                k = K.pop(T, tt)
                if k > 0:
                    with xform(cr, 600 if up else 1700, 300, max(0.01, k)):
                        arrow(cr, 0, 70 if up else -70, 0, -70 if up else 70, 16, c, head=46)
                        text(cr, lab, 0, 130, 54, face=FONT_TITLE, c=c, outline=INK, ow=6)
    b.fx(st4 + 0.1, "rise", -10)
    b.fx(t_fall, "crash", -8)

    # 4. villages into cities, then unimaginable technology
    st5 = s("c1_04") - 0.15
    t_grow, t_city, t_tech, t_imag = (w("c1_04", "grow"), w("c1_04", "cities"), w("c1_04", "technologies"),
                                      w("c1_04", "imagine"))

    @b.shot(st5, "fade", 0.3)
    def timelapse(cr, t, d, T):
        cyc = 0.5 + 0.5 * math.cos(T * 2.4)
        nk = clamp(1 - cyc * 1.4)
        vgrad(cr, lerpc((0.62, 0.80, 0.98), (0.07, 0.08, 0.20), nk), lerpc((0.95, 0.92, 0.85), (0.20, 0.18, 0.32), nk))
        stars(cr, T, n=120, alpha=nk * 0.8, area=(0, 0, W, 600))
        with K.ken(cr, t, d, 1.0, 1.05, 1100, 600):
            a_s = T * 2.4
            P.sun(cr, 1100 + math.sin(a_s) * 800, 700 - math.cos(a_s) * 520, 60, T, a=clamp(1 - nk))
            kc = ease(prog(T, t_grow - 0.2, t_city - t_grow + 0.9))
            kv = 1 - clamp(kc * 1.6)
            if kv > 0:
                with group(cr, kv):
                    for i, x in enumerate((880, 1120, 1380, 1640)):
                        thatched_hut(cr, x, 900, 0.65)
            if kc > 0:
                P.skyline(cr, 760, 900, 1360, 560 * kc, seed=8, fill=lerpc((0.55, 0.58, 0.66), (0.16, 0.17, 0.25), nk),
                          lit=nk > 0.3, t=T, outline=INK)
                for i, x in enumerate((900, 1300, 1700)):
                    k2 = clamp(kc * 1.5 - 0.3 - i * 0.15)
                    if k2 > 0:
                        P.house(cr, x, 900, 0.5 * k2 + 0.01, lit=nk)
            S.floor(cr, 900, lerpc((0.62, 0.78, 0.48), (0.15, 0.20, 0.15), nk))
            kt = prog(T, t_tech - 0.2, 0.5)
            if kt > 0:
                for i in range(4):
                    f = (T * 0.25 + i * 0.27) % 1
                    x = lerp(2200, 600, f)
                    y = 300 + i * 70 + 20 * math.sin(T * 3 + i)
                    with group(cr, kt):
                        P.drone(cr, x, y, 0.45, T, version=1 + i % 3)
                ki = K.pop(T, t_imag)
                if ki > 0:
                    for i, (x, y) in enumerate(((1000, 200), (1350, 150), (1680, 230))):
                        glow(cr, x, y, 110, CYAN, 0.45 * clamp(ki))
                        with xform(cr, x, y + 8 * math.sin(T * 3 + i), max(0.01, ki)):
                            circle(cr, 0, 0, 52, fill=(0.85, 0.97, 1.0), stroke=INK, w=5)
                            text(cr, "?", 0, 4, 62, face=FONT_TITLE, c=BLUE)
            P.hill(cr, 300, 905, 760, 150, c=lerpc((0.55, 0.72, 0.42), (0.10, 0.14, 0.10), nk), ink=INK)
            p = sm.pose("sit", x=330, face=1, a1f=40, a2f=40, a1b=30, a2b=40, gx=0.6, gy=-0.3, smile=0.5)
            p["y"] = 768
            sm.draw(cr, sm.idle(p, T, 1), acc=HERO, ink=lerpc(INK, NIGHT_INK, nk), fill=lerpc(WHITE, NF, nk))
        if T > t_city:
            label_box(cr, "VILLAGES  >  CITIES", 1300, 1000, 46, c=INK, scale=K.pop(T, t_city))
    b.fx(st5 + 0.2, "fastforward", -10)
    b.fx(t_city, "pop", -12)
    b.fx(t_tech, "whoosh", -12)
    b.fx(t_imag, "shimmer", -10)

    # 5a. master every skill
    st6 = s("c1_05") - 0.15
    t_vis, t_read, t_twice = w("c1_05", "visit"), w("c1_05", "read"), w("c1_05", "twice")

    @b.shot(st6, "slide", 0.4)
    def skills(cr, t, d, T):
        vgrad(cr, (0.95, 0.90, 1.0), (0.85, 0.82, 0.96))
        radial_lines(cr, CX, 600, T, n=24, c=WHITE, a=0.35, w=26)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.floor(cr, 900, (0.75, 0.70, 0.85))
            for i in range(10):
                a = T * 0.9 + i * TAU / 10
                k = K.pop(T, st6 + 0.1 + i * 0.12)
                if k > 0:
                    x, y = CX + math.cos(a) * 470, 560 + math.sin(a) * 210
                    with xform(cr, x, y, max(0.01, k) * 0.95):
                        circle(cr, 0, 0, 78, fill=WHITE, stroke=INK, w=5)
                        skill_icon(cr, i * 2, T)
            K.hero(cr, T, CX, 900, "cheer", s=1.0, smile=1.0)
        title_text(cr, "MASTER EVERY SKILL", 140, 72, c=WHITE, k=eout(prog(t, 0.0, 0.3)))
    for i in range(10):
        b.fx(st6 + 0.1 + i * 0.12, "blip", -18)

    # 5b. visit every country
    @b.shot(t_vis - 0.15, "slide", 0.35)
    def countries(cr, t, d, T):
        vgrad(cr, (0.55, 0.78, 0.98), (0.88, 0.95, 1.0))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            P.cloud(cr, 300, 250, 1.0)
            P.cloud(cr, 1650, 200, 0.8)
            P.globe(cr, CX, 600, 300, T * 1.5)
            g = rng(12)
            for i in range(14):
                k = K.pop(T, t_vis + 0.1 + i * 0.1, 0.3)
                if k > 0:
                    a = g.uniform(0, TAU)
                    rr = g.uniform(0, 250)
                    x, y = CX + math.cos(a) * rr, 600 + math.sin(a) * rr * 0.9
                    with xform(cr, x, y, max(0.01, k)):
                        line(cr, 0, 0, 0, -50, 5, INK)
                        circle(cr, 0, -56, 14, fill=[RED, YELLOW, GREEN, BLUE][i % 4], stroke=INK, w=3)
            a = T * 1.6
            jet(cr, CX + math.cos(a) * 420, 600 + math.sin(a) * 330, 0.45, rot=a + math.pi / 2)
        title_text(cr, "VISIT EVERY COUNTRY", 140, 72, c=WHITE)
    b.fx(t_vis - 0.1, "whoosh", -10)
    for i in range(0, 14, 3):
        b.fx(t_vis + 0.1 + i * 0.1, "pop", -18)

    # 5c. read almost every book, twice
    @b.shot(t_read - 0.15, "slide", 0.35)
    def books(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            S.room(cr, T, wall=(0.96, 0.90, 0.80), floor_c=(0.62, 0.45, 0.32), fy=900)
            for i, x in enumerate((180, 440, 1480, 1740)):
                P.bookshelf(cr, x, 900, 1.6, highlight=1.0)
            n = int(clamp(prog(T, t_read, t_twice - t_read)) * 9)
            for i in range(n + 1):
                P.book(cr, 1180, 880 - i * 26, 0.5, c=[BLUE, RED, GREEN, ORANGE, PURPLE][i % 5], rot=math.pi / 2)
            p = sm.pose("sit", x=820, face=1, a1f=60, a2f=60, a1b=50, a2b=70, gy=0.5, smile=0.6)
            p["y"] = 740
            P.chair(cr, 800, 900, 1.0)
            J = sm.draw(cr, sm.idle(p, T, 4), acc=HERO)
            P.book(cr, J["hand_f"][0] + 20, J["hand_f"][1] - 20, 0.6, open_=1.0)
        title_text(cr, "READ EVERY BOOK", 140, 72, c=WHITE)
        if T > t_twice:
            stamp(cr, "TWICE!", 1500, 560, T - t_twice, 110, c=RED, rot=-0.1)
    b.fx(t_read - 0.1, "page", -8)
    b.fx(t_twice, "stamp", -6)

    # 6. but here's the question
    b.add(s("c1_06") - 0.2, K.real_question(s("c1_06")), "black", 0.4)
    b.fx(s("c1_06"), "tick", -8)
    b.fx(s("c1_06") + 0.5, "tock", -8)

    # 7. gift or curse?
    st8 = s("c1_07") - 0.1
    t_or = w("c1_07", "or the")

    def gift(cr, cx, T):
        radial_lines(cr, cx, 460, T, n=24, c=YELLOW, a=0.35, w=26)
        for i in range(24):
            g = rng(i)
            y = (g.uniform(0, 1100) + T * g.uniform(80, 160)) % 1100 - 50
            rect(cr, cx + g.uniform(-460, 460), y, 14, 22, fill=[RED, BLUE, GREEN, PURPLE, ORANGE][i % 5])
        with xform(cr, cx, 900, 1.0):
            rect(cr, -190, -260, 380, 260, fill=RED, stroke=INK, lw=6)
            rect(cr, -210, -300, 420, 60, fill=(0.85, 0.12, 0.15), stroke=INK, lw=6)
            rect(cr, -24, -300, 48, 300, fill=YELLOW, stroke=INK, lw=4)
            for k in (-1, 1):
                ellipse(cr, k * 60, -330, 62, 32, fill=YELLOW, stroke=INK, w=4, rot=k * 0.4)
        K.hero(cr, T, cx, 572, "cheer", s=0.9, smile=1.0)

    def curse(cr, cx, T):
        glow(cr, cx + 200, 230, 220, (0.8, 0.85, 1.0), 0.35)
        circle(cr, cx + 200, 230, 60, fill=(0.92, 0.93, 0.98))
        S.floor(cr, 900, (0.08, 0.09, 0.14), ink=(0.3, 0.3, 0.4))
        for i, x in enumerate((-330, -180, 170, 330)):
            gravestone(cr, cx + x, 905 + (i % 2) * 30, 0.85, "R.I.P.", c=(0.35, 0.37, 0.45))
        K.hero(cr, T, cx, 905, "sad", s=0.95, ink=NIGHT_INK, fill=NF)

    b.add(st8, K.split(dict(title="THE GREATEST GIFT?", bg=(1.0, 0.95, 0.78), draw=gift),
                       dict(title="THE LONELIEST CURSE?", bg=(0.10, 0.11, 0.20), draw=curse), t_or), "fade", 0.3)
    b.fx(st8, "chime", -8)
    b.fx(t_or, "darkwhoosh", -6)

    # 8. title
    st9 = e("c1_07") - 0.2

    @b.shot(st9, "cut")
    def title(cr, t, d, T):
        TITLE(cr, t)
    b.fx(st9, "whoosh", -4)
    b.fx(st9 + 0.5, "boom", 0)
    b.fx(st9 + 0.55, "shimmer", -8)
    return b.result()
