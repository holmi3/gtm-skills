# Model format (`model.json`)

The model is data. `scripts/score.py` holds no weights of its own, so a weight change is a one-line edit and a rerun. See `../example/model_v3.json` for a complete file.

## Top level
| Key | What |
|---|---|
| `name` | shown on the page; say what changed in this version |
| `key` | the row key column, usually `domain` |
| `parts` | ordered map of score parts: `{"fit": {"max": 40, "unknown_note": "...", "rules": [...]}, ...}` |
| `disqualify` | conditions that zero a row and set band `out` |
| `confidence` | how confidence is computed |
| `bands` | `{"hot": 60, "warm": 45}` |
| `owner_rules` | first-match table for the likely owner (stage 5) |
| `brief` | brief scope, length, field labels, banned words (stage 5) |
| `fields` | optional closed lists for columns agents fill, used by `apply_evidence.py`: `{"work_mode": ["remote", "hybrid", "office"], "employees": "number"}`. Without it the lists come from the rules: a `map` rule's values, `yes`/`no` for a `flag`, a number for `bands`. `unknown` is always allowed. |

## Rule types (inside a part's `rules`)
Every rule may carry `label`, `note` (why it exists; name the row that exposed it) and `only_if` (a list of conditions; the rule is skipped, not unknown, when they fail).

| Type | Keys | Points |
|---|---|---|
| `map` | `column`, `points` (value to points), optional `default`, `names` (value to receipt text), `best_of` + `split` for multi-value cells | points for the cell's value |
| `flag` | `column`, `equals` (default `yes`), `points` | points when the cell matches |
| `bands` | `column`, `steps` `[{"min", "max", "points"}]` first match wins, optional `recency` | points for the number's band, times the recency multiplier |
| `ratio` | `num`, `den`, `steps` on the share | points for a concentration, for example agents / staff |
| `count_of` | `any` (list of conditions), `each`, `max` | points per condition met |

`recency`: `{"column": "last_job_post", "multipliers": [[183, 1.0], [365, 0.85], [548, 0.65], [null, 0.4]]}` (days since the date, then the multiplier).

## Unknown
A rule whose input cell is blank or `unknown` is unknown. A part where every rule is unknown scores 0, is listed in `S<n>-missing`, and the receipt reads `<part> unknown (<unknown_note>)`. It is never filled with an average. Negative rules count; each part is clamped to 0 and its max.

## Conditions
`{"column": "...", "op": "...", "value": ...}` with ops `eq`, `ne`, `in`, `not_in`, `nonblank`, `blank`, `gte`, `lt`, `contains`.

## Disqualify
A list of conditions, checked first. `"reason": "from_column"` copies the cell (for an `exclusion_reason` column); any other string is written as the reason.

## Confidence
```json
{"read_column": "page_read", "min_known_parts": 3,
 "quotable": [{"column": "rival_tool", "op": "in", "value": ["legacy_helpdesk"]}]}
```
low = no page read or fewer than `min_known_parts` parts known; high = medium plus at least one quotable condition; medium otherwise. Low confidence always bands as `research`.

## Output columns per set
`S<n>-<part>` for each part, `S<n>-total`, `S<n>-confidence`, `S<n>-band`, `S<n>-missing`, `S<n>-why` (the receipt), `S<n>-scored_on`, and a plain `band` that follows the last set written.

## Owner rules
```json
[{"when": [{"column": "industry", "op": "in", "value": ["fintech"]}], "owner": "Head of Support Operations",
  "champion": "support operations lead", "basis": "regulated industry ... [assumption]"},
 {"when": [], "owner": "Head of Support", "champion": "", "basis": "... [assumption]"}]
```
First match wins; an empty `when` is the fallback.
