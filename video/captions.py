"""Write subtitles (SRT) and a timestamped narration script from build/timeline.json."""
import json
import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video import project as PROJECT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEAKERS = {"narrator": None, "hero": "YOU", "friend": "SAM", "friend2": "MIA"}


def ts(t, sep=","):
    ms_total = int(round(t * 1000))
    h, rem = divmod(ms_total, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main():
    P = PROJECT.get()
    tl = json.load(open(P.timeline))
    out_dir = P.out
    srt, md = [], [f"# {P.title} — narration script", "",
                   "Timestamps are taken from the final video.", ""]
    n = 1
    starts = [tl[str(c)]["start"] + b["start"] for c in range(1, 11) for b in tl[str(c)]["beats"]] + [1e9]
    for ch in range(1, 11):
        d = tl[str(ch)]
        md += [f"## Chapter {ch}: {d['title']} ({ts(d['start'], '.')[3:8]}–{ts(d['end'], '.')[3:8]})", ""]
        for b in d["beats"]:
            t0, t1 = d["start"] + b["start"], d["start"] + b["end"]
            who = getattr(P.script, "SPEAKER_NAMES", SPEAKERS)[b["voice"]]
            line = f"{who}: {b['text']}" if who else b["text"]
            end = min(t1 + 0.15, starts[n] - 0.02)
            srt += [str(n), f"{ts(t0)} --> {ts(end)}", "\n".join(textwrap.wrap(line, 48)), ""]
            md.append(f"- `{ts(t0, '.')[3:10]}` {'**' + who + ':** ' if who else ''}{b['text']}")
            n += 1
        md.append("")
    S = P.script
    end_lines = getattr(S, "END_CARD", ["INTELLIGENCE IS POWER. WISDOM IS HOW YOU USE IT.",
                                         "If you could ask a 500-IQ mind one question, what would it be?"])
    md += ["## Closing screen", ""] + sum([[f"> {ln}", ""] for ln in end_lines], [])
    words = sum(len(b["text"].split()) for ch in range(1, 11) for b in tl[str(ch)]["beats"])
    md.insert(3, f"Total narration: {words} words.\n")
    open(os.path.join(out_dir, f"{P.name}.srt"), "w").write("\n".join(srt))
    open(os.path.join(out_dir, "narration_script.md"), "w").write("\n".join(md))
    print(f"{n - 1} subtitle cues, {words} words")


if __name__ == "__main__":
    PROJECT.pop_project_arg(sys.argv)
    main()
