# Stage 0: a context layer from the client's website

Before any list, the agent learns the client from their own public pages and writes what it learns into a context layer (`../../../context-layer-template`). The ICP interview in stage 1 then starts from suggestions with sources, so the client corrects a draft instead of filling a blank form. The same visit reads the client's look for the ranked page.

Only the client's own site and public pages about them. No logins, no forms, no gated downloads.

## Steps

1. **Copy the template.** `cp -r context-layer-template <client>-context` (or open the client's existing context layer and skip to step 3 for anything already filled).

2. **Read the client's pages.**
   ```
   python scripts/fetch_pages.py --domain <client-domain> --preset client --out <client>-context/research/pages
   ```
   This saves the homepage, pricing, customers or case studies, product and integrations, security or trust, about and careers pages as text, and follows the homepage's own links to them. Check `research/pages/index.csv`: a page marked `thin_page_try_browser` or `error:...` is drawn by JavaScript or blocked for scripts. Read it with a browser tool instead, save the text, and register it:
   ```
   python scripts/fetch_pages.py --import-text saved.txt --url <page-url> --out <client>-context/research/pages
   ```

3. **Read the client's look** (for stage 6). Open the homepage in a browser tool, let it load, run `scripts/theme_probe.js` as page JavaScript, and save the JSON it returns as `<client>-context/research/homepage_probe.json`. Then:
   ```
   python scripts/brand_theme.py --probe <client>-context/research/homepage_probe.json --client "<Client>" --out theme.json
   ```
   Where Playwright is installed, `--url https://<client-domain>` does both in one step. See `client-theme.md`.

4. **Draft the context files from the saved pages.** One pass per file, quoting the page each line rests on:

   | File | What to draft from the pages |
   |---|---|
   | `context/company.md` | what they sell, to whom, products and plans, price points shown, regions served |
   | `context/positioning.md` | their own words for the problem, the point of difference they claim, public proof (logos, numbers, case studies) |
   | `context/personas.md` | the titles their case studies and pricing page speak to (titles, never people) |
   | `context/icp.md` | segments the customer page implies (industry, size, motion), a size range from the plans, anti-ICP hints (plan limits, "not for") |
   | `context/signals.md` | what a good-fit account would show in public: job posts for a role the product serves, a tool the product replaces or connects to, a compliance need from the trust page |
   | `context/competitors/` | rivals the client names (comparison pages, "switch from" pages), one file each |
   | `context/suppression.md` | which lists to ask for: customers named on the site, partners on the integrations page |

   Rules for every line: tag `[source: <url>, read YYYY-MM-DD]` when a saved page says it, `[assumption]` when it is the agent's reading of several pages. Never `[stated by user]` before the client has said it. Every `[assumption]` gets a `QUESTIONS.md` line.

5. **Show the draft, then interview.** Give the client a one-screen summary: what you think they sell, to whom, the segments you see, the closed lists you propose, and the three biggest open questions. Then run `prompts/bootstrap-interview.md` from the template: each question opens with the drafted answer and its source, so most answers are "yes" or a short correction. Answers become `[stated by user]` lines.

6. **Hand over to stage 1.** The ICP, positioning, personas, signals and suppression files are what stage 1 turns into `scoring_model.md` and `model.json`.

## What good looks like
- Every line in `context/` has a tag, and a person can open the saved page behind every `[source]` line.
- The client has corrected the draft at least once. A draft nobody pushed back on was probably not read.
- `QUESTIONS.md` holds what the pages cannot say: deal sizes, win rates, who actually signs, which segment the team wants first.
