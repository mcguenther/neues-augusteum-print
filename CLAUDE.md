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

## Steckmechanismus (LED-Gebäude), Paket `plug/`

Gebäude mit WS2812B-LED werden in eine Grundplatte gesteckt (Plan B mit dem Dupont-Set). Alles dazu liegt im Paket `plug/`.
Einstieg: `plug/STATUS.md` (Stand, Chronologie, Konstanten mit Herkunft, Passprobe-Runden, Offenes, Repo-Ablage) und
`plug/PLAN.md` (Plan B Dupont, Institutsgebäude mit Kassette, JST-Variante als Archiv).

Aufrufe (aus dem Repo-Wurzelverzeichnis, die Ausgabe muss `dicht=True` und „keine Kollisionen“ zeigen):

| Befehl | Erzeugt |
|---|---|
| `python3 -m plug.dupont` (ca. 20 s) | Platte mit Docks A/B/C, Deckel, Würfel, Kassette, Schieber, Proben nach `stl/steckmodul_dupont/`, Bilder nach `vorschau/steckmodul_dupont/`, `plug/views/dupont/data.json` |
| `python3 -m plug.institute` (ca. 45 s) | Institutsgebäude mit Fuß, Kassette, Schieber, Platte, Deckel; kleine Teile nach `stl/steckmodul_institut/`, große Dateien (`gebaeude.stl`, `data.json`, `view.html`) nach `plug/build/institute/` (gitignored) |
| `python3 -m plug.sample` (ca. 15 s) | Probestück 22 × 36 mm mit Kassette, Schieber, Mini-Platte, Deckel, dazu die Passprobe `0_passprobe.stl`, `README.txt` und `probedruck_kassette.zip` nach `stl/steckmodul_probe/`, Bilder nach `vorschau/steckmodul_probe/` |
| `python3 -m plug.views.build_views [dupont\|institute\|all]` | 3D-Seiten `plug/views/dupont/view.html` bzw. `plug/build/institute/view.html` aus Vorlage und `data.json` |
| `python3 -m plug.fit_test.build_page` | Anleitungsseite der Passprobe `plug/fit_test/page.html` |
| `python3 -m plug.build_all [--skip-institute]` | alles nacheinander |
| `python3 -m plug.check [--skip-institute]` | führt die Generatoren aus und bricht ab, wenn eine STL nicht dicht ist oder eine Kollision gemeldet wird |

Aufbau: `plug/parts.py` ist die einzige Quelle für Kaufteil-Maße und Passungen (Quelle B belegt, M gemessen, A abgeleitet,
S geschätzt, E Entscheidung); `plug/geom.py` enthält die Geometriewerkzeuge; `plug/dupont.py` wird von den anderen Modulen
als `sd` importiert (dort nichts umbenennen); `plug/fit_test/generator.py` ist die Passprobe-Geometrie. Die JST-Variante
liegt archiviert unter `plug/archive/jst/` (nicht gepflegt).

Festgelegte Maße der Winkelleiste (nicht ändern ohne neue Messung): Körper **2,0 mm** hoch (`HDR_BODY`) und dick (`HDR_T`),
nicht 2,54; er sitzt neben den senkrechten Pins, siehe `plug/fit_test/angled_pin.html`. Nach jeder Konstantenänderung
`python3 -m plug.build_all` laufen lassen, Seiten (Artifacts) neu veröffentlichen und `plug/STATUS.md` nachziehen.

Namenskonvention: neue Dateien und Ordner bekommen englische Namen, soweit sinnvoll (README statt LIESMICH, `build_*`,
`view`, `check`); Seitentexte, Kommentare und Chat bleiben deutsch. Die Ausgabeordner `stl/steckmodul_*` und
`vorschau/steckmodul_*` und die STL-Dateinamen sind noch deutsch (Umbenennen ist ein offener Schritt, siehe STATUS).

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
