// theme_probe.js: read a rendered page's look from computed styles. Returns one JSON object.
// Run it in the client's homepage after it has loaded: in a browser tool ("run JavaScript on the page"),
// or from brand_theme.py, which runs it through Playwright. Read-only: it changes nothing on the page.
(() => {
  const rgb = s => { const m = (s || "").match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?/); return m ? { r: +m[1], g: +m[2], b: +m[3], a: m[4] === undefined ? 1 : +m[4] } : null; };
  const hex = c => "#" + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, "0")).join("");
  const solid = s => { const c = rgb(s); return c && c.a > 0.5 ? hex(c) : null; };
  const visible = el => { const r = el.getBoundingClientRect(); const st = getComputedStyle(el); return r.width > 4 && r.height > 4 && st.visibility !== "hidden" && st.display !== "none" && +st.opacity > 0.2; };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = solid(getComputedStyle(e).backgroundColor); if (c) return c; } return "#ffffff"; };
  const first = sel => [...document.querySelectorAll(sel)].find(visible) || null;
  const font = el => el ? getComputedStyle(el).fontFamily : null;

  // Colors weighted by on-screen area (backgrounds) and by text length (text colors), top of page only.
  const area = {}, ink = {};
  for (const el of document.querySelectorAll("body *")) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.top > 2400) continue;
    const st = getComputedStyle(el);
    const bg = solid(st.backgroundColor);
    if (bg) area[bg] = (area[bg] || 0) + Math.min(r.width * r.height, 2e6);
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join("");
    const fg = solid(st.color);
    if (fg && own.length) ink[fg] = (ink[fg] || 0) + own.length;
  }
  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([c, w]) => ({ color: c, weight: Math.round(w) }));

  // The main call-to-action: the most colorful visible button or button-like link near the top.
  const sat = h => { const c = rgb(h.replace(/^#(..)(..)(..)$/, (_, r, g, b) => `rgb(${parseInt(r, 16)},${parseInt(g, 16)},${parseInt(b, 16)})`)); const mx = Math.max(c.r, c.g, c.b), mn = Math.min(c.r, c.g, c.b); return mx ? (mx - mn) / mx : 0; };
  const ctas = [...document.querySelectorAll("a, button")].filter(visible).map(el => {
    const st = getComputedStyle(el), bg = solid(st.backgroundColor);
    return bg ? { el, bg, fg: solid(st.color), radius: st.borderRadius, top: el.getBoundingClientRect().top } : null;
  }).filter(x => x && x.top < 1200 && x.bg !== bgOf(document.body));
  ctas.sort((a, b) => sat(b.bg) - sat(a.bg));
  const cta = ctas[0] || null;

  const body = document.body, h1 = first("h1") || first("h2"), link = first("main a, a");
  return {
    url: location.href,
    title: document.title,
    read_on: new Date().toISOString().slice(0, 10),
    page_bg: bgOf(body),
    text: solid(getComputedStyle(body).color) || (top(ink, 1)[0] || {}).color,
    heading_color: h1 ? solid(getComputedStyle(h1).color) : null,
    link_color: link ? solid(getComputedStyle(link).color) : null,
    cta: cta ? { bg: cta.bg, fg: cta.fg, radius: cta.radius, label: (cta.el.textContent || "").trim().slice(0, 40) } : null,
    fonts: { body: font(body), heading: font(h1) },
    heading_weight: h1 ? getComputedStyle(h1).fontWeight : null,
    font_links: [...document.querySelectorAll('link[href*="fonts.googleapis.com"], link[href*="fonts.bunny.net"]')].map(l => l.href),
    theme_color_meta: (document.querySelector('meta[name="theme-color"]') || {}).content || null,
    background_palette: top(area, 8),
    text_palette: top(ink, 6),
    prefers_dark_site: (() => { const c = rgb(getComputedStyle(body).backgroundColor) || { r: 255, g: 255, b: 255 }; return (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b) < 90; })()
  };
})()
