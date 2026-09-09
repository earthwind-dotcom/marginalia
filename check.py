#!/usr/bin/env python3
"""Check marginalia.html against the conventions in README.md.

Every rule here is one the 2026-09-07 audit had to find by hand. Exit 1 on any
violation so a pre-commit hook can stop the commit.

    python3 check.py [file]
"""
import sys
import re
from html.parser import HTMLParser
from pathlib import Path

PATH = Path(sys.argv[1] if len(sys.argv) > 1 else "marginalia.html")

CONF_LABELS = {
    "en": {"Consensus", "Strong majority", "Debated", "Our read", "Rejected"},
    "es": {"Consenso", "Mayoría amplia", "En debate", "Nuestra lectura", "Rechazado"},
    "pt": {"Consenso", "Maioria ampla", "Em debate", "Nossa leitura", "Rejeitado"},
}
ALL_CONF = set().union(*CONF_LABELS.values())
BRACKET_LABELS = {s.lower() for s in ALL_CONF}

SECTIONS = ["reflections", "encounter", "roots", "provenance", "wonder", "colophon"]

failures = []


def fail(rule, detail):
    failures.append((rule, detail))


class Doc(HTMLParser):
    """Collect ids, articles with their direct-child language panes, toc items,
    cross-reference links and confidence labels. Markup only: everything inside
    <script> and <style> is ignored, so JS template strings never register."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.articles = {}        # id -> {"langs": set, "view": str, "xlate": bool}
        self.toc = []             # (view, target)
        self.xrefs = []           # (section, article)
        self.views = set()
        self.conf_texts = []
        self.stack = []           # open tags as (tag, attrs)
        self.article = None       # (id, depth)
        self.view = None          # (name, depth)
        self.capture = None       # collecting text for a conf span
        self.in_skip = 0

    # -- helpers -------------------------------------------------------
    def cls(self, attrs):
        return (dict(attrs).get("class") or "").split()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.in_skip += 1
            return
        if self.in_skip:
            return
        depth = len(self.stack)
        self.stack.append(tag)

        if "id" in a:
            self.ids.append(a["id"])
        classes = self.cls(attrs)

        if tag == "div" and a.get("id", "").startswith("view-"):
            name = a["id"][len("view-"):]
            self.views.add(name)
            self.view = (name, depth)

        if tag == "article":
            aid = a.get("id")
            if not aid:
                fail("article-id", f"an <article> in view {self.view and self.view[0]} has no id")
                aid = f"__anon{len(self.articles)}"
            self.articles[aid] = {
                "langs": set(),
                "view": self.view[0] if self.view else None,
                "xlate": False,
            }
            self.article = (aid, depth)

        # direct-child language pane of an article
        if self.article and depth == self.article[1] + 1:
            for c in classes:
                if c in ("l-en", "l-es", "l-pt"):
                    self.articles[self.article[0]]["langs"].add(c[2:])

        if self.article and "xlate" in classes:
            self.articles[self.article[0]]["xlate"] = True

        if "toc-item" in classes and "data-target" in a:
            self.toc.append((self.view[0] if self.view else None, a["data-target"]))

        if "data-xsec" in a:
            self.xrefs.append((a["data-xsec"], a.get("data-xart")))

        if any(c == "conf" or c.startswith("conf-") for c in classes):
            self.capture = ""

        if tag in ("br", "img", "input", "meta", "link", "hr"):
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_skip = max(0, self.in_skip - 1)
            return
        if self.in_skip:
            return
        if self.capture is not None:
            text = self.capture.strip()
            if text:
                self.conf_texts.append(text)
            self.capture = None
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        depth = len(self.stack)
        if self.article and depth <= self.article[1]:
            self.article = None
        if self.view and depth <= self.view[1]:
            self.view = None

    def handle_data(self, data):
        if self.in_skip:
            return
        if self.capture is not None:
            self.capture += data


raw = PATH.read_text(encoding="utf-8")
doc = Doc()
doc.feed(raw)

markup = raw.split("<script>")[0]

# 1 -- no em dashes anywhere -------------------------------------------------
n = raw.count("—") + len(re.findall(r"&mdash;", raw))
if n:
    fail("em-dash", f"{n} em dash(es) in the file; the voice convention is zero")

# 2 -- ids are unique --------------------------------------------------------
seen, dupes = set(), set()
for i in doc.ids:
    if i in seen:
        dupes.add(i)
    seen.add(i)
for d in sorted(dupes):
    fail("duplicate-id", f'id="{d}" appears more than once')

# 3 -- every cross reference resolves ---------------------------------------
for section, art in doc.xrefs:
    if section not in SECTIONS:
        fail("xref-section", f'data-xsec="{section}" is not a section')
    elif section not in doc.views:
        fail("xref-section", f'data-xsec="{section}" has no #view-{section}')
    if art and art not in seen:
        fail("xref-target", f'data-xart="{art}" points at nothing')

# 4 -- every contents entry resolves, and lands in its own view --------------
for view, target in doc.toc:
    if target not in doc.articles:
        fail("toc-target", f'data-target="{target}" is not an article id')
    elif doc.articles[target]["view"] != view:
        fail("toc-view", f'"{target}" is listed under {view} but lives in {doc.articles[target]["view"]}')

# 5 -- every article is reachable from a contents list -----------------------
listed = {t for _, t in doc.toc}
for aid, meta in doc.articles.items():
    if aid not in listed:
        fail("orphan-article", f'"{aid}" ({meta["view"]}) is in no contents list, so nothing links to it')

# 6 -- confidence labels are the five, and only the five ---------------------
for text in doc.conf_texts:
    if text not in ALL_CONF:
        fail("confidence-label", f'"{text}" is not one of the five confidence labels')
for label in re.findall(r"\[([^\[\]<>\n]{3,30})\]", markup):
    low = label.strip().lower()
    if low in BRACKET_LABELS or low in {"name", "section", "hidden"}:
        continue
    if any(low.startswith(w) for w in ("consens", "strong", "debat", "our read", "reject",
                                       "mayor", "nuestra", "rechaz", "maioria", "nossa", "rejeit")):
        fail("confidence-label", f'bracketed "[{label}]" is close to a confidence label but not one of the five')

# 7 -- an article's only copy is never wrapped in .l-en ----------------------
for aid, meta in sorted(doc.articles.items()):
    langs = meta["langs"]
    if langs and "en" in langs and not (langs & {"es", "pt"}):
        fail("lang-blank", f'"{aid}" wraps its only copy in .l-en, so it goes blank on a language switch')

# 8 -- partial translation is announced, not silent -------------------------
# An article with no .l-es / .l-pt pane is English-only, whether or not its
# English copy is wrapped in .l-en. Either way the reader who switched language
# is owed the notice. build_reflections.py regressed exactly this in 12 entries.
for aid, meta in sorted(doc.articles.items()):
    missing = {"es", "pt"} - meta["langs"]
    if missing and not meta["xlate"]:
        fail("xlate-notice",
             f'"{aid}" has no .l-{"/.l-".join(sorted(missing))} pane and no .xlate '
             f'notice, so a reader who switches language gets English with no explanation')

# 9 -- the six sections all exist -------------------------------------------
for s in SECTIONS:
    if s not in doc.views:
        fail("missing-view", f"#view-{s} is gone")

# -- report -----------------------------------------------------------------
if failures:
    width = max(len(r) for r, _ in failures)
    for rule, detail in failures:
        print(f"{rule.ljust(width)}  {detail}")
    print(f"\n{len(failures)} problem(s) in {PATH}")
    sys.exit(1)

print(f"{PATH}: {len(doc.articles)} articles, "
      f"{len(doc.views & set(SECTIONS))} sections, all checks pass")
