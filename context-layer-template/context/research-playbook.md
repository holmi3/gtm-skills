# Research playbook

How an agent researches and scores accounts from public evidence without wasting money.

## Order of work for a segment
1. Write the brief: the segment, the signal that defines it, the offer from `positioning.md`, the size tiers from `icp.md`.
2. Build the account list from the cheapest source first. Qualify accounts before touching people, and research each company once, never once per contact.
3. Run 10 rows and read the tool's cost estimate before anything at scale. Then run, inspect the exceptions, and decide the next step.
4. Score with a formula, not a model, so a weight change is a number edit and not a rerun.
5. Spot-check 10 scored accounts by hand. Fix the query that produced false positives instead of deleting rows.
6. Stop live searches and scheduled refreshes when the run is done.

## Researching one account from public pages
- Fetch in this order: homepage, careers or jobs page, security or trust page, pricing or product pages, recent news. If a page is blocked or nearly empty, fall back to a web search for its title and snippet.
- Classify against closed lists only (`icp.md`) and attach a confidence (high, medium, low).
- Weak signals stack. Record each piece with its URL and read date.
- Passive checks only.

## What a model does and what a script does
- A model **reads**: it turns a page or a title into one value from a closed list, with the exact quote saved beside it.
- A script **counts**: numbers, dates, exact matches and every point in the score.
- Before any step that calls a paid API or a model at scale, write down the number of calls and get a yes.

## Cost rules
- Sample first: the same request with a small limit, so the owner can check results before paying for all of them.
- Test "missing data" on the value columns, never on a URL or ID column. A blank link next to a filled count is not a gap.
- Keep a short record of what each paid run cost and what it returned, in the run's research file.

## Handoff
Per account: a short brief, the likely owner (title, not a person), a confidence level on every agent-derived answer, and the angle. Contacts stay in the CRM or a private sheet.
