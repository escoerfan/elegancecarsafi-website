#!/usr/bin/env python3
"""Erzeugt die Blog-Beiträge (blog-<name>.html) und die Galerie-Vorschau auf blog.html.

Quelle: je Beitrag eine Datei _blog/<name>.md (Anleitung: _blog/LIESMICH.md).
Dateien, deren Name mit _ beginnt (z. B. _vorlage.md), und Beiträge mit
"entwurf: ja" werden übersprungen. Der Ordner _blog wird von GitHub Pages
(Jekyll) nicht veröffentlicht.

Je Beitrag:
- blog-<name>.html mit Menü und Footer aus blog.html (bleibt so automatisch
  aktuell), Titelbild oben, Text, weitere Bilder, Bildnachweis
- Bildvarianten (AVIF/WebP/JPG) in assets/img/opt/, falls noch nicht vorhanden
  (Original liegt in assets/img/, benötigt Pillow wie _tools/bilder.py)
- og:type article + article:published_time -> schema.py macht daraus BlogPosting

blog.html: Karten zwischen <!-- blog:start --> und <!-- blog:end -->, neueste
zuerst; ohne Beiträge steht dort der Hinweis „Die ersten Beiträge sind in Arbeit“.
Nicht mehr vorhandene Beiträge (Quelle gelöscht oder wieder Entwurf) werden entfernt.

Aufruf:  python3 _tools/blog.py
Danach:  Übersetzungen prüfen (python3 _tools/i18n_check.py blog.html) – der
Beitragstext selbst bleibt bewusst deutsch (data-no-i18n), wie die Fahrzeugtexte.
"""
import datetime, glob, html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://elegancecarsafi.com/'
SRC_DIR = os.path.join(ROOT, '_blog')
IMG = os.path.join(ROOT, 'assets', 'img')
OPT = os.path.join(IMG, 'opt')
MARK = '<!-- erzeugt von _tools/blog.py – nicht von Hand bearbeiten, Quelle: _blog/%s.md -->'
START, END = '<!-- blog:start -->', '<!-- blog:end -->'
WIDTHS = [960, 1600]
MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
          'September', 'Oktober', 'November', 'Dezember']

EMPTY = '''    <div class="blog-empty reveal">
      <p class="eyebrow">Bald hier</p>
      <h2 class="h2">Die ersten Beiträge sind in Arbeit.</h2>
      <p class="lead">Bis dahin finden Sie viele Antworten in unseren häufigen Fragen und auf den Seiten zu Ankauf und Export.</p>
      <ul class="blog-empty__links">
        <li><a href="faq">Häufige Fragen</a></li>
        <li><a href="unsere-arbeit">So läuft ein Ankauf ab</a></li>
        <li><a href="export">Export und Verzollung</a></li>
        <li><a href="fahrzeuge">Fahrzeuge im Bestand</a></li>
      </ul>
    </div>'''

esc = lambda s: html.escape(s, quote=True)


def fail(msg):
    sys.exit('blog.py: ' + msg)


# ------------------------------------------------------------------ Quelle lesen
def read_post(path):
    name = os.path.splitext(os.path.basename(path))[0]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name):
        fail('%s: Dateiname nur aus Kleinbuchstaben, Ziffern und Bindestrichen (wird zur URL)' % path)
    src = open(path, encoding='utf-8').read()
    m = re.match(r'---\n([\s\S]*?)\n---\n([\s\S]*)$', src)
    if not m:
        fail('%s: Kopfbereich zwischen --- und --- fehlt' % path)
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            k, _, v = line.partition(':')
            meta[k.strip().lower()] = v.strip()
    for key in ('titel', 'beschreibung', 'datum', 'bild', 'bild_alt'):
        if not meta.get(key):
            fail('%s: Angabe „%s“ fehlt' % (path, key))
    meta['name'] = name
    meta['body'] = m.group(2).strip()
    meta['datum_obj'] = datetime.date.fromisoformat(meta['datum'])
    meta['aktualisiert_obj'] = datetime.date.fromisoformat(meta.get('aktualisiert') or meta['datum'])
    return meta


def de_date(d):
    return '%d. %s %d' % (d.day, MONATE[d.month - 1], d.year)


# ------------------------------------------------------------------ Bilder
def ensure_image(name):
    """Bildvarianten in assets/img/opt anlegen (falls nötig) -> (Stamm, Breiten, Breite, Höhe)."""
    path = os.path.join(IMG, name)
    if not os.path.exists(path):
        fail('Bild assets/img/%s fehlt' % name)
    stem = os.path.splitext(name)[0]
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is None:
        have = sorted(glob.glob(os.path.join(OPT, stem + '-*.jpg')))
        if not have:
            fail('Pillow fehlt (pip install pillow) – Bildvarianten für %s können nicht erzeugt werden' % name)
        widths = sorted(int(re.search(r'-(\d+)\.jpg$', h).group(1)) for h in have)
        return stem, widths, widths[-1], None
    im = Image.open(path)
    widths = sorted({min(w, im.width) for w in WIDTHS})
    if not all(os.path.exists(os.path.join(OPT, '%s-%d.jpg' % (stem, w))) for w in widths):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from bilder import save_photo
        save_photo(im.convert('RGB'), widths, stem)
    return stem, widths, im.width, im.height


def portrait(name):
    """Hochformat? Dann bekommt die Figur die Klasse …--hoch und läuft nicht über die ganze Breite."""
    _, _, w, h = ensure_image(name)
    return h is not None and h > w


def picture(name, alt, sizes, lazy=True, priority=False):
    stem, widths, w, h = ensure_image(name)
    def srcset(ext):
        return ', '.join('assets/img/opt/%s-%d.%s %dw' % (stem, x, ext, x) for x in widths)
    big = widths[-1]
    h = h and round(h * big / w)
    attrs = ' width="%d" height="%d"' % (big, h) if h else ''
    attrs += ' loading="lazy" decoding="async"' if lazy else ''
    attrs += ' fetchpriority="high"' if priority else ''
    return ('<picture>'
            '<source type="image/avif" srcset="%s" sizes="%s">'
            '<source type="image/webp" srcset="%s" sizes="%s">'
            '<img src="assets/img/opt/%s-%d.jpg" srcset="%s" sizes="%s" alt="%s"%s>'
            '</picture>') % (srcset('avif'), sizes, srcset('webp'), sizes,
                             stem, big, srcset('jpg'), sizes, esc(alt), attrs)


# ------------------------------------------------------------------ Text (Markdown-Teilmenge)
def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)

    def link(m):
        text, url = m.group(1), html.unescape(m.group(2))
        ext = url.startswith(('http://', 'https://')) and 'elegancecarsafi.com' not in url
        return '<a href="%s"%s>%s</a>' % (esc(url), ' target="_blank" rel="noopener"' if ext else '', text)
    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, s)


def render(body):
    """## / ### Überschriften, Absätze, Listen (- / 1.), **fett**, *kursiv*, [Link](url),
    Bild auf eigener Zeile: ![Alt-Text](datei.webp "Bildunterschrift") – Bildunterschrift = kursive Beschreibung für Leser."""
    out, images = [], []
    for block in re.split(r'\n\s*\n', body):
        block = block.strip()
        if not block:
            continue
        img = re.fullmatch(r'!\[([^\]]+)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)', block)
        if img:
            alt, name, cap = img.groups()
            images.append(name)
            fig = '<figure class="post__figure%s">' % (' post__figure--hoch' if portrait(name) else '') + picture(name, alt, '(max-width: 800px) 100vw, 760px')
            if cap:
                fig += '<figcaption>%s</figcaption>' % inline(cap)
            out.append(fig + '</figure>')
        elif block.startswith('### '):
            out.append('<h3>%s</h3>' % inline(block[4:]))
        elif block.startswith('## '):
            out.append('<h2>%s</h2>' % inline(block[3:]))
        elif all(re.match(r'[-*] ', l) for l in block.splitlines()):
            out.append('<ul>' + ''.join('<li>%s</li>' % inline(l[2:]) for l in block.splitlines()) + '</ul>')
        elif all(re.match(r'\d+\. ', l) for l in block.splitlines()):
            out.append('<ol>' + ''.join('<li>%s</li>' % inline(re.sub(r'^\d+\. ', '', l)) for l in block.splitlines()) + '</ol>')
        else:
            out.append('<p>%s</p>' % inline(' '.join(l.strip() for l in block.splitlines())))
    return '\n      '.join(out), images


def reading_time(body):
    words = len(re.findall(r'\w+', re.sub(r'!\[[^\]]*\]\([^)]*\)', '', body)))
    return max(1, round(words / 200))


# ------------------------------------------------------------------ Bausteine
def card(p):
    return '''      <li class="blog-card reveal">
        <a class="blog-card__link" href="blog-%s">
          <div class="blog-card__media">%s</div>
          <p class="blog-card__meta" data-no-i18n><time datetime="%s">%s</time>%s</p>
          <h2 class="blog-card__title" data-no-i18n>%s</h2>
          <p class="blog-card__excerpt" data-no-i18n>%s</p>
          <span class="blog-card__more">Weiterlesen</span>
        </a>
      </li>''' % (p['name'], picture(p['bild'], p['bild_alt'], '(max-width: 640px) 100vw, (max-width: 991px) 50vw, 430px'),
                  p['datum'], de_date(p['datum_obj']),
                  (' · ' + esc(p['kategorie'])) if p.get('kategorie') else '',
                  esc(p['titel']), esc(p.get('anriss') or p['beschreibung']))


def grid(posts):
    return '    <ul class="blog-grid">\n' + '\n'.join(card(p) for p in posts) + '\n    </ul>'


def set_meta(src, attr, key, value):
    pat = r'(<meta %s="%s" content=")[^"]*' % (attr, re.escape(key))
    if not re.search(pat, src):
        fail('Meta-Angabe %s fehlt in blog.html' % key)
    return re.sub(pat, lambda m: m.group(1) + esc(value), src, count=1)


def build_post(shell, p, others):
    url = BASE + 'blog-' + p['name']
    title = p.get('seitentitel') or '%s | Blog der ECS Exclusive Commerce Services GmbH' % p['titel']
    stem, widths, _, _ = ensure_image(p['bild'])
    cover_url = BASE + 'assets/img/opt/%s-%d.jpg' % (stem, widths[-1])

    src = shell
    src = re.sub(r'<title>[\s\S]*?</title>', lambda m: '<title>%s</title>' % esc(title), src, count=1)
    src = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, src, count=1)
    src = set_meta(src, 'name', 'description', p['beschreibung'])
    for attr, key, val in (('property', 'og:type', 'article'), ('property', 'og:title', title),
                           ('property', 'og:url', url), ('property', 'og:description', p['beschreibung']),
                           ('property', 'og:image', cover_url), ('property', 'og:image:secure_url', cover_url),
                           ('property', 'og:image:alt', p['bild_alt']), ('name', 'twitter:title', title),
                           ('name', 'twitter:description', p['beschreibung']), ('name', 'twitter:image', cover_url),
                           ('name', 'twitter:image:alt', p['bild_alt'])):
        src = set_meta(src, attr, key, val)
    src = re.sub(r'\n<meta property="og:image:(width|height)" content="\d+">', '', src)
    extra = ['<meta property="article:published_time" content="%s">' % p['datum'],
             '<meta property="article:modified_time" content="%s">' % p['aktualisiert_obj'].isoformat()]
    if p.get('kategorie'):
        extra.append('<meta property="article:section" content="%s">' % esc(p['kategorie']))
    if p.get('stichworte'):
        extra.append('<meta name="keywords" content="%s">' % esc(p['stichworte']))
    src = src.replace('<meta name="twitter:card"', '\n'.join(extra) + '\n<meta name="twitter:card"', 1)
    src = re.sub(r'<!-- schema:start -->[\s\S]*?<!-- schema:end -->', '<!-- schema:start -->\n<!-- schema:end -->', src)
    src = src.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n' + MARK % p['name'], 1)

    body, images = render(p['body'])
    credit = p.get('bildnachweis') or 'ECS GmbH'
    if p.get('ki_bild', '').lower() in ('ja', 'yes', 'true'):
        credit += ' (KI-generiert)'
    updated = ''
    if p['aktualisiert_obj'] != p['datum_obj']:
        updated = ' · aktualisiert am <time datetime="%s">%s</time>' % (p['aktualisiert_obj'].isoformat(), de_date(p['aktualisiert_obj']))

    main = '''
<!-- ============================================================ Seitenkopf -->
<section class="page-hero page-hero--compact">
  <div class="container">
    <p class="eyebrow"><span><a href="blog">Blog</a>%s</span></p>
    <h1 class="h1 page-hero__title" data-no-i18n>%s</h1>
    <p class="page-hero__meta" data-no-i18n><time datetime="%s">%s</time>%s · %d Min. Lesezeit</p>
  </div>
</section>

<!-- ============================================================== Beitrag -->
<article class="post">
  <div class="container">
    <figure class="post__cover%s" data-no-i18n>%s</figure>
    <div class="post__body" data-no-i18n>
      %s
    </div>
    <p class="post__note" data-no-i18n>Hinweis: Dieser Beitrag dient der allgemeinen Information und ersetzt keine Rechts- oder Steuerberatung. Alle Angaben ohne Gewähr, Stand: %s. Genannte Marken und Modellbezeichnungen gehören ihren jeweiligen Inhabern. Die ECS GmbH ist ein unabhängiger Händler und steht in keiner Verbindung zu den Herstellern.</p>
    <footer class="post__footer">
      <span>Bildnachweis: <span data-no-i18n>%s</span></span>
      <a href="blog">Alle Beiträge</a>
    </footer>
  </div>
</article>
''' % ((' · <span data-no-i18n>%s</span>' % esc(p['kategorie'])) if p.get('kategorie') else '',
       esc(p['titel']), p['datum'], de_date(p['datum_obj']), updated, reading_time(p['body']),
       ' post__cover--hoch' if portrait(p['bild']) else '',
       picture(p['bild'], p['bild_alt'], '(max-width: 1148px) 100vw, 1100px', lazy=False, priority=True)
       + ('<figcaption>%s</figcaption>' % inline(p['bild_text']) if p.get('bild_text') else ''),
       body, de_date(p['aktualisiert_obj']), esc(credit))
    if others:
        main += '''
<!-- ======================================================= Weitere Beiträge -->
<section class="post-more" aria-labelledby="more-title">
  <div class="container">
    <p class="eyebrow">Blog</p>
    <h2 class="h2" id="more-title">Weitere Beiträge</h2>
%s
  </div>
</section>
''' % grid(others[:3])
    cta = re.search(r'\n<!-- =+ Kontakt-Band -->[\s\S]*?</section>\n', shell)
    main += cta.group(0) if cta else ''
    src = re.sub(r'<main>[\s\S]*?</main>', lambda m: '<main>\n' + main + '\n</main>', src, count=1)
    return src, [p['bild']] + images


def main():
    shell_path = os.path.join(ROOT, 'blog.html')
    shell = open(shell_path, encoding='utf-8').read()
    if START not in shell or END not in shell:
        fail('Marken %s / %s fehlen in blog.html' % (START, END))

    posts = []
    for path in sorted(glob.glob(os.path.join(SRC_DIR, '*.md'))):
        if os.path.basename(path).startswith('_') or os.path.basename(path).upper().startswith('LIESMICH'):
            continue
        p = read_post(path)
        if p.get('entwurf', '').lower() in ('ja', 'yes', 'true'):
            continue
        if p['datum_obj'] > datetime.date.today():
            print('übersprungen (Datum in der Zukunft): ' + p['name'])
            continue
        posts.append(p)
    # gleiches Datum: optionale Uhrzeit (zeit: 14:30) entscheidet, dann der Dateiname
    posts.sort(key=lambda p: (p['datum_obj'], p.get('zeit', '00:00'), p['name']), reverse=True)

    # Galerie-Vorschau auf blog.html
    inner = grid(posts) if posts else EMPTY
    new_shell = re.sub(re.escape(START) + r'[\s\S]*?' + re.escape(END),
                       lambda m: START + '\n' + inner + '\n' + END, shell, count=1)
    if new_shell != shell:
        open(shell_path, 'w', encoding='utf-8').write(new_shell)
        print('blog.html')

    # Beitragsseiten
    written = set()
    for p in posts:
        others = [o for o in posts if o is not p]
        out, _ = build_post(new_shell, p, others)
        target = os.path.join(ROOT, 'blog-%s.html' % p['name'])
        old = open(target, encoding='utf-8').read() if os.path.exists(target) else ''
        written.add(os.path.basename(target))
        if out != old:
            open(target, 'w', encoding='utf-8').write(out)
            print(os.path.basename(target))

    # verwaiste Beitragsseiten entfernen (nur solche, die dieses Skript erzeugt hat)
    for target in glob.glob(os.path.join(ROOT, 'blog-*.html')):
        name = os.path.basename(target)
        if name not in written and '<!-- erzeugt von _tools/blog.py' in open(target, encoding='utf-8').read(400):
            os.remove(target)
            print('entfernt: ' + name)


if __name__ == '__main__':
    main()
