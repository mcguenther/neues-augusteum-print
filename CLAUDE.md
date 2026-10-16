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

## Laufzeit / Schnelllauf

Ein voller `python3 generate.py` brauchte früher ~24 min, fast alles davon im
Software-Renderer (`preview.render`) und nicht in den Laserdaten. Heute: ~5 min auf
4 Kernen (alle Optimierungen ergeben dasselbe Ergebnis; Details und Messung:
`werkzeuge/performance/`).

- **Zum Testen/Iterieren: `python3 generate.py --fast`** – gleiche Daten, aber Laser-Raster
  0,6 statt 0,3 m, Vorschau ohne Kantenglättung, nur Maßstab 1:1500, keine
  README-/Fassaden-/Vergleichsbilder (~1,5 min). Schreibt nach `stl-fast/` und
  `vorschau-fast/` (nicht eingecheckt, fasst `stl/` und `vorschau/` nicht an). Mit
  `--quelle laserscan` / `--scale 1000` weiter eingrenzbar. Für Bilder im Chat reicht das.
- Vor dem Commit der echten Ausgaben (`stl/`, `vorschau/`, README) den vollen Lauf ohne `--fast`.
- `--jobs N` begrenzt die Prozesse (Standard: alle Kerne, `--jobs 1` seriell); am Ende
  druckt `generate.py` die Laufzeit je Phase.

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
   - Farben: `vorschau/farben.png`, Gegenüberstellung Foto | alt | neu `vorschau/farbvergleich/index.html`
     (und die Bilder darin)
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
Farben: je Gebäude `data/fassaden/<slug>.json` (handgesetzte Zonen + Rückfallfarben als `hex`;
die alten Messfelder stehen als `proben_alt`). Die Fassadenfarben von Paulinum, Neuem Augusteum,
Institutsgebäude und City-Hochhaus (Seminargebäude: nur einzelne Zonen) kommen aus der **Fotoprojektion**: `python3 farbmessung.py messen`
(liest `data/messfotos.json`, schreibt `data/messung.json`). Neue Fotos aufnehmen und ausrichten:
`registrierung.py suche [--seeds=3] <id>` (Pose per Himmelslinie plus Kantenabgleich), Überlagerung ansehen
(`registrierung.py pruefen <id>`, vollständig ansehen, nicht nur im Kontaktbogen), bei Passung `"geprueft": true` im
Katalog setzen, sonst `"verworfen": "<Grund>"`. Eine gemessene Farbe lässt sich in `data/fassaden/<slug>.json` mit
`"beibehalten": "<Grund>"` auf dem Wert der Handmessung festhalten (so bleiben die weißen Platten von Hörsaal-, Seminar- und
Institutsgebäude hell, das Mittel über Platten und Fenster wurde zu grau); Flächen darüber gelten nur ab ΔE 25 (`HALTEN_MIN_DE`). Fotos aus einer Recherche (Flickr/Commons über Openverse) übernimmt
`werkzeuge/farbmessung/katalog_recherche.py <katalog.json> <nr> …`. Panoramax lieferte nur beschattete Fassaden. Wikimedia drosselt geteilte IPs (die Commons-API
liefert 429; Seiten und `thumb.wikimedia.org` mit ≤ Originalbreite gehen). `farben.py` setzt
`data/farben.json` zusammen (macht `generate.py` automatisch bei Änderungen).
Profile für wenige Filamente: `farben.PROFILE` (3 und 4 Filamente: Beige, Blaugrau, Graphit,
Rotbraun) mit den Regeln `PROFIL_FENSTER` (Glas/Fenster immer Blaugrau) und `PROFIL_DACH_BLAU`
(nur Paulinum, Neues Augusteum, Uniriese dürfen blaugraue Dächer haben, sonst Beige);
`generate.py` schreibt `komplett_*_objekte_<N>filamente.3mf` (ohne `--filamente` nur Laserscan mit Extras,
mit `--filamente N` für alle gewählten Quellen/Varianten). Nach Änderungen am Profil das Vergleichsbild zeigen.
Zonen prüfen: `python3 fassaden.py <slug>` → `vorschau/fassaden/<slug>_zonen.png`
(Fassadenansichten mit Höhen-/entlang-Raster) und `<slug>_fotos.jpg` (Fotos der Messung).
Alt/neu aus der Foto-Kamera: `werkzeuge/farbmessung/vergleich_bilder.py <alte farben.json>`, dann
`werkzeuge/farbmessung/bericht.py <alte farben.json>` (HTML nach `vorschau/farbvergleich/`, Runde 1).
Runde 2 (vorher/nachher mit interaktivem 3D-Modell, three.js über CDN): `vergleich_bilder.py <alte farben.json> <ordner>
--fotos id,id,…`, dann `bericht_runde2.py <alte farben.json>` (liest daneben `messung.json` und `vorschau_laserscan/` des
alten Stands; Texte in `bericht_runde2_texte.json`; HTML nach `vorschau/farbvergleich_runde2/`).
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
| `python3 -m plug.roadmap.build` | Fahrplan der Testdrucke (Abhängigkeiten, Zeitplan, Karten) `plug/roadmap/page.html` |
| `python3 -m plug.feedback.build` | Testbogen zu den Serien (Schritte, Zeichnungen mit Regler, Formulare, Ergebnistext) `plug/feedback/page.html` |
| `python3 -m plug.series` (ca. 6 min) | Passungsserien mit Spielgravur für Nachtdrucke: `stl/steckmodul_night1/` (STL, README.txt, ZIP), Bilder nach `vorschau/steckmodul_night1/` |
| `python3 -m plug.decision.build` | Entscheidungsdokument nach Nacht 1 (Vorher/Nachher-Zeichnungen, Umgesetztes) `plug/decision/page.html` |
| `python3 -m plug.feedback.build_night2` | Testbogen zu Nacht 2 (K, C v2, N, E, D, FM; Zeichnungen mit Regler, Formulare, Ergebnistext) `plug/feedback/page_night2.html` |
| `python3 -m plug.testcase.build_plan` | Planungsseite für den kompletten Testfall (Kassette v4, Mini-Gebäude, Mini-Grundplatte; Schnitt mit Regler, Draufsicht, Maßkette, Entscheidungen) `plug/testcase/plan.html`; Sollwerte in `plug/testcase/params.py`, Kassette v4 mit `python3 -m plug.testcase.kassette` |
| `python3 -m plug.testcase.build_feedback` | Testbogen zum Testfall (Kassette bestücken, Einpressen, Mulde, Winkelleiste, Stecken, Durchgang, Abziehen; Zeichnungen mit Regler, Formulare, Ergebnistext) `plug/testcase/feedback.html` |
| `python3 -m plug.testcase.build` (ca. 2 min) | STL, README und ZIP des Testfalls (2 Kassetten v4, Mini-Gebäude A/B, Mini-Grundplatte, Mini-Deckel) nach `stl/steckmodul_testcase/`, Bilder nach `vorschau/steckmodul_testcase/` |
| `python3 -m plug.series2` (ca. 2 min) | zweiter Nachtdruck (K, C v2, N Schieber, E Einpressen, D v7, FM): `stl/steckmodul_night2/` (STL, README.txt, ZIP), Bilder nach `vorschau/steckmodul_night2/` |
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

## Testdruck-Modus und Logbuch (Steckmechanismus)

Einstieg: `plug/logbook/README.md`. Ablauf jeder Runde: **Plan als HTML mit Grafiken** (Entscheidungskarten, Maßkette, Risiken) → der Nutzer nickt ab →
**STL, README, ZIP** mit Prüfbericht (dicht, keine Kollisionen, Überhänge) → der Nutzer druckt → **Testbogen als HTML-Formular** → der Nutzer fügt den
Ergebnistext im Chat ein → **Auswertung**: erst Erkenntnisse zusammenfassen und bewerten, Unklarheiten benennen, dann ins Logbuch eintragen und committen.

- Vor jedem Plan `plug/logbook/lessons.md` und `current.md` lesen; vor jeder STL die Vorab-Checkliste in `lessons.md` durchgehen.
- Ohne abgenickten Plan keine STL. Maßkette im Plan mit Worst-Case rechnen. Formularfelder nur fühlbar oder ja/nein, Variante (A/B) immer abfragen.
- Nach jeder Auswertung: `rounds/rN_*/summary.md` und `result.txt` (wörtlich), `current.md`, `lessons.md`, `next.md` und `plug/STATUS.md` nachziehen; den getesteten Satz einfrieren.
- `plug/parts.py` erst ändern, wenn ein Wert bewährt ist; neue Werte stehen bis dahin in `plug/<paket>/params.py`.

## Prüfen vor dem Commit

- Ausgabe von `generate.py`: alle STL-Zeilen müssen `dicht=True` zeigen.
- Vorschaubilder ansehen (siehe oben).
