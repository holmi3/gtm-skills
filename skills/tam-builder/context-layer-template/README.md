# Context layer template

A plain-file "company brain" that AI agents (Claude Code, Codex, Cursor, any agent that can read a folder) read before they research accounts, score a list or draft a message. It holds **authored context**: what the company sells, who buys it, how to talk about it, who never gets contacted, and how the files themselves change over time.

This is the empty structure, the rules and the prompts. There is no company data in it. Copy the folder, run the bootstrap interview in `prompts/bootstrap-interview.md`, and the agent fills it with you one question at a time.

## Why plain files

- **Captured vs authored context.** Your CRM, call recordings and product usage are captured context; tools already collect them. The ICP, the positioning, the rules of engagement and the exclusions are authored context. People carry them in their heads, so agents never see them. A versioned folder is the cheapest way to hand them over.
- **Curation, not collection.** Each file is the distilled answer for one kind of task. A file nobody reads during real work gets deleted.
- **Ontology first.** `ontology.md` names the objects (products, personas, use cases, segments, competitors, motions) before any content goes in, so every agent traverses the same map.
- **Two-way, with a human gate.** Agents propose edits as small pull requests with the evidence attached. A person merges or closes. Nothing changes on `main` without a human.
- **Every claim is tagged.** `[source: <url>, read YYYY-MM-DD]`, `[stated by user]` or `[assumption]`. An untagged line is treated as an assumption. An agent that cannot find a fact writes a line in `QUESTIONS.md` instead of inventing it.

## Layout

```
AGENTS.md                start here: routing table (what to read for what), principles, three-hop rule
CLAUDE.md                hard rules; wins over everything else
QUESTIONS.md             what agents still need from a person
ontology.md              the objects and how they relate (fill this first)
context/
  company.md             what the company sells: products, plans, platforms, public proof
  positioning.md         why a customer buys, point of difference, offer per segment
  icp.md                 segments, size tiers, anti-ICP, the account scoring rubric
  personas.md            who buys, who signs, who champions (roles and titles, never people)
  signals.md             public signals per segment and where each one comes from
  suppression.md         who never gets contacted: customers, partners, rivals, anti-ICP rules
  competitors/_template.md   one file per rival, identical headings
  research-playbook.md   how to research and score an account cheaply
  outreach-rules.md      channels, cadence, guardrails, and "what the results say"
agents/
  meeting-prep.md        example agent: a domain and attendee roles in, a one-page brief out
research/_template.md    one file per research run
proposals/_example.md    what a refresh-loop proposal looks like
loop/
  refresh-loop.md        the rule: scheduled runs propose diffs, a human accepts
  log.md                 append-only record of what the loop changed
prompts/
  bootstrap-interview.md fill the layer with an interview, one question at a time
  research-session.md    the standing prompt for a research run
```

## How to start

1. Copy this folder into a new private repo.
2. Open your agent in the folder and paste `prompts/bootstrap-interview.md`.
3. Answer one question at a time. Say "skip" when you don't know; it becomes a `QUESTIONS.md` line.
4. Review the diff, commit, and set `AGENTS.md` status from `bootstrap` to `stable` when you trust it. From then on changes arrive as proposals (see `loop/refresh-loop.md`).

## Pairs with

- The TAM builder this template ships inside (`skills/tam-builder`): builds and scores the account list from this layer.
- `skills/outreach-learning-loop`: turns real results into proposals against `context/outreach-rules.md` and `context/icp.md`.
- `skills/copy-review`: the second reader every draft goes through.

## Credits

Inspired in part by the brainstarter skill from Jared Waxman's GTM Engineer School, which also builds a plain-file company brain from an interview and tags every line with its source. This template adds the refresh loop (agents propose, a person merges), suppression rules, and learning from real outreach results.
