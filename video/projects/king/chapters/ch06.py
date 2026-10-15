"""King - Chapter 6: The Dark Side of Power (4:50-5:50)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403

DARK_TAG = True
PALE = (0.86, 0.87, 0.90)
NF = (0.12, 0.13, 0.17)


def music_plan(tl):
    return K.music(tl, [(0.0, "dark", "dark", 60, 0.7), ("c6_08", "warm", "warm_d", 72, 0.55)])


def dark_palace(cr, T, k=1.0):
    S.palace(cr, T, warm=0.2)
    src(cr, (0.03, 0.03, 0.06), 0.72 * k)
    cr.paint()


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    # 1. the dark side creeps in
    @b.shot(0, "fade", 0.5)
    def creep(cr, t, d, T):
        k = ease(prog(t, 0.3, d - 0.3))
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            dark_palace(cr, T, k)
            P.throne(cr, CX, 900, 1.2)
            p = sm.pose("sit", x=CX, fo=0.0, a1f=60, a2f=40, a1b=-60, a2b=-40, smile=lerp(0.5, 0.2, k), brow=0.6 * k)
            p["y"] = 730
            sm.draw(cr, sm.idle(p, T, 2), acc=KING, ink=lerpc(INK, PALE, k), fill=lerpc(WHITE, NF, k))
        vignette(cr, 0.6 * k)
    b.fx(0.4, "darkwhoosh", -6)

    # 2. a cartoon in the newspaper
    st2 = s("c6_02") - 0.15
    t_shut = w("c6_02", "shut")

    def cartoon(c):
        p = sm.pose("front", x=0, s=0.55, smile=-0.3, eye=1.4)
        p = sm.on_ground(p, 50)
        sm.draw(c, p, acc=("tuft", "crown"))
        ellipse(c, 12, -100, 30, 16, fill=(1.0, 0.75, 0.6), stroke=INK, w=3)
        text(c, "HIS ROYAL NOSE-NESS", 0, 40, 18, face=FONT_HAND, bold=True)

    @b.shot(st2, "fade", 0.3)
    def paper_shot(cr, t, d, T):
        S.dark_room(cr, T, 960, 200, lamp=False)
        with K.ken(cr, t, d, 1.0, 1.06):
            P2.newspaper(cr, 760, 520, 1.3, headline="THE DAILY TRUTH", rot=-0.05, cartoon=cartoon)
            ks = prog(T, t_shut - 0.3, 0.6)
            if ks > 0:
                with xform(cr, 1400, lerp(80, 360, ease(ks)), 1.2):
                    rect(cr, -120, -40, 240, 80, fill=RED, stroke=INK, lw=5)
                    text(cr, "SHUT DOWN", 0, 0, 40, face=FONT_TITLE, c=WHITE)
                    rect(cr, -30, -160, 60, 120, fill=(0.4, 0.25, 0.15), stroke=INK, lw=4)
        vignette(cr, 0.5)
    b.fx(t_shut, "stamp", -10)

    # 3. a protest outside
    st3 = s("c6_03") - 0.15
    t_army = w("c6_03", "army")

    @b.shot(st3, "fade", 0.3)
    def protest(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            S.city(cr, T, 0, gy=820, night=True, sky=((0.05, 0.06, 0.13), (0.16, 0.16, 0.26)))
            crowd(cr, T, n=26, y0=860, y1=1050, cheer=0.0, ink=PALE, fill=NF,
                  signs=["LISTEN\nTO US", "FAIR\nWAGES", "WE\nMATTER"], x0=-100, x1=1250)
            ka = prog(T, t_army - 0.2, 0.6)
            for i in range(6):
                x = 1350 + i * 110
                K.person(cr, T, x, 1000, "stand", face=-1, s=0.75, acc=GUARD, ink=(0.4, 0.4, 0.45), fill=(0.08, 0.08, 0.1),
                         alpha=ka, a1f=0, a1b=0)
        vignette(cr, 0.5)
    b.fx(st3, "murmur", -12, dur=3.0)
    b.fx(t_army - 0.2, "darkwhoosh", -10)

    # 4. your face everywhere
    st4 = s("c6_04") - 0.15

    def ic_coin(cr, T):
        circle(cr, 0, 0, 110, fill=GOLD, stroke=INK, w=6)
        circle(cr, 0, 0, 92, stroke=(0.55, 0.38, 0.08), w=3)
        cr.save()
        cr.arc(0, 0, 90, 0, TAU)
        cr.clip()
        p = sm.pose("front", x=0, s=1.0, smile=0.5)
        sm.draw(cr, head_at(p, 0, 10), acc=("tuft", "crown"), ink=(0.55, 0.38, 0.08), fill=GOLD)
        cr.restore()
        cr.new_path()

    def ic_poster(cr, T):
        rect(cr, -100, -130, 200, 240, fill=RED, stroke=INK, lw=6)
        cr.save()
        cr.rectangle(-97, -127, 194, 160)
        cr.clip()
        p = sm.pose("front", x=0, s=1.0, smile=0.7)
        sm.draw(cr, head_at(p, 0, -30), acc=("tuft", "crown"))
        cr.restore()
        cr.new_path()
        text(cr, "OUR KING", 0, 75, 32, face=FONT_TITLE, c=WHITE)

    def ic_statue(cr, T):
        P2.statue(cr, 0, 140, 0.55)

    b.add(st4, K.icons("YOUR FACE. EVERYWHERE.", [(ic_coin, "ON EVERY COIN", w("c6_04", "coin")), (ic_poster, "ON EVERY WALL", w("c6_04", "wall")),
                            (ic_statue, "A GIANT GOLDEN STATUE", w("c6_04", "statue"))],
                       bg=(0.10, 0.08, 0.10), title_c=YELLOW, label_c=PALE, y=540, size=1.1, label_size=36, dark=True), "fade", 0.3)
    for wd in ("coin", "wall", "statue"):
        b.fx(w("c6_04", wd), "pop", -10)

    # 4b. so easy; nobody could stop you
    st4b = s("c6_04b") - 0.15

    @b.shot(st4b, "fade", 0.3)
    def alone(cr, t, d, T):
        with K.ken(cr, t, d, 1.2, 1.0, CX, 640):
            dark_palace(cr, T, 1.0)
            K.hero(cr, T, CX, 900, "hips", acc=KING, face=1, fo=0.2, smile=0.5, brow=0.8, ink=PALE, fill=NF, s=0.9)
            text(cr, "NOBODY COULD STOP YOU", CX, 200, 64, face=FONT_TITLE, c=RED, a=eout(prog(T, w("c6_04b", "nobody"), 0.4)))
        vignette(cr, 0.6)
    b.fx(w("c6_04b", "nobody"), "stinger", -8)

    # 5. Lord Acton
    st5 = s("c6_05") - 0.15
    t_q = w("c6_05", "power tends") - 0.5

    @b.shot(st5, "fade", 0.4)
    def acton(cr, t, d, T):
        vgrad(cr, (0.10, 0.09, 0.12), (0.03, 0.03, 0.05))
        with K.ken(cr, t, d, 1.0, 1.08, CX, 480):
            k = K.pop(T, st5 + 0.3)
            with xform(cr, CX, 470, max(0.01, k)):
                rrect(cr, -210, -260, 420, 500, 20, fill=(0.85, 0.80, 0.68), stroke=(0.55, 0.40, 0.12), lw=16)
                rrect(cr, -175, -225, 350, 430, 12, fill=(0.55, 0.48, 0.38), stroke=INK, lw=4)
                cr.save()
                cr.rectangle(-175, -225, 350, 430)
                cr.clip()
                p = sm.pose("front", x=0, s=2.4, smile=0.0, brow=-0.3)
                sm.draw(cr, sm.on_ground(sm.idle(p, T, 3), 650), acc=("beard", "mustache", "bowtie"))
                cr.restore()
                cr.new_path()
            text(cr, "LORD ACTON", CX, 820, 64, face=FONT_TITLE, c=WHITE, a=eout(prog(T, st5 + 0.8, 0.4)))
            text(cr, "Historian  •  1887", CX, 900, 40, face=FONT_HAND, c=YELLOW, a=eout(prog(T, st5 + 1.1, 0.4)))
        vignette(cr, 0.5)
    b.fx(st5 + 0.3, "page", -12)

    b.add(t_q, K.quote(["POWER TENDS TO CORRUPT,", "AND ABSOLUTE POWER", "CORRUPTS ABSOLUTELY."], w("c6_05", "power tends"),
                       author="Lord Acton, 1887", color=RED, size=66), "fade", 0.5)
    b.fx(w("c6_05", "power tends"), "chime", -14)

    # 6. power up, empathy down
    st6 = s("c6_06") - 0.15

    @b.shot(st6, "fade", 0.3)
    def meters(cr, t, d, T):
        S.dark_room(cr, T, 960, 200, lamp=False)
        with K.ken(cr, t, d, 1.0, 1.04):
            text(cr, "SOME RESEARCH SUGGESTS...", CX, 140, 52, face=FONT_TITLE, c=PALE)
            k = ease(prog(t, 0.6, d - 1.0))
            for i, (lab, v, col) in enumerate((("FEELING POWERFUL", lerp(0.3, 0.95, k), YELLOW),
                                              ("NOTICING OTHERS' FEELINGS", lerp(0.8, 0.35, k), CYAN))):
                y = 420 + i * 240
                text(cr, lab, 300, y - 60, 40, face=FONT_TITLE, c=PALE, align="left")
                rrect(cr, 300, y, 1100, 70, 34, fill=(0.2, 0.2, 0.26))
                rrect(cr, 300, y, 1100 * v, 70, 34, fill=col)
            K.hero(cr, T, 1640, 980, "confident" if k > 0.5 else "stand", acc=KING, face=-1, ink=PALE, fill=NF, s=0.85)
        vignette(cr, 0.5)
    b.fx(st6 + 0.6, "rise", -12)

    # 7. the mirror
    st7 = s("c6_07") - 0.15
    t_rec = w("c6_07", "recognize")

    def reflection(cr_, T, k):
        fill_bg(cr_, (0.15, 0.10, 0.12))
        p = sm.pose("front", x=0, s=1.0, fo=0.0, smile=lerp(0.2, 0.9, k), brow=lerp(0.0, 1.0, k), eye=lerp(1.0, 0.8, k))
        p = head_at(sm.idle(p, T, 6), 0, -40)
        sm.draw(cr_, p, acc=("tuft", "crown", "cape"), ink=lerpc(INK, RED, k), fill=lerpc(WHITE, (0.25, 0.05, 0.08), k))

    @b.shot(st7, "fade", 0.4)
    def mirror_shot(cr, t, d, T):
        k = ease(prog(T, t_rec - 0.3, 0.6))
        with K.ken(cr, t, d, 1.0, 1.1, 1100, 520):
            S.dark_room(cr, T, 1100, 160, lamp=False)
            P2.mirror(cr, 1250, 500, 1.3, inner=lambda c: reflection(c, T, k))
            K.hero(cr, T, 640, 900, "surprised" if k > 0.3 else "stand", acc=KING, face=1, ink=PALE, fill=NF, eye=1.0 + 0.3 * k)
        vignette(cr, 0.6)
    b.fx(t_rec - 0.3, "glitch", -8)

    # 8. step away
    st8 = s("c6_08") - 0.3
    t_pen, t_alone = w("c6_08", "pen"), w("c6_08", "newspaper")

    @b.shot(st8, "fade", 0.5)
    def step_away(cr, t, d, T):
        k = ease(prog(t, 0.3, d - 0.5))
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            dark_palace(cr, T, lerp(1.0, 0.35, k))
            P.desk(cr, 1000, 900, 520)
            P2.newspaper(cr, 1000, 700, 0.35, rot=0.1)
            kp = prog(T, t_pen, 0.5)
            line(cr, 1120, 740 + 0 * kp, 1180, 745 + 0 * kp, 6, INK)
            x = lerp(900, 520, ease(prog(T, st8 + 0.4, 1.8)))
            p = sm.walk(sm.pose(x=x, face=-1, smile=0.2), T, 0.8) if T < st8 + 2.2 else sm.pose("stand", x=520, face=1, smile=0.3)
            sm.draw(cr, sm.on_ground(p, 900), acc=KING, ink=lerpc(PALE, INK, k), fill=lerpc(NF, WHITE, k))
            if T > t_alone:
                label_box(cr, "LET IT BE", 1000, 520, 40, c=INK, scale=K.pop(T, t_alone))
        vignette(cr, 0.5 * (1 - k))
    b.fx(t_pen, "thud", -14)
    b.fx(st8 + 0.4, "footsteps", -14, dur=1.8)

    # 9. not strong, just scared
    st9 = s("c6_09") - 0.15
    t_sc = w("c6_09", "scared")

    @b.shot(st9, "fade", 0.3)
    def scared(cr, t, d, T):
        fill_bg(cr, (0.95, 0.94, 0.90))
        vignette(cr, 0.2)
        with K.ken(cr, t, d, 1.0, 1.05):
            text(cr, "A RULER WHO CAN'T HANDLE CRITICISM", CX, 380, 56, face=FONT_TITLE, a=eout(prog(t, 0.1, 0.5)))
            text(cr, "ISN'T STRONG.", CX, 520, 90, face=FONT_TITLE, c=INK, a=eout(prog(T, w("c6_09", "strong"), 0.4)))
            text(cr, "JUST SCARED.", CX, 680, 110, face=FONT_TITLE, c=RED, a=eout(prog(T, t_sc, 0.4)),
                 scale=lerp(1.3, 1.0, eout(prog(T, t_sc, 0.4))))
    b.fx(t_sc, "stamp", -8)
    return b.result()
