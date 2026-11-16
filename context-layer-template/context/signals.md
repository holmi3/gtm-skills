# Signals

One row per public signal. A signal earns points only when a column on the list actually holds it for most rows; a signal that is empty on most rows is tracked, not scored, until coverage improves.

| Signal | What it shows | Where it comes from | Fresh for | Score part | Column |
|---|---|---|---|---|---|
| Headcount in the roles that use the product | size of the prize | a job and people data provider, the company's own pages | 6 months | prize | `role_headcount` |
| Open roles in those functions | growth, why now | job boards, careers page | 6 months, then decays | timing | `open_roles`, `last_job_post` |
| A rival or the category already in use | awareness | job posts naming the tool, public case studies, tech-stack data | 12 months | awareness | `rival_in_use` |
| A new leader in the buying role | why now | job posts, press releases | 6 months | timing | `new_leader` |
| Funding in the last 12 months | budget, why now | press releases, public funding news | 12 months | timing | `funding_12m` |
| Work mode | how much of the work happens online | careers page, job posts | 12 months | fit | `work_mode` |

## Recency
Time-bound signals decay. A default multiplier: within 6 months 1.0, 6 to 12 months 0.85, 12 to 18 months 0.65, older 0.4. Change it here and in the scoring spec together.

## Strength
- A job post that names a tool shows how the company works; one employee listing it as a skill does not.
- Weak signals stack. One mention is thin; a job post plus a public case study plus a stack match is strong. Record each piece with its URL.

## Negative signals
Layoffs, office closures, a lost major customer. Decide per signal whether it is scored or only tracked. When the direction is unclear (a cut can be an efficiency push that makes a better buyer) or coverage is uneven (only companies the press covers would lose points), track it as a flag and a line in the brief, and give it 0 points.

## Rules
- Passive checks only: no logins, no probing, no form submissions.
- Every signal on a row has its URL and read date in an evidence file.
- "Not found" is a finding when the source was read; "not checked" is not a fact about the company and never goes into a brief.
