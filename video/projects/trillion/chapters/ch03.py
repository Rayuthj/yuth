"""Trillion - Chapter 3: The Ultimate Shopping Spree (1:40-2:40)."""
from video.projects.trillion.chapters._m import *  # noqa: F401,F403

CONTINENTS = [
    ("N. AMERICA", [(260, 300), (420, 230), (600, 260), (560, 420), (450, 520), (330, 440)], (430, 370)),
    ("S. AMERICA", [(520, 560), (640, 600), (620, 760), (560, 880), (510, 760)], (570, 690)),
    ("EUROPE", [(860, 270), (1000, 250), (1040, 340), (920, 380), (860, 340)], (950, 310)),
    ("AFRICA", [(900, 430), (1060, 420), (1120, 560), (1030, 760), (960, 640), (890, 520)], (1000, 560)),
    ("ASIA", [(1080, 240), (1450, 220), (1620, 320), (1480, 480), (1250, 470), (1090, 380)], (1320, 340)),
    ("AUSTRALIA", [(1440, 680), (1590, 660), (1640, 760), (1520, 820), (1430, 770)], (1530, 740)),
    ("ANTARCTICA", [(500, 980), (900, 950), (1400, 960), (1500, 1010), (500, 1020)], (960, 975)),
]


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 112, 0.75), ("c3_05", "discovery", "discovery", 100, 0.65),
                        ("c3_09", "reflective", "reflective", 76, 0.55)])


def blob(cr, pts, fill, stroke=INK, dy=0):
    """Smooth closed shape (Chaikin smoothing)."""
    out = [(x, y + dy) for x, y in pts]
    for _ in range(3):
        nxt = []
        for i in range(len(out)):
            a, b_ = out[i], out[(i + 1) % len(out)]
            nxt.append((0.75 * a[0] + 0.25 * b_[0], 0.75 * a[1] + 0.25 * b_[1]))
            nxt.append((0.25 * a[0] + 0.75 * b_[0], 0.25 * a[1] + 0.75 * b_[1]))
        out = nxt
    polyline(cr, out, 4, stroke, closed=True, fill=fill)


def build(tl):
    b = Builder(tl)
    s, e, w = timing(tl)

    # 1. so, you go shopping
    @b.shot(0, "fade", 0.3)
    def go_shop(cr, t, d, T):
        with K.ken(cr, t, d, 1.12, 1.18, 900, 700):
            S.city(cr, T, T * 60, gy=900)
            for i, (lab, c) in enumerate((("YACHTS", BLUE), ("JETS", RED), ("ISLANDS", GREEN), ("CASTLES", PURPLE))):
                P.shop(cr, 260 + i * 470 - (T * 60) % 470 + 235, 900, 1.25, sign=lab, lit=0.4, awn=c)
            J = dude(cr, T, lerp(380, 900, ease(prog(t, 0.0, 1.8))), 905, "point_up", s=1.1, walk=0.9 if t < 1.8 else 0,
                     smile=1.0, brow=0.4, over=shades, a1f=140, a2f=10)
            gold_card(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 50, 0.55, rot=-0.3)
            star_shape(cr, J["hand_f"][0] + 40, J["hand_f"][1] - 90, 10 + 14 * abs(math.sin(T * 4)), points=4,
                       inner=0.3, fill=WHITE)
            for k_, x_ in enumerate((-60, 70)):
                shopping_bag(cr, J["hand_b"][0] + x_ * 0.2, J["hand_b"][1] + 110, 0.6,
                             c=[(0.9, 0.3, 0.45), (0.3, 0.5, 0.9)][k_])
    b.fx(0.2, "footsteps", -14, dur=1.8)
    b.fx(0.9, "sparkle", -12)

    # 2a. a mansion on every continent
    st2 = s("c3_02") - 0.15
    t_fleet, t_yacht, t_small = w("c3_02", "fleet"), w("c3_02", "yacht"), w("c3_02", "smaller")
    t_cont = w("c3_02", "continent")

    @b.shot(st2, "fade", 0.3)
    def mansions(cr, t, d, T):
        fill_bg(cr, (0.62, 0.82, 0.95))
        for i in range(12):
            arc(cr, (i * 173) % W, 100 + (i * 97) % 900, 18, math.pi * 1.15, math.pi * 1.85, 3, WHITE, 0.5)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            for i, (lab, pts, (mx, my)) in enumerate(CONTINENTS):
                blob(cr, pts, (0.62, 0.80, 0.50) if lab != "ANTARCTICA" else (0.96, 0.97, 1.0), dy=50)
            for i, (lab, pts, (mx, my)) in enumerate(CONTINENTS):
                my += 50 if lab != "ANTARCTICA" else 30
                k = K.pop(T, st2 + 0.3 + i * (t_cont - st2 - 0.1) / 7)
                if k <= 0:
                    continue
                with xform(cr, mx, my + 30, max(0.01, k)):
                    mansion(cr, 0, 0, 0.17)
                if lab == "ANTARCTICA":
                    P.penguin(cr, mx + 110, my + 30, 0.35, T)
                text(cr, lab, mx, my + 58, 24, face=FONT_BOLD, a=clamp(k))
        text(cr, "A MANSION ON EVERY CONTINENT", CX, 205, 60, face=FONT_TITLE, c=WHITE, outline=INK, ow=10,
             a=eout(prog(t, 0.2, 0.4)))
    for i in range(7):
        b.fx(st2 + 0.3 + i * (t_cont - st2 - 0.1) / 7, "pop", -14)

    # 2b. a fleet of private jets
    @b.shot(t_fleet - 0.25, "wipe", 0.35)
    def jets(cr, t, d, T):
        vgrad(cr, (0.45, 0.70, 0.98), (0.85, 0.93, 0.99))
        for i in range(6):
            P.cloud(cr, (i * 380 - T * 300) % (W + 600) - 300, 700 + (i % 3) * 110, 1.0, a=0.9)
        for i, (dx, dy) in enumerate(((0, 0), (-260, -110), (-260, 110), (-520, -220), (-520, 220))):
            x = lerp(-300, 1500, ease(prog(t, 0.0, d))) + dx
            jet(cr, x, 470 + dy + 8 * math.sin(T * 3 + i), 0.55, face=1, accent=GOLD)
        text(cr, "A FLEET OF PRIVATE JETS", CX, 150, 64, face=FONT_TITLE, c=WHITE, outline=INK, ow=10)
    b.fx(t_fleet - 0.25, "whoosh", -6)

    # 2c. a yacht with its own smaller yacht inside
    @b.shot(t_yacht - 0.25, "wipe", 0.35)
    def yachts(cr, t, d, T):
        vgrad(cr, (0.98, 0.84, 0.62), (0.80, 0.90, 0.98))
        P.sun(cr, 1600, 200, 70, T)
        with K.ken(cr, t, d, 1.0, 1.08, 900, 640):
            waves(cr, T, 760)
            yacht(cr, 1150, 770, 1.15, T, mini=prog(T, t_small - 0.2, 1.8))
            if T > t_small + 0.6:
                label_box(cr, "MINI YACHT", 330, 560, 40, c=INK, bg=YELLOW, face=FONT_TITLE, bold=False,
                          scale=K.pop(T, t_small + 0.6))
                arrow(cr, 330, 600, 330, 690, 6, INK, head=20)
        text(cr, "A YACHT... WITH A YACHT INSIDE", CX, 150, 64, face=FONT_TITLE, c=WHITE, outline=INK, ow=10)
    b.fx(t_yacht - 0.25, "swoosh", -8)
    b.fx(t_small, "clank", -10)
    b.fx(t_small + 0.6, "boing", -10)

    # 2d. golden toilets, diamond phone cases, a pool shaped like your face
    st2b = s("c3_02b") - 0.15
    items = [(toilet, "GOLDEN TOILET", w("c3_02b", "golden")),
             (diamond_phone, "DIAMOND PHONE CASE", w("c3_02b", "diamond")),
             (face_pool, "A POOL SHAPED\nLIKE YOUR FACE", w("c3_02b", "swimming"))]

    @b.shot(st2b, "fade", 0.3)
    def catalog(cr, t, d, T):
        fill_bg(cr, (0.98, 0.94, 0.86))
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.03):
            text(cr, "LUXURY CATALOG", CX, 120, 56, face=FONT_TITLE, c=GOLD_D, a=eout(prog(t, 0.05, 0.4)))
            for i, (fn, lab, ta) in enumerate(items):
                k = K.pop(T, ta)
                if k <= 0:
                    continue
                x = 400 + i * 560
                with xform(cr, x, 560, max(0.01, k)):
                    rrect(cr, -240, -330, 480, 640, 24, fill=WHITE, stroke=GOLD_D, lw=8)
                    if fn is toilet:
                        toilet(cr, 20, 120, 0.95, t=T)
                    elif fn is diamond_phone:
                        diamond_phone(cr, 0, -20, 1.0, T)
                    else:
                        face_pool(cr, 0, -30, 0.85, T)
                    rows = lab.split("\n")
                    for r, row in enumerate(rows):
                        text(cr, row, 0, 220 + r * 46 - (len(rows) - 1) * 23, 38, face=FONT_TITLE)
                stamp(cr, "SOLD", x + 140, 300, T - ta - 0.5, 50, c=RED, rot=0.15)
    for (_, _, ta) in items:
        b.fx(ta, "pop", -8)
        b.fx(ta + 0.5, "stamp", -12)

    # 3. a tropical island, a castle in the mountains, a football team "just because"
    st3 = s("c3_03") - 0.15
    t_isl, t_cas, t_team, t_just = (w("c3_03", "tropical"), w("c3_03", "castle"), w("c3_03", "football"),
                                    w("c3_03", "just because"))

    def p_island(cr, T):
        vgrad(cr, (0.98, 0.82, 0.60), (0.75, 0.88, 0.98))
        waves(cr, T, 430, x0=-10, x1=540)
        island(cr, 260, 440, 0.8, T)

    def p_castle(cr, T):
        vgrad(cr, (0.62, 0.80, 0.98), (0.88, 0.94, 0.99))
        polyline(cr, [(-40, 620), (150, 300), (260, 420), (400, 240), (600, 620)], 5, INK, closed=True,
                 fill=(0.55, 0.55, 0.62))
        polyline(cr, [(360, 300), (400, 240), (440, 300), (420, 290), (400, 310), (380, 290)], 3, INK, closed=True,
                 fill=WHITE)
        S.castle(cr, 400, 330, 0.28, t=T)
        P.cloud(cr, 130, 160, 0.6)

    def p_team(cr, T):
        vgrad(cr, (0.55, 0.78, 0.98), (0.85, 0.93, 0.99))
        rect(cr, 0, 420, 520, 200, fill=(0.40, 0.72, 0.38))
        line(cr, 0, 420, 520, 420, 4, INK)
        for i, dx in enumerate((90, 200, 320, 430)):
            dude(cr, T, dx, 470, "cheer", s=0.55, acc=[("cap",), ("bun",), (), ("glasses",)][i], seed=i, smile=1,
                 under=jersey(RED, 4 + i))
        stadium_ball(cr, 260, 530 - abs(math.sin(T * 5)) * 50, 26, T * 4)

    paths_fn = K.three_paths([("TROPICAL ISLAND", BLUE, p_island, t_isl), ("MOUNTAIN CASTLE", PURPLE, p_castle, t_cas),
                              ("FOOTBALL TEAM", RED, p_team, t_team)], bg=(0.97, 0.95, 0.90))

    def places(cr, t, d, T):
        paths_fn(cr, t, d, T)
        kj = K.pop(T, t_just)
        if kj > 0:
            with xform(cr, CX, 140, max(0.01, kj), -0.04):
                rrect(cr, -260, -50, 520, 100, 20, fill=YELLOW, stroke=INK, lw=6)
                text(cr, "...JUST BECAUSE", 0, 0, 52, face=FONT_TITLE)

    b.add(st3, places, "fade", 0.3)
    for ta in (t_isl, t_cas, t_team):
        b.fx(ta, "pop", -8)
    b.fx(t_team + 0.3, "cheer", -14, dur=1.5)
    b.fx(t_just, "boing", -8)

    # 4. "I'll take one of everything. Actually, make it two."
    st4 = s("c3_04") - 0.15
    t_two = w("c3_04", "make it two")

    def store(cr, T):
        S.room(cr, T, wall=(0.20, 0.18, 0.22), floor_c=(0.85, 0.78, 0.62), fy=900)
        for i in range(5):
            x = 200 + i * 380
            glow(cr, x, 120, 260, (1.0, 0.9, 0.6), 0.25)
            line(cr, x, 0, x, 80, 3, (0.5, 0.5, 0.5))
            ellipse(cr, x, 92, 40, 14, fill=(1.0, 0.92, 0.6))
        for r in range(2):
            rect(cr, 60, 330 + r * 190, 1800, 16, fill=GOLD, stroke=INK, lw=3)
        g = rng(5)
        for r in range(2):
            x = 120
            while x < 1800:
                kind = g.randrange(4)
                yb = 330 + r * 190
                if kind == 0:
                    for j in range(3):
                        polyline(cr, [(x - 30, yb - j * 22), (x + 30, yb - j * 22), (x + 22, yb - 22 - j * 22),
                                      (x - 22, yb - 22 - j * 22)], 3, GOLD_D, closed=True, fill=GOLD)
                elif kind == 1:
                    diamond(cr, x, yb - 40, 30)
                elif kind == 2:
                    circle(cr, x, yb - 45, 30, fill=WHITE, stroke=GOLD_D, w=8)
                    line(cr, x, yb - 45, x + 12, yb - 55, 3, INK)
                else:
                    P.car(cr, x, yb - 4, 0.35, c=RED)
                x += g.uniform(120, 200)
        # the counter and a very surprised shop assistant
        rect(cr, 1080, 700, 760, 200, fill=(0.35, 0.22, 0.15), stroke=INK, lw=6)
        rect(cr, 1060, 680, 800, 30, fill=GOLD, stroke=INK, lw=5)
        sup = T > t_two
        dude(cr, T, 1460, 900, "surprised" if sup else "stand", face=-1, s=1.0, acc=("bowtie", "glasses"),
             smile=0.5 if not sup else 0.0, eye=1.4 if sup else 1.0)
        rect(cr, 1080, 700, 760, 200, fill=(0.35, 0.22, 0.15), stroke=INK, lw=6)
        rect(cr, 1060, 680, 800, 30, fill=GOLD, stroke=INK, lw=5)
        if sup:
            text(cr, "×2", 1640, 520, 120, face=FONT_TITLE, c=GOLD, outline=INK, ow=8, scale=K.pop(T, t_two),
                 rot=0.1)

    b.add(st4, K.dialogue(tl, store, [dict(x=760, gy=900, acc=HERO, face=1, g="point", talk_g="present",
                                           kw=dict(smile=0.9, brow=0.3))],
                          [(0, "I'll take one of everything. Actually, make it two.", "c3_04", (720, 330))],
                          zoom=(1.0, 1.05), focus=(CX, 560)), "fade", 0.3)
    b.fx(st4, "ding", -12)
    b.fx(t_two, "boing", -8)

    # 5. a whole year of crazy spending: a few billion dollars
    st5 = s("c3_05") - 0.15
    t_few = w("c3_05", "few billion")
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    @b.shot(st5, "fade", 0.3)
    def year(cr, t, d, T):
        k = prog(T, st5 + 0.2, max(0.5, t_few - st5 - 0.4))
        with K.ken(cr, t, d, 1.15, 1.22, CX, 720):
            S.room(cr, T, wall=(0.93, 0.88, 0.80), floor_c=(0.70, 0.55, 0.42), fy=900)
            g = rng(8)
            n = int(30 * k)
            for i in range(n):
                x, sz = g.uniform(250, 1700), g.uniform(1.0, 1.5)
                kind = i % 4
                if kind == 0:
                    shopping_bag(cr, x, 905, 0.9 * sz, c=g.choice([RED, BLUE, PURPLE, ORANGE]))
                elif kind == 1:
                    rect(cr, x - 60 * sz, 905 - 100 * sz, 120 * sz, 100 * sz, fill=g.choice([YELLOW, CYAN, PURPLE]),
                         stroke=INK, lw=4)
                    line(cr, x, 905 - 100 * sz, x, 905, 6, RED)
                elif kind == 2:
                    P.car(cr, x, 905, 0.6 * sz, c=g.choice([RED, BLUE, GOLD]))
                else:
                    toilet(cr, x, 905, 0.35 * sz, t=T)
            dude(cr, T, CX, 905, "cheer" if k < 1 else "shrug", s=1.0, smile=0.9, over=shades)
            calendar(cr, 420, 440, 0.8, "YEAR 1", months[min(11, int(k * 12))], c=RED)
        rrect(cr, 1240, 60, 620, 150, 20, fill=WHITE, stroke=INK, lw=5)
        text(cr, "SPENT SO FAR", 1550, 100, 32, face=FONT_BOLD, c=GRAY)
        if k < 1:
            g2 = rng(int(T * 20))
            digits = "".join(str(g2.randrange(10)) for _ in range(3))
            text(cr, f"${max(1, int(k * 9))},{digits},000,000", 1550, 160, 50, face=FONT_TITLE, c=RED)
        else:
            text(cr, "A FEW BILLION", 1550, 160, 54, face=FONT_TITLE, c=RED, scale=K.pop(T, t_few))
    b.fx(st5 + 0.2, "fastforward", -10, dur=2.5)
    b.fx(t_few, "coins", -8)

    # 6. check your balance: it has barely moved
    st6 = s("c3_06") - 0.15
    t_bar = w("c3_06", "barely")

    @b.shot(st6, "fade", 0.3)
    def balance(cr, t, d, T):
        vgrad(cr, (0.18, 0.20, 0.30), (0.06, 0.06, 0.10))
        glow(cr, 1250, 640, 700, (0.55, 0.75, 1.0), 0.25)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            p = sm.pose("front", s=3.3, lw=5.5, fo=0.25, face=1, gx=0.9, gy=0.1, smile=-0.1, brow=-0.3, eye=0.9,
                        browy=0.0)
            p = head_at(sm.idle(p, T, 2, 0.4), 430, 640)
            cr.save()
            cr.rectangle(0, 0, 900, 812)
            cr.clip()
            sm.draw(cr, p, acc=HERO)
            cr.restore()
            cr.new_path()
            big_phone(cr, 1250, 690, 1.0, rot=0.05, screen=bank_screen("≈ $1 TRILLION", sub="Balance", bar=0.997))
            for k_ in (-1, 1):
                circle(cr, 1250 + k_ * 195, 830, 34, fill=WHITE, stroke=INK, w=7)
        if T > t_bar:
            k = K.pop(T, t_bar)
            with xform(cr, 1250, 220, max(0.01, k)):
                rrect(cr, -380, -70, 760, 140, 24, fill=YELLOW, stroke=INK, lw=6)
                text(cr, "BARELY MOVED", 0, 0, 72, face=FONT_TITLE)
        vignette(cr, 0.35)
    b.fx(st6, "blip", -10)
    b.fx(t_bar, "boing", -10)

    # 7. invested at 4%: about $110 million every single day
    st7 = s("c3_07") - 0.15
    t_inv, t_four, t_110 = w("c3_07", "invested"), w("c3_07", "four percent"), w("c3_07", "hundred and ten")

    def money_tree(cr, x, y, s_, T, k):
        with xform(cr, x, y, s_):
            polyline(cr, [(-30, 0), (-18, -220), (18, -220), (30, 0)], 5, INK, closed=True, fill=(0.55, 0.38, 0.22))
            for (bx, by, r_) in ((0, -330, 150), (-120, -260, 100), (120, -260, 100), (0, -200, 90)):
                circle(cr, bx, by, r_, fill=(0.35, 0.68, 0.35), stroke=INK, w=5)
            g = rng(3)
            n = int(4 + 18 * k)
            for i in range(n):
                bx, by = g.uniform(-170, 170), g.uniform(-420, -190)
                kk = K.pop(T, st7 + 0.3 + i * 0.3)
                if kk > 0:
                    bill(cr, bx, by, 0.32 * max(0.01, kk), g.uniform(-0.6, 0.6))

    @b.shot(st7, "fade", 0.3)
    def interest(cr, t, d, T):
        fill_bg(cr, (0.96, 0.95, 0.90))
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.03):
            S.floor(cr, 920, (0.80, 0.85, 0.70))
            money_tree(cr, 380, 920, 1.25, T, prog(T, st7, d))
            text(cr, "INVESTED", 380, 980, 44, face=FONT_TITLE, c=CASH_D)
            k1 = eout(prog(T, t_inv, 0.4))
            text(cr, "≈ $1,000,000,000,000", 1240, 220, 64, face=FONT_TITLE, a=k1)
            k2 = eout(prog(T, t_four, 0.4))
            text(cr, "× 4% A YEAR", 1240, 330, 64, face=FONT_TITLE, c=BLUE, a=k2)
            if k2 > 0:
                partial_line(cr, 900, 400, 1580, 400, ease(prog(T, t_four + 0.4, 0.4)), 6, INK)
            k3 = eout(prog(T, t_four + 0.9, 0.4))
            text(cr, "≈ $40 BILLION A YEAR", 1240, 470, 64, face=FONT_TITLE, c=CASH_D, a=k3)
            k4 = eout(prog(T, t_110 - 0.9, 0.4))
            text(cr, "÷ 365 DAYS", 1240, 580, 56, face=FONT_TITLE, c=GRAY, a=k4)
            k5 = K.pop(T, t_110)
            if k5 > 0:
                with xform(cr, 1240, 760, max(0.01, k5)):
                    rrect(cr, -560, -110, 1120, 220, 30, fill=CASH_D, stroke=INK, lw=6)
                    text(cr, "≈ $110 MILLION", 0, -30, 84, face=FONT_TITLE, c=WHITE)
                    text(cr, "EVERY SINGLE DAY", 0, 60, 44, face=FONT_TITLE, c=MONEY_G)
    b.fx(t_inv, "pop", -10)
    b.fx(t_four, "pop", -10)
    b.fx(t_four + 0.9, "ding", -10)
    b.fx(t_110, "success", -6)
    for i in range(0, 18, 3):
        b.fx(st7 + 0.3 + i * 0.3, "blip", -18)

    # 8a. you can't spend it faster than it grows
    st8 = s("c3_08") - 0.15
    t_mult = w("c3_08", "keeps multiplying")

    @b.shot(st8, "fade", 0.3)
    def tank(cr, t, d, T):
        fill_bg(cr, (0.95, 0.95, 0.92))
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.floor(cr, 920, (0.78, 0.78, 0.76))
            lvl = lerp(0.55, 0.85, ease(prog(t, 0.0, d)))
            rect(cr, 640, 360, 640, 560, fill=WHITE, stroke=INK, lw=8)
            cr.save()
            cr.rectangle(640, 360, 640, 560)
            cr.clip()
            yl = 920 - 560 * lvl
            rect(cr, 640, yl, 640, 600, fill=CASH)
            g = rng(4)
            for i in range(40):
                bx, by = g.uniform(660, 1260), g.uniform(yl + 10, 900)
                bill(cr, bx + 6 * math.sin(T * 2 + i), by, 0.3, g.uniform(-1, 1))
            cr.restore()
            cr.new_path()
            text(cr, "YOUR FORTUNE", 960, 320, 48, face=FONT_TITLE)
            # the inflow pipe
            rect(cr, 1240, 180, 420, 70, fill=GRAY, stroke=INK, lw=6)
            rect(cr, 1180, 180, 70, 200, fill=GRAY, stroke=INK, lw=6)
            for i in range(10):
                f = (T * 2.5 + i / 10) % 1
                bill(cr, 1215 + 14 * math.sin(i * 3 + T * 4), 380 + f * (yl - 380), 0.32, f * 4 + i)
            label_box(cr, "+$110M A DAY", 1500, 140, 40, c=WHITE, bg=CASH_D, face=FONT_TITLE, bold=False)
            # the spender with a tiny bucket
            ph = (T * 1.2) % 1
            J = dude(cr, T, 500, 920, "hold", s=1.0, face=1, smile=-0.2, brow=-0.5, a1f=lerp(40, 150, math.sin(ph * math.pi)),
                     a2f=20)
            rect(cr, J["hand_f"][0] - 18, J["hand_f"][1] - 10, 36, 30, fill=LIGHT, stroke=INK, lw=3)
            label_box(cr, "SPENDING", 330, 470, 36, c=RED, bg=WHITE, face=FONT_TITLE, bold=False)
    b.fx(st8, "pour", -10, dur=3.0)

    # 8b. ...while you sleep
    @b.shot(t_mult - 0.25, "fade", 0.35)
    def sleep(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, 900, 620):
            S.dark_room(cr, T, 900, 260)
            P.window(cr, 300, 380, 300, 240, T, sky=(0.06, 0.07, 0.18), night=True)
            P.bed(cr, 860, 880, 1.3)
            p = sm.pose("stand", x=0, s=0.9, smile=0.5, blink=1.0)
            with xform(cr, 640, 740, 1, -math.pi / 2):
                sm.draw(cr, head_at(p, 0, 0), acc=HERO, ink=NIGHT_INK, fill=NIGHT_FILL)
            rrect(cr, 700, 720, 450, 60, 20, fill=(0.25, 0.30, 0.50), stroke=NIGHT_INK, lw=4)
            for i in range(3):
                f = (T * 0.6 + i / 3) % 1
                text(cr, "z", 660 + f * 120, 640 - f * 180, 40 + f * 30, face=FONT_TITLE, c=NIGHT_INK, a=1 - f)
            k = prog(T, t_mult - 0.2, 5.0)
            rows = 3 + int(5 * k)
            cash_pile(cr, 1500, 885, 0.5, rows=rows, seed=31)
            for i in range(6):
                f = (T * 1.4 + i / 6) % 1
                bill(cr, 1500 + 120 * math.sin(i * 2.1), 885 - rows * 29 - 40 - f * 120, 0.35, f * 2, a=1 - f)
        earned = int(max(0.0, T - (t_mult - 0.25)) * 110_000_000 / 86400)
        rrect(cr, 1220, 60, 640, 150, 20, fill=(0.10, 0.12, 0.16), stroke=NIGHT_INK, lw=4)
        text(cr, "EARNED WHILE YOU SLEEP", 1540, 100, 30, face=FONT_BOLD, c=NIGHT_INK)
        text(cr, f"+${earned:,}", 1540, 160, 56, face=FONT_TITLE, c=MONEY_G)
    b.fx(t_mult - 0.2, "snore", -12, dur=3.0)
    b.fx(t_mult + 0.5, "coins", -14, dur=2.0)

    # 9. after the tenth mansion, buying stops feeling exciting
    st9 = s("c3_09") - 0.15
    t_tenth = w("c3_09", "tenth")

    @b.shot(st9, "fade", 0.3)
    def tenth(cr, t, d, T):
        cam = lerp(0, 1900, ease(prog(T, st9 + 0.3, max(0.5, t_tenth + 0.4 - st9 - 0.3))))
        vgrad(cr, (0.62, 0.80, 0.98), (0.90, 0.95, 0.99))
        S.floor(cr, 900, (0.55, 0.75, 0.45))
        with xform(cr, -cam, 0):
            for i in range(10):
                x = 300 + i * 260
                mansion(cr, x, 880, 0.36, roof=[RED, BLUE, PURPLE, ORANGE, GREEN][i % 5])
                label_box(cr, f"#{i + 1}", x, 560, 34, c=INK, bg=WHITE, face=FONT_TITLE, bold=False)
        bored = clamp(prog(T, t_tenth, 0.6))
        dude(cr, T, 1500, 960, "slump" if bored > 0.5 else "stand", s=1.0, face=-1, smile=lerp(0.6, -0.3, bored),
             brow=-0.3 * bored)
        n = 1 + int(9 * clamp(cam / 1900))
        rrect(cr, 60, 60, 520, 210, 20, fill=WHITE, stroke=INK, lw=5)
        text(cr, "EXCITEMENT", 320, 100, 34, face=FONT_TITLE)
        P2.gauge(cr, 320, 240, 110, lerp(0.95, 0.08, (n - 1) / 9), t=T)
        word = ["WOW!!!", "WOW!!", "WOW!", "NICE!", "NICE", "COOL", "OK", "OK...", "SURE", "MEH."][n - 1]
        text(cr, word, 760, 160, 60, face=FONT_TITLE, c=lerpc(GREEN, GRAY, (n - 1) / 9))
        if bored > 0:
            thought_bubble(cr, 1720, 470, 260, 160, 1530, 620, scale=back(bored), t=T)
            text(cr, "meh.", 1720, 470, 54, face=FONT_HAND, bold=True, a=bored)
    b.fx(st9 + 0.3, "swoosh", -12)
    b.fx(t_tenth, "soft_x", -10)

    # 10. hedonic adaptation
    st10 = s("c3_10") - 0.15
    t_term, t_fast = w("c3_10", "hedonic"), w("c3_10", "surprisingly")
    spikes = [(0.12, 1.0, "car"), (0.36, 0.8, "yacht"), (0.58, 0.62, "mansion"), (0.78, 0.45, "jet")]

    def happy_fn(u):
        v = 0.25
        for (u0, hgt, _) in spikes:
            if u >= u0:
                v += hgt * 0.62 * math.exp(-(u - u0) * 28)
        return v

    @b.shot(st10, "fade", 0.3)
    def hedonic(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.03):
            k = K.pop(T, t_term)
            if k > 0:
                with xform(cr, CX, 170, max(0.01, k)):
                    rrect(cr, -470, -62, 940, 124, 20, fill=BLUE, stroke=INK, lw=6)
                    text(cr, "HEDONIC ADAPTATION", 0, 0, 72, face=FONT_TITLE, c=WHITE)
            x0, y0, wd, ht = 260, 900, 1400, 520
            p_ = ease(prog(T, st10 + 0.2, d - 1.0))
            line(cr, x0, y0 - ht * 0.25, x0 + wd, y0 - ht * 0.25, 3, GRAY, 0.7, dash=[14, 10])
            text(cr, "BACK TO NORMAL", x0 + wd - 10, y0 - ht * 0.25 + 30, 26, face=FONT_BOLD, c=GRAY, align="right")
            chart_line(cr, x0, y0, wd, ht, happy_fn, p=p_, c=RED, lw=8, n=240)
            text(cr, "HAPPINESS", x0 - 20, y0 - ht - 60, 32, face=FONT_TITLE, align="left")
            text(cr, "TIME →", x0 + wd, y0 + 40, 30, face=FONT_TITLE, align="right")
            for (u0, hgt, kind) in spikes:
                if p_ >= u0:
                    xx = x0 + wd * u0
                    yy = y0 - ht * (0.25 + hgt * 0.62) - 70
                    kk = K.pop(T, st10 + 0.2 + (d - 1.0) * u0 * 0.9)
                    with xform(cr, xx + 20, yy, max(0.01, kk) * 0.85):
                        if kind == "car":
                            P.car(cr, 0, 40, 0.8, c=RED)
                        elif kind == "yacht":
                            yacht(cr, 0, 30, 0.22, T)
                        elif kind == "mansion":
                            mansion(cr, 0, 50, 0.25)
                        else:
                            jet(cr, 0, 0, 0.3)
            if T > t_fast:
                label_box(cr, "WE GET USED TO IT FAST", 1240, 340, 46, c=INK, bg=YELLOW, face=FONT_TITLE, bold=False,
                          scale=K.pop(T, t_fast))
    b.fx(t_term, "ding", -8)
    for (u0, _, _) in spikes:
        b.fx(st10 + 0.2 + (tl.dur - st10 - 1.0) * u0 * 0.9, "pop", -12)
    b.fx(t_fast, "pop", -8)
    return b.result()
