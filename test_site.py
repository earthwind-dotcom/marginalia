#!/usr/bin/env python3
"""Tests for build_site.py.

Builds the site into a temporary directory and checks the output the way a
crawler and a link unfurler would read it: every internal link resolves, each
article page carries exactly one visible article, every page has the head tags
a preview needs, titles are distinct, and the markup balances.

    python3 test_site.py
"""
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).parent
SITE = "https://marginalia.test"
BASE = "/marginalia"   # exercise the project-site path too

VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.bad = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.bad.append(f"stray </{tag}>")
        elif self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
            self.bad.append(f"crossed </{tag}>")
        else:
            self.bad.append(f"stray </{tag}>")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, MARGINALIA_URL=SITE, MARGINALIA_BASE=BASE)
        r = subprocess.run([sys.executable, str(HERE / "build_site.py")],
                           cwd=HERE, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL  build_site.py exited nonzero:\n" + r.stdout + r.stderr)
            return 1
        out = HERE / "dist"

        problems = []
        pages = sorted(out.rglob("index.html"))
        app = out / "index.html"

        def exists(href):
            if BASE:
                if not href.startswith(BASE):
                    return False          # a link that forgot the base path
                href = href[len(BASE):] or "/"
            if href == "/":
                return app.exists()
            p = out / href.strip("/")
            return (p / "index.html").exists() or p.exists()

        links = 0
        for f in pages:
            rel = f.relative_to(out)
            s = f.read_text(encoding="utf-8")

            for href in re.findall(r'href="(/[^"#?]*)"', s):
                links += 1
                if not exists(href):
                    problems.append(f"{rel}: dead link {href}")

            # the app keeps hash routing on purpose; the static pages must not
            if f != app:
                for href in sorted(set(re.findall(r'href="(#[a-z]+/[^"]*)"', s))):
                    problems.append(f"{rel}: unrewritten hash link {href}")

            head = s[:s.index("</head>")]
            for need in ("<title>", 'name="description"', 'property="og:title"',
                         'property="og:image"', 'property="og:url"',
                         'rel="canonical"', 'name="viewport"', 'rel="icon"'):
                if need not in head:
                    problems.append(f"{rel}: head missing {need}")
            if SITE not in head:
                problems.append(f"{rel}: head has no absolute URL, so previews break")

            b = Balance()
            b.feed(s)
            if b.bad or b.stack:
                problems.append(f"{rel}: unbalanced markup {b.bad[:2]} open={b.stack[:3]}")

            if len(rel.parts) == 3:  # section/id/index.html
                arts = re.findall(r'<article\b[^>]*id="([^"]+)"([^>]*)>', s)
                if len(arts) != 1:
                    problems.append(f"{rel}: {len(arts)} articles, expected exactly 1")
                elif arts[0][0] != rel.parts[1]:
                    problems.append(f"{rel}: holds {arts[0][0]}")
                elif "hidden" in arts[0][1]:
                    problems.append(f"{rel}: the article is still hidden")
                if 'class="toc-item"' not in s:
                    problems.append(f"{rel}: no contents list, so it is a dead end")

        titles = {}
        for f in pages:
            t = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8")).group(1)
            titles.setdefault(t, []).append(str(f.relative_to(out)))
        for t, where in titles.items():
            if len(where) > 1:
                problems.append(f"duplicate <title> {t!r} on {where[:3]}")

        sitemap = out / "sitemap.xml"
        if not sitemap.exists():
            problems.append("no sitemap.xml")
        else:
            locs = set(re.findall(r"<loc>(.*?)</loc>", sitemap.read_text(encoding="utf-8")))
            if len(locs) != len(pages):
                problems.append(f"sitemap lists {len(locs)} urls for {len(pages)} pages")
            for loc in sorted(locs):
                if not exists(loc[len(SITE):]):
                    problems.append(f"sitemap lists a page that was not built: {loc}")

        for extra in ("robots.txt", "_headers"):
            if not (out / extra).exists():
                problems.append(f"no {extra}")

        imgs = list((out / "og").rglob("*.png")) if (out / "og").exists() else []
        if len(imgs) < len(pages) - 10:
            problems.append(f"only {len(imgs)} preview images for {len(pages)} pages")

        print(f"{len(pages)} pages, {links} internal links, {len(imgs)} preview images")
        if problems:
            for p in problems[:30]:
                print("  FAIL  " + p)
            print(f"\n{len(problems)} problems")
            return 1
        print("all checks pass")
        return 0


if __name__ == "__main__":
    sys.exit(main())
