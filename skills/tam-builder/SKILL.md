---
name: tam-builder
description: Build a scored, ranked TAM (total addressable market) account list for any company from public signals, end to end - define the ICP and exclusions, build the account universe, score with a deterministic formula, tune it on a known test set, write a short brief and likely owner per top account, render a ranked page for sales, hand check, and export. Use when asked to build a TAM, a target account list, an ICP-scored account list, account tiers for sales, or "which accounts should we go after first and why".
---

# TAM builder

A TAM is not a list of logos. It is a ranked list where every account says why it ranks, who likely owns the decision, and what is still unknown, built so a rep trusts it and a RevOps lead can change a weight and rerun it in seconds.

This skill runs the whole flow in eight stages with a human checkpoint after stages 1, 4, 7 and 8. It pairs with a context layer (`../../context-layer-template`), reuses the scoring approach of `../scored-lead-model` and the tuning loop of `../score-tuning`, and ships the scripts to run it (`scripts/`, Python 3 standard library only). A complete worked example on invented data is in `example/` (`bash example/run_example.sh`).

## Ground rules (every stage)
- **Public sources only**, unless the owner names an approved internal source. Every fact gets `[source: <url>, read YYYY-MM-DD]` in an evidence file. Passive reads: no logins, no probing, no form submissions.
- **Accounts before contacts.** This skill builds and scores companies. People's names, emails and profile URLs never go into the list, the repo or the page; a later, separate step finds contacts in a CRM or a private sheet.
- **Never invent.** A missing value is `unknown`. "Not found after reading <page>" is a finding; "not checked" is not, and never appears in a brief.
- **A model reads, a script counts.** LLMs turn pages into closed-list values with a quote and a confidence. `scripts/score.py` turns values into points from a JSON model. Nobody types a score.
- **Spend is approved.** Before any paid enrichment or model run at scale: run 10 rows, show the cost and the output, then ask. Test "missing data" on value columns, never on URL or ID columns.
- **Nothing sends, nothing syncs** to a CRM without the owner's explicit go.

## Stage 1: ICP, offer and exclusions (checkpoint)
Interview the owner one question at a time (or read `context/icp.md`, `positioning.md`, `personas.md`, `suppression.md` from their context layer). Settle:
- the offer and point of difference, before any list
- segments, with the one public signal that defines each, and which segment goes first
- size tiers (primary, confirm-floor, above-ceiling, under-floor) and territory
- anti-ICP and suppression: the company itself, customers (by motion), partners, competitors and builders, under the size floor, regions out of scope
- closed lists for every column an agent will fill (industry, work mode, tool in use)
- the four score parts and their maxima (default fit 40, prize 25, awareness 15, timing 20) and the band cut-offs, set from the team's weekly capacity

Write `scoring_model.md` (spec in words) and `model.json` (the same thing as data, format in `references/model-format.md`). **Stop for approval.**

## Stage 2: universe
Build one file, `accounts.csv`, one row per root domain (lower case, no `www`). Sources, cheapest first: job-post and technology searches per segment, company search by firmographics, lookalikes of the best known accounts (round two, not round one), public customer and partner pages. Details in `references/universe.md`.
- Keep a `list_source` column (which search or list each row came from) and `segments_all` (every segment it appeared in).
- Dedupe by domain; fold subsidiaries and product domains into the parent only when the product is sold by the parent.
- Move competitors and builders into `competitors.csv` and out-of-territory rows into their own file. Disqualify, never delete, everything else: a disqualified row keeps `exclusion_reason` so nobody researches it again.
- Record the count per source and per segment in `research/YYYY-MM-DD-universe.md`.

## Stage 3: signals and evidence
Fill the columns the model reads. For each:
- prefer a column a data source already returns over a page read; prefer a page read over a model guess
- classify into the closed list with a confidence, and write one evidence line per fact (`domain, field, value, quote, url, read_on, confidence`)
- report coverage per column: a signal empty on most rows is tracked, not scored, until coverage improves
- mark `page_read = yes` only when a page was actually read for the row; confidence depends on it

## Stage 4: score and tune (checkpoint)
1. Pick a test set before scoring: 5 strong (real customers or obvious fits), 5 decent, 5 bad, as `test_group` on copies of those rows in `test_set.csv`.
2. `python scripts/score.py --model model.json --file test_set.csv --write` (baseline set S1), then `--groups`.
3. Follow `../score-tuning/SKILL.md`: judge every row against the rubric with a fact, name the cause (weight, input or test group), change one thing, rerun with `--next`, log it. Stop when strong > decent > bad with a gap of at least 5, or after three changes with the blocker written down.
4. Roll out: `python scripts/score.py --model model.json --file accounts.csv --write`. The main file carries one set only, the accepted model.

Show the owner the iteration log, the band counts and the top 25. **Stop for approval.**

## Stage 5: briefs and likely owner
For hot and warm rows only:
1. `python scripts/brief_facts.py --model model.json --file accounts.csv --evidence evidence.csv --out facts.jsonl` builds one fact pack per row: what the company is, the reasons it ranks (strongest first, points removed), signals, the likely owner from the model's first-match `owner_rules`, and what is unknown.
2. Writers (people, or model subagents in shards of about 150 rows) write one paragraph per pack from the pack alone, using `references/brief-writer-prompt.md`.
3. `python scripts/check_briefs.py --model model.json --facts facts.jsonl --briefs briefs.csv` fails any brief with a number not in its pack, score language, internal wording, a dash, a link, a missing owner title, the wrong length, or a duplicate. Fix and rerun until it passes, then add `--apply accounts.csv`.

The owner is a title, never a person, and every owner basis that rests on judgment ends `[assumption]`.

## Stage 6: ranked page
`python scripts/render_page.py --model model.json --file accounts.csv --evidence evidence.csv --out ranked.html --title "..."`. One self-contained file: band tiles that filter, search, the ranked table, and per account the brief, the owner, a receipt for every point and the sources. It works in light and dark mode and on a phone. Readability for sales matters more than completeness: bands with plain definitions, a legend, the brief first, numbers second.

## Stage 7: hand check (checkpoint)
Follow `references/hand-check.md`: a fixed-seed sample of 25 hot accounts, one claim and its link per account, checked by a person. Record good, stale (a closed job post), wrong. Fix the input or the rule behind each wrong row, rerun stages 4 to 6, and note the result in the research log. **Stop for the owner's sign-off.** Do not quote an accuracy number before a hand check.

## Stage 8: export and handoff (checkpoint)
- `accounts.csv` sorted by band then total, with a short data dictionary (`README.md` next to it) and the page.
- A one-paragraph summary: universe size, band counts, what the score rests on, what it does not know, the date it was built and when it goes stale.
- Ask the owner before anything leaves the folder: emailing it, sharing a link, or a CRM import. Contacts are a separate, later step.

## Refreshing
Rerunning is cheap by design: change a weight and rerun stage 4 onward. Re-pull the fluid signals (timing) on a schedule; fit and prize change rarely. Any change to the model goes through the iteration log, never a hand edit to a score column.

## Files
| Path | What |
|---|---|
| `scripts/score.py` | the scorer: JSON model in, S<n>- column sets out, `--next`, `--groups`, `--test`, `--check` |
| `scripts/brief_facts.py` | fact packs and likely owner for hot and warm rows |
| `scripts/check_briefs.py` | holds every brief to its pack; `--apply` writes briefs onto the list |
| `scripts/render_page.py` | the ranked page |
| `references/model-format.md` | the model JSON: parts, rule types, disqualify, confidence, bands, owner rules, brief settings |
| `references/universe.md` | building and cleaning the universe |
| `references/brief-writer-prompt.md` | the prompt for brief writers |
| `references/hand-check.md` | the hand check procedure |
| `example/` | the whole flow on invented data |
