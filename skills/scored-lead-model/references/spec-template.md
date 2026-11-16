# Scoring model v1 ({company}, YYYY-MM-DD)

Every number below is `[assumption]` until the eval rows pass and the owner signs off. The formula runs on columns every row has; no model picks a score.

## Rows and motion
- One row = {person | account}. Motion: {inbound | outbound}.

## Anti-ICP (disqualify, keep the row)
| Rule | Column | Matches | disqualified_reason |
|---|---|---|---|

## Fit, max {40} (static)
| Signal | Column | Points | Unknown when |
|---|---|---|---|

## {Persona | Prize}, max {25}
| Signal | Column | Points | Unknown when |
|---|---|---|---|

## {Intent | Awareness}, max {15}
| Signal | Column | Points | Unknown when |
|---|---|---|---|

## Timing, max {20} (fluid)
| Signal | Column | Points | Recency rule | Unknown when |
|---|---|---|---|---|

## Unknown
A part whose inputs are all blank or `unknown` scores 0, is listed in `missing_parts`, and the why string says "unknown (<reason>)". Never averaged.

## Confidence
- low: {rule}
- medium: {rule}
- high: {rule}

## Bands
| Band | Rule | What happens |
|---|---|---|

## Eval rows
| Row | Expected | Why |
|---|---|---|
| {domain or id} | top | |
| {domain or id} | bottom | |

## Never
- {from question 14}

## TODO
- {every skipped question}
