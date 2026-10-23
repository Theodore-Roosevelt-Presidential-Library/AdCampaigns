#!/usr/bin/env python3
"""Pull partner/public images into creative/web/ with their source recorded in catalog.json.

  python3 scripts/fetch_web.py wiki <slug> <Wikipedia_Page_Title> [season] [scene]
      lead image of a Wikipedia article (via the REST summary API; Commons file, 2000px)
  python3 scripts/fetch_web.py url <slug> <image-url> <source-label> [season] [scene]
      any direct image URL (trlibrary.com, nps.gov, medora.com, ndtourism.com, ...)

Matt confirmed (Oct 22 2026) the Library has rights to use images from Wikipedia, NPS, Medora /
TRMF, Discover Medora, ND Tourism and trlibrary.com. Record the source on every image anyway.
Wikimedia rate-limits shared cloud IPs: on HTTP 429 the script waits and retries."""
import json, subprocess, sys, time, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "creative" / "web"; CAT = OUT / "catalog.json"
UA = "TRPLAdDashboard/1.0 (https://ads.labs.trlibrary.com; mkbriney@gmail.com)"

def curl(url, out=None):
    for wait in (0, 15, 45, 90):
        time.sleep(wait)
        args = ["curl", "-s", "-L", "--max-time", "60", "-A", UA, "-w", "\n%{http_code}", url]
        if out: args[1:1] = ["-o", str(out)]
        r = subprocess.run(args, capture_output=True, text=not out)
        txt = r.stdout if not out else r.stdout.decode()
        code = txt.rsplit("\n", 1)[-1]
        if code == "200": return txt.rsplit("\n", 1)[0] if not out else True
        if code != "429": return None
    return None

def save(slug, raw, rec):
    from PIL import Image; Image.MAX_IMAGE_PIXELS = None
    im = Image.open(raw).convert("RGB"); im.thumbnail((2048, 2048)); im.save(OUT / f"{slug}.jpg", quality=86)
    cat = json.loads(CAT.read_text()) if CAT.exists() else []
    cat = [c for c in cat if c["file"] != f"creative/web/{slug}.jpg"] + [{"file": f"creative/web/{slug}.jpg", **rec}]
    CAT.write_text(json.dumps(cat, indent=1) + "\n"); print(slug, im.size)

def main():
    OUT.mkdir(parents=True, exist_ok=True); kind, slug = sys.argv[1], sys.argv[2]; raw = pathlib.Path(f"/tmp/{slug}.raw")
    if kind == "wiki":
        title = sys.argv[3]; season = sys.argv[4] if len(sys.argv) > 4 else "summer"; scene = sys.argv[5] if len(sys.argv) > 5 else "outdoor"
        j = json.loads(curl(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}") or "{}")
        img = (j.get("originalimage") or {}).get("source")
        if not img or img.lower().endswith(".svg"): sys.exit(f"{slug}: no usable lead image")
        fn = img.split("/")[-1]; thumb = img.replace("/commons/", "/commons/thumb/") + f"/2000px-{fn}" if "/thumb/" not in img else img
        if not (curl(thumb, raw) or curl(img, raw)): sys.exit(f"{slug}: download failed")
        save(slug, raw, {"source": "Wikipedia / Wikimedia Commons", "orig": img, "page": f"https://en.wikipedia.org/wiki/{title}", "season": season, "scene": scene})
    elif kind == "url":
        url, label = sys.argv[3], sys.argv[4]; season = sys.argv[5] if len(sys.argv) > 5 else "summer"; scene = sys.argv[6] if len(sys.argv) > 6 else "outdoor"
        if not curl(url, raw): sys.exit(f"{slug}: download failed")
        save(slug, raw, {"source": label, "orig": url, "season": season, "scene": scene})
    raw.unlink(missing_ok=True)

if __name__ == "__main__": main()
