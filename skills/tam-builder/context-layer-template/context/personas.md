# Personas

Roles and titles only, never a named person. Who signs versus who only recommends is the most common open question; keep it in `QUESTIONS.md` until it is answered.

| Persona | Title patterns | What they own | What they care about | Role in the deal | Qualifies when | Source |
|---|---|---|---|---|---|---|
| {IT or security owner} | CIO, CISO, VP or Director of IT, IT Manager | tools on company devices, access, data policy | security review, rollout effort, one fewer tool | signer | the company manages devices centrally or is regulated | `[tag]` |
| {Department head} | VP of Sales, VP of Engineering, Head of Support | the team that uses the product daily | output per person, ramp time | buyer | the team is large enough to feel the pain | `[tag]` |
| {Champion} | ops lead for that department | process and tooling for the team | fewer manual steps, clean data | champion | | `[tag]` |
| {Finance or procurement} | | spend | consolidation, price per seat | approver | | `[tag]` |

## Owner rule (for account briefs)
When a list needs one likely owner per account, write the rule as a first-match table so the same row facts always give the same title. Example shape:

| # | Row fact | Owner | Support |
|---|---|---|---|
| 1 | flagged partner or vendor | none, no outreach | `suppression.md` |
| 2 | evidence of central device management | IT or security owner | this file, row 1 |
| 3 | regulated industry | security owner | this file, row 1 |
| 4 | otherwise, headcount counted is in sales roles | VP of Sales | this file, row 2 |
| 5 | otherwise, headcount counted is in engineering roles | VP of Engineering | this file, row 2 |

Every title the rule picks is a starting point for the rep, not a finding.
