"""Write subtitles (SRT) and a timestamped narration script from build/timeline.json."""
import json
import os
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEAKERS = {"narrator": None, "hero": "YOU", "friend": "SAM", "friend2": "MIA"}


def ts(t, sep=","):
    ms_total = int(round(t * 1000))
    h, rem = divmod(ms_total, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main():
    tl = json.load(open(os.path.join(ROOT, "build", "timeline.json")))
    out_dir = os.path.join(ROOT, "output")
    srt, md = [], ["# What If You Had 500 IQ? — narration script", "",
                   "Timestamps are taken from the final video.", ""]
    n = 1
    starts = [tl[str(c)]["start"] + b["start"] for c in range(1, 11) for b in tl[str(c)]["beats"]] + [1e9]
    for ch in range(1, 11):
        d = tl[str(ch)]
        md += [f"## Chapter {ch}: {d['title']} ({ts(d['start'], '.')[3:8]}–{ts(d['end'], '.')[3:8]})", ""]
        for b in d["beats"]:
            t0, t1 = d["start"] + b["start"], d["start"] + b["end"]
            who = SPEAKERS[b["voice"]]
            line = f"{who}: {b['text']}" if who else b["text"]
            end = min(t1 + 0.15, starts[n] - 0.02)
            srt += [str(n), f"{ts(t0)} --> {ts(end)}", "\n".join(textwrap.wrap(line, 48)), ""]
            md.append(f"- `{ts(t0, '.')[3:10]}` {'**' + who + ':** ' if who else ''}{b['text']}")
            n += 1
        md.append("")
    md += ["## Closing screen", "", "> INTELLIGENCE IS POWER. WISDOM IS HOW YOU USE IT.", "",
           "> If you could ask a 500-IQ mind one question, what would it be?", ""]
    words = sum(len(b["text"].split()) for ch in range(1, 11) for b in tl[str(ch)]["beats"])
    md.insert(3, f"Total narration: {words} words.\n")
    open(os.path.join(out_dir, "what_if_you_had_500_iq.srt"), "w").write("\n".join(srt))
    open(os.path.join(out_dir, "narration_script.md"), "w").write("\n".join(md))
    print(f"{n - 1} subtitle cues, {words} words")


if __name__ == "__main__":
    main()
