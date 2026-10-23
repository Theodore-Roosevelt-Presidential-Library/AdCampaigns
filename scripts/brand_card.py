#!/usr/bin/env python3
"""Put a headline on a photo in the Library's brand type (Dharma Gothic E, all caps) and colors.

  python3 scripts/brand_card.py <photo> <out.jpg> --ratio 4:5 --lines "TRADE SCREENS|FOR SKIES" \
      [--accent 2] [--sub "Medora, North Dakota"] [--pos top|bottom] [--focus 0.5]

Fonts: the Library's licensed web fonts, converted to .otf in .work/fonts/ (gitignored — never
commit font files; the repo is public). Get them with the steps in llm.txt ("Brand cards").
Colors from the brand guidelines: accent colors are for headline text only.

Layout follows Peter Troutner's cleanup of the Trade Screens for Skies cards (Oct 23):
  - the headline fills the width inside 8.5% side margins; tight leading (0.82 x font size)
  - subline in ITC Clearface italic at 5.5% of width, set 4.5% of width below the headline
  - the text block starts about 19% down, in open sky, with air above it, not pinned to the top
  - no dark fade by default: pick a photo whose sky is dark enough to carry white type
    (deep blue, wispy high cloud, golden-hour light); only a soft shadow under the type
  - the subject (the building) sits low, across the lower third, with clean foreground."""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parents[1]; F = ROOT / ".work" / "fonts"
COLORS = {"white": "#FFFFFF", "sunset-yellow": "#F9D635", "sunset-orange": "#FC924E", "sunset-pink": "#F36079",
          "spring-green": "#87BB41", "deep-orange": "#E7805D", "sand": "#D1CCBD", "night-sky": "#092A4D", "dark-gray": "#25282A"}
SIZES = {"1:1": (1080, 1080), "4:5": (1080, 1350), "9:16": (1080, 1920), "16:9": (1920, 1080)}

def cover(im, w, h, focus):
    r = max(w / im.width, h / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = round((im.width - w) * focus[0]); y = round((im.height - h) * focus[1]); return im.crop((x, y, x + w, y + h))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("photo"); ap.add_argument("out")
    ap.add_argument("--ratio", default="4:5"); ap.add_argument("--lines", required=True)
    ap.add_argument("--accent", type=int, default=2, help="1-based line number drawn in the accent color (0 = none)")
    ap.add_argument("--color", default="white"); ap.add_argument("--accent-color", default="sunset-yellow")
    ap.add_argument("--sub", default=""); ap.add_argument("--pos", default="top", choices=["top", "bottom"])
    ap.add_argument("--shade", type=int, default=0, help="darkness of the fade behind the text, 0-255")
    ap.add_argument("--fx", type=float, default=0.5); ap.add_argument("--fy", type=float, default=0.5)
    a = ap.parse_args(); W, H = SIZES[a.ratio]
    im = cover(Image.open(a.photo).convert("RGB"), W, H, (a.fx, a.fy))
    # soft dark fade behind the text
    fade = Image.new("L", (1, 256)); fade.putdata([int(a.shade * (1 - i / 255) ** 1.4) for i in range(256)])
    fade = fade.resize((W, int(H * 0.55)))
    if a.pos == "bottom": fade = fade.transpose(Image.FLIP_TOP_BOTTOM)
    shade = Image.new("RGB", (W, fade.height), (10, 14, 20))
    im.paste(shade, (0, 0 if a.pos == "top" else H - fade.height), fade)
    d = ImageDraw.Draw(im); lines = [l.upper() for l in a.lines.split("|")]
    margin = int(W * 0.085); maxw = W - 2 * margin
    size = 400
    font = lambda s: ImageFont.truetype(str(F / "dharma_type-dharmagothice-exbold.otf"), s)
    while max(d.textlength(l, font=font(size)) for l in lines) > maxw: size -= 4
    size = min(size, int(H * 0.22))
    f = font(size); lh = int(size * 0.82)
    sub_f = ImageFont.truetype(str(F / "clearfacestd-italic.otf"), int(W * 0.055))
    gap = int(W * 0.045)
    block = lh * len(lines) + (gap + int(W * 0.055) if a.sub else 0)
    y = int(H * 0.19) - int(size * 0.16) if a.pos == "top" else H - block - int(H * 0.09)
    # soft shadow under the type so it holds up over bright skies and clouds
    sh = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(sh); yy = y
    for l in lines: sd.text(((W - d.textlength(l, font=f)) / 2, yy + size * 0.03), l, font=f, fill=120); yy += lh
    if a.sub: sd.text(((W - d.textlength(a.sub, font=sub_f)) / 2, yy + gap + int(size * 0.02) + 2), a.sub, font=sub_f, fill=120)
    im.paste(Image.new("RGB", (W, H), (8, 12, 18)), (0, 0), sh.filter(ImageFilter.GaussianBlur(size * 0.06)))
    for i, l in enumerate(lines, 1):
        col = COLORS[a.accent_color] if i == a.accent else COLORS[a.color]
        d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill=col); y += lh
    if a.sub:
        d.text(((W - d.textlength(a.sub, font=sub_f)) / 2, y + gap + int(size * 0.02)), a.sub, font=sub_f, fill=COLORS["white"])
    im.save(a.out, quality=90); print(a.out, im.size, "headline", size, "px")

if __name__ == "__main__": main()
