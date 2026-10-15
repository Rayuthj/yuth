"""Shot templates shared by the series.

Every template returns a draw function ``fn(cr, t, d, T)`` (t = time in shot,
d = shot duration, T = chapter time) that can be registered with
``Builder.add(start, fn, trans)``. Times passed to templates are chapter-time
seconds, normally computed from ``tl.s(beat)`` / ``tl.w(beat, word)``.
"""
import math

from .core import *  # noqa: F401,F403
from .core import (W, H, CX, CY, INK, WHITE, BLACK, PAPER, PAPER2, LIGHT, MID, GRAY, RED, BLUE, CYAN, YELLOW, GREEN,
                   ORANGE, PURPLE, TAU, FONT_TITLE, FONT_BOLD, FONT_HAND, FONT_SERIF, src, fill_bg, vgrad, vignette,
                   glow, stars, text, text_w, font, label_box, stamp, pop_text, typewriter, rect, rrect, rrect_path,
                   line, partial_line, partial_poly, polyline, circle, ellipse, arc, arrow, check, cross, xform, group,
                   camera, clamp, lerp, lerpc, prog, ease, eout, ein, back, bounce, rng, burst, radial_lines,
                   floating_symbols, speech_bubble, thought_bubble, shake, bezier_pts)
from . import stickman as sm
from . import props as P
from . import sets as S

HERO = ("tuft",)


# ---------------------------------------------------------------- characters
def person(cr, T, x, ground_y, g="stand", face=1, s=1.0, acc=HERO, seed=0, ink=INK, fill=WHITE, walk=0.0, talk=None,
           alpha=1.0, idle=True, y=None, **kw):
    """Draw a stickman standing on y=ground_y (or with hip at y if given). Extra kw go to the pose
    (so gx/gy keep their meaning as gaze). Returns joints."""
    p = sm.pose(g, x=x, face=face, s=s, **kw)
    if walk:
        p = sm.walk(p, T + seed, walk)
    elif idle:
        p = sm.idle(p, T, seed)
    if talk is not None:
        p = sm.talk(p, T, talk)
    if y is not None:
        p["y"] = y
    else:
        p = sm.on_ground(p, ground_y)
    return sm.draw(cr, p, ink=ink, fill=fill, acc=acc, alpha=alpha)


def hero(cr, T, x, ground_y, g="stand", **kw):
    kw.setdefault("acc", HERO)
    return person(cr, T, x, ground_y, g, **kw)


def pop(T, t, dur=0.4, s=1.8):
    return back(prog(T, t, dur), s)


def ken(cr, t, d, z0=1.0, z1=1.05, fx=CX, fy=CY):
    k = ease(t / d) if d > 0 else 0
    return camera(cr, lerp(z0, z1, k), fx, fy)


# ---------------------------------------------------------------- music helper
def music(tl, sections, tail=1.2):
    """sections: [(start, style, prog, bpm, intensity), ...]; start is seconds or a beat id."""
    rows = []
    for i, (st, style, prog_, bpm, inten) in enumerate(sections):
        t0 = st if isinstance(st, (int, float)) else max(0.0, tl.s(st) - 0.3)
        if i + 1 < len(sections):
            nx = sections[i + 1][0]
            t1 = nx if isinstance(nx, (int, float)) else max(0.0, tl.s(nx) - 0.3)
        else:
            t1 = tl.dur + tail
        rows.append((t0, t1, style, prog_, bpm, inten, 0.8 if i else 1.2, 0.8))
    return rows


# ---------------------------------------------------------------- generic shots
def icons(title, items, bg=PAPER, title_c=INK, label_c=INK, hero_at=None, y=520, size=1.0, label_size=40,
          zoom=(1.0, 1.04), dark=False):
    """items: [(draw(cr, T), label, t_appear)]; drawn centred at the origin, ~200px wide at size 1."""
    n = len(items)
    rows = 1 if n <= 4 else 2
    per_row = math.ceil(n / rows)

    def fn(cr, t, d, T):
        if callable(bg):
            bg(cr, T)
        else:
            fill_bg(cr, bg)
            vignette(cr, 0.18 if not dark else 0.5)
        with ken(cr, t, d, *zoom):
            if title:
                text(cr, title, CX, 150, 60, face=FONT_TITLE, c=title_c, a=eout(prog(t, 0.05, 0.4)))
            for i, (draw, label, ta) in enumerate(items):
                r, c = divmod(i, per_row)
                cnt = per_row if r < rows - 1 else n - per_row * (rows - 1)
                span = 1500 if cnt > 2 else 1000
                x = CX - span / 2 + span * (c + 0.5) / cnt if cnt > 1 else CX
                yy = y + (r - (rows - 1) / 2) * 330
                k = pop(T, ta)
                if k <= 0:
                    continue
                with xform(cr, x, yy, max(0.01, k) * size * (0.8 if rows > 1 else 1.0)):
                    draw(cr, T)
                if label:
                    text(cr, label, x, yy + 150 * size * (0.8 if rows > 1 else 1.0), label_size, face=FONT_BOLD,
                         c=label_c, a=clamp(k))
            if hero_at:
                hx, gy, g, face = hero_at
                hero(cr, T, hx, gy, g, face=face, ink=WHITE if dark else INK, fill=(0.08, 0.08, 0.12) if dark else WHITE)
    return fn


def big_number(value, t_in, label=None, t_label=None, color=YELLOW, sub=None, t_sub=None, bg="dark",
               hero_gy=None, glow_c=None):
    def fn(cr, t, d, T):
        if bg == "dark":
            vgrad(cr, (0.07, 0.07, 0.13), (0.02, 0.02, 0.05))
            stars(cr, T, n=140, alpha=0.6)
        elif callable(bg):
            bg(cr, T)
        else:
            fill_bg(cr, bg)
        k = prog(T, t_in, 0.35)
        sx, sy = shake(T - t_in, 16 * max(0, 1 - (T - t_in) * 2.5) if T > t_in else 0)
        with camera(cr, 1.0 + 0.02 * t, CX - sx, CY - sy):
            if k > 0:
                glow(cr, CX, 470, 560, glow_c or color, 0.32 * k)
                text(cr, value, CX, 470, 300 if len(value) <= 6 else 220, c=color, face=FONT_TITLE,
                     scale=lerp(2.6, 1.0, eout(k)), a=clamp(k * 3), outline=(0.12, 0.08, 0.02), ow=12)
                burst(cr, CX, 470, T - t_in, n=26, dist=760, size=9, c=WHITE, dur=0.9, seed=4, shape="line")
            if label:
                kl = eout(prog(T, t_label if t_label is not None else t_in + 0.3, 0.4))
                text(cr, label, CX, 720, 64, face=FONT_TITLE, c=WHITE if bg == "dark" else INK, a=kl)
            if sub:
                ks = eout(prog(T, t_sub if t_sub is not None else t_in + 0.8, 0.4))
                text(cr, sub, CX, 820, 44, face=FONT_HAND, bold=True, c=(0.8, 0.82, 0.9) if bg == "dark" else GRAY, a=ks)
            if hero_gy:
                hero(cr, T, 300, hero_gy, "surprised" if k > 0 else "stand", ink=WHITE if bg == "dark" else INK,
                     fill=(0.06, 0.06, 0.1) if bg == "dark" else WHITE)
        vignette(cr, 0.4)
    return fn


def split(left, right, t_right, t_left=None):
    """left/right: dict(title, bg=(r,g,b), ink, draw(cr, cx, T))."""
    def fn(cr, t, d, T):
        k_r = eout(prog(T, t_right, 0.5))
        sx = lerp(W, CX, k_r)
        rect(cr, 0, 0, W, H, fill=left.get("bg", (1.0, 0.95, 0.8)))
        lx = sx / 2
        left["draw"](cr, lx, T)
        kl = eout(prog(T, t_left if t_left is not None else t - t, 0.4)) if t_left is not None else 1.0
        text(cr, left["title"], lx, 140, 60 if k_r < 0.5 else 52, face=FONT_TITLE, c=left.get("ink", INK), a=kl)
        if k_r > 0:
            cr.save()
            cr.rectangle(sx, 0, W - sx, H)
            cr.clip()
            rect(cr, 0, 0, W, H, fill=right.get("bg", (0.25, 0.04, 0.06)))
            rx = sx + (W - sx) / 2
            right["draw"](cr, rx, T)
            text(cr, right["title"], rx, 140, 52, face=FONT_TITLE, c=right.get("ink", WHITE))
            cr.restore()
            polyline(cr, [(sx, 0), (sx - 20, 300), (sx + 18, 480), (sx - 14, 700), (sx, H)], 10, INK)
    return fn


def checklist(title, items, bg=PAPER, side=None, x0=360, y0=330, gap=120, size=60):
    """items: [(label, t)]; side(cr, T) draws an optional figure on the right."""
    def fn(cr, t, d, T):
        fill_bg(cr, bg)
        vignette(cr, 0.18)
        with ken(cr, t, d, 1.0, 1.03):
            text(cr, title, 820, 170, 54, face=FONT_TITLE, a=eout(prog(t, 0.05, 0.4)))
            for i, (lab, ta) in enumerate(items):
                kk = prog(T, ta, 0.35)
                y = y0 + i * gap
                rrect(cr, x0, y - 40, 80, 80, 12, fill=WHITE, stroke=INK, lw=5)
                text(cr, lab, x0 + 120, y, size, face=FONT_TITLE, align="left", a=0.25 + 0.75 * clamp(kk * 2))
                if kk > 0:
                    check(cr, x0 + 40, y, 1.7, p=kk)
            if side:
                side(cr, T)
    return fn


def bars(title, values, labels, t0, colors=None, fmt=None, bg=PAPER, side=None, h=480, w=1000, x=CX, base=820):
    def fn(cr, t, d, T):
        fill_bg(cr, bg)
        vignette(cr, 0.18)
        with ken(cr, t, d, 1.0, 1.03):
            text(cr, title, CX, 150, 56, face=FONT_TITLE, a=eout(prog(t, 0.05, 0.4)))
            k = ease(prog(T, t0, 1.2))
            P.bar_chart(cr, x, base, values, labels, w=w, h=h, p=k, colors=colors or [BLUE, GREEN, ORANGE, RED, PURPLE],
                        size=38)
            if fmt:
                n = len(values)
                mx = max(values)
                for i, v in enumerate(values):
                    kk = clamp(k * n * 0.7 - i * 0.7 + 0.7)
                    if kk > 0.9:
                        bx = x - w / 2 + (i + 0.5) * w / n
                        text(cr, fmt(v), bx, base - h * v / mx - 40, 42, face=FONT_BOLD)
            if side:
                side(cr, T)
    return fn


def timeline(title, marks, t0, bg=PAPER, y=640, x0=220, x1=1700, ink=INK):
    """marks: [(label, t, icon(cr, T) or None)] spread evenly along a line that draws from t0."""
    def fn(cr, t, d, T):
        if callable(bg):
            bg(cr, T)
        else:
            fill_bg(cr, bg)
            vignette(cr, 0.18)
        with ken(cr, t, d, 1.0, 1.03):
            if title:
                text(cr, title, CX, 150, 56, face=FONT_TITLE, c=ink, a=eout(prog(t, 0.05, 0.4)))
            k = ease(prog(T, t0, 0.8))
            partial_line(cr, x0, y, x1, y, k, 10, ink)
            n = len(marks)
            for i, (lab, ta, icon) in enumerate(marks):
                x = x0 + (x1 - x0) * (i + 0.5) / n
                kk = pop(T, ta)
                if kk <= 0:
                    continue
                circle(cr, x, y, 18 * clamp(kk), fill=YELLOW, stroke=ink, w=5)
                if icon:
                    with xform(cr, x, y - 170, max(0.01, kk) * 0.8):
                        icon(cr, T)
                for li, row in enumerate(lab.split("\n")):
                    text(cr, row, x, y + 70 + li * 46, 38 if li == 0 else 32, face=FONT_BOLD, c=ink, a=clamp(kk))
    return fn


def quote(lines, t_in, author=None, bg="dark", color=YELLOW, size=72):
    def fn(cr, t, d, T):
        if bg == "dark":
            vgrad(cr, (0.08, 0.08, 0.13), (0.03, 0.03, 0.06))
        else:
            fill_bg(cr, bg)
        with ken(cr, t, d, 1.0, 1.04):
            n = len(lines)
            text(cr, "“", 260, 300, 300, face=FONT_SERIF, c=color, a=0.5 * eout(prog(T, t_in, 0.4)))
            for i, ln in enumerate(lines):
                k = eout(prog(T, t_in + i * 0.35, 0.5))
                text(cr, ln, CX, CY - (n - 1) * size * 0.65 + i * size * 1.3 + (1 - k) * 30, size, face=FONT_TITLE,
                     c=WHITE if bg == "dark" else INK, a=k)
            if author:
                ka = eout(prog(T, t_in + n * 0.35 + 0.2, 0.5))
                text(cr, "— " + author, CX, CY + n * size * 0.8 + 40, 44, face=FONT_HAND, bold=True, c=color, a=ka)
        vignette(cr, 0.4)
    return fn


def card(num, title, content, bg=None):
    """Blueprint project card with a sliding header; content(cr, t, d, T)."""
    def fn(cr, t, d, T):
        S.blueprint(cr) if bg is None else fill_bg(cr, bg)
        k = eout(prog(t, 0.05, 0.35))
        x = lerp(-600, 70, k)
        content(cr, t, d, T)
        rrect(cr, x, 60, 140, 60, 10, fill=INK)
        text(cr, f"#{num:02d}", x + 70, 90, 34, c=YELLOW, face=FONT_BOLD)
        text(cr, title, x + 165, 90, 46, face=FONT_TITLE, align="left")
    return fn


def three_paths(paths, bg=PAPER, title=None):
    """paths: [(label, color, draw(cr, T) at panel origin 520x600, t_appear)] -> three panels."""
    def fn(cr, t, d, T):
        fill_bg(cr, bg)
        vignette(cr, 0.15)
        if title:
            text(cr, title, CX, 110, 56, face=FONT_TITLE, a=eout(prog(t, 0.05, 0.4)))
        for i, (label, col, draw, ta) in enumerate(paths):
            k = back(prog(T, ta, 0.45))
            if k <= 0:
                continue
            x0 = 120 + i * 580
            with xform(cr, x0 + 260, 560, max(0.01, k)):
                cr.save()
                cr.translate(-260, -300)
                rrect_path(cr, 0, 0, 520, 600, 24)
                cr.clip()
                draw(cr, T)
                cr.restore()
                rrect(cr, -260, -300, 520, 600, 24, stroke=col, lw=10)
            rrect(cr, x0 + 60, 900, 400, 70, 14, fill=col, a=clamp(k))
            text(cr, label, x0 + 260, 935, 40, face=FONT_TITLE, c=WHITE, a=clamp(k))
    return fn


def dialogue(tl, setting, cast, lines, zoom=(1.0, 1.05), focus=(CX, CY)):
    """setting(cr, T); cast: [dict(x, gy, acc, face, g, s, ink, fill, y=None)];
    lines: [(cast_index, text, beat_id, bubble_xy or None)] -> lip-synced speakers with speech bubbles."""
    def fn(cr, t, d, T):
        with ken(cr, t, d, zoom[0], zoom[1], *focus):
            setting(cr, T)
            joints = []
            for ci, c in enumerate(cast):
                env = 0.0
                speaking = False
                for (who, _, bid, _) in lines:
                    if who == ci:
                        e = tl.env(bid, T)
                        if e > 0 or (tl.s(bid) - 0.05 <= T <= tl.e(bid)):
                            speaking = True
                        env = max(env, e)
                g = c.get("talk_g", c.get("g", "stand")) if speaking else c.get("g", "stand")
                J = person(cr, T, c["x"], c.get("gy", 900), g, face=c.get("face", 1), s=c.get("s", 1.0),
                           acc=c.get("acc", ()), seed=ci + 3, ink=c.get("ink", INK), fill=c.get("fill", WHITE),
                           talk=env if speaking else None, y=c.get("y"), **c.get("kw", {}))
                joints.append(J)
            for (who, txt, bid, pos) in lines:
                if tl.s(bid) - 0.15 <= T <= tl.e(bid) + 0.6:
                    kb = back(prog(T, tl.s(bid) - 0.15, 0.3))
                    hx, hy = joints[who]["head"]
                    bx, by = pos if pos else (hx + (260 if cast[who].get("face", 1) > 0 else -260), hy - 220)
                    font(cr, FONT_HAND, 38, True)
                    words = txt.split()
                    rows, cur = [], ""
                    for wd in words:
                        trial = (cur + " " + wd).strip()
                        if cr.text_extents(trial)[4] > 560 and cur:
                            rows.append(cur)
                            cur = wd
                        else:
                            cur = trial
                    rows.append(cur)
                    bw = max(cr.text_extents(r)[4] for r in rows) + 70
                    bh = 46 * len(rows) + 50
                    speech_bubble(cr, bx, by, bw, bh, hx, hy - 50, scale=kb)
                    for ri, r in enumerate(rows):
                        text(cr, r, bx, by - (len(rows) - 1) * 23 + ri * 46, 38, face=FONT_HAND, bold=True, a=clamp(kb))
    return fn


# ---------------------------------------------------------------- hook / finale pieces
def eyes_awaken(symbols, t_sym, t_smirk, color=CYAN, size=54):
    """Dark opening: eyes open, the face appears, ideas orbit the head."""
    def fn(cr, t, d, T):
        fill_bg(cr, BLACK)
        hx, hy = CX, 450
        p_head = ease(prog(T, 0.8, 1.0))
        p_sym = prog(T, t_sym, 4.0)
        with camera(cr, lerp(1.0, 1.1, ease(t / d)), CX, hy + 40):
            glow(cr, hx, hy, 700, color, 0.20 * p_head)
            for k, (rr, n, sp) in enumerate(((230, 48, 0.12), (330, 72, -0.08), (440, 96, 0.05))):
                kk = clamp(p_sym * 3 - k)
                for i in range(int(n * kk)):
                    a = i / n * TAU + T * sp
                    circle(cr, hx + math.cos(a) * rr, hy + math.sin(a) * rr, 2.6, fill=color, a=0.55)
            syms = symbols[:max(0, int(len(symbols) * clamp(p_sym * 1.3)))]
            floating_symbols(cr, T, syms, hx, hy + 20, 560, 330, size=size, c=WHITE, a=0.9, seed=4, speed=0.22,
                             face=FONT_BOLD, italic=False)
            smirk = ease(prog(T, t_smirk, 0.6))
            p = sm.pose("front", s=3.0, lw=5.2, smile=lerp(0.1, 0.75, smirk), browy=0.5 * smirk,
                        gx=0.25 * math.sin(T * 0.8), gy=-0.2)
            p["blink"] = max(1 - ease(prog(T, 0.3, 0.4)), sm.blink(T, 2, 3.1) if T > 1.5 else 0)
            from video.chapters.common import head_at
            p = head_at(p, hx, hy)
            nf = (0.06, 0.065, 0.09)
            sm.draw(cr, p, ink=WHITE, fill=nf, alpha=p_head)
            if p_head < 1:
                sm.draw(cr, p, ink=WHITE, fill=nf, face_only=True, alpha=1 - p_head)
        vignette(cr, 0.6)
    return fn


def real_question(t0):
    """'But here's the question:' - the hero alone in a spotlight."""
    def fn(cr, t, d, T):
        import cairo
        fill_bg(cr, BLACK)
        k = ease(prog(t, 0, 0.6))
        cr.move_to(CX - 60, -10)
        cr.line_to(CX + 60, -10)
        cr.line_to(CX + 330, 900)
        cr.line_to(CX - 330, 900)
        cr.close_path()
        g = cairo.LinearGradient(0, 0, 0, 900)
        g.add_color_stop_rgba(0, 1, 1, 0.9, 0.18 * k)
        g.add_color_stop_rgba(1, 1, 1, 0.9, 0.04 * k)
        cr.set_source(g)
        cr.fill()
        ellipse(cr, CX, 905, 330, 40, fill=(1, 1, 0.9), a=0.12 * k)
        r = rng(4)
        for i in range(40):
            px = CX + r.uniform(-200, 200) + math.sin(T * 0.5 + i) * 20
            py = (r.uniform(0, 900) + T * 15) % 900
            circle(cr, px + (py / 900) * r.uniform(-120, 120), py, 2, fill=WHITE, a=0.35 * k)
        hero(cr, T, CX, 905, "front", s=1.1, smile=0.0, gy=-0.9, ink=WHITE, fill=(0.06, 0.065, 0.09), alpha=k)
    return fn


def title_card(top, big, color=YELLOW, edge=(0.35, 0.22, 0.0), symbols=None, big_size=230):
    """Animated title. Returns fn(cr, t) where t = seconds since the reveal started."""
    def fn(cr, t, a=1.0):
        vgrad(cr, (0.07, 0.07, 0.12), (0.02, 0.02, 0.04))
        stars(cr, t, n=220, alpha=0.6)
        sx, sy = shake(t, 14 * max(0.0, 1 - (t - 0.55) * 3) if t > 0.55 else 0, seed=3)
        with camera(cr, 1 + 0.03 * t, CX - sx, CY - sy):
            radial_lines(cr, CX, CY + 40, t, n=40, r0=260, c=color, a=0.07 * clamp(t * 2), w=14, spin=0.04)
            if symbols:
                floating_symbols(cr, t, symbols, CX, CY + 20, 820, 380, size=46, c=WHITE, a=0.22 * clamp(t * 2),
                                 seed=8, speed=0.18, face=FONT_BOLD, italic=False)
            glow(cr, CX, CY + 80, 520, color, 0.22 * clamp((t - 0.5) * 2))
            words = top.split()
            ws = [text_w(cr, wd, FONT_TITLE, 96) for wd in words]
            gap = 34
            x = CX - (sum(ws) + gap * (len(ws) - 1)) / 2
            for i, wd in enumerate(words):
                k = prog(t, i * 0.08, 0.22)
                if k > 0:
                    text(cr, wd, x + ws[i] / 2, CY - 130, 96, c=WHITE, a=a * clamp(k * 2), face=FONT_TITLE,
                         scale=lerp(2.6, 1.0, eout(k)))
                x += ws[i] + gap
            k = prog(t, 0.5, 0.35)
            if k > 0:
                size = big_size if text_w(cr, big, FONT_TITLE, big_size) < 1700 else big_size * 1700 / text_w(cr, big, FONT_TITLE, big_size)
                text(cr, big, CX, CY + 70, size, c=color, a=a * clamp(k * 3), face=FONT_TITLE,
                     scale=lerp(3.0, 1.0, back(k, 1.4)), outline=edge, ow=10)
            burst(cr, CX, CY + 70, t - 0.62, n=26, dist=700, size=10, c=color, dur=1.1, seed=5)
            burst(cr, CX, CY + 70, t - 0.62, n=18, dist=520, size=12, c=WHITE, dur=0.9, seed=9, shape="line")
            k2 = prog(t, 1.1, 0.5)
            if k2 > 0:
                line(cr, CX - 360 * eout(k2), CY + 225, CX + 360 * eout(k2), CY + 225, 6, WHITE, 0.6 * a)
    return fn


CONSTELLATIONS = {
    "heart": [(0, 0.8), (-0.85, -0.05), (-0.75, -0.6), (-0.35, -0.75), (0, -0.4), (0.35, -0.75), (0.75, -0.6),
              (0.85, -0.05), (0, 0.8)],
    "clock": [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), None,
              (0, 0), (0, -0.6), None, (0, 0), (0.45, 0.2)],
    "crown": [(-1, 0.6), (-1, -0.4), (-0.5, 0.1), (0, -0.8), (0.5, 0.1), (1, -0.4), (1, 0.6), (-1, 0.6)],
    "star": [(0, -1), (0.25, -0.3), (0.95, -0.3), (0.4, 0.15), (0.6, 0.9), (0, 0.45), (-0.6, 0.9), (-0.4, 0.15),
             (-0.95, -0.3), (-0.25, -0.3), (0, -1)],
    "house": [(-0.8, 0.8), (-0.8, -0.1), (0, -0.8), (0.8, -0.1), (0.8, 0.8), (-0.8, 0.8)],
    "people": [(-0.9, 0.8), (-0.6, 0.0), (-0.3, 0.8), None, (-0.6, 0.0), (-0.6, -0.5), None, (0.3, 0.8), (0.6, 0.0),
               (0.9, 0.8), None, (0.6, 0.0), (0.6, -0.5), None, (-0.6, -0.3), (0.6, -0.3)],
    "tree": [(0, 0.9), (0, -0.1), None, (0, 0.2), (-0.6, -0.3), None, (0, 0.0), (0.6, -0.5), None, (0, -0.1),
             (0, -0.9)],
    "hourglass": [(-0.6, -0.9), (0.6, -0.9), (-0.6, 0.9), (0.6, 0.9), (-0.6, -0.9)],
    "book": [(-1, -0.6), (0, -0.4), (1, -0.6), (1, 0.6), (0, 0.8), (-1, 0.6), (-1, -0.6), None, (0, -0.4), (0, 0.8)],
    "moon": [(0.3, -0.9), (-0.4, -0.7), (-0.8, 0), (-0.4, 0.7), (0.3, 0.9), (-0.05, 0.4), (-0.15, 0), (-0.05, -0.4),
             (0.3, -0.9)],
    "coin": [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), None,
             (0, -0.5), (0, 0.5)],
    "question": [(-0.5, -0.5), (-0.3, -0.85), (0.2, -0.95), (0.55, -0.6), (0.4, -0.2), (0, 0.05), (0, 0.4), None,
                 (0, 0.85)],
}


def constellation(cr, shape, cx, cy, size, k, T, c=(0.92, 0.94, 1.0), a=1.0, label=None):
    pts = CONSTELLATIONS[shape]
    segs, cur = [], []
    for p in pts:
        if p is None:
            segs.append(cur)
            cur = []
        else:
            cur.append((cx + p[0] * size, cy + p[1] * size))
    segs.append(cur)
    total = sum(max(0, len(sg) - 1) for sg in segs)
    done = k * total
    for sg in segs:
        if len(sg) >= 2:
            n = len(sg) - 1
            partial_poly(cr, sg, clamp(done / n), 2.5, c, 0.55 * a)
            done -= n
    seen = set()
    for sg in segs:
        for (x, y) in sg:
            key = (round(x), round(y))
            if key in seen or k <= 0:
                continue
            seen.add(key)
            tw = 0.7 + 0.3 * math.sin(T * 2.3 + x * 0.05 + y * 0.03)
            glow(cr, x, y, 26, c, 0.35 * a * clamp(k * 3) * tw)
            circle(cr, x, y, 4.5, fill=WHITE, a=a * clamp(k * 3) * tw)
    if label and k > 0.6:
        text(cr, label, cx, cy + size + 50, 34, face=FONT_BOLD, c=c, a=a * clamp((k - 0.6) * 3))


def small_hero_night(cr, T, x=CX, ground_y=912, **kw):
    kw.setdefault("gy", -0.9)
    g = kw.pop("g", "front")
    return hero(cr, T, x, ground_y, g, s=0.8, fo=0.2, ink=(0.9, 0.9, 1.0), fill=(0.05, 0.055, 0.10), **kw)


def finale_ending(tl, last_beat, quote1, quote2, cta, handle="@WhatIfForeverYT"):
    """Close-up smile -> fade to black -> two-line quote -> call to action held to the end."""
    st = tl.e(last_beat) - 0.15
    t_fade = st + 0.9
    t_quote = t_fade + 0.55
    t_cta = tl.dur - 4.0
    sky1 = (0.03, 0.035, 0.08)
    nf = (0.05, 0.055, 0.10)

    def fn(cr, t, d, T):
        if T < t_fade + 0.5:
            S.night_sky(cr, T, hill=False)
            src(cr, sky1, 0.93)
            cr.paint()
            sm_k = ease(prog(T, st, 0.6))
            p = sm.pose("front", s=3.2, lw=5.0, fo=0.0, gy=0.0, smile=lerp(0.15, 0.7, sm_k), browy=0.25 * sm_k)
            from video.chapters.common import head_at
            p = head_at(sm.idle(p, T, 4, 0.3), CX, 560)
            sm.hero(cr, p, ink=(0.92, 0.92, 1.0), fill=nf)
            fk = ease(prog(T, t_fade, 0.5))
            if fk > 0:
                src(cr, BLACK, fk)
                cr.paint()
            return
        fill_bg(cr, BLACK)
        kq1 = eout(prog(T, t_quote, 0.6))
        kq2 = eout(prog(T, t_quote + 0.8, 0.6))
        up = ease(prog(T, t_cta - 0.2, 0.6))
        y1 = lerp(470, 250, up)
        sc = lerp(1.0, 0.72, up)
        s1 = min(92, 1700 / max(1, text_w(cr, quote1, FONT_TITLE, 92)) * 92)
        s2 = min(92, 1700 / max(1, text_w(cr, quote2, FONT_TITLE, 92)) * 92)
        text(cr, quote1, CX, y1, s1 * sc, face=FONT_TITLE, c=WHITE, a=kq1)
        text(cr, quote2, CX, y1 + 120 * sc, s2 * sc, face=FONT_TITLE, c=YELLOW, a=kq2)
        kc = eout(prog(T, t_cta, 0.6))
        if kc > 0:
            line(cr, CX - 300 * kc, 450, CX + 300 * kc, 450, 4, MID)
            font(cr, FONT_HAND, 54, True)
            rows, cur = [], ""
            for wd in cta.split():
                trial = (cur + " " + wd).strip()
                if cr.text_extents(trial)[4] > 1400 and cur:
                    rows.append(cur)
                    cur = wd
                else:
                    cur = trial
            rows.append(cur)
            for i, r in enumerate(rows):
                text(cr, r, CX, 580 + i * 78, 54, face=FONT_HAND, bold=True, c=WHITE, a=kc)
            kb = back(prog(T, t_cta + 0.5, 0.5))
            speech_bubble(cr, CX + 60, 860, 300, 100, CX - 40, 960, fill=(0.12, 0.12, 0.14), stroke=WHITE, scale=kb)
            text(cr, "comment below", CX + 60, 860, 36, face=FONT_HAND, bold=True, c=YELLOW, a=clamp(kb))
            if handle:
                text(cr, "Subscribe  " + handle, CX, 1010, 34, face=FONT_BOLD, c=CYAN, a=clamp(kb))
            p = sm.pose("wave", x=CX - 330, s=0.55, smile=0.9)
            p = sm.apply(p, a2f=42 + 22 * math.sin(T * 8))
            p = sm.on_ground(sm.idle(p, T, 5), 1000)
            sm.hero(cr, p, ink=WHITE, fill=BLACK, alpha=kc)
    return st, t_fade, t_quote, t_cta, fn
