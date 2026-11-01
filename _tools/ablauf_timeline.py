#!/usr/bin/env python3
"""Baut die Ablauf-Schritte aller Seiten zur Zeitleiste (.timeline) um.

Liest Titel und Text je Schritt aus der Seite (alte .steps- oder neue
.timeline-Liste) und setzt je Schritt eine Karte mit Bildfläche
(Mockup aus HTML/CSS oder Hof-Foto) ein. Idempotent.
Aufruf (im Repo-Ordner): python3 _tools/ablauf_timeline.py
"""
import os, re, sys, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img', 'opt')

# ------------------------------------------------------------------ Icons
ICON = {
    'chat':  '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'doc':   '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h6M9 16h6"/>',
    'truck': '<path d="M2 6h12v10H2z"/><path d="M14 9h4l4 4v3h-8z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    'pin':   '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    'key':   '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
    'firm':  '<path d="M4 21V5h10v16M14 9h6v12M2 21h20"/><path d="M7 9h1M10 9h1M7 13h1M10 13h1M7 17h1M10 17h1"/>',
    'id':    '<path d="M3 5h18v14H3z"/><circle cx="9" cy="11" r="2.2"/><path d="M5.5 16c.8-1.8 2-2.5 3.5-2.5s2.7.7 3.5 2.5M14.5 10h4M14.5 13.5h4"/>',
    'list':  '<path d="M4 4h16v16H4zM4 9h16M4 14h16M10 4v16"/>',
    'scan':  '<path d="M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4M7 12h10"/>',
    'cal':   '<path d="M4 5h16v15H4zM4 10h16M9 3v4M15 3v4"/>',
    'shield':'<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'euro':  '<path d="M17 6.5A6.5 6.5 0 1 0 17 17.5M4 10.5h9M4 13.5h9"/>',
}


def svg(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="square">' + ICON[name] + '</svg>')


def ico(name):
    return '<span class="mk-ico">' + svg(name) + '</span>'


def tick(on=True):
    return '<span class="mk-tick' + ('' if on else ' mk-tick--off') + '">' + (svg('check') if on else '') + '</span>'


def lines(*widths):
    return '<span class="mk-lines">' + ''.join('<i style="width:%d%%"></i>' % w for w in widths) + '</span>'


def esc(s):
    return html.escape(s, quote=False)


def nt(s):
    """Sprachneutrale Angabe (Modell, Zahl) – nicht übersetzen."""
    return '<span data-no-i18n>' + esc(s) + '</span>'


# ------------------------------------------------------------------ Fotos
def widths(name):
    ws = set()
    for f in glob.glob(os.path.join(IMG, name + '-*.jpg')):
        m = re.search(r'-(\d+)\.jpg$', f)
        if m:
            ws.add(int(m.group(1)))
    if not ws:
        raise SystemExit('Foto fehlt: ' + name)
    return sorted(ws)


def photo(name, cls='mk-photo', pos='50% 50%', sizes='(max-width: 991px) 92vw, 600px'):
    ws = widths(name)
    def ss(ext):
        return ', '.join('assets/img/opt/%s-%d.%s %dw' % (name, w, ext, w) for w in ws)
    big = ws[-1]
    return ('<picture>'
            '<source type="image/avif" srcset="%s" sizes="%s">'
            '<source type="image/webp" srcset="%s" sizes="%s">'
            '<img class="%s" src="assets/img/opt/%s-%d.jpg" srcset="%s" sizes="%s" alt="" '
            'style="object-position: %s" loading="lazy" decoding="async">'
            '</picture>') % (ss('avif'), sizes, ss('webp'), sizes, cls, name, big, ss('jpg'), sizes, pos)


def thumb(name, crop):
    """crop: (Ausschnitt-Mitte x %, y %, Zoom) – drei Ansichten aus einem Foto."""
    w = widths(name)[0]
    x, y, z = crop
    return ('<span class="mk-thumb"><img src="assets/img/opt/%s-%d.webp" alt="" '
            'style="transform-origin: %d%% %d%%; scale: %s" loading="lazy" decoding="async"></span>') % (name, w, x, y, z)


# ------------------------------------------------------------------ Szenen
# Alle Maße in em: die Szene ist immer 40em × 25em (font-size 2.5cqw).
def scene(kind, inner):
    return ('<div class="tl-visual tl-visual--%s" aria-hidden="true"><div class="mk-scene">%s</div></div>'
            % (kind, inner))


def v_chat(veh, msg, pos=((50, 50, 1), (30, 45, 2.2), (75, 75, 2.6))):
    return scene('chat',
        '<span class="mk-ghost mk-ghost--1"></span><span class="mk-ghost mk-ghost--2"></span>'
        '<div class="mk-card mk-note mk-in">' + ico('chat') +
        '<div class="mk-note__text"><p class="mk-title">Neue Anfrage</p>'
        '<p class="mk-text">' + nt(msg) + '</p>'
        '<div class="mk-thumbs">' + ''.join(thumb(veh, p) for p in pos) + '<span>' + nt('+5') + '</span></div>'
        '</div><span class="mk-time">' + nt('09:41') + '</span></div>')


def v_check(veh, title, items, pos='50% 50%'):
    rows = ''.join('<li class="mk-in" style="--d:%dms">%s<span>%s</span></li>' % (150 + i * 140, tick(), esc(t))
                   for i, t in enumerate(items))
    return scene('check',
        '<div class="mk-photo-box">' + photo(veh, pos=pos) + '</div>'
        '<div class="mk-card mk-check"><p class="mk-title">' + esc(title) + '</p><ul>' + rows + '</ul></div>')


def sheet(bar, body, cls=''):
    return ('<div class="mk-sheet ' + cls + '"><div class="mk-bar">'
            '<img src="assets/img/opt/logo-ecs-360.webp" alt="" width="360" height="202" loading="lazy">'
            '<span>' + esc(bar) + '</span></div>' + body + '</div>')


def v_offer(bar, rows, sum_label, chip):
    body = lines(78, 92, 64)
    if rows:
        body += '<ul class="mk-rows">' + ''.join(
            '<li class="mk-in" style="--d:%dms"><span>%s</span>%s</li>' % (150 + i * 120, r, v)
            for i, (r, v) in enumerate(rows)) + '</ul>'
    body += ('<div class="mk-sum"><span>' + esc(sum_label) + '</span><b>' + nt('€ ••.•••') + '</b></div>')
    return scene('doc',
        '<span class="mk-sheet mk-sheet--ghost"></span>' + sheet(bar, body) +
        '<span class="mk-chip mk-chip--float mk-in" style="--d:350ms">' + tick() + esc(chip) + '</span>')


def v_sign(bar, labels, chip, stamp=None):
    sig = ('<svg class="mk-sig" viewBox="0 0 120 40" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"><path pathLength="1" d="M4 28c10-2 14-22 22-20 6 2-6 26 2 26 '
           '7 0 10-18 16-18 5 0 1 14 7 14 6 0 9-10 15-10 5 0 4 7 9 7 6 0 10-6 17-8 5-1 12 0 20 1"/></svg>')
    boxes = ''.join('<div class="mk-signbox">%s<span>%s</span></div>' % (sig if i == 0 or not stamp else '', esc(l))
                    for i, l in enumerate(labels))
    body = lines(88, 72, 94, 60) + ('<div class="mk-signs">' + boxes + '</div>' if labels else lines(80, 66, 90))
    if stamp:
        body += '<span class="mk-stamp mk-in" style="--d:450ms">' + esc(stamp) + '</span>'
    return scene('doc',
        '<span class="mk-sheet mk-sheet--ghost"></span>' + sheet(bar, body) +
        ('<span class="mk-chip mk-chip--float mk-in" style="--d:350ms">' + tick() + esc(chip) + '</span>' if chip else ''))


def v_photo(img, icon, title, sub, pos='50% 50%'):
    return scene('photo',
        photo(img, pos=pos) +
        '<div class="mk-card mk-badge mk-in">' + ico(icon) +
        '<div><p class="mk-title">' + esc(title) + '</p><p class="mk-text">' + esc(sub) + '</p></div></div>')


def v_route(start, end, chips=()):
    path = 'M5 19.5 C 14 19.5, 13 9, 22 10 S 30 6.5, 35 5.5'
    out = ('<svg class="mk-route" viewBox="0 0 40 25" fill="none" preserveAspectRatio="none">'
           '<path class="mk-route__base" d="' + path + '"/>'
           '<path class="mk-route__line" pathLength="1" d="' + path + '"/></svg>'
           '<div class="mk-card mk-pin mk-pin--a">' + ico('pin') + '<span>' + start + '</span></div>'
           '<div class="mk-card mk-pin mk-pin--b mk-in" style="--d:700ms">' + ico('pin') + '<span>' + end + '</span></div>'
           '<span class="mk-truck mk-in" style="--d:400ms">' + svg('truck') + '</span>')
    if chips:
        out += '<div class="mk-chips">' + ''.join('<span class="mk-chip">%s%s</span>' % (tick(), esc(c)) for c in chips) + '</div>'
    return scene('route', out)


def v_list(icon, title, rows, chip=None, cls=''):
    """rows: (label, 'tick' | 'bar' | html-Wert)"""
    li = []
    for i, (label, val) in enumerate(rows):
        if val == 'tick':
            right = tick()
        elif val == 'bar':
            right = '<i class="mk-val"></i>'
        else:
            right = '<b>' + val + '</b>'
        li.append('<li class="mk-in" style="--d:%dms"><span>%s</span>%s</li>' % (120 + i * 110, esc(label), right))
    return scene('list',
        '<span class="mk-ghost mk-ghost--1"></span>'
        '<div class="mk-card mk-listcard ' + cls + '"><div class="mk-listcard__head">' + ico(icon) +
        '<p class="mk-title">' + esc(title) + '</p>' +
        ('<span class="mk-chip">' + chip + '</span>' if chip else '') +
        '</div><ul>' + ''.join(li) + '</ul></div>')


FLEET = [('Actros 1845', '2018', '610.000', 'Hannover'),
         ('Atego 1224', '2019', '380.000', 'Hannover'),
         ('Sprinter 316 CDI', '2020', '190.000', 'Bremen'),
         ('TGX 18.470', '2017', '720.000', 'Hamburg')]


def v_table(title, checked=False):
    head = ['Fahrzeug', 'EZ', 'km', 'Bewertet' if checked else 'Standort']
    rows = ''
    for i, r in enumerate(FLEET):
        last = tick() if checked else nt(r[3])
        rows += ('<div class="mk-tr mk-in" style="--d:%dms"><span>%s</span><span>%s</span><span>%s</span><span>%s</span></div>'
                 % (120 + i * 110, nt(r[0]), nt(r[1]), nt(r[2]), last))
    return scene('table',
        '<div class="mk-card mk-table"><div class="mk-listcard__head">' + ico('list') +
        '<p class="mk-title">' + esc(title) + '</p><span class="mk-chip">' + nt('.xlsx') + '</span></div>'
        '<div class="mk-tr mk-th">' + ''.join('<span>%s</span>' % esc(h) for h in head) + '</div>' + rows + '</div>')


def v_passport():
    mrz = '&lt;' * 30
    return scene('id',
        '<div class="mk-card mk-idcard"><p class="mk-idcard__head"><span>Reisepass</span>' + nt('EU') + '</p>'
        '<div class="mk-idcard__body"><span class="mk-idcard__photo">' + svg('id') + '</span>' + lines(70, 90, 55, 80, 62) + '</div>'
        '<p class="mk-mrz" data-no-i18n>' + mrz + '<br>' + mrz + '</p></div>'
        '<span class="mk-chip mk-chip--float mk-in" style="--d:350ms">' + tick() + 'Kopie</span>')


def v_plate():
    return scene('plate',
        '<div class="mk-plate mk-in" data-no-i18n><span class="mk-plate__eu">D</span>'
        '<span class="mk-plate__nr">H 0123A</span><span class="mk-plate__date">11<br>26</span></div>'
        '<div class="mk-chips">' + ''.join('<span class="mk-chip mk-in" style="--d:%dms">%s%s</span>' % (250 + i * 120, tick(), esc(c))
                                           for i, c in enumerate(['Hauptuntersuchung', 'Versicherung', 'Tieflader', 'Verschiffung'])) + '</div>')


def v_customs():
    body = (lines(80, 66) + '<span class="mk-barcode"></span>' + lines(90, 74, 52) +
            '<span class="mk-stamp mk-stamp--big mk-in" style="--d:400ms">Zoll<small>' + nt('✓') + '</small></span>')
    return scene('doc tl-visual--wide', '<span class="mk-sheet mk-sheet--ghost"></span>' + sheet('Ausfuhrbegleitdokument', body))


def v_exit():
    return scene('exit',
        '<span class="mk-sheet mk-sheet--ghost"></span>'
        '<div class="mk-card mk-exit mk-in"><span class="mk-exit__icon">' + svg('shield') + '</span>'
        '<p class="mk-title">Ausgangsvermerk</p><p class="mk-text">Ausgang bestätigt</p>' + lines(84, 62) + '</div>')


def v_schedule(img, pos='50% 50%'):
    stages = [(1, 4, True), (2, 3, False), (3, 5, False)]
    rows = ''.join('<li class="mk-in" style="--d:%dms">%s<span>Etappe %s</span><b>%s Fahrzeuge</b></li>'
                   % (150 + i * 140, tick(on), nt(str(n)), nt(str(c))) for i, (n, c, on) in enumerate(stages))
    return scene('check',
        '<div class="mk-photo-box">' + photo(img, pos=pos) + '</div>'
        '<div class="mk-card mk-check mk-check--wide"><p class="mk-title">Gestaffelte Abholung</p><ul>' + rows + '</ul></div>')


ANKAUF_CHECK = ['Ausstattung', 'Laufleistung', 'Wartungshistorie', 'Nachfrage']
ECS = 'ECS GmbH'


def ankauf(veh, msg, vpos='50% 50%', pick=None, ppos='50% 50%', check=ANKAUF_CHECK, thumbs=None, what='Fahrzeug'):
    t = thumbs or ((50, 50, 1), (30, 45, 2.2), (75, 75, 2.6))
    if pick:
        last = v_photo(pick, 'truck', 'Abholung', 'Deutschlandweit', ppos)
    else:
        last = v_route('Ihr Standort', nt(ECS))
    return [
        v_chat(veh, msg, t),
        v_check(veh, 'Bewertung', check, vpos),
        v_offer('Angebot', None, 'Ankaufpreis', 'Unverbindlich'),
        v_sign('Kaufvertrag', ['Verkäufer', 'Käufer'], 'Verbindlich vereinbart'),
        last,
    ]


PAGES = {
    'lkw-verkaufen.html': ankauf('ablauf-man-tgx', 'MAN TGX 18.510 · 2019 · 540.000 km', '33% 50%',
                                 pick='ablauf-axor-gruen', ppos='50% 60%',
                                 check=['Angaben', 'Aufbau', 'Betriebsstunden', 'Prüfnachweise']),
    'reisebus-verkaufen.html': ankauf('reisebus-magelys', 'Iveco Magelys · 2017 · 610.000 km', '50% 50%'),
    'linienbus-verkaufen.html': ankauf('angebot-linienbus-citaro', 'Mercedes-Benz Citaro · 2015 · 720.000 km', '50% 50%'),
    'transporter-verkaufen.html': ankauf('bewertung-sprinter', 'Mercedes-Benz Sprinter · 2020 · 180.000 km', '50% 50%'),
    'bau-und-kommunalfahrzeuge-verkaufen.html': ankauf('angebot-radlader-cat', 'Caterpillar 950 · 2016 · 9.800 h', '50% 50%',
                                 pick='ablauf-axor-gruen', ppos='50% 60%'),
    'unsere-arbeit.html': ankauf('ablauf-man-tgx', 'MAN TGX 18.510 · 2019 · 540.000 km', '33% 50%',
                                 pick='ablauf-axor-gruen', ppos='50% 60%'),
    'fuhrpark-verkaufen.html': [
        v_table('Fahrzeugliste'),
        v_table('Bewertung', checked=True),
        v_offer('Paketangebot', [('Fahrzeug ' + nt('01'), nt('€ ••.•••')), ('Fahrzeug ' + nt('02'), nt('€ ••.•••')),
                                 ('Fahrzeug ' + nt('03'), nt('€ ••.•••'))], 'Gesamtangebot', 'Werte je Fahrzeug'),
        v_sign('Kaufvertrag', ['Verkäufer', 'Käufer'], 'Ein Vertrag für alle Fahrzeuge'),
        v_schedule('kontakt-atego-reihe', '50% 62%'),
    ],
    'export.html': [
        v_chat('export-eu-actros-rot', 'Mercedes-Benz Actros · DE → GE'),
        v_offer('Angebot', [('Fahrzeug', tick()), ('Exportpapiere', tick()), ('Transport', tick())], 'Gesamtpreis', 'Unverbindlich'),
        v_list('doc', 'Ausfuhrpapiere', [('Rechnung', 'tick'), ('Fahrzeugpapiere', 'tick'), ('Zollabwicklung', 'tick'),
                                         ('EU oder Drittland', 'tick')]),
        v_route(nt('Gehrden'), 'Zielland', ['Straße', 'Verschiffung']),
        v_photo('export-eu-actros-rot', 'key', 'Übergabe', 'Mit allen Papieren', '50% 55%'),
    ],
    'export-eu.html': [
        v_list('firm', 'Firmendaten', [('Firmenanschrift', 'bar'), ('Telefon und Fax', 'bar'), ('E-Mail', 'bar'),
                                      ('Branche', 'bar'), ('Internetadresse', 'bar')]),
        v_list('scan', 'Umsatzsteuer-ID', [('USt-IdNr.', nt('EU ••• ••• •••')), ('Name', 'tick'), ('Anschrift', 'tick')],
               chip=nt('VIES')),
        v_sign('Firmennachweis', [], None, stamp='Kopie'),
        v_passport(),
        v_sign('Vollmacht', ['Inhaber', 'Fahrer'], None, stamp='Firmenstempel'),
    ],
    'export-drittland.html': [
        v_list('doc', 'Unterlagen', [('Käufer', 'tick'), ('Empfänger', 'tick'), ('Zielland', 'tick'),
                                     ('Reisepass oder Ausweis', 'tick'), ('Firmendaten', 'tick')]),
        v_list('scan', 'Ausfuhranmeldung', [('MRN', nt('26DE••••••••••••')), ('Zoll', nt('ATLAS')), ('Übermittelt', 'tick')],
               chip=nt('ATLAS')),
        v_customs(),
        v_plate(),
        v_exit(),
    ],
}

# ------------------------------------------------------------------ Umbau
LIST_RE = re.compile(r'(?P<indent>[ \t]*)<ol class="(?:steps reveal|timeline)"[^>]*>.*?</ol>', re.S)
STEP_RE = re.compile(r'<(?P<tag>h[23]) class="(?:step__label|tl-card__title)">(?P<title>.*?)</(?P=tag)>\s*'
                     r'<p class="(?:step__body|tl-card__body)">(?P<body>.*?)</p>', re.S)


def build(page, visuals):
    path = os.path.join(ROOT, page)
    src = open(path, encoding='utf-8').read()
    m = LIST_RE.search(src)
    if not m:
        raise SystemExit('Keine Schritt-Liste: ' + page)
    steps = STEP_RE.findall(m.group(0))
    if len(steps) != len(visuals):
        raise SystemExit('%s: %d Schritte, %d Bilder' % (page, len(steps), len(visuals)))
    ind = m.group('indent')
    out = [ind + '<ol class="timeline">']
    for i, ((tag, title, body), vis) in enumerate(zip(steps, visuals), 1):
        out.append('%s  <li class="tl-step" style="--n: %d">' % (ind, i))
        out.append('%s    <span class="tl-step__num" aria-hidden="true">%02d</span>' % (ind, i))
        out.append('%s    <article class="tl-card reveal">' % ind)
        out.append('%s      %s' % (ind, vis))
        out.append('%s      <%s class="tl-card__title">%s</%s>' % (ind, tag, title, tag))
        out.append('%s      <p class="tl-card__body">%s</p>' % (ind, body))
        out.append('%s    </article>' % ind)
        out.append('%s  </li>' % ind)
    out.append(ind + '</ol>')
    src = src[:m.start()] + '\n'.join(out) + src[m.end():]
    open(path, 'w', encoding='utf-8').write(src)
    print('ok', page, len(steps))


for page, visuals in PAGES.items():
    build(page, visuals)
