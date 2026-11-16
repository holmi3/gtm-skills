# GTM engineering skills and templates

Five reusable agent skills and one template for go-to-market work, generalized from systems I built and ran: a context layer my agents read before they do anything, a scored and tuned account list, a second-reader review for every outreach draft, and a loop that turns outreach results into rule changes a person approves.

Everything here is data-free. Examples use invented companies on `.example` domains.

| Piece | What it does | Start with |
|---|---|---|
| [Context layer template](context-layer-template/) | A plain-file "company brain": ICP, positioning, personas, signals, suppression and a refresh loop where agents propose and a person merges | `prompts/bootstrap-interview.md` |
| [Scored lead model](skills/scored-lead-model/) | Interview, spec, then a deterministic four-part score (fit, persona or prize, intent or awareness, timing) with a reason string on every row | `SKILL.md` |
| [Score tuning](skills/score-tuning/) | Tune the model on strong, decent and bad test rows, one change per iteration, until the groups separate by a clear margin | `SKILL.md` |
| [Copy review](skills/copy-review/) | An independent reviewer scores how AI a draft sounds (1 to 10), checks hard rules and the recipient, and returns PASS or REVISE | `SKILL.md` |
| [Outreach learning loop](skills/outreach-learning-loop/) | Nightly results log, claims re-checked against the records, weekly pull requests a person merges, and a preflight every draft runs | `SKILL.md` |
| [TAM builder](skills/tam-builder/) | The whole account-list flow: ICP and exclusions, universe, public signals, score, tune, briefs, a ranked page for sales, hand check, export | `example/run_example.sh` |

## How they fit

```
context layer  -->  tam-builder (uses scored-lead-model + score-tuning)  -->  ranked list and briefs
      ^                                                                            |
      |                                                                     drafts for the top accounts
      |                                                                            v
outreach-learning-loop  <--  results  <--  a person sends  <--  copy-review
```

## Principles they share
- **A model reads, a script counts.** LLMs turn messy text into a value from a closed list with a quote. Scripts do every number, so a weight change is a one-line edit and a rerun.
- **Unknown is a value.** Missing data is shown as missing, never averaged or guessed.
- **Every claim has a source**, and every row explains itself.
- **A person decides.** Agents propose changes as pull requests and draft messages; nothing merges, syncs or sends on its own.
- **No personal data in git.** Roles and titles, never names.

## Try it
```
cd skills/tam-builder/example
bash run_example.sh        # Python 3.8+, standard library only
open output/ranked.html
```

The skills follow the `SKILL.md` format used by Claude Code and other agents that read skill folders; copy a folder into your agent's skills directory to install it.
