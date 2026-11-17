#!/usr/bin/env python3
"""Meldet geänderte Seiten per IndexNow (Bing, Yandex, Seznam, Naver teilen die Meldungen).

Aufruf:  python3 _tools/indexnow.py          -> Seiten aus dem letzten Commit
         python3 _tools/indexnow.py --alle   -> alle Seiten aus sitemap.xml
Läuft automatisch nach jedem Pages-Build (.github/workflows/indexnow.yml).
Schlüssel-Datei im Repo-Wurzelordner: d797bdf3ce88b7140b0c0baef9eb4c86.txt
"""
import json, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'elegancecarsafi.com'
KEY = 'd797bdf3ce88b7140b0c0baef9eb4c86'
BASE = 'https://' + HOST + '/'


def sitemap_urls():
    return re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read())


def changed_urls():
    out = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    known = set(sitemap_urls())
    urls = []
    for f in out:
        if '/' in f or not f.endswith('.html'):
            continue
        slug = f[:-5]
        url = BASE if slug == 'index' else BASE + slug
        if url in known:
            urls.append(url)
    return urls


def main():
    urls = sitemap_urls() if '--alle' in sys.argv else changed_urls()
    if not urls:
        print('Keine geänderten Seiten.')
        return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': BASE + KEY + '.txt',
                       'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow', r.status, '-', len(urls), 'Seiten:')
    print('\n'.join(urls))


if __name__ == '__main__':
    main()
