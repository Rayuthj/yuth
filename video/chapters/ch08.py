"""Chapter 8 - The Biggest Problem: Other People (6:50-7:50)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

FLOOR = 900
MARKER = (0.15, 0.35, 0.75)
FRIENDS = [("SAM", ("cap",), 1180), ("MIA", ("ponytail",), 1420), ("LEO", ("glasses",), 1660)]


def living_room(cr, T):
    fill_bg(cr, (0.95, 0.93, 0.88))
    rect(cr, -300, FLOOR, W + 600, H - FLOOR + 300, fill=(0.80, 0.70, 0.58))
    ground(cr, FLOOR, x0=-300, x1=W + 300)
    # couch
    rrect(cr, 1040, 700, 760, 90, 20, fill=(0.45, 0.60, 0.80), stroke=INK, lw=5)
    rrect(cr, 1040, 600, 760, 110, 24, fill=(0.50, 0.66, 0.86), stroke=INK, lw=5)
    for x in (1080, 1760):
        line(cr, x, 790, x, FLOOR, 6, INK)
    P.lightbulb(cr, 1450, 120, 0.4, on=0.0)


def whiteboard(cr, x=520, y=430, w=760, h=460):
    rect(cr, x - w / 2, y - h / 2, w, h, fill=WHITE, stroke=(0.55, 0.55, 0.6), lw=10)
    line(cr, x - w / 3, y + h / 2 + 5, x - w / 3 - 30, FLOOR, 6, INK)
    line(cr, x + w / 3, y + h / 2 + 5, x + w / 3 + 30, FLOOR, 6, INK)


def friend_pose(i, T, mood=0.0, asleep=False, x=None):
    """mood: 0 interested, 1 confused."""
    name, acc, fx = FRIENDS[i]
    p = sm.pose("sit", x=x if x is not None else fx, face=-1, a1f=20, a2f=40, a1b=-10, a2b=30,
                gx=0.5, smile=lerp(0.5, -0.3, mood), brow=-0.6 * mood, browy=0.4 * (1 - mood))
    p = sm.idle(p, T, i + 3)
    if asleep:
        p = sm.apply(p, head=-25, lean=-14, blink=1.0, smile=0.1, mo=0.25, a1f=10, a2f=10)
    p["y"] = 700
    return p, acc


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. other people
    t_other = w("c8_01", "other people")

    @b.shot(0, "fade", 0.4)
    def warning(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.05):
            text(cr, "THE PROBLEM NOBODY WARNS", CX, 170, 60, face=FONT_TITLE, a=eout(prog(t, 0.2, 0.4)))
            text(cr, "GENIUSES ABOUT:", CX, 245, 60, face=FONT_TITLE, a=eout(prog(t, 0.35, 0.4)))
            k = prog(T, t_other, 0.4)
            p = sm.pose("front", x=CX, smile=0.5 - 0.6 * clamp(k * 2), eye=1 + 0.25 * k, browy=0.6 * k)
            p = sm.on_ground(sm.idle(p, T, 1), 950)
            sm.hero(cr, p)
            if k > 0:
                stamp(cr, "OTHER PEOPLE", CX, 380, T - t_other, 80, c=RED, rot=-0.05)
                for i, (name, acc, _) in enumerate(FRIENDS + [("", ("bun",), 0)]):
                    kk = back(prog(T, t_other + 0.25 + i * 0.12, 0.4))
                    if kk > 0:
                        x = [520, 1400, 300, 1640][i]
                        q = sm.pose("front", x=x, s=0.9 * kk + 0.01, smile=0.3, gx=(CX - x) / 900)
                        q = sm.on_ground(sm.idle(q, T, i), 950)
                        sm.draw(cr, q, acc=acc)
            ground(cr, 950, x0=150, x1=1770)

    b.fx(t_other, "stamp", -6)
    for i in range(4):
        b.fx(t_other + 0.25 + i * 0.12, "pop", -12)

    # ------------------------------------------------------------ 2-3. the explanation
    st2 = s("c8_02") - 0.25
    t_talk = s("c8_03")
    jargon = ["feedback loop", "nonlinear", "probability space", "recursive variables"]

    def diagram(cr, k, T, ox=520, oy=430, scale=1.0, a=1.0):
        """A growing, increasingly incomprehensible diagram."""
        r = rng(77)
        n = int(60 * k)
        with xform(cr, ox, oy, scale):
            nodes = [(r.uniform(-340, 340), r.uniform(-200, 200)) for _ in range(60)]
            for i in range(n):
                x1, y1 = nodes[i]
                x2, y2 = nodes[(i * 7 + 3) % 60]
                line(cr, x1, y1, x2, y2, 3, MARKER, a * 0.8)
                circle(cr, x1, y1, 9, stroke=MARKER, w=3, a=a)
            syms = ["∂f/∂x", "Σ", "λ²", "P(A|B)", "∮", "∇·F", "e^-λt", "lim", "⊗", "f(f(x))"]
            for i in range(int(len(syms) * k)):
                x, y = nodes[i * 5]
                text(cr, syms[i], x + 30, y - 18, 30, c=RED if i % 3 == 0 else MARKER, face=FONT_SERIF, italic=True, a=a)

    @b.shot(st2, "fade", 0.4)
    def explain(cr, t, d, T):
        k_d = prog(T, t_talk, e("c8_03") - t_talk + 0.4)
        with ken(cr, t, d, 1.0, 1.04, 960, 560):
            living_room(cr, T)
            whiteboard(cr)
            diagram(cr, k_d, T)
            for i in range(3):
                mood = clamp(k_d * 1.6 - 0.3 - i * 0.15)
                p, acc = friend_pose(i, T, mood)
                J = sm.draw(cr, p, acc=acc)
                if mood > 0.5:
                    P.question_mark(cr, J["head"][0] + 10 * math.sin(T * 3 + i), J["head"][1] - 90, 56, c=RED,
                                    a=clamp(mood * 2 - 1))
            hp = sm.pose("point", x=980, face=-1, a1f=95, smile=0.9, brow=0.4)
            if T < t_talk:
                hp = sm.pose("present", x=980, face=1, smile=0.9)
            hp = sm.talk(sm.idle(hp, T, 2), T, tl.env("c8_03", T)) if T >= t_talk else sm.idle(hp, T, 2)
            hp = sm.on_ground(hp, FLOOR)
            J = sm.hero(cr, hp)
            if T >= t_talk - 0.1:
                kb = back(prog(T, t_talk - 0.1, 0.3))
                speech_bubble(cr, 760, 150, 900, 120, J["head"][0] - 10, J["head"][1] - 50, scale=kb)
                shown = [wd for i, wd in enumerate(jargon) if T > w("c8_03", wd.split()[0]) - 0.1]
                line_txt = "...".join(shown) + "..." if shown else "So, if we map..."
                text(cr, line_txt, 760, 150, 34 if len(line_txt) < 50 else 28, face=FONT_HAND, bold=True,
                     a=clamp(kb))

    b.fx(st2 + 0.2, "footsteps", -14, dur=1.0)
    b.fx(t_talk, "marker", -10, dur=e("c8_03") - t_talk)

    # ------------------------------------------------------------ 4. ten minutes later
    st4 = s("c8_04") - 0.25
    t_asleep = w("c8_04", "asleep")

    @b.shot(st4, "cut")
    def later(cr, t, d, T):
        if t < 1.1:
            fill_bg(cr, (0.12, 0.25, 0.55))
            text(cr, "10 MINUTES LATER...", CX, CY, 96, face=FONT_HAND, bold=True, c=YELLOW,
                 scale=1 + 0.05 * math.sin(t * 6))
            P.clock(cr, CX, CY + 200, 60, t * 200, hours=3, minutes=10, speed=60, face=WHITE)
            return
        k = ease(prog(t, 1.1, 1.0))
        with ken(cr, t, d, 1.0, 0.92, 960, 560):
            living_room(cr, T)
            diagram(cr, 1.0, T, 960, 450, lerp(1.0, 2.6, k))
            r = rng(5)
            for i in range(26):
                x1, y1 = r.uniform(0, W), r.uniform(0, FLOOR)
                x2, y2 = r.uniform(0, W), r.uniform(0, FLOOR)
                partial_line(cr, x1, y1, x2, y2, k, 4, MARKER, 0.6)
                text(cr, r.choice(["Σ", "∂", "λ", "∞", "⊗", "→"]), x1, y1, 40, c=RED, a=0.7 * k, face=FONT_SERIF)
            for i in range(3):
                asleep = (i == 2) and T > t_asleep - 0.3
                p, acc = friend_pose(i, T, 1.0, asleep=asleep)
                J = sm.draw(cr, p, acc=acc)
                if asleep:
                    for j in range(3):
                        f = (T * 0.7 + j / 3) % 1
                        text(cr, "Z", J["head"][0] + 30 + f * 60, J["head"][1] - 40 - f * 120, 30 + 30 * f,
                             face=FONT_HAND, bold=True, c=INK, a=1 - f)
                else:
                    P.question_mark(cr, J["head"][0], J["head"][1] - 90, 56, c=RED)
            hp = sm.pose("point_up", x=760, face=1, smile=0.9, brow=0.4, s=0.95)
            hp = sm.on_ground(sm.talk(sm.idle(hp, T, 3), T, None, 0.6), FLOOR)
            sm.hero(cr, hp)

    b.fx(st4, "fastforward", -8, dur=1.0)
    b.fx(st4 + 1.1, "swoosh", -10)
    b.fx(t_asleep - 0.3, "snore", -8, dur=2.5)

    # ------------------------------------------------------------ 5. in normal words?
    st5 = s("c8_05") - 0.25

    @b.shot(st5, "cut")
    def normal_words(cr, t, d, T):
        with ken(cr, t, d, 1.15, 1.25, 1350, 520):
            living_room(cr, T)
            diagram(cr, 1.0, T, 960, 450, 2.6, a=0.5)
            for i in range(3):
                p, acc = friend_pose(i, T, 0.6, asleep=(i == 2))
                if i == 1:
                    p = sm.apply(p, a1f=150, a2f=20, smile=0.0, browy=0.5, brow=-0.3)
                    p = sm.talk(p, T, tl.env("c8_05", T))
                J = sm.draw(cr, p, acc=acc)
                if i == 1:
                    kb = back(prog(T, s("c8_05") - 0.1, 0.3))
                    speech_bubble(cr, J["head"][0] - 200, J["head"][1] - 200, 470, 110, J["head"][0] - 30,
                                  J["head"][1] - 50, scale=kb)
                    text(cr, "Can you say that...", J["head"][0] - 200, J["head"][1] - 218, 36, face=FONT_HAND,
                         bold=True, a=clamp(kb))
                    text(cr, "in normal words?", J["head"][0] - 200, J["head"][1] - 178, 36, face=FONT_HAND,
                         bold=True, a=clamp(kb))

    b.fx(st5, "pop", -10)

    # ------------------------------------------------------------ 6-7. the snowball
    st6 = s("c8_06") - 0.25
    t_draw = w("c8_06", "one simple")
    t_roll = w("c8_06", "rolling")
    t_small = s("c8_07")

    def snowball_drawing(cr, k_hill, k_roll, ox=520, oy=430):
        hill = [(ox - 330, oy - 160), (ox - 100, oy - 60), (ox + 120, oy + 80), (ox + 330, oy + 170)]
        partial_poly(cr, bezier_pts(hill, 30), k_hill, 7, MARKER)
        if k_roll > 0:
            pts = bezier_pts(hill, 30)
            idx = int(clamp(k_roll) * 29)
            x, y = pts[idx]
            r_ = 14 + 70 * k_roll ** 1.4
            circle(cr, x, y - r_, r_, fill=WHITE, stroke=MARKER, w=6)
            arc(cr, x, y - r_, r_ * 0.6, k_roll * 20, k_roll * 20 + 2, 4, MARKER)
            for j in range(3):
                circle(cr, x - r_ - 20 - j * 30, y - 10 - j * 6, 5, fill=MARKER, a=0.5)

    @b.shot(st6, "fade", 0.35)
    def snowball(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.05, 760, 520):
            living_room(cr, T)
            whiteboard(cr)
            k_hill = ease(prog(T, t_draw, 0.8))
            k_roll = ease(prog(T, t_roll - 0.2, 2.2))
            snowball_drawing(cr, k_hill, k_roll)
            for i in range(3):
                p, acc = friend_pose(i, T, 0.3 - 0.3 * k_roll)
                sm.draw(cr, p, acc=acc)
            hp = sm.pose("write", x=980, face=-1, smile=0.6, a2f=-10 + 14 * math.sin(T * 8) * (k_hill < 1))
            if T > t_small - 0.2:
                hp = sm.pose("present", x=980, face=1, smile=0.8)
                hp = sm.talk(hp, T, tl.env("c8_07", T))
            hp = sm.on_ground(sm.idle(hp, T, 4), FLOOR)
            J = sm.hero(cr, hp)
            if T > t_small - 0.1:
                kb = back(prog(T, t_small - 0.1, 0.3))
                speech_bubble(cr, 1250, 250, 640, 100, J["head"][0] + 20, J["head"][1] - 50, scale=kb)
                text(cr, "Small changes can grow into huge ones.", 1250, 250, 34, face=FONT_HAND, bold=True,
                     a=clamp(kb))

    b.fx(st6 + 0.1, "erase", -8)
    b.fx(t_draw, "marker", -10, dur=0.8)
    b.fx(t_roll - 0.2, "roll", -8, dur=2.2)

    # ------------------------------------------------------------ 8. why didn't you just say that?
    st8 = s("c8_08") - 0.2

    @b.shot(st8, "cut")
    def aha(cr, t, d, T):
        with ken(cr, t, d, 1.08, 1.12, 1350, 560):
            living_room(cr, T)
            for i in range(3):
                kk = prog(T, st8 + 0.1 + i * 0.12, 0.3)
                p, acc = friend_pose(i, T, 0.0)
                p = sm.apply(p, smile=1.0, eye=1.15, mo=0.4 if i != 0 else 0)
                if i == 0:
                    p = sm.apply(p, a1f=110, a2f=20, a1b=-100, a2b=-20)
                    p = sm.talk(p, T, tl.env("c8_08", T))
                J = sm.draw(cr, p, acc=acc)
                if kk > 0:
                    P.lightbulb(cr, J["head"][0], J["head"][1] - 130, 0.45 * back(kk) + 0.01, on=1.0, t=T)
            J0 = sm.joints(friend_pose(0, T)[0])
            kb = back(prog(T, s("c8_08") - 0.1, 0.3))
            speech_bubble(cr, J0["head"][0] - 330, J0["head"][1] - 160, 560, 100, J0["head"][0] - 40, J0["head"][1] - 40,
                          scale=kb)
            text(cr, "Oh! Why didn't you just say that?", J0["head"][0] - 330, J0["head"][1] - 160, 34, face=FONT_HAND,
                 bold=True, a=clamp(kb))

    for i in range(3):
        b.fx(st8 + 0.1 + i * 0.12, "ding", -10 - i * 2)

    # ------------------------------------------------------------ 9. two different skills
    st9 = s("c8_09") - 0.25
    t_expl = w("c8_09", "explaining")

    @b.shot(st9, "fade", 0.35)
    def skills(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.04):
            k1 = back(prog(t, 0.2, 0.4))
            k2 = back(prog(T, t_expl, 0.4))
            with xform(cr, 560, 430, max(0.01, k1)):
                P.brain(cr, 0, 0, 1.3)
                P.gear(cr, 0, -10, 30, 8, T, fill=YELLOW)
            text(cr, "UNDERSTANDING", 560, 680, 52, face=FONT_TITLE, a=clamp(k1))
            if k2 > 0:
                with xform(cr, 1360, 430, max(0.01, k2)):
                    polyline(cr, [(-110, -40), (-30, -40), (90, -120), (90, 120), (-30, 40), (-110, 40)], 6, INK,
                             closed=True, fill=YELLOW)
                    for j in range(3):
                        arc(cr, 120, 0, 40 + j * 30, -0.6, 0.6, 6, INK, 0.5 + 0.5 * math.sin(T * 6 - j))
                text(cr, "EXPLAINING", 1360, 680, 52, face=FONT_TITLE, a=clamp(k2))
                text(cr, "≠", 960, 440, 160, face="DejaVu Sans", c=RED, a=clamp(k2))
            for i, (x, v, col) in enumerate(((560, 1.0, BLUE), (1360, lerp(0.25, 0.85, ease(prog(T, t_expl + 0.8, 2.0))),
                                                                    ORANGE))):
                if (k1 if i == 0 else k2) > 0:
                    rrect(cr, x - 220, 760, 440, 40, 20, fill=LIGHT)
                    rrect(cr, x - 220, 760, 440 * v * clamp((k1 if i == 0 else k2)), 40, 20, fill=col)

    b.fx(st9 + 0.2, "pop", -10)
    b.fx(t_expl, "pop", -8)

    # ------------------------------------------------------------ 10. listen, ask, collaborate
    st10 = s("c8_10") - 0.25
    t_listen, t_ask, t_work = w("c8_10", "listen"), w("c8_10", "ask"), w("c8_10", "work with")
    roles = [("ARTIST", "artist", ("beret",), 520), ("ORGANIZER", "organizer", ("glasses", "tie"), 1400),
             ("GETS PEOPLE", "just gets", ("ponytail",), 1700)]

    @b.shot(st10, "fade", 0.35)
    def team(cr, t, d, T):
        paper(cr, (0.97, 0.95, 0.90))
        ground(cr, 920)
        with ken(cr, t, d, 1.0, 1.04):
            kl = back(prog(T, t_listen, 0.4))
            ka = back(prog(T, t_ask, 0.4))
            k_work = ease(prog(T, t_work, 0.8))
            hx = lerp(CX, 960, k_work)
            p = sm.pose("listen", x=hx, face=1, smile=0.7)
            if T > t_ask:
                p = sm.pose("point_up", x=hx, face=1, smile=0.6)
            p = sm.on_ground(sm.idle(p, T, 5), 920)
            J = sm.hero(cr, p)
            if kl > 0 and k_work < 1:
                with group(cr, 1 - k_work):
                    with xform(cr, 560, 380, max(0.01, kl)):
                        ellipse(cr, 0, 0, 70, 105, fill=(1.0, 0.85, 0.75), stroke=INK, w=6)
                        arc(cr, 5, -10, 40, -2.2, 1.2, 6, INK)
                        arc(cr, 10, 0, 18, -2.0, 1.4, 5, INK)
                    text(cr, "LISTEN", 560, 540, 50, face=FONT_TITLE, a=clamp(kl))
                    if ka > 0:
                        P.question_mark(cr, 1360, 380, 200 * ka + 1, c=BLUE)
                        text(cr, "ASK", 1360, 540, 50, face=FONT_TITLE, a=clamp(ka))
            # big shared canvas
            if k_work > 0:
                with group(cr, k_work):
                    rect(cr, 640, 200, 640, 360, fill=WHITE, stroke=INK, lw=6)
                    kp = prog(T, t_work + 0.5, 6.0)
                    P.sun(cr, 760, 300, 40, T, rays=False, a=clamp(kp * 4))
                    rect(cr, 900, 420, 120, 140 * clamp(kp * 3 - 0.5), fill=BLUE, a=0.8)
                    partial_poly(cr, [(660, 520), (800, 420), (960, 500), (1120, 380), (1260, 480)], clamp(kp * 2), 6, GREEN)
                    P.heart(cr, 1180, 280, 0.5 * clamp(kp * 3 - 1.5), a=1.0)
            for i, (lab, word, acc, x) in enumerate(roles):
                tj = w("c8_10", word)
                k = ease(prog(T, tj - 0.5, 0.7))
                if k <= 0:
                    continue
                xx = lerp(x + (1 if x > CX else -1) * 700, x, k)
                q = sm.walk(sm.pose(x=xx, face=1 if x < CX else -1), T, 1.0) if k < 1 else \
                    sm.pose(["present", "hips", "wave"][i], x=x, face=1 if x < CX else -1, smile=0.8)
                q = sm.on_ground(sm.idle(q, T, 6 + i), 920)
                Jq = sm.draw(cr, q, acc=acc)
                label_box(cr, lab, xx, 470, 32, c=INK, scale=back(prog(T, tj, 0.3)))
                if i == 0 and k >= 1:
                    hx_, hy_ = Jq["hand_f"]
                    ellipse(cr, hx_ + 10, hy_, 36, 26, fill=(0.95, 0.85, 0.65), stroke=INK, w=3)
                    for j, c in enumerate((RED, BLUE, YELLOW)):
                        circle(cr, hx_ - 6 + j * 14, hy_ - 6, 6, fill=c)
                if i == 1 and k >= 1:
                    hx_, hy_ = Jq["hand_f"]
                    rrect(cr, hx_ - 25, hy_ - 60, 60, 80, 6, fill=(0.75, 0.6, 0.45), stroke=INK, lw=3)
                if i == 2 and k >= 1:
                    P.heart(cr, Jq["head"][0], Jq["head"][1] - 90, 0.35, beat=max(0, math.sin(T * 6)))

    b.fx(t_listen, "pop", -10)
    b.fx(t_ask, "pop", -10)
    for lab, word, acc, x in roles:
        b.fx(w("c8_10", word) - 0.5, "footsteps", -14, dur=0.7)
        b.fx(w("c8_10", word), "pop", -10)

    # ------------------------------------------------------------ 11. part of being smart
    st11 = s("c8_11") - 0.3
    traits = [("CREATIVITY", "creativity", PURPLE), ("EMPATHY", "empathy", RED), ("PATIENCE", "patience", GREEN),
              ("TEAMWORK", "teamwork", BLUE)]
    t_part = w("c8_11", "part of")

    @b.shot(st11, "fade", 0.4)
    def smart(cr, t, d, T):
        paper(cr)
        hx, hy = CX, 520
        kp = ease(prog(T, t_part, 0.8))
        with ken(cr, t, d, 1.0, 1.05, CX, 540):
            if kp > 0:
                glow(cr, hx, hy, 420, YELLOW, 0.45 * kp)
                radial_lines(cr, hx, hy, T, n=24, r0=200, r1=900, c=YELLOW, a=0.25 * kp, w=16)
            for i, (lab, word, col) in enumerate(traits):
                k = back(prog(T, w("c8_11", word), 0.4))
                if k <= 0:
                    continue
                a = -math.pi * 0.85 + i * math.pi * 0.57 + T * 0.1
                rr = lerp(420, 300, kp)
                x, y = hx + math.cos(a) * rr * 1.25, hy + math.sin(a) * rr * 0.75
                label_box(cr, lab, x, y, 44, c=WHITE, bg=col, face=FONT_TITLE, bold=False, scale=k, lw=0)
                if kp > 0:
                    line(cr, x, y, hx, hy, 5, col, 0.6 * kp)
            p = sm.pose("cheer" if kp > 0.5 else "front", s=1.15, smile=0.9)
            p = head_at(sm.idle(p, T, 7), hx, hy)
            sm.hero(cr, p)
            if kp > 0:
                text(cr, "= PART OF BEING SMART", CX, 960, 64, face=FONT_TITLE, a=kp, outline=WHITE, ow=8)

    for lab, word, col in traits:
        b.fx(w("c8_11", word), "pop", -8)
    b.fx(t_part, "chime", -6)
    return b.result()
