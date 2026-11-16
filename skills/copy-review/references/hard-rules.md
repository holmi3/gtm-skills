# Hard rules (automatic fail)

A message that breaks one of these does not ship, however good it reads. These are sensible defaults for short business-casual outreach; edit the table to your own rules and keep `scripts/lint.py` in step. Rules marked [lint] are checked by the script.

| # | Rule | Notes |
|---|---|---|
| H1 | No em dashes or en dashes. [lint] | Also no spaced hyphen used as a dash. Use a period or a comma. |
| H2 | No colons in body prose. [lint] | Allowed in times (3:30), URLs and the `Subject:` line. |
| H3 | Few hyphenated compounds. [lint] | Max 1 per message, 0 in connection notes and nudges. Never stack them ("cross-functional, data-driven"). |
| H4 | No superiority claims. [lint] | No "unique", "unlike most", "the right person", "perfect fit". |
| H5 | Facts only from the facts file. | No invented metrics, titles, tools, dates, mutual connections or outcomes. Never claim to use the recipient's product unless the facts file says so. |
| H6 | {Your own rule: a topic you never raise, a phrase you never use about your work.} | |
| H8 | No banned phrases. [lint] | `scripts/banned_phrases.txt`, exact and near-exact matches. |
| H9 | No emoji, bullets, bold, headers or decorative links inside the message. [lint] | One plain URL is fine when the ask needs it. |
| H10 | Straight quotes and apostrophes only. [lint] | |
| H11 | Channel limits from `channels.md`. [lint] | Connection notes hard cap 300 characters. |
| H12 | One ask, as a question or a clear request. | Not two asks, not zero. |

Flags and concerns about a message always go below it, never inside it.
