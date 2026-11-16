# Bootstrap interview: fill the context layer

Paste the box into Claude Code (or any agent that can read and write files) opened in a copy of this template. It interviews you one question at a time and writes the answers into the right files with tags.

```
You are filling a plain-file context layer with me. The folder you are in is the template. Read AGENTS.md, CLAUDE.md and ontology.md first and follow their rules for the whole session.

How to ask:
- ONE question per message. Wait for my answer.
- Start each question with a suggested answer if anything you have read or found on a public page lets you make one, so I can reply "yes" or correct it. Cite the page for any suggestion that came from the web.
- Show the number ("Question 4 of 16").
- If I say "skip" or "I don't know", write a QUESTIONS.md line for it and move on.
- Never invent a fact. Tag every line you write: [source: <url>, read YYYY-MM-DD] for a public page, [stated by user] for my answers, [assumption] for anything else.

Before the first question, ask me for the company name and domain, then read its homepage, pricing page, trust or security page and careers page (public pages only, passive reads) so your suggestions are grounded.

Questions, in this order:
1. In one sentence: what does the company sell, and to whom? -> context/company.md
2. Products and plans, from the pages you read: correct? -> context/company.md
3. What is the point of difference against the status quo and the nearest rival? -> context/positioning.md
4. Who signs, who buys, who champions? Titles only. -> context/personas.md
5. Which size tiers are primary, which need a confirm step, which are out? -> context/icp.md
6. Which segments, and which one goes first? -> context/icp.md
7. For each segment: the one public signal that defines it, and where it can be seen. -> context/signals.md
8. Anti-ICP: who is disqualified no matter what? -> context/icp.md
9. Who never gets contacted (customers, partners, competitors, do-not-contact)? Where do those lists come from? Do not paste the lists here. -> context/suppression.md
10. The three closest competitors (I will fill one file each from public pages after the interview). -> context/competitors/
11. The offer per segment and the first step we ask for. -> context/positioning.md
12. Proof points that are public. -> context/positioning.md
13. Outreach mechanics: channels, number of touches, who sends. -> context/outreach-rules.md
14. Bands: the score cut-offs for hot, warm, cold, and how many accounts the team can actually work per week. -> context/icp.md
15. Who owns the refresh loop, and on what schedule? -> loop/refresh-loop.md
16. Anything an agent must never do with this layer or its data? -> CLAUDE.md (I approve the exact wording)

After question 16:
- Fill context/competitors/<name>.md for each named rival from public pages, same headings as _template.md.
- Show me a summary: files written, lines per tag type ([source], [stated by user], [assumption]), and the QUESTIONS.md lines added.
- Append one line to loop/log.md.
- Do not commit or push. I review the diff and commit myself.
```
