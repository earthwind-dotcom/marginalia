#!/usr/bin/env python3
"""Audit pass 3 — per-entry work applied across every article.

A1 cross-references between the sermon, the word study and the text history
that share a passage · A5 revision dates · C2 honest notices on entries that
are not translated yet, plus the last untranslated chrome.
"""
import re
from pathlib import Path

p = Path("marginalia.html")
s = p.read_text(encoding="utf-8")
before = len(s)

# ---------------------------------------------------------------- A1 map
XREF = {
    "meek": ["roots-praus"],
    "dust": ["roots-nephesh"],
    "psalm88": ["roots-sheol"],
    "whose-world": ["prov-genesis"],
    "frame": ["roots-raqia", "prov-genesis"],
    "verse-bent": ["prov-ham"],
    "moabite": ["prov-ruth"],
    "two-drafts": ["prov-chronicles"],
    "rule-breaks": ["prov-wisdom"],
    "third-way": ["prov-cheek"],
    "life-age": ["roots-aionios"],
    "luke-checked": ["prov-gospels"],
    "couldnt-lose": ["prov-adultery"],
    "dead-rise": ["prov-rapture", "roots-sheol"],
    "church-shape": ["prov-paul"],
    "roots-praus": ["meek"],
    "roots-raqia": ["frame", "prov-genesis"],
    "roots-aionios": ["life-age"],
    "roots-nephesh": ["dust", "roots-sheol"],
    "roots-sheol": ["psalm88", "dead-rise", "roots-nephesh"],
    "prov-gospels": ["luke-checked"],
    "prov-adultery": ["couldnt-lose"],
    "prov-paul": ["church-shape"],
    "prov-chronicles": ["two-drafts"],
    "prov-genesis": ["whose-world", "frame", "roots-raqia"],
    "prov-ham": ["verse-bent"],
    "prov-rapture": ["dead-rise"],
    "prov-ruth": ["moabite"],
    "prov-wisdom": ["rule-breaks"],
    "prov-cheek": ["third-way"],
}
LABEL = {"reflections": "Reflections", "encounter": "Encounter", "roots": "Roots",
         "provenance": "Provenance", "wonder": "Wonder", "colophon": "Colophon"}
LATE = {"col-what", "col-method", "col-status", "col-coming",
        "roots-nephesh", "roots-sheol"}

DATE = {
    "l-en": ("Revised 6 September 2026", "Revised 7 September 2026"),
    "l-es": ("Revisado el 6 de septiembre de 2026", "Revisado el 7 de septiembre de 2026"),
    "l-pt": ("Revisado em 6 de setembro de 2026", "Revisado em 7 de setembro de 2026"),
}
XLATE = ('<p class="xlate">'
         '<span class="l-es">Esta pieza a&uacute;n no est&aacute; traducida. '
         'El texto que sigue est&aacute; en ingl&eacute;s.</span>'
         '<span class="l-pt">Esta pe&ccedil;a ainda n&atilde;o foi traduzida. '
         'O texto a seguir est&aacute; em ingl&ecirc;s.</span></p>')
WHY = ('<p class="why">'
       '<span class="l-en">Same passage, same worksheet, different job. Reflections '
       'preaches it, Roots takes a single word apart, Provenance asks where the text '
       'came from.</span>'
       '<span class="l-es">Mismo pasaje, misma hoja de trabajo, distinto trabajo. '
       'Reflections lo predica, Roots desarma una palabra, Provenance pregunta de '
       'd&oacute;nde vino el texto.</span>'
       '<span class="l-pt">Mesma passagem, mesma folha de trabalho, trabalho diferente. '
       'Reflections prega, Roots desmonta uma palavra, Provenance pergunta de onde o '
       'texto veio.</span></p>')

ART = re.compile(r'<article id="([a-z0-9-]+)"[^>]*>.*?\n(\s*)</article>', re.S)
VIEW = re.compile(r'<div class="view" id="view-([a-z]+)"')

# section for every article id, and every article's English title
sections, titles = {}, {}
cur = None
for m in re.finditer(r'<div class="view" id="view-([a-z]+)"|<article id="([a-z0-9-]+)"[^>]*>', s):
    if m.group(1):
        cur = m.group(1)
    else:
        sections[m.group(2)] = cur
for m in ART.finditer(s):
    h = re.search(r"<h1[^>]*>(.*?)</h1>", m.group(0), re.S)
    if h:
        titles[m.group(1)] = re.sub(r"\s+", " ", h.group(1)).strip()

missing = [t for v in XREF.values() for t in v if t not in titles]
assert not missing, f"cross-reference target(s) not found: {missing}"


def rewrite(m):
    art_id, indent = m.group(1), m.group(2)
    block = m.group(0)
    late = art_id in LATE

    # --- A5: a revision date at the top of every language pane
    def datestamp(dm):
        pad = dm.group(1)
        spans = "".join(
            f'<span class="{cls}">{pair[1] if late else pair[0]}</span>'
            for cls, pair in DATE.items())
        return f'{pad}<p class="entrydate">{spans}</p>\n{pad}<div class="body">'

    block, nd = re.subn(r'(\n\s*)<div class="body">', datestamp, block)

    # --- C2: say so when an entry has no translation
    if '<div class="l-es">' not in block:
        block = re.sub(r'(<article id="[a-z0-9-]+"[^>]*>\n)(\s*)',
                       lambda mm: mm.group(1) + mm.group(2) + XLATE + "\n" + mm.group(2),
                       block, count=1)

    # --- A1: link the entries that share a passage
    targets = XREF.get(art_id)
    if targets:
        lis = "".join(
            f'\n{indent}    <li><span class="sec">{LABEL[sections[t]]}</span>'
            f'<a href="#{sections[t]}/{t}" data-xsec="{sections[t]}" data-xart="{t}">'
            f'{titles[t]}</a></li>'
            for t in targets)
        aside = (f'\n{indent}  <aside class="xref">\n'
                 f'{indent}    <h4><span class="l-en">Also on this passage</span>'
                 f'<span class="l-es">Tambi&eacute;n sobre este pasaje</span>'
                 f'<span class="l-pt">Tamb&eacute;m sobre esta passagem</span></h4>\n'
                 f'{indent}    <ul>{lis}\n{indent}    </ul>\n'
                 f'{indent}    {WHY}\n'
                 f'{indent}  </aside>\n{indent}')
        block = block[: block.rindex(f"\n{indent}</article>")] + aside + "</article>"
    return block


s, n = ART.subn(rewrite, s)
print(f"A1/A5/C2  rewrote {n} articles")
print(f"A1        cross-referenced {len(XREF)} entries")
print(f"C2        translation notices on {s.count('class=\"xlate\"')} entries")
print(f"A5        {s.count('class=\"entrydate\"')} date lines")

# ---------------------------------------------------------------- C2 chrome
s = s.replace(
    '<p class="sectionnote">Where a text came from, how it reached us, and what surrounded it when it was written.</p>',
    '''<p class="sectionnote">
    <span class="l-en">Where a text came from, how it reached us, and what surrounded it when it was written.</span>
    <span class="l-es">De d&oacute;nde vino un texto, c&oacute;mo lleg&oacute; hasta nosotros, y qu&eacute; lo rodeaba cuando se escribi&oacute;.</span>
    <span class="l-pt">De onde veio um texto, como chegou at&eacute; n&oacute;s, e o que o cercava quando foi escrito.</span>
  </p>''')
s = s.replace(
    '<p class="sectionnote">Who makes this, how, and what is still unfinished.</p>',
    '''<p class="sectionnote">
    <span class="l-en">Who makes this, how, and what is still unfinished.</span>
    <span class="l-es">Qui&eacute;n hace esto, c&oacute;mo, y qu&eacute; sigue sin terminar.</span>
    <span class="l-pt">Quem faz isto, como, e o que ainda est&aacute; por terminar.</span>
  </p>''')
s = s.replace(
    '      <h2>Studies</h2>',
    '      <h2><span class="l-en">Studies</span><span class="l-es">Estudios</span>'
    '<span class="l-pt">Estudos</span></h2>')
s = s.replace(
    '<span class="n">About</span><span class="t">How Provenance works</span>',
    '<span class="n"><span class="l-en">About</span><span class="l-es">Acerca de</span>'
    '<span class="l-pt">Sobre</span></span><span class="t">How Provenance works</span>')
print("C2        Provenance and Colophon chrome translated")

# ---------------------------------------------------------------- C5 chrome
s = s.replace(
    '      <h1 id="qhead">Search</h1>',
    '      <h1 id="qhead"><span class="l-en">Search</span><span class="l-es">Buscar</span>'
    '<span class="l-pt">Buscar</span></h1>')
s = s.replace(
    """      qcount.textContent = hits.length === 0
        ? 'Nothing matches that.'
        : hits.length + (hits.length === 1 ? ' entry' : ' entries');""",
    """      var L = curLang();
      var none = {en:'Nothing matches that.', es:'No hay nada que coincida.',
                  pt:'Nada corresponde a isso.'}[L];
      var one  = {en:' entry', es:' entrada', pt:' entrada'}[L];
      var many = {en:' entries', es:' entradas', pt:' entradas'}[L];
      qcount.textContent = hits.length === 0
        ? none
        : hits.length + (hits.length === 1 ? one : many);""")
print("C5        search results speak the selected language")

p.write_text(s, encoding="utf-8")
print(f"\nmarginalia.html {before} -> {len(s)} bytes")
