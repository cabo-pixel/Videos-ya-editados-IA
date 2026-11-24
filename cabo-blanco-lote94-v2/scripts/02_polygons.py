"""Detecta el polígono azul del lote en las fotos marcadas → build/polygons.json (coords en px de la foto 1365x1024)."""
import json, cv2, numpy as np
SRC = "../cabo-blanco-lote94/source/fotos"
out = {}
for n in ["IMG_0192", "IMG_0193", "IMG_0195", "IMG_0196"]:
    im = cv2.imread(f"{SRC}/{n}.jpg")
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    m = ((h > 100) & (h < 125) & (s > 35) & (s < 140) & (v > 120)).astype(np.uint8) * 255
    m[: int(im.shape[0] * 0.3)] = 0                      # sin cielo ni mar del horizonte
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    ap = cv2.approxPolyDP(hull, 0.02 * cv2.arcLength(hull, True), True)[:, 0, :].tolist()
    out[n] = ap
    dbg = im.copy(); cv2.polylines(dbg, [np.array(ap)], True, (255, 255, 255), 2)
    for p in ap: cv2.circle(dbg, tuple(p), 6, (0, 0, 255), -1)
    cv2.imwrite(f"build/poly_{n}.jpg", cv2.resize(dbg, (683, 512)))
    print(n, cv2.contourArea(c), ap)
json.dump(out, open("build/polygons.json", "w"))
