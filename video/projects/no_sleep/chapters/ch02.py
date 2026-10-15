"""No Sleep - Chapter 2: The First Sleepless Night (0:40-1:40)."""
from video.projects.no_sleep.chapters._n import *  # noqa: F401,F403

DARK_TAG = True


def music_plan(tl):
    return K.music(tl, [(0.6, "wonder", "wonder", 84, 0.55), ("c2_02", "playful", "playful", 108, 0.6),
                        ("c2_03", "mystery", "mystery", 70, 0.45), ("c2_04", "wonder", "wonder", 80, 0.55),
                        ("c2_06", "playful", "playful_g", 100, 0.5), ("c2_07", "warm", "warm", 84, 0.65),
                        ("c2_08", "playful", "playful", 104, 0.6), ("c2_09", "uplift", "uplift", 96, 0.7)])


def kitchen_day(cr, T, fy=880):
    S.room(cr, T, wall=(0.96, 0.92, 0.80), floor_c=(0.80, 0.70, 0.55), fy=fy)
    P.window(cr, 900, 330, 380, 300, T, sky=(0.75, 0.88, 1.0))
    rect(cr, 120, 560, 520, 320, fill=(0.85, 0.88, 0.92), stroke=INK, lw=5)
    rect(cr, 100, 540, 560, 30, fill=(0.65, 0.50, 0.38), stroke=INK, lw=5)
    for i in range(3):
        rect(cr, 150 + i * 165, 620, 140, 220, fill=(0.92, 0.94, 0.96), stroke=INK, lw=4)
        circle(cr, 260 + i * 165, 730, 7, fill=INK)
    P.coffee(cr, 300, 540, 0.6, T)


def build(tl):
    b = Builder(tl)
    s, e, w = tl.s, tl.e, tl.w

    @b.shot(0)
    def title_out(cr, t, d, T):
        TITLE(cr, TITLE_T_END + t)

    # 1. night one: everyone goes to bed, you don't
    t_bed, t_dont = w("c2_01", "goes to bed"), w("c2_01", "you don't")

    @b.shot(0.7, "zoom", 0.6)
    def night_one(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 560):
            asleep = T > t_bed
            lights = (1 - prog(T, t_bed, 0.3), 1 - prog(T, t_bed + 0.25, 0.3), 1.0, 1 - prog(T, t_bed + 0.5, 0.3))
            dont = T > t_dont
            house_cutaway(cr, T, lights=lights, fam_sleep=1.0 if asleep else 0.0,
                          hero_g="cheer" if dont else "stand",
                          hero_kw=dict(eye=1.35 if dont else 1.0, smile=1.0 if dont else 0.4, face=-1 if dont else 1))
        text(cr, "NIGHT 1", 300, 215, 76, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, a=eout(prog(T, 1.0, 0.4)))
        if dont:
            chip(cr, "YOU DON'T.", 1440, 300, 54, bg=WHITE, scale=K.pop(T, t_dont))
    b.fx(0.7, "whoosh", -8)
    b.fx(t_bed, "blip", -12)
    b.fx(t_bed + 0.25, "blip", -14)
    b.fx(t_dont, "ding", -8)

    # 2. exciting: clean room, homework, three movies
    st2 = s("c2_02") - 0.15
    t_clean, t_home, t_mov = w("c2_02", "clean"), w("c2_02", "homework"), w("c2_02", "three movies")
    items = ["CLEAN ROOM", "HOMEWORK", "3 MOVIES"]

    @b.shot(st2, "fade", 0.3)
    def busy_night(cr, t, d, T):
        k = prog(T, st2, d)
        with K.ken(cr, t, d, 1.0, 1.04, CX, 560):
            night_room(cr, T, lamp=1.0, win=(330, 330))
            P.clock(cr, 800, 250, 70, k * 3 * 3600, hours=22, minutes=0, speed=1, face=(0.95, 0.94, 0.90))
            nightstand_lamp(cr, 1180, 880, 0.8, on=1.0)
            if T < t_clean:
                nhero(cr, T, 700, 900, "cheer", face=1, ink=INK, fill=WHITE)
                burst(cr, 700, 520, T - st2 - 0.2, n=14, dist=200, c=YELLOW)
            elif T < t_home:
                kk = prog(T, t_clean, t_home - t_clean)
                sw = math.sin(T * 14)
                J = K.hero(cr, T, 640, 900, "hold", face=1, a1f=60 + 25 * sw, a2f=20, a1b=50 + 25 * sw, smile=0.8)
                line(cr, J["hand_f"][0] - 40, J["hand_f"][1] - 60, J["hand_f"][0] + 70 + sw * 30, 896, 7, WOOD)
                rect(cr, 900, 790, 200, 110, fill=(0.85, 0.65, 0.40), stroke=INK, lw=5)
                text(cr, "STUFF", 1000, 845, 30, face=FONT_TITLE)
                for i in range(5):
                    f = clamp(kk * 5 - i)
                    if 0 < f < 1:
                        x0, y0 = 400 + i * 60, 880
                        px, py = lerp(x0, 1000, f), lerp(y0, 780, f) - 220 * math.sin(f * math.pi)
                        mem_card(cr, px, py, ["ball", "book", "star", "test", "pizza"][i], 0.45, i, rot=f * 6)
            elif T < t_mov:
                P.desk(cr, 720, 900, 420)
                P.chair(cr, 560, 900, 1.0)
                p = sm.pose("sit", x=580, face=1, a1f=75, a2f=30, a1b=60, a2b=40, smile=0.5, gy=0.7)
                p["y"] = 900 - 152
                sm.draw(cr, sm.idle(p, T, 2), acc=HERO)
                P.notebook(cr, 760, 735, 0.5, pages=prog(T, t_home, 1.5), t=T)
            else:
                bed2(cr, T, 640, 900, 1.0, ink=INK)
                p = sm.pose("sit", x=520, face=1, a1f=50, a2f=60, a1b=40, a2b=70, smile=0.9)
                p["y"] = 900 - 106
                sm.draw(cr, sm.idle(p, T, 3), acc=HERO)
                P.monitor(cr, 820, 700, 200, 130, screen=lambda c, x, y, w_, h_: (
                    fill_bg(c, (0.25, 0.35, 0.6)),
                    text(c, f"MOVIE {min(3, 1 + int((T - t_mov) / 0.6))}", x + w_ / 2, y + h_ / 2, 30, face=FONT_TITLE,
                         c=WHITE)))
                ellipse(cr, 560, 780, 50, 20, fill=(0.95, 0.85, 0.5), stroke=INK, w=4)
            todo_list(cr, 1560, 540, items, k_items=1.0,
                      k_checks=(prog(T, t_home - 0.3, 0.3) + prog(T, t_mov - 0.3, 0.3) + prog(T, t_mov + 1.2, 0.3)) / 3,
                      title="TONIGHT", w=440, size=44)
        if T < t_clean + 0.3:
            text(cr, "SO EXCITING!", 780, 400, 64, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8,
                 a=eout(prog(T, st2 + 0.2, 0.3)) * (1 - prog(T, t_clean, 0.3)))
    b.fx(st2 + 0.2, "sparkle", -12)
    b.fx(t_clean, "swish", -10)
    b.fx(t_home, "scribble", -12)
    b.fx(t_mov, "pop", -10)
    for tt in (t_home - 0.3, t_mov - 0.3, t_mov + 1.2):
        b.fx(tt, "check", -14)

    # 3. two a.m.: silent house, quiet phone, nobody online
    st3 = s("c2_03") - 0.15
    t_sil, t_ph, t_on = w("c2_03", "silent"), w("c2_03", "phone"), w("c2_03", "online")

    @b.shot(st3, "fade", 0.4)
    def two_am(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, CX, 600):
            night_room(cr, T, lamp=0.0, win=(330, 330))
            bed2(cr, T, 640, 880, 1.25, ink=NI)
            nightstand_lamp(cr, 1100, 880, 0.8, on=0.0, ink=NI)
            digital_clock(cr, 1100, 640, "2:00", 0.6)
            p = sm.pose("phone", x=600, face=1, smile=-0.1, l1f=86, l2f=-86, l1b=80, l2b=-80, gy=0.3)
            p["y"] = 880 - 133 - 22
            J = sm.draw(cr, sm.idle(p, T, 1), ink=NI, fill=NF, acc=HERO)
            glow(cr, J["hand_f"][0] + 10, J["hand_f"][1], 160, (0.5, 0.75, 1.0), 0.5)
            P.phone(cr, J["hand_f"][0] + 14, J["hand_f"][1] - 6, 0.35, T, rot=0.2)
            if T > t_sil:
                text(cr, "shhh...", 860, 380, 56, face=FONT_HAND, bold=True, c=NI, a=prog(T, t_sil, 0.4))
        kp = K.pop(T, t_ph - 0.1)
        if kp > 0:
            names = ["SAM", "MIA", "GRANDMA", "LEO"]
            phone_big(cr, 1500, 540, 0.95 * max(0.01, kp),
                      content=lambda c: contacts(c, names, "ONLINE: 0" if T > t_on else "CHATS", T,
                                                 k=prog(T, t_on - 0.4, 0.8) if T > t_on - 0.4 else 0.0))
            if T < t_on - 0.4:
                text(cr, "0 new messages", 1500, 540, 34, face=FONT_HAND, bold=True, c=GRAY, a=clamp(kp))
    b.fx(t_sil, "night", -16, dur=2.0)
    b.fx(t_ph - 0.1, "pop", -12)
    b.fx(t_on, "soft_x", -12)

    # 4. three a.m.: the city at night
    st4 = s("c2_04") - 0.15
    t_diff = w("c2_04", "different")

    @b.shot(st4, "fade", 0.4)
    def city3(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.06, CX, 600):
            night_street(cr, T, cam=T * 20)
            moon(cr, 1500, 170, 55)
            for x in (250, 950, 1650):
                streetlamp(cr, x, 880, 0.9)
            x = lerp(300, 820, ease(prog(T, st4, t_diff - st4)))
            stop = T > t_diff
            nhero(cr, T, x, 900, "surprised" if stop else "stand", face=1, walk=0 if stop else 0.7, gx=0.6,
                  gy=-0.6 if stop else 0, eye=1.2)
        digital_clock(cr, 1600, 280, "3:00", 0.7)
        text(cr, "AM", 1600, 365, 34, face=FONT_TITLE, c=(1.0, 0.4, 0.35))
        if stop:
            chip(cr, "A DIFFERENT CITY", CX, 980, 52, bg=YELLOW, scale=K.pop(T, t_diff))
    b.fx(st4, "footsteps", -14, dur=2.0)
    b.fx(t_diff, "shimmer", -12)

    # 4b. birds asleep; then the hum of the fridge
    st4b = s("c2_04b") - 0.15
    t_birds, t_hum = w("c2_04b", "birds"), w("c2_04b", "only sound")

    @b.shot(st4b, "fade", 0.3)
    def birds(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.08, CX, 480):
            night_bg(cr, T, 0.9)
            moon(cr, 1600, 200, 60)
            pts = bezier_pts([(-100, 420), (CX, 560), (W + 100, 420)], 30)
            polyline(cr, pts, 5, (0.05, 0.05, 0.08))
            line(cr, 120, 380, 120, 1200, 16, (0.10, 0.08, 0.08))
            line(cr, 1800, 380, 1800, 1200, 16, (0.10, 0.08, 0.08))
            for i, x in enumerate((560, 800, 1060, 1300)):
                k = K.pop(T, st4b + 0.05 + i * 0.12)
                if k <= 0:
                    continue
                yy = 420 + (560 - 420) * (1 - ((x - CX) / (W / 2 + 100)) ** 2)
                bird_sleep(cr, x, yy, 1.0 * max(0.01, k), T + i, branch=False, face=1 if i % 2 else -1)
                zzz(cr, x + 10, yy - 110, T, 0.9, c=NI, seed=i, a=prog(T, t_birds + i * 0.1, 0.3))
        chip(cr, "EVEN THE BIRDS ARE ASLEEP", CX, 900, 52, bg=WHITE, scale=K.pop(T, t_birds + 0.3))
    b.fx(t_birds, "flutter", -16)

    @b.shot(t_hum - 0.15, "cut")
    def fridge_hum(cr, t, d, T):
        with K.ken(cr, t, d, 1.05, 1.15, 1000, 560):
            S.vgrad(cr, (0.10, 0.11, 0.16), (0.05, 0.05, 0.08))
            S.floor(cr, 880, (0.08, 0.08, 0.10), (0.25, 0.25, 0.3), 4)
            glow(cr, 1150, 560, 700, (0.75, 0.90, 1.0), 0.18)
            fridge(cr, 1150, 880, 1.25, T, hum=1.0, c=(0.80, 0.84, 0.90))
            nhero(cr, T, 700, 900, "listen", face=1, gx=0.8, smile=0.2)
            for i, ch in enumerate("HMMMMMM"):
                text(cr, ch, 1150 - 210 + i * 70, 250 + 18 * math.sin(T * 6 + i * 0.8), 64, face=FONT_TITLE,
                     c=(0.70, 0.88, 1.0), a=eout(prog(t, 0.1 + i * 0.05, 0.3)))
        vignette(cr, 0.5)
    b.fx(t_hum - 0.1, "hum", -10, dur=3.0)

    # 5. empty streets, blinking lights, a baker, a nurse
    st5 = s("c2_05") - 0.15
    t_emp, t_blk, t_bak, t_nur = (w("c2_05", "empty"), w("c2_05", "blinking"), w("c2_05", "baker"),
                                  w("c2_05", "nurse"))
    t_shift = w("c2_05", "twelve")
    stops = [(t_emp, 0), (t_blk, 500), (t_bak, 1450), (t_nur, 2450)]

    def cam_at(T):
        x = stops[0][1]
        for (ta, cx_) in stops[1:]:
            x = lerp(x, cx_, ease(prog(T, ta - 0.5, 0.9)))
        return x

    @b.shot(st5, "slide", 0.4)
    def street_tour(cr, t, d, T):
        cam = cam_at(T)
        night_bg(cr, T, 0.8)
        with xform(cr, -cam * 0.3, 0):
            P.skyline(cr, -400, 760, 4200, 380, seed=51, fill=(0.14, 0.15, 0.22), lit=True, t=T)
        with xform(cr, -cam, 0):
            rect(cr, -400, 760, 4800, 120, fill=(0.20, 0.20, 0.25))
            line(cr, -400, 760, 4400, 760, 4, (0.35, 0.35, 0.4))
            rect(cr, -400, 880, 4800, 400, fill=(0.12, 0.12, 0.15))
            for i in range(-2, 30):
                rect(cr, i * 200, 975, 100, 10, fill=(0.85, 0.80, 0.4), a=0.7)
            for x in (300, 1100, 1900, 2700, 3400):
                streetlamp(cr, x, 880, 0.9)
            traffic_light(cr, 1200, 880, 1.0, T)
            # bakery
            building(cr, 2350, 880, 600, 520, c=(0.45, 0.32, 0.25), sign="BAKERY", lit=1.0, T=T, win_rows=2,
                     awn=(0.85, 0.35, 0.25), door=False, seed=3)
            rect(cr, 2120, 650, 300, 180, fill=(1.0, 0.86, 0.55), stroke=INK, lw=5)
            for i in range(4):
                ellipse(cr, 2160 + i * 70, 800, 30, 18, fill=(0.85, 0.55, 0.25), stroke=INK, w=3)
            J = K.person(cr, T, 2560, 900, "hold", face=-1, acc=BAKER, s=0.95, smile=0.7)
            rect(cr, J["hand_f"][0] - 90, J["hand_f"][1] - 12, 120, 14, fill=LIGHT, stroke=INK, lw=3)
            for i in range(3):
                ellipse(cr, J["hand_f"][0] - 70 + i * 40, J["hand_f"][1] - 24, 18, 12, fill=(0.85, 0.55, 0.25),
                        stroke=INK, w=3)
            # hospital
            building(cr, 3350, 880, 700, 600, c=(0.78, 0.80, 0.84), sign="HOSPITAL", sign_c=(1.0, 0.4, 0.4), lit=1.0,
                     T=T, seed=5)
            rect(cr, 3330, 300, 40, 120, fill=RED)
            rect(cr, 3290, 340, 120, 40, fill=RED)
            nx = lerp(3300, 2950, ease(prog(T, t_nur, 3.0)))
            K.person(cr, T, nx, 900, "stand", face=-1, acc=NURSE, walk=0.5 if T > t_nur else 0.0, s=0.95,
                     smile=-0.2, blink=0.5, mo=0.5 * prog(T, t_shift + 0.4, 0.3) * (1 - prog(T, t_shift + 1.3, 0.3)))
            # walker
            nhero(cr, T, 200 + T * 25, 900, "stand", face=1, walk=0.5, s=0.85)
            for (lab, x, ta) in (("EMPTY STREETS", 300, t_emp), ("BLINKING LIGHTS", 1200, t_blk),
                                 ("A BAKER", 2350, t_bak), ("A NURSE", 3200, t_nur)):
                k = K.pop(T, ta)
                if k > 0:
                    chip(cr, lab, x + (0 if lab != "EMPTY STREETS" else 380) - (250 if lab == "A NURSE" else 0), 150, 50, bg=YELLOW, scale=k)
            ks = K.pop(T, t_shift)
            if ks > 0:
                label_dark(cr, "12-HOUR SHIFT: DONE", nx - 60, 480, 40, c=WHITE, bg=(0.15, 0.35, 0.55), scale=ks)
        vignette(cr, 0.35)
    b.fx(st5, "wind", -18, dur=3.0)
    for ta in (t_emp, t_blk, t_bak, t_nur):
        b.fx(ta, "pop", -12)
    b.fx(t_shift + 0.4, "groan", -14)

    # 6. nothing good on TV at 4 a.m.
    st6 = s("c2_06") - 0.15
    t_noth = w("c2_06", "nothing good")

    @b.shot(st6, "fade", 0.3)
    def tv_4am(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.05, 1000, 600):
            S.vgrad(cr, (0.14, 0.15, 0.22), (0.07, 0.07, 0.11))
            S.floor(cr, 880, (0.12, 0.10, 0.12), (0.3, 0.3, 0.35), 4)
            ch = [0, 1, 2, 3, 1, 0][int((T - st6) / 0.75) % 6]
            tv(cr, 1450, 880, 1.15, T, ch=ch)
            digital_clock(cr, 1450, 330, "4:00", 0.5)
            couch(cr, 620, 880, 1.1, c=(0.40, 0.25, 0.30), ink=NI)
            p = sm.pose("sit", x=620, face=1, a1f=60, a2f=20, a1b=-20, a2b=-10, smile=-0.5, brow=-0.3, lean=-14,
                        head=8, gx=1.0)
            p["y"] = 880 - 175
            J = sm.draw(cr, sm.idle(p, T, 2), ink=NI, fill=NF, acc=HERO)
            rrect(cr, J["hand_f"][0] - 8, J["hand_f"][1] - 30, 22, 50, 6, fill=(0.2, 0.2, 0.22), stroke=NI, lw=3)
            glow(cr, 1100, 600, 500, (0.6, 0.75, 1.0), 0.06 + 0.05 * math.sin(T * 8))
        k = K.pop(T, t_noth)
        if k > 0:
            chip(cr, "NOTHING GOOD ON TV", 700, 260, 56, bg=WHITE, scale=k)
    for i in range(6):
        b.fx(st6 + i * 0.75, "clicks", -16)
    b.fx(t_noth, "boing", -14)

    # 7. the first sunrise: weirdly proud
    st7 = s("c2_07") - 0.15
    t_sun, t_proud = w("c2_07", "sunrise"), w("c2_07", "proud")

    @b.shot(st7, "fade", 0.6)
    def sunrise(cr, t, d, T):
        k = ease(prog(T, st7, 4.5))
        with K.ken(cr, t, d, 1.0, 1.06, CX, 640):
            sky_dawn(cr, 0.25 + 0.75 * k, T)
            P.sun(cr, 1350, lerp(820, 470, k), 95, T)
            P.skyline(cr, -100, 860, 2200, 300, seed=8, fill=lerpc((0.12, 0.12, 0.2), (0.45, 0.32, 0.40), k), lit=True,
                      t=T)
            polyline(cr, [(-100, 1200), (-100, 860), (1100, 820), (2100, 900), (2100, 1200)], 6, INK, closed=True,
                     fill=(0.30, 0.22, 0.25))
            proud = T > t_proud
            ink = lerpc(NI, INK, k)
            fill = lerpc(NF, WHITE, k)
            if not proud:
                p = sm.pose("sit", x=600, face=1, a1f=-30, a2f=-10, a1b=-40, smile=0.6, gx=1.0, gy=-0.3)
                p["y"] = 839
                sm.draw(cr, sm.idle(p, T, 1), ink=ink, fill=fill, acc=HERO)
            else:
                K.hero(cr, T, 620, 840, "confident", face=1, ink=ink, fill=fill, smile=1.0)
                burst(cr, 620, 520, T - t_proud, n=16, dist=220, c=YELLOW, dur=0.8)
        if T > t_sun:
            text(cr, "FIRST SUNRISE EVER", 1300, 170, 64, face=FONT_TITLE, c=WHITE, outline=INK, ow=8,
                 a=eout(prog(T, t_sun, 0.4)))
        if proud:
            chip(cr, "WEIRDLY PROUD", 620, 380, 46, bg=YELLOW, scale=K.pop(T, t_proud))
    b.fx(t_sun, "swell", -12, dur=2.5)
    b.fx(t_proud, "ding", -10)

    # 7b. beautiful, and nobody you know is awake
    st7b = s("c2_07b") - 0.15
    t_nob = w("c2_07b", "nobody")

    @b.shot(st7b, "fade", 0.4)
    def nobody(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            sky_dawn(cr, 1.0, T)
            P.sun(cr, 1690, 240, 85, T)
            S.floor(cr, 860, (0.45, 0.55, 0.35), INK, 5)
            for i, (hx, rf) in enumerate(((260, RED), (560, BLUE), (1300, GREEN), (1620, ORANGE))):
                P.house(cr, hx, 860, 1.2, lit=0.0, roof=rf)
                if T > t_nob:
                    zzz(cr, hx + 30, 640, T, 1.1, seed=i, a=prog(T, t_nob + i * 0.12, 0.3))
            J = K.hero(cr, T, 930, 880, "phone", face=1, a1f=120, a2f=30, smile=0.8)
            P.phone(cr, J["hand_f"][0] + 10, J["hand_f"][1] - 30, 0.45, T)
        k = K.pop(T, st7b + 0.4)
        if k > 0:
            with xform(cr, 1330, 520, max(0.01, k)):
                rrect(cr, -250, -70, 500, 140, 26, fill=(0.25, 0.55, 0.95), stroke=INK, lw=5)
                text(cr, "Anyone up?? Look!!", 0, -12, 40, face=FONT_HAND, bold=True, c=WHITE)
                text(cr, "Seen by 0", 160, 46, 24, face=FONT_BOLD, c=WHITE)
        if T > t_nob:
            chip(cr, "NOBODY ELSE IS AWAKE", 760, 200, 52, bg=WHITE, scale=K.pop(T, t_nob))
    b.fx(st7b + 0.4, "ping", -12)
    b.fx(t_nob, "soft_x", -14)

    # 8. family wakes up grumpy; 24 hours awake and fine
    st8 = s("c2_08") - 0.15
    t_yawn, t_24, t_fine = w("c2_08", "yawning"), w("c2_08", "twenty-four"), w("c2_08", "fine")

    @b.shot(st8, "fade", 0.3)
    def family(cr, t, d, T):
        with K.ken(cr, t, d, 1.0, 1.04, CX, 600):
            kitchen_day(cr, T)
            rect(cr, 1150, 720, 560, 22, fill=WOOD, stroke=INK, lw=5)
            line(cr, 1190, 742, 1190, 880, 8, INK)
            line(cr, 1670, 742, 1670, 880, 8, INK)
            for i, (acc, x1, sc) in enumerate(((DAD, 760, 1.0), (MOM, 960, 0.98), (SIS, 560, 0.82))):
                x = lerp(x1 - 700, x1, ease(prog(T, st8 + i * 0.3, 1.6)))
                walking = T < st8 + i * 0.3 + 1.6
                yawn = 0.5 + 0.5 * math.sin(T * 2 + i)
                K.person(cr, T, x, 900, "slump", face=1, acc=acc, s=sc, walk=0.4 if walking else 0.0, seed=i,
                         mo=0.8 * yawn if T > t_yawn else 0.0, blink=0.7, brow=0.9, smile=-0.6)
                if T > t_yawn and i < 2:
                    P.coffee(cr, x + 80 * sc, 900 - 165 * sc, 0.4, T)
            fine = T > t_fine
            K.hero(cr, T, 1430, 900, "confident" if fine else "stand", face=-1, smile=1.0 if fine else 0.5,
                   eye=1.15)
            P.coffee(cr, 1300, 720, 0.45, T, steam=False)
        k24 = K.pop(T, t_24)
        if k24 > 0:
            with xform(cr, 1430, 220, max(0.01, k24)):
                rrect(cr, -250, -60, 500, 120, 20, fill=INK, stroke=WHITE, lw=4)
                text(cr, "AWAKE: 24 HRS", 0, 0, 52, face=FONT_TITLE, c=BONUS)
        if fine:
            text(cr, "...FINE!", 1430, 380, 72, face=FONT_TITLE, c=YELLOW, outline=INK, ow=8, scale=K.pop(T, t_fine))
    b.fx(st8 + 0.3, "footsteps", -16, dur=1.8)
    b.fx(t_yawn, "groan", -12)
    b.fx(t_24, "pop", -10)
    b.fx(t_fine, "ding", -8)

    # 9. a secret extra day hidden inside every night
    st9 = s("c2_09") - 0.15
    t_sec = w("c2_09", "secret")

    def sun_inside(cr):
        k = ease(prog(cr_T[0], t_sec, 1.2))
        radial_lines(cr, 0, -260, cr_T[0], n=24, r0=60, r1=900, c=YELLOW, a=0.25 * k, w=24)
        P.sun(cr, 0, lerp(-200, -420, k), 80 + 20 * k, cr_T[0])

    cr_T = [0.0]

    @b.shot(st9, "fade", 0.4)
    def secret_day(cr, t, d, T):
        cr_T[0] = T
        with K.ken(cr, t, d, 1.0, 1.06, CX, 560):
            night_bg(cr, T, 1.0)
            moon(cr, 300, 220, 70)
            S.floor(cr, 900, (0.10, 0.10, 0.16), (0.3, 0.3, 0.35), 4)
            ko = ease(prog(T, t_sec, 0.6))
            gift_box(cr, CX, 900, 1.15, k_open=ko, T=T, inner=sun_inside)
            nhero(cr, T, 1380, 900, "surprised" if ko > 0.3 else "point", face=-1, smile=0.9, eye=1.2,
                  ink=lerpc(NI, INK, ko * 0.0), fill=NF)
            text(cr, "NIGHT", CX, 720, 50, face=FONT_TITLE, c=WHITE)
        if ko > 0.3:
            text(cr, "A SECRET EXTRA DAY", CX, 200, 80, face=FONT_TITLE, c=YELLOW, outline=INK, ow=10,
                 scale=K.pop(T, t_sec + 0.3))
    b.fx(t_sec, "sparkle", -8)
    b.fx(t_sec + 0.3, "chime", -10)
    return b.result()
