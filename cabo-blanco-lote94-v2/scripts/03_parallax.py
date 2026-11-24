"""Convierte fotos fijas en tomas tipo dron con movimiento de cámara 2.5D (paralaje por profundidad).

Para cada toma: ventana vertical 9:16 sobre la foto + desplazamiento con paralaje según el mapa de
profundidad (Depth Anything V2). También dibuja, siguiendo el mismo movimiento, los gráficos "pegados al
terreno" de la referencia (trazo blanco del lote, etiqueta en perspectiva, callouts con punto y línea).

Uso: python3 scripts/03_parallax.py [nombre_toma ...]   → build/clips/<toma>.mp4 (1080x1920, 30 fps)
"""
import json, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 30
OW, OH = 1080, 1920
SRC = "../cabo-blanco-lote94/source/fotos"
FONT_SEMI = "hf/assets/fonts/Montserrat-600.ttf"
FONT_BOLD = "hf/assets/fonts/InterTight-800.ttf"
POLY = json.load(open("build/polygons.json"))

# ---------------------------------------------------------------------------------------------
# Tomas: cx = centro horizontal de la ventana (0-1) · pan = desplazamiento de cx durante la toma
# Z = dolly (acercamiento con paralaje) · T = traslación lateral con paralaje (px de foto) · rise = subida
# ---------------------------------------------------------------------------------------------
SHOTS = {
    "s2_IMG_0194": dict(img="IMG_0194", dur=3.7, cx=0.30, pan=0.10, Z=0.16, T=(40, 0), win=0.92),
    "s3_IMG_0196": dict(img="IMG_0196", dur=4.3, cx=0.53, pan=0.05, Z=0.24, T=(-30, 0), win=0.95, trace=True),
    "s4_IMG_0195": dict(img="IMG_0195", dur=4.3, cx=0.54, pan=-0.20, Z=0.08, T=(55, 0), cy=0.5, win=1.0, trace=True),
    "s5_IMG_0193": dict(img="IMG_0193", dur=4.7, cx=0.53, pan=0.24, Z=0.08, T=(-45, -10), cy=0.58, win=0.86, trace=True,
                        ground="45 × 41 M", ground_sub="FLAT · READY TO BUILD"),
    "s6_IMG_0189": dict(img="IMG_0189", dur=4.2, cx=0.46, pan=0.10, Z=0.14, T=(35, 0), win=0.95,
                        callouts=[(0.45, 0.83, "PAVED\nSTREET ACCESS", -1), (0.60, 0.66, "CFE POWER\nCITY WATER", 1)]),
    "s7_IMG_0192": dict(img="IMG_0192", dur=3.9, cx=0.46, pan=0.16, Z=0.10, T=(-40, 0), cy=0.56, win=0.86, trace=True,
                        callouts=[(0.24, 0.513, "TRANSPENINSULAR\nHIGHWAY", 1)]),
    "s8_IMG_0191": dict(img="IMG_0191", dur=3.7, cx=0.50, pan=0.10, Z=0.18, T=(30, 0), win=0.92),
    "s9_IMG_0190": dict(img="IMG_0190", dur=4.8, cx=0.62, pan=0.08, Z=0.15, T=(-30, 0), win=0.95),
}


def smooth(t):  # velocidad casi constante, con arranque/frenado muy suaves (como un dron)
    return t * t * (3 - 2 * t) * 0.35 + t * 0.65


def load(name):
    img = cv2.imread(f"{SRC}/{name}.jpg")
    img = cv2.resize(img, (img.shape[1] * 2, img.shape[0] * 2), interpolation=cv2.INTER_LANCZOS4)
    d = np.load(f"build/depth/{name}.npy").astype(np.float32)
    d = cv2.resize(d, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    d = cv2.GaussianBlur(d, (0, 0), 6)  # bordes de profundidad suaves → menos desgarros
    return img, d


def grade(frame):
    """Look de la referencia: natural, un poco menos saturado, cálido suave, contraste medio."""
    f = frame.astype(np.float32) / 255.0
    lum = f @ np.array([0.114, 0.587, 0.299], np.float32)
    f = lum[..., None] + (f - lum[..., None]) * 0.90           # saturación 0.90
    f = np.clip((f - 0.5) * 1.05 + 0.5, 0, 1)                   # contraste +5 %
    f[..., 2] *= 1.025; f[..., 0] *= 0.975                      # cálido sutil (BGR)
    return (np.clip(f, 0, 1) ** 1.02 * 255).astype(np.uint8)


class Cam:
    def __init__(s, cfg, img, depth):
        s.cfg, s.img, s.d = cfg, img, depth
        H, W = img.shape[:2]
        s.H, s.W = H, W
        s.wh = H * cfg.get("win", 0.95)          # alto de la ventana en px de foto
        s.ww = s.wh * OW / OH
        s.sc = s.wh / OH                        # px de foto por px de salida
        s.df = float(np.median(depth))          # plano de enfoque del paralaje

    def params(s, t):
        c = s.cfg
        e = smooth(t)
        cx = (c["cx"] + c["pan"] * (e - 0.5)) * s.W
        cx = np.clip(cx, s.ww / 2 + 4, s.W - s.ww / 2 - 4)
        cy = np.clip(c.get("cy", 0.5) * s.H, s.wh / 2, s.H - s.wh / 2)
        z = c["Z"] * e
        tx, ty = c["T"][0] * 2 * (e - 0.5), c["T"][1] * 2 * (e - 0.5)
        return cx, cy, z, tx, ty

    def fwd(s, pts, t):
        """Foto (px de la foto original 1365x1024) → salida (px)."""
        cx, cy, z, tx, ty = s.params(t)
        out = []
        for (x, y) in pts:
            X, Y = x * 2.0, y * 2.0
            dv = float(s.d[int(np.clip(Y, 0, s.H - 1)), int(np.clip(X, 0, s.W - 1))])
            g = 1 + z * (0.35 + 0.65 * dv)
            Xo = cx + (X - cx) * g + tx * (dv - s.df)
            Yo = cy + (Y - cy) * g + ty * (dv - s.df)
            out.append(((Xo - (cx - s.ww / 2)) / s.sc, (Yo - (cy - s.wh / 2)) / s.sc))
        return out

    def render(s, t):
        cx, cy, z, tx, ty = s.params(t)
        u, v = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))
        X = ((cx - s.ww / 2) + u * s.sc).astype(np.float32)
        Y = ((cy - s.wh / 2) + v * s.sc).astype(np.float32)
        Sx, Sy = X.copy(), Y.copy()
        for _ in range(4):  # punto fijo: busca el píxel fuente cuya proyección cae aquí
            dv = cv2.remap(s.d, Sx, Sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            g = 1 + z * (0.35 + 0.65 * dv)
            Sx = (cx + (X - tx * (dv - s.df) - cx) / g).astype(np.float32)
            Sy = (cy + (Y - ty * (dv - s.df) - cy) / g).astype(np.float32)
        return cv2.remap(s.img, Sx, Sy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def draw_overlays(frame, cam, cfg, t, tsec):
    name = cfg["img"]
    ov = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    if cfg.get("trace") and name in POLY:
        pts = cam.fwd(POLY[name], t)
        pts = pts + [pts[0]]
        segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        total = sum(segs)
        prog = ease_out((tsec - 0.35) / 1.6) * total     # trazo que se dibuja en 1.6 s
        acc = 0.0
        path = [pts[0]]
        for i, L in enumerate(segs):
            if acc + L <= prog:
                path.append(pts[i + 1]); acc += L
            else:
                r = max(0.0, (prog - acc) / L)
                path.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r))
                break
        if len(path) > 1 and prog > 0:
            glow = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
            ImageDraw.Draw(glow).line(path, fill=(255, 255, 255, 150), width=10, joint="curve")
            ov.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))
            dr.line(path, fill=(255, 255, 255, 255), width=5, joint="curve")
            for p in path[:-1]:
                dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=(255, 255, 255, 255))
    if cfg.get("ground") and name in POLY:
        # etiqueta en perspectiva sobre el terreno (homografía al cuadrilátero interior del lote)
        a = ease_out((tsec - 1.3) / 0.7)
        if a > 0:
            P = np.array(POLY[name], np.float32)
            o = P.mean(axis=0)
            # eje u = borde frontal (v3→v2), eje w = hacia el fondo (v3→v0): etiqueta "acostada" en el terreno
            u = P[2] - P[3]; u = u / np.linalg.norm(u)
            w = P[0] - P[3]; w = w - u * (w @ u); w = w / np.linalg.norm(w)
            Lu = 0.85 * np.linalg.norm(P[2] - P[3]); Lw = Lu * 0.5
            o = (P[2] + P[3]) / 2 - w * (Lw / 2 + 12)          # sobre el terreno libre, frente al borde del lote
            corners = [o - u * Lu / 2 + w * Lw / 2, o + u * Lu / 2 + w * Lw / 2, o + u * Lu / 2 - w * Lw / 2, o - u * Lu / 2 - w * Lw / 2]
            dst = np.array(cam.fwd([c.tolist() for c in corners], t), np.float32)
            lab = Image.new("RGBA", (1400, 700), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lab)
            fb = ImageFont.truetype(FONT_BOLD, 300)
            fs = ImageFont.truetype(FONT_SEMI, 92)
            ld.text((700, 250), cfg["ground"], font=fb, fill=(255, 255, 255, 255), anchor="mm")
            ld.text((700, 530), cfg["ground_sub"], font=fs, fill=(255, 255, 255, 255), anchor="mm")
            src = np.array([[0, 0], [1400, 0], [1400, 700], [0, 700]], np.float32)
            M = cv2.getPerspectiveTransform(src, dst)
            warped = cv2.warpPerspective(np.array(lab), M, (OW, OH), flags=cv2.INTER_LINEAR)
            warped[..., 3] = (warped[..., 3] * a * 0.95).astype(np.uint8)
            ov.alpha_composite(Image.fromarray(warped))
    for (fx, fy, text, side) in cfg.get("callouts", []):
        a = ease_out((tsec - 0.6) / 0.5)
        if a <= 0:
            continue
        (px, py), = cam.fwd([(fx * 1365, fy * 1024)], t)
        f = ImageFont.truetype(FONT_SEMI, 44)
        lines = text.split("\n")
        tw = max(dr.textlength(ln, font=f) for ln in lines)
        # el texto debe caber en cuadro (margen 60 px): si no cabe hacia el lado pedido, se voltea
        if side > 0 and px + 130 + 12 + tw > OW - 60: side = -1
        elif side < 0 and px - 130 - 12 - tw < 60: side = 1
        ex, ey = px + side * 120 * a, py - 110 * a
        dr.line([(px, py), (ex, ey)], fill=(255, 255, 255, int(255 * a)), width=4)
        dr.ellipse([px - 11, py - 11, px + 11, py + 11], fill=(255, 255, 255, int(255 * a)))
        ta = ease_out((tsec - 0.9) / 0.5)
        for i, ln in enumerate(lines):
            ty_ = ey - 18 - (len(lines) - 1 - i) * 52
            tx_ = ex + (12 if side > 0 else -12)
            tx_ = min(max(tx_, 60 + (tw if side < 0 else 0)), OW - 60 - (tw if side > 0 else 0))
            dr.text((tx_ + 2, ty_ + 2), ln, font=f, fill=(0, 0, 0, int(90 * ta)), anchor="ls" if side > 0 else "rs")
            dr.text((tx_, ty_), ln, font=f, fill=(255, 255, 255, int(255 * ta)), anchor="ls" if side > 0 else "rs")
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    base = Image.fromarray(rgb).convert("RGBA")
    base.alpha_composite(ov)
    return cv2.cvtColor(np.array(base.convert("RGB")), cv2.COLOR_RGB2BGR)


def main(names):
    os.makedirs("build/clips", exist_ok=True)
    for key in names:
        cfg = SHOTS[key]
        img, d = load(cfg["img"])
        cam = Cam(cfg, img, d)
        n = int(round(cfg["dur"] * FPS))
        out = f"build/clips/{key}.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                              "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(n):
            t = i / (n - 1)
            fr = grade(cam.render(t))
            fr = draw_overlays(fr, cam, cfg, t, i / FPS)
            p.stdin.write(fr.tobytes())
        p.stdin.close(); p.wait()
        print("ok", out, n, "frames")


if __name__ == "__main__":
    main(sys.argv[1:] or list(SHOTS))
