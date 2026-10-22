/* Meta ad mockups: Facebook Feed, Instagram Feed and Instagram Stories/Reels.
   Approximations of how Meta renders each format — good enough to judge copy,
   crop and CTA, not pixel-exact. Every ad object comes from data/campaigns.json. */
(function (g) {
  "use strict";
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const PAGE = "Theodore Roosevelt Presidential Library", IG = "trlibrary", AV = "creative/brand/avatar.jpg";
  const domainOf = u => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (e) { return ""; } };

  // Truncation roughly where Meta adds "See more" / "more".
  function clip(t, n) {
    t = String(t || "");
    if (t.length <= n) return esc(t);
    const cut = t.slice(0, n).replace(/\s+\S*$/, "");
    return esc(cut) + '<span class="more">… See more</span>';
  }

  function media(m, ratio, extra) {
    if (!m) return `<div class="media" style="aspect-ratio:${ratio}"></div>`;
    const ph = extra && extra.placeholder ? '<span class="ph">PLACEHOLDER</span>' : "";
    const vid = m.type === "video"
      ? `<div class="play" data-yt="${esc(m.youtube)}" title="Play ${esc(m.title)}"><span></span></div><span class="dur">${esc(m.duration || "")}</span>` : "";
    return `<div class="media${m.type === "product" ? " prod" : ""}" style="aspect-ratio:${ratio}"><img loading="lazy" src="${esc(m.src)}" alt="${esc(m.title || m.alt || "")}">${vid}${ph}</div>`;
  }

  function cards(ad) {
    if (ad.format === "catalog") return (ad.products || []).map(p => ({ media: p, headline: p.title, desc: p.price }));
    return ad.cards || [];
  }

  function fbFeed(ad) {
    const head = `<div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${PAGE}</div><div class="sp">Sponsored · 🌐</div></div><div class="dots">···</div></div>`;
    const text = `<div class="tx">${clip(ad.primary, 125)}</div>`;
    const rx = `<div class="rx"><span>👍 Like</span><span>💬 Comment</span><span>↗ Share</span></div>`;
    if (ad.format === "carousel" || ad.format === "catalog") {
      const cs = cards(ad).map(c => `<div class="card">${media(c.media, "1/1")}<div class="cf"><div class="l"><div class="hl">${esc(c.headline)}</div><div class="ds">${esc(c.desc || "")}</div></div><div class="cta">${esc(ad.cta)}</div></div></div>`).join("");
      return `<div><p class="mock-label">Facebook Feed</p><div class="m fb">${head}${text}<div class="car">${cs}</div>${rx}</div></div>`;
    }
    const ratio = ad.format === "video" ? "16/9" : "1/1";
    return `<div><p class="mock-label">Facebook Feed</p><div class="m fb">${head}${text}${media(ad.media, ratio, ad)}
      <div class="link"><div class="l"><div class="dom">${esc(domainOf(ad.url))}</div><div class="hl">${esc(ad.headline)}</div><div class="ds">${esc(ad.desc || "")}</div></div><div class="cta">${esc(ad.cta)}</div></div>${rx}</div></div>`;
  }

  function igFeed(ad) {
    const head = `<div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${IG}</div><div class="sp">Sponsored</div></div><div class="dots">···</div></div>`;
    const multi = ad.format === "carousel" || ad.format === "catalog";
    const first = multi ? cards(ad)[0] : null;
    const m = multi ? media(first && first.media, "1/1") : media(ad.media, "4/5", ad);
    const dots = multi ? `<div class="igdots">${cards(ad).map(() => "<i></i>").join("")}</div>` : "";
    return `<div><p class="mock-label">Instagram Feed</p><div class="m ig">${head}${m}
      <div class="bar blue"><span>${esc(ad.cta)}</span><span>›</span></div>${dots}
      <div class="icons"><span>♡</span><span>💬</span><span>➤</span><span class="sv">🔖</span></div>
      <div class="cap"><b>${IG}</b>${clip(ad.primary, 90).replace("… See more", "… more")}</div></div></div>`;
  }

  // 9:16 video (scripts/vertical.py) plays inline in the Stories/Reels mock.
  function vertical(m, extra) {
    const ph = extra && extra.placeholder ? '<span class="ph">PLACEHOLDER</span>' : "";
    return `<div class="media" style="aspect-ratio:9/16"><video src="${esc(m.vertical.src)}" poster="${esc(m.vertical.poster)}" preload="none" playsinline muted loop onclick="this.paused?this.play():this.pause()" title="Click to play the 9:16 cut"></video><span class="vtag">▶ 9:16</span>${ph}</div>`;
  }

  function igStory(ad) {
    const multi = ad.format === "carousel" || ad.format === "catalog";
    const m = multi ? (cards(ad)[0] || {}).media : ad.media;
    const md = m && m.vertical ? vertical(m, ad) : media(m, "9/16", ad);
    return `<div><p class="mock-label">Stories / Reels${m && m.vertical ? " · vertical cut" : ""}</p><div class="m st"><div class="prog"></div>${md}
      <div class="hd"><img class="av" src="${AV}" alt=""><div><div class="nm">${IG}</div><div class="sp">Sponsored</div></div></div>
      <div class="bt"><div class="t">${esc(ad.primary)}</div><span class="c">${esc(ad.cta)}</span></div></div></div>`;
  }

  function render(ad) {
    const p = ad.placements || ["fb_feed", "ig_feed", "ig_story"];
    return `<div class="mocks">${p.includes("fb_feed") ? fbFeed(ad) : ""}${p.includes("ig_feed") ? igFeed(ad) : ""}${p.includes("ig_story") ? igStory(ad) : ""}</div>`;
  }

  g.MetaMock = { render, esc };
})(window);
