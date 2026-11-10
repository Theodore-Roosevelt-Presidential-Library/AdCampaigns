"""Make placement-sized versions of ad photos (Matt, Nov 10 2026: ad units didn't match creative sizes).
4x5 = Feed, 9x16 = Stories/Reels, 1x1 = carousel cards. Uses 2048px DAM originals from .work/hires when present.
Text graphics are never cropped: they are fitted whole over a blurred fill (video rule applies to stills too).
Usage: python3 scripts/placements.py <src> <slug> <ratios,...> [--fit] [--fx 0.0-1.0]"""
import sys, pathlib, cv2, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
R = {"4x5": (1080, 1350), "9x16": (1080, 1920), "1x1": (1080, 1080)}
OUT = pathlib.Path("creative/placements")

def load(src):
    hi = pathlib.Path(".work/hires") / pathlib.Path(src).name
    p = hi if hi.exists() and src.startswith("creative/dam/") else pathlib.Path(src)
    return Image.open(p).convert("RGB")

def focus_x(im):
    a = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    s = cv2.saliency.StaticSaliencySpectralResidual_create(); ok, m = s.computeSaliency(cv2.resize(a, (a.shape[1] // 4, a.shape[0] // 4)))
    col = m.sum(0); col = np.convolve(col, np.ones(9) / 9, "same"); return float((col * np.arange(len(col))).sum() / col.sum() / len(col))

def crop(im, W, H, fx):
    r = W / H; w, h = im.size
    if w / h > r:
        cw = int(h * r); x = int(min(max(fx * w - cw / 2, 0), w - cw)); box = (x, 0, x + cw, h)
    else:
        ch = int(w / r); y = int((h - ch) * 0.4); box = (0, y, w, y + ch)
    return im.crop(box).resize((W, H), Image.LANCZOS)

def fit(im, W, H):
    bg = crop(im, W, H, 0.5).filter(ImageFilter.GaussianBlur(40)); bg = ImageEnhance.Brightness(bg).enhance(0.55)
    f = im.copy(); f.thumbnail((W, int(H * (0.62 if H > W * 1.5 else 1.0))), Image.LANCZOS)
    y = (H - f.height) // 2 if H <= W * 1.5 else int(H * 0.42 - f.height / 2)
    bg.paste(f, ((W - f.width) // 2, max(y, 0))); return bg

if __name__ == "__main__":
    a = sys.argv[1:]; src, slug, ratios = a[0], a[1], a[2].split(","); isfit = "--fit" in a
    fx = float(a[a.index("--fx") + 1]) if "--fx" in a else None
    im = load(src); fx = focus_x(im) if fx is None else fx
    for k in ratios:
        W, H = R[k]; out = (fit(im, W, H) if isfit else crop(im, W, H, fx))
        out.save(OUT / f"{slug}-{k}.jpg", quality=88, optimize=True, progressive=True)
    print(slug, src, f"fx={fx:.2f}", "fit" if isfit else "crop", ratios)
