"""End-to-end build of "What If You Had 500 IQ?".

    python3 video/build.py              # everything: narration -> audio -> video -> final MP4 -> checks
    python3 video/build.py --assemble   # only concatenate rendered chapters + soundtrack and validate

Output: output/what_if_you_had_500_iq.mp4 (1920x1080, 30 fps, H.264 + AAC, 10:00)
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "output", "what_if_you_had_500_iq.mp4")


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def assemble():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lst = os.path.join(BUILD, "chapters.txt")
    with open(lst, "w") as f:
        for ch in range(1, 11):
            f.write(f"file '{os.path.join(BUILD, f'ch{ch:02d}.mp4')}'\n")
    video = os.path.join(BUILD, "video_only.mp4")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", video])
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video, "-i",
         os.path.join(BUILD, "soundtrack.m4a"), "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
         "-t", "600", "-movflags", "+faststart",
         "-metadata", "title=What If You Had 500 IQ?", OUT])
    return OUT


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,"
                        "r_frame_rate,nb_frames,duration,sample_rate,channels", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def validate(path):
    info = probe(path)
    fmt = info["format"]
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    dur = float(fmt["duration"])
    checks = {
        "duration ~600s": abs(dur - 600) < 0.5,
        "1920x1080": (v["width"], v["height"]) == (1920, 1080),
        "30 fps": v["r_frame_rate"] in ("30/1", "30000/1000"),
        "h264 video": v["codec_name"] == "h264",
        "aac audio": a["codec_name"] == "aac",
        "audio length matches": abs(float(a.get("duration", dur)) - dur) < 0.5,
    }
    print(json.dumps({"duration": dur, "size_MB": round(int(fmt["size"]) / 1e6, 1),
                      "video": {k: v.get(k) for k in ("codec_name", "width", "height", "r_frame_rate", "nb_frames")},
                      "audio": {k: a.get(k) for k in ("codec_name", "sample_rate", "channels", "duration")}},
                     indent=1))
    for k, ok in checks.items():
        print(f"  [{'OK' if ok else 'FAIL'}] {k}")
    # full decode pass catches corrupt frames
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"], capture_output=True, text=True)
    print(f"  [{'OK' if not r.stderr.strip() else 'FAIL'}] decodes cleanly", r.stderr.strip()[:300])
    return all(checks.values()) and not r.stderr.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args()
    if not a.assemble:
        from video import timeline
        timeline.build()
        run([sys.executable, os.path.join(ROOT, "video", "audio", "mix.py")])
        run([sys.executable, os.path.join(ROOT, "video", "render.py"), "all", "-j", str(a.j)])
    out = assemble()
    ok = validate(out)
    print("FINAL:", out, "OK" if ok else "CHECK FAILURES")


if __name__ == "__main__":
    main()
