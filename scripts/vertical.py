#!/usr/bin/env python3
"""Make 9:16 (1080x1920) versions of 16:9 or 4:5 videos for Stories and Reels — without cropping text.

    python3 scripts/vertical.py <source.mp4> <out.mp4> [--mode auto|fit] [--full RANGE ...]

RULE (Matt, Oct 2026): a vertical version must never crop on-screen text. This script enforces it.

How it works
  1. Splits the video into shots (ffmpeg scene detection).
  2. In each shot, samples three frames and finds
       - text (RapidOCR text detection: titles, captions, end cards, wall signs, screens), and
       - people (OpenCV face/profile/body detection).
  3. Picks a crop window per shot:
       - no text: a full-height 9:16 window centred on the people (fills the phone screen);
       - text that fits in a 9:16 window: the window is placed so all of the text is inside it,
         then nudged toward the people;
       - text wider than a 9:16 window: the window widens to hold all the text plus a margin, is
         scaled to the phone's width, and sits in the middle of a dark, heavily blurred copy of
         the frame (so nothing is cut and the text is as large as it can be).
--mode fit      every shot uses the full frame width (old "letterbox on blur" look).
--full A-B      force the full frame for a time range in seconds (e.g. --full 73.5-90), repeatable.

Writes <out>.json next to the video with each shot's window and the text it found, so a person can
check it. After rendering, LOOK at a contact sheet of the result before using it:
  ffmpeg -i out.mp4 -vf "fps=1/2,scale=96:-2,tile=14x4" -frames:v 1 sheet.jpg
Sources: download the Library's own commercials with yt-dlp on Matt's Mac (YouTube blocks cloud
IPs) into .work/ (gitignored). AV1/VP9 downloads are transcoded to h264 automatically.
Requires ffmpeg, opencv-python-headless, rapidocr-onnxruntime."""
import json, re, subprocess, pathlib, argparse, tempfile
import cv2

W, H = 1080, 1920
MARGIN = 0.03          # extra room around text, as a share of frame width
MIN_TEXT_H = 0.018     # ignore text shorter than this share of frame height (unreadable fine print)

def probe(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,codec_name:format=duration", "-of", "json", src], capture_output=True, text=True).stdout
    d = json.loads(o); s = d["streams"][0]
    return s["width"], s["height"], float(d["format"]["duration"]), s["codec_name"]

def scenes(src, dur, thresh=0.28):
    o = subprocess.run(["ffmpeg", "-i", src, "-vf", f"select='gt(scene,{thresh})',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", o)]
    pts = [0.0] + [c for c in cuts if c > 0.4] + [dur]
    return [(a, b) for a, b in zip(pts, pts[1:]) if b - a > 0.15]

FACE = PROF = HOG = OCR = None
def detectors():
    global FACE, PROF, HOG, OCR
    if FACE is None:
        FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
        HOG = cv2.HOGDescriptor(); HOG.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        from rapidocr_onnxruntime import RapidOCR
        OCR = RapidOCR()

def frame_at(cap, t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
    return fr if ok else None

def people_x(fr):
    """Weighted horizontal centre (0-1) of people in the frame, or None."""
    small = cv2.resize(fr, (960, int(960 * fr.shape[0] / fr.shape[1]))); g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    boxes = [(x, w, w * h * 3) for (x, y, w, h) in FACE.detectMultiScale(g, 1.1, 6, minSize=(28, 28))]
    boxes += [(x, w, w * h * 2) for (x, y, w, h) in PROF.detectMultiScale(g, 1.1, 6, minSize=(28, 28))]
    if not boxes:
        rects, wts = HOG.detectMultiScale(small, winStride=(8, 8), scale=1.05)
        boxes = [(x, w, w * h * float(s)) for (x, y, w, h), s in zip(rects, wts) if float(s) > 0.6]
    if not boxes: return None
    tot = sum(b[2] for b in boxes)
    return sum((x + w / 2) / 960 * b for x, w, b in boxes) / tot

def text_boxes(fr):
    """[(x0, x1, words)] in source pixels for readable text in the frame."""
    k = 960 / fr.shape[1]
    r, _ = OCR(cv2.resize(fr, (960, int(fr.shape[0] * k))))
    r = [([(px / k, py / k) for px, py in box], t, sc) for box, t, sc in (r or [])]
    out = []
    for box, txt, score in (r or []):
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        if float(score) < 0.5 or (max(ys) - min(ys)) < MIN_TEXT_H * fr.shape[0] or len(txt.strip()) < 2: continue
        out.append((min(xs), max(xs), txt))
    return out

def parse_range(s):
    a, b = s.split("-"); return float(a), float(b)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--mode", default="auto", choices=["auto", "fit"])
    ap.add_argument("--full", action="append", default=[], type=parse_range)
    ap.add_argument("--crf", default="23")
    a = ap.parse_args()
    src = a.src
    vw, vh, dur, codec = probe(src)
    tmp = None
    if codec not in ("h264", "hevc", "mpeg4", "prores"):  # OpenCV can't read AV1/VP9 reliably
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-c:a", "copy", tmp], check=True)
        src = tmp
    cw = int(vh * 9 / 16) // 2 * 2   # 9:16 window width in source pixels
    # shots, split further at any forced full-frame boundaries
    shots = scenes(src, dur)
    for (fa, fb) in a.full:
        nxt = []
        for s, e in shots:
            cuts = sorted({s, e} | {t for t in (fa, fb) if s < t < e}); nxt += list(zip(cuts, cuts[1:]))
        shots = nxt
    detectors(); cap = cv2.VideoCapture(src); plan = []
    for s, e in shots:
        forced = a.mode == "fit" or any(fa <= (s + e) / 2 < fb for fa, fb in a.full)
        frames = [frame_at(cap, s + (e - s) * f) for f in (.2, .5, .8)]
        frames = [f for f in frames if f is not None]
        px = [x for x in (people_x(f) for f in frames) if x is not None]
        # text: every 0.4 s through the shot, so text that pans or animates in is caught
        n = max(3, int((e - s) / 0.4)); tframes = [frame_at(cap, s + (e - s) * (i + .5) / n) for i in range(n)]
        per = [text_boxes(f) for f in tframes if f is not None]
        tb = [b for fb in per for b in fb]
        cents = [(min(b[0] for b in fb) + max(b[1] for b in fb)) / 2 for fb in per if fb]
        moving = len(cents) > 1 and max(cents) - min(cents) > 0.05 * vw   # camera pans across text
        cx = (sum(px) / len(px) if px else 0.5) * vw
        if forced:
            x, w = 0, vw
        elif tb and moving:        # text slides through the frame: only the full width is safe
            x, w = 0, vw
        elif tb:
            t0 = max(0, min(b[0] for b in tb) - MARGIN * vw); t1 = min(vw, max(b[1] for b in tb) + MARGIN * vw)
            if t1 - t0 <= cw:      # text fits in a 9:16 window: keep it all in, lean toward the people
                x, w = min(max(cx - cw / 2, t1 - cw), t0), cw
            else:                  # still text wider than 9:16: widen the window to the text (+ margin)
                x, w = t0, t1 - t0
        else:
            x, w = cx - cw / 2, cw
        w = int(min(max(w, cw), vw)) // 2 * 2; x = int(min(max(x, 0), vw - w))
        plan.append({"start": round(s, 3), "end": round(e, 3), "x": x, "w": w, "fill": w == cw,
                     "people": bool(px), "text": sorted({b[2] for b in tb})[:8]})
    # one filter chain per shot, then concat
    parts, labels = [], []
    for i, p in enumerate(plan):
        seg = f"[0:v]trim=start={p['start']}:end={p['end']},setpts=PTS-STARTPTS"
        if p["fill"]:
            parts.append(f"{seg},crop={p['w']}:{vh}:{p['x']}:0,scale={W}:{H},setsar=1[s{i}]")
        else:
            parts.append(f"{seg},split=2[b{i}][f{i}];"
                         f"[b{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=60:3,eq=brightness=-0.32[bb{i}];"
                         f"[f{i}]crop={p['w']}:{vh}:{p['x']}:0,scale={W}:-2[ff{i}];[bb{i}][ff{i}]overlay=0:(H-h)/2,setsar=1[s{i}]")
        labels.append(f"[s{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(plan)}:v=1:a=0[out]"
    script = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False); script.write(fc); script.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex_script", script.name, "-map", "[out]", "-map", "0:a?",
                    "-c:v", "libx264", "-preset", "medium", "-crf", a.crf, "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", a.out], check=True)
    pathlib.Path(a.out).with_suffix(".json").write_text(json.dumps(
        {"source": pathlib.Path(a.src).name, "mode": a.mode, "full": a.full, "crop_width": cw, "shots": plan}, indent=1) + "\n")
    n_text = sum(1 for p in plan if p["text"]); n_wide = sum(1 for p in plan if not p["fill"])
    print(f"{a.out}: {len(plan)} shots, {n_text} with text, {n_wide} widened so no text is cut")
    if tmp: pathlib.Path(tmp).unlink(missing_ok=True)

if __name__ == "__main__": main()
