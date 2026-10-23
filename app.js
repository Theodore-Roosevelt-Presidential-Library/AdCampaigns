/* TRPL Meta Ads dashboard. Static: reads data/campaigns.json (proposed),
   data/live.json (snapshot of the ad account) and creative/dam/catalog.json. */
(function () {
  "use strict";
  const { render: mock, esc } = window.MetaMock;
  const $ = s => document.querySelector(s);
  const money = (n, d = 0) => "$" + Number(n || 0).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  const k = n => n >= 1000 ? "$" + (n / 1000).toLocaleString("en-US", { maximumFractionDigits: 1 }) + "K" : money(n);
  const D = s => new Date(s + "T12:00:00");
  const fmtD = s => D(s).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const PROGRAMS = ["Tickets & visits", "Membership & giving", "Retail", "Salt+Scoria", "Events", "Brand & audience building", "Retargeting"];
  const PDESC = {
    "Tickets & visits": "Admission sales. Summer-trip planning is the biggest revenue lever this winter.",
    "Membership & giving": "Gift memberships, new-year joins and year-end gifts.",
    "Retail": "The Library store online (18 products) through the holiday shipping window.",
    "Salt+Scoria": "Private dining leads and café awareness near Medora.",
    "Events": "What's on the Library calendar Nov–Jan.",
    "Brand & audience building": "Low-cost video reach that builds the audiences the revenue campaigns retarget.",
    "Retargeting": "Brings back people the other campaigns warmed up."
  };
  const color = p => `var(--s${PROGRAMS.indexOf(p) + 1})`;
  const fetchJSON = (u, fb) => fetch(u, { cache: "no-store" }).then(r => r.ok ? r.json() : fb).catch(() => fb);

  let PLAN, LIVE, CAT, filter = "all", WEB = [];

  Promise.all([fetchJSON("data/campaigns.json", null), fetchJSON("data/live.json", { campaigns: [] }), fetchJSON("creative/dam/catalog.json", []), fetchJSON("creative/web/catalog.json", [])])
    .then(([p, l, c, w]) => { PLAN = p; LIVE = l; CAT = c; WEB = w; boot(); });

  function boot() {
    $("#asof").textContent = "plan updated " + new Date(PLAN.generated).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) +
      (LIVE.as_of ? " · Meta synced " + new Date(LIVE.as_of).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "");
    $("#n-proposed").textContent = PLAN.campaigns.length;
    $("#n-live").textContent = (LIVE.campaigns || []).length;
    $("#n-creative").textContent = CAT.length + 7;
    document.querySelectorAll(".tabs button").forEach(b => b.addEventListener("click", () => show(b.dataset.tab)));
    window.addEventListener("hashchange", () => show(location.hash.slice(1) || "proposed", true));
    renderProposed(); renderLive(); renderPacing(); renderCreative();
    show(location.hash.slice(1) || "proposed", true);
    document.addEventListener("click", e => {
      const p = e.target.closest(".play"); if (p) openVideo(p.dataset.yt);
      if (e.target.closest(".modal-x") || e.target.id === "modal") closeVideo();
    });
  }

  function show(t, fromHash) {
    if (!document.getElementById("tab-" + t)) t = "proposed";
    document.querySelectorAll(".tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === t));
    document.querySelectorAll(".tab").forEach(s => s.hidden = s.id !== "tab-" + t);
    if (!fromHash) history.replaceState(null, "", "#" + t);
  }
  function openVideo(id) { $("#modal .modal-body").innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${esc(id)}?autoplay=1&rel=0" allow="autoplay; encrypted-media" allowfullscreen></iframe>`; $("#modal").hidden = false; }
  function closeVideo() { $("#modal").hidden = true; $("#modal .modal-body").innerHTML = ""; }

  const liveSpend = () => Number((LIVE.account && LIVE.account.amount_spent) || (LIVE.campaigns || []).reduce((s, c) => s + Number((c.insights || {}).spend || 0), 0));
  const daysLeft = () => Math.max(0, Math.ceil((new Date(PLAN.credit.expires + "T00:00:00-06:00") - new Date()) / 864e5));
  const liveFor = id => (LIVE.campaigns || []).find(c => (c.name || "").includes("[" + id + "]"));

  // ---------------- Proposed ----------------
  function renderProposed() {
    const C = PLAN.campaigns, planned = C.reduce((s, c) => s + c.budget, 0);
    const rev = C.filter(c => c.revenue).reduce((s, c) => s + c.budget, 0);
    const ads = C.reduce((s, c) => s + c.ads.length, 0);
    const el = $("#tab-proposed");
    el.innerHTML = `<p class="lede">Campaigns proposed for the credit, grouped by program, with mockups of each ad as it would appear on Facebook and Instagram. Nothing here is live until Matt approves a campaign by name; it is then built paused in Meta and shows up under Live in Meta.</p>
      <div class="stats">
        ${stat("Ad credit", k(PLAN.credit.total), "expires " + fmtD(PLAN.credit.expires))}
        ${stat("Planned", k(planned), "+ " + k(PLAN.reserve.budget) + " reserve")}
        ${stat("Revenue campaigns", Math.round(rev / planned * 100) + "%", "of planned spend")}
        ${stat("Campaigns", C.length, ads + " ads")}
        ${stat("Spent in Meta", k(liveSpend()), "")}
        ${stat("Days left", daysLeft(), "to use the credit")}
      </div>
      <div class="pills" id="pf">${["all", ...PROGRAMS].map(p => `<button class="pill" data-p="${esc(p)}" aria-pressed="${p === filter}">${p === "all" ? "All programs" : esc(p)}</button>`).join("")}</div>
      <div id="groups"></div>
      <div class="group"><h2>Reserve <span class="meta">${money(PLAN.reserve.budget)}</span></h2><p class="gdesc">${esc(PLAN.reserve.why)}</p></div>`;
    el.querySelectorAll("#pf .pill").forEach(b => b.onclick = () => { filter = b.dataset.p; el.querySelectorAll("#pf .pill").forEach(x => x.setAttribute("aria-pressed", x === b)); groups(); });
    groups();
  }
  function stat(kk, v, s) { return `<div class="stat"><div class="k">${esc(kk)}</div><div class="v">${v}</div>${s ? `<div class="k" style="color:var(--ink-3)">${esc(s)}</div>` : ""}</div>`; }

  function groups() {
    const C = PLAN.campaigns;
    $("#groups").innerHTML = PROGRAMS.filter(p => filter === "all" || filter === p).map(p => {
      const cs = C.filter(c => c.program === p).sort((a, b) => a.priority - b.priority || a.start.localeCompare(b.start));
      if (!cs.length) return "";
      const tot = cs.reduce((s, c) => s + c.budget, 0);
      return `<div class="group"><h2><span><i style="display:inline-block;width:10px;height:10px;border-radius:3px;background:${color(p)};margin-right:8px"></i>${esc(p)}</span><span class="meta">${cs.length} campaign${cs.length > 1 ? "s" : ""} · ${money(tot)}</span></h2>
        <p class="gdesc">${esc(PDESC[p] || "")}</p>${timeline(cs)}${cs.map(campaign).join("")}</div>`;
    }).join("");
  }

  // Flight bars across the credit window, like the HouseFile send timeline.
  function timeline(cs) {
    const a = D("2026-10-26"), b = D(PLAN.credit.expires), span = b - a;
    const pos = s => Math.max(0, Math.min(100, (D(s) - a) / span * 100));
    const marks = [["2026-11-01", "Nov"], ["2026-12-01", "Dec"], ["2027-01-01", "Jan"], [PLAN.credit.expires, "Ends"]];
    return `<div style="position:relative;margin:6px 0 4px;padding-top:16px">
      ${marks.map(([d, l]) => `<span style="position:absolute;top:0;left:${pos(d)}%;transform:translateX(${pos(d) > 95 ? "-100%" : "-50%"});font-size:11px;color:var(--ink-3);white-space:nowrap">${l}</span>`).join("")}
      ${cs.map(c => `<div title="${esc(c.name)}: ${fmtD(c.start)}–${fmtD(c.end)}" style="position:relative;height:8px;margin:4px 0;background:var(--line-2);border-radius:4px"><div style="position:absolute;left:${pos(c.start)}%;width:${Math.max(1, pos(c.end) - pos(c.start))}%;top:0;bottom:0;background:${color(c.program)};border-radius:4px"></div></div>`).join("")}
    </div>`;
  }

  function campaign(c) {
    const live = liveFor(c.id);
    const status = live ? `<span class="chip ${String(live.effective_status || live.status).toLowerCase() === "active" ? "active" : "paused"}">In Meta: ${esc(live.effective_status || live.status)}</span>` : `<span class="chip proposed">Proposed</span>`;
    return `<div class="camp" id="c-${esc(c.id)}"><div class="camp-head">
      <div class="camp-budget"><div class="big">${k(c.budget)}</div><div class="small">${money(c.daily)}/day avg</div><div class="small">${c.days} days</div></div>
      <div style="flex:1;min-width:0">
        <h3>${esc(c.name)} ${status}${c.revenue ? '<span class="chip rev">Revenue</span>' : ""}${c.spend ? `<span class="chip ${c.spend.mode}">${c.spend.mode === "test" ? "Test, then scale" : "Burst: spend it all"}</span>` : ""}</h3>
        <p class="why">${esc(c.why)}</p>${spendPlan(c)}
        <dl class="spec">
          <dt>Flight</dt><dd>${fmtD(c.start)} – ${fmtD(c.end)}</dd>
          <dt>Objective</dt><dd>${esc(c.objective)}</dd>
          <dt>Optimize for</dt><dd>${esc(c.optimization)}</dd>
          <dt>Plan ID</dt><dd><code>${esc(c.id)}</code></dd>
        </dl>
        <table class="aud"><thead><tr><th>Ad set</th><th>Where</th><th>Who</th><th class="num">Budget</th></tr></thead><tbody>
          ${c.audiences.map(a => `<tr><td>${esc(a.name)}</td><td>${esc(a.geo)}<br><span style="color:var(--ink-3)">Ages ${esc(a.age)}</span></td><td>${esc(a.detail)}</td><td class="num">${money(c.budget * a.share)}</td></tr>`).join("")}
        </tbody></table>
        ${c.open_items && c.open_items.length ? `<div class="open"><b>Open before launch</b><ul>${c.open_items.map(o => `<li>${esc(o)}</li>`).join("")}</ul></div>` : ""}
      </div></div>
      <details class="ads" open><summary>${c.ads.length} ad${c.ads.length > 1 ? "s" : ""} — mockups</summary>${c.ads.map(ad).join("")}</details>
    </div>`;
  }

  function spendPlan(c) {
    const sp = c.spend; if (!sp) return "";
    if (sp.mode === "burst") return `<div class="spendplan"><b>Burst.</b> ${esc(sp.why)} All ads on from day one at ${money(c.daily)}/day. Judged on ${esc(sp.metric.toLowerCase())}; reserve moves in if it's delivering.</div>`;
    const [t, r] = c.schedule;
    return `<div class="spendplan"><b>Test, then scale.</b> ${fmtD(t.start)}–${fmtD(t.end)}: every ad runs at ${money(t.daily)}/day (${Math.round(sp.test_frac * 100)}% of plan). Decide on ${fmtD(sp.decide_on)} using ${esc(sp.metric.toLowerCase())} (target ${esc(sp.target)}): pause ads over 1.5× the best ad, keep the top two. Then ${money(r.daily)}/day through ${fmtD(r.end)}, raised no more than 25% every 3 days while on target.</div>`;
  }

  function ad(a) {
    const src = a.format === "catalog" ? "Shopify catalog" : a.format === "carousel" ? [...new Set(a.cards.map(c => c.media.source))].join(", ") : a.media.source;
    return `<div class="ad"><h4>${esc(a.name)}<span class="id">${esc(a.id)}</span></h4>${mock(a)}
      <dl class="spec">
        ${a.for ? `<dt>Shown to</dt><dd>${esc(a.for)} ad set only</dd>` : ""}
        <dt>Format</dt><dd>${esc(a.format)}${a.flight ? " · runs " + esc(a.flight) : ""}</dd>
        <dt>Button</dt><dd>${esc(a.cta)}</dd>
        <dt>Link</dt><dd><a href="${esc(a.tracked_url)}" target="_blank" rel="noopener">${esc(a.url)}</a> <span style="color:var(--ink-3)">+ UTMs</span>${(a.cards || []).some(c => c.url) ? `<br>${a.cards.map(c => c.url ? `<span style="color:var(--ink-3)">${esc(c.headline)}:</span> <a href="${esc(c.tracked_url)}" target="_blank" rel="noopener">${esc(c.url.replace("https://www.trlibrary.com", ""))}</a>` : "").filter(Boolean).join("<br>")}` : ""}</dd>
        <dt>Creative</dt><dd>${esc(src)}${a.media && a.media.placeholder || a.placeholder ? ' · <span class="verify">placeholder</span>' : ""}</dd>
        ${a.verify ? `<dt>Verify</dt><dd><span class="verify">${esc(a.verify)}</span></dd>` : ""}
      </dl></div>`;
  }

  // ---------------- Live ----------------
  function renderLive() {
    const el = $("#tab-live"), C = LIVE.campaigns || [], spent = liveSpend();
    const remaining = Math.max(0, PLAN.credit.total - spent), dl = daysLeft();
    el.innerHTML = `<p class="lede">What is actually in the TRPL FB Grant ad account, synced from Meta${LIVE.as_of ? " on " + new Date(LIVE.as_of).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" }) : ""}. Campaign names carry their plan ID in brackets, e.g. <code>[tix-summer]</code>, to link back to the proposal.</p>
      <div class="stats">
        ${stat("Spent", money(spent), "")}
        ${stat("Credit remaining", k(remaining), "")}
        ${stat("Needed per day", money(dl ? remaining / dl : 0), "to use it all")}
        ${stat("Campaigns", C.length, C.filter(c => (c.effective_status || c.status) === "ACTIVE").length + " active")}
      </div>
      ${C.length ? C.map(liveCampaign).join("") : `<div class="empty"><b>No campaigns in the account yet.</b><br>Approved proposals are created paused, then appear here with their real ads and results.</div>`}`;
  }
  function liveCampaign(c) {
    const i = c.insights || {}, budget = c.daily_budget ? money(c.daily_budget / 100) + "/day" : c.lifetime_budget ? money(c.lifetime_budget / 100) + " lifetime" : "budget on ad sets";
    const st = String(c.effective_status || c.status || "").toLowerCase();
    return `<div class="group"><h2><span>${esc(c.name)} <span class="chip ${st === "active" ? "active" : "paused"}">${esc(c.effective_status || c.status)}</span></span><span class="meta">${budget}</span></h2>
      <p class="gdesc">${esc(c.objective || "")}${c.start_time ? " · " + new Date(c.start_time).toLocaleDateString() : ""}${c.stop_time ? " – " + new Date(c.stop_time).toLocaleDateString() : ""}</p>
      <div class="stats">${stat("Spend", money(i.spend, 2), "")}${stat("Impressions", Number(i.impressions || 0).toLocaleString(), "")}${stat("Reach", Number(i.reach || 0).toLocaleString(), "")}${stat("Link clicks", Number(i.clicks || 0).toLocaleString(), i.ctr ? Number(i.ctr).toFixed(2) + "% CTR" : "")}${stat("Results", Number(i.results || 0).toLocaleString(), i.result_type || "")}</div>
      ${(c.ads || []).map(a => {
        const cr = a.creative || {};
        const obj = { format: cr.video_id ? "video" : "image", primary: cr.body || "", headline: cr.title || "", desc: cr.description || "", cta: (cr.call_to_action_type || "LEARN_MORE").replace(/_/g, " ").toLowerCase().replace(/\b\w/g, m => m.toUpperCase()), url: cr.link || "", media: { type: "image", src: cr.image_url || cr.thumbnail_url || "" } };
        return `<div class="ad"><h4>${esc(a.name)} <span class="chip ${String(a.effective_status || "").toLowerCase() === "active" ? "active" : "paused"}">${esc(a.effective_status || a.status || "")}</span><span class="id">${esc(a.id)}</span></h4>${mock(obj)}</div>`;
      }).join("")}</div>`;
  }

  // ---------------- Pacing ----------------
  function weeks() {
    const out = []; let d = D("2026-10-26"); const end = D(PLAN.credit.expires);
    while (d < end) { const n = new Date(d); n.setDate(n.getDate() + 7); out.push([new Date(d), n]); d = n; }
    return out;
  }
  function spendIn(c, a, b) { // planned spend of campaign c between dates a (incl) and b (excl), following its test→scale schedule
    const parts = c.schedule || [{ start: c.start, end: c.end, daily: c.daily }];
    return parts.reduce((sum, p) => {
      const s = D(p.start), e = D(p.end); e.setDate(e.getDate() + 1);
      const lo = Math.max(s, a), hi = Math.min(e, b);
      return sum + (hi > lo ? p.daily * Math.round((hi - lo) / 864e5) : 0);
    }, 0);
  }
  function renderPacing() {
    const W = weeks(), R = { start: "2026-12-14", end: "2027-01-19" };
    const rDays = (D(R.end) - D(R.start)) / 864e5 + 1, reserve = { ...R, daily: PLAN.reserve.budget / rDays };
    const rows = W.map(([a, b]) => {
      const v = {}; PROGRAMS.forEach(p => v[p] = PLAN.campaigns.filter(c => c.program === p).reduce((s, c) => s + spendIn(c, a, b), 0));
      v.Reserve = spendIn(reserve, a, b); return { a, v, tot: Object.values(v).reduce((s, x) => s + x, 0) };
    });
    const keys = [...PROGRAMS, "Reserve"], col = p => p === "Reserve" ? "var(--s0)" : color(p);
    const max = Math.max(...rows.map(r => r.tot)), VW = 1000, L = 52, H = 240, BW = (VW - L) / rows.length;
    const nice = Math.ceil(max / 5000) * 5000;
    const bars = rows.map((r, i) => {
      let y = H; const x = L + i * BW;
      const segs = keys.map(p => { const h = r.v[p] / nice * H; if (h < .5) return ""; y -= h; return `<rect x="${x + BW * .18}" y="${y + 1}" width="${BW * .64}" height="${Math.max(0, h - 2)}" rx="3" fill="${col(p)}"></rect>`; }).join("");
      return `<g class="wk" data-i="${i}">${segs}<rect x="${x}" y="0" width="${BW}" height="${H}" fill="transparent"></rect></g>`;
    }).join("");
    const ticks = [0, .25, .5, .75, 1].map(f => `<line class="grid" x1="${L}" x2="${VW}" y1="${H - f * H}" y2="${H - f * H}"></line><text x="${L - 6}" y="${H - f * H + 4}" text-anchor="end">${k(nice * f)}</text>`).join("");
    const lbl = rows.map((r, i) => `<text x="${L + i * BW + BW / 2}" y="${H + 16}" text-anchor="middle">${r.a.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</text>`).join("");
    let run = 0; const cum = rows.map(r => (run += r.tot));
    const CH = 170, cmax = PLAN.credit.total * 1.08, cy = v => CH - v / cmax * CH;
    const pts = [`${L},${CH}`, ...cum.map((v, i) => `${L + (i + 1) * BW},${cy(v)}`)].join(" ");
    const sp = liveSpend(), now = new Date(), nowF = Math.max(0, Math.min(1, (now - D("2026-10-26")) / (rows.length * 7 * 864e5)));
    const nowX = L + nowF * (VW - L);
    $("#tab-pacing").innerHTML = `<p class="lede">Planned spend by week if every proposed campaign runs as drawn. The reserve is spread over Dec 14–Jan 19 until it's assigned.</p>
      <div class="chart"><h3>Planned spend per week</h3><p class="cap">Weeks start Monday. Peak is the holiday stretch, when gifts, giving and summer-trip planning overlap.</p>
        <div class="legend">${keys.map(p => `<span><i style="background:${col(p)}"></i>${esc(p)}</span>`).join("")}</div>
        <svg viewBox="0 0 ${VW} ${H + 24}" id="wkchart">${ticks}${bars}${lbl}</svg></div>
      <div class="chart"><h3>Cumulative spend vs. the $150K credit</h3><p class="cap">Line: planned. Dashed: the credit. Dot: actual spend to date from Meta.</p>
        <svg viewBox="0 0 ${VW} ${CH + 26}">
          ${[0, 50000, 100000].map(v => `<line class="grid" x1="${L}" x2="${VW}" y1="${cy(v)}" y2="${cy(v)}"></line><text x="${L - 6}" y="${cy(v) + 4}" text-anchor="end">${k(v)}</text>`).join("")}
          <line x1="${L}" x2="${VW}" y1="${cy(PLAN.credit.total)}" y2="${cy(PLAN.credit.total)}" stroke-dasharray="5 5" stroke="var(--ink-3)"></line>
          <text x="${L - 6}" y="${cy(PLAN.credit.total) + 4}" text-anchor="end">$150K</text>
          <polyline points="${pts}" fill="none" stroke="var(--s1)" stroke-width="2"></polyline>
          <circle cx="${nowX}" cy="${cy(sp)}" r="5" fill="var(--s2)" stroke="var(--card)" stroke-width="2"></circle>
          <text x="${nowX + 8}" y="${cy(sp) - 8}">Today · ${k(sp)} spent</text>
          ${rows.map((r, i) => i % 2 ? "" : `<text x="${L + i * BW + BW / 2}" y="${CH + 18}" text-anchor="middle">${r.a.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</text>`).join("")}
        </svg></div>
      <div class="chart"><h3>Testing and guardrails</h3><p class="cap">How the credit gets spent without burning it. Test campaigns start low and earn their budget; burst campaigns are tied to something happening now.</p>
        <table class="data"><thead><tr><th>Campaign</th><th>Mode</th><th>Test window</th><th>Judged on</th><th class="num">Test $/day</th><th class="num">After $/day</th></tr></thead><tbody>
        ${PLAN.campaigns.slice().sort((x, y) => x.start.localeCompare(y.start)).map(c => { const sc = c.schedule || []; const t = c.spend.mode === "test"; return `<tr><td>${esc(c.name)}</td><td>${t ? "Test" : "Burst"}</td><td>${t ? fmtD(sc[0].start) + "–" + fmtD(sc[0].end) : "—"}</td><td>${esc(c.spend.metric)}${t ? " (" + esc(c.spend.target) + ")" : ""}</td><td class="num">${t ? money(sc[0].daily) : "—"}</td><td class="num">${money(sc[sc.length - 1].daily)}</td></tr>`; }).join("")}
        </tbody></table>
        <ul class="guard">${(PLAN.guardrails || []).map(g => `<li>${esc(g)}</li>`).join("")}</ul></div>
      <div class="chart"><h3>Table view</h3><table class="data"><thead><tr><th>Week of</th>${keys.map(p => `<th class="num">${esc(p)}</th>`).join("")}<th class="num">Total</th><th class="num">Cumulative</th></tr></thead><tbody>
        ${rows.map((r, i) => `<tr><td>${r.a.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</td>${keys.map(p => `<td class="num">${r.v[p] ? money(r.v[p]) : "—"}</td>`).join("")}<td class="num"><b>${money(r.tot)}</b></td><td class="num">${money(cum[i])}</td></tr>`).join("")}
      </tbody></table></div>`;

    const tip = document.createElement("div"); tip.className = "tip"; tip.hidden = true; document.body.appendChild(tip);
    $("#wkchart").addEventListener("mousemove", e => {
      const g = e.target.closest(".wk"); if (!g) { tip.hidden = true; return; }
      const r = rows[g.dataset.i];
      tip.innerHTML = `<b>Week of ${r.a.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</b> · ${money(r.tot)}<br>` + keys.filter(p => r.v[p]).map(p => `${esc(p)}: ${money(r.v[p])}`).join("<br>");
      tip.hidden = false; tip.style.left = Math.min(e.clientX + 14, innerWidth - 270) + "px"; tip.style.top = e.clientY + 14 + "px";
    });
    $("#wkchart").addEventListener("mouseleave", () => tip.hidden = true);
  }

  // ---------------- Creative ----------------
  function renderCreative() {
    const used = new Map();
    PLAN.campaigns.forEach(c => c.ads.forEach(a => {
      const ms = a.cards ? a.cards.map(x => x.media) : a.media ? [a.media] : [];
      ms.forEach(m => { if (!used.has(m.src)) used.set(m.src, []); used.get(m.src).push(a.id); });
    }));
    const vids = [["W9sq8PuGQVo", "Discover the Theodore Roosevelt Presidential Library", "3:35"], ["qrwdZmqFO5A", "Your Journey Starts Here — The Trailblazer", "1:21"], ["-mcN1M3ZEps", "In the Room: Exhibition Preview", "1:23"],
      ["yEEsRy7sdng", "Step Into the Amazon: River of Doubt", "0:53"], ["zRPJAdE-IBI", "The TR Library Boardwalk", "1:34"], ["gtDTwBMTn2Q", "\"Resolute\" — TR in His Own Words", "0:31"], ["k3U8V1HmKDs", "\"Arena\" — JFK Reads \"Man in the Arena\"", "0:31"]];
    const FILES = new Set(); PLAN.campaigns.forEach(c => c.ads.forEach(a => { const m = a.media; if (m && m.youtube && m.file) FILES.add(m.youtube); }));
    const fig = (src, title, sub, extra) => { const u = used.get(src) || []; return `<figure><img loading="lazy" src="${esc(src)}" alt="${esc(title)}">${extra || ""}<figcaption><b>${esc(title)}</b><br>${esc(sub)}${u.length ? `<br>Used in: ${u.map(esc).join(", ")}` : ""}</figcaption></figure>`; };
    $("#tab-creative").innerHTML = `<p class="lede">Real Library photography from the Acquia DAM press portal, the Commercials playlist, and Salt+Scoria's own photos. Pulled with <code>scripts/fetch_dam.py</code>; see llm.txt to add more.</p>
      <div class="group"><h2>Commercials <span class="meta">${vids.length} videos</span></h2><p class="gdesc">trlibrary.com/video — Commercials playlist. Click to play.</p>
        <div class="grid-lib">${vids.map(([id, t, d]) => { const u = used.get(`creative/video/yt_${id}.jpg`) || []; const file = FILES.has(id) ? `creative/video/feed/yt_${id}.mp4` : ""; return `<figure><div class="m" style="width:auto;flex:none;border:0;border-radius:0"><div class="media" style="aspect-ratio:16/9">${file ? `<video src="${file}" poster="creative/video/yt_${id}.jpg" preload="none" controls playsinline style="width:100%;height:100%;object-fit:cover"></video>` : `<img loading="lazy" src="creative/video/yt_${id}.jpg" alt="${esc(t)}"><div class="play" data-yt="${id}"><span></span></div><span class="dur">${d}</span>`}</div></div><figcaption><b>${esc(t)}</b>${u.length ? `<br>Used in: ${u.map(esc).join(", ")}` : ""}</figcaption></figure>`; }).join("")}</div></div>
      <div class="group"><h2>Acquia DAM <span class="meta">${CAT.length} photos</span></h2><p class="gdesc">Press portal galleries: Library in Action, Building Photography, Campfire and Prairie Talks, B-roll.</p>
        <div class="grid-lib">${CAT.map(c => fig(c.file, c.file.split("/").pop().replace(".jpg", ""), `${c.filename} · ${c.gallery}`)).join("")}</div></div>
      <div class="group"><h2>Partner and public photos <span class="meta">${WEB.length} photos</span></h2><p class="gdesc">The national park, Medora and road-trip stops, from trlibrary.com/visit, NPS, Medora.com (TRMF) and Wikipedia. Pulled with <code>scripts/fetch_web.py</code>; source on each.</p>
        <div class="grid-lib">${WEB.map(c => fig(c.file, c.file.split("/").pop().replace(".jpg", ""), c.source)).join("")}</div></div>
      <div class="group"><h2>Salt+Scoria <span class="meta">8 photos</span></h2><p class="gdesc">From saltandscoria.com. Not in the DAM yet; add them so they live with the rest of the image bank.</p>
        <div class="grid-lib">${["trpl-saltscoria_general-026", "trpl-saltscoria_general-027", "trpl-saltscoria_general-029", "trpl-saltscoria_general-033", "trpl-saltscoria_general-034", "trpl-saltscoria_general-047", "dsc00636-2", "dsc00885"].map(s => fig(`creative/saltscoria/${s}.jpg`, s, "saltandscoria.com")).join("")}</div></div>`;
  }
})();
