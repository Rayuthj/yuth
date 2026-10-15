"""Stop Time - Chapter 2: The First Freeze (0:40-1:40)."""
from video.projects.stop_time.chapters._s import *  # noqa: F401,F403

SUNNY = ((0.62, 0.80, 0.97), (0.92, 0.95, 0.98))
TITLE_HOLD = 2.8          # how long the chapter-1 title card had been on screen when chapter 1 ended


def music_plan(tl):
    return K.music(tl, [(0.6, "wonder", "wonder", 80, 0.6), ("c2_02", "playful", "playful_g", 100, 0.5),
                        ("c2_06", "cold", "cold", 66, 0.35), ("c2_07", "uplift", "uplift", 108, 0.7),
                        ("c2_08", "dark", "dark", 62, 0.55)])


def lamp_post(cr, x, gy, s=1.0):
    with xform(cr, x, gy, s):
        line(cr, 0, 0, 0, -420, 9, INK)
        line(cr, 0, -420, 50, -440, 7, INK)
        polyline(cr, [(30, -440), (90, -440), (80, -410), (40, -410)], 4, INK, closed=True, fill=(0.95, 0.9, 0.7))


def skateboard(cr, x, y, s=1.0, rot=0.0):
    with xform(cr, x, y, s, rot):
        rrect(cr, -80, -9, 160, 18, 9, fill=(0.85, 0.35, 0.25), stroke=INK, lw=4)
        for k in (-50, 50):
            circle(cr, k, 18, 10, fill=WHITE, stroke=INK, w=4)


def fountain(cr, x, gy, T, frozen=1.0):
    """Plaza fountain; with frozen=1 the water arcs are crystal sculptures."""
    with xform(cr, x, gy):
        ellipse(cr, 0, -40, 380, 70, fill=(0.75, 0.73, 0.70), stroke=INK, w=6)
        rect(cr, -380, -40, 760, 50, fill=(0.75, 0.73, 0.70))
        ellipse(cr, 0, 10, 380, 60, stroke=INK, w=6)
        line(cr, -380, -40, -380, 10, 6, INK)
        line(cr, 380, -40, 380, 10, 6, INK)
        ellipse(cr, 0, -40, 350, 55, fill=(0.55, 0.78, 0.95))
        rect(cr, -30, -300, 60, 260, fill=(0.80, 0.78, 0.74), stroke=INK, lw=5)
        ellipse(cr, 0, -300, 120, 26, fill=(0.80, 0.78, 0.74), stroke=INK, w=5)
        water = (0.70, 0.90, 1.0)
        for k in (-1, 1):
            for j, (dx, h) in enumerate(((200, 170), (300, 120))):
                pts = bezier_pts([(k * 40, -320), (k * dx * 0.5, -320 - h), (k * dx, -60)], 24)
                polyline(cr, pts, 26 - j * 6, (0.35, 0.60, 0.80), 0.9)
                polyline(cr, pts, 18 - j * 6, water, 0.95)
                polyline(cr, pts[3:14], 5, WHITE, 0.9)
        pts = bezier_pts([(0, -310), (0, -430), (0, -330)], 12)
        polyline(cr, [(0, -310), (0, -440)], 30, (0.35, 0.60, 0.80), 0.9)
        polyline(cr, [(0, -310), (0, -440)], 22, water, 0.95)
        circle(cr, 0, -450, 22, fill=water, stroke=(0.35, 0.60, 0.80), w=4)
        r = rng(3)
        for i in range(26):
            drop(cr, r.uniform(-330, 330), r.uniform(-420, -70), r.uniform(0.9, 1.6))
        if frozen > 0:
            for i in range(9):
                sx, sy = r.uniform(-320, 320), r.uniform(-460, -80)
                tw = clamp(math.sin(T * 2.3 + i * 1.9))
                if tw > 0.4:
                    star_shape(cr, sx, sy, 26 * (tw - 0.4) * 1.7, points=4, inner=0.25, fill=WHITE)
        del pts


def bread(cr, x, y, s=1.0, kind=0):
    with xform(cr, x, y, s):
        if kind == 0:
            ellipse(cr, 0, 0, 60, 26, fill=(0.85, 0.60, 0.30), stroke=INK, w=4)
            for k in (-25, 0, 25):
                line(cr, k - 8, -14, k + 8, 10, 3, (0.55, 0.35, 0.15))
        else:
            circle(cr, 0, 0, 28, fill=(0.80, 0.52, 0.25), stroke=INK, w=4)
            arc(cr, 0, 0, 14, 0.4, 2.6, 3, (0.55, 0.35, 0.15))


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    @b.shot(0)
    def title_out(cr, t, d, T):
        TITLE(cr, TITLE_HOLD + t)

    # 1. snap: the world stops
    t_snap = s("c2_01") + 0.02
    HX, GY = 960, 960

    def hero_p(T):
        k = ease(prog(T, t_snap - 0.35, 0.3))
        p = sm.pose("stand", x=HX, face=1, s=1.05, a1f=lerp(12, SNAP_KW["a1f"], k), a2f=lerp(10, SNAP_KW["a2f"], k),
                    smile=0.3 + 0.5 * k, brow=0.3 * k, gx=0.3)
        return sm.on_ground(sm.idle(p, T, 1), GY)

    @b.shot(0.55, "zoom", 0.4)
    def snap(cr, t, d, T):
        wt = wtime(T, t_snap)
        p = hero_p(T)
        J0 = sm.joints(p)
        hx, hy = J0["hand_f"]
        with K.ken(cr, t, d, 1.0, 1.05, HX, 620):
            S.city(cr, T, 0, sky=SUNNY, gy=820)
            P.sun(cr, 1120, 150, 60, 0.0)
            clock_tower(cr, 1500, 820, 0.95, wt, hours=10, minutes=15)
            flock(cr, wt, n=6, x0=300, y0=220, seed=7, s=1.0, speed=150)
            # a juggler whose balls will hang in the air
            Jj = statue(cr, wt, 420, 980, "cheer", face=1, s=0.95, acc=("hat",), a1f=60, a2f=70, a1b=-60, a2b=-70)
            for i in range(3):
                ph = (wt * 0.9 + i / 3) % 1
                bx = lerp(Jj["hand_b"][0], Jj["hand_f"][0], ph)
                by = Jj["hand_f"][1] - 260 * 4 * ph * (1 - ph)
                circle(cr, bx, by, 18, fill=[RED, YELLOW, GREEN][i], stroke=INK, w=4)
            # a balloon drifting up
            bx, by = 1260, 520 - wt * 60
            line(cr, bx, by + 60, bx - 10, by + 200, 3, INK)
            ellipse(cr, bx, by, 46, 58, fill=RED, stroke=INK, w=5)
            statue(cr, wt, 1700, 990, "stand", face=-1, s=0.9, acc=("ponytail",), walk=0.8)
            freeze_wave(cr, T, t_snap, hx, hy)
            if T > t_snap:
                hero_bubble(cr, J0, T, fk(T, t_snap + 0.2), s=1.05)
            sm.draw(cr, p, acc=HERO)
            snap_fx(cr, hx, hy, T - t_snap)
        frozen_hud(cr, fk(T, t_snap + 0.3), T)
    b.fx(0.55, "whoosh", -10)
    b.fx(0.62, "tick", -14)
    b.fx(t_snap, "snap", -2)
    b.fx(t_snap + 0.04, "slowmo", -6)
    b.fx(w("c2_01", "stops"), "shimmer", -12)

    # 2. a frozen street: mid-sneeze, a dog in mid-air
    st2 = s("c2_02") - 0.15
    V = 260
    t_sn, t_dog = w("c2_02", "sneeze"), w("c2_02", "dog")
    X_SN = 1300 + V * (t_sn - st2)
    X_DOG = 1350 + V * (t_dog + 1.7 - st2)

    @b.shot(st2, "fade", 0.3)
    def walk_street(cr, t, d, T):
        cam = V * (T - st2)
        with K.ken(cr, t, d, 1.0, 1.0):
            S.city(cr, T, cam, sky=SUNNY, gy=760)
            with xform(cr, -cam, 0):
                for X in range(200, 3000, 700):
                    lamp_post(cr, X, 860)
                # man caught mid-sneeze
                Js = statue(cr, 0, X_SN, 890, "stand", face=-1, s=0.95, acc=("hat",), head=-24, lean=-10, a1f=50,
                            a2f=110, eye=0.2, mo=0.8, smile=0.0, brow=0.6)
                hx, hy = Js["head"]
                r = rng(4)
                for i in range(40):
                    a = math.pi + r.uniform(-0.45, 0.35)
                    dd = r.uniform(40, 260)
                    circle(cr, hx + math.cos(a) * dd - 30, hy + 10 + math.sin(a) * dd * 0.6, r.uniform(2, 5),
                           fill=(0.65, 0.85, 0.95))
                text(cr, "ACHOO!", hx - 210, hy - 90, 64, face=FONT_TITLE, c=YELLOW, outline=INK, ow=7, rot=0.12)
                # dog frozen mid-leap, the ball just out of reach
                statue(cr, 0, X_DOG - 330, 890, "point", face=1, s=0.9, acc=("cap",), a1f=70)
                dog(cr, X_DOG, 760, 1.1, face=1, leap=1.0, ph=0.3)
                ball(cr, X_DOG + 205, 612, 22)
                for X in (150, X_DOG + 650):
                    statue(cr, 0.4, X, 895, "stand", face=-1, s=0.85, walk=0.8, acc=("ponytail",))
            frost(cr)
            J = K.hero(cr, T, 600, 1010, "stand", face=1, walk=0.9, smile=0.7, gx=0.6, eye=1.1, s=1.05)
            hero_bubble(cr, J, T, 1.0)
        for tt, lab in ((t_sn, "MID-SNEEZE"), (t_dog + 0.6, "MID-AIR")):
            k = K.pop(T, tt)
            if 0 < k and T < tt + 2.6:
                label_box(cr, lab, CX + 300, 180, 50, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False, scale=k)
        frozen_hud(cr, 1.0, T)
    b.fx(st2, "footsteps", -16, dur=8.0)
    b.fx(t_sn, "pop", -12)
    b.fx(t_dog + 0.6, "boing", -12)

    # 2b. a kid floating above the curb, mid-trick, huge grin
    st2b = s("c2_02b") - 0.15
    t_grin = w("c2_02b", "huge grin")
    t_float = w("c2_02b", "floats")

    @b.shot(st2b, "slide", 0.4)
    def skater(cr, t, d, T):
        kz = ease(prog(T, t_grin - 0.3, 1.2))
        with camera(cr, lerp(1.0, 1.7, kz), lerp(CX, 1030, kz), lerp(560, 420, kz)):
            S.city(cr, T, 900, sky=SUNNY, gy=760)
            rect(cr, -400, 900, W + 800, 20, fill=LIGHT, stroke=INK, lw=4)
            rect(cr, -400, 920, W + 800, 400, fill=(0.45, 0.46, 0.50))
            # kid in the air above the curb
            skateboard(cr, 1030, 700, 1.1, rot=-0.5)
            p = sm.pose("stand", x=1030, s=0.72, face=1, a1f=110, a2f=10, a1b=-120, a2b=-10, l1f=40, l2f=-70,
                        l1b=-30, l2b=-60, smile=1.0, mo=0.55, eye=1.2, lean=-6)
            p = sm.on_ground(p, 690)
            sm.draw(cr, p, acc=("cap",))
            ellipse(cr, 1030, 900, 90, 12, fill=INK, a=0.15)
            frost(cr)
            # hero checks for strings under the board
            k = ease(prog(T, t_float, 1.2))
            hx = lerp(500, 840, k)
            wave_ = math.sin(T * 9) * 20 if T > t_float + 1.2 else 0
            J = K.hero(cr, T, hx, 900, "point" if k >= 1 else "stand", face=1, walk=0.9 if 0 < k < 1 else 0.0,
                       smile=0.6, eye=1.2, gy=-0.6, a1f=70 + wave_)
            hero_bubble(cr, J, T, 1.0)
        if T > t_float + 1.4 and kz < 0.3:
            text(cr, "no strings?!", 640, 380, 46, face=FONT_HAND, bold=True, a=prog(T, t_float + 1.4, 0.3) * (1 - kz * 3))
        if kz > 0.6:
            label_box(cr, "HUGE GRIN", CX, 190, 56, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                      scale=K.pop(T, t_grin + 0.6))
        frozen_hud(cr, 1.0, T)
    b.fx(t_float + 1.4, "boing", -14)
    b.fx(t_grin + 0.6, "pop", -10)

    # 3. a fountain like a crystal sculpture
    st3 = s("c2_03") - 0.15

    @b.shot(st3, "fade", 0.3)
    def crystal(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, CX, 520):
            S.city(cr, T, 400, sky=SUNNY, gy=760)
            fountain(cr, CX, 900, T, 1.0)
            frost(cr, 0.8)
            k = ease(prog(T, st3 + 0.2, 1.6))
            J = K.hero(cr, T, lerp(1700, 1450, k), 1000, "point" if k >= 1 else "stand", face=-1,
                       walk=0.9 if k < 1 else 0.0, smile=0.8, eye=1.25, mo=0.3, gy=-0.4, a1f=80)
            hero_bubble(cr, J, T, 1.0)
        label_box(cr, "CRYSTAL SCULPTURE", CX, 170, 56, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                  scale=K.pop(T, w("c2_03", "sculpture")))
        frozen_hud(cr, 1.0, T)
    b.fx(st3 + 0.2, "shimmer", -10)
    b.fx(w("c2_03", "crystal"), "sparkle", -10)

    # 4. you poke a raindrop. it just... stays.
    st4 = s("c2_04") - 0.15
    t_poke, t_fall, t_stay = w("c2_04", "poke"), w("c2_04", "fall"), w("c2_04", "stays")
    _pf = sm.on_ground(sm.pose("point", x=760, face=1, s=1.9, a1f=72, a2f=4, lean=6), 1320)
    DX, DY = sm.joints(_pf)["hand_f"][0] + 70, sm.joints(_pf)["hand_f"][1] - 20

    @b.shot(st4, "fade", 0.3)
    def poke(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 540):
            S.city(cr, T, 600, sky=((0.66, 0.74, 0.84), (0.86, 0.88, 0.90)), gy=760)
            rain(cr, T, -100, n=60, seed=8, y1=1100, s=1.8)
            frost(cr)
            # wobble each time the finger touches the drop
            wob = 0.0
            for tt in (t_poke + 0.3, t_stay + 0.1):
                if T > tt:
                    wob += math.sin((T - tt) * 26) * math.exp(-(T - tt) * 4)
            reach = ease(prog(T, t_poke - 0.1, 0.4)) * (1 - 0.5 * ease(prog(T, t_poke + 0.6, 0.3)))
            reach = max(reach, ease(prog(T, t_stay - 0.2, 0.3)) * (1 - ease(prog(T, t_stay + 0.5, 0.3))))
            p = sm.pose("point", x=760, face=1, s=1.9, a1f=lerp(30, 72, reach), a2f=lerp(40, 4, reach), smile=0.7,
                        eye=1.2, gx=0.8, gy=-0.2, lean=6 * reach)
            p = sm.on_ground(sm.idle(p, T, 2), 1320)
            J = sm.joints(p)
            hero_bubble(cr, J, T, 0.8, s=1.9, glow_a=0.15)
            with xform(cr, DX, DY, 1.0):
                cr.scale(1 + 0.12 * wob, 1 - 0.12 * wob)
                drop(cr, 0, 0, 7.0)
            sm.draw(cr, p, acc=HERO)
        if T > t_fall:
            k = prog(T, t_fall, 0.4)
            arrow(cr, DX + 160, DY - 40, DX + 160, DY + 220, 8, RED, p=k, dash=[18, 12])
            if T > t_fall + 0.4:
                cross(cr, DX + 160, DY + 90, 1.6, p=prog(T, t_fall + 0.4, 0.3))
        if T > t_stay:
            text(cr, "it just... stays.", DX + 40, 820, 64, face=FONT_HAND, bold=True, c=ICE_D,
                 a=eout(prog(T, t_stay, 0.4)))
        frozen_hud(cr, 1.0, T)
    b.fx(t_poke + 0.3, "boing", -12)
    b.fx(t_fall + 0.4, "soft_x", -12)
    b.fx(t_stay + 0.1, "boing", -14)

    # 4b. flour hanging in the air like snow
    st4b = s("c2_04b") - 0.15

    @b.shot(st4b, "fade", 0.3)
    def bakery(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 560):
            S.room(cr, T, wall=(0.58, 0.38, 0.27), floor_c=(0.40, 0.27, 0.20), fy=900)
            rect(cr, 560, 110, 800, 90, fill=(0.55, 0.28, 0.18), stroke=INK, lw=6)
            text(cr, "BAKERY", CX, 155, 56, face=FONT_TITLE, c=WHITE)
            for row, yy in enumerate((330, 470)):
                rect(cr, 1260, yy, 520, 18, fill=(0.55, 0.38, 0.22), stroke=INK, lw=4)
                for i in range(5):
                    bread(cr, 1310 + i * 105, yy - 26, 0.8, (i + row) % 2)
            rect(cr, 320, 640, 820, 260, fill=(0.70, 0.48, 0.30), stroke=INK, lw=6)
            rect(cr, 300, 620, 860, 30, fill=(0.85, 0.70, 0.50), stroke=INK, lw=6)
            Jb = statue(cr, 0, 700, 640, "cheer", face=1, s=1.0, acc=("chef", "mustache"), a1f=120, a1b=-120,
                        smile=0.8, mo=0.4)
            glow(cr, Jb["head"][0], Jb["head"][1] - 120, 260, WHITE, 0.7)
            frost(cr, 0.85)
            snow_flour(cr, T, tf=-100, n=110, seed=5, x0=460, x1=960, y0=230, y1=640, size=(3, 9), a=1.0)
            snow_flour(cr, T, tf=-100, n=220, seed=6, x0=0, x1=W, y0=0, y1=900, size=(2, 6), a=0.95)
            k = ease(prog(T, st4b + 0.1, 1.2))
            J = K.hero(cr, T, lerp(2000, 1480, k), 1040, "arms_out" if k >= 1 else "stand", face=-1, s=1.2,
                       walk=0.9 if k < 1 else 0.0, smile=0.9, eye=1.2, gy=-0.8, mo=0.3)
            hero_bubble(cr, J, T, 1.0, s=1.2)
        label_box(cr, "LIKE SNOW", 700, 980, 50, c=ICE_D, bg=WHITE, face=FONT_TITLE, bold=False,
                  scale=K.pop(T, w("c2_04b", "snow")))
        frozen_hud(cr, 1.0, T)
    b.fx(st4b, "door", -10)
    b.fx(w("c2_04b", "flour"), "shimmer", -12)

    # 5. a selfie with a frozen pigeon
    st5 = s("c2_05") - 0.15
    t_self, t_best = w("c2_05", "selfie"), w("c2_05", "best photo")

    def selfie_scene(cr, T, flash=0.0):
        S.city(cr, T, 1200, sky=SUNNY, gy=760)
        P2.pigeon(cr, 1150, 560, 2.0, face=-1, flap=0.75, t=0.5)
        frost(cr)
        J = K.hero(cr, T, 860, 1000, "stand", face=1, s=1.3, smile=1.0, mo=0.35, eye=1.1, a1f=130, a2f=-10, gx=0.6,
                   gy=-0.5)
        hero_bubble(cr, J, T, 1.0, s=1.3)
        return J

    @b.shot(st5, "slide", 0.4)
    def selfie(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, 1000, 520):
            J = selfie_scene(cr, T)
            P.phone(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 30, 0.7, rot=-0.3, lit=0.6)
        fl = prog(T, t_self + 0.2, 0.5)
        if 0 < fl < 1:
            src(cr, WHITE, 0.9 * (1 - fl))
            cr.paint()
        kp = K.pop(T, t_best - 0.2)
        if kp > 0:
            src(cr, BLACK, 0.6 * clamp(kp))
            cr.paint()
            with xform(cr, CX, 500, max(0.01, kp) * 0.62, -0.04):
                rrect(cr, -420, -470, 840, 940, 60, fill=INK)
                cr.save()
                rrect_path(cr, -390, -440, 780, 880, 34)
                cr.clip()
                with xform(cr, 0, 0, 1.25):
                    with xform(cr, -1000, -600):
                        selfie_scene(cr, T)
                cr.restore()
                cr.new_path()
                P.heart(cr, -300, 360, 0.9)
                text(cr, "1", -230, 360, 60, face=FONT_TITLE, c=WHITE, align="left", outline=INK, ow=6)
            text(cr, "BEST PHOTO EVER", CX, 1000, 60, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, a=clamp(kp))
        frozen_hud(cr, 1.0, T)
    b.fx(t_self + 0.2, "camera", -6)
    b.fx(t_best - 0.2, "pop", -8)
    b.fx(t_best + 0.3, "ding", -10)

    # 6. the quietest place you've ever been
    st6 = s("c2_06") - 0.15
    t_car, t_voice, t_wind = w("c2_06", "no cars"), w("c2_06", "no voices"), w("c2_06", "no wind")

    def ic_car(cr, T):
        P.car(cr, 0, 60, 1.2, c=RED)

    def ic_voice(cr, T):
        speech_bubble(cr, 0, -20, 200, 120, -40, 80)
        text(cr, "blah", 0, -20, 44, face=FONT_HAND, bold=True)

    def ic_wind(cr, T):
        for i in range(3):
            pts = [(-110 + j * 18, -40 + i * 40 + 10 * math.sin(j * 0.6)) for j in range(12)]
            polyline(cr, pts, 8, (0.45, 0.65, 0.85))
            arc(cr, 100, -50 + i * 40, 18, -math.pi, 0.8, 8, (0.45, 0.65, 0.85))

    @b.shot(st6, "fade", 0.4)
    def quiet(cr, t, d, T):
        with K.ken(cr, t, d, 1.05, 1.0, CX, 600):
            S.city(cr, T, 1500, sky=SUNNY, gy=760)
            frozen_people(cr, 0.3, n=6, y0=900, y1=1000, seed=21, x0=-100, x1=600)
            frozen_people(cr, 0.3, n=6, y0=900, y1=1000, seed=22, x0=1350, x1=2050)
            frost(cr, 1.1)
            J = K.hero(cr, T, CX, 1000, "listen", face=1, s=1.0, smile=0.3, a1f=40, a2f=140, eye=1.1, gy=-0.3)
            hero_bubble(cr, J, T, 1.0)
        text(cr, "SHHH...", CX, 200, 80, face=FONT_TITLE, c=WHITE, outline=ICE_D, ow=8, a=eout(prog(T, st6 + 0.2, 0.4)))
        for i, (fn_, ta) in enumerate(((ic_car, t_car), (ic_voice, t_voice), (ic_wind, t_wind))):
            k = K.pop(T, ta)
            if k <= 0:
                continue
            x = 480 + i * 480
            with xform(cr, x, 430, max(0.01, k) * 0.9):
                circle(cr, 0, 0, 150, fill=WHITE, stroke=ICE_D, w=6, a=0.92)
                fn_(cr, T)
                x_out(cr, 0, 0, prog(T, ta + 0.3, 0.35), 105, w=18)
    for ta in (t_car, t_voice, t_wind):
        b.fx(ta, "pop", -12)
        b.fx(ta + 0.3, "scratch", -16)

    # 6b. your own heartbeat, your shoes on the pavement
    st6b = s("c2_06b") - 0.15
    t_hb, t_shoe = w("c2_06b", "heartbeat") - 0.1, w("c2_06b", "shoes") - 0.1

    @b.shot(st6b, "fade", 0.3)
    def heartbeat(cr, t, d, T):
        cam = 95 * max(0.0, T - t_shoe)
        with K.ken(cr, t, d, 1.35, 1.45, 960, 640):
            S.city(cr, T, 1700 + cam, sky=SUNNY, gy=760)
            with xform(cr, -cam, 0):
                frozen_people(cr, 0.7, n=5, y0=850, y1=870, seed=41, x0=1500, x1=3200, s0=0.6, s1=0.7)
                lamp_post(cr, 1500, 860, 0.9)
            frost(cr, 1.1)
            spd = 1.0 / (0.95 * 0.84)
            walking = T > t_shoe
            p = sm.pose("stand", x=960, face=1, s=1.0, smile=0.2, eye=1.1, gy=0.3)
            p = sm.walk(p, (T - t_shoe) + 0.13, spd) if walking else sm.idle(p, T, 4)
            p = sm.on_ground(p, 940)
            J = sm.joints(p)
            hero_bubble(cr, J, T, 1.0)
            sm.draw(cr, p, acc=HERO)
            if T > t_hb:
                ph = (T - t_hb - 0.1) % 0.85
                beat = math.exp(-ph * 9) + 0.7 * math.exp(-max(0, ph - 0.22) * 9) * (ph > 0.22)
                cx_, cy_ = lerp(J["neck"][0], J["hip"][0], 0.3) - 4, lerp(J["neck"][1], J["hip"][1], 0.3)
                glow(cr, cx_, cy_, 70, RED, 0.35 * beat)
                P.heart(cr, cx_, cy_ + 6, 0.32, beat=beat)
                if ph < 0.5:
                    text(cr, "ba-dum", cx_ + 120, cy_ - 60, 34, face=FONT_HAND, bold=True, c=RED, a=1 - ph * 2)
            if walking:
                for side in ("f", "b"):
                    fx_, fy_ = J["foot_" + side]
                    if fy_ > 935:
                        text(cr, "tap", fx_, fy_ + 40, 30, face=FONT_HAND, bold=True, c=ICE_D)
        frozen_hud(cr, 1.0, T)
    b.fx(t_hb, "heartbeat", -6, dur=e("c2_06b") - t_hb + 0.6)
    b.fx(t_shoe, "footsteps", -6, dur=e("c2_06b") - t_shoe + 0.8)

    # 7. the coolest thing that has ever happened to anyone
    st7 = s("c2_07") - 0.15
    t_cool = w("c2_07", "coolest")

    @b.shot(st7, "fade", 0.3)
    def coolest(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.city(cr, T, 2000, sky=SUNNY, gy=760)
            fountain(cr, 380, 860, T, 1.0)
            frozen_people(cr, 0.6, n=5, y0=900, y1=1000, seed=31, x0=1350, x1=2000)
            Jf = statue(cr, 0, 1180, 990, "wave", face=-1, s=0.95, acc=("bun",), smile=0.7)
            frost(cr)
            hop = abs(math.sin((T - st7) * 4.2)) * 60 if T < t_cool else 0
            J = K.hero(cr, T, 900, 1010 - hop, "cheer" if T < t_cool else "confident", face=1, smile=1.0, s=1.25)
            hero_bubble(cr, J, T, 1.0, s=1.25)
            if T > t_cool:
                k = ease(prog(T, t_cool, 0.4))
                hx, hy = J["head"]
                with group(cr, k):
                    sunglasses(cr, {"head": (hx, hy - 40 * (1 - k))}, 1.25, 1)
            del Jf
        rrect(cr, 60, 220, 300, 80, 16, fill=WHITE, stroke=ICE_D, lw=5)
        text(cr, "HOUR 1", 210, 260, 50, face=FONT_TITLE, c=ICE_D)
        stamp(cr, "COOLEST THING EVER", CX, 180, T - t_cool - 0.3, 76, c=YELLOW, rot=-0.04)
        frozen_hud(cr, 1.0, T)
    b.fx(st7 + 0.2, "cheer", -12)
    b.fx(t_cool, "swish", -10)
    b.fx(t_cool + 0.3, "stamp", -6)

    # 8. a deep breath... something feels very, very wrong
    st8 = s("c2_08") - 0.15
    t_breath, t_wrong = w("c2_08", "deep breath"), w("c2_08", "something")

    @b.shot(st8, "fade", 0.4)
    def wrong(cr, t, d, T):
        kw_ = ease(prog(T, t_wrong, 0.8))
        kz = ease(prog(T, st8, d))
        with camera(cr, lerp(1.5, 1.9, kz), 960, 520):
            S.city(cr, T, 2300, sky=SUNNY, gy=760)
            frost(cr, 1.1)
            inh = ease(prog(T, t_breath, 1.0)) * (1 - kw_)
            p = sm.pose("stand", x=960, face=1, s=1.0, a1f=lerp(12, 60, inh), a2f=lerp(10, 40, inh), a1b=lerp(-12, -60, inh),
                        a2b=lerp(-10, -40, inh), head=-10 * inh, smile=0.4 * (1 - kw_), blink=inh * 0.9, sq=1 + 0.03 * inh)
            if kw_ > 0:
                p = sm.mix(p, sm.pose("worried", x=960, face=1, s=1.0, a1f=25, a2f=150, eye=1.35, mo=0.5), kw_)
            p = sm.on_ground(p, 940)
            J = sm.joints(p)
            hero_bubble(cr, J, T, 1.0 - kw_)
            sm.draw(cr, p, acc=HERO)
            if inh > 0.3:
                for k in (-1, 1):
                    line(cr, J["head"][0] + 60 * k, J["head"][1] + 30, J["head"][0] + 30 * k, J["head"][1] + 20, 4,
                         ICE_D, inh)
        if kw_ > 0:
            src(cr, (0.25, 0.0, 0.03), 0.55 * kw_)
            cr.paint()
            vignette(cr, 0.85 * kw_)
            text(cr, "?!", 1240, 300, 140, face=FONT_TITLE, c=RED, outline=INK, ow=10, scale=max(0.01, K.pop(T, t_wrong + 0.2)))
        frozen_hud(cr, 1.0 - kw_, T)
    b.fx(t_breath, "wind", -14, dur=1.2)
    b.fx(t_wrong, "darkwhoosh", -6)
    b.fx(t_wrong + 0.2, "glitch", -8)
    b.fx(w("c2_08", "wrong") + 0.2, "heartbeat", -10, dur=2.4)
    return b.result()
