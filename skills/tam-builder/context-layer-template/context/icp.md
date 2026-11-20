# ICP: segments, anti-ICP, scoring rubric

Tags on every line. Most of this file starts as `[assumption]`; each assumption should have a matching `QUESTIONS.md` line until someone who owns the number answers it.

## Baseline filter (every segment)
- Country or territory: {for example US only, or US first then Canada, UK, Ireland, Australia, New Zealand} `[tag]`
- Business model: {B2B, B2C, both} `[tag]`

## Size tiers
| Tier | Employees | Treatment |
|---|---|---|
| primary | {200 to 5,000} | full scoring |
| confirm-floor | {20 to 199} | scored, confirm before outreach |
| above-ceiling | {above 5,000} | scored, flagged (different motion) |
| under-floor | {under 20} | anti-ICP |

## Segments
One segment goes first. The rest wait until the first one has been worked.

| # | Segment | Who (size, industry, stack, work mode) | Why they buy | Defining public signal | Disqualifiers |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

## Closed lists for classifiers
An agent that classifies a row picks from a fixed list and adds a confidence (high, medium, low). Free text does not filter.
- `industry`: {b2b_saas, fintech, healthcare, other}
- `work_mode`: remote, hybrid, office, unknown
- {any other column an agent fills}

## Anti-ICP (disqualify, keep the row)
A disqualified row stays in the list with its reason, so nobody researches it again.
- Under the size floor
- Competitors and companies that build the same thing (see `competitors/`)
- The company itself, its partners and resellers (see `suppression.md`)
- {regions you cannot sell to, sectors you will not serve}

## Scoring rubric
Four parts, scored separately, then added. Fit carries the list; the signal parts only rank within it.

| Part | Max | Moves | Measures |
|---|---|---|---|
| Fit | 40 | static | is this the right kind of company (segment, size, model, stack) |
| Prize | 25 | static | how big the win is (headcount in the roles that use the product, concentration of those roles) |
| Awareness | 15 | slow | do they already use the category, a rival, or the product |
| Timing | 20 | fluid | why now (hiring in target roles, a new leader, funding, a deadline) |

Weights are `[assumption]` until tested on a known set (see the score-tuning skill). The formula lives in the scoring spec next to the list, not here.

## Bands
| Band | Rule | What happens |
|---|---|---|
| hot | total >= {60} and confidence medium or high | personal outreach now |
| warm | {45} to below hot, confidence medium or high | after hot is done |
| cold | below {45}, confidence medium or high | nurture only |
| research | confidence low | not handed to sales until a page is read |
