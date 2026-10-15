# Authoring a "What If" video (series engine guide)

Each video is a *project* under `video/projects/<slug>/`:

```
script.py            narration (BEATS), TITLE, FILE_NAME, END_CARD, CHAPTER_SLOTS  -- narration is final; TTS is cached
thumbnail.py         CONCEPTS = [(name, draw(cr)), ...]  (first one = main thumbnail)
chapters/_x.py       project-wide helpers (accessory tuples, small props, title card)  -- see king/chapters/_k.py
chapters/chNN.py     build(tl) -> b.result(); music_plan(tl); optional DARK_TAG = True (chapter tag in light ink)
```

Reference implementation: `video/projects/king/` (all 10 chapters). Copy its patterns.

Do not edit the narration text: the timeline (`build/<slug>/timeline.json`) was synthesized from it.

## Commands

```
python3 video/render.py --project <slug> 4 --sheet      # 16-frame contact sheet -> build/<slug>/preview/sheet_ch04.png
python3 video/render.py --project <slug> 4 --at 12.5 30 # full-size PNG frames (chapter time, seconds)
python3 video/qc_sweep.py --project <slug> [chapters]   # draws every 0.25 s: exceptions + long near-blank stretches
python3 video/thumbkit.py --project <slug>              # thumbnails -> output/<slug>/, review sheet in build/<slug>/preview/
```

Full renders, the audio mix and assembly are run separately (`render.py all`, `audio/mix.py`, `build.py --assemble`).

## Time

`tl` (video/engine/scene.py `TL`): chapter-local seconds.
- `tl.s(beat_id)` / `tl.e(beat_id)` start / end of a beat's narration; `tl.dur` chapter length.
- `tl.w(beat_id, "words")` estimated time a word is spoken (case-insensitive substring of the beat text;
  raises KeyError if absent, so copy words exactly from the script).
- `tl.env(beat_id, T)` narration loudness 0..1 (lip-sync).

Convention: a shot for a beat starts at `s(beat) - 0.15`. Give every beat its own shot (or a clear visual change).
Something meaningful must be on screen within ~0.3 s of a shot starting: never leave a background alone for seconds
waiting for a word (a title or the main prop should be visible immediately; reveal details on words).

## Builder (video/chapters/common.py)

```python
b = Builder(tl)

@b.shot(start, "fade", 0.3)          # transitions: cut fade black white iris slide wipe zoom
def name(cr, t, d, T):               # t = time in shot, d = shot duration, T = chapter time
    ...

b.add(start, K.icons(...), "fade", 0.3)   # register a template draw fn(cr, t, d, T)
b.fx(T, "pop", -10, dur=2.0)              # sound effect at chapter time T, gain dB (names must be in the SFX list)
return b.result()
```

`music_plan(tl)` returns `K.music(tl, [(start_seconds_or_beat_id, style, prog, bpm, intensity 0..1), ...])`.
- styles: mystery dark cold discovery uplift playful wonder warm reflective
- progs: mystery discovery discovery_g playful playful_g uplift dark wonder warm warm_d reflective cold
- ch10 uses `tail=0.5`.

## Drawing

Frame is 1920x1080 (`W`, `H`, `CX`, `CY`). Draw sets/characters inside the camera:

```python
with K.ken(cr, t, d, 1.0, 1.05, fx, fy):    # slow zoom z0 -> z1 toward (fx, fy)
    S.palace(cr, T)                           # sets: room city park field dark_room night_sky palace castle village
    K.hero(cr, T, x, 900, "point", ...)       #       space blueprint office floor(cr, y, color)
text(cr, ...)                                 # screen-space overlays outside the camera
```

Characters (video/engine/kit.py):
- `K.person(cr, T, x, ground_y, gesture="stand", face=1|-1, s=1.0, acc=(...), seed=0, ink=INK, fill=WHITE,
  walk=0.0 (speed), talk=None|0..1, alpha=1.0, y=None (hip y instead of ground), **pose_kw)` -> joints dict
  (`J["head"]`, `J["hand_f"]`, `J["hand_b"]`, ...). `K.hero(...)` = person with acc default `("tuft",)`.
- gestures: stand front point point_up point_down wave think shrug cheer hips type present facepalm sad sit
  arms_out hold write surprised worried slump confident phone listen
- pose kw: smile (-1..1) brow (-1..1) eye (size, 1 = normal) gx gy (gaze) lean head (degrees) fo (0 = facing camera)
  a1f a2f a1b a2b (arm angles) mo (mouth open)
- accessories: tuft hair cap hat beret bun ponytail glasses mustache beard tie bowtie badge headset labcoat hardhat
  chef crown cape bearskin
- Low level: `p = sm.pose("sit", x=..., face=1, s=..); p = sm.on_ground(sm.idle(p, T, seed), ground_y)` or
  `p["y"] = hip_y`; `sm.draw(cr, p, ink=, fill=, acc=)`. `head_at(p, x, y)` (from video.chapters.common) puts the head
  at a point (body hangs below -- clip it if you only want a head).

Shot templates (kit, each returns fn(cr, t, d, T); times are chapter seconds):
- `K.icons(title, [(draw(cr, T), label, t_appear), ...], bg=PAPER, title_c, label_c, y=520, size=1.0, label_size=40,
  dark=False)` -- icons drawn at origin, about +-120 px; labels at +150*size. With 4 items keep labels <= ~14 chars.
- `K.big_number(value, t_in, label=None, sub=None, t_sub=None, color=YELLOW, glow_c=None)`
- `K.split(dict(title, bg, ink, draw(cr, cx, T)), dict(...), t_right)` -- left/right comparison with torn edge
- `K.checklist(title, items, ...)`, `K.bars(title, values, labels, t0, ...)`
- `K.timeline(title, [(label ("\n" for 2 rows), t, icon(cr, T) or None), ...], t0, y=640, x0=220, x1=1700)`
- `K.quote(lines, t_in, author=None, color=YELLOW, size=72)` -- dark quote card
- `K.three_paths([(label, color, draw(cr, T) in a 520x600 panel, t), x3], title=None)`
- `K.dialogue(tl, setting(cr, T), cast=[dict(x, gy, acc, face, g, talk_g, s)], lines=[(cast_i, text, beat_id,
  (bubble_x, bubble_y) or None)], zoom=(1.0, 1.05), focus=(CX, CY))` -- lip-synced speakers with speech bubbles;
  use for every beat voiced by a character (voice != narrator)
- `K.title_card(top, big, color, symbols=[...], big_size)` -> fn(cr, t): the chapter-1 title; see king ch01/ch02
- `K.real_question(t0)`, `K.eyes_awaken(...)`
- ch10: `K.constellation(cr, shape, cx, cy, size, k 0..1, T, c, label)` (shapes: heart clock crown star house people
  tree hourglass book moon coin question), `K.small_hero_night(cr, T, x, 912, acc=...)`, and
  `st, t_fade, t_quote, t_cta, fn = K.finale_ending(tl, last_beat, *script.END_CARD)` then `b.add(st, fn, "cut")`
  plus fx swell/chime/pop (see king ch10).
- `K.pop(T, t)` 0 -> overshoot -> 1 scale for pop-ins (use `max(0.01, k)` inside xform).

Core (video/engine/core.py): `text(cr, s, x, y, size, c=INK, a=1, face=FONT_TITLE|FONT_BOLD|FONT_HAND|FONT_SERIF,
align="center"|"left"|"right", bold, outline=None, ow=6, rot, scale)`, `label_box(cr, s, x, y, size, c, bg, scale)`,
`speech_bubble(cr, x, y, w, h, tail_x, tail_y, fill, scale)`, `thought_bubble`, `rect`, `rrect`, `circle`, `ellipse`,
`line`, `polyline(pts, w, c, closed, fill)`, `partial_line(..., p)`, `partial_poly(pts, p, w, c)`, `arc`, `arrow`,
`check`, `cross`, `stamp(cr, s, x, y, t_since, ...)`, `glow(cr, x, y, r, c, a)`, `vignette(cr, k)`, `vgrad(cr, top, bottom)`,
`fill_bg`, `stars`, `burst`, `radial_lines`, `floating_symbols`, `group(cr, alpha)` (context), `xform(cr, x, y, s,
rot, sx, sy)` (context), `camera`, `prog(T, t0, dur)`, `ease`, `eout`, `ein`, `back`, `clamp`, `lerp`, `lerpc`,
`rng(seed)`, `shake(t, amp)`. Colors: INK WHITE BLACK PAPER LIGHT MID GRAY RED BLUE CYAN YELLOW GREEN ORANGE PURPLE.

Props: `P.*` (video/engine/props.py: clock alarm_clock bed window skyline bookshelf phone book desk chair monitor
chalkboard flask lightbulb gear atom brain globe tree bush sun cloud door coffee notebook crown house tower
question_mark magnifier heart dna car telescope robot bell_curve checklist bar_chart galaxy road scale_balance shop
throne hill ...) and `P2.*` (video/engine/props2.py: carriage pillow_crown press_camera pie_chart ice_cream gauge coin
coin_pile money_stack factory cracked_ground newspaper sign statue mirror bus market_stall parchment gavel ballot_box
museum_case book_big hourglass horse cheese pigeon sandwich spreadsheet). Read the function for exact arguments.
Put new props for one video in that project's `chapters/_x.py`, not in the shared engine files.

## Gotchas (each of these produced a real bug)

- Chapters 2-10 show a chapter tag top-left for the first ~3 s: keep big titles in the first shot at y >= 190.
- Clipping: `cr.save(); cr.rectangle(...); cr.clip(); ...; cr.restore(); cr.new_path()`.
- Pop-in text belongs inside the same `xform` as its bubble/box so they scale together.
- Two texts at the same spot cross-fading look like a smear: move the old one away / fade it out first.
- Long labels collide: measure (about 0.55 * size px per character for FONT_TITLE caps); shorten or use 2 rows.
- Characters are ~330 px tall at s=1 (ground to head top ~ 330*s); don't place text where heads/bodies are.
- Mouth decorations drawn at fixed offsets miss the face (faces turn); use bubbles/icons instead.
- Big statues/props must fit under titles; check every sheet frame, then spot-check the frames between with --at.
- New SFX names must already exist (list below). Unknown names crash the mix.

SFX: alarm alert alien applause bell birds blink blip blips boing bonk boom boom_soft bubbles bulb bump buzz camera
chalk chaos charge check cheer chime clank clap clicks coins crack crash crowd dance darkwhoosh data dial ding dissolve
door draw drone erase fastforward flutter footsteps glitch groan gulp hammer heartbeat hit honk hum knock laugh machine
marker murmur network night page papers ping pop pour predict rise riser roll scan scratch scratch_out scribble servo
shatter shimmer slam slowmo snap snore soft_x space sparkle stamp static stinger strain success swell swish swoosh
thud tick toaster tock traffic typing ufo whoosh wind xray zap

## Style

Black-and-white stickmen (ink on white, or pale ink on dark fill for night scenes) with color only for props, sets
and accents. Friendly, funny, clear. Hedge scientific claims exactly as the narration does. Every chapter ends with
a beat that lands (a punchline, a stamp, a reveal).
