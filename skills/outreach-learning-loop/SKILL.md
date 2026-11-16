---
name: outreach-learning-loop
description: Close the loop from outreach results to the next draft - log sends, accepts and replies nightly, promote patterns that hold, re-check every claim against the source records, propose small pull requests against the context layer and the voice skill for a human to merge, mirror merged rules to where drafting agents read them, and run a preflight before every draft. Use when setting up or running a nightly outreach log, a weekly learning review, "what is working in my outreach", or when drafting agents should apply accepted learnings.
---

# Outreach learning loop

Most outreach setups write messages and forget them. This loop makes results change the next message, with a person deciding every rule change.

```
records of truth (CRM or tracker cards: sends, accepts, replies, the person's edits to drafts)
   |  nightly
   v
learnings log          a daily entry, plus patterns that held 3+ days
   |  nightly: re-check each claim against the records, then confirms / contradicts / new
   v
queue -> weekly: at most 2 proposal pull requests        evidence-only edits go in nightly (fast lane)
   |  a person merges (accept) or closes (reject)
   v
main -> nightly mirror -> drafting agents run the preflight before their first draft
   |
   v
next sends -> back to the top. 7 days after a merge, check whether the named number moved.
```

## Pieces
| Piece | Template | Who writes it |
|---|---|---|
| Learnings log | `references/learnings-log-template.md` | the nightly run |
| Ledger of proposals and check-ins | `references/ledger-template.md` | the nightly run; drafting tasks append gaps |
| Nightly and weekly routine | `references/proposal-step.md` | this skill |
| Drafting preflight | `references/drafting-preflight.md` | drafting tasks read it |
| Mirror script | `references/sync-mirror.sh` | the nightly run |
| The files that change | a context layer (`context/outreach-rules.md`, `context/icp.md`, `QUESTIONS.md`) and a voice skill (`channels.md`, `voice-profile.md` "What got replies", exemplars) | proposals only |

## Nightly
1. **Log the day** from the records: sends, accepts, replies, calls, what went dead, per approach and channel. Counts only; a cause is a claim and needs evidence.
2. **Promote** a pattern to the log's "patterns" list only when it held 3 or more days, with the dates it rests on.
3. **Re-check** every candidate claim against the records, not the daily summaries. Summaries compound errors: a "the people who posted the job reply on their own" pattern can survive three summaries and fail when the cards are read. When a promoted pattern fails, add a dated correction under it.
4. **Classify** each surviving candidate against the files: confirms (log it, no change), contradicts (propose an edit), new (propose an addition). Queue it in the ledger.
5. **Fast lane for evidence only**: a reply-count row in the voice profile, or a sent message that got a reply added as an exemplar (recipient masked). These go straight to `main` with a log line, because they are records, not rules. Anything that changes how a message is written is a rule and waits for the weekly review.
6. **Refresh the mirror** so tomorrow's drafts read today's `main`.

## Weekly (one sitting for the person)
1. **Check-ins** on changes merged 7 or more days ago: `holds` (the watch number moved as expected), `no signal yet` (fewer than about 10 sends under the change), or `contradicted` (moved the other way for 3+ days, which triggers a revert proposal). Say the n every time; these are small samples.
2. **Open at most 2 proposals**, highest confidence first, as pull requests on `proposal/YYYY-MM-DD-<topic>` branches. The rest stay queued.
3. **Brain review**, read-only: stale files, old `QUESTIONS.md` lines, broken links, contradictions between files.
4. One short summary for the person: the proposals with links, the check-ins, and anything the fast lane applied (each one revertable on request).

## A proposal
Branch `proposal/YYYY-MM-DD-<topic>`, the smallest diff that carries the learning, written in the file's own style, each new line ending with its evidence. The PR body: **Triggered by** (quoted, with dates), **Check against the layer** (confirms, contradicts `<file:line>`, new), **Change** (one sentence on what the next draft will do differently), **Confidence** with n, **Freshness**, **Watch** (the number that should move), **Decision** (merge, close, or comment).

## Never
- Send anything. Drafts only.
- Change `main` except the fast lane and log lines.
- Put a contacted person's name, email, profile link or company in a repo or a PR. Say "the person who posted the role", "3 of 6 accepts". Names stay in the private tracker.
- Propose changes to the hard rules, the sender's facts file, the loop's own rules, or anything the person holds back (for example a sequence they are redesigning).
- Re-propose a closed proposal unless the new evidence is at least twice what it rested on.

## Insight states
**emerging** (queued), **validated** (merged), **canonical** (held at the 7-day check). A contradicted check-in sends the line back to emerging with a note.
