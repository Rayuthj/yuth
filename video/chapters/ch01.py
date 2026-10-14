"""Chapter 1 - The Hook (0:00-0:40)."""
import math

from video.chapters.common import *  # noqa: F401,F403
from video.chapters.common import Builder, paper, dark, ground, ken, head_at, title_card, MATH_SYMBOLS
from video.engine.core import *  # noqa: F401,F403
from video.engine import stickman as sm
from video.engine import props as P

DARK_TAG = True
NIGHT_FILL = (0.06, 0.065, 0.09)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # ------------------------------------------------------------ 1. awakening in the dark
    @b.shot(0)
    def awaken(cr, t, d, T):
        fill_bg(cr, BLACK)
        hx, hy = CX, 450
        p_head = ease(prog(T, 0.9, 1.0))
        p_sym = prog(T, s("c1_01") + 0.4, 4.0)
        z = lerp(1.0, 1.10, ease(t / d))
        with camera(cr, z, CX, hy + 40):
            glow(cr, hx, hy, 700, BLUE, 0.20 * p_head)
            # pattern rings that draw themselves
            for k, (rr, n, sp) in enumerate(((230, 48, 0.12), (330, 72, -0.08), (440, 96, 0.05))):
                kk = clamp(p_sym * 3 - k)
                for i in range(int(n * kk)):
                    a = i / n * TAU + T * sp
                    circle(cr, hx + math.cos(a) * rr, hy + math.sin(a) * rr, 2.6, fill=CYAN, a=0.55)
            # golden spiral
            if p_sym > 0:
                pts = []
                for i in range(int(220 * clamp(p_sym * 1.2))):
                    th = i / 30
                    r = 6 * math.exp(0.3063 * th)
                    pts.append((hx + math.cos(th + T * 0.3) * r, hy + math.sin(th + T * 0.3) * r))
                polyline(cr, pts, 3, YELLOW, 0.45)
            syms = MATH_SYMBOLS[:max(0, int(len(MATH_SYMBOLS) * clamp(p_sym * 1.3)))]
            floating_symbols(cr, T, syms, hx, hy + 20, 560, 330, size=54, c=WHITE, a=0.9, seed=4, speed=0.22)
            # the hero: eyes first, then the whole face
            smirk = ease(prog(T, w("c1_01", "ridiculously"), 0.6))
            p = sm.pose("front", s=3.0, lw=5.2, smile=lerp(0.1, 0.75, smirk), browy=0.5 * smirk,
                        gx=0.25 * math.sin(T * 0.8), gy=-0.2)
            p["blink"] = max(1 - ease(prog(T, 0.35, 0.4)), sm.blink(T, 2, 3.1) if T > 1.5 else 0)
            p = head_at(p, hx, hy)
            sm.draw(cr, p, ink=WHITE, fill=NIGHT_FILL, alpha=p_head)
            if p_head < 1:
                sm.draw(cr, p, ink=WHITE, fill=NIGHT_FILL, face_only=True, alpha=1 - p_head)
        vignette(cr, 0.6)

    for k in range(int(s("c1_02") / 1.0) + 1):
        b.fx(k * 1.0, "tick" if k % 2 == 0 else "tock", -6 if k < 2 else -12)
    b.fx(0.35, "blink", -8)
    b.fx(s("c1_01") + 0.4, "shimmer", -10)

    # ------------------------------------------------------------ 2. mathematics? effortless
    st2 = s("c1_02") - 0.08

    @b.shot(st2, "white", 0.25)
    def maths(cr, t, d, T):
        paper(cr, grid_bg := PAPER)
        P_grid(cr)
        with ken(cr, t, d, 1.0, 1.05):
            eq = "(3x + 2)(x − 4) − 3x² + 10x"
            text(cr, eq, 700, 420, 76, face=FONT_SERIF, italic=True)
            k = prog(T, w("c1_02", "effortless"), 0.25)
            if k > 0:
                line(cr, 250, 420, 250 + 900 * eout(k), 420, 7, RED, 0.8)
                pop_text(cr, "= −8", 700, 580, T - w("c1_02", "effortless"), 140, face=FONT_SERIF, c=BLUE,
                         bold=True)
                check(cr, 1000, 570, 2.2, p=prog(T, w("c1_02", "effortless") + 0.15, 0.25))
            p = sm.pose("shrug", x=1480, face=-1, smile=0.8, s=1.45)
            p = sm.idle(p, T, 1)
            p = sm.on_ground(p, 1000)
            sm.hero(cr, p)
            ground(cr, 1000, x0=1180, x1=1780)

    def P_grid(cr):
        src(cr, INK, 0.04)
        cr.set_line_width(1.5)
        for x in range(0, W + 1, 60):
            cr.move_to(x, 0)
            cr.line_to(x, H)
        for y in range(0, H + 1, 60):
            cr.move_to(0, y)
            cr.line_to(W, y)
        cr.stroke()

    b.fx(st2, "whoosh", -6)
    b.fx(w("c1_02", "effortless") + 0.05, "ding", -6)

    # ------------------------------------------------------------ 3. languages
    st3 = s("c1_03") - 0.1
    words = [("Hola", 380, 300), ("Bonjour", 1500, 260), ("Привет", 320, 760), ("Ciao", 1580, 760),
             ("Olá", 640, 180), ("Hallo", 1270, 160), ("Γεια σου", 1600, 520), ("Merhaba", 300, 530),
             ("Salut", 700, 880), ("Hej", 1250, 900)]

    @b.shot(st3, "cut")
    def languages(cr, t, d, T):
        paper(cr)
        with ken(cr, t, d, 1.04, 1.0):
            k_sub = prog(T, w("c1_03", "instantly"), 0.4)
            for i, (wd, x, y) in enumerate(words):
                tt = t - i * 0.07
                latin = all(ord(ch) < 0x250 for ch in wd)
                pop_text(cr, wd, x, y, tt, 64 if latin else 54, face=FONT_HAND if latin else "DejaVu Sans",
                         bold=True, c=[BLUE, RED, INK, GREEN, PURPLE][i % 5])
                if k_sub > 0:
                    text(cr, "= hello", x, y + 56, 34, c=MID, a=clamp(k_sub * 2 - i * 0.1), face=FONT_HAND)
            p = sm.pose("front", x=CX, smile=0.5 + 0.4 * k_sub, s=1.25, gx=0.6 * math.sin(T * 3))
            p = add(p, head=6 * math.sin(T * 5) * k_sub)
            p = sm.on_ground(sm.idle(p, T, 2), 960)
            sm.hero(cr, p)
            ground(cr, 960, x0=760, x1=1160)

    def add(p, **kw):
        return sm.add(p, **kw)

    for i in range(len(words)):
        b.fx(st3 + i * 0.07, "pop", -14)

    # ------------------------------------------------------------ 4. human behaviour patterns
    st4 = s("c1_04") - 0.12
    crowd = []
    r = rng(21)
    for i in range(9):
        crowd.append(dict(x0=r.uniform(-200, W + 200), y=r.uniform(640, 820), sp=r.uniform(60, 120) * r.choice([-1, 1]),
                          s=r.uniform(0.45, 0.62), icon=i % 3, ph=r.uniform(0, 5)))
    crowd.sort(key=lambda c: c["y"])

    @b.shot(st4, "slide", 0.4)
    def behaviour(cr, t, d, T):
        paper(cr, PAPER2)
        with ken(cr, t, d, 1.0, 1.07, CX, CY + 40):
            P.skyline(cr, 0, 600, W, 260, seed=12, fill=LIGHT, win=False)
            ground(cr, 600, MID, 3)
            heads = []
            for c in crowd:
                x = (c["x0"] + c["sp"] * t) % (W + 400) - 200
                p = sm.walk(sm.pose(x=x, s=c["s"], face=1 if c["sp"] > 0 else -1), t + c["ph"], 0.9)
                p = sm.on_ground(p, c["y"])
                J = sm.draw(cr, p, ink=GRAY, acc=())
                heads.append((J["head"][0], J["head"][1] - 70 * c["s"], c["icon"]))
            k = prog(T, w("c1_04", "patterns"), 0.6)
            if k > 0:
                for icon in range(3):
                    pts = [(hx, hy) for hx, hy, ic in heads if ic == icon]
                    col = [BLUE, RED, GREEN][icon]
                    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                        partial_line(cr, x1, y1, x2, y2, k, 4, col, 0.75)
                    for (hx, hy) in pts:
                        circle(cr, hx, hy, 16 * eout(k), fill=col, stroke=INK, w=3)
            p = sm.pose("think", x=330, s=1.15, face=1, gx=math.sin(T * 2.2) * 0.9, brow=0.3)
            p = sm.on_ground(sm.idle(p, T, 3), 1010)
            sm.hero(cr, p)
        vignette(cr, 0.2)

    b.fx(st4, "whoosh", -8)
    b.fx(w("c1_04", "patterns"), "sparkle", -8)

    # ------------------------------------------------------------ 5. connecting fields
    st5 = s("c1_05") - 0.1
    icons = [("SCIENCE", 420, 300, "science", P.atom), ("PSYCHOLOGY", 1500, 300, "psychology", P.brain),
             ("TECHNOLOGY", 1500, 790, "technology", P.chip), ("HISTORY", 420, 790, "history", P.scroll)]

    @b.shot(st5, "fade", 0.3)
    def connect(cr, t, d, T):
        paper(cr)
        hx, hy = CX, 470
        k_net = prog(T, w("c1_05", "incredible"), 0.5)
        with ken(cr, t, d, 1.0, 1.04):
            if k_net > 0:
                glow(cr, hx, hy, 420, YELLOW, 0.4 * k_net)
                for i, (_, x, y, _, _) in enumerate(icons):
                    partial_line(cr, x, y, hx, hy, k_net, 6, YELLOW)
                    x2, y2 = icons[(i + 1) % 4][1], icons[(i + 1) % 4][2]
                    partial_line(cr, x, y, x2, y2, k_net, 4, BLUE, 0.6)
                    for j in range(3):
                        f = (T * 2.5 + j / 3 + i * 0.2) % 1
                        circle(cr, lerp(x, hx, f), lerp(y, hy, f), 7, fill=ORANGE, a=k_net)
            for i, (lab, x, y, word, fn) in enumerate(icons):
                tw0 = w("c1_05", word)
                k = back(prog(T, tw0, 0.4), 2.0)
                if k > 0:
                    with xform(cr, x, y, max(0.01, k)):
                        if fn is P.atom:
                            fn(cr, 0, 0, 1.1, T)
                        elif fn is P.brain:
                            fn(cr, 0, 0, 1.0, t=T)
                        else:
                            fn(cr, 0, 0, 1.0)
                    text(cr, lab, x, y + 140, 40, face=FONT_BOLD, a=clamp(k))
            p = sm.pose("front", s=1.2, smile=0.6 + 0.3 * k_net, eye=1 + 0.15 * k_net, gx=math.sin(T * 4) * 0.6)
            p = head_at(sm.idle(p, T, 4), hx, hy)
            sm.hero(cr, p)

    for _, _, _, word, _ in icons:
        b.fx(w("c1_05", word), "pop", -8)
    b.fx(w("c1_05", "incredible"), "zap", -8)

    # ------------------------------------------------------------ 6. off the charts
    st6 = s("c1_06") - 0.15
    grow_start = w("c1_06", "beyond")
    grow_dur = max(2.0, e("c1_06") - grow_start)

    @b.shot(st6, "black", 0.5)
    def chart(cr, t, d, T):
        k = ein(prog(T, grow_start, grow_dur)) * 0.85 + ease(prog(T, grow_start, grow_dur)) * 0.15
        base = 900
        you_h = lerp(0, 5200, k)
        top = base - you_h
        cam_y = min(CY + 60, top - 60)
        alt = clamp((CY - cam_y) / 4200)
        sky = lerpc(lerpc(PAPER, (0.62, 0.80, 0.98), clamp(alt * 3)), (0.03, 0.04, 0.10), clamp(alt * 1.6 - 0.5))
        fill_bg(cr, sky)
        if alt > 0.45:
            stars(cr, T, n=200, alpha=clamp((alt - 0.45) * 3))
        with camera(cr, 1.0, CX, cam_y):
            # clouds, a plane and a bird flock rushing by
            for (cx_, cy_, sc) in ((300, -500, 1.4), (1600, -900, 1.2), (700, -1500, 1.6), (1400, -2100, 1.1)):
                P.cloud(cr, cx_, cy_, sc)
            P_plane(cr, 1500, -1700, T)
            ground(cr, base, INK, 6, -2000, 4000)
            vals = [(560, 200, "AVERAGE", "100", BLUE), (860, 290, "VERY RARE", "145+", GREEN)]
            for x, h, lab, num, col in vals:
                kk = eout(prog(T, st6 + 0.2, 0.6))
                rect(cr, x - 80, base - h * kk, 160, h * kk, fill=col, stroke=INK, lw=5)
                text(cr, num, x, base - h * kk - 40, 48, face=FONT_BOLD, a=kk)
                text(cr, lab, x, base + 48, 38, face=FONT_HAND, bold=True)
            x = 1240
            rect(cr, x - 80, top, 160, you_h, fill=YELLOW, stroke=INK, lw=5)
            text(cr, "YOU", x, base + 48, 38, face=FONT_HAND, bold=True)
            text(cr, "???", x + 190, top - 200, 64, face=FONT_BOLD, a=clamp(k * 5), c=INK if alt < 0.4 else WHITE)
            p = sm.pose("surprised" if k > 0.05 else "front", x=x, face=-1)
            if k > 0.5:
                p = sm.mix(p, sm.pose("cheer", x=x, face=-1), ease((k - 0.5) * 3))
            p = sm.on_ground(sm.idle(p, T, 5), top)
            sm.hero(cr, p, ink=INK if alt < 0.55 else WHITE, fill=WHITE if alt < 0.55 else NIGHT_FILL)
            if k > 0.05:
                speed_lines(cr, T, n=18, c=INK if alt < 0.5 else WHITE, a=0.18 * clamp(k * 4), horizontal=False)
        vignette(cr, 0.25)

    def P_plane(cr, x, y, T):
        with xform(cr, x - (T * 120) % 600, y, 1.2):
            polyline(cr, [(-80, 0), (70, -6), (95, 4), (70, 12), (-80, 10)], 4, INK, closed=True, fill=WHITE)
            polyline(cr, [(-10, 4), (-40, 50), (-20, 50), (20, 6)], 4, INK, closed=True, fill=WHITE)
            polyline(cr, [(-70, 2), (-90, -30), (-75, -30), (-55, 2)], 4, INK, closed=True, fill=WHITE)

    b.fx(grow_start, "riser", -6, dur=grow_dur)
    b.fx(grow_start + grow_dur * 0.55, "whoosh", -8)

    # ------------------------------------------------------------ 7. a hypothetical IQ of 500
    st7 = s("c1_07") - 0.1
    t_hyp, t_500 = w("c1_07", "hypothetical"), w("c1_07", "500", lead=0.0)

    @b.shot(st7, "cut")
    def five_hundred(cr, t, d, T):
        dark(cr, T, star_a=1.0)
        k5 = prog(T, t_500, 0.3)
        sx, sy = shake(T - t_500, 18 * max(0, 1 - (T - t_500) * 2.5) if T > t_500 else 0)
        with camera(cr, 1.0 + 0.02 * t, CX - sx, CY - sy):
            P.globe(cr, CX, 1400, 520, T * 0.3)
            text(cr, "IQ", CX, 220, 90, c=WHITE, face=FONT_TITLE, a=eout(prog(t, 0, 0.3)))
            if k5 > 0:
                glow(cr, CX, 470, 600, YELLOW, 0.35 * k5)
                text(cr, "500", CX, 480, 380, c=YELLOW, face=FONT_TITLE, scale=lerp(3.0, 1.0, eout(k5)),
                     a=clamp(k5 * 3), outline=(0.3, 0.2, 0.0), ow=12)
                burst(cr, CX, 480, T - t_500, n=30, dist=900, size=10, c=WHITE, dur=1.0, seed=2, shape="line")
            stamp(cr, "HYPOTHETICAL", CX, 800, T - t_hyp, 64, c=CYAN, rot=-0.06)
        vignette(cr, 0.45)

    b.fx(t_hyp, "stamp", -6)
    b.fx(t_500, "boom", -4)

    # ------------------------------------------------------------ 8. the real question
    st8 = s("c1_08") - 0.2

    @b.shot(st8, "black", 0.4)
    def question(cr, t, d, T):
        fill_bg(cr, BLACK)
        k = ease(prog(t, 0, 0.6))
        # light cone
        cr.move_to(CX - 60, -10)
        cr.line_to(CX + 60, -10)
        cr.line_to(CX + 330, 900)
        cr.line_to(CX - 330, 900)
        cr.close_path()
        g = cairo_lin(0, 0, 0, 900, (1, 1, 0.9, 0.18 * k), (1, 1, 0.9, 0.04 * k))
        cr.set_source(g)
        cr.fill()
        ellipse(cr, CX, 905, 330, 40, fill=(1, 1, 0.9), a=0.12 * k)
        r = rng(4)
        for i in range(40):
            px = CX + r.uniform(-200, 200) + math.sin(T * 0.5 + i) * 20
            py = (r.uniform(0, 900) + T * 15) % 900
            circle(cr, px + (py / 900) * r.uniform(-120, 120), py, 2, fill=WHITE, a=0.35 * k)
        p = sm.pose("front", x=CX, smile=0.0, gy=-0.9, s=1.1)
        p = sm.on_ground(sm.idle(p, T, 6), 905)
        sm.hero(cr, p, ink=WHITE, fill=NIGHT_FILL, alpha=k)

    b.fx(st8 + 0.1, "tick", -8)
    b.fx(st8 + 0.6, "tock", -8)
    b.fx(st8 + 1.1, "tick", -8)
    b.fx(st8 + 1.6, "tock", -10)

    # ------------------------------------------------------------ 9. genius or problem?
    st9 = s("c1_09") - 0.1
    t_or = w("c1_09", "or would")

    @b.shot(st9, "fade", 0.3)
    def split(cr, t, d, T):
        k_r = eout(prog(T, t_or, 0.5))
        split_x = lerp(W, CX, k_r)
        # left: the smartest person alive
        rect(cr, 0, 0, W, H, fill=(1.0, 0.95, 0.80))
        radial_lines(cr, split_x / 2, 420, T, n=24, c=YELLOW, a=0.35, w=26)
        lx = split_x / 2
        rect(cr, lx - 130, 760, 260, 160, fill=WHITE, stroke=INK, lw=6)
        text(cr, "1", lx, 840, 90, face=FONT_TITLE, c=YELLOW, outline=INK, ow=5)
        p = sm.pose("cheer", x=lx, s=1.1)
        p = sm.on_ground(sm.idle(p, T, 7), 760)
        sm.draw(cr, p, acc=("tuft", "crown"))
        r = rng(8)
        for i in range(30):
            cx_ = (r.uniform(0, 1) * split_x)
            cy_ = (r.uniform(-200, H) + T * r.uniform(120, 260)) % (H + 100) - 50
            rect(cr, cx_, cy_, 14, 8, fill=[RED, BLUE, GREEN, YELLOW, PURPLE][i % 5])
        text(cr, "SMARTEST PERSON ALIVE?", lx, 140, 64 if k_r < 0.5 else 52, face=FONT_TITLE)
        # right: your own worst problem
        if k_r > 0:
            cr.save()
            cr.rectangle(split_x, 0, W - split_x, H)
            cr.clip()
            vgrad(cr, (0.25, 0.04, 0.06), (0.06, 0.02, 0.03))
            rx = split_x + (W - split_x) / 2
            r2 = rng(3)
            for i in range(14):
                pts = []
                cxs, cys = rx + r2.uniform(-260, 260), 440 + r2.uniform(-200, 160)
                for j in range(40):
                    a = j * 0.5 + T * r2.uniform(1, 3)
                    rr = 40 + j * 3
                    pts.append((cxs + math.cos(a) * rr * 0.9, cys + math.sin(a) * rr * 0.6))
                polyline(cr, pts, 3, RED, 0.5)
            for i in range(8):
                a = T * 1.5 + i * TAU / 8
                question_mark(cr, rx + math.cos(a) * 280, 430 + math.sin(a) * 200, 70, c=RED, rot=math.sin(T + i))
            p = sm.pose("worried", x=rx, s=1.1, face=-1)
            p = sm.apply(p, a1f=150, a2f=60, a1b=-150, a2b=-60, lean=8, head=10)
            p = sm.on_ground(sm.add(p, x=math.sin(T * 30) * 2), 900)
            sm.hero(cr, p, ink=WHITE, fill=(0.2, 0.04, 0.05))
            text(cr, "BIGGEST PROBLEM?", rx, 140, 52, face=FONT_TITLE, c=WHITE)
            cr.restore()
            polyline(cr, [(split_x, 0), (split_x - 20, 300), (split_x + 18, 480), (split_x - 14, 700),
                          (split_x, H)], 10, INK)

    def question_mark(cr, x, y, size, c, rot):
        P.question_mark(cr, x, y, size, c, 0.8, rot)

    b.fx(st9, "chime", -8)
    b.fx(t_or, "glitch", -6)

    # ------------------------------------------------------------ 10. title reveal
    st10 = e("c1_09") - 0.25

    @b.shot(st10, "cut")
    def title(cr, t, d, T):
        title_card(cr, t)

    b.fx(st10, "whoosh", -4)
    b.fx(st10 + 0.5, "boom", 0)
    b.fx(st10 + 0.55, "shimmer", -8)
    return b.result()


def cairo_lin(x0, y0, x1, y1, c0, c1):
    import cairo
    g = cairo.LinearGradient(x0, y0, x1, y1)
    g.add_color_stop_rgba(0, *c0)
    g.add_color_stop_rgba(1, *c1)
    return g
