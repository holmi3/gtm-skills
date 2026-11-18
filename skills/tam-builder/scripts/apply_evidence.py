#!/usr/bin/env python3
"""apply_evidence.py: check what the page readers extracted against the saved pages, then fill the list. Standard library only.

    python apply_evidence.py --model model.json --extractions extractions.csv --pages pages \\
        --accounts accounts.csv --evidence-out evidence.csv --report evidence_check.csv [--dry-run] [--overwrite]

The extraction file has one line per fact (CSV or JSONL): domain, field, value, quote, url, confidence. A line is kept
only when all of these hold:
  - the url is a page saved by fetch_pages.py (so a person can open the same text later)
  - the quote appears word for word in that saved page (case, spacing, curly quotes and dashes ignored)
  - the value is on the field's closed list (model "fields", or the keys of the model's map rules, or yes/no for flags)
  - for a number field, the number is in the quote
  - a "none_found" or "no" value carries a quote that starts with [checked] and names what was read; it is checked
    against the saved page existing, not the text, because absence cannot be quoted
Kept lines go to --evidence-out (merged with what is already there). For each domain and field the best kept line
(high over medium over low, then the newest) fills the account's cell when it is blank or unknown. A cell that already
holds a different value is reported as a conflict and left alone (out of the evidence file too) unless --overwrite. Domains with a saved page get the
model's read column (for example page_read) set to yes. --report lists every line with what happened to it.
"""
import argparse, csv, json, re, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import read, write  # noqa: E402

RANK = {"high": 3, "medium": 2, "low": 1}
EV_COLS = ["domain", "field", "value", "quote", "url", "read_on", "confidence"]
ABSENT = {"none_found", "no"}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                                   " ": " "}))
    return re.sub(r"\s+", " ", s).strip(" .\"'")


def url_key(u):
    return re.sub(r"^https?://(www\.)?", "", (u or "").strip()).split("#")[0].rstrip("/").lower()


def load_pages(folder):
    """url_key -> (text, read_on, domain) for every saved page."""
    pages = {}
    for f in Path(folder).glob("*/*.txt"):
        raw = f.read_text(encoding="utf-8")
        head, _, body = raw.partition("\n\n")
        meta = dict(ln.split(": ", 1) for ln in head.splitlines() if ": " in ln)
        if "URL" in meta:
            pages[url_key(meta["URL"])] = (body, meta.get("READ", ""), f.parent.name)
    return pages


def field_rules(model):
    """field -> ("list", allowed values) or ("number", None), from model["fields"] first, then the rules."""
    out = {}
    for part in model["parts"].values():
        for r in part["rules"]:
            col = r.get("column")
            if not col:
                continue
            if r["type"] == "map":
                out.setdefault(col, ("list", set(r["points"]) | {"unknown"}))
            elif r["type"] == "flag":
                out.setdefault(col, ("list", {str(r.get("equals", "yes")), "yes", "no", "unknown"}))
            elif r["type"] == "bands":
                out.setdefault(col, ("number", None))
    for col, spec in (model.get("fields") or {}).items():
        out[col] = ("number", None) if spec == "number" else ("list", set(spec) | {"unknown"})
    return out


def load_extractions(path):
    p = Path(path)
    if p.suffix.lower() == ".jsonl":
        return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def check(e, pages, rules):
    """Returns (status, read_on). status 'ok' means keep."""
    field, value, quote = e.get("field", ""), str(e.get("value", "")).strip(), e.get("quote", "")
    page = pages.get(url_key(e.get("url")))
    if field not in rules:
        return "rejected: field is not in the model", ""
    if not page:
        return "rejected: url is not a saved page", ""
    text, read_on, domain = page
    if domain.split(":")[0] != e.get("domain", "").split(":")[0]:
        return "rejected: page belongs to another domain", read_on
    kind, allowed = rules[field]
    if kind == "list" and value not in allowed:
        return f"rejected: '{value}' is not on the list ({', '.join(sorted(allowed))})", read_on
    if e.get("confidence") not in RANK:
        return "rejected: confidence must be high, medium or low", read_on
    if value in ABSENT:
        return ("ok" if quote.startswith("[checked]") else "rejected: an absent value needs a [checked] note"), read_on
    if kind == "number":
        num = value.replace(",", "")
        if not re.fullmatch(r"\d+(\.\d+)?", num):
            return "rejected: not a number", read_on
        if num not in re.sub(r"(?<=\d),(?=\d{3})", "", quote):
            return "rejected: the number is not in the quote", read_on
    q = norm(quote)
    if len(q.split()) < 3:
        return "rejected: quote shorter than three words", read_on
    if len(q.split()) > 40:
        return "rejected: quote longer than 40 words; quote the sentence that says it", read_on
    if q not in norm(text):
        return "rejected: quote not found on the saved page", read_on
    return "ok", read_on


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True); ap.add_argument("--extractions", required=True)
    ap.add_argument("--pages", required=True); ap.add_argument("--accounts", required=True)
    ap.add_argument("--evidence-out", required=True); ap.add_argument("--report", required=True)
    ap.add_argument("--dry-run", action="store_true", help="report only; change no file but the report")
    ap.add_argument("--overwrite", action="store_true", help="let a better-sourced value replace a different one")
    a = ap.parse_args()
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    key = model.get("key", "domain")
    read_col = (model.get("confidence") or {}).get("read_column")
    pages, rules = load_pages(a.pages), field_rules(model)
    lines = load_extractions(a.extractions)

    report, kept = [], []
    for e in lines:
        status, read_on = check(e, pages, rules)
        e = {**e, "value": str(e.get("value", "")).strip(), "read_on": e.get("read_on") or read_on}
        report.append({**{c: e.get(c, "") for c in EV_COLS}, "status": status})
        if status == "ok":
            kept.append((e, report[-1]))

    rows, cols = read(a.accounts)
    by_key = {r[key]: r for r in rows}
    best = {}
    for e, rep in kept:
        k = (e["domain"], e["field"])
        if k not in best or (RANK[e["confidence"]], e["read_on"]) > (RANK[best[k][0]["confidence"]], best[k][0]["read_on"]):
            best[k] = (e, rep)
    for e, rep in kept:
        if best[(e["domain"], e["field"])][1] is not rep:
            rep["status"] = "kept as evidence; a stronger line set the value"
    filled = conflicts = 0
    for (dom, field), (e, rep) in best.items():
        r = by_key.get(dom)
        if r is None:
            rep["status"] = "kept as evidence; domain is not on the list"
            continue
        if field not in cols:
            cols.append(field)
        cur = (r.get(field) or "").strip()
        if cur == e["value"]:
            rep["status"] = "confirmed: matches the list"
        elif cur in ("", "unknown") or a.overwrite:
            rep["status"] = f"applied (was '{cur or 'blank'}')"
            r[field] = e["value"]
            filled += 1
        else:
            rep["status"] = f"conflict: list says '{cur}', left as is"
            conflicts += 1
    read_domains = {d for _, _, d in pages.values()}
    marked = 0
    if read_col:
        if read_col not in cols:
            cols.append(read_col)
        for r in rows:
            if r[key] in read_domains and r.get(read_col) != "yes":
                r[read_col] = "yes"
                marked += 1

    with open(a.report, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EV_COLS + ["status"], lineterminator="\n")
        w.writeheader(); w.writerows(report)
    if not a.dry_run:
        old = list(csv.DictReader(open(a.evidence_out, newline="", encoding="utf-8"))) if Path(a.evidence_out).exists() else []
        seen = {(o["domain"], o["field"], url_key(o["url"]), norm(o["quote"])) for o in old}
        new = [e for e, rep in kept if not rep["status"].startswith("conflict")
               and (e["domain"], e["field"], url_key(e["url"]), norm(e["quote"])) not in seen]
        with open(a.evidence_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=EV_COLS, lineterminator="\n", extrasaction="ignore")
            w.writeheader(); w.writerows(old + new)
        write(a.accounts, rows, cols)
    bad = sum(1 for r in report if r["status"].startswith("rejected"))
    print(f"{len(lines)} lines: {len(kept)} kept, {bad} rejected; {filled} cells filled, {conflicts} conflicts, "
          f"{marked} rows marked {read_col}=yes{' (dry run, nothing written but the report)' if a.dry_run else ''}. "
          f"Report: {a.report}")


if __name__ == "__main__":
    main()
