# Marginalia

The public front end for the biblical-studies work and the Encounter pathway.
Reverent and critically honest at the same time: sermons printed with the
exegetical apparatus they rest on, word studies, text histories, and a four-stage
pathway into following Jesus.

**Live:** https://claude.ai/code/artifact/daa729a5-1fbc-4b41-afe5-97ebfc3f6b19

One HTML file, no framework. Everything the site is lives in `marginalia.html`,
and it opens in a browser as-is. There is a build, but only for deployment:
`build_site.py` wraps that file in a real `<head>` and writes a crawlable page
per article. Nothing generated is committed.

## Sections

| Section | Holds | Vault source |
|---|---|---|
| **Reflections** | 15 sermons, each with its apparatus | `02 Biblical Studies IG/Sermons/` |
| **Encounter** | The four-stage pathway and the plain-language offer | `03 Encounter/Curriculum/` |
| **Roots** | 5 word studies | `02 Biblical Studies IG/Research/` |
| **Provenance** | 10 studies of where texts came from | `02 Biblical Studies IG/Research/` |
| **Wonder** | Children's approach and one sample. Scaffolding only | not yet built |
| **Colophon** | Who makes this, how, and an honest status page | written for the site |

Section names are brand names and stay in English in every language.

Wonder is deliberately **not** in the tab row. It is still a full section at
`#wonder`, linked from Colophon → "What is coming". Put the tab back when the
review of existing children's material is done.

## Checks and tests

Run everything with `npm test`. It is fast and CI runs the same four on every
push.

| | |
|---|---|
| `python3 check.py marginalia.html` | the conventions below, machine-checked |
| `python3 test_check.py` | breaks the page ten ways and asserts each is caught |
| `node test_dom.js` | drives the real page in a DOM: routing, tabs, search |
| `python3 test_site.py` | builds the site and checks links, heads and sitemap |

`hooks/pre-commit` runs `check.py` against the staged `marginalia.html`, so a
commit that breaks a convention fails. It is live through `core.hooksPath`; a
fresh clone needs `git config core.hooksPath hooks` once. `npm install` gets
jsdom, which only the DOM test needs.

## Publishing

**To the artifact host, today.** Edit `marginalia.html`, then publish it to the
artifact URL above. Publishing to that URL from a conversation that has not read
it will be refused; pass the URL as `url` and read it first.

**To a real domain, once there is one.**

```
MARGINALIA_URL=https://example.org python3 build_site.py   # -> dist/
python3 -m http.server -d dist 8000                        # look at it
```

`dist/` is a static site: `index.html` is the app as it is now, and every
article also gets its own page at `/section/id/` holding only that article, its
own title and description, canonical and Open Graph tags, and a drawn preview
image. Plus `sitemap.xml`, `robots.txt` and `_headers`. It deploys as-is to
Cloudflare Pages or Netlify. Without `MARGINALIA_URL` the build still runs but
says it is leaving canonical, `og:url` and the sitemap out rather than inventing
a host.

**Viewers are pinned to a version.** Republishing does not change what someone
you already sent the link to sees until the share pin is moved from the page's
share menu.

## Regenerating Reflections from the vault

Reflections are generated from the sermon markdown rather than hand-written.

```
python3 build_reflections.py     # vault markdown -> reflections_articles.html + reflections_toc.html
python3 splice.py                # merges both into marginalia.html
```

`build_reflections.py` parses movements from the `**N · Title**` markers, the
apparatus from `## Prep — exegesis`, and sources and reading time from `## Notes`.
Maps at the top carry what the markdown does not: `STANDING` (the confidence
line in the header), `XREF` (the "Also on this passage" block), `REVISED` (the
date) and `TRANSLATED` (which entries already have Spanish and Portuguese, and
so should not get the "not translated yet" notice).

**`splice.py` is idempotent.** An entry already on the page is replaced in
place; a new one is inserted at its `ORDER` position. Do not trim `ORDER`: run
the whole thing. A full rebuild reproduces the published page byte for byte,
which makes this a regression test worth running after any change to the
generator:

```
python3 build_reflections.py && python3 splice.py && git diff --exit-code
```

**`ORDER` starts at the fourth sermon on purpose.** `meek`, `dust` and `psalm88`
are the only Reflections translated into Spanish and Portuguese, and the sermon
markdown in the vault is English only, so generating them would delete two
translations. Adding them to `ORDER` looks like closing a gap and is not.
`splice.py` refuses rather than relying on anyone reading this paragraph.

## Conventions

**Confidence labels.** Five, and only five, defined once in Roots → "How Roots
works" and repeated in Colophon → "How the work is done":

> Consensus · Strong majority · Debated · Our read · Rejected

with Spanish (Consenso · Mayoría amplia · En debate · Nuestra lectura ·
Rechazado) and Portuguese (Consenso · Maioria ampla · Em debate · Nossa leitura ·
Rejeitado). The header `Standing` line uses the same words lowercased in
brackets. Do not invent a sixth.

**Never invent a citation.** Anything that cannot be verified against publisher,
library or journal records gets dropped rather than softened. Where a figure is
widely repeated but unchecked, say so on the page instead of printing it: see
Roots → *Hell* on the KJV count for *Sheol*.

**Voice.** No em dashes anywhere. Contractions. Plain language, church words
translated. There are currently zero em dashes in the file and it should stay
that way.

**Languages.** English, Spanish, Portuguese, switched by a `data-elang`
attribute on the root element with `.l-en` / `.l-es` / `.l-pt` blocks. Coverage
is partial on purpose and degrades honestly: an entry with no `.l-es` block
keeps its English body and shows a translated `.xlate` notice saying it is not
translated yet. **Never wrap an article's only copy in `.l-en`** without adding
the other two, or the entry goes blank when someone switches language.

Portuguese has not been reviewed by a native speaker.

`translations.json` records which article carries which languages, and
`check.py` fails if one loses a language. That is the only way a deleted
translation gets noticed, because an article stripped back to English plus an
"not translated yet" notice satisfies every other rule. When a translation
legitimately changes, rerun `python3 check.py marginalia.html
--update-translations` and commit the result. 17 of 46 articles are translated
today.

**Only Reflections is generated, and only 12 of its 15 entries.** The other 31
articles are written directly in `marginalia.html` and their prose exists
nowhere else, not in the vault. The Research notes in the vault are exegesis
worksheets, not the published copy: `praus-meek.md` is the raw work behind
Roots → *Meek*, not a draft of it. So the HTML is the source of truth for those
entries, which is fine, and is why the checks matter more than they otherwise
would.

## Files

- `marginalia.html` — the site
- `check.py` — the conventions, machine-checked. `--update-translations`
  rewrites `translations.json`
- `test_check.py`, `test_dom.js`, `test_site.py` — the tests
- `translations.json` — which article carries which languages
- `build_reflections.py`, `splice.py` — the Reflections generator
- `build_site.py` — `marginalia.html` -> deployable `dist/`
- `hooks/pre-commit` — runs `check.py` on the staged file
- `audit_pass1.py` … `audit_pass4.py` — the 2026-09-07 audit, applied. Kept as
  the record of what changed and why; they are not re-runnable against the
  current file. Their findings now live as rules in `check.py`.

## Known gaps

- No contact address, no Instagram link, no newsletter. All three are named as
  gaps on the Colophon rather than pretended into existence. Slots are marked in
  the source with `CONTACT SLOT` and `CHANNEL SLOT`.
- Encounter has no date and no waitlist. The next-step block offers what a reader
  can do alone today; `WAITLIST SLOT` in `enc-offer` marks where capture goes.
- **No domain.** This is now the one thing blocking the most: link previews, a
  contact address that is not a personal Gmail, per-article URLs anyone can
  link to, and control over what is live. `build_site.py` is written and tested
  and produces the whole site; it needs a hostname and somewhere to put it.
- The whole page is in the DOM at once, ~500 KB. Fine now; it is the ceiling.
  The static build already splits it per article, so the fix exists when the
  app itself needs it.
