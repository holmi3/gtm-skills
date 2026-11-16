#!/usr/bin/env python3
"""Deterministic checker for the copy-review skill: hard rules, banned phrases, length per channel.

Edit CHANNELS below and scripts/banned_phrases.txt to match your own rules (references/hard-rules.md says which
check is which).

Usage:
  python3 scripts/lint.py --channel dm message.txt
  echo "text" | python3 scripts/lint.py --channel connection-note -
  python3 scripts/lint.py --channel cold-email --json msg.txt

If the first line starts with "Subject:" it is treated as the subject line.
Exit code 0 = no FAILs, 1 = at least one FAIL, 2 = usage error.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANNELS = {
    # channel: (min_words, max_words, max_chars, max_hyphen_compounds, needs_subject)
    "connection-note": (0, 60, 300, 0, False),
    "dm": (20, 90, None, 1, False),
    "inmail": (50, 100, None, 1, True),
    "cold-email": (25, 70, None, 1, True),  # as short as a DM
    "nudge": (6, 30, None, 0, False),       # after a connection is accepted: thanks plus a concrete time
    "follow-up": (20, 60, None, 1, False),
    "thank-you": (40, 100, None, 1, False),
    "info-ask": (50, 90, None, 1, False),
}
SOFT_VOCAB = ["additionally", "crucial", "foster", "garner", "intricate", "landscape", "interplay", "showcase",
              "underscore", "vibrant", "robust", "utilize", "facilitate", "endeavor", "comprehensive", "innovative",
              "dynamic", "impactful", "insights", "journey", "ecosystem", "alignment", "moreover", "furthermore",
              "interestingly", "importantly"]
WEAK_ADVERBS = ["very", "really", "quite", "truly", "basically", "essentially", "actually", "incredibly",
                "genuinely", "honestly", "definitely"]
SUPERIORITY = [r"\bunique(ly)?\b", r"\bunlike (most|other)\b", r"\bthe right person\b", r"\bideal candidate\b",
               r"\bbest candidate\b", r"\bstand out\b", r"\bstands? out from\b"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⬆↔-⇿]")


def load_phrases():
    out = []
    for line in (HERE / "banned_phrases.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line.lower())
    return out


def phrase_regex(p):
    parts = [re.escape(w) for w in p.split()]
    body = r"\s+".join(parts).replace("'", "['’]").replace(r"\-", r"[-\s]?")
    return re.compile(r"(?<![\w])" + body + r"(?![\w])", re.I)


def lint(text, channel):
    fails, warns = [], []
    text = text.replace("\r\n", "\n").strip("\n")
    subject = None
    lines = text.split("\n")
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
    else:
        body = text.strip()
    full = (subject + "\n" if subject else "") + body
    no_urls = re.sub(r"https?://\S+|www\.\S+|\S+@\S+\.\w+", " ", body)

    # H1 dashes
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        if ch in full:
            fails.append(f"H1 {name} found ({full.count(ch)}x)")
    if re.search(r"\w\s+-{1,2}\s+\w", no_urls) or "--" in no_urls:
        fails.append("H1 spaced hyphen or double hyphen used as a dash")
    # H2 colons
    c = re.sub(r"\b\d{1,2}:\d{2}\b", " ", no_urls)
    if ":" in c:
        fails.append(f"H2 colon in body prose ({c.count(':')}x)")
    # H3 hyphen compounds
    comps = re.findall(r"\b[A-Za-z]+(?:-[A-Za-z]+)+\b", no_urls + " " + (subject or ""))
    mn, mx, maxc, maxh, needs_subject = CHANNELS[channel]
    if len(comps) > maxh:
        fails.append(f"H3 too many hyphenated compounds ({len(comps)} > {maxh}): {', '.join(comps)}")
    elif comps:
        warns.append(f"H3 hyphenated compound present (allowed, but prefer none): {', '.join(comps)}")
    # H4/H8 banned phrases
    for p in load_phrases():
        if phrase_regex(p).search(full):
            fails.append(f"H8 banned phrase: '{p}'")
    for pat in SUPERIORITY:
        m = re.search(pat, full, re.I)
        if m:
            fails.append(f"H4 superiority claim: '{m.group(0)}'")
    # H9 formatting
    if EMOJI.search(full):
        fails.append("H9 emoji")
    if re.search(r"^\s*([-*•]|\d+[.)])\s+", body, re.M):
        fails.append("H9 bullet or numbered list")
    if "**" in full or "__" in full or re.search(r"^\s*#", body, re.M):
        fails.append("H9 markdown bold or header")
    if len(re.findall(r"https?://|www\.", body)) > 1:
        fails.append("H9 more than one link")
    # H10 quotes
    if re.search("[‘’“”]", full):
        fails.append("H10 curly quotes or apostrophes")
    # H11 length
    words = len(re.findall(r"\b[\w']+\b", body))
    chars = len(body)
    if maxc and chars > maxc:
        fails.append(f"H11 {chars} characters > {maxc}")
    if words > mx:
        fails.append(f"H11 {words} words > {mx} for {channel}")
    elif words < mn:
        warns.append(f"length {words} words < suggested {mn} for {channel}")
    if needs_subject:
        if not subject:
            fails.append("H11 missing 'Subject:' line")
        else:
            sw = len(subject.split())
            if not 2 <= sw <= 6:
                warns.append(f"subject is {sw} words (suggest 2 to 6)")
            if re.search(r"\b(quick question|opportunity|partnership|following up|checking in)\b", subject, re.I):
                fails.append(f"H8 weak subject: '{subject}'")
    # H12 ask heuristic
    q = body.count("?")
    if q == 0:
        warns.append("H12 no question mark; make sure there is exactly one clear ask")
    elif q > 1:
        warns.append(f"H12 {q} question marks; likely more than one ask")
    # nudge: the earlier note already asked for time, so offer a concrete time instead
    if channel == "nudge":
        m = re.search(r"\b(\d+|five|fifteen|ten) min(ute)?s?\b|\blearn more\b|\bshare the idea\b|\bpick your brain\b", body, re.I)
        if m:
            fails.append(f"S2 repeats the earlier ask or pitch: '{m.group(0)}' (offer a concrete time instead)")
        day = re.search(r"\b(mon|tues?|wed(nes)?|thu(rs)?|fri)(day)?\b|\btomorrow\b", body, re.I)
        clock = re.search(r"\b\d{1,2}(:\d{2})?\s?(am|pm)\b|\bnoon\b", body, re.I)
        if not (day and clock):
            fails.append("S2 no concrete time (needs a day and a clock time, e.g. 'Thursday at 10am PT')")
        elif not re.search(r"\b(PT|PST|PDT|ET|EST|EDT|CT|CST|CDT|MT|your time)\b", body):
            warns.append("S2 no time zone after the time (write it in their zone, e.g. PT or ET)")
    # soft checks
    if body.count("!") > 1:
        warns.append(f"{body.count('!')} exclamation points (max 1)")
    for w in SOFT_VOCAB:
        if re.search(rf"\b{w}\b", body, re.I):
            warns.append(f"soft vocab: '{w}'")
    for w in WEAK_ADVERBS:
        if re.search(rf"\b{w}\b", body, re.I):
            warns.append(f"weak adverb: '{w}'")
    if re.search(r"\bnot (just|only)\b.*\bbut\b", body, re.I | re.S):
        warns.append("B4 negative parallelism ('not just X but Y')")
    if re.search(r",\s+\w+ing\b[^.?!]*[.?!]", body) and re.search(r",\s+(showcasing|highlighting|reflecting|underscoring|demonstrating)\b", body, re.I):
        warns.append("B6 superficial -ing tail")
    sents = [s for s in re.split(r"(?<=[.?!])\s+", body) if s.strip()]
    if len(sents) >= 4:
        lens = [len(s.split()) for s in sents]
        if max(lens) - min(lens) <= 3:
            warns.append("B18 uniform sentence length")
    contractions = len(re.findall(r"\b\w+'(s|re|ve|ll|d|t|m)\b", body, re.I))
    if words >= 40 and contractions == 0:
        warns.append("no contractions (reads stiff in a business-casual register)")

    return {"channel": channel, "words": words, "chars": chars, "subject": subject,
            "fails": fails, "warns": warns, "pass": not fails}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True, choices=sorted(CHANNELS))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("path", nargs="?", default="-")
    a = ap.parse_args()
    text = sys.stdin.read() if a.path == "-" else Path(a.path).read_text(encoding="utf-8")
    r = lint(text, a.channel)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['channel']}  {r['words']} words, {r['chars']} chars")
        for f in r["fails"]:
            print("  FAIL", f)
        for w in r["warns"]:
            print("  warn", w)
    sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
