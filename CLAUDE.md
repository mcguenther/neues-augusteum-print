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
   Vorschaubilder nach `vorschau/` und die README-Bilder nach `vorschau/readme/`; danach aktualisiert
   `readme.py` die Platzhalter-Blöcke (`<!-- AUTO:... -->`) in `README.md`.
   Nur Vorschauen neu erzeugen: `python3 preview.py`.
2. Die passenden PNGs **im Chat mit `SendUserFile` (display: "render") zeigen**,
   nicht nur Pfade nennen. Vorher selbst mit `Read` ansehen und prüfen, ob die
   Darstellung plausibel ist.
   - Überblick: `vorschau/readme/hero.png` (Gesamtmodell 1:1500, farbige Objekte)
   - Alle README-Bilder (transparent, ohne Beschriftung): `vorschau/readme/`
   - Alle Einzelgebäude auf einen Blick: `vorschau/einzelgebaeude_1zu1000.png`
   - Geändertes Gebäude bzw. geänderte Datei: `vorschau/<maßstab>/<name>.png`
   - Bei Änderungen nach Möglichkeit Vorher/Nachher zeigen (alte Version vor der
     Änderung rendern, z. B. nach `$SCRATCHPAD` mit `--out`).
3. Auch bei reinen Fragen zu einem Modell das zugehörige Vorschaubild zeigen.
4. Beliebige Dateien/Ansichten rendern:
   `python3 preview.py datei.stl [--azim -90 --elev 40] [--out ordner]`
   (`--azim -90` = Blick von Süden, `0` = von Osten/Augustusplatz).

Die gerenderten Bilder in `vorschau/` werden mit committet.

## README

`README.md` ist normaler Text und darf von Hand bearbeitet werden – nur die Blöcke
zwischen `<!-- AUTO:name -->` und `<!-- /AUTO:name -->` (Titelbild, Campus-Vergleich,
Gebäudegalerie, Grundplatte) werden von `readme.py` überschrieben. Titel und
Kurzbeschreibung der Gebäude stehen in `BUILDINGS` (`generate.py`). Neue Gebäude
tauchen nach `python3 generate.py` automatisch in der Galerie auf. Nach Änderungen
die README mit Chromium/Playwright (hell und dunkel) rendern und ansehen.

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
