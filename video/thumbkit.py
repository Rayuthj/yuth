"""Shared helpers for per-project YouTube thumbnails.

    python3 video/thumbkit.py --project king   -> output/king/thumbnail.png + output/king/thumbnails/*.png

Each project provides video/projects/<slug>/thumbnail.py with CONCEPTS = [(name, draw(cr)), ...];
the first concept becomes thumbnail.png. Drawn at 1920x1080, saved at YouTube's 1280x720.
"""
import importlib
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from PIL import Image  # noqa: E402

from video.engine.core import *  # noqa: E402,F401,F403
from video.engine.core import W, H, TAU, BLACK, WHITE, FONT_TITLE, src, text, new_surface, new_ctx  # noqa: E402
from video import project as PROJECT  # noqa: E402


def rays(cr, x, y, n, c, a, r1=2200, spin=0.0, width=0.04):
    for i in range(n):
        ang = i / n * TAU + spin
        cr.move_to(x, y)
        cr.line_to(x + math.cos(ang - width) * r1, y + math.sin(ang - width) * r1)
        cr.line_to(x + math.cos(ang + width) * r1, y + math.sin(ang + width) * r1)
        cr.close_path()
        src(cr, c, a)
        cr.fill()


def radial(cr, x, y, c0, c1, c2, r=1500):
    import cairo
    g = cairo.RadialGradient(x, y, 40, x, y, r)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(0.45, *c1)
    g.add_color_stop_rgb(1, *c2)
    cr.set_source(g)
    cr.paint()


def big_text(cr, s, x, y, size, c, edge, ow=26, rot=0.0, shadow=True):
    if shadow:
        text(cr, s, x + 14, y + 16, size, c=BLACK, a=0.55, face=FONT_TITLE, rot=rot, outline=BLACK, ow=ow)
    text(cr, s, x, y, size, c=c, face=FONT_TITLE, rot=rot, outline=edge, ow=ow)


def render(fn, path):
    surf = new_surface()
    cr = new_ctx(surf)
    fn(cr)
    surf.flush()
    im = Image.frombuffer("RGB", (W, H), bytes(surf.get_data()), "raw", "BGRX", 0, 1)
    im = im.resize((1280, 720), Image.LANCZOS)
    im.save(path, optimize=True)
    return im


def make(slug):
    P = PROJECT.use(slug) or PROJECT.get()
    mod = importlib.import_module(f"video.projects.{slug}.thumbnail")
    out = P.out
    os.makedirs(os.path.join(out, "thumbnails"), exist_ok=True)
    ims = []
    for name, fn in mod.CONCEPTS:
        ims.append(render(fn, os.path.join(out, "thumbnails", f"thumbnail_{name}.png")))
    ims[0].save(os.path.join(out, "thumbnail.png"), optimize=True)
    sheet = Image.new("RGB", (1280 + 336, 720 * len(ims)), (40, 40, 40))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 720))
        sheet.paste(im.resize((320, 180), Image.LANCZOS), (1288, i * 720 + 8))
        sheet.paste(im.resize((168, 94), Image.LANCZOS), (1288, i * 720 + 200))
    os.makedirs(os.path.join(P.build, "preview"), exist_ok=True)
    review = os.path.join(P.build, "preview", "thumb_review.png")
    sheet.save(review)
    print("thumbnail:", os.path.join(out, "thumbnail.png"))
    print("review:", review)


if __name__ == "__main__":
    PROJECT.pop_project_arg(sys.argv)
    make(os.environ.get("VIDEO_PROJECT", "king"))
