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
    'ablauf-axor-gruen.webp': [960, 1320],        # Abholung (Foto aus dem Chat, 1320 px)
    # Vorschaubild des Erklärfilms (Startseite, Unsere Arbeit)
    'erklaerfilm-poster.webp': [960, 1920],
    'erklaerfilm-poster-hoch.webp': [720, 1080],   # Handy: Hochformat-Film
    # Export-Unterseiten EU / Drittland (Instagram-Fotos, 1320 px breit)
    'export-eu-actros-rot.webp': [960, 1320],
    'export-eu-atego-plane.webp': [960, 1320],
    'export-drittland-actros-schwarz.webp': [960, 1320],
    # Export-Hauptseite: Ablauf-Foto + Bildpaar bei „Welche Fahrzeuge wir exportieren“
    'export-ablauf-scania-kran.webp': [960, 1473],
    'export-actros-weiss-front.webp': [720, 1332],
    # Gebrauchte Nutzfahrzeuge: Sattelauflieger mit Kippmulde (Foto aus dem Chat, nur 1024 px)
    'angebot-auflieger-kippmulde.webp': [720, 1024],
    'angebot-kleinbus-sprinter.webp': [960, 1448],
    'angebot-radlader-cat.webp': [720, 877],        # nur 877 px aus dem Chat
    'angebot-linienbus-citaro.webp': [720, 889],    # nur 889 px aus dem Chat
    'angebot-spezial-econic.webp': [960, 1448],
    # Foto-Box neben dem Kontaktformular (Hochformat, object-fit: cover)
    'kontakt-atego-reihe.webp': [720, 1086],
    # Instagram-Fotos vom 01.11.2026: Originaldateien aus Bilder/Echt/Insta, unbearbeitet
    'blog-arocs-gruen.jpeg': [960, 1320],            # Blog: Arocs 6x4 (IMG_2081)
    'angebot-atego-koffer.jpeg': [960, 1320],        # Angebot Verteiler-LKW: Atego 1224 (IMG_2076)
    'angebot-actros-sattelzug.jpeg': [960, 1320],    # Angebot Sattelzugmaschinen: Actros (IMG_2080)
    'angebot-atego-kipper.jpeg': [960, 1320],        # Angebot Kipper: Atego Kipper im Schnee (IMG_2085)
    # Busfotos aus dem Chat (01.11.2026), Originaldateien unbearbeitet
    'reisebus-volvo-weiss.webp': [960, 1320],        # Reisebus: Ablauf-Kopf (Volvo)
    'reisebus-setra-silber.webp': [960, 1320],       # Reisebus: Zeitleiste Bewertung (Setra S 416 GT-HD)
    'angebot-setra-weiss.webp': [960, 1320],         # Angebot Reisebusse und Omnibusse (Setra)
    'fuhrpark-scania-rot.webp': [960, 1320],         # Fuhrpark: neben „Ein Angebot für Ihre ganze Flotte“ (Scania)
    'blog-kuehlauflieger.jpeg': [960, 1320],         # Blog „Nutzfahrzeuge im Alltag“: Kühlauflieger (IMG_2082)
    'bewertung-antos-rot.png': [720, 1086],
    'man-tgm-koffer-orange.jpeg': [960, 1600],       # Gebrauchte Nutzfahrzeuge „Mittelschwere LKW“ + Blog MAN 12-Tonner (TGM 15.290, Chat 05.11.)          # Unsere Arbeit: „Wie wir Ihr Fahrzeug bewerten“ (roter Antos, Hochformat)
}
# Hochformat-Ausschnitte für Handys: Datei -> (Seitenverhältnis B/H, Anker X, Breiten).
# Anker X = object-position im CSS; so bleibt bei object-fit: cover auf Bildschirmen
# bis zu diesem Seitenverhältnis exakt derselbe Bildbereich sichtbar.
CROPS = {
    'hero-actros.png': (3 / 4, 0.70, [810, 1215]),
}
# Logos (transparent): Datei -> Zielhöhe in Pixel (2x der Anzeigegröße).
# Marken-Logos werden vorher auf den sichtbaren Bereich zugeschnitten (kein Leerrand),
# damit der Abstand im Logo-Band überall gleich wirkt. Anzeigehöhe: --h in index.html.
LOGOS = {
    'marke-iveco.png': 48, 'marke-ford.png': 68, 'marke-mercedes.png': 104,
    'marke-man.png': 80, 'marke-setra.png': 56, 'marke-vw.png': 104,
}
# Freigestellte Fahrzeuge (transparent): Datei -> Breiten (AVIF/WebP/PNG mit Alpha)
CUTOUTS = {
    'kontakt-tourismo.png': [760, 1140, 1536],   # Kontakt-Band Startseite + Reisebus: Tourismo (Chat 07.11.)
    'kontakt-tourismo-reisebus.png': [760, 1140, 1535],  # Reisebus verkaufen: Tourismo „weißer Himmel“
    'kontakt-actros-szm.png': [760, 1140, 1536],      # LKW verkaufen: Actros MP3 Sattelzugmaschine
    'kontakt-cat-bagger.png': [760, 1140, 1536],      # Bau- und Kommunalfahrzeuge: CAT 320
    'kontakt-citaro.png': [760, 1140, 1536],          # Linienbus verkaufen: Citaro rot
    'kontakt-sprinter.png': [760, 1140, 1536],        # Transporter verkaufen: Sprinter orange
    'kontakt-atego-flotte.png': [760, 1140, 1536],    # Fuhrpark verkaufen: 4 Atego
    'kontakt-actros-mischer.png': [760, 1140, 1536],  # Nutzfahrzeug-Ankauf: Actros Betonmischer
    'kontakt-antos-koffer.png': [540, 810, 1086],     # Gebrauchte Nutzfahrzeuge: Antos Koffer (Hochformat)
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


def cutouts():
    for name, widths in CUTOUTS.items():
        if not wanted(name):
            continue
        im = Image.open(os.path.join(SRC, name)).convert('RGBA')
        for w in widths:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            r = im.resize((w, h), Image.LANCZOS) if w != im.width else im
            base = os.path.join(OUT, '%s-%d' % (stem(name), w))
            r.save(base + '.avif', quality=60, speed=4)
            r.save(base + '.webp', quality=82, method=6)
            r.save(base + '.png', optimize=True)


def logos(table):
    for name, size in table.items():
        if not wanted(name):
            continue
        im = Image.open(os.path.join(SRC, name)).convert('RGBA')
        if name.startswith('marke-'):
            im = im.crop(im.getchannel('A').getbbox())
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
    cutouts()
    logos(LOGOS)
    logos(ECS_LOGO)
    for f in sorted(os.listdir(OUT)):
        if ONLY and not any(f.startswith(stem(n) + '-') for n in ONLY):
            continue
        p = os.path.join(OUT, f)
        print('%-40s %6d KB  %s' % (f, os.path.getsize(p) // 1024, Image.open(p).size))
