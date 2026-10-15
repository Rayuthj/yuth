"""Vertical YouTube Short (1080x1920) cut from the hook of the main video.

    python3 video/short.py   -> output/short_what_if_you_had_500_iq.mp4

Layout keeps text inside the Shorts safe area (clear of the top bar, the
right-hand buttons and the bottom title/channel overlay):
  - animated title at the top
  - the 16:9 hook (0:00-0:40) in the middle
  - big captions below, with the word being spoken highlighted
  - a 3.5 s end card pointing to the full video
"""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import cairo  # noqa: E402

from video.engine.core import (INK, WHITE, YELLOW, RED, CYAN, BLACK, FONT_TITLE, FONT_BOLD, TAU, src, text, font,  # noqa: E402
                               clamp, ease, eout, back, prog, lerp, glow, stars, rrect, rrect_path, line, polyline,
                               floating_symbols, burst, xform)
from video.engine import stickman as sm  # noqa: E402
from video.chapters.common import MATH_SYMBOLS  # noqa: E402

SW, SH, FPS = 1080, 1920, 30
SRC_W, SRC_H = 1920, 1080
CLIP = 40.0          # seconds of the main video used (the whole hook)
END = 3.5            # end card length
TOTAL = CLIP + END
HANDLE = "@WhatIfForeverYT"
MASTER = os.path.join(ROOT, "output", "what_if_you_had_500_iq.mp4")
OUT = os.path.join(ROOT, "output", "short_what_if_you_had_500_iq.mp4")

VID_Y = 600                       # top of the embedded 16:9 video
VID_H = int(SW * SRC_H / SRC_W)   # 607
CAP_Y = VID_Y + VID_H + 70        # captions block top
CAP_W = 860                       # stays clear of the right-hand Shorts buttons
CAP_X = 70


def background(cr, T):
    g = cairo.LinearGradient(0, 0, 0, SH)
    g.add_color_stop_rgb(0, 0.06, 0.07, 0.16)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.04)
    cr.set_source(g)
    cr.paint()
    stars(cr, T, n=140, alpha=0.6, area=(0, 0, SW, SH))
    floating_symbols(cr, T, MATH_SYMBOLS, SW / 2, 900, 520, 820, size=58, c=WHITE, a=0.10, seed=4, speed=0.08)


def title(cr, T):
    k1 = eout(prog(T, 0.0, 0.5))
    k2 = back(prog(T, 0.25, 0.5), 1.8)
    text(cr, "WHAT IF YOU HAD", SW / 2, 270, 86, c=WHITE, face=FONT_TITLE, a=k1, outline=BLACK, ow=10,
         scale=lerp(0.8, 1.0, k1))
    pulse = 1 + 0.025 * math.sin(T * 3.2)
    glow(cr, SW / 2, 420, 330, YELLOW, 0.18 * k2)
    text(cr, "500 IQ?", SW / 2, 420, 190, c=YELLOW, face=FONT_TITLE, a=clamp(k2), outline=(0.25, 0.15, 0.0), ow=14,
         scale=max(0.01, k2) * pulse)


def video_frame(cr, frame_surf):
    with xform(cr, 0, VID_Y, 1.0):
        rrect_path(cr, 18, 0, SW - 36, VID_H, 26)
        cr.save()
        cr.clip()
        sc = (SW - 36) / SRC_W
        cr.translate(18, (VID_H - SRC_H * sc) / 2)
        cr.scale(sc, sc)
        cr.set_source_surface(frame_surf, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_GOOD)
        cr.paint()
        cr.restore()
        rrect(cr, 18, 0, SW - 36, VID_H, 26, stroke=YELLOW, lw=6)


def words_with_times(beat):
    """Split a line into words with estimated start times (by character position)."""
    txt = beat["text"]
    out, pos = [], 0
    for wd in txt.split():
        i = txt.find(wd, pos)
        out.append((wd, beat["start"] + (beat["end"] - beat["start"]) * i / len(txt)))
        pos = i + len(wd)
    return out


def captions(cr, T, beats):
    cur = next((b for b in beats if b["start"] - 0.1 <= T <= b["end"] + 0.25), None)
    if cur is None:
        return
    words = words_with_times(cur)
    size = 70
    font(cr, FONT_TITLE, size)
    space = cr.text_extents(" ")[4]
    lines, line_w, row = [[]], 0.0, 0
    for wd, t0 in words:
        w = cr.text_extents(wd)[4]
        if line_w + w > CAP_W and lines[-1]:
            lines.append([])
            line_w = 0.0
        lines[-1].append((wd, t0, w))
        line_w += w + space
    # show at most 3 lines: the window that contains the current word
    spoken = [i for i, (_, t0) in enumerate(words) if t0 <= T]
    idx = spoken[-1] if spoken else 0
    flat = [ln for ln in lines]
    cum = 0
    line_of = []
    for li, ln in enumerate(flat):
        line_of += [li] * len(ln)
        cum += len(ln)
    cur_line = line_of[min(idx, len(line_of) - 1)]
    first = max(0, min(cur_line - 1, len(flat) - 3))
    shown = flat[first:first + 3]
    k = eout(prog(T, cur["start"] - 0.1, 0.25))
    a = k * (1 - clamp((T - cur["end"]) / 0.25)) if T > cur["end"] else k
    n_before = sum(len(ln) for ln in flat[:first])
    wi = n_before
    for r, ln in enumerate(shown):
        total = sum(w for _, _, w in ln) + space * (len(ln) - 1)
        x = CAP_X + (CAP_W - total) / 2
        y = CAP_Y + 50 + r * size * 1.22 + (1 - k) * 20
        for wd, t0, w in ln:
            active = wi == idx and T <= cur["end"] + 0.05
            said = t0 <= T
            col = YELLOW if active else (WHITE if said else (0.78, 0.80, 0.86))
            text(cr, wd, x + w / 2, y, size, c=col, face=FONT_TITLE, a=a, outline=BLACK, ow=12)
            x += w + space
            wi += 1


def end_card(cr, t, thumb):
    background(cr, CLIP + t)
    k = back(prog(t, 0.0, 0.5), 1.6)
    text(cr, "WANT THE", SW / 2, 300, 110, c=WHITE, face=FONT_TITLE, outline=BLACK, ow=12, scale=max(0.01, k))
    text(cr, "FULL STORY?", SW / 2, 430, 120, c=YELLOW, face=FONT_TITLE, outline=(0.25, 0.15, 0.0), ow=12,
         scale=max(0.01, back(prog(t, 0.15, 0.5), 1.6)))
    kt = eout(prog(t, 0.35, 0.5))
    if kt > 0:
        w, h = 900, 506
        with xform(cr, SW / 2, 820 + (1 - kt) * 80, lerp(0.85, 1.0, kt)):
            glow(cr, 0, 0, 620, YELLOW, 0.25 * kt)
            rrect_path(cr, -w / 2, -h / 2, w, h, 28)
            cr.save()
            cr.clip()
            cr.scale(w / thumb.get_width(), h / thumb.get_height())
            cr.set_source_surface(thumb, -thumb.get_width() / 2, -thumb.get_height() / 2)
            cr.paint_with_alpha(kt)
            cr.restore()
            rrect(cr, -w / 2, -h / 2, w, h, 28, stroke=WHITE, lw=8, a=kt)
            circle_r = 70
            src(cr, RED, kt)
            cr.arc(0, 0, circle_r, 0, TAU)
            cr.fill()
            polyline(cr, [(-22, -36), (38, 0), (-22, 36)], 0, WHITE, closed=True, fill=WHITE, fa=kt)
    kf = eout(prog(t, 0.6, 0.5))
    text(cr, "FULL 10-MINUTE VIDEO", SW / 2, 1170, 66, c=WHITE, face=FONT_TITLE, a=kf, outline=BLACK, ow=10)
    text(cr, "ON MY CHANNEL", SW / 2, 1250, 66, c=WHITE, face=FONT_TITLE, a=kf, outline=BLACK, ow=10)
    kh = back(prog(t, 0.8, 0.5))
    text(cr, HANDLE, SW / 2, 1360, 60, c=CYAN, face=FONT_BOLD, a=clamp(kh), scale=max(0.01, kh))
    p = sm.pose("wave", x=140, s=0.8, smile=1.0)
    p = sm.apply(p, a2f=42 + 25 * math.sin(t * 9))
    p = sm.on_ground(sm.idle(p, t, 2), 1660)
    sm.hero(cr, p, ink=WHITE, fill=(0.05, 0.06, 0.12), alpha=kf)
    burst(cr, SW / 2, 430, t - 0.2, n=22, dist=520, size=10, c=YELLOW, dur=0.9, seed=3)


def main():
    beats = json.load(open(os.path.join(ROOT, "build", "timeline.json")))["1"]["beats"]
    thumb = cairo.ImageSurface.create_from_png(os.path.join(ROOT, "output", "thumbnail.png"))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-t", str(CLIP), "-i", MASTER, "-f", "rawvideo",
                            "-pix_fmt", "bgr0", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{SW}x{SH}",
                            "-r", str(FPS), "-i", "-", "-ss", "0", "-t", str(TOTAL), "-i", MASTER,
                            "-map", "0:v", "-map", "1:a",
                            "-af", f"afade=t=out:st={CLIP - 0.3}:d=1.4,apad=whole_dur={TOTAL}",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "animation",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(TOTAL),
                            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH)
    cr = cairo.Context(surf)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    frame_bytes = SRC_W * SRC_H * 4
    n = int(round(TOTAL * FPS))
    for i in range(n):
        T = i / FPS
        cr.save()
        if T < CLIP:
            raw = dec.stdout.read(frame_bytes)
            if len(raw) < frame_bytes:
                raw = last
            last = raw
            fs = cairo.ImageSurface.create_for_data(bytearray(raw), cairo.FORMAT_RGB24, SRC_W, SRC_H, SRC_W * 4)
            background(cr, T)
            title(cr, T)
            video_frame(cr, fs)
            captions(cr, T, beats)
            # fade the final frames into the end card
            fo = clamp((T - (CLIP - 0.35)) / 0.35)
            if fo > 0:
                src(cr, BLACK, fo * 0.6)
                cr.paint()
        else:
            end_card(cr, T - CLIP, thumb)
        cr.restore()
        surf.flush()
        enc.stdin.write(surf.get_data())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
