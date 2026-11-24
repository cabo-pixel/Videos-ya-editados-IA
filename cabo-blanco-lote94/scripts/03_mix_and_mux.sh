#!/usr/bin/env bash
# Mezcla música + SFX, normaliza a -14 LUFS / -1 dBTP (loudnorm en dos pasadas),
# añade grano fino al video y une todo en el MP4 final.
set -euo pipefail
cd "$(dirname "$0")/.."
MUSIC="hf/assets/audio/inspired_kevin-macleod.mp3"
VIDEO="render/video_sin_audio.mp4"
OUT="render/CaboBlanco_CaletaLoma_Lote94_9x16_40s.mp4"
mkdir -p build render

# 1) música: arranca en el primer beat (0.03 s), 40 s, fade-in corto y fade-out de 3 s al cierre
ffmpeg -y -v error -ss 0.03 -t 40 -i "$MUSIC" -af "aresample=48000,afade=t=in:st=0:d=0.05,afade=t=out:st=37:d=3" -ac 2 build/music.wav

# 2) SFX sintetizados
python3 scripts/02_sfx.py

# 3) mezcla (música base, SFX encima). Sin voz: la música va a nivel completo.
ffmpeg -y -v error -i build/music.wav -i build/sfx.wav -filter_complex \
  "[0]volume=0.85[m];[1]volume=1.0[s];[m][s]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" -map "[a]" -t 40 build/premix.wav

# 4) loudnorm dos pasadas → -14 LUFS, -1 dBTP
J=$(ffmpeg -hide_banner -i build/premix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -v error -i build/premix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" build/mix.wav

# 5) video: grano fino temporal + mux con AAC 320k
ffmpeg -y -v error -i "$VIDEO" -i build/mix.wav -map 0:v -map 1:a \
  -vf "noise=alls=2:allf=t" -c:v libx264 -preset slow -crf 18 -maxrate 20M -bufsize 40M -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 320k -ar 48000 -t 40 "$OUT"

echo "Medición final:"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary" | grep -E "I:|Peak:|dBFS"
echo "$OUT"
