#!/usr/bin/env python3
"""render_page.py: one self-contained HTML page of the ranked list, for sales to read. Standard library only.

    python render_page.py --model model.json --file accounts.csv --out ranked.html [--evidence evidence.csv] [--title "..."]
                          [--theme theme.json]

Reads the newest S<n>- set. Shows band tiles (click to filter), a search box, the ranked table, and per account the
brief, the likely owner, each part's receipt and the evidence links. Opens from disk; no server. The only network
request is the client's web font, when the theme names one on Google Fonts or Bunny Fonts.

--theme takes the file brand_theme.py writes: the client's colors for a light and a dark page, fonts, corner radius
and which mode opens first. Without it the page uses a neutral built-in look. Either way there is a Light / Dark switch.
"""
import argparse, csv, html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import read  # noqa: E402

# The built-in look when no --theme is given. Same token names brand_theme.py writes.
DEFAULT_THEME = {
    "client": None, "default_mode": None, "radius": "4px",
    "fonts": {"body": "system-ui, -apple-system, 'Segoe UI', sans-serif", "heading": None, "heading_weight": "650", "css_url": None},
    "light": {"bg": "#fbfbf9", "surface": "#ffffff", "fg": "#1d1d1b", "heading": "#1d1d1b", "muted": "#64635e", "line": "#e2e1dc",
              "accent": "#1d1d1b", "accent_fg": "#ffffff", "link": "#1d1d1b", "hot_bg": "#b4321e", "hot_fg": "#ffffff",
              "warm_bg": "#f0c463", "warm_fg": "#1d1d1b", "cold": "#2f6690", "research": "#64635e", "out": "#86857f"},
    "dark": {"bg": "#141413", "surface": "#1c1c1a", "fg": "#ecebe6", "heading": "#ecebe6", "muted": "#a3a29c", "line": "#2e2d2a",
             "accent": "#ecebe6", "accent_fg": "#141413", "link": "#ecebe6", "hot_bg": "#ef6f55", "hot_fg": "#141413",
             "warm_bg": "#e0b04a", "warm_fg": "#141413", "cold": "#7fb2dc", "research": "#a3a29c", "out": "#8a8983"},
}
TOKENS = ["bg", "surface", "fg", "heading", "muted", "line", "accent", "accent_fg", "link", "hot_bg", "hot_fg", "warm_bg",
          "warm_fg", "cold", "research", "out"]
FONT_HOSTS = ("https://fonts.googleapis.com/", "https://fonts.bunny.net/")
SAFE = re.compile(r"^[#\w\s.,'\"()%-]*$")  # what a font stack may contain; anything else is dropped
COLOR = re.compile(r"^(#[0-9a-fA-F]{3,8}|(rgb|hsl)a?\([\d.,%\s/]+\))$")  # what a color token may be


def css_vars(t, fallback):
    out = []
    for k in TOKENS:
        v = str(t.get(k) or fallback[k])
        out.append(f"--{k.replace('_', '-')}:{v if COLOR.match(v) else fallback[k]}")
    return ";".join(out)


def theme_css(theme):
    d = DEFAULT_THEME
    th = theme or d
    fonts = {**d["fonts"], **{k: v for k, v in (th.get("fonts") or {}).items() if v}}
    body = fonts["body"] if SAFE.match(fonts["body"]) else d["fonts"]["body"]
    if "sans-serif" not in body and "serif" not in body:
        body += ", system-ui, sans-serif"
    head = fonts.get("heading") or body
    head = head if SAFE.match(head) else body
    weight = str(fonts.get("heading_weight") or "650")
    weight = weight if weight.isdigit() else "650"
    radius = str(th.get("radius") or d["radius"])
    radius = radius if re.match(r"^\d+(\.\d+)?px$", radius) else d["radius"]
    url = fonts.get("css_url") or ""
    link = f"@import url('{url}');" if url.startswith(FONT_HOSTS) and "'" not in url else ""
    mode = th.get("default_mode") if th.get("default_mode") in ("light", "dark") else None
    return {"__FONTLINK__": link, "__LIGHT__": css_vars(th.get("light") or {}, d["light"]),
            "__DARK__": css_vars(th.get("dark") or {}, d["dark"]), "__RADIUS__": radius, "__BODYFONT__": body,
            "__HEADFONT__": head, "__HEADWEIGHT__": weight, "__MODEATTR__": f' data-theme="{mode}"' if mode else ""}


BANDS = [("hot", "personal outreach now"), ("warm", "after hot is done"), ("cold", "nurture only"),
         ("research", "not handed over until a page is read"), ("out", "disqualified, kept with its reason")]

PAGE = """<!doctype html>
<html lang="en"__MODEATTR__><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
__FONTLINK__
:root{__LIGHT__;--radius:__RADIUS__;--body-font:__BODYFONT__;--heading-font:__HEADFONT__;--heading-weight:__HEADWEIGHT__;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){__DARK__;color-scheme:dark}}
:root[data-theme=dark]{__DARK__;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 var(--body-font)}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}
header{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;border-bottom:3px solid var(--accent);padding-bottom:12px;margin-bottom:16px}
h1{font:var(--heading-weight) 24px/1.2 var(--heading-font);color:var(--heading);margin:0 0 4px}.sub{color:var(--muted);margin:0}
.mode{flex:none;background:var(--accent);color:var(--accent-fg);border:0;border-radius:var(--radius);padding:7px 14px;font:600 13px/1.2 var(--body-font);cursor:pointer}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-bottom:16px}
.tile{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:10px 12px;cursor:pointer;text-align:left;color:inherit;font:inherit}
.tile b{display:block;font-size:24px;line-height:1.2;margin-bottom:4px}.tile span.l{display:block;color:var(--muted);font-size:13px;margin-top:4px}.tile[aria-pressed=true]{outline:2px solid var(--fg);outline-offset:-1px}
input[type=search]{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);color:var(--fg);font:inherit;margin-bottom:12px}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}table{border-collapse:collapse;width:100%;min-width:680px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-size:12px;color:var(--muted);font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums}tr.row{cursor:pointer}tr.row:hover{background:color-mix(in srgb,var(--line) 35%,transparent)}
.chip{display:inline-block;padding:1px 9px;border:1px solid currentColor;border-radius:min(var(--radius),999px);font-size:12px;font-weight:600}
.chip.hot{background:var(--hot-bg);color:var(--hot-fg);border-color:var(--hot-bg)}.chip.warm{background:var(--warm-bg);color:var(--warm-fg);border-color:var(--warm-bg)}
.chip.cold{color:var(--cold)}.chip.research{color:var(--research);border-style:dashed}.chip.out{color:var(--out)}
tr.detail td{background:var(--bg)}.detail p{margin:4px 0 10px}.detail ul{margin:4px 0 10px;padding-left:18px}.k{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
details.legend{margin:16px 0;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);padding:10px 12px}details.legend summary{cursor:pointer}
.legend table{min-width:0}a{color:var(--link)}footer{color:var(--muted);font-size:12px;margin-top:24px}
</style></head><body><main>
<header><div><h1>__TITLE__</h1><p class="sub">__SUB__</p></div><button class="mode" id="mode" type="button">Dark</button></header>
<div class="tiles" id="tiles"></div>
<input type="search" id="q" placeholder="Search company, domain, owner or brief" aria-label="Search">
<div class="wrap"><table><thead><tr><th>#</th><th>Company</th><th>Band</th><th class="n">Total</th>__PARTHEADS__<th>Likely owner</th></tr></thead><tbody id="tb"></tbody></table></div>
<details class="legend"><summary>How to read this page</summary>__LEGEND__</details>
<footer>__FOOT__</footer>
</main>
<script>
const DATA = __DATA__; const PARTS = __PARTS__;
let band = null, q = "", open = null;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function tiles(){const t=document.getElementById("tiles");t.innerHTML="";for(const [b,label] of __BANDS__){const n=DATA.filter(r=>r.band===b).length;const el=document.createElement("button");el.className="tile";el.setAttribute("aria-pressed",band===b);el.innerHTML=`<b>${n}</b><span class="chip ${b}">${b}</span><span class="l">${esc(label)}</span>`;el.onclick=()=>{band=band===b?null:b;render()};t.appendChild(el)}}
function render(){tiles();const tb=document.getElementById("tb");tb.innerHTML="";const ql=q.toLowerCase();let i=0;
 for(const r of DATA){if(band&&r.band!==band)continue;if(ql&&!(r.company+r.key+r.owner+r.brief).toLowerCase().includes(ql))continue;i++;
  const tr=document.createElement("tr");tr.className="row";tr.innerHTML=`<td class="n">${i}</td><td><b>${esc(r.company)}</b><br><span class="k">${esc(r.key)}</span></td><td><span class="chip ${r.band}">${r.band}</span></td><td class="n">${esc(r.total)}</td>`+PARTS.map(p=>`<td class="n">${esc(r.parts[p])}</td>`).join("")+`<td>${esc(r.owner)}</td>`;
  tr.onclick=()=>{open=open===r.key?null:r.key;render()};tb.appendChild(tr);
  if(open===r.key){const d=document.createElement("tr");d.className="detail";const ev=r.evidence.map(e=>`<li>${esc(e.field)}: "${esc(e.quote)}" <a href="${esc(e.url)}" rel="noopener">source</a>, read ${esc(e.read_on)} (${esc(e.confidence)})</li>`).join("");
   d.innerHTML=`<td></td><td colspan="${4+PARTS.length}">`+(r.brief?`<div class="k">Account brief</div><p>${esc(r.brief)}</p>`:"")+(r.owner?`<div class="k">Likely owner</div><p>${esc(r.owner)}${r.champion?", with the "+esc(r.champion)+" as champion":""}. <span class="k">${esc(r.owner_basis)}</span></p>`:"")+`<div class="k">Why it scores ${esc(r.total)} (${esc(r.confidence||"no")} confidence)</div><ul>${r.why.split(" | ").map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`+(ev?`<div class="k">Evidence</div><ul>${ev}</ul>`:"")+`</td>`;tb.appendChild(d)}}
 if(!i)tb.innerHTML=`<tr><td colspan="${5+PARTS.length}">No accounts match.</td></tr>`}
document.getElementById("q").oninput=e=>{q=e.target.value;render()};render();
const root=document.documentElement,mb=document.getElementById("mode");
const isDark=()=>root.dataset.theme?root.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;
const label=()=>{mb.textContent=isDark()?"Light":"Dark";mb.setAttribute("aria-label","Switch to "+mb.textContent.toLowerCase()+" mode")};
mb.onclick=()=>{root.dataset.theme=isDark()?"light":"dark";label()};label();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True); ap.add_argument("--file", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--evidence"); ap.add_argument("--title", default="Ranked accounts")
    ap.add_argument("--theme", help="theme.json from brand_theme.py; leave out for the built-in look")
    a = ap.parse_args()
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    theme = json.loads(Path(a.theme).read_text(encoding="utf-8")) if a.theme else None
    key, parts = model.get("key", "domain"), list(model["parts"])
    rows, cols = read(a.file)
    sets = sorted({int(m.group(1)) for c in cols if (m := re.match(r"S(\d+)-total$", c))})
    if not sets:
        sys.exit("no scored set on the file; run score.py --write first")
    p = f"S{sets[-1]}-"
    ev = {}
    if a.evidence:
        for e in csv.DictReader(open(a.evidence, newline="", encoding="utf-8")):
            ev.setdefault(e[key], []).append(e)
    order = {b: i for i, (b, _) in enumerate(BANDS)}
    data = []
    for r in rows:
        data.append({"key": r[key], "company": r.get("company", r[key]), "band": r.get(p + "band", ""),
                     "total": r.get(p + "total", ""), "confidence": r.get(p + "confidence", ""),
                     "parts": {x: r.get(p + x, "") for x in parts}, "why": r.get(p + "why", ""),
                     "brief": r.get("brief", ""), "owner": r.get("owner", ""), "champion": r.get("champion", ""),
                     "owner_basis": r.get("owner_basis", ""), "evidence": ev.get(r[key], [])})
    data.sort(key=lambda d: (order.get(d["band"], 9), -float(d["total"] or 0)))
    b = model["bands"]
    legend = ("<table><tr><th>Band</th><th>Rule</th><th>What happens</th></tr>"
              f"<tr><td><span class='chip hot'>hot</span></td><td>total {b['hot']} or more, medium or high confidence</td><td>personal outreach now</td></tr>"
              f"<tr><td><span class='chip warm'>warm</span></td><td>{b['warm']} to below {b['hot']}, medium or high confidence</td><td>after hot is done</td></tr>"
              f"<tr><td><span class='chip cold'>cold</span></td><td>below {b['warm']}, medium or high confidence</td><td>nurture only</td></tr>"
              "<tr><td><span class='chip research'>research</span></td><td>low confidence: no page read yet, or too little data</td><td>not handed over until a page is read</td></tr>"
              "<tr><td><span class='chip out'>out</span></td><td>disqualified (anti-ICP, customer, partner, competitor)</td><td>kept so nobody researches it again</td></tr></table>"
              "<p>Each part has a maximum: " + ", ".join(f"{x} {model['parts'][x]['max']}" for x in parts) +
              ". Fit and prize come from what the company is; the other parts only rank within that. Click any row for the brief, the receipt behind every point, and the sources.</p>")
    sub = f"{len(rows)} accounts, scored by {model.get('name', 'the model')}"
    foot = "Built from public sources. Every point has a receipt; click a row to see it."
    if theme and theme.get("client"):
        sub = f"Prepared for {theme['client']}. " + sub
        foot += f" Colors and type follow {theme['client']}'s website" + (f", read {theme['read_on']}." if theme.get("read_on") else ".")
    out = PAGE
    for k, v in theme_css(theme).items():
        out = out.replace(k, v)
    out = (out.replace("__TITLE__", html.escape(a.title))
           .replace("__SUB__", html.escape(sub)).replace("__FOOT__", html.escape(foot))
           .replace("__PARTHEADS__", "".join(f'<th class="n">{html.escape(x.capitalize())}</th>' for x in parts))
           .replace("__LEGEND__", legend)
           .replace("__BANDS__", json.dumps(BANDS))
           .replace("__PARTS__", json.dumps(parts))
           .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"wrote {a.out} ({len(data)} accounts, {'theme for ' + str(theme.get('client')) if theme else 'built-in look'})")


if __name__ == "__main__":
    main()
