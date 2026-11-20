---
name: score-tuning
description: Tune a deterministic account or lead scoring model on a labeled test set (strong, decent, bad rows), one iteration at a time - run, judge every row with a fact, name the cause, change one weight or input, rerun into a new column set, and log it, until strong beats decent beats bad by a clear margin. Use when asked to tune, check, re-score, calibrate or debug a scoring model, or when a score "looks wrong" on a known account.
---

# Score tuning: run, judge, adjust, rerun

You are tuning a formula, not grading by feel. The script owns the numbers; you own the judgment about whether they are right and what in the model or the data makes them wrong. Nobody types a score into a score column.

Works with any scorer that can write each run into its own column set. The reference scorer is `../../scripts/score.py` (JSON model, `S1-`, `S2-`, ... sets); the commands below use it. A full worked run is in `../../example/iterations.md`.

## Files
- `test_set.csv`: copies of 10 to 20 rows from the main list with a `test_group` column: **strong** (real customers or obvious fits), **decent** (would buy, not first), **bad** (should never reach sales). Optional extra groups, such as companies on the seller's own logo strip, are reported but not part of the stop rule. Pick the groups **before** the first run, so the model is not tuned to whatever it already says.
- `model.json` (or the weights at the top of the scorer) and its spec in words, kept in step.
- The evidence file (one quoted fact per line with its URL).
- `iterations.md`: the log, one section per iteration, headed `## S<n>: <one line on what changed>` (template in `references/iteration-log-template.md`).

## One iteration
1. **Run.** Baseline: `python score.py --model model.json --file test_set.csv --write` (set S1). After each change: `--write --next`, which starts a new set and leaves the earlier ones for comparison. Then `--groups` for each set's group ranges and the separation check.
2. **Judge every row.** For each row read the latest `S<n>-why` (the receipt) and ask, part by part: is this number right for what the rubric says the part measures? Use the row's inputs, the evidence file and, if needed, one public page (cite it). One line per row in the log: `row | total | right / too high / too low | which part | why, with the fact`. "Feels high" is not a finding.
3. **Name the cause.** Every wrong score has one of three:
   - **A weight or rule in the model.** Fix it in the model and in the spec, one change at a time, with a `note` that names the row that exposed it. Common ones: a part that rewards "more" past the product's ceiling; a business-model penalty too small to stop signals lifting a poor fit; absolute size letting the biggest companies top every list (add concentration: target-role headcount over total staff).
   - **A missing or wrong input.** Fix the cell from a public source with the citation, or set it to `unknown`. Never fake a value to make a score come out.
   - **The test group is wrong.** Say so in the log and propose the swap. Do not move a row between groups yourself.
4. **Rerun** with `--next` and compare in a table: the same rows, previous total against new. A change must help the row that exposed the problem without breaking a row that was right. If it moves a right row by more than 5 points, say so and decide whether to keep it.
5. **Your own view.** If you still disagree with the formula on a row after the fix, write your own part scores into a separate `model-` column set with a two-sentence reason. That is the record of where judgment and formula differ. Never edit an `S<n>-` set.
6. **Stop.** Done when, on the latest set, strong > decent > bad with each group's lowest at least 5 points above the next group's highest, and every `why` reads right to someone who has never seen the rubric. If three changes have not got there, stop and write what is blocking (usually an input that needs a page read or an enrichment).

## Rules of the model
- Fit and size carry the list; signals only rank within it. Awareness and timing must not push a poor-fit account into the top.
- One table for every row. No per-row exceptions in code.
- `unknown` is a real value. A part that cannot be measured scores its floor and the receipt says so; never an average.
- A count is headcount only when its source says so; a count of mentions is ignored.
- Fix unclear receipts in the scorer's receipt text, not in the cell.
- A signal whose direction is unclear or whose coverage is uneven (layoffs are the usual example) is tracked as a flag and a line in the brief, with 0 points, until there is evidence for its sign.

## Rolling out
When the owner accepts an iteration, run the same model on the main list: `python score.py --model model.json --file accounts.csv --write`. The main file carries one set, the accepted model. Report: the before and after table for the test set, the changes made (file and line), rows still in dispute, and the band counts on the main list. Do not commit; the owner commits.
