#!/usr/bin/env python3
"""Erzeugt verkleinerte Fassungen von CSS und JS (*.min.css / *.min.js).

Bearbeitet werden immer nur die lesbaren Quelldateien (css/style.css,
js/main.js …). Die Seiten laden die .min-Fassungen daneben. Inhalt und
Wirkung sind gleich, nur Leerzeichen, Kommentare und lange Namen fallen weg
(style.css gzip 27 → 17 KB).

Läuft automatisch im pre-commit-Hook (_tools/hooks/pre-commit).
Von Hand:  python3 _tools/minify.py      (gibt die geänderten Dateien aus)

Werkzeug: esbuild (eine einzelne Programmdatei, kein Node nötig), gesucht in
$ESBUILD, ~/.local/esbuild/… oder im PATH. Installation einmalig:
  npm i esbuild --prefix ~/.local/esbuild
Die Sprachdateien js/lang/*.js bleiben unverkleinert (spart dort < 3 %).
"""
import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_esbuild():
    cands = [
        os.environ.get('ESBUILD'),
        os.path.expanduser('~/.local/esbuild/node_modules/@esbuild/darwin-arm64/bin/esbuild'),
        os.path.expanduser('~/.local/esbuild/node_modules/.bin/esbuild'),
        shutil.which('esbuild'),
    ]
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def sources():
    out = []
    for pat in ('css/*.css', 'js/*.js'):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            if '.min.' not in os.path.basename(f):
                out.append(f)
    return out


def target(src):
    base, ext = os.path.splitext(src)
    return base + '.min' + ext


def main():
    esb = find_esbuild()
    if not esb:
        sys.stderr.write('minify.py: esbuild fehlt (npm i esbuild --prefix ~/.local/esbuild)\n')
        return 1
    changed = []
    for src in sources():
        dst = target(src)
        res = subprocess.run(
            [esb, src, '--minify', '--charset=utf8', '--log-level=error'],
            capture_output=True)
        if res.returncode != 0:
            sys.stderr.write(res.stderr.decode('utf-8', 'replace'))
            return 1
        data = res.stdout
        old = open(dst, 'rb').read() if os.path.exists(dst) else None
        if data != old:
            with open(dst, 'wb') as fh:
                fh.write(data)
            changed.append(os.path.relpath(dst, ROOT))
    for c in changed:
        print(c)
    return 0


if __name__ == '__main__':
    sys.exit(main())
