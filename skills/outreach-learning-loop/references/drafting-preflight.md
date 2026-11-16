# Drafting preflight

Every task that drafts outreach (scheduled runs, pipeline reviews, a one-off "draft a reply") does this once per run, before the first draft. It is how accepted learnings reach the next message.

1. Read `mirror/VERSION`. It names the commits of the context layer and the voice skill the mirror holds, and when it was refreshed.
2. Read, in this order, from the mirror:
   - `context-layer/AGENTS.md` (the routing table). Lines in `context/` carry `[source]`, `[stated by user]` or `[assumption]` tags; never present an `[assumption]` as a fact about the sender.
   - `context-layer/context/outreach-rules.md`, especially **What the results say**. These are learnings the person accepted. Apply every one that fits the message (targeting, step, timing, shape).
   - `context-layer/context/icp.md` (who to target, and the buyer).
   - `skill/SKILL.md` and `skill/references/` (hard rules, channels, voice profile, exemplars, facts). Where the mirror differs from any other copy of the skill, **the mirror wins**. The task prompt still wins over both.
3. Hand every draft to the copy reviewer with the mirror's paths, not another copy of the skill.
4. Read only. Never edit the mirror; the nightly run rewrites it. If a draft needed context no file had, add one line to the **Gaps** list in the ledger (date, what was missing, which task). The nightly run turns gaps into `QUESTIONS.md` proposals.
5. If the mirror is missing or `VERSION` is more than 3 days old, draft from the installed skill and write "learning loop mirror stale" in the run log.

Open proposals are not rules yet. Do not apply them until they are merged.
