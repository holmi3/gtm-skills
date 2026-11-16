#!/usr/bin/env python3
"""check_briefs.py: hold every account brief to its fact pack. Standard library only.

    python check_briefs.py --model model.json --facts facts.jsonl --briefs briefs.csv            # check, writes nothing
    python check_briefs.py --model model.json --facts facts.jsonl --briefs briefs.csv --apply accounts.csv

briefs.csv columns: domain (the model's key), brief, note. A blank brief needs a note saying why.

Checks, one line per failure, exit code 1 if any:
- every pack in scope has a brief, or a note explaining the blank
- word count inside the model's brief.min_words to brief.max_words, one paragraph
- every number in the brief appears in the pack (facts, reasons or evidence)
- no score language, no internal wording (model brief.banned), no dash used as punctuation, no URL or email
- the brief names the pack's owner title
- no two briefs are the same once the company name is taken out
--apply (only when every check passes) writes brief, owner, champion and owner_basis onto the account file, after
saving a .bak copy beside it.
"""
import argparse, csv, json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import read, write  # noqa: E402

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
DASH = re.compile("[—–]| -- | - ")
LINK = re.compile(r"https?://|www\.|\S+@\S+\.\w")


def nums(text):
    return {t.replace(",", "").rstrip(".") for t in NUM.findall(text)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True); ap.add_argument("--facts", required=True)
    ap.add_argument("--briefs", required=True); ap.add_argument("--apply")
    a = ap.parse_args()
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    cfg, key = model["brief"], model.get("key", "domain")
    packs = {}
    for line in open(a.facts, encoding="utf-8"):
        p = json.loads(line)
        packs[p[key]] = p
    briefs = {b[key]: b for b in csv.DictReader(open(a.briefs, newline="", encoding="utf-8"))}
    banned = [(re.compile(r"\b" + re.escape(w) + r"\b", re.I), w) for w in cfg.get("banned", [])]
    fails, seen = [], {}

    for k, p in packs.items():
        b = briefs.get(k)
        text = (b or {}).get("brief", "").strip()
        if not text:
            if not (b or {}).get("note", "").strip():
                fails.append(f"{k}: no brief and no note")
            continue
        words = len(text.split())
        if "\n" in text:
            fails.append(f"{k}: more than one paragraph")
        if not cfg["min_words"] <= words <= cfg["max_words"]:
            fails.append(f"{k}: {words} words (allowed {cfg['min_words']} to {cfg['max_words']})")
        allowed = nums(json.dumps(p, ensure_ascii=False))
        extra = sorted(nums(text) - allowed)
        if extra:
            fails.append(f"{k}: numbers not in the pack: {', '.join(extra)}")
        for rx, w in banned:
            if rx.search(text):
                fails.append(f"{k}: banned wording '{w}'")
        if DASH.search(text):
            fails.append(f"{k}: dash used as punctuation")
        if LINK.search(text):
            fails.append(f"{k}: URL or email in the brief")
        if p["owner"] and p["owner"].lower() not in text.lower():
            fails.append(f"{k}: does not name the owner title '{p['owner']}'")
        body = re.sub(re.escape(p.get("company", "")), "", text, flags=re.I).strip().lower() if p.get("company") else text.lower()
        if body in seen:
            fails.append(f"{k}: same brief as {seen[body]}")
        seen[body] = k
    for k in briefs:
        if k not in packs:
            fails.append(f"{k}: brief for a row with no pack (out of scope)")

    for f in fails:
        print("FAIL", f)
    print(f"{len(packs)} packs, {sum(1 for k in packs if briefs.get(k, {}).get('brief', '').strip())} briefs, {len(fails)} failures")
    if fails:
        sys.exit(1)
    if a.apply:
        rows, cols = read(a.apply)
        shutil.copyfile(a.apply, a.apply + ".bak")
        for c in ("brief", "owner", "champion", "owner_basis"):
            if c not in cols: cols.append(c)
        for r in rows:
            p = packs.get(r[key])
            r["brief"] = briefs.get(r[key], {}).get("brief", "").strip() if p else ""
            r["owner"] = p["owner"] if p else ""
            r["champion"] = p["champion"] if p else ""
            r["owner_basis"] = p["owner_basis"] if p else ""
        write(a.apply, rows, cols)
        print(f"applied to {a.apply} (backup {a.apply}.bak)")


if __name__ == "__main__":
    main()
