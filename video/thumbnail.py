"""YouTube thumbnails for "What If You Had 500 IQ?".

    python3 video/thumbnail.py   -> output/thumbnail.png (1280x720) + output/thumbnails/*.png alternates

Rendered at 1920x1080 with the same engine and hero as the film, then
downscaled to YouTube's recommended 1280x720.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from PIL import Image  # noqa: E402

from video.engine.core import *  # noqa: E402,F401,F403
from video.engine import stickman as sm  # noqa: E402
from video.engine import props as P  # noqa: E402
from video.chapters.common import head_at, MATH_SYMBOLS  # noqa: E402

OUT = os.path.join(ROOT, "output")
NAVY = (0.03, 0.05, 0.12)
GOLD_EDGE = (0.30, 0.18, 0.0)


def rays(cr, x, y, n, c, a, w=60, r1=1800, spin=0.0):
    for i in range(n):
        ang = i / n * TAU + spin
        cr.move_to(x, y)
        cr.line_to(x + math.cos(ang - 0.04) * r1, y + math.sin(ang - 0.04) * r1)
        cr.line_to(x + math.cos(ang + 0.04) * r1, y + math.sin(ang + 0.04) * r1)
        cr.close_path()
        src(cr, c, a)
        cr.fill()


def arcs(cr, cx, cy, r, n=9, seed=3, c=CYAN):
    """Electric arcs leaping off the head."""
    g = rng(seed)
    for i in range(n):
        ang = g.uniform(-2.6, -0.5) if i % 3 else g.uniform(0.3, 2.8)
        pts = []
        rr = r * 1.02
        length = g.uniform(0.35, 0.8) * r
        steps = 7
        for k in range(steps + 1):
            d = rr + length * k / steps
            jitter = g.uniform(-0.09, 0.09) if 0 < k < steps else 0
            pts.append((cx + math.cos(ang + jitter) * d, cy + math.sin(ang + jitter) * d))
        polyline(cr, pts, 22, c, 0.18)
        polyline(cr, pts, 9, c, 0.55)
        polyline(cr, pts, 3.5, WHITE, 0.95)


def big_text(cr, s, x, y, size, c, edge, ow=26, rot=0.0, shadow=True):
    if shadow:
        text(cr, s, x + 14, y + 16, size, c=BLACK, a=0.55, face=FONT_TITLE, rot=rot, outline=BLACK, ow=ow)
    text(cr, s, x, y, size, c=c, face=FONT_TITLE, rot=rot, outline=edge, ow=ow)


def genius_face(cr, cx, cy, s, ink=INK, fill=WHITE, smirk=True):
    p = sm.pose("front", s=s, lw=3.4, fo=0.35, face=1, eye=1.45, gx=0.35, gy=-0.1,
                smile=0.75 if smirk else 0.0, mo=0.0, brow=0.55, browy=0.15)
    p = head_at(p, cx, cy)
    return sm.draw(cr, p, ink=ink, fill=fill, acc=("tuft",))


# ---------------------------------------------------------------- concept A: the genius
def concept_a(cr):
    g = __import__("cairo").RadialGradient(620, 560, 50, 620, 560, 1500)
    g.add_color_stop_rgb(0, 0.10, 0.20, 0.42)
    g.add_color_stop_rgb(0.45, 0.04, 0.07, 0.17)
    g.add_color_stop_rgb(1, 0.01, 0.01, 0.03)
    cr.set_source(g)
    cr.paint()
    rays(cr, 600, 560, 28, YELLOW, 0.06)
    floating_symbols(cr, 2.0, MATH_SYMBOLS, 620, 560, 560, 430, size=70, c=WHITE, a=0.35, seed=11, speed=0.2)
    glow(cr, 600, 560, 620, CYAN, 0.35)
    hx, hy, s = 600, 600, 7.2
    r = 40 * s
    arcs(cr, hx, hy, r, n=10, seed=5)
    J = genius_face(cr, hx, hy, s)
    # glowing eyes
    for ex in (-1, 1):
        x = hx + 11 * 0.35 * s + ex * 9.5 * s * (1 - 0.18 * 0.35) + 0.35 * 4.5 * s
        glow(cr, x, hy - 4 * s - 0.1 * 3.5 * s, 95, CYAN, 0.55)
    del J
    # title block
    big_text(cr, "500", 1450, 470, 400, YELLOW, GOLD_EDGE, ow=30, rot=-0.04)
    big_text(cr, "IQ", 1460, 790, 300, WHITE, INK, ow=26, rot=-0.04)
    # red arrow pointing at the head
    pts = bezier_pts([(1180, 1000), (1060, 1010), (985, 880)], 20)
    polyline(cr, pts, 30, RED)
    polyline(cr, [(950, 795), (1035, 880), (935, 905)], 0, RED, closed=True, fill=RED)
    vignette(cr, 0.45)


# ---------------------------------------------------------------- concept B: genius or curse?
def concept_b(cr):
    fill_bg(cr, (1.0, 0.86, 0.35))
    rays(cr, 480, 600, 22, WHITE, 0.35, spin=0.1)
    # right half: dark red chaos
    cr.save()
    cr.move_to(1040, 0)
    cr.line_to(W, 0)
    cr.line_to(W, H)
    cr.line_to(880, H)
    cr.close_path()
    cr.clip()
    vgrad(cr, (0.45, 0.04, 0.07), (0.12, 0.01, 0.02))
    g = rng(7)
    for i in range(18):
        pts = []
        cx_, cy_ = 1440 + g.uniform(-330, 330), 520 + g.uniform(-260, 220)
        for j in range(40):
            a = j * 0.5 + g.uniform(0, 6)
            rr = 30 + j * 4
            pts.append((cx_ + math.cos(a) * rr, cy_ + math.sin(a) * rr * 0.7))
        polyline(cr, pts, 6, RED, 0.55)
    cr.restore()
    polyline(cr, [(1040, 0), (1000, 300), (1060, 520), (960, 760), (880, H)], 26, INK)
    # left: crowned genius
    p = sm.pose("cheer", s=2.05, lw=4.6, smile=1.0, mo=0.5, eye=1.25)
    p = sm.on_ground(p, 1200)
    p["x"] = 480
    sm.draw(cr, p, acc=("tuft", "crown"))
    # right: overwhelmed
    q = sm.pose("worried", s=2.05, lw=4.6, face=-1, eye=1.5, mo=0.6)
    q = sm.apply(q, a1f=150, a2f=60, a1b=-150, a2b=-60, lean=6, head=8)
    q = sm.on_ground(q, 1200)
    q["x"] = 1460
    sm.draw(cr, q, ink=WHITE, fill=(0.25, 0.03, 0.05), acc=("tuft",))
    for i, (x, y, rot) in enumerate(((1220, 420, -0.3), (1750, 400, 0.25), (1230, 760, 0.2), (1770, 760, -0.2))):
        text(cr, "?", x, y, 150, c=RED, face=FONT_TITLE, rot=rot, outline=INK, ow=10)
    big_text(cr, "500 IQ", CX, 150, 200, YELLOW, INK, ow=28, rot=-0.03)
    big_text(cr, "GENIUS", 480, 980, 120, WHITE, INK, ow=18)
    big_text(cr, "OR CURSE?", 1450, 980, 120, WHITE, INK, ow=18)


# ---------------------------------------------------------------- concept C: off the charts
def concept_c(cr):
    vgrad(cr, (0.04, 0.05, 0.14), (0.30, 0.55, 0.92))
    stars(cr, 1.0, n=220, alpha=0.9, area=(0, 0, W, 520))
    base = 1010
    for x, h, lab, col in ((240, 150, "100", BLUE), (520, 230, "145", GREEN)):
        rect(cr, x - 95, base - h, 190, h, fill=col, stroke=INK, lw=10)
        big_text(cr, lab, x, base - h - 70, 90, WHITE, INK, ow=14, shadow=False)
    rect(cr, 760, 470, 230, base - 470, fill=YELLOW, stroke=INK, lw=12)
    glow(cr, 875, 300, 320, YELLOW, 0.5)
    p = sm.pose("cheer", s=1.25, lw=4.5, smile=1.0, mo=0.5, eye=1.2)
    p = sm.on_ground(p, 470)
    p["x"] = 875
    sm.draw(cr, p, ink=INK, fill=WHITE, acc=("tuft",))
    for i in range(10):
        line(cr, 700 + i * 34, 560 + (i % 3) * 110, 700 + i * 34, 760 + (i % 3) * 110, 6, WHITE, 0.35)
    line(cr, 0, base, W, base, 12, INK)
    big_text(cr, "500", 1450, 420, 380, YELLOW, GOLD_EDGE, ow=30, rot=-0.05)
    big_text(cr, "IQ", 1440, 740, 280, WHITE, INK, ow=26, rot=-0.05)
    big_text(cr, "OFF THE CHART", 1440, 960, 92, WHITE, RED, ow=16, rot=-0.05, shadow=False)


def render(fn, path):
    surf = new_surface()
    cr = new_ctx(surf)
    fn(cr)
    surf.flush()
    im = Image.frombuffer("RGB", (W, H), bytes(surf.get_data()), "raw", "BGRX", 0, 1)
    im = im.resize((1280, 720), Image.LANCZOS)
    im.save(path, optimize=True)
    return im


def main():
    os.makedirs(os.path.join(OUT, "thumbnails"), exist_ok=True)
    ims = {}
    for name, fn in (("a_genius", concept_a), ("b_genius_or_curse", concept_b), ("c_off_the_chart", concept_c)):
        ims[name] = render(fn, os.path.join(OUT, "thumbnails", f"thumbnail_{name}.png"))
    ims["a_genius"].save(os.path.join(OUT, "thumbnail.png"), optimize=True)
    # review sheet: each concept at full size and at YouTube's small list size
    sheet = Image.new("RGB", (1280 + 336, 720 * 3), (40, 40, 40))
    for i, im in enumerate(ims.values()):
        sheet.paste(im, (0, i * 720))
        sheet.paste(im.resize((320, 180), Image.LANCZOS), (1288, i * 720 + 8))
        sheet.paste(im.resize((168, 94), Image.LANCZOS), (1288, i * 720 + 200))
    sheet.save(os.path.join(ROOT, "build", "preview", "thumb_review.png"))
    for f in sorted(os.listdir(os.path.join(OUT, "thumbnails"))) + ["../thumbnail.png"]:
        p = os.path.join(OUT, "thumbnails", f)
        print(f, round(os.path.getsize(p) / 1024), "KB")


if __name__ == "__main__":
    main()
