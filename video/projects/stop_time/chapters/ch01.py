"""Stop Time - Chapter 1: The Hook (0:00-0:40)."""
from video.projects.stop_time.chapters._s import *  # noqa: F401,F403

DARK_TAG = True

RAIN_SKY = ((0.66, 0.74, 0.84), (0.86, 0.88, 0.90))


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 100, 0.45), (3.0, "cold", "cold", 70, 0.45),
                        ("c1_04", "uplift", "uplift", 100, 0.65), ("c1_06", "mystery", "mystery", 70, 0.55),
                        (tl.e("c1_07") + 0.2, "uplift", "mystery", 96, 0.9)])


UMB = [RED, YELLOW, BLUE, GREEN, ORANGE]
# pedestrians: (x at the freeze, ground y, face, scale, accessories, umbrella colour or None)
WALKERS = [(150, 925, 1, 0.9, ("ponytail",), RED), (430, 1010, -1, 0.95, ("cap",), None),
           (640, 905, 1, 0.85, ("hat",), YELLOW), (1290, 915, -1, 0.9, ("glasses",), BLUE),
           (1560, 1020, 1, 0.95, ("bun",), None), (1800, 930, -1, 0.88, (), GREEN)]


def walkers(cr, wt, t_ref, specs=WALKERS):
    """Pedestrians (some with umbrellas) walking in the rain; they stop when the world clock wt stops."""
    out = []
    for i, (xf, y, f, s, acc, uc) in sorted(enumerate(specs), key=lambda q: q[1][1]):
        xx = xf + f * sm.stride(0.7, s) * (wt - t_ref)
        p = sm.walk(sm.pose("stand", x=xx, face=f, s=s, smile=0.3), wt + i * 0.37, 0.7)
        if uc:
            p = sm.apply(p, a1f=95, a2f=70)
        p = sm.on_ground(p, y)
        J = sm.draw(cr, p, acc=acc)
        if uc:
            umbrella(cr, J["hand_f"][0], J["hand_f"][1] + 30, 0.9 * s, uc, rot=-0.12 * f)
        out.append(J)
    return out


def street_world(cr, T, wt, gy=720, cars=True, t_ref=0.0):
    S.city(cr, T, 0, sky=RAIN_SKY, gy=gy)
    for i in range(3):
        P.cloud(cr, 300 + i * 650, 110 + (i % 2) * 40, 1.3, c=(0.80, 0.83, 0.88))
    clock_tower(cr, 1660, gy, 0.85, wt, hours=8, minutes=59)
    flock(cr, wt - t_ref, n=5, x0=520, y0=230, seed=3, s=0.9, speed=140)
    # road, curb and sidewalk
    rect(cr, -400, gy, W + 800, 110, fill=(0.40, 0.41, 0.45))
    for i in range(-2, 12):
        rect(cr, i * 220, gy + 52, 110, 8, fill=WHITE, a=0.8)
    if cars:
        P.car(cr, 700 + (wt - t_ref) * 420, gy + 92, 1.25, c=RED, t=wt)
        P.car(cr, 1450 - (wt - t_ref) * 330, gy + 70, 1.1, c=(0.25, 0.55, 0.85), t=wt, face=-1)
    rect(cr, -400, gy + 110, W + 800, 16, fill=LIGHT, stroke=INK, lw=4)
    rect(cr, -400, gy + 126, W + 800, 800, fill=(0.84, 0.83, 0.80))
    for i in range(-3, 14):
        line(cr, i * 200, gy + 126, i * 200 - 160, H + 200, 3, MID, 0.4)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. a busy rainy street -> snap -> everything stops
    t_raise = w("c1_01", "snap") - 0.1
    t_snap = w("c1_01", "stop time")
    HX, GY = 960, 985

    def hero_p(T):
        k = ease(prog(T, t_raise, 0.4))
        p = sm.pose("stand", x=HX, face=1, s=1.08, a1f=lerp(12, SNAP_KW["a1f"], k), a2f=lerp(10, SNAP_KW["a2f"], k),
                    smile=0.2 + 0.5 * k, brow=0.3 * k, gx=0.4 * k, gy=-0.3 * k)
        return sm.on_ground(sm.idle(p, T, 1), GY)

    @b.shot(0)
    def street(cr, t, d, T):
        wt = wtime(T, t_snap)
        p = hero_p(T)
        J0 = sm.joints(p)
        hx, hy = J0["hand_f"]
        with K.ken(cr, t, d, 1.0, 1.06, HX, 640):
            street_world(cr, T, wt, t_ref=t_snap)
            walkers(cr, wt, t_snap)
            rain(cr, T, t_snap, n=230, seed=1, wave=(hx, hy), y1=1100, s=1.15)
            freeze_wave(cr, T, t_snap, hx, hy)
            if T > t_snap:
                hero_bubble(cr, J0, T, fk(T, t_snap + 0.2))
            sm.draw(cr, p, acc=HERO)
            snap_fx(cr, hx, hy, T - t_snap)
        frozen_hud(cr, fk(T, t_snap + 0.3), T)
    b.fx(0.0, "traffic", -20, dur=t_snap + 0.1)
    for i, tt in enumerate((0.35, 1.35, 2.35)):
        b.fx(tt, "tick" if i % 2 == 0 else "tock", -14)
    b.fx(t_snap, "snap", -2)
    b.fx(t_snap + 0.04, "slowmo", -6)
    b.fx(t_snap + 0.35, "shimmer", -12)

    # 2a. raindrops hang like glass beads
    st2 = s("c1_02") - 0.15
    t_birds = w("c1_02", "birds") - 0.1
    t_cof = w("c1_02", "coffee") - 0.1

    @b.shot(st2, "zoom", 0.5)
    def beads(cr, t, d, T):
        with K.ken(cr, t, d, 1.25, 1.45, 900, 520):
            street_world(cr, T, t_snap + SLOW / 2, t_ref=t_snap)
            walkers(cr, t_snap + SLOW / 2, t_snap)
            rain(cr, T, t_snap - 100, n=230, seed=1, y1=1100, s=1.15)
            frost(cr)
        r = rng(9)
        for i in range(16):
            x, y = r.uniform(80, 1840), r.uniform(80, 1000)
            sz = r.uniform(2.6, 5.0)
            drop(cr, x, y + 6 * math.sin(T * 0.6 + i), sz)
            tw = clamp(math.sin(T * 2.5 + i * 1.7))
            if tw > 0.6:
                star_shape(cr, x - 3 * sz, y - 2 * sz, 16 * (tw - 0.6) * 2.5, points=4, inner=0.25, fill=WHITE)
        label_box(cr, "LIKE GLASS BEADS", CX, 960, 48, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                  scale=K.pop(T, w("c1_02", "glass")))
        frozen_hud(cr, 1.0, T)
    b.fx(st2, "whoosh", -12)
    b.fx(w("c1_02", "glass"), "sparkle", -10)

    # 2b. birds frozen mid-flight
    @b.shot(t_birds, "slide", 0.35)
    def birds(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 500):
            S.vgrad(cr, (0.62, 0.72, 0.86), (0.84, 0.88, 0.92))
            for i in range(4):
                P.cloud(cr, 200 + i * 520, 180 + (i % 2) * 120, 1.6, c=(0.85, 0.88, 0.92))
            P.skyline(cr, -300, 1080, 2600, 260, seed=51, fill=(0.62, 0.65, 0.72))
            for i, (x, y, s_, ph) in enumerate(((420, 330, 2.6, 0.4), (880, 520, 3.4, 2.2), (1350, 300, 2.2, 1.2),
                                                (1650, 600, 2.8, 4.0), (640, 760, 1.8, 3.1))):
                bird(cr, x, y, s_, ph, face=1 if i % 2 else -1)
            rain(cr, T, t_snap - 100, n=90, seed=4, y1=1100, s=1.6)
            frost(cr)
            p = sm.pose("stand", x=1600, face=-1, s=1.9, gx=-0.4, gy=-1.0, smile=0.5, eye=1.25, mo=0.3, head=-8)
            p = head_at(sm.idle(p, T, 2), 1600, 960)
            sm.draw(cr, p, acc=HERO)
        label_box(cr, "MID-FLIGHT", 560, 960, 48, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                  scale=K.pop(T, w("c1_02", "mid-flight")))
        frozen_hud(cr, 1.0, T)
    b.fx(t_birds, "flutter", -14)

    # 2c. a coffee spill stops halfway to the floor
    @b.shot(t_cof, "slide", 0.35)
    def coffee(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, 900, 640):
            S.room(cr, T, wall=(0.93, 0.86, 0.76), floor_c=(0.62, 0.45, 0.32), fy=900)
            P.window(cr, 420, 360, 420, 300, T, sky=(0.66, 0.74, 0.84))
            rect(cr, 1150, 150, 300, 70, fill=(0.35, 0.22, 0.14), stroke=INK, lw=5)
            text(cr, "CAFE", 1300, 185, 44, face=FONT_TITLE, c=WHITE)
            # table
            rect(cr, 560, 600, 400, 26, fill=(0.62, 0.42, 0.26), stroke=INK, lw=5)
            line(cr, 760, 626, 760, 900, 10, INK)
            line(cr, 680, 900, 840, 900, 10, INK)
            P.coffee(cr, 640, 600, 0.7, steam=False)
            coffee_spill(cr, 900, 600, 1.5, 0.5, fall=190)
            # the person who bumped the table, frozen in a gasp
            statue(cr, 0.3, 470, 900, "surprised", face=1, s=1.0, acc=("glasses",), seed=4)
            frost(cr)
            J = K.hero(cr, T, 1320, 900, "point", face=-1, s=1.0, smile=0.7, eye=1.2, lean=12, a1f=75, gx=-0.6, gy=0.3)
            hero_bubble(cr, J, T, 0.8)
        kh = K.pop(T, w("c1_02", "halfway"))
        if kh > 0:
            label_box(cr, "HALFWAY TO THE FLOOR", 1180, 980, 44, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                      scale=max(0.01, kh))
        frozen_hud(cr, 1.0, T)
    b.fx(t_cof, "pour", -14)

    # 3. everyone stands perfectly still, except you
    st3 = s("c1_03") - 0.15
    t_exc = w("c1_03", "except you")

    @b.shot(st3, "fade", 0.3)
    def except_you(cr, t, d, T):
        wt0 = 0.5
        with K.ken(cr, t, d, 1.12, 1.0, CX, 640):
            S.city(cr, T, 300, sky=RAIN_SKY, gy=780)
            frozen_people(cr, wt0, n=9, y0=840, y1=1060, seed=8, s0=0.7, s1=0.95, x0=-150, x1=680)
            frozen_people(cr, wt0, n=8, y0=840, y1=1060, seed=12, s0=0.7, s1=0.95, x0=1350, x1=2100)
            # a jogger frozen mid-stride, both feet off the ground
            p = sm.run(sm.pose("stand", x=420, face=1, s=0.95), 0.18)
            p = sm.on_ground(p, 980)
            p["y"] -= 40
            sm.draw(cr, p, acc=("cap",))
            rain(cr, T, -100, n=110, seed=6, y1=1100)
            frost(cr, 1.25)
            x = lerp(820, 1080, ease(prog(T, st3, 3.0)))
            J = K.hero(cr, T, x, 1000, "stand" if T < t_exc else "wave", face=1, walk=0.9 if T < t_exc - 0.2 else 0.0,
                       smile=0.6, s=1.0)
            hero_bubble(cr, J, T, 1.0, glow_a=0.2 + 0.25 * eout(prog(T, t_exc, 0.4)))
        k = K.pop(T, t_exc)
        if k > 0:
            hx = lerp(820, 1080, ease(prog(T, st3, 3.0)))
            callout(cr, "EXCEPT YOU", hx + 360, 300, hx + 80, 560, k, size=56)
        frozen_hud(cr, 1.0, T)
    b.fx(st3, "footsteps", -14, dur=2.4)
    b.fx(t_exc, "ding", -8)

    # 3b. the whole planet, paused
    st3b = s("c1_03b") - 0.15
    t_pause = w("c1_03b", "paused")

    @b.shot(st3b, "zoom", 0.5)
    def planet(cr, t, d, T):
        S.space(cr, 0.0, drift=0)
        with K.ken(cr, t, d, 1.0, 1.08, CX, 500):
            glow(cr, CX, 500, 520, CYAN, 0.25)
            P.globe(cr, CX, 500, 330, 2.0)
            frost(cr, 0.6)
        k = K.pop(T, t_pause)
        if k > 0:
            with xform(cr, CX, 500, max(0.01, k)):
                circle(cr, 0, 0, 120, fill=BLACK, a=0.35)
            pause_icon(cr, CX, 500, 1.1 * max(0.01, k), c=WHITE)
        # a video-player bar along the bottom, stopped
        rrect(cr, 160, 960, 1600, 14, 7, fill=(0.4, 0.4, 0.5))
        rrect(cr, 160, 960, 700, 14, 7, fill=RED)
        circle(cr, 860, 967, 16, fill=RED, stroke=WHITE, w=4)
        text(cr, "PAUSED", CX, 880, 64, face=FONT_TITLE, c=WHITE, a=clamp(k), scale=max(0.01, k))
    b.fx(t_pause, "blip", -6)

    # 4. no deadlines, no waiting, all the time you want
    st4 = s("c1_04") - 0.15
    t_dl, t_wait, t_much = w("c1_04", "deadlines"), w("c1_04", "waiting"), w("c1_04", "as much time")
    t_when, t_where = w("c1_04", "whenever"), w("c1_04", "wherever")

    def ic_deadline(cr, T):
        rrect(cr, -110, -100, 220, 210, 14, fill=WHITE, stroke=INK, lw=6)
        rect(cr, -110, -100, 220, 56, fill=RED, stroke=INK, lw=6)
        text(cr, "DEADLINE", 0, -72, 30, face=FONT_TITLE, c=WHITE)
        text(cr, "FRI", 0, 30, 80, face=FONT_TITLE)
        x_out(cr, 0, 0, prog(T, t_dl + 0.35, 0.4), 120)

    def ic_wait(cr, T):
        for i in range(4):
            p = sm.on_ground(sm.pose("stand", x=-110 + i * 70, s=0.42, face=1, smile=-0.4, brow=-0.5), 100)
            sm.draw(cr, p, acc=[("cap",), (), ("ponytail",), ("hat",)][i])
        ang = T * 6
        for j in range(8):
            a = ang + j * TAU / 8
            circle(cr, 100 + math.cos(a) * 34, -110 + math.sin(a) * 34, 6, fill=INK, a=0.2 + 0.8 * j / 8)
        x_out(cr, 0, 0, prog(T, t_wait + 0.35, 0.4), 120)

    def ic_unlimited(cr, T):
        stopwatch(cr, 0, -10, 90, 12.0, glow_a=0.4)
        text(cr, "∞", 0, 30, 70, face=FONT_BOLD, c=BLUE)

    @b.shot(st4, "fade", 0.3)
    def unlimited(cr, t, d, T):
        fill_bg(cr, (0.92, 0.95, 0.99))
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "NO MORE...", CX, 140, 60, face=FONT_TITLE, a=eout(prog(t, 0.05, 0.4)))
            for i, (fn_, lab, ta) in enumerate(((ic_deadline, "NO DEADLINES", t_dl), (ic_wait, "NO WAITING", t_wait),
                                                (ic_unlimited, "ALL THE TIME YOU WANT", t_much))):
                k = K.pop(T, ta)
                if k <= 0:
                    continue
                x = 420 + i * 540
                with xform(cr, x, 460, max(0.01, k)):
                    fn_(cr, T)
                text(cr, lab, x, 640, 42, face=FONT_BOLD, a=clamp(k))
            for lab, ta, x in (("ANYTIME", t_when, 700), ("ANYWHERE", t_where, 1220)):
                k = K.pop(T, ta)
                if k > 0:
                    label_box(cr, lab, x, 840, 64, c=WHITE, bg=BLUE, face=FONT_TITLE, bold=False, scale=k)
    for ta in (t_dl, t_wait, t_much, t_when, t_where):
        b.fx(ta, "pop", -10)
    b.fx(t_dl + 0.35, "scratch", -14)
    b.fx(t_wait + 0.35, "scratch", -14)

    # 5. explore anywhere, fix any mistake, finish your homework
    st5 = s("c1_05") - 0.15
    t_exp, t_fix, t_hw = w("c1_05", "explore"), w("c1_05", "fix"), w("c1_05", "homework")

    def p_explore(cr, T):
        S.vgrad(cr, (0.55, 0.75, 0.95), (0.85, 0.93, 0.98))
        P.sun(cr, 420, 110, 50, 0.0)
        # a giant wave, frozen as it curls over
        pts = bezier_pts([(-20, 620), (-20, 420), (120, 300), (300, 250), (450, 300), (500, 400), (430, 450),
                          (390, 380), (330, 400), (340, 620)], 50)
        polyline(cr, pts + [(-20, 620)], 6, INK, closed=True, fill=(0.20, 0.55, 0.85))
        polyline(cr, bezier_pts([(90, 330), (250, 255), (420, 290), (480, 380)], 20), 14, WHITE, 0.9)
        for i in range(14):
            r = rng(i)
            drop(cr, 440 + r.uniform(-70, 60), 380 + r.uniform(-20, 160), 1.5)
        rect(cr, -20, 560, 600, 80, fill=(0.15, 0.45, 0.75))
        frost(cr)
        J = K.hero(cr, T, 220, 292, "cheer", face=1, s=0.62, smile=1.0)
        hero_bubble(cr, J, T, 0.7, s=0.62)

    def p_fix(cr, T):
        fill_bg(cr, (0.88, 0.86, 0.82))
        rect(cr, 0, 470, 520, 200, fill=(0.75, 0.73, 0.70))
        line(cr, 0, 470, 520, 470, 5, INK)
        p = sm.pose("stand", x=150, face=1, s=0.8, smile=0.2, gx=0.6)
        p = sm.walk(p, 0.62, 1.0)
        p = sm.on_ground(p, 480)
        sm.draw(cr, p, acc=("hat",))
        frost(cr)
        k = ease(prog(T, t_fix + 0.3, 0.9))
        bx, by = lerp(255, 430, k), lerp(478, 470, k)
        J = K.hero(cr, T, lerp(330, 470, k), 480, "point_down", face=-1, s=0.75, lean=30, smile=0.7)
        with xform(cr, bx, by, 0.9, -0.2):
            polyline(cr, bezier_pts([(-40, 0), (-20, -24), (0, -6), (20, -24), (40, 0)], 12) + [(-40, 0)], 4, INK,
                     closed=True, fill=YELLOW)
        if k >= 1:
            check(cr, 300, 220, 2.2, p=prog(T, t_fix + 1.2, 0.4))
        del J

    def p_homework(cr, T):
        fill_bg(cr, (0.95, 0.92, 0.86))
        P.clock(cr, 400, 110, 60, 0.0, hours=11, minutes=58, seconds=True)
        P.desk(cr, 230, 520, 360)
        P.chair(cr, 350, 520, 0.75, face=-1)
        for i in range(6):
            rect(cr, 120 + (i % 2) * 6, 352 - i * 26, 150, 24, fill=[RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE][i],
                 stroke=INK, lw=3)
        frost(cr)
        p = sm.pose("sit", x=330, face=-1, s=0.75, a1f=70, a2f=40, smile=0.8)
        p["y"] = 520 - 118
        J = sm.draw(cr, sm.idle(p, T, 3), acc=HERO)
        hero_bubble(cr, J, T, 0.6, s=0.7)
        if T > t_hw + 0.3:
            stamp(cr, "DONE!", 260, 200, T - t_hw - 0.3, 70, c=GREEN, rot=-0.15)

    b.add(st5, K.three_paths([("EXPLORE", BLUE, p_explore, t_exp), ("FIX MISTAKES", ORANGE, p_fix, t_fix),
                              ("HOMEWORK", GREEN, p_homework, t_hw)], bg=(0.92, 0.95, 0.99)), "slide", 0.4)
    for ta in (t_exp, t_fix, t_hw):
        b.fx(ta, "pop", -10)
    b.fx(t_hw + 0.3, "stamp", -10)

    # 6. but here's the question
    b.add(s("c1_06") - 0.2, K.real_question(s("c1_06")), "black", 0.4)
    b.fx(s("c1_06"), "tick", -8)
    b.fx(s("c1_06") + 0.5, "tock", -8)

    # 7. most powerful person alive... or all alone?
    st7 = s("c1_07") - 0.1
    t_or = w("c1_07", "or trapped")

    def powerful(cr, cx, T):
        radial_lines(cr, cx, 420, T, n=24, c=YELLOW, a=0.35, w=26)
        rect(cr, cx - 160, 820, 320, 90, fill=GOLD, stroke=INK, lw=6)
        J = K.hero(cr, T, cx, 820, "cheer", s=1.05, smile=1.0)
        stopwatch(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 70, 60, 0.0, glow_a=0.5)
        rect(cr, cx - 900, 910, 1800, 300, fill=(0.95, 0.85, 0.55))

    def alone(cr, cx, T):
        S.vgrad(cr, (0.18, 0.24, 0.36), (0.10, 0.12, 0.20))
        rect(cr, cx - 1000, 900, 2000, 300, fill=(0.30, 0.33, 0.40))
        line(cr, cx - 1000, 900, cx + 1000, 900, 4, INK)
        for i, (dx, gy, f, s_, acc) in enumerate(((-380, 900, 1, 0.85, ("cap",)), (-200, 930, -1, 0.8, ("hat",)),
                                                   (230, 915, 1, 0.85, ("ponytail",)), (400, 940, -1, 0.9, ()))):
            statue(cr, 0.4 + i, cx + dx, gy, "stand", face=f, s=s_, walk=0.7, seed=i, acc=acc)
        r2 = rng(3)
        for i in range(30):
            drop(cr, cx + r2.uniform(-480, 480), r2.uniform(250, 820), r2.uniform(0.8, 1.4), 0.8)
        frost(cr, 1.0)
        rect(cr, cx - 90, 935 - 92, 180, 92, fill=(0.55, 0.58, 0.65), stroke=INK, lw=5)
        p = sm.pose("sit", x=cx, face=1, s=0.95, a1f=35, a2f=120, a1b=25, a2b=125, lean=16, head=22, smile=-0.6,
                    brow=-0.7, gy=0.7)
        p["y"] = 935 - 92 - 4
        sm.draw(cr, sm.idle(p, T, 2), acc=HERO)

    b.add(st7, K.split(dict(title="MOST POWERFUL?", bg=(1.0, 0.95, 0.80), draw=powerful),
                       dict(title="ALL ALONE?", bg=(0.10, 0.13, 0.22), draw=alone), t_or), "fade", 0.3)
    b.fx(st7, "chime", -8)
    b.fx(t_or, "darkwhoosh", -6)

    # 8. title
    st8 = e("c1_07") - 0.2

    @b.shot(st8, "cut")
    def title(cr, t, d, T):
        TITLE(cr, t)
    b.fx(st8, "whoosh", -4)
    b.fx(st8 + 0.55, "snap", 0)
    b.fx(st8 + 0.57, "boom", -2)
    b.fx(st8 + 0.62, "shimmer", -8)
    return b.result()
