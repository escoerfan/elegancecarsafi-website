#!/usr/bin/env python3
"""Erzeugt sitemap.xml aus allen indexierbaren *.html-Seiten.

- Aufgenommen wird jede Seite mit <link rel="canonical"> und ohne "noindex".
- URL = Canonical-URL der Seite.
- lastmod = Datum des letzten Git-Commits der Datei; bei geänderten bzw.
  vorgemerkten (staged) Dateien das heutige Datum.

Läuft automatisch vor jedem Commit (_tools/hooks/pre-commit),
manuell:  python3 _tools/sitemap.py
"""
import datetime, glob, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def lastmod(name):
    changed = set(git('diff', '--name-only').splitlines()) | set(git('diff', '--cached', '--name-only').splitlines())
    untracked = set(git('ls-files', '--others', '--exclude-standard').splitlines())
    if name in changed or name in untracked:
        return datetime.date.today().isoformat()
    d = git('log', '-1', '--format=%cs', '--', name)
    return d or datetime.date.today().isoformat()


def main():
    entries = []
    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        html = open(path, encoding='utf-8').read()
        head = html[:html.find('</head>')]
        if re.search(r'<meta name="robots" content="[^"]*noindex', head):
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        if not m:
            continue
        entries.append((m.group(1), lastmod(os.path.basename(path))))
    # Startseite zuerst, dann alphabetisch
    entries.sort(key=lambda e: (e[0].rstrip('/').count('/') > 2, e[0]))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in entries:
        lines.append('  <url><loc>%s</loc><lastmod>%s</lastmod></url>' % (loc, mod))
    lines.append('</urlset>')
    out = '\n'.join(lines) + '\n'
    target = os.path.join(ROOT, 'sitemap.xml')
    old = open(target, encoding='utf-8').read() if os.path.exists(target) else ''
    if out != old:
        open(target, 'w', encoding='utf-8').write(out)
    print('sitemap.xml: %d URLs' % len(entries))


if __name__ == '__main__':
    main()
