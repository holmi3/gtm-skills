# The ranked page in the client's look

The ranked page is something the client's team opens every day, so it should look like theirs: their background, text and button colors, their font, their corners. `brand_theme.py` reads that from the client's homepage and writes `theme.json`; `render_page.py --theme theme.json` uses it.

## Steps
1. **Probe the homepage.** In a browser tool, open the client's homepage, wait for it to load, and run `scripts/theme_probe.js` as page JavaScript. It changes nothing; it returns one JSON object with the computed page background, text and heading colors, the main call-to-action button (its color, text color and corner radius), the fonts, any Google or Bunny font link, the `theme-color` meta tag, and the most used colors by area and by text. Save it as `homepage_probe.json`.
   With Playwright installed, `python scripts/brand_theme.py --url https://<client-domain> ...` runs the probe itself.
2. **Build the theme.**
   ```
   python scripts/brand_theme.py --probe homepage_probe.json --client "<Client>" --out theme.json
   ```
   It picks the brand colors (the button first, then strongly colored, frequent colors), builds tokens for a light and a dark page (whichever the site is not, it derives), and checks every text pair for contrast: 4.5:1 for text, 3:1 for chips and lines. A pair that fails is fixed by moving the color's lightness, keeping its hue. A filled chip keeps the brand's own text color when a small shift of the fill is enough.
3. **Read the review lines** it prints, for example:
   - the site's font is its own and will not load for viewers: pick the closest Google Font and set `fonts.css_url` and `fonts.body` in `theme.json`
   - no strongly colored brand color: the hot and warm chips use the site's neutral colors; check they are easy to tell apart or set `warm_bg` by hand
4. **Render and compare.**
   ```
   python scripts/render_page.py ... --theme theme.json
   ```
   Open the page next to the client's homepage, in light and dark (the button top right switches). Compare background, text, the button color, corners and font. Edit `theme.json` by hand if something is off; it is plain data and every value is checked again when the page renders.

## Tokens
`bg`, `surface` (cards and the table), `fg`, `heading`, `muted`, `line`, `accent` and `accent_fg` (the switch button and the header rule), `link`, `hot_bg` and `hot_fg`, `warm_bg` and `warm_fg` (filled chips), `cold`, `research` and `out` (outlined chips), one set under `light` and one under `dark`. Plus `fonts` (`body`, `heading`, `heading_weight`, `css_url`), `radius` (from the button, at most 16px) and `default_mode` (the mode the page opens in: the site's own).

Without `--theme`, the page uses a neutral built-in look with the same tokens.

## Limits
- Use it for a page made for the client, about their own market. Do not publish a page that imitates a company to anyone else.
- No logo, unless the client asks for one and provides it.
- A page drawn on a canvas or behind a cookie wall can give odd colors; check the probe's `page_bg` and `cta` before trusting the theme.
