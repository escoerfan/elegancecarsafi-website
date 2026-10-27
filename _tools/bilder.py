#!/usr/bin/env python3
"""Erzeugt optimierte Bildvarianten (AVIF, WebP, JPG/PNG) in assets/img/opt/.

Die Originale bleiben unverändert. Benötigt Pillow (pip install pillow).
Aufruf:  python3 _tools/bilder.py               (alle Bilder)
         python3 _tools/bilder.py datei.webp    (nur diese Originale)
"""
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'img')
OUT = os.path.join(SRC, 'opt')

# Fotos: Datei -> Breiten
PHOTOS = {
    'hero-actros.png': [960, 1440, 1920, 2880],
    'pitch-atego-koffer.webp': [960, 1448],
    'pitch-lkw-reihe.webp': [960, 1448],
    'fuhrpark-atego-reihe.webp': [720, 1086],
    'export-amg-halle.webp': [960, 1672],
    'bewertung-sprinter.webp': [960, 1672],
    'lkw-man-tgx.webp': [960, 1672],
    'reisebus-magelys.webp': [960, 1448],
    'bau-arocs-kipper.webp': [960, 1448],
    'export-actros-weiss.webp': [960, 1672],
    # Ablauf-Abschnitte (Foto neben der Überschrift)
    'ablauf-man-tgx.webp': [960, 1672],
    'ablauf-actros-planen.webp': [960, 1672],
    'ablauf-axor-kran.webp': [960, 1672],
    'ablauf-man-absetzkipper.webp': [960, 1672],
    'ablauf-man-tgl-koffer.webp': [960, 1448],
    # Vorschaubild des Erklärfilms (Startseite, Unsere Arbeit)
    'erklaerfilm-poster.webp': [960, 1920],
    'erklaerfilm-poster-hoch.webp': [720, 1080],   # Handy: Hochformat-Film
}
# Hochformat-Ausschnitte für Handys: Datei -> (Seitenverhältnis B/H, Anker X, Breiten).
# Anker X = object-position im CSS; so bleibt bei object-fit: cover auf Bildschirmen
# bis zu diesem Seitenverhältnis exakt derselbe Bildbereich sichtbar.
CROPS = {
    'hero-actros.png': (3 / 4, 0.70, [810, 1215]),
    # Foto-Box neben dem Kontaktformular (Desktop ca. 0,86, Handy 4:5)
    'kontakt-actros.webp': (0.9, 0.215, [720, 847]),
}
# Logos (transparent): Datei -> Zielhöhe in Pixel (2x der Anzeigegröße)
LOGOS = {
    'marke-iveco.png': 192, 'marke-ford.png': 88, 'marke-mercedes.png': 88,
    'marke-man.png': 88, 'marke-setra.png': 88, 'marke-vw.png': 88,
}
# ECS-Logo: Kopf 150 px, Fuß 180 px breit -> 2x = 360 px
ECS_LOGO = {'logo-ecs.png': 360}


def stem(name):
    return os.path.splitext(name)[0]


def save_photo(im, widths, prefix):
    for w in widths:
        w = min(w, im.width)
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS) if w != im.width else im
        base = os.path.join(OUT, '%s-%d' % (prefix, w))
        r.save(base + '.avif', quality=55, speed=4)
        r.save(base + '.webp', quality=78, method=6)
        r.save(base + '.jpg', quality=80, optimize=True, progressive=True)


def wanted(name):
    return not ONLY or name in ONLY


def photos():
    for name, widths in PHOTOS.items():
        if not wanted(name):
            continue
        im = Image.open(os.path.join(SRC, name)).convert('RGB')
        save_photo(im, widths, stem(name))


def crops():
    for name, (ratio, anchor, widths) in CROPS.items():
        if not wanted(name):
            continue
        im = Image.open(os.path.join(SRC, name)).convert('RGB')
        cw = round(im.height * ratio)
        x0 = round(anchor * (im.width - cw))
        save_photo(im.crop((x0, 0, x0 + cw, im.height)), widths, stem(name) + '-hoch')


def logos(table):
    for name, size in table.items():
        if not wanted(name):
            continue
        im = Image.open(os.path.join(SRC, name)).convert('RGBA')
        if name.startswith('logo-'):
            w, h = size, round(im.height * size / im.width)
        else:
            w, h = round(im.width * size / im.height), size
        r = im.resize((w, h), Image.LANCZOS)
        base = os.path.join(OUT, '%s-%d' % (stem(name), size))
        r.save(base + '.webp', quality=90, method=6)
        r.save(base + '.png', optimize=True)


ONLY = {os.path.basename(a) for a in sys.argv[1:]}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    photos()
    crops()
    logos(LOGOS)
    logos(ECS_LOGO)
    for f in sorted(os.listdir(OUT)):
        if ONLY and not any(f.startswith(stem(n) + '-') for n in ONLY):
            continue
        p = os.path.join(OUT, f)
        print('%-40s %6d KB  %s' % (f, os.path.getsize(p) // 1024, Image.open(p).size))
