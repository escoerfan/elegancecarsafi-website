#!/usr/bin/env python3
"""Grafik „LKW-Tonnenklassen und Führerscheine“ für den Blogbeitrag lkw-tonnenklassen.

Erzeugt assets/img/blog-lkw-tonnenklassen.webp und blog-lkw-fuehrerscheinklassen.webp (Chrome headless, wie kipper_grafiken.py).
Aufruf: python3 _tools/tonnenklassen_grafik.py
Rechtsstand: § 34 StVZO (Gewichte), § 6 FeV (Klassen), § 3 / § 18 / § 30 StVO, § 29 Abs. 3 StVO.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kipper_grafiken import Szene, lkw, render, svg_datei, INK, DARK, MID, LIGHT, PALE, NS  # noqa: E402

S = 21          # Pixel je Meter für alle Silhouetten (maßstäblich untereinander)
GRAU = '#5f5f5f'


def box(sz, x0, x1, y0, y1, fill=PALE, rippen=0):
    sz.add(sz.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, INK, 1.8))
    for i in range(1, rippen):
        x = x0 + (x1 - x0) * i / rippen
        sz.add(sz.line((x, y0 + 0.08), (x, y1 - 0.08), '#bdbdbd', 1))


def rad(sz, x, r=0.5):
    sz.add(sz.circ((x, r), r, INK, INK, 1))
    sz.add(sz.circ((x, r), r * 0.34, '#fff', '#fff', 1))


def transporter(sz):
    body = [(0.0, 0.45), (0.0, 1.05), (0.25, 1.25), (0.95, 1.55), (1.55, 2.55), (5.85, 2.62), (5.9, 0.45)]
    sz.add(sz.poly(body, INK, INK, 1))
    sz.add(sz.poly([(1.05, 1.6), (1.55, 2.38), (2.25, 2.4), (2.25, 1.62)], PALE, PALE, 1))
    for x in (1.05, 4.75):
        rad(sz, x, 0.36)


def koffer_lkw(sz, achsen, ende, hoehe, kabine=2.85, plane=False):
    lkw(sz, achsen, ende - 0.1, kabine)
    box(sz, 2.4, ende, 1.12, hoehe, PALE if not plane else '#e2e2e2', 8 if plane else 1)


def kipper(sz, achsen, ende):
    lkw(sz, achsen, ende - 0.2, 3.15)
    m = [(2.55, 1.15), (ende, 1.15), (ende, 2.55), (2.75, 2.55), (2.55, 2.3)]
    sz.add(sz.poly(m, PALE, INK, 2))
    for i in range(1, 6):
        x = 2.75 + (ende - 2.85) * i / 6
        sz.add(sz.line((x, 1.22), (x, 2.48), '#bdbdbd', 1))
    sz.add(sz.poly([(2.8, 2.55), (3.6, 2.78), (5.2, 2.68), (6.6, 2.8), (ende - 0.1, 2.55)], '#a3a3a3', INK, 1.2))


def sattelzug(sz):
    lkw(sz, [1.4, 5.0], 5.9, 3.25)
    sz.add(sz.poly([(4.3, 1.08), (5.5, 1.08), (5.5, 1.25), (4.3, 1.25)], '#555', INK, 1.2))
    # Auflieger 13,6 m
    x0, x1 = 2.9, 16.5
    sz.add(sz.poly([(x0, 1.28), (x1, 1.28), (x1, 1.55), (x0, 1.55)], '#6a6a6a', INK, 1.4))
    box(sz, x0, x1, 1.55, 4.0, '#e6e6e6', 14)
    sz.add(sz.beam((7.2, 1.28), (7.2, 0.25), 0.12, '#555', INK, 1.2))
    for x in (13.2, 14.5, 15.8):
        rad(sz, x, 0.47)


def schwertransport(sz):
    lkw(sz, [1.4, 4.7, 6.05], 6.9, 3.3)
    # Ballast / Zugkupplung
    box(sz, 2.45, 4.0, 1.1, 2.3, '#8a8a8a')
    sz.add(sz.poly([(5.2, 1.08), (6.6, 1.08), (6.6, 1.25), (5.2, 1.25)], '#555', INK, 1.2))
    # Tiefbett mit Schwanenhals
    hals = [(5.0, 1.25), (8.4, 1.25), (8.9, 0.75), (16.4, 0.75), (16.4, 1.05), (20.8, 1.05), (20.8, 0.6), (16.4, 0.6), (16.4, 0.45),
            (8.8, 0.45), (8.3, 0.95), (5.0, 0.95)]
    sz.add(sz.poly(hals, '#6a6a6a', INK, 1.6))
    for i in range(6):
        rad(sz, 16.0 + i * 0.8 + 0.4, 0.4)
    # Ladung: Transformator
    sz.add(sz.poly([(9.4, 0.75), (15.6, 0.75), (15.6, 4.1), (9.4, 4.1)], '#cfcfcf', INK, 2))
    for i in range(1, 7):
        x = 9.4 + i * 6.2 / 7
        sz.add(sz.line((x, 0.9), (x, 3.9), '#9f9f9f', 1.2))
    for x in (10.4, 12.5, 14.6):
        sz.add(sz.poly([(x - 0.25, 4.1), (x + 0.25, 4.1), (x + 0.18, 4.75), (x - 0.18, 4.75)], '#9a9a9a', INK, 1.3))
    # Warntafel hinten
    sz.add(sz.poly([(20.5, 1.05), (20.85, 1.05), (20.85, 2.0), (20.5, 2.0)], '#fff', INK, 1.4))
    for k in range(4):
        y = 1.1 + k * 0.24
        sz.add(sz.poly([(20.5, y), (20.85, y + 0.12), (20.85, y + 0.22), (20.5, y + 0.1)], INK, INK, 0.5))
    # Rundumleuchte
    sz.add(sz.poly([(0.9, 3.3), (1.3, 3.3), (1.25, 3.5), (0.95, 3.5)], '#555', INK, 1.2))


KARTEN = [
    # gewicht, name, zeichnen, länge (m), beispiel, zeile2, fuehrerschein
    ('3,5 t', 'Transporter', transporter, 5.9, 'z. B. Mercedes-Benz Sprinter', '2 Achsen · Handwerk, Kurier', 'B'),
    ('7,5 t', 'Leichter LKW', lambda sz: koffer_lkw(sz, [1.25, 4.35], 7.2, 3.35, 2.8), 7.2, 'z. B. Mercedes-Benz Atego 818', '2 Achsen · Verteilerverkehr', 'C1'),
    ('12 t', 'Mittlerer LKW', lambda sz: koffer_lkw(sz, [1.3, 4.9], 8.2, 3.55, 2.9), 8.2, 'z. B. MAN TGL 12.250', '2 Achsen · Verteiler, Handel', 'C'),
    ('18 t', 'Schwerer LKW', lambda sz: koffer_lkw(sz, [1.35, 5.6], 9.5, 3.8, 3.1, True), 9.5, 'z. B. Mercedes-Benz Antos 1836', '2 Achsen · Verteiler, Bau', 'C'),
    ('26 t', 'Dreiachser', lambda sz: kipper(sz, [1.4, 5.1, 6.45], 8.3), 8.4, 'z. B. Actros 2646', '3 Achsen · Kipper, Mischer', 'C'),
    ('32 t', 'Vierachser', lambda sz: kipper(sz, [1.4, 3.15, 6.5, 7.85], 9.4), 9.5, 'z. B. Arocs 3243', '4 Achsen · Baustelle, Beton', 'C'),
    ('40 t', 'Sattel- und Hängerzug', sattelzug, 16.6, 'z. B. Volvo FH mit Auflieger', '5 Achsen · Fernverkehr', 'CE'),
    ('über 40 t', 'Schwertransport', schwertransport, 20.9, 'Tieflader, Kranteile, Trafos', 'Erlaubnis nach § 29 Abs. 3 StVO', 'CE'),
]


HOEHE = [2.62, 3.35, 3.55, 3.8, 3.2, 3.2, 4.0, 4.75]   # Silhouettenhöhe je Karte (m)


def karte(out, x0, y0, w, h, k, hoehe):
    """Eine Klasse für die 760-px-Spalte: Gewicht, Bezeichnung, Silhouette, Führerschein."""
    gew, name, fn, laenge, bsp, z2, fs = k
    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fff" stroke="rgba(38,38,38,0.14)" stroke-width="1"/>' % (x0, y0, w, h))
    out.append('<text x="%d" y="%d" font-size="24" font-weight="600" fill="%s">%s</text>' % (x0 + 14, y0 + 34, INK, gew))
    out.append('<text x="%d" y="%d" font-size="14" font-weight="400" fill="%s">%s</text>' % (x0 + 14, y0 + 55, MID, name))
    s = min((w - 28) / laenge, 66 / hoehe)
    boden = y0 + h - 50
    sz = Szene(x0 + (w - laenge * s) / 2, boden, s)
    sz.add(sz.line((-0.3, 0), (laenge + 0.3, 0), INK, 1))
    fn(sz)
    out.append(sz.svg())
    bw = 22 + 11 * len(fs)
    out.append('<rect x="%d" y="%d" width="%d" height="24" fill="%s"/>' % (x0 + 14, y0 + h - 36, bw, INK))
    out.append('<text x="%.1f" y="%d" font-size="14" font-weight="600" fill="#fff" text-anchor="middle">%s</text>' % (x0 + 14 + bw / 2, y0 + h - 19, fs))
    out.append('<text x="%d" y="%d" font-size="14" font-weight="400" fill="%s">Führerschein</text>' % (x0 + 22 + bw, y0 + h - 19, MID))


def bild_klassen():
    W, cw, ch = 760, 190, 205
    out = []
    for i, k in enumerate(KARTEN):
        karte(out, (i % 4) * cw, (i // 4) * ch, cw, ch, k, HOEHE[i])
    return W, 2 * ch, ''.join(out), 'LKW-Tonnenklassen'


def bild_fuehrerschein():
    """Führerscheinklassen entlang der Gewichtsachse."""
    W = 760
    x0, x1 = 64, 740
    ticks = ['0', '3,5 t', '7,5 t', '12 t', '18 t', '26 t', '32 t', '40 t', 'mehr']
    n = len(ticks) - 1
    def X(i):
        return x0 + (x1 - x0) * i / n
    rows = [('B', 0, 1, 'bis 3,5 t'), ('C1', 1, 2, '3,5 bis 7,5 t'), ('C1E', 1, 3, 'C1 mit Anhänger, Zug bis 12 t'),
            ('C', 1, 6, 'alle LKW über 3,5 t'), ('CE', 3, 8, 'Sattel- und Hängerzüge')]
    out = []
    ry = 16
    for lab, a, b, txt in rows:
        xa, xb = X(a) + 1, X(b) - 1
        out.append('<text x="10" y="%d" font-size="16" font-weight="600" fill="%s">%s</text>' % (ry + 19, INK, lab))
        out.append('<rect x="%.1f" y="%d" width="%.1f" height="26" fill="%s"/>' % (xa, ry, xb - xa, INK if lab != 'C1E' else DARK))
        if xb < 520:
            out.append('<text x="%.1f" y="%d" font-size="14" fill="%s">%s</text>' % (xb + 10, ry + 18, INK, txt))
        else:
            out.append('<text x="%.1f" y="%d" font-size="14" fill="#fff">%s</text>' % (xa + 10, ry + 18, txt))
        ry += 38
    ay = ry + 8
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.5"/>' % (x0, ay, x1, ay, INK))
    for i, t in enumerate(ticks):
        anchor = 'end' if i == n else 'middle'
        out.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.5"/>' % (X(i), ay - 5, X(i), ay + 5, INK))
        out.append('<text x="%.1f" y="%d" font-size="14" font-weight="500" fill="%s" text-anchor="%s">%s</text>' % (X(i) + (4 if i == n else 0), ay + 24, INK, anchor, t))
    out.append('<text x="%d" y="%d" font-size="14" fill="%s">Zulässiges Gesamtgewicht des Fahrzeugs bzw. des Zuges</text>' % (x0, ay + 50, MID))
    return W, ay + 64, ''.join(out), 'Führerscheinklassen nach Gewicht'


if __name__ == '__main__':
    for name, f in [('blog-lkw-tonnenklassen', bild_klassen), ('blog-lkw-fuehrerscheinklassen', bild_fuehrerschein)]:
        W, H, inhalt, titel = f()
        render(name, W, H, svg_datei(W, H, inhalt, titel))
