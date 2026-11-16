# Building the universe

The universe is every company that could plausibly buy, before scoring. Breadth first: a TAM is a breadth list, and the score does the narrowing.

## Sources, cheapest first
1. **Job-post and technology searches per segment.** A company whose job posts name the category, a rival tool or the defining workflow is evidence of how it works. One search per segment, saved with its exact query.
2. **Firmographic company search** (industry, size, country) for segments defined by what the company is rather than what it does.
3. **Public customer, partner and integration pages** of the seller and its rivals. Customers of the seller go to suppression or an expansion list, depending on the motion.
4. **Lookalikes** of the strongest accounts, as round two once the first score exists.

For each source: sample 10 rows, read the cost estimate, then run. Web tables that cap their rows will silently truncate a segment; record when a cap was hit.

## Cleaning
- Key on the root domain, lower case. Strip `www`, paths and tracking parameters.
- Duplicates: keep one row, merge `list_source` and `segments_all`, record `duplicate_of` on the dropped one (or drop it if it was never researched).
- Product domains and subsidiaries: fold into the parent only when the parent sells and buys for it; otherwise keep separate and note the parent.
- Dead domains, acquired companies, non-companies (communities, open-source projects, nonprofits when out of scope): disqualify with a reason.
- A count from a data source is headcount only if the source says so. A count of mentions is not a count of people; keep a `count_type` column and let the model ignore mentions.

## Splits
- Competitors and builders go to `competitors.csv`, never into the account list.
- Out-of-territory rows go to their own file with the same columns, so they can be scored later without a rebuild.
- Rows with no country stay in the main file with a blank, to be filled from a public page.

## Log
`research/YYYY-MM-DD-universe.md`: rows per source, per segment, duplicates removed, rows moved, caps hit, cost.
