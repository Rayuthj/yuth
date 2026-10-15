"""Trillion - Chapter 2: How Big Is a Trillion? (0:40-1:40)."""
from video.projects.trillion.chapters._m import *  # noqa: F401,F403

TITLE_T = 2.8          # how long the title had been on screen when chapter 1 ended


def music_plan(tl):
    return K.music(tl, [(0.6, "discovery", "discovery", 100, 0.75), ("c2_05", "wonder", "wonder", 80, 0.7),
                        ("c2_07", "playful", "playful", 108, 0.7)])


def day_night(T, speed):
    """0 = noon, 1 = midnight."""
    return 0.5 - 0.5 * math.cos(T * speed)


def sky_window(cr, x, y, w_, h_, T, speed, ink=INK):
    k = day_night(T, speed)
    sky = lerpc((0.55, 0.78, 0.98), (0.04, 0.05, 0.15), k)
    rect(cr, x - w_ / 2, y - h_ / 2, w_, h_, fill=sky, stroke=ink, lw=8)
    cr.save()
    cr.rectangle(x - w_ / 2, y - h_ / 2, w_, h_)
    cr.clip()
    a = T * speed
    sx, sy = x + math.sin(a) * w_ * 0.42, y + h_ * 0.55 - math.cos(a) * h_ * 0.8
    P.sun(cr, sx, sy, 34, T, rays=False)
    mx, my = x - math.sin(a) * w_ * 0.42, y + h_ * 0.55 + math.cos(a) * h_ * 0.8
    circle(cr, mx, my, 28, fill=(0.95, 0.95, 0.85))
    if k > 0.5:
        stars(cr, T, n=30, alpha=(k - 0.5) * 2, area=(x - w_ / 2, y - h_ / 2, w_, h_))
    cr.restore()
    cr.new_path()
    line(cr, x, y - h_ / 2, x, y + h_ / 2, 6, ink)
    line(cr, x - w_ / 2, y, x + w_ / 2, y, 6, ink)
    return k


def build(tl):
    b = Builder(tl)
    s, e, w = timing(tl)

    @b.shot(0)
    def title_out(cr, t, d, T):
        TITLE(cr, TITLE_T + t)

    # 1. how big is a trillion, really?
    num = "1,000,000,000,000"

    @b.shot(0.7, "zoom", 0.6)
    def how_big(cr, t, d, T):
        S.blueprint(cr)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            text(cr, "HOW BIG IS A TRILLION?", CX, 250, 76, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
            n = int(len(num) * clamp(prog(t, 0.4, 1.2)))
            text(cr, num[:n], 860, 520, 150, face=FONT_TITLE, c=CASH_D)
            kz = prog(T, w("c2_01", "really"), 0.6)
            if kz > 0:
                x0, x1 = 860 - 700 + 120, 860 + 700
                partial_line(cr, x0, 620, x1, 620, ease(kz), 6, INK)
                line(cr, x0, 600, x0, 640, 6, INK, a=clamp(kz * 3))
                line(cr, x1, 600, x1, 640, 6, INK, a=ease(kz))
                label_box(cr, "12 ZEROS", (x0 + x1) / 2, 680, 44, c=INK, bg=YELLOW, face=FONT_TITLE, bold=False,
                          scale=K.pop(T, w("c2_01", "really") + 0.4))
            g = "think" if T < w("c2_01", "really") else "shrug"
            dude(cr, T, 1700, 960, g, face=-1, s=1.0)
            P.question_mark(cr, 1640, 560, 110, c=RED, rot=0.15 * math.sin(T * 3), a=clamp(prog(T, 2.0, 0.4)))
    b.fx(0.7, "whoosh", -8)
    b.fx(1.1, "typing", -14, dur=1.2)
    b.fx(w("c2_01", "really") + 0.4, "pop", -10)

    # 1b. our brains can't picture it
    st1b = s("c2_01b") - 0.15
    t_cmp = w("c2_01b", "comparisons")

    @b.shot(st1b, "fade", 0.3)
    def brain_err(cr, t, d, T):
        fill_bg(cr, (0.95, 0.93, 0.88))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 500):
            hot = clamp(prog(t, 0.3, 2.5))
            p = sm.pose("front", s=2.6, lw=5, fo=0.0, eye=1.0 + 0.3 * hot, browy=0.6 * hot, smile=-0.3 * hot,
                        mo=0.3 * hot, gx=0.6, gy=-0.5)
            p = head_at(sm.idle(p, T, 4, 0.5), 430, 470)
            sm.draw(cr, p, acc=HERO)
            for i in range(5):
                f = (T * 0.6 + i / 5) % 1
                circle(cr, 400 + 40 * math.sin(i * 2 + T), 330 - f * 220, 22 + f * 30, fill=(0.6, 0.6, 0.62),
                       a=0.5 * hot * (1 - f))
            kb = back(prog(t, 0.2, 0.4))
            thought_bubble(cr, 1240, 360, 900, 420, 560, 420, scale=kb, t=T)
            if kb > 0.5:
                P.brain(cr, 960, 360, 0.75, glow_a=0.3 * hot, t=T)
                cr.save()
                cr.rectangle(1080, 200, 520, 320)
                cr.clip()
                zs = "1,000,000,000,000,000,000,000,000,000"
                off = (T * 220) % 160
                text(cr, zs, 1090 - off, 300, 54, face=FONT_TITLE, c=CASH_D, align="left")
                cr.restore()
                cr.new_path()
                rrect(cr, 1100, 380, 460, 40, 20, fill=WHITE, stroke=INK, lw=4)
                rrect(cr, 1100, 380, 460 * 0.04, 40, 20, fill=RED)
                text(cr, "LOADING... 3%", 1330, 450, 32, face=FONT_BOLD, c=RED)
            if T > st1b + 1.6 and T < t_cmp:
                label_box(cr, "ERROR: NUMBER TOO BIG", 1240, 640, 46, c=WHITE, bg=RED, face=FONT_TITLE, bold=False,
                          scale=K.pop(T, st1b + 1.6))
            for i, (lab, icon, c) in enumerate((("TIME", "clock", BLUE), ("HEIGHT", "stack", GREEN),
                                                ("WEIGHT", "scale", ORANGE))):
                k = K.pop(T, t_cmp + i * 0.25)
                if k <= 0:
                    continue
                x = 780 + i * 420
                with xform(cr, x, 820, max(0.01, k)):
                    rrect(cr, -170, -110, 340, 220, 22, fill=WHITE, stroke=c, lw=8)
                    if icon == "clock":
                        P.clock(cr, 0, -20, 55, T * 20, hours=3, speed=60)
                    elif icon == "stack":
                        for j in range(6):
                            bill(cr, 0, 20 - j * 14, 0.42, 0.0)
                    else:
                        P.scale_balance(cr, 0, 40, 0.3, tilt=0.15 * math.sin(T * 3))
                    text(cr, lab, 0, 75, 40, face=FONT_TITLE, c=c)
    b.fx(st1b + 0.2, "bubbles", -12)
    b.fx(st1b + 1.6, "alert", -10)
    for i in range(3):
        b.fx(t_cmp + i * 0.25, "pop", -10)

    # 2. a million seconds ~ 11.5 days; a billion seconds ~ almost 32 years
    st2 = s("c2_02") - 0.15
    t_days, t_bil, t_yrs = w("c2_02", "days"), w("c2_02", "a billion"), w("c2_02", "years")

    @b.shot(st2, "fade", 0.3)
    def seconds(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.03):
            for i, (title, x, c, t0) in enumerate((("1 MILLION SECONDS", 500, BLUE, st2 + 0.1),
                                                     ("1 BILLION SECONDS", 1420, PURPLE, t_bil - 0.2))):
                k = K.pop(T, t0)
                if k <= 0:
                    continue
                with xform(cr, x, 560, max(0.01, k)):
                    rrect(cr, -400, -390, 800, 780, 30, fill=WHITE, stroke=c, lw=10)
                    rrect(cr, -400, -390, 800, 110, 30, fill=c)
                    rect(cr, -400, -320, 800, 40, fill=c)
                    text(cr, title, 0, -335, 54, face=FONT_TITLE, c=WHITE)
            k1 = prog(T, st2 + 0.3, max(0.3, t_days - st2 - 0.3))
            if K.pop(T, st2 + 0.1) > 0.5:
                day = 1 + int(10.5 * k1)
                big = f"{day}" if k1 < 1 else "11½"
                calendar(cr, 500, 520, 1.25, "DAY", big, c=BLUE)
                if T > t_days:
                    text(cr, "≈ 11½ DAYS", 500, 830, 72, face=FONT_TITLE, c=BLUE, a=eout(prog(T, t_days, 0.3)))
            if T > t_bil:
                k2 = clamp(prog(T, t_bil, max(0.3, t_yrs - t_bil)))
                age = int(31 * k2)
                sc = lerp(0.45, 1.05, ease(k2))
                dude(cr, T, 1420, 720, "stand" if k2 < 1 else "cheer", s=sc, smile=0.8,
                     acc=HERO)
                label_box(cr, f"AGE {age}", 1660, 330, 40, c=PURPLE, bg=WHITE, face=FONT_TITLE, bold=False)
                if T > t_yrs:
                    text(cr, "ALMOST 32 YEARS", 1420, 830, 72, face=FONT_TITLE, c=PURPLE, a=eout(prog(T, t_yrs, 0.3)))
    b.fx(st2 + 0.1, "pop", -10)
    b.fx(st2 + 0.3, "page", -10, dur=1.5)
    b.fx(t_days, "ding", -10)
    b.fx(t_bil - 0.2, "pop", -10)
    b.fx(t_yrs, "ding", -8)

    # 3. a trillion seconds ~ 31,700 years: longer than civilization
    st3 = s("c2_03") - 0.15
    t_tri, t_num, t_civ = w("c2_03", "trillion seconds"), w("c2_03", "thirty-one"), w("c2_03", "longer")
    X0, X1, RY = 200, 1760, 700

    def yx(years_ago):
        return X1 - (X1 - X0) * years_ago / 31700

    def mammoth(cr, x, y, s_):
        with xform(cr, x, y, s_):
            polyline(cr, bezier_pts([(-110, 0), (-130, -150), (0, -190), (120, -150), (110, -40)], 24), 5, INK,
                     closed=True, fill=(0.55, 0.40, 0.30))
            for lx in (-80, -30, 30, 80):
                rect(cr, lx - 16, -40, 32, 60, fill=(0.55, 0.40, 0.30), stroke=INK, lw=4)
            polyline(cr, bezier_pts([(110, -120), (170, -60), (150, 10), (120, 20)], 16), 22, INK)
            polyline(cr, bezier_pts([(110, -120), (170, -60), (150, 10), (120, 20)], 16), 14, (0.55, 0.40, 0.30))
            polyline(cr, bezier_pts([(120, -80), (190, -40), (210, -110)], 12), 8, (0.95, 0.92, 0.85))
            circle(cr, 120, -130, 6, fill=INK)

    def pyramid(cr, x, y, s_):
        polyline(cr, [(x - 70 * s_, y), (x, y - 90 * s_), (x + 70 * s_, y)], 4, INK, closed=True, fill=(0.95, 0.80, 0.45))

    def wheat(cr, x, y, s_):
        for k in (-1, 0, 1):
            line(cr, x + k * 18 * s_, y, x + k * 26 * s_, y - 90 * s_, 4, (0.65, 0.50, 0.15))
            for j in range(4):
                ellipse(cr, x + k * 26 * s_ - 6 * s_, y - (60 + j * 12) * s_, 6 * s_, 10 * s_, fill=GOLD, stroke=INK, w=2)

    @b.shot(st3, "fade", 0.3)
    def ribbon(cr, t, d, T):
        fill_bg(cr, (0.97, 0.95, 0.90))
        vignette(cr, 0.16)
        kz = ease(prog(T, st3 + 0.3, max(0.5, t_num + 0.8 - st3 - 0.3)))
        with camera(cr, lerp(2.0, 1.0, kz), lerp(X1 - 120, CX, kz), lerp(RY - 130, 600, kz)):
            rrect(cr, X0 - 30, RY - 16, X1 - X0 + 60, 32, 16, fill=(0.85, 0.80, 0.70), stroke=INK, lw=5)
            for i in range(32):
                x = yx(i * 1000)
                line(cr, x, RY - 16, x, RY + 16, 2 if i % 5 else 4, INK, 0.6)
            dude(cr, T, X1, RY - 18, "wave", s=0.55, face=-1, smile=0.8)
            text(cr, "TODAY", X1, RY + 50, 30, face=FONT_TITLE)
            pyramid(cr, yx(4500), RY - 18, 0.7)
            text(cr, "PYRAMIDS", yx(4500) - 30, RY + 50, 26, face=FONT_BOLD, c=GRAY)
            text(cr, "~4,500 YRS AGO", yx(4500) - 30, RY + 82, 24, face=FONT_BOLD, c=GRAY)
            wheat(cr, yx(12000), RY - 18, 0.8)
            text(cr, "FIRST FARMS", yx(12000), RY + 50, 26, face=FONT_BOLD, c=GRAY)
            text(cr, "~12,000 YRS AGO", yx(12000), RY + 82, 24, face=FONT_BOLD, c=GRAY)
            mammoth(cr, X0 + 90, RY - 18, 0.75)
            text(cr, "ICE AGE", X0 + 60, RY + 50, 30, face=FONT_TITLE, c=BLUE)
            text(cr, "31,700 YEARS AGO", X0 + 60, RY + 88, 28, face=FONT_BOLD, c=BLUE)
            kc = ease(prog(T, t_civ, 0.6))
            if kc > 0:
                xa, xb = yx(6000), X1
                y_ = RY - 150
                polyline(cr, [(xa, y_ + 30), (xa, y_), (lerp(xa, xb, kc), y_)], 6, RED)
                if kc >= 1:
                    line(cr, xb, y_, xb, y_ + 30, 6, RED)
                text(cr, "ALL OF CIVILIZATION", (xa + xb) / 2 - 60, y_ - 40, 34, face=FONT_TITLE, c=RED, a=kc)
                kk = ease(prog(T, t_civ + 0.6, 0.8))
                if kk > 0:
                    polyline(cr, [(X0, y_ + 30 - 90), (X0, y_ - 90), (lerp(X0, X1, kk), y_ - 90)], 6, PURPLE)
                    if kk >= 1:
                        line(cr, X1, y_ - 90, X1, y_ - 60, 6, PURPLE)
                    text(cr, "1 TRILLION SECONDS", lerp(X0, X1, 0.42), y_ - 130, 40, face=FONT_TITLE, c=PURPLE, a=kk)
        k1 = eout(prog(T, t_tri - 0.1, 0.4))
        text(cr, "1 TRILLION SECONDS", CX, 190, 70, face=FONT_TITLE, c=PURPLE, a=k1)
        if T > t_num:
            text(cr, "≈ 31,700 YEARS", CX, 290, 84, face=FONT_TITLE, c=INK, scale=K.pop(T, t_num))
    b.fx(t_tri, "pop", -10)
    b.fx(st3 + 0.4, "whoosh", -12)
    b.fx(t_num, "ding", -6)
    b.fx(t_civ, "draw", -10)

    # 4. counting one dollar per second, day and night
    st4 = s("c2_04") - 0.15
    t_30k = w("c2_04", "thirty thousand")

    @b.shot(st4, "fade", 0.3)
    def counting(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            k = day_night(T, 3.0)
            S.room(cr, T, wall=lerpc((0.93, 0.90, 0.84), (0.30, 0.30, 0.40), k),
                   floor_c=lerpc((0.75, 0.62, 0.48), (0.25, 0.22, 0.26), k), fy=900)
            sky_window(cr, 1500, 380, 420, 300, T, 3.0)
            P.clock(cr, 300, 260, 70, T * 400, hours=1, speed=60)
            P.desk(cr, 900, 900, 700)
            cash_pile(cr, 760, 750, 0.45, rows=4, seed=3)
            n = max(0, int(T - st4))
            for i in range(min(n, 8)):
                bill(cr, 1080, 742 - i * 6, 0.5, 0.05 * math.sin(i * 7))
            f = (T - st4) % 1.0
            if f < 0.5:
                bill(cr, lerp(900, 1080, ease(f * 2)), 700 - 60 * math.sin(f * 2 * math.pi), 0.5, f * 2)
            dude(cr, T, 950, 900, "hold", s=0.95, face=1, smile=0.3, gx=0.5, gy=0.6,
                 a1f=60 + 30 * math.sin(f * TAU), a2f=40, brow=-0.2 if T > t_30k else 0.0)
        rrect(cr, 60, 60, 760, 210, 20, fill=WHITE, stroke=INK, lw=5)
        text(cr, "COUNTED:", 90, 115, 40, face=FONT_TITLE, align="left")
        text(cr, f"${n:,}", 790, 115, 48, face=FONT_TITLE, c=CASH_D, align="right")
        text(cr, "STILL TO GO:", 90, 205, 40, face=FONT_TITLE, align="left")
        text(cr, f"${10 ** 12 - n:,}", 790, 205, 40, face=FONT_TITLE, c=RED, align="right")
        stamp(cr, "30,000+ YEARS", 1300, 860, T - t_30k, 90, c=RED, rot=-0.06)
    for i in range(int(e("c2_04") - st4) + 1):
        b.fx(st4 + i + 0.45, "blip", -20)
    b.fx(t_30k, "stamp", -4)

    # 5. stacked in $100 bills: over 1,000 km high, more than twice the ISS
    st5 = s("c2_05") - 0.15
    t_pile, t_km, t_iss = w("c2_05", "pile"), w("c2_05", "kilometers"), w("c2_05", "international")
    PPK0 = 330 / 0.0018
    PPK1 = (980 - 210) / 1100.0
    GY = 980

    @b.shot(st5, "fade", 0.3)
    def stack(cr, t, d, T):
        kz = ease(prog(T, t_pile, max(0.5, t_km + 0.8 - t_pile)))
        ppk = math.exp(lerp(math.log(PPK0), math.log(PPK1), kz))
        space = clamp((math.log(PPK0) - math.log(ppk)) / (math.log(PPK0) - math.log(PPK1)))
        vgrad(cr, lerpc((0.55, 0.78, 0.98), (0.02, 0.02, 0.08), clamp(space * 1.6 - 0.4)),
              lerpc((0.88, 0.94, 0.99), (0.10, 0.20, 0.45), clamp(space * 1.6 - 0.4)))
        if space > 0.4:
            stars(cr, T, n=160, alpha=clamp(space * 2 - 0.8))
        R = 6371 * ppk
        if R < 40000:
            circle(cr, CX, GY + R, R, fill=(0.30, 0.55, 0.85))
            circle(cr, CX, GY + R + 4, R, fill=(0.35, 0.62, 0.35))
            glow(cr, CX, GY, 900, (0.6, 0.8, 1.0), 0.25 * space)
        else:
            rect(cr, -10, GY, W + 20, H - GY + 10, fill=(0.45, 0.70, 0.40))
            line(cr, -10, GY, W + 10, GY, 5, INK)
        # markers
        def alt_y(km):
            return GY - km * ppk
        tw_ = 0.06 * ppk
        if 6 < tw_ < 3000:
            th_ = 0.45 * ppk
            rect(cr, 1500 - tw_ / 2, GY - th_, tw_, th_, fill=(0.55, 0.62, 0.72), stroke=INK, lw=3)
            if 60 < GY - th_ < GY - 40:
                text(cr, "SKYSCRAPER ~0.5 KM", 1500, GY - th_ - 40, 32, face=FONT_TITLE, c=WHITE, outline=INK, ow=6)
        ev = 8.8 * ppk
        if 20 < ev < 4000:
            polyline(cr, [(300 - ev * 1.3, GY), (300, GY - ev), (300 + ev * 1.3, GY)], 4, INK, closed=True,
                     fill=(0.55, 0.52, 0.55))
            polyline(cr, [(300 - ev * 0.3, GY - ev * 0.77), (300, GY - ev), (300 + ev * 0.3, GY - ev * 0.77)], 3, INK,
                     closed=True, fill=WHITE)
            if GY - ev > 70:
                text(cr, "MT. EVEREST ~9 KM", 300, GY - ev - 36, 32, face=FONT_TITLE, c=WHITE, outline=INK, ow=6)
        for km, lab in ((2, "CLOUDS ~2 KM"), (11, "PLANES ~10 KM"), (100, "SPACE BEGINS ~100 KM")):
            y = alt_y(km)
            if 60 < y < GY - 30:
                a = clamp((GY - y) / 300) * clamp(y / 200)
                if km == 2:
                    for i in range(4):
                        P.cloud(cr, 260 + i * 470, y, 0.6, a=a * 0.9)
                elif km == 11:
                    jet(cr, 1500, y, 0.35, face=-1, body=WHITE)
                else:
                    line(cr, 0, y, W, y, 3, WHITE, a * 0.6, dash=[18, 14])
                text(cr, lab, {2: 1300, 11: 1380}.get(km, 140), y - (70 if km == 11 else 44), 32, face=FONT_TITLE,
                     c=WHITE, outline=INK, ow=6, align="left", a=a)
        grow = ease(prog(T, st5 + 0.3, max(0.5, t_pile - st5 - 0.3)))
        top_km = 1100 if kz >= 1 else min(1100, (GY + 200) / ppk * (grow if kz <= 0 else 1.0))
        colw = max(0.000156 * ppk, 60)
        ytop = alt_y(top_km)
        rect(cr, CX - colw / 2, ytop, colw, GY - ytop, fill=CASH, stroke=CASH_D, lw=3)
        if colw < 200:
            for i in range(int((GY - ytop) / 10) + 1):
                yy = GY - i * 10
                if 0 < yy < H:
                    line(cr, CX - colw / 2, yy, CX + colw / 2, yy, 1.5, CASH_D, 0.5)
        if kz <= 0 and 0 < grow < 1:
            for i in range(5):
                f = (T * 2.2 + i / 5) % 1
                bill(cr, CX + 140 * math.sin(i * 2.3) * (1 - f), lerp(-60, max(ytop, 0), f), 0.4, f * 3 + i,
                     flip=math.cos(f * 8 + i))
        hs = 0.0018 * ppk / 330
        if hs > 0.03:
            dude(cr, T, CX - colw / 2 - 160 * hs, GY, "point_up", s=hs, face=1, smile=0.6, gy=-0.8)
        if hs > 0.4:
            label_box(cr, "$100 BILLS", CX + colw / 2 + 170, GY - 250 * hs, 44, c=CASH_D, bg=WHITE, face=FONT_TITLE,
                      bold=False)
        t_ov = w("c2_05", "over twice")
        y_iss = alt_y(400)
        if 0 < y_iss < GY - 20:
            ki = K.pop(T, t_ov)
            if ki > 0:
                iss(cr, 1350, y_iss, 0.45 * max(0.01, ki), T)
                line(cr, CX + 40, y_iss, 1230, y_iss, 3, WHITE, 0.6, dash=[10, 8])
                text(cr, "SPACE STATION", 1350, y_iss + 80, 34, face=FONT_TITLE, c=WHITE, a=clamp(ki))
                text(cr, "~400 KM", 1350, y_iss + 122, 34, face=FONT_TITLE, c=WHITE, a=clamp(ki))
        if kz >= 1:
            kt = K.pop(T, t_km + 0.8)
            label_box(cr, "1,000+ KM", CX + 230, ytop + 10, 50, c=INK, bg=YELLOW, face=FONT_TITLE, bold=False,
                      scale=kt)
            kk = eout(prog(T, t_iss, 0.5))
            if kk > 0:
                text(cr, "OVER 2× HIGHER", 520, 360, 60, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, a=kk)
        # height readout
        if grow > 0:
            hk = min(top_km, (GY - max(ytop, 0)) / ppk)
            val = "1,000+ KM" if kz >= 1 else (f"{hk * 1000:,.0f} M" if hk < 1 else f"{min(hk, 999):,.0f} KM")
            rrect(cr, 1460, 50, 400, 100, 18, fill=WHITE, stroke=INK, lw=5, a=0.95)
            text(cr, "STACK HEIGHT", 1660, 78, 28, face=FONT_BOLD, c=GRAY)
            text(cr, val, 1660, 120, 46, face=FONT_TITLE, c=CASH_D)
    b.fx(st5 + 0.2, "papers", -10)
    b.fx(t_pile, "riser", -8, dur=3.0)
    b.fx(t_km + 0.8, "ding", -6)
    b.fx(t_iss - 0.3, "space", -12, dur=3.0)

    # 6-6b. ten thousand tons ~ the Eiffel Tower
    st6 = s("c2_06") - 0.15
    t_ton, t_eif = w("c2_06", "ten thousand"), w("c2_06b", "eiffel")

    @b.shot(st6, "fade", 0.3)
    def weigh(cr, t, d, T):
        fill_bg(cr, (0.95, 0.94, 0.90))
        vignette(cr, 0.16)
        with K.ken(cr, t, d, 1.0, 1.03, CX, 560):
            S.floor(cr, 960, (0.80, 0.78, 0.74))
            drop = ein(prog(T, t_eif - 0.5, 0.5))
            tilt = lerp(-0.22, 0.0, ease(prog(T, t_eif, 0.6))) + 0.02 * math.sin(T * 5) * (1 - prog(T, t_eif, 1.2))
            bx, by, L = CX, 380, 520
            polyline(cr, [(bx - 110, 960), (bx, 920), (bx + 110, 960)], 5, INK, closed=True, fill=GRAY)
            rect(cr, bx - 16, by, 32, 540, fill=GRAY, stroke=INK, lw=5)
            pans = []
            with xform(cr, bx, by, 1, tilt):
                rect(cr, -L - 10, -12, 2 * L + 20, 24, fill=(0.75, 0.75, 0.78), stroke=INK, lw=5)
                for k_ in (-1, 1):
                    pans.append((k_ * L * math.cos(tilt) + bx, by + k_ * L * math.sin(tilt)))
            circle(cr, bx, by, 22, fill=INK)
            for k_, (px, py) in zip((-1, 1), pans):
                line(cr, px, py, px - 150, py + 300, 4, INK)
                line(cr, px, py, px + 150, py + 300, 4, INK)
                polyline(cr, [(px - 220, py + 300), (px + 220, py + 300), (px + 180, py + 340), (px - 180, py + 340)],
                         5, INK, closed=True, fill=(0.75, 0.75, 0.78))
            lx, ly = pans[0]
            cash_pile(cr, lx, ly + 300, 0.42, rows=5, seed=8)
            text(cr, "$1 TRILLION", lx, ly + 400, 44, face=FONT_TITLE, c=CASH_D)
            text(cr, "IN $100 BILLS", lx, ly + 446, 30, face=FONT_BOLD, c=GRAY)
            rx, ry = pans[1]
            if T > t_eif - 0.5:
                eiffel(cr, rx, lerp(-200, ry + 300, drop), 0.52)
                text(cr, "THE EIFFEL TOWER", rx, ry + 400, 44, face=FONT_TITLE, a=clamp(drop * 2))
            kt = K.pop(T, t_ton)
            if kt > 0:
                with xform(cr, bx, 200, max(0.01, kt)):
                    rrect(cr, -240, -60, 480, 120, 18, fill=(0.12, 0.14, 0.12), stroke=INK, lw=6)
                    text(cr, "≈ 10,000 TONS", 0, 0, 58, face=FONT_TITLE, c=(0.4, 1.0, 0.5))
            if T > t_eif + 0.6:
                text(cr, "≈", bx, 760, 140, face=FONT_TITLE, c=RED, scale=K.pop(T, t_eif + 0.6))
    b.fx(t_ton, "ding", -8)
    b.fx(t_eif - 0.5, "whoosh", -10)
    b.fx(t_eif, "clank", -4)
    b.fx(t_eif + 0.6, "pop", -10)

    # 7. a million dollars a day: 2,700+ years
    st7 = s("c2_07") - 0.15
    t_2700 = w("c2_07", "two thousand")

    @b.shot(st7, "fade", 0.3)
    def spend(cr, t, d, T):
        speed = lerp(3.0, 14.0, ease(prog(T, st7, d)))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            k = day_night(T, 3.0)
            S.room(cr, T, wall=lerpc((0.90, 0.92, 0.86), (0.28, 0.30, 0.40), k),
                   floor_c=lerpc((0.70, 0.60, 0.50), (0.25, 0.22, 0.26), k), fy=900)
            sky_window(cr, 1650, 420, 360, 300, T, 3.0)
            cash_pile(cr, 420, 900, 0.75, rows=6, seed=12)
            f = (T * 3.0 / TAU) % 1.0
            J = dude(cr, T, 1100, 900, "hold", s=1.0, face=1, smile=0.4, a1f=lerp(40, 140, ease(f * 2) if f < 0.5 else 0),
                     a2f=30)
            if f < 0.5:
                money_bag(cr, J["hand_f"][0] + 30, J["hand_f"][1] + 60, 0.45, "$1M")
            else:
                ff = (f - 0.5) * 2
                money_bag(cr, lerp(J["hand_f"][0] + 30, 1650, ff), lerp(J["hand_f"][1] + 60, 440, ff) - 120 * math.sin(
                    ff * math.pi), 0.45 * (1 - ff * 0.6), "$1M")
            days = int((T - st7) * 3.0 / TAU * 1.0 * (1 + 40 * ease(prog(T, st7 + 2.0, d)))) + 1
            calendar(cr, 330, 360, 0.8, "DAY", f"{days:,}", c=RED)
        rrect(cr, 60, 960, 1800, 70, 20, fill=WHITE, stroke=INK, lw=5)
        text(cr, "YOUR TRILLION", 100, 995, 36, face=FONT_TITLE, align="left")
        frac = 1 - 0.003 * ease(prog(T, st7, d))
        rrect(cr, 440, 975, 1380, 40, 20, fill=LIGHT)
        rrect(cr, 440, 975, 1380 * frac, 40, 20, fill=GREEN)
        text(cr, "$1,000,000 EVERY DAY", CX, 170, 64, face=FONT_TITLE, c=CASH_D, a=eout(prog(t, 0.2, 0.4)))
        stamp(cr, "2,700+ YEARS", 1010, 340, T - t_2700, 84, c=RED, rot=0.05)
        del speed
    b.fx(st7 + 0.3, "swish", -12)
    b.fx(st7 + 2.4, "swish", -14)
    b.fx(st7 + 4.5, "swish", -14)
    b.fx(t_2700, "stamp", -4)

    # 8. your money outlives you
    st8 = s("c2_08") - 0.15
    t_out = w("c2_08", "outlive")

    @b.shot(st8, "fade", 0.4)
    def outlive(cr, t, d, T):
        vgrad(cr, (0.55, 0.62, 0.78), (0.85, 0.85, 0.90))
        with K.ken(cr, t, d, 1.0, 1.05, CX, 640):
            S.floor(cr, 900, (0.45, 0.62, 0.40))
            gravestone(cr, 430, 830, 1.1, ("R.I.P.", "YOU"))
            for i, c in enumerate((RED, YELLOW, PURPLE)):
                circle(cr, 380 + i * 50, 822, 14, fill=c, stroke=INK, w=3)
            cash_pile(cr, 1450, 830, 0.62, rows=6, seed=21)
            P2.sign(cr, 1450, 470, 0.9, "STILL\nHERE!", c=WHITE)
            gy_ = 700 + 14 * math.sin(T * 2)
            dude(cr, T, 760, gy_, "wave", s=0.8, face=1, smile=0.7, ink=(0.30, 0.36, 0.58), fill=(0.95, 0.97, 1.0),
                 alpha=0.8, a2f=40 + 20 * math.sin(T * 6))
            ellipse(cr, 760 - 4, gy_ - 330 * 0.8 - 10, 36, 10, stroke=GOLD, w=6)
        rrect(cr, 60, 880, 1800, 170, 20, fill=WHITE, stroke=INK, lw=5, a=0.95)
        text(cr, "YOUR LIFE", 340, 925, 34, face=FONT_TITLE, align="right")
        rrect(cr, 370, 908, 80, 34, 17, fill=BLUE)
        text(cr, "YOUR MONEY", 340, 1000, 34, face=FONT_TITLE, align="right")
        km = ease(prog(T, st8 + 0.3, 1.6))
        rrect(cr, 370, 983, 1460 * km + 10, 34, 17, fill=GREEN)
        if km >= 1:
            text(cr, "...THOUSANDS OF YEARS →", 1800, 1000, 30, face=FONT_TITLE, c=WHITE, align="right")
        stamp(cr, "OUTLIVES YOU", CX, 200, T - t_out, 80, c=RED, rot=-0.05)
    b.fx(st8 + 0.3, "rise", -12)
    b.fx(t_out, "stamp", -6)
    return b.result()
