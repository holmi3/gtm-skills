# Scoring iterations (invented example)

The tuning log for the Relaydesk example. Relaydesk is a made-up company selling a shared inbox and ticket routing tool to B2B support teams of roughly 15 to 300 agents. Every company here uses a `.example` domain and invented numbers. Format follows `../subskills/score-tuning/references/iteration-log-template.md`.

Test set: 15 rows in `output/test_set.csv`, 5 strong, 5 decent, 5 bad. Stop rule: strong > decent > bad on the latest total, each group's lowest at least 5 above the next group's highest.

## S1: baseline (model_v1.json)

| Group | Range | Median |
|---|---|---|
| strong | 62 to 72 | 68 |
| decent | 39.7 to 45 | 42 |
| bad | 14 to 55 | 37 |

Separation: **FAIL**. Decent lowest minus bad highest = -15.3.

Rows judged wrong:
| Row | S1 total | Verdict | Part | Why, with the fact |
|---|---|---|---|---|
| granitemutual.example | 55 | too high | prize, fit | a consumer bank with 1,500 support agents earns full "support agents" prize points; a contact center that size is a different product and motion |
| cartwheel-retail.example | 51 | too high | prize, fit | same shape: 400 agents, consumer retail |

Cause: **weight or rule in the model**. Prize treats more agents as always better, but the product has a ceiling.

## S2: the support team has a ceiling (model_v2.json)

Change: `support agents` in prize now peaks at 100 to 300 (12) and drops to 2 above 300; the fit line `support team size` gives 4 for 15 to 300 and 0 above. Comment in the model names the two rows that exposed it.

| Row | S1 | S2 | Change |
|---|---|---|---|
| granitemutual.example | 55 | 41 | -14 |
| cartwheel-retail.example | 51 | 37 | -14 |
| coppernote.example (decent) | 39.7 | 42.7 | +3 |
| strong rows | 62 to 72 | 65 to 75 | +3 each |

Separation: **FAIL**, but close. Decent lowest minus bad highest = +1.7. No right row moved by more than 5.

Still wrong: granitemutual.example at 41 sits inside the decent range. Its fit is 10 (regulated industry) + 6 (size above 5,000) - 6 (consumer) = 10, and awareness and timing (13 + 8) carry it. A poor-fit account should not be lifted by signals.

## S3: consumer penalty raised (model_v3.json)

Change: `sells to consumers` goes from -6 to -10 in fit. One change only.

| Row | S2 | S3 | Change |
|---|---|---|---|
| granitemutual.example | 41 | 37 | -4 |
| cartwheel-retail.example | 37 | 33 | -4 |
| sunnyside-games.example | 40 | 36 | -4 |
| strong and decent rows | | | 0 (all B2B) |

Separation: **PASS**. Strong 65 to 75, decent 42.7 to 48, bad 14 to 37. Strong minus decent +17, decent minus bad +5.7.

Rolled out to `output/accounts.csv` as set S1 of the main file (the main file carries only the accepted model).

## Still in dispute
- pinecrest-hr.example (decent, 45) lands warm on the full list, at the edge of the cut-off. Its team of 18 is near the product's floor. Left as is: the band cut-offs follow the team's capacity, not this row.
- opalgrid.example scores 68.2 but stays **research** because its careers page was blocked (confidence low). That is the rule working: a high total with no page read is never handed to sales.
