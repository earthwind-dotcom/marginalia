#!/usr/bin/env python3
"""Tests for check.py.

A checker that has only ever printed "pass" is worthless. Each case below
breaks marginalia.html in one specific way and asserts that check.py exits 1
and names the rule. Run with `python3 test_check.py`; CI runs it on every push.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
PAGE = HERE / "marginalia.html"
CHECK = HERE / "check.py"


def run(html):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    try:
        r = subprocess.run([sys.executable, str(CHECK), tmp],
                           capture_output=True, text=True)
        return r.returncode, r.stdout
    finally:
        Path(tmp).unlink()


def drop_translated_panes(s):
    """Turn a fully translated article into an English-only one."""
    m = re.search(r'<article[^>]*id="roots-praus".*?</article>', s, re.S)
    art = m.group(0)
    i = art.find('<div class="l-es">')
    return s.replace(art, art[:i] + "</article>", 1)


def strip_xlate(s):
    """Remove one .xlate notice from an article that needs it."""
    return re.sub(r'\s*<p class="xlate">.*?</p>', "", s, count=1, flags=re.S)


CASES = [
    ("em-dash", "an em dash anywhere",
     lambda s: s.replace("<h1>Meek</h1>", "<h1>Meek, a study</h1>".replace(",", " —"), 1)),
    ("duplicate-id", "two articles sharing an id",
     lambda s: s.replace('<article id="roots-praus"', '<article id="roots-sheol"', 1)),
    ("xref-target", "a cross reference pointing at nothing",
     lambda s: s.replace('data-xart="meek"', 'data-xart="does-not-exist"', 1)),
    ("toc-target", "a contents entry pointing at nothing",
     lambda s: s.replace('data-target="meek"', 'data-target="ghost"', 1)),
    ("orphan-article", "an article no contents list links to",
     lambda s: s.replace('href="#reflections/meek" data-target="meek"',
                         'href="#reflections/dust" data-target="dust"', 1)),
    ("confidence-label", "a sixth confidence label",
     lambda s: re.sub(r'(class="conf[^"]*"[^>]*>)Consensus', r"\1Near certain", s, count=1)),
    ("lang-blank", "an article whose only copy is wrapped in .l-en",
     drop_translated_panes),
    ("xlate-notice", "an untranslated article with no notice saying so",
     strip_xlate),
    ("missing-view", "a section that has gone missing",
     lambda s: s.replace('id="view-wonder"', 'id="view-gone"', 1)),
    ("translation-lost", "a translated article quietly reduced to English",
     drop_translated_panes),
]


def main():
    base = PAGE.read_text(encoding="utf-8")

    code, out = run(base)
    if code != 0:
        print("FAIL  marginalia.html does not pass its own checks:")
        print(out)
        return 1
    print(f"ok    marginalia.html passes ({len(CASES)} negative cases to go)")

    failures = 0
    for rule, description, mutate in CASES:
        broken = mutate(base)
        if broken == base:
            print(f"FAIL  {rule}: the mutation did not apply, so nothing was tested")
            failures += 1
            continue
        code, out = run(broken)
        if code == 1 and rule in out:
            print(f"ok    {rule}: caught {description}")
        else:
            print(f"FAIL  {rule}: did not catch {description} (exit {code})")
            print("      " + (out.strip().replace("\n", "\n      ") or "<no output>"))
            failures += 1

    print(f"\n{len(CASES) - failures}/{len(CASES)} rules verified")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
