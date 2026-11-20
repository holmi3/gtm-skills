# Research session prompt

The standing prompt for one research run on the layer. Replace the braces.

```
Read CLAUDE.md, AGENTS.md, ontology.md, context/icp.md, context/signals.md and context/research-playbook.md. Their rules win over this prompt.

Task: {research segment N / fill column X for the hot and warm rows / check the 25 top accounts by hand}.
Scope: {rows, segment, or a file}. Budget: {calls or credits}; stop and ask before going over it.

1. Run 10 rows first and show me what came back and what it cost before running the rest.
2. Public sources only, passive reads. Every finding gets a URL and a read date in the evidence file, and a confidence (high, medium, low).
3. Classify against the closed lists in icp.md. A value outside the list is "unknown" plus a note.
4. Never fill a gap with a guess. "Not found after reading <page>" is a finding; "not checked" is not.
5. Write research/YYYY-MM-DD-<topic>.md from research/_template.md.
6. If a context file turned out wrong or thin, propose the change per loop/refresh-loop.md (or edit it directly if AGENTS.md says bootstrap) and log it in loop/log.md.
7. Do not commit, push or send anything. Report: rows touched, what changed, what it cost, what is still unknown.
```
