# Hinweise für `plug/` (Steckmechanismus für LED-Gebäude)

Wird automatisch geladen, sobald Dateien unter `plug/` gelesen werden. Allgemeines (Chat auf Deutsch, Vorschaubilder,
Commit-Stil) steht in der `CLAUDE.md` im Repo-Wurzelverzeichnis.

**Token sparen:** Nicht ungefragt lesen: `plug/**/page*.html`, `plan*.html`, `feedback*.html`, `view.html`, `data.json`
(alles erzeugt, 80 KB bis 430 KB; die Quellen sind `build*.py` und `*.template.html`), `plug/archive/` (JST, nicht gepflegt),
`plug/PLAN.md` (40 KB) und `plug/STATUS.md` (30 KB) nur abschnittsweise (`grep -n '^## '`, dann `Read` mit `offset`/`limit`).
Einstieg ist das Logbuch (`logbook/README.md`, dann `current.md` und `lessons.md`, je 6 bis 8 KB).

**Schnell prüfen:** Statt `python3 -m plug.build_all` nur den Generator laufen lassen, den die Änderung betrifft; `plug.dupont`
(ca. 20 s), `plug.sample` (ca. 15 s) und `plug.institute` (ca. 45 s) sind voneinander unabhängig und lassen sich als getrennte
Hintergrundprozesse gleichzeitig starten (`run_in_background`; alle drei zusammen ca. 50 s statt ca. 85 s nacheinander, gemessen auf 4 Kernen). Ohne Institutsgebäude: `--skip-institute`. Die Seiten-Generatoren
(`build_*`) brauchen Sekunden und lesen nur `params.py`/`data.json`. Der Agent `plug-pruefer` (`.claude/agents/`) macht das
und meldet nur Fehler.

**Nebenwirkung:** Die Generatoren überschreiben eingecheckte Dateien (`stl/steckmodul_*`, `vorschau/steckmodul_*`, `plug/views/dupont/data.json`). Nach einem Probelauf `git status --short` ansehen und
Zufallsabweichungen, die nicht zur Änderung gehören (z. B. `stl/steckmodul_probe/README.txt`, die ZIP), mit `git checkout -- <pfad>` zurücknehmen.

## Steckmechanismus, Paket `plug/`

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
| `python3 -m plug.testcase.build_plan2` | Planungsseite Steckprobe 2 (Faden-Lasche mit V-Kanal und Trichter an der Unterseite, Kassette 14,60, Schacht 17,40, Entscheidungskarten) `plug/testcase/plan2.html`; Vorschläge in `PROP` der Datei, nach dem Abnicken nach `params.py` |
| `python3 -m plug.testcase.build_plan3` | Planungsseite Kassetten-Varianten V1 (Streifen quer auf einer Wand) und V2 (Streifen hochkant): Passstudie in den Grundrissen, Schnitte, Maßkette, Entscheidungskarten `plug/testcase/plan3.html`; Konzeptgeometrie `python3 -m plug.testcase.variants` (Bild, keine STL), Passstudie `python3 -m plug.testcase.fit_study` (ca. 2 min, Ergebnis `variants_fit.json`) |
| `python3 -m plug.hollow.build_plan` | Plan und Stand „Gebäude als Hohlkörper“ (3D-Ansicht mit Schnitt, aufgeschnittene Bilder und Schnitte aller sechs Gebäude, Ablauf im Generator, Spannweiten der Decken, Beschlüsse) `plug/hollow/plan.html`, ca. 30 s, Ansichten aus `plug/hollow/views.py` (Bilder nach `vorschau/hohl/`); Zahlen aus `plug/hollow/study.json`, neu mit `python3 -m plug.hollow.study` (ca. 20 s, Messung in `plug/hollow/shell.py`); das Verfahren selbst steht in `hohl.py` (Wurzel) und läuft in `generate.py` |
| `python3 -m plug.campus` (ca. 20 s) | Steckplatte des Campus bei 1:1300 (Platte 115,6 × 220,8 × 14,6 mm mit **flacher Unterseite** wie das Test-Dock: Mulde 14,2 mit Einführfase 0,5, Muldenboden 0,4 als unterste Schicht, 24 Pin-Löcher mit Fase, Fase 1,5 an der Oberkante, Schrift erhaben, keine Hohlräume, kein Support; Kassettenwahl je Gebäude aus `params.CASSETTE`, Hof-Aussparung) nach `stl/steckmodul_campus/`, Bilder nach `vorschau/steckmodul_campus/`; Festlegung in `plug/logbook/scale.md` (alle Werte dort sind Planwerte und noch ungetestet, Liste im Abschnitt „Ungetestete Planwerte“), Prüfseite `python3 -m plug.scale1176.build` (`plug/scale1176/page.html`); Platzierungs-App `python3 -m plug.scale1176.app_data` und `python3 -m plug.scale1176.build_app` (`plug/scale1176/placer.html`, Lagen ziehen und als JSON für `placements_1300.json` kopieren; danach `python3 -m plug.campus`) |
| `python3 -m plug.buildings [slug …] [--bruecke 2]` (ca. 1 bis 2 min je Gebäude) | steckbare Gebäude zur Steckplatte bei 1:1300 (Laserscan): Hohlkörper (`hohl.py`) mit Fuß 14,2 mm über den vollen Grundriss, Boden 1,2, Schachtrohr und Aufnahme je Kassette (v4, V1RS, V2R aus `params.CASSETTE`; Einpressspiel, Einführfase, Anschlag mit 45°-Unterseite, Freiraum für LED, Streifen und Blatt), 45°-Dach über allen Schnitten; Prüfung dicht, Kollision mit der Kassette, Platz, Brücken und Kragstücke je 0,2-mm-Lage; STL und JSON nach `stl/steckmodul_campus/gebaeude/`, Schnittbilder nach `vorschau/steckmodul_campus/gebaeude/` |
| `python3 -m plug.views.campus.build_view` (ca. 20 s) | interaktive 3D-Seite der Steckplatte, neu gegen gedruckt (r7), feste Ansichten je Änderung `plug/views/campus/view.html` (aus `view.template.html`; Artifact) |
| `python3 -m plug.testcase.build_feedback` | Testbogen zum Testfall (Kassette bestücken, Einpressen, Mulde, Winkelleiste, Stecken, Durchgang, Abziehen; Zeichnungen mit Regler, Formulare, Ergebnistext) `plug/testcase/feedback.html` |
| `python3 -m plug.testcase.build` (ca. 2 min) | STL, README und ZIP des Testfalls (2 Kassetten v4, Mini-Gebäude A/B, Mini-Grundplatte, Mini-Deckel) nach `stl/steckmodul_testcase/`, Bilder nach `vorschau/steckmodul_testcase/` |
| `python3 -m plug.series2` (ca. 2 min) | zweiter Nachtdruck (K, C v2, N Schieber, E Einpressen, D v7, FM): `stl/steckmodul_night2/` (STL, README.txt, ZIP), Bilder nach `vorschau/steckmodul_night2/` |
| `python3 -m plug.power.build_concept` (ca. 30 s) | Konzeptseite Grundplatte mit Powerbank (Maßstäbe 1:1000 und 1:1300, Oberplatte + hohler Unterkasten, Dock mit Kabelnische, Faden-V, Fasen-Check, Passmaße, Testdrucke) `plug/power/concept.html`; Werte in `plug/power/params.py` (liest die Steckprobe-Werte aus `plug/testcase/`), Plan Kapitel 6 |
| `python3 -m plug.testcase.build2` (ca. 2 min) | Steckprobe 2 (Zwei-Lagen-Aufbau: 1 Kassette v5, keine Reserve, Mini-Gebäude, Mini-Oberplatte mit Dock/Nische und 4 Faden-V 53°/40°, Mini-Unterkasten hohl), Prüfbericht, README, ZIP nach `stl/steckmodul_testcase2/`, Bilder nach `vorschau/steckmodul_testcase2/` |
| `python3 -m plug.testcase.build_feedback2` | Testbogen Steckprobe 2 mit Aufbau-Zeichnungen (Regler), 13 Schritten, Formularen und Ergebnistext `plug/testcase/feedback2.html` |
| `python3 -m plug.power.build_plan_fach` (ca. 20 s) | Plan der Fachprobe Powerbank (Draufsicht, Schnitt, Maßkette, Entscheidungskarten) `plug/power/plan_fach.html`; Geometrie in `plug/power/fachprobe.py` |
| `python3 -m plug.power.build_fach` (ca. 1 min) | Fachprobe Powerbank, Variante B (Fach, Deckplatte; ohne Taste, Stößel, Schablone), Prüfbericht, README, ZIP nach `stl/steckmodul_fachprobe/`, Bilder nach `vorschau/steckmodul_fachprobe/` |
| `python3 -m plug.power.build_feedback_fach` | Testbogen Fachprobe (Powerbank einlegen, Deckplatte, Fenster, Stecker und Kabel) `plug/power/feedback_fach.html` |
| `python3 -m plug.power.build_layout [--collect]` (`--collect` ca. 2 min, sonst Sekunden) | Lösungsfindung 1:1300: interaktive Platte, Powerbank-Fach ziehen und drehen, freie Docks, Karte, Ohr, zweite Etage `plug/power/layout.html` (Daten `layout_data.json`, Vorlage `layout.template.html`) |
| `python3 -m plug.power.build_plan_dock` (ca. 5 s) | Plan Test-Dock mit durchgehendem Steckerraum (Schnitt, Unterseite, Maßkette, Entscheidungskarten) `plug/power/plan_dock.html`; Werte in `PROP` der Datei, STL erst nach dem Abnicken |
| `python3 -m plug.power.build_dock` (ca. 2 min) | Test-Dock flache Unterseite (Mini-Oberplatte ohne Tasche, Stufe und Support, zwei Sätze Füße 3,5 und 2,5), Prüfbericht, README, ZIP nach `stl/steckmodul_testdock/`, Bilder nach `vorschau/steckmodul_testdock/` |
| `python3 -m plug.power.build_feedback_dock` | Testbogen Test-Dock (Leiste ankleben, Stecken, Halt des Klebers, Luft, Zapfen) `plug/power/feedback_dock.html` |
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


## HTML-Seiten präsentieren

Plan-, Test- und Ansichtsseiten immer als privates Artifact veröffentlichen, Link in `plug/STATUS.md` (Tabelle der Artifacts) eintragen; Regel und Skill `artifact-design`: Wurzel-`CLAUDE.md`.
