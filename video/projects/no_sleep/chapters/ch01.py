"""No Sleep - Chapter 1: The Hook (0:00-0:40)."""
from video.projects.no_sleep.chapters._n import *  # noqa: F401,F403

DARK_TAG = True


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 70, 0.5), ("c1_02", "playful", "playful", 104, 0.6),
                        ("c1_05", "wonder", "wonder", 92, 0.65), ("c1_06", "mystery", "mystery", 70, 0.55),
                        (tl.e("c1_07") - 0.2, "uplift", "mystery", 96, 0.9)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. asleep... then never again
    t_never = w("c1_01", "never")

    @b.shot(0)
    def wake(cr, t, d, T):
        awake = T > t_never
        with K.ken(cr, t, d, 1.1, 1.28, 820, 660):
            night_room(cr, T, lamp=0.0, win=(1430, 360))
            bed2(cr, T, 820, 880, 1.45, who="sit" if awake else "sleep", ink=NI, fill=NF, z=False,
                 kw=dict(eye=1.45, smile=0.9, browy=0.6, mo=0.3 * (1 - prog(T, t_never + 0.5, 0.4))))
            nightstand_lamp(cr, 1290, 880, 0.9, on=0.0, ink=NI)
            digital_clock(cr, 1290, 700, "3:00", 0.55)
            if not awake:
                zzz(cr, 640, 560, T, 1.6, c=NI)
            else:
                hx, hy = 820 - 150 * 1.45, 880 - 248 * 1.45
                burst(cr, hx, hy - 30, T - t_never, n=16, dist=260, size=10, c=YELLOW, dur=0.7)
                for k_ in (-1, 1):
                    glow(cr, hx + k_ * 10, hy - 4, 40, (0.6, 0.9, 1.0), 0.5 * prog(T, t_never, 0.3))
        vignette(cr, 0.45)
    b.fx(0.3, "snore", -12, dur=1.5)
    b.fx(t_never, "blink", -6)
    b.fx(t_never + 0.05, "sparkle", -12)

    # 2. no more alarms, yawning, dragging out of bed
    st2 = s("c1_02") - 0.15
    words2 = ("alarms", "yawning", "dragging")

    def ic_alarm(cr, T):
        P.alarm_clock(cr, 0, -10, 1.15, T, ring=1.0)

    def ic_yawn(cr, T):
        P.desk(cr, 30, 110, 260, 1.0)
        p = sm.pose("sit", x=-30, s=0.62, face=1, a1f=150, a2f=30, a1b=60, a2b=40, mo=0.9, blink=0.8, head=-12,
                    smile=0.0)
        p["y"] = 110 - 96
        sm.draw(cr, sm.idle(p, T, 2), acc=HERO)
        P.book(cr, 60, -50, 0.5, open_=1.0)
        text(cr, "YAWN", 105, -150, 34, face=FONT_TITLE, c=GRAY, rot=0.1)

    def ic_drag(cr, T):
        bed2(cr, T, 40, 110, 0.42, who="empty")
        p = sm.pose("slump", x=-90, s=0.6, face=1, lean=35, a1f=120, a2f=10, a1b=100, smile=-0.7, brow=-0.6)
        p = sm.on_ground(sm.walk(p, T, 0.5, 0.4), 110)
        sm.draw(cr, p, acc=HERO)

    items = []
    for fn_, lab, wd in ((ic_alarm, "ALARMS", "alarms"), (ic_yawn, "YAWNING IN CLASS", "yawning"),
                         (ic_drag, "DRAGGING OUT OF BED", "dragging")):
        ta = w("c1_02", wd)

        def drawx(cr, T, fn_=fn_, ta=ta):
            fn_(cr, T)
            cross_out(cr, 0, 0, 125, prog(T, ta + 0.45, 0.3), 18)
        items.append((drawx, lab, ta))
    b.add(st2, K.icons("NO MORE...", items, bg=(0.97, 0.94, 0.86), y=540, size=1.1, label_size=36), "slide", 0.4)
    b.fx(st2, "whoosh", -10)
    b.fx(w("c1_02", "alarms") - 0.1, "alarm", -14, dur=0.6)
    for wd in words2:
        b.fx(w("c1_02", wd) + 0.45, "scratch_out", -12)

    # 3. eight extra hours a day -> almost 3,000 a year
    st3 = s("c1_03") - 0.15
    t_eight, t_three = w("c1_03", "eight extra"), w("c1_03", "three thousand")

    @b.shot(st3, "fade", 0.3)
    def ring(cr, t, d, T):
        night_bg(cr, T, 0.6)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            kb = ease(prog(T, t_eight, 1.2))
            day_ring(cr, 600, 580, 250, T, k_bonus=kb, k_in=ease(prog(t, 0.05, 0.7)),
                     center="24 HOURS" if kb < 0.5 else "+8 HOURS", center_c=WHITE if kb < 0.5 else BONUS,
                     center_size=58)
            if kb <= 0:
                ks = clamp(prog(t, 0.8, 0.4))
                text(cr, "SLEEP", 600 + 190, 580 - 330, 34, face=FONT_TITLE, c=(0.6, 0.68, 1.0), a=ks)
            k1 = K.pop(T, t_eight)
            if k1 > 0:
                with xform(cr, 1380, 330, max(0.01, k1)):
                    text(cr, "+8 HOURS", 0, 0, 110, face=FONT_TITLE, c=BONUS, outline=INK, ow=10)
                    text(cr, "EVERY DAY", 0, 90, 46, face=FONT_TITLE, c=WHITE)
            kx = eout(prog(T, t_eight + 1.2, 0.4))
            if kx > 0:
                text(cr, "× 365 DAYS", 1380, 500, 50, face=FONT_BOLD, c=NI, a=kx)
            k2 = K.pop(T, t_three)
            if k2 > 0:
                with xform(cr, 1380, 680, max(0.01, k2)):
                    text(cr, "≈ 2,920", 0, 0, 140, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10)
                    text(cr, "EXTRA HOURS A YEAR", 0, 110, 46, face=FONT_TITLE, c=WHITE)
                text(cr, "(almost 3,000!)", 1380, 870, 40, face=FONT_HAND, bold=True, c=NI, a=clamp(k2))
        vignette(cr, 0.4)
    b.fx(t_eight, "rise", -10)
    b.fx(t_three, "coins", -10)

    # 4. around twenty extra years awake
    st4 = s("c1_04") - 0.15
    t_twenty, t_awake = w("c1_04", "twenty"), w("c1_04", "awake")

    @b.shot(st4, "fade", 0.3)
    def years(cr, t, d, T):
        vgrad(cr, (0.10, 0.10, 0.20), (0.03, 0.03, 0.07))
        stars(cr, T, n=140, alpha=0.5)
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            text(cr, "OVER A LIFETIME", CX, 190, 64, face=FONT_TITLE, c=WHITE, a=eout(prog(t, 0.05, 0.4)))
            P2.hourglass(cr, 470, 600, 1.5, p=prog(T, st4, d * 0.9), t=T, c=(0.45, 0.85, 0.70))
            nhero(cr, T, 760, 900, "surprised" if T > t_twenty else "point", face=1, s=0.9, eye=1.2)
            k = K.pop(T, t_twenty, 0.5)
            if k > 0:
                glow(cr, 1330, 520, 420, YELLOW, 0.25 * clamp(k))
                text(cr, "≈ 20 YEARS", 1330, 520, 150, face=FONT_TITLE, c=YELLOW, outline=INK, ow=12,
                     scale=max(0.01, k))
                burst(cr, 1330, 520, T - t_twenty, n=24, dist=520, size=9, c=WHITE, dur=0.9, shape="line")
            ka = eout(prog(T, t_awake - 0.2, 0.4))
            text(cr, "EXTRA YEARS AWAKE", 1330, 680, 60, face=FONT_TITLE, c=WHITE, a=ka)
            text(cr, "(roughly, in a long life)", 1330, 770, 40, face=FONT_HAND, bold=True, c=NI, a=ka)
        vignette(cr, 0.4)
    b.fx(t_twenty, "boom_soft", -8)

    # 5. learn, build, play, explore while the world sleeps
    st5 = s("c1_05") - 0.15
    acts = [("LEARN", "learn"), ("BUILD", "build"), ("PLAY", "play"), ("EXPLORE", "explore")]
    t_acts = [w("c1_05", wd) for _, wd in acts]
    t_asleep, t_dream = w("c1_05", "asleep"), w("c1_05", "dreaming")

    @b.shot(st5, "fade", 0.3)
    def world_sleeps(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            night_bg(cr, T, 0.9)
            moon(cr, 1730, 380, 56)
            S.floor(cr, 880, (0.10, 0.11, 0.14), (0.3, 0.3, 0.35), 4)
            for i, (hx, sc, rf) in enumerate(((180, 1.3, (0.35, 0.18, 0.2)), (470, 1.1, (0.2, 0.25, 0.4)),
                                               (1450, 1.15, (0.25, 0.3, 0.2)), (1760, 1.35, (0.35, 0.25, 0.15)))):
                P.house(cr, hx, 880, sc, lit=0.0, c=(0.20, 0.21, 0.28), roof=rf)
                if T > t_asleep:
                    zzz(cr, hx + 20 * sc, 880 - 200 * sc, T, 1.0, c=NI, seed=i, a=prog(T, t_asleep + i * 0.15, 0.4))
                kd = K.pop(T, t_dream + i * 0.12)
                if kd > 0:
                    by = 880 - 330 * sc
                    thought_bubble(cr, hx + 40, by, 150, 110, hx, 880 - 160 * sc, scale=kd, t=T)
                    with xform(cr, hx + 40, by, 0.6 * max(0.01, kd)):
                        mem_icon(cr, ["rocket", "cat", "pizza", "star"][i])
            idx = sum(1 for ta in t_acts if T >= ta - 0.1) - 1
            gx = CX
            if idx <= 0:
                J = nhero(cr, T, gx, 900, "hold", face=1, smile=0.8, gy=0.6)
                P.book(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 25, 0.6, open_=1.0)
            elif idx == 1:
                P.robot(cr, gx + 190, 900, 0.55, T)
                sw = math.sin(T * 12)
                J = nhero(cr, T, gx, 900, "point", face=1, a1f=70 + 30 * sw, a2f=20, smile=0.8)
                with xform(cr, J["hand_f"][0], J["hand_f"][1], 1.0, -0.6 + 0.5 * sw):
                    line(cr, 0, 0, 0, -70, 8, (0.6, 0.45, 0.3))
                    rrect(cr, -28, -92, 56, 26, 6, fill=GRAY, stroke=NI, lw=3)
            elif idx == 2:
                J = nhero(cr, T, gx, 900, "hold", face=1, smile=1.0, a1f=70 + 10 * math.sin(T * 10), a2f=40,
                          a1b=40, a2b=80, mo=0.4)
                guitar(cr, J["hip"][0] + 10, J["hip"][1] - 70, 0.55, rot=-1.0)
                for i in range(3):
                    ph = (T * 0.8 + i / 3) % 1
                    text(cr, "♪", gx + 120 + ph * 120, 560 - ph * 140, 44, face=FONT_BOLD, c=YELLOW, a=1 - ph)
            else:
                P.telescope(cr, gx + 130, 900, 1.0, rot=-0.75)
                nhero(cr, T, gx - 30, 900, "point_up", face=1, smile=0.9, gx=1.0)
            for i, ((lab, _), ta) in enumerate(zip(acts, t_acts)):
                k = K.pop(T, ta)
                if k > 0:
                    chip(cr, lab, 420 + i * 360, 200, 52, bg=YELLOW, scale=k)
        vignette(cr, 0.35)
    for ta in t_acts:
        b.fx(ta, "pop", -10)
    b.fx(t_asleep, "night", -14, dur=2.5)

    # 6. but here's the question
    b.add(s("c1_06") - 0.2, K.real_question(s("c1_06")), "black", 0.4)
    b.fx(s("c1_06"), "tick", -8)
    b.fx(s("c1_06") + 0.5, "tock", -8)

    # 7. wasted time... or secretly essential?
    st7 = s("c1_07") - 0.1
    t_or = w("c1_07", "or is it")

    def wasted(cr, cx, T):
        bed2(cr, T, cx - 40, 860, 1.05, who="sleep", seed=2)
        with xform(cr, cx + 270, 560, 1.0):
            rect(cr, -70, -40, 140, 160, fill=(0.6, 0.62, 0.66), stroke=INK, lw=5)
            rect(cr, -82, -60, 164, 26, fill=(0.5, 0.52, 0.56), stroke=INK, lw=5)
            text(cr, "TRASH", 0, 50, 30, face=FONT_TITLE, c=WHITE)
        f = (T * 0.8) % 1
        cy_ = lerp(280, 520, ein(f))
        P.clock(cr, cx + 270, cy_, 38, T, hours=11, speed=40)
        label_box(cr, "8 HOURS", cx + 270, cy_ - 70, 26, c=INK, bg=WHITE)

    def secret(cr, cx, T):
        radial_lines(cr, cx, 520, T, n=24, c=(0.6, 0.8, 1.0), a=0.12, w=20)
        brain_big(cr, cx, 520, 2.2, T, glow_a=0.6)
        for i in range(3):
            P.gear(cr, cx - 120 + i * 120, 520 + (40 if i % 2 else -40), 34, 8, T * (1 if i % 2 else -1) * 1.4,
                   fill=(0.9, 0.9, 0.95))
        for i in range(5):
            a = T * 0.6 + i * 1.26
            text(cr, "?", cx + math.cos(a) * 330, 560 + math.sin(a) * 220, 70, face=FONT_TITLE, c=YELLOW, a=0.8)

    b.add(st7, K.split(dict(title="WASTED TIME?", bg=(0.97, 0.93, 0.84), draw=wasted),
                       dict(title="SECRETLY ESSENTIAL?", bg=(0.08, 0.10, 0.22), draw=secret), t_or), "fade", 0.3)
    b.fx(st7, "chime", -10)
    b.fx(t_or, "glitch", -8)

    # 8. title
    st8 = e("c1_07") - 0.2

    @b.shot(st8, "cut")
    def title(cr, t, d, T):
        TITLE(cr, t)
    b.fx(st8, "whoosh", -4)
    b.fx(st8 + 0.5, "boom", 0)
    b.fx(st8 + 0.55, "shimmer", -8)
    return b.result()
