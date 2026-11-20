# Meeting prep agent (example)

An example of an agent that runs on this layer. It turns a domain and the attendees' roles into a one-page brief.

## Input
- `{domain}` of the account
- `{attendees}` as roles (for example "Director of Sales Ops, IT Manager")
- `{motion}` net new or expansion

## Steps
1. Public research on `{domain}`: size, industry, stack, work mode, public signs the category or a rival is already in use. Cite each fact.
2. Map the account to a segment and each attendee to a persona, using `../ontology.md`.
3. Pull the cross-section from `../context/`: use case, proof point, objections, discovery questions, competitor notes if a rival is in use.
4. Write the brief below. Every line cites a context file or a public URL. If nothing covers a section, write "no context" and log it as a gap.
5. Append one line to a run log: date, account, sections with no context, and any correction the rep made afterwards. Corrections feed the refresh loop.

## Output: one page
- Who they are (two lines)
- Signs the category or a rival is in use (public only)
- Stack that matters
- Likely buyer and where adoption starts
- The angle (one sentence)
- Three discovery questions
- Two likely objections with answers
- Suggested next step
