# KONTEXT:Wochenzeitung RSS Feed

Automatisch generierter RSS-Feed für die [KONTEXT:Wochenzeitung](https://www.kontextwochenzeitung.de/) – investigativer Regionaljournalismus aus Stuttgart/BW.

## Feed-URL

```
https://tilian86.github.io/kontext-rss/feed.xml
```

## Wie funktioniert das?

- GitHub Actions scrapt jeden Mittwoch (wenn die neue Ausgabe erscheint) die Startseite
- Extrahiert Artikeltitel, Links, Teaser, Rubriken und Datum
- Generiert eine RSS 2.0 XML-Datei
- Veröffentlicht über GitHub Pages

## Manuell ausführen

```bash
pip install requests beautifulsoup4
python scrape.py
```
