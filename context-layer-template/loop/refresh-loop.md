# Refresh loop

Storage is nearly free. The learning loop is the hard part, and it needs a named owner or the context decays.

## The rule
On a schedule the owner picks (hourly, nightly or weekly), an agent:
1. Reads what changed since the last run: run logs, corrections people made to agent output, results (sends, replies, meetings), and questions that came back empty.
2. Checks each item against the context files and labels it: **confirms** (a line already says it, no change), **contradicts** (propose an edit) or **new** (propose an addition).
3. Re-checks every claim against the source records, not against summaries of them. Summaries compound errors.
4. Proposes the smallest diff that carries the change, on a branch named `proposal/YYYY-MM-DD-<topic>`, and opens a pull request.
5. Changes nothing on `main`. A person accepts (merge) or rejects (close).

## What a proposal contains
- The file and the exact lines to change.
- **Triggered by:** the log entries or corrections behind it, quoted, with dates.
- **Check against the layer:** confirms, contradicts `<file:line>`, or new.
- **Confidence** (high, medium, low) with the n, and **freshness** (static, or market-sensitive with a re-check date).
- **Watch:** the number that should move if the change is right.

## Evidence bar
- A pattern that held three or more days, or an explicit correction from the owner. One-off wins stay in the log.
- Small samples are normal. Say the n every time.
- A closed (rejected) proposal is not proposed again unless the new evidence is at least twice what it rested on.

## Insight states
**emerging** (queued, not a rule), **validated** (merged), **canonical** (held at the 7-day check). Seven days after a merge, the loop checks the watch number: `holds`, `no signal yet`, or `contradicted`. A contradicted change gets a revert proposal.

## Weekly brain review
Read-only, once a week: files not changed in 30 days, `QUESTIONS.md` lines older than 14 days, links that do not resolve, contradictions between files. Findings become proposals, never direct edits.

## What the loop may not touch
`CLAUDE.md`, this file, and any file the owner marks as theirs alone (facts about the company, hard rules). A missing fact becomes a `QUESTIONS.md` line.
