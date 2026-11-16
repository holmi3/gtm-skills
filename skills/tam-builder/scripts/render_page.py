#!/usr/bin/env python3
"""render_page.py: one self-contained HTML page of the ranked list, for sales to read. Standard library only.

    python render_page.py --model model.json --file accounts.csv --out ranked.html [--evidence evidence.csv] [--title "..."]

Reads the newest S<n>- set. Shows band tiles (click to filter), a search box, the ranked table, and per account the
brief, the likely owner, each part's receipt and the evidence links. Opens from disk; no server, no network.
"""
import argparse, csv, html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import read  # noqa: E402

BANDS = [("hot", "personal outreach now"), ("warm", "after hot is done"), ("cold", "nurture only"),
         ("research", "not handed over until a page is read"), ("out", "disqualified, kept with its reason")]

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#fbfbf9;--fg:#1d1d1b;--muted:#6b6b66;--line:#e2e1dc;--card:#ffffff;--hot:#b4321e;--warm:#b07a12;--cold:#2f6690;--research:#6b6b66;--out:#9a9a94;--accent:#1d1d1b}
@media (prefers-color-scheme: dark){:root{--bg:#141413;--fg:#ecebe6;--muted:#a3a29c;--line:#2e2d2a;--card:#1c1c1a;--hot:#ef6f55;--warm:#e0b04a;--cold:#7fb2dc;--research:#a3a29c;--out:#77766f;--accent:#ecebe6}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:22px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 20px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-bottom:16px}
.tile{border:1px solid var(--line);background:var(--card);padding:10px 12px;cursor:pointer;text-align:left;color:inherit;font:inherit}
.tile b{display:block;font-size:24px}.tile span{color:var(--muted);font-size:13px}.tile[aria-pressed=true]{outline:2px solid var(--accent)}
input[type=search]{width:100%;padding:9px 10px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit;margin-bottom:12px}
.wrap{overflow-x:auto;border:1px solid var(--line);background:var(--card)}table{border-collapse:collapse;width:100%;min-width:680px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-size:12px;color:var(--muted);font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums}tr.row{cursor:pointer}tr.row:hover{background:color-mix(in srgb,var(--line) 35%,transparent)}
.chip{display:inline-block;padding:1px 8px;border:1px solid currentColor;font-size:12px}.hot{color:var(--hot)}.warm{color:var(--warm)}.cold{color:var(--cold)}.research{color:var(--research)}.out{color:var(--out)}
tr.detail td{background:var(--bg)}.detail p{margin:4px 0 10px}.detail ul{margin:4px 0 10px;padding-left:18px}.k{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
details.legend{margin:16px 0;border:1px solid var(--line);background:var(--card);padding:10px 12px}details.legend summary{cursor:pointer}
.legend table{min-width:0}a{color:inherit}
</style></head><body><main>
<h1>__TITLE__</h1><p class="sub">__SUB__</p>
<div class="tiles" id="tiles"></div>
<input type="search" id="q" placeholder="Search company, domain, owner or brief" aria-label="Search">
<div class="wrap"><table><thead><tr><th>#</th><th>Company</th><th>Band</th><th class="n">Total</th>__PARTHEADS__<th>Likely owner</th></tr></thead><tbody id="tb"></tbody></table></div>
<details class="legend"><summary>How to read this page</summary>__LEGEND__</details>
</main>
<script>
const DATA = __DATA__; const PARTS = __PARTS__;
let band = null, q = "", open = null;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function tiles(){const t=document.getElementById("tiles");t.innerHTML="";for(const [b,label] of __BANDS__){const n=DATA.filter(r=>r.band===b).length;const el=document.createElement("button");el.className="tile";el.setAttribute("aria-pressed",band===b);el.innerHTML=`<b class="${b}">${n}</b>${b}<br><span>${esc(label)}</span>`;el.onclick=()=>{band=band===b?null:b;render()};t.appendChild(el)}}
function render(){tiles();const tb=document.getElementById("tb");tb.innerHTML="";const ql=q.toLowerCase();let i=0;
 for(const r of DATA){if(band&&r.band!==band)continue;if(ql&&!(r.company+r.key+r.owner+r.brief).toLowerCase().includes(ql))continue;i++;
  const tr=document.createElement("tr");tr.className="row";tr.innerHTML=`<td class="n">${i}</td><td><b>${esc(r.company)}</b><br><span class="k">${esc(r.key)}</span></td><td><span class="chip ${r.band}">${r.band}</span></td><td class="n">${esc(r.total)}</td>`+PARTS.map(p=>`<td class="n">${esc(r.parts[p])}</td>`).join("")+`<td>${esc(r.owner)}</td>`;
  tr.onclick=()=>{open=open===r.key?null:r.key;render()};tb.appendChild(tr);
  if(open===r.key){const d=document.createElement("tr");d.className="detail";const ev=r.evidence.map(e=>`<li>${esc(e.field)}: "${esc(e.quote)}" <a href="${esc(e.url)}" rel="noopener">source</a>, read ${esc(e.read_on)} (${esc(e.confidence)})</li>`).join("");
   d.innerHTML=`<td></td><td colspan="${4+PARTS.length}">`+(r.brief?`<div class="k">Account brief</div><p>${esc(r.brief)}</p>`:"")+(r.owner?`<div class="k">Likely owner</div><p>${esc(r.owner)}${r.champion?", with the "+esc(r.champion)+" as champion":""}. <span class="k">${esc(r.owner_basis)}</span></p>`:"")+`<div class="k">Why it scores ${esc(r.total)} (${esc(r.confidence||"no")} confidence)</div><ul>${r.why.split(" | ").map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`+(ev?`<div class="k">Evidence</div><ul>${ev}</ul>`:"")+`</td>`;tb.appendChild(d)}}
 if(!i)tb.innerHTML=`<tr><td colspan="${5+PARTS.length}">No accounts match.</td></tr>`}
document.getElementById("q").oninput=e=>{q=e.target.value;render()};render();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True); ap.add_argument("--file", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--evidence"); ap.add_argument("--title", default="Ranked accounts")
    a = ap.parse_args()
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
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
              f"<tr><td class='hot'>hot</td><td>total {b['hot']} or more, medium or high confidence</td><td>personal outreach now</td></tr>"
              f"<tr><td class='warm'>warm</td><td>{b['warm']} to below {b['hot']}, medium or high confidence</td><td>after hot is done</td></tr>"
              f"<tr><td class='cold'>cold</td><td>below {b['warm']}, medium or high confidence</td><td>nurture only</td></tr>"
              "<tr><td class='research'>research</td><td>low confidence: no page read yet, or too little data</td><td>not handed over until a page is read</td></tr>"
              "<tr><td class='out'>out</td><td>disqualified (anti-ICP, customer, partner, competitor)</td><td>kept so nobody researches it again</td></tr></table>"
              "<p>Each part has a maximum: " + ", ".join(f"{x} {model['parts'][x]['max']}" for x in parts) +
              ". Fit and prize come from what the company is; the other parts only rank within that. Click any row for the brief, the receipt behind every point, and the sources.</p>")
    out = (PAGE.replace("__TITLE__", html.escape(a.title))
           .replace("__SUB__", html.escape(f"{len(rows)} accounts, scored by {model.get('name', 'the model')}"))
           .replace("__PARTHEADS__", "".join(f'<th class="n">{html.escape(x.capitalize())}</th>' for x in parts))
           .replace("__LEGEND__", legend)
           .replace("__BANDS__", json.dumps(BANDS))
           .replace("__PARTS__", json.dumps(parts))
           .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"wrote {a.out} ({len(data)} accounts)")


if __name__ == "__main__":
    main()
