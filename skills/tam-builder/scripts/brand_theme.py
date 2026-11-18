#!/usr/bin/env python3
"""brand_theme.py: turn a client's homepage look into theme.json for render_page.py. Standard library only.

    python brand_theme.py --probe probe.json --client "Acme" --out theme.json   # from a probe a browser tool returned
    python brand_theme.py --url https://acme.example --client "Acme" --out theme.json   # runs the probe itself (needs Playwright)

The probe is scripts/theme_probe.js run on the rendered homepage: computed colors, fonts, the main call-to-action
button and the most used colors. This script turns it into design tokens for a light and a dark page, checks every
text pair for contrast (WCAG: 4.5 for text, 3 for chips and lines) and fixes the ones that fail, and lists what a
person should look at before the page goes out (fonts that will not load, a brand with no strong color).

Use: a page for the client themselves, in their own look. Do not publish a page that imitates a company to anyone
else, and leave their logo out unless the client asked for it.
"""
import argparse, colorsys, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------- color math ----------
def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    """t = share of b."""
    return hexc(tuple(x * (1 - t) + y * t for x, y in zip(rgb(a), rgb(b))))


def sat(h):
    r, g, b = rgb(h)
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn) / mx if mx else 0


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5


def best_text(bg, *candidates):
    pool = [c for c in candidates if c] + ["#000000", "#ffffff"]
    return max(pool, key=lambda c: (contrast(bg, c) >= 4.5, contrast(bg, c) if c in ("#000000", "#ffffff") else contrast(bg, c) + 2))


def push(color, bg, target):
    """Move a color's lightness away from bg until contrast(color, bg) >= target, keeping its hue."""
    if contrast(color, bg) >= target:
        return color
    r, g, b = (v / 255 for v in rgb(color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    darker = lum(bg) > 0.4
    for _ in range(60):
        l = max(0.0, l - 0.02) if darker else min(1.0, l + 0.02)
        c = hexc(tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s)))
        if contrast(c, bg) >= target:
            return c
    return "#000000" if darker else "#ffffff"


def fill(bg, preferred=None):
    """A filled chip or button: (background, text). Keeps the brand's own text color when a small shift in the
    background's lightness is enough to reach 4.5:1; otherwise keeps the background and picks black or white text."""
    preferred = preferred or ("#ffffff" if lum(bg) < 0.3 else "#000000")
    if contrast(bg, preferred) >= 4.5:
        return bg, preferred
    r, g, b = (v / 255 for v in rgb(bg))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    step = -0.01 if lum(preferred) > 0.5 else 0.01
    for _ in range(30):
        l = min(1.0, max(0.0, l + step))
        c = hexc(tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s)))
        if contrast(c, preferred) >= 4.5:
            return (c, preferred) if dist(c, bg) <= 70 else (bg, best_text(bg))
    return bg, best_text(bg)


# ---------- tokens ----------
def brand_colors(p, bg, fg):
    out = []
    if p.get("cta") and p["cta"].get("bg"):
        out.append(p["cta"]["bg"])
    for item in p.get("background_palette", []) + p.get("text_palette", []):
        c = item["color"]
        if sat(c) > 0.35 and dist(c, bg) > 60 and dist(c, fg) > 60 and all(dist(c, o) > 40 for o in out):
            out.append(c)
    if p.get("theme_color_meta") and re.match(r"^#[0-9a-fA-F]{3,6}$", p["theme_color_meta"]):
        if all(dist(p["theme_color_meta"], o) > 40 for o in out):
            out.append(p["theme_color_meta"])
    return out


def tokens(bg, fg, brands, heading=None, accent_fg=None):
    fg = push(fg, bg, 7)
    accent = brands[0] if brands else mix(fg, bg, 0.2)
    vanish = lambda c: sat(c) < 0.2 and contrast(c, bg) < 1.6  # a grey chip on a page of nearly the same grey
    if vanish(accent):
        accent = mix(fg, bg, 0.08)
    second = brands[1] if len(brands) > 1 and not vanish(brands[1]) else mix(accent, bg, 0.5)
    hot_bg, hot_fg = fill(accent, accent_fg)
    warm_bg, warm_fg = fill(second)
    surface_target = 0.035 if lum(bg) > 0.4 else 0.06
    t = {
        "bg": bg,
        "surface": mix(bg, fg, surface_target),
        "fg": fg,
        "heading": heading if heading and contrast(heading, bg) >= 4.5 else fg,
        "muted": push(mix(fg, bg, 0.45), bg, 4.5),
        "line": push(mix(bg, fg, 0.14), bg, 1.3),
        "accent": hot_bg,
        "accent_fg": hot_fg,
        "link": push(accent, bg, 4.5) if sat(accent) > 0.35 else fg,
        "hot_bg": hot_bg, "hot_fg": hot_fg,
        "warm_bg": warm_bg, "warm_fg": warm_fg,
        "cold": push(mix(fg, bg, 0.3), bg, 4.5),
        "research": push(mix(fg, bg, 0.55), bg, 3),
        "out": push(mix(fg, bg, 0.65), bg, 3),
    }
    return t


def checks(t, mode):
    pairs = [("fg", "bg", 4.5), ("muted", "bg", 4.5), ("heading", "bg", 4.5), ("link", "bg", 4.5), ("hot_fg", "hot_bg", 4.5),
             ("warm_fg", "warm_bg", 4.5), ("cold", "bg", 3), ("research", "bg", 3), ("out", "bg", 3), ("fg", "surface", 4.5)]
    return [{"mode": mode, "pair": f"{a} on {b}", "ratio": round(contrast(t[a], t[b]), 2), "ok": contrast(t[a], t[b]) >= need}
            for a, b, need in pairs]


def first_family(stack):
    return (stack or "").split(",")[0].strip().strip('"\'')


def build(p, client):
    bg, fg = p.get("page_bg") or "#ffffff", p.get("text") or "#111111"
    dark_site = lum(bg) < 0.2
    brands = brand_colors(p, bg, fg)
    cta_fg = (p.get("cta") or {}).get("fg")
    main = tokens(bg, fg, brands, p.get("heading_color"), cta_fg)
    if dark_site:
        dark, light_bg = main, mix("#ffffff", brands[0], 0.03) if brands else "#ffffff"
        light = tokens(light_bg, mix(bg, "#000000", 0.2), brands, None, cta_fg)
    else:
        light, dark_bg = main, mix("#121212", brands[0], 0.06) if brands else "#121212"
        dark = tokens(dark_bg, mix(bg, "#ffffff", 0.5), brands, None, cta_fg)

    body, heading = (p.get("fonts") or {}).get("body") or "", (p.get("fonts") or {}).get("heading") or ""
    fams = {first_family(body).lower(), first_family(heading).lower()}
    css_url, review = None, []
    for link in p.get("font_links", []):
        names = {n.replace("+", " ").split(":")[0].lower() for n in re.findall(r"family=([^&]+)", link)}
        if names & fams:
            css_url = link
    if not css_url and first_family(body).lower() not in ("", "system-ui", "-apple-system", "arial", "helvetica", "inter", "georgia"):
        review.append(f"Font '{first_family(body)}' is the site's own font and will not load on a viewer's machine; the page falls "
                      f"back to the rest of the stack. Pick a close Google Font and set fonts.css_url if the fallback looks off.")
    if not [b for b in brands if sat(b) > 0.35]:
        review.append("No strongly colored brand color found; hot and warm chips use the site's neutral button color. Check the "
                      "chips are easy to tell apart, or set warm_bg by hand.")
    ck = checks(light, "light") + checks(dark, "dark")
    review += [f"Contrast still low: {c['pair']} ({c['mode']}) {c['ratio']}" for c in ck if not c["ok"]]
    review.append("Open the page next to the client's homepage and compare: background, text, the button color, corners, font.")
    radius = (p.get("cta") or {}).get("radius") or "6px"
    m = re.match(r"([\d.]+)px", radius)
    radius = f"{min(float(m.group(1)), 16):g}px" if m else "6px"
    return {"client": client, "source_url": p.get("url"), "read_on": p.get("read_on"),
            "default_mode": "dark" if dark_site else "light",
            "fonts": {"body": body or "system-ui, sans-serif", "heading": heading or body or "system-ui, sans-serif",
                      "heading_weight": p.get("heading_weight") or "650", "css_url": css_url},
            "radius": radius, "brand_colors": brands, "light": light, "dark": dark, "checks": ck, "review": review}


def run_probe(url):
    try:
        from playwright.sync_api import sync_playwright  # optional dependency
    except ImportError:
        sys.exit("Playwright is not installed. Run theme_probe.js in a browser tool on the homepage, save the JSON it "
                 "returns, and pass it with --probe.")
    js = (HERE / "theme_probe.js").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1366, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=45000)
        probe = page.evaluate(js)
        b.close()
    return probe


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe"); ap.add_argument("--url"); ap.add_argument("--client", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not (a.probe or a.url):
        ap.error("--probe or --url is required")
    probe = json.loads(Path(a.probe).read_text(encoding="utf-8")) if a.probe else run_probe(a.url)
    theme = build(probe, a.client)
    Path(a.out).write_text(json.dumps(theme, indent=2), encoding="utf-8")
    bad = [c for c in theme["checks"] if not c["ok"]]
    print(f"wrote {a.out}: {theme['default_mode']} site, {len(theme['brand_colors'])} brand colors, "
          f"{len(theme['checks']) - len(bad)} of {len(theme['checks'])} contrast checks pass")
    for r in theme["review"]:
        print("  review:", r)


if __name__ == "__main__":
    main()
