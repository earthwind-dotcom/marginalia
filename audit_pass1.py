#!/usr/bin/env python3
"""Audit pass 1 — chrome, styles, behaviour.

Mechanical fixes plus the CSS and JS the content pass needs:
C1 stray markdown rules · B1 confidence-label vocabulary · B2 Standing lines ·
A5 dates · B4 footer · D1 Wonder out of the primary nav · C2 languages back on ·
C4 accessibility · C5 search · C6 print.
"""
import re
from pathlib import Path

p = Path("marginalia.html")
s = p.read_text(encoding="utf-8")
before = len(s)


def once(pattern, repl, text, flags=0, expect=1):
    text, n = re.subn(pattern, repl, text, flags=flags)
    assert n == expect, f"expected {expect} replacement(s), made {n}: {pattern[:60]}"
    return text


# ---------------------------------------------------------------- C1
# build_reflections.py passed markdown horizontal rules straight through.
s, n = re.subn(r"\n\s*<p>---</p>", "", s)
print(f"C1  removed {n} stray markdown rules")

# ---------------------------------------------------------------- B1
# Eight ad-hoc labels collapse to five defined ones.
LABELS = {
    "One major view": "Debated",
    "Contested": "Debated",
    "Majority": "Strong majority",
}
for old, new in LABELS.items():
    s, n = re.subn(rf'(class="conf">){re.escape(old)}(<)', rf"\1{new}\2", s)
    if n:
        print(f"B1  {old} -> {new} ({n})")

# ---------------------------------------------------------------- B2
# Only the three hand-built Reflections carried a Standing line.
STANDING = {
    "whose-world": "Genesis 1 read against ANE cosmology [consensus] &middot; a direct rebuttal of <i>Enuma Elish</i> [debated] &middot; <i>tehom</i> borrowed from Tiamat [rejected]",
    "frame": "<i>raqia&#703;</i> understood as a solid dome [consensus] &middot; the ANE three-tier cosmos [consensus] &middot; Genesis describes rather than defends it [our read]",
    "verse-bent": "the curse falls on Canaan, not Ham [consensus] &middot; the racial reading is a later construction [consensus] &middot; the nature of Ham&rsquo;s offence [debated]",
    "moabite": "Ezra&ndash;Nehemiah dissolved foreign marriages [consensus] &middot; Ruth and Jonah as canonical counter-voices [strong majority] &middot; written to answer Ezra [debated]",
    "two-drafts": "Chronicles rewrites Samuel&ndash;Kings with a consistent tendency [consensus] &middot; <i>&#347;&#257;&#7789;&#257;n</i> as a proper name in 1 Chr 21:1 [debated]",
    "rule-breaks": "Job 21 denies strict retribution [consensus] &middot; Proverbs&rsquo; sayings were never guarantees [consensus] &middot; the wisdom books as a preserved debate [strong majority]",
    "third-way": "the passage rejects retaliation in kind [consensus] &middot; the three examples are active, not passive [strong majority] &middot; Wink&rsquo;s specific reconstructions [debated]",
    "life-age": "<i>ai&#333;nios</i> often means &ldquo;of the Age to Come&rdquo; [consensus] &middot; it also carries &ldquo;unending&rdquo; [consensus] &middot; the duration of final punishment [debated]",
    "luke-checked": "the Gospels are textually anonymous [consensus] &middot; the traditional names are the only ones attested [consensus] &middot; whether the names were attached late [debated]",
    "couldnt-lose": "not part of John&rsquo;s original text [consensus] &middot; preserves genuine early Jesus tradition [strong majority] &middot; still Scripture, as most traditions hold [our read]",
    "dead-rise": "<i>apant&#275;sis</i> pictures a welcoming party, not an evacuation [strong majority] &middot; one public parousia [strong majority] &middot; the pretrib system is 19th-century [consensus]",
    "church-shape": "the Pastorals describe a more structured church than the undisputed seven [consensus] &middot; non-Pauline authorship [strong majority] &middot; Pauline authorship via a secretary [debated]",
}
for art_id, line in STANDING.items():
    pat = rf'(<article id="{art_id}".*?<span><k>Reading</k>[^<]*</span>\n)'
    s = once(pat, rf'\1          <span class="wide"><k>Standing</k>{line}</span>\n',
             s, re.S)
print(f"B2  added Standing to {len(STANDING)} Reflections")

# ---------------------------------------------------------------- B4
# "a working mock-up" was status, not identity. It moves to the Colophon.
s = once(
    r'<span class="l-en">Marginalia &middot; a working mock-up &middot;[^<]*</span>',
    '<span class="l-en">Marginalia &middot; Reflections &middot; Encounter &middot; Roots '
    '&middot; Provenance &middot; Wonder &middot; Colophon<br>Revised 7 September 2026 '
    '&middot; <a href="#colophon/col-status" data-xsec="colophon" data-xart="col-status">'
    'what is finished and what is not</a></span>', s)
s = once(
    r'<span class="l-es">Marginalia &middot; una maqueta de trabajo &middot;[^<]*</span>',
    '<span class="l-es">Marginalia &middot; Reflections &middot; Encounter &middot; Roots '
    '&middot; Provenance &middot; Wonder &middot; Colophon<br>Revisado el 7 de septiembre '
    'de 2026 &middot; <a href="#colophon/col-status" data-xsec="colophon" '
    'data-xart="col-status">qu&eacute; est&aacute; terminado y qu&eacute; no</a></span>', s)
s = once(
    r'<span class="l-pt">Marginalia &middot; uma maquete de trabalho &middot;[^<]*</span>',
    '<span class="l-pt">Marginalia &middot; Reflections &middot; Encounter &middot; Roots '
    '&middot; Provenance &middot; Wonder &middot; Colophon<br>Revisado em 7 de setembro '
    'de 2026 &middot; <a href="#colophon/col-status" data-xsec="colophon" '
    'data-xart="col-status">o que est&aacute; pronto e o que n&atilde;o est&aacute;</a></span>', s)
print("B4  footer restated with a revision date")

# ---------------------------------------------------------------- D1
# Wonder keeps its section, URL and accent but leaves the primary tab row
# until the review of existing children's material has been done.
s = once(r'\s*<button class="tab" type="button" data-section="wonder">Wonder</button>', "", s)
print("D1  Wonder removed from the tab row (still reachable at #wonder)")

# ---------------------------------------------------------------- C5 / a11y markup
s = once(r'<nav class="sectionbar" aria-label="Sections">\n  <div class="tabs">',
         '<nav class="sectionbar" aria-label="Sections">\n  <div class="tabs" role="tablist">', s)
s, n = re.subn(r'<button class="tab" type="button"', '<button class="tab" type="button" role="tab"', s)
print(f"C4  tablist roles on {n} tabs")

s = once(r'(<div class="langpick" hidden>)',
         '''<div class="searchwrap">
    <input id="q" type="search" autocomplete="off" spellcheck="false"
           aria-label="Search Marginalia" placeholder="Search">
  </div>
  \\1''', s)
s = once(r'(<footer class="siteftr">)',
         '''<div class="view" id="view-search" hidden>
  <div class="wrap wrap-wide">
    <main>
      <h1 id="qhead">Search</h1>
      <p class="lede" id="qcount"></p>
      <div id="qresults"></div>
    </main>
  </div>
</div>

\\1''', s)
print("C5  search field and results view added")

# ---------------------------------------------------------------- CSS
CSS = """
  /* ---------- entry date (A5) ---------- */
  .entrydate{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.66rem;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:var(--faint);
    text-indent:0;
    margin:0 0 1.6rem;
  }

  /* ---------- cross references (A1) ---------- */
  .xref{
    margin:2.8rem 0 0;
    padding:1.15rem 1.4rem 1.25rem;
    border:1px solid var(--rule);
    border-radius:2px;
  }
  .xref h4{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.66rem;
    font-weight:500;
    letter-spacing:.18em;
    text-transform:uppercase;
    color:var(--faint);
    margin:0 0 .85rem;
  }
  .xref ul{list-style:none;margin:0;padding:0}
  .xref li{padding:.32rem 0;text-indent:0;line-height:1.45}
  .xref .sec{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.62rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:var(--faint);
    display:inline-block;
    min-width:9.2em;
  }
  .xref a{font-size:.99rem}
  .xref .why{
    margin:.9rem 0 0;
    font-style:italic;
    font-size:.9rem;
    line-height:1.5;
    color:var(--faint);
    text-indent:0;
  }

  /* ---------- next step (A2) ---------- */
  .nextstep{
    margin:2.8rem 0 0;
    padding:1.5rem 1.7rem 1.6rem;
    background:var(--accent-soft);
    border:1px solid var(--rule);
    border-radius:2px;
  }
  .nextstep h4{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.66rem;
    font-weight:500;
    letter-spacing:.18em;
    text-transform:uppercase;
    color:var(--accent);
    margin:0 0 .9rem;
  }
  .nextstep p{text-indent:0;font-size:.99rem;line-height:1.55;color:var(--ink-soft);margin:0}
  .nextstep p + p{margin-top:.7em}

  /* ---------- untranslated notice (C2) ---------- */
  .xlate{
    margin:0 0 2rem;
    padding:.85rem 1.1rem;
    border:1px dashed var(--rule);
    border-radius:2px;
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.72rem;
    line-height:1.65;
    color:var(--faint);
    text-indent:0;
  }
  :root:not([data-elang="es"]):not([data-elang="pt"]) .xlate{display:none}

  /* ---------- search (C5) ---------- */
  .searchwrap{display:flex;align-items:center;padding-bottom:8px}
  .searchwrap input{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.7rem;
    letter-spacing:.08em;
    color:var(--ink);
    background:none;
    border:1px solid var(--rule);
    border-radius:2px;
    padding:5px 9px;
    width:11rem;
    max-width:40vw;
  }
  .searchwrap input::placeholder{color:var(--faint);text-transform:uppercase;letter-spacing:.14em}
  .searchwrap input:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--faint)}
  .wrap-wide{grid-template-columns:1fr}
  .wrap-wide main{max-width:var(--measure)}
  .qhit{
    display:block;
    padding:1rem 0;
    border-top:1px solid var(--rule);
    text-indent:0;
  }
  .qhit .sec{
    font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
    font-size:.62rem;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:var(--accent);
    display:block;
    margin-bottom:.2rem;
  }
  .qhit .t{display:block;font-size:1.12rem;line-height:1.3;color:var(--ink)}
  .qhit:hover .t{color:var(--accent)}
  .qhit .snip{
    display:block;
    margin-top:.3rem;
    font-size:.93rem;
    line-height:1.5;
    color:var(--ink-soft);
  }
  .qhit .snip b{color:var(--ink);background:var(--accent-soft);font-weight:500}

  /* ---------- print (C6) ---------- */
  @media print{
    .masthead .toggle,.sectionbar,.sectionnote,.contents,.siteftr,
    .xref,.availability,.xlate,#view-search{display:none!important}
    body{background:#fff;color:#000;font-size:11pt;line-height:1.5}
    .wrap{display:block;padding:0;max-width:none}
    main{max-width:none;padding:0}
    .masthead{padding:0 0 12pt;border-bottom:1px solid #999}
    article[hidden]{display:none!important}
    h1{font-size:20pt}
    .body h2{page-break-after:avoid;font-size:13pt}
    .pull{font-size:12pt;page-break-inside:avoid}
    .apparatus{page-break-inside:avoid;background:none;border:1px solid #999;margin-top:18pt}
    .epigraph,.apphead,.entrydate{color:#000}
    a{color:#000;text-decoration:none}
  }
"""
s = once(r"\n</style>", CSS + "</style>", s)
print("CSS added: xref, next-step, translation notice, search, print")

# ---------------------------------------------------------------- JS
NEW_JS = """
  (function(){
    var root = document.documentElement;

    /* ---------------- theme ---------------- */
    var themeBtn = document.getElementById('themeBtn');
    function sysDark(){ return window.matchMedia('(prefers-color-scheme: dark)').matches; }
    function curTheme(){ var t = root.getAttribute('data-theme'); return t ? t : (sysDark() ? 'dark' : 'light'); }
    function paintTheme(){ themeBtn.textContent = curTheme() === 'dark' ? 'Light' : 'Dark'; }
    try{
      var savedTheme = localStorage.getItem('marginalia-theme');
      if(savedTheme === 'dark' || savedTheme === 'light') root.setAttribute('data-theme', savedTheme);
    }catch(e){}
    paintTheme();
    themeBtn.addEventListener('click', function(){
      var next = curTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try{ localStorage.setItem('marginalia-theme', next); }catch(e){}
      paintTheme();
    });

    /* ---------------- language ----------------
       Entries with no .l-es / .l-pt block stay in English and carry a
       translated .xlate notice saying so, so partial coverage degrades
       honestly instead of blanking the page. */
    var LANGS_ENABLED = true;

    var langpick = document.querySelector('.langpick');
    var langBtns = Array.prototype.slice.call(document.querySelectorAll('.langpick button'));
    function curLang(){
      var l = root.getAttribute('data-elang');
      return (l === 'es' || l === 'pt') ? l : 'en';
    }
    function paintLang(){
      langBtns.forEach(function(b){
        b.setAttribute('aria-current', b.dataset.lang === curLang() ? 'true' : 'false');
      });
      root.setAttribute('lang', curLang());
    }
    function setLang(lang){
      root.setAttribute('data-elang', lang);
      try{ localStorage.setItem('marginalia-lang', lang); }catch(e){}
      paintLang();
      buildIndex();
    }
    if(LANGS_ENABLED){
      try{
        var savedLang = localStorage.getItem('marginalia-lang');
        if(savedLang === 'es' || savedLang === 'pt' || savedLang === 'en') root.setAttribute('data-elang', savedLang);
      }catch(e){}
      if(langpick) langpick.hidden = false;
      langBtns.forEach(function(b){
        b.addEventListener('click', function(){ setLang(b.dataset.lang); });
      });
      document.addEventListener('click', function(e){
        var t = e.target.closest ? e.target.closest('[data-setlang]') : null;
        if(t){ e.preventDefault(); setLang(t.getAttribute('data-setlang')); }
      });
    }
    if(!LANGS_ENABLED || !root.getAttribute('data-elang')) root.setAttribute('data-elang', 'en');
    paintLang();

    /* ---------------- per-view article swapping ---------------- */
    var LABEL = {
      reflections:'Reflections', encounter:'Encounter', roots:'Roots',
      provenance:'Provenance', wonder:'Wonder', colophon:'Colophon'
    };

    function makeSwapper(view){
      var items = Array.prototype.slice.call(view.querySelectorAll('.toc-item'));
      var articles = Array.prototype.slice.call(view.querySelectorAll('main > article'));
      function show(id, focus){
        var match = null;
        articles.forEach(function(a){ if(a.id === id) match = a; });
        if(!match) match = articles[0];
        if(!match) return null;
        articles.forEach(function(a){
          var on = a === match;
          a.hidden = !on;
          if(on){
            a.style.opacity = '0';
            requestAnimationFrame(function(){ a.style.opacity = '1'; });
          }
        });
        items.forEach(function(t){
          t.setAttribute('aria-current', t.dataset.target === match.id ? 'true' : 'false');
        });
        /* move focus to the heading so a screen reader hears the change */
        if(focus){
          var h = match.querySelector('h1');
          if(h){ h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); }
        }
        return match.id;
      }
      items.forEach(function(t){
        t.addEventListener('click', function(e){
          e.preventDefault();
          var id = show(t.dataset.target, true);
          setHash(view.dataset.section, id);
          window.scrollTo(0, 0);
        });
      });
      return show;
    }

    var order = ['reflections','encounter','roots','provenance','wonder','colophon'];
    var views = {};
    var swap = {};
    order.forEach(function(name){
      var v = document.getElementById('view-' + name);
      if(v){
        views[name] = v;
        swap[name] = makeSwapper(v);
        var m = v.querySelector('main');
        if(m){ m.setAttribute('role','tabpanel'); m.setAttribute('aria-live','polite'); }
      }
    });

    var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
    var searchView = document.getElementById('view-search');

    function setHash(section, article){
      try{ history.replaceState(null, '', '#' + section + (article ? '/' + article : '')); }catch(e){}
    }

    function showSection(section, article, scroll, focus){
      if(!views[section]) section = 'reflections';
      if(searchView) searchView.hidden = true;
      root.setAttribute('data-accent', section);
      order.forEach(function(name){
        if(views[name]) views[name].hidden = name !== section;
      });
      tabs.forEach(function(t){
        t.setAttribute('aria-current', t.dataset.section === section ? 'true' : 'false');
        t.setAttribute('aria-selected', t.dataset.section === section ? 'true' : 'false');
      });
      var id = swap[section](article, focus);
      try{ localStorage.setItem('marginalia-section', section); }catch(e){}
      if(scroll) window.scrollTo(0, 0);
      setHash(section, id);
    }

    tabs.forEach(function(t){
      t.addEventListener('click', function(){ showSection(t.dataset.section, null, true, true); });
    });

    /* ---------------- cross-section links ---------------- */
    document.addEventListener('click', function(e){
      var a = e.target.closest ? e.target.closest('[data-xsec]') : null;
      if(!a) return;
      e.preventDefault();
      showSection(a.getAttribute('data-xsec'), a.getAttribute('data-xart'), true, true);
    });

    /* ---------------- search ---------------- */
    var q = document.getElementById('q');
    var qresults = document.getElementById('qresults');
    var qcount = document.getElementById('qcount');
    var index = [];

    function buildIndex(){
      index = [];
      order.forEach(function(name){
        var v = views[name];
        if(!v) return;
        Array.prototype.slice.call(v.querySelectorAll('main > article')).forEach(function(a){
          /* index only the language actually being shown */
          var lang = curLang();
          var pane = a.querySelector(':scope > .l-' + lang) || a.querySelector(':scope > .l-en') || a;
          var h1 = pane.querySelector('h1');
          index.push({
            section: name,
            id: a.id,
            title: h1 ? h1.textContent.trim() : a.id,
            text: (pane.textContent || '').replace(/\\s+/g, ' ').trim()
          });
        });
      });
    }

    function esc(t){
      return t.replace(/[&<>]/g, function(c){
        return c === '&' ? '&amp;' : c === '<' ? '&lt;' : '&gt;';
      });
    }

    function snippet(text, term){
      var i = text.toLowerCase().indexOf(term);
      if(i < 0) return esc(text.slice(0, 150)) + '&hellip;';
      var start = Math.max(0, i - 70);
      var cut = text.slice(start, i + term.length + 90);
      var at = i - start;
      return (start > 0 ? '&hellip;' : '') + esc(cut.slice(0, at)) +
             '<b>' + esc(cut.slice(at, at + term.length)) + '</b>' +
             esc(cut.slice(at + term.length)) + '&hellip;';
    }

    function runSearch(term){
      term = term.trim().toLowerCase();
      if(term.length < 2){
        showSection(root.getAttribute('data-accent') || 'reflections', null, false, false);
        return;
      }
      if(!index.length) buildIndex();
      var hits = [];
      index.forEach(function(e){
        var lt = e.title.toLowerCase(), lx = e.text.toLowerCase();
        if(lt.indexOf(term) >= 0) hits.push({e:e, rank:0});
        else if(lx.indexOf(term) >= 0) hits.push({e:e, rank:1});
      });
      hits.sort(function(a,b){ return a.rank - b.rank; });

      order.forEach(function(name){ if(views[name]) views[name].hidden = true; });
      tabs.forEach(function(t){
        t.setAttribute('aria-current','false');
        t.setAttribute('aria-selected','false');
      });
      searchView.hidden = false;
      qcount.textContent = hits.length === 0
        ? 'Nothing matches that.'
        : hits.length + (hits.length === 1 ? ' entry' : ' entries');
      qresults.innerHTML = hits.slice(0, 20).map(function(h){
        return '<a class="qhit" href="#' + h.e.section + '/' + h.e.id + '"' +
               ' data-xsec="' + h.e.section + '" data-xart="' + h.e.id + '">' +
               '<span class="sec">' + LABEL[h.e.section] + '</span>' +
               '<span class="t">' + esc(h.e.title) + '</span>' +
               '<span class="snip">' + snippet(h.e.text, term) + '</span></a>';
      }).join('');
    }

    if(q){
      var timer = null;
      q.addEventListener('input', function(){
        clearTimeout(timer);
        timer = setTimeout(function(){ runSearch(q.value); }, 120);
      });
      q.addEventListener('keydown', function(e){
        if(e.key === 'Escape'){ q.value = ''; runSearch(''); q.blur(); }
      });
    }

    /* ---------------- initial route ---------------- */
    var parts = (location.hash || '').replace(/^#/, '').split('/');
    var startSection = parts[0];
    var startArticle = parts[1];
    if(!views[startSection]){
      startArticle = null;
      try{ startSection = localStorage.getItem('marginalia-section') || 'reflections'; }catch(e){ startSection = 'reflections'; }
    }
    showSection(startSection, startArticle, false, false);
    buildIndex();
  })();
"""
s = once(r"<script>\n.*?\n</script>", lambda m: "<script>" + NEW_JS + "</script>", s, re.S)
print("JS replaced: languages on, xref routing, search, focus management")

p.write_text(s, encoding="utf-8")
print(f"\nmarginalia.html {before} -> {len(s)} bytes")
