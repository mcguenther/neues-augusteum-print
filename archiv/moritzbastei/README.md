# Moritzbastei (zurückgestellt)

Vorerst aus Generator, Vorschaubildern, README und Steckmechanismus (`plug/`) herausgenommen. Alles, was zum
Wiederaufnehmen nötig ist, steht hier oder liegt weiter unverändert im Repo.

## Daten

| Quelle | Woher | Wo im Repo |
|---|---|---|
| OSM | Relation `r1769862` (Name „Moritzbastei“, Multipolygon, Gebäudehöhe aus OSM) | in `data/augustusplatz.osm` (bbox `12.3770,51.3370,12.3830,51.3400`, `generate.py --fetch`) |
| LoD2 | Stadtmodell Leipzig; `lod2.py` ordnet die Gebäude per Überlappung mit dem OSM-Grundriss zu | `data/lod2_campus.gml` |
| Laserscan | GeoSN, Kachel mit Höhenraster 0,3 m; Kronen über Dachkanten liefern mehrere Echos, `laserscan.py` nimmt das letzte | `data/laserscan_campus.laz` |
| Luftbild | Dachklassen (Dachfarbe) | `data/luftbild2024_campus.jpg` |

Alle Rohdaten-Ausschnitte bleiben in `data/`; die Moritzbastei liegt darin weiter drin, sie wird nur nicht mehr verarbeitet.

Maße (Laserscan, 1:1500): 44,6 × 43,0 × 6,1 mm. Im README stand bei 1:1000 „67 × 64 × 9 mm“. Sie wurde als Gruppe `extra`
geführt (nur in `komplett_campus_mit_extras*`). Im Steckmechanismus war sie als einziges Gebäude ohne LED vorgesehen
(zu niedrig; mit tieferer Mulde, Fuß 13,8 mm bei 1:1500 bzw. 10,8 mm bei 1:1000, wäre es gegangen; siehe `plug/PLAN.md`).

## Farben

- `fassade.json`: handgesetzte Zonen und Farben (Format wie `data/fassaden/<slug>.json`). Basis Ziegel `#8c5439`,
  Naturstein `#928e89` (Süd/Ost/Südwest, teils mit kahlem Efeu), Putzanbau am Nordende `#d8d2c4`, Brüstungsband Ziegel.
  Die Farben stammen aus der Handmessung bzw. Prüfläufen an sonnigen Fotos; die Fotoprojektion (`farbmessung.py`) lieferte
  für die Moritzbastei keine registrierbaren sonnigen Fotos, sie hat also **keine** Messwerte.
- `farben_gemessen.json`: der letzte Eintrag aus `data/farben.json` (aufgelöst, mit Filamentzuordnung).
- Filament-Profile (`farben.PROFILE`): Ziegel wurde bei 4 Filamenten Rotbraun, Stein Beige/Blaugrau, Dach Beige (nie Blaugrau,
  das Blaugrau im Luftbild ist dort Schatten).

## Fotos

Katalog `data/fotos.json` (Einträge `07_moritzbastei_1` … `_4`, Commons, Joachim Köhler / andere) und `data/messfotos.json`
(Katalog der Fotoprojektion; zwei Fotos tragen die Gebäudenummer `07`). Quellenangaben: `FOTOQUELLEN.md` (Zeilen `07_pano_se_*`).
Beide Dateien sind unverändert geblieben, die Einträge werden nur nicht mehr benutzt.

## Wiederaufnehmen

1. In `generate.py` den Eintrag aus `ARCHIV` zurück nach `BUILDINGS` verschieben.
2. `fassade.json` nach `data/fassaden/07_moritzbastei.json` kopieren.
3. In `preview.py` (`NAMES`), `werkzeuge/farbmessung/bericht.py` (`NAMEN`) und `plug/parts.py` (`BUILDINGS`) die Zeile wieder einfügen.
4. `python3 generate.py`, dann README und Vorschau neu (`readme.py` erzeugt die Galerie von selbst).
