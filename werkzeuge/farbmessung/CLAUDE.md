# Hinweise für `werkzeuge/farbmessung/` (Fassadenfarben aus Fotos)

Wird geladen, sobald Dateien in diesem Ordner gelesen werden. Die Skripte der Messung selbst liegen im Repo-Wurzelverzeichnis:
`farbmessung.py` (Messung, 45 KB), `registrierung.py` (Katalog und Ausrichtung), `skyline.py` und `kamera.py` (Pose, Projektion),
`szene.py` (Modell, Sonne), `vergleich.py`, `fassaden.py` (Zonen), `farben.py` (Zusammenführung). Daten: `data/messfotos.json`
(Katalog), `data/messung.json` (Ergebnis), `data/fassaden/<slug>.json` (Zonen und Farben), `FOTOQUELLEN.md` (Urheber, Lizenzen).

**Token sparen:** `bericht_runde2_vorlage.html`, `viewer.js` und die erzeugte `vorschau/farbvergleich_runde2/index.html`
(3,3 MB) nicht lesen; die Quellen sind die Vorlagen und `bericht_runde2_texte.json`.

## Fotoprojektion

- Messung: `python3 farbmessung.py messen` (liest `data/messfotos.json`, schreibt `data/messung.json`).
- Neue Fotos aufnehmen und ausrichten: `registrierung.py suche [--seeds=3] <id>` (Pose per Himmelslinie plus Kantenabgleich),
  Überlagerung ansehen (`registrierung.py pruefen <id>`, **vollständig ansehen, nicht nur im Kontaktbogen**), bei Passung
  `"geprueft": true` im Katalog setzen, sonst `"verworfen": "<Grund>"`. (Das Sichten der Überlagerungen kann der Agent
  `foto-registrierung` übernehmen.)
- Fotos aus einer Recherche (Flickr/Commons über Openverse) übernimmt
  `werkzeuge/farbmessung/katalog_recherche.py <katalog.json> <nr> …`. Panoramax lieferte nur beschattete Fassaden.
  Wikimedia drosselt geteilte IPs (die Commons-API liefert 429; Seiten und `thumb.wikimedia.org` mit ≤ Originalbreite gehen).
- Nur freie Fotos (CC), Urheber und Lizenz in `FOTOQUELLEN.md`; professionelle Fotos sind geschützt und nicht verwendet.
- `farben.py` setzt `data/farben.json` zusammen (macht `generate.py` automatisch bei Änderungen).

## Alt/neu-Vergleich

- Runde 1: Alt/neu aus der Foto-Kamera: `werkzeuge/farbmessung/vergleich_bilder.py <alte farben.json>`, dann
  `werkzeuge/farbmessung/bericht.py <alte farben.json>` (HTML nach `vorschau/farbvergleich/`).
- Runde 2 (vorher/nachher mit interaktivem 3D-Modell, three.js über CDN): `vergleich_bilder.py <alte farben.json> <ordner>
  --fotos id,id,…`, dann `bericht_runde2.py <alte farben.json>` (liest daneben `messung.json` und `vorschau_laserscan/` des
  alten Stands; Texte in `bericht_runde2_texte.json`; HTML nach `vorschau/farbvergleich_runde2/`).
- HTML-Berichte als Artifact veröffentlichen (siehe Wurzel-`CLAUDE.md`).
