"""Rigged 2D stickman.

A pose is a plain dict. Limb angles are in degrees measured from straight
down; positive values point toward the direction the character faces.
Elbow/knee angles are relative to the parent limb. Arm angles follow the
torso lean; leg angles are absolute.

The hero is always drawn with the same proportions and his hair tuft so he
stays recognizable in every scene.
"""
import math

from .core import (INK, WHITE, YELLOW, RED, BLUE, GRAY, TAU, src, circle, ellipse, polyline,
                   bezier_pts, line, lerp, clamp, group, rrect, xform)

TORSO, NECK, HEAD = 118.0, 9.0, 40.0
UARM, FARM = 64.0, 60.0
THIGH, SHIN = 80.0, 78.0
LEG = THIGH + SHIN

BASE = dict(
    x=960.0, y=700.0, s=1.0, face=1, fo=1.0, lean=0.0, head=0.0,
    a1b=-12.0, a2b=-10.0, a1f=12.0, a2f=10.0,
    l1b=-4.0, l2b=0.0, l1f=4.0, l2f=0.0,
    gx=0.0, gy=0.0, blink=0.0, smile=0.35, mo=0.0, brow=0.0, browy=0.0, eye=1.0,
    lw=7.5, sq=1.0,
)

NUMERIC = [k for k, v in BASE.items() if isinstance(v, float)]

GESTURES = {
    "stand": {},
    "front": dict(fo=0.0, a1f=16, a2f=6, a1b=-16, a2b=-6, l1f=6, l1b=-6),
    "point": dict(a1f=88, a2f=0),
    "point_up": dict(a1f=128, a2f=22, gy=-0.8),
    "point_down": dict(a1f=55, a2f=-10, gy=0.8),
    "wave": dict(a1f=118, a2f=42, smile=0.8),
    "think": dict(a1f=28, a2f=128, head=6, gy=-0.7, gx=0.5, smile=0.0),
    "shrug": dict(a1f=38, a2f=78, a1b=-38, a2b=-78, head=-8, browy=0.6, smile=0.1),
    "cheer": dict(a1f=158, a2f=8, a1b=-158, a2b=-8, smile=1.0, mo=0.55),
    "hips": dict(a1f=38, a2f=-118, a1b=-38, a2b=118),
    "type": dict(a1f=72, a2f=22, a1b=58, a2b=32, gy=0.6),
    "present": dict(a1f=62, a2f=28, a1b=-18, a2b=-12, smile=0.6),
    "facepalm": dict(a1f=34, a2f=138, head=14, smile=-0.3),
    "sad": dict(lean=8, head=16, a1f=4, a2f=2, a1b=-4, a2b=-2, smile=-0.6, brow=-0.7, gy=0.7),
    "sit": dict(l1f=86, l2f=-86, l1b=80, l2b=-80),
    "arms_out": dict(a1f=95, a2f=0, a1b=-95, a2b=0),
    "hold": dict(a1f=55, a2f=45, a1b=48, a2b=52),
    "write": dict(a1f=120, a2f=-10, a1b=-10, a2b=-8),
    "surprised": dict(a1f=40, a2f=110, a1b=-40, a2b=-110, eye=1.35, browy=1.0, mo=0.7, smile=0.0),
    "worried": dict(a1f=20, a2f=100, a1b=-20, a2b=-100, brow=-0.8, smile=-0.4, eye=1.1),
    "slump": dict(lean=22, head=20, a1f=10, a2f=0, a1b=0, a2b=0, smile=-0.5, brow=-0.5, gy=0.8),
    "confident": dict(a1f=38, a2f=-118, a1b=-38, a2b=118, smile=0.9, brow=0.5, head=-6),
    "phone": dict(a1f=24, a2f=150, head=4),
    "listen": dict(a1f=10, a2f=8, a1b=-10, a2b=-8, head=10, smile=0.5),
}


def pose(*gestures, **kw):
    p = dict(BASE)
    for g in gestures:
        p.update(GESTURES[g])
    p.update(kw)
    return p


def mix(p1, p2, t):
    """Blend two poses (numeric fields only)."""
    if t <= 0:
        return dict(p1)
    if t >= 1:
        return dict(p2)
    out = dict(p2)
    for k in NUMERIC:
        out[k] = lerp(p1.get(k, BASE[k]), p2.get(k, BASE[k]), t)
    out["face"] = p1["face"] if t < 0.5 else p2["face"]
    return out


def apply(p, **kw):
    q = dict(p)
    q.update(kw)
    return q


def add(p, **kw):
    """Add offsets to numeric pose fields."""
    q = dict(p)
    for k, v in kw.items():
        q[k] = q.get(k, BASE.get(k, 0.0)) + v
    return q


# ---------------------------------------------------------------- motion
def blink(t, seed=0, every=3.4):
    ph = (t + seed * 1.37) % every
    return clamp(1 - abs(ph - 0.09) / 0.09) if ph < 0.18 else 0.0


def idle(p, t, seed=0, amt=1.0):
    """Breathing, a little sway, and blinking."""
    q = dict(p)
    br = math.sin(t * 2.1 + seed)
    q["lean"] = p["lean"] + br * 1.2 * amt
    q["head"] = p["head"] + math.sin(t * 1.3 + seed * 2) * 2.0 * amt
    q["a1f"] = p["a1f"] + math.sin(t * 2.1 + seed + 0.5) * 2.5 * amt
    q["a1b"] = p["a1b"] - math.sin(t * 2.1 + seed + 0.8) * 2.5 * amt
    q["blink"] = max(p.get("blink", 0.0), blink(t, seed))
    return q


def walk(p, t, speed=1.0, amp=1.0, arms=True):
    """Walk cycle. Returns pose; horizontal travel is the caller's job (stride())."""
    ph = t * TAU * 0.95 * speed
    q = dict(p)
    a = 26 * amp
    q["l1f"] = a * math.sin(ph)
    q["l1b"] = -a * math.sin(ph)
    q["l2f"] = -38 * amp * max(0.0, math.cos(ph)) - 4
    q["l2b"] = -38 * amp * max(0.0, -math.cos(ph)) - 4
    if arms:
        q["a1f"] = -22 * amp * math.sin(ph) + p.get("lean", 0) * 0.3
        q["a1b"] = 22 * amp * math.sin(ph)
        q["a2f"] = 14 + 10 * amp * max(0.0, -math.sin(ph))
        q["a2b"] = 14 + 10 * amp * max(0.0, math.sin(ph))
    q["lean"] = p.get("lean", 0) + 3 * amp
    q["head"] = p.get("head", 0) + 2 * math.sin(ph * 2)
    return q


def run(p, t, speed=1.0, amp=1.0):
    ph = t * TAU * 1.6 * speed
    q = dict(p)
    q["l1f"] = 42 * amp * math.sin(ph) + 8
    q["l1b"] = -42 * amp * math.sin(ph) + 8
    q["l2f"] = -70 * amp * max(0.0, math.cos(ph)) - 15
    q["l2b"] = -70 * amp * max(0.0, -math.cos(ph)) - 15
    q["a1f"] = -48 * amp * math.sin(ph) + 15
    q["a1b"] = 48 * amp * math.sin(ph) + 15
    q["a2f"] = 85
    q["a2b"] = 85
    q["lean"] = p.get("lean", 0) + 14 * amp
    return q


def stride(speed=1.0, s=1.0, amp=1.0):
    """Horizontal speed (px/s) that roughly matches walk() without foot sliding."""
    step = 2 * LEG * math.sin(math.radians(26 * amp)) * s
    return step * 2 * 0.95 * speed * 0.92


def talk(p, t, env=None, amt=1.0):
    """Open the mouth from a loudness value (0..1) or a synthetic flap."""
    q = dict(p)
    if env is None:
        env = 0.5 + 0.5 * math.sin(t * 22) * math.sin(t * 7.3)
    q["mo"] = max(p.get("mo", 0.0), clamp(env * 1.3) * 0.8 * amt)
    return q


# ---------------------------------------------------------------- geometry
def _dir(angle_deg, face):
    a = math.radians(angle_deg)
    return math.sin(a) * face, math.cos(a)


def joints(p):
    s, f = p["s"], p["face"]
    hx, hy = p["x"], p["y"]
    lean = p["lean"]
    lr = math.radians(lean)
    tx, ty = math.sin(lr) * f, -math.cos(lr)
    tl = TORSO * s * p.get("sq", 1.0)
    neck = (hx + tx * tl, hy + ty * tl)
    sh = (hx + tx * tl * 0.86, hy + ty * tl * 0.86)
    ha = math.radians(lean + p["head"])
    hd = (NECK + HEAD) * s
    hc = (neck[0] + math.sin(ha) * f * hd, neck[1] - math.cos(ha) * hd)
    J = dict(hip=(hx, hy), neck=neck, sh=sh, head=hc, ha=ha * f)
    for side in ("f", "b"):
        d1 = _dir(p["a1" + side] + lean, f)
        e = (sh[0] + d1[0] * UARM * s, sh[1] + d1[1] * UARM * s)
        d2 = _dir(p["a1" + side] + p["a2" + side] + lean, f)
        hnd = (e[0] + d2[0] * FARM * s, e[1] + d2[1] * FARM * s)
        J["elbow_" + side], J["hand_" + side] = e, hnd
        J["hand_ang_" + side] = math.atan2(d2[1], d2[0])
        d1 = _dir(p["l1" + side], f)
        k = (hx + d1[0] * THIGH * s, hy + d1[1] * THIGH * s)
        d2 = _dir(p["l1" + side] + p["l2" + side], f)
        ft = (k[0] + d2[0] * SHIN * s, k[1] + d2[1] * SHIN * s)
        J["knee_" + side], J["foot_" + side] = k, ft
        J["foot_dir_" + side] = _dir(p["l1" + side] + p["l2" + side] + 90, f)
    return J


def on_ground(p, gy):
    """Shift the pose vertically so its lowest foot rests on y = gy."""
    J = joints(p)
    low = max(J["foot_f"][1], J["foot_b"][1])
    q = dict(p)
    q["y"] = p["y"] + (gy - low)
    return q


def standing_y(gy, s=1.0):
    return gy - LEG * s


# ---------------------------------------------------------------- drawing
def _rot(hc, ang, dx, dy):
    c, s_ = math.cos(ang), math.sin(ang)
    return hc[0] + dx * c - dy * s_, hc[1] + dx * s_ + dy * c


def draw(cr, p, ink=INK, fill=WHITE, acc=("tuft",), alpha=1.0, feet=True, item=None, glow_c=None,
         face_only=False):
    """Draw a stickman. `acc` lists accessories; `item(cr, J)` draws held props."""
    if alpha <= 0.01:
        return joints(p)
    J = joints(p)
    if face_only:
        with group(cr, alpha):
            _head(cr, J, p, ink, fill, (), p["lw"] * p["s"], face_only=True)
        return J
    s = p["s"]
    lw = p["lw"] * s
    with group(cr, alpha):
        if glow_c is not None:
            from .core import glow
            glow(cr, J["head"][0], (J["head"][1] + J["hip"][1]) / 2, 260 * s, glow_c, 0.35)
        if "cape" in acc:
            _cape(cr, J, p, ink)
        if "labcoat" in acc:
            _labcoat(cr, J, p, ink)
        if "ponytail" in acc:
            _ponytail(cr, J, p, ink, back=True)

        def limb(a, b, c):
            polyline(cr, [a, b, c], lw, ink)

        limb(J["hip"], J["knee_b"], J["foot_b"])
        if feet:
            _foot(cr, J, "b", s, lw, ink)
        limb(J["sh"], J["elbow_b"], J["hand_b"])
        line(cr, J["hip"][0], J["hip"][1], J["neck"][0], J["neck"][1], lw, ink)
        if "tie" in acc:
            _tie(cr, J, p)
        if "badge" in acc:
            _badge(cr, J, p)
        if "bowtie" in acc:
            _bowtie(cr, J, p)
        limb(J["hip"], J["knee_f"], J["foot_f"])
        if feet:
            _foot(cr, J, "f", s, lw, ink)
        _head(cr, J, p, ink, fill, acc, lw)
        if item is not None:
            item(cr, J)
        limb(J["sh"], J["elbow_f"], J["hand_f"])
        circle(cr, J["hand_f"][0], J["hand_f"][1], lw * 0.62, fill=ink)
        circle(cr, J["hand_b"][0], J["hand_b"][1], lw * 0.62, fill=ink)
    return J


def _foot(cr, J, side, s, lw, ink):
    fx, fy = J["foot_" + side]
    dx, dy = J["foot_dir_" + side]
    line(cr, fx, fy, fx + dx * 13 * s, fy + dy * 13 * s, lw, ink)


def _head(cr, J, p, ink, fill, acc, lw, face_only=False):
    hc, ang, s, f = J["head"], J["ha"], p["s"], p["face"]
    r = HEAD * s
    if "hair" in acc:
        _long_hair(cr, J, p, ink)
    if not face_only:
        circle(cr, hc[0], hc[1], r, fill=fill, stroke=ink, w=lw)
    fo = p.get("fo", 1.0)
    off = 11 * fo * f
    ey = (-4 + p["gy"] * 3.5) * s
    egx = p["gx"] * 4.5 * s * (f if fo else 1)
    eye = p["eye"]
    rx, ry = 5.0 * s * eye, 7.6 * s * eye
    bl = clamp(p["blink"])
    sep = 9.5 * s * (1 - 0.18 * fo)
    for k, side in ((-1, "l"), (1, "r")):
        ex, eyy = _rot(hc, ang, off * s + k * sep + egx, ey)
        if bl > 0.75:
            line(cr, ex - rx * 1.1, eyy, ex + rx * 1.1, eyy, max(2.0, lw * 0.45), ink)
        else:
            ellipse(cr, ex, eyy, rx, max(1.0, ry * (1 - bl)), fill=ink, rot=ang)
            if s > 0.35:
                circle(cr, ex + rx * 0.35, eyy - ry * 0.35 * (1 - bl), max(0.8, 1.6 * s), fill=WHITE)
        # brows
        if abs(p["brow"]) > 0.05 or p["browy"] > 0.05:
            # brow > 0: angry (inner end down); brow < 0: worried (inner end up)
            by = ey - (12.5 + 6 * p["browy"]) * s * eye
            cxe = off * s + k * sep + egx
            tilt = p["brow"] * 4.5 * s
            x1, y1 = _rot(hc, ang, cxe - k * 6 * s, by + tilt)
            x2, y2 = _rot(hc, ang, cxe + k * 6 * s, by - tilt)
            line(cr, x1, y1, x2, y2, max(2.0, lw * 0.5), ink)
    if face_only:
        return
    # mouth
    mx, my = off * s * 0.95 + egx * 0.4, 17 * s
    sm, mo = p["smile"], clamp(p["mo"])
    mw = 9.5 * s
    if mo > 0.04:
        h = (3 + 11 * mo) * s
        pts = []
        for i in range(17):
            a = i / 16 * TAU
            pts.append(_rot(hc, ang, mx + math.cos(a) * mw * (0.8 + 0.2 * mo),
                            my + 2 * s + math.sin(a) * h * (1 if math.sin(a) > 0 else 0.35) - sm * 2 * s))
        polyline(cr, pts, max(2.0, lw * 0.45), ink, closed=True, fill=ink)
    else:
        ctrl = [_rot(hc, ang, mx - mw, my - sm * 2.5 * s),
                _rot(hc, ang, mx, my + sm * 8 * s),
                _rot(hc, ang, mx + mw, my - sm * 2.5 * s)]
        polyline(cr, bezier_pts(ctrl, 10), max(2.0, lw * 0.5), ink)
    # accessories on the head
    if "tuft" in acc:
        for c in ([(-3, -39), (-10, -55), (1, -63)], [(5, -39), (7, -52), (17, -55)]):
            pts = [_rot(hc, ang, dx * s * f, dy * s) for dx, dy in c]
            polyline(cr, bezier_pts(pts, 10), lw * 0.8, ink)
    if "glasses" in acc:
        for k in (-1, 1):
            ex, eyy = _rot(hc, ang, off * s + k * sep + egx * 0.3, ey)
            circle(cr, ex, eyy, 10.5 * s, stroke=ink, w=max(2, lw * 0.4))
        a1 = _rot(hc, ang, off * s - sep + 10.5 * s, ey)
        a2 = _rot(hc, ang, off * s + sep - 10.5 * s, ey)
        line(cr, a1[0], a1[1], a2[0], a2[1], max(2, lw * 0.4), ink)
    if "cap" in acc:
        pts = [_rot(hc, ang, math.cos(a) * r * 1.04, -abs(math.sin(a)) * r * 1.04 - 2 * s)
               for a in [math.pi + i * math.pi / 16 for i in range(17)]]
        polyline(cr, pts, lw * 0.6, ink, closed=True, fill=ink)
        b1 = _rot(hc, ang, r * 0.2 * f, -r * 0.18)
        b2 = _rot(hc, ang, (r * 1.55) * f, -r * 0.1)
        line(cr, b1[0], b1[1], b2[0], b2[1], lw * 1.1, ink)
    if "hardhat" in acc:
        pts = [_rot(hc, ang, math.cos(a) * r * 1.08, -abs(math.sin(a)) * r * 1.1 - 6 * s)
               for a in [math.pi + i * math.pi / 16 for i in range(17)]]
        polyline(cr, pts, lw * 0.5, ink, closed=True, fill=YELLOW)
        b1 = _rot(hc, ang, -r * 1.25, -r * 0.18)
        b2 = _rot(hc, ang, r * 1.25, -r * 0.18)
        line(cr, b1[0], b1[1], b2[0], b2[1], lw * 0.9, ink)
    if "beret" in acc:
        ellipse(cr, *_rot(hc, ang, -4 * s * f, -r * 0.92), r * 1.05, r * 0.42, fill=RED, stroke=ink, w=lw * 0.5, rot=ang - 0.2 * f)
    if "bun" in acc:
        circle(cr, *_rot(hc, ang, -r * 0.55 * f, -r * 0.95), r * 0.38, fill=ink)
    if "crown" in acc:
        base = [(-26, -34), (-30, -66), (-14, -50), (0, -72), (14, -50), (30, -66), (26, -34)]
        pts = [_rot(hc, ang, dx * s, dy * s) for dx, dy in base]
        polyline(cr, pts, lw * 0.5, ink, closed=True, fill=YELLOW)
    if "headset" in acc:
        arc(cr, hc[0], hc[1], r * 1.08, math.pi * 1.1, math.pi * 1.9, lw * 0.7, ink)
        circle(cr, *_rot(hc, ang, -r * 0.95 * f, 0), r * 0.25, fill=ink)
    if "ponytail" in acc:
        _ponytail(cr, J, p, ink, back=False)
    if "bearskin" in acc:
        pts = [_rot(hc, ang, dx * s, dy * s) for dx, dy in
               [(-36, -18), (-42, -70), (-30, -110), (0, -122), (30, -110), (42, -70), (36, -18)]]
        polyline(cr, bezier_pts(pts, 20), lw * 0.4, ink, closed=True, fill=ink)
    if "chef" in acc:
        base = [_rot(hc, ang, dx * s, dy * s) for dx, dy in [(-30, -30), (30, -30), (30, -52), (-30, -52)]]
        polyline(cr, base, lw * 0.4, ink, closed=True, fill=WHITE)
        for dx in (-22, 0, 22):
            circle(cr, *_rot(hc, ang, dx * s, -70 * s), 22 * s, fill=WHITE, stroke=ink, w=lw * 0.4)
        polyline(cr, base, 0, ink, closed=True, fill=WHITE)
    if "hat" in acc:
        b1 = _rot(hc, ang, -r * 1.25, -r * 0.55)
        b2 = _rot(hc, ang, r * 1.25, -r * 0.55)
        line(cr, b1[0], b1[1], b2[0], b2[1], lw * 1.1, ink)
        pts = [_rot(hc, ang, dx * s, dy * s) for dx, dy in [(-26, -24), (-22, -62), (22, -62), (26, -24)]]
        polyline(cr, pts, lw * 0.4, ink, closed=True, fill=ink)
    if "beard" in acc:
        pts = [_rot(hc, ang, dx * s * (1 if f > 0 else 1), dy * s) for dx, dy in
               [(-30, 12), (-24, 40), (0, 58), (24, 40), (30, 12), (14, 26), (0, 30), (-14, 26)]]
        polyline(cr, pts, lw * 0.3, ink, closed=True, fill=(0.85, 0.85, 0.85))
    if "mustache" in acc:
        c = _rot(hc, ang, mx, my - 5 * s)
        ellipse(cr, c[0] - 6 * s, c[1], 7 * s, 3 * s, fill=ink, rot=ang + 0.2)
        ellipse(cr, c[0] + 6 * s, c[1], 7 * s, 3 * s, fill=ink, rot=ang - 0.2)


def arc(cr, x, y, r, a1, a2, w, c):
    src(cr, c)
    cr.set_line_width(w)
    cr.new_sub_path()
    cr.arc(x, y, r, a1, a2)
    cr.stroke()


def _ponytail(cr, J, p, ink, back):
    hc, ang, s, f = J["head"], J["ha"], p["s"], p["face"]
    r = HEAD * s
    if back:
        pts = [_rot(hc, ang, dx * s * f, dy * s) for dx, dy in [(-30, -26), (-62, -14), (-66, 22), (-50, 30), (-44, 0)]]
        polyline(cr, bezier_pts(pts, 14), 0, ink, closed=True, fill=ink)
    else:
        pts = [_rot(hc, ang, math.cos(a) * r * 1.02, math.sin(a) * r * 1.02)
               for a in [math.pi * 1.05 + i * math.pi * 0.95 / 14 for i in range(15)]]
        polyline(cr, pts + [_rot(hc, ang, 10 * s * f, -18 * s)], lw_of(p) * 0.4, ink, closed=True, fill=ink)


def _long_hair(cr, J, p, ink):
    hc, ang, s, f = J["head"], J["ha"], p["s"], p["face"]
    r = HEAD * s
    pts = [_rot(hc, ang, math.cos(a) * r * 1.12, math.sin(a) * r * 1.12) for a in
           [math.pi * 0.55 + i * math.pi * 1.6 / 20 for i in range(21)]]
    pts += [_rot(hc, ang, r * 0.9 * -f, r * 1.4), _rot(hc, ang, r * 0.2 * -f, r * 1.2)]
    polyline(cr, pts, 0, ink, closed=True, fill=ink)


def lw_of(p):
    return p["lw"] * p["s"]


def _tie(cr, J, p):
    s = p["s"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    dx, dy = (hx - nx), (hy - ny)
    pts = [(nx + dx * 0.08 - 6 * s, ny + dy * 0.08), (nx + dx * 0.08 + 6 * s, ny + dy * 0.08),
           (nx + dx * 0.55 + 9 * s, ny + dy * 0.55), (nx + dx * 0.62, ny + dy * 0.62),
           (nx + dx * 0.55 - 9 * s, ny + dy * 0.55)]
    polyline(cr, pts, 3 * s, INK, closed=True, fill=RED)


def _badge(cr, J, p):
    s = p["s"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    x, y = lerp(nx, hx, 0.3) + 14 * s * p["face"], lerp(ny, hy, 0.3)
    rrect(cr, x - 13 * s, y - 13 * s, 26 * s, 26 * s, 5 * s, fill=WHITE, stroke=INK, lw=2.5 * s)
    line(cr, x, y - 8 * s, x, y + 8 * s, 5 * s, RED)
    line(cr, x - 8 * s, y, x + 8 * s, y, 5 * s, RED)


def _cape(cr, J, p, ink):
    from .core import RED as _RED
    s = p["s"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    f = p["face"]
    sway = 10 * s * math.sin(p.get("x", 0) * 0.01)
    pts = [(nx - 18 * s * f, ny + 6 * s), (nx + 10 * s * f, ny + 6 * s), (hx - 30 * s * f + sway, hy + 110 * s),
           (hx - 95 * s * f + sway, hy + 100 * s)]
    polyline(cr, pts, 3.5 * s, ink, closed=True, fill=(0.72, 0.08, 0.12))
    line(cr, nx - 24 * s, ny + 6 * s, nx + 24 * s, ny + 6 * s, 9 * s, YELLOW)


def _bowtie(cr, J, p):
    s = p["s"]
    nx, ny = J["neck"]
    x, y = nx, ny + 10 * s
    polyline(cr, [(x, y), (x - 14 * s, y - 8 * s), (x - 14 * s, y + 8 * s)], 2.5 * s, INK, closed=True, fill=RED)
    polyline(cr, [(x, y), (x + 14 * s, y - 8 * s), (x + 14 * s, y + 8 * s)], 2.5 * s, INK, closed=True, fill=RED)


def _labcoat(cr, J, p, ink):
    s = p["s"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    w1, w2 = 22 * s, 36 * s
    pts = [(nx - w1, ny + 8 * s), (nx + w1, ny + 8 * s), (hx + w2, hy + 46 * s), (hx - w2, hy + 46 * s)]
    polyline(cr, pts, 3.5 * s, ink, closed=True, fill=WHITE)
    line(cr, nx, ny + 10 * s, hx, hy + 44 * s, 2.5 * s, ink)


# ---------------------------------------------------------------- characters
HERO = ("tuft",)
FRIEND = ("cap",)
FRIEND2 = ("ponytail",)


def hero(cr, p, **kw):
    kw.setdefault("acc", HERO)
    return draw(cr, p, **kw)
