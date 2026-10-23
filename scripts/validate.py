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
CAT = {m["file"]: m for m in json.loads((ROOT / "creative" / "dam" / "catalog.json").read_text())}
def winter_overlap(s, e):  # flight touches Nov 15 – Mar 31 (snow/cold season)
    s, e = dt.date.fromisoformat(s), dt.date.fromisoformat(e)
    return e >= dt.date(2026, 11, 15)
ids = set()
for c in P["campaigns"]:
    if c["id"] in ids: err.append(f"duplicate campaign id {c['id']}")
    ids.add(c["id"])
    if dt.date.fromisoformat(c["end"]) >= exp: err.append(f"{c['id']}: ends on/after credit expiry")
    if abs(sum(a["share"] for a in c["audiences"]) - 1) > .001: err.append(f"{c['id']}: audience shares must add to 1")
    sched = c.get("schedule", [])
    sched_total = sum(x["daily"] * ((dt.date.fromisoformat(x["end"]) - dt.date.fromisoformat(x["start"])).days + 1) for x in sched)
    if not sched or abs(sched_total - c["budget"]) > max(5, c["budget"] * .002): err.append(f"{c['id']}: schedule sums to ${sched_total:,.0f}, budget is ${c['budget']:,}")
    if c.get("spend", {}).get("mode") not in ("test", "burst"): err.append(f"{c['id']}: spend mode must be test or burst")
    # Most people have never heard of the Library: any ad that can reach a cold audience must say
    # what and where it is. Only campaigns aimed entirely at warm audiences may skip it.
    cold = any(not re.search(r"warm|past visitors|retarget", x["name"], re.I) for x in c["audiences"])
    for a in c["ads"]:
        if cold:
            allt = " ".join([a.get("primary", ""), a.get("headline", ""), a.get("desc", "")])
            if "Theodore Roosevelt Presidential Library" not in allt: err.append(f"{a['id']}: cold audience — name the Theodore Roosevelt Presidential Library")
            if not re.search(r"Medora|North Dakota", allt): err.append(f"{a['id']}: cold audience — say where it is (Medora, North Dakota)")
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
            for v in ([m["vertical"]["src"], m["vertical"]["poster"]] if m.get("vertical") else []):
                if not (ROOT / v).exists(): err.append(f"{a['id']}: missing vertical {v}")
            cm = CAT.get(m["src"])
            if cm and cm.get("season") == "summer" and winter_overlap(c["start"], c["end"]) and a.get("sells") != "summer":
                warn.append(f"{a['id']}: summer photo {m['src'].split('/')[-1]} in an ad that runs in winter (mark sells:'summer' only if the ad sells a summer trip)")
for w in warn: print("WARN ", w)
for e in err: print("ERROR", e)
print(f"{len(P['campaigns'])} campaigns · ${total:,} planned incl. reserve · {len(err)} errors · {len(warn)} warnings")
sys.exit(1 if err else 0)
