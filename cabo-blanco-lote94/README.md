# Cabo Blanco · Caleta Loma, Lote 94 — Reel 9:16 de 40 s

Video vertical (1080×1920, 30 fps, 40 s) del lote MLS #26-5012 (Caleta Loma, Lote 94, Palmilla Oceanside, San José del Cabo)
hecho solo con las 9 fotos aéreas del listing, motion graphics de HyperFrames y música libre.

**Render final:** `render/CaboBlanco_CaletaLoma_Lote94_9x16_40s.mp4`

## Estructura
```
source/fotos/        9 fotos originales (Drive / listing, 1365×1024)
hf/                  proyecto HyperFrames (index.html = composición completa)
  assets/img/        fotos etalonadas y escaladas ×2 (generadas por scripts/01)
  assets/fonts/      Cormorant Garamond + Montserrat (Google Fonts, OFL) en local
  assets/audio/      música (Kevin MacLeod, CC BY 4.0)
  assets/vendor/     GSAP 3.15 en local
scripts/
  01_grade_photos.sh escala ×2 + nitidez + etalonaje parejo (ffmpeg)
  02_sfx.py          sintetiza los efectos de sonido alineados a la línea de tiempo
  03_mix_and_mux.sh  mezcla música+SFX, loudnorm −14 LUFS / −1 dBTP, grano y mux final
GUIA_DE_ESTILO.md    guía de estilo
LINEA_DE_TIEMPO.md   segundo → toma → origen → texto
render/              MP4 final
```

## Volver a renderizar
Requisitos: ffmpeg, Node 22+, Python 3 con `numpy` y `scipy` (`pip install numpy scipy`).
```bash
./scripts/01_grade_photos.sh                               # solo si cambian las fotos o el etalonaje
cd hf
npx hyperframes@0.9.86 check                               # debe dar 0 errores
npx hyperframes@0.9.86 snapshot --at 0,4.5,7.8,11,18.5,30.5,36.5
npx hyperframes@0.9.86 render --fps 30 --quality delivery -o ../render/video_sin_audio.mp4
cd ..
./scripts/03_mix_and_mux.sh                                # genera el MP4 final con audio
```
Para editar textos o tiempos: `hf/index.html` (cada escena es un `<div class="clip">` con `data-start`/`data-duration`;
las animaciones están en el `<script>` al final, con tiempos absolutos en segundos). Si mueves un corte, mueve también su
whoosh en `scripts/02_sfx.py`.

## Créditos
Music: "Inspired" Kevin MacLeod (incompetech.com) — Licensed under Creative Commons: By Attribution 4.0 —
http://creativecommons.org/licenses/by/4.0/
