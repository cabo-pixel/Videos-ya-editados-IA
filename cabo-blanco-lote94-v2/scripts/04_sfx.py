"""Sintetiza la pista de efectos de sonido (whooshes, impactos, pops) alineada a la línea de tiempo.

Salida: build/sfx.wav (48 kHz, estéreo, 40 s). Todo es síntesis propia → sin problemas de licencia.
Uso: python3 scripts/04_sfx.py
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


# --- línea de tiempo v2 (s): pocos efectos, como la referencia ---
place(whoosh(0.9, 200, 2500, 0.8), 0.0, 0.18)            # entrada del vuelo
place(whoosh(0.6, 400, 4000), 0.5 - 0.42, 0.20)           # título CALETA LOMA
place(impact(1.4), 0.75, 0.30)
for cut in [4.5, 8.0, 12.0, 16.0, 20.5, 24.5, 28.0, 31.5]:
    place(whoosh(0.5, 300, 3500), cut - 0.35, 0.16, 0.2)
place(shimmer(1.0), 13.6, 0.06)                           # fin del contador 1,832
place(whoosh(0.9, 2500, 200, 0.35), 35.5, 0.22)           # fundido al logo
place(impact(1.8), 36.0, 0.32)                            # logo

out = np.clip(out, -1, 1)
os.makedirs("build", exist_ok=True)
with wave.open("build/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("build/sfx.wav ok")
