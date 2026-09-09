#!/usr/bin/env python3
"""Build a deployable static site from marginalia.html.

marginalia.html stays the single source of truth. This script wraps it in a
real document and, alongside it, writes one crawlable page per article.

Why this exists. On the artifact host the page has no <head> of its own, so
there are no link previews, no canonical URLs, no favicon and no way for a
search engine to see anything but a single page. Everything here is output;
dist/ is not committed.

    python3 build_site.py            # -> dist/
    python3 -m http.server -d dist   # look at it

Set the domain once it exists:

    MARGINALIA_URL=https://example.org python3 build_site.py
"""
import html as html_mod
import os
import re
import shutil
import sys
from pathlib import Path

SRC = Path("marginalia.html")
OUT = Path("dist")
SITE = os.environ.get("MARGINALIA_URL", "").rstrip("/")
# A GitHub project site is served from /<repo>/, not the domain root, so every
# link and asset needs that prefix. Empty for a custom domain at the root.
BASE = "/" + os.environ.get("MARGINALIA_BASE", "").strip("/") if os.environ.get("MARGINALIA_BASE", "").strip("/") else ""

SECTIONS = ["reflections", "encounter", "roots", "provenance", "wonder", "colophon"]
TAB_ORDER = ["reflections", "encounter", "roots", "provenance", "colophon"]
LABEL = {s: s.capitalize() for s in SECTIONS}

TAGLINE = "Reading the text closely, and saying it plainly."
BLURB = {
    "reflections": "Sermons, printed with the exegetical work they rest on.",
    "encounter": "A four-stage pathway into following Jesus, in plain language.",
    "roots": "Word studies: what a word carried before English got hold of it.",
    "provenance": "Where these texts came from, and how we know.",
    "wonder": "The same honesty, for children.",
    "colophon": "Who makes this, how it is made, and what is still missing.",
}


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def match_element(s, start, tag):
    """Index just past the element opening at `start`, counting nesting."""
    open_re = re.compile(r"<%s\b" % tag, re.I)
    close = "</%s>" % tag
    depth, i = 0, start
    while i < len(s):
        nxt_open = open_re.search(s, i)
        nxt_close = s.find(close, i)
        if nxt_close < 0:
            sys.exit("unclosed <%s>" % tag)
        if nxt_open and nxt_open.start() < nxt_close:
            depth += 1
            i = nxt_open.end()
        else:
            depth -= 1
            i = nxt_close + len(close)
            if depth == 0:
                return i
    sys.exit("unclosed <%s>" % tag)


def strip_tags(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_mod.unescape(text)).strip()


def parse(source):
    style = source[source.index("<style>"):source.index("</style>") + len("</style>")]
    m_start = source.index('<div class="masthead">')
    nav_start = source.index('<nav class="sectionbar"')
    nav_end = source.index("</nav>", nav_start) + len("</nav>")
    script = source[source.index("<script>"):]

    views = {}
    for name in SECTIONS:
        i = source.find('id="view-%s"' % name)
        if i < 0:
            continue
        start = source.rfind("<div", 0, i)
        views[name] = source[start:match_element(source, start, "div")]

    footer = ""
    f = source.find('<footer')
    if f < 0:
        f = source.find('class="siteftr"')
        if f >= 0:
            f = source.rfind("<", 0, f)
    if f >= 0:
        tag = re.match(r"<(\w+)", source[f:]).group(1)
        footer = source[f:match_element(source, f, tag)]

    return {
        "style": style,
        "masthead": source[m_start:nav_start],
        "nav": source[nav_start:nav_end],
        "views": views,
        "script": script,
        "footer": footer,
    }


def articles_in(view_html):
    """[(id, html)] in document order."""
    out = []
    for m in re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>', view_html):
        start = view_html.rfind("\n", 0, m.start()) + 1
        if view_html[start:m.start()].strip():
            start = m.start()
        out.append((m.group(1), view_html[start:match_element(view_html, m.start(), "article")]))
    return out


def english(fragment):
    """The English pane of an article, or the whole thing when it has no panes."""
    m = re.search(r'<div class="l-en">', fragment)
    if not m:
        return fragment
    return fragment[m.start():match_element(fragment, m.start(), "div")]


def title_of(article_html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", english(article_html), re.S)
    return strip_tags(m.group(1)) if m else "Marginalia"


def description_of(article_html, section):
    pane = english(article_html)
    for pattern in (r'<p class="epigraph">(.*?)</p>',
                    r'<div class="body">.*?<p>(.*?)</p>'):
        m = re.search(pattern, pane, re.S)
        if m:
            text = strip_tags(m.group(1))
            if len(text) > 30:
                return text[:157].rsplit(" ", 1)[0] + "…" if len(text) > 160 else text
    return BLURB.get(section, TAGLINE)


# --------------------------------------------------------------------------
# rewriting for static pages
# --------------------------------------------------------------------------

def url(section=None, art=None):
    """A site-absolute link, base path included."""
    if section is None:
        return BASE + "/"
    return BASE + ("/%s/" % section if art is None else "/%s/%s/" % (section, art))


def asset(path):
    """A site-absolute link to a built file, e.g. /og/roots/meek.png."""
    return BASE + path


def rewrite_links(fragment):
    """SPA hash links become real paths, so a crawler and a middle click work."""
    fragment = re.sub(r'href="#([a-z]+)/([A-Za-z0-9_-]+)"',
                      lambda m: 'href="%s"' % url(m.group(1), m.group(2)), fragment)
    fragment = re.sub(r'href="#([a-z]+)"',
                      lambda m: 'href="%s"' % url(m.group(1)), fragment)
    return fragment


def static_nav(nav_html, current):
    """Turn the tab buttons into links and the live search box into a link."""
    def as_link(m):
        section = m.group("section")
        label = m.group("label")
        cur = ' aria-current="true"' if section == current else ""
        return '<a class="tab" href="%s"%s>%s</a>' % (url(section), cur, label)

    nav = re.sub(
        r'<button class="tab"[^>]*data-section="(?P<section>[a-z]+)"[^>]*>(?P<label>[^<]*)</button>',
        as_link, nav_html)

    nav = re.sub(r'<div class="searchwrap">.*?</div>',
                 '<div class="searchwrap"><a class="tab" href="%s">'
                 '<span class="l-en">Search</span><span class="l-es">Buscar</span>'
                 '<span class="l-pt">Buscar</span></a></div>' % url(),
                 nav, flags=re.S)
    return rewrite_links(nav)


def static_masthead(masthead_html):
    return masthead_html.replace(
        '<span class="brand">Marginalia</span>',
        '<a class="brand" href="%s">Marginalia</a>' % url()
    ).replace(
        '<button class="toggle" id="themeBtn" type="button">Dark</button>',
        '<button class="toggle" id="themeBtn" type="button">Dark</button>')


def one_article_view(view_html, keep_id):
    """The section view with every article but `keep_id` removed."""
    out = view_html
    for aid, art in articles_in(view_html):
        if aid != keep_id:
            out = out.replace(art, "", 1)
    shown = re.sub(r'(<article\b[^>]*\bid="%s"[^>]*)\shidden' % re.escape(keep_id),
                   r"\1", out, count=1)
    return rewrite_links(shown)


# --------------------------------------------------------------------------
# document shell
# --------------------------------------------------------------------------

STATIC_JS = """
<script>
  (function(){
    var root = document.documentElement;
    function sysDark(){ return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches); }
    function cur(){ var t = root.getAttribute('data-theme'); return t ? t : (sysDark() ? 'dark' : 'light'); }
    var btn = document.getElementById('themeBtn');
    try{ var s = localStorage.getItem('marginalia-theme');
         if(s === 'dark' || s === 'light') root.setAttribute('data-theme', s); }catch(e){}
    function paint(){ if(btn) btn.textContent = cur() === 'dark' ? 'Light' : 'Dark'; }
    paint();
    if(btn) btn.addEventListener('click', function(){
      var next = cur() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try{ localStorage.setItem('marginalia-theme', next); }catch(e){}
      paint();
    });

    var picker = document.querySelector('.langpick');
    if(picker) picker.hidden = false;
    function setLang(l){
      root.setAttribute('data-elang', l);
      root.setAttribute('lang', l);
      try{ localStorage.setItem('marginalia-lang', l); }catch(e){}
      Array.prototype.forEach.call(document.querySelectorAll('.langpick button'), function(b){
        b.setAttribute('aria-current', b.dataset.lang === l ? 'true' : 'false');
      });
    }
    var saved = 'en';
    try{ var v = localStorage.getItem('marginalia-lang');
         if(v === 'es' || v === 'pt' || v === 'en') saved = v; }catch(e){}
    setLang(saved);
    Array.prototype.forEach.call(document.querySelectorAll('.langpick button'), function(b){
      b.addEventListener('click', function(){ setLang(b.dataset.lang); });
    });
    document.addEventListener('click', function(e){
      var t = e.target.closest ? e.target.closest('[data-setlang]') : null;
      if(t){ e.preventDefault(); setLang(t.getAttribute('data-setlang')); }
    });
  })();
</script>
"""

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='6' fill='%231c1a17'/%3E"
    "%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='20' "
    "fill='%23e8e2d6' text-anchor='middle'%3EM%3C/text%3E%3C/svg%3E"
)


def document(*, title, description, canonical, body, style, image, accent, noindex=False):
    full_title = title if title == "Marginalia" else "%s · Marginalia" % title
    abs_url = (SITE + canonical) if SITE else canonical
    abs_img = (SITE + image) if SITE and image else (image or "")
    esc = html_mod.escape

    head = [
        '<!doctype html>',
        '<html lang="en" data-elang="en" data-accent="%s">' % accent,
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s</title>' % esc(full_title),
        '<meta name="description" content="%s">' % esc(description),
        '<link rel="icon" href="%s">' % FAVICON,
        '<meta name="color-scheme" content="light dark">',
    ]
    if noindex:
        head.append('<meta name="robots" content="noindex,follow">')
    if SITE:
        head.append('<link rel="canonical" href="%s">' % esc(abs_url))
    head += [
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="Marginalia">',
        '<meta property="og:title" content="%s">' % esc(full_title),
        '<meta property="og:description" content="%s">' % esc(description),
    ]
    if SITE:
        head.append('<meta property="og:url" content="%s">' % esc(abs_url))
    if abs_img:
        head += ['<meta property="og:image" content="%s">' % esc(abs_img),
                 '<meta property="og:image:width" content="1200">',
                 '<meta property="og:image:height" content="630">']
    head += [
        '<meta name="twitter:card" content="%s">' % ("summary_large_image" if abs_img else "summary"),
        '<meta name="twitter:title" content="%s">' % esc(full_title),
        '<meta name="twitter:description" content="%s">' % esc(description),
    ]
    if abs_img:
        head.append('<meta name="twitter:image" content="%s">' % esc(abs_img))
    head += [style, '</head>', '<body>', body, '</body>', '</html>', '']
    return "\n".join(head)


# --------------------------------------------------------------------------
# og images
# --------------------------------------------------------------------------

def og_image(title, section, path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    serif = next((f for f in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
                              "/System/Library/Fonts/NewYork.ttf",
                              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
                  if Path(f).exists()), None)
    if not serif:
        return False

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (28, 26, 23))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=(176, 141, 87))

    big = ImageFont.truetype(serif, 66)
    small = ImageFont.truetype(serif, 30)

    words, lines, line = title.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if d.textlength(trial, font=big) > W - 200 and line:
            lines.append(line)
            line = w
        else:
            line = trial
    lines.append(line)
    lines = lines[:4]

    d.text((100, 92), "MARGINALIA", font=small, fill=(176, 141, 87))
    y = 210
    for ln in lines:
        d.text((100, y), ln, font=big, fill=(232, 226, 214))
        y += 84
    d.text((100, H - 96), LABEL.get(section, "Marginalia"), font=small, fill=(150, 143, 130))

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return True


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def main():
    if not SRC.exists():
        sys.exit("run this from the repo root")
    source = SRC.read_text(encoding="utf-8")
    p = parse(source)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    if not SITE:
        print("note: MARGINALIA_URL is not set, so canonical and og:url are "
              "omitted and no sitemap is written.\n"
              "      Set it when the site has an address.\n")
    if BASE:
        print(f"base path: {BASE}\n")

    pages = []          # (path, url, changefreq, priority)
    images_made = 0

    # ---- the app itself, unchanged apart from a real <head> ---------------
    app_body = "\n".join([p["masthead"], p["nav"],
                          *[p["views"][s] for s in SECTIONS if s in p["views"]]])
    app_body = source[source.index('<div class="masthead">'):source.index("<script>")]
    if og_image("Marginalia", "reflections", OUT / "og" / "site.png"):
        images_made += 1
        site_img = asset("/og/site.png")
    else:
        site_img = ""
    (OUT / "index.html").write_text(document(
        title="Marginalia",
        description=TAGLINE + " Sermons with their exegetical apparatus, word "
                              "studies, and text histories.",
        canonical=url(), body=app_body + "\n" + p["script"],
        style=p["style"], image=site_img, accent="reflections"), encoding="utf-8")
    pages.append((url(), "weekly", "1.0"))

    # ---- one page per article --------------------------------------------
    for section in SECTIONS:
        view = p["views"].get(section)
        if not view:
            continue
        arts = articles_in(view)

        for aid, art in arts:
            title = title_of(art)
            desc = description_of(art, section)
            img_path = "og/%s/%s.png" % (section, aid)
            if og_image(title, section, OUT / img_path):
                images_made += 1
                img = asset("/" + img_path)
            else:
                img = site_img

            body = "\n".join([
                static_masthead(p["masthead"]),
                static_nav(p["nav"], section),
                one_article_view(view, aid),
                rewrite_links(p["footer"]),
                STATIC_JS,
            ])
            page = OUT / section / aid / "index.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(document(
                title=title, description=desc, canonical=url(section, aid),
                body=body, style=p["style"], image=img, accent=section),
                encoding="utf-8")
            pages.append((url(section, aid), "monthly", "0.8"))

        # ---- a section index that is just its contents list ---------------
        body = "\n".join([
            static_masthead(p["masthead"]),
            static_nav(p["nav"], section),
            re.sub(r"<main\b.*?</main>", "", rewrite_links(view), flags=re.S),
            rewrite_links(p["footer"]),
            STATIC_JS,
        ])
        page = OUT / section / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(document(
            title=LABEL[section], description=BLURB[section],
            canonical=url(section), body=body, style=p["style"],
            image=site_img, accent=section), encoding="utf-8")
        pages.append((url(section), "monthly", "0.6"))

    # ---- sitemap, robots, headers ----------------------------------------
    if SITE:
        urls = "\n".join(
            "  <url><loc>%s%s</loc><changefreq>%s</changefreq>"
            "<priority>%s</priority></url>" % (SITE, loc, freq, pri)
            for loc, freq, pri in pages)
        (OUT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n", encoding="utf-8")
        (OUT / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE, encoding="utf-8")
    else:
        (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")

    # GitHub Pages would otherwise treat this as a Jekyll site and drop
    # anything whose name starts with an underscore.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Cloudflare Pages and Netlify read this; GitHub Pages ignores it, and
    # serves the site without custom headers.
    (OUT / "_headers").write_text(
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "\n"
        "/og/*\n"
        "  Cache-Control: public, max-age=604800\n", encoding="utf-8")

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"dist/  {len(pages)} pages, {images_made} preview images, "
          f"{total / 1_000_000:.1f} MB")
    print("       python3 -m http.server -d dist 8000")


if __name__ == "__main__":
    main()
