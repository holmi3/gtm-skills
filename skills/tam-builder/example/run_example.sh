#!/usr/bin/env bash
# Rebuild every file in output/ from input/ and the three model versions. Standard library Python 3.8+ only.
set -euo pipefail
cd "$(dirname "$0")"
S=../scripts
AS_OF=2026-01-15                        # the example's "today", so recency multipliers never drift
mkdir -p output
cp input/accounts.csv output/accounts.csv
python3 $S/score.py --check

# 1. Tune on the test set: the rows with a test_group (strong, decent, bad), one S<n>- column set per model version.
python3 - <<'PY'
import csv
rows = [r for r in csv.DictReader(open("input/accounts.csv", newline="")) if r["test_group"]]
w = csv.DictWriter(open("output/test_set.csv", "w", newline=""), fieldnames=list(rows[0]), lineterminator="\n")
w.writeheader(); w.writerows(rows)
PY
python3 $S/score.py --model model_v1.json --file output/test_set.csv --as-of $AS_OF --write
python3 $S/score.py --model model_v2.json --file output/test_set.csv --as-of $AS_OF --write --next
python3 $S/score.py --model model_v3.json --file output/test_set.csv --as-of $AS_OF --write --next
python3 $S/score.py --model model_v3.json --file output/test_set.csv --groups

# 2. Roll the accepted model out to the full list.
python3 $S/score.py --model model_v3.json --file output/accounts.csv --as-of $AS_OF --write

# 3. Fact packs for hot and warm rows, briefs checked against them, then applied.
python3 $S/brief_facts.py --model model_v3.json --file output/accounts.csv --evidence input/evidence.csv --out output/facts.jsonl
python3 $S/check_briefs.py --model model_v3.json --facts output/facts.jsonl --briefs briefs.csv --apply output/accounts.csv
rm -f output/accounts.csv.bak

# 4. The ranked page.
python3 $S/render_page.py --model model_v3.json --file output/accounts.csv --evidence input/evidence.csv --out output/ranked.html --title "Relaydesk target accounts (invented example)"
