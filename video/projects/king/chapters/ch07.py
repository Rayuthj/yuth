"""King - Chapter 7: Listening to the People (5:50-6:50)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403

DISGUISE = ("hat", "mustache")


def music_plan(tl):
    return K.music(tl, [(0.0, "playful", "playful", 104, 0.6), ("c7_03", "warm", "warm", 80, 0.55),
                        ("c7_06", "mystery", "mystery", 72, 0.5), ("c7_08", "uplift", "uplift", 96, 0.65),
                        ("c7_09", "playful", "playful", 108, 0.6)])


def peeking_crown(cr, J, s=1.0):
    """Crown tips poking out from under the hat."""
    hx, hy = J["head"]
    for dx in (-30, 0, 30):
        polyline(cr, [(hx + (dx - 10) * s, hy - 48 * s), (hx + dx * s, hy - 66 * s), (hx + (dx + 10) * s, hy - 48 * s)],
                 3, INK, closed=True, fill=GOLD)


def street(cr, T, cam=0.0):
    S.city(cr, T, cam, gy=880)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. something no king is supposed to do
    @b.shot(0, "fade", 0.3)
    def secret(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.1, CX, 560):
            S.palace(cr, T)
            J = K.hero(cr, T, CX, 900, "think", acc=KING, face=1, smile=0.6, brow=0.6, gx=1.0)
            del J
        text(cr, "A SECRET PLAN", CX, 200, 64, face=FONT_TITLE, c=WHITE, outline=INK, ow=8, a=eout(prog(t, 0.5, 0.4)))
    b.fx(0.6, "sparkle", -14)

    # 2. the world's worst disguise
    st2 = s("c7_02") - 0.15
    t_mus, t_hat, t_worst, t_sneak = w("c7_02", "mustache"), w("c7_02", "hat"), w("c7_02", "worst"), w("c7_02", "sneak")

    @b.shot(st2, "fade", 0.3)
    def disguise(cr, t, d, T):
        with K.ken(cr, t, d, 1.05, 1.0, CX, 600):
            S.palace(cr, T)
            P.door(cr, 1600, 880, 1.2, open_=ease(prog(T, t_sneak - 0.3, 0.5)))
            acc = ["tuft", "cape"]
            if T > t_mus:
                acc.append("mustache")
            if T > t_hat:
                acc.append("hat")
            else:
                acc.append("crown")
            if T < t_sneak:
                J = K.hero(cr, T, 820, 900, "hips" if T > t_worst else "stand", acc=tuple(acc), face=1, smile=0.7)
            else:
                x = lerp(820, 1640, ease(prog(T, t_sneak, 2.2)))
                J = K.hero(cr, T, x, 900, "stand", acc=tuple(acc), face=1, walk=0.5, smile=0.5, lean=10, a1f=50, a2f=60)
            if T > t_hat:
                peeking_crown(cr, J)
            for tt, lab, dx in ((t_mus, "FAKE MUSTACHE", -260), (t_hat, "HAT", 240)):
                k = K.pop(T, tt)
                if k > 0 and T < t_sneak:
                    label_box(cr, lab, J["head"][0] + dx, J["head"][1] - 120, 34, c=INK, scale=k)
            if t_worst < T < t_sneak + 0.6:
                label_box(cr, "WORST DISGUISE EVER", CX, 180, 52, c=RED, scale=K.pop(T, t_worst))
    b.fx(t_mus, "pop", -10)
    b.fx(t_hat, "pop", -10)
    b.fx(t_worst, "boing", -12)
    b.fx(t_sneak, "footsteps", -14, dur=2.0)

    # 2b. nobody recognizes you; pigeon steals sandwich; free
    st2b = s("c7_02b") - 0.15
    t_pig, t_free = w("c7_02b", "pigeon"), w("c7_02b", "free")

    @b.shot(st2b, "slide", 0.4)
    def freedom(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            street(cr, T, T * 40)
            for i in range(5):
                x = (i * 420 + T * (90 if i % 2 else -110)) % (W + 400) - 200
                K.person(cr, T, x, 900 + (i % 2) * 40, "stand", face=1 if i % 2 else -1, s=0.85, walk=0.6, seed=i * 3,
                         acc=[("cap",), ("ponytail",), ("glasses",), ("bun",), ("hat",)][i])
            kp = prog(T, t_pig - 0.4, 1.4)
            free = T > t_free
            J = K.hero(cr, T, 900, 920, "cheer" if free else "hold", acc=("tuft", "cape") + DISGUISE, face=1,
                       smile=1.0 if free else 0.4)
            peeking_crown(cr, J)
            if kp <= 0:
                P2.sandwich(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 10, 0.6)
            px = lerp(1500, J["hand_f"][0], ease(clamp(kp * 2))) if kp < 0.5 else lerp(J["hand_f"][0], 1900, ease(kp * 2 - 1))
            py = lerp(500, J["hand_f"][1] + 40, ease(clamp(kp * 2))) if kp < 0.5 else lerp(J["hand_f"][1] + 40, 300,
                                                                                            ease(kp * 2 - 1))
            if 0 < kp < 1:
                P2.pigeon(cr, px, py, 0.9, face=-1 if kp < 0.5 else 1, flap=1.0, t=T)
                if kp > 0.5:
                    P2.sandwich(cr, px + 50, py - 40, 0.5, rot=0.3)
            elif kp <= 0:
                P2.pigeon(cr, 1500, 500, 0.9, face=-1, flap=1.0, t=T)
            if free:
                text(cr, "FREE!", 900, 260, 90, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, scale=K.pop(T, t_free))
    b.fx(t_pig - 0.4, "flutter", -10)
    b.fx(t_free, "ding", -12)

    # 3. the nurse on the bus
    st3 = s("c7_03") - 0.15
    t_two, t_rent = w("c7_03", "two jobs"), w("c7_03", "rent")

    @b.shot(st3, "fade", 0.3)
    def bus_shot(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            fill_bg(cr, (0.98, 0.86, 0.45))
            rect(cr, -400, 860, W + 800, 400, fill=(0.55, 0.55, 0.6))
            for i in range(4):
                x0 = 120 + i * 460
                rrect(cr, x0, 200, 380, 300, 18, fill=(0.75, 0.88, 1.0))
                cr.save()
                cr.rectangle(x0, 200, 380, 300)
                cr.clip()
                for k in range(-1, 3):
                    bx = x0 + 40 + k * 200 - (T * 300 % 200)
                    rect(cr, bx, 380 - (k % 2) * 60, 90, 180, fill=(0.6, 0.65, 0.72))
                cr.restore()
                cr.new_path()
                rrect(cr, x0, 200, 380, 300, 18, stroke=INK, lw=6)
            line(cr, -400, 160, W + 400, 160, 10, (0.6, 0.6, 0.65))
            for x in (500, 1420):
                line(cr, x, 160, x, 860, 8, (0.75, 0.75, 0.8))
            for x in (700, 1200):
                rrect(cr, x - 150, 700, 300, 60, 14, fill=(0.25, 0.45, 0.75), stroke=INK, lw=5)
                rrect(cr, x + (100 if x < CX else -150), 560, 50, 200, 14, fill=(0.25, 0.45, 0.75), stroke=INK, lw=5)
            bump = 6 * math.sin(T * 9)
            p = sm.pose("sit", x=740, face=1, a1f=40, a2f=40, smile=0.3)
            p["y"] = 640 + bump
            J = sm.draw(cr, sm.idle(p, T, 1), acc=("tuft", "cape") + DISGUISE)
            peeking_crown(cr, J)
            env = tl.env("c7_03", T)
            p = sm.pose("sit", x=1160, face=-1, a1f=20, a2f=60, smile=-0.3, brow=-0.4)
            p["y"] = 640 + bump
            p = sm.talk(sm.idle(p, T, 5), T, 0.4 * env)
            J2 = sm.draw(cr, p, acc=("ponytail",))
            hx, hy = J2["head"]
            rect(cr, hx - 34, hy - 58, 68, 22, fill=WHITE, stroke=INK, lw=3)
            line(cr, hx - 8, hy - 47, hx + 8, hy - 47, 4, RED)
            line(cr, hx, hy - 55, hx, hy - 39, 4, RED)
            for tt, lab, x in ((t_two, "2 JOBS", 1420), (t_rent, "RENT: TOO HIGH", 1500)):
                k = K.pop(T, tt)
                if k > 0:
                    label_box(cr, lab, x, 260 if lab == "2 JOBS" else 380, 44, c=RED if "RENT" in lab else INK, scale=k)
        text(cr, "THE NURSE", 300, 110, 50, face=FONT_TITLE)
    b.fx(st3, "traffic", -18, dur=4.0)
    b.fx(t_two, "pop", -12)
    b.fx(t_rent, "pop", -10)

    # 4. the market: the new road skipped his neighborhood
    st4 = s("c7_04") - 0.15
    t_road, t_skip = w("c7_04", "road"), w("c7_04", "skipped")

    @b.shot(st4, "slide", 0.4)
    def market(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, 700, 600):
            street(cr, T, 300)
            P2.market_stall(cr, 520, 900, 1.3)
            K.person(cr, T, 520, 900, "present", face=1, acc=("mustache", "cap"), talk=tl.env("c7_04", T), seed=4)
            J = K.hero(cr, T, 900, 900, "listen", acc=("tuft", "cape") + DISGUISE, face=-1)
            peeking_crown(cr, J)
            k = back(prog(T, t_road - 0.3, 0.5))
            if k > 0:
                with xform(cr, 1450, 480, max(0.01, k)):
                    rrect(cr, -330, -260, 660, 520, 20, fill=(0.93, 0.95, 0.88), stroke=INK, lw=6)
                    text(cr, "THE NEW ROAD", 0, -215, 34, face=FONT_TITLE)
                    for (hx, hy) in ((-160, 40), (-80, 90), (-190, 140), (-90, 10), (-130, 190)):
                        P.house(cr, hx, hy, 0.18)
                    kr = prog(T, t_road, 1.6)
                    pts = [(-300, -150), (-60, -150), (60, -100), (120, 50), (120, 220)]
                    partial_poly(cr, pts, kr, 22, (0.4, 0.4, 0.45))
                    partial_poly(cr, pts, kr, 3, YELLOW)
                    if T > t_skip:
                        ks = clamp(prog(T, t_skip, 0.4))
                        ellipse(cr, -130, 100, 120, 130, stroke=RED, w=8, a=ks)
                        text(cr, "SKIPPED!", -130, -40, 40, face=FONT_TITLE, c=RED, a=ks)
    b.fx(t_road - 0.3, "whoosh", -14)
    b.fx(t_skip, "buzz", -12)

    # 5. a teenager: schools look great, not enough teachers
    st5 = s("c7_05") - 0.15
    t_teach = w("c7_05", "teachers")

    @b.shot(st5, "slide", 0.4)
    def teen(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            vgrad(cr, (0.75, 0.88, 0.98), (0.95, 0.97, 0.98))
            S.floor(cr, 880, (0.80, 0.85, 0.70))
            rect(cr, 760, 360, 760, 520, fill=(0.95, 0.88, 0.78), stroke=INK, lw=6)
            polyline(cr, [(720, 360), (1140, 200), (1560, 360)], 6, INK, closed=True, fill=RED)
            text(cr, "NEW SCHOOL", 1140, 310, 40, face=FONT_TITLE, c=WHITE)
            for i in range(3):
                for j in range(2):
                    x, y = 830 + i * 230, 420 + j * 210
                    rect(cr, x, y, 160, 150, fill=(0.85, 0.93, 1.0), stroke=INK, lw=5)
                    rect(cr, x + 30, y + 100, 100, 12, fill=(0.6, 0.45, 0.3))
                    if T > t_teach:
                        text(cr, "?", x + 80, y + 60, 50, face=FONT_TITLE, c=RED, a=prog(T, t_teach + (i + j) * 0.1, 0.3))
            K.person(cr, T, 480, 900, "shrug" if T > t_teach else "point", face=1, s=0.85, acc=("cap",),
                     talk=tl.env("c7_05", T), seed=8)
            J = K.hero(cr, T, 260, 900, "listen", acc=("tuft", "cape") + DISGUISE, face=1)
            peeking_crown(cr, J)
            if T > t_teach:
                label_box(cr, "NOT ENOUGH TEACHERS", 1140, 960, 46, c=RED, scale=K.pop(T, t_teach))
    b.fx(t_teach, "alert", -14)

    # 6. none of this was in your reports
    st6 = s("c7_06") - 0.15
    t_adv = w("c7_06", "advisors")

    @b.shot(st6, "fade", 0.3)
    def reports(cr, t, d, T):
        fill_bg(cr, PAPER)
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.05):
            with xform(cr, 700, 520, 1.0, -0.03):
                rect(cr, -330, -400, 660, 800, fill=WHITE, stroke=INK, lw=6)
                text(cr, "ROYAL REPORT", 0, -340, 50, face=FONT_TITLE)
                for i, lab in enumerate(("HOUSING", "ROADS", "SCHOOLS", "JOBS", "HAPPINESS")):
                    y = -220 + i * 110
                    text(cr, lab, -260, y, 40, face=FONT_HAND, bold=True, align="left")
                    kk = prog(T, st6 + 0.3 + i * 0.25, 0.3)
                    if kk > 0:
                        polyline(cr, [(170, y), (200, y + 25), (250, y - 25)], 8, GREEN, a=kk)
                text(cr, "EVERYTHING IS GREAT! :)", 0, 340, 40, face=FONT_TITLE, c=GREEN)
            ka = prog(T, t_adv - 0.3, 0.5)
            if ka > 0:
                x = lerp(2100, 1450, ease(ka))
                K.person(cr, T, x, 980, "point_up", face=-1, acc=ADV, smile=1.0, seed=2)
                if ka >= 1:
                    speech_bubble(cr, x - 40, 420, 380, 130, x - 30, 560, scale=K.pop(T, t_adv + 0.3))
                    text(cr, "All great, sire!", x - 40, 420, 42, face=FONT_HAND, bold=True, a=clamp(K.pop(T, t_adv + 0.3)))
    for i in range(5):
        b.fx(st6 + 0.3 + i * 0.25, "tick", -16)
    b.fx(t_adv - 0.3, "whoosh", -14)

    # 7. numbers on a spreadsheet are real lives
    st7 = s("c7_07") - 0.15
    t_lives = w("c7_07", "real lives")

    @b.shot(st7, "fade", 0.3)
    def sheet(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 480):
            S.palace(cr, T, warm=0.5)
            src(cr, (0.0, 0.0, 0.0), 0.35)
            cr.paint()
            P2.spreadsheet(cr, CX, 430, k_people=prog(T, t_lives - 0.3, 1.6), t=T)
            K.hero(cr, T, 300, 980, "think", acc=KING, face=1, s=0.9)
            if T > t_lives:
                text(cr, "REAL LIVES", CX, 860, 72, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, scale=K.pop(T, t_lives))
    b.fx(t_lives - 0.3, "shimmer", -12)

    # 8. town hall meetings
    st8 = s("c7_08") - 0.15

    @b.shot(st8, "fade", 0.3)
    def town_hall(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            fill_bg(cr, (0.90, 0.86, 0.78))
            S.floor(cr, 760, (0.62, 0.48, 0.34))
            rect(cr, 560, 80, 800, 110, fill=(0.20, 0.35, 0.60), stroke=INK, lw=6)
            text(cr, "TOWN HALL: ASK ANYTHING", CX, 135, 48, face=FONT_TITLE, c=WHITE)
            rect(cr, CX - 90, 560, 180, 200, fill=(0.55, 0.38, 0.22), stroke=INK, lw=6)
            line(cr, CX + 40, 560, CX + 70, 470, 5, INK)
            circle(cr, CX + 72, 462, 12, fill=INK)
            K.hero(cr, T, CX - 20, 760, "present", acc=KING, face=1, s=0.8, talk=0.0)
            crowd(cr, T, n=30, y0=900, y1=1080, cheer=0.0, x0=-50, x1=1970, s0=0.6, s1=0.85)
    b.fx(st8, "murmur", -14, dur=3.0)

    # 8b. no guards, no scripts, no advisors
    st8b = s("c7_08b") - 0.15

    def crossed(draw):
        def fn(cr, T, draw=draw):
            draw(cr, T)
        return fn

    def ic_guard(cr, T):
        p = sm.pose("stand", x=0, s=0.7)
        sm.draw(cr, sm.on_ground(p, 130), acc=GUARD)

    def ic_script(cr, T):
        rect(cr, -80, -110, 160, 220, fill=WHITE, stroke=INK, lw=5)
        for i in range(6):
            line(cr, -55, -70 + i * 30, 55, -70 + i * 30, 4, MID)
        text(cr, "SCRIPT", 0, -90, 26, face=FONT_TITLE)

    def ic_whisper(cr, T):
        p = sm.pose("stand", x=0, s=0.7, a1f=80, a2f=110)
        sm.draw(cr, sm.on_ground(p, 130), acc=ADV)
        text(cr, "psst...", 80, -110, 30, face=FONT_HAND, bold=True)

    items = []
    for fn_, lab, wd in ((ic_guard, "NO GUARDS", "guards"), (ic_script, "NO SCRIPTS", "scripts"),
                         (ic_whisper, "NO WHISPERING", "advisors")):
        ta = w("c7_08b", wd)

        def drawx(cr, T, fn_=fn_, ta=ta):
            fn_(cr, T)
            kx = prog(T, ta + 0.25, 0.25)
            if kx > 0:
                partial_line(cr, -120, -120, 120, 120, kx, 16, RED)
                partial_line(cr, 120, -120, -120, 120, clamp(kx * 2 - 1), 16, RED)
        items.append((drawx, lab, ta))
    b.add(st8b, K.icons("JUST YOU AND THE PEOPLE", items, y=520, size=1.1, label_size=40), "fade", 0.3)
    for wd in ("guards", "scripts", "advisors"):
        b.fx(w("c7_08b", wd) + 0.25, "scratch", -14)

    # 9. tough, rude, and Mondays
    st9 = s("c7_09") - 0.15
    t_tough, t_rude, t_kid = w("c7_09", "tough"), w("c7_09", "rude"), w("c7_09", "one kid")

    @b.shot(st9, "fade", 0.3)
    def questions(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            fill_bg(cr, (0.90, 0.86, 0.78))
            S.floor(cr, 760, (0.62, 0.48, 0.34))
            K.hero(cr, T, 1500, 760, "listen", acc=KING, face=-1, s=0.8, smile=0.4 if T < t_kid else 0.8)
            for i, (x, acc, g, tt, txt, col) in enumerate((
                    (300, ("glasses",), "point", t_tough, "WHY ARE PRICES SO HIGH?", INK),
                    (680, ("cap",), "point", t_rude, "#@%&!", RED))):
                K.person(cr, T, x, 900, g if T > tt else "stand", face=1, s=0.85, acc=acc, seed=i)
                k = K.pop(T, tt)
                if k > 0:
                    speech_bubble(cr, x + 60, 470 - i * 30, 420 if i == 0 else 220, 110, x + 10, 600, scale=k)
                    text(cr, txt, x + 60, 470 - i * 30, 32 if i == 0 else 44, face=FONT_HAND if i == 0 else FONT_TITLE,
                         bold=True, c=col, a=clamp(k))
            K.person(cr, T, 1050, 900, "point_up" if T > t_kid else "stand", face=1, s=0.55, acc=("cap",), seed=7,
                     smile=0.9)
            k = K.pop(T, t_kid + 0.4)
            if k > 0:
                speech_bubble(cr, 1060, 300, 560, 150, 1050, 650, scale=k, fill=(1.0, 0.97, 0.85))
                text(cr, "Can you make MONDAYS", 1060, 275, 40, face=FONT_HAND, bold=True, a=clamp(k))
                text(cr, "illegal?", 1060, 325, 40, face=FONT_HAND, bold=True, c=RED, a=clamp(k))
    b.fx(t_tough, "pop", -12)
    b.fx(t_rude, "buzz", -14)
    b.fx(t_kid + 0.4, "boing", -12)

    # 10. you're still thinking about that one
    st10 = s("c7_10") - 0.2

    @b.shot(st10, "cut")
    def monday(cr, t, d, T):
        with K.ken(cr, t, d, 1.15, 1.25, 1500, 560):
            fill_bg(cr, (0.90, 0.86, 0.78))
            S.floor(cr, 760, (0.62, 0.48, 0.34))
            J = K.hero(cr, T, 1500, 760, "think", acc=KING, face=-1, s=0.8, brow=0.4)
            hx, hy = J["head"]
            for i, r in enumerate((10, 16, 22)):
                circle(cr, hx - 60 - i * 40, hy - 70 - i * 40, r, fill=WHITE, stroke=INK, w=4)
            rrect(cr, hx - 470, hy - 330, 300, 200, 40, fill=WHITE, stroke=INK, lw=5)
            rect(cr, hx - 400, hy - 300, 160, 140, fill=WHITE, stroke=INK, lw=4)
            rect(cr, hx - 400, hy - 300, 160, 40, fill=RED, stroke=INK, lw=4)
            text(cr, "MON", hx - 320, hy - 280, 26, face=FONT_TITLE, c=WHITE)
            text(cr, "?", hx - 320, hy - 205, 60, face=FONT_TITLE, c=INK)
    b.fx(st10 + 0.3, "tick", -14)
    return b.result()
