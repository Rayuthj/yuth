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

echo "== 4/4 encode"
ffmpeg -y -framerate 30 -i build/frames/frame_%06d.jpg -i build/soundtrack.wav \
  -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -g 120 \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart -t 600 \
  What_If_You_Lived_1_Trillion_Years.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 What_If_You_Lived_1_Trillion_Years.mp4
