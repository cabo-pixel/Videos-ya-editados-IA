#!/usr/bin/env bash
# v2: música (fade-in 2 s como la referencia, baja en el logo) + SFX → -14 LUFS / -1 dBTP → MP4 final.
set -euo pipefail
cd "$(dirname "$0")/.."
MUSIC="hf/assets/audio/galactic-rap_kevin-macleod.mp3"
VIDEO="render/video_sin_audio.mp4"
OUT="render/CaboBlanco_CaletaLoma_Lote94_v2_dron_9x16_40s.mp4"
mkdir -p build render
ffmpeg -y -v error -ss 0.03 -t 40 -i "$MUSIC" -af "aresample=48000,afade=t=in:st=0:d=2:curve=qsin,volume=1.0,afade=t=out:st=36.2:d=3.8" -ac 2 build/music.wav
python3 scripts/04_sfx.py
ffmpeg -y -v error -i build/music.wav -i build/sfx.wav -filter_complex "[0][1]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" -map "[a]" -t 40 build/premix.wav
J=$(ffmpeg -hide_banner -i build/premix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i build/premix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" build/mix.wav
ffmpeg -y -v error -i "$VIDEO" -i build/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -maxrate 20M -bufsize 40M \
  -pix_fmt yuv420p -profile:v high -movflags +faststart -c:a aac -b:a 320k -ar 48000 -t 40 "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A20 "Summary" | grep -E "I:|Peak:"
echo "$OUT"
