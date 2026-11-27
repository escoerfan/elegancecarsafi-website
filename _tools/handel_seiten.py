#!/usr/bin/env python3
"""Erzeugt die vier Handel-Seiten (15.11.2026):
/nutzfahrzeughandel, /lkw-handel, /omnibushandel, /baumaschinenhandel.

Kopfzeile, Fußzeile und Fotoblöcke kommen aus gebrauchte-nutzfahrzeuge.html,
das Design aus css/fahrzeugtypen.css. JSON-LD schreibt danach _tools/schema.py.
Regeln: keine Modellnamen, kein Zustand, keine Zahlungsart, keine internen Zahlen.

Aufruf:  python3 _tools/handel_seiten.py
"""
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMA = 'ECS Exclusive Commerce Services GmbH'
BASE = 'https://elegancecarsafi.com/'

# In mehreren Seiten gleich (ein Übersetzungsschlüssel)
BESTAND = ('Jedes verfügbare Fahrzeug steht mit Bildern, Daten und Preis im aktuellen Bestand. '
           'Eine Besichtigung auf unserem Hof ist nach Terminabsprache möglich.')
# Ankauf steht nur unter „Unsere Arbeit“; hier nur ein Verweis (15.11.: Menülogik)
ANKAUF_VERWEIS = 'Wie der Ankauf abläuft, was wir ankaufen und welche Unterlagen Sie brauchen, steht auf unseren Ankaufseiten.'
FAQ_SUCHE = ('Was ist, wenn das gewünschte Fahrzeug nicht im Bestand ist?',
             'Sprechen Sie uns an. Wir helfen Ihnen bei der Suche nach dem passenden Fahrzeug.')
EXPORT = 'Exportabwicklung, Ausfuhrpapiere und Transport organisieren wir auf Wunsch.'
KIPPER = 'Dreiseitenkipper, Hinterkipper, Absetz- und Abrollkipper für Bau und Entsorgung.'
FAQ_AUSLAND = ('Liefern Sie auch ins Ausland?',
               'Ja. Wir verkaufen an Unternehmen in der EU und exportieren in Drittländer. '
               'Auf Wunsch organisieren wir den Transport.')
FAQ_ZAHLUNG = ('Kann ich mein altes Fahrzeug in Zahlung geben?',
               'Ja, eine Inzahlungnahme ist möglich. Wir bewerten Ihr Fahrzeug und verrechnen den Wert mit dem Kaufpreis.')

NAMEN = {'nutzfahrzeughandel': 'Nutzfahrzeughandel', 'lkw-handel': 'LKW Handel',
         'omnibushandel': 'Omnibushandel', 'baumaschinenhandel': 'Baumaschinenhandel'}

# Zeile: (Titel, Text, Foto-Titel in gebrauchte-nutzfahrzeuge.html oder None, Link oder None)
SEITEN = {
    'nutzfahrzeughandel': dict(
        verkauf2='Unsere Käufer sind Speditionen, Busunternehmen, Bauunternehmen, Kommunen und Händler aus Deutschland und dem Ausland.',
        titel='Nutzfahrzeughandel: Ankauf, Verkauf und Export',
        beschreibung='Nutzfahrzeughandel der ECS GmbH bei Hannover: Ankauf, Verkauf und Export gebrauchter LKW, '
                     'Busse, Transporter und Baumaschinen. Deutschlandweit und international.',
        eyebrow='Nutzfahrzeughändler bei Hannover', h1='Nutzfahrzeughandel',
        lead='Ankauf, Verkauf und Export gebrauchter Nutzfahrzeuge.',
        intro='Die ECS GmbH ist ein Nutzfahrzeughandel bei Hannover. Wir verkaufen gebrauchte LKW, Busse, '
              'Transporter und Baumaschinen an Unternehmen im In- und Ausland.',
        # Kasten "Auf einen Blick" (17.11.2026, für Google und KI-Suchen; nur diese Handel-Seite)
        fakten=[('Wir handeln', 'Gebrauchte LKW, Busse, Transporter und Baumaschinen'),
                ('Für wen', 'Speditionen, Busunternehmen, Bauunternehmen, Kommunen und Händler im In- und Ausland'),
                ('Export', 'Ganz Europa, Asien und Afrika, auch VAE, Saudi-Arabien und weitere Golfstaaten'),
                ('Angebot', 'In der Regel innerhalb von 24 Stunden')],
        verkauf_h2='Gebrauchte Nutzfahrzeuge kaufen',
        verkauf='Als Nutzfahrzeughändler haben wir laufend gebrauchte LKW, Sattelzugmaschinen, Kipper, Auflieger, '
                'Transporter, Reisebusse, Linienbusse und Baumaschinen im Angebot. Die Fahrzeuge stammen von '
                'Mercedes-Benz, MAN, Scania, Volvo, DAF, Iveco und Setra.',
        ankauf_h2='Sie möchten ein Nutzfahrzeug verkaufen?',
        ankauf='Wir kaufen auch an: einzelne Fahrzeuge ebenso wie ganze Fuhrparks.',
        ankauf_links=[('nutzfahrzeug-ankauf', 'Was wir ankaufen'), ('fuhrpark-verkaufen', 'Fuhrpark verkaufen')],
        liste_h2='LKW, Busse und Baumaschinen',
        zeilen=[
            ('LKW Handel', 'Verteiler-LKW, Sattelzugmaschinen, Kipper und Auflieger im An- und Verkauf.',
             'Sattelzugmaschinen', 'lkw-handel'),
            ('Omnibushandel', 'Reisebusse, Linienbusse, Überlandbusse und Kleinbusse im An- und Verkauf.',
             'Reisebusse und Omnibusse', 'omnibushandel'),
            ('Baumaschinenhandel', 'Bagger, Radlader, Betonmischer und Betonpumpen im An- und Verkauf.',
             'Bagger und Radlader', 'baumaschinenhandel'),
        ],
        export_h2='Nutzfahrzeuge für den Export',
        export='Wir exportieren Nutzfahrzeuge in ganz Europa, nach Asien und Afrika, auch in die VAE, nach Saudi-Arabien und in weitere Golfstaaten.',
        faq_h2='Häufige Fragen zum Nutzfahrzeughandel',
        faq=[('Was macht ein Nutzfahrzeughandel?',
              'Ein Nutzfahrzeughandel kauft und verkauft gewerblich genutzte Fahrzeuge wie LKW, Busse, Transporter '
              'und Baumaschinen. Die ECS GmbH übernimmt Ankauf, Verkauf und Export aus einer Hand.'),
             FAQ_SUCHE,
             FAQ_AUSLAND, FAQ_ZAHLUNG],
        mehr=[('fuhrpark-verkaufen', 'Fuhrpark verkaufen'), ('transporter-verkaufen', 'Transporter verkaufen')],
        service=('Nutzfahrzeughandel', 'Ankauf, Verkauf und Export gebrauchter Nutzfahrzeuge'),
    ),
    'lkw-handel': dict(
        verkauf2='Ob Koffer, Plane, Kipper oder Zugmaschine: Nennen Sie uns Aufbau, Gewichtsklasse und Einsatz. Weil wir laufend LKW ankaufen, kommen passende Fahrzeuge regelmäßig nach.',
        titel='LKW Handel: LKW Ankauf und LKW Verkauf',
        beschreibung='LKW Handel der ECS GmbH bei Hannover: LKW Verkauf und LKW Ankauf deutschlandweit, dazu Export. '
                     'Gebrauchte LKW, Sattelzugmaschinen, Kipper und Auflieger.',
        eyebrow='LKW Händler bei Hannover', h1='LKW Handel',
        lead='LKW Ankauf, LKW Verkauf und Export.',
        intro='Die ECS GmbH handelt mit gebrauchten LKW: vom 7,5-Tonner über Kipper bis zur Sattelzugmaschine. '
              'Wir verkaufen sie an Speditionen, Bauunternehmen und Händler im In- und Ausland.',
        verkauf_h2='LKW Verkauf: gebrauchte LKW kaufen',
        verkauf='Im LKW Verkauf bieten wir Verteiler-LKW, Sattelzugmaschinen, Kipper, Fahrgestelle und Auflieger an. '
                'Die Fahrzeuge stammen von Mercedes-Benz, MAN, Scania, Volvo, DAF und Iveco.',
        ankauf_h2='Sie möchten Ihren LKW verkaufen?',
        ankauf='Wir kaufen auch an: einzelne LKW und ganze Flotten.',
        ankauf_links=[('lkw-verkaufen', 'LKW verkaufen')],
        liste_h2='Diese LKW handeln wir',
        zeilen=[
            ('Verteiler-LKW', 'Koffer, Plane, Pritsche und Kühlkoffer von 7,5 bis 18 Tonnen.', 'Verteiler-LKW', None),
            ('Sattelzugmaschinen', 'Sattelzugmaschinen für den Fern- und Verteilerverkehr von allen großen Herstellern.',
             'Sattelzugmaschinen', None),
            ('Kipper und Baustellen-LKW', KIPPER, 'Kipper und Baustellen-LKW', None),
            ('Sattelauflieger und Anhänger', 'Planen-, Koffer- und Kippauflieger sowie Anhänger.',
             'Sattelauflieger und Anhänger', None),
        ],
        export_h2='LKW Export',
        export='Viele LKW verkaufen wir in den Export: in ganz Europa, nach Asien und Afrika, auch in die VAE, nach Saudi-Arabien und in weitere Golfstaaten.',
        faq_h2='Häufige Fragen zum LKW Handel',
        faq=[('Was ist der Unterschied zwischen LKW Ankauf und LKW Verkauf?',
              'Beim LKW Ankauf verkaufen Sie Ihren LKW an uns. Beim LKW Verkauf kaufen Sie einen gebrauchten LKW '
              'aus unserem Bestand. Als LKW Händler bieten wir beides an.'),
             FAQ_SUCHE,
             FAQ_AUSLAND, FAQ_ZAHLUNG],
        mehr=[('lkw-verkaufen', 'LKW verkaufen'), ('fuhrpark-verkaufen', 'Fuhrpark verkaufen')],
        service=('LKW Handel', 'Ankauf, Verkauf und Export gebrauchter LKW'),
    ),
    'omnibushandel': dict(
        verkauf2='Unsere Käufer sind Busunternehmen, Reiseveranstalter und Händler aus Deutschland und dem Ausland.',
        titel='Omnibushandel: Bushandel mit Ankauf und Verkauf',
        beschreibung='Omnibushandel der ECS GmbH bei Hannover: Bushandel mit Ankauf, Verkauf und Export gebrauchter '
                     'Reisebusse, Linienbusse, Überlandbusse und Kleinbusse.',
        eyebrow='Bushändler bei Hannover', h1='Omnibushandel',
        lead='Bushandel mit Ankauf, Verkauf und Export.',
        intro='Die ECS GmbH ist ein Omnibushandel bei Hannover. Wir verkaufen gebrauchte Reisebusse, '
              'Linienbusse und Kleinbusse an Busunternehmen und Händler im In- und Ausland.',
        verkauf_h2='Gebrauchte Busse kaufen',
        verkauf='Im Bushandel bieten wir Reisebusse, Überlandbusse, Linienbusse und Kleinbusse an. '
                'Die Omnibusse stammen von Mercedes-Benz, Setra, MAN, Neoplan, Volvo und Iveco.',
        ankauf_h2='Sie möchten einen Bus verkaufen?',
        ankauf='Wir kaufen auch an: einzelne Omnibusse, ganze Busflotten und komplette Busunternehmen.',
        ankauf_links=[('reisebus-verkaufen', 'Reisebus verkaufen'), ('linienbus-verkaufen', 'Linienbus verkaufen')],
        liste_h2='Diese Busse handeln wir',
        zeilen=[
            ('Reisebusse und Omnibusse', 'Hochdecker und Doppeldecker für Reiseverkehr und Fernlinie.',
             'Reisebusse und Omnibusse', None),
            ('Linienbusse', 'Stadtbusse, Gelenkbusse und Überlandbusse aus dem Linienverkehr.', 'Linienbusse', None),
            ('Kleinbusse', 'Kleinbusse und Midibusse für Shuttle, Schulverkehr und kleine Gruppen.', 'Kleinbusse', None),
        ],
        export_h2='Busexport',
        export='Gebrauchte Omnibusse sind im Ausland gefragt. Wir exportieren Busse in ganz Europa, nach Asien '
               'und Afrika, auch in die VAE, nach Saudi-Arabien und in weitere Golfstaaten.',
        faq_h2='Häufige Fragen zum Omnibushandel',
        faq=[('Was ist der Unterschied zwischen Omnibushandel und Bushandel?',
              'Keiner. Omnibus ist die ausführliche Bezeichnung für Bus. Beide Begriffe meinen den An- und Verkauf '
              'von Reisebussen, Linienbussen und Kleinbussen.'),
             FAQ_SUCHE,
             FAQ_AUSLAND, FAQ_ZAHLUNG],
        mehr=[('reisebus-verkaufen', 'Reisebus verkaufen'), ('linienbus-verkaufen', 'Linienbus verkaufen')],
        service=('Omnibushandel', 'Ankauf, Verkauf und Export gebrauchter Omnibusse'),
    ),
    'baumaschinenhandel': dict(
        verkauf2='Unsere Käufer sind Bauunternehmen und Händler aus Deutschland und dem Ausland. Nennen Sie uns Maschinentyp und Einsatz, wenn Sie etwas Bestimmtes suchen.',
        titel='Baumaschinenhandel: Baumaschinen Ankauf und Verkauf',
        beschreibung='Baumaschinenhandel der ECS GmbH bei Hannover: Ankauf, Verkauf und Export gebrauchter Baumaschinen '
                     'und Baufahrzeuge. Bagger, Radlader, Kipper, Betonmischer.',
        eyebrow='Baumaschinen Händler bei Hannover', h1='Baumaschinenhandel',
        lead='Baumaschinen Ankauf, Verkauf und Export.',
        intro='Die ECS GmbH handelt mit gebrauchten Baumaschinen und Baufahrzeugen. Wir verkaufen Bagger, Radlader, Kipper, '
              'Betonmischer und Betonpumpen an Bauunternehmen und Händler im In- und Ausland.',
        verkauf_h2='Gebrauchte Baumaschinen kaufen',
        verkauf='Im Baumaschinenhandel bieten wir Bagger, Radlader, Kipper und Baustellen-LKW an, '
                'dazu Fahrmischer und Autobetonpumpen.',
        ankauf_h2='Sie möchten eine Baumaschine verkaufen?',
        ankauf='Wir kaufen auch an: einzelne Baumaschinen sowie Bau- und Kommunalfahrzeuge.',
        ankauf_links=[('bau-und-kommunalfahrzeuge-verkaufen', 'Bau- und Kommunalfahrzeuge')],
        liste_h2='Diese Baumaschinen handeln wir',
        zeilen=[
            ('Bagger und Radlader', 'Bagger und Radlader für Erdbau und Umschlag.', 'Bagger und Radlader', None),
            ('Kipper und Baustellen-LKW', KIPPER, 'Kipper und Baustellen-LKW', None),
            ('Betonmischer und Betonpumpen', 'Fahrmischer und Autobetonpumpen auf LKW-Fahrgestell.', None, None),
        ],
        export_h2='Baumaschinen Export',
        export='Gebrauchte Baumaschinen exportieren wir in ganz Europa, nach Asien und Afrika, auch in die VAE, nach Saudi-Arabien und in weitere Golfstaaten.',
        faq_h2='Häufige Fragen zum Baumaschinenhandel',
        faq=[('Welche Baumaschinen bieten Sie an?',
              'Bagger, Radlader, Kipper und Baustellen-LKW sowie Fahrmischer und Autobetonpumpen. '
              'Was gerade verfügbar ist, sehen Sie im aktuellen Bestand.'),
             FAQ_SUCHE,
             FAQ_AUSLAND, FAQ_ZAHLUNG],
        mehr=[('bau-und-kommunalfahrzeuge-verkaufen', 'Bau- und Kommunalfahrzeuge')],
        service=('Baumaschinenhandel', 'Ankauf, Verkauf und Export gebrauchter Baumaschinen'),
    ),
}

e = html.escape


def fotos(vorlage):
    """Foto-Blöcke der Vorlage nach Zeilentitel."""
    out = {}
    for m in re.finditer(r'<h3 class="typo__title">(.*?)</h3>.*?(<div class="typo__media">.*?</div>)\s*</li>', vorlage, re.S):
        out[html.unescape(m.group(1))] = m.group(2)
    return out


def statement(eyebrow, h2, absaetze, links=()):
    ps = ''.join('\n      <p class="lead">%s</p>' % e(a) for a in absaetze)
    if links:
        ps += '\n      <div class="statement__actions">' + ''.join(
            '\n        <a class="btn btn--primary" href="%s">%s</a>' % (h, e(t)) for h, t in links) + '\n      </div>'
    return '''
<section class="statement">
  <div class="container statement__grid">
    <div class="reveal">
      <p class="eyebrow">%s</p>
      <h2 class="h2">%s</h2>
    </div>
    <div class="statement__text reveal">%s
    </div>
  </div>
</section>
''' % (e(eyebrow), e(h2), ps)


def zeile(titel, text, foto, link):
    t = '<a href="%s">%s</a>' % (link, e(titel)) if link else e(titel)
    return '''      <li class="typo__row%s reveal">
        <div class="typo__body">
          <div class="typo__name">
            <h3 class="typo__title">%s</h3>
          </div>
          <p class="typo__text">%s</p>
        </div>%s
      </li>
''' % ('' if foto else ' typo__row--plain', t, e(text), '\n        ' + foto if foto else '')


def faq(h2, fragen):
    items = ''.join('''      <details class="accordion-item">
        <summary class="accordion__head">
          <span class="accordion__label">%s</span>
          <svg class="plus" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
        </summary>
        <div class="accordion__body">%s</div>
      </details>
''' % (e(q), e(a)) for q, a in fragen)
    return '''
<section class="faq" id="faq">
  <div class="container faq__inner">
    <p class="eyebrow eyebrow--center">FAQ</p>
    <h2 class="h2 faq__title">%s</h2>
    <div class="accordion">
%s    </div>
  </div>
</section>
''' % (e(h2), items)


def fakten(items):
    """Kasten "Auf einen Blick" (css/style.css .facts) direkt unter der Einleitung."""
    rows = ''.join('      <div class="facts__item"><dt>%s</dt><dd>%s</dd></div>\n' % (e(a), e(b)) for a, b in items)
    return ('\n<section class="facts" aria-labelledby="facts-title">\n  <div class="container reveal">\n'
            '    <h2 class="facts__title" id="facts-title">Auf einen Blick</h2>\n    <dl class="facts__list">\n'
            + rows + '    </dl>\n  </div>\n</section>\n')


# Bild unter dem Seitenkopf mit halbtransparentem Kasten wie auf /export (21.11.2026).
# Fotos aus assets/img/opt (Originale unbearbeitet), Alt-Texte ohne Modellnamen.
# (Datei, Breiten, Höhe der größten Breite, Bildausschnitt, Kasten rechts?, Alt-Text, Überschrift)
KOPFBILD = {
    # 21.11.: Erfan wünscht weißen Actros MP3 (Nutzfahrzeughandel) und weißen Atego (LKW Handel)
    'nutzfahrzeughandel': ('export-drittland-actros-schwarz', (720, 960, 1320), 950, '50% 60%', False,
                           'Gebrauchte schwarze Sattelzugmaschine von vorne auf dem Hof der ECS GmbH bei Hannover',
                           'Nutzfahrzeuge aus einer Hand.'),
    'lkw-handel': ('pitch-atego-koffer', (720, 960, 1448), 1086, '30% 85%', True,
                   'Gebrauchter weißer Koffer-LKW auf dem Hof der ECS GmbH bei Hannover',
                   'Gebrauchte LKW für Ihren Fuhrpark.'),
    'omnibushandel': ('reisebus-magelys', (720, 960, 1448), 1086, '50% 62%', True,
                      'Gebrauchter Reisebus auf dem Hof der ECS GmbH bei Hannover',
                      'Gebrauchte Busse für Ihr Unternehmen.'),
    'baumaschinenhandel': ('bau-arocs-kipper', (720, 960, 1448), 1086, '50% 62%', True,
                           'Gebrauchter Kipper mit angehobener Mulde auf dem Hof der ECS GmbH bei Hannover',
                           'Baumaschinen für Ihre Baustelle.'),
}


def kopfbild(slug, s):
    datei, breiten, hoehe, pos, rechts, alt, h2 = KOPFBILD[slug]
    def srcset(ext):
        return ', '.join('assets/img/opt/%s-%d.%s %dw' % (datei, b, ext, b) for b in breiten)
    gross = 'assets/img/opt/%s-%d.jpg' % (datei, breiten[-1])
    return '''
<section class="pitch pitch--export pitch--handel%s">
  <div class="pitch__media">
    <picture>
      <source type="image/avif" srcset="%s" sizes="100vw">
      <source type="image/webp" srcset="%s" sizes="100vw">
      <img src="%s" srcset="%s" sizes="100vw" alt="%s" width="%d" height="%d" style="object-position: %s" fetchpriority="high">
    </picture>
  </div>

  <div class="container pitch__grid">
    <div class="pitch__content reveal">
      <p class="eyebrow pitch__kicker">Verkauf, Besichtigung und Export.</p>
      <h2 class="h2 pitch__title">%s</h2>
      <p class="lead pitch__lead">%s</p>
      <div class="pitch__actions">
        <a class="btn btn--primary" href="fahrzeuge">Aktuellen Bestand ansehen</a>
        <a class="btn btn--secondary" href="kontakt#anfrage-form">Zum Anfrageformular</a>
      </div>
    </div>
  </div>
</section>
''' % (' pitch--rechts' if rechts else '', srcset('avif'), srcset('webp'), gross, srcset('jpg'), e(alt),
       breiten[-1], hoehe, pos, e(h2), e(s['intro']))


def main_html(slug, s, bilder):
    out = '''<main>

<section class="page-hero">
  <div class="container">
    <p class="eyebrow">%s</p>
    <h1 class="h1 page-hero__title">%s</h1>
    <p class="lead page-hero__lead">%s</p>
  </div>
</section>
''' % (e(s['eyebrow']), e(s['h1']), e(s['lead'])) + kopfbild(slug, s)
    if s.get('fakten'):
        out += fakten(s['fakten'])
    out += statement('Verkauf', s['verkauf_h2'], [s['verkauf'], s['verkauf2'], BESTAND], [('fahrzeuge', 'Aktuellen Bestand ansehen')])
    out += statement('Ankauf', s['ankauf_h2'], [s['ankauf'], ANKAUF_VERWEIS],
                     s['ankauf_links'] + [('unsere-arbeit', 'So läuft ein Ankauf ab')])
    out += '''
<section class="typo" id="fahrzeugtypen">
  <div class="container">
    <div class="typo__head reveal">
      <p class="eyebrow">Fahrzeugtypen</p>
      <div>
        <h2 class="h2">%s</h2>
      </div>
    </div>
    <ul class="typo__list">
%s    </ul>
  </div>
</section>
''' % (e(s['liste_h2']), ''.join(zeile(t, x, bilder[f] if f else None, l) for t, x, f, l in s['zeilen']))
    out += statement('Export', s['export_h2'], [s['export'], EXPORT], [('export', 'Export im Überblick')])
    out += faq(s['faq_h2'], s['faq'])
    links = [(k, v) for k, v in NAMEN.items() if k != slug] + s['mehr'] + [
        ('fahrzeuge', 'Fahrzeuge im Bestand'), ('kontakt', 'Kontakt')]
    out += '''
<section class="related">
  <div class="container">
    <p class="eyebrow">Mehr erfahren</p>
    <h2 class="h2 related__title">Weitere Handelsbereiche</h2>
    <ul class="link-list">
%s    </ul>
  </div>
</section>
''' % ''.join('      <li><a href="%s">%s</a></li>\n' % (h, e(t)) for h, t in links)
    return out


def build():
    vorlage = open(os.path.join(ROOT, 'gebrauchte-nutzfahrzeuge.html'), encoding='utf-8').read()
    bilder = fotos(vorlage)
    kopf, rest = vorlage.split('<main>', 1)
    band = rest[rest.index('<!-- ============================================================ Kontakt-Band -->'):]
    alt_titel = re.search(r'<title>(.*?)</title>', kopf).group(1)
    alt_beschr = re.search(r'<meta name="description" content="(.*?)">', kopf).group(1)
    for slug, s in SEITEN.items():
        k = kopf.replace(alt_titel, e(s['titel'] + ' | ' + FIRMA)).replace(alt_beschr, e(s['beschreibung']))
        k = k.replace(BASE + 'gebrauchte-nutzfahrzeuge', BASE + slug)
        k = k.replace('<a href="gebrauchte-nutzfahrzeuge" aria-current="page">', '<a href="gebrauchte-nutzfahrzeuge">')
        k = k.replace('<a href="%s">%s</a>' % (slug, NAMEN[slug]),
                      '<a href="%s" aria-current="page">%s</a>' % (slug, NAMEN[slug]))
        seite = k + main_html(slug, s, bilder) + '\n' + band
        open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8').write(seite)
        print(slug + '.html')


if __name__ == '__main__':
    build()
