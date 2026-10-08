#!/usr/bin/env python3
"""Erzeugt die strukturierten Daten (JSON-LD) aller Seiten.

- Jede Seite: Organization + AutoDealer (Firmendaten) + WebPage
- Startseite zusätzlich WebSite
- Unterseiten: BreadcrumbList (Startseite > Seite)
- Seiten mit FAQ-Akkordeon: FAQPage – Fragen/Antworten werden direkt aus dem
  sichtbaren HTML gelesen, damit Schema und Text immer übereinstimmen
- Ankaufseiten und Export: Service
Keine Bewertungen (Review/AggregateRating), weil es keine belegten gibt.
Der Fahrzeugbestand (Vehicle/Offer) kommt per JS: js/bestand-schema.js.

Der Block steht zwischen <!-- schema:start --> und <!-- schema:end --> im <head>.
Aufruf:  python3 _tools/schema.py   (läuft auch im pre-commit-Hook)
"""
import glob, html, json, os, re

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
]
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
    'telephone': '+49 171 362 1298',
    'vatID': 'DE452884436',
    'address': ADDRESS,
    'sameAs': SAME_AS,
}

DEALER = {
    '@type': 'AutoDealer',
    '@id': DEALER_ID,
    'name': 'ECS Exclusive Commerce Services GmbH – Elegance Car Safi',
    'parentOrganization': {'@id': ORG_ID},
    'url': BASE,
    'image': BASE + 'assets/img/og-hero.jpg',
    'logo': BASE + 'assets/img/logo-ecs.png',
    'telephone': '+49 171 362 1298',
    'email': 'info@elegancecarsafi.com',
    'address': ADDRESS,
    'geo': {'@type': 'GeoCoordinates', 'latitude': 52.3225528, 'longitude': 9.5968503},
    'openingHoursSpecification': [
        {'@type': 'OpeningHoursSpecification',
         'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
         'opens': '09:00', 'closes': '19:00'},
        {'@type': 'OpeningHoursSpecification',
         'dayOfWeek': ['Saturday', 'Sunday'],
         'opens': '10:00', 'closes': '18:00'},
    ],
    'areaServed': BUY_COUNTRIES,
    'knowsLanguage': ['de', 'en', 'pl', 'ru', 'es', 'ar'],
    'sameAs': SAME_AS,
}

# Service-Angaben je Seite (Seite -> Name, serviceType)
SERVICES = {
    'reisebus-verkaufen': ('Ankauf von Reisebussen', 'Ankauf gebrauchter Reisebusse'),
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


def text(fragment):
    """HTML-Fragment -> reiner Text (ohne SVG, Leerraum zusammengefasst)."""
    fragment = re.sub(r'<svg[\s\S]*?</svg>', '', fragment)
    fragment = re.sub(r'<br\s*/?>', ' ', fragment)
    fragment = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(fragment)).strip()


def meta(head, attr, key):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(key)), head)
    return html.unescape(m.group(1)) if m else ''


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
    }
    graph = [ORGANIZATION, DEALER]
    if not slug:
        graph.append({'@type': 'WebSite', '@id': SITE_ID, 'url': BASE,
                      'name': 'Elegance Car Safi', 'alternateName': 'ECS GmbH',
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
