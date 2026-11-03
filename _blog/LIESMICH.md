# Blog – so kommt ein neuer Beitrag auf die Website

Dieser Ordner wird **nicht** veröffentlicht (GitHub Pages/Jekyll überspringt Ordner mit `_`).
Aus jeder Datei `_blog/<name>.md` erzeugt `_tools/blog.py` die Seite
`https://elegancecarsafi.com/blog-<name>` und die Vorschau-Karte auf `/blog`.

## Ablauf

1. Titelbild (und weitere Bilder) als `.webp`/`.jpg`/`.png` nach `assets/img/` legen,
   Dateiname mit `blog-` beginnen, z. B. `assets/img/blog-lkw-verkaufen.webp`
   (mind. 1600 px breit, Querformat 3:2 oder 16:9 – die Vorschau-Karte zeigt 3:2).
2. `_blog/_vorlage.md` kopieren, umbenennen (`lkw-verkaufen-tipps.md` → URL `/blog-lkw-verkaufen-tipps`)
   und ausfüllen. Dateiname: nur Kleinbuchstaben, Ziffern, Bindestriche (ä → ae usw.).
3. `python3 _tools/blog.py` ausführen (braucht Pillow für die Bildvarianten, wie `_tools/bilder.py`).
4. Vorschau prüfen, dann committen und pushen – Sitemap und strukturierte Daten
   (BlogPosting) erzeugt der pre-commit-Hook automatisch.

Beiträge mit `entwurf: ja` oder einem Datum in der Zukunft werden nicht veröffentlicht.
Wird eine Datei gelöscht, entfernt `blog.py` die zugehörige Seite beim nächsten Lauf.

## Textformat

    ## Zwischenüberschrift
    ### Unterüberschrift
    Normaler Absatz. **fett**, *kursiv*, [Linktext](lkw-verkaufen) oder [extern](https://…)
    - Aufzählung
    1. nummerierte Liste
    ![Alt-Text: was auf dem Bild zu sehen ist](blog-datei.webp "Bildunterschrift (optional)")

Bilder stehen allein in einer Zeile mit Leerzeile davor und danach.
Der Beitragstext bleibt in allen Sprachen deutsch (wie die Fahrzeugtexte).

## SEO

- `titel`: die Hauptfrage bzw. das Haupt-Suchwort vorne, max. ca. 60 Zeichen.
- `beschreibung`: 120–155 Zeichen, Suchwort + Nutzen, erscheint bei Google unter dem Titel.
- `stichworte`: weitere Suchbegriffe (nur in den strukturierten Daten, nicht sichtbar).
- Im Text auf passende Seiten verlinken (z. B. `lkw-verkaufen`, `export-eu`, `kontakt`).
- Keine Modelllisten und keine Zustandsbegriffe (Defekt, Unfall, hohe Laufleistung) –
  wie auf der übrigen Website.

## Rechtlich sauber – Checkliste vor jedem Beitrag

- **Bilder:** nur eigene Fotos oder Bilder mit Nutzungsrecht (Lizenz schriftlich aufheben).
  Fremde Quelle → `bildnachweis:` ausfüllen (z. B. „Foto: Name / Plattform“). KI-Bild → `ki_bild: ja`
  (erscheint als „KI-generiert“ im Bildnachweis).
- **Kennzeichen, Firmenschriftzüge fremder Firmen, Telefonnummern** auf Fahrzeugen unkenntlich machen.
- **Personen** nur mit schriftlicher Einwilligung zeigen (auch Mitarbeitende).
- **Texte** selbst schreiben, nichts von anderen Websites kopieren; kurze Zitate mit Quelle.
- **Fakten** (Zoll, Steuern, Fristen) nur mit Quelle und neutral formulieren, mit Datum
  (`aktualisiert:` setzen, wenn sich etwas ändert). Keine Rechts- oder Steuerberatung versprechen.
- **Keine Einbettungen** (YouTube, Instagram, Google Maps) ohne Zwei-Klick-Lösung – sonst
  fließen Daten an Dritte und die Datenschutzerklärung müsste erweitert werden.
- Verantwortlich nach § 18 Abs. 2 MStV ist die ECS GmbH, vertreten durch den Geschäftsführer (Impressum).
- **Werbeaussagen** nur, wenn sie belegbar sind (z. B. „über 30 Jahre Erfahrung im Fahrzeughandel“, nicht „die GmbH seit 30 Jahren“). Keine absoluten Zusagen wie „wir haben für jedes Fahrzeug einen Abnehmer“.
- **Hersteller-Logos** nicht als Bild verwenden, Marken- und Modellnamen nur beschreibend. Der Hinweis zu Marken, Stand und „keine Rechtsberatung“ steht automatisch unter jedem Beitrag.
