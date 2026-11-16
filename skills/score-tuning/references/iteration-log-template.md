# Scoring iterations

Test set: {n} rows in `test_set.csv` ({n} strong, {n} decent, {n} bad). Stop rule: strong > decent > bad on the latest total, each group's lowest at least {5} above the next group's highest.

## S1: baseline

| Group | Range | Median |
|---|---|---|
| strong | | |
| decent | | |
| bad | | |

Separation: PASS / FAIL ({group} lowest minus {group} highest = {n}).

Rows judged wrong:
| Row | Total | Verdict | Part | Why, with the fact (and source) |
|---|---|---|---|---|

Cause: weight or rule / missing or wrong input / test group wrong.

## S2: {one line on what changed}

Change: {file, rule, old value -> new value}. Exposed by: {row}.

| Row | S1 | S2 | Change |
|---|---|---|---|

Separation: PASS / FAIL. Right rows moved by more than 5: {none / which, and the decision}.

## Still in dispute
- {row}: {formula says, judgment says, what would settle it}
