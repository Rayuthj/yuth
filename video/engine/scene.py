"""Shots, transitions and the per-chapter timeline helper."""
import math

from .core import (W, H, CX, CY, FPS, INK, WHITE, BLACK, PAPER, YELLOW, src, clamp, ease, eout, prog,
                   lerp, text, rrect, line, speed_lines, FONT_BOLD, FONT_UI, group, saved)


class TL:
    """Chapter-local timing for narration beats."""

    def __init__(self, data):
        self.data = data
        self.dur = data["end"] - data["start"]
        self.start = data["start"]
        self.beats = {b["id"]: b for b in data["beats"]}
        self.order = [b["id"] for b in data["beats"]]

    def s(self, bid, frac=0.0):
        b = self.beats[bid]
        return b["start"] + (b["end"] - b["start"]) * frac

    def e(self, bid):
        return self.beats[bid]["end"]

    def d(self, bid):
        b = self.beats[bid]
        return b["end"] - b["start"]

    def env(self, bid, T):
        """Narration loudness (0..1) of a beat at chapter time T, for lip-sync."""
        b = self.beats[bid]
        if T < b["start"] or T > b["end"]:
            return 0.0
        i = int((T - b["start"]) * FPS)
        e = b["env"]
        return e[i] if 0 <= i < len(e) else 0.0

    def w(self, bid, word, occ=0, lead=0.08):
        """Estimated time a word is spoken (proportional to character offset)."""
        b = self.beats[bid]
        txt = b["text"]
        low = txt.lower()
        i = -1
        for _ in range(occ + 1):
            i = low.find(word.lower(), i + 1)
        if i < 0:
            raise KeyError(f"{word!r} not in {bid}")
        return b["start"] + (b["end"] - b["start"]) * (i / max(1, len(txt))) - lead

    def speaking(self, ids, T):
        return max((self.env(i, T) for i in ids), default=0.0)

    def next_start(self, bid):
        i = self.order.index(bid)
        return self.s(self.order[i + 1]) if i + 1 < len(self.order) else self.dur


class Shot:
    def __init__(self, start, draw, trans="cut", tdur=0.5, name=""):
        self.start = start
        self.draw = draw
        self.trans = trans
        self.tdur = tdur
        self.name = name
        self.dur = None


def finalize(shots, total):
    shots = sorted(shots, key=lambda s: s.start)
    for a, b in zip(shots, shots[1:]):
        a.dur = b.start - a.start
    shots[-1].dur = total - shots[-1].start
    return shots


def active(shots, T):
    idx = 0
    for i, s in enumerate(shots):
        if s.start <= T + 1e-9:
            idx = i
    return idx


def draw_frame(cr, shots, T, overlay=None):
    i = active(shots, T)
    cur = shots[i]
    prev = shots[i - 1] if i > 0 else None
    nxt = shots[i + 1] if i + 1 < len(shots) else None
    t = T - cur.start
    tr = cur.trans

    # dip transitions straddle the cut
    if nxt is not None and nxt.trans in ("black", "white") and T > nxt.start - nxt.tdur / 2:
        cur.draw(cr, t, cur.dur)
        a = clamp(1 - (nxt.start - T) / (nxt.tdur / 2))
        src(cr, BLACK if nxt.trans == "black" else WHITE, ease(a))
        cr.paint()
    elif prev is None or tr == "cut" or t >= cur.tdur:
        cur.draw(cr, t, cur.dur)
        if tr in ("black", "white") and prev is not None and t < cur.tdur / 2:
            a = 1 - t / (cur.tdur / 2)
            src(cr, BLACK if tr == "black" else WHITE, ease(a))
            cr.paint()
    else:
        p = t / cur.tdur
        tp = T - prev.start
        if tr in ("black", "white"):
            cur.draw(cr, t, cur.dur)
            a = 1 - t / (cur.tdur / 2) if t < cur.tdur / 2 else 0
            src(cr, BLACK if tr == "black" else WHITE, ease(clamp(a)))
            cr.paint()
        elif tr == "fade":
            prev.draw(cr, tp, prev.dur)
            cr.push_group()
            cur.draw(cr, t, cur.dur)
            cr.pop_group_to_source()
            cr.paint_with_alpha(ease(p))
        elif tr == "iris":
            prev.draw(cr, tp, prev.dur)
            cr.save()
            r = eout(p) * math.hypot(W, H) / 2 + 1
            cr.arc(CX, CY, r, 0, math.tau)
            cr.clip()
            cur.draw(cr, t, cur.dur)
            cr.restore()
            cr.set_line_width(10)
            src(cr, INK, 1 - p)
            cr.arc(CX, CY, r, 0, math.tau)
            cr.stroke()
        elif tr in ("slide", "slide_r"):
            k = -1 if tr == "slide" else 1
            e = ease(p)
            with saved(cr):
                cr.translate(k * W * e, 0)
                prev.draw(cr, tp, prev.dur)
            with saved(cr):
                cr.translate(-k * W * (1 - e), 0)
                cur.draw(cr, t, cur.dur)
            speed_lines(cr, T, n=30, c=INK, a=0.35 * math.sin(p * math.pi))
        elif tr == "wipe":
            e = ease(p)
            prev.draw(cr, tp, prev.dur)
            cr.save()
            cr.rectangle(0, 0, W * e, H)
            cr.clip()
            cur.draw(cr, t, cur.dur)
            cr.restore()
            line(cr, W * e, 0, W * e, H, 14, INK)
        elif tr == "zoom":
            e = ease(p)
            if p < 0.5:
                with saved(cr):
                    z = 1 + 1.5 * ein2(p * 2)
                    cr.translate(CX, CY)
                    cr.scale(z, z)
                    cr.translate(-CX, -CY)
                    prev.draw(cr, tp, prev.dur)
                src(cr, WHITE, clamp(p * 2) * 0.9)
                cr.paint()
            else:
                with saved(cr):
                    z = 0.85 + 0.15 * eout((p - 0.5) * 2)
                    cr.translate(CX, CY)
                    cr.scale(z, z)
                    cr.translate(-CX, -CY)
                    cur.draw(cr, t, cur.dur)
                src(cr, WHITE, clamp(1 - (p - 0.5) * 2) * 0.9)
                cr.paint()
            del e
        else:
            cur.draw(cr, t, cur.dur)
    if overlay is not None:
        overlay(cr, T)


def ein2(t):
    return t * t


def chapter_tag(num, title, dark=False, start=0.25, hold=3.4):
    """Small animated chapter label in the top-left corner."""
    def ov(cr, T):
        if T < start or T > start + hold + 0.6:
            return
        p_in = eout(prog(T, start, 0.5))
        p_out = ease(prog(T, start + hold, 0.5))
        a = p_in * (1 - p_out)
        if a <= 0:
            return
        fg = WHITE if dark else INK
        bg = INK if not dark else WHITE
        x = 70 - 40 * (1 - p_in)
        y = 70
        from .core import font
        font(cr, FONT_BOLD, 26)
        label = f"CHAPTER {num}"
        lw_ = cr.text_extents(label)[4]
        font(cr, FONT_BOLD, 34)
        tw = cr.text_extents(title.upper())[4]
        with group(cr, a):
            rrect(cr, x, y, lw_ + 32, 44, 8, fill=YELLOW)
            text(cr, label, x + 16, y + 22, 26, c=INK, face=FONT_BOLD, align="left")
            rrect(cr, x + lw_ + 40, y, tw + 32, 44, 8, fill=bg, fa=0.85)
            text(cr, title.upper(), x + lw_ + 56, y + 22, 34, c=fg if dark else WHITE, face=FONT_BOLD, align="left") \
                if not dark else text(cr, title.upper(), x + lw_ + 56, y + 22, 34, c=INK, face=FONT_BOLD, align="left")
    return ov
