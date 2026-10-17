# Hinweise für Claude

Repo: 3D-Druckmodelle des Campus Augustusplatz (Uni Leipzig) aus OSM-Daten, LoD2 und Laserscan.
Antworten im Chat auf Deutsch.

Diese Datei ist bewusst kurz und gilt für alles. Details stehen in Unterordner-`CLAUDE.md`, die automatisch geladen werden,
sobald man dort Dateien liest:

| Datei | Inhalt |
|---|---|
| `plug/CLAUDE.md` | Steckmechanismus (LED-Gebäude): Befehlstabelle, Maße, Testdruck-Modus, Logbuch, Artifact-Regeln |
| `data/CLAUDE.md` | Rohdaten, Farben, Fassaden-Zonen, Filament-Profile |
| `werkzeuge/farbmessung/CLAUDE.md` | Fassadenfarben aus Fotos (Registrierung, Messung, Alt/neu-Berichte) |
| `vorschau/CLAUDE.md` | Bildkatalog: welches Vorschaubild man wozu im Chat zeigt |

## Arbeitsweise

Teilaufgaben wie Recherche, Datenquellen prüfen oder viele Dateien/Fotos
durchsuchen an Sonnet-Subagents (`model: "sonnet"`) abgeben, wo das sinnvoll ist;
Geometrie- und Generatorarbeit selbst machen. Fertige Agents in `.claude/agents/`:

| Agent | Wofür |
|---|---|
| `quellen-recherche` | Datenquellen, Fotos, Lizenzen im Netz suchen und prüfen (ändert nichts) |
| `vorschau-pruefer` | `generate.py --fast` bzw. `preview.py` laufen lassen, `dicht=True` auswerten, Bilder sichten, knapp berichten |
| `foto-registrierung` | Fotos am Modell ausrichten, Überlagerungen sichten, `geprueft`/`verworfen` im Katalog setzen |
| `plug-pruefer` | Generatoren in `plug/` laufen lassen, dicht/Kollisionen/Überhänge auswerten |
| `logbuch-pfleger` | bestätigte Auswertung einer Testdruck-Runde ins Logbuch eintragen |

Den Agents gibt man Ziel, betroffene Dateien und was schon ausgeschlossen ist mit; ihre Berichte sind kurz gehalten (Logs und
Bilder bleiben im Agent). Auswertung und Entscheidungen bleiben im Hauptchat.

## Projektkarte

```
generate.py            Hauptskript: Modelle bauen (STL, 3MF), Platten, Farben, Vorschauen; Optionen unten
preview.py             Software-Renderer, Standard-Vorschauen, README-Bilder (`python3 preview.py datei.stl`)
readme.py              schreibt die AUTO-Blöcke der README
parallel.py            Mehrprozess-Hilfe (`--jobs`), Laufzeit je Phase
laserscan.py lod2.py   Geometrie je Datenquelle (Quelle osm steckt in generate.py)
innenhof.py            Innenhof als eigenes Druckteil (blockiger Umriss ohne Stege, Treppen als Stufen auf dem Einsatz; Vergleich vorher/nachher: `plug/hof/`)
hohl.py               Gebäude als Hohlkörper (Wand 0,8, unten offen, glattes 45°-Gewölbe bis zum First unter Decken mit mehr als 10 mm Spannweite); `generate.py` schreibt sie nach `einzeln_hohl/` (STL einfarbig, 3MF farbig), `--no-hohl` lässt sie weg; Plan: `plug/hollow/plan.html`
farben.py              Farben und Filament-Profile (3/4/15) → data/farben.json
fassaden.py            Fassaden-Zonen, Prüfansichten (`python3 fassaden.py <slug>`)
farbmessung.py kamera.py skyline.py registrierung.py szene.py vergleich.py   Fotomessung der Fassadenfarben
data/                  Rohdaten-Ausschnitte, Zonen je Gebäude (data/fassaden/), Katalog der Messfotos
stl/<quelle>/1zu1000|1zu1300|1zu1500/   Ausgabe (osm, lod2, laserscan; einzeln/ massiv, einzeln_hohl/ Hohlkörper) + stl/steckmodul_*   (erzeugt, eingecheckt)
vorschau/              Ausgabe-Bilder (erzeugt, eingecheckt); vorschau/readme/ für die README
stl-fast/ vorschau-fast/   Ausgabe von `--fast` (gitignored)
plug/                  Steckmechanismus für LED-Gebäude (eigenes Paket, Logbuch in plug/logbook/); Slicer-Einstellungen der steckbaren Gebäude: plug/slicer.md
werkzeuge/             Hilfsskripte: farbmessung/, performance/ (Messung der Laufzeit), innenhof_messen.py, rosette_kamera.py
archiv/                zurückgestellte Gebäude (moritzbastei/)
esphome/               ESPHome-Firmware des ESP32 (`doktorhut-max.yaml`, Pinbelegung und Verhalten in `esphome/README.md`; `secrets.yaml` nicht im Repo)
docs/                  Komponenten-Doku (Display, Hauptschalter, ESP32 …): je Bauteil eine .md, Fotos in docs/bilder/, Datenblätter in docs/datenblaetter/
README.md FOTOQUELLEN.md   README (Blöcke AUTO), Foto-Urheber und Lizenzen
```

Gebäude und ihre Slugs: `BUILDINGS` in `generate.py` (Paulinum, Neues Augusteum, Hörsaal-, Seminar-, Institutsgebäude, City-Hochhaus „Uniriese“,
Innenhof; Moritzbastei in `ARCHIV`). Quellen: `osm`, `lod2`, `laserscan`; Maßstäbe 1:1000, 1:1300 und 1:1500.

## Setup

In Cloud-Sessions installiert der SessionStart-Hook
(`.claude/hooks/session-start.sh`) die Abhängigkeiten automatisch. Lokal bzw.
falls etwas fehlt:

```bash
pip install -r requirements.txt
```

## Laufzeit / Schnelllauf

Ein voller `python3 generate.py` brauchte früher ~24 min, fast alles davon im
Software-Renderer (`preview.render`) und nicht in den Laserdaten. Heute: ~5 min auf
4 Kernen (alle Optimierungen ergeben dasselbe Ergebnis; Details und Messung:
`werkzeuge/performance/`).

- **Zum Testen/Iterieren: `python3 generate.py --fast`** – gleiche Daten, aber Laser-Raster
  0,6 statt 0,3 m, Vorschau ohne Kantenglättung, nur Maßstab 1:1500, keine
  README-/Fassaden-/Vergleichsbilder (~100 s). Schreibt nach `stl-fast/` und
  `vorschau-fast/` (nicht eingecheckt, fasst `stl/` und `vorschau/` nicht an). Mit
  `--quelle laserscan` / `--scale 1000` weiter eingrenzbar. Für Bilder im Chat reicht das.
- Vor dem Commit der echten Ausgaben (`stl/`, `vorschau/`, README) den vollen Lauf ohne `--fast`.
- `--jobs N` begrenzt die Prozesse (Standard: alle Kerne, `--jobs 1` seriell); am Ende
  druckt `generate.py` die Laufzeit je Phase.

### Noch schneller: den kleinsten Lauf wählen

| Ich will … | Aufruf | Dauer (4 Kerne) |
|---|---|---|
| nur prüfen, ob die Geometrie baut und `dicht=True` ist | `generate.py --fast --quelle <q> --no-preview` | osm ca. 20 s, laserscan ca. 46 s (gemessen 16.10.2026) |
| ein Bild einer Quelle | `generate.py --fast --quelle <q>` | osm kürzer (ohne Bilder 20 s), laserscan ca. 100 s |
| alles im Schnelllauf | `generate.py --fast` | ca. 100 s (der Laserscan bestimmt die Zeit, `--quelle laserscan` spart nichts) |
| **eine** Datei/Ansicht rendern | `python3 preview.py datei.stl [--azim -90 --elev 40] --out <ordner>` | Sekunden |
| ein Gebäude farblich prüfen | `python3 fassaden.py <slug>` | ca. 10 s |
| die bestehenden Bilder nur ansehen | `Read` auf `vorschau/…` (kein Lauf nötig) | – |

Regeln dazu:

- Nur so viel bauen, wie die Änderung berührt: `--quelle` und `--scale` immer eingrenzen; `--no-preview`, wenn kein Bild gebraucht wird.
- Der Laserscan ist die teure Quelle (500 000 Dreiecke, vor allem beim Rendern); die Änderung betrifft meist `osm`/`lod2` nicht, und
  umgekehrt. Für Änderungen an gemeinsamem Code (`BUILDINGS`, Farben, Platte) reicht `--fast --quelle osm` als Funktionstest und
  `--fast --quelle laserscan` für das Bild.
- Lange Läufe (voller Lauf, `plug.series`, `plug.build_all`) mit `run_in_background` starten und währenddessen weiterarbeiten
  (z. B. Texte schreiben); nicht pollen, die Benachrichtigung kommt. Mehrere unabhängige Läufe nicht gleichzeitig auf den 4 Kernen
  laufen lassen, wenn man ihre Zeiten vergleichen will (`parallel.JOBS` teilt sich die Kerne).
- Bildprüfung und Logauswertung an den Agent `vorschau-pruefer` bzw. `plug-pruefer` geben: der Hauptchat bekommt dann 10 Zeilen statt des Logs.
- Neue Beschleunigungen (z. B. Cache, weniger Rendering) in `werkzeuge/performance/README.md` mit Messung festhalten; sie müssen
  dasselbe Ergebnis liefern (STL byte-gleich bzw. Fläche/Volumen gleich und dicht).

## Token sparen

- Nicht lesen (groß, erzeugt oder binär): `stl/**`, `data/*.laz`, `data/*.gml`, `data/*.osm`, `plug/**/*.html` (Seiten, 80 KB bis 430 KB),
  `plug/views/**/data.json`, `vorschau/farbvergleich_runde2/index.html` (3,3 MB), `data/messung.json` (70 KB). Gesucht wird mit `Grep`,
  gelesen wird gezielt mit `offset`/`limit`. Quellen der HTML-Seiten sind die `build*.py` und `*.template.html`.
- Große Skripte nicht ganz lesen: `generate.py` (900 Zeilen; Optionen und `main()` ab Zeile ~840, Gebäudetabelle ab ~39),
  `farbmessung.py` (930), `plug/dupont.py` (950), `plug/series2.py` (600). Erst `grep -n "^def \|^class "`, dann den Abschnitt lesen.
- Lange Dokumente nur abschnittsweise: `README.md` (26 KB; Blöcke `AUTO` sind erzeugt), `plug/STATUS.md` (30 KB), `plug/PLAN.md` (40 KB).
  Für den Steckmechanismus zuerst `plug/logbook/README.md`, `current.md`, `lessons.md`.
- Bilder nur ansehen, wenn sie gezeigt oder beurteilt werden müssen (siehe unten); ein Bild kostet viele Tokens. Eine Ansicht reicht
  meist, `vorschau/vergleich_*.png` statt aller Einzelbilder.
- Dateien nicht „zur Sicherheit“ erneut lesen, die man gerade bearbeitet hat; erzeugte Dateien (`stl/`, `vorschau/`) nie per `Read` auf Text prüfen.

## Vorschaubilder im Chat – immer

Der Nutzer will in jedem Chat einen visuellen Eindruck bekommen. Deshalb:

1. Nach **jeder Änderung** an Modellen oder Generator `python3 generate.py`
   ausführen. Das erzeugt die STL/3MF-Dateien und rendert automatisch alle
   Vorschaubilder nach `vorschau/` (und `vorschau.png` für die README).
   Nur Vorschauen neu erzeugen: `python3 preview.py`.
   (Zum Iterieren genügt `--fast`, siehe oben; der volle Lauf kommt vor dem Commit der echten Ausgaben.)
2. Die passenden PNGs **im Chat mit `SendUserFile` (display: "render") zeigen**,
   nicht nur Pfade nennen. Vorher selbst mit `Read` ansehen und prüfen, ob die
   Darstellung plausibel ist.
   - Überblick: `vorschau.png` (Gesamtmodell 1:1500, Laserscan-Variante, farbig)
   - Welches Bild wozu (README-Bilder, Quellenvergleich, Einzelgebäude, Farben, Filament-Profile): Katalog in `vorschau/CLAUDE.md`
   - Bei Änderungen nach Möglichkeit Vorher/Nachher zeigen (alte Version vor der
     Änderung rendern, z. B. nach `$SCRATCHPAD` mit `--out`).
3. Auch bei reinen Fragen zu einem Modell das zugehörige Vorschaubild zeigen.
4. Beliebige Dateien/Ansichten rendern:
   `python3 preview.py datei.stl [--azim -90 --elev 40] [--out ordner]`
   (`--azim -90` = Blick von Süden, `0` = von Osten/Augustusplatz).

Die gerenderten Bilder in `vorschau/` werden mit committet.

## README

`README.md` darf von Hand bearbeitet werden, nur die Blöcke zwischen `<!-- AUTO:name -->` und `<!-- /AUTO:name -->` überschreibt
`readme.py` (Ablauf und Quellen der Bilder: Docstring dort; Titel und Kurzbeschreibung der Gebäude: `BUILDINGS` in `generate.py`,
neue Gebäude erscheinen automatisch in der Galerie). `generate.py`/`preview.py` rufen es nach dem Rendern auf. Nach Änderungen die README mit
Chromium/Playwright (hell und dunkel) rendern und ansehen.

## HTML-Seiten präsentieren

Plan-, Test- und Ansichtsseiten (HTML) immer mit dem **Artifact-Tool** veröffentlichen (privat), damit sie sich in der Claude-Code-App öffnen; `SendUserFile` allein reicht nicht. Bei einer Änderung dieselbe Datei erneut veröffentlichen (gleiche URL). Link in der Antwort nennen und in `plug/STATUS.md` (Tabelle der Artifacts) eintragen. Vorher den Skill `artifact-design` laden.

## Git-Konventionen (aus dem bisherigen Verlauf)

- **Branches:** `claude/<name>-<zufall>` (Cloud-Sessions vergeben den Namen); nie direkt auf `main`. PR nur auf ausdrückliche Bitte.
  Frühere PRs wurden vom Nutzer selbst zusammengeführt (Merge-Commit „Merge pull request #N from …“, kein Squash); main bei Konflikten in den Zweig mergen,
  nicht rebasen.
- **Commit-Nachrichten:** deutsch, eine lange Zeile, kein Präfix („feat:“ o. Ä.), sagt *was* gebaut/geändert wurde und nennt die Dateien oder das Paket,
  Aufzählungen mit Kommas, am Ende ggf. „…; Logbuch, STATUS und CLAUDE.md nachgezogen“. Beispiele: „Weiße Plattenfassaden bleiben hell: Plattenfarben von
  Hörsaal-, Seminar- und Institutsgebäude behalten den Wert der Handmessung“; „Testbogen zum Testfall Kassette (plug/testcase/build_feedback.py)“.
  Danach die Attribution-Zeilen aus dem Systemhinweis.
- **Ein Commit pro abgeschlossenem Schritt**, Dokumentation (Logbuch, STATUS, CLAUDE.md, README) im selben Commit oder direkt dahinter nachziehen.
  Erzeugte Dateien (`stl/`, `vorschau/`, HTML-Seiten) gehören mit in den Commit.
- **PR-Beschreibung** (deutsch): `## Worum es geht` (bzw. `## Was`) · `## Inhalt`/`## Änderungen` (Dateien, Befehle in Backticks) · `## Ergebnis`
  (falls Zahlen) · `## Prüfung` (welche Läufe, `dicht=True`, welche Bilder angesehen, was *nicht* geprüft wurde) · `## Hinweise`/`## Offene Punkte`/`## Grenzen`.
  Bei Messungen eine Tabelle Vorher/Nachher.
- Namen neuer Dateien: Python-Module und Ordner englisch bzw. sprechend (`build_*`, `check`), Seitentexte, Kommentare, Docstrings und Chat deutsch.

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
- Steckmechanismus: `python3 -m plug.check` (`dicht=True` und „keine Kollisionen“), siehe `plug/CLAUDE.md`.
- Ist `CLAUDE.md` oder eine Unterordner-`CLAUDE.md` durch die Änderung veraltet (neue Befehle, Dateien, Maße)? Mit nachziehen.
