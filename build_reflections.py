#!/usr/bin/env python3
"""Convert sermon markdown from the vault into Marginalia <article> blocks."""
import os
import re, sys, html
from pathlib import Path

# The vault is not in this repo. Override with MARGINALIA_SERMONS if it moves.
SRC = Path(os.environ.get(
    "MARGINALIA_SERMONS",
    Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents"
                  "/Personal Vault/02 Biblical Studies IG/Sermons"))

# (filename stem, article id, display passage for .apphead / toc)
ORDER = [
    ("Sermon — Whose World Is This (Genesis 1)",                              "whose-world",  "Genesis 1"),
    ("Sermon — God Speaks Into Your Frame (Genesis 1.6–8)",                   "frame",        "Genesis 1:6–8"),
    ("Sermon — The Verse They Bent (Genesis 9.20–27)",                        "verse-bent",   "Genesis 9:20–27"),
    ("Sermon — A Moabite in the Family Tree (Ruth 4.13–22)",                  "moabite",      "Ruth 4:13–22"),
    ("Sermon — Two Drafts of the Same Story (2 Samuel 24 and 1 Chronicles 21)","two-drafts",   "2 Samuel 24 · 1 Chronicles 21"),
    ("Sermon — When the Rule Breaks (Job 21)",                                "rule-breaks",  "Job 21"),
    ("Sermon — The Third Way (Matthew 5.38–42)",                              "third-way",    "Matthew 5:38–42"),
    ("Sermon — The Life of the Age (Matthew 25.31–46)",                       "life-age",     "Matthew 25:31–46"),
    ("Sermon — Luke Checked (Luke 1.1–4)",                                    "luke-checked", "Luke 1:1–4"),
    ("Sermon — The Story the Church Couldn't Lose (John 7.53–8.11)",          "couldnt-lose", "John 7:53–8:11"),
    ("Sermon — The Dead Rise First (1 Thessalonians 4.13–18)",                "dead-rise",    "1 Thessalonians 4:13–18"),
    ("Sermon — When the Church Changed Shape (1 Timothy 3.1–13)",             "church-shape", "1 Timothy 3:1–13"),
]
START_NUM = 4  # existing site already has Reflection 01–03

# Where each claim sits, shown in the .apphead. Labels must be one of the five
# defined in Roots -> "How Roots works": consensus, strong majority, debated,
# our read, rejected.
STANDING = {
    'whose-world': 'Genesis 1 read against ANE cosmology [consensus] &middot; a direct rebuttal of <i>Enuma Elish</i> [debated] &middot; <i>tehom</i> borrowed from Tiamat [rejected]',
    'frame': '<i>raqia&#703;</i> understood as a solid dome [consensus] &middot; the ANE three-tier cosmos [consensus] &middot; Genesis describes rather than defends it [our read]',
    'verse-bent': 'the curse falls on Canaan, not Ham [consensus] &middot; the racial reading is a later construction [consensus] &middot; the nature of Ham&rsquo;s offence [debated]',
    'moabite': 'Ezra&ndash;Nehemiah dissolved foreign marriages [consensus] &middot; Ruth and Jonah as canonical counter-voices [strong majority] &middot; written to answer Ezra [debated]',
    'two-drafts': 'Chronicles rewrites Samuel&ndash;Kings with a consistent tendency [consensus] &middot; <i>&#347;&#257;&#7789;&#257;n</i> as a proper name in 1 Chr 21:1 [debated]',
    'rule-breaks': 'Job 21 denies strict retribution [consensus] &middot; Proverbs&rsquo; sayings were never guarantees [consensus] &middot; the wisdom books as a preserved debate [strong majority]',
    'third-way': 'the passage rejects retaliation in kind [consensus] &middot; the three examples are active, not passive [strong majority] &middot; Wink&rsquo;s specific reconstructions [debated]',
    'life-age': '<i>ai&#333;nios</i> often means &ldquo;of the Age to Come&rdquo; [consensus] &middot; it also carries &ldquo;unending&rdquo; [consensus] &middot; the duration of final punishment [debated]',
    'luke-checked': 'the Gospels are textually anonymous [consensus] &middot; the traditional names are the only ones attested [consensus] &middot; whether the names were attached late [debated]',
    'couldnt-lose': 'not part of John&rsquo;s original text [consensus] &middot; preserves genuine early Jesus tradition [strong majority] &middot; still Scripture, as most traditions hold [our read]',
    'dead-rise': '<i>apant&#275;sis</i> pictures a welcoming party, not an evacuation [strong majority] &middot; one public parousia [strong majority] &middot; the pretrib system is 19th-century [consensus]',
    'church-shape': 'the Pastorals describe a more structured church than the undisputed seven [consensus] &middot; non-Pauline authorship [strong majority] &middot; Pauline authorship via a secretary [debated]',
}

# The word study or text history that shares this passage, as (section, id).
# Rendered as the "Also on this passage" block. Keep in step with the same map
# in audit_pass3.py.
XREF = {
    'whose-world': [('provenance', 'prov-genesis', 'Genesis 1 and its neighbours')],
    'frame': [('roots', 'roots-raqia', 'Firmament'), ('provenance', 'prov-genesis', 'Genesis 1 and its neighbours')],
    'verse-bent': [('provenance', 'prov-ham', 'The verse they bent')],
    'moabite': [('provenance', 'prov-ruth', 'The canon arguing with itself')],
    'two-drafts': [('provenance', 'prov-chronicles', 'Two drafts of one story')],
    'rule-breaks': [('provenance', 'prov-wisdom', 'When the rule breaks')],
    'third-way': [('provenance', 'prov-cheek', 'Turn the other cheek')],
    'life-age': [('roots', 'roots-aionios', 'Eternal')],
    'luke-checked': [('provenance', 'prov-gospels', 'Who wrote the Gospels?')],
    'couldnt-lose': [('provenance', 'prov-adultery', 'The story that floats')],
    'dead-rise': [('provenance', 'prov-rapture', 'Where the rapture came from'), ('roots', 'roots-sheol', 'Hell')],
    'church-shape': [('provenance', 'prov-paul', 'Which letters are Paul&rsquo;s?')],
}

# Every entry carries a revision date.
# Entries with a real .l-es / .l-pt translation. Anything not listed here is
# English-only and gets the .xlate notice, so a reader who switches language is
# told why the text stayed in English instead of just seeing English.
TRANSLATED = set()

XLATE = ('        <p class="xlate">'
         '<span class="l-es">Esta pieza a&uacute;n no est&aacute; traducida. '
         'El texto que sigue est&aacute; en ingl&eacute;s.</span>'
         '<span class="l-pt">Esta pe&ccedil;a ainda n&atilde;o foi traduzida. '
         'O texto a seguir est&aacute; em ingl&ecirc;s.</span></p>')

REVISED = ("Revised 6 September 2026",
           "Revisado el 6 de septiembre de 2026",
           "Revisado em 6 de setembro de 2026")

# sermons whose Notes carry no parsable sources bullet; taken from their research note
SOURCES_OVERRIDE = {
    "whose-world": ("*Enuma Elish* (Lambert, *Babylonian Creation Myths*; Heidel, "
                    "*The Babylonian Genesis*); Sarna, *JPS Genesis*; Westermann, "
                    "*Genesis 1–11*; Walton, *Genesis 1 as Ancient Cosmology*"),
}


def esc(t):
    return html.escape(t, quote=False)


def smart(t):
    """Straight quotes -> typographic entities. Apostrophes dominate, so ' is always rsquo."""
    out, open_q = [], True
    for ch in t:
        if ch == '"':
            out.append("&ldquo;" if open_q else "&rdquo;")
            open_q = not open_q
        elif ch == "'":
            out.append("&rsquo;")
        else:
            out.append(ch)
    return "".join(out)


def inline(t):
    """Markdown inline -> HTML. Escape first, then apply emphasis, then smart quotes."""
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t, flags=re.S)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t, flags=re.S)
    t = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", t)   # strip wikilinks
    # drop "See some-vault-slug." pointers left behind by wikilink stripping
    t = re.sub(r"\s*\bSee [a-z0-9]+(?:-[a-z0-9]+)+\.", "", t)
    t = re.sub(r"\s*\bVia [a-z0-9]+(?:-[a-z0-9]+)+\.", "", t)
    return smart(t)


def unwrap(block):
    """Join hard-wrapped lines into one logical paragraph."""
    return " ".join(l.strip() for l in block.strip().splitlines() if l.strip())


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm, body = {}, text[m.end():] if m else text
    if m:
        for key in ("passage", "big-idea", "fcf"):
            km = re.search(rf"^{key}:\s*(.+)$", m.group(1), re.M)
            if km:
                fm[key] = km.group(1).strip().strip('"')
    return fm, body


def section(body, name, nxt):
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## {re.escape(nxt)})", body, re.S | re.M)
    return m.group(1) if m else ""


def build(stem, art_id, passage, num):
    text = (SRC / f"{stem}.md").read_text(encoding="utf-8")
    fm, body = frontmatter(text)
    title = re.search(r"^# (.+)$", body, re.M).group(1).strip()

    prep = section(body, "Prep — exegesis", "Outline")
    manu = section(body, "Manuscript", "Notes")
    notes_m = re.search(r"^## Notes\s*\n(.*)$", body, re.S | re.M)
    notes = notes_m.group(1) if notes_m else ""

    # --- apparatus: "N. **Label.** text" possibly wrapped over lines
    items = []
    for m in re.finditer(r"^\d+\.\s+\*\*(.+?)\.?\*\*\s*(.*?)(?=^\d+\.\s+\*\*|^\*\*|\Z)",
                         prep, re.S | re.M):
        items.append((m.group(1).strip().rstrip("."), unwrap(m.group(2))))

    # --- sources + reading time from Notes
    # the sources bullet appears under several labels across the corpus
    src = ""
    sm = re.search(
        r"^-\s+(?:\*\*)?(?:Commentar\w*|Framing|Word data)[^:\n]*:(?:\*\*)?\s*"
        r"(.+?)(?=\n-\s|\Z)", notes, re.S | re.M | re.I)
    if sm:
        src = unwrap(sm.group(1))
        src = re.sub(r"\s*(?:Via|Framing from|Sheol framing from)\s*\[\[[^\]]+\]\]\.?\s*$",
                     "", src, flags=re.I)
        src = re.sub(r"\s*(?:via|from)\s*\[\[[^\]]+\]\]\.?\s*$", "", src, flags=re.I)
        src = src.rstrip(". ")
    if not src:
        src = SOURCES_OVERRIDE.get(art_id, "")
    lm = re.search(r"roughly\s+(\d+)\s+minutes", notes)
    mins = lm.group(1) if lm else str(max(8, round(len(manu.split()) / 130)))

    # --- manuscript movements
    parts = re.split(r"^\*\*(\d+)\s*·\s*(.+?)\*\*\s*$", manu, flags=re.M)
    movements = [(parts[i], parts[i + 1], parts[i + 2]) for i in range(1, len(parts), 3)]

    out = [f'      <article id="{art_id}" hidden>']
    if art_id not in TRANSLATED:
        out.append(XLATE)
    out += [f'        <p class="eyebrow">Reflection {num:02d} &nbsp;&middot;&nbsp; <b>{esc(passage)}</b></p>',
           f'        <h1>{inline(title)}</h1>']
    if fm.get("big-idea"):
        out.append(f'        <p class="epigraph">{inline(fm["big-idea"])}</p>')
    out += ['        <div class="apphead">',
            f'          <span class="wide"><k>Text</k>{esc(passage)}</span>',
            '          <span><k>Form</k>five movements</span>',
            f'          <span><k>Reading</k>~{mins} min</span>']
    if STANDING.get(art_id):
        out.append(f'          <span class="wide"><k>Standing</k>{STANDING[art_id]}</span>')
    out += ['        </div>',
            '',
            '        <p class="entrydate">'
            + "".join(f'<span class="l-{c}">{t}</span>'
                      for c, t in zip(("en", "es", "pt"), REVISED))
            + '</p>',
            '',
            '',
            '        <div class="body">']

    for n, head, chunk in movements:
        out.append(f'          <h2><span class="mv">{n}</span> {inline(head.strip())}</h2>')
        for para in re.split(r"\n\s*\n", chunk.strip()):
            para = unwrap(para)
            if not para:
                continue
            if re.fullmatch(r"[-*_]\s*(?:[-*_]\s*){2,}", para):
                continue  # markdown horizontal rule, not a paragraph
            # a wholly-bold paragraph, or a lead-in ending in one long bold
            # sentence, is the big-idea beat -> pull quote
            whole = re.fullmatch(r"\*\*(.+)\*\*", para, re.S)
            trailing = re.fullmatch(r"(.*?[.!?])\s+\*\*(.+?)\*\*", para, re.S)
            if whole:
                out.append(f'          <p class="pull">{inline(whole.group(1))}</p>')
            elif trailing and len(trailing.group(2)) > 60 and "**" not in trailing.group(1):
                out.append(f'          <p>{inline(trailing.group(1))}</p>')
                out.append(f'          <p class="pull">{inline(trailing.group(2))}</p>')
            else:
                out.append(f'          <p>{inline(para)}</p>')
    out.append('        </div>')

    if items:
        out += ['', '        <section class="apparatus">', '          <h3>Apparatus</h3>',
                '          <dl>']
        for label, val in items:
            out.append(f'            <dt>{inline(label)}</dt><dd>{inline(val)}</dd>')
        out.append('          </dl>')
        if src:
            out.append(f'          <p class="sources"><k>Sources</k>{inline(src)}</p>')
        out.append('        </section>')
    if XREF.get(art_id):
        out += ['        <aside class="xref">',
                '          <h4><span class="l-en">Also on this passage</span>'
                '<span class="l-es">Tambi&eacute;n sobre este pasaje</span>'
                '<span class="l-pt">Tamb&eacute;m sobre esta passagem</span></h4>',
                '          <ul>']
        for sec, tid, label in XREF[art_id]:
            out.append(f'          <li><span class="sec">{sec.title()}</span>'
                       f'<a href="#{sec}/{tid}" data-xsec="{sec}" data-xart="{tid}">'
                       f'{label}</a></li>')
        out += ['          </ul>',
                '          <p class="why">'
                '<span class="l-en">Same passage, same worksheet, different job. '
                'Reflections preaches it, Roots takes a single word apart, '
                'Provenance asks where the text came from.</span>'
                '<span class="l-es">Mismo pasaje, misma hoja de trabajo, distinto '
                'trabajo. Reflections lo predica, Roots desarma una palabra, '
                'Provenance pregunta de d&oacute;nde vino el texto.</span>'
                '<span class="l-pt">Mesma passagem, mesma folha de trabalho, trabalho '
                'diferente. Reflections prega, Roots desmonta uma palavra, Provenance '
                'pergunta de onde o texto veio.</span></p>',
                '        </aside>']
    out.append('      </article>')
    return "\n".join(out), title, mins


def toc(art_id, title, passage, num):
    return ('        <a class="toc-item" href="#reflections/%s" data-target="%s">\n'
            '          <span class="n">%02d</span>\n'
            '          <span class="t">%s</span>\n'
            '          <span class="r">%s</span>\n'
            '        </a>' % (art_id, art_id, num, inline(title), esc(passage)))


arts, tocs = [], []
for i, (stem, art_id, passage) in enumerate(ORDER):
    a, title, mins = build(stem, art_id, passage, START_NUM + i)
    arts.append(a)
    tocs.append(toc(art_id, title, passage, START_NUM + i))
    print(f"  {START_NUM+i:02d} {art_id:<14} {title[:38]:<38} ~{mins}min", file=sys.stderr)

Path("reflections_articles.html").write_text("\n\n".join(arts) + "\n", encoding="utf-8")
Path("reflections_toc.html").write_text("\n".join(tocs) + "\n", encoding="utf-8")
print(f"\nwrote {len(arts)} articles", file=sys.stderr)
