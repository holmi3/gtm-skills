# One-shot prompt: a scored lead model instead of pass/fail

The same flow as the skill, as one paste-in prompt for anyone without skills installed. Put the CSV in a folder, open Claude Code in that folder, and paste the box. It interviews you first, writes the scoring plan for you to approve, and only then builds and runs it.

```
You are going to build a small, deterministic lead-scoring model with me in this folder. It gives every row a score made of four separate parts, not a pass/fail verdict. Work in three phases and do not skip ahead.

=== PHASE 1: INTERVIEW ME (no code yet) ===
First, find the CSV in this folder (ask me for the path if there is more than one or none). Read only its header and the first 5 rows, so your suggestions fit my real columns. Then ask me the questions below.

How to ask:
- ONE question per message. Wait for my answer before the next one.
- Start each question with a suggested answer based on my columns and what I've told you so far, so I can reply "yes" or correct it.
- If I say "skip" or "I don't know", mark it TODO, keep going, and treat that signal as unknown later.
- Never invent facts about my company. If you need a fact you don't have, ask.
- Show the question number (for example "Question 4 of 14") so I know where we are.

The questions, in this order:
1. What company is this for, and what do they sell, to whom? (one sentence + domain)
2. Is this inbound or outbound?
3. What is one row: a person at a company, or a company (account)?
4. What happens to a scored row? Suggest tiers for my motion. Inbound example: A to an AE within 1 hour, B to an SDR, C to nurture, D out. Outbound example: A gets a 1:1 sequence, B a segment sequence, C waits for a signal, D out.
5. Anti-ICP: which rows must be disqualified no matter what? (suggest: competitors, students, personal email with no company, too small, regions we can't sell to)
6. FIT (about the company): which signals make a company a good fit, and which column holds each? Suggest 3 to 5 from my columns (industry, size band, tech stack, region, business model).
7. PERSONA (about the person): which titles or departments are the buyer, the influencer, the user? Skip this one if a row is a company.
8. INTENT (what they did): which actions show interest, and which column holds each? Inbound: demo or contact-sales form, pricing page, content download, a free-text answer that names a pain. Outbound: reply, click, website visit, engaging with a post. If it's outbound with no engagement data yet, say so: intent will be unknown for now and timing carries the "why now".
9. TIMING (why now): which recent events matter? Suggest: hiring in the target department, funding in the last 6 months, a new leader in the buying role, a tech change. Ask how recent counts as recent.
10. Weights: propose a maximum for each part, totaling 100 (default fit 40, persona 20, intent 25, timing 15; outbound with no intent data: fit 45, persona 20, intent 0, timing 35). Ask me to accept or change them.
11. Points per signal: for each signal from questions 6 to 9, propose the points inside its part's maximum, as one table. Ask me to accept or change it.
12. Tier cut-offs: propose thresholds (default A >= 70, B >= 50, C >= 30, else D) and confirm that low-confidence rows never go to tier A.
13. Eval rows: which 2 or 3 rows should land at the TOP, and which 2 or 3 at the BOTTOM? (real customers or deals I already know about are best)
14. Anything the model should never do with this data? (for example: no people data leaves this folder, nothing gets pushed to a CRM)

After question 14, write scoring_model.md: every answer, as a spec with tables (anti-ICP rules, the four parts with their signals, columns and points, what counts as unknown, tiers, eval rows), and a TODO list of anything I skipped. Show it to me and ask: "Build it as written?" Do not continue until I say yes. If I ask for changes, update the spec and ask again.

=== PHASE 2: BUILD (after I approve the spec) ===
1. Copy the CSV to ./work/input.csv and never change the original.
2. weights.py: every number from the spec as a named constant at the top, so I can change a weight and rerun without touching the logic.
3. extract.py, only for columns that need judgment (for example job title to persona level, or free text to pain yes/no). Each field comes from a CLOSED LIST of values (for example decision_maker, influencer, user, not_relevant, unknown), with the exact source text saved beside it. Anything that a rule can compute (numbers, dates, exact matches) uses the rule, not a model. If any step needs model or API calls, tell me how many and wait for my OK.
4. score.py computes, per row:
   - fit, persona, intent and timing as separate numbers, each capped at its maximum.
   - A part whose inputs are all missing = "unknown", not 0. total = the sum of the known parts. missing_parts lists the unknown ones.
   - An anti-ICP hit: fit = 0, tier = D, disqualified_reason filled.
   - A "why" string, for example: "fit 24 = 12 industry SaaS + 12 size 340 | persona 12 = VP Marketing | intent 21 = demo + pricing | timing unknown (no hiring data)".
   - confidence: high if 3 or more parts are known and nothing was guessed, medium if 2, low otherwise.
   - tier, from the cut-offs.
   - A self-test (python score.py --check) with 3 made-up rows (one perfect, one anti-ICP, one with missing data) that asserts the expected points.

=== PHASE 3: RUN AND REPORT ===
1. Run --check, then score every row. Write ./work/scored.csv: every original column plus fit, persona, intent, timing, total, missing_parts, confidence, tier, disqualified_reason, why.
2. Write ./work/report.md:
   - the top 10 and bottom 5 rows, with their why strings
   - the eval check: PASS or FAIL for each named row, and if FAIL, which part caused it
   - coverage: for each signal, how many rows had a real value (a signal that's empty on most rows isn't ready to carry points)
   - the count per tier (A, B, C, D)
   - three suggested weight changes for v2, one line each, marked as suggestions
3. Stop and show me the report. Don't change weights on your own. When I give you v2 weights, rerun and add a "v1 vs v2" table (rank changes for the eval rows) to the report.

Rules for the whole session: never invent a value; unknown stays unknown. Nothing gets sent or pushed anywhere. This session only builds and scores.
```

## Tips

- **Start with 5 to 10 real rows.** Mix easy, average and edge cases, so a run takes seconds and every row can be checked by hand.
- **Points should reflect what predicts a deal, not what's easy to collect.** Real customers make the best eval rows.
- **Keep fit and intent apart.** That separation is what turns pass/fail into a ranked list.
- **Include a signal even if there's no column for it yet.** The coverage line will show it as unknown, which tells you what data to go get next.
