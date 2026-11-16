# Proposal step (the nightly and weekly routine)

Runs after the nightly learnings entry is written. Assumes two repos: a context layer and a voice skill, each with its own `main`.

## 0. Clones
Fresh throwaway clones in the run's own workspace, both on `origin/main`. Never touch the person's working copies.

## 1. Update the ledger
For each `open` row, read the pull request itself (not a list endpoint, which can report a merged PR as unmerged): merged sets `merged YYYY-MM-DD`; closed sets `closed YYYY-MM-DD` plus any comment the person left. For each row merged tonight and each fast-lane commit, append one line to the context layer's `loop/log.md` and commit it to `main` (log lines are allowed there).

## 2. Refresh the mirror (every night)
`bash sync-mirror.sh <context-layer clone> <skill clone> <mirror dir>`. Log the two short hashes.

## 3. Check-ins (weekly run)
For each merged row 7 or more days old with an empty check-in: read the log entries since the merge and the records they cite. Write `holds`, `no signal yet` (check again in 7 days) or `contradicted` in the ledger and the day's entry, with the n.

## 4. Find candidates (nightly, queued)
- a pattern in the log's patterns list with no ledger row
- a promoted pattern that today's entry contradicts
- a correction from the person: a draft they rewrote or rejected, or an instruction on how to write something (explicit instructions are high confidence on their own; anything inferred needs 3+ days)
- lines under **Gaps** (they become a `QUESTIONS.md` proposal)

## 5. Check, then propose
Re-check each claim against the records first. Then read the matching file and decide confirms, contradicts or new.

| The learning is about | File |
|---|---|
| who to target, timing signals | context layer `context/icp.md` |
| cadence, channels, what the results say | context layer `context/outreach-rules.md` |
| context a draft needed and no file had | context layer `QUESTIONS.md` |
| message shape, length, ask per channel | voice skill `references/channels.md` |
| sends and replies per approach | voice skill `references/voice-profile.md`, "What got replies" (fast lane) |
| a sent message that got a reply | voice skill exemplars, recipient masked as `[NAME]` (fast lane) |

On the weekly run only, open at most 2 PRs from the queue, highest confidence first, with the body described in `../SKILL.md`. Assign the person and request their review. Add a ledger row (`L<NN>`) and remove the item from the queue.

## 6. Report
Nightly: nothing unless something changed. Weekly: one line per new proposal (topic, link, confidence), one per check-in, one per fast-lane change.
