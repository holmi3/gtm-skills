#!/usr/bin/env python3
"""brief_facts.py: one fact pack per account in scope, for the brief writers. Standard library only. Writes one file.

    python brief_facts.py --model model.json --file accounts.csv --evidence evidence.csv --out facts.jsonl

A pack holds only what the row and its evidence lines say: what the company is, the reasons it ranks (strongest
first, points removed), the signals, the likely owner from the model's first-match owner_rules, and what is unknown.
Writers (people or model subagents) write each brief from its pack alone, with no outside knowledge, and
check_briefs.py then holds every number in a brief to the pack.
"""
import argparse, csv, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import cond, blank, read  # noqa: E402


def newest_prefix(cols):
    sets = sorted({int(m.group(1)) for c in cols if (m := re.match(r"S(\d+)-total$", c))})
    return f"S{sets[-1]}-" if sets else None


def reasons(why):
    """'fit 33 = 12 segment 1 + 12 size (640) | prize ...' -> ['segment 1', 'size (640)', ...], strongest first."""
    items = []
    for part in why.split(" | "):
        if " = " not in part:
            continue
        body = part.split(" = ", 1)[1]
        for line in re.split(r" (?=[+-] \d)", body):
            m = re.match(r"[+-]?\s*(-?\d+(?:\.\d+)?)\s+(.*)", line.strip())
            if m and float(m.group(1)) != 0:
                sign = -1 if line.strip().startswith("-") else 1
                items.append((sign * float(m.group(1)), m.group(2)))
    return [t for _, t in sorted(items, key=lambda x: -x[0])]


def owner(row, rules):
    for r in rules:
        if all(cond(row, c) for c in r["when"]):
            return r
    return {"owner": "", "champion": "", "basis": "no owner rule matched"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True); ap.add_argument("--file", required=True)
    ap.add_argument("--evidence"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    cfg, key = model["brief"], model.get("key", "domain")
    rows, cols = read(a.file)
    p = newest_prefix(cols)
    if not p:
        sys.exit("no scored set on the file; run score.py --write first")
    ev = {}
    if a.evidence:
        for e in csv.DictReader(open(a.evidence, newline="", encoding="utf-8")):
            ev.setdefault(e[key], []).append({k: e[k] for k in ("field", "value", "quote", "url", "read_on", "confidence") if k in e})
    n = 0
    with open(a.out, "w", encoding="utf-8") as out:
        for r in rows:
            if r.get(p + "band") not in cfg["scope_bands"]:
                continue
            facts = {}
            for col, label in cfg["fields"].items():
                v = r.get(col, "")
                if blank(v):
                    continue
                facts[label] = cfg.get("value_labels", {}).get(col, {}).get(v, v)
            o = owner(r, model.get("owner_rules", []))
            missing = [x for x in (r.get(p + "missing") or "").split(";") if x]
            pack = {key: r[key], "company": r.get("company", ""), "band": r[p + "band"], "facts": facts,
                    "reasons_strongest_first": reasons(r.get(p + "why", "")),
                    "owner": o["owner"], "champion": o.get("champion", ""), "owner_basis": o["basis"],
                    "unknown": [model["parts"][m].get("unknown_note", m) for m in missing],
                    "evidence": ev.get(r[key], [])}
            out.write(json.dumps(pack, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} fact packs to {a.out}")


if __name__ == "__main__":
    main()
