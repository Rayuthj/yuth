"""Render chapters to video, or preview frames as PNG contact sheets.

    python3 video/render.py 3                 # render chapter 3 -> build/ch03.mp4
    python3 video/render.py all -j 4          # render all chapters in parallel
    python3 video/render.py 3 --sheet         # 16-frame contact sheet of chapter 3
    python3 video/render.py 3 --at 12.5 20    # full-size PNGs at chapter times
"""
import argparse
import importlib
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video.engine.core import W, H, FPS, new_surface, new_ctx  # noqa: E402
from video.engine.scene import TL, finalize, draw_frame, chapter_tag  # noqa: E402
from video import timeline as timeline_mod  # noqa: E402
from video import project as PROJECT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def BUILD():
    return PROJECT.get().build


def PREVIEW():
    d = os.path.join(PROJECT.get().build, "preview")
    os.makedirs(d, exist_ok=True)
    return d

X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "animation",
        "-pix_fmt", "yuv420p", "-g", "60", "-r", str(FPS)]


def load_chapter(ch, tl_all=None):
    tl_all = tl_all or timeline_mod.load()
    tl = TL(tl_all[str(ch)])
    mod = PROJECT.get().chapter(ch)
    shots, sfx = mod.build(tl)
    shots = finalize(shots, tl.dur)
    overlay = None
    if ch > 1:
        overlay = chapter_tag(ch, tl.data["title"], dark=getattr(mod, "DARK_TAG", False))
    return tl, shots, sfx, overlay


def render_chapter(ch, out=None):
    tl, shots, _, overlay = load_chapter(ch)
    n = int(round(tl.dur * FPS))
    out = out or os.path.join(BUILD(), f"ch{ch:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *X264, "-threads", "3", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = new_surface()
    cr = new_ctx(surf)
    t0 = time.time()
    for i in range(n):
        T = i / FPS
        cr.save()
        draw_frame(cr, shots, T, overlay)
        cr.restore()
        surf.flush()
        proc.stdin.write(surf.get_data())
        if i % 300 == 0:
            print(f"ch{ch:02d}: frame {i}/{n} ({time.time() - t0:.0f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"ch{ch:02d}: done {n} frames in {time.time() - t0:.0f}s -> {out}", flush=True)
    return out


def frame_png(ch, T, path, loaded=None):
    tl, shots, _, overlay = loaded or load_chapter(ch)
    surf = new_surface()
    cr = new_ctx(surf)
    draw_frame(cr, shots, T, overlay)
    surf.write_to_png(path)
    return path


def sheet(ch, times=None, cols=4, rows=4, path=None):
    from PIL import Image, ImageDraw
    loaded = load_chapter(ch)
    tl = loaded[0]
    k = cols * rows
    times = times or [tl.dur * (i + 0.5) / k for i in range(k)]
    tw, th = W // cols, H // rows
    out = Image.new("RGB", (W, H), "white")
    surf = new_surface()
    cr = new_ctx(surf)
    for i, T in enumerate(times[:k]):
        cr.save()
        draw_frame(cr, loaded[1], T, loaded[3])
        cr.restore()
        surf.flush()
        im = Image.frombuffer("RGB", (W, H), bytes(surf.get_data()), "raw", "BGRX", 0, 1)
        im = im.resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 70, 22], fill="black")
        d.text((4, 4), f"{T:5.1f}s", fill="white")
        out.paste(im, ((i % cols) * tw, (i // cols) * th))
    path = path or os.path.join(PREVIEW(), f"sheet_ch{ch:02d}.png")
    out.save(path)
    return path


def main():
    PROJECT.pop_project_arg(sys.argv)
    ap = argparse.ArgumentParser()
    ap.add_argument("chapters", nargs="+")
    ap.add_argument("-j", type=int, default=1)
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--from", dest="t_from", type=float)
    ap.add_argument("--to", dest="t_to", type=float)
    ap.add_argument("--at", nargs="*", type=float)
    a = ap.parse_args()
    chs = list(range(1, 11)) if a.chapters == ["all"] else [int(c) for c in a.chapters]
    if a.sheet:
        for ch in chs:
            times = None
            if a.t_from is not None:
                t1 = a.t_to if a.t_to is not None else a.t_from + 16
                times = [a.t_from + (t1 - a.t_from) * i / 15 for i in range(16)]
            print(sheet(ch, times))
        return
    if a.at:
        loaded = load_chapter(chs[0])
        for T in a.at:
            print(frame_png(chs[0], T, os.path.join(PREVIEW(), f"ch{chs[0]:02d}_{T:06.2f}.png"), loaded))
        return
    if a.j > 1:
        with ProcessPoolExecutor(a.j) as ex:
            list(ex.map(render_chapter, chs))
    else:
        for ch in chs:
            render_chapter(ch)


if __name__ == "__main__":
    main()
