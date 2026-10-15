"""Thousand Years - Chapter 5: Watching the World Change (3:40-4:50)."""
from video.projects.thousand_years.chapters._t import *  # noqa: F401,F403


def music_plan(tl):
    return K.music(tl, [(0.0, "reflective", "reflective", 72, 0.55), ("c5_02", "mystery", "discovery", 86, 0.55),
                        ("c5_04", "discovery", "discovery_g", 100, 0.65), ("c5_06", "wonder", "wonder", 82, 0.65),
                        ("c5_07", "warm", "warm", 84, 0.6)])


def victorian_street(cr, T, gy=880):
    S.vgrad(cr, (0.80, 0.78, 0.74), (0.92, 0.88, 0.80))
    for i, x in enumerate(range(-100, 2100, 330)):
        h = 420 + (i % 3) * 70
        rect(cr, x, gy - h, 300, h, fill=[(0.62, 0.32, 0.25), (0.55, 0.36, 0.30), (0.66, 0.40, 0.30)][i % 3],
             stroke=INK, lw=5)
        for r_ in range(int(h / 130)):
            for c_ in range(3):
                rect(cr, x + 30 + c_ * 90, gy - h + 40 + r_ * 130, 55, 80, fill=(0.95, 0.88, 0.60), stroke=INK, lw=3)
        rect(cr, x + 120, gy - h - 60, 30, 60, fill=(0.40, 0.25, 0.20), stroke=INK, lw=3)
    S.floor(cr, gy, (0.55, 0.52, 0.50))


def era_bg(cr, T, i, gy=880):
    """Five eras for the 'world keeps changing' montage."""
    i = i % 5
    if i == 0:
        medieval_village(cr, T, gy)
    elif i == 1:
        victorian_street(cr, T, gy)
        steam_train(cr, 1500, gy, 0.55, T, face=-1, cars=1)
    elif i == 2:
        S.vgrad(cr, (0.70, 0.88, 0.98), (0.95, 0.96, 0.90))
        S.floor(cr, gy, (0.62, 0.78, 0.50))
        for j, x in enumerate((200, 520, 1440, 1760)):
            P.house(cr, x, gy, 1.1, roof=[(0.85, 0.55, 0.60), (0.55, 0.75, 0.85), (0.95, 0.80, 0.45), (0.65, 0.80, 0.60)][j])
            line(cr, x + 40, gy - 190, x + 40, gy - 260, 4, INK)
            line(cr, x + 15, gy - 240, x + 65, gy - 240, 4, INK)
            line(cr, x + 20, gy - 225, x + 60, gy - 225, 4, INK)
        P.car(cr, 1150, gy + 40, 1.2, c=(0.35, 0.75, 0.75))
    elif i == 3:
        S.city(cr, T, 0, gy=gy)
    else:
        S.vgrad(cr, (0.10, 0.12, 0.30), (0.45, 0.30, 0.55))
        stars(cr, T, n=80, alpha=0.6, area=(0, 0, W, 500))
        for j, x in enumerate((150, 420, 1450, 1720)):
            h = 520 + (j % 2) * 160
            polyline(cr, [(x - 60, gy), (x - 30, gy - h), (x + 30, gy - h), (x + 60, gy)], 5, INK, closed=True,
                     fill=(0.75, 0.85, 0.95))
            circle(cr, x, gy - h, 50, fill=(0.85, 0.95, 1.0), stroke=INK, w=5)
            glow(cr, x, gy - h, 90, CYAN, 0.4)
        S.floor(cr, gy, (0.25, 0.25, 0.35), ink=(0.5, 0.5, 0.6))
        for j in range(3):
            f = (T * 0.4 + j * 0.33) % 1
            P.drone(cr, lerp(-200, 2100, f), 260 + j * 90, 0.45, T, version=3)


def mini_person(cr, x, y, s=1.0, c=INK):
    circle(cr, x, y - 46 * s, 12 * s, fill=c)
    line(cr, x, y - 34 * s, x, y - 8 * s, 6 * s, c)
    line(cr, x - 14 * s, y - 26 * s, x + 14 * s, y - 26 * s, 5 * s, c)
    line(cr, x, y - 8 * s, x - 10 * s, y + 10 * s, 5 * s, c)
    line(cr, x, y - 8 * s, x + 10 * s, y + 10 * s, 5 * s, c)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. looking back over a thousand years
    @b.shot(0, "fade", 0.4)
    def back_road(cr, t, d, T):
        vgrad(cr, (0.98, 0.80, 0.58), (0.90, 0.88, 0.92))
        with K.ken(cr, t, d, 1.0, 1.06, 900, 600):
            P.sun(cr, 820, 330, 70, T, c=(1.0, 0.85, 0.55))
            S.floor(cr, 560, (0.62, 0.74, 0.50))
            polyline(cr, bezier_pts([(1700, 1300), (1300, 860), (500, 760), (260, 565)], 30) +
                     bezier_pts([(330, 565), (700, 740), (1650, 820), (2200, 1300)], 30), 0, INK, closed=True,
                     fill=(0.85, 0.75, 0.58))
            S.castle(cr, 330, 572, 0.10, t=T)
            for x, sc in ((560, 0.22), (700, 0.26)):
                thatched_hut(cr, x, 640, sc)
            steam_train(cr, 1150, 735, 0.22, T, face=-1, cars=1)
            P.skyline(cr, 1300, 840, 520, 230, seed=21, fill=(0.55, 0.58, 0.68), outline=INK)
            K.hero(cr, T, 1620, 1000, "stand", face=-1, s=1.1, gx=-0.8, head=-6, smile=0.4, a1b=-30, a2b=-80)
            text(cr, "1,000 YEARS AGO", 330, 480, 34, face=FONT_TITLE, c=INK, a=eout(prog(T, 1.2, 0.5)))
            text(cr, "TODAY", 1450, 960, 34, face=FONT_TITLE, c=INK, a=eout(prog(T, 1.6, 0.5)))
        title_text(cr, "LOOKING BACK", 220, 80, c=WHITE, k=eout(prog(t, 0.2, 0.4)))
    b.fx(0.3, "wind", -16, dur=3.0)

    # 2. the year 1025: no printing press, telescopes, electricity
    st2 = s("c5_02") - 0.15

    def crossed(fn, ta, extra=None):
        def draw(cr, T):
            fn(cr, T)
            if extra:
                text(cr, extra, 0, 200, 34, face=FONT_HAND, bold=True, c=GRAY)
            xmark(cr, 0, 0, 120, prog(T, ta + 0.45, 0.35), w=18)
        return draw

    def bg2(cr, T):
        medieval_village(cr, T, 900)
        src(cr, (1.0, 0.97, 0.90), 0.72)
        cr.paint()

    t_pp, t_tel, t_el = w("c5_02", "printing"), w("c5_02", "telescopes"), w("c5_02", "electricity")
    b.add(st2, K.icons("THE YEAR 1025", [
        (crossed(lambda cr, T: printing_press(cr, 0, 0, 1.0), t_pp, "(in Europe)"), "NO PRINTING PRESS", t_pp),
        (crossed(lambda cr, T: P.telescope(cr, 0, 100, 1.1, rot=-0.5), t_tel), "NO TELESCOPES", t_tel),
        (crossed(lambda cr, T: P.lightbulb(cr, 0, 0, 1.0, on=1.0, t=T), t_el), "NO ELECTRICITY", t_el)],
        bg=bg2, y=540, size=1.1, label_size=44), "fade", 0.4)
    for tt in (t_pp, t_tel, t_el):
        b.fx(tt, "pop", -10)
        b.fx(tt + 0.45, "scratch_out", -12)

    # 2b. many never traveled far from their village
    st3 = s("c5_02b") - 0.15
    t_vil = w("c5_02b", "village")

    @b.shot(st3, "fade", 0.3)
    def map_shot(cr, t, d, T):
        fill_bg(cr, (0.40, 0.30, 0.22))
        with K.ken(cr, t, d, 1.05, 1.0, CX, 560):
            rect(cr, 160, 120, 1600, 880, fill=(0.95, 0.88, 0.70), stroke=INK, lw=6)
            g = rng(7)
            for i in range(26):
                x, y = g.uniform(220, 1700), g.uniform(170, 960)
                if math.hypot(x - CX, y - 560) < 330:
                    continue
                kind = g.random()
                if kind < 0.45:
                    polyline(cr, [(x - 40, y + 20), (x, y - 50), (x + 40, y + 20)], 4, INK, closed=True,
                             fill=(0.70, 0.62, 0.50))
                elif kind < 0.85:
                    circle(cr, x, y, 22, fill=(0.40, 0.62, 0.38), stroke=INK, w=3)
                    line(cr, x, y + 22, x, y + 40, 4, INK)
                else:
                    text(cr, "?", x, y, 60, face=FONT_SERIF, bold=True, c=SEPIA_D)
            polyline(cr, bezier_pts([(1500, 160), (1400, 500), (1650, 960)], 20) + [(1760, 960), (1760, 160)], 4, INK,
                     closed=True, fill=(0.55, 0.75, 0.90))
            for i, (dx, dy) in enumerate(((-50, -10), (30, -30), (0, 40), (60, 30), (-40, 50))):
                P.house(cr, CX + dx, 560 + dy, 0.28, roof=(0.75, 0.45, 0.25))
            kr = ease(prog(T, st3 + 0.3, 1.0))
            cr.set_dash([18, 14])
            arc(cr, CX, 560, 290 * kr + 1, 0, TAU, 6, RED)
            cr.set_dash([])
            ang = T * 1.4
            mini_person(cr, CX + math.cos(ang) * 170, 560 + math.sin(ang) * 120, 0.8, INK)
            if T > t_vil:
                label_box(cr, "THEIR WHOLE WORLD", CX, 905, 44, c=RED, bg=(0.98, 0.94, 0.82), scale=K.pop(T, t_vil))
        title_text(cr, "BORN HERE. STAYED HERE.", 70, 60, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
    b.fx(st3 + 0.3, "draw", -12)
    b.fx(t_vil, "pop", -12)

    # 3. 300 million then, 8 billion now
    st4 = s("c5_03") - 0.15
    t_300, t_8 = w("c5_03", "three hundred"), w("c5_03", "eight billion")

    @b.shot(st4, "fade", 0.3)
    def population(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.15)
        with K.ken(cr, t, d, 1.0, 1.02):
            text(cr, "PEOPLE ON EARTH", CX, 120, 64, face=FONT_TITLE, a=eout(prog(t, 0.0, 0.3)))
            rrect(cr, 100, 210, 520, 640, 24, fill=(0.96, 0.90, 0.76), stroke=INK, lw=5)
            rrect(cr, 680, 210, 1140, 640, 24, fill=(0.86, 0.92, 1.0), stroke=INK, lw=5)
            text(cr, "AROUND 1025", 360, 270, 46, face=FONT_TITLE, c=SEPIA_D)
            text(cr, "TODAY", 1250, 270, 46, face=FONT_TITLE, c=BLUE)
            for i in range(3):
                k = K.pop(T, t_300 + i * 0.15)
                if k > 0:
                    with xform(cr, 250 + i * 110, 560, max(0.01, k)):
                        mini_person(cr, 0, 0, 2.0, SEPIA_D)
            if T > t_300:
                text(cr, "~300 MILLION", 360, 760, 58, face=FONT_TITLE, c=SEPIA_D, scale=K.pop(T, t_300 + 0.3))
            n = int(80 * clamp(prog(T, t_8 - 0.2, 1.4)))
            for i in range(n):
                r_, c_ = divmod(i, 16)
                mini_person(cr, 760 + c_ * 66, 400 + r_ * 70, 1.0, BLUE)
            if T > t_8:
                text(cr, "8+ BILLION", 1250, 790, 72, face=FONT_TITLE, c=BLUE, scale=K.pop(T, t_8 + 1.2))
            mini_person(cr, 760, 975, 0.9, INK)
            text(cr, "= 100 MILLION PEOPLE", 800, 960, 34, face=FONT_BOLD, align="left", a=eout(prog(T, t_300, 0.4)))
    b.fx(t_300, "pop", -10)
    b.fx(t_8 - 0.2, "blips", -10, dur=1.4)
    b.fx(t_8 + 1.2, "ding", -8)

    # 4. plagues, revolutions, airplanes, the moon
    st5 = s("c5_04") - 0.15
    marks = [("PLAGUES", w("c5_04", "plagues"), lambda cr, T: plague_mask(cr, 0, 20, 1.0)),
             ("REVOLUTIONS", w("c5_04", "revolutions"), lambda cr, T: revolution(cr, -20, 10, 1.0, T)),
             ("AIRPLANES", w("c5_04", "airplanes"), lambda cr, T: biplane(cr, 0, 0, 0.75, T)),
             ("FIRST STEPS\nON THE MOON", w("c5_04", "footsteps"), lambda cr, T: moon_icon(cr, 0, 50, 0.75))]
    b.add(st5, K.timeline("YOU'D HAVE LIVED THROUGH...", marks, st5 + 0.1, bg=(0.97, 0.94, 0.88), y=660), "slide", 0.4)
    for (_, tt, _) in marks:
        b.fx(tt, "pop", -8)

    # 4b. steam trains roar into town
    st6 = s("c5_04b") - 0.15
    t_tr, t_roar, t_tel2 = w("c5_04b", "steam trains"), w("c5_04b", "roared"), w("c5_04b", "telephone")

    @b.shot(st6, "fade", 0.3)
    def train(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            victorian_street(cr, T, 760)
            rect(cr, -400, 860, W + 800, 20, fill=(0.45, 0.35, 0.28))
            for i in range(-2, 30):
                rect(cr, i * 80, 870, 40, 16, fill=(0.35, 0.25, 0.18))
            kx = ease(prog(T, t_tr - 0.4, 2.0))
            steam_train(cr, lerp(2700, 1100, kx), 870, 0.95, T, face=-1, cars=2)
            roar = T > t_roar
            for i, (x, acc, st_) in enumerate(((240, ("hat", "mustache"), "stand"), (420, ("bun",), "stand"),
                                               (760, ("hat",), "stand"))):
                K.person(cr, T, x, 1000, "surprised" if roar else "stand", face=1, s=0.85, acc=acc, seed=i, eye=1.2)
            K.hero(cr, T, 590, 1000, "cheer" if roar else "point", face=1, s=0.85, smile=0.9)
            if roar:
                text(cr, "CHOO CHOO!", 1300, 220, 80, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8,
                     scale=K.pop(T, t_roar), rot=-0.05)
        text(cr, "THE FIRST STEAM TRAINS", 520, 110, 52, face=FONT_TITLE, c=WHITE, outline=INK, ow=7,
             a=eout(prog(t, 0.1, 0.4)))
    b.fx(t_tr - 0.4, "machine", -10, dur=2.0)
    b.fx(t_roar, "honk", -8)

    # 4c. a voice through a telephone
    @b.shot(t_tel2 - 0.2, "fade", 0.3)
    def phone_call(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.room(cr, T, wall=(0.88, 0.80, 0.68), floor_c=(0.50, 0.34, 0.24), fy=900)
            for x in range(0, W, 120):
                line(cr, x, 0, x, 900, 3, (0.80, 0.70, 0.56))
            rect(cr, 680, 650, 420, 30, fill=(0.50, 0.32, 0.20), stroke=INK, lw=4)
            line(cr, 720, 680, 720, 900, 8, INK)
            line(cr, 1060, 680, 1060, 900, 8, INK)
            candlestick_phone(cr, 820, 650, 0.9)
            J = K.person(cr, T, 1020, 900, "phone", face=-1, acc=("bun",), seed=3, eye=1.35, browy=1.0, mo=0.5)
            for k in range(3):
                f = (T * 1.5 + k / 3) % 1
                arc(cr, J["hand_f"][0], J["hand_f"][1], 30 + 60 * f, -0.9, 0.5, 5, BLUE, 1 - f)
            say(cr, "Hello...?", 1330, 330, J["hand_f"][0] + 20, J["hand_f"][1] - 20, K.pop(T, t_tel2 + 0.3), size=52)
            K.hero(cr, T, 420, 900, "surprised", face=1, s=0.95)
        text(cr, "A VOICE THROUGH A WIRE!", CX, 120, 60, face=FONT_TITLE, c=WHITE, outline=INK, ow=8,
             a=eout(prog(t, 0.1, 0.4)))
    b.fx(t_tel2, "bell", -10)

    # 5. every few decades the world vanishes and a new one appears
    st7 = s("c5_05") - 0.15
    t_van, t_new = w("c5_05", "vanish"), w("c5_05", "new one")

    @b.shot(st7, "fade", 0.3)
    def eras(cr, t, d, T):
        per = (t_new - 0.3 - st7) / 4.0
        u = (T - st7) / per
        i = min(4, int(u))
        f = u - i if i < 4 else 0.0
        era_bg(cr, T, i)
        if f > 0.7:
            k = ease((f - 0.7) / 0.3)
            cr.save()
            cr.arc(CX, 700, k * 1300 + 1, 0, TAU)
            cr.clip()
            era_bg(cr, T, i + 1)
            cr.restore()
            cr.new_path()
            arc(cr, CX, 700, k * 1300 + 1, 0, TAU, 10, WHITE, 1 - k)
        K.hero(cr, T, CX, 900, "stand", face=1, s=1.05, smile=0.3, gx=0.6 * math.sin(T * 3))
        text(cr, ["~1100", "~1850", "~1960", "TODAY", "FUTURE?"][min(4, i + (1 if f > 0.85 else 0))], 1700, 120, 60,
             face=FONT_TITLE, c=WHITE,
             outline=INK, ow=8)
        if T > t_van:
            text(cr, "THE WORLD YOU KNEW VANISHES...", CX, 1010, 52, face=FONT_TITLE, c=WHITE, outline=INK, ow=7,
                 a=eout(prog(T, t_van, 0.3)) * (1 - prog(T, t_new - 0.2, 0.2)))
        if T > t_new:
            text(cr, "...AND A NEW ONE TAKES ITS PLACE", CX, 1010, 52, face=FONT_TITLE, c=YELLOW, outline=INK, ow=7,
                 a=eout(prog(T, t_new, 0.3)))
    for i in range(4):
        b.fx(st7 + (t_new - 0.3 - st7) / 4.0 * (i + 0.7), "swish", -14)

    # 6. the next thousand years: Mars, medicines, nameless tech - speculation
    st8 = s("c5_06") - 0.15
    t_mars, t_med, t_name, t_spec = (w("c5_06", "mars"), w("c5_06", "medicines"), w("c5_06", "name"),
                                     w("c5_06", "speculation"))

    @b.shot(st8, "fade", 0.4)
    def future(cr, t, d, T):
        vgrad(cr, (0.95, 0.62, 0.40), (0.98, 0.82, 0.62))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            circle(cr, 1600, 230, 40, fill=(1.0, 0.95, 0.85))
            polyline(cr, [(-400, 760), (300, 700), (800, 740), (1400, 690), (2300, 760), (2300, 1500), (-400, 1500)],
                     5, INK, closed=True, fill=(0.80, 0.42, 0.25))
            for i in range(10):
                g = rng(i + 4)
                ellipse(cr, g.uniform(0, W), g.uniform(800, 1060), g.uniform(40, 90), g.uniform(12, 24),
                        fill=(0.68, 0.34, 0.20))
            km = K.pop(T, t_mars)
            if km > 0:
                with xform(cr, 560, 760, max(0.01, km)):
                    dome_city(cr, 0, 0, 1.1, T)
                label_box(cr, "CITIES ON MARS?", 560, 900, 44, c=INK, scale=km)
            kl = ease(prog(T, st8 + 0.2, 2.5))
            rocket(cr, 1560, lerp(-300, 640, kl), 0.8, T, flame=1.0 if kl < 1 else 0.0)
            kd = K.pop(T, t_med)
            if kd > 0:
                with xform(cr, 1080, 420, max(0.01, kd)):
                    circle(cr, 0, 0, 100, fill=WHITE, stroke=INK, w=5)
                    with xform(cr, 0, 0, 1.0, -0.6):
                        rrect(cr, -60, -24, 120, 48, 24, fill=WHITE, stroke=INK, lw=4)
                        rrect(cr, -60, -24, 60, 48, 24, fill=RED)
                        rrect(cr, -60, -24, 120, 48, 24, stroke=INK, lw=4)
                text(cr, "NEW MEDICINES?", 1080, 560, 40, face=FONT_TITLE, c=WHITE, outline=INK, ow=5, a=clamp(kd))
            kn = K.pop(T, t_name)
            if kn > 0:
                glow(cr, 1500, 320, 160, CYAN, 0.5 * clamp(kn))
                with xform(cr, 1500, 320 + 10 * math.sin(T * 2), max(0.01, kn), T * 0.5):
                    polyline(cr, [(0, -80), (70, 0), (0, 80), (-70, 0)], 5, INK, closed=True, fill=(0.75, 0.95, 1.0))
                    text(cr, "?", 0, 4, 70, face=FONT_TITLE, c=BLUE)
        title_text(cr, "THE NEXT 1,000 YEARS?", 140, 70, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
        if T > t_spec:
            stamp(cr, "PURE SPECULATION", CX, 640, T - t_spec, 80, c=PURPLE, rot=-0.06)
    b.fx(st8 + 0.2, "charge", -12)
    b.fx(t_mars, "pop", -10)
    b.fx(t_med, "pop", -10)
    b.fx(t_name, "shimmer", -10)
    b.fx(t_spec, "stamp", -6)

    # 6b. robots, the stars, or a surprise
    st9 = s("c5_06b") - 0.15

    def p_robot(cr, T):
        vgrad(cr, (0.85, 0.92, 1.0), (0.95, 0.97, 1.0), 0, 0, 520, 600)
        rect(cr, 0, 470, 520, 130, fill=(0.75, 0.75, 0.80))
        P.robot(cr, 200, 480, 0.85, T)
        for i in range(3):
            rect(cr, 340, 470 - (i + 1) * 60, 90, 56, fill=(0.80, 0.62, 0.40), stroke=INK, lw=4)

    def p_space(cr, T):
        vgrad(cr, (0.05, 0.05, 0.15), (0.12, 0.08, 0.25), 0, 0, 520, 600)
        stars(cr, T, n=60, area=(0, 0, 520, 600))
        circle(cr, 400, 470, 150, fill=(0.35, 0.55, 0.85))
        rocket(cr, 220, 260, 0.75, T, rot=0.5)
        rect(cr, 60, 120, 120, 40, fill=LIGHT, stroke=INK, lw=4)
        circle(cr, 120, 140, 30, fill=WHITE, stroke=INK, w=4)

    def p_surprise(cr, T):
        vgrad(cr, (1.0, 0.92, 0.75), (1.0, 0.85, 0.65), 0, 0, 520, 600)
        radial_lines(cr, 260, 300, T, n=18, c=WHITE, a=0.6, w=24, r0=60, r1=500)
        rect(cr, 140, 300, 240, 220, fill=PURPLE, stroke=INK, lw=6)
        rect(cr, 120, 260, 280, 60, fill=(0.65, 0.45, 0.95), stroke=INK, lw=6)
        rect(cr, 240, 260, 40, 260, fill=YELLOW, stroke=INK, lw=4)
        text(cr, "?", 260, 160 + 10 * math.sin(T * 3), 130, face=FONT_TITLE, c=ORANGE, outline=INK, ow=6)

    b.add(st9, K.three_paths([("ROBOTS AT WORK?", BLUE, p_robot, w("c5_06b", "robots")),
                              ("LIFE IN SPACE?", PURPLE, p_space, w("c5_06b", "stars")),
                              ("A BIG SURPRISE?", ORANGE, p_surprise, w("c5_06b", "surprise"))],
                             title="MAYBE..."), "fade", 0.3)
    for wd in ("robots", "stars", "surprise"):
        b.fx(w("c5_06b", wd), "pop", -8)

    # 7. a living history book
    st10 = s("c5_07") - 0.15
    t_only = w("c5_07", "only person")

    @b.shot(st10, "fade", 0.3)
    def history_book(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.room(cr, T, wall=(0.92, 0.88, 0.80), floor_c=(0.62, 0.48, 0.36), fy=900)
            glow(cr, 1200, 560, 500, YELLOW, 0.25)
            P2.book_big(cr, 1200, 640, 1.15, title="HISTORY")
            with xform(cr, 1215, 700, 1.0):
                circle(cr, 0, 0, 90, fill=(0.98, 0.94, 0.82), stroke=INK, w=5)
                cr.save()
                cr.arc(0, 0, 86, 0, TAU)
                cr.clip()
                sm.draw(cr, head_at(sm.pose("front", s=1.3, smile=0.8), 0, 14), acc=HERO)
                cr.restore()
                cr.new_path()
            K.hero(cr, T, 620, 900, "present", face=1, smile=0.8)
            if T > t_only:
                for i, (x, acc) in enumerate(((240, ("cap",)), (380, ("ponytail",)))):
                    K.person(cr, T, x, 900, "shrug", face=1, s=0.8, acc=acc, seed=i, alpha=clamp(K.pop(T, t_only + i * 0.2)))
                J = sm.joints(sm.on_ground(sm.pose("present", x=620, face=1), 900))
                thought_bubble(cr, 780, 350, 300, 200, J["head"][0] + 30, J["head"][1] - 60, t=T,
                               scale=K.pop(T, t_only + 0.3))
                if T > t_only + 0.5:
                    S.castle(cr, 780, 420, 0.22, t=T)
        title_text(cr, "A LIVING HISTORY BOOK", 140, 66, c=WHITE, k=eout(prog(t, 0.1, 0.4)))
    b.fx(st10 + 0.2, "page", -8)
    b.fx(t_only + 0.3, "pop", -12)

    # 8. telling a classroom about life before the internet... and electricity
    st11 = s("c5_08") - 0.15
    t_int, t_ele = w("c5_08", "internet"), w("c5_08", "electricity")

    @b.shot(st11, "fade", 0.3)
    def classroom_shot(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            classroom(cr, T, [("BEFORE THE INTERNET...", eout(prog(T, t_int, 0.4))),
                              ("...AND BEFORE ELECTRICITY", eout(prog(T, t_ele, 0.4)))])
            K.hero(cr, T, 380, 860, "point" if T < t_ele else "present", face=1, s=1.0, talk=0.6, smile=0.7)
            shock = T > t_ele + 0.3
            for i, (x, acc) in enumerate(((760, ("cap",)), (1080, ("ponytail",)), (1400, ("glasses",)), (1720, ("bun",)))):
                lean = 0
                if shock and i == 2:
                    lean = -40 * ease(prog(T, t_ele + 0.6, 0.5))
                J = desk_kid(cr, T, x, 1050, acc=acc, seed=i, face=-1, s=0.78, eye=1.4 if shock else 1.0,
                             mo=0.7 if shock else 0.0, browy=1.0 if shock else 0.0, lean=lean, smile=0.0 if shock else 0.4)
            if shock:
                say(cr, "WHAT?!", 1080, 560, 1080, 700, K.pop(T, t_ele + 0.3), size=60, face=FONT_TITLE, bold=False)
    b.fx(t_int, "chalk", -10)
    b.fx(t_ele, "chalk", -10)
    b.fx(t_ele + 0.3, "boing", -10)
    return b.result()
