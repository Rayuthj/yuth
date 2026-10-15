"""King - Chapter 8: Rules for the Ruler (6:50-7:50)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403

JOHN = ("crown", "beard", "cape")
BARON = ("hat", "beard")


def music_plan(tl):
    return K.music(tl, [(0.0, "discovery", "discovery", 100, 0.65), ("c8_05", "playful", "playful", 108, 0.6),
                        ("c8_08", "wonder", "wonder", 76, 0.6), ("c8_10", "uplift", "uplift", 92, 0.7)])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. the boldest idea yet
    t_idea = w("c8_01", "boldest")

    @b.shot(0, "fade", 0.3)
    def idea(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.1, CX, 520):
            S.dark_room(cr, T, 960, 260, flicker=0.05)
            P.desk(cr, CX, 880, 600)
            J = K.hero(cr, T, CX, 900, "point_up" if T > t_idea else "think", acc=KING, face=1, ink=(0.9, 0.9, 0.95),
                       fill=(0.12, 0.13, 0.17), smile=0.8 if T > t_idea else 0.0, eye=1.2 if T > t_idea else 1.0)
            k = K.pop(T, t_idea)
            if k > 0:
                glow(cr, J["head"][0], J["head"][1] - 190, 260, YELLOW, 0.4 * clamp(k))
                P.lightbulb(cr, J["head"][0], J["head"][1] - 190, 1.1 * k, on=1.0, t=T)
        vignette(cr, 0.4)
    b.fx(t_idea, "bulb", -8)

    # 2. the ruler follows the rules too
    st2 = s("c8_02") - 0.15
    t_too = w("c8_02", "too")

    @b.shot(st2, "fade", 0.3)
    def everyone(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.18)
        with K.ken(cr, t, d, 1.0, 1.04):
            kb = back(prog(T, st2 + 0.2, 0.5))
            with xform(cr, CX, 260, max(0.01, kb)):
                rrect(cr, -420, -90, 840, 180, 20, fill=(0.20, 0.35, 0.60), stroke=INK, lw=6)
                text(cr, "THE RULES", 0, 0, 80, face=FONT_TITLE, c=WHITE)
            for i, (x, acc) in enumerate(((360, ("cap",)), (560, ("ponytail",)), (760, ("glasses",)), (1160, ("hat",)),
                                          (1360, ("bun",)), (1560, ("hardhat",)))):
                K.person(cr, T, x, 900, "stand", face=1 if x < CX else -1, s=0.85, acc=acc, seed=i, smile=0.5)
            kk = ease(prog(T, t_too - 0.4, 0.8))
            J = K.hero(cr, T, CX, lerp(1300, 900, kk), "wave" if kk >= 1 else "stand", acc=KING, face=1, smile=0.8)
            if kk >= 1:
                for x in (360, 560, 760, CX, 1160, 1360, 1560):
                    line(cr, x, 820 - 420 if x != CX else J["head"][1] - 90, x, 380, 3, (0.2, 0.35, 0.6), 0.25)
                text(cr, "EVERYONE. EVEN THE KING.", CX, 1010, 56, face=FONT_TITLE, c=RED, a=eout(prog(T, t_too + 0.3, 0.4)))
    b.fx(st2 + 0.2, "pop", -10)
    b.fx(t_too, "ding", -12)

    # 3. a constitution that limits your own power
    st3 = s("c8_03") - 0.15
    t_lim = w("c8_03", "limits")

    @b.shot(st3, "fade", 0.3)
    def constitution(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, 900, 520):
            S.palace(cr, T, warm=0.6)
            P.desk(cr, 1000, 900, 700)
            ku = prog(T, st3 + 0.2, 0.8)
            P2.parchment(cr, 1100, 560, 560, 520, title="CONSTITUTION",
                         lines_=["1. The king must", "   follow the law.", "2. The people", "   choose leaders."],
                         t_unroll=ku, size=32, rot=-0.03)
            J = K.hero(cr, T, 640, 900, "write", acc=KING, face=1)
            hx, hy = J["hand_f"]
            line(cr, hx, hy, hx + 50, hy - 90, 5, INK)
            polyline(cr, [(hx + 50, hy - 90), (hx + 90, hy - 160), (hx + 60, hy - 80)], 3, INK, closed=True, fill=WHITE)
            if T > t_lim:
                label_box(cr, "LIMITS ON MY OWN POWER", 1100, 210, 44, c=RED, scale=K.pop(T, t_lim))
    b.fx(st3 + 0.2, "page", -10)
    b.fx(st3 + 1.0, "scribble", -14, dur=1.5)

    # 4. courts, free press, elections, term limits
    st4 = s("c8_04") - 0.15

    def ic_court(cr, T):
        P.scale_balance(cr, 0, 110, 0.75, tilt=0.06 * math.sin(T * 2))
        P2.gavel(cr, 80, -40, 0.55, rot=-0.6)

    def ic_press(cr, T):
        P2.newspaper(cr, 0, -10, 0.55, headline="FREE PRESS", rot=0.05)

    def ic_vote(cr, T):
        P2.ballot_box(cr, 0, 120, 0.8, drop=(T * 0.8) % 1.4)

    def ic_term(cr, T):
        P2.hourglass(cr, 0, -10, 0.7, p=(T * 0.15) % 1.0, t=T)

    b.add(st4, K.icons("RULES FOR THE RULER", [(ic_court, "COURTS", w("c8_04", "independent courts")),
                                              (ic_press, "FREE PRESS", w("c8_04", "free press")),
                                              (ic_vote, "ELECTIONS", w("c8_04", "elections")),
                                              (ic_term, "TERM LIMITS", w("c8_04", "term limits"))],
                       y=540, size=1.0, label_size=42), "fade", 0.3)
    for wd in ("independent courts", "free press", "elections", "term limits"):
        b.fx(w("c8_04", wd), "pop", -10)

    # 5. advisors nearly faint; one actually does
    st5 = s("c8_05") - 0.15
    t_does = w("c8_05", "actually")

    @b.shot(st5, "fade", 0.3)
    def faint(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            S.palace(cr, T)
            for i, x in enumerate((560, 820, 1100, 1360)):
                if i == 2:
                    kf = ease(prog(T, t_does + 0.2, 0.6))
                    p = sm.pose("surprised", x=x, face=-1, eye=1.4, smile=-0.5)
                    p = sm.on_ground(sm.idle(p, T, i), 900)
                    with xform(cr, x - 60 * kf, 900, 1.0, -1.45 * kf):
                        with xform(cr, -x, -900):
                            sm.draw(cr, p, acc=ADV)
                    if kf >= 1:
                        for k in range(3):
                            a = T * 4 + k * 2.1
                            text(cr, "*", x - 300 + 50 * math.cos(a), 840 + 18 * math.sin(a), 40, face=FONT_TITLE, c=YELLOW)
                else:
                    K.person(cr, T, x, 900, "surprised", face=1 if i == 0 else -1, acc=ADV, seed=i, eye=1.4,
                             head=6 * math.sin(T * 12 + i))
            K.hero(cr, T, 200, 900, "shrug", acc=KING, face=1, smile=0.4)
    b.fx(st5 + 0.2, "gulp", -12)
    b.fx(t_does + 0.7, "thud", -6)

    # 6-7. advisor vs. hero
    st6 = s("c8_06") - 0.2

    def setting(cr, T):
        S.palace(cr, T)

    b.add(st6, K.dialogue(tl, setting, [
        dict(x=1250, gy=900, acc=ADV, face=-1, g="worried", talk_g="worried"),
        dict(x=640, gy=900, acc=KING, face=1, g="stand", talk_g="present"),
    ], [
        (0, "Your Majesty, you're giving your power away!", "c8_06", (1300, 330)),
        (1, "No. I'm making sure nobody can ever misuse it. Including me.", "c8_07", (680, 330)),
    ], zoom=(1.05, 1.12), focus=(CX, 600)), "fade", 0.3)

    # 8. Magna Carta, 1215
    st8 = s("c8_08") - 0.2
    t_1215, t_john, t_mc, t_law = (w("c8_08", "1215"), w("c8_08", "king john"), w("c8_08", "magna carta"),
                                   w("c8_08", "not above"))

    @b.shot(st8, "fade", 0.5)
    def magna(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            S.field(cr, T, gy=880, sky=((0.85, 0.80, 0.62), (0.96, 0.92, 0.80)), grass=(0.62, 0.70, 0.40))
            for x, c in ((260, RED), (1680, BLUE)):
                polyline(cr, [(x - 160, 880), (x, 560), (x + 160, 880)], 6, INK, closed=True, fill=c)
                line(cr, x, 560, x, 480, 5, INK)
                polyline(cr, [(x, 480), (x + 60, 500), (x, 520)], 4, INK, closed=True, fill=YELLOW)
            rect(cr, 760, 760, 400, 30, fill=(0.55, 0.38, 0.22), stroke=INK, lw=5)
            for x in (790, 1130):
                line(cr, x, 790, x, 880, 6, INK)
            P2.parchment(cr, CX, 700, 260, 160, title="", t_unroll=1.0, s=0.8)
            k = K.pop(T, t_mc)
            if k > 0:
                label_box(cr, "MAGNA CARTA", CX - 60, 950, 44, c=INK, scale=k, face=FONT_SERIF)
            sign_k = ease(prog(T, t_mc + 0.3, 0.8))
            K.person(cr, T, 1000, 880, "write" if sign_k < 1 else "hips", face=-1, acc=JOHN, seed=3,
                     smile=-0.6, brow=-0.6)
            for i, x in enumerate((520, 640, 1300, 1420)):
                K.person(cr, T, x, 880, "point" if i in (1, 2) else "hips", face=1 if x < CX else -1, s=0.95, acc=BARON,
                         seed=i + 5, smile=0.2, brow=-0.3)
            if T > t_john:
                label_box(cr, "KING JOHN", 1000, 480, 34, c=INK, scale=K.pop(T, t_john))
        kt = K.pop(T, t_1215)
        if kt > 0:
            text(cr, "1215", CX, 150, 120, face=FONT_TITLE, c=WHITE, outline=INK, ow=10, scale=kt)
        if T > t_law:
            label_box(cr, "EVEN THE KING IS NOT ABOVE THE LAW", CX, 1010, 46, c=RED, scale=K.pop(T, t_law))
    b.fx(t_1215, "stamp", -10)
    b.fx(t_mc + 0.3, "scribble", -14, dur=0.9)
    b.fx(t_law, "ding", -12)

    # 9. it took centuries
    st9 = s("c8_09") - 0.15
    t_cent, t_dem = w("c8_09", "centuries"), w("c8_09", "democracies")

    def ic_doc(c_):
        def f(cr, T, c_=c_):
            rect(cr, -55, -70, 110, 140, fill=(0.96, 0.89, 0.72), stroke=INK, lw=4)
            for i in range(4):
                line(cr, -35, -40 + i * 25, 35, -40 + i * 25, 3, MID)
            circle(cr, 30, 50, 14, fill=c_, stroke=INK, w=3)
        return f

    def ic_ballot(cr, T):
        P2.ballot_box(cr, 0, 80, 0.55)

    b.add(st9, K.timeline("IT TOOK CENTURIES", [("1215\nMAGNA CARTA", st9 + 0.4, ic_doc(RED)),
                                                ("1689\nENGLISH BILL OF RIGHTS", t_cent, ic_doc(BLUE)),
                                                ("1787\nU.S. CONSTITUTION", t_cent + 0.7, ic_doc(GREEN)),
                                                ("TODAY\nMANY DEMOCRACIES", t_dem, ic_ballot)], st9 + 0.3,
                          y=640, x0=160, x1=1760), "fade", 0.3)
    b.fx(st9 + 0.4, "pop", -12)
    b.fx(t_cent, "pop", -12)
    b.fx(t_cent + 0.7, "pop", -12)
    b.fx(t_dem, "chime", -12)

    # 10. the strongest thing you can do with power
    st10 = s("c8_10") - 0.15
    t_put = w("c8_10", "put limits")

    @b.shot(st10, "fade", 0.4)
    def strongest(cr, t, d, T):
        fill_bg(cr, (0.95, 0.94, 0.90))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.05):
            text(cr, "THE STRONGEST THING YOU CAN DO WITH POWER...", CX, 380, 56, face=FONT_TITLE,
                 a=eout(prog(t, 0.1, 0.5)))
            k = eout(prog(T, t_put, 0.4))
            text(cr, "...IS PUT LIMITS ON IT.", CX, 540, 100, face=FONT_TITLE, c=RED, a=k, scale=lerp(1.25, 1.0, k))
            K.hero(cr, T, CX, 1000, "confident" if T > t_put else "stand", acc=KING, face=1, s=0.6, smile=0.8)
    b.fx(t_put, "stamp", -8)
    return b.result()
