#!/usr/bin/env python3
"""Erzeugt die Export-Checklisten als PDF.

  assets/docs/ecs-checkliste-eu-kunden.pdf        (Export EU)
  assets/docs/ecs-checkliste-drittland-kunden.pdf (Export Drittland)

Aufruf:  python3 _tools/pdfs.py
Braucht: playwright (mit installiertem Google Chrome) und pypdf.

Aufbau wie die ursprüngliche EU-Checkliste (Sept. 2026): schwarzes Logo links,
grauer Großbuchstaben-Titel rechts, Karte mit nummerierter Liste, Fußzeile
mit zwei feinen Linien. Je Sprache eine Seite (1 Deutsch, 2 Englisch), oben
rechts in der Karte die Flagge der Sprache. Keine schwarzen Balken.
Nur die Farben sind angepasst: Schwarz statt Orange, wie die Website.
Boxen eckig, Schriftstärke höchstens 500. Die EU-Checkliste trägt oben
rechts die EU-Flagge (offizielles Muster, als Vektor).
Maße in pt sind aus dem alten PDF übernommen.

Inhalte nur von /export-eu und /export-drittland, keine internen Angaben
(Namen, Preise, Bankdaten). Die Metadaten werden danach mit pypdf komplett
neu gesetzt, damit kein Chrome-/Skia-Eintrag und kein lokaler Pfad im
Dokument steht.
"""
import datetime, html, os, shutil, tempfile

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, TextStringObject, DictionaryObject

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'docs')
FIRMA = 'ECS Exclusive Commerce Services GmbH'

# ------------------------------------------------------------------ Inhalte
# Karte: (Sprache, Titel, Einleitung, [Listenpunkte], [Schlussabsätze])
EU = {
    'datei': 'ecs-checkliste-eu-kunden.pdf',
    'kopf': 'EU Documentation Requirements',
    'meta': {
        'title': 'Checkliste für EU Kunden – Dokumentenpflicht / Checklist for EU Customers',
        'subject': 'Unterlagen für den Export von Nutzfahrzeugen in EU-Mitgliedstaaten / '
                   'Documents required for exports to EU member states',
        'keywords': 'Export EU, Dokumentenpflicht, innergemeinschaftliche Lieferung, Umsatzsteuer-ID, '
                    'EU export, documentation requirements, ECS GmbH',
    },
    'karten': [
        ('de', 'Checkliste für EU Kunden, Dokumentenpflicht',
         'Aufgrund gestiegener Dokumentenpflicht verlangt das deutsche Finanzamt bei Exporten in '
         'EU-Mitgliedstaaten folgende Unterlagen und Informationen von uns.',
         ['Vollständige und exakte Firmenanschrift, Telefonnummer, Faxnummer, E-Mail-Adresse, Angabe '
          'des Gewerbezweiges bzw. der Branche und falls vorhanden Internetadresse, Visitenkarte etc.',
          'Europäische Umsatzsteuer-Identifikationsnummer.',
          'Handelsregisterauszug, Gewerbe- oder anderer amtlicher Firmennachweis (z. B. durch die '
          'Handelskammer) in Kopie.',
          'Passkopie des Firmeninhabers bzw. Geschäftsführers.',
          'Falls er die Abholung nicht persönlich vornimmt: eine von ihm unterzeichnete Vollmacht, '
          'möglichst mit Firmenstempel, für den abholenden Fahrer.'],
         ['Können uns keine Dokumente überlassen werden, aus denen die Unternehmereigenschaft und die '
          'Vertretungsbefugnis eindeutig hervorgehen, erheben wir eine Kaution.',
          'Der Kautionsbetrag wird erstattet, sobald Sie uns die vorgenannten Unterlagen vorlegen.']),
        ('en', 'Checklist for EU Customers, documentation requirements',
         'Due to increased documentation requirements, the German tax office requires the following '
         'documents and information from us for exports to EU member states.',
         ['Complete and exact company address, phone number, fax number, e-mail address, line of '
          'business and, if available, website, business card etc.',
          'European VAT identification number.',
          'Copy of an excerpt from the commercial register, trade licence or other official proof of '
          'company (e.g. from the chamber of commerce).',
          'Passport copy of the company owner or managing director.',
          'If the owner does not collect the vehicle in person: an authorisation signed by the owner, '
          'ideally with the company stamp, for the collecting driver.'],
         ['If no documents can be provided that clearly prove the company status and the authority to '
          'represent the company, we charge a security deposit.',
          'The deposit will be refunded as soon as you provide the documents listed above.']),
    ],
}

DRITTLAND = {
    'datei': 'ecs-checkliste-drittland-kunden.pdf',
    'kopf': 'Non-EU Export Requirements',
    'meta': {
        'title': 'Checkliste für Kunden aus Drittländern – Ausfuhr / Checklist for Non-EU Customers',
        'subject': 'Unterlagen für den Export von Nutzfahrzeugen in Länder außerhalb der EU / '
                   'Documents required for exports to countries outside the EU',
        'keywords': 'Export Drittland, Ausfuhr, Ausfuhranmeldung, ATLAS, Ausfuhrbegleitdokument, '
                    'Ausgangsvermerk, Ausfuhrkennzeichen, EUR.1, non-EU export, ECS GmbH',
    },
    'karten': [
        ('de', 'Checkliste für Kunden aus Drittländern, Ausfuhr',
         'Für die Ausfuhr eines Fahrzeugs in ein Land außerhalb der Europäischen Union benötigen wir '
         'folgende Unterlagen und Informationen von Ihnen.',
         ['Name und vollständige Anschrift von Käufer und Empfänger sowie das Zielland, bei Firmen '
          'zusätzlich die Firmendaten.',
          'Kopie des Reisepasses oder Personalausweises des Käufers bzw. des abholenden Fahrers.',
          'Angabe, ob das Fahrzeug auf eigener Achse fährt oder per Tieflader bzw. Schiff transportiert wird.',
          'Bei Fahrt auf eigener Achse: Ausfuhrkennzeichen mit gültiger Hauptuntersuchung (TÜV) und '
          'Kfz-Haftpflichtversicherung für die Dauer der Überführung.',
          'Falls gewünscht: Warenverkehrsbescheinigung EUR.1, sofern das Zielland ein Präferenzabkommen '
          'mit der EU hat.'],
         ['Die Ausfuhr wird beim Zoll elektronisch über ATLAS angemeldet. Das Ausfuhrbegleitdokument (ABD) '
          'reist mit dem Fahrzeug bis zur letzten Grenze der EU, dort erteilt der Zoll den Ausgangsvermerk.',
          'Einfuhrzoll, Steuern und Zulassung richten sich nach den Vorschriften im Zielland.']),
        ('en', 'Checklist for Non-EU Customers, export',
         'To export a vehicle to a country outside the European Union, we need the following documents '
         'and information from you.',
         ['Name and full address of buyer and consignee and the country of destination, for companies '
          'also the company details.',
          'Copy of the passport or ID card of the buyer or the collecting driver.',
          'Whether the vehicle is driven on its own wheels or transported by low-loader or ship.',
          'For driving on its own wheels: export number plates with a valid roadworthiness test (TÜV) and '
          'motor liability insurance for the transfer.',
          'If required: movement certificate EUR.1, provided the country of destination has a '
          'preferential agreement with the EU.'],
         ['The export is declared to customs electronically via ATLAS. The export accompanying document '
          '(EAD) travels with the vehicle to the last EU border, where customs issues the exit endorsement.',
          'Import duties, taxes and registration follow the rules of the country of destination.']),
    ],
}

# ------------------------------------------------------------------ Layout
SCHWARZ = '#1a1a1a'   # ersetzt das frühere Orange #e05c00

CSS = """
@font-face { font-family: "DM Sans"; font-weight: 100 1000;
  src: url("dm-sans-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2212; }
@font-face { font-family: "DM Sans"; font-weight: 100 1000;
  src: url("dm-sans-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1E00-1E9F, U+20A0-20AB, U+20AD-20C4; }
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "DM Sans", Arial, sans-serif; color: #1a1a1a; font-size: 11pt; }

/* Briefränder nach DIN 5008: links 25 mm, rechts 20 mm */
.page { position: relative; width: 595.28pt; height: 841.89pt; padding: 0 56.7pt 0 70.9pt; overflow: hidden;
  break-after: page; }
.page:last-child { break-after: auto; }

.head { display: flex; justify-content: space-between; align-items: flex-start; padding-top: 51pt; height: 122pt; margin-bottom: 26pt; }
.head img { width: 85pt; height: auto; display: block; }
.head__side { display: flex; align-items: center; gap: 8pt; margin-top: 11pt; }
.head__side svg { width: 21pt; height: 14pt; display: block; }
.head p { font-size: 9pt; font-weight: 500; letter-spacing: 0.17em;
  text-transform: uppercase; color: #888; }

.card { position: relative; border: 0.75pt solid #ddd;
  padding: 26pt 28pt 22pt; }
.card__flag { position: absolute; top: 31.5pt; right: 28pt; height: 14pt; }
.card__flag svg { height: 14pt; width: auto; display: block; border: 0.5pt solid #ddd; }
.card h2 { padding-right: 40pt; font-size: 16pt; font-weight: 500; line-height: 1.45; color: #1a1a1a; margin-bottom: 12pt; }
.card p { color: #555; line-height: 1.65; margin-bottom: 10pt; }
.card ol { list-style: none; margin: 18pt 0 18pt; }
.card li { position: relative; padding-left: 20pt; line-height: 1.6; margin-bottom: 13pt; }
.card li span { position: absolute; left: 0; top: 0; font-weight: 500; color: ACCENT; }

.foot { position: absolute; left: 70.9pt; right: 56.7pt; top: 785.2pt; display: flex;
  justify-content: space-between; font-size: 8.5pt; }
.foot p { border-top: 0.75pt solid #eee; padding-top: 5pt; }
.foot p:first-child { width: 48%; font-weight: 500; color: #555; }
.foot p:last-child { width: 36%; text-align: right; color: #888; }
""".replace('ACCENT', SCHWARZ)


def e(t):
    return html.escape(t, quote=True)


def eu_flagge():
    """EU-Flagge nach offiziellem Muster: Blau #003399, 12 goldene Sterne #FFCC00
    auf einem Kreis mit Radius 1/3 der Höhe, Sternradius 1/18 der Höhe."""
    import math
    h = 200.0
    w, cx, cy, r, sr = 300.0, 150.0, 100.0, h / 3, h / 18
    sterne = []
    for i in range(12):
        a = math.radians(i * 30)
        x, y = cx + r * math.sin(a), cy - r * math.cos(a)
        pkt = []
        for k in range(10):
            rr = sr if k % 2 == 0 else sr * 0.382
            b = math.radians(k * 36)
            pkt.append(f'{x + rr * math.sin(b):.2f},{y - rr * math.cos(b):.2f}')
        sterne.append(f'<polygon points="{" ".join(pkt)}"/>')
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Flagge der Europäischen Union">'
            f'<rect width="{w:.0f}" height="{h:.0f}" fill="#003399"/><g fill="#FFCC00">{"".join(sterne)}</g></svg>')



def de_flagge():
    """Deutschland, 5:3, Schwarz-Rot-Gold."""
    return ('<svg viewBox="0 0 5 3" role="img" aria-label="Deutsch">'
            '<rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#DD0000"/>'
            '<rect y="2" width="5" height="1" fill="#FFCE00"/></svg>')


def uk_flagge():
    """Vereinigtes Königreich (Union Jack), 2:1."""
    return ('<svg viewBox="0 0 60 30" role="img" aria-label="English">'
            '<clipPath id="uk-s"><path d="M0,0 v30 h60 v-30 z"/></clipPath>'
            '<clipPath id="uk-t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath>'
            '<g clip-path="url(#uk-s)"><path d="M0,0 v30 h60 v-30 z" fill="#012169"/>'
            '<path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>'
            '<path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#uk-t)" stroke="#C8102E" stroke-width="4"/>'
            '<path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>'
            '<path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></g></svg>')


EU['flagge'] = eu_flagge()
FLAGGEN = {'de': de_flagge(), 'en': uk_flagge()}


def karte(k):
    lang, titel, intro, punkte, schluss = k
    li = ''.join(f'<li><span>{i}.</span>{e(t)}</li>' for i, t in enumerate(punkte, 1))
    ps = ''.join(f'<p>{e(t)}</p>' for t in schluss)
    return f'<section class="card" lang="{lang}"><span class="card__flag">{FLAGGEN[lang]}</span><h2>{e(titel)}</h2><p>{e(intro)}</p><ol>{li}</ol>{ps}</section>'


def dokument(doc):
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>{e(doc['meta']['title'])}</title><style>{CSS}</style></head><body>
{''.join(seite(doc, k) for k in doc['karten'])}</body></html>"""


def seite(doc, k):
    return f"""<div class="page" lang="{k[0]}">
  <header class="head"><img src="logo-ecs-schwarz.png" alt="ECS Exclusive Commerce Services GmbH"><div class="head__side">{doc.get('flagge', '')}<p>{e(doc['kopf'])}</p></div></header>
  {karte(k)}
  <footer class="foot"><p>{e(FIRMA)}</p><p>Gehrden bei Hannover</p></footer>
</div>"""


def metadaten(pfad, meta, jetzt):
    """Schreibt das PDF neu: nur eigene Metadaten, Titel statt Dateiname im Fenster."""
    reader = PdfReader(pfad)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    datum = jetzt.strftime("D:%Y%m%d%H%M%S+01'00'")
    writer.add_metadata({
        '/Title': meta['title'],
        '/Author': FIRMA,
        '/Subject': meta['subject'],
        '/Keywords': meta['keywords'],
        '/Creator': FIRMA,
        '/Producer': FIRMA,
        '/CreationDate': datum,
        '/ModDate': datum,
    })
    writer._root_object[NameObject('/Lang')] = TextStringObject('de-DE')
    writer._root_object[NameObject('/ViewerPreferences')] = DictionaryObject(
        {NameObject('/DisplayDocTitle'): BooleanObject(True)})
    with open(pfad, 'wb') as f:
        writer.write(f)


def main():
    jetzt = datetime.datetime.now()
    # Schriften und Logo in einen Arbeitsordner kopieren (Chrome darf je nach
    # macOS-Freigabe nicht direkt im Desktop-Ordner lesen)
    tmp = tempfile.mkdtemp(prefix='ecs-pdf-')
    for f in ('assets/fonts/dm-sans-latin.woff2', 'assets/fonts/dm-sans-latin-ext.woff2',
              '_tools/logo-ecs-schwarz.png'):
        shutil.copy(os.path.join(ROOT, f), tmp)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome')
            page = browser.new_page()
            for doc in (EU, DRITTLAND):
                src = os.path.join(tmp, doc['datei'] + '.html')
                open(src, 'w', encoding='utf-8').write(dokument(doc))
                page.goto('file://' + src)
                page.evaluate('document.fonts.ready')
                # Karten dürfen nicht in die Fußzeile laufen
                luft = page.evaluate("[...document.querySelectorAll('.page')].map(p => p.querySelector('.foot').getBoundingClientRect().top - p.querySelector('.card').getBoundingClientRect().bottom)")
                print('  Abstand Karte–Fußzeile je Seite (px):', [round(x) for x in luft])
                if min(luft) < 10:
                    raise SystemExit(f"{doc['datei']}: Karte läuft in die Fußzeile, Abstand je Seite in px: {luft}")
                ziel = os.path.join(OUT, doc['datei'])
                page.pdf(path=ziel, format='A4', print_background=True, prefer_css_page_size=True,
                         margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
                metadaten(ziel, doc['meta'], jetzt)
                print('geschrieben:', os.path.relpath(ziel, ROOT))
            browser.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
