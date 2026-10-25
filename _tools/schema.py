#!/usr/bin/env python3
"""Erzeugt die strukturierten Daten (JSON-LD) aller Seiten.

- Jede Seite: Organization + AutoDealer (Firmendaten) + WebPage
- Startseite zusätzlich WebSite
- Unterseiten: BreadcrumbList (Startseite > Seite)
- Seiten mit FAQ-Akkordeon: FAQPage – Fragen/Antworten werden direkt aus dem
  sichtbaren HTML gelesen, damit Schema und Text immer übereinstimmen
- Ankaufseiten und Export: Service (Ankaufseiten mit Service.brand)
- WebPage.keywords: Suchbegriffe, Marken und Modelle aus _tools/seo_begriffe.py
- WebPage.primaryImageOfPage: erstes Foto im <main> mit Alt-Text als caption,
  sonst das og:image der Seite
Keine Bewertungen (Review/AggregateRating), weil es keine belegten gibt.
Der Fahrzeugbestand (Vehicle/Offer) kommt per JS: js/bestand-schema.js.

Der Block steht zwischen <!-- schema:start --> und <!-- schema:end --> im <head>.
Aufruf:  python3 _tools/schema.py   (läuft auch im pre-commit-Hook)
"""
import glob, html, json, os, re

from seo_begriffe import brands, keywords

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://elegancecarsafi.com/'
START, END = '<!-- schema:start -->', '<!-- schema:end -->'

ORG_ID = BASE + '#organization'
DEALER_ID = BASE + '#autodealer'
SITE_ID = BASE + '#website'

ADDRESS = {
    '@type': 'PostalAddress',
    'streetAddress': 'Bünteweg 13',
    'postalCode': '30989',
    'addressLocality': 'Gehrden',
    'addressRegion': 'Niedersachsen',
    'addressCountry': 'DE',
}
SAME_AS = [
    'https://www.instagram.com/elegancecarsafi/',
    'https://www.tiktok.com/@elegancecarsafi',
    'https://www.google.com/search?kgmid=/g/11xt2n0_th',   # Google-Unternehmensprofil
    'https://home.mobile.de/ELEGANCECARSAFI',               # Händlerseite bei mobile.de
]
# beide Nummern wie auf der Website (die zweite steht auch im Google-Profil)
PHONES = ['+49 171 362 1298', '+49 1514 0315387']
BUY_COUNTRIES = [{'@type': 'Country', 'name': n} for n in ('Deutschland', 'Österreich', 'Schweiz', 'Tschechien')]

ORGANIZATION = {
    '@type': 'Organization',
    '@id': ORG_ID,
    'name': 'ECS Exclusive Commerce Services GmbH',
    'legalName': 'ECS Exclusive Commerce Services GmbH',
    'alternateName': ['Elegance Car Safi', 'ECS GmbH'],
    'url': BASE,
    'logo': {'@type': 'ImageObject', 'url': BASE + 'assets/img/logo-ecs.png', 'width': 1000, 'height': 562},
    'email': 'info@elegancecarsafi.com',
    'telephone': PHONES,
    'vatID': 'DE452884436',
    # Handelsregister wie im Impressum – verknüpft die Firma mit Registereinträgen
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'Handelsregister',
                   'value': 'HRB 228497, Amtsgericht Hannover'},
    'address': ADDRESS,
    'sameAs': SAME_AS,
}

DEALER = {
    '@type': 'AutoDealer',
    '@id': DEALER_ID,
    'name': 'ECS Exclusive Commerce Services GmbH – Elegance Car Safi',
    'parentOrganization': {'@id': ORG_ID},
    'url': BASE,
    # echte Hof-Fotos zuerst, dann das Vorschaubild
    'image': [BASE + 'assets/img/opt/pitch-lkw-reihe-1448.jpg',
              BASE + 'assets/img/opt/fuhrpark-atego-reihe-1086.jpg',
              BASE + 'assets/img/opt/pitch-atego-koffer-1448.jpg',
              BASE + 'assets/img/og-hero.jpg'],
    'logo': BASE + 'assets/img/logo-ecs.png',
    'telephone': PHONES,
    'email': 'info@elegancecarsafi.com',
    'address': ADDRESS,
    'geo': {'@type': 'GeoCoordinates', 'latitude': 52.3225528, 'longitude': 9.5968503},
    'openingHoursSpecification': [
        # wie im Google-Unternehmensprofil; Sa–So geschlossen
        {'@type': 'OpeningHoursSpecification',
         'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
         'opens': '08:00', 'closes': '18:00'},
        {'@type': 'OpeningHoursSpecification',
         'dayOfWeek': ['Friday'],
         'opens': '08:00', 'closes': '12:00'},
    ],
    'areaServed': BUY_COUNTRIES,
    # Kerngebiete wie auf der Website (Ankaufseiten, Bestand, Export)
    'knowsAbout': ['Nutzfahrzeughandel', 'Import und Export von Nutzfahrzeugen', 'Reisebusse',
                   'Linienbusse', 'Kleinbusse', 'LKW', 'Sattelzugmaschinen', 'Transporter',
                   'Bau- und Kommunalfahrzeuge', 'Verzollung und Exportabwicklung'],
    'knowsLanguage': ['de', 'en', 'pl', 'ru', 'es', 'ar'],
    'sameAs': SAME_AS,
}

# Service-Angaben je Seite (Seite -> Name, serviceType)
SERVICES = {
    'reisebus-verkaufen': ('Ankauf von Reisebussen und Kleinbussen', 'Ankauf gebrauchter Reisebusse'),
    'linienbus-verkaufen': ('Ankauf von Linienbussen', 'Ankauf gebrauchter Linienbusse'),
    'lkw-verkaufen': ('Ankauf von LKW und Sattelzugmaschinen', 'Ankauf gebrauchter LKW'),
    'transporter-verkaufen': ('Ankauf von Transportern', 'Ankauf gebrauchter Transporter'),
    'bau-und-kommunalfahrzeuge-verkaufen': ('Ankauf von Bau- und Kommunalfahrzeugen', 'Ankauf gebrauchter Bau- und Kommunalfahrzeuge'),
    'fuhrpark-verkaufen': ('Ankauf von Fuhrparks', 'Ankauf von Firmenfahrzeugen und Flotten'),
    'export': ('Export und Verzollung von Nutzfahrzeugen', 'Export gebrauchter Nutzfahrzeuge'),
}
# Kurznamen für die Brotkrumen (wie in Navigation und Footer)
CRUMB = {
    'ueber-uns': 'Über uns', 'fahrzeuge': 'Fahrzeuge', 'unsere-arbeit': 'Unsere Arbeit',
    'export': 'Export', 'kontakt': 'Kontakt', 'faq': 'FAQ',
    'reisebus-verkaufen': 'Reisebus verkaufen', 'linienbus-verkaufen': 'Linienbus verkaufen',
    'lkw-verkaufen': 'LKW verkaufen', 'transporter-verkaufen': 'Transporter verkaufen',
    'bau-und-kommunalfahrzeuge-verkaufen': 'Bau- und Kommunalfahrzeuge verkaufen',
    'fuhrpark-verkaufen': 'Fuhrpark verkaufen',
}
# Übergeordnete Seite im Menü (Untermenü "Unsere Arbeit")
PARENT = {k: 'unsere-arbeit' for k in (
    'reisebus-verkaufen', 'linienbus-verkaufen', 'lkw-verkaufen', 'transporter-verkaufen',
    'bau-und-kommunalfahrzeuge-verkaufen', 'fuhrpark-verkaufen')}
EXPORT_AREA = [{'@type': 'Continent', 'name': n} for n in ('Europa', 'Asien', 'Afrika')]
EXPORT_AREA += [{'@type': 'Place', 'name': n} for n in ('Osteuropa', 'Naher Osten')]


def text(fragment):
    """HTML-Fragment -> reiner Text (ohne SVG, Leerraum zusammengefasst)."""
    fragment = re.sub(r'<svg[\s\S]*?</svg>', '', fragment)
    fragment = re.sub(r'<br\s*/?>', ' ', fragment)
    fragment = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(fragment)).strip()


def meta(head, attr, key):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(key)), head)
    return html.unescape(m.group(1)) if m else ''


def main_photo(body, head):
    """Erstes Foto im <main> (ohne Logos/Markenlogos) -> (URL, Alt-Text); sonst og:image."""
    for tag in re.findall(r'<img\b[^>]*>', body):
        src = re.search(r'\bsrc="([^"]+)"', tag)
        if not src:
            continue
        name = os.path.basename(src.group(1))
        if name.startswith(('logo-', 'marke-')) or name.endswith('.svg'):
            continue
        alt = re.search(r'\balt="([^"]*)"', tag)
        return BASE + src.group(1).lstrip('/'), html.unescape(alt.group(1)) if alt else ''
    return meta(head, 'property', 'og:image'), meta(head, 'property', 'og:image:alt')


def faq_items(body):
    items = []
    for m in re.finditer(r'<details class="accordion-item">([\s\S]*?)</details>', body):
        block = m.group(1)
        q = re.search(r'<span class="accordion__label">([\s\S]*?)</span>', block)
        a = re.search(r'<div class="accordion__body">([\s\S]*?)</div>', block)
        if q and a:
            items.append({'@type': 'Question', 'name': text(q.group(1)),
                          'acceptedAnswer': {'@type': 'Answer', 'text': text(a.group(1))}})
    return items


def build(path):
    src = open(path, encoding='utf-8').read()
    head = src[:src.index('</head>')]
    if re.search(r'<meta name="robots" content="[^"]*noindex', head):
        return None                                  # 404, Rechtliches, Detailseite
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', head)
    if not canon:
        return None
    url = canon.group(1)
    slug = url[len(BASE):]
    title = html.unescape(re.search(r'<title>([\s\S]*?)</title>', head).group(1)).strip()
    desc = meta(head, 'name', 'description')
    body = src[src.index('<main'):src.index('</main>')]
    h1 = text(re.search(r'<h1[^>]*>([\s\S]*?)</h1>', body).group(1))
    img, caption = main_photo(body, head)

    page = {
        '@type': 'WebPage',
        '@id': url + '#webpage',
        'url': url,
        'name': title,
        'description': desc,
        'inLanguage': 'de-DE',
        'isPartOf': {'@id': SITE_ID},
        'about': {'@id': DEALER_ID},
        'publisher': {'@id': ORG_ID},
        # Suchbegriffe, Marken und Modelle – nur hier, nicht im sichtbaren Text (_tools/seo_begriffe.py)
        'keywords': ', '.join(keywords(slug)),
    }
    if img:
        page['primaryImageOfPage'] = {'@type': 'ImageObject', '@id': url + '#primaryimage',
                                      'url': img, 'contentUrl': img, 'caption': caption,
                                      'inLanguage': 'de-DE'}
        page['image'] = {'@id': url + '#primaryimage'}
    graph = [ORGANIZATION, DEALER]
    if not slug:
        graph.append({'@type': 'WebSite', '@id': SITE_ID, 'url': BASE,
                      'name': 'Elegance Car Safi',
                      'alternateName': ['ECS GmbH', 'ECS Exclusive Commerce Services GmbH'],
                      'inLanguage': 'de-DE', 'publisher': {'@id': ORG_ID}})
    else:
        trail = [('Startseite', BASE)]
        if slug in PARENT:                       # Ankaufseiten liegen unter "Unsere Arbeit"
            trail.append((CRUMB[PARENT[slug]], BASE + PARENT[slug]))
        trail.append((CRUMB.get(slug, h1), url))
        crumbs = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': n, 'item': u} for i, (n, u) in enumerate(trail, 1)
        ]}
        page['breadcrumb'] = {'@id': url + '#breadcrumb'}
        graph.append(crumbs)
    graph.append(page)

    if slug in SERVICES:
        name, stype = SERVICES[slug]
        graph.append({'@type': 'Service', '@id': url + '#service', 'name': name, 'serviceType': stype,
                      'description': desc, 'url': url, 'provider': {'@id': DEALER_ID},
                      'areaServed': EXPORT_AREA if slug == 'export' else BUY_COUNTRIES})
        if brands(slug):
            graph[-1]['brand'] = brands(slug)

    faqs = faq_items(body)
    if faqs:
        graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'url': url, 'mainEntity': faqs})

    data = {'@context': 'https://schema.org', '@graph': graph}
    block = (START + '\n<script type="application/ld+json">\n' +
             json.dumps(data, ensure_ascii=False, indent=1) + '\n</script>\n' + END)

    if START in src:
        new = re.sub(re.escape(START) + r'[\s\S]*?' + re.escape(END), lambda m: block, src, count=1)
    else:
        # alten, handgeschriebenen AutoDealer-Block der Startseite ersetzen
        new = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>\n?', '', src, count=1) \
            if 'application/ld+json' in head else src
        new = new.replace('</head>', block + '\n</head>', 1)
    if new != src:
        open(path, 'w', encoding='utf-8').write(new)
        return os.path.basename(path)
    return ''


if __name__ == '__main__':
    changed = []
    for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        r = build(p)
        if r:
            changed.append(r)
    print('\n'.join(changed))
