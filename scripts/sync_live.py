#!/usr/bin/env python3
"""Snapshot the TRPL FB Grant ad account into data/live.json (read-only).

Runs in GitHub Actions when the repo secret META_ACCESS_TOKEN is set (a system-user
token with ads_read on act_960679053196120). Without the secret it exits quietly and
agents refresh data/live.json through the Meta Ads connector instead (see llm.txt).
Never writes to Meta."""
import json, os, sys, urllib.request, urllib.parse, datetime as dt, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACCT = "act_960679053196120"
TOKEN = os.environ.get("META_ACCESS_TOKEN")
V = "https://graph.facebook.com/v21.0"

def get(path, **params):
    params["access_token"] = TOKEN
    url = f"{V}/{path}?{urllib.parse.urlencode(params)}"; out = []
    while url:
        d = json.load(urllib.request.urlopen(url, timeout=60))
        if "data" not in d: return d
        out += d["data"]; url = d.get("paging", {}).get("next")
    return out

def ins(obj_id):
    r = get(f"{obj_id}/insights", fields="spend,impressions,reach,clicks,ctr,cpc,actions", date_preset="maximum")
    if not r: return {}
    i = r[0]; acts = {a["action_type"]: float(a["value"]) for a in i.get("actions", [])}
    res = acts.get("offsite_conversion.fb_pixel_purchase") or acts.get("landing_page_view") or acts.get("video_view") or 0
    return {**{k: i.get(k) for k in ("spend", "impressions", "reach", "clicks", "ctr", "cpc")}, "results": res, "actions": acts}

def main():
    if not TOKEN:
        print("META_ACCESS_TOKEN not set; leaving data/live.json as is."); return
    acct = get(ACCT, fields="name,amount_spent,currency,account_status")
    camps = []
    for c in get(f"{ACCT}/campaigns", fields="id,name,status,effective_status,objective,daily_budget,lifetime_budget,start_time,stop_time", limit=100):
        c["insights"] = ins(c["id"])
        c["ads"] = []
        for a in get(f"{c['id']}/ads", fields="id,name,status,effective_status,creative{title,body,image_url,thumbnail_url,video_id,call_to_action_type,object_story_spec}", limit=100):
            cr = a.get("creative", {}); link = ((cr.get("object_story_spec") or {}).get("link_data") or {}).get("link")
            cr["link"] = link; cr.pop("object_story_spec", None); a["creative"] = cr; c["ads"].append(a)
        camps.append(c)
    out = {"as_of": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "source": "graph-api",
           "account": {"id": ACCT, "name": acct.get("name"), "currency": acct.get("currency"),
                       "amount_spent": float(acct.get("amount_spent", 0)) / 100}, "campaigns": camps}
    (ROOT / "data" / "live.json").write_text(json.dumps(out, indent=1) + "\n"); print(f"{len(camps)} campaigns synced")

if __name__ == "__main__": main()
