"""Stop Time - Chapter 3: The Physics Problem (1:40-2:40)."""
from video.projects.stop_time.chapters._s import *  # noqa: F401,F403

DARK_TAG = True
BP = (0.10, 0.16, 0.26)        # dark blueprint background for the diagrams
BP2 = (0.05, 0.08, 0.14)


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 72, 0.5), ("c3_02", "cold", "cold", 66, 0.5),
                        ("c3_05", "dark", "dark", 60, 0.5), ("c3_06", "discovery", "discovery", 96, 0.6),
                        ("c3_09", "uplift", "uplift", 104, 0.7)])


def bp_bg(cr, T, grid_a=0.10):
    S.vgrad(cr, BP, BP2)
    src(cr, (0.5, 0.7, 1.0), grid_a)
    cr.set_line_width(1.5)
    for x in range(-400, W + 400, 60):
        cr.move_to(x, -400)
        cr.line_to(x, H + 400)
    for y in range(-400, H + 400, 60):
        cr.move_to(-400, y)
        cr.line_to(W + 400, y)
    cr.stroke()


def big_eye(cr, x, y, r, T, lit=1.0, img=1.0):
    """Side view of an eye looking left: cornea/lens at the left, retina at the right."""
    with xform(cr, x, y):
        circle(cr, 0, 0, r, fill=WHITE, stroke=INK, w=8)
        arc(cr, 0, 0, r * 0.97, -0.9, 0.9, r * 0.08, (0.95, 0.45, 0.45), 0.9)      # retina
        ellipse(cr, -r * 0.82, 0, r * 0.12, r * 0.42, fill=(0.40, 0.65, 0.95), stroke=INK, w=5)  # iris/lens
        ellipse(cr, -r * 0.70, 0, r * 0.10, r * 0.30, fill=(0.85, 0.93, 1.0), stroke=INK, w=4)
        line(cr, r * 0.95, 0, r * 1.5, r * 0.2, 12, (0.95, 0.75, 0.55))           # optic nerve
        if img > 0:
            with xform(cr, r * 0.86, 0, 0.5, math.pi):
                P.tree(cr, 0, 60, 0.5 * img + 0.001)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. what the movies never tell you
    t_never = w("c3_01", "never")

    @b.shot(0, "fade", 0.3)
    def cinema(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 460):
            S.vgrad(cr, (0.10, 0.07, 0.10), (0.04, 0.03, 0.05))
            glow(cr, CX, 420, 900, (0.6, 0.75, 1.0), 0.18)
            rect(cr, 330, 200, 1260, 560, fill=(0.75, 0.86, 0.98), stroke=(0.3, 0.3, 0.35), lw=10)
            cr.save()
            cr.rectangle(330, 200, 1260, 560)
            cr.clip()
            S.city(cr, T, 0, gy=640)
            r = rng(5)
            for i in range(40):
                drop(cr, r.uniform(340, 1580), r.uniform(220, 740), r.uniform(1.2, 2.0))
            frost(cr)
            p = sm.pose("confident", x=CX, s=1.2, smile=0.9, brow=0.6)
            sm.draw(cr, sm.on_ground(p, 720), acc=HERO)
            text(cr, "TIME STOP: THE MOVIE", CX, 260, 54, face=FONT_TITLE, c=WHITE, outline=INK, ow=7)
            cr.restore()
            cr.new_path()
            for row in range(3):
                y = 860 + row * 110
                for i in range(12):
                    x = -60 + i * 180 + row * 60
                    rrect(cr, x - 70, y, 140, 160, 30, fill=(0.45, 0.08, 0.12), stroke=BLACK, lw=4)
                    if (i + row) % 3:
                        circle(cr, x, y - 20, 48, fill=(0.08, 0.06, 0.08))
            # the hero in the audience with popcorn, turning to us
            circle(cr, 1240, 880, 54, fill=WHITE, stroke=INK, w=7)
            p = sm.pose("front", s=1.35, smile=0.4, brow=0.4, gx=0.3)
            sm.draw(cr, head_at(sm.idle(p, T, 2), 1240, 860), acc=HERO)
            polyline(cr, [(1330, 960), (1440, 960), (1420, 1080), (1350, 1080)], 5, INK, closed=True, fill=RED)
            for i in range(7):
                circle(cr, 1345 + i * 15, 950 - (i % 2) * 10, 16, fill=(1.0, 0.96, 0.8), stroke=INK, w=3)
        stamp(cr, "REALITY CHECK", CX, 480, T - t_never - 0.3, 100, c=RED, rot=-0.08)
    b.fx(0.1, "clicks", -18)
    b.fx(t_never + 0.3, "stamp", -4)
    b.fx(t_never + 0.3, "scratch", -10)

    # 2. light would stop too -> no light reaches your eyes -> completely dark
    st2 = s("c3_02") - 0.15
    t_stop, t_none, t_dark = w("c3_02", "light would stop"), w("c3_02", "no light"), w("c3_02", "completely dark")
    SUN = (330, 260)
    HX, GY = 1450, 960

    @b.shot(st2, "fade", 0.4)
    def light(cr, t, d, T):
        wt = wtime(T, t_stop)
        kd = ease(prog(T, t_dark, 1.0))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.field(cr, T, gy=880)
            P.sun(cr, SUN[0], SUN[1], 80, wt)
            P.tree(cr, 700, 880, 1.2, wt)
            p = sm.pose("stand", x=HX, face=-1, s=1.15, smile=0.4, gx=-0.4, gy=-0.4)
            p = sm.on_ground(sm.idle(p, T, 1), GY)
            J = sm.joints(p)
            ex, ey = J["head"][0] - 12, J["head"][1] - 4
            frozen = T > t_stop
            for ray in range(3):
                x0, y0 = SUN[0] + 60, SUN[1] + (ray - 1) * 30
                ang = math.atan2(ey - y0, ex - x0)
                for i in range(6):
                    f = (wt * 0.35 + i / 6 + ray * 0.11) % 1
                    if T > t_none and not frozen:
                        continue
                    if T > t_none and f > 0.85:
                        continue
                    photon(cr, lerp(x0, ex, f), lerp(y0, ey, f), 1.0, ang=ang, moving=wvel(T, t_stop), s=1.7)
            if frozen:
                frost(cr, 1.0)
            sm.draw(cr, p, acc=HERO)
        if T > t_stop:
            label_box(cr, "LIGHT STOPS TOO", 820, 140, 50, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                      scale=K.pop(T, t_stop))
        if T > t_none:
            k = K.pop(T, t_none)
            with xform(cr, 1700, 420, max(0.01, k)):
                ellipse(cr, 0, 0, 70, 40, fill=WHITE, stroke=INK, w=6)
                circle(cr, 0, 0, 22, fill=INK)
                x_out(cr, 0, 0, prog(T, t_none + 0.3, 0.3), 70, w=12)
        if kd > 0:
            src(cr, BLACK, 0.97 * kd)
            cr.paint()
            if kd > 0.6:
                bl = sm.blink(T, 3, 2.0)
                for k in (-1, 1):
                    ellipse(cr, CX + k * 28, 520, 10, max(1, 15 * (1 - bl)), fill=WHITE, a=kd)
                text(cr, "PITCH BLACK", CX, 700, 60, face=FONT_TITLE, c=(0.6, 0.6, 0.7), a=clamp((kd - 0.6) * 3))
    b.fx(t_stop, "slowmo", -8)
    b.fx(t_none + 0.3, "soft_x", -10)
    b.fx(t_dark, "darkwhoosh", -6)

    # 2b. your eyes only work because light travels into them
    st2b = s("c3_02b") - 0.15
    t_into, t_frz, t_blind = w("c3_02b", "travels"), w("c3_02b", "freeze the light"), w("c3_02b", "blind")
    EX, EY, ER = 1250, 560, 240

    @b.shot(st2b, "fade", 0.4)
    def eye(cr, t, d, T):
        wt = wtime(T, t_frz)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            bp_bg(cr, T)
            P.tree(cr, 330, 760, 1.3, wt)
            img = 1.0 - ease(prog(T, t_frz + 0.3, 0.8))
            big_eye(cr, EX, EY, ER, T, img=img)
            for ray in range(2):
                y0 = 420 + ray * 260
                x1, y1 = EX - ER * 0.8, EY + (ray - 0.5) * 60
                ang = math.atan2(y1 - y0, x1 - 480)
                for i in range(7):
                    f = (wt * 0.45 + i / 7 + ray * 0.2) % 1
                    if T < t_into:
                        continue
                    photon(cr, lerp(480, x1, f), lerp(y0, y1, f), 1.0, ang=ang, moving=wvel(T, t_frz), s=1.5)
                partial_line(cr, 480, y0, x1, y1, prog(T, t_into - 0.3, 0.5), 3, YELLOW, 0.4)
            if T > t_frz:
                frost(cr, 0.8)
        text(cr, "YOUR EYE", EX, 200, 54, face=FONT_TITLE, c=WHITE, a=eout(prog(T, st2b + 0.2, 0.4)))
        if T > t_frz - 0.2:
            rrect(cr, 120, 860, 520, 120, 18, fill=WHITE, stroke=INK, lw=5)
            text(cr, "BRAIN SEES:", 270, 920, 34, face=FONT_TITLE)
            rect(cr, 440, 880, 180, 80, fill=lerpc((0.75, 0.88, 0.98), BLACK, 1 - img), stroke=INK, lw=4)
            if img > 0.05:
                P.tree(cr, 530, 955, 0.25)
        stamp(cr, "BLIND", EX, 900, T - t_blind, 100, c=RED, rot=-0.06)
    b.fx(t_into, "shimmer", -12)
    b.fx(t_frz, "slowmo", -8)
    b.fx(t_blind, "stamp", -6)

    # 3. air freezes: like pushing through solid stone, and you couldn't breathe
    st3 = s("c3_03") - 0.15
    t_afz, t_push, t_br = w("c3_03", "freeze in place"), w("c3_03", "pushing"), w("c3_03", "breathe")

    @b.shot(st3, "fade", 0.4)
    def air_wall(cr, t, d, T):
        wt = wtime(T, t_afz)
        kp = ease(prog(T, t_push - 0.2, 0.6))
        with K.ken(cr, t, d, 1.0, 1.06, 900, 600):
            S.field(cr, T, gy=900)
            air(cr, wt, n=70, x0=-100, x1=W + 100, y0=-50, y1=880, seed=5, s=1.2)
            if T > t_afz:
                frost(cr, 1.0)
            if kp > 0:
                with group(cr, 0.55 * kp):
                    rect(cr, 1040, 120, 900, 780, fill=(0.55, 0.55, 0.60))
                    r = rng(3)
                    for i in range(40):
                        x, y = r.uniform(1060, 1900), r.uniform(140, 880)
                        polyline(cr, [(x, y), (x + r.uniform(20, 50), y + r.uniform(-15, 15)),
                                      (x + r.uniform(10, 40), y + r.uniform(20, 40))], 3, (0.35, 0.35, 0.40))
                text(cr, "SOLID AS STONE", 1490, 220, 56, face=FONT_TITLE, c=WHITE, outline=INK, ow=7, a=kp)
            strain = math.sin(T * 30) * 3 * kp
            g = "stand"
            p = sm.pose(g, x=900 + strain, face=1, s=1.15, lean=28 * kp, a1f=lerp(12, 95, kp), a2f=lerp(10, 5, kp),
                        a1b=lerp(-12, 85, kp), a2b=lerp(-10, 15, kp), l1f=25 * kp, l1b=-35 * kp, smile=-0.5 * kp,
                        brow=-0.8 * kp, eye=1.0 + 0.2 * kp)
            p = sm.on_ground(sm.idle(p, T, 3), 990)
            kb = ease(prog(T, t_br - 0.2, 0.5))
            J = sm.draw(cr, p, acc=HERO, fill=lerpc(WHITE, (0.75, 0.85, 1.0), kb))
            if kb > 0:
                label_box(cr, "CAN'T BREATHE", J["head"][0] - 260, J["head"][1] - 160, 44, c=RED, scale=K.pop(T, t_br))
    b.fx(t_afz, "slowmo", -8)
    b.fx(t_push, "strain", -8, dur=2.5)
    b.fx(t_br, "gulp", -8)

    # 4. no sound at all: sound needs moving air
    st4 = s("c3_04") - 0.15
    t_ns, t_need = w("c3_04", "no sound"), w("c3_04", "moving air")

    @b.shot(st4, "fade", 0.3)
    def sound(cr, t, d, T):
        wt = wtime(T, t_ns)
        with K.ken(cr, t, d, 1.0, 1.03):
            bp_bg(cr, T)
            # speaker
            rrect(cr, 180, 380, 200, 320, 20, fill=(0.25, 0.27, 0.32), stroke=WHITE, lw=5)
            circle(cr, 280, 470, 50, fill=(0.4, 0.42, 0.5), stroke=WHITE, w=4)
            circle(cr, 280, 610, 70 + 6 * math.sin(wt * 30), fill=(0.4, 0.42, 0.5), stroke=WHITE, w=4)
            # molecules in columns pushed by the wave
            for i in range(14):
                for j in range(6):
                    x0 = 470 + i * 85
                    y = 330 + j * 80
                    dx = 22 * math.sin(wt * 6 - i * 0.8)
                    molecule(cr, x0 + dx, y + (i % 2) * 20, 0.8)
            # ear
            with xform(cr, 1760, 540, 1.3):
                polyline(cr, bezier_pts([(-30, -90), (50, -110), (60, 0), (10, 40), (0, 100), (-30, 90)], 30), 8,
                         (0.95, 0.75, 0.6))
            for k in range(3):
                rr = ((wt * 300 + k * 140) % 420) + 60
                arc(cr, 300, 540, rr, -0.5, 0.5, 6, YELLOW, 0.8 * (1 - rr / 480) * wvel(T, t_ns))
            if T > t_ns:
                frost(cr, 1.0)
        text(cr, "SOUND = MOVING AIR", CX, 200, 64, face=FONT_TITLE, c=WHITE, a=eout(prog(T, t_need - 0.2, 0.4)))
        k = K.pop(T, t_ns + 0.2)
        if k > 0:
            with xform(cr, CX, 870, max(0.01, k)):
                circle(cr, 0, 0, 90, fill=WHITE, stroke=INK, w=6)
                polyline(cr, [(-50, -20), (-20, -20), (15, -50), (15, 50), (-20, 20), (-50, 20)], 5, INK, closed=True,
                         fill=INK)
                x_out(cr, 30, 0, 1.0, 40, w=10)
    b.fx(st4, "hum", -16, dur=t_ns - st4)
    b.fx(t_ns + 0.2, "soft_x", -8)

    # 4b. shout as loud as you want: not a single sound travels
    st4b = s("c3_04b") - 0.15
    t_shout, t_travel = w("c3_04b", "shout"), w("c3_04b", "travel")

    @b.shot(st4b, "slide", 0.4)
    def shout(cr, t, d, T):
        with K.ken(cr, t, d, 1.3, 1.38, 980, 640):
            S.city(cr, T, 0, gy=820)
            statue(cr, 0, 1360, 990, "stand", face=-1, s=1.0, acc=("cap",), walk=0.7, seed=2)
            frost(cr)
            ks = ease(prog(T, t_shout - 0.3, 0.3))
            J = K.hero(cr, T, 640, 990, "stand", face=1, s=1.1, a1f=lerp(12, 70, ks), a2f=lerp(10, 110, ks),
                       a1b=lerp(-12, 60, ks), a2b=lerp(-10, 120, ks), mo=0.9 * ks, eye=1.2, brow=0.6 * ks, head=-8 * ks)
            hx, hy = J["head"]
            letters = "HEEEY!!"
            n = int(clamp((T - t_shout) / 1.6) * len(letters)) if T > t_shout else 0
            for i in range(n):
                # letters come out... and crash into each other right at the mouth
                text(cr, letters[i], hx + 80 + i * 24, hy + 12 + 14 * math.sin(i * 2.3), 84, face=FONT_TITLE, c=YELLOW,
                     outline=INK, ow=7, rot=0.35 * math.sin(i * 1.7))
            if n >= 3:
                for i in range(3):
                    a = T * 3 + i * 2.1
                    star_shape(cr, hx + 150 + math.cos(a) * 70, hy - 60 + math.sin(a) * 20, 12, fill=WHITE, stroke=INK,
                               w=2)
            hero_bubble(cr, J, T, 0.8, s=1.1)
        if T > t_travel:
            text(cr, "...not a single sound travels", CX + 200, 260, 54, face=FONT_HAND, bold=True, c=WHITE,
                 outline=INK, ow=6, a=eout(prog(T, t_travel, 0.4)))
        frozen_hud(cr, 1.0, T)
    b.fx(t_shout + 0.4, "bonk", -14)
    b.fx(t_shout + 1.0, "bonk", -16)

    # 5. pitch black, silent, impossible to move through
    st5 = s("c3_05") - 0.15
    t_pb, t_sil, t_imp = w("c3_05", "pitch black"), w("c3_05", "silent"), w("c3_05", "impossible")

    def ic_black(cr, T):
        circle(cr, 0, 0, 110, fill=BLACK, stroke=WHITE, w=5)
        for k in (-1, 1):
            arc(cr, k * 35, -5, 18, 0.2, math.pi - 0.2, 5, WHITE)

    def ic_silent(cr, T):
        polyline(cr, [(-70, -30), (-30, -30), (20, -80), (20, 80), (-30, 30), (-70, 30)], 6, WHITE, closed=True,
                 fill=(0.3, 0.32, 0.4))
        x_out(cr, 70, 0, 1.0, 35, w=10)

    def ic_stuck(cr, T):
        rect(cr, -110, -120, 220, 230, fill=(0.55, 0.75, 0.95), stroke=WHITE, lw=5)
        p = sm.pose("stand", x=0, s=0.6, a1f=90, a2f=10, a1b=80, a2b=10, lean=20, smile=-0.5, brow=-0.8)
        sm.draw(cr, sm.on_ground(p, 100), acc=HERO)
        frost(cr, 0.3)

    @b.shot(st5, "fade", 0.4)
    def frozen_universe(cr, t, d, T):
        bp_bg(cr, T)
        vignette(cr, 0.5)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "A TRULY FROZEN UNIVERSE", CX, 170, 64, face=FONT_TITLE, c=WHITE, a=eout(prog(t, 0.05, 0.4)))
            # a frozen Earth hangs behind until the three verdicts arrive
            kg = 1 - ease(prog(T, t_pb - 0.3, 0.5))
            if kg > 0:
                with group(cr, kg):
                    glow(cr, CX, 560, 380, ICE, 0.3)
                    P.globe(cr, CX, 560, 230, 1.0)
                    frost(cr, 0.0)
                    circle(cr, CX, 560, 230, fill=FROST, a=0.45)
                    pause_icon(cr, CX, 560, 0.9, c=WHITE)
            for i, (fn_, lab, ta) in enumerate(((ic_black, "PITCH BLACK", t_pb), (ic_silent, "SILENT", t_sil),
                                                (ic_stuck, "IMPOSSIBLE TO MOVE", t_imp))):
                k = K.pop(T, ta)
                if k <= 0:
                    continue
                x = 420 + i * 540
                with xform(cr, x, 540, max(0.01, k) * 1.1):
                    fn_(cr, T)
                text(cr, lab, x, 740, 44, face=FONT_BOLD, c=WHITE, a=clamp(k))
    for ta in (t_pb, t_sil, t_imp):
        b.fx(ta, "thud", -8)
    b.fx(st5 + 0.2, "drone", -16, dur=2.5)

    # 6. let's cheat a little: a bubble of normal time
    st6 = s("c3_06") - 0.15
    t_cheat, t_bub, t_trav = w("c3_06", "cheat"), w("c3_06", "bubble"), w("c3_06", "travels")

    @b.shot(st6, "fade", 0.4)
    def cheat(cr, t, d, T):
        kb = ease(prog(T, t_bub - 0.1, 0.8))
        kw_ = ease(prog(T, t_trav, 1.6))
        hx = lerp(860, 1060, kw_)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.city(cr, T, 200, gy=800)
            r = rng(2)
            for i in range(50):
                drop(cr, r.uniform(0, W), r.uniform(80, 1000), r.uniform(1.0, 1.6))
            frozen_people(cr, 0.5, n=6, y0=880, y1=960, seed=51, x0=-100, x1=520)
            frozen_people(cr, 0.5, n=5, y0=880, y1=960, seed=52, x0=1500, x1=2050)
            R = 330 * kb
            if kb > 0:
                frost_outside(cr, hx, 720, R)
                bubble(cr, hx, 720, max(1, R), T, kb, glow_a=0.25)
            else:
                frost(cr)
            J = K.hero(cr, T, hx, 1000, "stand" if T < t_cheat else "confident", face=1, s=1.05,
                       walk=0.8 if 0 < kw_ < 1 else 0.0, smile=0.8, brow=0.5,
                       blink=1.0 if t_cheat < T < t_cheat + 0.4 else 0.0)
            del J
        if T > t_cheat:
            k = K.pop(T, t_cheat)
            with xform(cr, 300, 260, max(0.01, k)):
                rrect(cr, -190, -60, 380, 120, 60, fill=WHITE, stroke=INK, lw=6)
                on = prog(T, t_cheat + 0.3, 0.2)
                rrect(cr, 30, -40, 140, 80, 40, fill=lerpc(LIGHT, GREEN, on), stroke=INK, lw=4)
                circle(cr, lerp(70, 130, on), 0, 32, fill=WHITE, stroke=INK, w=4)
                text(cr, "CHEAT", -80, 0, 40, face=FONT_TITLE)
        if kb > 0.5:
            label_box(cr, "BUBBLE OF NORMAL TIME", CX, 190, 52, c=INK, bg=WARM, face=FONT_TITLE, bold=False,
                      scale=K.pop(T, w("c3_06", "normal time")))
    b.fx(t_cheat, "blink", -10)
    b.fx(t_cheat + 0.3, "check", -10)
    b.fx(t_bub, "bubbles", -8)
    b.fx(t_bub + 0.1, "shimmer", -10)

    # 7. inside the bubble: light moves, air flows, you can breathe
    st7 = s("c3_07") - 0.15
    t_l, t_a, t_b = w("c3_07", "light moves"), w("c3_07", "air flows"), w("c3_07", "breathe")
    BX, BY, BR = 640, 560, 400

    @b.shot(st7, "fade", 0.3)
    def inside(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04):
            S.field(cr, T, gy=900)
            inside_ = (lambda x, y: math.hypot(x - BX, y - BY) < BR - 20)
            air(cr, 0.0, n=60, x0=-100, x1=W + 100, y0=0, y1=880, seed=7, s=1.0, skip=inside_)
            for i in range(8):
                f = (i / 8)
                photon(cr, lerp(-100, W, f), 200 + 40 * (i % 3), moving=0.0)
            frost_outside(cr, BX, BY, BR)
            cr.save()
            cr.arc(BX, BY, BR, 0, TAU)
            cr.clip()
            air(cr, T, n=40, x0=BX - BR, x1=BX + BR, y0=BY - BR, y1=BY + BR, seed=8, s=1.0)
            for i in range(6):
                f = (T * 0.5 + i / 6) % 1
                photon(cr, lerp(BX - BR, BX + BR, f), BY - 230 + 70 * (i % 3), moving=1.0)
            cr.restore()
            cr.new_path()
            bubble(cr, BX, BY, BR, T, 1.0, glow_a=0.25)
            br = 0.5 + 0.5 * math.sin(T * 2.4)
            p = sm.pose("stand", x=BX, face=1, s=1.05, smile=0.8, a1f=20 + 10 * br, a1b=-20 - 10 * br, sq=1 + 0.02 * br)
            sm.draw(cr, sm.on_ground(p, 900), acc=HERO)
        for i, (lab, ta) in enumerate((("LIGHT MOVES", t_l), ("AIR FLOWS", t_a), ("YOU CAN BREATHE", t_b))):
            k = prog(T, ta, 0.35)
            y = 380 + i * 130
            rrect(cr, 1240, y - 45, 90, 90, 14, fill=WHITE, stroke=INK, lw=5, a=clamp(k * 3))
            text(cr, lab, 1360, y, 54, face=FONT_TITLE, align="left", a=clamp(k * 3), c=WHITE, outline=INK, ow=6)
            if k > 0:
                check(cr, 1285, y, 1.8, p=k)
    for ta in (t_l, t_a, t_b):
        b.fx(ta, "check", -8)

    # 8. scientists: impossible. us: a thought experiment
    st8 = s("c3_08") - 0.15
    t_imp2, t_te = w("c3_08", "impossible"), w("c3_08", "thought experiment")

    @b.shot(st8, "fade", 0.3)
    def thought(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.room(cr, T, wall=(0.86, 0.90, 0.95), floor_c=(0.70, 0.72, 0.76), fy=900)
            P.chalkboard(cr, CX, 360, 700, 380)
            text(cr, "BUBBLE OF TIME", CX, 250, 50, face=FONT_HAND, bold=True, c=WHITE)
            circle(cr, CX, 400, 90, stroke=WHITE, w=5)
            p = sm.on_ground(sm.pose("stand", x=CX, s=0.4), 470)
            sm.draw(cr, p, ink=WHITE, fill=BOARD, acc=HERO)
            text(cr, "= ?", CX + 180, 400, 60, face=FONT_HAND, bold=True, c=WHITE)
            Js = K.person(cr, T, 480, 990, "point" if T > t_imp2 else "hold", face=1, acc=SCI, smile=-0.3, brow=0.5,
                          seed=3)
            del Js
            Jh = K.hero(cr, T, 1440, 990, "think" if T < t_te else "present", face=-1, smile=0.7, brow=0.4)
            if T > t_te:
                P.lightbulb(cr, Jh["head"][0] - 130, Jh["head"][1] - 40, 0.42, on=prog(T, t_te, 0.3), t=T)
        stamp(cr, "IMPOSSIBLE", 430, 480, T - t_imp2, 60, c=RED, rot=-0.1)
        stamp(cr, "THOUGHT EXPERIMENT", 1500, 480, T - t_te, 46, c=BLUE, rot=0.06)
    b.fx(t_imp2, "stamp", -6)
    b.fx(t_te, "stamp", -6)
    b.fx(t_te + 0.1, "bulb", -10)

    # 9. now you're ready to use your power
    st9 = s("c3_09") - 0.15
    t_ready = w("c3_09", "ready")

    @b.shot(st9, "zoom", 0.4)
    def ready(cr, t, d, T):
        S.vgrad(cr, (0.10, 0.18, 0.35), (0.03, 0.05, 0.12))
        stars(cr, T, n=120, alpha=0.5)
        radial_lines(cr, CX, 560, T, n=30, c=ICE, a=0.10, w=22)
        with K.ken(cr, t, d, 1.0, 1.08, CX, 600):
            bubble(cr, CX, 700, 300, T, 1.0, glow_a=0.35)
            J = K.hero(cr, T, CX, 960, "confident", face=1, s=1.1, smile=0.9, brow=0.6, ink=NIGHT_INK,
                       fill=NIGHT_FILL, a1f=120, a2f=30)
            stopwatch(cr, J["hand_f"][0] + 20, J["hand_f"][1] - 60, 55, 0.0, glow_a=0.5)
        stamp(cr, "POWER: READY", CX, 200, T - t_ready, 84, c=YELLOW, rot=-0.04)
    b.fx(st9, "charge", -8)
    b.fx(t_ready, "stamp", -4)
    return b.result()
