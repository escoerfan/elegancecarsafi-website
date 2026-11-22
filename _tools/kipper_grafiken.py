#!/usr/bin/env python3
"""Schnittgrafiken (Seitenansicht) für die Blogbeiträge Abrollkipper und Absetzkipper.

Erzeugt SVG, rendert sie mit Chrome headless und speichert WebP-Quellen in assets/img:
  blog-abrollkipper-aufbau.webp, blog-abrollkipper-ablauf.webp,
  blog-absetzkipper-aufbau.webp, blog-absetzkipper-ablauf.webp
Danach erzeugt _tools/blog.py die Ladeversionen.

Aufruf:  python3 _tools/kipper_grafiken.py [--nur-svg]
Maße in Metern, y nach oben, Fahrzeug fährt nach links.
"""
import math, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.environ.get('KIPPER_OUT') or os.path.join(ROOT, 'assets', 'img')
FONT = os.path.join(ROOT, 'assets', 'fonts', 'dm-sans-latin.woff2')
FONT_EXT = os.path.join(ROOT, 'assets', 'fonts', 'dm-sans-latin-ext.woff2')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# Farben wie css/style.css: --ink #262626, --ink-soft #505050, --muted-light #707070, helle Flächen #f4f4f4
INK = '#262626'
DARK = '#505050'
MID = '#707070'
LIGHT = '#bdbdbd'
PALE = '#f4f4f4'
LINIE = 1.5          # einheitliche Strichstärke (px)


def _lum(f):
    f = f.lstrip('#')
    if len(f) == 3:
        f = ''.join(c * 2 for c in f)
    r, g, b = (int(f[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def farbe(f):
    """Reduziert jede Füllfarbe auf drei Töne: Ink, Grau, Hell (schlichter Stil der Website)."""
    if not f or f == 'none' or not f.startswith('#'):
        return f
    l = _lum(f)
    if l < 0.5:
        return INK
    if l < 0.8:
        return LIGHT
    return '#ffffff' if l > 0.99 else PALE
NS = 'vector-effect="non-scaling-stroke"'


# ------------------------------------------------------------------ Geometrie
def rot(p, c, deg):
    """Punkt p um c drehen (Grad, gegen den Uhrzeigersinn bei y nach oben)."""
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def pts(lst):
    return ' '.join('%.3f,%.3f' % p for p in lst)


class Szene:
    """Zeichenfläche: Meter-Koordinaten (y oben) in einer Gruppe, Text in Pixeln."""

    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s
        self.g = []      # Elemente im Meter-System
        self.t = []      # Text / Pixel-Elemente obendrauf

    def px(self, p):
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)

    def add(self, el):
        self.g.append(el)

    def svg(self):
        return ('<g transform="translate(%.2f %.2f) scale(%.4f %.4f)">%s</g>%s'
                % (self.ox, self.oy, self.s, -self.s, ''.join(self.g), ''.join(self.t)))

    # --- Grundformen (Meter)
    def poly(self, p, fill='none', stroke=INK, sw=2, extra=''):
        return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="miter" %s %s/>' % (pts(p), farbe(fill), INK, min(sw, LINIE), NS, extra)

    def line(self, a, b, stroke=INK, sw=2, extra=''):
        # schlicht: helle Zier- und Rippenlinien entfallen
        if stroke.startswith('#') and 0.45 < _lum(stroke) < 0.95:
            return ''
        stroke = INK if stroke.startswith('#') else stroke
        sw = sw if sw >= 4 else min(sw, LINIE)
        return '<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" stroke="%s" stroke-width="%s" stroke-linecap="round" %s %s/>' % (a[0], a[1], b[0], b[1], stroke, sw, NS, extra)

    def circ(self, c, r, fill='none', stroke=INK, sw=2):
        return '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (c[0], c[1], r, farbe(fill), INK, min(sw, LINIE), NS)

    def beam(self, a, b, w, fill=DARK, stroke=INK, sw=2):
        """Rechteckiger Träger von a nach b mit Breite w."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l * w / 2, dx / l * w / 2
        return self.poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], fill, stroke, sw)

    def zylinder(self, a, b, w=0.13):
        """Hydraulikzylinder: dickes Rohr (60 %) + dünne Kolbenstange."""
        m = (a[0] + (b[0] - a[0]) * 0.6, a[1] + (b[1] - a[1]) * 0.6)
        return self.beam(a, m, w * 0.8, INK, INK, 1) + self.beam(m, b, w * 0.35, INK, INK, 1)

    def kette(self, a, b, n=None):
        # schlicht: Kette als Punktlinie
        return ('<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-dasharray="0.1 5" %s/>'
                % (a[0], a[1], b[0], b[1], INK, NS))

    # --- Text (Pixel)
    def text(self, p_px, s, size=22, weight=500, anchor='start', fill=INK):
        self.t.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="%d" text-anchor="%s" fill="%s">%s</text>'
                      % (p_px[0], p_px[1], size, weight, anchor, fill, s))

    def label(self, ziel_m, text_px, s, anchor='start', nr=None):
        """Beschriftung mit Führungslinie vom Bauteil (Meter) zum Text (Pixel)."""
        z = self.px(ziel_m)
        tx, ty = text_px
        # Linie endet knapp vor dem Text
        ex = tx - 8 if anchor == 'start' else (tx + 8 if anchor == 'end' else tx)
        ey = ty - 7
        self.t.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.4"/>' % (z[0], z[1], ex, ey, INK))
        self.t.append('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s"/>' % (z[0], z[1], INK))
        self.text((tx, ty), s, 21, 500, anchor)

    def labelv(self, ziel_m, tx, ty, s, anchor='middle'):
        """Beschriftung: Text bei (tx, ty) in Pixeln, Führungslinie vom Bauteil bis knapp über/unter den Text."""
        z = self.px(ziel_m)
        if anchor == 'middle':
            ey = ty - 19 if ty > z[1] else ty + 7
            ex = tx
        else:   # seitlich: Linie endet links/rechts vom Text auf Mitte der Zeile
            ex = tx - 8 if anchor == 'start' else tx + 8
            ey = ty - 7
        self.t.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>' % (z[0], z[1], ex, ey, MID))
        self.t.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s" stroke="#fff" stroke-width="1"/>' % (z[0], z[1], INK))
        self.text((tx, ty), s, 15, 500, anchor)

    def bemassung(self, a_m, b_m, s, seite=1):
        """Senkrechtes Maß zwischen zwei Punkten gleicher x-Lage."""
        a, b = self.px(a_m), self.px(b_m)
        x = a[0]
        self.t.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" marker-start="url(#pf)" marker-end="url(#pf)"/>' % (x, a[1], x, b[1], INK))
        self.text((x + 10 * seite, (a[1] + b[1]) / 2 + 7), s, 20, 600, 'start' if seite > 0 else 'end')

    def boden(self, x0, x1):
        self.add(self.line((x0, 0), (x1, 0), INK, 1.5))


# ------------------------------------------------------------------ Fahrzeug
def lkw(sz, achsen, rahmen_ende, kabine_hoehe=3.15):
    """Frontlenker-LKW als schlichte Silhouette, Front bei x=0, fährt nach links."""
    a = sz.add
    h = kabine_hoehe
    a(sz.poly([(0.3, 0.8), (rahmen_ende, 0.8), (rahmen_ende, 1.08), (0.3, 1.08)], INK, INK, 1))
    kab = [(0.05, 0.62), (0.0, 1.9), (0.08, h - 0.12), (0.3, h), (2.22, h), (2.25, 0.62)]
    a(sz.poly(kab, INK, INK, 1))
    a(sz.poly([(0.85, 1.95), (0.88, h - 0.3), (1.95, h - 0.3), (1.95, 1.95)], PALE, PALE, 1))
    for x in achsen:
        a(sz.circ((x, 0.5), 0.5, INK, '#fff', 1))
        a(sz.circ((x, 0.5), 0.17, '#fff', '#fff', 1))


# ------------------------------------------------------------------ Abrollkipper
# Kennwerte (angelehnt an 26-t-Abrollkipper, Behälter 6,4 m, Bügelhöhe 1.570 mm nach DIN 30722-1)
AB = dict(achsen=[1.4, 5.1, 6.45], rahmen=8.05,
          P=(7.78, 1.27),      # Kipplager hinten
          K=(5.9, 1.33),       # Knickgelenk
          C=(2.68, 1.33),      # Ecke Hakenarm
          H=(2.56, 3.0),       # Haken (Bügelmitte)
          rolle=(8.0, 1.3), rr=0.13,
          L=6.4, BH=1.57)


def abroll_behaelter(sz, F, beta, voll=True):
    """Abrollbehälter, F = vordere Unterkante (Längsträger), beta = Neigung (Grad, + = Front höher)."""
    L = AB['L']
    def T(lx, ly):   # lokale Koordinaten -> Welt
        return rot((F[0] + lx, F[1] + ly), F, -beta)
    a = sz.add
    # Längsträger
    a(sz.poly([T(0, 0), T(L, 0), T(L, 0.14), T(0, 0.14)], '#4a4a4a', INK, 1.6))
    # Mulde
    mulde = [T(0.1, 0.14), T(L - 0.05, 0.14), T(L - 0.05, 1.72), T(0.32, 1.72), T(0.1, 1.45)]
    a(sz.poly(mulde, PALE, INK, 2.2))
    for i in range(1, 9):
        x = 0.32 + i * (L - 0.4) / 9
        a(sz.line(T(x, 0.2), T(x, 1.66), '#b5b5b5', 1.2))
    a(sz.line(T(0.3, 1.6), T(L - 0.1, 1.6), '#9a9a9a', 1.2))
    # Ladung
    if voll:
        a(sz.poly([T(0.4, 1.72), T(1.0, 1.95), T(2.0, 1.86), T(3.2, 2.02), T(4.5, 1.9), T(5.6, 1.98), T(L - 0.15, 1.72)], '#a3a3a3', INK, 1.4))
    # Bügel mit Stütze vorn
    a(sz.beam(T(0.12, 0.14), T(-0.12, AB['BH']), 0.1, '#5a5a5a', INK, 1.4))
    a(sz.circ(T(-0.12, AB['BH']), 0.07, '#fff', INK, 2))
    # Behälterrollen hinten
    a(sz.circ(T(L - 0.25, -0.02), 0.13, '#2b2b2b', INK, 1.5))
    a(sz.circ(T(L - 0.25, -0.02), 0.05, '#bbb', INK, 1))
    return T


def abroll_lkw(sz, knick=0.0, kipp=0.0):
    """Abrollkipper mit Hakenarm. knick = Drehung Hakenarm um Knickgelenk (Grad, im Uhrzeigersinn),
    kipp = Drehung Kipprahmen um Kipplager (Grad, im Uhrzeigersinn)."""
    P, K, C, H = AB['P'], AB['K'], AB['C'], AB['H']
    lkw(sz, AB['achsen'], AB['rahmen'])
    a = sz.add
    # Hilfsrahmen
    a(sz.poly([(2.5, 1.08), (8.05, 1.08), (8.05, 1.24), (2.5, 1.24)], '#a9a9a9', INK, 1.8))
    # Heckrolle
    a(sz.circ(AB['rolle'], AB['rr'], '#d0d0d0', INK, 1.8))
    a(sz.circ(AB['rolle'], 0.04, INK, INK, 1))

    def K2(p):   # Kippen um P
        return rot(p, P, -kipp)

    def A2(p):   # Knick um K, dann Kippen
        return K2(rot(p, K, -knick))

    # Kippzylinder: Hilfsrahmen vorn -> Kipprahmen
    a(sz.zylinder((3.35, 1.15), K2((5.7, 1.26)), 0.11))
    # Kipprahmen K..P
    a(sz.beam(K2(K), K2(P), 0.15, '#777', INK, 1.8))
    # Knickzylinder: Kipprahmen hinten -> Hakenarm
    a(sz.zylinder(K2((7.4, 1.17)), A2((4.8, 1.3)), 0.11))
    # Hakenarm: langer Arm C..K, Hakenteil C..H
    a(sz.beam(A2(C), A2(K), 0.16, '#3d3d3d', INK, 1.8))
    a(sz.beam(A2((C[0], C[1] - 0.08)), A2((H[0] - 0.12, H[1] - 0.06)), 0.17, '#3d3d3d', INK, 1.8))
    # Haken: legt sich von vorn über den Bügel
    bogen = [A2((H[0] + 0.14 * math.cos(math.radians(f)), H[1] + 0.14 * math.sin(math.radians(f)))) for f in range(200, -41, -15)]
    a('<polyline points="%s" fill="none" stroke="%s" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" %s/>' % (pts(bogen), INK, NS))
    a(sz.circ(K2(K), 0.07, '#fff', INK, 2))
    a(sz.circ(P, 0.08, '#fff', INK, 2))
    return K2, A2


def abroll_pose(knick):
    """Lage des Behälters, wenn der Haken bei 'knick' im Bügel hängt.
    Behälter liegt hinten mit den Rollen auf dem Boden und vorn auf der Heckrolle bzw. hängt am Haken."""
    P, K, H = AB['P'], AB['K'], AB['H']
    hk = rot(H, K, -knick)
    L, BH = AB['L'], AB['BH']
    rolle_oben = (AB['rolle'][0], AB['rolle'][1] + AB['rr'])
    best = None
    for i in range(0, 900):
        beta = i * 0.05          # Grad, Front höher
        b = math.radians(beta)
        d = (math.cos(b), -math.sin(b))
        n = (math.sin(b), math.cos(b))
        F = (hk[0] + 0.12 * d[0] - BH * n[0], hk[1] + 0.12 * d[1] - BH * n[1])
        rear = (F[0] + (L - 0.25) * d[0] - 0.15 * n[0], F[1] + (L - 0.25) * d[1] - 0.15 * n[1])
        err = abs(rear[1])
        if best is None or err < best[0]:
            best = (err, beta, F)
    return best[2], best[1]


def abroll_riegel(sz, kipp=0.0):
    """Hydraulische Verriegelung hinten: greift über den Längsträger des Behälters."""
    P = AB['P']
    q = [rot(p, P, -kipp) for p in [(7.28, 1.24), (7.4, 1.24), (7.4, 1.63), (7.16, 1.63), (7.16, 1.55), (7.28, 1.55)]]
    sz.add(sz.poly(q, '#222', INK, 1.4))


def kachel(out, x0, y0, pw, ph, nr, t, sub=''):
    """Schritt-Kachel für die 760-px-Spalte: eckige Nummer + kurzer Titel, Haarlinie."""
    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="rgba(38,38,38,0.14)" stroke-width="1"/>' % (x0 + 3, y0 + 3, pw - 6, ph - 6))
    out.append('<rect x="%d" y="%d" width="24" height="24" fill="%s"/><text x="%d" y="%d" font-size="14" font-weight="600" fill="#fff" text-anchor="middle">%s</text>' % (x0 + 16, y0 + 16, INK, x0 + 28, y0 + 33, nr))
    out.append('<text x="%d" y="%d" font-size="16" font-weight="600" fill="%s">%s</text>' % (x0 + 50, y0 + 34, INK, t))


def bild_abroll_aufbau():
    W, Hh = 760, 440
    sz = Szene(55, 325, 70)
    sz.boden(-0.6, 9.9)
    abroll_lkw(sz)
    abroll_behaelter(sz, (2.68, 1.43), 0)
    abroll_riegel(sz)
    P, K = AB['P'], AB['K']
    sz.labelv((2.5, 3.06), 240, 38, 'Haken im Bügel')
    sz.labelv((5.8, 2.4), 470, 38, 'Abrollbehälter')
    sz.labelv((2.62, 2.2), 242, 372, 'Hakenarm')
    sz.labelv(K, 480, 372, 'Knickgelenk')
    sz.labelv(AB['rolle'], 668, 372, 'Heckrolle')
    sz.labelv((4.9, 1.27), 380, 404, 'Hydraulikzylinder')
    sz.labelv(P, 588, 404, 'Kipplager')
    xm = 3.4
    for yy in (1.43, 3.0):
        sz.t.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>' % (*sz.px((2.55, yy)), *sz.px((xm + 0.12, yy)), DARK))
    sz.bemassung((xm, 1.43), (xm, 3.0), '', 1)
    p = sz.px((xm, 2.2))
    sz.text((p[0] + 10, p[1] - 3), 'Bügelhöhe', 15, 600, 'start')
    sz.text((p[0] + 10, p[1] + 16), '1.570 mm', 15, 600, 'start')
    return W, Hh, sz.svg(), 'Abrollkipper im Schnitt'


def bild_abroll_ablauf():
    pw = 380
    rows = [(175, 19.5), (245, 25)]
    W, Hh = 760, rows[0][0] + rows[1][0]
    F1, b1 = abroll_pose(151.6)
    F2, b2 = abroll_pose(108)
    specs = [('1', 'Haken einhängen', 151.6, 0, F1, b1), ('2', 'Aufziehen', 108, 0, F2, b2),
             ('3', 'Fahren', 0, 0, (2.68, 1.43), 0), ('4', 'Kippen', 0, 50, None, 0)]
    out = []
    for i, (nr, t, knick, kipp, F, beta) in enumerate(specs):
        col, row = i % 2, i // 2
        ph, s = rows[row]
        x0, y0 = col * pw, (0 if row == 0 else rows[0][0])
        sz = Szene(x0 + (14 if row == 0 else 70), y0 + ph - 18, s)
        sz.boden(-0.4, (17.6 if row == 0 else 11.4))
        abroll_lkw(sz, knick, kipp)
        if nr == '4':
            P = AB['P']
            Tk = abroll_behaelter(sz, rot((2.68, 1.43), P, -kipp), kipp)
            abroll_riegel(sz, kipp)
            q = Tk(AB['L'] + 0.05, 1.1)
            gx = q[0] + 0.45
            sz.add(sz.poly([(gx - 0.8, 0), (gx + 0.9, 0), (gx + 0.45, 0.42), (gx - 0.25, 0.46)], '#a3a3a3', INK, 1))
        else:
            abroll_behaelter(sz, F, beta)
            if nr == '3':
                abroll_riegel(sz)
        kachel(out, x0, y0, pw, ph, nr, t)
        out.append(sz.svg())
    return W, Hh, ''.join(out), 'Abrollkipper: Ablauf in vier Schritten'


# ------------------------------------------------------------------ Absetzkipper
AS = dict(achsen=[1.35, 4.85], rahmen=6.25,
          Q=(6.45, 1.22),       # Drehpunkt der Schwenkarme
          LA=3.4,               # Armlänge
          zyl_fuss=(4.3, 1.05), zyl_arm=1.75,
          bu=2.7, to=3.7, hoehe=1.45,
          zapfen=(1.7, 1.25), kipplager=(-1.32, 0.18))


def absetz_mulde(sz, M, deg=0.0, voll=True, dreh=None):
    """Absetzmulde, M = Mitte Unterkante, deg = Drehung (Grad, + = gegen Uhrzeigersinn) um 'dreh' (lokal, Standard M)."""
    bu, to, h = AS['bu'] / 2, AS['to'] / 2, AS['hoehe']
    dz = dreh or (0.0, 0.0)
    c = (M[0] + dz[0], M[1] + dz[1])
    def T(lx, ly):
        return rot((M[0] + lx, M[1] + ly), c, deg)
    a = sz.add
    a(sz.poly([T(-bu, 0), T(bu, 0), T(to, h), T(-to, h)], PALE, INK, 2.2))
    a(sz.poly([T(-to, h), T(to, h), T(to - 0.04, h - 0.12), T(-to + 0.04, h - 0.12)], '#9a9a9a', INK, 1.2))
    for i in range(1, 6):
        x = -bu + i * (2 * bu) / 6
        a(sz.line(T(x, 0.05), T(x * (to / bu) * 0.97, h - 0.14), '#b5b5b5', 1.2))
    a(sz.poly([T(-bu - 0.05, -0.08), T(bu + 0.05, -0.08), T(bu + 0.05, 0.02), T(-bu - 0.05, 0.02)], '#4a4a4a', INK, 1.2))
    if voll:
        a(sz.poly([T(-to + 0.1, h), T(-1.0, h + 0.25), T(0.0, h + 0.16), T(0.9, h + 0.28), T(to - 0.1, h)], '#a3a3a3', INK, 1.4))
    zx, zy = AS['zapfen']
    for sx in (-1, 1):
        a(sz.circ(T(sx * zx, zy), 0.075, '#fff', INK, 2.2))
    kx, ky = AS['kipplager']
    a(sz.poly([T(kx - 0.08, ky - 0.08), T(kx + 0.08, ky - 0.08), T(kx + 0.08, ky + 0.08), T(kx - 0.08, ky + 0.08)], '#666', INK, 1.2))
    return T


def absetz_tip(winkel):
    Q, LA = AS['Q'], AS['LA']
    return (Q[0] + LA * math.cos(math.radians(winkel)), Q[1] + LA * math.sin(math.radians(winkel)))


def absetz_lkw(sz, stuetze=True):
    """Fahrgestell, Grundrahmen und Abstützung (Arme separat, damit sie vor der Mulde liegen)."""
    lkw(sz, AS['achsen'], AS['rahmen'])
    a = sz.add
    a(sz.poly([(2.45, 1.08), (6.6, 1.08), (6.6, 1.28), (2.45, 1.28)], '#a9a9a9', INK, 1.8))
    a(sz.poly([(5.9, 0.75), (6.75, 0.75), (6.75, 1.3), (5.9, 1.3)], '#8f8f8f', INK, 1.6))
    if stuetze:
        a(sz.beam((6.62, 0.85), (6.62, 0.08), 0.13, '#5b5b5b', INK, 1.6))
        a(sz.poly([(6.42, 0.0), (6.82, 0.0), (6.82, 0.08), (6.42, 0.08)], '#2b2b2b', INK, 1.2))
    else:
        a(sz.beam((6.62, 0.85), (6.62, 0.55), 0.13, '#5b5b5b', INK, 1.6))


def absetz_arme(sz, winkel):
    Q = AS['Q']
    tip = absetz_tip(winkel)
    za = (Q[0] + AS['zyl_arm'] * math.cos(math.radians(winkel)), Q[1] + AS['zyl_arm'] * math.sin(math.radians(winkel)))
    sz.add(sz.zylinder(AS['zyl_fuss'], za, 0.16))
    sz.add(sz.beam(Q, tip, 0.24, '#3d3d3d', INK, 1.8))
    m = (Q[0] + 2.2 * math.cos(math.radians(winkel)), Q[1] + 2.2 * math.sin(math.radians(winkel)))
    sz.add(sz.beam(m, tip, 0.18, '#555', INK, 1.4))
    sz.add(sz.circ(Q, 0.09, '#fff', INK, 2.2))
    sz.add(sz.circ(tip, 0.07, '#fff', INK, 2))
    return tip, za


def haengend(tip):
    zx, zy = AS['zapfen']
    return (tip[0], tip[1] - math.sqrt(2.1 ** 2 - zx ** 2) - zy)


def arm_fuer(Mx, My):
    zx, zy = AS['zapfen']
    ty = My + zy + math.sqrt(2.1 ** 2 - zx ** 2)
    return min((math.hypot(absetz_tip(i * 0.1)[0] - Mx, absetz_tip(i * 0.1)[1] - ty), i * 0.1) for i in range(1800))[1]


def ketten(sz, tip, T):
    zx, zy = AS['zapfen']
    sz.add(sz.kette(tip, T(-zx, zy)))
    sz.add(sz.kette(tip, T(zx, zy)))


def kipp_lage(deg=-118, abstand=0.55, boden=0.3):
    """Kipp-Stellung: Mulde hängt mit dem Kipplager 'abstand' unter der Armspitze, um 'deg' gedreht.
    Gesucht wird der kleinste Armwinkel, bei dem die Mulde 'boden' Meter Bodenfreiheit hat."""
    kx, ky = AS['kipplager']
    bu, to, h = AS['bu'] / 2, AS['to'] / 2, AS['hoehe']
    ecken = [(-bu, 0), (bu, 0), (to, h), (-to, h)]
    for i in range(300, 900):
        w = i * 0.1
        tip = absetz_tip(w)
        kl = (tip[0], tip[1] - abstand)
        M = (kl[0] - kx, kl[1] - ky)
        ys = [rot((M[0] + x, M[1] + y), kl, deg)[1] for x, y in ecken]
        if min(ys) >= boden:
            return w, M
    return 90, M


def bild_absetz_aufbau():
    W, Hh = 760, 400
    sz = Szene(40, 310, 58)
    sz.boden(-0.4, 12.2)
    w = arm_fuer(9.6, 0.0)
    absetz_lkw(sz, True)
    T = absetz_mulde(sz, (9.6, 0.0))
    tip, za = absetz_arme(sz, w)
    ketten(sz, tip, T)
    Q = AS['Q']
    zm = ((AS['zyl_fuss'][0] + za[0]) / 2, (AS['zyl_fuss'][1] + za[1]) / 2 + 0.02)
    zx, zy = AS['zapfen']
    arm_p = (Q[0] + 1.3 * math.cos(math.radians(w)), Q[1] + 1.3 * math.sin(math.radians(w)) + 0.05)
    kmid = ((tip[0] + T(-zx, zy)[0]) / 2, (tip[1] + T(-zx, zy)[1]) / 2)
    sz.labelv(arm_p, 400, 70, 'Schwenkarm')
    sz.labelv(kmid, 560, 70, 'Ketten')
    sz.labelv(T(zx, zy), 690, 70, 'Tragzapfen')
    sz.labelv(zm, 300, 362, 'Hubzylinder')
    sz.labelv((6.62, 0.4), 450, 362, 'Abstützung')
    sz.labelv(T(0.4, 0.75), 615, 362, 'Absetzmulde')
    return W, Hh, sz.svg(), 'Absetzkipper im Schnitt'


def bild_absetz_ablauf():
    pw, ph = 380, 190
    W, Hh = 760, 2 * ph
    out = []
    w1 = arm_fuer(9.6, 0.0)
    w3 = arm_fuer(4.25, 1.3)
    wk, Mk = kipp_lage()
    specs = [
        ('1', 'Einhängen', 'Stützen ab, Arme nach hinten, Ketten an die Tragzapfen.', w1, True, 'boden'),
        ('2', 'Anheben', 'Die Hubzylinder schwenken die Arme, die Mulde hängt frei.', 80, True, 'haengt'),
        ('3', 'Fahren', 'Die Mulde steht auf dem Aufbau, Stützen eingefahren.', w3, False, 'auf'),
        ('4', 'Auskippen', 'Ketten im Kipplager: Die Mulde dreht sich und kippt nach hinten aus.', wk, True, 'kipp'),
    ]
    for i, (nr, t, sub, w, st, art) in enumerate(specs):
        col, row = i % 2, i // 2
        x0, y0 = col * pw, row * ph
        sz = Szene(x0 + 18, y0 + ph - 18, 25)
        sz.boden(-0.4, 13.8)
        absetz_lkw(sz, st)
        tip = absetz_tip(w)
        if art == 'boden':
            T = absetz_mulde(sz, (9.6, 0.0))
        elif art == 'auf':
            T = absetz_mulde(sz, (4.25, 1.3))
        elif art == 'haengt':
            T = absetz_mulde(sz, haengend(tip))
        else:
            kx, ky = AS['kipplager']
            T = absetz_mulde(sz, Mk, -118, voll=False, dreh=(kx, ky))
        absetz_arme(sz, w)
        if art == 'kipp':
            zx, zy = AS['zapfen']
            sz.add(sz.kette(tip, T(kx, ky)))
            # hintere Kette hängt locker
            rp = T(zx, zy)
            mid = ((tip[0] + rp[0]) / 2 + 0.35, (tip[1] + rp[1]) / 2)
            sz.add(sz.kette(tip, mid)); sz.add(sz.kette(mid, rp))
            o1, o2 = T(-AS['to'] / 2, AS['hoehe']), T(AS['to'] / 2, AS['hoehe'])
            ox = max(o1[0], o2[0]) + 0.1
            oy = min(o1[1], o2[1])
            sz.add(sz.poly([(ox - 0.6, 0), (ox + 1.2, 0), (ox + 0.7, 0.4), (ox + 0.05, 0.42)], '#a3a3a3', INK, 1.4))
        else:
            ketten(sz, tip, T)
        kachel(out, x0, y0, pw, ph, nr, t)
        out.append(sz.svg())
    return W, Hh, ''.join(out), 'Absetzkipper: Ablauf in vier Schritten'



# ------------------------------------------------------------------ Ausgabe
def svg_datei(W, H, inhalt, titel):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="DM Sans, Arial, sans-serif">'
            '<title>%s</title><defs><marker id="pf" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M0,1 L9,5 L0,9 z" fill="%s"/></marker></defs>'
            '<rect width="100%%" height="100%%" fill="#fff"/>%s</svg>') % (W, H, W, H, titel, INK, inhalt)


def render(name, W, H, svg, nur_svg=False):
    tmp = tempfile.mkdtemp()
    svgp = os.path.join(tmp, name + '.svg')
    open(svgp, 'w', encoding='utf-8').write(svg)
    if nur_svg:
        print(svgp); return svgp
    html = os.path.join(tmp, name + '.html')
    open(html, 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8"><style>@font-face{font-family:"DM Sans";src:url("file://%s") format("woff2");font-weight:100 1000}'
        '@font-face{font-family:"DM Sans";src:url("file://%s") format("woff2");font-weight:100 1000}'
        'html,body{margin:0;background:#fff}</style>%s' % (FONT, FONT_EXT, svg))
    png = os.path.join(tmp, name + '.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    '--force-device-scale-factor=2.5', '--window-size=%d,%d' % (W, H), '--virtual-time-budget=3000',
                    '--screenshot=' + png, 'file://' + html], check=True, capture_output=True)
    from PIL import Image
    im = Image.open(png).convert('RGB')
    ziel = os.path.join(IMG, name + '.webp')
    im.save(ziel, 'WEBP', quality=90, method=6)
    print(ziel, im.size)
    return ziel


def main():
    nur_svg = '--nur-svg' in sys.argv
    for name, f in [('blog-abrollkipper-aufbau', bild_abroll_aufbau), ('blog-abrollkipper-ablauf', bild_abroll_ablauf),
                    ('blog-absetzkipper-aufbau', bild_absetz_aufbau), ('blog-absetzkipper-ablauf', bild_absetz_ablauf)]:
        W, H, inhalt, titel = f()
        render(name, W, H, svg_datei(W, H, inhalt, titel), nur_svg)


if __name__ == '__main__':
    main()
