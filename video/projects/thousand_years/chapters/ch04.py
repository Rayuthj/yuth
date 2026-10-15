"""Thousand Years - Chapter 4: The Money Machine (2:40-3:40)."""
from video.projects.thousand_years.chapters._t import *  # noqa: F401,F403

DARK_TAG = True
MONEY_BG = ((0.10, 0.22, 0.16), (0.03, 0.08, 0.06))


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "discovery", 90, 0.55), ("c4_02", "discovery", "discovery_g", 100, 0.65),
                        ("c4_04", "uplift", "uplift", 108, 0.75), ("c4_07", "dark", "dark", 64, 0.55),
                        ("c4_09", "warm", "warm", 84, 0.6)])


def safe(cr, x, y, s=1.0, locked=0.0, t=0.0):
    """Bank vault safe, base at floor."""
    with xform(cr, x, y, s):
        rrect(cr, -200, -420, 400, 420, 24, fill=(0.55, 0.58, 0.62), stroke=INK, lw=6)
        circle(cr, 0, -220, 140, fill=(0.68, 0.70, 0.74), stroke=INK, w=6)
        for i in range(6):
            a = i / 6 * TAU + t * 0.2
            line(cr, 0, -220, math.cos(a) * 110, -220 + math.sin(a) * 110, 10, INK)
        circle(cr, 0, -220, 34, fill=(0.85, 0.75, 0.30), stroke=INK, w=5)
        if locked > 0:
            with group(cr, clamp(locked)):
                for k in (-1, 1):
                    pts = [(-220, -340 if k > 0 else -100), (220, -100 if k > 0 else -340)]
                    line(cr, pts[0][0], pts[0][1], pts[1][0], pts[1][1], 22, (0.45, 0.45, 0.48))
                    for j in range(9):
                        f = j / 8
                        ellipse(cr, lerp(pts[0][0], pts[1][0], f), lerp(pts[0][1], pts[1][1], f), 22, 14,
                                stroke=INK, w=5, rot=math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]))
                rrect(cr, -55, -260, 110, 90, 14, fill=YELLOW, stroke=INK, lw=5)
                arc(cr, 0, -260, 36, math.pi, TAU, 12, INK)
                circle(cr, 0, -222, 10, fill=INK)


def growth_counter(cr, T, t0, t1, v0, v1, label, y=870, title=None, sub=None, t_sub=None):
    k = ease(prog(T, t0, t1 - t0))
    v = int(v0 + (v1 - v0) * (k ** 3 if v1 / max(1, v0) > 50 else k))
    text(cr, f"${v:,}", CX, y, 120, face=FONT_TITLE, c=YELLOW, outline=(0.25, 0.18, 0.0), ow=12)
    if title:
        text(cr, title, CX, 160, 74, face=FONT_TITLE, c=WHITE, outline=INK, ow=9)
    if sub and T > (t_sub or t1):
        label_box(cr, sub, CX, y + 105, 44, c=INK, bg=WHITE, face=FONT_TITLE, bold=False, scale=K.pop(T, t_sub or t1))


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. money: a secret weapon
    t_money, t_weap = w("c4_01", "money"), w("c4_01", "secret weapon")

    @b.shot(0, "fade", 0.4)
    def weapon(cr, t, d, T):
        vgrad(cr, *MONEY_BG)
        with K.ken(cr, t, d, 1.0, 1.08, CX, 600):
            kw = prog(T, t_weap, 0.5)
            glow(cr, CX + 160, 640, 520, YELLOW, 0.15 + 0.35 * kw)
            radial_lines(cr, CX + 160, 640, T, n=26, c=YELLOW, a=0.12 * kw, w=26)
            if T > t_money - 0.2:
                for i in range(22):
                    g = rng(i)
                    y = (g.uniform(-200, 900) + (T - t_money) * g.uniform(300, 500)) % 1300 - 200
                    P2.coin(cr, g.uniform(100, 1820), y, g.uniform(18, 30), rot=T * g.uniform(2, 5))
            S.floor(cr, 900, (0.06, 0.12, 0.09), ink=(0.25, 0.4, 0.3))
            J = K.hero(cr, T, CX - 120, 900, "hold", face=1, s=1.1, ink=NIGHT_INK, fill=(0.08, 0.14, 0.11),
                       smile=0.4 + 0.5 * kw, brow=0.4 * kw)
            piggy(cr, J["hand_f"][0] + 120, J["hand_f"][1] + 70, 0.9 + 0.1 * K.pop(T, t_weap))
            if kw > 0:
                sparkles(cr, T, CX + 160, 600, 240, 160, n=8, c=YELLOW, seed=4)
        if T > t_weap:
            title_text(cr, "SECRET WEAPON", 230, 96, c=YELLOW, k=1)
    b.fx(t_money, "coins", -8)
    b.fx(t_weap, "shimmer", -6)

    # 2. compound interest = a rolling snowball
    st2 = s("c4_02") - 0.15
    t_ci = w("c4_02", "compound")

    @b.shot(st2, "slide", 0.4)
    def snowball(cr, t, d, T):
        vgrad(cr, (0.70, 0.84, 0.98), (0.92, 0.96, 1.0))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            polyline(cr, [(-400, 380), (200, 420), (1800, 960), (2400, 1000), (2400, 1500), (-400, 1500)], 6, INK,
                     closed=True, fill=WHITE)
            k = ease(prog(T, st2 + 0.4, d - 0.5))
            x = lerp(260, 1480, k)
            yb = 420 + (x - 200) * (540 / 1600)
            r_ = lerp(26, 165, k)
            ang = math.atan2(540, 1600)
            cx_ = x + math.sin(ang) * r_
            cy_ = yb - math.cos(ang) * r_
            for j in range(8):
                f = (j + 1) / 9
                circle(cr, lerp(260, x, f), 420 + (lerp(260, x, f) - 200) * (540 / 1600) - 6, lerp(8, r_ * 0.3, f),
                       fill=(0.9, 0.95, 1.0), a=0.6)
            circle(cr, cx_, cy_, r_, fill=(0.96, 0.98, 1.0), stroke=INK, w=6)
            with xform(cr, cx_, cy_, r_ / 100, T * 1.5 + k * 8):
                text(cr, "$", 0, 0, 110, face=FONT_TITLE, c=GREEN)
            K.hero(cr, T, 200 if k < 0.05 else 160, 420, "point", face=1, s=0.8, smile=0.9)
        kc = K.pop(T, t_ci)
        if kc > 0:
            label_box(cr, "COMPOUND INTEREST", 1180, 220, 72, c=WHITE, bg=GREEN, face=FONT_TITLE, bold=False, scale=kc)
            text(cr, "interest earns interest", 1180, 320, 44, face=FONT_HAND, bold=True, c=INK, a=clamp(kc))
    b.fx(st2 + 0.4, "roll", -10, dur=3.0)
    b.fx(t_ci, "ding", -8)

    # 3. $1,000 at 5% a year, never touch it
    st3 = s("c4_03") - 0.15
    t_1k, t_5, t_nev = w("c4_03", "one thousand"), w("c4_03", "five percent"), w("c4_03", "never")

    @b.shot(st3, "fade", 0.3)
    def deposit(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.room(cr, T, wall=(0.88, 0.90, 0.86), floor_c=(0.55, 0.52, 0.50), fy=900)
            safe(cr, 1300, 900, 1.15, locked=ease(prog(T, t_nev, 0.5)), t=T)
            kd = ease(prog(T, t_1k + 0.5, 1.0))
            J = K.hero(cr, T, 640, 900, "hold" if kd < 1 else "hips", face=1, s=1.05, smile=0.8)
            if kd < 1:
                bx = lerp(J["hand_f"][0] + 70, 1300, kd)
                by = lerp(J["hand_f"][1] - 20, 650, kd)
                banknote(cr, bx, by, 1.2 * (1 - 0.6 * kd), rot=0.1 + kd, label="$1,000")
            k5 = K.pop(T, t_5)
            if k5 > 0:
                label_box(cr, "+5% EVERY YEAR", 1300, 300, 60, c=WHITE, bg=GREEN, face=FONT_TITLE, bold=False, scale=k5)
            if T > t_nev:
                stamp(cr, "DON'T TOUCH!", 640, 330, T - t_nev - 0.4, 70, c=RED, rot=-0.08)
        text(cr, "$1,000", 300, 160, 90, face=FONT_TITLE, c=GREEN, outline=INK, ow=8, scale=max(0.01, K.pop(T, t_1k)))
    b.fx(t_1k, "pop", -10)
    b.fx(t_1k + 1.3, "clank", -10)
    b.fx(t_5, "ding", -10)
    b.fx(t_nev + 0.4, "slam", -8)

    # 4. after 100 years: $131,501
    st4 = s("c4_04") - 0.15

    @b.shot(st4, "zoom", 0.5)
    def y100(cr, t, d, T):
        vgrad(cr, *MONEY_BG)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.floor(cr, 700, (0.06, 0.12, 0.09), ink=(0.25, 0.4, 0.3))
            k = ease(prog(T, st4 + 0.3, 2.6))
            money_pile(cr, 1080, 700, 0.12 + 0.30 * k, seed=1)
            K.hero(cr, T, 760, 700, "point", face=1, s=0.9, ink=NIGHT_INK, fill=(0.08, 0.14, 0.11), smile=0.8)
        growth_counter(cr, T, st4 + 0.3, w("c4_04", "thirty") + 0.3, 1000, 131501, None, title="AFTER 100 YEARS",
                       sub="ABOUT $130,000")
    b.fx(st4 + 0.3, "coins", -10)
    b.fx(w("c4_04", "thirty") + 0.3, "ding", -8)

    # 5. after 200 years: $17 million
    st5 = s("c4_05") - 0.15

    @b.shot(st5, "zoom", 0.5)
    def y200(cr, t, d, T):
        vgrad(cr, *MONEY_BG)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.floor(cr, 760, (0.06, 0.12, 0.09), ink=(0.25, 0.4, 0.3))
            P.house(cr, 480, 760, 1.4, lit=1.0, c=(0.75, 0.78, 0.80))
            k = ease(prog(T, st5 + 0.2, 1.6))
            money_pile(cr, 1200, 760, 0.6 + 0.8 * k, seed=2)
            top = 760 - 330 * (0.6 + 0.8 * k)
            K.hero(cr, T, 1200, top - 18, "cheer", face=1, s=0.55, ink=NIGHT_INK, fill=(0.08, 0.14, 0.11))
        growth_counter(cr, T, st5 + 0.2, w("c4_05", "seventeen") + 0.4, 131501, 17292580, None,
                       title="AFTER 200 YEARS", sub="MORE THAN 17 MILLION", y=890)
    b.fx(st5 + 0.2, "coins", -8)
    b.fx(w("c4_05", "seventeen") + 0.4, "ding", -6)

    # 5b. after 300 years: $2.27 billion
    st6 = s("c4_05b") - 0.15

    @b.shot(st6, "zoom", 0.5)
    def y300(cr, t, d, T):
        vgrad(cr, (0.12, 0.25, 0.20), (0.03, 0.08, 0.06))
        z = lerp(0.32, 0.29, ease(t / max(d, 0.1)))
        with camera(cr, z, CX, -200):
            S.floor(cr, 760, (0.06, 0.12, 0.09), ink=(0.25, 0.4, 0.3))
            rect(cr, -2600, 760, 7000, 1400, fill=(0.06, 0.12, 0.09))
            P.skyline(cr, -1700, 760, 1800, 700, seed=12, fill=(0.20, 0.26, 0.30), lit=True, t=T)
            P.skyline(cr, 2000, 760, 1600, 600, seed=13, fill=(0.20, 0.26, 0.30), lit=True, t=T)
            k = ease(prog(T, st6 + 0.2, 1.4))
            sc = 1.6 + 2.0 * k
            money_pile(cr, CX, 760, sc, seed=3)
            top = 760 - 330 * sc
            K.hero(cr, T, CX, top - 30, "cheer", face=1, s=1.6, ink=NIGHT_INK, fill=(0.08, 0.14, 0.11))
            line(cr, CX + 90, top - 30, CX + 90, top - 420, 10, WHITE)
            polyline(cr, [(CX + 90, top - 420), (CX + 300, top - 370), (CX + 90, top - 320)], 6, INK, closed=True,
                     fill=RED)
        growth_counter(cr, T, st6 + 0.2, w("c4_05b", "two billion") + 0.3, 17292580, 2273996128, None,
                       title="AFTER 300 YEARS", sub="OVER 2 BILLION", y=880)
    b.fx(st6 + 0.2, "coins", -6)
    b.fx(w("c4_05b", "two billion") + 0.3, "boom_soft", -8)

    # 6. after 1,000 years: more than all the money in the world (on paper)
    st7 = s("c4_06") - 0.15
    t_pap, t_world = w("c4_06", "on paper"), w("c4_06", "entire world")
    big = "$1,546,318,920,731,927,238,984,568"

    @b.shot(st7, "fade", 0.3)
    def y1000(cr, t, d, T):
        vgrad(cr, (0.06, 0.07, 0.14), (0.02, 0.02, 0.05))
        stars(cr, T, n=160, alpha=0.6)
        title_text(cr, "AFTER 1,000 YEARS?", 170, 80, c=WHITE, k=eout(prog(t, 0.0, 0.3)))
        tw = text_w(cr, big, FONT_TITLE, 150)
        x = lerp(W + 50, W - tw - 120, ease(prog(T, st7 + 0.3, 3.6)))
        rect(cr, -10, 360, W + 20, 220, fill=(0.98, 0.96, 0.88))
        line(cr, -10, 360, W + 10, 360, 5, INK)
        line(cr, -10, 580, W + 10, 580, 5, INK)
        text(cr, big, x, 470, 150, face=FONT_TITLE, c=GREEN, align="left", outline=INK, ow=6)
        kp = K.pop(T, t_pap)
        if kp > 0:
            label_box(cr, "ON PAPER", 260, 330, 50, c=WHITE, bg=RED, face=FONT_TITLE, bold=False, scale=kp, r=8)
        text(cr, "(about $1.5 septillion)", CX, 640, 44, face=FONT_HAND, bold=True, c=(0.8, 0.85, 0.95),
             a=eout(prog(T, t_pap + 0.5, 0.4)))
        kw = K.pop(T, t_world)
        if kw > 0:
            P.globe(cr, 520, 860, 120 * max(0.01, kw), T)
            text(cr, "MORE THAN ALL", 1180, 820, 70, face=FONT_TITLE, c=YELLOW, a=clamp(kw))
            text(cr, "THE MONEY ON EARTH", 1180, 910, 70, face=FONT_TITLE, c=YELLOW, a=clamp(kw))
    b.fx(st7 + 0.3, "data", -12, dur=3.0)
    b.fx(t_pap, "pop", -10)
    b.fx(t_world, "swell", -8, dur=2.0)

    # 7. reality: banks collapse, currencies disappear
    st8 = s("c4_07") - 0.15
    t_bank, t_cur, t_wars = w("c4_07", "banks collapse"), w("c4_07", "currencies"), w("c4_07", "wars")

    @b.shot(st8, "fade", 0.3)
    def reality(cr, t, d, T):
        vgrad(cr, (0.70, 0.72, 0.78), (0.88, 0.88, 0.90))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.floor(cr, 900, (0.60, 0.60, 0.62))
            bank(cr, 620, 900, 1.0, crack=ease(prog(T, t_bank + 0.2, 1.0)), t=T)
            kc = prog(T, t_cur, 1.4)
            for i in range(6):
                g = rng(i + 20)
                bx = 1200 + (i % 3) * 230
                by = 420 + (i // 3) * 200 + 15 * math.sin(T * 2 + i)
                fade = clamp(kc * 1.5 - g.random() * 0.5)
                banknote(cr, bx, by, 1.0, rot=g.uniform(-0.3, 0.3), a=1 - fade,
                         c=[(0.55, 0.78, 0.50), (0.85, 0.70, 0.55), (0.65, 0.65, 0.90)][i % 3],
                         label=["$", "£", "¥", "€", "₣", "₤"][i])
                if 0 < fade < 1:
                    for j in range(6):
                        circle(cr, bx + g.uniform(-90, 90), by - 80 * fade - g.uniform(0, 60), 5, fill=GRAY, a=1 - fade)
        title_text(cr, "BUT REALITY GETS IN THE WAY", 150, 64, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
        if T > t_bank:
            label_box(cr, "BANKS COLLAPSE", 620, 990, 46, c=RED, scale=K.pop(T, t_bank))
        if T > t_cur:
            label_box(cr, "CURRENCIES DISAPPEAR", 1430, 990, 46, c=RED, scale=K.pop(T, t_cur))
    b.fx(t_bank + 0.2, "crash", -6)
    b.fx(t_cur, "dissolve", -8)

    # 7b. wars, inflation, taxes eat into everything
    t_inf, t_tax = w("c4_07", "inflation"), w("c4_07", "taxes")

    @b.shot(t_wars - 0.15, "fade", 0.3)
    def eaten(cr, t, d, T):
        fill_bg(cr, (0.95, 0.92, 0.85))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.floor(cr, 880, (0.75, 0.70, 0.62))
            bites = [(t_wars, "WARS", 560, 700, 0.0, RED), (t_inf, "INFLATION", CX, 340, math.pi / 2, ORANGE),
                     (t_tax, "TAXES", 1360, 700, -1, PURPLE)]
            money_pile(cr, CX, 880, 1.0, seed=5)
            for i, (tt, lab, x, y, rot, c) in enumerate(bites):
                if T > tt + 0.3:
                    bx, by = [(CX - 210, 790), (CX, 590), (CX + 210, 790)][i]
                    circle(cr, bx, by, 62, fill=(0.95, 0.92, 0.85))
            for i, (tt, lab, x, y, rot, c) in enumerate(bites):
                k = K.pop(T, tt)
                if k <= 0:
                    continue
                ch = abs(math.sin((T - tt) * 9)) if T - tt < 1.2 else 0.2
                kk = max(0.01, k)
                with xform(cr, x, y, kk, 0 if rot < 0 else rot, sx=-kk if rot < 0 else None, sy=kk if rot < 0 else None):
                    cr.new_path()
                    cr.move_to(0, 0)
                    cr.arc(0, 0, 100, 0.25 + 0.5 * ch, TAU - 0.25 - 0.5 * ch)
                    cr.close_path()
                    src(cr, c)
                    cr.fill_preserve()
                    src(cr, INK)
                    cr.set_line_width(6)
                    cr.stroke()
                    circle(cr, 10, -55, 12, fill=INK)
                lx, ly = [(560, 880), (CX, 180), (1360, 880)][i]
                text(cr, lab, lx, ly + 20, 56, face=FONT_TITLE, c=c, outline=INK, ow=5, scale=max(0.01, k))
    for tt in (t_wars, t_inf, t_tax):
        b.fx(tt, "bonk", -10)

    # 8. very few banks or currencies survive a few centuries
    st9 = s("c4_08") - 0.15
    stones = [("LIRA", "1861-2002"), ("DRACHMA", "1832-2002"), ("FRANC", "1795-2002"), ("MARK", "1948-2002"),
              ("PESETA", "1868-2002")]

    @b.shot(st9, "fade", 0.3)
    def graveyard(cr, t, d, T):
        vgrad(cr, (0.30, 0.32, 0.45), (0.12, 0.13, 0.20))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 640):
            glow(cr, 1600, 220, 200, (0.9, 0.9, 1.0), 0.3)
            circle(cr, 1600, 220, 60, fill=(0.92, 0.93, 0.98))
            S.floor(cr, 880, (0.18, 0.22, 0.20), ink=(0.35, 0.4, 0.4))
            for i, (nm, yrs) in enumerate(stones):
                k = K.pop(T, st9 + 0.3 + i * 0.35)
                if k > 0:
                    with xform(cr, 300 + i * 330, 900, max(0.01, k)):
                        gravestone(cr, 0, 0, 1.25, nm, yrs, c=(0.65, 0.66, 0.70))
        title_text(cr, "MONEY DOESN'T LAST FOREVER", 150, 62, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
        text(cr, "(all replaced by the euro)", CX, 1010, 40, face=FONT_HAND, bold=True, c=(0.85, 0.85, 0.95),
             a=eout(prog(T, st9 + 2.2, 0.4)))
    for i in range(5):
        b.fx(st9 + 0.3 + i * 0.35, "thud", -14)

    # 9. not a magic bank account: patience
    st10 = s("c4_09") - 0.15
    t_mag, t_pat = w("c4_09", "magic"), w("c4_09", "patience")

    @b.shot(st10, "fade", 0.3)
    def patience(cr, t, d, T):
        kp = ease(prog(T, t_pat - 0.2, 0.6))
        vgrad(cr, lerpc((0.25, 0.20, 0.40), (1.0, 0.90, 0.70), kp), lerpc((0.10, 0.08, 0.18), (0.98, 0.80, 0.60), kp))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            if kp < 1:
                with group(cr, 1 - kp):
                    with xform(cr, CX, 520, 1.0, -0.08 + 0.03 * math.sin(T * 2)):
                        rrect(cr, -300, -180, 600, 360, 30, fill=GOLD, stroke=INK, lw=6)
                        rect(cr, -300, -110, 600, 60, fill=INK)
                        rrect(cr, -240, 0, 120, 80, 10, fill=(0.85, 0.7, 0.3), stroke=INK, lw=4)
                        text(cr, "MAGIC BANK", 80, 90, 44, face=FONT_TITLE, c=INK)
                    sparkles(cr, T, CX, 520, 380, 240, n=10, c=WHITE, seed=6)
                    xmark(cr, CX, 520, 260, prog(T, t_mag + 0.7, 0.4))
            if kp > 0:
                with group(cr, kp):
                    S.floor(cr, 880, (0.75, 0.62, 0.45))
                    glow(cr, CX, 600, 400, YELLOW, 0.35)
                    p = sm.pose("sit", x=CX, fo=0.0, a1f=40, a2f=60, a1b=-40, a2b=-60, smile=0.6, l1f=80, l2f=-150,
                                l1b=-80, l2b=150, blink=1.0)
                    p["y"] = 820 - 6 * math.sin(T * 1.5)
                    sm.draw(cr, p, acc=HERO)
                    P2.hourglass(cr, CX + 330, 790, 0.5, p=prog(T, t_pat, 4.0), t=T)
                    P2.hourglass(cr, CX - 330, 790, 0.5, p=prog(T, t_pat, 4.0), t=T)
        if T > t_pat:
            title_text(cr, "PATIENCE", 230, 120, c=YELLOW, k=K.pop(T, t_pat))
    b.fx(t_mag + 0.7, "scratch_out", -10)
    b.fx(t_pat, "chime", -8)

    # 10. everyone else: next year. you: the next hundred
    st11 = s("c4_10") - 0.15
    t_you = w("c4_10", "you can")

    def others(cr, cx, T):
        S.floor(cr, 900, (0.80, 0.78, 0.74))
        for i, (dx, acc) in enumerate(((-260, ("cap",)), (0, ("ponytail",)), (260, ("glasses",)))):
            J = K.person(cr, T, cx + dx, 900, "think", face=1, s=0.8, acc=acc, seed=i)
            thought_bubble(cr, cx + dx + 40, 360, 200, 130, J["head"][0], J["head"][1] - 50, t=T)
            text(cr, "NEXT", cx + dx + 40, 340, 30, face=FONT_TITLE, c=GRAY)
            text(cr, "YEAR", cx + dx + 40, 378, 30, face=FONT_TITLE, c=GRAY)

    def hundred(cr, cx, T):
        S.floor(cr, 900, (0.30, 0.40, 0.30), ink=(0.5, 0.6, 0.5))
        J = K.hero(cr, T, cx - 260, 900, "point", face=1, s=0.85, ink=WHITE, fill=(0.12, 0.2, 0.15), smile=0.8)
        k = ease(prog(T, t_you + 0.2, 1.8))
        partial_line(cr, cx - 160, 520, cx + 420, 520, k, 10, YELLOW)
        for i in range(6):
            x = cx - 160 + i * 116
            if k > i / 5 - 0.01:
                line(cr, x, 500, x, 540, 6, YELLOW)
                text(cr, f"+{i * 20}", x, 580, 26, face=FONT_BOLD, c=WHITE)
                P.tree(cr, x, 490, 0.12 + 0.1 * i, T)
        del J

    b.add(st11, K.split(dict(title="EVERYONE ELSE: NEXT YEAR", bg=(0.95, 0.93, 0.88), draw=others),
                        dict(title="YOU: THE NEXT 100 YEARS", bg=(0.12, 0.25, 0.18), draw=hundred), t_you), "fade", 0.3)
    b.fx(t_you, "whoosh", -10)

    # 11. invest in forests, research, people
    st12 = s("c4_11") - 0.15

    def ic_forest(cr, T):
        for i, (x, sc) in enumerate(((-90, 0.42), (0, 0.55), (90, 0.42))):
            P.tree(cr, x, 110, sc, T + i)

    def ic_research(cr, T):
        P.flask(cr, -50, 110, 0.9, c=GREEN, t=T)
        P.atom(cr, 60, -40, 0.7, t=T)

    def ic_people(cr, T):
        p = sm.on_ground(sm.pose("point", x=-70, s=0.5, smile=0.7), 110)
        sm.draw(cr, p, acc=HERO)
        for i, x in enumerate((30, 90)):
            p = sm.on_ground(sm.pose("point_up", x=x, s=0.32, face=-1, smile=0.9), 110)
            sm.draw(cr, p, acc=[("cap",), ("ponytail",)][i])

    def bg12(cr, T):
        vgrad(cr, (0.88, 0.96, 0.86), (0.75, 0.88, 0.72))

    b.add(st12, K.icons("INVEST FOR GENERATIONS", [(ic_forest, "FORESTS", w("c4_11", "forests")),
                                                   (ic_research, "RESEARCH", w("c4_11", "research")),
                                                   (ic_people, "PEOPLE", w("c4_11", "people"))],
                        bg=bg12, y=560, size=1.3, label_size=54), "fade", 0.3)
    for wd in ("forests", "research", "people"):
        b.fx(w("c4_11", wd), "pop", -8)
    return b.result()
