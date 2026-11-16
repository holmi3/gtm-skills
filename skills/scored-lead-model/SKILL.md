---
name: scored-lead-model
description: Build a small, deterministic lead or account scoring model from a CSV, with four separate parts (fit, persona or prize, intent or awareness, timing) instead of a pass/fail verdict. Interviews the user first, writes a spec for approval, then builds and runs a script that explains every score. Use when someone asks to score leads, rank accounts, build a lead scoring model, replace pass/fail qualification, or tier a list into A/B/C/D or hot/warm/cold.
---

# Scored lead model

Turns a CSV of leads or accounts into a ranked list where every row explains its own score. Works for inbound or outbound, people or companies.

## Why four parts instead of pass/fail
- **Separate parts, not one verdict.** Fit (right company), persona or prize (right person, or size of the win), intent or awareness (what they did, what they already use) and timing (why now) each get their own points. A perfect-fit company with no intent never looks the same as a weak fit with high intent.
- **The model reads, a formula counts.** An LLM only turns messy text into a value from a closed list (a job title into `decision_maker`). A script turns values into points, so a weight change is a number edit and every row gets the same math.
- **Unknown is not zero.** A missing signal shows as unknown, and the row says which part is missing. A part with no data scores its floor and is named in `missing_parts`, never filled with an average.
- **Every row explains itself** with a why string: `fit 24 = 12 industry SaaS + 12 size 340 | timing unknown (no hiring data)`.
- **It tests itself** against rows whose answer is already known (real customers at the top, obvious misfits at the bottom).

## Three phases. Do not skip ahead.

### Phase 1: interview (no code)
Find the CSV (ask if there is more than one or none). Read only the header and the first 5 rows. Then ask the questions in `references/interview.md`: **one per message**, each with a suggested answer drawn from the real columns, numbered ("Question 4 of 14"). "Skip" or "I don't know" becomes a TODO and the signal is treated as unknown. Never invent a fact about the user's company.

After the last question, write `scoring_model.md` from `references/spec-template.md`: anti-ICP rules, the four parts with their signals, columns and points, what counts as unknown, confidence rule, bands, eval rows, and a TODO list. Show it and ask: "Build it as written?" Do not continue until the answer is yes.

### Phase 2: build (after the spec is approved)
1. Copy the CSV to `./work/input.csv`. Never change the original.
2. `weights.py`: every number from the spec as a named constant at the top.
3. `extract.py`, only for columns that need judgment. Each field comes from a **closed list** with the exact source text saved beside it. Anything a rule can compute (numbers, dates, exact matches) uses the rule. If any step needs model or API calls, say how many and wait for an OK.
4. `score.py`, per row: each part capped at its maximum; a part whose inputs are all missing is `unknown` (listed in `missing_parts`, scores 0, never averaged); anti-ICP hit means fit 0, band out, `disqualified_reason` filled; a why string; confidence; band. Plus `python score.py --check`: three made-up rows (perfect, anti-ICP, missing data) with asserted points.

A ready reference implementation of this shape (config-driven rules, receipts, iteration columns, bands) is in `../tam-builder/scripts/score.py`. Use it when the user would rather configure than generate code.

### Phase 3: run and report
1. `--check`, then score every row into `./work/scored.csv`: every original column plus `fit, persona, intent, timing, total, missing_parts, confidence, band, disqualified_reason, why`.
2. `./work/report.md`: top 10 and bottom 5 with why strings; the eval check (PASS or FAIL per named row, and which part caused a FAIL); coverage per signal (a signal empty on most rows is not ready to carry points); count per band; three suggested weight changes for v2, marked as suggestions.
3. Stop and show the report. Do not change weights on your own. When the user gives v2 weights, rerun and add a v1 vs v2 table. For repeated tuning rounds, hand over to the `score-tuning` skill.

## Bands (defaults, change in the spec)
| Band | Rule | Meaning |
|---|---|---|
| hot (A) | total >= 60 and confidence medium or high | personal outreach now |
| warm (B) | 45 to 59.9, confidence medium or high | after hot is done |
| cold (C) | under 45, confidence medium or high | nurture, or wait for a signal |
| research | confidence low or no total | not handed to sales until someone reads a page |
| out (D) | disqualified | kept in the file with its reason |

A low-confidence row never lands in hot, however high its total. Set the cut-offs from the team's capacity (how many accounts they can actually work this week), not from the data.

## Confidence
- **low**: two or fewer parts known, or a part was guessed, or no source page was read for the row
- **medium**: three parts known and a source read
- **high**: medium plus at least one signal a rep can quote with a link

## Rules for the whole session
Never invent a value; unknown stays unknown. Nothing is sent, pushed or written to a CRM. No people data leaves the folder. The session builds and scores, nothing else.

## Files
- `references/interview.md`: the 14 questions
- `references/spec-template.md`: the shape of `scoring_model.md`
- `references/one-shot-prompt.md`: the same flow as a single paste-in prompt, for someone without skills installed
