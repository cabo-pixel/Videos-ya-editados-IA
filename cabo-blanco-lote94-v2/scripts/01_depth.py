"""Mapas de profundidad (Depth Anything V2 Small) para el movimiento de cámara 2.5D."""
import glob, os, sys
import numpy as np
from PIL import Image
from transformers import pipeline
src = sys.argv[1] if len(sys.argv) > 1 else "../cabo-blanco-lote94/source/fotos"
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
os.makedirs("build/depth", exist_ok=True)
for f in sorted(glob.glob(f"{src}/*.jpg")):
    n = os.path.splitext(os.path.basename(f))[0]
    im = Image.open(f).convert("RGB")
    d = pipe(im)["predicted_depth"]
    d = np.array(d.squeeze().cpu().numpy(), dtype=np.float32)
    d = np.array(Image.fromarray(d).resize(im.size, Image.BICUBIC))
    d = (d - d.min()) / (d.max() - d.min() + 1e-6)   # 1 = cerca, 0 = lejos
    np.save(f"build/depth/{n}.npy", d)
    Image.fromarray((d * 255).astype(np.uint8)).save(f"build/depth/{n}.png")
    print(n, d.shape)
