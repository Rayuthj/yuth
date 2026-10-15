"""King - Chapter 4: Everyone Wants Something (2:40-3:40)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 108, 0.7), ("c4_07", "mystery", "mystery", 70, 0.55),
                        ("c4_09", "discovery", "discovery", 100, 0.7)])


def queue(cr, T, cam, n=14, seed=8):
    r = rng(seed)
    kinds = [(("bearskin",), "GENERAL"), (("tie",), "BUSINESS"), (("hat",), "FARMER"), (("glasses", "tie"), "AMBASSADOR"),
             (("cap",), ""), (("ponytail",), ""), (("bun",), "")]
    for i in range(n):
        acc, _ = kinds[i % len(kinds)]
        x = 520 + i * 150 - cam
        if -100 < x < W + 100:
            K.person(cr, T, x, 900, "stand", face=-1, s=0.85, acc=acc, seed=i + seed, smile=r.uniform(-0.3, 0.6))


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. a line that never ends
    @b.shot(0, "fade", 0.3)
    def line_up(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 0.92, 900, 600):
            S.palace(cr, T)
            queue(cr, T, T * 120, n=40)
            P.throne(cr, 260, 900, 0.9)
            p = sm.pose("sit", x=260, face=1, smile=-0.2, brow=-0.3, gx=0.8)
            p["y"] = 900 - 130
            sm.draw(cr, sm.idle(p, T, 1), acc=KING)
        text(cr, "THE LINE NEVER ENDS", CX, 200, 60, face=FONT_TITLE, c=WHITE, outline=INK, ow=8,
             a=eout(prog(t, 0.6, 0.4)))
    b.fx(0.2, "murmur", -14, dur=3.5)

    # 2. generals, business owners, farmers
    st2 = s("c4_02") - 0.15
    asks = [("bearskin",), "BIGGER ARMY", "generals"], [("tie",), "LOWER TAXES", "business"], [("hat",), "RAIN", "farmers"]

    @b.shot(st2, "cut")
    def asks_shot(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.palace(cr, T)
            for i, (acc, want, wd) in enumerate(asks):
                k = K.pop(T, w("c4_02", wd))
                x = 420 + i * 420
                K.person(cr, T, x, 900, "point" if i < 2 else "point_up", face=1, acc=acc, seed=i, alpha=clamp(k * 2))
                if k > 0:
                    speech_bubble(cr, x + 60, 420, 320, 100, x + 20, 600, scale=k)
                    text(cr, want, x + 60, 420, 38, face=FONT_TITLE, c=[RED, GREEN, BLUE][i], a=clamp(k))
            kr = prog(T, w("c4_02", "sadly"), 0.4)
            K.hero(cr, T, 1650, 900, "shrug" if kr > 0 else "listen", acc=KING, face=-1)
            if kr > 0:
                P.cloud(cr, 1260, 220, 0.8)
                cross(cr, 1260, 220, 1.2, p=kr)
    for wd in ("generals", "business", "farmers"):
        b.fx(w("c4_02", wd), "pop", -10)
    b.fx(w("c4_02", "sadly"), "buzz", -14)

    # 3. gifts with strings attached
    st3 = s("c4_03") - 0.15
    t_fav = w("c4_03", "favor")

    @b.shot(st3, "fade", 0.3)
    def gifts(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            S.palace(cr, T)
            J = K.person(cr, T, 700, 900, "hold", face=1, acc=("glasses", "tie"), a1f=70, a2f=20)
            gx_, gy_ = J["hand_f"][0] + 60, J["hand_f"][1] - 30
            rrect(cr, gx_ - 70, gy_ - 60, 140, 120, 8, fill=RED, stroke=INK, lw=5)
            rect(cr, gx_ - 10, gy_ - 60, 20, 120, fill=YELLOW)
            rect(cr, gx_ - 70, gy_ - 10, 140, 20, fill=YELLOW)
            H = K.hero(cr, T, 1300, 900, "hold", acc=KING, face=-1, a1f=60, a2f=30)
            kf = prog(T, t_fav - 0.3, 0.6)
            if kf > 0:
                pts = bezier_pts([(gx_, gy_ + 60), ((gx_ + H["hand_f"][0]) / 2, gy_ + 260), (H["hand_f"][0], H["hand_f"][1])], 30)
                partial_poly(cr, pts, ease(kf), 4, INK)
                label_box(cr, "STRINGS ATTACHED", 1000, 300, 46, c=RED, scale=back(kf))
    b.fx(t_fav - 0.3, "swish", -10)

    # 3b. a golden horse and a very suspicious cheese
    st3b = s("c4_03b") - 0.15

    def ic_horse(cr, T):
        P2.horse(cr, 0, 110, 0.8)

    def ic_cheese(cr, T):
        P2.cheese(cr, 0, 60, 1.3)
        for i in range(3):
            f = (T * 0.7 + i / 3) % 1
            pts = [(-30 + i * 30 + 10 * math.sin(f * 9 + i), -40 - f * 140 - j * 10) for j in range(4)]
            polyline(cr, pts, 5, GREEN, 1 - f)

    b.add(st3b, K.icons("GIFTS FROM ABROAD", [(ic_horse, "A GOLDEN HORSE", w("c4_03b", "golden")),
                                              (ic_cheese, "A VERY SUSPICIOUS CHEESE", w("c4_03b", "suspicious"))],
                        bg=(0.97, 0.94, 0.86), y=520, size=1.3, label_size=40), "slide", 0.4)
    b.fx(w("c4_03b", "golden"), "ding", -10)
    b.fx(w("c4_03b", "suspicious"), "boing", -8)

    # 4-6. yes-men and the bridge to the moon
    st4 = s("c4_04") - 0.15

    def court(cr, T):
        S.palace(cr, T)
        if T > s("c4_06") - 0.1:
            k = ease(prog(T, s("c4_06"), 1.2))
            rrect(cr, 1340, 140, 460, 300, 12, fill=(0.93, 0.96, 1.0), stroke=INK, lw=5)
            circle(cr, 1720, 210, 46, fill=(0.95, 0.95, 0.85), stroke=INK, w=4)
            pts = [(1380, 420), (1500, 330), (1620, 260), (1700, 220)]
            partial_poly(cr, pts, k, 6, INK)
            for i in range(4):
                if k > i / 4:
                    line(cr, pts[i][0], pts[i][1], pts[i][0], 420, 3, INK)
            text(cr, "MOON BRIDGE (APPROVED)", 1570, 470, 28, face=FONT_HAND, bold=True, c=GREEN, a=k)

    nods = dict(head=0.0)
    b.add(st4, K.dialogue(tl, court, [
        dict(x=520, gy=900, acc=ADV, face=1, g="listen", kw=dict(smile=0.9)),
        dict(x=720, gy=900, acc=("glasses", "bowtie"), face=1, g="listen", kw=dict(smile=0.9)),
        dict(x=920, gy=900, acc=("mustache", "bowtie"), face=1, g="listen", kw=dict(smile=0.9)),
        dict(x=1280, gy=900, acc=KING, face=-1, g="present", talk_g="point_up"),
    ], [(3, "What if we built a bridge to the moon?", "c4_05", (1150, 330)),
        (0, "Magnificent idea, Your Majesty!", "c4_06", (520, 330))], zoom=(1.0, 1.05)), "fade", 0.3)
    del nods
    b.fx(s("c4_04") + 0.3, "boing", -16)
    b.fx(s("c4_06") + 0.6, "applause", -12, dur=1.6)

    # 7. what you want to hear vs need to hear
    st7 = s("c4_07") - 0.15
    t_want, t_need = w("c4_07", "want to hear"), w("c4_07", "need to hear")

    @b.shot(st7, "fade", 0.3)
    def hear(cr, t, d, T):
        fill_bg(cr, (0.95, 0.93, 0.88))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.04):
            K.hero(cr, T, CX, 980, "think", acc=KING, face=1, smile=-0.1, brow=-0.3)
            kw_ = K.pop(T, t_want)
            if kw_ > 0:
                speech_bubble(cr, 520, 360, 560, 220, 820, 520, fill=(1.0, 0.92, 0.95), scale=kw_)
                with xform(cr, 520, 360, max(0.01, kw_)):
                    text(cr, "WHAT YOU WANT", 0, -30, 46, face=FONT_TITLE, c=(0.85, 0.3, 0.5))
                    text(cr, "TO HEAR", 0, 30, 46, face=FONT_TITLE, c=(0.85, 0.3, 0.5))
                for i in range(3):
                    P.heart(cr, 330 + i * 190, 560, 0.3, a=clamp(kw_))
            kn = K.pop(T, t_need)
            if kn > 0:
                speech_bubble(cr, 1400, 360, 560, 220, 1100, 520, fill=(1.0, 0.97, 0.85), scale=kn)
                with xform(cr, 1400, 360, max(0.01, kn)):
                    text(cr, "WHAT YOU NEED", 0, -30, 46, face=FONT_TITLE, c=RED)
                    text(cr, "TO HEAR", 0, 30, 46, face=FONT_TITLE, c=RED)
                with group(cr, clamp(kn)):
                    polyline(cr, [(1400, 520), (1450, 600), (1350, 600)], 4, INK, closed=True, fill=YELLOW)
                    text(cr, "!", 1400, 578, 40, face=FONT_TITLE)
    b.fx(t_want, "pop", -10)
    b.fx(t_need, "alert", -12)

    # 8. yes-men until disaster struck
    st8 = s("c4_08") - 0.15
    t_dis = w("c4_08", "disaster")

    @b.shot(st8, "fade", 0.3)
    def disaster(cr, t, d, T):
        kd = prog(T, t_dis - 0.2, 1.2)
        sx, sy = shake(T - t_dis, 12 * max(0, 1 - (T - t_dis)) if T > t_dis else 0)
        with camera(cr, 1.0, CX - sx, CY - sy):
            vgrad(cr, (0.85, 0.80, 0.70), (0.65, 0.58, 0.50))
            S.floor(cr, 900, (0.55, 0.45, 0.35))
            S.castle(cr, CX, 900, 0.9, c=(0.75, 0.72, 0.68), t=T)
            if kd > 0:
                for i in range(6):
                    f = clamp(kd * 1.4 - i * 0.1)
                    rect(cr, 700 + i * 90, 500 + 400 * ein(f), 60, 40, fill=(0.75, 0.72, 0.68), stroke=INK, lw=4)
                polyline(cr, [(820, 560), (860, 640), (830, 720), (880, 800)], 6, INK)
            p = sm.pose("cheer", x=CX, s=0.9, smile=1.0)
            p = sm.on_ground(sm.idle(p, T, 2), 1030)
            sm.draw(cr, p, acc=("crown", "beard", "cape"))
            for i, x in enumerate((640, 760, 1160, 1280)):
                K.person(cr, T, x, 1030, "listen", face=1 if x < CX else -1, s=0.75, acc=ADV, seed=i,
                         head=8 * math.sin(T * 6 + i), smile=1.0)
        ko, kn_ = clamp(kd * 3), clamp(kd * 3 - 1)
        if ko < 1:
            text(cr, "YES, YOUR MAJESTY!", CX, 120 - 60 * ko, 56, face=FONT_TITLE, c=INK, a=1 - ko)
        if kn_ > 0:
            text(cr, "...UNTIL DISASTER", CX, 120, 66, face=FONT_TITLE, c=RED, a=kn_)
    b.fx(t_dis - 0.2, "crash", -6)

    # 9. reward bad news
    st9 = s("c4_09") - 0.15
    t_rew = w("c4_09", "reward")

    @b.shot(st9, "fade", 0.3)
    def new_rule(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            S.palace(cr, T)
            P2.parchment(cr, CX, 360, 760, 280, title="NEW RULE", lines_=["Bad news = a REWARD", "not a punishment."],
                         t_unroll=ease(prog(t, 0.2, 0.8)), size=44)
            kr = prog(T, t_rew, 0.5)
            J = K.person(cr, T, 700, 950, "hold", face=1, acc=ADV, a1f=70, a2f=20, smile=lerp(-0.4, 0.9, kr))
            rrect(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 70, 110, 140, 6, fill=WHITE, stroke=INK, lw=4)
            text(cr, "PROBLEM", J["hand_f"][0] + 65, J["hand_f"][1] - 30, 22, face=FONT_TITLE, c=RED)
            H = K.hero(cr, T, 1250, 950, "present" if kr > 0 else "listen", acc=KING, face=-1)
            if kr > 0:
                f = ease(kr)
                P2.coin(cr, lerp(H["hand_f"][0], J["hand_f"][0] + 80, f), lerp(H["hand_f"][1], J["hand_f"][1] - 120, f) -
                        120 * math.sin(f * math.pi), 34, rot=T * 6)
    b.fx(t_rew, "coins", -8, dur=0.8)

    # 10. suddenly, a lot more to say
    st10 = s("c4_10") - 0.15

    @b.shot(st10, "fade", 0.3)
    def more_to_say(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            S.palace(cr, T)
            for i, (x, acc) in enumerate(((420, ADV), (700, ("glasses", "bowtie")), (980, ("mustache", "bowtie")))):
                J = K.person(cr, T, x, 900, "present", face=1, acc=acc, seed=i, talk=0.5 + 0.5 * math.sin(T * 7 + i))
                k = K.pop(T, st10 + 0.4 + i * 0.4)
                if k > 0:
                    rrect(cr, x - 110, 300 - i * 30, 220, 150, 10, fill=WHITE, stroke=INK, lw=4, a=clamp(k))
                    pts = [(x - 90 + j * 36, 420 - i * 30 - 40 * math.sin(j + i) - j * 10) for j in range(6)]
                    polyline(cr, pts, 4, [RED, BLUE, GREEN][i], clamp(k))
            K.hero(cr, T, 1450, 900, "listen", acc=KING, face=-1, smile=0.6)
            text(cr, "USEFUL!", 1450, 360, 50, face=FONT_TITLE, c=GREEN, a=eout(prog(T, w("c4_10", "useful"), 0.4)))
    for i in range(3):
        b.fx(st10 + 0.4 + i * 0.4, "pop", -12)
    b.fx(w("c4_10", "useful"), "ding", -10)
    return b.result()
