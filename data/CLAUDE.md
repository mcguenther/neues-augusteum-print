# Hinweise für `data/` (Rohdaten, Farben, Fassaden-Zonen)

Wird geladen, sobald Dateien unter `data/` gelesen werden. Allgemeines steht in der `CLAUDE.md` im Repo-Wurzelverzeichnis. Querverweise: Fotomessung `werkzeuge/farbmessung/CLAUDE.md`, Bildkatalog `vorschau/CLAUDE.md`, Steckmechanismus `plug/CLAUDE.md`.

## Inhalt

| Datei | Was | Lesen? |
|---|---|---|
| `augustusplatz.osm` | OSM-Ausschnitt (Quelle `osm`) | nur gezielt (`grep`) |
| `lod2_campus.gml` | LoD2-Stadtmodell, Ausschnitt (Quelle `lod2`) | nie ganz lesen |
| `laserscan_campus.laz` | Laserscan-Punktwolke GeoSN (Quelle `laserscan`), binär | nie lesen |
| `luftbild2024_campus.jpg` | Luftbild für Dachfarben | nur mit `Read` als Bild, wenn nötig |
| `fassaden/<slug>.json` | handgesetzte Farbzonen je Gebäude (klein, hier wird editiert) | ja |
| `farben.json` | von `farben.py` zusammengesetzt, **nicht von Hand ändern** (`generate.py` erneuert sie bei Änderungen) | nein |
| `messung.json`, `messfotos.json`, `fotos.json` | Ergebnis bzw. Katalog der Fotomessung (`messung.json` 70 KB) | nur gezielt |
| `innenhof.json` | Objekte des Innenhofs (gemessen mit `werkzeuge/innenhof_messen.py`) | bei Hof-Arbeit |
| `cache/` | gitignored, wird bei Bedarf erzeugt | nein |

Gebäude-Slugs: `01_paulinum`, `02_neues_augusteum`, `03_hoersaalgebaeude`, `04_seminargebaeude`, `05_institutsgebaeude`,
`06_city_hochhaus`, `08_innenhof` (die Moritzbastei ist archiviert: `archiv/moritzbastei/`, Wiederaufnehmen steht dort in der README).

## Datenquellen

`generate.py` erzeugt jede Quelle in `stl/<quelle>/` (`--quelle osm|lod2|laserscan`,
Standard: alle). Die Rohdaten-Ausschnitte liegen in `data/`; `--fetch` lädt sie neu
(LoD2: 130 MB Stadtmodell, Laserscan: 240 MB Kachel – nur bei Bedarf).

## Farben

Je Gebäude `data/fassaden/<slug>.json` (handgesetzte Zonen + Rückfallfarben als `hex`;
die alten Messfelder stehen als `proben_alt`). Die Fassadenfarben von Paulinum, Neuem Augusteum,
Institutsgebäude und City-Hochhaus (Seminargebäude: nur einzelne Zonen) kommen aus der **Fotoprojektion**
(Ablauf: `werkzeuge/farbmessung/CLAUDE.md`). Eine gemessene Farbe lässt sich in `data/fassaden/<slug>.json` mit
`"beibehalten": "<Grund>"` auf dem Wert der Handmessung festhalten (so bleiben die weißen Platten von Hörsaal-, Seminar- und
Institutsgebäude hell, das Mittel über Platten und Fenster wurde zu grau); Flächen darüber gelten nur ab ΔE 25 (`HALTEN_MIN_DE`).
`farben.py` setzt `data/farben.json` zusammen (macht `generate.py` automatisch bei Änderungen).

Filamente des Nutzers: `farben.FILAMENTE` (Stand 19.10.2026: Hauptfarben Beige, Graublau, Weinrot, Space Grey; Reserve Weiß,
Schwarz, Grasgrün; Hex-Werte nach den Namen geschätzt, nicht gemessen), höchstens `farben.GLEICHZEITIG` = 4 je Druck. Profile:
`farben.PROFILE` (4 = die Hauptfarben, 3 = ohne Weinrot) mit den Regeln `PROFIL_FENSTER` (Glas/Fenster immer Graublau),
`PROFIL_ROLLEN` (rote Dächer Weinrot, Baumkronen und Beete Grasgrün, wenn im Satz) und `PROFIL_DACH_BLAU` (nur Paulinum, Neues Augusteum,
Uniriese dürfen graublaue Dächer haben, sonst die hellste Farbe); `farben.waehle_filamente` sucht je Druck die besten 4 aus allen 7
(flächengewichteter ΔE, Reserve mit Aufschlag `RESERVE_KOSTEN`). `generate.py` schreibt `komplett_*_objekte_<N>filamente.3mf`
(ohne `--filamente` nur Laserscan mit Extras, mit `--filamente N` für alle gewählten Quellen/Varianten); die steckbaren Gebäude
farbig macht `python3 -m plug.colour` (siehe `plug/CLAUDE.md`). Nach Änderungen am Profil das Vergleichsbild zeigen.

Zonen prüfen: `python3 fassaden.py <slug>` → `vorschau/fassaden/<slug>_zonen.png`
(Fassadenansichten mit Höhen-/entlang-Raster) und `<slug>_fotos.jpg` (Fotos der Messung).

Bei Farbänderungen zeigen: `vorschau/vergleich_farbig_ost.png`,
`vorschau/<quelle>/einzelgebaeude_farbig_1zu1000.png`, `vorschau/fassaden/`.

## Schneller testen nach Farbänderungen

- Nur ein Gebäude prüfen: `python3 fassaden.py <slug>` (Sekunden), statt `generate.py`.
- Gesamtmodell farbig prüfen: `python3 generate.py --fast --quelle laserscan` (siehe Wurzel-`CLAUDE.md`), Bilder in `vorschau-fast/`.
- Die Fotomessung (`farbmessung.py messen`) nur starten, wenn sich `messfotos.json` oder die Geometrie geändert hat;
  `generate.py` erkennt Änderungen an den Farben selbst (`refresh_colours`).
