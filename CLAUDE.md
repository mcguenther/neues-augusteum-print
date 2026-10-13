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
   - Vergleich der Datenquellen: `vorschau/vergleich_1zu1000.png` (alle Einzelgebäude,
     OSM | LoD2 | Laserscan nebeneinander), `vorschau/vergleich/<name>_1zu1000.png`,
     `vorschau/vergleich_farbig_ost.png`
   - Alle Einzelgebäude einer Quelle: `vorschau/<quelle>/einzelgebaeude_1zu1000.png`
   - Geändertes Gebäude bzw. geänderte Datei: `vorschau/<quelle>/<maßstab>/<name>.png`
   - Farben: `vorschau/farben.png`, Messfelder `vorschau/farben_fotoproben.jpg`
   - Profile mit 3/4 Filamenten: `vorschau/filamente_vergleich.png` (alle Farben | 4 | 3, je
     Gesamtmodell, Seminargebäude-Bänder, Paulinum-Fenster), `vorschau/laserscan/1zu1500/komplett_campus_mit_extras_farbig_ost_<N>filamente.png`
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
Profile für wenige Filamente: `farben.PROFILE` (3 und 4 Filamente: Beige, Blaugrau, Graphit,
Rotbraun) mit den Regeln `PROFIL_FENSTER` (Glas/Fenster immer Blaugrau) und `PROFIL_DACH_BLAU`
(nur Paulinum, Neues Augusteum, Uniriese dürfen blaugraue Dächer haben, sonst Beige);
`generate.py` schreibt `komplett_*_objekte_<N>filamente.3mf` (ohne `--filamente` nur Laserscan mit Extras,
mit `--filamente N` für alle gewählten Quellen/Varianten). Nach Änderungen am Profil das Vergleichsbild zeigen.
Zonen prüfen: `python3 fassaden.py <slug>` → `vorschau/fassaden/<slug>_zonen.png`
(Fassadenansichten mit Höhen-/entlang-Raster) und `<slug>_fotos.jpg` (Messfelder).
Bei Farbänderungen zeigen: `vorschau/vergleich_farbig_ost.png`,
`vorschau/<quelle>/einzelgebaeude_farbig_1zu1000.png`, `vorschau/fassaden/`.

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
