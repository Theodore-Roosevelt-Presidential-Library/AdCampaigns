# AdCampaigns

Planning and review dashboard for the Theodore Roosevelt Presidential Library's $150K Meta ad credit (expires Jan 20, 2027).

**Live:** https://ads.trlibrary.com

- **Proposed** — every campaign under consideration, with Facebook Feed, Instagram Feed and Stories/Reels mockups of each ad. Mockups only; nothing runs until approved.
- **Live in Meta** — what is actually in the TRPL FB Grant ad account, with spend and results.
- **Pacing** — planned weekly spend against the credit.
- **Creative** — the Library photos and commercials used in the ads.

Agents: read [`llm.txt`](llm.txt) before changing anything.

## Run locally

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install pillow            # only needed for scripts/fetch_dam.py
python3 scripts/plan.py && python3 scripts/validate.py
python3 -m http.server 8000   # open http://localhost:8000
```

## Setup

- Settings → Pages → Source: **GitHub Actions**. Custom domain: `ads.trlibrary.com` (CNAME file in repo).
- DNS: `ads` CNAME → `theodore-roosevelt-presidential-library.github.io`.
- Optional: repo secret `META_ACCESS_TOKEN` (system-user token, `ads_read` on `act_960679053196120`) so the daily Action refreshes `data/live.json`.
