---
name: copy-review
description: Second-reader review for outreach copy before a person sees it - an independent reviewer that never saw how the draft was written checks it against hard rules and a voice profile, scores how AI it sounds from 1 to 10, checks it makes sense for the recipient, and returns PASS or REVISE with quoted flags. Use for every connection note, DM, cold email, follow-up, reply, cover letter or application answer an agent drafts, and when anyone asks "does this sound like AI", "review this message", or "is this ready to send".
---

# Copy review

Code gets reviewed before it merges. Copy should get reviewed before a person reads it. This skill is the review step: a separate reader, with no stake in the draft, checks it and returns a verdict the drafter has to act on.

It works with any drafting setup. Your voice lives in `references/voice-profile.md` (a template: fill it from your own sent messages). The rules, the reviewer prompt and the linter are generic.

## Why a separate reader
The model that wrote a draft reads its own intent into it. A reviewer that sees only the final text, the channel and the recipient context reads it the way the recipient will. So the reviewer **never** gets the drafts, the reasoning or the brief's wording.

## Inputs
- `message` (and `subject` for email)
- `channel`: connection-note, dm, inmail, cold-email, nudge, follow-up, thank-you, info-ask, reply, cover-letter, application-answer
- `already_sent`: earlier messages in the thread, if any (so a repeated ask is caught)
- `recipient_context`: who they are, and the one real hook the message was supposed to use
- the reference files in `references/`

## Procedure
1. **Lint** (if code can run): `python3 scripts/lint.py --channel <channel> --json <file>`. Any lint FAIL is a gate failure. Without code, do the same checks by hand.
2. **Spawn the reviewer** with `agents/reviewer.md` as its instructions and only the inputs above.
   - Claude Code or any agent with subagents: a subagent, on a strong model at high effort.
   - An agent framework with task delegation: delegate with the reviewer prompt as the task.
   - A plain chat with no subagents: a cold read. Set the draft aside, re-read only `agents/reviewer.md` and the final text, and review it as if a stranger wrote it.
3. **Act on the verdict.** PASS: hand the message to the person with the review block under it. REVISE: fix only what the flags name, then review again with a fresh reviewer. **Two revisions at most.** If it still fails, hand over the best version with the open flags listed.

## What the person sees
1. The message, ready to paste. Nothing inside it but the message: no notes, brackets or placeholders.
2. Under it, the **review block**: PASS or REVISE, the AI score (1 to 10), the five scores, and any flags with the quoted text.
3. Under that, **questions or concerns**: a missing fact, a weak hook, a risky claim, a time to double-check. Never inside the message.

For an agent caller, return JSON: `{"channel": "...", "subject": null, "message": "...", "review": {...reviewer JSON...}, "needs_human": [...]}`.

## Never
- Send, schedule or queue a message. A person sends every one.
- Invent or round up a fact about the sender or the recipient. A fact that is not in the sender's facts file is a question for the person.
- Pass a message with a fake or generic hook. No message is better than a message that could be pasted onto anyone.

## Files
| File | What |
|---|---|
| `agents/reviewer.md` | the reviewer prompt: gates, scores, AI score, verdict, JSON output |
| `references/hard-rules.md` | automatic fails (edit to your own rules) |
| `references/slop-patterns.md` | AI tells: banned phrases, structural tells, soft vocabulary |
| `references/channels.md` | length, shape and ask per channel |
| `references/voice-profile.md` | template for your voice and your facts file |
| `scripts/lint.py`, `scripts/banned_phrases.txt` | the deterministic checks |
