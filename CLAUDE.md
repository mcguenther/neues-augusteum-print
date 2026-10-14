# Hinweise für Claude

Repo: 3D-Druckmodelle des Campus Augustusplatz (Uni Leipzig) aus OSM-Daten.
Antworten im Chat auf Deutsch.

## Arbeitsweise

Teilaufgaben wie Recherche, Datenquellen prüfen oder viele Dateien/Fotos
durchsuchen an Sonnet-Subagents (`model: "sonnet"`) abgeben, wo das sinnvoll ist;
Geometrie- und Generatorarbeit selbst machen.

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
   - README-Bilder (farbig, transparent, ohne Beschriftung): `vorschau/readme/`
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
Farben: je Gebäude `data/fassaden/<slug>.json` (Farben mit Messfeldern in Fotos +
Fassaden-Zonen), Fotokatalog `data/fotos.json` (Panoramax/Wikimedia Commons; Commons
drosselt geteilte IPs, `farben.py` wiederholt dann mit Wartezeit). `farben.py` misst
alles und schreibt `data/farben.json` (macht `generate.py` automatisch bei Änderungen).
Zonen prüfen: `python3 fassaden.py <slug>` → `vorschau/fassaden/<slug>_zonen.png`
(Fassadenansichten mit Höhen-/entlang-Raster) und `<slug>_fotos.jpg` (Messfelder).
Bei Farbänderungen zeigen: `vorschau/vergleich_farbig_ost.png`,
`vorschau/<quelle>/einzelgebaeude_farbig_1zu1000.png`, `vorschau/fassaden/`.

## README

`README.md` ist normaler Text und darf von Hand bearbeitet werden – nur die Blöcke
zwischen `<!-- AUTO:name -->` und `<!-- /AUTO:name -->` (Titelbild, Quellenvergleich,
Maßstäbe, Gebäudegalerie mit Maßen, Grundplatte) werden von `readme.py` überschrieben.
`generate.py`/`preview.py` rufen es nach dem Rendern auf; die Bilder dafür
(`preview.readme_assets`) entstehen farbig aus den `*_objekte.3mf`. Titel und
Kurzbeschreibung der Gebäude stehen in `BUILDINGS` (`generate.py`), neue Gebäude
erscheinen automatisch in der Galerie. Nach Änderungen die README mit
Chromium/Playwright (hell und dunkel) rendern und ansehen.

## Steckmechanismus (LED-Gebäude)

Plan und Prototyp für beleuchtete Gebäude (WS2812B, JST-XH-Stecker): `stecker/PLAN.md`.
`python3 steckmodul.py` erzeugt Dock-Platte, Steckmodule, Würfel und Passprobe nach
`stl/steckmodul/`, Vorschaubilder nach `vorschau/steckmodul/` und `stecker/daten.json`;
`python3 stecker/baue_ansicht.py` setzt daraus `stecker/ansicht.html` (3D-Ansicht mit
Animation) zusammen. Die Ausgabe muss `dicht=True` und „keine Kollisionen“ zeigen. Die
Steckermaße stehen oben in `steckmodul.py` und sind teils aus Zeichnungen abgeleitet.

## Steckmechanismus mit Dupont-Teilen (Plan B)

Alternative aus dem vorhandenen 2,54-mm-Dupont-Set: `stecker/dupont/PLAN.md`. Gebäude haben
immer einen Fuß; die Buchse sitzt im Fuß und wird in einer Druckpause eingelegt (Rückfallebene:
Kassette von unten mit Schieber). `python3 steckmodul_dupont.py` erzeugt Platte mit Docks A/B/C,
Deckel, Würfel (Pause/Kassette), Kassette, Schieber, Pausenprobe, Montagelehre und Passprobe nach
`stl/steckmodul_dupont/`, Bilder nach `vorschau/steckmodul_dupont/` und
`stecker/dupont/daten.json`; die Ausgabe nennt die Pausenhöhe und muss `dicht=True` und
„keine Kollisionen“ zeigen. `python3 stecker/dupont/baue_ansicht.py` baut
`stecker/dupont/ansicht.html`. Kaufteil-Maße (belegt/geschätzt markiert) stehen oben im
Generator; Zahlen in Plan und Seite kommen aus `dims()`, `forces()` und `building_table()`.
Hilfsfunktionen werden aus `steckmodul.py` importiert, dort also nichts umbenennen.

## Institutsgebäude mit Kassette

Echtes Gebäude für die Kassetten-Variante des Dupont-Plans: `stecker/institut/PLAN.md`.
`python3 steckmodul_institut.py` (rund 45 s) erzeugt Gebäude mit Fuß, Kassette, Schieber, Platte und Deckel nach
`stl/steckmodul_institut/`, Bilder nach `vorschau/steckmodul_institut/` und `stecker/institut/daten.json`;
`python3 stecker/institut/baue_ansicht.py` baut `stecker/institut/ansicht.html`. Die Ausgabe muss `dicht=True` und
„keine Kollisionen“ zeigen. Der Generator importiert Kaufteile und Hilfsfunktionen aus `steckmodul_dupont.py`.

## Festgelegte Maße der Winkelleiste (nicht ändern ohne neue Messung)

Der Körper der Winkelleiste ist **2,0 mm** (Höhe `HDR_BODY` und Dicke `HDR_T`), nicht 2,54. Das gilt für Passprobe,
Platte, Probestück, Institutsgebäude und alle Docks. Weitere Maße, Herkunft und Stand: `stecker/STAND.md`.

## Probedruck Kassette

Kleines Probestück (22 × 36 mm Ausschnitt des Institutsgebäude-Hauptbalkens) mit Kassette, Schieber, Mini-Platte und
Deckel: `python3 steckmodul_probe.py` (rund 15 s) schreibt STL, `LIESMICH.txt` und `probedruck_kassette.zip` nach
`stl/steckmodul_probe/` und Bilder nach `vorschau/steckmodul_probe/`. Es nutzt `steckmodul_institut.py`
(`build_all(source=…)`); die Ausgabe nennt Kollisionen und waagerechte Decken (Brücken) je Teil.
Die Passprobe (`passprobe()` in `steckmodul_probe.py`, `0_passprobe.stl`, 4 cm³) prüft nur die Winkelleiste (Körper neben den senkrechten Pins,
siehe `stecker/probe/winkelpin.html`): zwei Zeilen Taschenspiel, drei Spalten Pinlage. Anleitung als Seite:
`python3 stecker/probe/baue_passprobe.py` baut `stecker/probe/passprobe.html` aus `passprobe.template.html`.

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
