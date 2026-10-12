# Campus Augustusplatz – 3D-Druck

Druckdateien für das **Neue Augusteum**, das **Paulinum** und die übrigen Gebäude
des Campus Augustusplatz der Universität Leipzig. Jedes Gebäude lässt sich einzeln
drucken. Zusätzlich gibt es ein Komplettmodell und eine Grundplatte mit Aussparungen,
in die man die einzeln gedruckten Gebäude einsetzen kann.

Alle Modelle gibt es aus **drei Datenquellen nebeneinander**, damit man sie vergleichen
kann (Details siehe [Datenquellen](#datenquellen)):

| Quelle | Ordner | Detailgrad |
|--------|--------|------------|
| OpenStreetMap | `stl/osm/` | Klötzchen aus Grundriss + Höhe, Höhen teils nur geschätzt |
| 3D-Stadtmodell LoD2 der Stadt Leipzig | `stl/lod2/` | amtliche Höhen, Dachformen und größere Dachaufbauten |
| Laserscan GeoSN 2023 (+ LoD2) | `stl/laserscan/` | gemessene Dachlandschaft: Technikaufbauten, Oberlichter, Höfe, Turmkrone |

![Vorschau](vorschau.png)

![Vergleich der Quellen](vorschau/vergleich_1zu1000.png)

![Vergleich farbig](vorschau/vergleich_farbig_ost.png)

Vorschaubilder zu jeder einzelnen Datei liegen in [`vorschau/`](vorschau/)
(`vorschau/<quelle>/…`, Einzelvergleiche in `vorschau/vergleich/`).

## Gebäude

Maße bei 1:1000 (B × T × H in mm, 1 mm = 1 m):

| Nr. | Gebäude | OSM | LoD2 | Laserscan |
|----|---------|-----|------|-----------|
| 01 | Paulinum (Aula/Universitätskirche St. Pauli) | 55 × 41 × 55 | 59 × 37 × 59 | 59 × 37 × 59 |
| 02 | Neues Augusteum | 60 × 70 × 28 | 63 × 78 × 34 | 63 × 78 × 38 |
| 03 | Hörsaalgebäude (mit Mensa am Park) | 82 × 136 × 14 | 83 × 136 × 23 | 83 × 136 × 25 |
| 04 | Seminargebäude | 38 × 98 × 21 | 39 × 100 × 24 | 39 × 100 × 28 |
| 05 | Institutsgebäude / Wirtschaftswiss. Fakultät (Grimmaische Str. 12) | 105 × 48 × 18 | 106 × 45 × 31 | 105 × 45 × 32 |
| 06 | *Extra:* City-Hochhaus („Uniriese“) | 48 × 45 × 155 | 47 × 46 × 142 | 47 × 46 × 145 |
| 07 | *Extra:* Moritzbastei | 67 × 65 × 4 | 67 × 64 × 6 | 67 × 64 × 9 |

Auffällig: Für Hörsaal-, Seminar- und Institutsgebäude hat OSM keine Höhen, sie
werden dort aus der Geschosszahl geschätzt und sind deutlich zu niedrig (z. B.
Institutsgebäude 17,5 m statt 31 m). Der Uniriese ist in OSM mit Antenne (155 m)
eingetragen; LoD2/Laserscan enden an der Dachkrone (142–145 m).

Paulinum und Neues Augusteum bilden in echt einen zusammenhängenden Baukörper;
hier sind sie getrennt, passen aber Kante an Kante zusammen. Bei LoD2/Laserscan
verläuft die Trennung entlang der OSM-Grundrisse (siehe `lod2.py`).

## Dateien

Unter `stl/<quelle>/1zu1000/` und `stl/<quelle>/1zu1500/` liegen jeweils:

| Datei | Inhalt |
|-------|--------|
| `einzeln/NN_name.stl` | Jedes Gebäude einzeln, flache Unterseite, zentriert |
| `komplett_campus*.stl` | Alle Campusgebäude auf einer 2 mm Sockelplatte, in einem Stück |
| `komplett_campus_mit_extras*.stl` | Dasselbe mit Uniriese und Moritzbastei |
| `grundplatte_campus*.stl` | 3 mm Platte mit 1 mm tiefen Aussparungen (0,25 mm Spiel) für die Einzelgebäude |
| `komplett_*_objekte.3mf` | Sockelplatte und Gebäude als **getrennte Objekte** an der richtigen Position, **mehrfarbig vorbereitet**: jedes Gebäude hat sein Fassaden-Filament, die Dächer sind mit dem Dach-Filament vorbemalt (siehe [Mehrfarbig drucken](#mehrfarbig-drucken)) |

Die Platten tragen eine eingravierte Beschriftung (mit Quellenangabe) und einen Nordpfeil.

**1:1500** passt komplett auf übliche Druckbetten (Komplettmodell ca. 100 × 196 mm,
mit Extras 100 × 215 mm).
**1:1000** ist für die Platten zu groß für ein 250-mm-Bett und wurde deshalb
automatisch in `_teil1`/`_teil2` geteilt (stumpf aneinanderkleben). Die Einzelgebäude
passen auf jedes Bett.

## Datenquellen

### OpenStreetMap (`stl/osm/`)
Grundrisse, Höhen und Dachformen aus OSM (`data/augustusplatz.osm`), Klötzchenmodell
LoD 1–2. Wo OSM keine Höhe angibt, wird sie aus der Geschosszahl geschätzt
(3,5 m je Geschoss).

### 3D-Stadtmodell LoD2 der Stadt Leipzig (`stl/lod2/`)
[Open Data der Stadt Leipzig](https://opendata.leipzig.de/dataset/3d-stadtmodell-lod2-stadt-leipzig)
(CityGML, Stand 2023/24, ohne Texturen). Amtliche Gebäudehöhen und Dachformen aus
Kataster und Laserscan, inkl. größerer Dachaufbauten. Im Repo liegt nur der
Ausschnitt mit den Campus-Gebäuden (`data/lod2_campus.gml`). Der Gebäudekomplex
Paulinum/Augusteum/Hörsaalgebäude ist dort *ein* Gebäude mit 47 Bauteilen und wird
entlang der OSM-Grundrisse aufgeteilt; Volumen = Prismen unter allen Dachflächen.

### Laserscan GeoSN (`stl/laserscan/`)
[Laserscandaten des GeoSN](https://www.geodaten.sachsen.de/downloadbereich-digitale-hoehenmodelle-4851.html)
(Befliegung 9. 1. 2023, ca. 18 Punkte/m²). Ausschnitt in `data/laserscan_campus.laz`.
Je Gebäude wird ein Höhenraster (30 cm, an der Hauptachse des Gebäudes
ausgerichtet, damit Kanten nicht treppig werden) aus den Dachpunkten gebildet und
mit dem LoD2-Grundriss ausgeschnitten – dadurch senkrechte, glatte Außenwände. Wo
der Scan höchstens ±0,5 m vom LoD2-Dach abweicht, wird die glatte LoD2-Dachfläche
genommen (kein Messrauschen); schmale Vertiefungen unter dem LoD2-Dach (< 3 m,
meist Messlücken an Dachkanten oder über Glas) werden ebenfalls aus LoD2 gefüllt.
Alles andere (Aufbauten, Oberlichter, Lichthöfe, Dachterrassen, Turmkrone) kommt
aus dem Scan. Fassadendetails (Fenster, Gesimse) enthält auch der Laserscan
nicht – er sieht nur von oben.

### Weitere geprüfte Quellen
- **LoD2 des GeoSN** (landesweit, Stand 2024): gleiche Detailstufe wie das Leipziger
  Modell, deshalb nicht zusätzlich eingebaut.
- **DOM1** (Oberflächenmodell 1 m, GeoSN): gröber als die Punktwolke.
- **Texturiertes LoD2 / LoD3 der Stadt Leipzig**: existiert, ist aber nur im
  Web-Viewer zu sehen, nicht als Open Data herunterladbar.
- **Schrägluftbilder**: für Leipzig nicht offen verfügbar.

## Farben

`data/farben.json` enthält je Gebäude eine Fassaden- und eine Dachfarbe (plus
Akzentfarben), erzeugt mit `python3 farben.py`:

- **Dächer**: [Luftbild 2024 der Stadt Leipzig](https://opendata.leipzig.de/dataset/luftbild-2024-20-cm-bodenauflosung-stadt-leipzig)
  (20 cm, dl-de/by-2-0), Median im Grundriss. In den farbigen Vorschauen wird jede
  Dachfläche einzeln aus dem Luftbild eingefärbt. Das GeoSN-Orthofoto 2025 ist auch
  frei, aber im März aufgenommen, mit langen Schatten des Uniriesen über dem Campus.
- **Fassaden**: Für Fassaden gibt es keine offenen Farbdaten (das texturierte
  Stadtmodell ist nicht frei). Gemessen wird deshalb in offen lizenzierten
  **Straßenfotos** in festgelegten Bildausschnitten (`data/fassaden_proben.json`),
  mit Weißabgleich am grauen Pflaster in derselben Beleuchtung:
  - Paulinum, Neues Augusteum, Institutsgebäude: Panoramax (März 2022),
  - Hörsaal- und Seminargebäude: 360°-Fahrt durch die Universitätsstraße
    (Mapillary-Spiegel auf Wikimedia Commons, Oktober 2025) – `farben.py` rechnet
    die Panoramen selbst in normale Ansichten um,
  - Uniriese und Moritzbastei: Fotos von Wikimedia Commons.

  Je Gebäude wird über mehrere Messfelder (oft aus mehreren Fotos) der Median
  genommen. Auffällige Zweitfarben (rote Verkleidung der Mensa am Park, rote
  Brücke am Seminargebäude, rotbraunes Band am Institutsgebäude, dunkle Sockel)
  stehen als Akzentfarben in `data/farben.json`.

![Farben](vorschau/farben.png)

![Messfelder](vorschau/farben_fotoproben.jpg)

Die Farben sind Anhaltswerte (Fotos im Schatten, Glasfassaden spiegeln) – zum
Auswählen von Filamenten taugen sie, als exakte Farbtöne nicht.

## Mehrfarbig drucken

Die `*_objekte.3mf` enthalten die Farben in den Formaten, die die Slicer selbst
lesen (geprüft am Quellcode von PrusaSlicer 2.7–2.9, Bambu Studio und OrcaSlicer):

- **Objekt-Filament** = Fassadenfarbe des Gebäudes (`Metadata/model_settings.config`
  für Bambu/Orca, `Metadata/Slic3r_PE_model.config` für PrusaSlicer).
- **Dächer vorbemalt** mit der Dachfarbe (`paint_color` bzw.
  `slic3rpe:mmu_segmentation` an den Dachdreiecken) – im Slicer als
  Mehrfarben-Bemalung sichtbar und nachbearbeitbar.
- Zusätzlich `basematerials` (3MF-Standard) für Betrachter wie den Windows-3D-Viewer;
  Slicer ignorieren diese.

Die Filament-Nummern F1–F10 sind für alle Dateien gleich; welche Farbe zu welcher
Nummer gehört, zeigt `vorschau/farben.png` (Feld „F…“, Liste in
`data/farben.json` → `_filamente`). Kaum unterscheidbare Töne (z. B. die hellen
Fassaden von Paulinum und Hörsaalgebäude) teilen sich ein Filament
(`FILAMENT_TOLERANZ` in `farben.py`). Die Filamentfarben selbst kann eine 3MF-Datei
ohne vollständiges Druckerprofil nicht mitbringen: Bambu Studio/OrcaSlicer legen
beim Öffnen automatisch genügend Filamente an (Farben anpassen bzw. gleiche Farben
zusammenlegen), in PrusaSlicer braucht es ein Mehrfarb-Druckerprofil (MMU/XL).
Wer weniger Filamente hat, ordnet einfach mehreren Nummern dasselbe Filament zu.
Cura liest keine Farben aus 3MF.

## Druckhinweise

- Material: PLA, 0,4-mm-Düse, Schichthöhe 0,12–0,2 mm.
- Keine Stützstrukturen nötig: Überhänge (z. B. aufgeständerte Bauteile) sind
  zum Drucken nach unten aufgefüllt.
- Infill 10–15 %, 2–3 Wände genügen. Beim Uniriese (ca. 145 mm hoch bei 1:1000) ggf.
  Brim verwenden.
- Laserscan-Modelle: viele kleine Dachdetails (0,3 mm Raster) – feine Schichthöhe
  (0,12 mm) lohnt sich.
- Schrift auf den Platten: am besten mit 0,4-mm-Düse und feiner Schichthöhe;
  alternativ im Slicer „Ironing“ für die Oberseite.
- Ist die Passung in der Grundplatte zu stramm/locker, `POCKET_CLEARANCE` in
  `generate.py` anpassen und neu erzeugen.

## Neu erzeugen / anpassen

```bash
pip install -r requirements.txt
python3 generate.py                     # alle Quellen, 1:1000 und 1:1500
python3 generate.py --quelle laserscan  # nur eine Quelle (mehrfach angebbar)
python3 generate.py --scale 750         # anderer Maßstab (mehrfach angebbar)
python3 generate.py --fetch             # Quelldaten neu laden (LoD2 130 MB, Laserscan 240 MB)
python3 farben.py                       # Farben neu bestimmen (data/farben.json)
python3 preview.py                      # nur Vorschaubilder neu rendern
python3 preview.py datei.stl --azim -90 --elev 40   # eigene Ansicht einer Datei
```

`generate.py` rendert am Ende automatisch alle Vorschaubilder nach `vorschau/`
(eigener Software-Renderer, keine Grafikkarte/kein Display nötig).

Welche Gebäude enthalten sind, steht in der Liste `BUILDINGS` in `generate.py`
(per OSM-ID). Weitere Gebäude, z. B. Gewandhaus (`r152769`) oder Oper
(`w18920139`), lassen sich dort ergänzen, sofern sie im Datenausschnitt
(`OSM_BBOX`) liegen; für LoD2/Laserscan danach `--fetch` ausführen, damit die
Ausschnitte in `data/` neu geschnitten werden. Weitere Parameter (Wandstärke,
Plattendicke, Bettgröße) stehen oben in `generate.py`, die Laserscan-Parameter
(Raster, Einrast-Toleranz) oben in `laserscan.py`.

## Lizenzen der Daten

- Geometrie und Höhen OSM: © OpenStreetMap-Mitwirkende,
  [ODbL](https://www.openstreetmap.org/copyright).
- 3D-Stadtmodell LoD2 und Luftbild 2024: © Stadt Leipzig, Amt für Geoinformation und
  Bodenordnung, [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0).
- Laserscandaten: © Landesamt für Geobasisinformation Sachsen (GeoSN),
  [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0).
- Straßenfotos für die Fassadenfarben (`vorschau/farben_fotoproben.jpg`, Urheber und
  Lizenz je Foto in der Bildunterschrift und in `data/fassaden_proben.json`):
  Robot8A via [Panoramax](https://panoramax.xyz) (CC-BY-SA-4.0); osmplus_org
  (Mapillary-Spiegel), Krzysztof Golik, Chabe01 (alle CC BY-SA 4.0), Fred Romero
  (CC BY 2.0) und NutzerAusBerlin (CC0) via
  [Wikimedia Commons](https://commons.wikimedia.org).

Die erzeugten Modelle sind abgeleitete Werke; bei Weitergabe bitte die Quellen nennen.
