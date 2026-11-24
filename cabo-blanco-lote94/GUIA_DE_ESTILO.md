# Guía de estilo · Cabo Blanco (Lote 94, Caleta Loma)

> **Ojo:** no recibimos videos de referencia del cliente. Esta guía es una **propuesta** basada en el material
> (9 fotos aéreas de dron del listing MLS #26-5012), en el segmento (lote de lujo frente al mar en Palmilla, San José del Cabo)
> y en lo habitual en Reels inmobiliarios de lujo de Los Cabos. Con referencias reales se ajusta.

## Estructura y narrativa
- **Hook (0–3 s):** titular ya en pantalla en el frame 0 (sirve de miniatura) + punch-in sobre la foto principal con vista al mar.
  «One of the last Oceanside lots in Palmilla» (sale de la descripción del MLS).
- **Desarrollo:** ubicación (Palmilla) → revelado del lote (pin «LOT 94») → superficie (contador 1,832 m²) → vistas →
  características (chips al beat) → comunidad → aspiracional.
- **Cierre:** precio con contador ($1,450,000 USD + MLS) → transición iris → tarjeta final de marca con CTA y contacto.

## Ritmo
- Música a 120 BPM: beat = 0.5 s, compás = 2 s. **Todos los cortes caen en beat**; tomas de 3–4 s (solo hay 9 fotos y no se repiten),
  con un evento animado nuevo cada 0.5–1 s para que el ritmo se sienta de 1–2 s.
- Sin voz → sin pausas musicales; la música va a nivel completo.

## Transiciones (variadas, todas rápidas: 0.2–0.7 s)
Whip con desenfoque direccional · zoom-through · foto a sangre que se encoge a tarjeta · push lateral dentro de la tarjeta ·
barrido vertical con máscara · tarjeta que se expande a pantalla completa · flash blanco · tarjeta que entra con giro y rebote · iris circular.

## Gráficos y texto
- Texto alineado a la izquierda (x = 120 px), estilo editorial, siempre dentro de la zona segura común TikTok/Reels/Shorts
  (y 288–1248, x 120–888; ≤ 780 bajo y 840).
- Revelado por máscara (línea sube desde abajo, `expo.out`), filetes dorados que se dibujan, letras escalonadas (PALMILLA, CABO BLANCO),
  contadores numéricos, chips con iconos lineales, pin con onda pulsante.
- Fotos con el polígono del lote → layout «tarjeta» (960×780, radio 26 px, filete arena) sobre la misma foto desenfocada + tinte navy,
  para que el polígono entero quepa en 9:16.

## Tipografía y paleta
- Titulares: **Cormorant Garamond** 600 / 500 itálica (serif de lujo).
- Etiquetas y datos: **Montserrat** 500–700, etiquetas en mayúsculas con tracking 0.3 em.
- Paleta: navy `#0C2535` / `#123548`, arena `#E6CF9F` (acento), blanco `#FFFFFF`. Mar y cielo de las fotos aportan el azul.

## Color y look
- Etalonaje parejo en las 9 fotos (ffmpeg): escalado ×2 lanczos + unsharp suave, contraste +6 %, saturación +10 %,
  curva medium contrast, sombras/medios ligeramente cálidos y altas luces neutras.
- Degradado navy arriba (legibilidad), viñeta suave y grano fino temporal en el render final.

## Audio
- Música: «Inspired» – Kevin MacLeod (incompetech.com), CC BY 4.0, 120 BPM, optimista/aspiracional.
- SFX sintetizados (sin licencia de terceros): impacto en el hook y en el logo, whoosh en cada corte, pops en pin/chips/tags, brillo en el flash y el precio.
- Master: −14 LUFS integrado, pico verdadero < −1 dBTP, fade-out de 3 s.

## Tarjeta final / CTA
Fondo navy con líneas de ola animadas → wordmark «CABO BLANCO» (letras que se juntan) → «NEWPORT» → filete →
«Schedule your private showing» → teléfono y correo con iconos → fundido a negro.
