"""Sintetiza la pista de efectos de sonido (whooshes, impactos, pops) alineada a la línea de tiempo.

Salida: build/sfx.wav (48 kHz, estéreo, 40 s). Todo es síntesis propia → sin problemas de licencia.
Uso: python3 scripts/02_sfx.py
"""
import os
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 40.0
rng = np.random.default_rng(94)  # semilla fija → render reproducible
out = np.zeros((int(SR * DUR), 2))


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    n = min(len(sig), len(out) - i)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    out[i:i + n, 0] += sig[:n] * gain * l * 1.41
    out[i:i + n, 1] += sig[:n] * gain * r * 1.41


def whoosh(length=0.55, f0=300, f1=3500, peak=0.7):
    n = int(length * SR)
    noise = rng.standard_normal(n)
    y = np.zeros(n)
    blk = 512
    for s in range(0, n, blk):  # banda que sube de f0 a f1 (barrido)
        p = s / n
        fc = f0 * (f1 / f0) ** p
        sos = butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        y[s:s + blk] = sosfilt(sos, noise[max(0, s - 2048):s + blk])[-len(y[s:s + blk]):]
    t = np.linspace(0, 1, n)
    env = np.where(t < peak, (t / peak) ** 2.5, np.exp(-(t - peak) / (1 - peak) * 4))
    y = y * env
    return y / (np.abs(y).max() + 1e-9)


def impact(length=1.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 75 * np.exp(-t * 3) + 38
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    click = sosfilt(butter(2, 2500, btype="high", fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t * 60) * 0.4
    y = body + click
    return y / np.abs(y).max()


def pop(freq=900, length=0.12):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38)
    return y / np.abs(y).max()


def shimmer(length=0.9):
    n = int(length * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t) for f in (1568, 2093, 2637, 3136)) * np.exp(-t * 5)
    y *= np.minimum(1, t / 0.02)
    return y / np.abs(y).max()


# --- línea de tiempo (s) ---
place(impact(), 0.0, 0.55)
for cut, pan in [(3.0, -0.4), (6.0, 0.0), (9.0, -0.5), (12.5, 0.3), (16.0, 0.0), (23.0, 0.2), (27.0, 0.5)]:
    w = whoosh()
    place(w, cut - 0.55 * 0.7, 0.32, pan)  # pico del whoosh justo en el corte
place(whoosh(0.5, 600, 6000), 19.5 - 0.35, 0.22)  # flash
place(shimmer(), 19.45, 0.10)
place(whoosh(0.8, 2500, 200, 0.4), 32.5 - 0.32, 0.30)  # iris (barrido descendente)
place(impact(1.6), 33.0, 0.35)  # logo
place(pop(1000), 6.9, 0.16)  # pin
place(pop(1250), 7.1, 0.14)  # etiqueta LOT 94
for i, t in enumerate([16.5, 17.0, 17.5, 18.0]):  # chips
    place(pop(820 + i * 110), t + 0.05, 0.16, -0.3)
place(pop(1100), 20.55, 0.14, 0.2)
place(pop(1300), 21.05, 0.14, 0.2)
place(shimmer(1.2), 28.95, 0.08)  # precio al terminar el contador

out = np.clip(out, -1, 1)
os.makedirs("build", exist_ok=True)
with wave.open("build/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("build/sfx.wav ok")
