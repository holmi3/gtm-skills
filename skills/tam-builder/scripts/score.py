#!/usr/bin/env python3
"""score.py: deterministic account scoring from a JSON model. Standard library only.

The model file holds every weight; this script holds no numbers of its own. A model (or a person) never picks a
score: the same table applies to every row, and every row carries a receipt of the lines that gave its points.

    python score.py --model model.json --file accounts.csv                 # dry run: distribution and top 10, writes nothing
    python score.py --model model.json --file accounts.csv --test a.example b.example   # arithmetic for named rows
    python score.py --model model.json --file accounts.csv --write         # write set S1- (fit, prize, ..., total, band, why)
    python score.py --model model.json --file test_set.csv --write --next  # write the next free set (S2-, S3-, ...)
    python score.py --model model.json --file test_set.csv --write --prefix S2-   # rerun one set in place
    python score.py --model model.json --file test_set.csv --groups        # group ranges per set, separation check
    python score.py --check                                                # self-test on three made-up rows

Earlier sets are never overwritten unless named with --prefix. The plain `band` column always follows the set just
written. Use --as-of YYYY-MM-DD to fix "today" for recency (default: today), so a rerun is reproducible.
"""
import argparse, csv, datetime as dt, json, re, sys
from pathlib import Path

UNKNOWN = {"", "unknown", "n/a", "na", "none", "null", "?"}
PARTS_DEFAULT = ["fit", "prize", "awareness", "timing"]
SET_COLS = ["total", "confidence", "band", "missing", "why", "scored_on"]


# ---------- values ----------
def blank(v):
    return v is None or str(v).strip().lower() in UNKNOWN


def num(v):
    if blank(v):
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return None


def parse_date(v):
    if blank(v):
        return None
    try:
        return dt.date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        return None


def fmt(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.1f}"


def cond(row, c):
    """One condition: {"column", "op", "value"}. ops: eq, ne, in, not_in, nonblank, blank, gte, lt, contains."""
    v, op, want = row.get(c["column"], ""), c.get("op", "eq"), c.get("value")
    s = str(v).strip().lower()
    if op == "nonblank": return not blank(v)
    if op == "blank": return blank(v)
    if op == "eq": return s == str(want).lower()
    if op == "ne": return s != str(want).lower()
    if op == "in": return s in {str(w).lower() for w in want}
    if op == "not_in": return s not in {str(w).lower() for w in want}
    if op == "contains": return any(str(w).lower() in s for w in (want if isinstance(want, list) else [want]))
    n = num(v)
    if n is None: return False
    if op == "gte": return n >= float(want)
    if op == "lt": return n < float(want)
    raise ValueError(f"unknown op {op}")


def step_points(x, steps):
    """steps: [{"min": a, "max": b, "points": p}], first match wins; max may be omitted."""
    for s in steps:
        lo, hi = s.get("min"), s.get("max")
        if (lo is None or x >= lo) and (hi is None or x <= hi):
            return s["points"]
    return 0


def recency(row, rec, as_of):
    d = parse_date(row.get(rec["column"]))
    if d is None:
        return rec.get("unknown", 1.0), "date unknown"
    days = (as_of - d).days
    for limit, mult in rec["multipliers"]:
        if limit is None or days <= limit:
            return mult, f"last {d.isoformat()}"
    return rec["multipliers"][-1][1], f"last {d.isoformat()}"


# ---------- one rule ----------
def apply_rule(row, r, as_of):
    """Returns (points, receipt or None, known). known=False means the rule's input was missing."""
    t, label = r["type"], r.get("label", r.get("column", ""))
    if "only_if" in r and not all(cond(row, c) for c in r["only_if"]):
        return 0, None, True                       # rule does not apply to this row (for example a count of another kind)
    if t == "map":
        v = row.get(r["column"], "")
        if blank(v): return 0, None, False
        vals = [x.strip().lower() for x in str(v).split(r.get("split", ";"))] if r.get("best_of") else [str(v).strip().lower()]
        pts = max((r["points"].get(x, r.get("default", 0)) for x in vals), default=0)
        shown = r.get("names", {}).get(str(v).strip().lower(), f"{label} {v}".strip())
        return pts, (f"{fmt(pts)} {shown}" if pts else None), True
    if t == "flag":
        v = row.get(r["column"], "")
        if blank(v): return 0, None, False
        hit = cond(row, {"column": r["column"], "op": r.get("op", "eq"), "value": r.get("equals", "yes")})
        pts = r["points"] if hit else 0
        return pts, (f"{fmt(pts)} {label}" if hit and pts else None), True
    if t == "bands":
        x = num(row.get(r["column"]))
        if x is None: return 0, None, False
        pts = step_points(x, r["steps"])
        note = f"{fmt(x)}"
        if pts and "recency" in r:
            mult, why = recency(row, r["recency"], as_of)
            pts, note = round(pts * mult, 1), f"{note}, {why}, x{mult}"
        return pts, (f"{fmt(pts)} {label} ({note})" if pts else None), True
    if t == "ratio":
        a, b = num(row.get(r["num"])), num(row.get(r["den"]))
        if a is None or not b: return 0, None, False
        share = a / b
        pts = step_points(share, r["steps"])
        return pts, (f"{fmt(pts)} {label} ({share:.0%})" if pts else None), True
    if t == "count_of":
        hits = [c["column"] for c in r["any"] if cond(row, c)]
        known = any(not blank(row.get(c["column"])) for c in r["any"])
        pts = min(len(hits) * r["each"], r.get("max", 99))
        return pts, (f"{fmt(pts)} {label} ({', '.join(hits)})" if pts else None), known
    raise ValueError(f"unknown rule type {t}")


# ---------- one row ----------
def score_row(row, model, as_of):
    parts = list(model["parts"])
    out = {"parts": {}, "receipts": [], "missing": []}
    for d in model.get("disqualify", []):
        if cond(row, d):
            reason = row.get(d["column"]) if d.get("reason") == "from_column" else d["reason"]
            for p in parts: out["parts"][p] = 0
            out.update(total=0, confidence="", band="out", disqualified=reason, why=f"disqualified: {reason}")
            return out
    for p in parts:
        spec, pts, known = model["parts"][p], 0.0, False
        lines = []
        for r in spec["rules"]:
            got, rec, k = apply_rule(row, r, as_of)
            known |= k
            pts += got
            if rec: lines.append(rec)
        pts = max(0.0, min(pts, spec["max"]))
        out["parts"][p] = round(pts, 1)
        if known:
            out["receipts"].append(f"{p} {fmt(pts)} = " + (join_lines(lines) if lines else "0"))
        else:
            out["missing"].append(p)
            out["receipts"].append(f"{p} unknown ({spec.get('unknown_note', 'no data')})")
    out["total"] = round(sum(out["parts"].values()), 1)
    out["confidence"] = confidence(row, model, len(parts) - len(out["missing"]))
    out["band"] = band(out["total"], out["confidence"], model["bands"])
    out["disqualified"] = ""
    out["why"] = " | ".join(out["receipts"])
    return out


def join_lines(lines):
    """'12 segment 1', '-10 model b2c' -> '12 segment 1 - 10 model b2c'."""
    out = lines[0]
    for l in lines[1:]:
        out += f" - {l[1:]}" if l.startswith("-") else f" + {l}"
    return out


def confidence(row, model, known_parts):
    c = model.get("confidence", {})
    read = c.get("read_column")
    page_read = (not read) or str(row.get(read, "")).strip().lower() == "yes"
    if not page_read or known_parts < c.get("min_known_parts", 3):
        return "low"
    quotable = [q for q in c.get("quotable", []) if cond(row, q)]
    return "high" if quotable else "medium"


def band(total, conf, b):
    if conf not in ("medium", "high"):
        return "research"
    return "hot" if total >= b["hot"] else "warm" if total >= b["warm"] else "cold"


# ---------- files ----------
def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows, (list(rows[0].keys()) if rows else [])


def write(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def sets_in(cols):
    return sorted({int(m.group(1)) for c in cols if (m := re.match(r"S(\d+)-total$", c))})


def set_columns(prefix, parts):
    return [prefix + p for p in parts] + [prefix + c for c in SET_COLS]


def groups_report(rows, cols, gap):
    ok_all = True
    for n in sets_in(cols):
        p = f"S{n}-"
        by = {}
        for r in rows:
            g, t = r.get("test_group", ""), num(r.get(p + "total"))
            if g and t is not None:
                by.setdefault(g, []).append(t)
        order = [g for g in ("strong", "decent", "bad") if g in by]
        print(f"\n{p}  " + "  ".join(f"{g}: {min(by[g]):.1f} to {max(by[g]):.1f} (median {sorted(by[g])[len(by[g])//2]:.1f})" for g in order))
        sep = all(min(by[a]) >= max(by[b]) + gap for a, b in zip(order, order[1:]))
        print(f"    separation (each group's lowest >= next group's highest + {gap}): {'PASS' if sep else 'FAIL'}")
        for a, b in zip(order, order[1:]):
            margin = min(by[a]) - max(by[b])
            print(f"    {a} lowest - {b} highest = {margin:+.1f}")
        ok_all = sep
    return ok_all


def self_check():
    model = {
        "parts": {
            "fit": {"max": 40, "rules": [{"type": "map", "column": "segment", "points": {"1": 12}},
                                         {"type": "bands", "column": "employees", "label": "size", "steps": [{"min": 200, "max": 5000, "points": 12}]}]},
            "timing": {"max": 20, "rules": [{"type": "flag", "column": "funding_12m", "points": 4, "label": "funding"}]},
        },
        "disqualify": [{"column": "employees", "op": "lt", "value": 20, "reason": "under_20_employees"}],
        "confidence": {"min_known_parts": 1},
        "bands": {"hot": 60, "warm": 45},
    }
    day = dt.date(2026, 1, 15)
    perfect = score_row({"segment": "1", "employees": "800", "funding_12m": "yes"}, model, day)
    assert perfect["total"] == 28 and perfect["parts"]["fit"] == 24, perfect
    dq = score_row({"segment": "1", "employees": "12", "funding_12m": "yes"}, model, day)
    assert dq["band"] == "out" and dq["disqualified"] == "under_20_employees", dq
    gap = score_row({"segment": "1", "employees": "800", "funding_12m": ""}, model, day)
    assert gap["missing"] == ["timing"] and "timing unknown" in gap["why"], gap
    print("check: 3 of 3 passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model"); ap.add_argument("--file")
    ap.add_argument("--write", action="store_true"); ap.add_argument("--next", action="store_true")
    ap.add_argument("--prefix"); ap.add_argument("--test", nargs="*")
    ap.add_argument("--groups", action="store_true"); ap.add_argument("--gap", type=float, default=5)
    ap.add_argument("--check", action="store_true"); ap.add_argument("--as-of")
    a = ap.parse_args()
    if a.check:
        return self_check()
    if not (a.model and a.file):
        ap.error("--model and --file are required")
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    rows, cols = read(a.file)
    if a.groups:
        sys.exit(0 if groups_report(rows, cols, a.gap) else 1)
    as_of = dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today()
    key = model.get("key", "domain")
    parts = list(model["parts"])
    scored = [(r, score_row(r, model, as_of)) for r in rows]

    if a.test is not None:
        for r, s in scored:
            if r[key] in a.test:
                print(f"{r[key]}: total {fmt(s['total'])}, {s['confidence'] or '-'}, {s['band']}\n  {s['why']}")
        return

    if not a.write:
        counts = {}
        for _, s in scored: counts[s["band"]] = counts.get(s["band"], 0) + 1
        print("bands: " + ", ".join(f"{b} {counts.get(b, 0)}" for b in ("hot", "warm", "cold", "research", "out")))
        for r, s in sorted(scored, key=lambda x: -x[1]["total"])[:10]:
            print(f"{s['total']:>5}  {s['band']:<8} {r[key]:<28} {s['why'][:110]}")
        return

    existing = sets_in(cols)
    prefix = a.prefix or (f"S{(max(existing) if existing else 0) + 1}-" if a.next else "S1-")
    new_cols = set_columns(prefix, parts)
    for c in new_cols + ["band"]:
        if c not in cols: cols.append(c)
    today = dt.date.today().isoformat()
    for r, s in scored:
        for p in parts: r[prefix + p] = fmt(s["parts"][p])
        r[prefix + "total"] = fmt(s["total"]); r[prefix + "confidence"] = s["confidence"]
        r[prefix + "band"] = s["band"]; r[prefix + "missing"] = ";".join(s.get("missing", []))
        r[prefix + "why"] = s["why"]; r[prefix + "scored_on"] = today
        r["band"] = s["band"]
    write(a.file, rows, cols)
    counts = {}
    for _, s in scored: counts[s["band"]] = counts.get(s["band"], 0) + 1
    print(f"wrote {prefix}* on {len(rows)} rows: " + ", ".join(f"{b} {counts.get(b, 0)}" for b in ("hot", "warm", "cold", "research", "out")))


if __name__ == "__main__":
    main()
