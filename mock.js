/* Meta ad mockups: Facebook Feed, Instagram Feed and Instagram Stories/Reels.
   Built to behave like the apps: "See more" expands the text, videos autoplay muted when
   on screen (tap the speaker for sound, tap the video to pause), carousels swipe, and in
   Stories each carousel card is its own panel with segmented progress bars (tap left/right).
   Images that aren't 9:16 sit on a blurred fill in Stories, the way Meta places them, so
   nothing is cropped. Every ad object comes from data/campaigns.json. */
(function (g) {
  "use strict";
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const PAGE = "Theodore Roosevelt Presidential Library", IG = "trlibrary", AV = "creative/brand/avatar.jpg";
  const domainOf = u => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (e) { return ""; } };
  const STORY_MS = 5000; // how long an image panel shows in Stories

  // Text that truncates where Meta does and expands in place when "See more"/"more" is tapped.
  function clip(t, n, label) {
    t = String(t || "");
    if (t.length <= n) return esc(t);
    const cut = t.slice(0, n).replace(/\s+\S*$/, "").replace(/[.,;:!?]+$/, "");
    return `<span class="clip"><span class="s">${esc(cut)}… <button type="button" class="more">${label || "See more"}</button></span><span class="f" hidden>${esc(t)}</span></span>`;
  }

  const ph = extra => extra && extra.placeholder ? '<span class="ph">PLACEHOLDER</span>' : "";
  const vidTag = (file, poster) => `<video src="${esc(file)}" poster="${esc(poster)}" preload="none" playsinline muted loop></video>
    <button type="button" class="snd" aria-label="Sound">🔇</button><span class="paused-ic"></span>`;

  // Feed media. Videos are the files that will be uploaded to Meta (never a YouTube link).
  function media(m, ratio, extra) {
    if (!m) return `<div class="media" style="aspect-ratio:${ratio}"></div>`;
    if (m.type === "video" && m.feed) { m = m.feed; ratio = m.ratio || ratio; }  // e.g. a 4:5 cut for feeds
    if (m.type === "video" && m.file)
      return `<div class="media vid" style="aspect-ratio:${ratio}">${vidTag(m.file, m.src)}<span class="dur">${esc(m.duration || "")}</span>${ph(extra)}</div>`;
    const vid = m.type === "video" ? `<span class="dur">${esc(m.duration || "")}</span>` : "";
    return `<div class="media${m.type === "product" ? " prod" : ""}" style="aspect-ratio:${ratio}"><img loading="lazy" src="${esc(m.src)}" alt="${esc(m.title || m.alt || "")}">${vid}${ph(extra)}</div>`;
  }

  function cards(ad) {
    if (ad.format === "catalog") return (ad.products || []).map(p => ({ media: p, headline: p.title, desc: p.price }));
    return ad.cards || [];
  }
  const multi = ad => ad.format === "carousel" || ad.format === "catalog";

  function fbFeed(ad) {
    const head = `<div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${PAGE}</div><div class="sp">Sponsored · 🌐</div></div><div class="dots">···</div></div>`;
    const text = `<div class="tx">${clip(ad.primary, 125)}</div>`;
    const rx = `<div class="rx"><span>👍 Like</span><span>💬 Comment</span><span>↗ Share</span></div>`;
    if (multi(ad)) {
      const cs = cards(ad).map(c => `<div class="card">${media(c.media, "1/1")}<div class="cf"><div class="l"><div class="hl">${esc(c.headline)}</div><div class="ds">${esc(c.desc || "")}</div></div><div class="cta">${esc(ad.cta)}</div></div></div>`).join("");
      return `<div><p class="mock-label">Facebook Feed</p><div class="m fb">${head}${text}<div class="car">${cs}</div>${rx}</div></div>`;
    }
    const ratio = ad.format === "video" ? (ad.media.feed ? ad.media.feed.ratio : "16/9") : (ad.media.ratio || "1/1");  // designed images keep their shape
    return `<div><p class="mock-label">Facebook Feed</p><div class="m fb">${head}${text}${media(ad.media, ratio, ad)}
      <div class="link"><div class="l"><div class="dom">${esc(domainOf(ad.url))}</div><div class="hl">${esc(ad.headline)}</div><div class="ds">${esc(ad.desc || "")}</div></div><div class="cta">${esc(ad.cta)}</div></div>${rx}</div></div>`;
  }

  function igFeed(ad) {
    const head = `<div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${IG}</div><div class="sp">Sponsored</div></div><div class="dots">···</div></div>`;
    let m, dots = "";
    if (multi(ad)) {
      const cs = cards(ad);
      m = `<div class="igcar">${cs.map(c => `<div class="slide">${media(c.media, "1/1")}</div>`).join("")}</div>`;
      dots = `<div class="igdots">${cs.map((_, i) => `<i${i ? "" : ' class="on"'}></i>`).join("")}</div>`;
    } else m = media(ad.media, ad.format === "video" ? "16/9" : "4/5", ad);  // video keeps its own shape (no cropped text)
    return `<div><p class="mock-label">Instagram Feed</p><div class="m ig">${head}${m}
      <div class="bar blue"><span>${esc(ad.cta)}</span><span>›</span></div>${dots}
      <div class="icons"><span>♡</span><span>💬</span><span>➤</span><span class="sv">🔖</span></div>
      <div class="cap"><b>${IG}</b> ${clip(ad.primary, 90, "more")}</div></div></div>`;
  }

  // One Stories panel: a 9:16 video plays full screen; anything else sits on a blurred fill.
  function panel(m, extra) {
    if (m && m.story) return `<div class="panel"><img class="full" src="${esc(m.story)}" alt="">${ph(extra)}</div>`;  // a 9:16 version made for Stories
    if (m && m.vertical) return `<div class="panel">${vidTag(m.vertical.src, m.vertical.poster)}${ph(extra)}</div>`;
    if (m && m.type === "video" && (m.file || (m.feed && m.feed.file))) {
      const f = m.feed && m.feed.file ? m.feed : m;
      return `<div class="panel fit"><img class="bg" src="${esc(f.src)}" alt="">${vidTag(f.file, f.src)}${ph(extra)}</div>`;
    }
    const src = m ? m.src : "";
    return `<div class="panel fit"><img class="bg" src="${esc(src)}" alt=""><img class="fg${m && m.type === "product" ? " prod" : ""}" src="${esc(src)}" alt="">${ph(extra)}</div>`;
  }

  function igStory(ad) {
    const ps = multi(ad) ? cards(ad).map(c => ({ m: c.media, h: c.headline })) : [{ m: ad.media }];
    const isVert = !multi(ad) && ad.media && ad.media.vertical;
    const label = multi(ad) ? `Stories / Reels · ${ps.length} cards` : isVert ? "Stories / Reels · vertical cut" : "Stories / Reels";
    return `<div><p class="mock-label">${label}</p><div class="m st" data-n="${ps.length}">
      <div class="segs">${ps.map(() => '<i><b></b></i>').join("")}</div>
      ${ps.map((p, i) => `<div class="pnl${i ? "" : " on"}">${panel(p.m, ad)}${p.h ? `<div class="chl">${esc(p.h)}</div>` : ""}</div>`).join("")}
      <div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${IG}</div><div class="sp">Sponsored</div></div></div>
      ${ps.length > 1 ? '<div class="tap prev"></div><div class="tap next"></div>' : '<div class="tap toggle"></div>'}
      <div class="bt"><div class="t">${clip(ad.primary, 70, "more")}</div><span class="c">${esc(ad.cta)}</span></div></div></div>`;
  }

  function render(ad) {
    const p = ad.placements || ["fb_feed", "ig_feed", "ig_story"];
    return `<div class="mocks">${p.includes("fb_feed") ? fbFeed(ad) : ""}${p.includes("ig_feed") ? igFeed(ad) : ""}${p.includes("ig_story") ? igStory(ad) : ""}</div>`;
  }

  // ---------------- behaviour ----------------
  const play = v => { if (v) { const p = v.play(); if (p && p.catch) p.catch(() => {}); } };
  function storyGo(st, i) {
    const pn = [...st.querySelectorAll(".pnl")], segs = [...st.querySelectorAll(".segs i")];
    i = (i + pn.length) % pn.length; st._i = i; st._t0 = performance.now();
    pn.forEach((p, k) => { p.classList.toggle("on", k === i); const v = p.querySelector("video"); if (v) { if (k === i && st._vis) { v.currentTime = 0; play(v); } else v.pause(); } });
    segs.forEach((s, k) => s.firstChild.style.width = k < i ? "100%" : "0%");
  }
  function tick() {
    document.querySelectorAll(".m.st").forEach(st => {
      if (!st._vis || st._hold) return;
      const i = st._i || 0, seg = st.querySelectorAll(".segs i")[i], v = st.querySelectorAll(".pnl")[i].querySelector("video");
      let f;
      if (v) f = v.duration ? v.currentTime / v.duration : 0;
      else { f = (performance.now() - (st._t0 || performance.now())) / STORY_MS; if (f >= 1) { storyGo(st, i + 1); return; } }
      if (seg) seg.firstChild.style.width = Math.min(100, f * 100) + "%";
    });
    requestAnimationFrame(tick);
  }
  const io = "IntersectionObserver" in g ? new IntersectionObserver(es => es.forEach(e => {
    const el = e.target, vis = e.isIntersecting;
    if (el.classList.contains("st")) {
      el._vis = vis;
      if (vis) { if (el._i == null) storyGo(el, 0); else { el._t0 = performance.now(); play(el.querySelector(".pnl.on video")); } }
      else el.querySelectorAll("video").forEach(v => v.pause());
    } else if (el.tagName === "VIDEO" && !el.closest(".st")) { if (vis && !el._userPaused) play(el); else el.pause(); }
  }), { threshold: 0.6 }) : null;
  function wire(root) {
    if (!io) return;
    (root || document).querySelectorAll(".m video:not([controls]), .m.st").forEach(el => { if (!el._wired) { el._wired = 1; io.observe(el); } });
  }
  if (g.document) {
    new MutationObserver(() => wire()).observe(document.documentElement, { childList: true, subtree: true });
    requestAnimationFrame(tick);
    document.addEventListener("click", e => {
      // Stories/Reels: tapping anywhere on the caption expands it upward over the video; tap again to close
      const cap = e.target.closest(".st .bt .t");
      const stx = e.target.closest(".m.st");
      if (cap || (stx && stx.classList.contains("expanded") && !e.target.closest(".c"))) {
        const st = stx, open = !st.classList.contains("expanded");
        st.classList.toggle("expanded", open); st._hold = open; if (!open) st._t0 = performance.now();
        st.querySelectorAll(".clip").forEach(c => { c.querySelector(".s").hidden = open; c.querySelector(".f").hidden = !open; });
        if (open) { const t = st.querySelector(".bt .t"); t.scrollTop = 0; }
        e.stopPropagation(); return;
      }
      const more = e.target.closest(".clip .more");   // feeds: "See more" / "more" expands in place
      if (more) { const c = more.closest(".clip"); c.querySelector(".s").hidden = true; c.querySelector(".f").hidden = false; e.stopPropagation(); return; }
      const snd = e.target.closest(".snd");
      if (snd) { const v = snd.parentElement.querySelector("video"); v.muted = !v.muted; snd.textContent = v.muted ? "🔇" : "🔊"; if (!v.muted) play(v); return; }
      const tap = e.target.closest(".st .tap");
      if (tap) {
        const s = tap.closest(".st");
        if (tap.classList.contains("toggle")) { const v = s.querySelector(".pnl.on video"); if (v) { v.paused ? play(v) : v.pause(); s._hold = v.paused; } else s._hold = !s._hold; }
        else storyGo(s, (s._i || 0) + (tap.classList.contains("next") ? 1 : -1));
        return;
      }
      const vid = e.target.closest(".m .media.vid");
      if (vid) { const v = vid.querySelector("video"); if (v.paused) { v._userPaused = false; play(v); } else { v._userPaused = true; v.pause(); } vid.classList.toggle("is-paused", v.paused); }
    });
    document.addEventListener("scroll", e => {  // Instagram carousel dots follow the swipe
      const c = e.target; if (!c.classList || !c.classList.contains("igcar")) return;
      const i = Math.round(c.scrollLeft / c.clientWidth);
      c.parentElement.querySelectorAll(".igdots i").forEach((d, k) => d.classList.toggle("on", k === i));
    }, true);
  }

  g.MetaMock = { render, esc, wire };
})(window);
