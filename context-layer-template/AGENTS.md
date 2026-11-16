# AGENTS.md: start here

The context layer for **{Company}** ({domain}): the plain files any agent reads before it researches accounts, scores a list or drafts a message. `CLAUDE.md` holds the hard rules. Every fact in this repo is reachable from this table in three links or fewer.

**Status: `bootstrap`.** While this line says `bootstrap`, agents may edit `context/` directly and must log each change in `loop/log.md`. When the owner changes it to `stable`, every change to `context/` goes on a branch as a pull request (see `loop/refresh-loop.md`).

## What this layer is for
{One or two sentences: the job this layer supports, for example "a scored account list and meeting briefs for the sales team, built from public sources only".} `[stated by user]`

## Routing table

| If you need | Read | Notes |
|---|---|---|
| The objects and how they relate | `ontology.md` | read once per session |
| What the company sells: products, plans, platforms | `context/company.md` | public pages only, each line sourced |
| Why a customer buys, the point of difference, the offer per segment | `context/positioning.md` | the scoring rubric is supposed to encode this |
| Which segments to target, size tiers, anti-ICP, the scoring rubric | `context/icp.md` | one segment first; the rest wait |
| Who buys, signs and champions | `context/personas.md` | roles and titles, never people |
| Public signals per segment and their sources | `context/signals.md` | |
| Who never gets contacted | `context/suppression.md` | check before any handoff |
| A rival and how to position against it | `context/competitors/<name>.md` | identical headings in every file |
| How to research and score an account cheaply | `context/research-playbook.md` | read before any run |
| Channels, cadence, guardrails and what results have shown | `context/outreach-rules.md` | "What the results say" holds accepted learnings |
| What a research run found | `research/YYYY-MM-DD-<topic>.md` | one file per run |
| What still needs an answer | `QUESTIONS.md` | add a line when a task hit a gap |
| How files here change, and what changed | `loop/refresh-loop.md`, `loop/log.md` | |

## Principles
1. **One home per fact.** A fact lives in one file; everything else links to it.
2. **Tag every claim.** `[source: <url>, read YYYY-MM-DD]`, `[stated by user]` or `[assumption]`. An untagged line is an assumption.
3. **Three hops max** from this file. If a fact needs more, fix the layout instead of duplicating the fact.
4. **Lean beats thorough.** A file exists only if an agent reads it during real work. Split a file past about 150 lines.
5. **Accounts before contacts.** Build and score the account list first. People come later and never go into git.
6. **Fit apart from intent.** Static fit and fluid timing stay in separate columns, so nobody mistakes a good-fit account for a ready one.
7. **The offer before the list.** A row with no "now what" is a spreadsheet nobody uses; every account gets an angle from `positioning.md`.
8. **Nothing sends.** Agents research, score and draft. A person sends.

## How a session runs
1. Read `CLAUDE.md`, this file, `ontology.md`, then only the files the task needs.
2. Do the work. Write findings to `research/YYYY-MM-DD-<topic>.md` with one source line per claim and a list of what is still unknown.
3. If a context file turned out wrong or thin: fix it (status `bootstrap`) or propose it (status `stable`). Leave `TODO:` where a source is still missing.
4. Append one line to `loop/log.md`: date, what changed, why.

## Skills
List the skills that run on this layer here, one line each: name, what it does, where it lives.
