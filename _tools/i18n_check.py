#!/usr/bin/env python3
"""Prüft, ob alle deutschen Texte der HTML-Seiten in js/lang/*.js übersetzt sind.

Aufruf (im Repo-Ordner):  python3 _tools/i18n_check.py [seite.html ...]
Ohne Argumente werden alle *.html geprüft. Ausgabe: fehlende Schlüssel je Sprache.
Ordner mit _ am Anfang veröffentlicht GitHub Pages (Jekyll) nicht.
"""
import glob, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ['en', 'pl', 'ru', 'es', 'ar']
ATTRS = ('alt', 'aria-label', 'placeholder', 'title')       # wie js/i18n.js
SKIP = {'script', 'style', 'noscript', 'svg', 'textarea'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
HAS_LETTER = re.compile(r'[A-Za-zÀ-ÿ]')

# Namen und Angaben, die in jeder Sprache gleich bleiben (brauchen keinen Schlüssel)
INVARIANT = {
    'Instagram', 'TikTok', 'WhatsApp', 'Elegance Car Safi', 'ECS', 'FAQ',
    'ECS Exclusive Commerce Services GmbH', 'ECS Exclusive Commerce Services GmbH – Elegance Car Safi',
    'ECS Exclusive Commerce Services GmbH „Elegance Car Safi“',
    'Scania', 'IVECO', 'Ford', 'Mercedes-Benz', 'MAN', 'Setra', 'Volvo', 'Volkswagen',
}
INVARIANT_RE = re.compile(r'^(\S+@\S+|https?://\S+|[+\d][\d\s/()+-]*)$')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []        # (tag, skipped)
        self.texts = []
        self.in_title = False

    def skipped(self):
        return bool(self.stack) and self.stack[-1][1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        skip = self.skipped() or tag in SKIP or 'data-no-i18n' in a
        if tag == 'title':
            self.in_title = True
        if not skip and tag not in ('meta', 'link', 'head', 'html'):
            for k in ATTRS:
                v = a.get(k)
                if v and HAS_LETTER.search(v):
                    self.texts.append(norm(v))
        if tag not in VOID:
            self.stack.append((tag, skip))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.in_title or not self.skipped():
            t = norm(data)
            if t and HAS_LETTER.search(t):
                self.texts.append(t)


def load_dict(code):
    src = open(os.path.join(ROOT, 'js', 'lang', code + '.js'), encoding='utf-8').read()
    body = src[src.index('= {', src.index(').' + code)) + 2: src.rindex('}') + 1]
    body = re.sub(r'^\s*/\*.*?\*/\s*$', '', body, flags=re.M)          # Kommentarzeilen
    body = re.sub(r',(\s*})', r'\1', body)                              # Komma am Ende
    return json.loads(body)


def compile_patterns(d):
    pats = []
    for key in d:
        if '{' in key and re.search(r'\{[a-z]\}', key):
            rx = re.escape(key)
            rx = re.sub(r'\\\{([a-z])\\\}', '(.+?)', rx)
            pats.append(re.compile('^' + rx + '$'))
    return pats


def main(files):
    files = files or sorted(glob.glob(os.path.join(ROOT, '*.html')))
    dicts = {c: load_dict(c) for c in LANGS}
    pats = {c: compile_patterns(dicts[c]) for c in LANGS}
    missing_total = 0
    for f in files:
        c = Collector()
        c.feed(open(f, encoding='utf-8').read())
        seen = []
        for t in c.texts:
            if t not in seen:
                seen.append(t)
        seen = [t for t in seen if t not in INVARIANT and not INVARIANT_RE.match(t)]
        for code in LANGS:
            miss = [t for t in seen
                    if t not in dicts[code] and not any(p.match(t) for p in pats[code])]
            if miss:
                missing_total += len(miss)
                print('%s [%s] fehlt %d:' % (os.path.basename(f), code, len(miss)))
                for t in miss:
                    print('   ', json.dumps(t, ensure_ascii=False))
    print('Fehlende Übersetzungen gesamt:', missing_total)
    return 1 if missing_total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
