"""Suchbegriffe, Marken und Modelle für die strukturierten Daten (nicht sichtbar).

schema.py schreibt daraus WebPage.keywords und, auf Seiten mit Service, Service.brand.
Erfans Wunsch (25.10.2026): Fahrzeugnamen nicht als Text auf der Website, nur im Hintergrund.
Bewusst nicht enthalten: Zustand (Defekt, Unfall, hohe Laufleistung) und Sofortzahlung.
"""

# Auf jeder Seite
BASIS = [
    'ECS Exclusive Commerce Services GmbH', 'ECS GmbH', 'Elegance Car Safi', 'Nutzfahrzeughandel',
    'Nutzfahrzeuge', 'Export Nutzfahrzeuge', 'Import Nutzfahrzeuge', 'Gehrden', 'Hannover',
]
REGION = ['Region Hannover', 'Niedersachsen', 'Norddeutschland', 'Deutschland', 'Österreich', 'Schweiz', 'Tschechien']
TYPEN = [
    'Reisebus', 'Omnibus', 'Fernbus', 'Hochdecker', 'Doppeldecker', 'Midibus', 'Kleinbus', 'Schulbus',
    'Überlandbus', 'Linienbus', 'Stadtbus', 'Gelenkbus', 'Niederflurbus', 'Nutzfahrzeug', 'LKW', 'Lastwagen',
    'Sattelzug', 'Zugmaschine', 'Transporter', 'Kastenwagen', 'Lieferwagen', 'Kommunalfahrzeug', 'Baufahrzeug',
]

# Marken -> Modelle je Seite
REISEBUS = [
    ('Setra', 'S 515 HD, S 516 HD, S 516 HDH, S 517 HD, S 517 HDH, S 518 HD, S 519 HD, S 531 DT, S 431 DT, S 411 HD, S 415 HD, S 416 HDH, S 416 GT-HD, S 415 GT-HD, S 417 HDH, S 511 HD, S 315 HD, S 315 GT-HD, S 215 HD, ComfortClass 500, TopClass 500, ComfortClass 400, TopClass 400'),
    ('Mercedes-Benz', 'Tourismo, Tourismo M, Tourismo M/2, Tourismo L, Tourismo RHD, Tourismo K, Travego, Travego M, Travego L, Intouro, Intouro M, Integro, Tourino O 510, Sprinter Travel'),
    ('MAN', 'Lion’s Coach, Lion’s Coach C, Lion’s Coach L, Lion’s Intercity, Lion’s Regio'),
    ('Neoplan', 'Cityliner, Tourliner, Skyliner, Starliner, Jetliner, Trendliner, Euroliner, Transliner'),
    ('VDL', 'Futura FHD2, Futura FDD2, Futura FMD2'),
    ('Bova', 'Futura, Magiq'),
    ('Van Hool', 'TX15, TX16 Acron, TX16 Astron, TX17 Astron, TX16 Alicron, TDX27 Astromega, EX15, EX16, EX17, T915, T916, T917'),
    ('Irizar', 'i6, i6S, i8, i4, i3, PB, Century'),
    ('Scania', 'Touring, Interlink'),
    ('Higer', 'A30'),
    ('Volvo', '9700, 9900, 9500, 8900, B8R, B11R, B13R'),
    ('Iveco Bus', 'Evadys, Magelys, Crossway, Arway, Domino'),
    ('Irisbus', 'Evadys, Magelys, Crossway, Arway, Domino'),
    ('Temsa', 'HD 12, HD 13, LD 12, LD 13, MD9, Safari, Opalin'),
    ('Otokar', 'Navigo, Vectio, Territo, Kent'),
    ('Isuzu', 'Visigo, Turquoise, Novo'),
    ('BMC', 'Probus, Neocity'),
    ('Yutong', ''), ('King Long', ''), ('Kässbohrer', ''),
    # Kleinbusse und Midibusse
    ('Mercedes-Benz', 'Sprinter Kleinbus, Sprinter Transfer, Sprinter Travel, Sprinter City, Sprinter Mobility, Vito Tourer, V-Klasse'),
    ('VW', 'Crafter Kleinbus, T6.1 Caravelle, T7 Multivan'),
    ('Ford', 'Transit Kleinbus, Transit Custom Kombi'),
    ('Iveco', 'Daily Line, Daily Tourys'),
    ('Fiat', 'Ducato Kleinbus'), ('Renault', 'Master Bus'), ('Opel', 'Movano Bus'),
    ('Peugeot', 'Boxer Bus'), ('Citroën', 'Jumper Bus'), ('MAN', 'TGE Kleinbus'),
    ('Altas', ''), ('Indcar', ''), ('Ferqui', ''), ('Unvi', ''), ('Sitcar', ''), ('Kutsenits', ''),
    ('Esterer', ''), ('Tiger', ''), ('Car-Bus.net', ''), ('Excellence', ''),
]
LINIENBUS = [
    ('Mercedes-Benz', 'Citaro O 530, Citaro G, Citaro K, Citaro LE, Citaro Ü, Citaro hybrid, eCitaro, Conecto, Intouro Ü'),
    ('MAN', 'Lion’s City, Lion’s City G, Lion’s City 12, Lion’s City 18, Lion’s City E, Lion’s City LE, NL 263, NG 313'),
    ('Setra', 'S 415 NF, S 416 NF, S 415 UL, S 416 UL, S 415 LE business, MultiClass 400, MultiClass 500'),
    ('Solaris', 'Urbino 8.9 LE, Urbino 12, Urbino 18, InterUrbino'),
    ('Iveco', 'Urbanway, Crossway LE'),
    ('Irisbus', 'Citelis'),
    ('VDL', 'Citea SLF, Citea LLE'),
    ('Scania', 'Citywide, OmniCity, OmniLink'),
    ('Volvo', '7900, 7700, 8900'),
]
LKW = [
    ('Mercedes-Benz', 'Actros, Actros L, Arocs, Antos, Atego, Axor, Econic, Zetros, eActros'),
    ('MAN', 'TGX, TGS, TGM, TGL, TGA'),
    ('Scania', 'R-Serie, S-Serie, G-Serie, P-Serie, L-Serie, Streamline'),
    ('Volvo', 'FH, FH16, FM, FMX, FL, FE'),
    ('DAF', 'XF, XG, XG+, XD, CF, LF'),
    ('Iveco', 'S-Way, Stralis, X-Way, T-Way, Trakker, Eurocargo'),
    ('Renault Trucks', 'T, T High, C, K, D, D Wide, Premium, Magnum, Kerax'),
    ('Mitsubishi Fuso', 'Canter'), ('Isuzu', 'N-Serie, NPR, NQR, NLR'),
    ('Nissan', 'Cabstar, NT400'), ('Toyota', 'Dyna'), ('Ford Trucks', 'F-Max'),
    # Aufbau- und Kranhersteller
    ('Schmitz Cargobull', ''), ('Krone', ''), ('Kögel', ''), ('Meiller', ''), ('Schwarzmüller', ''),
    ('Wielton', ''), ('Langendorf', ''), ('Palfinger', ''), ('Hiab', ''), ('Fassi', ''), ('Atlas', ''),
    ('Liebherr', ''), ('Putzmeister', ''), ('Stetter', ''),
]
TRANSPORTER = [
    ('Mercedes-Benz', 'Sprinter, Sprinter 906, Sprinter 907, Sprinter 910, Sprinter 211 CDI, Sprinter 213 CDI, Sprinter 313 CDI, Sprinter 316 CDI, Sprinter 319 CDI, Sprinter 516 CDI, Sprinter 519 CDI, eSprinter, Vito, eVito, Citan'),
    ('VW', 'Crafter, Crafter 35, Crafter 50, T5, T6, T6.1, T7 Transporter, Caddy, ID. Buzz Cargo'),
    ('Ford', 'Transit, Transit Custom, Transit Connect, Transit Courier, E-Transit'),
    ('Iveco', 'Daily, Daily 35S, Daily 35C, Daily 50C, Daily 70C, eDaily'),
    ('Renault', 'Master, Trafic, Kangoo'),
    ('Opel', 'Movano, Vivaro, Combo'),
    ('Fiat', 'Ducato, Talento, Scudo, Doblò'),
    ('Peugeot', 'Boxer, Expert, Partner'),
    ('Citroën', 'Jumper, Jumpy, Berlingo'),
    ('Nissan', 'Interstar, NV400, Primastar, NV300'),
    ('Toyota', 'Proace, Proace City, Hiace'),
    ('MAN', 'TGE'),
    ('Hyundai', 'H350'),
]
BAU = [
    ('Mercedes-Benz', 'Unimog, Unimog U 20, Unimog U 400, Unimog U 423, Unimog U 427, Unimog U 430, Unimog U 530, Unimog U 535'),
    ('Multicar', 'M26, M27, M31, Tremo, Fumo'),
    ('Holder', ''), ('Aebi', ''), ('Hako', ''), ('Ladog', ''), ('Boschung', ''), ('Kärcher', ''),
    ('Schmidt', 'Swingo, Cleango'), ('Bucher', 'CityCat'), ('FAUN', 'Variopress, Rotopress, Viajet'),
    ('Zoeller', 'Medium XL'),
    ('Kaiser', ''), ('Kroll', ''), ('Wiedemann', ''), ('Müller Umwelttechnik', ''), ('Ruthmann', ''),
    ('Palfinger Platforms', ''), ('Multitel', ''), ('Versalift', ''), ('Rosenbauer', ''), ('Ziegler', ''),
    ('Magirus', ''),
    ('Liebherr', ''), ('Caterpillar', ''), ('Komatsu', ''), ('JCB', ''), ('Volvo CE', ''), ('Hitachi', ''),
    ('Kubota', ''), ('Takeuchi', ''), ('Wacker Neuson', ''), ('Kramer', ''), ('Atlas', ''), ('Bobcat', ''),
]

AUSSTATTUNG_BUS = ['Euro 5', 'Euro 6', 'Euro 6d', 'EEV', 'Automatik', 'Schaltgetriebe', 'Retarder', 'WC', 'Küche',
                   'Bordküche', 'Kühlschrank', 'Kaffeemaschine', 'Klimaanlage', 'Standheizung', 'Rollstuhllift',
                   'Gurte', '3-Punkt-Gurte', 'Fernseher', 'Bordmikrofon', '49 Sitze', '57 Sitze', '61 Sitze', '79 Sitze']
TECHNIK_LKW = ['Euro 5', 'Euro 6', 'Euro 6d', 'EEV', 'Automatik', 'Schaltgetriebe', 'Retarder', 'Intarder',
               'Allrad 4x4', '6x4', '6x2', '8x4', 'Lift-Achse', 'Fahrerkabine', 'Schlafkabine', 'Hochdach Kabine']
AUFBAUTEN_LKW = ['Sattelzugmaschine', 'Pritsche', 'Plane', 'Pritsche mit Plane', 'Koffer', 'Kühlkoffer',
                 'Ladebordwand', 'Kipper', 'Dreiseitenkipper', 'Abrollkipper', 'Absetzkipper', 'Hakenlift',
                 'Ladekran', 'Autotransporter', 'Tankwagen', 'Silofahrzeug', 'Betonmischer', 'Wechselbrücke BDF',
                 'Fahrgestell']
VARIANTEN_TRANSPORTER = ['Kastenwagen', 'Hochdach', 'Maxi', 'L2H2', 'L3H2', 'L3H3', 'L4H3', 'Pritsche', 'Doppelkabine',
                         'Pritsche Doppelkabine', 'Kipper', 'Koffer mit Ladebordwand', 'Kühlwagen', 'Fahrgestell',
                         'Kombi', '9-Sitzer', 'Werkstattwagen']
KOMMUNAL = ['Kehrmaschine', 'Müllwagen', 'Saugwagen', 'Kanalreinigungsfahrzeug', 'Winterdienstfahrzeug', 'Streuer',
            'Hubsteiger', 'Arbeitsbühne', 'Feuerwehrfahrzeug', 'Baumaschinen', 'Kommunaltechnik']

# Seite -> (Marken/Modelle, weitere Begriffe)
SEITEN = {
    '': ([], TYPEN + REGION),
    'ueber-uns': ([], REGION),
    'fahrzeuge': ([], ['gebrauchter Reisebus kaufen', 'Reisebus gebraucht', 'Linienbus gebraucht', 'LKW gebraucht',
                       'Sprinter gebraucht', 'Nutzfahrzeughändler', 'Bushändler']),
    'export': ([], ['Busexport', 'LKW Export', 'Export Afrika', 'Export Osteuropa', 'Export Naher Osten',
                    'Verzollung', 'Exportabwicklung']),
    'export-eu': ([], ['Export EU', 'Nutzfahrzeug Export EU', 'LKW Export EU', 'Bus Export EU', 'Fahrzeugexport EU',
                       'innergemeinschaftliche Lieferung', 'Gelangensbestätigung', 'Umsatzsteuer-Identifikationsnummer',
                       'USt-IdNr', 'EU-Checkliste', 'Export Osteuropa', 'Fahrzeuge exportieren']),
    'export-drittland': ([], ['Export Drittland', 'Export Drittländer', 'Ausfuhr Drittland', 'Nutzfahrzeug Export Drittland',
                              'Fahrzeugexport', 'Ausfuhrabfertigung', 'Ausfuhranmeldung', 'ATLAS Ausfuhr',
                              'Ausfuhrbegleitdokument', 'Ausgangsvermerk', 'Ausfuhrkennzeichen', 'Ausfuhrlieferung',
                              'Verzollung', 'Busexport', 'LKW Export', 'Export Afrika', 'Export Naher Osten',
                              'Export Osteuropa', 'Fahrzeuge exportieren']),
    'unsere-arbeit': ([], ['Nutzfahrzeug Ankauf', 'Nutzfahrzeug verkaufen', 'Ankauf mit Abholung']),
    'faq': ([], ['Nutzfahrzeug Ankauf', 'Nutzfahrzeug verkaufen']),
    'kontakt': ([], REGION),
    'reisebus-verkaufen': (REISEBUS, ['Reisebus verkaufen', 'Bus verkaufen', 'Bus Ankauf', 'Reisebus Ankauf',
                                      'Busunternehmen Fahrzeuge verkaufen', 'Ankauf mit Abholung', 'Kleinbus',
                                      'Midibus', 'Hochdecker', 'Doppeldecker', 'Fernbus'] + AUSSTATTUNG_BUS),
    'linienbus-verkaufen': (LINIENBUS, ['Linienbus verkaufen', 'Bus verkaufen', 'Bus Ankauf', 'Stadtbus',
                                        'Gelenkbus', 'Niederflurbus', 'Überlandbus', 'Schulbus']),
    'lkw-verkaufen': (LKW, ['LKW verkaufen', 'LKW Ankauf', 'Sattelzugmaschine verkaufen', 'Ankauf mit Abholung']
                      + AUFBAUTEN_LKW + TECHNIK_LKW),
    'transporter-verkaufen': (TRANSPORTER, ['Transporter verkaufen', 'Sprinter verkaufen', 'Sprinter Ankauf',
                                            'Kastenwagen Ankauf', 'Lieferwagen'] + VARIANTEN_TRANSPORTER),
    'bau-und-kommunalfahrzeuge-verkaufen': (BAU, ['Kommunalfahrzeug', 'Baufahrzeug'] + KOMMUNAL),
    'fuhrpark-verkaufen': ([], ['Fuhrpark verkaufen', 'Flottenauflösung', 'Nutzfahrzeug Ankauf',
                                'Nutzfahrzeug verkaufen', 'Busunternehmen Fahrzeuge verkaufen']),
}


def keywords(slug):
    """Begriffe der Seite: Basis + Seitenbegriffe + 'Marke Modell', ohne Dubletten."""
    marken, begriffe = SEITEN.get(slug, ([], []))
    out = BASIS + begriffe
    for marke, modelle in marken:
        out.append(marke)
        out += [marke + ' ' + m.strip() for m in modelle.split(',') if m.strip()]
    seen = set()
    return [k for k in out if not (k in seen or seen.add(k))]


def brands(slug):
    """Markennamen der Seite für Service.brand."""
    seen = []
    for marke, _ in SEITEN.get(slug, ([], []))[0]:
        if marke not in seen:
            seen.append(marke)
    return [{'@type': 'Brand', 'name': m} for m in seen]
