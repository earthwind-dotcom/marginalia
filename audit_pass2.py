#!/usr/bin/env python3
"""Audit pass 2 — content.

A1 cross-references · A2 Encounter next step · A3 byline and corrections ·
A4 channel slots · A5 per-entry dates · B1 label legends · B3 honest status ·
C2 translation notices and translated chrome · D1 Wonder pointer ·
D2 the two finished word studies that were never published.
"""
import re
from pathlib import Path

p = Path("marginalia.html")
s = p.read_text(encoding="utf-8")
before = len(s)


def once(pattern, repl, text, flags=0, expect=1):
    text, n = re.subn(pattern, repl if callable(repl) else (lambda m, r=repl: r),
                      text, flags=flags)
    assert n == expect, f"expected {expect}, made {n}: {pattern[:70]}"
    return text


# ================================================================ D2
# Two finished exegesis worksheets that never made it onto the site.
NEPHESH = """      <article id="roots-nephesh" hidden>
        <div class="l-en">
          <p class="eyebrow">Roots 04 &nbsp;&middot;&nbsp; <b>Genesis 2:7</b></p>
          <h1>Soul</h1>
          <div class="wordcard">
            <p class="orig">&#x05E0;&#x05B6;&#x05E4;&#x05B6;&#x05E9;&#x05C1;</p>
            <p class="tr">nephesh &nbsp;&middot;&nbsp; H5315</p>
            <p class="ref">soul (KJV) &middot; being (NRSV, ESV, NIV) &middot; creature &middot; life &middot; person</p>
          </div>
          <div class="body">
            <h2>What the word is made of</h2>
            <p>The concrete sense is <b>throat</b>. The gullet, the neck. When a psalm says the waters have come up to my <i>nephesh</i>, it means up to my neck, I am drowning. Sheol &ldquo;widens its <i>nephesh</i>&rdquo; and swallows.</p>
            <p>From throat the word stretches to <b>appetite</b>, the part of you that craves. From appetite to <b>life</b> itself. From life to <b>a person</b>, someone, anyone, the way a ship carries so many souls on board. It turns up about seven hundred and fifty times, and an immaterial deathless part of a human being is not among the senses the lexicons list.</p>
            <p>And here is the one that settles it. <i>Nephesh</i> can mean a <b>corpse</b>. The purity laws speak of not going near a dead <i>nephesh</i>. Whatever this word names, it is not the thing in you that death cannot touch.</p>

            <h2>What it meant to the people reading it</h2>
            <p>Genesis 2:7 is a recipe with two ingredients and a result. Dust from the ground, the breath of God into the nostrils, and &ldquo;the man became a living being,&rdquo; <i>nephesh &#7717;ayyah</i>.</p>
            <p>That phrase is not reserved for humans. Genesis has already used it, two chapters earlier, for the sea creatures, the birds and the livestock, and it uses it again twelve verses later for the animals the man names. It is the category God&rsquo;s creatures share.</p>
            <p>So the grammar is doing something specific. The man does not <i>receive</i> a <i>nephesh</i>. He <i>becomes</i> one. It is the outcome of the process, not a component installed partway through it. And Genesis closes the loop itself: &ldquo;dust you are, and to dust you shall return.&rdquo; Death, in this story, is verse 7 run backwards.</p>

            <h2>How it drifted</h2>
            <p>When the Hebrew Bible was put into Greek, <i>nephesh</i> became <i>psych&#275;</i>, and <i>psych&#275;</i> already carried a load the Hebrew never had: the immaterial self, trapped in a body, waiting to get free. That idea is real, and it is a good deal older than Christianity, but it is Greek.</p>
            <p>You can watch the drift happen in English. The King James renders the identical Hebrew phrase &ldquo;living creature&rdquo; when Genesis 1 is talking about animals and &ldquo;living soul&rdquo; when Genesis 2 is talking about the man. One phrase, two translations, and a whole anthropology smuggled in between them.</p>

            <h2>Why it matters</h2>
            <p>Because it changes where hope has to come from. If you already own a deathless core, resurrection is a formality and grief is a lapse of nerve. If you are dust that God breathed on, then death is real, and the only hope available is that the God who breathed the first time has promised to breathe again.</p>
            <p>Which is, as it happens, exactly what the Bible offers. Not the survival of a part. The raising of a person.</p>
          </div>
          <section class="apparatus">
            <h3>Standing</h3>
            <dl>
              <dt>Claim 1</dt><dd><span class="conf">Consensus</span> In Genesis 2:7 <i>nephesh &#7717;ayyah</i> means &ldquo;living being / creature,&rdquo; the same category the chapter gives the animals. It does not name an immortal soul.</dd>
              <dt>Claim 2</dt><dd><span class="conf">Consensus</span> <i>Nephesh</i> denotes the whole living person, described from the angle of life and appetite, rather than a separable part of one.</dd>
              <dt>Claim 3</dt><dd><span class="conf">Consensus</span> The immortal-soul reading is a later overlay, carried in largely through the Greek <i>psych&#275;</i>.</dd>
              <dt>Claim 4</dt><dd><span class="conf">Debated</span> Whether <i>any</i> Israelite text imagines a <i>nephesh</i> apart from the body. The standard answer is no; Steiner dissents on a handful of passages, none of them Genesis 2:7.</dd>
              <dt>Counter-view</dt><dd>Steiner (2015) argues that some texts, notably Ezekiel 13:17&ndash;21 and Rachel&rsquo;s <i>nephesh</i> &ldquo;departing&rdquo; in Genesis 35:18, do picture a soul that can leave the body. Even there the sense is &ldquo;life,&rdquo; not a conscious self with a post-mortem career, and it does not touch this verse.</dd>
            </dl>
            <p class="sources"><k>Sources</k>HALOT and BDB, s.v. &#x05E0;&#x05B6;&#x05E4;&#x05B6;&#x05E9;&#x05C1; &middot; Wolff, <i>Anthropology of the Old Testament</i> &middot; Westermann, <i>Genesis 1&ndash;11</i> (Continental) &middot; Wenham, <i>Genesis 1&ndash;15</i> (WBC) &middot; Barr, <i>The Garden of Eden and the Hope of Immortality</i> &middot; Steiner, <i>Disembodied Souls</i> (ANEM 11)</p>
          </section>
        </div>
      </article>"""

SHEOL = """      <article id="roots-sheol" hidden>
        <div class="l-en">
          <p class="eyebrow">Roots 05 &nbsp;&middot;&nbsp; <b>Psalm 88</b>, and about sixty-five other places</p>
          <h1>Hell</h1>
          <div class="wordcard">
            <p class="orig">&#x05E9;&#x05C1;&#x05B0;&#x05D0;&#x05D5;&#x05B9;&#x05DC;</p>
            <p class="tr">&#353;&#601;&#702;&#244;l &nbsp;&middot;&nbsp; H7585</p>
            <p class="ref">hell <i>and</i> grave (KJV) &middot; Sheol (ESV, NRSV) &middot; the realm of the dead (NIV)</p>
          </div>
          <div class="body">
            <h2>What the word is made of</h2>
            <p>Nobody knows. The etymology of <i>Sheol</i> is genuinely uncertain, and that is worth saying out loud, because popular word studies love an origin story and this word refuses to give one. What we have instead is about sixty-five occurrences, heavily concentrated in poetry, and they are remarkably consistent about what the place is like.</p>

            <h2>What it meant to the people reading it</h2>
            <p>It is where everyone goes. Jacob expects to go down to Sheol mourning for his son. Job asks God to <i>hide</i> him there, as a refuge from suffering. Ecclesiastes says the wise and the fool arrive at the same place. It is the destination of the patriarch and the scoundrel alike.</p>
            <p>The imagery is fixed: <b>down</b>, always down. Darkness, dust, silence, forgetfulness. A pit with bars and gates. What is not there is just as consistent. No fire. No courtroom. No sorting of anybody into anything.</p>
            <p>Psalm 88 is the sustained example, and it is unsparing. The psalmist counts himself already among the dead, in the regions dark and deep, and asks whether God&rsquo;s wonders and his steadfast love are known in the land of forgetfulness. The expected answer is no. The psalm never turns, and it ends on the word &ldquo;darkness.&rdquo;</p>
            <p>So Sheol is a destination, not a verdict.</p>

            <h2>Where &ldquo;hell&rdquo; came from</h2>
            <p>Two steps. First the Greek: the Septuagint renders <i>Sheol</i> with <i>Had&#275;s</i>, importing a term from another culture&rsquo;s underworld, and over centuries the Greek associations come along with it. Then the English: the King James renders the same Hebrew word &ldquo;hell&rdquo; in some places and &ldquo;grave&rdquo; in others, on no consistent principle a reader can see.</p>
            <p>The clearest tell is Jonah. He prays &ldquo;out of the belly of hell,&rdquo; in the King James, from inside a fish. Whatever he means, he does not mean the place of final punishment. He means the grave, he means as good as dead.</p>
            <p>And the fire? That is a different word entirely. When the Gospels talk about fire and judgment they almost always say <i>Gehenna</i>, which is not a cosmological realm at all. It is the Valley of Hinnom, a real ravine south of Jerusalem with a grim history behind it. Two words, two concepts, one English word laid over both.</p>

            <h2>Why it matters</h2>
            <p>Mostly it changes how you read the laments. When Psalm 88 says the dead do not praise God, it is not teaching you the afterlife. It is arguing with God: rescue me <i>now</i>, while I can still say something. That is a prayer, not a doctrine, and the canon kept it without an ending.</p>
            <p>It also relocates the hope. The Hebrew Bible does not comfort you by telling you a part of you cannot die. It pushes, slowly and late, toward something harder and better: that God raises the dead.</p>
          </div>
          <section class="apparatus">
            <h3>Standing</h3>
            <dl>
              <dt>Claim 1</dt><dd><span class="conf">Consensus</span> <i>Sheol</i> does not carry the English &ldquo;hell&rdquo; concept. There is no fire, no torment and no judgment scene attached to it.</dd>
              <dt>Claim 2</dt><dd><span class="conf">Strong majority</span> In most texts Sheol is the common destination of all the dead, righteous and wicked together, rather than a fate assigned to some.</dd>
              <dt>Claim 3</dt><dd><span class="conf">Consensus</span> The fiery-judgment imagery in the Gospels enters mainly through <i>Gehenna</i>, the Valley of Hinnom, a separate word with a separate history.</dd>
              <dt>Claim 4</dt><dd><span class="conf">Rejected</span> That the Old Testament has no afterlife hope at all. Isaiah 26:19 and Daniel 12:2 are real, if late and comparatively rare.</dd>
              <dt>Counter-view</dt><dd>Some conservative readers harmonise <i>Sheol</i> with a later two-compartment picture of the dead, on the strength of Luke 16. That is a synthesis across the whole canon rather than what the Hebrew texts describe on their own terms, and it should be labelled as one.</dd>
              <dt>Still to verify</dt><dd>The exact number of times the King James renders <i>Sheol</i> as &ldquo;hell&rdquo; is quoted as thirty-one in a great many places. The count varies by method and is not printed here until it has been checked against a concordance.</dd>
            </dl>
            <p class="sources"><k>Sources</k>HALOT and BDB, s.v. &#x05E9;&#x05C1;&#x05B0;&#x05D0;&#x05D5;&#x05B9;&#x05DC; &middot; Johnston, <i>Shades of Sheol</i> (2002) &middot; Bernstein, <i>The Formation of Hell</i> (1993) &middot; Levenson, <i>Resurrection and the Restoration of Israel</i> (2006) &middot; Lewis, &ldquo;Dead, Abode of the,&rdquo; <i>ABD</i> 2 &middot; Bailey, &ldquo;Gehenna: The Topography of Hell,&rdquo; <i>Biblical Archaeologist</i> 49 (1986) &middot; Tromp, <i>Primitive Conceptions of Death and the Nether World</i> (1969)</p>
          </section>
        </div>
      </article>"""

s = once(r'(      <article id="roots-praus".*?\n      </article>\n)',
         lambda m: m.group(1) + "\n" + NEPHESH + "\n\n" + SHEOL + "\n", s, re.S)

ROOTS_TOC = """        <a class="toc-item" href="#roots/roots-nephesh" data-target="roots-nephesh">
          <span class="n">04</span>
          <span class="t"><span class="l-en">Soul</span><span class="l-es">Alma</span><span class="l-pt">Alma</span></span>
          <span class="r">Genesis 2:7</span>
        </a>
        <a class="toc-item" href="#roots/roots-sheol" data-target="roots-sheol">
          <span class="n">05</span>
          <span class="t"><span class="l-en">Hell</span><span class="l-es">Infierno</span><span class="l-pt">Inferno</span></span>
          <span class="r">Psalm 88</span>
        </a>
"""
s = once(r'(        <a class="toc-item" href="#roots/roots-praus".*?\n        </a>\n)',
         lambda m: m.group(1) + ROOTS_TOC, s, re.S)
print("D2  published roots-nephesh and roots-sheol")

# ================================================================ D1
# Colophon picks up the Wonder pointer that the tab row gave up.
COMING = """      <article id="col-coming" hidden>
        <p class="eyebrow">Colophon 04 &nbsp;&middot;&nbsp; <b>Not yet</b></p>
        <h1>What is coming</h1>
        <p class="epigraph">The work that is planned, described honestly, so that nothing on this site has to pretend it is further along than it is.</p>
        <div class="body">
          <h2>Wonder</h2>
          <p>The same honesty, built for children, so that nothing they are told has to be unlearned at nineteen. The approach, three age bands and one worked sample are written and you can read them: <a href="#wonder/wonder-about" data-xsec="wonder" data-xart="wonder-about">Wonder</a>.</p>
          <p>The curriculum itself is not written, and it will not be until a proper review of what already exists in children&rsquo;s biblical material has been done and the real gaps are known. Building it before that would just add another opinionated series to a crowded shelf. Wonder is off the main navigation until then, which seemed more honest than giving an empty room its own door.</p>

          <h2>More word studies</h2>
          <p>Roots publishes five. More are drafted as full worksheets and will go up as they are checked.</p>

          <h2>A way to reach me</h2>
          <p>There is no contact address on this site yet, which is a real gap on a site that invites correction. One is being set up and will appear on <a href="#colophon/col-method" data-xsec="colophon" data-xart="col-method">How the work is done</a>.</p>

          <h2>The rest of the translation</h2>
          <p>Spanish and Portuguese cover the navigation, Encounter, Roots and Wonder. Reflections and Provenance are still English, and each entry says so when you switch. That gap closes as the content stops moving.</p>
        </div>
      </article>"""
s = once(r'(      <article id="col-status".*?\n      </article>\n)',
         lambda m: m.group(1) + "\n" + COMING + "\n", s, re.S)
s = once(r'(        <a class="toc-item" href="#colophon/col-status".*?\n        </a>\n)',
         lambda m: m.group(1) + """        <a class="toc-item" href="#colophon/col-coming" data-target="col-coming">
          <span class="n">04</span><span class="t">What is coming</span><span class="r">not yet</span>
        </a>
""", s, re.S)
print("D1  Colophon gained 'What is coming', pointing at Wonder")

# ================================================================ B1
# The legends have to name the five labels actually in use.
s = once(
    r'<h2>The three labels</h2>\n(\s*)<p>Every claim carries one, so you always know what you are being handed\.</p>\n\s*<ul class="plain">\n.*?</ul>',
    lambda m: '''<h2>The five labels</h2>
            <p>Every claim carries one, so you always know what you are being handed.</p>
            <ul class="plain">
              <li><span class="conf">Consensus</span> Critical scholarship broadly agrees. You can lean on it.</li>
              <li><span class="conf">Strong majority</span> Most of the field, with a serious minority holding out. Named where it matters.</li>
              <li><span class="conf">Debated</span> Serious scholars land in different places. Both sides get stated.</li>
              <li><span class="conf">Our read</span> A judgement call made here, and labelled as one.</li>
              <li><span class="conf">Rejected</span> A claim you will meet elsewhere that the evidence does not support.</li>
            </ul>''', s, re.S)
s = once(
    r'<h2>Las tres etiquetas</h2>\n\s*<p>Cada afirmaci&oacute;n lleva una, para que siempre sepas qu&eacute; te est&aacute;n dando\.</p>\n\s*<ul class="plain">\n.*?</ul>',
    lambda m: '''<h2>Las cinco etiquetas</h2>
            <p>Cada afirmaci&oacute;n lleva una, para que siempre sepas qu&eacute; te est&aacute;n dando.</p>
            <ul class="plain">
              <li><span class="conf">Consenso</span> La investigaci&oacute;n cr&iacute;tica coincide en general. Te puedes apoyar en eso.</li>
              <li><span class="conf">Mayor&iacute;a amplia</span> Casi todo el campo, con una minor&iacute;a seria que no lo acepta. Se la nombra cuando importa.</li>
              <li><span class="conf">En debate</span> Estudiosos serios llegan a conclusiones distintas. Se exponen los dos lados.</li>
              <li><span class="conf">Nuestra lectura</span> Un juicio tomado aqu&iacute;, y etiquetado como tal.</li>
              <li><span class="conf">Descartado</span> Una afirmaci&oacute;n que vas a encontrar por ah&iacute; y que la evidencia no sostiene.</li>
            </ul>''', s, re.S)
s = once(
    r'<h2>As tr&ecirc;s etiquetas</h2>\n\s*<p>Toda afirma&ccedil;&atilde;o carrega uma, para que voc&ecirc; sempre saiba o que est&aacute; recebendo\.</p>\n\s*<ul class="plain">\n.*?</ul>',
    lambda m: '''<h2>As cinco etiquetas</h2>
            <p>Toda afirma&ccedil;&atilde;o carrega uma, para que voc&ecirc; sempre saiba o que est&aacute; recebendo.</p>
            <ul class="plain">
              <li><span class="conf">Consenso</span> A pesquisa cr&iacute;tica concorda de modo geral. D&aacute; para se apoiar nisso.</li>
              <li><span class="conf">Maioria ampla</span> Quase todo o campo, com uma minoria s&eacute;ria que discorda. &Eacute; nomeada quando importa.</li>
              <li><span class="conf">Em debate</span> Estudiosos s&eacute;rios chegam a lugares diferentes. Os dois lados s&atilde;o expostos.</li>
              <li><span class="conf">Nossa leitura</span> Um ju&iacute;zo feito aqui, e rotulado como tal.</li>
              <li><span class="conf">Rejeitado</span> Uma afirma&ccedil;&atilde;o que voc&ecirc; vai encontrar por a&iacute; e que as evid&ecirc;ncias n&atilde;o sustentam.</li>
            </ul>''', s, re.S)

FIVE = ('<span class="conf">Consensus</span> <span class="conf">Strong majority</span> '
        '<span class="conf">Debated</span> <span class="conf">Our read</span> '
        '<span class="conf">Rejected</span>')
s, n = re.subn(r'<span class="conf">Consensus</span> <span class="conf">Debated</span> '
               r'<span class="conf">Our read</span>', FIVE, s)
print(f"B1  legends updated (3 language legends, {n} inline label rows)")

# ================================================================ A2
NEXTSTEP = {
    "l-en": ('What you can do now',
             '<p>The course is not scheduled yet. When it is, the date will be posted here. In the meantime three things are open to you today, and none of them require you to tell anyone anything.</p>'
             '<p><b>Read Mark.</b> It is the shortest of the four accounts, about ninety minutes end to end. Read it the way you would read anybody&rsquo;s account of a person they knew and could not get over. If you want to know where the document itself came from, <a href="#provenance/prov-gospels" data-xsec="provenance" data-xart="prov-gospels">Provenance</a> lays that out.</p>'
             '<p><b>Try five minutes.</b> Somewhere quiet, say plainly whatever is actually true for you, including that you are not sure anyone is listening. That is a real prayer. It is where most people start, and it does not commit you to anything.</p>'
             '<p><b>Have one honest conversation.</b> With somebody who will not perform certainty at you. One of those is worth more than any course, including this one.</p>'
             '<p>And if none of that appeals, that is a real answer too. Nothing here needs you to decide anything today.</p>'),
    "l-es": ('Qu&eacute; puedes hacer ahora',
             '<p>El curso todav&iacute;a no tiene fecha. Cuando la tenga, se publicar&aacute; aqu&iacute;. Mientras tanto hay tres cosas abiertas para ti hoy, y ninguna te obliga a decirle nada a nadie.</p>'
             '<p><b>Lee Marcos.</b> Es el m&aacute;s corto de los cuatro relatos, unos noventa minutos de principio a fin. L&eacute;elo como leer&iacute;as el relato de cualquiera sobre una persona a la que conoci&oacute; y no pudo olvidar.</p>'
             '<p><b>Prueba cinco minutos.</b> En un lugar tranquilo, di con claridad lo que de verdad te pasa, incluso que no est&aacute;s seguro de que alguien te escuche. Eso es una oraci&oacute;n de verdad. Ah&iacute; empieza casi todo el mundo, y no te compromete a nada.</p>'
             '<p><b>Ten una conversaci&oacute;n honesta.</b> Con alguien que no te act&uacute;e una certeza que no tiene. Una de esas vale m&aacute;s que cualquier curso, incluido este.</p>'
             '<p>Y si nada de eso te atrae, esa tambi&eacute;n es una respuesta v&aacute;lida. Aqu&iacute; nada necesita que decidas nada hoy.</p>'),
    "l-pt": ('O que voc&ecirc; pode fazer agora',
             '<p>O curso ainda n&atilde;o tem data. Quando tiver, ela ser&aacute; publicada aqui. Enquanto isso h&aacute; tr&ecirc;s coisas abertas para voc&ecirc; hoje, e nenhuma delas exige que voc&ecirc; conte nada a ningu&eacute;m.</p>'
             '<p><b>Leia Marcos.</b> &Eacute; o mais curto dos quatro relatos, cerca de noventa minutos do come&ccedil;o ao fim. Leia como leria o relato de qualquer pessoa sobre algu&eacute;m que conheceu e n&atilde;o conseguiu esquecer.</p>'
             '<p><b>Experimente cinco minutos.</b> Num lugar quieto, diga com clareza o que de fato se passa com voc&ecirc;, inclusive que n&atilde;o tem certeza de que algu&eacute;m esteja ouvindo. Isso &eacute; uma ora&ccedil;&atilde;o de verdade. &Eacute; onde quase todo mundo come&ccedil;a, e n&atilde;o compromete voc&ecirc; a nada.</p>'
             '<p><b>Tenha uma conversa honesta.</b> Com algu&eacute;m que n&atilde;o v&aacute; encenar uma certeza que n&atilde;o tem. Uma dessas vale mais que qualquer curso, incluindo este.</p>'
             '<p>E se nada disso lhe atrai, essa tamb&eacute;m &eacute; uma resposta v&aacute;lida. Aqui nada precisa que voc&ecirc; decida nada hoje.</p>'),
}
# The waitlist block goes in here once there is an address and a date.
SLOT = ('\n          <!-- WAITLIST SLOT: when a contact address and a start date exist,\n'
        '               replace the first paragraph above with the capture block. -->')
m = re.search(r'<article id="enc-offer".*?\n      </article>', s, re.S)
offer = m.group(0)
new_offer = offer
for cls, (head, paras) in NEXTSTEP.items():
    block = (f'\n          <div class="nextstep">\n            <h4>{head}</h4>\n'
             f'            {paras}\n          </div>' +
             (SLOT if cls == "l-en" else ""))
    # close of the .body div inside this language pane
    pat = rf'(<div class="{cls}">.*?)(\n          </div>\n        </div>)'
    new_offer, n = re.subn(pat, lambda mm, b=block: mm.group(1) + b + mm.group(2),
                           new_offer, count=1, flags=re.S)
    assert n == 1, f"next-step insert failed for {cls}"
s = s.replace(offer, new_offer)
print("A2  Encounter gained a real next step in all three languages")

# ================================================================ A3 / A4 / B3
s = once(
    r'          <h2>Marginalia, the word</h2>',
    lambda m: '''          <h2>Who makes this</h2>
          <p>Marginalia is written by Irwin Ortega. The method it runs on is the inductive exegetical procedure taught in the biblical exposition and exegesis practicum sequence at Life Pacific University, worked station by station over every passage before a word of the public piece is written.</p>
          <p>That is the whole of the qualification and it is stated plainly for the same reason everything else here is, so that you can weigh it. The scholarship this site leans on is not mine. It is named on every page, and where the people who produced it disagree with each other, the disagreement is printed rather than resolved quietly in my favour.</p>

          <h2>Marginalia, the word</h2>''', s)

s = once(
    r'          <h2>A note on the voice</h2>',
    lambda m: '''          <h2>Corrections</h2>
          <p>If something here is wrong it should be fixed, not defended. A site that labels its own confidence levels has no business being precious about a mistake, and the corrections that have been made are noted on <a href="#colophon/col-status" data-xsec="colophon" data-xart="col-status">the status page</a>.</p>
          <!-- CONTACT SLOT: publish the address here and in col-coming once it exists. -->
          <p>A contact address for corrections and questions is being set up and will be published here. Until it is, this is a genuine gap, and it is listed as one.</p>

          <h2>Where else this lives</h2>
          <!-- CHANNEL SLOT: Instagram handle and newsletter link go here when chosen. -->
          <p>Short pieces drawn from the same research are planned for an Instagram account, and a newsletter after that. Neither is open yet. Both will be linked from this page when they are, and not before.</p>

          <h2>A note on the voice</h2>''', s)
print("A3/A4  byline, corrections and channel slots added to the Colophon")

s = once(
    r'(<article id="col-status".*?)<div class="body">\n.*?\n        </div>\n(      </article>)',
    lambda m: m.group(1) + '''<div class="body">
          <h2>Finished</h2>
          <ul class="plain">
            <li><b>Reflections.</b> All fifteen sermons are up, each printed with the exegetical apparatus it rests on.</li>
            <li><b>Provenance.</b> Ten studies, each drawn from a full exegesis worksheet.</li>
            <li><b>Roots.</b> The method and five word studies.</li>
            <li><b>Encounter.</b> All four stages, the unit progression, the session shape and the plain-language presentation. Complete as a description of the pathway.</li>
          </ul>

          <h2>In progress</h2>
          <ul class="plain">
            <li><b>Translation.</b> The navigation, Encounter, Roots and Wonder are in English, Spanish and Portuguese. Reflections and Provenance are English only, and each entry says so when you switch languages rather than quietly showing you the wrong thing.</li>
            <li><b>Portuguese.</b> The Portuguese has not been read by a native speaker. Treat it as a working draft.</li>
            <li><b>Roots.</b> More word studies exist as finished worksheets than are published here.</li>
          </ul>

          <h2>Not started</h2>
          <ul class="plain">
            <li><b>The Wonder curriculum.</b> The approach, the age bands and one worked sample are written. The curriculum is not, and it should not be built until a proper review of the existing children&rsquo;s material has been done. See <a href="#colophon/col-coming" data-xsec="colophon" data-xart="col-coming">what is coming</a>.</li>
            <li><b>A contact address, an Instagram account and a newsletter.</b> All three are named on <a href="#colophon/col-method" data-xsec="colophon" data-xart="col-method">How the work is done</a> as gaps rather than as things that exist.</li>
          </ul>

          <h2>Corrections made</h2>
          <ul class="plain">
            <li><b>7 September 2026.</b> The confidence labels were being used with eight different names against a legend that defined three. They are now five, defined once, and applied everywhere.</li>
            <li><b>7 September 2026.</b> Twelve Reflections were published without the standing line that says where each claim sits. They have it now.</li>
            <li><b>7 September 2026.</b> A claim about how many times the King James renders <i>Sheol</i> as &ldquo;hell&rdquo; is quoted everywhere as thirty-one. It is not printed here, because it has not been checked against a concordance. See <a href="#roots/roots-sheol" data-xsec="roots" data-xart="roots-sheol">Hell</a>.</li>
          </ul>

          <h2>What this site is not, yet</h2>
          <p>It has no home of its own. It is one HTML file, and it is shared by link rather than published at an address. That is a deliberate stage, not an oversight, but it is worth knowing when you are deciding how much weight to put on it.</p>
        </div>
''' + m.group(2), s, re.S)
print("B3  status page rewritten and made accurate")

p.write_text(s, encoding="utf-8")
print(f"\nmarginalia.html {before} -> {len(s)} bytes")
