# Campus Augustusplatz – 3D-Druck

Druckdateien für das **Neue Augusteum**, das **Paulinum** und die übrigen Gebäude
des Campus Augustusplatz der Universität Leipzig, erzeugt aus OpenStreetMap-Daten.
Jedes Gebäude lässt sich einzeln drucken. Zusätzlich gibt es ein Komplettmodell
und eine Grundplatte mit Aussparungen, in die man die einzeln gedruckten Gebäude
einsetzen kann.

![Vorschau](vorschau.png)

![Einzelgebäude 1:1000](vorschau/einzelgebaeude_1zu1000.png)

Vorschaubilder zu jeder einzelnen Datei liegen in [`vorschau/`](vorschau/).

## Gebäude

| Nr. | Gebäude | 1:1000 (B × T × H) | 1:1500 (B × T × H) |
|----|---------|--------------------|--------------------|
| 01 | Paulinum (Aula/Universitätskirche St. Pauli) | 55 × 41 × 55 mm | 38 × 28 × 37 mm |
| 02 | Neues Augusteum | 60 × 70 × 28 mm | 40 × 47 × 19 mm |
| 03 | Hörsaalgebäude (mit Mensa am Park) | 82 × 136 × 14 mm | 55 × 90 × 9 mm |
| 04 | Seminargebäude | 38 × 98 × 21 mm | 25 × 65 × 14 mm |
| 05 | Institutsgebäude / Wirtschaftswiss. Fakultät (Grimmaische Str. 12) | 105 × 48 × 18 mm | 70 × 32 × 12 mm |
| 06 | *Extra:* City-Hochhaus („Uniriese“) | 48 × 45 × 155 mm | 33 × 30 × 103 mm |
| 07 | *Extra:* Moritzbastei | 67 × 65 × 4 mm | 45 × 43 × 3 mm |

Paulinum und Neues Augusteum bilden in echt einen zusammenhängenden Baukörper;
hier sind sie getrennt, passen aber Kante an Kante zusammen.

## Dateien

Unter `stl/1zu1000/` und `stl/1zu1500/` liegen jeweils:

| Datei | Inhalt |
|-------|--------|
| `einzeln/NN_name.stl` | Jedes Gebäude einzeln, flache Unterseite, zentriert |
| `komplett_campus*.stl` | Alle Campusgebäude auf einer 2 mm Sockelplatte, in einem Stück |
| `komplett_campus_mit_extras*.stl` | Dasselbe mit Uniriese und Moritzbastei |
| `grundplatte_campus*.stl` | 3 mm Platte mit 1 mm tiefen Aussparungen (0,25 mm Spiel) für die Einzelgebäude |
| `komplett_*_objekte.3mf` | Sockelplatte und Gebäude als **getrennte Objekte** an der richtigen Position: im Slicer einzelne Teile weglassen oder verschiedenen Farben/Filamenten zuordnen |

Die Platten tragen eine eingravierte Beschriftung und einen Nordpfeil.

**1:1500** passt komplett auf übliche Druckbetten (Komplettmodell ca. 100 × 196 mm,
mit Extras 100 × 215 mm).
**1:1000** ist für die Platten zu groß für ein 250-mm-Bett und wurde deshalb
automatisch in `_teil1`/`_teil2` geteilt (stumpf aneinanderkleben). Die Einzelgebäude
passen auf jedes Bett.

## Druckhinweise

- Material: PLA, 0,4-mm-Düse, Schichthöhe 0,12–0,2 mm.
- Keine Stützstrukturen nötig: Überhänge (z. B. aufgeständerte Bauteile) sind
  zum Drucken nach unten aufgefüllt.
- Infill 10–15 %, 2–3 Wände genügen. Beim Uniriese (155 mm hoch bei 1:1000) ggf.
  Brim verwenden.
- Schrift auf den Platten: am besten mit 0,4-mm-Düse und feiner Schichthöhe;
  alternativ im Slicer „Ironing“ für die Oberseite.
- Ist die Passung in der Grundplatte zu stramm/locker, `POCKET_CLEARANCE` in
  `generate.py` anpassen und neu erzeugen.

## Genauigkeit

Die Modelle sind vereinfachte Klötzchenmodelle (LoD 1–2) aus OSM-Grundrissen,
Höhen und Dachformen – keine Fassadendetails. Wo OSM keine Höhe angibt, wird sie aus
der Geschosszahl geschätzt (3,5 m je Geschoss): Hörsaalgebäude 14 m,
Seminargebäude 21 m, Institutsgebäude 17,5 m. Paulinum (51 m, Turm 55 m) und
Neues Augusteum (28 / 12,6 / 8 m) nutzen die in OSM eingetragenen Höhen.

## Neu erzeugen / anpassen

```bash
pip install -r requirements.txt
python3 generate.py                # 1:1000 und 1:1500
python3 generate.py --scale 750    # anderer Maßstab (mehrfach angebbar)
python3 generate.py --fetch        # aktuelle OSM-Daten laden
python3 preview.py                 # nur Vorschaubilder neu rendern
python3 preview.py datei.stl --azim -90 --elev 40   # eigene Ansicht einer Datei
```

`generate.py` rendert am Ende automatisch alle Vorschaubilder nach `vorschau/`
(eigener Software-Renderer, kein Grafikkarte/Display nötig).

Welche Gebäude enthalten sind, steht in der Liste `BUILDINGS` in `generate.py`
(per OSM-ID). Weitere Gebäude, z. B. Gewandhaus (`r152769`) oder Oper
(`w18920139`), lassen sich dort ergänzen, sofern sie im Datenausschnitt
(`OSM_BBOX`) liegen. Weitere Parameter (Wandstärke, Plattendicke, Bettgröße)
stehen oben im Skript.

## Lizenz der Daten

Geometrie und Höhen: © OpenStreetMap-Mitwirkende, verfügbar unter der
[Open Database License (ODbL)](https://www.openstreetmap.org/copyright).
Die erzeugten Modelle sind ein abgeleitetes Werk; bei Weitergabe bitte die
Quelle nennen.
