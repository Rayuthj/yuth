"""Shared defaults for the series' narration scripts (same 10-chapter, 10-minute format)."""

VOICES = {
    "narrator": "af_heart",
    "hero": "am_michael",
    "friend": "am_puck",
    "friend2": "bf_emma",
    "advisor": "bm_george",
}

SPEAKER_NAMES = {"narrator": None, "hero": "YOU", "friend": "SAM", "friend2": "MIA", "advisor": "ADVISOR"}

SLOTS = [(0, 40), (40, 100), (100, 160), (160, 220), (220, 290), (290, 350), (350, 410), (410, 470), (470, 540),
         (540, 600)]

CHAPTER_TIMING = {
    1: dict(lead=1.2, tail=2.6),
    2: dict(lead=1.0, tail=1.6),
    3: dict(lead=1.0, tail=1.4),
    4: dict(lead=1.0, tail=1.4),
    5: dict(lead=1.0, tail=1.6),
    6: dict(lead=1.6, tail=1.6),
    7: dict(lead=1.0, tail=1.4),
    8: dict(lead=1.0, tail=1.4),
    9: dict(lead=1.0, tail=2.0),
    10: dict(lead=0.8, tail=7.6),
}

TARGET_GAP = {1: 0.30, 2: 0.70, 3: 0.70, 4: 0.75, 5: 0.65, 6: 0.95, 7: 0.70, 8: 0.70, 9: 0.75, 10: 0.55}


def B(id, text, voice="narrator", gap=1.0):
    return dict(id=id, text=text, voice=voice, gap=gap)


def slots(titles):
    return [(i + 1, t, a, b) for i, (t, (a, b)) in enumerate(zip(titles, SLOTS))]


def word_report(beats):
    total = 0
    for ch in sorted(beats):
        n = sum(len(b["text"].split()) for b in beats[ch])
        total += n
        print(f"chapter {ch:2d}: {n:4d} words")
    print("total:", total)
