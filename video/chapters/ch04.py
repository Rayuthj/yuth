"""Chapter 4 - You Can Predict People (2:40-3:40)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

WALK_Y = 900
HUD = CYAN


def city(cr, t, cam_x=0.0, sky=((0.80, 0.88, 0.97), (0.96, 0.96, 0.97))):
    vgrad(cr, *sky)
    with camera(cr, 1.0, CX + cam_x * 0.3, CY):
        P.skyline(cr, -800, 720, 3600, 420, seed=51, fill=(0.80, 0.82, 0.86), win=False)
    with camera(cr, 1.0, CX + cam_x * 0.6, CY):
        P.skyline(cr, -800, 760, 3600, 360, seed=52, fill=(0.62, 0.65, 0.72), win=True)
    rect(cr, 0, 760, W, 320, fill=(0.86, 0.85, 0.82))
    ground(cr, 760, MID, 3)
    for i in range(-2, 12):
        x = (i * 240 - cam_x) % (W + 480) - 240
        line(cr, x, 760, x - 120, H, 3, MID, 0.5)


def hud(cr, T, a=1.0, label="ANALYZING..."):
    if a <= 0:
        return
    m, L = 60, 90
    for (x, y, dx, dy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        line(cr, x, y, x + dx * L, y, 6, HUD, a)
        line(cr, x, y, x, y + dy * L, 6, HUD, a)
    sy = (T * 400) % H
    line(cr, 0, sy, W, sy, 3, HUD, 0.25 * a)
    if label:
        text(cr, label, m + 20, H - m - 40, 30, c=HUD, a=a * (0.6 + 0.4 * math.sin(T * 8)), face=FONT_BOLD, align="left")


def tag(cr, x, y, txt, pct, k, c=HUD):
    """Prediction tag with a probability bar."""
    if k <= 0:
        return
    with xform(cr, x, y, max(0.01, back(k))):
        rrect(cr, -150, -50, 300, 100, 12, fill=(0.05, 0.12, 0.18), stroke=c, lw=4, a=0.92)
        text(cr, txt, 0, -18, 28, c=WHITE, face=FONT_BOLD)
        rrect(cr, -120, 14, 240, 18, 9, fill=(0.2, 0.3, 0.35))
        rrect(cr, -120, 14, 240 * pct * clamp(k * 1.5), 18, 9, fill=c)
        text(cr, f"{int(pct * 100 * clamp(k * 1.5))}%", 0, 62, 26, c=c, face=FONT_BOLD)


def crowd(seed=21, n=10):
    r = rng(seed)
    out = []
    for i in range(n):
        out.append(dict(x0=r.uniform(-300, W + 300), y=r.uniform(780, 1000), sp=r.uniform(70, 130) * r.choice([-1, 1]),
                        s=r.uniform(0.62, 0.85), ph=r.uniform(0, 4),
                        acc=r.choice([(), ("cap",), ("ponytail",), ("glasses",), ("tie",), ("bun",)])))
    return sorted(out, key=lambda c: c["y"])


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w
    people = crowd()

    def draw_crowd(cr, t, slow=1.0, trees=0.0, T=0.0, hero_x=None):
        heads = []
        for i, c in enumerate(people):
            x = (c["x0"] + c["sp"] * t * slow) % (W + 600) - 300
            p = sm.walk(sm.pose(x=x, s=c["s"], face=1 if c["sp"] > 0 else -1), (t + c["ph"]) * slow, 0.95)
            p = sm.on_ground(p, c["y"])
            J = sm.draw(cr, p, ink=GRAY, acc=c["acc"])
            heads.append(J["head"])
            if trees > 0 and i % 3 == 1:
                P.decision_tree(cr, J["head"][0], J["head"][1] - 70 * c["s"], depth=3, spread=90, dy=55,
                                p=trees, ink=HUD, lw=3, highlight=[i % 2, (i + 1) % 2, 0], hc=YELLOW)
        return heads

    # ------------------------------------------------------------ 1. into the city
    t_int = w("c4_01", "interesting")

    @b.shot(0, "fade", 0.4)
    def street(cr, t, d, T):
        cam = T * 60
        city(cr, T, cam)
        draw_crowd(cr, T)
        x = lerp(-100, 700, ease(prog(t, 0, 3.0)))
        p = sm.walk(sm.pose(x=x, face=1, smile=0.5, s=1.05), T, 1.0) if t < 3.0 else sm.pose("confident", x=x, s=1.05)
        p = sm.on_ground(p, 1040)
        k = prog(T, t_int, 0.4)
        if k > 0:
            p = sm.apply(p, brow=0.6, smile=0.8)
        J = sm.hero(cr, p)
        if k > 0:
            for ex in (-9, 9):
                glow(cr, J["head"][0] + 11 + ex, J["head"][1] - 4, 40, HUD, 0.8 * k)
        hud(cr, T, k * 0.9, "SCAN MODE")

    b.fx(0.2, "crowd", -16, dur=tl.dur - 0.5)
    b.fx(t_int, "scan", -8)

    # ------------------------------------------------------------ 2. habits, incentives, routines
    st2 = s("c4_02") - 0.2
    words = [("HABITS", "habits", 420), ("INCENTIVES", "incentives", 960), ("ROUTINES", "routines", 1500)]

    @b.shot(st2, "cut")
    def patterns(cr, t, d, T):
        city(cr, T, T * 60, sky=((0.55, 0.65, 0.78), (0.75, 0.78, 0.82)))
        src(cr, (0.0, 0.1, 0.2), 0.25)
        cr.paint()
        draw_crowd(cr, T, slow=0.25, trees=ease(prog(t, 0.3, 1.5)), T=T)
        for lab, word, x in words:
            k = back(prog(T, w("c4_02", word), 0.4))
            if k > 0:
                label_box(cr, lab, x, 220, 46, c=HUD, bg=(0.05, 0.12, 0.18), face=FONT_BOLD, bold=False, scale=k)
        text(cr, "PEOPLE AREN'T RANDOM", CX, 110, 56, face=FONT_TITLE, c=WHITE, a=eout(prog(t, 0.2, 0.4)))
        hud(cr, T, 1.0, "")

    b.fx(st2, "slowmo", -8)
    for lab, word, x in words:
        b.fx(w("c4_02", word), "blip", -8)

    # ------------------------------------------------------------ 3. the man checking his watch
    st3 = s("c4_03") - 0.2
    t_late = w("c4_03", "late")

    @b.shot(st3, "cut")
    def watch(cr, t, d, T):
        city(cr, T, 200 + T * 30)
        with ken(cr, t, d, 1.1, 1.18, 820, 640):
            x = lerp(500, 1100, t / d)
            p = sm.walk(sm.pose(x=x, face=1), T * 1.4, 1.3)
            p = sm.apply(p, a1f=40, a2f=125, head=10, gy=0.6, gx=0.4, brow=-0.6, smile=-0.3)
            p = sm.on_ground(p, 900)
            J = sm.draw(cr, p, acc=("tie",))
            hx, hy = J["hand_f"]
            circle(cr, hx, hy, 14, fill=WHITE, stroke=INK, w=4)
            line(cr, hx, hy, hx, hy - 9, 3, INK)
            line(cr, hx, hy, hx + 6, hy, 3, INK)
            for i in range(3):
                circle(cr, J["head"][0] + 50 + i * 8, J["head"][1] - 40 - i * 12, 6 - i, fill=CYAN)
            P.decision_tree(cr, J["head"][0], J["head"][1] - 80, depth=2, spread=110, dy=70, p=ease(prog(t, 0.3, 0.8)),
                            ink=HUD, lw=4, highlight=[1, 1], hc=YELLOW)
            tag(cr, J["head"][0] + 300, J["head"][1] - 60, "RUNNING LATE", 0.87, prog(T, t_late - 0.2, 0.5))
        hud(cr, T, 1.0, "SUBJECT 041")

    b.fx(st3, "blip", -10)
    b.fx(t_late - 0.2, "predict", -8)

    # ------------------------------------------------------------ 4. the woman and the menu
    st4 = s("c4_04") - 0.2
    t_change = w("c4_04", "change")

    @b.shot(st4, "slide", 0.4)
    def cafe(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.06, 900, 560):
            fill_bg(cr, (0.97, 0.93, 0.86))
            rect(cr, -200, 900, W + 400, 380, fill=(0.62, 0.45, 0.32))
            ground(cr, 900, x0=-200, x1=W + 200)
            rrect(cr, 920, 120, 700, 420, 14, fill=(0.15, 0.15, 0.17), stroke=(0.5, 0.35, 0.2), lw=12)
            text(cr, "MENU", 1270, 180, 54, face=FONT_HAND, bold=True, c=WHITE)
            items = ["COFFEE ........ 3", "TEA ............. 2", "SMOOTHIE ..... 4", "HOT CHOCOLATE 3"]
            for i, it in enumerate(items):
                text(cr, it, 1000, 260 + i * 66, 40, face=FONT_HAND, c=WHITE, align="left")
            rect(cr, 900, 680, 900, 220, fill=(0.80, 0.62, 0.45), stroke=INK, lw=6)
            P.coffee(cr, 1500, 680, 0.8, T)
            p = sm.pose("think", x=700, face=1, gy=-0.7, gx=0.8)
            p = sm.on_ground(sm.idle(p, T, 2), 900)
            J = sm.draw(cr, p, acc=("ponytail",))
            sel = 0 if T < t_change + 0.4 else 2
            k_ch = prog(T, t_change + 0.4, 0.3)
            ry = 260 + sel * 66
            rrect(cr, 985, ry - 30, 400, 60, 10, stroke=YELLOW, lw=6, a=1 if sel == 0 else k_ch)
            tag(cr, 430, 360, "WILL CHANGE ORDER", 0.76, prog(T, s("c4_04") + 0.6, 0.5))
            thought_bubble(cr, 560, 640, 180, 120, J["head"][0] - 20, J["head"][1] - 20, scale=0.8, t=T)
            text(cr, "☕" if sel == 0 else "🥤", 560, 640, 54, face="DejaVu Sans") if False else \
                text(cr, "COFFEE?" if sel == 0 else "SMOOTHIE!", 560, 640, 30, face=FONT_HAND, bold=True,
                     c=INK if sel == 0 else GREEN)
        hud(cr, T, 0.9, "SUBJECT 112")

    b.fx(st4, "whoosh", -8)
    b.fx(s("c4_04") + 0.6, "predict", -10)
    b.fx(t_change + 0.4, "ding", -10)

    # ------------------------------------------------------------ 5. one tiny choice ripples outward
    st5 = s("c4_05") - 0.2
    t_tie, t_rip, t_big = w("c4_05", "tie"), w("c4_05", "ripples"), w("c4_05", "bigger")
    chain = [(560, "bump"), (760, "bump"), (960, "bike"), (1180, "coffee"), (1400, "bump"), (1620, "phone")]

    @b.shot(st5, "fade", 0.35)
    def ripple(cr, t, d, T):
        k_big = ease(prog(T, t_big - 0.3, 1.4))
        city(cr, T, 400)
        z = lerp(1.0, 0.55, k_big)
        with camera(cr, z, lerp(CX, CX + 100, k_big), lerp(CY, CY - 80, k_big)):
            kneel = ease(prog(T, t_tie - 0.3, 0.5))
            p = sm.pose("stand", x=340, face=1)
            if kneel > 0:
                p = sm.mix(p, sm.apply(sm.pose("stand", x=340, face=1), lean=45, head=30, a1f=95, a2f=10, a1b=80, a2b=10,
                                       l1f=80, l2f=-100, l1b=-10, l2b=-80), kneel)
            p = sm.on_ground(p, 920)
            sm.draw(cr, p, acc=("cap",))
            k_r = prog(T, t_rip, 3.5)
            if k_r > 0:
                for j in range(4):
                    rr = (k_r * 1600 - j * 300)
                    if rr > 0:
                        ellipse(cr, 340, 920, rr, rr * 0.25, stroke=HUD, w=6, a=clamp(1 - rr / 1600) * 0.9)
            for i, (x, kind) in enumerate(chain):
                hit = t_rip + i * 0.35
                k = prog(T, hit, 0.3)
                if kind == "bike":
                    bx = x + (0 if T < hit else 30 * math.sin((T - hit) * 18) * max(0, 1 - (T - hit)))
                    for wx in (-50, 50):
                        circle(cr, bx + wx, 890, 30, stroke=INK, w=5)
                    polyline(cr, [(bx - 50, 890), (bx - 10, 840), (bx + 40, 840), (bx + 50, 890)], 5, INK)
                    pb = sm.pose("sit", x=bx, face=-1, a1f=70, a2f=0, a1b=60, a2b=0, l1f=60, l2f=-60, l1b=20, l2b=-30,
                                 s=0.85, eye=1 + 0.3 * k)
                    pb = sm.on_ground(pb, 860)
                    pb["y"] = 840 - 0
                    sm.draw(cr, pb, acc=("headset",))
                else:
                    jump = math.sin(k * math.pi) * 40
                    pp = sm.pose("surprised" if k > 0 else "stand", x=x, face=-1, s=0.9)
                    pp = sm.on_ground(pp, 920)
                    pp["y"] -= jump
                    sm.draw(cr, pp, acc=[("glasses",), ("ponytail",), ("bun",), ("tie",), ("cap",), ()][i])
                    if kind == "coffee" and k > 0:
                        for j in range(6):
                            circle(cr, x - 60 - j * 12, 760 + j * 25 * k, 9, fill=(0.45, 0.28, 0.15), a=1 - k * 0.3)
                if k > 0:
                    text(cr, "!", x, 520, 70, face=FONT_TITLE, c=RED, a=clamp(1.5 - (T - hit)))
            if k_big > 0:
                for j in range(5):
                    yy = 980 + j * 30
                    rect(cr, -400 + j * 160, yy, 2600 - j * 320, 18, fill=RED, a=0.4 * k_big)
                text(cr, "TRAFFIC JAM OF FOOTSTEPS", CX, 1180, 70, face=FONT_TITLE, c=RED, a=k_big)
        hud(cr, T, 0.9, "CAUSE → EFFECT")

    b.fx(t_tie - 0.3, "swoosh", -12)
    for i in range(len(chain)):
        b.fx(t_rip + i * 0.35, "boing" if i % 2 else "bump", -10)
    b.fx(t_big - 0.3, "whoosh", -8)

    # ------------------------------------------------------------ 6. reading the future
    st6 = s("c4_06") - 0.2

    @b.shot(st6, "fade", 0.35)
    def future(cr, t, d, T):
        dark(cr, T, star_a=0.5, c1=(0.05, 0.12, 0.2), c2=(0.02, 0.04, 0.08))
        with ken(cr, t, d, 1.0, 1.08, CX, 520):
            radial_lines(cr, CX, 430, T, n=30, c=HUD, a=0.08, w=16)
            for i in range(10):
                a = T * 0.4 + i * TAU / 10
                x, y = CX + math.cos(a) * 560, 470 + math.sin(a) * 300
                pct = 90 + (i * 7) % 10
                label_box(cr, f"{pct}%", x, y, 30, c=HUD, bg=(0.05, 0.12, 0.18), face=FONT_BOLD, bold=False,
                          scale=eout(prog(t, i * 0.08, 0.4)))
            p = sm.pose("confident", s=1.5, smile=1.0, brow=0.6)
            p = head_at(sm.idle(p, T, 3), CX, 360)
            J = sm.hero(cr, p, ink=WHITE, fill=(0.05, 0.12, 0.2))
            for ex in (-14, 14):
                glow(cr, J["head"][0] + 16 + ex, J["head"][1] - 6, 70, HUD, 0.9)
            text(cr, "FUTURE: PREDICTED", CX, 985, 64, face=FONT_TITLE, c=HUD, a=eout(prog(t, 0.5, 0.4)),
                 outline=(0.02, 0.04, 0.08), ow=10)

    b.fx(st6, "shimmer", -8)

    # ------------------------------------------------------------ 7. ...and then he dances right
    st7 = s("c4_07") - 0.2
    t_dance, t_right = w("c4_07", "dance"), w("c4_07", "right")

    @b.shot(st7, "cut")
    def dance(cr, t, d, T):
        city(cr, T, 600)
        k_err = prog(T, t_right, 0.3)
        with ken(cr, t, d, 1.0, 1.04):
            gx = 960
            dt = T - t_dance
            if T < t_dance:
                p = sm.walk(sm.pose(x=gx - 200 + t * 80, face=1), T, 0.9)
                gx = gx - 200 + t * 80
            elif T < t_right:
                gx = gx - 200 + (t_dance - st7) * 80
                ph = dt * 9
                p = sm.pose("cheer", x=gx, face=1 if math.sin(ph) > 0 else -1, smile=1, mo=0.5)
                p = sm.apply(p, a1f=150 + 25 * math.sin(ph), a1b=-150 + 25 * math.sin(ph + 1),
                             l1f=20 * math.sin(ph), l1b=-20 * math.sin(ph), lean=8 * math.sin(ph))
            else:
                gx = gx - 200 + (t_dance - st7) * 80 + (T - t_right) * 260
                p = sm.walk(sm.pose(x=gx, face=1, smile=1), T, 1.1)
            p = sm.on_ground(p, 920)
            if T >= t_dance and T < t_right:
                p["y"] -= abs(math.sin((T - t_dance) * 9)) * 30
            sm.draw(cr, p, acc=("tie", "glasses"))
            # the confident prediction
            ax = 960 - 200 + (t_dance - st7) * 80
            col = HUD if k_err <= 0 else RED
            if k_err < 1:
                arrow(cr, ax, 380, ax - 330, 380, 16, col, head=50, a=1 - k_err)
                text(cr, "WILL TURN LEFT: 97%", ax - 160, 300, 44, face=FONT_TITLE, c=col, a=1 - k_err)
            if k_err > 0:
                gl = math.sin(T * 60) * 8
                text(cr, "PREDICTION ERROR", CX + gl, 300, 90, face=FONT_TITLE, c=RED, a=k_err)
                cross(cr, ax - 160, 400, 2.0, p=k_err)
            hp = sm.pose("confident" if k_err <= 0 else "surprised", x=260, face=1, s=1.1)
            if k_err > 0:
                hp = sm.apply(hp, eye=1.4, mo=0.8)
            hp = sm.on_ground(sm.idle(hp, T, 4), 1060)
            sm.hero(cr, hp)
        hud(cr, T, 1.0 if k_err <= 0 else 0.6 + 0.4 * math.sin(T * 40), "SUBJECT 207")

    b.fx(t_dance, "dance", -6, dur=t_right - t_dance)
    b.fx(t_right, "scratch", -4)
    b.fx(t_right + 0.1, "glitch", -8)

    # ------------------------------------------------------------ 8. probabilities, not mind reading
    st8 = s("c4_08") - 0.2
    t_prob, t_eq, t_mind = w("c4_08", "probability"), w("c4_08", "equations"), w("c4_08", "read minds")

    @b.shot(st8, "fade", 0.35)
    def probability(cr, t, d, T):
        paper(cr)
        k_eq = prog(T, t_eq - 0.2, 0.4)
        k_mind = prog(T, t_mind - 0.6, 0.5)
        with ken(cr, t, d, 1.0, 1.04):
            # bars
            a_bars = 1 - ease(prog(T, t_eq - 0.4, 0.4))
            if a_bars > 0:
                with group(cr, a_bars):
                    text(cr, "A GUESS IS A PROBABILITY", CX, 150, 58, face=FONT_TITLE)
                    P.bar_chart(cr, CX, 800, [60, 30, 10], ["LEFT", "RIGHT", "DANCE"], w=900, h=480,
                                p=ease(prog(t, 0.3, 1.0)), colors=[BLUE, GREEN, RED], size=40)
                    for i, v in enumerate([60, 30, 10]):
                        text(cr, f"{v}%", CX - 300 + i * 300, 800 - 480 * v / 60 - 40, 40, face=FONT_BOLD,
                             a=prog(t, 1.0, 0.4))
                    kk = prog(T, t_prob, 0.6)
                    if kk > 0:
                        text(cr, "?", CX + 520, 500, 220, face=FONT_TITLE, c=YELLOW, rot=math.sin(T * 3) * 0.2, a=kk)
            if k_eq > 0 and k_mind < 1:
                with group(cr, (1 - k_mind)):
                    text(cr, "PERSON = x + y", CX, 380, 120, face=FONT_SERIF, italic=True, a=k_eq)
                    line(cr, CX - 450, 380, CX - 450 + 900 * ease(prog(T, t_eq + 0.3, 0.3)), 380, 14, RED)
                    for i, sym in enumerate(["moods", "secrets", "surprises", "memories", "jokes"]):
                        label_box(cr, sym, CX - 500 + i * 250, 640, 38, c=[RED, PURPLE, BLUE, GREEN, ORANGE][i],
                                  scale=back(prog(T, t_eq + 0.4 + i * 0.12, 0.4)))
            if k_mind > 0:
                with group(cr, k_mind):
                    p = sm.pose("think", x=620, face=1, brow=0.7, smile=0.0, eye=0.85)
                    p = sm.on_ground(sm.idle(p, T, 5), 920)
                    J = sm.hero(cr, p)
                    hx, hy = J["head"]
                    rrect(cr, hx - 52, hy - 70, 104, 40, 14, fill=MID, stroke=INK, lw=4)
                    for k in (-1, 1):
                        line(cr, hx + k * 30, hy - 70, hx + k * 50, hy - 140, 4, INK)
                        circle(cr, hx + k * 50, hy - 140, 10, fill=RED if math.sin(T * 10) > 0 else YELLOW)
                    q = sm.pose("listen", x=1300, face=-1, smile=0.6)
                    q = sm.on_ground(sm.idle(q, T, 6), 920)
                    J2 = sm.draw(cr, q, acc=("ponytail",))
                    for i in range(5):
                        f = ((T * 1.2 + i * 0.2) % 1)
                        x1 = lerp(hx + 60, J2["head"][0] - 60, f)
                        arc(cr, x1, hy - 100, 30 + 10 * i % 3, -0.8, 0.8, 4, HUD, 1 - f)
                    rrect(cr, 760, 220, 400, 90, 14, fill=(0.1, 0.1, 0.12))
                    text(cr, "NO SIGNAL", 960, 265, 54, face=FONT_TITLE, c=RED if math.sin(T * 6) > -0.3 else WHITE)

    b.fx(st8 + 0.3, "rise", -12)
    b.fx(t_eq + 0.3, "scratch_out", -10)
    b.fx(t_mind - 0.6, "static", -12, dur=2.5)

    # ------------------------------------------------------------ 9-11. the best friend
    st9 = s("c4_09") - 0.2
    t_q = s("c4_11")
    t_end = s("c4_12")

    def park(cr, T):
        vgrad(cr, (0.75, 0.88, 0.98), (0.92, 0.97, 0.92))
        P.cloud(cr, 400, 170, 1.0)
        P.cloud(cr, 1500, 130, 0.8)
        rect(cr, 0, 860, W, 220, fill=(0.62, 0.80, 0.50))
        ground(cr, 860)
        P.tree(cr, 220, 860, 1.4, T)
        P.tree(cr, 1750, 860, 1.2, T + 1)
        rect(cr, 640, 740, 640, 22, fill=(0.6, 0.42, 0.28), stroke=INK, lw=5)
        rect(cr, 640, 640, 640, 18, fill=(0.6, 0.42, 0.28), stroke=INK, lw=5)
        for x in (680, 1240):
            line(cr, x, 760, x, 860, 6, INK)

    @b.shot(st9, "fade", 0.4)
    def friends(cr, t, d, T):
        park(cr, T)
        with ken(cr, t, d, 1.0, 1.08, CX, 600):
            fx_ = lerp(1700, 1080, ease(prog(t, 0, 1.4)))
            arrive = prog(t, 0, 1.4)
            fp = sm.walk(sm.pose(x=fx_, face=-1, smile=0.6), T, 1.0) if arrive < 1 else sm.pose("sit", x=1080, face=-1)
            if arrive < 1:
                fp = sm.on_ground(fp, 860)
            else:
                fp = sm.on_ground(fp, 860)
                fp["y"] = 752
            fp = sm.idle(fp, T, 7) if arrive >= 1 else fp
            # lip-sync
            fp = sm.talk(fp, T, tl.env("c4_11", T)) if T > t_q - 0.1 else fp
            if T > t_q:
                fp = sm.apply(fp, smile=0.4, gy=-0.4, browy=0.3)
            sm.draw(cr, fp, acc=("cap",))
            hp = sm.pose("sit", x=800, face=1, smile=0.6)
            hp["y"] = 752
            hp = sm.idle(hp, T, 8)
            if s("c4_10") - 0.2 < T < t_q:
                hp = sm.apply(hp, a1f=128, a2f=22, smile=0.9, brow=0.5)
                hp = sm.talk(hp, T, tl.env("c4_10", T))
            if T >= t_q:
                k = ease(prog(T, t_q + 0.3, 0.3))
                hp = sm.apply(hp, eye=1 + 0.45 * k, mo=0.5 * k, smile=0.0, browy=1.0 * k, a1f=lerp(128, 30, k),
                              a2f=lerp(22, 110, k))
            J = sm.hero(cr, hp)
            # hero's prediction & speech
            k10 = prog(T, s("c4_10") - 0.1, 0.3)
            if k10 > 0 and T < t_q + 0.5:
                pop = 1 - ease(prog(T, t_q + 0.2, 0.25))
                thought_bubble(cr, 420, 250, 260, 180, J["head"][0] - 30, J["head"][1] - 60, scale=k10 * pop + 0.001, t=T)
                with xform(cr, 420, 250, max(0.01, k10 * pop)):
                    circle(cr, 0, 0, 50, fill=WHITE, stroke=INK, w=5)
                    polyline(cr, [(0, -18), (17, -6), (11, 15), (-11, 15), (-17, -6)], 3, INK, closed=True, fill=INK)
                    text(cr, "THE GAME", 0, 76, 26, face=FONT_HAND, bold=True)
                if pop < 1:
                    burst(cr, 420, 250, T - t_q - 0.2, n=12, dist=160, c=MID, dur=0.4)
            if s("c4_10") - 0.15 < T < t_q - 0.1:
                kb = back(prog(T, s("c4_10") - 0.15, 0.3))
                speech_bubble(cr, 900, 410, 560, 110, J["head"][0] + 20, J["head"][1] - 40, scale=kb)
                text(cr, "I know exactly what you're", 900, 390, 34, face=FONT_HAND, bold=True, a=clamp(kb))
                text(cr, "about to say.", 900, 430, 34, face=FONT_HAND, bold=True, a=clamp(kb))
            if T >= t_q - 0.1:
                kb = back(prog(T, t_q - 0.1, 0.3))
                speech_bubble(cr, 1260, 400, 500, 110, 1100, 560, scale=kb)
                text(cr, "Do penguins have knees?", 1260, 400, 38, face=FONT_HAND, bold=True, a=clamp(kb))

    b.fx(st9, "birds", -16, dur=t_end - st9)
    b.fx(st9 + 0.1, "footsteps", -14, dur=1.3)
    b.fx(s("c4_10") - 0.15, "pop", -12)
    b.fx(t_q + 0.2, "pop", -8)
    b.fx(t_q + 0.3, "boing", -6)

    # ------------------------------------------------------------ 12. for the record, they do
    st12 = t_end - 0.2
    t_do = w("c4_12", "they do")

    @b.shot(st12, "fade", 0.35)
    def knees(cr, t, d, T):
        paper(cr, (0.88, 0.94, 0.98))
        with ken(cr, t, d, 1.0, 1.05):
            text(cr, "FOR THE RECORD...", CX, 140, 60, face=FONT_TITLE, a=eout(prog(t, 0, 0.4)))
            P.penguin(cr, CX, 900, 2.0, T, xray=ease(prog(T, t_do - 0.3, 0.5)))
            hp = sm.pose("surprised", x=380, face=1, eye=1.3)
            hp = sm.on_ground(sm.idle(hp, T, 9), 900)
            sm.hero(cr, hp)
            fp = sm.pose("cheer", x=1540, face=-1)
            fp = sm.on_ground(sm.idle(fp, T, 10), 900)
            sm.draw(cr, fp, acc=("cap",))
            ground(cr, 900)
            if T > t_do + 0.4:
                text(cr, "(it's true)", CX, 1010, 40, face=FONT_HAND, bold=True, c=MID)

    b.fx(st12, "whoosh", -10)
    b.fx(t_do - 0.3, "xray", -8)
    b.fx(t_do + 0.2, "ding", -10)
    return b.result()
