#!/usr/bin/env python3
"""Audit pass 4 — two things a full read of the live page turned up.

Encounter still described the confidence labels as three, in all three
languages, and the Wonder sample pointed at its adult counterpart in prose
without linking to it.
"""
import re
from pathlib import Path

p = Path("marginalia.html")
s = p.read_text(encoding="utf-8")
before = len(s)


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n} of {old[:60]!r}, found {s.count(old)}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- B1, continued
sub("Same sources, same three confidence labels, and the same hard rule",
    "Same sources, same five confidence labels, and the same hard rule")
sub("<p>The three labels get introduced in session 1 and used every week after:",
    "<p>The five labels get introduced in session 1 and used every week after:")

sub("Mismas fuentes, mismas tres etiquetas de confianza, y la misma regla dura",
    "Mismas fuentes, mismas cinco etiquetas de confianza, y la misma regla dura")
sub('<p>Las tres etiquetas se presentan en la sesi&oacute;n 1 y se usan cada semana: '
    '<span class="conf">Consenso</span> <span class="conf">En debate</span> '
    '<span class="conf">Nuestra lectura</span>.',
    '<p>Las cinco etiquetas se presentan en la sesi&oacute;n 1 y se usan cada semana: '
    '<span class="conf">Consenso</span> <span class="conf">Mayor&iacute;a amplia</span> '
    '<span class="conf">En debate</span> <span class="conf">Nuestra lectura</span> '
    '<span class="conf">Rechazado</span>.')

sub("Mesmas fontes, mesmas tr&ecirc;s etiquetas de confian&ccedil;a, e a mesma regra dura",
    "Mesmas fontes, mesmas cinco etiquetas de confian&ccedil;a, e a mesma regra dura")
sub('<p>As tr&ecirc;s etiquetas s&atilde;o apresentadas no encontro 1 e usadas toda semana: '
    '<span class="conf">Consenso</span> <span class="conf">Em debate</span> '
    '<span class="conf">Nossa leitura</span>.',
    '<p>As cinco etiquetas s&atilde;o apresentadas no encontro 1 e usadas toda semana: '
    '<span class="conf">Consenso</span> <span class="conf">Maioria ampla</span> '
    '<span class="conf">Em debate</span> <span class="conf">Nossa leitura</span> '
    '<span class="conf">Rejeitado</span>.')
print("B1  Encounter now describes five labels, in all three languages")

# ---------------------------------------------------------------- A1, continued
# The Wonder sample already names its adult counterpart. Make it a link.
LINK = ('<a href="#roots/roots-raqia" data-xsec="roots" data-xart="roots-raqia">'
        'Roots 01, <i>%s</i></a>')
sub("Roots 01, <i>Firmament</i>, which is the adult version of this same page.",
    (LINK % "Firmament") + ", which is the adult version of this same page.")
sub("Roots 01, <i>Firmamento</i>, que es la versi&oacute;n adulta de esta misma p&aacute;gina.",
    (LINK % "Firmamento") + ", que es la versi&oacute;n adulta de esta misma p&aacute;gina.")
sub("Roots 01, <i>Firmamento</i>, que &eacute; a vers&atilde;o adulta desta mesma p&aacute;gina.",
    (LINK % "Firmamento") + ", que &eacute; a vers&atilde;o adulta desta mesma p&aacute;gina.")
print("A1  Wonder sample links through to its adult counterpart")

p.write_text(s, encoding="utf-8")
print(f"\nmarginalia.html {before} -> {len(s)} bytes")
