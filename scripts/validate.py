#!/usr/bin/env python3
"""Checks data/campaigns.json before anything is shown to Matt or pushed to Meta.
Fails (exit 1) on errors; prints warnings. Run after scripts/plan.py."""
import json, re, sys, pathlib, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "data" / "campaigns.json").read_text())
err, warn = [], []
total = sum(c["budget"] for c in P["campaigns"]) + P["reserve"]["budget"]
if total > P["credit"]["total"]: err.append(f"Planned ${total:,} exceeds the ${P['credit']['total']:,} credit")
if total < P["credit"]["total"]: warn.append(f"${P['credit']['total'] - total:,} of the credit is unplanned")
exp = dt.date.fromisoformat(P["credit"]["expires"])
BANNED = re.compile(r"\b(stunning|breathtaking|world-class|transformative|amazing|unforgettable journey)\b", re.I)
YEAR = re.compile(r"\b20[2-9]\d\b")  # no current/future years in visitor copy
ids = set()
for c in P["campaigns"]:
    if c["id"] in ids: err.append(f"duplicate campaign id {c['id']}")
    ids.add(c["id"])
    if dt.date.fromisoformat(c["end"]) >= exp: err.append(f"{c['id']}: ends on/after credit expiry")
    if abs(sum(a["share"] for a in c["audiences"]) - 1) > .001: err.append(f"{c['id']}: audience shares must add to 1")
    for a in c["ads"]:
        if a["id"] in ids: err.append(f"duplicate ad id {a['id']}")
        ids.add(a["id"])
        texts = [a.get("primary", ""), a.get("headline", ""), a.get("desc", "")] + [x.get("headline", "") + " " + x.get("desc", "") for x in a.get("cards", [])]
        for t in texts:
            if YEAR.search(t): err.append(f"{a['id']}: year in copy → '{t[:60]}'")
            if BANNED.search(t): err.append(f"{a['id']}: banned word → '{BANNED.search(t).group(0)}'")
            if re.search(r"\b[1-3] hours?\b|\b2½ hours\b", t): err.append(f"{a['id']}: a visit is 3½ hours")
        if len(a.get("headline", "")) > 40: warn.append(f"{a['id']}: headline over 40 chars")
        if len(a.get("primary", "")) > 280: warn.append(f"{a['id']}: primary text over 280 chars")
        if not a["url"].startswith("https://"): err.append(f"{a['id']}: link must be https")
        media = [x["media"] for x in a.get("cards", [])] + ([a["media"]] if a.get("media") else [])
        for m in media:
            if not m["src"].startswith("http") and not (ROOT / m["src"]).exists(): err.append(f"{a['id']}: missing {m['src']}")
for w in warn: print("WARN ", w)
for e in err: print("ERROR", e)
print(f"{len(P['campaigns'])} campaigns · ${total:,} planned incl. reserve · {len(err)} errors · {len(warn)} warnings")
sys.exit(1 if err else 0)
