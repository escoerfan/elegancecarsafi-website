#!/usr/bin/env python3
"""Erzeugt die Export-Checklisten als PDF im Design der Website.

  assets/docs/ecs-checkliste-eu-kunden.pdf        (Export EU, Deutsch + Englisch)
  assets/docs/ecs-checkliste-drittland-kunden.pdf (Export Drittland, Deutsch + Englisch)

Aufruf:  python3 _tools/pdfs.py
Braucht: playwright (mit installiertem Google Chrome) und pypdf.

Seite 1 Deutsch, Seite 2 Englisch. Weißer Hintergrund (druckfreundlich), schwarzes Logo, DM Sans, Schriftstärke
höchstens 400, eckige Nummern wie die Zeitleiste auf der Website.
Inhalte nur aus den Seiten /export-eu und /export-drittland übernehmen,
keine internen Angaben (Namen, Preise, Bankdaten) in die PDFs schreiben.
Die Metadaten werden danach mit pypdf komplett neu gesetzt, damit kein
Chrome-/Skia-Eintrag und kein lokaler Pfad im Dokument steht.
"""
import datetime, html, os, re, shutil, tempfile

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, TextStringObject, DictionaryObject

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'docs')

FIRMA = 'ECS Exclusive Commerce Services GmbH'
ADRESSE = 'Bünteweg 13, 30989 Gehrden'
TEL = [('+49 171 362 1298', '+491713621298'), ('+49 1514 0315387', '+4915140315387')]
MAIL = 'info@elegancecarsafi.com'
WEB = 'elegancecarsafi.com'

# ------------------------------------------------------------------ Inhalte
EU = {
    'datei': 'ecs-checkliste-eu-kunden.pdf',
    'meta': {
        'title': 'Checkliste Export EU – Unterlagen für Kunden aus der EU',
        'subject': 'Unterlagen für den Export von Nutzfahrzeugen in EU-Länder / '
                   'Documents for exporting commercial vehicles to EU countries',
        'keywords': 'Export EU, Nutzfahrzeug Export, innergemeinschaftliche Lieferung, '
                    'Umsatzsteuer-ID, Gelangensbestätigung, EU export, commercial vehicles, ECS GmbH',
    },
    'seiten': [
        {
            'lang': 'de', 'sprache': 'Deutsch', 'seite': 'Seite',
            'eyebrow': 'Export EU',
            'titel': 'Checkliste für Kunden aus der EU',
            'lead': 'Diese Unterlagen brauchen wir für den Export Ihres Nutzfahrzeugs in ein EU-Land.',
            'intro': 'Das deutsche Finanzamt verlangt für jeden Export in einen EU-Mitgliedstaat bestimmte '
                     'Unterlagen und Angaben von uns. Nur dann kann das Fahrzeug als innergemeinschaftliche '
                     'Lieferung ohne deutsche Umsatzsteuer verkauft werden. Am besten schicken Sie uns alles '
                     'vor der Abholung per E-Mail oder WhatsApp.',
            'abschnitte': [
                ('liste', 'Diese Unterlagen brauchen wir von Ihnen', [
                    ('Firmendaten', 'Vollständige und genaue Firmenanschrift, Telefon- und Faxnummer, '
                     'E-Mail-Adresse und Branche, falls vorhanden auch Internetadresse und Visitenkarte.'),
                    ('Umsatzsteuer-ID', 'Ihre europäische Umsatzsteuer-Identifikationsnummer. Name und '
                     'Anschrift müssen mit Ihren Firmendaten übereinstimmen.'),
                    ('Firmennachweis', 'Handelsregisterauszug, Gewerbeanmeldung oder ein anderer amtlicher '
                     'Firmennachweis, zum Beispiel von der Handelskammer, in Kopie.'),
                    ('Passkopie', 'Eine Kopie des Reisepasses des Firmeninhabers bzw. Geschäftsführers.'),
                    ('Vollmacht für den Fahrer', 'Holt der Inhaber das Fahrzeug nicht selbst ab, braucht der '
                     'Fahrer eine von ihm unterschriebene Vollmacht, möglichst mit Firmenstempel.'),
                ]),
                ('hinweis', 'Kaution', 'Liegen keine Unterlagen vor, aus denen die Unternehmereigenschaft und '
                 'die Vertretungsbefugnis eindeutig hervorgehen, erheben wir eine Kaution. Sie wird erstattet, '
                 'sobald Sie uns die Unterlagen nachreichen.'),
                ('spalten', 'So läuft der Export in die EU ab', [
                    ('Unterlagen und Rechnung', 'Sie wählen ein Fahrzeug und schicken uns die Unterlagen. '
                     'Sind sie vollständig, erhalten Sie die Rechnung ohne deutsche Umsatzsteuer.'),
                    ('Abholung oder Transport', 'Sie holen das Fahrzeug in Gehrden selbst ab, schicken einen '
                     'Fahrer mit Vollmacht, oder wir organisieren den Transport zu Ihnen.'),
                    ('Gelangensbestätigung', 'Ist das Fahrzeug im Bestimmungsland angekommen, unterschreiben '
                     'Sie die Gelangensbestätigung und senden sie an uns zurück.'),
                ]),
            ],
            'fuss': 'Allgemeine Informationen ohne Gewähr, keine Steuer- oder Rechtsberatung.',
        },
        {
            'lang': 'en', 'sprache': 'English', 'seite': 'Page',
            'eyebrow': 'Export EU',
            'titel': 'Checklist for customers from the EU',
            'lead': 'The documents we need to export your commercial vehicle to an EU country.',
            'intro': 'For every export to an EU member state, the German tax office requires certain documents '
                     'and details from us. Only then can the vehicle be sold as an intra-community supply '
                     'without German VAT. Ideally, send us everything by e-mail or WhatsApp before collection.',
            'abschnitte': [
                ('liste', 'The documents we need from you', [
                    ('Company details', 'Complete and exact company address, phone and fax number, e-mail '
                     'address and line of business, and if available your website and business card.'),
                    ('VAT ID', 'Your European VAT identification number. Name and address must match your '
                     'company details.'),
                    ('Proof of company', 'A copy of your commercial register extract, trade licence or other '
                     'official proof of company, for example from the chamber of commerce.'),
                    ('Passport copy', 'A copy of the passport of the company owner or managing director.'),
                    ('Authorisation for the driver', 'If the owner does not collect the vehicle in person, the '
                     'driver needs an authorisation signed by the owner, ideally with the company stamp.'),
                ]),
                ('hinweis', 'Security deposit', 'If no documents are provided that clearly prove the company '
                 'status and the authority to represent it, we charge a security deposit. It is refunded as soon '
                 'as you send us the documents.'),
                ('spalten', 'How the export to the EU works', [
                    ('Documents and invoice', 'You choose a vehicle and send us the documents. Once they are '
                     'complete, you receive the invoice without German VAT.'),
                    ('Collection or transport', 'You collect the vehicle in Gehrden yourself, send a driver '
                     'with an authorisation, or we arrange transport to you.'),
                    ('Entry certificate', 'Once the vehicle has arrived in the country of destination, you sign '
                     'the entry certificate (Gelangensbestätigung) and send it back to us.'),
                ]),
            ],
            'fuss': 'General information without guarantee, not tax or legal advice.',
        },
    ],
}

DRITTLAND = {
    'datei': 'ecs-checkliste-drittland-kunden.pdf',
    'meta': {
        'title': 'Checkliste Export Drittland – Unterlagen und Ablauf der Ausfuhr',
        'subject': 'Unterlagen und Ablauf für den Export von Nutzfahrzeugen in Länder außerhalb der EU / '
                   'Documents and procedure for exporting commercial vehicles outside the EU',
        'keywords': 'Export Drittland, Nutzfahrzeug Export, Ausfuhranmeldung, ATLAS, Ausfuhrbegleitdokument, '
                    'Ausfuhrkennzeichen, Ausgangsvermerk, EUR.1, export outside the EU, ECS GmbH',
    },
    'seiten': [
        {
            'lang': 'de', 'sprache': 'Deutsch', 'seite': 'Seite',
            'eyebrow': 'Export Drittland',
            'titel': 'Checkliste für den Export in Drittländer',
            'lead': 'Unterlagen und Ablauf für die Ausfuhr Ihres Nutzfahrzeugs aus der EU.',
            'intro': 'Ein Drittland ist jedes Land außerhalb der Europäischen Union. Für die Ausfuhr wird beim '
                     'Zoll eine Ausfuhranmeldung abgegeben, beim Verlassen der EU bestätigt der Zoll die Ausfuhr '
                     'mit dem Ausgangsvermerk. Ausfuhrpapiere und Zollabwicklung in Deutschland übernehmen wir '
                     'für Sie.',
            'abschnitte': [
                ('liste', 'Diese Unterlagen werden benötigt', [
                    ('Ausweis und Käuferdaten', 'Reisepass oder Personalausweis des Käufers bzw. Fahrers, Name '
                     'und Anschrift von Käufer und Empfänger sowie das Zielland. Bei Firmen zusätzlich die '
                     'Firmendaten.'),
                    ('Fahrzeugpapiere und Rechnung', 'Zulassungsbescheinigung Teil I und Teil II, die Rechnung '
                     'bzw. der Kaufvertrag und die Fahrzeug-Identifikationsnummer.'),
                    ('Kennzeichen und Versicherung', 'Für die Fahrt auf eigener Achse: Ausfuhrkennzeichen mit '
                     'gültiger Hauptuntersuchung (TÜV) und Kfz-Haftpflichtversicherung für die Überführung.'),
                ]),
                ('schritte', 'So läuft die Ausfuhr ab', [
                    ('Angebot', 'Sie wählen ein Fahrzeug und nennen uns Käufer, Empfänger und Zielland.'),
                    ('Ausfuhranmeldung', 'Die Ausfuhr wird beim Zoll elektronisch angemeldet, in Deutschland '
                     'über das System ATLAS.'),
                    ('Ausfuhrabfertigung', 'Das Fahrzeug wird beim Zoll vorgeführt und erhält das '
                     'Ausfuhrbegleitdokument (ABD), das bis zur Grenze mitreist.'),
                    ('Transport', 'Auf eigener Achse mit Ausfuhrkennzeichen, per Tieflader oder per Schiff.'),
                    ('Ausgangsvermerk', 'An der letzten Grenze der EU oder im Hafen bestätigt der Zoll den '
                     'Ausgang. Das ist der Nachweis für die umsatzsteuerfreie Ausfuhr.'),
                ]),
                ('boxen', [
                    ('Warenverkehrsbescheinigung EUR.1', 'Hat das Zielland ein Präferenzabkommen mit der EU, '
                     'zahlt der Käufer mit der EUR.1 ermäßigte oder gar keine Einfuhrzölle. Auf Anfrage '
                     'übernehmen wir den Antrag.'),
                    ('Einfuhr im Zielland', 'Einfuhrzoll, Steuern und Zulassung richten sich nach den '
                     'Vorschriften im Zielland. Klären Sie diese am besten vorab mit der zuständigen Behörde.'),
                ]),
            ],
            'fuss': 'Allgemeine Informationen ohne Gewähr, keine Zoll-, Steuer- oder Rechtsberatung.',
        },
        {
            'lang': 'en', 'sprache': 'English', 'seite': 'Page',
            'eyebrow': 'Export outside the EU',
            'titel': 'Checklist for exports outside the EU',
            'lead': 'Documents and procedure for exporting your commercial vehicle from the EU.',
            'intro': 'A third country is any country outside the European Union. For the export, an export '
                     'declaration is lodged with customs, and when the vehicle leaves the EU, customs confirms '
                     'the export with the exit endorsement. We take care of the export papers and customs '
                     'clearance in Germany for you.',
            'abschnitte': [
                ('liste', 'The documents required', [
                    ('ID and buyer details', 'Passport or ID card of the buyer or driver, name and address of '
                     'buyer and consignee, and the country of destination. For companies also the company '
                     'details.'),
                    ('Vehicle papers and invoice', 'Registration certificate part I and part II, the invoice or '
                     'purchase contract and the vehicle identification number.'),
                    ('Plates and insurance', 'For driving on its own wheels: export number plates with a valid '
                     'roadworthiness test (TÜV) and motor liability insurance for the transfer.'),
                ]),
                ('schritte', 'How the export works', [
                    ('Offer', 'You choose a vehicle and tell us the buyer, consignee and country of '
                     'destination.'),
                    ('Export declaration', 'The export is declared to customs electronically, in Germany via '
                     'the ATLAS system.'),
                    ('Export clearance', 'The vehicle is presented to customs and receives the export '
                     'accompanying document (EAD), which travels with it to the border.'),
                    ('Transport', 'On its own wheels with export plates, by low-loader or by ship.'),
                    ('Exit endorsement', 'At the last EU border or in the port, customs confirms the exit. This '
                     'is the proof for the VAT-free export.'),
                ]),
                ('boxen', [
                    ('Movement certificate EUR.1', 'If the country of destination has a preferential agreement '
                     'with the EU, the EUR.1 lets the buyer pay reduced or no import duties. On request, we '
                     'handle the application.'),
                    ('Import in the country of destination', 'Import duties, taxes and registration follow the '
                     'rules of the country of destination. Ideally, clarify them in advance with the '
                     'responsible authority.'),
                ]),
            ],
            'fuss': 'General information without guarantee, not customs, tax or legal advice.',
        },
    ],
}

# ------------------------------------------------------------------ Layout
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
body { font-family: "DM Sans", Arial, sans-serif; font-weight: 400; color: #262626;
  font-size: 9.2pt; line-height: 1.45; }
h1, h2, h3, b, strong { font-weight: 400; }
a { color: inherit; text-decoration: none; }
.nw { white-space: nowrap; }

.page { position: relative; width: 210mm; height: 297mm; overflow: hidden;
  display: flex; flex-direction: column; break-after: page; }
.page:last-child { break-after: auto; }

/* Kopf: weiß und druckfreundlich, Haarlinie als Abschluss */
.head { color: #262626; margin: 0 18mm; padding: 12mm 0 7mm; border-bottom: 1px solid rgba(38,38,38,.2); }
.head__top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6mm; }
.head__logo { width: 27mm; height: auto; display: block; filter: brightness(0); }  /* weißes Logo → schwarz */
.head__meta { font-size: 8pt; color: #838383; text-align: right; line-height: 1.6; }
.eyebrow { font-size: 10pt; color: #505050; margin-bottom: 3mm; }
.title { font-size: 23pt; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 3.5mm; }
.lead { font-size: 10pt; color: #505050; max-width: 150mm; }

.body { flex: 1; padding: 7mm 18mm 0; }
.intro { font-size: 9.6pt; color: #505050; margin-bottom: 5mm; }
.h2 { font-size: 13pt; letter-spacing: -0.01em; margin-bottom: 2.5mm; }
section { margin-bottom: 5mm; }

/* Liste: Nummer | Titel | Text, Haarlinien wie die Zeitleiste */
.rows { list-style: none; border-top: 1px solid rgba(38,38,38,.14); }
.rows li { display: grid; grid-template-columns: 11mm 47mm 1fr; align-items: start;
  padding: 2.2mm 0; border-bottom: 1px solid rgba(38,38,38,.14); }
.num { width: 7.5mm; height: 7.5mm; display: grid; place-items: center; font-size: 8.5pt;
  border: 1px solid rgba(38,38,38,.2); font-variant-numeric: tabular-nums; }
.rows li:last-child .num, .steps li:last-child .num { background: #262626; border-color: #262626; color: #fff; }
.rows h3 { font-size: 10pt; padding-top: 1mm; padding-right: 4mm; }
.rows p { padding-top: 1mm; color: #505050; }

/* Schritte als waagerechte Zeitleiste */
.steps { list-style: none; display: grid; grid-template-columns: repeat(5, 1fr); gap: 0 4mm; position: relative; }
.steps::before { content: ""; position: absolute; left: 0; right: 0; top: 3.75mm; height: 1px;
  background: rgba(38,38,38,.2); }
.steps li { position: relative; }
.steps .num { background: #fff; margin-bottom: 3mm; position: relative; }
.steps h3 { font-size: 10pt; margin-bottom: 1mm; }
.steps p { font-size: 8.6pt; color: #505050; line-height: 1.45; }

/* Spalten (EU-Ablauf) */
.cols { list-style: none; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0 6mm;
  border-top: 1px solid rgba(38,38,38,.14); padding-top: 3.5mm; }
.cols h3 { font-size: 10pt; margin-bottom: 1mm; }
.cols p { font-size: 8.8pt; color: #505050; }

/* Hinweis- und Infoboxen: nur Rahmen, keine Fläche (druckfreundlich) */
.note { border: 1px solid rgba(38,38,38,.2); padding: 4mm 6mm; display: grid; grid-template-columns: 52mm 1fr; }
.note h3 { font-size: 10pt; }
.note p { color: #505050; }
.boxes { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.box { border: 1px solid rgba(38,38,38,.2); padding: 4mm 6mm; }
.box h3 { font-size: 10pt; margin-bottom: 1.5mm; }
.box p { color: #505050; font-size: 8.8pt; }

/* Fuß: Kontakt unter einer Haarlinie, ohne Fläche */
.foot { padding: 0 18mm 7mm; }
.foot__note { font-size: 7.6pt; color: #838383; margin-bottom: 3mm; }
.foot__bar { color: #505050; padding-top: 3.5mm; border-top: 1px solid rgba(38,38,38,.2); display: grid;
  grid-template-columns: 1fr auto; gap: 6mm; align-items: center; font-size: 8.2pt; line-height: 1.55; }
.foot__bar strong { color: #262626; }
.foot__page { color: #838383; text-align: right; white-space: nowrap; }
"""


def e(t):
    t = html.escape(t, quote=True)
    return re.sub(r'[^\s/()]+-[^\s/()]+', lambda m: (
        f'<span class="nw">{m.group(0)}</span>' if len(m.group(0)) <= 16 else m.group(0)), t)


def abschnitt(a):
    art = a[0]
    if art == 'liste':
        rows = ''.join(
            f'<li><span class="num">{i:02d}</span><h3>{e(t)}</h3><p>{e(x)}</p></li>'
            for i, (t, x) in enumerate(a[2], 1))
        return f'<section><h2 class="h2">{e(a[1])}</h2><ol class="rows">{rows}</ol></section>'
    if art == 'schritte':
        rows = ''.join(
            f'<li><span class="num">{i:02d}</span><h3>{e(t)}</h3><p>{e(x)}</p></li>'
            for i, (t, x) in enumerate(a[2], 1))
        return f'<section><h2 class="h2">{e(a[1])}</h2><ol class="steps">{rows}</ol></section>'
    if art == 'spalten':
        rows = ''.join(f'<li><h3>{e(t)}</h3><p>{e(x)}</p></li>' for t, x in a[2])
        return f'<section><h2 class="h2">{e(a[1])}</h2><ul class="cols">{rows}</ul></section>'
    if art == 'hinweis':
        return f'<section class="note"><h3>{e(a[1])}</h3><p>{e(a[2])}</p></section>'
    if art == 'boxen':
        rows = ''.join(f'<div class="box"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in a[1])
        return f'<section class="boxes">{rows}</section>'
    raise ValueError(art)


def seite(s, nr, gesamt, stand):
    tel = '<br>'.join(f'<a href="tel:{h}">{e(t)}</a>' for t, h in TEL)
    return f"""
<div class="page" lang="{s['lang']}">
  <header class="head">
    <div class="head__top">
      <img class="head__logo" src="logo-ecs-weiss.png" alt="ECS">
      <p class="head__meta">{e(s['sprache'])}<br>{e(stand)}</p>
    </div>
    <p class="eyebrow">{e(s['eyebrow'])}</p>
    <h1 class="title">{e(s['titel'])}</h1>
    <p class="lead">{e(s['lead'])}</p>
  </header>
  <main class="body">
    <p class="intro">{e(s['intro'])}</p>
    {''.join(abschnitt(a) for a in s['abschnitte'])}
  </main>
  <footer class="foot">
    <p class="foot__note">{e(s['fuss'])}</p>
    <div class="foot__bar">
      <p><strong>{e(FIRMA)}</strong><br>{e(ADRESSE)} · <a href="mailto:{MAIL}">{MAIL}</a> ·
        <a href="https://{WEB}">{WEB}</a></p>
      <p class="foot__page">{tel}<br>{e(s['seite'])} {nr} / {gesamt}</p>
    </div>
  </footer>
</div>"""


def dokument(doc, stand):
    n = len(doc['seiten'])
    pages = ''.join(seite(s, i, n, stand[s['lang']]) for i, s in enumerate(doc['seiten'], 1))
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<title>{e(doc["meta"]["title"])}</title><style>{CSS}</style></head><body>{pages}</body></html>')


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


MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
          'September', 'Oktober', 'November', 'Dezember']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']


def main():
    jetzt = datetime.datetime.now()
    stand = {'de': f'Stand {MONATE[jetzt.month - 1]} {jetzt.year}',
             'en': f'As of {MONTHS[jetzt.month - 1]} {jetzt.year}'}
    # Schriften und Logo in einen Arbeitsordner kopieren (Chrome darf je nach
    # macOS-Freigabe nicht direkt im Desktop-Ordner lesen)
    tmp = tempfile.mkdtemp(prefix='ecs-pdf-')
    for f in ('assets/fonts/dm-sans-latin.woff2', 'assets/fonts/dm-sans-latin-ext.woff2',
              'assets/img/logo-ecs-weiss.png'):
        shutil.copy(os.path.join(ROOT, f), tmp)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome')
            page = browser.new_page()
            for doc in (EU, DRITTLAND):
                src = os.path.join(tmp, doc['datei'] + '.html')
                open(src, 'w', encoding='utf-8').write(dokument(doc, stand))
                page.goto('file://' + src)
                page.evaluate('document.fonts.ready')
                zu_lang = page.evaluate("[...document.querySelectorAll('.page')].map(p => p.scrollHeight - p.clientHeight)")
                if any(z > 0 for z in zu_lang):
                    raise SystemExit(f"{doc['datei']}: Inhalt zu lang für A4, Überlauf in px je Seite: {zu_lang}")
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
