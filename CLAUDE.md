# Hinweise für Claude

Repo: 3D-Druckmodelle des Campus Augustusplatz (Uni Leipzig) aus OSM-Daten.
Antworten im Chat auf Deutsch.

## Setup

In Cloud-Sessions installiert der SessionStart-Hook
(`.claude/hooks/session-start.sh`) die Abhängigkeiten automatisch. Lokal bzw.
falls etwas fehlt:

```bash
pip install -r requirements.txt
```

## Vorschaubilder im Chat – immer

Der Nutzer will in jedem Chat einen visuellen Eindruck bekommen. Deshalb:

1. Nach **jeder Änderung** an Modellen oder Generator `python3 generate.py`
   ausführen. Das erzeugt die STL/3MF-Dateien und rendert automatisch alle
   Vorschaubilder nach `vorschau/` (und `vorschau.png` für die README).
   Nur Vorschauen neu erzeugen: `python3 preview.py`.
2. Die passenden PNGs **im Chat mit `SendUserFile` (display: "render") zeigen**,
   nicht nur Pfade nennen. Vorher selbst mit `Read` ansehen und prüfen, ob die
   Darstellung plausibel ist.
   - Überblick: `vorschau.png` (Gesamtmodell 1:1500, Laserscan-Variante, farbig)
   - Vergleich der Datenquellen: `vorschau/vergleich_1zu1000.png` (alle Einzelgebäude,
     OSM | LoD2 | Laserscan nebeneinander), `vorschau/vergleich/<name>_1zu1000.png`,
     `vorschau/vergleich_farbig_ost.png`
   - Alle Einzelgebäude einer Quelle: `vorschau/<quelle>/einzelgebaeude_1zu1000.png`
   - Geändertes Gebäude bzw. geänderte Datei: `vorschau/<quelle>/<maßstab>/<name>.png`
   - Farben: `vorschau/farben.png`, Messfelder `vorschau/farben_fotoproben.jpg`
   - Bei Änderungen nach Möglichkeit Vorher/Nachher zeigen (alte Version vor der
     Änderung rendern, z. B. nach `$SCRATCHPAD` mit `--out`).
3. Auch bei reinen Fragen zu einem Modell das zugehörige Vorschaubild zeigen.
4. Beliebige Dateien/Ansichten rendern:
   `python3 preview.py datei.stl [--azim -90 --elev 40] [--out ordner]`
   (`--azim -90` = Blick von Süden, `0` = von Osten/Augustusplatz).

Die gerenderten Bilder in `vorschau/` werden mit committet.

## Datenquellen

`generate.py` erzeugt jede Quelle in `stl/<quelle>/` (`--quelle osm|lod2|laserscan`,
Standard: alle). Die Rohdaten-Ausschnitte liegen in `data/`; `--fetch` lädt sie neu
(LoD2: 130 MB Stadtmodell, Laserscan: 240 MB Kachel – nur bei Bedarf).
Farben: `python3 farben.py` schreibt `data/farben.json` (Messfelder für Fassaden in
`data/fassaden_proben.json`).

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
