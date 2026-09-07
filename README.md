# Marginalia

The public front end for the biblical-studies work and the Encounter pathway.
Reverent and critically honest at the same time: sermons printed with the
exegetical apparatus they rest on, word studies, text histories, and a four-stage
pathway into following Jesus.

**Live:** https://claude.ai/code/artifact/daa729a5-1fbc-4b41-afe5-97ebfc3f6b19

One HTML file, no build step, no framework. Everything is in `marginalia.html`.

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

## How to publish

Edit `marginalia.html`, then publish it to the artifact URL above. Publishing to
that URL from a conversation that has not read it will be refused; pass the URL
as `url` and read it first.

**Viewers are pinned to a version.** Republishing does not change what someone
you already sent the link to sees until the share pin is moved from the page's
share menu.

## Regenerating Reflections from the vault

Reflections are generated from the sermon markdown rather than hand-written.

```
python3 build_reflections.py     # vault markdown -> reflections_articles.html + reflections_toc.html
python3 splice.py                # inserts both into marginalia.html
```

`build_reflections.py` parses movements from the `**N · Title**` markers, the
apparatus from `## Prep — exegesis`, and sources and reading time from `## Notes`.
Three maps at the top carry what the markdown does not: `STANDING` (the
confidence line in the header), `XREF` (the "Also on this passage" block) and
`REVISED` (the date). A rebuild currently reproduces the published articles
exactly; if you change the generator, check that it still does.

**`splice.py` appends.** It is right for adding a new sermon and wrong for
re-running an entry that is already on the page, which would duplicate it. Trim
`ORDER` to just the new sermons before running.

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

## Files

- `marginalia.html` — the site
- `build_reflections.py`, `splice.py` — the Reflections generator
- `audit_pass1.py` … `audit_pass4.py` — the 2026-09-07 audit, applied. Kept as
  the record of what changed and why; they are not re-runnable against the
  current file.

## Known gaps

- No contact address, no Instagram link, no newsletter. All three are named as
  gaps on the Colophon rather than pretended into existence. Slots are marked in
  the source with `CONTACT SLOT` and `CHANNEL SLOT`.
- Encounter has no date and no waitlist. The next-step block offers what a reader
  can do alone today; `WAITLIST SLOT` in `enc-offer` marks where capture goes.
- No link previews. The artifact host owns `<head>`, so `og:` tags are not
  possible. A real domain fixes this.
- The whole page is in the DOM at once, ~500 KB. Fine now; it is the ceiling.
