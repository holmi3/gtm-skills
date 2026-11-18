#!/usr/bin/env python3
"""fetch_pages.py: read a short list of public pages per domain and save their text, politely. Standard library only.

    python fetch_pages.py --domain acme.example --preset client --out pages            # the client's own site (stage 0)
    python fetch_pages.py --domains accounts.csv --preset account --out pages --limit 50  # target accounts (stage 3)
    python fetch_pages.py --import-text saved.txt --url https://acme.example/careers --out pages   # a page a browser tool read

Each page is saved as pages/<domain>/<slug>.txt: three header lines (URL, READ, SOURCE), a blank line, then the visible
text. pages/index.csv gets one row per attempt: domain, url, status, chars, read_on, source. extract and check steps
read only these files, so every quote can be traced back to a saved page.

Polite by default: it obeys robots.txt, waits --delay seconds (default 2) between requests to the same host, sends a
plain user agent that says what it is, reads at most --max-pages per domain, never logs in, never submits a form,
and skips a page already saved unless --refresh. Use it on public pages only.

When the script cannot reach the web (a locked-down sandbox, a site that blocks scripts, a page drawn by JavaScript),
read the page with a browser tool instead, save its text, and register it with --import-text so the rest of the flow
treats it the same way.
"""
import argparse, csv, datetime as dt, re, sys, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

UA = "tam-builder-page-reader/1.0 (reads a few public pages per company; obeys robots.txt)"
PRESETS = {
    # the client's own site: what they sell, to whom, proof, and how they look
    "client": ["/", "/pricing", "/customers", "/case-studies", "/product", "/platform", "/features", "/integrations",
               "/security", "/trust", "/about", "/company", "/careers", "/jobs"],
    # a target account: what it is, how big, how it works, and what it is hiring for
    "account": ["/", "/about", "/company", "/careers", "/jobs", "/customers", "/security", "/support"],
}
DISCOVER = re.compile(r"career|jobs|join-us|work-with-us|about|customers|case-stud|pricing|security|trust|integrations",
                      re.I)
SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "iframe", "head"}
BLOCK_TAGS = {"p", "div", "section", "article", "li", "ul", "ol", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td",
              "th", "header", "footer", "nav", "main", "aside", "blockquote", "figcaption", "dd", "dt", "table"}
INDEX_COLS = ["domain", "url", "status", "chars", "read_on", "source"]


class Text(HTMLParser):
    """Visible text plus the page's links. Not a browser: text drawn by JavaScript is not seen."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.links, self.skip, self.title = [], [], 0, ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag == "title":
            self._in_title = True
        if tag in BLOCK_TAGS:
            self.out.append("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag == "title":
            self._in_title = False
        if tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip:
            self.out.append(data)

    def text(self):
        raw = "".join(self.out)
        lines = [re.sub(r"[ \t\r\f\v ]+", " ", ln).strip() for ln in raw.split("\n")]
        out, last = [], None
        for ln in lines:
            if ln and ln != last:
                out.append(ln)
            last = ln
        return "\n".join(out)


def slug(url):
    p = urllib.parse.urlparse(url).path.strip("/")
    return re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-")[:80] or "home"


def root_domain(s):
    s = s.strip().lower()
    s = re.sub(r"^https?://", "", s).split("/")[0]
    return s[4:] if s.startswith("www.") else s


class Reader:
    def __init__(self, out, delay, timeout, refresh):
        self.out, self.delay, self.timeout, self.refresh = Path(out), delay, timeout, refresh
        self.robots, self.last = {}, {}
        self.today = dt.date.today().isoformat()
        self.index = self.out / "index.csv"
        self.out.mkdir(parents=True, exist_ok=True)
        if not self.index.exists():
            with open(self.index, "w", newline="", encoding="utf-8") as f:
                csv.writer(f, lineterminator="\n").writerow(INDEX_COLS)

    def log(self, domain, url, status, chars, source="script"):
        with open(self.index, "a", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerow([domain, url, status, chars, self.today, source])

    def allowed(self, url):
        base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    rp.parse(r.read().decode("utf-8", "replace").splitlines())
            except urllib.error.HTTPError as e:
                rp.parse([] if e.code in (404, 410) else ["User-agent: *", "Disallow: /"])  # no file: allowed; error: stay out
            except Exception:
                rp = None  # unreachable host; the page fetch reports it
            self.robots[base] = rp
        rp = self.robots[base]
        return rp is None or rp.can_fetch(UA, url)

    def wait(self, host):
        gap = time.time() - self.last.get(host, 0)
        if gap < self.delay:
            time.sleep(self.delay - gap)
        self.last[host] = time.time()

    def save(self, domain, url, text, title="", source="script"):
        d = self.out / domain
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{slug(url)}.txt"
        head = f"URL: {url}\nREAD: {self.today}\nSOURCE: {source}\n" + (f"TITLE: {title.strip()}\n" if title.strip() else "")
        path.write_text(head + "\n" + text + "\n", encoding="utf-8")
        self.log(domain, url, "ok", len(text), source)
        return path

    def fetch(self, domain, url):
        """Returns the parser on success, None otherwise. Every outcome goes in the index."""
        path = self.out / domain / f"{slug(url)}.txt"
        if path.exists() and not self.refresh:
            return "cached"
        if not self.allowed(url):
            self.log(domain, url, "robots_disallow", 0)
            return None
        host = urllib.parse.urlparse(url).netloc
        self.wait(host)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                final = r.geturl()
                if root_domain(final) != domain and not root_domain(final).endswith("." + domain):
                    self.log(domain, url, f"redirect_offsite:{root_domain(final)}", 0)
                    return None
                ctype = r.headers.get("Content-Type", "")
                if "html" not in ctype and "text" not in ctype:
                    self.log(domain, url, f"skipped_type:{ctype.split(';')[0]}", 0)
                    return None
                body = r.read(2_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
        except urllib.error.HTTPError as e:
            self.log(domain, url, f"http_{e.code}", 0)
            return None
        except Exception as e:  # DNS, TLS, timeout, proxy refusal
            self.log(domain, url, f"error:{type(e).__name__}", 0)
            return None
        p = Text()
        p.feed(body)
        text = p.text()
        if len(text) < 200:
            self.log(domain, url, "thin_page_try_browser", len(text))
            return None
        self.save(domain, final, text, p.title)
        return p


def run_domain(rd, domain, paths, max_pages, base=None):
    base = base or f"https://{domain}"
    queue = [base + p for p in paths]
    seen, n = set(), 0
    while queue and n < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        res = rd.fetch(domain, url)
        if res is None:
            continue
        n += 1
        if url == base + "/" and res != "cached":
            # Follow the homepage's own links to careers, about, customers and the like, on the same domain only.
            for href in res.links:
                full = urllib.parse.urljoin(base + "/", href).split("#")[0].split("?")[0]
                if root_domain(full) == domain and DISCOVER.search(urllib.parse.urlparse(full).path) and full not in seen:
                    queue.insert(0, full) if re.search(r"career|jobs", full, re.I) else queue.append(full)
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--domain", help="one domain")
    src.add_argument("--domains", help="a CSV with a domain column (or a text file, one per line)")
    src.add_argument("--import-text", help="a text file saved from a browser tool; needs --url")
    ap.add_argument("--url", help="with --import-text: the page the text came from")
    ap.add_argument("--out", default="pages")
    ap.add_argument("--preset", choices=PRESETS, default="account")
    ap.add_argument("--paths", help="comma separated paths instead of the preset, e.g. /,/careers")
    ap.add_argument("--max-pages", type=int, default=8, help="pages saved per domain (default 8)")
    ap.add_argument("--limit", type=int, help="first N domains only; run 10 first and look before a big run")
    ap.add_argument("--only-missing", help="with --domains: skip rows where this column already has a value")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests to one host (default 2, minimum 1)")
    ap.add_argument("--timeout", type=float, default=20)
    ap.add_argument("--refresh", action="store_true", help="read pages again even if saved")
    a = ap.parse_args()
    rd = Reader(a.out, max(a.delay, 1.0), a.timeout, a.refresh)

    if a.import_text:
        if not a.url:
            ap.error("--import-text needs --url")
        text = Path(a.import_text).read_text(encoding="utf-8")
        p = rd.save(root_domain(a.url), a.url, text.strip(), source="browser")
        print(f"saved {p}")
        return

    if a.domain:
        domains = [root_domain(a.domain)]
    else:
        f = Path(a.domains)
        if f.suffix.lower() == ".csv":
            rows = list(csv.DictReader(open(f, newline="", encoding="utf-8")))
            if a.only_missing:
                rows = [r for r in rows if not (r.get(a.only_missing) or "").strip()]
            domains = [root_domain(r["domain"]) for r in rows if r.get("domain")]
        else:
            domains = [root_domain(x) for x in f.read_text(encoding="utf-8").split() if x.strip()]
    domains = list(dict.fromkeys(domains))[: a.limit or None]
    paths = [p if p.startswith("/") else "/" + p for p in a.paths.split(",")] if a.paths else PRESETS[a.preset]

    # A domain given with http:// (a local test server) keeps its scheme; everything else is read over https.
    bases = {root_domain(a.domain): a.domain.rstrip("/")} if a.domain and a.domain.startswith("http://") else {}
    total = 0
    for i, d in enumerate(domains, 1):
        n = run_domain(rd, d, paths, a.max_pages, bases.get(d))
        total += n
        print(f"[{i}/{len(domains)}] {d}: {n} pages")
    print(f"done: {total} pages for {len(domains)} domains in {a.out}/ (index: {rd.index})")
    if total == 0:
        print("Nothing saved. If every row in the index says error:..., this machine cannot reach the web: read the pages "
              "with a browser tool and register each with --import-text.", file=sys.stderr)


if __name__ == "__main__":
    main()
