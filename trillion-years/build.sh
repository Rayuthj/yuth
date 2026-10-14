#!/usr/bin/env bash
# Rebuild "What If You Lived for 1 Trillion Years?" from scratch.
#
# Requirements: python3 (numpy, soundfile, kokoro-onnx), node 18+, ffmpeg,
# and a Chromium that Playwright can drive. Kokoro model files are expected in
# ./models (kokoro-v1.0.onnx, voices-v1.0.bin) from
# https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build

echo "== 1/4 narration + timeline"
python3 audio/tts.py

echo "== 2/4 music + mix"
python3 audio/music.py

echo "== 3/4 render frames (1280x720 @ 30fps, two workers)"
(cd render && npm install --no-audit --no-fund >/dev/null)
(cd render && node render.mjs --start 0 --end 9000) &
(cd render && node render.mjs --start 9000 --end 18000) &
wait

echo "== 4/4 encode (two-pass H.264, sized to stay under GitHub's 100 MB limit)"
ffmpeg -y -loglevel error -i build/soundtrack.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 build/soundtrack_norm.wav
X264="-c:v libx264 -preset slower -b:v 1120k -maxrate 3000k -bufsize 6000k -g 300 -keyint_min 30 \
  -x264-params aq-mode=3:aq-strength=0.9:psy-rd=1.0,0.15:deblock=-1,-1:bframes=5:ref=6 -pix_fmt yuv420p"
ffmpeg -y -loglevel error -framerate 30 -i build/frames/frame_%06d.jpg $X264 -pass 1 -passlogfile build/x264 -an -f null -
ffmpeg -y -loglevel error -framerate 30 -i build/frames/frame_%06d.jpg -i build/soundtrack_norm.wav $X264 -pass 2 -passlogfile build/x264 \
  -c:a aac -b:a 128k -ar 48000 -movflags +faststart -t 600 \
  -metadata title="What If You Lived for 1 Trillion Years?" \
  What_If_You_Lived_1_Trillion_Years.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 What_If_You_Lived_1_Trillion_Years.mp4
