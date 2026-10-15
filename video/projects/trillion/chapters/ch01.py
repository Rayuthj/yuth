"""Trillion - Chapter 1: The Hook (0:00-0:40)."""
from video.projects.trillion.chapters._m import *  # noqa: F401,F403

DARK_TAG = True


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 72, 0.5), ("c1_02", "uplift", "uplift", 104, 0.75),
                        ("c1_06", "mystery", "mystery", 70, 0.55), (tl.e("c1_07") + 0.2, "uplift", "mystery", 96, 0.9)])


def bedroom(cr, T, dawn=0.0):
    S.room(cr, T, wall=lerpc((0.20, 0.22, 0.32), (0.55, 0.58, 0.70), dawn), floor_c=lerpc((0.16, 0.15, 0.20),
           (0.40, 0.36, 0.38), dawn), fy=900)
    P.window(cr, 1450, 380, 380, 300, T, sky=lerpc((0.10, 0.12, 0.28), (0.98, 0.80, 0.60), dawn),
             sky2=lerpc((0.20, 0.20, 0.40), (0.75, 0.86, 0.98), dawn), city=True, night=dawn < 0.5)


def build(tl):
    b = Builder(tl)
    s, e, w = timing(tl)

    # 1. early morning: the phone buzzes, you grab it
    t_app = w("c1_01", "banking")
    st1b = t_app + 0.15

    @b.shot(0)
    def wake(cr, t, d, T):
        with K.ken(cr, t, d, 1.3, 1.42, 860, 700):
            bedroom(cr, T, 0.25 * ease(t / max(d, 0.1)))
            P.bed(cr, 760, 900, 1.25)
            P.nightstand(cr, 1120, 900, 1.0)
            k = ease(prog(T, 0.9, 0.8))
            buzz = math.sin(T * 70) * 5 * (1 - k) * (1 if (T % 0.8) < 0.5 else 0)
            p = sm.pose("sit", x=700, face=1, smile=0.0, brow=-0.2, gx=0.8, a1f=lerp(10, 70, k), a2f=lerp(5, 40, k),
                        l1f=86, l2f=-86, l1b=82, l2b=-82, blink=0.6 * (1 - k))
            p["y"] = lerp(820, 760, k)
            J = sm.draw(cr, sm.idle(p, T, 1), acc=HERO)
            if k < 0.6:
                P.phone(cr, 1120 + buzz, 690, 0.55, T, lit=1.0)
                for i in range(2):
                    arc(cr, 1120, 690, 60 + i * 22, -0.7, 0.7, 4, YELLOW, 0.8 * (1 - k))
                    arc(cr, 1120, 690, 60 + i * 22, math.pi - 0.7, math.pi + 0.7, 4, YELLOW, 0.8 * (1 - k))
            else:
                P.phone(cr, J["hand_f"][0] + 18, J["hand_f"][1] - 30, 0.6, T, lit=1.0, rot=0.2)
                glow(cr, J["hand_f"][0] + 18, J["hand_f"][1] - 30, 140, (0.7, 0.85, 1.0), 0.4)
            # blanket over the legs
            polyline(cr, [(560, 760), (900, 760), (1020, 790), (1020, 840), (560, 840)], 5, INK, closed=True,
                     fill=(0.35, 0.45, 0.70))
    b.fx(0.2, "buzz", -12, dur=0.7)
    b.fx(1.1, "swish", -14)

    # 1b. the app: a one... followed by twelve zeros
    t_one = w("c1_01", "one")
    t_fol = w("c1_01", "followed")
    t_z = e("c1_01") - 0.05
    zt = [lerp(t_fol, t_z, i / 11) for i in range(12)]

    def n_zeros(T):
        return sum(1 for z in zt if T >= z)

    @b.shot(st1b, "zoom", 0.5)
    def app(cr, t, d, T):
        vgrad(cr, (0.16, 0.18, 0.28), (0.06, 0.06, 0.10))
        glow(cr, 1250, 640, 700, (0.55, 0.75, 1.0), 0.25)
        nz = n_zeros(T)
        amt = "$0" if T < t_one else money_str(nz)
        kz = nz / 12
        sx, sy = shake(T, 6 * kz if nz >= 12 and T < t_z + 0.6 else 0)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 560):
            # the hero's face, eyes growing with every zero
            p = sm.pose("front", s=3.3, lw=5.5, fo=0.25, face=1, gx=0.9, gy=0.1, smile=lerp(0.1, 0.3, kz),
                        eye=1.0 + 0.45 * kz, browy=kz, mo=0.55 * kz if nz >= 12 else 0.0)
            p = head_at(sm.idle(p, T, 2, 0.4), 430 + sx, 640 + sy)
            cr.save()
            cr.rectangle(0, 0, 900, 640 + sy + 3.3 * 40 + 40)
            cr.clip()
            sm.draw(cr, p, acc=HERO)
            cr.restore()
            cr.new_path()
            big_phone(cr, 1250, 690, 1.0, rot=0.05, screen=bank_screen(amt, k_glow=kz))
            for k_ in (-1, 1):
                circle(cr, 1250 + k_ * 195, 830, 34, fill=WHITE, stroke=INK, w=7)
        if T >= t_one:
            k1 = K.pop(T, t_one)
            big = money_str(nz)
            size = fit_size(cr, big, 1500, 140)
            text(cr, big, CX, 165, size, face=FONT_TITLE, c=MONEY_G, outline=(0.03, 0.22, 0.06), ow=12,
                 scale=max(0.01, k1) if nz == 0 else 1.0)
            if nz > 0:
                label_box(cr, f"ZEROS: {nz}", 300, 300, 46, c=INK, bg=YELLOW if nz == 12 else WHITE, face=FONT_TITLE,
                          bold=False, scale=1.0 + 0.18 * (1 - prog(T, zt[nz - 1], 0.15)))
            if nz >= 12:
                burst(cr, CX, 165, T - zt[-1], n=28, dist=760, size=10, c=MONEY_G, dur=0.9, seed=3)
        vignette(cr, 0.35)
    b.fx(st1b, "whoosh", -10)
    b.fx(t_one, "ding", -8)
    for i, z in enumerate(zt):
        b.fx(z, "blip", -16 + i * 0.4)
    b.fx(zt[-1] + 0.05, "success", -6)

    # 2. one trillion dollars, all yours, every last cent
    st2 = s("c1_02") - 0.15
    t_yours, t_cent = w("c1_02", "all yours"), w("c1_02", "cent")

    @b.shot(st2, "white", 0.3)
    def rich(cr, t, d, T):
        vgrad(cr, (0.06, 0.30, 0.14), (0.02, 0.12, 0.06))
        radial_lines(cr, CX, 520, T, n=30, c=GOLD, a=0.12, w=24)
        glow(cr, CX, 560, 600, GOLD, 0.25)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            cash_pile(cr, 520, 960, 0.8, rows=5, seed=2)
            cash_pile(cr, 1420, 960, 0.8, rows=5, seed=5)
            S.floor(cr, 960, (0.05, 0.18, 0.09), ink=(0.3, 0.5, 0.3))
            kc = prog(T, t_cent - 0.6, 0.6)
            g = "cheer" if T < t_cent - 0.6 else "hold"
            J = dude(cr, T, CX, 960, g, s=1.25, smile=1.0, eye=1.15, ink=WHITE, fill=(0.05, 0.18, 0.09),
                     mo=0.5 if g == "cheer" else 0.0, a1f=60 if g == "hold" else 158, a2f=70 if g == "hold" else 8,
                     a1b=-158 if g == "cheer" else -20, gx=0.6 if g == "hold" else 0.0, gy=0.5 if g == "hold" else 0.0)
            if kc > 0:
                hx, hy = J["hand_f"]
                cy = lerp(-80, hy - 18, ein(kc)) if kc < 1 else hy - 18 + 3 * math.sin(T * 6)
                P2.coin(cr, hx + 6, cy, 22, c=(0.85, 0.50, 0.25), rot=T * 7 if kc < 1 else 0.0)
                if kc >= 1:
                    label_box(cr, "1¢", hx + 90, hy - 80, 44, c=INK, bg=WHITE, face=FONT_TITLE, bold=False,
                              scale=K.pop(T, t_cent))
        money_rain(cr, T, n=26, seed=4, s=0.42)
        text(cr, "ONE TRILLION DOLLARS", CX, 150, 96, face=FONT_TITLE, c=MONEY_G, outline=(0.02, 0.15, 0.05), ow=12,
             scale=lerp(1.6, 1.0, eout(prog(t, 0.1, 0.4))), a=clamp(prog(t, 0.1, 0.2) * 2))
        stamp(cr, "ALL YOURS", 1560, 330, T - t_yours, 70, c=GOLD, rot=0.08)
        if T > t_cent:
            text(cr, "...EVERY LAST CENT", 400, 330, 52, face=FONT_TITLE, c=WHITE, a=eout(prog(T, t_cent, 0.4)))
    b.fx(st2 + 0.1, "coins", -6, dur=2.5)
    b.fx(st2 + 0.2, "cheer", -12, dur=2.0)
    b.fx(t_yours, "stamp", -6)
    b.fx(t_cent, "ding", -6)

    # 3. a private island before breakfast, a sports team before lunch
    st3 = s("c1_03") - 0.15
    t_isl, t_team = w("c1_03", "private"), w("c1_03", "sports team")
    t_bf, t_lunch = w("c1_03", "breakfast"), w("c1_03", "lunch")

    def panel_island(cr, cx, T):
        vgrad(cr, (0.98, 0.80, 0.55), (0.75, 0.88, 0.98))
        P.sun(cr, cx + 250, 300, 60, T)
        waves(cr, T, 760)
        k = K.pop(T, t_isl)
        if k > 0:
            with xform(cr, cx, 760, max(0.01, k)):
                island(cr, 0, 0, 1.2, T)
                J = dude(cr, T, 60, -96, "hold", s=0.62, face=1, smile=0.9, a1f=70, a2f=60)
                P.coffee(cr, J["hand_f"][0] + 14, J["hand_f"][1] - 6, 0.4, T)
        P.clock(cr, cx - 280, 320, 70, T, hours=7, minutes=30, speed=0)
        stamp(cr, "SOLD", cx + 230, 520, T - t_bf, 64, c=RED, rot=-0.12)

    def panel_team(cr, cx, T):
        vgrad(cr, (0.55, 0.78, 0.98), (0.85, 0.93, 0.98))
        rect(cr, cx - 600, 760, 1200, 400, fill=(0.40, 0.72, 0.38))
        line(cr, cx - 600, 760, cx + 600, 760, 4, INK)
        for i in range(3):
            line(cr, cx - 600, 820 + i * 80, cx + 600, 820 + i * 80, 3, WHITE, 0.6)
        k = K.pop(T, t_team)
        if k > 0:
            for i, (dx, acc) in enumerate(((-230, ("cap",)), (-110, ("bun",)), (110, ("glasses",)), (230, ()))):
                dude(cr, T, cx + dx, 880, "cheer", s=0.6, acc=acc, seed=i, smile=1, under=jersey(BLUE, 7 + i),
                     alpha=clamp(k))
            dude(cr, T, cx, 900, "cheer", s=0.7, smile=1, under=jersey(GOLD, 1), alpha=clamp(k))
            stadium_ball(cr, cx + 330, 870 - abs(math.sin(T * 5)) * 60, 26, T * 4)
        P.clock(cr, cx - 280, 320, 70, T, hours=11, minutes=55, speed=0)
        stamp(cr, "SOLD", cx + 230, 520, T - t_lunch, 64, c=RED, rot=0.1)

    b.add(st3, K.split(dict(title="BEFORE BREAKFAST", bg=(0.98, 0.9, 0.8), draw=panel_island),
                       dict(title="BEFORE LUNCH", bg=(0.85, 0.93, 0.98), ink=INK, draw=panel_team), t_team - 0.5),
          "slide", 0.4)
    b.fx(t_isl, "pop", -8)
    b.fx(t_bf, "stamp", -8)
    b.fx(t_team - 0.5, "swoosh", -10)
    b.fx(t_team, "cheer", -12, dur=1.5)
    b.fx(t_lunch, "stamp", -8)

    # 4. a space program, a city, a house for everyone you know
    st4 = s("c1_04") - 0.15
    t_sp, t_city, t_house = w("c1_04", "space"), w("c1_04", "city"), w("c1_04", "house")

    def ic_rocket(cr, T):
        k = ease(prog(T, t_sp + 0.2, 2.5))
        rocket(cr, 0, 100 - 140 * k, 0.55, T, flame=1.0 if k > 0 else 0.3)
        for i in range(3):
            P.cloud(cr, -80 + i * 80, 105, 0.32, c=(0.92, 0.92, 0.94))

    def ic_city(cr, T):
        k = ease(prog(T, t_city, 1.2))
        for i, (dx, hh, c) in enumerate(((-120, 160, BLUE), (-50, 230, (0.55, 0.65, 0.80)), (30, 290, (0.35, 0.45, 0.65)),
                                          (110, 190, (0.65, 0.72, 0.85)))):
            h_ = hh * clamp(k * 1.5 - i * 0.15)
            if h_ > 2:
                rect(cr, dx - 36, 130 - h_, 72, h_, fill=c, stroke=INK, lw=4)
                for j in range(int(h_ // 40)):
                    rect(cr, dx - 20, 130 - h_ + 14 + j * 40, 14, 18, fill=YELLOW)
                    rect(cr, dx + 6, 130 - h_ + 14 + j * 40, 14, 18, fill=YELLOW)
        line(cr, -180, 130, 180, 130, 5, INK)

    def ic_houses(cr, T):
        for i, dx in enumerate((-110, 0, 110)):
            k = K.pop(T, t_house + i * 0.15)
            if k > 0:
                P.house(cr, dx, 40, 0.45 * max(0.01, k), roof=[RED, BLUE, GREEN][i])
        for i, (dx, acc) in enumerate(((-130, ("cap",)), (-40, ("ponytail",)), (50, ("glasses",)), (140, ("bun",)))):
            p = sm.on_ground(sm.idle(sm.pose("cheer", x=dx, s=0.3, smile=1.0), T, i), 135)
            sm.draw(cr, p, acc=acc)

    b.add(st4, icons2("WITH $1 TRILLION, YOU COULD...", [(ic_rocket, "FUND A\nSPACE PROGRAM", st4 + 0.25),
                                                         (ic_city, "BUILD\nA CITY", t_city),
                                                         (ic_houses, "A HOUSE FOR\nEVERYONE YOU KNOW", t_house)],
                      bg=(0.96, 0.95, 0.90), y=500, size=1.25, label_size=40, title_y=150), "slide", 0.4)
    for tt in (t_sp, t_city, t_house):
        b.fx(tt, "pop", -8)
    b.fx(t_sp + 0.3, "rise", -12)

    # 5. never check a price tag again
    st5 = s("c1_05") - 0.15
    tags = [("GROCERIES  $84.20", w("c1_05", "groceries"), 480, 170, -0.10),
            ("HOUSE  $1,250,000", w("c1_05", "houses"), 960, 120, 0.06),
            ("ANYTHING  $$$$", w("c1_05", "anything"), 1460, 170, -0.05)]
    t_tag0 = st5 + 0.3
    t_ever = w("c1_05", "ever.")

    @b.shot(st5, "fade", 0.3)
    def no_prices(cr, t, d, T):
        with K.ken(cr, t, d, 1.12, 1.18, CX, 700):
            S.room(cr, T, wall=(0.93, 0.95, 0.96), floor_c=(0.82, 0.84, 0.86), fy=900)
            for row in range(3):
                y0 = 470 + row * 150
                rect(cr, -100, y0, 2200, 14, fill=(0.65, 0.68, 0.72), stroke=INK, lw=3)
                g = rng(row + 2)
                x = -80
                while x < 2100:
                    bw = g.uniform(50, 90)
                    bh = g.uniform(60, 110)
                    rect(cr, x, y0 - bh, bw, bh, fill=g.choice([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CASH]),
                         stroke=INK, lw=3)
                    x += bw + 8
            hx = lerp(380, 1150, ease(prog(t, 0.0, d * 0.8)))
            cart(cr, hx + 190, 905, 1.1, items=1.0, t=T)
            J = dude(cr, T, hx, 905, "point", s=1.05, walk=0.8 if t < d * 0.8 else 0.0, smile=0.9, brow=0.3,
                     a1f=80, a2f=10)
            # a price tag tossed over the shoulder
            kt = prog(T, t_tag0, 0.9)
            if 0 < kt < 1:
                price_tag(cr, J["head"][0] - 260 * kt, J["head"][1] - 40 - 220 * math.sin(kt * math.pi), 0.8,
                          "$4.99", -kt * 6, size=36)
        for (lab, ta, x, y, rot) in tags:
            k = K.pop(T, ta)
            if k > 0:
                fly = ease(prog(T, ta + 0.9, 0.6))
                price_tag(cr, x + 400 * fly, y - 260 * fly, max(0.01, k), lab, rot + 2.5 * fly, size=54,
                          a=1 - fly)
                if fly < 0.6:
                    cross(cr, x + 20 + 400 * fly, y - 260 * fly, 2.2, p=prog(T, ta + 0.35, 0.3), a=1 - fly)
        stamp(cr, "EVER.", CX, 820, T - t_ever, 110, c=RED, rot=-0.06)
    b.fx(st5, "footsteps", -16, dur=3.0)
    b.fx(t_tag0, "swish", -12)
    for (_, ta, _, _, _) in tags:
        b.fx(ta, "pop", -10)
        b.fx(ta + 0.35, "scratch_out", -12)
    b.fx(t_ever, "stamp", -4)

    # 6. but here's the question
    b.add(s("c1_06") - 0.2, K.real_question(s("c1_06")), "black", 0.4)
    b.fx(s("c1_06"), "tick", -8)
    b.fx(s("c1_06") + 0.5, "tock", -8)

    # 7. happiest person alive... or buried under problems?
    st7 = s("c1_07") - 0.1
    t_or = w("c1_07", "or bury")

    def happy(cr, cx, T):
        radial_lines(cr, cx, 420, T, n=24, c=YELLOW, a=0.35, w=26)
        cash_pile(cr, cx, 960, 0.75, rows=4, seed=7)
        J = dude(cr, T, cx, 960 - 4 * 58 * 0.75 - 40, "cheer", s=1.0, smile=1.0, mo=0.5)
        del J
        g = rng(3)
        for i in range(24):
            f = (T * 0.4 + g.random()) % 1
            x = cx + g.uniform(-420, 420)
            rect(cr, x, 200 + f * 800, 14, 22, fill=g.choice([RED, BLUE, YELLOW, GREEN, PURPLE]))

    def buried(cr, cx, T):
        g = rng(11)
        for i in range(60):
            bill(cr, cx + g.uniform(-380, 380), 980 - g.uniform(0, 260) * (1 - abs(g.uniform(-1, 1)) * 0.4), 0.55,
                 g.uniform(-0.8, 0.8), flip=1)
        p = sm.pose("front", s=1.0, fo=0.0, smile=-0.6, brow=-0.8, eye=1.2, gy=-0.6)
        p = head_at(sm.idle(p, T, 3), cx - 40, 760)
        cr.save()
        cr.rectangle(cx - 300, 0, 600, 790)
        cr.clip()
        sm.draw(cr, p, acc=HERO, ink=WHITE, fill=(0.25, 0.04, 0.06))
        cr.restore()
        cr.new_path()
        polyline(cr, [(cx + 60, 800), (cx + 70, 700), (cx + 90 + 10 * math.sin(T * 6), 640)], 7, WHITE)
        for i, (lab, x, y) in enumerate((("SCAMS", -260, 300), ("LAWSUITS", 200, 260), ("FAKE FRIENDS", -170, 470),
                                         ("BODYGUARDS", 230, 450))):
            k = K.pop(T, t_or + 0.4 + i * 0.3)
            if k > 0:
                label_box(cr, lab, cx + x, y + 6 * math.sin(T * 2 + i), 34, c=WHITE, bg=(0.45, 0.06, 0.08),
                          face=FONT_TITLE, bold=False, scale=k)

    b.add(st7, K.split(dict(title="THE HAPPIEST PERSON ALIVE?", bg=(1.0, 0.95, 0.80), draw=happy),
                       dict(title="BURIED UNDER PROBLEMS?", bg=(0.25, 0.04, 0.06), draw=buried), t_or), "fade", 0.3)
    b.fx(st7, "chime", -8)
    b.fx(t_or, "glitch", -6)
    for i in range(4):
        b.fx(t_or + 0.4 + i * 0.3, "pop", -14)

    # 8. title
    st9 = e("c1_07") - 0.2

    @b.shot(st9, "cut")
    def title(cr, t, d, T):
        TITLE(cr, t)
    b.fx(st9, "whoosh", -4)
    b.fx(st9 + 0.5, "boom", 0)
    b.fx(st9 + 0.55, "coins", -8)
    return b.result()
