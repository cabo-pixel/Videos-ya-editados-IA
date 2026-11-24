"""Clip IA del gancho → versiones 9:16 y 16:9 con el mismo etalonaje cinematográfico que las tomas 2.5D."""
import subprocess, sys
import numpy as np
sys.argv = [sys.argv[0]]
ns = {}
exec(open("scripts/03_parallax.py").read().replace('if __name__ == "__main__":', "if False:"), ns)
grade = ns["grade"]
SRC = "source/ia/hook_IMG_0188_kling.mp4"
for name, vf, W, H in [
    ("hf/assets/clips/s1_hook_IMG_0188_ia.mp4", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920:flags=lanczos,fps=30", 1080, 1920),
    ("hf_h/assets/clips/s1_hook_IMG_0188_ia.mp4", "crop=1660:934:0:150,scale=1920:1080:flags=lanczos,fps=30", 1920, 1080),
]:
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf + ",unsharp=5:5:0.4", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", name], stdin=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = dec.stdout.read(n)
        if len(b) < n:
            break
        enc.stdin.write(grade(np.frombuffer(b, np.uint8).reshape(H, W, 3)).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    print("ok", name)
