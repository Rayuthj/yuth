"""King - Chapter 9: Your Legacy (7:50-9:00)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403

OLD = ("tuft", "crown", "cape", "beard")
IRON = (0.42, 0.44, 0.48)


def music_plan(tl):
    return K.music(tl, [(0.0, "wonder", "wonder", 76, 0.6), ("c9_03", "dark", "dark", 62, 0.55),
                        ("c9_04", "mystery", "mystery", 70, 0.5), ("c9_05", "uplift", "uplift", 92, 0.65),
                        ("c9_06b", "reflective", "reflective", 72, 0.6), ("c9_08", "warm", "warm", 80, 0.7)])


def version_tag(cr, n, name, col, a=1.0):
    rrect(cr, CX - 120, 60, 240, 64, 14, fill=col, stroke=INK, lw=4, a=a)
    text(cr, f"VERSION {n}", CX, 92, 36, face=FONT_TITLE, c=WHITE, a=a)
    text(cr, name, CX, 180, 70, face=FONT_TITLE, c=WHITE, a=a, outline=INK, ow=9)


def monument(cr, x, y, s=1.0, kind=0, c=GOLD):
    with xform(cr, x, y, s):
        if kind == 0:   # arch
            polyline(cr, [(-120, 0), (-120, -220), (-60, -300), (60, -300), (120, -220), (120, 0), (60, 0), (60, -180),
                          (-60, -180), (-60, 0)], 5, INK, closed=True, fill=c)
        elif kind == 1:  # obelisk
            polyline(cr, [(-50, 0), (-35, -380), (0, -430), (35, -380), (50, 0)], 5, INK, closed=True, fill=c)
        else:            # dome palace
            rect(cr, -170, -160, 340, 160, fill=c, stroke=INK, lw=5)
            cr.new_path()
            cr.arc(0, -160, 110, math.pi, 0)
            cr.close_path()
            src(cr, c)
            cr.fill_preserve()
            src(cr, INK)
            cr.set_line_width(5)
            cr.stroke()
            for i in range(4):
                rect(cr, -140 + i * 80, -130, 40, 130, fill=WHITE, stroke=INK, lw=3)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. fast-forward fifty years
    @b.shot(0, "fade", 0.3)
    def ff(cr, t, d, T):
        vgrad(cr, (0.18, 0.20, 0.35), (0.08, 0.08, 0.16))
        with K.ken(cr, t, d, 1.0, 1.06):
            k = ease(prog(T, 0.6, 2.2))
            P.clock(cr, CX, 470, 220, T * 2000, hours=int(k * 600) % 12, minutes=0, speed=4000, face=(0.95, 0.94, 0.9),
                    ink=INK)
            for i in range(10):
                a = T * 3 + i * 0.63
                r = 380 + 40 * math.sin(i)
                with xform(cr, CX + r * math.cos(a), 470 + 0.55 * r * math.sin(a), 0.5, a):
                    rect(cr, -60, -45, 120, 90, fill=WHITE, stroke=INK, lw=4)
                    text(cr, str(2030 + int(k * 50) + i), 0, 0, 30, face=FONT_TITLE)
            text(cr, f"+{int(50 * k)} YEARS", CX, 900, 100, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10)
    b.fx(0.4, "fastforward", -8)

    # 2. history books, kids reading, what will they say?
    st2 = s("c9_02") - 0.15
    t_kids, t_say = w("c9_02", "kids"), w("c9_02", "what will")

    @b.shot(st2, "fade", 0.3)
    def books(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            if T < t_kids - 0.3:
                fill_bg(cr, PAPER)
                vignette(cr, 0.18)
                P2.book_big(cr, CX, 540, 1.3, title="HISTORY")
                p = sm.pose("front", x=0, s=0.9, smile=0.6)
                with xform(cr, CX + 10, 560, 1.0):
                    circle(cr, 0, 0, 90, fill=(0.96, 0.89, 0.72), stroke=INK, w=5)
                    cr.save()
                    cr.arc(0, 0, 86, 0, TAU)
                    cr.clip()
                    sm.draw(cr, head_at(p, 0, 5), acc=("tuft", "crown"))
                    cr.restore()
                    cr.new_path()
            else:
                S.room(cr, T, wall=(0.92, 0.94, 0.86), floor_c=(0.75, 0.65, 0.50))
                P.chalkboard(cr, CX, 330, 900, 300)
                text(cr, "THE KING WHO...?", CX, 330, 70, face=FONT_HAND, bold=True, c=WHITE)
                for i, x in enumerate((420, 760, 1160, 1500)):
                    P.desk(cr, x, 900, 260)
                    p = sm.pose("sit", x=x - 40, face=1, s=0.7, a1f=60, a2f=60, smile=0.3,
                                gy=0.6 if T < t_say else -0.6)
                    p["y"] = 900 - 95
                    sm.draw(cr, sm.idle(p, T, i), acc=[("cap",), ("ponytail",), ("bun",), ("glasses",)][i])
                    rect(cr, x - 10, 860, 60, 40, fill=[RED, BLUE, GREEN, ORANGE][i], stroke=INK, lw=3)
                if T > t_say:
                    text(cr, "?", 1700, 600, 200, face=FONT_TITLE, c=RED, scale=K.pop(T, t_say))
    b.fx(st2 + 0.2, "page", -10)
    b.fx(t_say, "stinger", -10)

    # 3. version one: the iron king
    st3 = s("c9_03") - 0.15
    t_obey, t_crash = w("c9_03", "obeyed"), w("c9_03", "crashing")

    @b.shot(st3, "fade", 0.4)
    def iron(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            vgrad(cr, (0.40, 0.40, 0.45), (0.62, 0.62, 0.66))
            S.floor(cr, 880, (0.45, 0.45, 0.48))
            kc = ein(prog(T, t_crash, 0.9))
            P2.statue(cr, CX + 200 * kc, 880, 1.0, gold=False, tilt=1.5 * kc)
            if kc >= 1:
                for i in range(8):
                    g = rng(i + 4)
                    circle(cr, CX + 260 + g.uniform(-300, 300), 860 - g.uniform(0, 80) * max(0, 1 - (T - t_crash - 0.9)),
                           g.uniform(6, 20), fill=(0.6, 0.6, 0.6), a=0.7)
            for i, x in enumerate((260, 460, 1460, 1660)):
                K.person(cr, T, x, 880, "sad" if T > t_obey else "stand", face=1 if x < CX else -1, s=0.85, seed=i,
                         acc=(), smile=-0.4, ink=(0.2, 0.2, 0.25))
        version_tag(cr, 1, "THE IRON KING", IRON, a=eout(prog(t, 0.1, 0.4)))
    b.fx(t_crash, "crash", -6)
    b.fx(t_crash + 0.9, "boom_soft", -8)

    # 4. version two: the golden king
    st4 = s("c9_04") - 0.15
    t_pal, t_bri, t_mon, t_voice = (w("c9_04", "palaces"), w("c9_04", "bridges"), w("c9_04", "monuments"),
                                    w("c9_04", "voice"))

    @b.shot(st4, "fade", 0.4)
    def golden(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            vgrad(cr, (1.0, 0.92, 0.65), (1.0, 0.97, 0.85))
            S.floor(cr, 880, (0.85, 0.75, 0.50))
            for tt, x, kind, sc in ((t_pal, 420, 2, 1.1), (t_bri, CX, 0, 1.2), (t_mon, 1500, 1, 1.0)):
                k = back(prog(T, tt, 0.45))
                if k > 0:
                    with xform(cr, x, 880, 1.0, 0, 1.0, max(0.01, k)):
                        monument(cr, 0, 0, sc, kind)
            for i, x in enumerate((180, 760, 1180, 1760)):
                K.person(cr, T, x, 1000, "stand", face=1 if x < CX else -1, s=0.7, seed=i, smile=-0.2)
                if T > t_voice:
                    k = K.pop(T, t_voice + i * 0.12)
                    if k > 0:
                        with xform(cr, x + 40, 690, max(0.01, k)):
                            speech_bubble(cr, 0, 0, 110, 80, -30, 70, scale=1.0)
                            partial_line(cr, -25, -20, 25, 20, 1.0, 8, RED)
                            partial_line(cr, 25, -20, -25, 20, 1.0, 8, RED)
        version_tag(cr, 2, "THE GOLDEN KING", (0.80, 0.58, 0.10), a=eout(prog(t, 0.1, 0.4)))
        if T > t_voice:
            label_box(cr, "BUT NO VOICE", CX, 1010, 44, c=RED, scale=K.pop(T, t_voice))
    for tt in (t_pal, t_bri, t_mon):
        b.fx(tt, "pop", -10)
    b.fx(t_voice, "soft_x", -10)

    # 5. version three: the king who gave power back
    st5 = s("c9_05") - 0.15
    t_grow, t_free, t_without = w("c9_05", "stronger"), w("c9_05", "freer"), w("c9_05", "without")

    @b.shot(st5, "fade", 0.4)
    def gave_back(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.field(cr, T, gy=880)
            kg = ease(prog(T, t_grow - 0.2, 2.5))
            for i in range(7):
                x = 220 + i * 250
                h = 1 + i % 3
                kk = clamp(kg * 1.5 - i * 0.08)
                if kk > 0:
                    P.house(cr, x, 880, 0.6 + 0.25 * h * kk)
            P.tree(cr, 1680, 880, 0.8 + 0.6 * kg, T)
            kf = prog(T, t_free, 0.6)
            crowd(cr, T, n=14, y0=940, y1=1060, cheer=0.6 + 0.4 * kf, x0=200, x1=1300, seed=9)
            P2.ballot_box(cr, 1460, 1040, 0.6, drop=(T * 0.7) % 1.4)
            if T > t_without:
                x = lerp(1000, 2100, ease(prog(T, t_without, 2.5)))
                K.hero(cr, T, x, 1000, "wave", acc=("tuft", "beard"), face=1, walk=0.6, s=0.8, smile=0.9)
        version_tag(cr, 3, "THE KING WHO GAVE POWER BACK", (0.20, 0.55, 0.30), a=eout(prog(t, 0.1, 0.4)))
    b.fx(t_grow, "rise", -12)
    b.fx(t_free, "cheer", -14)

    # 6. the third king is remembered with love
    st6 = s("c9_06") - 0.15
    t_love = w("c9_06", "love")

    def p_iron(cr, T):
        fill_bg(cr, (0.55, 0.55, 0.58))
        P2.statue(cr, 260, 560, 1.0, gold=False, tilt=1.4)

    def p_gold(cr, T):
        fill_bg(cr, (1.0, 0.92, 0.65))
        monument(cr, 260, 520, 1.0, 1)

    def p_love(cr, T):
        fill_bg(cr, (0.85, 0.95, 0.85))
        crowd(cr, T, n=10, y0=470, y1=560, cheer=1.0, x0=60, x1=460, seed=2)
        for i in range(6):
            yy = 380 - ((T * 60 + i * 70) % 380)
            P.heart(cr, 60 + i * 80, yy, 0.35, a=0.8)

    b.add(st6, K.three_paths([("IRON", IRON, p_iron, st6 + 0.2), ("GOLDEN", (0.80, 0.58, 0.10), p_gold, st6 + 0.5),
                              ("GAVE IT BACK", (0.20, 0.55, 0.30), p_love, t_love - 0.4)],
                             title="WHO DO PEOPLE REMEMBER WITH LOVE?"), "fade", 0.3)
    b.fx(st6 + 0.2, "pop", -12)
    b.fx(st6 + 0.5, "pop", -12)
    b.fx(t_love - 0.4, "sparkle", -10)

    # 6b. statues crumble, monuments forgotten, freedom grows
    st6b = s("c9_06b") - 0.15
    t_crum, t_forg, t_grows = w("c9_06b", "crumble"), w("c9_06b", "forgotten"), w("c9_06b", "keeps growing")

    @b.shot(st6b, "fade", 0.4)
    def crumble(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.field(cr, T, gy=880, sky=((0.75, 0.82, 0.92), (0.95, 0.96, 0.97)))
            kc = prog(T, t_crum, 1.2)
            cr.save()
            cr.rectangle(0, -200, 700, 880 + 200 - 400 * kc + 400)
            cr.clip()
            with xform(cr, 0, 400 * ein(kc)):
                P2.statue(cr, 360, 880, 1.4, gold=False)
            cr.restore()
            cr.new_path()
            for i in range(int(12 * kc)):
                g = rng(i)
                circle(cr, 360 + g.uniform(-160, 160), 870 - g.uniform(0, 30), g.uniform(8, 18), fill=(0.75, 0.75, 0.72),
                       stroke=INK, w=2)
            kf = prog(T, t_forg, 1.0)
            monument(cr, CX, 880, 1.0, 2, c=lerpc(GOLD, (0.6, 0.6, 0.55), kf))
            if kf > 0:
                for i in range(6):
                    g = rng(20 + i)
                    x0, y0 = CX + g.uniform(-170, 170), 880
                    partial_poly(cr, [(x0, y0), (x0 + 10, y0 - 60), (x0 - 10, y0 - 120), (x0 + 15, y0 - 180)], kf, 6, GREEN)
                text(cr, "zzz", CX + 220, 600, 50, face=FONT_HAND, bold=True, c=GRAY, a=kf)
            kg = ease(prog(T, t_grows - 0.5, 2.5))
            P.tree(cr, 1560, 880, 0.6 + 1.0 * kg, T)
            for i in range(4):
                K.person(cr, T, 1380 + i * 120, 900 + (i % 2) * 30, "cheer" if kg > 0.5 else "stand", face=1, s=0.6,
                         seed=i, alpha=clamp(kg * 2))
    b.fx(t_crum, "crack", -8)
    b.fx(t_grows - 0.5, "rise", -12)

    # 7. legacy: not statue height but better lives
    st7 = s("c9_07") - 0.15
    t_better = w("c9_07", "how much better")

    def left_draw(cr, cx, T):
        P2.statue(cr, cx, 900, 1.2, gold=True)
        line(cr, cx + 200, 900, cx + 200, 900 - 1.2 * 480, 6, INK)
        for i in range(11):
            yy = 900 - i * 1.2 * 48
            line(cr, cx + 180, yy, cx + 220, yy, 4, INK)
        text(cr, "HOW TALL?", cx, 1000, 50, face=FONT_TITLE, c=RED)
        partial_line(cr, cx - 200, 940, cx + 200, 1060, prog(T, t_better + 0.4, 0.3), 10, RED)

    def right_draw(cr, cx, T):
        S.floor(cr, 900, (0.80, 0.88, 0.70))
        for i in range(3):
            P.house(cr, cx - 280 + i * 280, 760, 0.7, lit=1.0)
        for i, acc in enumerate((("cap",), ("ponytail",), ("bun",), ("glasses",))):
            K.person(cr, T, cx - 270 + i * 180, 900, "cheer" if i % 2 else "wave", face=1, s=0.65, acc=acc, seed=i)
        text(cr, "HOW MUCH BETTER?", cx, 1000, 50, face=FONT_TITLE, c=(0.15, 0.55, 0.25))

    b.add(st7, K.split(dict(title="A LEGACY ISN'T...", bg=(0.95, 0.92, 0.85), draw=left_draw),
                       dict(title="IT'S...", bg=(0.86, 0.95, 0.98), ink=INK, draw=right_draw), t_better - 0.3),
          "fade", 0.3)
    b.fx(t_better - 0.3, "whoosh", -10)

    # 8. the crown goes into a glass case
    st8 = s("c9_08") - 0.15
    t_place = w("c9_08", "place")

    def museum_room(cr, T):
        fill_bg(cr, (0.93, 0.91, 0.86))
        S.floor(cr, 880, (0.75, 0.70, 0.62))
        for x in (200, 1720):
            rect(cr, x - 40, 100, 80, 780, fill=(0.98, 0.97, 0.94), stroke=INK, lw=5)
        rect(cr, 640, 70, 640, 90, fill=(0.25, 0.25, 0.30), stroke=INK, lw=5)
        text(cr, "PEOPLE'S MUSEUM", CX, 115, 50, face=FONT_TITLE, c=WHITE)

    @b.shot(st8, "fade", 0.4)
    def museum(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            museum_room(cr, T)
            kp = ease(prog(T, t_place, 1.2))
            P2.museum_case(cr, 1150, 880, 1.2)
            crown_on = kp < 1
            J = K.hero(cr, T, lerp(700, 860, kp), 880, "hold" if crown_on else "stand",
                       acc=("tuft", "cape", "beard"), face=1, smile=0.6)
            if crown_on:
                cx_ = lerp(J["hand_f"][0] + 20, 1150, kp)
                cy_ = lerp(J["hand_f"][1] - 30, 880 - 1.2 * 260, kp)
                P.crown(cr, cx_, cy_, 0.7)
            else:
                P.crown(cr, 1150, 880 - 1.2 * 260, 0.7)
                glow(cr, 1150, 880 - 1.2 * 260, 140, YELLOW, 0.25)
            # glass front
            rect(cr, 1150 - 1.2 * 130, 880 - 1.2 * 420, 1.2 * 260, 1.2 * 320, fill=(0.85, 0.95, 1.0), a=0.35)
            rect(cr, 1150 - 1.2 * 130, 880 - 1.2 * 420, 1.2 * 260, 1.2 * 320, stroke=INK, lw=5)
    b.fx(t_place + 1.1, "clank", -12)

    # 9. the sign
    st9 = s("c9_09") - 0.15
    t_bor = w("c9_09", "only borrowed")

    @b.shot(st9, "fade", 0.4)
    def sign_shot(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, CX, 520):
            museum_room(cr, T)
            P2.museum_case(cr, 760, 880, 1.6)
            P.crown(cr, 760, 880 - 1.6 * 260, 1.0)
            glow(cr, 760, 880 - 1.6 * 260, 200, YELLOW, 0.25)
            rect(cr, 760 - 1.6 * 130, 880 - 1.6 * 420, 1.6 * 260, 1.6 * 320, fill=(0.85, 0.95, 1.0), a=0.35)
            rect(cr, 760 - 1.6 * 130, 880 - 1.6 * 420, 1.6 * 260, 1.6 * 320, stroke=INK, lw=5)
            k = back(prog(T, st9 + 0.3, 0.5))
            with xform(cr, 1380, 560, max(0.01, k)):
                line(cr, 0, 120, 0, 320, 8, INK)
                rrect(cr, -300, -170, 600, 300, 14, fill=(0.98, 0.96, 0.90), stroke=INK, lw=6)
                text(cr, "POWER BELONGS", 0, -100, 48, face=FONT_TITLE)
                text(cr, "TO THE PEOPLE.", 0, -40, 48, face=FONT_TITLE)
                kb = eout(prog(T, t_bor, 0.5))
                text(cr, "It was only borrowed.", 0, 50, 48, face=FONT_HAND, bold=True, c=RED, a=kb)
    b.fx(st9 + 0.3, "pop", -12)
    b.fx(t_bor, "chime", -10)

    # 10. the crowd isn't bowing anymore, they're cheering
    st10 = s("c9_10") - 0.15
    t_bow, t_cheer = w("c9_10", "bowing"), w("c9_10", "cheering")

    @b.shot(st10, "fade", 0.4)
    def cheering(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.city(cr, T, 0, gy=800)
            rect(cr, 560, 260, 800, 540, fill=(0.93, 0.91, 0.86), stroke=INK, lw=6)
            polyline(cr, [(520, 260), (CX, 120), (1400, 260)], 6, INK, closed=True, fill=(0.93, 0.91, 0.86))
            for x in (640, 780, 1140, 1280):
                rect(cr, x - 25, 330, 50, 470, fill=WHITE, stroke=INK, lw=4)
            P.door(cr, CX, 800, 1.1, open_=1.0)
            kw_ = ease(prog(T, st10 + 0.3, 2.0))
            K.hero(cr, T, CX, lerp(800, 860, kw_), "wave", acc=("tuft", "beard"), face=1, s=lerp(0.8, 0.95, kw_),
                   walk=0.5 if kw_ < 1 else 0.0, smile=1.0)
            cheer = clamp(prog(T, t_cheer - 0.3, 0.6))
            r = rng(5)
            for i in range(26):
                x = r.uniform(-50, 1970)
                if 760 < x < 1160:
                    continue
                y = r.uniform(920, 1070)
                sc = r.uniform(0.55, 0.75)
                g = "cheer" if cheer > 0.5 else "stand"
                p = sm.pose(g, x=x, s=sc, face=1 if x < CX else -1, smile=0.4 + 0.6 * cheer,
                            lean=lerp(35, 0, cheer), head=lerp(30, 0, cheer))
                if g == "cheer":
                    p = sm.apply(p, a1f=150 + 15 * math.sin(T * 8 + i), a1b=-150 + 15 * math.sin(T * 8 + i + 1))
                p = sm.on_ground(sm.idle(p, T, i), y)
                if cheer > 0.5:
                    p["y"] -= abs(math.sin(T * 6 + i)) * 18 * sc
                sm.draw(cr, p, acc=r.choice([(), ("cap",), ("ponytail",), ("bun",), ("hat",)]))
            if cheer > 0:
                for i in range(40):
                    g = rng(i + 50)
                    x = g.uniform(0, W)
                    y = ((T - t_cheer) * g.uniform(150, 300) + g.uniform(-600, 0)) % 1200 - 100
                    rect(cr, x, y, 14, 22, fill=[RED, YELLOW, BLUE, GREEN, ORANGE][i % 5], a=cheer)
        if T > t_bow and T < t_cheer - 0.2:
            label_box(cr, "NOT BOWING...", CX, 180, 50, c=INK, scale=K.pop(T, t_bow))
        if T > t_cheer - 0.2:
            text(cr, "CHEERING!", CX, 180, 90, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10, scale=K.pop(T, t_cheer - 0.2))
    b.fx(st10 + 0.3, "door", -12)
    b.fx(t_cheer - 0.3, "cheer", -6)
    b.fx(t_cheer, "applause", -8, dur=4.0)
    return b.result()
