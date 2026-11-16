# Brief writer prompt

Give each writer (a person or a model subagent) this prompt and one shard of `facts.jsonl`, about 150 packs. Writers never see the account file, the score columns or each other's output.

```
You write one short account brief per fact pack in the file you were given. A brief is read by a sales or RevOps
leader who has never seen the scoring model. It tells them what the company is, why it is worth their time now, and
who to start with.

Rules:
- One paragraph, {min_words} to {max_words} words.
- Use only the pack. No outside knowledge, no guesses, nothing from memory about the company.
- Every number must appear in the pack exactly as written there (you may add thousands separators).
- Start with what the company is (kind of company, where, how big), then the two or three strongest reasons from
  reasons_strongest_first in plain words, then the timing if there is any, then the owner.
- Name the owner title exactly as in the pack's "owner" field. Mention the champion if there is one. Never a person.
- Plain words. No score language (score, points, band, tier, fit, prize), no internal wording (segment, target list,
  our, we), no dashes as punctuation, no links, no emails, no hype.
- If the pack has evidence lines, you may use their quoted facts. A pack's "unknown" list is not a fact about the
  company: never write that something "has not been checked".
- If a pack is too thin for a useful brief, leave the brief blank and write why in the note column.

Output: a CSV with columns domain, brief, note, one row per pack, in pack order.
Then run: python scripts/check_briefs.py --model model.json --facts <your shard> --briefs <your csv>
and fix every failure before returning.
```
