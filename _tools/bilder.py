#!/usr/bin/env python3
"""Erzeugt optimierte Bildvarianten (AVIF, WebP, JPG/PNG) in assets/img/opt/.

Die Originale bleiben unverändert. Benötigt Pillow (pip install pillow).
Aufruf:  python3 _tools/bilder.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'img')
OUT = os.path.join(SRC, 'opt')

# Fotos: Datei -> Breiten
PHOTOS = {
    'hero-actros.png': [960, 1440, 1920, 2880],
    'pitch-actros-frontal.jpg': [960, 1672],
    'export-autotransporter.jpg': [960, 1672],
    'kontakt-fahrzeuge-halle.jpg': [960, 1672],
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


def photos():
    for name, widths in PHOTOS.items():
        im = Image.open(os.path.join(SRC, name)).convert('RGB')
        for w in widths:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            r = im.resize((w, h), Image.LANCZOS) if w != im.width else im
            base = os.path.join(OUT, '%s-%d' % (stem(name), w))
            r.save(base + '.avif', quality=55, speed=4)
            r.save(base + '.webp', quality=78, method=6)
            r.save(base + '.jpg', quality=80, optimize=True, progressive=True)


def logos(table):
    for name, size in table.items():
        im = Image.open(os.path.join(SRC, name)).convert('RGBA')
        if name.startswith('logo-'):
            w, h = size, round(im.height * size / im.width)
        else:
            w, h = round(im.width * size / im.height), size
        r = im.resize((w, h), Image.LANCZOS)
        base = os.path.join(OUT, '%s-%d' % (stem(name), size))
        r.save(base + '.webp', quality=90, method=6)
        r.save(base + '.png', optimize=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    photos()
    logos(LOGOS)
    logos(ECS_LOGO)
    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        print('%-40s %6d KB  %s' % (f, os.path.getsize(p) // 1024, Image.open(p).size))
