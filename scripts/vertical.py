#!/usr/bin/env python3
"""Make 9:16 (1080x1920) versions of 16:9 commercials for Stories and Reels.

    python3 scripts/vertical.py <source.mp4> <out.mp4> [--mode reframe|fit] [--fit-from SECONDS] [--fit-until SECONDS]

reframe  Cuts the video into shots (scene detection), finds people in each shot
         (face + body detection, OpenCV) and crops a 9:16 window around them.
         Shots with no one in them stay centered. Audio and timing are untouched.
fit      The full 16:9 frame, scaled to the width of the phone, on a blurred,
         darkened copy of itself. Use when text is burned into the picture
         (Resolute, Arena) or for end cards.
--fit-from / --fit-until  switch to fit for the opening title or end card of a
         reframed video (e.g. --fit-from 78 for an end card starting at 1:18).

Writes <out>.json next to the video with each shot's crop position so a person
can adjust and re-run. Source files: download the Library's own commercials with
yt-dlp on Matt's Mac (YouTube blocks cloud IPs) into .work/ (gitignored).
Requires ffmpeg and opencv-python-headless."""
import json, re, subprocess, sys, pathlib, argparse
import cv2

W, H = 1080, 1920

def probe(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", src], capture_output=True, text=True).stdout
    d = json.loads(o); s = d["streams"][0]
    return s["width"], s["height"], float(d["format"]["duration"])

def scenes(src, dur, thresh=0.28):
    o = subprocess.run(["ffmpeg", "-i", src, "-vf", f"select='gt(scene,{thresh})',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", o)]
    pts = [0.0] + [c for c in cuts if c > 0.4] + [dur]
    return [(a, b) for a, b in zip(pts, pts[1:]) if b - a > 0.15]

FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
HOG = cv2.HOGDescriptor(); HOG.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def subject_x(cap, t, vw):
    """Horizontal centre (0-1) of the people in the frame at time t, or None."""
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
    if not ok: return None
    small = cv2.resize(fr, (960, 540)); g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    boxes = [(x, w, w * h * 3) for (x, y, w, h) in FACE.detectMultiScale(g, 1.1, 6, minSize=(28, 28))]
    boxes += [(x, w, w * h * 2) for (x, y, w, h) in PROF.detectMultiScale(g, 1.1, 6, minSize=(28, 28))]
    if not boxes:
        rects, wts = HOG.detectMultiScale(small, winStride=(8, 8), scale=1.05)
        boxes = [(x, w, w * h * float(s)) for (x, y, w, h), s in zip(rects, wts) if float(s) > 0.6]
    if not boxes: return None
    tot = sum(b[2] for b in boxes)
    return sum((x + w / 2) / 960 * b for x, w, b in boxes) / tot

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--mode", default="reframe", choices=["reframe", "fit"])
    ap.add_argument("--fit-from", type=float); ap.add_argument("--fit-until", type=float)
    ap.add_argument("--crf", default="23")
    a = ap.parse_args()
    vw, vh, dur = probe(a.src)
    cw = vh * 9 / 16  # crop width in source pixels
    shots = []
    if a.mode == "reframe":
        cap = cv2.VideoCapture(a.src)
        for s, e in scenes(a.src, dur):
            xs = [subject_x(cap, s + (e - s) * f, vw) for f in (.25, .5, .75)]
            xs = [x for x in xs if x is not None]
            cx = sum(xs) / len(xs) if xs else 0.5
            left = min(max(cx * vw - cw / 2, 0), vw - cw)
            shots.append({"start": round(s, 2), "end": round(e, 2), "x": int(left), "people": bool(xs)})
    # fit composite: blurred fill + full frame centred
    fit = (f"[0:v]split=2[bg][fg];[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.18[bgb];"
           f"[fg]scale={W}:-2[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2[fit]")
    if a.mode == "fit":
        fc, outv = fit, "[fit]"
    else:
        xexpr = "0"
        for sh in reversed(shots):
            xexpr = f"if(between(t,{sh['start']},{sh['end']}),{sh['x']},{xexpr})"
        crop = f"[0:v]split=2[v1][v2];[v1]crop={int(cw)}:{vh}:'{xexpr}':0,scale={W}:{H}[cr]"
        rng = []
        if a.fit_from is not None: rng.append(f"gte(t,{a.fit_from})")
        if a.fit_until is not None: rng.append(f"lt(t,{a.fit_until})")
        if rng:
            fit2 = fit.replace("[0:v]split=2[bg][fg]", "[v2]split=2[bg][fg]")
            fc = f"{crop};{fit2};[fit][cr]overlay=0:0:enable='not({'+'.join(rng)})'[out]"
        else:
            fc = f"[0:v]crop={int(cw)}:{vh}:'{xexpr}':0,scale={W}:{H}[out]"
        outv = "[out]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex", fc, "-map", outv, "-map", "0:a?",
           "-c:v", "libx264", "-preset", "medium", "-crf", a.crf, "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "128k", a.out]
    subprocess.run(cmd, check=True)
    pathlib.Path(a.out).with_suffix(".json").write_text(json.dumps(
        {"source": pathlib.Path(a.src).name, "mode": a.mode, "fit_from": a.fit_from, "fit_until": a.fit_until, "shots": shots}, indent=1) + "\n")
    print(f"{a.out}: {len(shots)} shots, {sum(s['people'] for s in shots)} with people")

if __name__ == "__main__": main()
