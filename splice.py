#!/usr/bin/env python3
"""Merge generated Reflections into marginalia.html.

Idempotent. An entry whose id is already on the page is REPLACED in place; an
entry that is new is inserted at its ORDER position, not blindly at the end. So
running it twice is the same as running it once, and

    python3 build_reflections.py && python3 splice.py && git diff --exit-code

is a regression test for "the generator still reproduces the published page".

The old version appended unconditionally and relied on you remembering to trim
ORDER first, which duplicated any entry already on the page.
"""
import re
import sys
from pathlib import Path

PAGE = Path("marginalia.html")
ARTS = Path("reflections_articles.html")
TOCS = Path("reflections_toc.html")

REGION_START = "<!-- ==================== REFLECTIONS ==================== -->"
REGION_END = "<!-- ==================== ENCOUNTER"

ART_OPEN = r'<article\b[^>]*\bid="([^"]+)"[^>]*>'
TOC_OPEN = r'<a\b[^>]*\bclass="toc-item"[^>]*\bdata-target="([^"]+)"[^>]*>'


def split_elements(html, open_re, close_tag):
    """[(id, element_html)] for non-nesting elements.

    The capture starts at the beginning of the element's line so that its
    indentation travels with it; otherwise an inserted element lands flush
    against the left margin.
    """
    out = []
    for m in re.finditer(open_re, html):
        start = m.start()
        line = html.rfind("\n", 0, start) + 1
        if html[line:start].strip() == "":
            start = line
        end = html.find(close_tag, m.end())
        if end < 0:
            sys.exit(f"unclosed {close_tag} for {m.group(1)}")
        out.append((m.group(1), html[start:end + len(close_tag)]))
    return out


def translated(fragment):
    """True if this element carries Spanish or Portuguese of its own."""
    return ('class="l-es"' in fragment) or ('class="l-pt"' in fragment)


def merge(region, generated, open_re, close_tag, anchor, sep, label):
    existing = dict(split_elements(region, open_re, close_tag))

    # The sermon markdown in the vault is English only, so anything generated
    # from it is English only. Three Reflections (meek, dust, psalm88) were
    # written before the generator existed and are the only ones translated
    # into Spanish and Portuguese, which is exactly why ORDER starts at the
    # fourth. Adding one of them to ORDER would look like tidying up and would
    # silently delete two translations, so refuse instead of trusting a comment.
    losses = [k for k, new_html in generated
              if k in existing and translated(existing[k]) and not translated(new_html)]
    if losses and "--allow-translation-loss" not in sys.argv:
        sys.exit(
            "refusing to overwrite translated %s: %s\n"
            "These are translated on the page and the generator produces English only,\n"
            "so this would delete the Spanish and Portuguese. Remove them from ORDER in\n"
            "build_reflections.py, or pass --allow-translation-loss if you truly mean it."
            % (label, ", ".join(losses)))

    keys = [k for k, _ in generated]
    replaced, added = [], []
    prev = None  # element html of the previous generated entry, as now placed

    for pos, (key, new_html) in enumerate(generated):
        if key in existing:
            if existing[key] != new_html:
                region = region.replace(existing[key], new_html, 1)
                replaced.append(key)
            existing[key] = new_html
        else:
            if prev is not None:
                i = region.index(prev) + len(prev)
                region = region[:i] + sep + new_html + region[i:]
            else:
                # nothing generated precedes it: sit before the next generated
                # entry that is already on the page, else at the end of the list
                nxt = next((existing[k] for k in keys[pos + 1:] if k in existing), None)
                i = region.index(nxt) if nxt else region.rindex(anchor)
                region = region[:i] + new_html + sep + region[i:]
            existing[key] = new_html
            added.append(key)
        prev = existing[key]

    print(f"{label}: {len(added)} added, {len(replaced)} updated, "
          f"{len(generated) - len(added) - len(replaced)} unchanged")
    for name, ks in (("added", added), ("updated", replaced)):
        if ks:
            print(f"  {name}: {', '.join(ks)}")
    return region


def main():
    for f in (PAGE, ARTS, TOCS):
        if not f.exists():
            sys.exit(f"missing {f}; run build_reflections.py first")

    page = PAGE.read_text(encoding="utf-8")
    start, end = page.index(REGION_START), page.index(REGION_END)
    head, region, tail = page[:start], page[start:end], page[end:]

    gen_arts = split_elements(ARTS.read_text(encoding="utf-8"), ART_OPEN, "</article>")
    gen_tocs = split_elements(TOCS.read_text(encoding="utf-8"), TOC_OPEN, "</a>")
    if not gen_arts:
        sys.exit("no articles in reflections_articles.html")
    if {k for k, _ in gen_arts} != {k for k, _ in gen_tocs}:
        sys.exit("the generated articles and contents entries do not cover the same ids")

    region = merge(region, gen_tocs, TOC_OPEN, "</a>",
                   "      </div>\n    </nav>", "\n", "contents")
    region = merge(region, gen_arts, ART_OPEN, "</article>",
                   "    </main>", "\n\n", "articles")

    new = head + region + tail
    if new == page:
        print("marginalia.html already matches the generated Reflections")
        return
    PAGE.write_text(new, encoding="utf-8")
    print("spliced")


if __name__ == "__main__":
    main()
