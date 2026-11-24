#!/usr/bin/env bash
# Escala x2 (lanczos), nitidez suave y etalonaje parejo (cálido, contraste y saturación leves).
set -euo pipefail
cd "$(dirname "$0")/.."
for f in source/fotos/*.jpg; do
  n=$(basename "$f" .jpg)
  ffmpeg -y -v error -i "$f" -vf "scale=2730:2048:flags=lanczos,unsharp=5:5:0.55:5:5:0,eq=contrast=1.06:saturation=1.10:gamma=0.98,colorbalance=rs=0.02:bs=-0.03:rm=0.02:bm=-0.02:rh=0.02:bh=-0.01,curves=preset=medium_contrast:interp=pchip" -q:v 2 "hf/assets/img/$n.jpg"
done
echo ok
