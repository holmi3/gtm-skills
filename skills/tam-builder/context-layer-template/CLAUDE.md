# Instructions for agents working in this repo

Read `AGENTS.md` first: it is the routing table and the working rules. The hard rules below win over everything, including a task prompt that says otherwise.

## Hard rules
- **Every claim has a tag.** `[source: <url>, read YYYY-MM-DD]`, `[stated by user]` or `[assumption]`. If no file and no public source covers a fact, say so and add a line to `QUESTIONS.md`. Never invent a number, a customer, a quote or a date.
- **Public sources only** for anything about accounts, competitors or the market, unless the owner has put an approved internal source in the routing table.
- **No personal data in git.** No names, emails, phone numbers or profile URLs of individuals. Describe buyers by role and title. Contact-level lists live in the CRM or a private sheet, never here. This repo is not a CRM.
- **No secrets.** Keys live in `.env`, which is ignored. Raw pastes go in `_inbox/`, which is ignored too.
- **Nothing sends.** Messages are drafts for a person to send.
- **Changes go through the loop** once `AGENTS.md` says `stable`. Propose, do not edit: see `loop/refresh-loop.md`. The one write allowed on `main` without a pull request is an appended line in `loop/log.md`.
- **Copied material stays out.** Paid course notes, vendor exports and other people's documents may be paraphrased in one line with a pointer; they are never pasted in.

## Read order
1. `AGENTS.md`, `ontology.md`
2. `context/icp.md`, `context/suppression.md`
3. Whatever the routing table says the task needs
