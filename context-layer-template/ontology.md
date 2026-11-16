# Ontology

Write the objects and how they relate before any content goes in. Storage is an implementation detail; the same objects work in files, a database or a paid messaging tool.

## Objects

| Object | File | One entry has |
|---|---|---|
| Product | `context/company.md` | name, what it does, plan or tier, source URL |
| Segment | `context/icp.md` | who (size, industry, stack, work mode), why they buy, disqualifiers |
| Persona | `context/personas.md` | title pattern, what they own, what they care about, qualifiers, role in the deal (signer, buyer, champion, user) |
| Use case | `context/positioning.md` | job to be done, which personas, which products |
| Signal | `context/signals.md` | what it is, where it comes from, how fresh it must be, which part of the score it feeds |
| Competitor | `context/competitors/<name>.md` | overlap, how to position, source URL |
| Proof point | `context/positioning.md` | the claim, the number, the customer, source URL |
| Objection | `context/positioning.md` | the objection, persona, answer, proof point used |
| Suppression rule | `context/suppression.md` | rule key, what it matches, why |
| Motion | (a field on every entry) | net new, expansion, renewal |

## Relations agents traverse
- Segment -> personas -> use cases -> products
- Persona + use case -> objections, discovery questions, proof points
- Competitor -> objections ("we already use X")
- Signal -> score part (fit, prize, awareness, timing) -> band -> play

A meeting brief is the cross-section for one meeting: the attendee's persona, in the account's segment, on its likeliest use case. An account brief is the same cross-section without a meeting.
