"""King - Chapter 10: The Final Revelation (9:00-10:00)."""
from video.projects.king.chapters._k import *  # noqa: F401,F403
from video.projects.king import script as SCRIPT

DARK_TAG = True
STAR = (0.92, 0.94, 1.0)
PALE = (0.9, 0.9, 1.0)
NF = (0.05, 0.055, 0.10)


def music_plan(tl):
    return K.music(tl, [(0.0, "reflective", "reflective", 70, 0.6), ("c10_05", "wonder", "wonder", 76, 0.65),
                        ("c10_08", "warm", "warm", 80, 0.75)], tail=0.5)


def sky(cr, T, star_a=1.0):
    S.night_sky(cr, T, star_a=star_a)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w
    q1, q2, cta = SCRIPT.END_CARD

    # 1-3b. the sky fills with what a king could have
    marks = [("crown", 420, 300, 110, w("c10_02", "palaces"), "PALACES"),
             ("coin", 760, 210, 90, w("c10_02", "gold"), "GOLD"),
             ("people", 1100, 300, 110, w("c10_02", "army"), "AN ARMY"),
             ("book", 1460, 210, 90, w("c10_03", "schools"), "SCHOOLS"),
             ("house", 1700, 380, 90, w("c10_03", "problems"), "FIX PROBLEMS"),
             ("people", 260, 560, 80, w("c10_03", "millions"), "MILLIONS OF LIVES")]
    t_hero, t_warn = w("c10_03b", "hero"), w("c10_03b", "warning")
    st4 = s("c10_04") - 0.15

    @b.shot(0, "fade", 0.6)
    def sky_fill(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 520):
            sky(cr, T)
            for (shape, x, y, sz, ta, lab) in marks:
                k = ease(prog(T, ta, 1.0))
                if k > 0:
                    K.constellation(cr, shape, x, y, sz, k, T, c=STAR, label=lab)
            kh = ease(prog(T, t_hero, 0.8))
            if kh > 0:
                K.constellation(cr, "star", 1300, 600, 90, kh, T, c=(1.0, 0.9, 0.5), label="A HERO")
            kw_ = ease(prog(T, t_warn, 0.8))
            if kw_ > 0:
                K.constellation(cr, "question", 1650, 650, 80, kw_, T, c=(1.0, 0.55, 0.55), label="OR A WARNING")
            K.small_hero_night(cr, T, CX, 912, acc=("tuft", "crown"))

    for (_, _, _, _, ta, _) in marks:
        b.fx(ta, "sparkle", -14)
    b.fx(t_hero, "chime", -14)
    b.fx(t_warn, "soft_x", -14)

    # 4. impossible choices, temptations, yes-men
    t_ch, t_tm, t_yes = w("c10_04", "impossible"), w("c10_04", "temptations"), w("c10_04", "people who")

    @b.shot(st4, "fade", 0.5)
    def burdens(cr, t, d, T):
        with K.ken(cr, t, d, 1.05, 1.0, CX, 520):
            sky(cr, T, star_a=0.7)
            src(cr, (0.0, 0.0, 0.0), 0.25)
            cr.paint()
            for i, (lab, ta, x, y) in enumerate((("IMPOSSIBLE CHOICES", t_ch, 520, 260), ("ENDLESS TEMPTATIONS", t_tm, 1400, 260),
                                                 ("ONLY HEARING WHAT YOU WANT TO HEAR", t_yes, CX, 470))):
                k = eout(prog(T, ta, 0.6))
                if k > 0:
                    glow(cr, x, y, 260, (0.6, 0.6, 1.0), 0.15 * k)
                    text(cr, lab, x, y, 54, face=FONT_TITLE, c=STAR, a=0.85 * k)
            p = sm.pose("sad", x=CX, s=0.8, fo=0.2, gy=0.4)
            p = sm.on_ground(sm.idle(p, T, 2), 912)
            J = sm.draw(cr, p, ink=PALE, fill=NF, acc=("tuft",))
            P.crown(cr, J["head"][0], J["head"][1] - 52, 0.42 + 0.12 * clamp(prog(T, t_ch, 6.0)))
    b.fx(t_ch, "darkwhoosh", -12)
    b.fx(t_tm, "darkwhoosh", -14)
    b.fx(t_yes, "darkwhoosh", -14)

    # 5-6. not what you take, what you give
    st5 = s("c10_05") - 0.15
    t_take, t_give = w("c10_05", "take"), w("c10_06", "give")

    @b.shot(st5, "fade", 0.5)
    def take_give(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, CX, 560):
            sky(cr, T)
            kg = ease(prog(T, t_give - 0.2, 0.8))
            K.constellation(cr, "heart", CX, 330, 150, kg, T, c=(1.0, 0.75, 0.8))
            J = K.hero(cr, T, CX, 912, "present" if T > t_give - 0.2 else "stand", acc=("tuft", "crown"), face=1, s=0.8,
                       ink=PALE, fill=NF, smile=0.3 + 0.5 * kg, fo=0.2)
            if kg > 0:
                glow(cr, J["hand_f"][0], J["hand_f"][1], 120, (1.0, 0.75, 0.8), 0.5 * kg)
                P.heart(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 20, 0.4 * kg)
        kt = eout(prog(T, t_take - 0.2, 0.4))
        text(cr, "NOT WHAT YOU TAKE...", 500, 600, 56, face=FONT_TITLE, c=STAR, a=kt * (1 - 0.6 * kg))
        if T > t_take:
            partial_line(cr, 200, 600, 800, 600, prog(T, t_take + 0.5, 0.4), 8, RED, a=1 - 0.6 * kg)
        if kg > 0:
            text(cr, "...WHAT YOU GIVE.", 1420, 600, 64, face=FONT_TITLE, c=(1.0, 0.85, 0.5), a=kg)
    b.fx(t_take + 0.5, "scratch", -14)
    b.fx(t_give - 0.2, "shimmer", -10)

    # 7. maybe you'll never wear a crown
    st7 = s("c10_07") - 0.15

    @b.shot(st7, "fade", 0.4)
    def crown_off(cr, t, d, T):
        with K.ken(cr, t, d, 1.15, 1.25, CX, 640):
            sky(cr, T)
            k = ease(prog(T, st7 + 0.3, 1.2))
            J = K.hero(cr, T, CX, 912, "hold" if k < 1 else "stand", acc=("tuft",), face=1, s=0.8, ink=PALE, fill=NF,
                       smile=0.4, fo=0.2)
            hx, hy = J["head"]
            cx_ = lerp(hx, hx + 140, k)
            cy_ = lerp(hy - 52, 905, ein(k))
            P.crown(cr, cx_, cy_, 0.42)
            glow(cr, cx_, cy_, 80, YELLOW, 0.3)
    b.fx(st7 + 1.4, "clank", -16)

    # 8. a little power every day: words, choices, how you treat people
    st8 = s("c10_08") - 0.15
    t_wd, t_cho, t_tr = w("c10_08", "words"), w("c10_08", "choices"), w("c10_08", "treat")

    @b.shot(st8, "fade", 0.5)
    def little_power(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 520):
            sky(cr, T)
            for (shape, x, ta, lab, c) in (("book", 480, t_wd, "YOUR WORDS", STAR), ("star", CX, t_cho, "YOUR CHOICES", STAR),
                                           ("heart", 1440, t_tr, "HOW YOU TREAT PEOPLE", (1.0, 0.75, 0.8))):
                k = ease(prog(T, ta, 1.0))
                if k > 0:
                    K.constellation(cr, shape, x, 330, 110, k, T, c=c, label=lab)
            K.small_hero_night(cr, T, CX, 912, acc=("tuft",), smile=0.6)
            P.crown(cr, CX + 140, 905, 0.42)
    for ta in (t_wd, t_cho, t_tr):
        b.fx(ta, "sparkle", -12)

    # 8b. fairness over favorites, listening over shouting
    st8b = s("c10_08b") - 0.15
    t_fair, t_list, t_well = w("c10_08b", "fairness"), w("c10_08b", "listening"), w("c10_08b", "ruling well")

    @b.shot(st8b, "fade", 0.5)
    def ruling_well(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            sky(cr, T)
            for i, (x, acc) in enumerate(((560, ("ponytail",)), (760, ("cap",)), (1160, ("glasses",)), (1360, ("bun",)))):
                K.person(cr, T, x, 912, "listen" if T < t_well else "cheer", face=1 if x < CX else -1, s=0.7, acc=acc,
                         seed=i, ink=PALE, fill=NF, smile=0.7)
            K.hero(cr, T, CX, 912, "listen" if T < t_well else "wave", acc=("tuft",), face=1, s=0.8, ink=PALE, fill=NF,
                   smile=0.8, fo=0.2)
            for (lab, ta, y) in (("FAIRNESS > FAVORITES", t_fair, 240), ("LISTENING > SHOUTING", t_list, 340)):
                k = eout(prog(T, ta, 0.5))
                if k > 0:
                    text(cr, lab, CX, y, 60, face=FONT_TITLE, c=STAR, a=k)
            if T > t_well:
                kk = ease(prog(T, t_well, 1.0))
                K.constellation(cr, "crown", 1560, 470, 90, kk, T, c=(1.0, 0.9, 0.5), label="RULING WELL")
    b.fx(t_fair, "pop", -14)
    b.fx(t_list, "pop", -14)
    b.fx(t_well, "chime", -10)

    # 9. in that small kingdom...
    st9 = s("c10_09") - 0.15

    @b.shot(st9, "fade", 0.6)
    def small_kingdom(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.12, CX, 700):
            sky(cr, T)
            P.house(cr, 1250, 930, 0.9, lit=1.0, c=(0.15, 0.15, 0.22), roof=(0.25, 0.12, 0.15))
            K.constellation(cr, "crown", 1250, 520, 90, 1.0, T, c=(1.0, 0.9, 0.5))
            K.small_hero_night(cr, T, 860, 912, acc=("tuft",), g="stand", face=1, gx=1.0, gy=-0.6)
            P.crown(cr, 1000, 905, 0.42)
    b.fx(st9 + 0.2, "night", -16, dur=3.0)

    # 10. what kind of ruler would you be? -> ending
    st10 = s("c10_10") - 0.15

    @b.shot(st10, "fade", 0.4)
    def ask(cr, t, d, T):
        with K.ken(cr, t, d, 1.15, 1.35, CX, 640):
            sky(cr, T)
            K.small_hero_night(cr, T, CX, 912, acc=("tuft",), smile=0.5)
            K.constellation(cr, "question", CX, 330, 120, ease(prog(T, st10 + 0.1, 0.8)), T, c=STAR)

    st_end, t_fade, t_quote, t_cta, end_fn = K.finale_ending(tl, "c10_10", q1, q2, cta)
    b.add(st_end, end_fn, "cut")
    b.fx(t_quote, "swell", -10)
    b.fx(t_quote + 0.8, "chime", -12)
    b.fx(t_cta, "pop", -12)
    return b.result()
