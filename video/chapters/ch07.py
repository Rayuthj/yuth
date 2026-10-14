"""Chapter 7 - Could You Invent the Future? (5:50-6:50)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

DARK_TAG = True
HOLO = (0.35, 0.90, 1.0)
NAVY = (0.04, 0.08, 0.16)
NAVY2 = (0.02, 0.03, 0.07)


def holo_bg(cr, T):
    vgrad(cr, NAVY, NAVY2)
    src(cr, HOLO, 0.06)
    cr.set_line_width(1.5)
    for x in range(0, W, 60):
        cr.move_to(x, 0)
        cr.line_to(x, H)
    for y in range(0, H, 60):
        cr.move_to(0, y)
        cr.line_to(W, y)
    cr.stroke()
    sy = (T * 220) % H
    line(cr, 0, sy, W, sy, 2, HOLO, 0.15)


def tag(cr, t, kind="POSSIBILITY"):
    col = GREEN if kind == "POSSIBILITY" else ORANGE
    k = back(prog(t, 0.3, 0.4))
    if k > 0:
        with xform(cr, W - 270, 110, k):
            rrect(cr, -200, -36, 400, 72, 12, fill=(0.05, 0.08, 0.12), stroke=col, lw=5)
            text(cr, kind, 0, 0, 40, face=FONT_TITLE, c=col)


def headline(cr, t, s_):
    text(cr, s_, 90, 110, 52, face=FONT_TITLE, c=WHITE, align="left", a=eout(prog(t, 0.1, 0.4)))


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. imagining the future
    t_scifi, t_little = w("c7_01", "not science"), w("c7_01", "maybe")

    @b.shot(0, "fade", 0.5)
    def dream(cr, t, d, T):
        vgrad(cr, (0.18, 0.20, 0.42), (0.85, 0.62, 0.55))
        stars(cr, T, n=80, alpha=0.6, area=(0, 0, W, 500))
        with ken(cr, t, d, 1.0, 1.05, CX, 560):
            k = ease(prog(t, 0.6, 2.5))
            with group(cr, k * 0.85):
                for i, (x, h) in enumerate(((600, 380), (720, 520), (850, 300), (1000, 600), (1140, 420), (1280, 340))):
                    rrect(cr, x - 50, 760 - h, 100, h, 30, stroke=HOLO, lw=4)
                    for j in range(int(h / 60)):
                        line(cr, x - 30, 760 - h + 40 + j * 60, x + 30, 760 - h + 40 + j * 60, 3, HOLO, 0.6)
                ellipse(cr, 940, 260, 380, 60, stroke=HOLO, w=4)
                for i in range(3):
                    f = (T * 0.15 + i / 3) % 1
                    x = lerp(500, 1400, f)
                    ellipse(cr, x, 240 - 40 * math.sin(f * math.pi), 34, 12, fill=HOLO, a=0.8)
            rect(cr, 0, 860, W, 220, fill=(0.15, 0.13, 0.20))
            P.hill(cr, 380, 870, 760, 120, c=(0.15, 0.13, 0.20))
            p = sm.pose("sit", x=380, face=1, a1f=30, a2f=40, a1b=-30, a2b=-30, gy=-0.8, gx=0.6, smile=0.6)
            p = sm.on_ground(sm.idle(p, T, 1), 780)
            p["y"] = 640
            if T > t_little:
                p = sm.apply(p, a1f=40, a2f=78, a1b=-38, a2b=-78, browy=0.6, smile=0.4)
            sm.hero(cr, p, ink=(0.08, 0.07, 0.12), fill=(0.95, 0.8, 0.75))
            ks = prog(T, t_scifi, 0.4)
            if ks > 0:
                rot = lerp(0, 0.18, ease(prog(T, t_little, 0.4)))
                label_box(cr, "NOT SCI-FI", 1500, 820, 46, c=WHITE, bg=(0.1, 0.1, 0.2), scale=back(ks))
                if T > t_little:
                    with xform(cr, 1500, 910, 1.0, rot):
                        text(cr, "(well... maybe a little)", 0, 0, 36, face=FONT_HAND, bold=True, c=YELLOW,
                             a=prog(T, t_little, 0.4))

    b.fx(0.6, "shimmer", -8)
    b.fx(t_little, "boing", -12)

    # ------------------------------------------------------------ 2. medical scanners
    st2 = s("c7_02") - 0.25
    t_early = w("c7_02", "years earlier")

    @b.shot(st2, "fade", 0.35)
    def scanner(cr, t, d, T):
        holo_bg(cr, T)
        headline(cr, t, "EARLIER DIAGNOSIS")
        tag(cr, t, "POSSIBILITY")
        with ken(cr, t, d, 1.0, 1.04):
            rrect(cr, 360, 640, 1200, 60, 20, fill=(0.1, 0.18, 0.28), stroke=HOLO, lw=4)
            with xform(cr, 960, 600, 1.0, -math.pi / 2):
                p = sm.pose("stand", x=0, s=1.2, blink=1.0, smile=0.4)
                p = sm.on_ground(p, 0)
                p["x"], p["y"] = 0, -10
                sm.draw(cr, p, acc=(), ink=HOLO, fill=NAVY)
            sx = lerp(400, 1520, (T * 0.45) % 1)
            line(cr, sx, 420, sx, 700, 6, HOLO)
            glow(cr, sx, 560, 160, HOLO, 0.25)
            kd = prog(T, s("c7_02") + 1.0, 0.4)
            if kd > 0:
                circle(cr, 1040, 600, 14 + 6 * math.sin(T * 8), fill=RED, a=kd)
                circle(cr, 1040, 600, 50, stroke=RED, w=4, a=kd)
                label_box(cr, "DETECTED EARLY", 1040, 480, 32, c=RED, bg=(0.1, 0.05, 0.07), scale=back(kd))
            ke = prog(T, t_early, 0.6)
            if ke > 0:
                line(cr, 460, 900, 1460, 900, 5, WHITE)
                for i, lab in enumerate(("TODAY", "", "")):
                    pass
                text(cr, "TODAY", 1400, 950, 32, face=FONT_BOLD, c=WHITE)
                circle(cr, 1400, 900, 12, fill=WHITE)
                arrow(cr, 1400, 860, lerp(1400, 600, ease(ke)), 860, 8, GREEN, head=28)
                text(cr, "YEARS EARLIER", 600, 950, 32, face=FONT_BOLD, c=GREEN, a=ke)

    b.fx(st2 + 0.2, "scan", -8)
    b.fx(s("c7_02") + 1.0, "blip", -8)

    # ------------------------------------------------------------ 3. new materials
    st3 = s("c7_03") - 0.25
    t_light, t_strong = w("c7_03", "lighter"), w("c7_03", "stronger")

    @b.shot(st3, "slide", 0.4)
    def materials(cr, t, d, T):
        holo_bg(cr, T)
        headline(cr, t, "NEW MATERIALS")
        tag(cr, t, "POSSIBILITY")
        with ken(cr, t, d, 1.0, 1.04):
            # rotating lattice
            with xform(cr, 420, 560, 1.0, T * 0.3):
                for i in range(-3, 4):
                    for j in range(-3, 4):
                        x, y = i * 70 + (j % 2) * 35, j * 60
                        if x * x + y * y < 230 * 230:
                            circle(cr, x, y, 12, fill=HOLO)
                            if i < 3:
                                line(cr, x, y, x + 70, y, 3, HOLO, 0.6)
                            line(cr, x, y, x + 35, y + 60, 3, HOLO, 0.6)
            kl = ease(prog(T, t_light, 0.8))

            def left_pan(c):
                rect(c, -40, 40, 80, 50, fill=HOLO, stroke=WHITE, lw=3)
                text(c, "NEW", 0, 65, 22, face=FONT_BOLD, c=NAVY)

            def right_pan(c):
                rect(c, -60, 30, 120, 60, fill=MID, stroke=WHITE, lw=3)
                text(c, "STEEL", 0, 60, 22, face=FONT_BOLD, c=WHITE)

            with group(cr, 1.0):
                P.scale_balance(cr, 1300, 900, 1.7, tilt=0.28 * kl, left=left_pan, right=right_pan)
            ks = prog(T, t_strong, 0.5)
            if ks > 0:
                label_box(cr, "LIGHTER", 960, 330, 40, c=GREEN, bg=NAVY, scale=back(kl))
                label_box(cr, "STRONGER", 1640, 250, 40, c=YELLOW, bg=NAVY, scale=back(ks))

    b.fx(st3, "whoosh", -8)
    b.fx(t_light, "clank", -10)
    b.fx(t_strong, "ding", -10)

    # ------------------------------------------------------------ 4. batteries
    st4 = s("c7_04") - 0.25

    @b.shot(st4, "slide", 0.4)
    def batteries(cr, t, d, T):
        holo_bg(cr, T)
        headline(cr, t, "BETTER BATTERIES")
        tag(cr, t, "SPECULATION")
        with ken(cr, t, d, 1.0, 1.06):
            P.battery(cr, 700, 560, 1.6, level=0.25, c=ORANGE)
            text(cr, "TODAY", 700, 820, 36, face=FONT_BOLD, c=WHITE)
            k = ease(prog(t, 0.3, 1.6))
            P.battery(cr, 1220, 560, 1.9, level=k, c=GREEN)
            if k > 0.2:
                glow(cr, 1220, 560, 300, GREEN, 0.25 * k)
            text(cr, "TOMORROW?", 1220, 860, 36, face=FONT_BOLD, c=GREEN)

    b.fx(st4 + 0.3, "charge", -8, dur=1.6)

    # ------------------------------------------------------------ 5. AI research assistants
    st5 = s("c7_05") - 0.25
    t_thou = w("c7_05", "thousands")

    @b.shot(st5, "slide", 0.4)
    def ai_lab(cr, t, d, T):
        holo_bg(cr, T)
        headline(cr, t, "AI LAB ASSISTANTS")
        tag(cr, t, "POSSIBILITY")
        with ken(cr, t, d, 1.0, 1.04):
            P.robot(cr, 360, 940, 1.0, T, c=(0.75, 0.85, 0.95))
            p = sm.pose("present", x=600, face=1, smile=0.7)
            p = sm.on_ground(sm.idle(p, T, 2), 940)
            sm.draw(cr, p, acc=("labcoat", "glasses"), ink=WHITE, fill=NAVY)
            k = prog(T, t_thou - 0.6, 2.4)
            n_done = int(400 * k)
            r = rng(4)
            for i in range(400):
                gx, gy = 820 + (i % 40) * 26, 260 + (i // 40) * 52
                if i < n_done:
                    ok = r.random() < 0.12
                    rect(cr, gx, gy, 20, 40, fill=GREEN if ok else (0.35, 0.15, 0.2))
                else:
                    r.random()
                    rect(cr, gx, gy, 20, 40, stroke=HOLO, lw=1.5, a=0.5)
            text(cr, f"IDEAS TESTED: {int(4800 * k):,}", 1340, 860, 48, face=FONT_TITLE, c=HOLO)

    b.fx(st5, "whoosh", -8)
    b.fx(t_thou - 0.6, "data", -12, dur=2.4)

    # ------------------------------------------------------------ 6. exploring the universe
    st6 = s("c7_06") - 0.25
    t_tel, t_probe = w("c7_06", "telescopes"), w("c7_06", "probes")

    @b.shot(st6, "fade", 0.4)
    def space(cr, t, d, T):
        vgrad(cr, (0.02, 0.02, 0.06), (0.06, 0.05, 0.14))
        stars(cr, T, n=320, drift=6)
        tag(cr, t, "SPECULATION")
        with ken(cr, t, d, 1.0, 1.08, CX, 520):
            P.galaxy(cr, 1350, 330, 320, T, seed=3, rot=0.3)
            circle(cr, 560, 300, 90, fill=(0.85, 0.55, 0.35), stroke=WHITE, w=3)
            ellipse(cr, 560, 300, 150, 26, stroke=(0.95, 0.85, 0.7), w=5, rot=-0.3)
            P.globe(cr, 300, 1240, 520, T * 0.2)
            kt = prog(T, t_tel - 0.3, 0.5)
            if kt > 0:
                with group(cr, kt):
                    P.telescope(cr, 520, 760, 1.0, rot=-0.7)
                    for i in range(3):
                        f = (T * 0.8 + i / 3) % 1
                        line(cr, lerp(620, 1200, f), lerp(600, 380, f), lerp(640, 1220, f), lerp(592, 372, f), 4, HOLO,
                             1 - f)
            kp = prog(T, t_probe - 0.3, 3.0)
            if kp > 0:
                for i in range(3):
                    f = clamp(kp * 1.3 - i * 0.15)
                    x = lerp(400, 1350 + i * 60, ease(f))
                    y = lerp(700, 330 - i * 50, ease(f))
                    P.probe(cr, x, y, 0.45, T, rot=-0.5)
            p = sm.pose("point_up", x=760, face=1, s=0.6, smile=0.9)
            p = sm.on_ground(sm.idle(p, T, 3), 770)
            sm.hero(cr, p, ink=WHITE, fill=NAVY)

    b.fx(st6, "space", -10, dur=5.0)
    b.fx(t_probe - 0.3, "whoosh", -10)

    # ------------------------------------------------------------ 7. nothing is guaranteed
    st7 = s("c7_07") - 0.25
    pillars = [("KNOWLEDGE", "knowledge", 300), ("TOOLS", "tools", 640), ("EXPERIMENTS", "experiments", 980)]
    t_phys = w("c7_07", "laws")
    t_bend = w("c7_07", "bend")

    @b.shot(st7, "fade", 0.35)
    def guarantee(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.03):
            text(cr, "INVENTIONS DEPEND ON...", 760, 140, 56, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.4)))
            ground(cr, 900)
            for lab, word, x in pillars:
                k = eout(prog(T, w("c7_07", word), 0.45))
                if k > 0:
                    h = 420 * k
                    rect(cr, x - 70, 900 - h, 140, h, fill=(0.88, 0.86, 0.80), stroke=INK, lw=5)
                    rect(cr, x - 95, 900 - h - 30, 190, 30, fill=(0.88, 0.86, 0.80), stroke=INK, lw=5)
                    text(cr, lab, x, 900 - h - 70, 34, face=FONT_BOLD, a=k)
            kp = prog(T, t_phys, 0.35)
            if kp > 0:
                y = lerp(-400, 470, bounce(kp))
                with xform(cr, 1480, y, 1.0):
                    rrect(cr, -230, -330, 460, 760, 80, fill=(0.7, 0.68, 0.65), stroke=INK, lw=8)
                    text(cr, "LAWS OF", 0, -200, 56, face=FONT_TITLE)
                    text(cr, "PHYSICS", 0, -130, 56, face=FONT_TITLE)
                    for i, eq in enumerate(("F = ma", "E = mc²", "ΔS ≥ 0", "c = const.")):
                        text(cr, eq, 0, -20 + i * 80, 50, face=FONT_SERIF, italic=True)
            kb = prog(T, t_bend - 0.3, 0.3)
            p = sm.pose("stand", x=1180, face=1)
            if kb > 0:
                p = sm.apply(p, lean=28, a1f=90, a2f=-10, a1b=80, a2b=0, l1f=30, l1b=-35, l2b=-5, brow=0.8, smile=-0.6,
                             eye=0.8)
                p["x"] += math.sin(T * 40) * 2
            p = sm.on_ground(sm.idle(p, T, 4), 900)
            J = sm.hero(cr, p)
            if kb > 0:
                for i in range(3):
                    f = (T * 1.5 + i / 3) % 1
                    circle(cr, J["head"][0] - 50 - f * 40, J["head"][1] - 20 + f * 60, 7, fill=CYAN, a=1 - f)
                text(cr, "DOESN'T BEND", 1480, 1000, 44, face=FONT_TITLE, c=RED, a=kb)

    for lab, word, x in pillars:
        b.fx(w("c7_07", word), "thud", -10)
    b.fx(t_phys + 0.2, "slam", -2)
    b.fx(t_bend - 0.3, "strain", -10, dur=2.0)

    # ------------------------------------------------------------ 8. a prototype
    st8 = s("c7_08") - 0.25

    def workshop(cr, T):
        fill_bg(cr, (0.90, 0.88, 0.84))
        rect(cr, 0, 900, W, 180, fill=(0.6, 0.6, 0.62))
        ground(cr, 900)
        rect(cr, 1250, 160, 560, 360, fill=(0.20, 0.35, 0.62), stroke=INK, lw=6)
        for i in range(8):
            line(cr, 1270 + i * 70, 180, 1270 + i * 70, 500, 1.5, WHITE, 0.25)
        P.drone(cr, 1530, 330, 1.1, T, version=1, spin=0.0)
        text(cr, "DRONE v1", 1530, 470, 40, face=FONT_HAND, bold=True, c=WHITE)

    @b.shot(st8, "fade", 0.35)
    def prototype(cr, t, d, T):
        with ken(cr, t, d, 1.0, 1.05, 860, 600):
            workshop(cr, T)
            rect(cr, 380, 720, 700, 26, fill=(0.55, 0.42, 0.3), stroke=INK, lw=5)
            for x in (420, 1040):
                line(cr, x, 746, x, 900, 6, INK)
            P.drone(cr, 730, 690, 1.0, T, version=1, spin=0.0)
            p = sm.pose("hold", x=1200, face=-1, smile=0.8, a1f=80, a2f=30)
            p = sm.apply(p, a2f=30 + 25 * math.sin(T * 8))
            p = sm.on_ground(sm.idle(p, T, 5), 900)
            J = sm.hero(cr, p)
            hx, hy = J["hand_f"]
            with xform(cr, hx, hy, 1.0, -0.8 + 0.3 * math.sin(T * 8)):
                line(cr, 0, 0, -60, 0, 9, MID)
                arc(cr, -70, 0, 14, 0.8, 5.5, 7, MID)

    b.fx(st8, "clank", -10)
    b.fx(st8 + 0.8, "clank", -12)
    b.fx(st8 + 1.6, "clank", -12)

    # ------------------------------------------------------------ 9. tests one and two
    st9 = s("c7_09") - 0.25
    t_two = w("c7_09", "test two")
    t_bush = w("c7_09", "bush")

    def field(cr, T):
        vgrad(cr, (0.62, 0.82, 0.98), (0.92, 0.96, 0.98))
        P.cloud(cr, 500, 200, 0.9)
        P.cloud(cr, 1400, 160, 0.7)
        rect(cr, 0, 900, W, 180, fill=(0.62, 0.80, 0.50))
        ground(cr, 900)

    @b.shot(st9, "slide", 0.4)
    def tests(cr, t, d, T):
        field(cr, T)
        P.bush(cr, 1500, 900, 1.4, shake=max(0, 1 - (T - t_bush - 0.4) * 2) if T > t_bush + 0.4 else 0, t=T)
        p = sm.pose("think" if T < t_two else "facepalm", x=300, face=1)
        p = sm.on_ground(sm.idle(p, T, 6), 900)
        sm.hero(cr, p)
        if T < t_two:
            u = T - st9
            k = prog(u, 0.4, 1.0)
            y = lerp(860, 520, ease(k))
            spin = u * 9 * k
            P.drone(cr, 900 + math.cos(spin) * 120 * k, y + math.sin(spin) * 40 * k, 0.9, T, rot=math.sin(spin) * 0.3,
                    version=1)
            label_box(cr, "TEST 1", 900, 200, 50, c=INK)
            if u > 2.0:
                cross(cr, 1080, 200, 1.4, p=prog(u, 2.0, 0.3))
                text(cr, "SPINS IN CIRCLES", 900, 290, 38, face=FONT_HAND, bold=True, c=RED)
        else:
            u = T - t_two
            k = prog(u, 0.3, 1.6)
            x = lerp(900, 1500, ease(k))
            y = lerp(860, 560, math.sin(k * math.pi * 0.9)) if k < 1 else 840
            if k < 1:
                P.drone(cr, x, y, 0.9, T, rot=k * math.pi * 1.0, version=2)
            label_box(cr, "TEST 2", 900, 200, 50, c=INK)
            if k >= 1:
                cross(cr, 1080, 200, 1.4, p=prog(u, 2.0, 0.3))
                text(cr, "FLIPS INTO A BUSH", 900, 290, 38, face=FONT_HAND, bold=True, c=RED)
                for i in range(6):
                    f = clamp((u - 1.9) * 1.3)
                    a = -math.pi / 2 + (i - 2.5) * 0.4
                    circle(cr, 1500 + math.cos(a) * 200 * f, 780 + math.sin(a) * 160 * f + 200 * f * f, 10,
                           fill=GREEN, a=1 - f)

    b.fx(st9 + 0.4, "drone", -10, dur=t_two - st9 - 0.6)
    b.fx(st9 + 2.2, "buzz", -10)
    b.fx(t_two + 0.3, "drone", -10, dur=1.6)
    b.fx(t_two + 1.9, "crash", -4)
    b.fx(t_two + 2.3, "buzz", -10)

    # ------------------------------------------------------------ 10. study, change, test again
    st10 = s("c7_10") - 0.25
    t_change = w("c7_10", "change")

    @b.shot(st10, "fade", 0.35)
    def redesign(cr, t, d, T):
        fill_bg(cr, (0.16, 0.30, 0.55))
        src(cr, WHITE, 0.08)
        cr.set_line_width(1.5)
        for x in range(0, W, 40):
            cr.move_to(x, 0)
            cr.line_to(x, H)
        for y in range(0, H, 40):
            cr.move_to(0, y)
            cr.line_to(W, y)
        cr.stroke()
        with ken(cr, t, d, 1.0, 1.05):
            v = 2 if T < t_change + 0.3 else 3
            with group(cr, 0.95):
                P.drone(cr, 760, 480, 2.0, T, version=v, spin=0.2)
            text(cr, f"DRONE v{v}", 760, 760, 64, face=FONT_HAND, bold=True, c=WHITE)
            k = prog(T, st10 + 0.4, 1.2)
            notes = ["props too small", "center of mass?", "needs legs"]
            for i, n in enumerate(notes):
                kk = clamp(k * 3 - i)
                if kk > 0:
                    text(cr, "• " + n, 1260, 360 + i * 70, 42, face=FONT_HAND, bold=True, c=YELLOW, align="left", a=kk)
            kc = prog(T, t_change, 0.4)
            if kc > 0:
                circle(cr, 760, 560, 260, stroke=YELLOW, w=6, a=kc * (1 - prog(T, t_change + 1.2, 0.4)))
            p = sm.pose("think", x=1550, face=-1, smile=0.4)
            p = sm.on_ground(sm.idle(p, T, 7), 1000)
            sm.hero(cr, p, ink=WHITE, fill=(0.16, 0.30, 0.55))
            P.magnifier(cr, 1100, 500 + 30 * math.sin(T * 2), 0.9)

    b.fx(st10 + 0.4, "scribble", -10, dur=1.5)
    b.fx(t_change + 0.3, "swoosh", -10)

    # ------------------------------------------------------------ 11. test three: it flies
    st11 = s("c7_11") - 0.25
    t_flies = w("c7_11", "flies")

    @b.shot(st11, "slide", 0.4)
    def flies(cr, t, d, T):
        field(cr, T)
        k = prog(T, t_flies - 0.6, 3.0)
        x = lerp(500, 1700, ease(k))
        y = lerp(860, 330, eout(clamp(k * 2))) + 12 * math.sin(T * 3)
        P.drone(cr, x, y, 0.95, T, rot=0.05 * math.sin(T * 2), version=3)
        p = sm.pose("cheer" if k > 0.2 else "point_up", x=330, face=1, smile=1, mo=0.5 if k > 0.2 else 0)
        p = sm.on_ground(sm.idle(p, T, 8), 900)
        if k > 0.2:
            p["y"] -= abs(math.sin(T * 7)) * 30
        sm.hero(cr, p)
        label_box(cr, "TEST 3", 900, 200, 50, c=INK)
        if k > 0.25:
            check(cr, 1090, 200, 1.6, p=prog(k, 0.25, 0.1))

    b.fx(t_flies - 0.6, "drone", -10, dur=3.0)
    b.fx(t_flies + 0.2, "success", -6)

    # ------------------------------------------------------------ 12. survive contact with reality
    st12 = s("c7_12") - 0.3
    t_real = w("c7_12", "reality")

    @b.shot(st12, "fade", 0.4)
    def contact(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.0, 1.04):
            # reality wall
            for row in range(9):
                for col in range(3):
                    off = 40 if row % 2 else 0
                    rect(cr, 1200 + col * 100 - off, 160 + row * 80, 100, 80, fill=(0.75, 0.35, 0.28), stroke=INK, lw=4)
            text(cr, "REALITY", 1310, 110, 56, face=FONT_TITLE)
            ground(cr, 880)
            # ideas fly into it; most break, one gets through
            for i in range(5):
                start = st12 + 0.5 + i * 0.55
                k = prog(T, start, 0.9)
                if k <= 0:
                    continue
                y = 300 + i * 110
                survivor = i == 3
                if survivor:
                    x = lerp(200, 1700, ease(prog(T, start, 1.8)))
                    if x > 1150:
                        cr.save()
                        cr.rectangle(1440, 0, W - 1440, H)
                        cr.clip()
                    P.lightbulb(cr, x, y, 0.55, on=1.0, t=T)
                    if x > 1150:
                        cr.restore()
                        if x < 1440:
                            P.lightbulb(cr, x, y, 0.55, on=1.0, t=T)
                else:
                    x = lerp(200, 1150, ein(k))
                    if k < 1:
                        P.lightbulb(cr, x, y, 0.55, on=0.6, t=T)
                    else:
                        burst(cr, 1150, y, T - start - 0.9, n=10, dist=110, size=7, c=(0.8, 0.85, 0.9), dur=0.5, seed=i)
            label_box(cr, "TESTED IDEA", 1700, 760, 36, c=GREEN, scale=back(prog(T, t_real, 0.4)))

    for i in range(5):
        if i != 3:
            b.fx(st12 + 0.5 + i * 0.55 + 0.9, "shatter", -12)
    b.fx(t_real, "success", -8)
    return b.result()
