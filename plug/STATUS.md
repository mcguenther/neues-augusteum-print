# Steckmechanismus für LED-Gebäude: Stand und Fahrplan (`plug/STATUS.md`)

Diese Datei fasst den Zweig `claude/led-stecker-mechanismus-319vgb` zusammen, damit in neuen Sessions
weitergearbeitet werden kann. Sie ist von Hand geschrieben (kein Generator überschreibt sie). Quellen:
Git-Verlauf, die Generatoren und Pläne im Paket `plug/`, `stl/steckmodul_probe/README.txt`
und die Rückmeldungen des Nutzers aus dem Chat. Was sich daraus nicht belegen lässt, steht als „unbelegt“.

Stand: nach dem Umbau auf die Entscheidungen der Passprobe-Runde 4 (Körperhöhe 2,0, Loch 1,4, Spiel Leiste 0,1,
`STEP_CLR` 0,1, Stufe für das Lötende). Generatoren, Plan-Zahlen, `LIESMICH.txt` und Seiten sind auf diesen Stand
gebracht. Die Abweichungen aus der ersten Fassung (Abschnitt 3.3) sind geschlossen. Das Probestück ist gedruckt (Ergebnis: Abschnitt 4); Passprobe v6 ist nicht gedruckt. Die Dateien liegen seit der
Umstrukturierung im Paket `plug/` (Abschnitt 5).

## Festgelegte Maße (merken)

- **Körper der Winkelleiste: 2,0 mm** in beiden Richtungen, `HDR_T` (Dicke in Pin-Richtung) und `HDR_BODY` (Höhe quer zur
  Pin-Reihe). Das gilt für die Passprobe und für alle anderen Teile (Platte Dock A, Probestück, Institutsgebäude, Dock B/C).
  Der Datenblattwert 2,54 mm ist falsch für das Kit des Nutzers; `HDR_UP` und die Stufe des Lötendenschlitzes folgen daraus.
- Körperlänge 10,66 mm (abgebrochen), Pin-Vierkant 0,64, senkrechter Pin 7 mm, 1 mm gerader Pin bis zum Knick, 3 mm Lötende.
- Spiel Leistenkörper 0,1 mm je Seite, Spiel Buchse 0,22 mm, Pinlöcher 1,4 mm mit 0,3-mm-Senkung, Muldenboden 0,8 mm,
  Fase 0,5 mm an den Taschenrändern, `STEP_CLR` 0,1 mm.
- Passprobe v6 prüft nur noch, auf welcher Höhe die Stufe liegen muss (Körperhöhe 2,0 / 1,8 / 1,6).

## 1. Ziel

Die Gebäude des Campusmodells sollen mit je einer WS2812B-LED von innen beleuchtet werden. Jedes Gebäude hat
einen Fuß, der in eine tiefe Mulde der Grundplatte taucht; die Stifte der Platte (abgewinkelte Stiftleiste) und
die Buchse im Fuß (Dupont-Gehäuse 1×4 mit gecrimpten Adern) stellen beim Einstecken den Kontakt her, am
Gebäude steht kein Stecker heraus. Gebaut wird mit den Teilen des vorhandenen 2,54-mm-Dupont-Sets (Plan B),
die Maße der Kaufteile und die Passungen werden mit gedruckten Proben am echten Material nachgemessen.
Ziel des Zweigs ist ein druckbarer, mit dem Probestück geprüfter Mechanismus, den der Nutzer in den
Hauptzweig mergen will.

## 2. Chronologie und Entscheidungen

Reihenfolge nach `git log` (älteste zuerst). Hashes sind die Anfangsstellen der Commits. Die Dateinamen in dieser
Tabelle sind die damaligen; seit der Umstrukturierung (Abschnitt 6) liegt alles unter `plug/` (`steckmodul_dupont.py` ist
`plug/dupont.py`, `steckmodul_institut.py` ist `plug/institute.py`, `steckmodul_probe.py` ist `plug/sample.py`, der JST-Teil
von `steckmodul.py` ist `plug/archive/jst/jst.py`, `stecker/` ist `plug/`).

| Schritt | Commit | Was gebaut wurde | Warum / Entscheidung |
|---|---|---|---|
| a | `a8943b0` | Erster Plan mit JST-XH-Stecker: `steckmodul.py`, `stecker/PLAN.md`, `stecker/ansicht.html` (3D-Ansicht mit Animation), Dock-Platte, Steckmodule A/B/C, Würfel, Passprobe | Ausgangsidee mit Kaufteil-Stecker. Danach durch Plan B abgelöst, weil das Dupont-Set schon vorhanden ist (Begründung aus dem Chat, im Plan nicht gesondert belegt). |
| b | `6a16780` | Variante „Gebäude mit Fuß“ (tiefe Mulde statt Schacht), `dock_platte_fuss_ABC.stl`, `wuerfel_fuss.stl` | Kein herausstehender Teil am Gebäude; der Fuß wird durch die Mulde geführt. Seitdem haben alle Gebäude einen Fuß. |
| c | `8eb7bc5`, `60a829b` | Plan B mit Dupont-Teilen: `steckmodul_dupont.py`, `stecker/dupont/PLAN.md`, Ansicht mit Druckablauf. Buchse im Fuß, abgewinkelte Stiftleiste in der Platte (Dock A); Dock B (gerade Leiste) und Dock C (Male-Crimp im Gehäuse) als Alternativen. Platte mit Deckel und Stempeln gegen Steckdruck, Federzunge in der Mulde, Fase am Fuß | Hauptvariante „Pause“: Druck hält an, Buchse samt Adern und LED wird eingelegt, ein Riegel überdruckt sie. Rückfallebene „Kassette“: Buchse, Adern und LED-Streifen in einer gedruckten Kassette, von unten in den Fuß geschoben und von einem Schwalbenschwanz-Schieber (zugleich Trichterplatte) gehalten. |
| d | `99541b8` | Echtes Gebäude: Institutsgebäude (Laserscan, 1:1000) mit Kassette: `steckmodul_institut.py`, `stecker/institut/` | Zeigt, dass die Kassette an einem echten Gebäude funktioniert (großzügige LED-Ablage, Schieber quer durch die lange Wand). |
| e | `db01aae` | Probestück (22 × 36 mm Ausschnitt des Hauptbalkens) mit Kassette, Schieber, Mini-Platte, Deckel: `steckmodul_probe.py`, `stl/steckmodul_probe/` | Billiger Drucktest für Schieber, Kassette, Stecken und Licht durch die 0,4-mm-Wand. |
| f | `5f8f992` bis `a58143d` | Passproben `passprobe()` in `steckmodul_probe.py` mit Anleitungsseite `stecker/probe/`; mehrere Runden (Abschnitt 3) | Die Maße der echten Kaufteile (Buchse, Winkelleiste, Pins) sind teils geschätzt; die Probe gleicht sie am Druck ab. |

Wichtige Konstruktionsentscheidungen aus dem Chat und den Commits:

- Winkelleiste falsch modelliert (Commit `5d123b3`): Nach einem Foto und den Maßen des Nutzers sitzt der
  Körper der Winkelleiste neben den senkrechten Pins; der waagerechte Pin geht durch den Körper. Die frühere
  Modellierung (senkrechter Pin durch den Körper, Knick darunter) war falsch. Folge: Umbau von Dock A
  (`dock_a_cuts`, `header_part` A, Lötendenschlitz, Schacht, Deckelstempel), Muldenboden wieder 0,8 mm,
  Fußhöhe von 10,6 auf 9,6 mm, `HDR_UP` abgeleitet (5,41 mm, mit Körperhöhe 2,0 danach 5,68 mm).
- Löcher nie auf die erste Schicht (Passprobe Runde 1): Elefantenfuß verschließt sie. Die Passprobe wurde
  danach so gedreht, dass die Schrift (mit Senkung an den Löchern) auf dem Bett liegt und die Taschen nach oben
  offen sind.
- Körperhöhe der Winkelleiste 2,0 statt 2,54 mm (letzte Rückmeldung des Nutzers, Abschnitt 3).
- Die Anleitungen und Ansichten sind Seiten (HTML), die aus `daten.json` oder aus den Generator-Konstanten
  gebaut werden; Zahlen in Plan und Seite sollen aus `dims()`, `forces()` und `building_table()` stammen.

Zum Namensschema: Im Code und in den Commit-Texten heißen die Passprobe-Versionen v4 und v5; in den
Chat-Runden unten ist es Runde 2 (= „v4“) und Runde 3 (= „v5“). Die Spalte „Chat-Runde“ zeigt die Zuordnung.
Commit-Nachrichten und Code-Kommentare sind dabei nicht ganz konsistent (z. B. nennt Commit `013b5af` „Passprobe v5“
für einen Stand vor der heutigen Runde 3); die Tabelle unten folgt dem Chat.

## 3. Passprobe-Ergebnisse und Herkunft der Konstanten

Gedruckt wird mit 0,4-mm-Düse, 0,2 mm Schichthöhe, PLA.

### 3.1 Runden

| Chat-Runde | Teil | Aufbau | Ergebnis | Folgerung |
|---|---|---|---|---|
| 1 | Block 66 × 44 × 9 mm, 22 cm³ | Taschen mit 0,0 / 0,1 / 0,2 mm Spiel, Pinlöcher 0,9 bis 1,3 mm auf der Druckbettseite | Alles zu eng, Löcher unten am Bett zugequollen (Elefantenfuß) | Löcher nicht auf die erste Schicht, Spiel größer, kompakter drucken (5,3 cm³) |
| 2 (Code: v4) | 5,3 cm³ | Spiel 0,25 / 0,275 / 0,30 / 0,33, Fase 0,5 mm an den Taschenrändern, Pinlöcher 1,2 bis 1,8 mm | Buchse mit 0,25 mm sitzt sehr gut (darf minimal kleiner); Pins gehen ab 1,2 mm ohne Kraft durch, ein einzelnes tiefes Loch erst ab 1,4 mm. Leistenkörper durch ungenaues Abbrechen etwa 0,5 mm länger | `SNUG` 0,10 auf 0,22, `HOLE` 1,1 auf 1,25, `HDR_W` 10,16 auf 10,66 |
| Foto und Maße | Winkelleiste | senkrechter Pin 7 mm (±0,5) bis Außenkante der Biegung, 1 mm gerader Pin, Körper etwa 2 mm, 3 mm Pin dahinter, Pin 0,64 | Körper sitzt neben den senkrechten Pins | Dock A umgebaut (Abschnitt 2), `HDR_LEG` 7,0, `RA_BACK` 1,0, `RA_TAIL` 3,0 |
| 3 (Code: v5) | 4 cm³ | 3 Spalten Pinlage (−0,4 / 0 / +0,4) mal 2 Zeilen Spiel (0,2 / 0,3) | Körper passt mit 0,2 mm Spiel, alle vier Pins gehen in allen drei Spalten durch, Lötenden passen frei im Schlitz, aber der Körper wackelt: Tasche in y 2,54 + 0,4 breit bei Körperdicke etwa 2,0, Pins kommen schief heraus | `HDR_T` = 2,0 (Körperdicke in Pin-Richtung), Pinlage bleibt bei Soll |
| 4 (Code v5/v6-Vorstufe, 4,5 cm³) | `0_passprobe.stl` | `HDR_T` 2,0, Spiel 0,15 / 0,10 / 0,05 (Spalten), Löcher 1,5 / 1,3 mm (Zeilen), Beschriftung 3,4 mm fett, 0,6 tief | Rückmeldung des Nutzers: Tiefe der Körpertasche stimmt nicht, Körper fällt zu tief, das Lötende liegt nicht flach auf seiner Stufe. Körperhöhe 2,54 ist falsch, es sind etwa 2,0 | Entscheidung für v6 (nächste Zeile) |
| 5 (v6, gebaut, 1,8 cm³, nicht gedruckt) | `0_passprobe.stl`, 40,5 × 16,1 × 4,0 mm | drei Varianten der Stufenhöhe: Körperhöhe 2,0 (Hauptwert), 1,8 und 1,6 als Test; Loch 1,4 mm; Spiel 0,1 mm | Ergebnis steht aus | Stufe = Pin-Oberseite; Abstand Decke bis Stufe = h/2 − 0,32 (Pin liegt mittig, Vierkant 0,64) |

Das Probestück (Abschnitt 4) ist gedruckt. Ergebnis laut Nutzer: Es wackelt überall etwas, mit 2,0 mm für die Winkelleiste passt es.

### 3.2 Konstanten: Sollwert, Code, Herkunft

Spalte „Code“ zeigt den Wert in `plug/parts.py` (früher oben in `steckmodul_dupont.py`) nach dem Umbau auf Runde 4.
Die Quellenbuchstaben stammen aus dem Generator: B belegt (Zeichnung), M gemessen, A abgeleitet, S geschätzt;
E = Entscheidung aus dem Chat.

| Konstante | Soll | Code | Quelle / Runde | Begründung |
|---|---|---|---|---|
| `PITCH` | 2,54 | 2,54 | B | Raster |
| `HSG_W` | 10,16 | 10,16 | B, Pololu-Zeichnung | Gehäuse 1×4, n · 2,54 (±0,3) |
| `HSG_T` | 2,54 | 2,54 | B | Gehäusedicke |
| `HSG_H` | 14,0 | 14,00 | B | Höhe 14,00 ±0,25 (`HSG_TOL` 0,25 macht die Tasche entsprechend höher) |
| `PIN_SQ` | 0,64 | 0,64 | B | Vierkant der Stifte |
| `HDR_W` | 10,66 | `NPIN * PITCH + 0.5` = 10,66 | M, Runde 2 | Körper wegen Abbruchrest etwa 0,5 mm länger als 4 · 2,54 |
| `HDR_BODY` | 2,0 | 2,0 | E, Runde 4 / v6 | Körperhöhe der Winkelleiste; 2,54 wurde aus dem Datenblatt (Würth WR-PHD 2,54 ±0,15) übernommen, am Kit gemessen etwa 2,0 |
| `HDR_T` | 2,0 | 2,0 | M, Runde 3 | Körperdicke in Pin-Richtung; mit 2,54 wackelte der Körper |
| `HDR_LEG` | 7,0 | 7,0 | M (±0,5) | senkrechter Pin bis Außenkante der Biegung |
| `RA_BACK` | 1,0 | 1,0 | M (±0,5) | gerader Pin zwischen Körper und senkrechtem Pin |
| `RA_TAIL` | 3,0 | 3,0 | M (±0,5) | Lötende hinter dem Körper |
| `HDR_UP` | abgeleitet | `HDR_LEG - PIN_SQ/2 - HDR_BODY/2` = 5,68 | A | Stiftspitze über Körperoberkante, Biegung auf halber Körperhöhe |
| `SNUG` | 0,22 | 0,22 | Runde 2 | Spiel je Seite Buchse in der Tasche: 0,25 passt sehr gut, darf etwas kleiner |
| `SNUG_HDR` | 0,1 | 0,1 | E | Spiel je Seite Leistenkörper in der Tasche; Runde 3 ging mit 0,2, Runde 4 testete 0,15 / 0,10 / 0,05 |
| `RIB` | 0,12 | 0,12 | unbelegt (Herkunft) | Übermaß der Crush-Rippen |
| `HOLE` | 1,4 | 1,4 | E | Stiftloch (Muldenboden, Trichterhals). Runde 2: 1,2 geht ohne Kraft, tiefes Einzelloch erst ab 1,4; deshalb 1,4 |
| `CEIL` | 0,8 | 0,8 | Umbau Winkelleiste | Muldenboden über dem Steckerteil |
| `FUNNEL_T` | 1,0 | 1,0 | Plan | Trichterplatte (bei der Kassette zugleich Schieber) |
| `FUNNEL_D` | 2,4 | 2,4 | Plan | Trichteröffnung unten |
| `STEP_CLR` | 0,1 | 0,1 | E | Luft zwischen Stufe und Pin im echten Dock A (neu mit v6) |
| `CLR` | 0,25 | 0,25 | Plan | Spiel je Seite Fuß in der Mulde (Führungsband) |
| `RELIEF` | 0,30 | 0,30 | Plan | zusätzliches Spiel unter dem Führungsband |
| Fußhöhe `F` | abgeleitet | `layer_up(g1 + GUIDE + CH_F + CH_P)` | A | 9,8 mm nach dem Umbau (vorher 9,6); E 3,88 mm, g1 4,88, Plattendicke 30,6 mm (Dupont) |

### 3.3 Abweichungen zwischen Code und Sollwerten (geschlossen)

In der ersten Fassung dieser Datei standen noch die Werte vor Runde 4 im Code. Umgesetzt: `HDR_BODY` 2,0, `HOLE` 1,4,
`SNUG_HDR` 0,1, neu `STEP_CLR` 0,1 und die Funktion `step_z()` für die Stufe des Lötendenschlitzes. `HDR_UP` ist jetzt
`HDR_LEG - PIN_SQ/2 - HDR_BODY/2` = 5,68 statt mit festem 1,27 gerechnet. Offen bleibt:

1. `HDR_BODY` hat zwei Bedeutungen: Höhe der Winkelleiste (Dock A) und Dicke der geraden Leiste (Dock B). Dock B und C
   rechnen jetzt ebenfalls mit 2,0 und kollidieren nicht; ob die gerade Leiste aus dem Kit tatsächlich 2,0 hat, ist
   unbelegt. Sonst braucht Dock B eine eigene Konstante.
2. Das Rundenschema ist uneinheitlich: Code und Commits sagen v4/v5/v6, der Chat Runde 2/3/4/5; Tabelle in 3.2 ordnet zu.

## 4. Das Probestück

Was: Ausschnitt (22 × 36 mm, 12 mm sichtbare Höhe plus 9,8 mm Fuß) des Hauptbalkens des Institutsgebäudes
im Maßstab 1:1000, mit denselben Maßen für Fuß, Schacht, Nut, Kassette und Schieber wie das Gebäude. Es
prüft Schieber, Kassette, das Stecken in die Platte und das Licht durch die 0,4-mm-Wand. Die Passprobe ist
getrennt davon (sie prüft nur die Winkelleiste) und liegt als `0_passprobe.stl` im selben Ordner.

Erzeugen: `python3 -m plug.sample` (rund 15 s). Es schreibt STL, `README.txt` und
`probedruck_kassette.zip` nach `stl/steckmodul_probe/` und Bilder nach `vorschau/steckmodul_probe/`. Die
Ausgabe nennt `dicht=True` je Teil, die Kollisionsprüfung (muss „keine Kollisionen“ zeigen) sowie
Überhänge und waagerechte Decken je Teil.

| Datei | Inhalt | Volumen | Hinweis |
|---|---|---|---|
| `0_passprobe.stl` | Passprobe Winkelleiste v6 (Abschnitt 3) | 1,8 cm³ | Schriftseite unten, Taschen offen nach oben |
| `1_probestueck.stl` | Gebäude mit Fuß | 6,1 cm³ | Fuß nach unten, Dach oben; nur das Dach ist Brücke (19,6 mm) |
| `2_kassette.stl` | Kassette | 5,8 cm³ | steht aufrecht, Buchsentasche unten offen |
| `3_schieber.stl` | Schieber (Trichterplatte, 1 mm) | 0,6 cm³ | liegt flach, ohne Brim, erste Schicht 20 mm/s |
| `4_platte.stl` | Mini-Platte mit Mulde, Dock A, Federzunge | 16,2 cm³ | |
| `5_deckel.stl` | Deckel mit zwei Stempeln | 3,3 cm³ | Stempel zeigen nach oben |

Alle fünf Teile des Probestücks zusammen 32 cm³ (bei 100 % Füllung etwa 40 g PLA).

Druckreihenfolge laut `README.txt`: zuerst die Passprobe 0, dann 3 und 2 (klein), dann 1, dann 4 und 5.

Slicer-Einstellungen: Düse 0,4 mm, Schichthöhe 0,2 mm, PLA oder PETG, Wände 3 Linien (1,2 mm), Füllung 15 %,
Brückenerkennung an, keine Stützen. Die Lichtfenster sind nur 0,4 mm dick (eine Linie); der Slicer muss
dünne Wände drucken (Arachne in PrusaSlicer 2.6 und neuer, Bambu Studio, Cura, sonst „Dünne Wände erkennen“
bzw. „Lücken zwischen Wänden füllen“). Im Slicer-Vorschaubild prüfen, ob die Fenster vorhanden sind.
Kassette und Schieber vor dem Zusammenstecken entgraten (Elefantenfuß).

Zusätzlich nötig: Dupont-Gehäuse 1×4 mit 4 gecrimpten Adern, ein Stück Winkelstiftleiste mit 4 Pins,
WS2812B-Streifenstück (60/m 10 mm oder 144/m 12 mm), 4 Blechschrauben M3 × 8 oder Heißkleber für den Deckel.

Zu messen: Schieber (gleitet, bündig), Kassette (ohne Spiel, Anschlag), Stecken (Einstecken unter 10 N,
Herausziehen 3 bis 8 N, hebt die Mini-Platte mit?), Kontakt (LED leuchtet, DETECT-Pin liest LOW; Stifte
stecken 3,9 mm in der Buchse, Kontaktpunkt geschätzt), Licht (gleichmäßig auf allen vier Seiten).
Ergebnis des Drucks (Nutzer, im Chat): Das Probestück ist gedruckt und passt mit der Körperhöhe 2,0 mm der Winkelleiste. Überall
wackelt etwas; das wird mit einem Tropfen Heißkleber gelöst und gilt als akzeptiert. Zu den einzelnen Messpunkten (Schieber,
Kassette, Einsteck- und Haltekraft, Kontakt, Licht) liegen keine getrennten Angaben vor; sie wurden nicht als Problem gemeldet.

## 5. Ablage im Repo (nach der Umstrukturierung)

Die Generatoren, Seiten und Dokumente liegen im Paket `plug/` (englische Namen). Ausgaben bleiben in `stl/steckmodul_*` und
`vorschau/steckmodul_*` (Schritt 6 der Vorschlagsliste wurde nicht gemacht).

### 5.1 Übersicht

| Pfad | Art | Inhalt |
|---|---|---|
| `plug/parts.py` | Konstanten | Kaufteil-Maße und Passungen, einzige Quelle; Quelle je Wert B/M/A/S/E |
| `plug/geom.py` | Werkzeuge | `box, cbox, cyl, union, diff, frustum, ext, keyed, prism_x/y, vol_int, xcut, ycut, to_tm, encode` |
| `plug/dupont.py` | Generator | Plan B: Platte mit Docks A/B/C, Deckel, Würfel, Kassette, Schieber, Proben; wird als `sd` importiert |
| `plug/institute.py` | Generator | Institutsgebäude mit Fuß, Kassette, Schieber, Platte, Deckel |
| `plug/sample.py` | Generator | Probestück (22 × 36 mm), `README.txt`, ZIP; ruft die Passprobe auf |
| `plug/fit_test/` | Passprobe | `generator.py` (Geometrie), `build_page.py`, `page.template.html`, `page.html`, `angled_pin.html` (Maße der Winkelleiste) |
| `plug/views/` | 3D-Seiten | `build_views.py`; `dupont/` (`view.template.html`, `data.json`, `view.html`), `institute/view.template.html` |
| `plug/build/institute/` | gitignored, erzeugt | `gebaeude.stl` (4,9 MB), `data.json`, `view.html` (je etwa 5 MB); mit `python3 -m plug.build_all` neu erzeugen |
| `plug/check.py`, `plug/build_all.py` | Hilfsskripte | prüfen bzw. alles neu erzeugen |
| `plug/power/` | Konzept | `build_concept.py`, `concept.template.html`, `concept.html`: Powerbank Intenso XS5000 in der Platte (PLAN Kapitel 6) |
| `plug/PLAN.md`, `plug/STATUS.md` | handgeschrieben | Plan (Dupont, Institut, JST-Archiv) und diese Datei |
| `plug/archive/jst/` | archiviert | JST-Variante: `jst.py`, `PLAN.md`, `view.template.html`, `build_view.py`, `view.html`, `data.json`, `stl/`, `preview/` (nicht gepflegt) |
| `stl/steckmodul_dupont/`, `stl/steckmodul_institut/`, `stl/steckmodul_probe/` | Ausgabe, eingecheckt | STL, `README.txt` und ZIP des Probestücks (`gebaeude.stl` des Instituts nicht) |
| `vorschau/steckmodul_dupont/`, `_institut/`, `_probe/` | Ausgabe, eingecheckt | Vorschaubilder |

Alte Passproben wurden entfernt (`stl/steckmodul_dupont/passprobe.stl`, `passprobe()` in `plug/dupont.py` und im JST-Code); die
aktuelle ist `plug/fit_test/generator.py` mit `0_passprobe.stl` im Ordner des Probestücks. `plug/archive/jst/stl/passprobe.stl`
ist Altlast im Archiv.

### 5.2 Abhängigkeiten

```
plug/parts.py        (nur Zahlen)
plug/geom.py         (Werkzeuge)
   ^
plug/dupont.py       importiert parts (alles) und geom; wird von den anderen als `sd` importiert
   ^
plug/institute.py    importiert dupont as sd, geom
   ^
plug/fit_test/generator.py   importiert dupont as sd, geom
plug/sample.py       importiert dupont as sd, institute as I, fit_test.generator, geom
   ^
plug/fit_test/build_page.py   importiert dupont, fit_test.generator
plug/views/build_views.py     liest nur Vorlage und data.json
plug/check.py, plug/build_all.py   rufen die Module per `python3 -m` auf
```

`import preview` (Repo-Wurzel) funktioniert, weil immer aus dem Wurzelverzeichnis gestartet wird.

### 5.3 Wer überschreibt was

| Befehl | Überschreibt |
|---|---|
| `python3 -m plug.dupont` | `stl/steckmodul_dupont/*`, `vorschau/steckmodul_dupont/*`, `plug/views/dupont/data.json` |
| `python3 -m plug.institute` | `stl/steckmodul_institut/*`, `vorschau/steckmodul_institut/*`, `plug/build/institute/{gebaeude.stl,data.json}` |
| `python3 -m plug.sample` | `stl/steckmodul_probe/*` (inkl. `README.txt`, ZIP), `vorschau/steckmodul_probe/*` |
| `python3 -m plug.views.build_views` | `plug/views/dupont/view.html`, `plug/build/institute/view.html` |
| `python3 -m plug.fit_test.build_page` | `plug/fit_test/page.html` |
| `python3 -m plug.build_all` | alles obige nacheinander |

Nicht überschrieben (Handarbeit): `PLAN.md`, `STATUS.md`, alle `*.template.html`, `angled_pin.html`.

### 5.4 Veröffentlichungen (Artifacts, privat)

| Seite | Quelle im Repo | Link |
|---|---|---|
| JST-Plan | `plug/archive/jst/view.html` | https://claude.ai/artifact/Fd9vyn5hzE1rdPCqa7BwQX |
| Dupont-Plan | `plug/views/dupont/view.html` | https://claude.ai/artifact/HUoXswtTaEGpmn4ikCrLah |
| Institutsgebäude | `plug/build/institute/view.html` | https://claude.ai/artifact/RfeBQrttmpknjsPJphQuUW |
| Passprobe | `plug/fit_test/page.html` | https://claude.ai/artifact/EWUEh7fdeEpGbfcjBiLhnF |
| Winkelpin Maße | `plug/fit_test/angled_pin.html` | https://claude.ai/artifact/4fBA8t6idKF33UpsA7bd4g |
| Powerbank-Konzept | `plug/power/concept.html` | https://claude.ai/artifact/WPkLCy4M1m8ehMzJTTr5iS |

Nach jeder Konstantenänderung neu erzeugen und veröffentlichen.

## 6. Umstrukturierung: erledigt und offen

Entscheidung des Nutzers: Schritte 1, 2, 3, 4, 5, 7, 8, 9 umsetzen; Schritt 6 nicht.

| Nr. | Schritt | Stand |
|---|---|---|
| 1 | Check-Skript | erledigt: `python3 -m plug.check` |
| 2 | „alles neu erzeugen“ | erledigt: `python3 -m plug.build_all` |
| 3 | gemeinsame Konstantendatei | erledigt: `plug/parts.py`, `plug/dupont.py` importiert sie vollständig |
| 4 | JST stilllegen | erledigt: `plug/archive/jst/`, Werkzeuge in `plug/geom.py` |
| 5 | Paket statt Wurzel-Skripte | erledigt: `python3 -m plug.<modul>` |
| 6 | Ausgabeordner umbenennen | nicht gemacht; `stl/` und `vorschau/` bleiben, STL-Dateinamen sind noch deutsch |
| 7 | große generierte Dateien nicht einchecken | erledigt: `plug/build/` in `.gitignore` (Institutsgebäude: STL, Daten, Seite) |
| 8 | Pläne zusammenführen | erledigt: `plug/PLAN.md` |
| 9 | alte Passproben entfernen | erledigt |

Namenskonvention (Entscheidung): neue Dateien und Ordner englisch, soweit sinnvoll (`README.txt` statt `LIESMICH.txt`); Texte deutsch.
Wenn später doch umbenannt werden soll: STL-Dateinamen (`gebaeude`, `kassette`, `schieber`, `platte`, `deckel`, `1_probestueck`)
und die Ordner `stl/steckmodul_*`, `vorschau/steckmodul_*` sind noch deutsch; die Seiten und `README.txt` nennen die Namen.

## 7. Offene Punkte und nächste Schritte

1. Körper der Winkelleiste: bleibt bei 2,0 mm. Etwas Wackeln gibt es immer; ein Tropfen Heißkleber in der Tasche hilft und
   ist gewollt. Passprobe v6 (Stufe 2,0 / 1,8 / 1,6) ist nur noch eine Bestätigung der Stufenhöhe.
2. Probestück (Dateien 1 bis 5) ist gedruckt und passt, es wackelt überall etwas (Heißkleber). Erledigt; Einzelwerte (Kräfte, Kontakt)
   werden bei Bedarf später gemessen.
3. Dock B (gerade Leiste) rechnet mit den aktuellen Werten (`HDR_BODY` 2,0) mit; das ist reines Durchreichen der Konstanten aus
   `plug/parts.py`. Ob die gerade Leiste aus dem Kit wirklich 2,0 hat, ist unbelegt.
4. Seiten (Artifacts) nach jedem Umbau neu veröffentlichen (Links in 5.4).
5. Kontaktpunkt der Buchse (`CONTACT` 1,5 mm, `TERM_OFF` 0,5 mm, `HSG_HOLE` 1,0) ist geschätzt; Federzunge und Kräfte sind
   berechnet, nicht gemessen (Zielwerte: Einstecken unter 10 N, Herausziehen 3 bis 8 N). Der Nutzer will das später testen.
6. Entscheidung zu Umstrukturierung und großen Dateien: getroffen, siehe Abschnitt 6.
7. Die Vorgaben aus CLAUDE.md gelten weiter: nach Generatoränderungen `python3 -m plug.check`, Vorschaubilder im Chat zeigen,
   Commits mit dem Trailer.
8. Stromversorgung und Doktorhut (Konzept, Stand 2): Powerbank Intenso XS5000 (90 × 63 × 12,6 mm). Oberplatte nur noch 12,6 mm
   (Mulde + Muldenboden + Leistenkörper) über einem hohlen Unterkasten (14,4 mm, ersetzt den Deckel), zusammen 27,0 statt 31,2 mm,
   Material bei 1:1000 etwa 278 statt 397 g. Powerbank 35 mm hinter der Kante (gerader USB-A-Stecker, Kabelkanal an der Längsseite),
   Fenster und Tastenstößel. Vier Ösen zum Annähen an einen Doktorhut (Faden zieht die Oberplatte auf den Unterkasten). Ganz unter
   den Innenhof passt die Powerbank erst ab 1:403. Offen: Hut und Powerbank messen, Abschaltschwelle, Maßstab entscheiden.
   Details: `plug/PLAN.md` Kapitel 6, Seite `plug/power/concept.html`.
