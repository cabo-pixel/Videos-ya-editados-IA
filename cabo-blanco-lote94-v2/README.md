# Cabo Blanco · Caleta Loma, Lote 94 — v2 «dron» (estilo Cerro Colorado) · 9:16 · 40 s

Las 9 fotos fijas del listing convertidas en tomas tipo dron. La toma del gancho es un clip de imagen→video
generado con IA (Kling 3.0 Pro en Higgsfield). Las otras 8 son movimientos de cámara 2.5D, con paralaje calculado
a partir de un mapa de profundidad (Depth Anything V2). La edición sigue el estilo de la referencia de Cabo Blanco y
cierra con su placa de logo.

**Renders finales:**
- Vertical 9:16 (Reels/TikTok, 1080×1920, 30 fps): `render/CaboBlanco_CaletaLoma_Lote94_v2_dron_9x16_40s.mp4` — proyecto `hf/`
- Horizontal 16:9 (como la referencia, 1920×1080, 29.97 fps): `render/CaboBlanco_CaletaLoma_Lote94_v2_dron_16x9_40s.mp4` — proyecto `hf_h/`

La versión 16:9 usa el mismo clip IA recortado a 16:9 (no gastó créditos), tomas 2.5D con encuadre propio
(`FORMAT=h python3 scripts/03_parallax.py` → `build/clips_h`) y una placa de logo 16:9 reconstruida a partir de
`CB_logo.mp4` (`hf_h/assets/clips/CB_logo_16x9.mp4`, mismo fondo, logo y URL).
Mezcla: `./scripts/05_mix_and_mux.sh render/video_sin_audio_16x9.mp4 render/CaboBlanco_CaletaLoma_Lote94_v2_dron_16x9_40s.mp4`

## Línea de tiempo
| Seg. | Toma | Origen / movimiento | Texto / gráfico |
|---|---|---|---|
| 0–4.5 | Lote de frente → mar | IMG_0188 · **video IA** (Kling 3.0 Pro), vuelo hacia adelante | CALETA LOMA / LOT 94 |
| 4.5–8 | Costa de Palmilla | IMG_0194 · 2.5D: avance + travelling | ONE OF THE LAST OCEANSIDE LOTS |
| 8–12 | Lote, vista amplia | IMG_0196 · 2.5D: avance | Trazo blanco del lote · PALMILLA'S OCEANSIDE CORRIDOR |
| 12–16 | Lote cercano | IMG_0195 · 2.5D: barrido lateral | Trazo · contador **1,832 m2** OF OCEANVIEW LAND |
| 16–20.5 | Lote con el mar al fondo | IMG_0193 · 2.5D: barrido | Trazo · etiqueta en el terreno «45 × 41 M · FLAT · READY TO BUILD» |
| 20.5–24.5 | Lote junto a la calle | IMG_0189 · 2.5D | Callouts: PAVED STREET ACCESS · CFE POWER / CITY WATER |
| 24.5–28 | Lote con el cerro | IMG_0192 · 2.5D | Trazo · callout TRANSPENINSULAR HIGHWAY |
| 28–31.5 | Lote y bahía | IMG_0191 · 2.5D | YOUR CANVAS  YOUR LEGACY |
| 31.5–36 | Lote y bahía de San José | IMG_0190 · 2.5D | LOCATION / ACCESS / VIEWS → OWN THE HORIZON, INQUIRE TODAY · $1,450,000 USD |
| 36–40 | Placa de marca | CB_logo.mp4 (del cliente) | Cabo Blanco Real Estate · caboblanco.mx |

## Volver a renderizar
Requisitos: ffmpeg, Node 22+, Python 3 con `numpy scipy opencv-python-headless pillow transformers torch`.
```bash
python3 scripts/01_depth.py            # mapas de profundidad → build/depth
python3 scripts/02_polygons.py         # detecta el polígono azul del lote → build/polygons.json
python3 scripts/03_parallax.py         # tomas 2.5D con trazos/etiquetas/callouts → build/clips
cp build/clips/*.mp4 hf/assets/clips/
cd hf && npx hyperframes@0.9.86 check && npx hyperframes@0.9.86 render --fps 30 --quality delivery -o ../render/video_sin_audio.mp4 && cd ..
./scripts/05_mix_and_mux.sh            # música + SFX, −14 LUFS, MP4 final
```
El clip IA original está en `source/ia/hook_IMG_0188_kling.mp4`; su versión vertical etalonada está en `hf/assets/clips/s1_hook_IMG_0188_ia.mp4`.
Los movimientos de cámara (centro, barrido, dolly, paralaje, encuadre) y los gráficos sobre el terreno se ajustan en el diccionario `SHOTS` de `scripts/03_parallax.py`.

## Créditos
Music: "Galactic Rap" Kevin MacLeod (incompetech.com) — Licensed under Creative Commons: By Attribution 4.0 —
http://creativecommons.org/licenses/by/4.0/
Los efectos de sonido son síntesis propia, sin licencia de terceros.
