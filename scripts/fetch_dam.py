#!/usr/bin/env python3
"""Pull Library photos from the PUBLIC Acquia DAM press portal (no token needed).

    python3 scripts/fetch_dam.py list                     # galleries in the portal
    python3 scripts/fetch_dam.py sheet action  --out /tmp/sheets   # contact sheets to pick from (needs Pillow)
    python3 scripts/fetch_dam.py get action <external_id> <slug>   # add one photo to creative/dam/

Gallery keys: action, building, campfire, drone, broll, video, ceremony, benefactor.
Photos land in creative/dam/<slug>.jpg (max 1200px JPEG) and are recorded in
creative/dam/catalog.json with their DAM IDs. Acquia's preview URLs are signed and
expire, so always download; never hot-link them.
For the full (non-press) DAM, use the token-based API documented in Outline:
TRPL / Acquia DAM (Widen) — API Access."""
import json, sys, os, io, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = "https://trlibrary.acquiadam.com/portals/api"
PORTAL = "ob41lpui"
MORE, OPEN = "c5dd89a5-7aae-4ae1-83fa-ed61fc419f74", "ce25be09-83a1-4e9d-a037-b45415e49a93"
G = {"action": (MORE, "bd220376-08e3-42bf-be99-ee73f37fb07a"), "building": (MORE, "999c0bf9-cf3c-4a41-bcb6-ca66504e4284"),
     "broll": (MORE, "656c10c7-e9c3-4a4d-b61c-73d21e129bb8"), "video": (MORE, "95b7619d-7c74-49ab-98ed-7f6f445766ad"),
     "campfire": (OPEN, "b0c74015-083e-418a-9af6-c8d65b5d7904"), "drone": (OPEN, "19add399-d64e-4e86-988f-68082d2fb676"),
     "ceremony": (OPEN, "009702e2-3e6d-4aed-ad81-edc857d05349"), "benefactor": (OPEN, "1ec77de2-12b9-43bd-bf36-3e49bdfe3930")}

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))

def assets(key):
    s, c = G[key]; off, out = 0, []
    while True:
        d = post(f"{API}/assets/search/public/section/{s}/collection/{c}", {"expands": "file_properties,image_previews", "limit": 100, "offset": off})
        out += d["items"]; off += 100
        if off >= d["total_count"]: return out

def main(a):
    if not a or a[0] == "list":
        d = json.load(urllib.request.urlopen(f"{API}/view/sections/portal/{PORTAL}?expand=collectionPreviews"))
        for sec in d["items"]:
            for col in sec.get("collections", []): print(f'{col.get("total_items", "?"):>5}  {col.get("title")}  {col["id"]}')
        return
    if a[0] == "sheet":
        from PIL import Image, ImageDraw
        out = pathlib.Path(a[2] if len(a) > 2 else "sheets"); out.mkdir(parents=True, exist_ok=True)
        items = assets(a[1]); W, H, C = 240, 170, 8
        for s in range(0, len(items), 48):
            chunk = items[s:s + 48]; rows = (len(chunk) + C - 1) // C
            sh = Image.new("RGB", (W * C, (H + 16) * rows), "white"); dr = ImageDraw.Draw(sh)
            for k, it in enumerate(chunk):
                u = it["image_previews"]["thumbnails"].get("300px")
                if not u: continue
                im = Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=60).read())).convert("RGB"); im.thumbnail((W - 6, H - 4))
                x, y = (k % C) * W, (k // C) * (H + 16); sh.paste(im, (x + 3, y + 2)); dr.text((x + 4, y + H), f'{it["external_id"]} {it["filename"][:20]}', fill="black")
            sh.save(out / f"{a[1]}_{s // 48:02d}.jpg", quality=70)
        print("sheets in", out); return
    if a[0] == "get":
        from PIL import Image
        key, ext, slug = a[1], a[2], a[3]
        it = next(x for x in assets(key) if x["external_id"] == ext)
        t = it["image_previews"]["thumbnails"]; u = t.get("2048px") or t.get("1080px")
        im = Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=120).read())).convert("RGB"); im.thumbnail((1200, 1200))
        f = ROOT / "creative" / "dam" / f"{slug}.jpg"; im.save(f, "JPEG", quality=82, optimize=True, progressive=True)
        catp = ROOT / "creative" / "dam" / "catalog.json"; cat = json.loads(catp.read_text())
        cat = [c for c in cat if c["file"] != f"creative/dam/{slug}.jpg"]
        fp = (it.get("file_properties") or {}).get("image_properties") or {}
        cat.append({"file": f"creative/dam/{slug}.jpg", "dam_asset_id": it["id"], "dam_external_id": ext, "filename": it["filename"], "gallery": key,
                    "w": fp.get("width"), "h": fp.get("height"), "preview_w": im.width, "preview_h": im.height, "source": "Acquia DAM press portal"})
        catp.write_text(json.dumps(cat, indent=1) + "\n"); print("saved", f); return
    print(__doc__)

if __name__ == "__main__": main(sys.argv[1:])
