"""King - Chapter 1: The Hook (0:00-0:40)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403

DARK_TAG = True


def music_plan(tl):
    return K.music(tl, [(0.0, "mystery", "mystery", 70, 0.5), ("c1_05", "uplift", "uplift", 104, 0.7),
                        ("c1_07", "mystery", "mystery", 70, 0.55), (tl.e("c1_08") + 0.2, "uplift", "mystery", 96, 0.9)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. a knock on the door
    t_knock = 0.35

    @b.shot(0)
    def knock(cr, t, d, T):
        with K.ken(cr, t, d, 1.06, 1.0, 1100, 560):
            S.room(cr, T, wall=(0.30, 0.30, 0.38), floor_c=(0.22, 0.20, 0.24), fy=900)
            glow(cr, 1500, 500, 500, (1.0, 0.9, 0.6), 0.25)
            shk = sum(max(0, 1 - abs(T - (t_knock + i * 0.32)) * 8) for i in range(3))
            P.door(cr, 1500 + math.sin(T * 80) * 4 * shk, 900, 1.3, open_=0.0, frame_fill=(0.75, 0.6, 0.45))
            for i in range(3):
                kk = prog(T, t_knock + i * 0.32, 0.35)
                if 0 < kk < 1:
                    text(cr, "KNOCK", 1500 + (i - 1) * 170, 380 - i * 30, 60, face=FONT_TITLE, c=YELLOW, a=1 - kk,
                         scale=lerp(0.8, 1.25, kk))
            x = lerp(300, 1180, ease(prog(T, 1.0, d - 1.0)))
            K.hero(cr, T, x, 900, walk=0.8 if T > 1.0 else 0.0, face=1, smile=0.0, blink=0.5, ink=(0.85, 0.85, 0.9),
                   fill=(0.30, 0.30, 0.38))
    for i in range(3):
        b.fx(t_knock + i * 0.32, "knock", -2)
    b.fx(1.2, "footsteps", -12, dur=2.0)

    # 2. outside: carriage, reporters, the crown
    st2 = s("c1_02") - 0.15
    t_rep, t_crown = w("c1_02", "reporters"), w("c1_02", "crown")

    @b.shot(st2, "iris", 0.5)
    def outside(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, 1000, 560):
            S.city(cr, T, 0, gy=880)
            P2.carriage(cr, 520, 880, 1.25, T)
            k_r = prog(T, t_rep - 0.3, 0.4)
            for i, x in enumerate((900, 1050, 1720, 1850)):
                if k_r <= 0:
                    break
                J = K.person(cr, T, x, 900, "hold", face=1 if x < 1300 else -1, s=0.85, acc=(("cap",), ("glasses",),
                             ("hat",), ("ponytail",))[i], seed=i)
                fl = max(0.0, math.sin(T * 9 + i * 2.1)) ** 8
                P2.press_camera(cr, J["hand_f"][0], J["hand_f"][1] - 10, 0.7, flash=fl * k_r)
            k_c = prog(T, t_crown - 0.3, 0.5)
            ax = 1350
            K.person(cr, T, ax, 900, "hold", face=-1, acc=ADV, a1f=70, a2f=20, a1b=60, a2b=30)
            P2.pillow_crown(cr, ax - 105, 690, 0.65, glow_a=0.6 * k_c)
            K.hero(cr, T, 1600, 900, "surprised", face=-1, eye=1.2, s=1.0)
        vignette(cr, 0.25)
    b.fx(st2, "whoosh", -8)
    b.fx(t_rep - 0.2, "camera", -10)
    b.fx(t_rep + 0.4, "camera", -12)
    b.fx(t_crown - 0.2, "shimmer", -10)

    # 3-4. "Your Majesty. The country is yours."
    st3 = s("c1_03") - 0.15

    def bow_setting(cr, T):
        S.city(cr, T, 0, gy=880)
    b.add(st3, K.dialogue(tl, bow_setting, [
        dict(x=760, gy=900, acc=ADV, face=1, g="hold", kw=dict(lean=28, head=18, a1f=80, a2f=10)),
        dict(x=1220, gy=900, acc=("tuft",), face=-1, g="surprised", kw=dict(eye=1.3)),
    ], [(0, "Your Majesty. The country is yours.", "c1_04", (720, 380))], zoom=(1.1, 1.18), focus=(980, 640)), "cut")
    b.fx(s("c1_04"), "pop", -10)

    # 5. crowned; the whole nation
    st5 = s("c1_05") - 0.15

    @b.shot(st5, "white", 0.3)
    def crowned(cr, t, d, T):
        S.palace(cr, T)
        k = ease(prog(t, 0.0, 0.7))
        p = sm.pose("cheer" if t > 0.8 else "surprised", x=CX, s=1.4, smile=0.9, eye=1.15)
        p = sm.on_ground(sm.idle(p, T, 1), 980)
        J = sm.draw(cr, p, acc=("tuft", "cape") if k < 1 else KING)
        if k < 1:
            P.crown(cr, J["head"][0], lerp(-200, J["head"][1] - 70, k), 0.75)
        burst(cr, J["head"][0], J["head"][1] - 60, t - 0.7, n=20, dist=300, c=YELLOW, dur=0.8)
        stamp(cr, "YOUR MAJESTY", CX, 220, t - 0.9, 90, c=YELLOW, rot=-0.05)
    b.fx(st5 + 0.6, "ding", -6)
    b.fx(st5 + 0.9, "stamp", -6)

    # 6. millions of people, gold, army, palace, power
    st6 = s("c1_06") - 0.15

    def ic_people(cr, T):
        for i, x in enumerate((-70, 0, 70)):
            p = sm.on_ground(sm.pose("cheer", x=x, s=0.42, smile=1), 90)
            sm.draw(cr, p, acc=[("cap",), ("tuft",), ("ponytail",)][i])

    def ic_gold(cr, T):
        P2.coin_pile(cr, 0, 95, 0.9)
        for i in range(4):
            P2.coin(cr, -60 + i * 40, -40 - 10 * math.sin(T * 3 + i), 26, rot=T * 3 + i)

    def ic_army(cr, T):
        for i, x in enumerate((-60, 0, 60)):
            p = sm.on_ground(sm.pose("stand", x=x, s=0.42, a1f=0, a1b=0), 90)
            sm.draw(cr, p, acc=GUARD)

    def ic_palace(cr, T):
        S.castle(cr, 0, 100, 0.33, t=T)

    b.add(st6, K.icons("", [(ic_people, "MILLIONS OF PEOPLE", w("c1_06", "millions")),
                            (ic_gold, "A TREASURY", w("c1_06", "treasury")),
                            (ic_army, "AN ARMY", w("c1_06", "army")),
                            (ic_palace, "A PALACE", w("c1_06", "palace"))], bg=(0.97, 0.94, 0.86), y=460), "slide", 0.4)
    for wd in ("millions", "treasury", "army", "palace"):
        b.fx(w("c1_06", wd), "pop", -8)
    t_sig = w("c1_06", "signature")

    # 6b. every law, coin, decision
    st6b = s("c1_06b") - 0.15

    @b.shot(st6b, "fade", 0.3)
    def yours(cr, t, d, T):
        vgrad(cr, (0.35, 0.10, 0.12), (0.12, 0.03, 0.05))
        radial_lines(cr, CX, 520, T, n=30, c=YELLOW, a=0.12, w=20)
        with K.ken(cr, t, d, 1.0, 1.06, CX, 560):
            P.throne(cr, CX, 900, 1.2)
            p = sm.pose("sit", x=CX, fo=0.0, a1f=60, a2f=40, a1b=-60, a2b=-40, smile=0.6, brow=0.3)
            p["y"] = 900 - 170
            sm.draw(cr, sm.idle(p, T, 2), acc=KING, ink=WHITE, fill=(0.3, 0.06, 0.08))
            for i, (lab, wd) in enumerate((("LAW", "law"), ("COIN", "coin"), ("DECISION", "decision"))):
                k = K.pop(T, w("c1_06b", wd))
                if k > 0:
                    a = -math.pi / 2 + (i - 1) * 0.9 + T * 0.2
                    label_box(cr, lab, CX + math.cos(a) * 520, 470 + math.sin(a) * 260, 50, c=INK, bg=YELLOW,
                              face=FONT_TITLE, bold=False, scale=k)
            stamp(cr, "ALL YOURS", CX, 980, T - w("c1_06b", "yours"), 70, c=YELLOW, rot=0.04)
    for wd in ("law", "coin", "decision"):
        b.fx(w("c1_06b", wd), "pop", -10)
    b.fx(w("c1_06b", "yours"), "stamp", -6)
    del t_sig

    # 7. the real question
    b.add(s("c1_07") - 0.2, K.real_question(s("c1_07")), "black", 0.4)
    b.fx(s("c1_07"), "tick", -8)
    b.fx(s("c1_07") + 0.5, "tock", -8)

    # 8. legend or villain?
    st8 = s("c1_08") - 0.1
    t_or = w("c1_08", "or the")

    def legend(cr, cx, T):
        radial_lines(cr, cx, 420, T, n=24, c=YELLOW, a=0.35, w=26)
        crowd(cr, T, n=14, y0=930, y1=1060, cheer=1.0, x0=cx - 500, x1=cx + 500, seed=5)
        K.person(cr, T, cx, 900, "cheer", acc=KING, s=1.1, smile=1.0)

    def villain(cr, cx, T):
        r2 = rng(3)
        for i in range(10):
            pts = []
            cxs, cys = cx + r2.uniform(-260, 260), 440 + r2.uniform(-200, 160)
            for j in range(40):
                a = j * 0.5 + T * r2.uniform(1, 3)
                pts.append((cxs + math.cos(a) * (40 + j * 3) * 0.9, cys + math.sin(a) * (40 + j * 3) * 0.6))
            polyline(cr, pts, 3, RED, 0.45)
        P2.book_big(cr, cx + 230, 760, 0.55, title="VILLAINS", c=(0.25, 0.05, 0.06))
        K.person(cr, T, cx - 80, 900, "hips", acc=KING, s=1.1, face=-1, smile=0.6, brow=1.0, ink=WHITE,
                 fill=(0.2, 0.04, 0.05))

    b.add(st8, K.split(dict(title="LEGENDARY RULER?", bg=(1.0, 0.95, 0.80), draw=legend),
                       dict(title="HISTORY'S VILLAIN?", bg=(0.25, 0.04, 0.06), draw=villain), t_or), "fade", 0.3)
    b.fx(st8, "chime", -8)
    b.fx(t_or, "glitch", -6)

    # 9. title
    st9 = e("c1_08") - 0.2

    @b.shot(st9, "cut")
    def title(cr, t, d, T):
        TITLE(cr, t)
    b.fx(st9, "whoosh", -4)
    b.fx(st9 + 0.5, "boom", 0)
    b.fx(st9 + 0.55, "shimmer", -8)
    return b.result()


