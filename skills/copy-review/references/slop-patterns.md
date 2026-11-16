# Slop patterns

Section A is enforced by `scripts/lint.py` (phrases in `scripts/banned_phrases.txt`). Sections B and C are judged by the reviewer. Partly based on the public Wikipedia guide "Signs of AI writing", plus tells specific to cold outreach.

## A. Banned phrases (hard fail, H8)
Openers ("I hope this message finds you well", "I came across your profile", "I wanted to reach out"), filler and hype ("leverage", "synergy", "game-changer", "seamless", "delve", "transformative"), closers ("Please don't hesitate", "I look forward to hearing from you", "Best regards") and chatbot artifacts ("Certainly", "Great question"). The full list is in the script's phrase file.

## B. Structural tells (reviewer judges)
1. **The template:** compliment, pivot to self, three benefits, ask.
2. **Vague flattery:** "impressive background", "great work". If it fits anyone, it fails.
3. **Rule of three:** forcing ideas into triplets. One strong point beats three.
4. **Negative parallelism:** "not just X, but Y", "it's not about X, it's about Y".
5. **Significance inflation:** "marks a pivotal moment", "plays a vital role".
6. **Superficial -ing tails:** ", showcasing...", ", highlighting...".
7. **Copula avoidance:** "serves as", "stands as", "boasts" instead of "is" or "has".
8. **Elegant variation:** swapping synonyms to avoid repeating a word.
9. **Rhetorical question answered right away:** "The result? ..."
10. **Dramatic fragments:** "Simple. Fast. Reliable."
11. **Authority tropes:** "The real question is", "At its core".
12. **Signposting:** "Here's the thing", "Let me explain".
13. **Hedging stacks:** "might potentially". One hedge at most.
14. **Weak adverbs:** very, really, quite, truly, basically, actually.
15. **Passive voice hiding who did it:** "a pipeline was built". Say who built it.
16. **Sycophancy and reassurance kickers:** "no pressure at all!", "totally understand if you're busy!" One light easy out is fine.
17. **Sentence-opener tics:** "Interestingly,", "Additionally,", "Moreover,".
18. **Uniform rhythm:** every sentence the same length.
19. **Over-polish:** perfect parallel structure, zero contractions, words nobody says out loud.
20. **Fake specificity:** a detail that sounds researched but is generic ("your work in the SaaS space").
21. **Hyphen pairs:** "data-driven", "results-oriented".
22. **Title Case or bold anywhere in the message.**
23. **Exclamation points:** one at most, usually none.
24. **PS lines** used as a second pitch.

## C. Soft vocabulary (warn; replace if a plainer word works)
additionally, crucial, foster, garner, intricate, landscape, interplay, showcase, underscore, vibrant, robust, utilize, facilitate, endeavor, comprehensive, innovative, dynamic, impactful, insights, journey, space (as in "the AI space"), ecosystem, align, alignment, opportunity (when vague).

## Before and after
AI slop:
> I hope this message finds you well! I came across your profile and was truly impressed by your background in revenue operations. I'd love to connect and explore potential synergies between our teams.

Human:
> Saw your team moved support onto a shared inbox last quarter. How did the agents take the switch? Happy to compare notes.
