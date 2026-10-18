# Maßstab, Mulden und Kassettenwahl (festgelegt am 2026-10-16, Maßstab am Ende auf 1:1300 geändert)

Entscheidungen des Nutzers im Chat; Rechnung und Grafiken: `plug/scale1176/page.html` (Artifact https://claude.ai/artifact/S3qGmVQRr9tAPNqm2NyLQx, Ordnername von der ersten Fassung bei 1:1176).
**Alles Planung, nichts gedruckt, keine STL.** Werte in `plug/parts.py` und `plug/testcase/params.py` sind noch nicht umgestellt.

## Umstellung auf flache Unterseite (2026-10-16, Steckplatte)

Auf Wunsch des Nutzers (Konzept des Test-Docks, `plug/power/build_dock.py`): Die Steckplatte `plug/campus.py` hat **keine Docks im Plattenkörper** mehr. Platte 14,6 mm (F 14,2 + Muldenboden 0,4), der Muldenboden ist die unterste Schicht auf dem Bett, die Unterseite ist eben, 24 Pin-Löcher (6 Gebäude × 4) mit Fase 0,15 beidseitig, Bettkante mit Fase 0,5 (`EF_CH_T`), kein Support, Überhang 0 mm². Die Winkelleiste wird von unten aufgeklebt (Körper 2,0, Lötenden und Draht darunter). Die Lagen aus der Platzierungs-App bleiben gültig (Hüllkurve des alten Docks unverändert als Platzhalter für die Leiste unter der Platte). **Die Zeilen unten, die von Plattendicke 20,2 und Dock im Plattenkörper sprechen, sind damit überholt.** Offen: Unterkasten mit Füßen und Zapfenlöchern, Faden (Ecken), Halt der aufgeklebten Leiste (Test-Dock steht noch aus); Test-Dock-Ergebnisse können Luft und Lagen noch ändern.

## Festgelegt

| Punkt | Entscheidung | Beleg |
|---|---|---|
| Größe der Platte | höchstens 230 × 230 mm (Druckbett mit Reserve) | Nutzer |
| Maßstab | **1:1250** (Grenze für 230 mm ist 1:1242); Platte 119,7 × 228,7 mm, einteilig | `plug/scale1176/page.html`, Abschnitt Maßstab |
| Muldentiefe | **überall 4 mm tiefer**: F 14,2 statt 10,2 mm, Platte 20,2 statt 16,2 mm; die LED liegt dadurch 4 mm tiefer gegenüber dem Dach | Nutzer, Vorschlag aus dem senkrechten Schnitt |
| Standard-Kassette | **v4** (LED strahlt nach oben), überall wo sie passt (bei 1:1300: Neues Augusteum, Hörsaalgebäude, Paulinum; Paulinum nur 0,9 mm Wand, knapp, Wechsel auf V1RS möglich) | Nutzer |
| City-Hochhaus | **V2R** (zwei LEDs, hochkant, Konzept aus `cassettes.md`), weil v4 dort nicht passt | Nutzer |
| Innenhof | eigenes Einsteckteil, Bäume angedruckt (bestätigt: „Bäume andrucken ist super“) | Nutzer, Seite Abschnitt Innenhof |
| **Maßstab (aktuell)** | **1:1300**, Platte 115,6 × 220,8 mm einteilig; dafür V1RS in Institutsgebäude und Seminargebäude | Nutzer, nach Rechnung V1RS bei 1:1300 |
| Maßstab (überholt) | 1:1250 war zwischenzeitlich bestätigt (Platte 119,7 × 228,7 mm); (1:1200 ergäbe eine Platte von etwa 237 × 124 mm, über der 230-mm-Grenze); 1,3 mm Reserve auf 230 mm sind in Ordnung; Drehen der Platte (auch diagonal) bringt nichts | Nutzer |
| LED-Streifen | nur der 10-mm-Streifen, wie immer geplant; Kassettenwahl je Gebäude bleibt (v4 überall, V2R Hochhaus) | Nutzer |
| Hof-Einsatz | **ohne die 4 mm Zusatztiefe** (1 mm unter, 1,9 mm über der Oberfläche wie bisher), aber **einsetzen wie die Gebäude: mit Einführfase** (0,4 bis 0,5 mm wie `ENTRY_CH_T`/`EF_CH_T`); Stämme erst mit 0,8 mm im Probedruck testen, 1 mm als Rückfall | Nutzer |
| Institutsgebäude | **V1RS** (Wand ≥ 3,0 mm, Luft 10,2 mm bei 1:1300); Rückfall v4 nur bei 1:1250 (Luft 4,4 mm) | Nutzer, ersetzt „v4 testen“ |
| Seminargebäude | **V1RS** (Wand ≥ 3,0 mm, Luft 10,2 mm bei 1:1300); v4 hätte bei 1:1300 nur 0,6 mm Wand und passt nicht | Nutzer, ersetzt „v4 ausprobieren“ |

## Rechnung bei 1:1250 (Stand vor der Änderung auf 1:1300; Mulde +4 mm, Wand 0,8 mm Mindestmaß)

Größte Wand um den Schacht bei Grundriss und Höhe zusammen und Luft von der LED-Mitte bis zum Dach an der höchsten Stelle, an der der Schacht passt. LED v4: 2,9 mm über der Platte (6,9 − 4).

| Gebäude | Kassette | Wand mm | Dachhöhe mm | Luft LED bis Dach mm |
|---|---|---|---|---|
| Paulinum | v4 | 1,2 | 23,9 | 21,0 |
| Neues Augusteum | v4 | ≥ 3,0 | 12,5 | 9,6 |
| Hörsaalgebäude | v4 | ≥ 3,0 | 14,6 | 11,7 |
| Seminargebäude | v4 | 0,9 (knapp) | 19,2 | 16,3 |
| Institutsgebäude | v4 | 1,9 | 7,3 | **4,4** |
| City-Hochhaus | V2R | ≥ 3,0 | 95,7 | 84,1 |

## Rechnung bei 1:1300 (aktuell, Mulde +4 mm, Wand 0,8 mm Mindestmaß)

| Gebäude | Kassette | Wand mm | Luft LED bis Dach mm |
|---|---|---|---|
| Paulinum | v4 (Alternative V1RS: ≥ 3,0 / 22,4) | 0,9 (knapp) | 18,3 |
| Neues Augusteum | v4 | ≥ 3,0 | 9,1 |
| Hörsaalgebäude | v4 | ≥ 3,0 | 11,2 |
| Seminargebäude | **V1RS** (v4: 0,6, passt nicht) | ≥ 3,0 | 10,2 |
| Institutsgebäude | **V1RS** (v4: 1,6 / Luft 4,1) | ≥ 3,0 | 10,2 |
| City-Hochhaus | V2R | ≥ 3,0 | 80,4 |

Bis 1:1350 trägt der Plan, wenn auch das Paulinum V1RS bekommt (Hochhaus bei 1:1350 nicht geprüft). **V1RS**: Streifen quer, zwei LEDs (vorn und hinten), Unterbau 19,2 × 6,4 mm, 27,7 mm hoch, Verkettung am Blattrand vorbei; die LED strahlt seitlich; Konzept, Adernweg und Streifendicke 2,2 mm ungetestet. Der Hof (Maße, Stämme 0,8 mm) ist bei 1:1300 neu zu rechnen; die Zahlen der Seite für Hof, Platte und Tabellen gelten bei 1:1250.

## Offen aus dieser Festlegung

- **Institutsgebäude (jetzt V1RS; Hinweis galt für v4):** nur 4,4 mm Luft über der LED, der Schacht darf nur unter dem niedrigen Dachteil (7,3 mm hoch) liegen. Richtwert 8 mm ist eine Annahme, ungetestet. Möglichkeiten: Kassette dort anders legen, V1 (Luft 12,3 mm bei +4 mm, LED dort 6,9 mm über der Platte, strahlt aber seitlich), oder nur dort tiefer.
- **Seminargebäude (jetzt V1RS; Hinweis galt für v4):** Wand nur 0,9 mm (knapp).
- **Hochhaus V2R:** Konzept, Streifendicke 2,2 mm nicht gemessen, Adern und Verkettung ungetestet; das Hochhaus braucht eine Kassette V2R mit Schacht 12,96 × 6,4 mm und Gebäude mindestens 23,9 mm hoch (es ist 116 mm hoch). Die LED blickt dort seitlich, nicht nach oben.
- **Fuß 14,2 mm** statt 10,2 mm ist nicht getestet (Führung in der Mulde, Kippen). Dock, Kabelraum, Muldenboden und Platte rücken 4 mm tiefer; Platte 20,2 mm dick.
- Schächte sind noch Vollkörper im Generator (kein Hohlraum, kein Lichtfenster im Gebäude).
- Licht durch die Wand und Druckbarkeit der 0,8-mm-Stämme des Hofs bei 1:1250: nur ein Probedruck zeigt es.
- **Hof-Einsatz:** Fuge, Halt (Reibrippen oder Kleber) und Oberkante 1,9 mm über der Straße sind nicht festgelegt; bei 20,2 mm Plattendicke Aussparungstiefe und Einsatzdicke (heute 1 mm unter, 1,9 mm über der Oberfläche) prüfen.
- **Kabelraum und Löträume der Nachbarn** bei tieferen Docks nicht gerechnet; Fadenführung (Plan Steckprobe 2) hängt von der Plattendicke ab.
- **Platte 20,2 mm dick und 230 mm lang:** Druckzeit und Material, Auflage auf dem A1-Bett mit Reserve 1,3 mm; Verzug bei der langen Seite.
- **Steckprobe für 1:1250:** Kassette v4 mit Podest in Mulde 14,2 mm; Mini-Gebäude im neuen Maßstab; Probedruck V2R fürs Hochhaus.
- **Werte umstellen:** nach bewährtem Test `params.py` und `parts.py` auf F 14,2 setzen, Generator für den Fuß mit Mulde 14,2 und für die Platte mit allen Docks.
- **To-do (anderer Chat): Gebäude als Hohlkörper.** Jedes Gebäude braucht einen Hohlraum, in dem die Aufnahme für die Kassette (Schacht im Fuß, Lichtfenster, Dachanschlag) sitzt; heute erzeugt `generate.py` Vollkörper.

## Werte, die für die Festlegung umzustellen sind (noch nicht umgesetzt)

| Wert | Wo | alt | neu | Warum |
|---|---|---|---|---|
| Zusatztiefe der Mulde | neue Konstante `MULDE_EXTRA_T` in `plug/testcase/params.py`, geht in `F = layer_up(g1 + GUIDE + CH_F + CH_P + MULDE_EXTRA_T)` ein (Bedeutung: die 4 mm sind der **Gebäudekörper in voller Umrissform** unter der Plattenoberfläche, die Umrisse sind auf der Platte erkennbar; darunter folgt der Fuß mit der getesteten 10,2-mm-Mulde) | 0 | 4,0 | LED sitzt 4 mm tiefer unter dem Dach |
| Fußhöhe / Muldentiefe F | abgeleitet, `dims()["F"]` | 10,2 | 14,2 | folgt aus der Zusatztiefe |
| Plattendicke | abgeleitet, `dims()["plate_t"]` | 16,2 | 20,2 | Dock und Kabelraum rücken mit nach unten |
| Lage von Winkelleiste, Pin-Spitze, Kabelraum | abgeleitet (`z_hb`, `z_bb`, `z_tip`, `z_lt`) | −10,6 / −12,6 / −4,92 / −16,2 | −14,6 / −16,6 / −8,92 / −20,2 | alles unter dem Muldenboden hängt an F |
| Kassettenoberkante über der Platte | abgeleitet, `kass_top` | 6,75 | 2,75 | gleiche Kassette, Fuß 4 mm länger |
| Dach über der Kassette (Gebäudehöhe mindestens) | abgeleitet, `box_top` | 7,95 | 3,95 | wie oben; die Gebäude brauchen weniger Höhe |
| Einstecktiefe E, Muldenboden, Kassettenmaße, Schachtspiel, Fasen | `E` 5,28, `CEIL_T` 0,4, `KASS_CLR_T` 0,06, `ENTRY_CH_T` 0,4 | | **unverändert** | bewährte Werte gelten weiter; `box_h` (Fußunterkante bis Dach) bleibt 18,15 |
| Maßstab | `python3 generate.py --scale 1250`, README-Block Maßstäbe | 1000 und 1500 | 1250 zusätzlich | neue Vorgabe 230 × 230 mm |
| Plattendicke im Generator | `generate.py`: `PLATE_THICKNESS` | 3,0 | 20,2 (aus `params.dims()`), neue Platte mit Docks | die heutige Grundplatte hat weder Muldentiefe noch Docks |
| Hof-Einsatz | `generate.py`/`innenhof.py`: `POCKET_DEPTH` | 1,0 | 1,0 (unverändert), neu: Einführfase 0,4 bis 0,5 | ohne Zusatztiefe, aber einsetzen wie die Gebäude |
| Kassettenwahl je Gebäude | neue Tabelle in `params.py` | – | v4 überall, V2R für City-Hochhaus | Festlegung oben |
| `plug/parts.py` | Kaufteil-Maße und alte Werte | | **bleibt**, bis die Steckprobe 3 die 14,2 mm bestätigt | Regel aus CLAUDE.md |

## Umstellen: jetzt oder erst nach Test

Der Nutzer (2026-10-16): Steckprobe 3 ist nicht wichtig (Reserve-Druck), weil schon viel geklappt hat. Deshalb alles, was nur Planung und Parameter ist, **jetzt** in `plug/testcase/params.py` und im Generator; `plug/parts.py` und alles, was gedruckte Teile festlegt, erst nach Test.

| Jetzt (Parameter, Planung, Generator) | Erst nach Test |
|---|---|
| `MULDE_EXTRA_T = 4.0` in `params.py` (F 14,2, Platte 20,2 und alle abgeleiteten Lagen) | Umriss-Aussparung 4 mm tief plus Fußmulde 10,2 als bewährt (Steckprobe 3); danach `plug/parts.py` |
| Maßstab 1300 im Generator (`--scale 1300`), README-Block Maßstäbe | Hof-Stämme 0,8 mm als bewährt (Probedruck) |
| Kassettenwahl je Gebäude als Tabelle in `params.py` | V1RS und V2R als druckfertige Teile (Streifendicke 2,2 mm messen, Adernweg, Verkettung) |
| Hof-Einführfase 0,4 bis 0,5 mm | Fuß 14,2 mm als bewährt (Führung, Kippen) |
| Neue Platte mit Docks im Generator (statt 3 mm Grundplatte) | Paulinum v4 mit 0,9 mm Wand |

### Umgesetzt am 2026-10-16 (linke Spalte)

- `plug/testcase/params.py`: `MULDE_EXTRA_T = 4.0`, `dims(extra)` und `dims_plan()` (F 14,2, Platte 20,2; `dims()` ohne Argument bleibt unverändert, die eingefrorene Steckprobe 1 ist damit identisch, STL geprüft), `SCALE_PLAN = 1300`, `CASSETTE` (v4: Paulinum, Neues Augusteum, Hörsaal; V1RS: Seminar, Institut; V2R: Hochhaus), `HOF_CH_T = 0.4`.
- `plug/campus.py` (`python3 -m plug.campus`, etwa 20 s): neue Steckplatte 115,6 × 220,8 × 20,2 mm mit Mulde und Dock je Gebäude und Hof-Aussparung (1 mm tief, Fuge 0,15, Einführfase oben 0,4) nach `stl/steckmodul_campus/steckplatte_1zu1300.stl`, Bilder nach `vorschau/steckmodul_campus/`; Lagen in `plug/scale1176/placements_1300.json`. Ausgabe: dicht, keine Kollisionen (Löträume liegen frei und in der Platte).
- `innenhof.py`: Einführfase 0,4 mm an der Unterkante des Hof-Einsatzes; keine Zusatztiefe.
- `generate.py`: Maßstab 1:1300 gehört zu den Standard-Maßstäben; `readme.py` und `preview.py` zeigen 1:1300 im Maßstäbe-Block.
- Wände: Paulinum v4 nur 0,8 mm (Mindestmaß), alle anderen 1,2 mm. Die Mulde-Fase (1 mm) am Rand reicht bei Hörsaal- und Seminargebäude um wenige mm² über den Grundriss; unkritisch, bei Hohlkörper-Gebäuden prüfen.
- Noch nicht umgesetzt: Gebäude mit Fuß und Schacht (Hohlkörper, anderer Chat), Kabelführung zwischen den Docks, Faden-Lasche.

### Korrektur 2026-10-16 (Nutzer: Umrisse erkennbar, Hof zu flach)

- **Gebäude werden um die 4 mm nach unten verlängert:** Der volle Gebäudeumriss (Laserscan-Grundriss) reicht 4 mm unter die Plattenoberfläche (`OUTLINE_CLR_T` 0,1 Spiel), darunter folgt wie getestet die Fußmulde mit 10,2 mm (um 4 mm nach unten verschoben, auf die Umriss-Aussparung begrenzt). Gesamttiefe F bleibt 14,2, Platte 20,2. Auf der Platte sind so die Gebäudeumrisse zu sehen. Die erste Umsetzung (reine 4 mm Führungslänge im Fuß) war ein Missverständnis. Der Gebäude-Generator (Fuß und Körper 4 mm länger) bleibt To-do im Hohlkörper-Chat.
- **Hof-Einsatz tiefer:** statt 1 mm jetzt `HOF_DEPTH_T = 6,0` mm unter der Oberfläche (Nutzer; vorher 1 mm, dann 3 mm), Fuge `HOF_CLR_T` 0,1, Einführfase unten 0,4 (Einsatz); Aussparung ohne Fase oben, damit die Wand zur Gebäude-Aussparung 0,4 mm bleibt. `innenhof.model(s, fps, tiefe, spiel)`, Einsatz als `stl/steckmodul_campus/hof_einsatz_1zu1300.stl`.

### Korrektur 2026-10-17 (Nutzer: Hof-Einsatz ein solider Klotz, Steg am Hörsaalgebäude weg; erste Fassung, siehe die Korrektur 2 danach)

- **Befund:** Der Hof-Umriss (`innenhof.flaeche_mm`) hatte einen Spalt zwischen Hofgrenze und Terrasse (die beiden Treppen gehören im Scan zu keiner der Flächen) und dahinter einen Steg der Terrasse am Hörsaalgebäude (3,8 mm breit, rund 20 mm lang). In der Platte stand dort eine Rippe von 0,6 mm Breite und 6 mm Höhe, im Einsatz hing eine Zunge. Dazu kamen zwei Zungen an den Passagen (Nord, Ost), ein zweiter Spalt (Bucht am Nordende der Terrasse) und ein Splitterloch.
- **Änderung (`innenhof.py`):** Spalte bis 6 m werden geschlossen (`HOF_SCHLIESSEN` 3 m je Seite), Zungen und Zähne unter `HOF_MIN_BREITE` 4 mm entfallen, Löcher unter 16 mm² gefüllt. Der Umriss rückt nie näher an ein Gebäude, die Wand von 0,4 mm zu den Gebäude-Mulden bleibt. Die Treppen liegen als Stufen auf dem Einsatz (`treppen_mm`, `TREPPE_STUFEN` 3, Terrasse 0,55 mm, Zwischenstufen 0,36 und 0,18 mm), nicht mehr als Ausschnitt in der Platte. Geländer sind nicht modelliert (unter 0,4 mm).
- **Ergebnis bei 1:1300 (Laserscan):** Umfang 273 → 200 mm, schmale Stellen 5 → 0, Löcher 1 → 0, Einsatz 36,8 × 72,7 mm (vorher 40,9 × 72,8), dicht; alle Quellen und Maßstäbe geprüft (ein Teil, ohne Löcher, Abstand zu Gebäuden 0,50). Vergleichsseite `plug/hof/page.html`, alter Stand in `plug/hof/alt/`.
- **Ungetestet:** Sitz des Einsatzes mit dem durchgehenden Klotz (Steckprobe 3), Druck der Zwischenstufen (Slicer glättet oder druckt Absatz), an den Passagen bleibt Plattenfläche statt Hof (bis zu 5 mm).

### Korrektur 2 zum Hof (2026-10-17, Nutzer): bis an die Fassaden, gerade Treppen, Südtreppe, Trennwand A/B (Südtreppe und B danach ersetzt, siehe Korrektur 3)

Ersetzt das Schließen des Spalts (`HOF_SCHLIESSEN`) und die Treppen aus der Korrektur davor. Der Nutzer sah weiße Flächen zwischen Hof und Nachbargebäuden (Bucht an der Westfassade, Streifen entlang der Fassaden, Gang im Südwesten) und wollte alles gerade, gefüllt und den Fassaden folgend.

- **Hoffläche:** OSM-Fußgängerfläche (um 2 m vergrößert) in einer Hülle, bis an die Laser-Grundrisse der Gebäude. Gerade Schnitte nur am Durchgang im Nordosten (Ecke des Paulinum) und am Ende der Südtreppe. Zungen unter 4 mm entfallen, Löcher unter 16 mm² sind gefüllt. Die Messflächen `grenze` und `terrasse` bleiben in `data/innenhof.json` für die Luftbildproben, die Form steht im Abschnitt `form` (Hofsystem: Achse 11,8°, u quer, t längs, Meter).
- **Treppen als Rechtecke im Hofsystem** (`innenhof.treppen_mm`), Maße aus Höhenprofilen des Scans: W am Seminargebäude (u bis -119,5 m, t von -12 bis 4 m, drei Stufen nach Norden), K an der Kante vor dem Hörsaalgebäude (t von -18 bis -16 m, drei Stufen), S im Gang zwischen Seminar- und Hörsaalgebäude (7 m, sechs Stufen von der Terrasse 2,35 mm über der Platte bis auf Plattenhöhe, die letzte bündig mit der Grundplatte, Stufenhöhe 0,39 mm). Terrasse als Rechtecke (`form.terrasse`).
- **Trennwand zwischen Hof-Aussparung und Gebäude-Mulden** (`HOF_WALL_T` in `params.py`, `plug.campus.build(hof_wand=…)`): A mit 0,8 mm (Hof-Umriss 0,9 mm vom Grundriss: Spiel der Mulde 0,1 plus Wand), B ohne Wand (Aussparung greift `HOF_OVERLAP_T` 0,02 in die Mulde, Hof liegt zwischen den Gebäuden). `python3 -m plug.campus` schreibt beide: `steckplatte_1zu1300.stl` und `hof_einsatz_1zu1300.stl` (A), `…_ohne_wand.stl` (B). Oben schneidet die Einführfase der Mulde (0,5) die Wand A auf 0,3 mm an.
- **Ergebnis bei 1:1300:** Einsatz A 36,5 × 76,0 mm (Fläche 1595 mm²), B 38,7 × 77,2 mm (1763 mm²), vorher 40,9 × 72,8 mm; alle dicht, alle Quellen und Maßstäbe geprüft (ein Teil, ohne Löcher und schmale Stellen). Vergleichsseite `plug/hof/page.html`.
- **Empfehlung:** A drucken, B als Rückfall; in Steckprobe 3 beide.

### Korrektur 4 (2026-10-17, Nutzer): Steg am Weg zwischen Seminar- und Hörsaalgebäude weg, Treppe endet an der Gebäudekante

Seite: `plug/weg/plan.html` (`python3 -m plug.weg.build_page`). Der Gang auf Terrassenhöhe zwischen Seminar- und Hörsaalgebäude war durch einen Steg am Hörsaalgebäude auf 1,9 mm verengt (Weg sonst 6,7 mm). Der Steg ist im Luftbild ein Verbindungsgang in der Höhe und steht nur im LoD2-Grundriss (OSM kennt ihn nicht), im LoD2 als Vollblock bis zum Boden.

- **Steg entfernt, in allen Quellen und Maßstäben:** `lod2.OHNE_STEG` (Fenster in lokalen m) mit `lod2.ohne_steg` in `lod2.models` nach der Aufteilung der Zellen: im Fenster entfällt vom Hörsaalgebäude, was als Auswuchs schmaler ist als 2 × `STEG_OEFFNUNG` (2 m). Laserscan übernimmt den Grundriss aus LoD2. Fläche 10 mm² bei 1:1300 (etwa 17 m²), Hörsaal-Grundriss 4094,1 → 4084,0 mm².
- **Treppe am Westende beginnt an der Gebäudekante:** `data/innenhof.json` `form.platte.gang_sued.u[0]` von -145,5 auf -145,0 m (Westkante des Hörsaalgebäudes; das Seminargebäude endet bei -145,6). Vorher stand die unterste Stufe 0,5 m über die Gebäudekante hinaus und lief als schmaler Streifen an der Westwand des Hörsaalgebäudes entlang (Nutzer-Hinweis auf der Planseite).
- **Absatz in der Kante des Hörsaalgebäudes bleibt** (steht auch in OSM), ebenso die Treppe selbst.
- **Prüfung:** `generate.py` alle STL `dicht=True`; `plug.campus` dicht, keine Kollisionen, Kassettenlagen unverändert (zwischengespeichert); Hof-Aussparung unverändert (1556 mm²); `plug.buildings 03_hoersaalgebaeude` dicht, keine Kollisionen. `plug.check` (alle Generatoren) nicht gelaufen. Nicht gedruckt.

### Korrektur 3 zum Hof (2026-10-17, Nutzer): Fassung A bleibt, Gang im Süden auf Terrassenhöhe, Treppen in der Platte

Ersetzt die Südtreppe des Einsatzes und die Fassung B (ohne Trennwand) aus der Korrektur davor. Foto des Nutzers: Der Gang zwischen Seminar- und Hörsaalgebäude liegt nahtlos auf Terrassenhöhe und mündet nach Westen auf die Straße, dort kommen Treppen.

- **Trennwand:** nur Fassung A mit `HOF_WALL_T` 0,8 mm. B (`…_ohne_wand.stl`, `HOF_OVERLAP_T`) ist entfallen.
- **Einsatz endet am Südende des Hofs** (`form.huelle.t_sued` -26 m im Hofsystem) mit geradem Rand auf Terrassenhöhe; die Südtreppe im Einsatz entfällt. Treppen im Einsatz bleiben W (Seminargebäude) und K (Kante vor dem Hörsaalgebäude).
- **Aufbauten der Platte** (`innenhof.platte_aufbau_mm`, in `plug/campus.py` zur Platte addiert, bevor Mulden und Hof-Aussparung sie zuschneiden; die Mulden schneiden dafür bis `SCHNITT_OBEN` 3 mm über die Oberfläche): **Gang im Süden** auf Terrassenhöhe (2,35 mm über der Platte, Scan: 0,75 m über dem Hof) bis zum Westende, wo Seminar- und Hörsaalgebäude enden (u -145,5 m im Hofsystem); dort **Treppe** mit 6 Stufen à 0,39 mm, 5,4 mm lang, zwischen den Gebäudewänden, die letzte Stufe auf Plattenhöhe. **Nordost:** Gang am Paulinum bleibt auf Plattenhöhe, eine Treppe mit 6 Stufen à 0,30 mm (5,4 mm) steigt zum Hofboden (1,8 mm), der Einsatz hat dort einen geraden Rand. Alle Maße in `data/innenhof.json`, Abschnitt `form.platte`.
- **Ergebnis bei 1:1300:** Einsatz 35,5 × 70,7 mm, Hoffläche der Aussparung 1556 mm² (Original 1631), Platte und Einsatz dicht, keine Kollisionen; Vergleichsseite `plug/hof/page.html` (Original gegen neu, Höhenplan, Schnitte durch Trennwand und Gang, 3D).
- **Baumkronen 1 mm kleiner** (`KRONE_ABZUG` in `innenhof.py`, Nutzer: Kronen sollen beim Einsetzen nicht an den Gebäuden anstoßen), gilt für alle Quellen und Maßstäbe.
- **Ungetestet:** Trennwand 0,8 mm im Druck, Platte um bis zu 2,35 mm höher als der Rand (Druckzeit, Verzug), Stufen der Platte (zwei Schichten je Stufe).

### Korrektur 4 (2026-10-17, Nutzer): Durchgang zwischen Paulinum und Institutsgebäude frei, Treppe bis zum Ostende

Befund (Seite `plug/passage/page.html`): Das Laserscan-Höhenfeld sah über der Gasse nur das Dach der Brücke (LoD2: 131,1 bis 145,0 m ü. NHN) und machte daraus einen Vollblock im Paulinum (Grundriss `plug/passage/geom.py TUNNEL_M`, 27 mm²); die senkrechten Streifen an der Ostwand sind Rasterfacetten. Der Nutzer wollte erst einen Durchgang mit waagerechter Decke, dann (nach dem ersten Vorschlag) „einfach das ganze Teil weg“, weil noch Flächen die Gasse versperrten (Absatz in der Nordwand, Splitter an der Institutswand, Grat an der Ostmündung).

- **Laserscan-Modell:** `laserscan.durchgang_schnitt` schneidet alles nördlich der Nordwand des Paulinums ab (Wandlinie `DURCHGANG_WAND_T` 61,15 m im Hofsystem, Länge `DURCHGANG_U`), Körper und Grundriss. Nur Quelle laserscan; OSM und LoD2 unverändert. Institutsgebäude unverändert, keine Brücke.
- **Treppe der Platte im Nordosten** (`data/innenhof.json` `form.platte.nordost`): 9 Stufen à 0,2 mm (eine Druckschicht), Teilung 42,75 m, von der Hofkante (u -94) bis zum Ostende der früheren Brücke (u -56), nur in der Gasse (t 61,0 bis 67,6), nicht mehr auf die OSM-Fläche begrenzt (sie deckt den Durchgang nicht ab). Vorher 6 Stufen à 0,3 mm auf 7 m.
- **Mulde und Fuß:** `plug.campus` (Platte) und `plug.buildings` (Paulinum) nehmen den neuen Grundriss automatisch aus `G.source_models("laserscan")`; die Kassettenlagen bleiben (die Paulinum-Kassette liegt mit ihrer Wand dicht an der Nordwand, die Wandlinie bleibt dieselbe; der Schnitt trifft sie nicht).
- **Prüfung:** `plug.passage.geom.freie_gasse` schneidet beide Körper in 18 Höhen (0,2 bis 28 mm) und sucht Material im Streifen zwischen den Wänden: keines, engste freie Breite 6,3 m (4,8 mm); vorher 28 mm² Rest.
- **Ergebnis (2026-10-17):** `plug.campus` Platte und Hof-Einsatz dicht, keine Kollisionen; `plug.buildings` alle sechs Gebäude neu mit Fuß-Fase 2,0, alle dicht, keine Kollisionen. Beim Paulinum musste dafür die Fase auf dem Randstück vor dem Rohr entfallen (siehe `next.md`, Folge aus r8): die Kassette (Wand 1,2) sitzt dicht an der Nordwand, die Fase 2,0 samt Innenring wäre in den Schacht gelaufen (schon mit dem alten Grundriss 33,6 mm³ Kollision).
- **Ungetestet:** Stufen von 0,2 mm im Druck, neuer Muldenumriss des Paulinums (gerade Nordwand), Paulinum ohne Fuß-Fase auf dem Stück vor der Kassette.

### Korrektur 5 (2026-10-17, Nutzer): Trennwand zwischen aneinanderstoßenden Gebäuden, Fuge über die ganze Höhe

Befund (Seite `plug/divider/page.html`): Vier Paare stoßen in OSM, LoD2 und Laserscan ohne Abstand aneinander (Paulinum / Neues Augusteum 53,2 mm Naht, Neues Augusteum / Hörsaalgebäude 20,6, Hörsaalgebäude / Hochhaus 24,6, Seminar- / Institutsgebäude 21,6; zusammen 120 mm = 156 m). Die Mulden verschmolzen dort, es stand keine Wand. Paulinum und Neues Augusteum überlappten sich auf 29 mm² (bis 4,8 mm breit), die Hohlkörper-STL durchdrangen sich auf ganzer Höhe (1,3 mm² je Lage): beide ließen sich nicht gleichzeitig einsetzen.

- **Entscheidung des Nutzers:** Schlitz zwischen den Gebäuden über die ganze Höhe, Wand 0,8 mm (wie `HOF_WALL_T`), Spiel weiter 0,1 mm, das Neue Augusteum verkleinern, das Paulinum nicht. Fuge = 2 × Spiel + Wand = **1,0 mm** (1,3 m in echt).
- **Umsetzung:** `plug/divider/geom.py` (`trenn`, `getrennt`) schneidet Grundriss und Körper der weichenden Gebäude (Körper ∩ neuer Grundriss); `plug.campus.models_plan` ruft es auf, `plug.campus.build`, `plug.buildings` und `plug.power.build_concept` benutzen es; `plug.campus.TRENNWAND = False` gibt den Stand davor. Nur Steckplatte und steckbare Gebäude (Laserscan 1:1300); die Komplettmodelle in `stl/osm`, `stl/lod2`, `stl/laserscan` bleiben.
- **Wer weicht (Regel in `trenn`):** je Naht beide zur Hälfte, solange jedes Schachtrohr danach mindestens `RESTWAND_T` = 2,9 mm (Wand 0,8 plus `FUELLEN_T` 2,0 plus 0,1) vom neuen Rand bleibt, sonst gibt der Nachbar die ganze Fuge. Ergebnis: Neues Augusteum gibt die Überlappung und die Fuge zum Paulinum ab (−82 mm², das Rohr des Paulinums sitzt nur 0,18 mm von der Naht), das Hörsaalgebäude gibt die Fuge zum Neuen Augusteum und zum Hochhaus allein ab (−47 mm², Rohre dort 3,35 und 3,18 mm von der Naht), Seminar- und Institutsgebäude je zur Hälfte (−10,6 und −10,5 mm²), Paulinum und Hochhaus unverändert.
- **Lehre (Hohlverfahren):** Mit halber Fuge am Hochhaus (Rohr 2,68 mm vom Rand) blieben zwischen Rohr und Wand weniger als 2 mm Luft; `hohl.spalten` füllte den Spalt und das Gewölbe wurde zu Vollmaterial (27,9 statt 13,5 cm³ im Hochhaus). Ab einer Fuge von etwa 0,76 mm kippte es, bei 0,5 mm nicht. Deshalb die Regel mit 2,9 mm. Vor jeder weiteren Änderung des Umrisses das Volumen je Gebäude vergleichen.
- **Platte und Batteriefach:** Plattenmaß unverändert 115,583 × 220,844 mm (die Nähte liegen innerhalb der äußeren Grundrisse); Powerbank-Fach, Elektronikbox, Stützen, Schalter und Docks im Konzept `plug.power.build_concept` bleiben identisch (verglichen mit und ohne Trennwand, nur die Materialschätzung der Oberplatte steigt von 120 auf 124); Hof-Aussparung ändert sich um 0,006 mm².
- **Ergebnis:** `plug.campus` Platte und Hof-Einsatz dicht, keine Kollisionen; Wand zwischen den Mulden 0,80 mm über alle vier Nähte, 130 mm Wand insgesamt; `plug.buildings` Neues Augusteum 24,04 (vorher 24,83 cm³), Hörsaalgebäude 43,78 (43,97), Seminargebäude 11,55 (11,67), Institutsgebäude 18,52 (18,72), Hochhaus 13,54 (unverändert), alle dicht, keine Kollisionen mit der Kassette; `python3 -m plug.divider.check`: Gebäude untereinander kein gemeinsames Volumen, Abstand an den Nähten 1,00 mm (0,999 beim Paulinum).
- **Nachtrag 2026-10-18, versucht und wieder zurückgenommen (Nutzer: vorher besser, wichtig nur, dass die Trennwand zulasten des Neuen Augusteums geht; `GERADE_NAHT` und `SCHLITZ_FENSTER` sind leer, Platte und Gebäude 01 und 02 sind byte-gleich zum Stand davor, Commit d44409f)** (Nutzerwunsch: Wand zwischen Paulinum und Neuem Augusteum soll einfach von West nach Ost laufen): Die Naht ist eine gerade Kante (Südkante des Paulinums = Nordkante des Augusteums), nur zwei Zähne des Paulinums (rechteckig 29 mm², dünn, zusammen 38 mm²) ragen nach Süden in den Augusteum-Grundriss; die Wand wand sich um beide, im Nordosten blieb ein kleiner Streifen des Augusteums stehen. Jetzt schneidet `geom.trenn` das Paulinum an der Geraden durch (-62,48 | 44,28) und (-22,08 | 35,95) ab (`GERADE_NAHT`) und füllt den Schlitz, den der große Zahn im Augusteum hinterlässt (1 mm breit, 4 mm tief, `SCHLITZ_FENSTER`, `SCHLITZ_R` 1,2); `getrennt` füllt dabei auch den Körper bis zur Dachhöhe der Umgebung (12,1 mm). Wand jetzt 42 mm lang in einer Linie. **Preis:** der große Zahn trägt den höchsten Firstpunkt des Paulinums (Laserscan), das Paulinum verliert 38 mm² (5,1 %) und wird 2,3 mm (3,0 m in echt) niedriger (45,2 statt 42,9 mm über der Platte), der Fuß und die Kassette bleiben. Neues Augusteum verliert netto 34 statt 82 mm² (24,75 cm³, Höhe wieder 28,8 mm über der Platte wie im Original, vorher durch den Beschnitt 26,0). Paulinum 6,75 statt 7,49 cm³, Brücken 8,9 statt 13,2 mm², Kragstücke 30,0 mm², `fase_entfaellt` 271 statt 280 mm². Platte, Fach, Docks, Schalter unverändert (verglichen mit und ohne Trennwand). Wieder eingeschaltet wird es mit den Werten aus dem Kommentar an `GERADE_NAHT` und `SCHLITZ_FENSTER` in `plug/divider/geom.py`, danach `plug.campus` und `plug.buildings 01_paulinum 02_neues_augusteum`.
- **Stand ohne gerade Naht, Zahlen für den Zipfel (dünner Zahn des Paulinums im Osten):** 1,0 mm breit (Mindestmaß 0,8), 3,3 mm lang, steht von z = -12,5 bis etwa 10 bis 20 mm über der Platte (rund 25 mm hoch, kein Zahn über die ganze Höhe); die Fuß-Fase 2,0 schneidet seine untersten 1,7 mm weg, die Spitze wächst zwischen z = -13 und -12,2 an (Kragstück bis 1,0 mm je Lage wie die übrigen Kragstücke des Paulinums, keine Stelle der Überhangprüfung liegt dort); in der Platte ein Schlitz 1,2 × 3,4 mm, Wand zum Augusteum 0,8. Das Neue Augusteum bleibt in diesem Stand 40,1 statt 43,0 mm hoch (der überlappende Block trägt seinen höchsten Punkt). Ungedruckt.
- **Ungetestet:** Slicer und Druck der freistehenden Wand 0,8 × 14 mm (wie die Hof-Wand); Einsetzen aller sechs Gebäude gleichzeitig. Nicht neu erzeugt: Hof-Seite, Steckplatten-Ansicht (`plug.views.campus.build_view`) und Konzeptseite; sie nehmen die Fuge beim nächsten Lauf automatisch auf.

### Korrektur 6 (2026-10-18): Zapfenaufnahmen und Fadenösen in der Steckplatte

Die Steckplatte hatte unten nur die 24 Pin-Löcher. Jetzt hat sie auch die Teile, die sie mit dem Unterkasten des Konzepts (`plug/power/build_concept.py`, `variant(1300)`) verbinden. Code: neues Modul `plug/campus_underside.py`, eingehängt in `plug.campus.build` (`UNTEN = True`; `--ohne-unten` gibt den Stand davor); die Lagen der Zapfen werden einmal aus dem Konzept gelesen und in `plug/scale1176/underside_1300.json` zwischengespeichert (veraltet der Stand, rechnet `build` ihn neu; erzwingen mit `python3 -m plug.campus --unten-neu`). Passprobe im Rechner: `python3 -m plug.campus_underside` (ca. 20 s). Beides ist nach unten offen (Bett), kein Support. Platte, Pin-Löcher, Mulden, Hof, Aufbauten und Hof-Einsatz sind unverändert (Schnitte alt/neu bei z = 9 bis 14,5: Differenz 0,0000 mm²; `hof_einsatz_1zu1300.stl` byte-gleich).

**Zapfenaufnahmen (Sacklöcher), 2 Stück** (Werte des Konzepts, `PP.PIN_PLAN`, `PP.POST`, Auswahl in `variant()`: von den 6 Stützen tragen nur 2 einen Zapfen):

| Größe | Wert | Herkunft |
|---|---|---|
| Loch | Ø 4,3, 2,8 tief ab Plattenunterseite, Einführfase 0,5 am Bett | Konzept (Zapfen Ø 4,0 × 2,5, Gleitspiel 0,15 je Seite, 0,3 Luft über der Spitze; L10, L34) |
| Lage (Rohkoordinaten der Platte) | (−108,75; −101,91) und (−28,75; −101,91), im Konzeptsystem (Südwestecke = 0; 0) (20; 20) und (100; 20), über den Stützen an der Südkante | `variant(1300)` |
| Mindestwand | 1,71 mm zu Mulden und Pin-Löchern (gefordert 0,8), Hof 99 mm weit weg, Plattenrand 12,9 mm | gemessen in `plug.campus_underside.walls` (Schnitte der Platte ohne Unterseite bei z = 0,1 bis 8) |
| Überhang | Decke Ø 4,3 bei z = 2,8 (Brücke 4,3 mm, unter 10 mm), Fase in 0,2-mm-Stufen | `layer_overhang` |

Die Löcher liegen nirgends unter einer Mulde (die Mulden lassen nur 0,4 mm Boden): kein Zapfenloch schneidet Mulde, Hof, Pin-Loch oder Trennwand. Zapfen im Rechner eingesetzt: 0 mm³ Überschneidung (Konzept-Unterkasten ganz, und nur die Zapfen); Kontrollen greifen (Unterkasten 0,20 seitlich: 0,22 mm³, Zapfen 0,35 höher: 0,43 mm³).

**Fadenösen: die „halbe Pille mit Steg“ aus `plug/thread/`, nicht der V-Kanal des Konzepts.** Der Auftrag nannte den V-Kanal (Ø 2,2, Scheitel 3,4, Trichter R 2,0) als getestet. Er wurde in Steckprobe 2 (r4) verworfen (der Faden kam durch keinen Kanal, Kanäle unter etwa 3 mm schließen sich im Druck, L32). Der Nachfolger `plug/thread/` (Plan Stand 2, abgenickt 16.10.; Eckmuster P3 und P45 gedruckt: Decke glatt, Faden geht durch, r6) ist der festgelegte Stand für die große Platte (`plug/thread/round/r6_eckmuster/summary.md`, „Folgen“), also gebaut:

- **Maße** (`plug/thread/params.py`, `PILL`, `CHOSEN_AIR`, `WALL_MIN`, `NOTCH_PAD`): Luft über dem Steg 4,0, Steg 5,0 × 4,5, Decke 8,5, Taschenbreite 10, Länge am Boden 22, Mündung mit Fase 2,0 am Rand und 1,0 am Steg-Fuß 26 × 14, Wand zu Rand, Mulden, Hof und Zapfenlöchern mindestens 1,4, darüber 6,1 mm Platte (14,6 − 8,5). Faden Ø 0,8 (doppelt, ungemessen).
- **Lagen** (Mitte der Mündung, Rohkoordinaten | Konzeptsystem; so nah an der Ecke wie möglich, Ausrichtung automatisch, an der Fach-Kante nur mit der schmalen Seite zur Kante):

| Ecke | Mitte roh | Mitte Konzept | lange Seite | Abstand zur Ecke (Summe der Verschiebungen) | Eckaussparung im Unterkasten (Konzeptsystem, offen zum Rand) |
|---|---|---|---|---|---|
| SW | (−112,8; −113,0) | (15,9; 8,9) | x | 2,0 | x −1,0 bis 30,9, y −1,0 bis 17,9 (32 × 19) |
| SO | (−29,1; −113,0) | (99,7; 8,9) | x | 2,0 | x 84,7 bis 116,6, y −1,0 bis 17,9 (32 × 19) |
| NW | (−120,3; 58,0) | (8,5; 179,9) | y | 26,5 | x −1,0 bis 17,4, y 164,9 bis 194,9 (18 × 30); die Ecke ist von der Mulde fast bis an den Rand belegt, die Tasche sitzt erst an der Westkante weiter südlich (y 166,9 bis 192,9) |
| NO | (−22,1; 83,0) | (106,7; 204,9) | y | 2,0 | x 97,7 bis 116,6, y 189,9 bis 221,8 (19 × 32) |

- **Messwerte:** Wand zu Mulden und Pin-Löchern 1,78 mm, zum Plattenrand 1,40 (am Bett wegen der Randfase 0,5 nur 0,9), zum Zapfenloch 1,45, Hof 24 mm; Kuppel: größter Sprung 3,0 mm in der obersten Lage (flache Decke über dem Steg), in 7 Lagen über 0,25 mm; die Kuppel ist dieselbe Form wie in P3 und P45 (dort ohne Support gedruckt, Decke glatt). Volumen der Platte 215,16 → 209,26 cm³, dicht, 0 Berührkanten.
- **Faden-Passprobe im Rechner** (Faden Ø 0,8 taut vom Hut unter dem Unterkasten durch Eingang, über die Stegkante, durch den Ausgang): 0,000 mm³ gegen die Platte an allen vier Ecken; gegen den Konzept-Unterkasten ohne neue Eckaussparung 1,09 mm³ (der Boden steht im Weg), mit der Eckaussparung der Tabelle 0,000 mm³.

**Was sich gegenüber dem Konzept ändern muss (Unterkasten, noch nicht umgesetzt, nicht Teil dieser Änderung):**
- Die Eckaussparungen sind größer als die V-Aussparungen des Konzepts (8 × 15): `build_concept.place_vs`/`v_solid` durch `plug.campus_underside` ersetzen (`notch_boxes(lay)`).
- Die Aussparung SW und SO schneidet die Stützen bei (20; 20) und (100; 20) an (5,4 mm² je Ecke), NW die Stütze (20; 180) (2,4 mm²), NO das Powerbank-Fach (77,4 mm²). Das Konzept muss Stützen, Zapfen und Fach neu rechnen, mit diesen Aussparungen als Sperrfläche: dann hat das Fach an der Nordkante 6 Kandidaten (um etwa 8 mm nach Westen), die Elektronikbox 60 × 35 passt weiter; bei Aussparungen in 30 mm Breite an beiden Nordecken wäre es kein Kandidat (deshalb dort nur die schmale Ausrichtung). Die Zapfenlöcher der Platte folgen dann den neuen Zapfenstützen (`python3 -m plug.campus --unten-neu`).
- Die Konzeptseite zeigt den V mit nur einem Schenkel: in `build_concept.v_solid` liegt das Polygon des Schenkels s = −1 im Uhrzeigersinn und fällt weg (`CrossSection` ohne `ccw`); `plug/campus_underside.v_cut` ist korrigiert.

**Alternative V-Kanal (`python3 -m plug.campus --faden v`, `campus_underside.FADEN = "v"`):** die vier V des Konzepts an den Lagen des Konzepts (Mitten (−123,8; −113,9), (−18,1; −113,9), (−123,8; 91,0), (−18,1; 91,0), Achse y; Wand zum Rand 1,9, zu den Mulden 12 mm; Eckaussparung des Konzepts 8 × 15, kollidiert mit nichts), Ø `V_D` = 2,2 wie im Konzept (r4: „mindestens 1 mm weiter“, ändern in `campus_underside.V_D`); größter Überhang je Lage 1,19 mm am Übergang Trichter/Schenkel, 0,24 mm je Lage im Schenkel; Volumen nur 0,32 cm³ weniger. Passt zum Unterkasten des Konzepts, aber der Faden-Test r4 sagt: nicht durchfädelbar.

**Ungetestet** (alles neu bei der großen Platte): Zapfen 2,5 mm lang (nie gedruckt; 1,5 wackelte), Druck der Zapfenloch-Decke Ø 4,3 und der Taschenkuppel in einer 14,6 mm dicken Platte ohne Support, Luft 4,0 (Kompromiss zwischen den gedruckten 3,0 und 4,5), Einfädeln und Zugprobe (offen seit r6), Lage der Taschen weit von der Ecke (NW 26,5 mm) und die Eckaussparungen im Unterkasten (gibt es noch nicht). Druck: nichts davon geprüft.

- **Nachtrag 2026-10-18 (Nutzer: Position des einen Zapfens ändern, halbe Pille bleibt, Oberplatte wird getestet):** Das Batteriefach (Unterkasten Stand 7, PR #32, Branch `ccr-395903c6-2y3sex`, noch nicht in diesem Branch, Logbuch dort: „Testdruck Unterkasten läuft, wartet auf den Testbogen (17.10.)“) ist schon im Druck. Seine Zapfen stehen laut `U_unterkasten.stl` bei (20 | 20) und (100 | 180) in Plattenkoordinaten (Ecke unten links, Süden y = 0), seine Oberplatte `U_oberplatte.stl` hat dort Zapfenlöcher Ø 4,3, 2,8 tief mit Fase 0,5. Das Konzept dieses Branches (ohne `FACH_FIX`) hatte den zweiten Zapfen bei (100 | 20) gesetzt, 160 mm daneben. Jetzt: `ZAPFEN_LOKAL = [(20,20), (100,180)]` in `plug/campus_underside.py` (Zapfenlöcher bei (-108,75 | -101,91) und (-28,75 | 58,09) in Rohkoordinaten). Prüfung am gedruckten Unterkasten: Überschneidung Kasten mit neuer Platte 0,0000 mm³ (Kasten 17,6 hoch, Platte aufgelegt), Kontrolle mit 0,3 mm seitlich verschobenem Kasten 1,23 mm³; Zapfenlöcher in der neuen Platte gleich wie in `U_oberplatte.stl` (gleiche Mitten, Ø 4,3). Mindestwand des neuen Zapfenlochs zu Mulden und Pin-Löchern 1,21 mm.
- **Offen (Fäden):** Die vier Fadentaschen (halbe Pille) brauchen im Unterkasten Eckaussparungen von etwa 32 × 19 mm; der gedruckte Kasten hat die kleineren der Faden-V (Rand 2,0). Die Oberplatte lässt sich allein testen (Zapfen, Taschen, Einfädeln von oben und unten); mit dem gedruckten Kasten stößt der Faden an dessen Boden an, bis dort die Aussparungen vergrößert werden (oder die Ecken abgesägt). Die Faden-V der gedruckten Oberplatte von PR #32 (Ø 3,6 am Bett) wurden nicht übernommen.

### Korrektur 7 (2026-10-18): Display-Mulde und Dock in der Steckplatte

Die Steckplatte hat jetzt auch die Mulde und das Dock für das **Display-Gebäude** (OLED mit INA226, `plug/display/`, Entwurf E4). Code: neues Modul `plug/campus_display.py` (Maße, Lage, Prüfungen), eingehängt in `plug.campus.build` (`DISPLAY = True`, `--ohne-display` gibt den Stand davor; `mulde_body` bekam den Parameter `clr`, Standard unverändert). Das Display-Gebäude steht nicht in `params.CASSETTE` und nicht in `placements_1300.json`; die Lage ist die Konstante `campus_display.DISPLAY_LAGE`. Platte außerhalb des neuen Docks unverändert (Schnitte alt/neu bei z = 0,1 bis 14,5: 0,0000 mm², nichts hinzugekommen, abgetragen 3115,5 mm³ nur im Bereich x 86,8 bis 101,7, y 26,1 bis 42,7; `hof_einsatz_1zu1300.stl` byte-gleich, Gebäude-STL, Trennwände, Zapfenlöcher, Fadentaschen und Unterkasten nicht angefasst).

**Maße: erster Satz** (Commit 59000df, Probedruck 1; Fuß, Mulde mit Kodierecke und Einführfase 0,5 waren dort „in Ordnung“, Vorgabe des Nutzers). Der Code friert die Werte ein (`campus_display.SATZ1`); `SATZ = 2` baut dieselbe Mulde nach dem aktuellen, ungedruckten Stand von `body4.py`.

| Größe | Wert (Plattenkoordinaten, SW-Ecke = 0) | Herkunft |
|---|---|---|
| Lage Kopf | Ostfläche des Kopfes x = 111,5 (4,1 mm von der Plattenkante, `layout.EAST_XE`), Mitte **y = 34,4** | Vorgabe des Nutzers (Ostrand, Display links = Süden), südlichste Lage der Prüfung (unten) |
| Mulde | Fuß 13,86 (x) × 15,48 (y) plus Spiel `CLR_MULDE` 0,15 je Seite = 14,16 × 15,78, x 87,19 bis 101,35, y 26,51 bis 42,29; Kodierecke 3,0 vorn Süd (Südostecke); Tiefe 14,2 bis auf den Muldenboden 0,4; Einführfase 0,5 | 59000df: Hals 15,48 × 7,86 (Schacht 13,08 × 5,46 = V2-Unterbau 12,96 × 5,34 plus 0,06 je Seite, Wand 1,2), Verlängerung nach vorn `FOOT_EXT` 6,0, `KEY` 3,0 |
| Pin-Löcher | vier, Ø 1,4 mit Fase 0,15 beidseitig, Reihe in y bei x = 91,27 (20,23 hinter der Ostfläche des Kopfes), y = 30,59 / 33,13 / 35,67 / 38,21, Teilung 2,54 | `C.pin_holes` (dieselbe Geometrie wie bei den Gebäuden), gedreht wie D4/D5 in `plug/display/build.py` |
| Dockzone (Steckerraum unter der Platte) | x 80,95 bis 92,05, y 26,97 bis 41,83 (11,1 × 14,9), Lötenden nach Westen | `BC.dock_zone()` (wie die Gebäude-Docks) |

**Die Mulde ist die gedruckte Mulde der Mini-Platte D5 aus 59000df:** Schnitte in z = 0,1 / 0,3 / 0,5 / 14,1 / 14,35 / 14,55 und die Pin-Löcher decken sich mit der Mulde der großen Platte (Flächendifferenz 0,0000 mm², Lochmitten gleich). Der echte D1 aus 59000df (STL, in die Weltlage zurückgerechnet; `git show 59000df:stl/steckmodul_display/D1_koerper.stl`) sitzt in der neuen Mulde mit 0 mm³ Überschneidung (Kopf 0,3 mm in der Luft), 0,10 mm Verschiebung geht noch, 0,20 mm stößt (7,1 bis 9,0 mm³), 90° / 180° / 270° stoßen (780 / 1186 / 772 mm³), gespiegelt (Kodierecke Nord) stößt (50 mm³). Die Hülle aus Fuß und Kopf, die `plug.campus` im Rechner benutzt, enthält den echten D1 vollständig (Differenz 0 mm³).

**Lage: südlichste freie Stelle am Ostrand** (`campus_display.lage_suche`, 0,1-mm-Schritte, y 20 bis 110; Kopf bei x = 111,5; freie Lagen y = **34,4 bis 56,0** und 90,3 bis 97,0). Die Prüfung rechnet mit den echten Teilen dieser Platte, nicht mit denen des Konzepts (`plug/display/layout4.Plate4` nimmt die Faden-V des Konzepts und meldet 39 bis 58):
- **Untergrenze 34,4 (Kopf y 15,25 bis 53,55):** der Kopf (38,3 breit) bleibt 1,5 mm (`AIR_MARGIN`) über der erhabenen Schrift und dem Nordpfeil; der Buchstabe N des Nordpfeils reicht bis y = 13,69, Luft jetzt 1,56 mm. Eine Stufe weiter südlich (34,3) ist der Kopf gesperrt („Luft“). Die Schrift (bis y ≈ 13) liegt darunter, `LABEL_Y` 15 ist eingehalten. Der Kopf steht über keiner Beschriftung. Die Fadentaschen im Süden (SO bei (100,7 | 9,9), Mündung bis y 16,9) und das Zapfenloch (20 | 20) sperren nichts: die Mulde liegt 9,6 mm von der Fadentasche SO, die Dockzone 18,3 mm von der Eckaussparung.
- **Obergrenze 56,0:** darüber liegt die Dockzone näher als 1,0 mm an der Dockzone des City-Hochhauses (Abstand bei 56,0: 1,05 mm), noch weiter nördlich auch der Kopf am Hochhaus. 90,3 bis 97,0 ist die zweite Lücke (nördlich des Hochhauses, die Dockzone läge teilweise über der ESP-Fläche des Kastens), nicht gewählt.
- **Ansicht von Osten (`vorschau/steckmodul_campus/steckplatte_mit_display_von_osten.png`):** links (Süden) das Display, dahinter (westlich) das Hörsaalgebäude (y 18,0 bis 122,7, östlichster Punkt x = 69,2), rechts (nördlich) davon das City-Hochhaus (y 58,7 bis 93,7, Abstand zum Kopf in y 5,2 mm), Nordpfeil frei. Draufsicht `steckplatte_mit_display_oben.png`.

**Prüfwerte** (`python3 -m plug.campus`: dicht, keine Kollisionen; Passprobe `python3 -m plug.campus_display`, ca. 40 s):
- Platte dicht, Volumen 206,148 cm³ (eigen) gegen 206,148 cm³ (`prusa-slicer --info`, manifold yes), alt 209,264 cm³.
- Mindestwand der Mulde zu anderen Aussparungen 9,7 mm (Fadentasche SO 9,6, Zapfenloch 64,9, Plattenrand 14,2; gefordert 0,8 bzw. 1,4); Pin-Löcher liegen in der Mulde (Muldenboden 0,4). Dock außerhalb oder überlappt 0,00 mm²; Dockzone 20,9 mm von der nächsten Dockzone eines Gebäudes, 23,5 mm vom Plattenrand.
- Überhang je 0,2-mm-Lage (Mulde, Pin-Löcher): kein Sprung über 0,25 mm; Boden 0,4 auf dem Bett, Mulde oben offen: keine Brücke, kein Support.
- Kopf in der Luft gegen die sechs Gebäude-STL (Weltlage, z = 0 = Plattenoberfläche): Überschneidung 0,000 mm³ (Hülle erster und zweiter Satz, Körper mit Blende und Rückdeckel), kleinster Abstand 16,0 mm zum Hochhaus (3D, über der Platte; in der Draufsicht 5,2 mm), zum Hörsaalgebäude 31,5 mm, zu den übrigen vier über 50 mm; gefordert mindestens 1,5. Kontrolle: Kopf 30 mm nach Norden stößt am Hochhaus (345 mm³). Alle sechs Gebäude gegen die Platte mit Display-Dock: 0,000 mm³.
- **Dockzone gegen den gedruckten Unterkasten Stand 7** (`U_unterkasten.stl`, Kasten 17,6 hoch, Platte mit der Unterseite auf z = 17,6; Dockzone als Körper von z = 14,1 bis 17,6, Steckerraum 3,5): Überschneidung der Dockzone mit dem Kasten 0,0000 mm³; Platte (mit Dock) auf dem Kasten 0,0002 mm³ (Rauschen), Kontrolle 0,3 mm seitlich 1,24 mm³; Kontrolle Dockzone 6,6 mm zur nächsten Stütze verschoben 0,15 mm³. Abstand der Dockzone zu den Teilen des Kastens in der Draufsicht: nächste Stütze (97,0 | 23,0) 6,3 mm, ESP-Fläche (x 47 bis 107, y 53 bis 88) 11,6 mm, Eckaussparungen 18,3 mm, Außenwand 21,1 mm, Fach der Powerbank 50,6 mm, Zapfen 59,2 mm, Schalterloch (Westwand, y = 40) 78,5 mm. Kein Konflikt, die Lage muss nicht ausweichen. Bild `vorschau/steckmodul_campus/display_dock_unterkasten.png` (Wände, Stützen, Zapfen, Fach, ESP-Fläche, Eckaussparungen, Schalterloch, Dockzonen, Display-Mulde).

**Fuß des zweiten Satzes in dieser Mulde** (`plug/display/body4.py` heute: Hals 12,96 × 5,34 statt 15,48 × 7,86, Fuß 11,34 × 12,96 statt 13,86 × 15,48; Kopf 38,34 breit, Rückwand 2,6, Vorderkante des Fußes gleich): Der Fuß passt hinein (0 mm³ mit den Stiften an den Pin-Löchern), sitzt aber **lose**: Luft 1,41 mm je Seite (West, Ost, Süd, Nord) statt 0,15, und die Stifte liegen 1,26 mm näher an der Vorderkante des Fußes (8,67 statt 9,93), der Körper muss also 1,26 mm weiter westlich stehen (Ostfläche des Kopfes x = 110,24 statt 111,5). Die Lage der Pin-Löcher ist an der Mulde des ersten Satzes festgelegt; mit 1,4 mm Spiel in beide Richtungen treffen die Stifte nicht sicher die Löcher (Loch Ø 1,4, Fase 0,15). Die Verdrehsicherung bleibt (180° stößt an die Verlängerung), die Kodierecke wirkt nicht mehr. **Soll der zweite Satz passen, braucht er eine eigene Mulde:** `SATZ = 2` (Mulde 11,64 × 13,26, Pin-Reihe bei x = 92,5) oder der Fuß wird auf das Maß des ersten Satzes verbreitert. Der Kopf des zweiten Satzes ist 0,04 mm breiter (38,34 gegen 38,3) und 0,9 mm tiefer (8,8 statt 7,9 mm bis zum Rückenkeil); beide Köpfe sind gegen die Gebäude geprüft.

**Ungetestet:** Mulde und Pin-Löcher sind die gedruckten und in Ordnung befundenen Maße aus Probedruck 1, aber nur an der 26 × 28 mm kleinen Mini-Platte; in der 14,6 mm dicken großen Platte (Verzug, Druck der Mulde neben den anderen) nie gedruckt. Die Lage (Kopf 1,56 mm über dem Nordpfeil, 5,2 mm vom Hochhaus), der Winkelleisten-Einbau und die Lötenden unter der Platte (Dockzone, Aderweg zur ESP-Fläche 11,6 mm weiter nördlich) sind gerechnet, nicht gebaut. Der zweite Satz des Display-Gebäudes ist ungedruckt (Probedruck am 2026-10-18 erwartet); passt er nicht, `SATZ = 2` oder Fuß anpassen und die Lagesuche wiederholen.

### Korrektur 2 (2026-10-16): keine Stufen in der Mulde, LED mittig im Gebäude

- **Mulde ohne Stufen:** gerade Wände mit Spiel 0,1 (`MULDE_CLR_T`) über die ganze Tiefe von 10,2 mm, oben eine 45°-Fase von 0,5 mm (`MULDE_CH_T`). Weggefallen sind Entlastung (`RELIEF`), Führungsband (`BAND`) und die Treppenfase aus `institute.pocket_cuts`. Das ist eine Abweichung vom getesteten Aufbau der Steckprobe 1 (dort mit diesen Stufen), also in Steckprobe 3 zu prüfen (Einstecken, Wackeln, Kippen). Die einzige Stufe, die bleibt, ist der Boden der 4 mm tiefen Umriss-Aussparung.
- **Lage der Kassette:** `plug/campus.py` sucht jetzt die Lage, bei der die LED möglichst nahe am Flächenschwerpunkt des Gebäudes sitzt (LED-Lage je Kassette in `led_local`: v4 Mitte der Auflage, V-Varianten Chip auf dem Blatt). Bedingungen: Schacht mit Wand 1,2 (sonst 0,8), Gebäude an der Stelle hoch genug, Dock und Lötraum innerhalb der Platte ohne Überlappung. Ergebnis (1:1300): LED 0,0 bis 0,3 mm von der Gebäudemitte (Paulinum, Neues Augusteum, Hörsaal, Seminar, Hochhaus), Institutsgebäude 4,0 mm.
- **Preis der Mitte (Luft LED bis Dach an dieser Stelle):** Paulinum 18,1 mm, Neues Augusteum **4,1** (Dach in der Mitte nur 7,0 mm hoch), Hörsaal **7,6**, Seminar 10,3, Institut 10,3, Hochhaus 80,9. Neues Augusteum und Hörsaal liegen unter dem Richtwert von 8 mm (Annahme, ungetestet). Möglichkeiten dort: Kassette außermittig (früher: Luft 9,1 bzw. 11,2), nur dort tiefere Mulde, oder v4 mit tieferer LED-Fläche.

### Korrektur 2 (Nutzer, 2026-10-16): eine Ebene, LED mittig

- **Keine Stufen in den Mulden.** Die Mulde ist nur noch der **volle Gebäudeumriss, durchgehend bis F 14,2** (Spiel `OUTLINE_CLR_T` 0,1, keine Fase oben, damit die Wand zum Hof 0,4 mm bleibt). Die zweite Ebene in Form der Kassette (Fußmulde 10,2) entfällt. Der Gebäudekörper hat unten eine durchgehende Fläche, die Kassette sitzt eingesetzt darin und ragt nicht heraus (bündig). Die alte „Fußmulde“ der Steckprobe 1 (L-Fuß, 10,2 mm) gilt für die Probe weiter, nicht für die Campus-Platte.
- **Das ändert Annahmen:** Der Gebäudefuß ist der ganze Körper, 14,2 mm lang, mit ganzer Grundfläche; Führung und Kippen sind damit anders als in Steckprobe 1 und müssen in Steckprobe 3 geprüft werden (große Mulde, Brücke 0,4 mm Muldenboden über dem Dock bleibt). Die Wand um den Schacht (0,8 bis 1,2 mm) betrifft jetzt die Wand des Körpers um die Kassette.
- **LED mittig in der Grundfläche:** `plug/campus.py` sucht für jedes Gebäude die Lage (Drehung 0 bis 355°) mit der LED am nächsten zur Mitte der Grundfläche (Schwerpunkt, sonst Stelle mit größtem Randabstand), bei Wand mindestens 0,8 (bevorzugt 1,2) und Dock innerhalb der Platte ohne Überlappung mit anderen Docks. Zwei LEDs (V1RS, V2R): Mitte zwischen beiden.
- Ergebnis bei 1:1300 (Dach = Höhe über dem Schacht, Luft = Dach minus LED-Höhe über der Platte bei Mulde +4):

| Gebäude | Kassette | Wand | LED von der Mitte | Dach mm | Luft mm |
|---|---|---|---|---|---|
| Paulinum | v4 | 0,8 | 0,3 | 21,2 | 18,3 |
| Neues Augusteum | v4 | 1,2 | 0,0 | 7,0 | **4,1** |
| Hörsaalgebäude | v4 | 1,2 | 0,0 | 10,9 | 8,0 |
| Seminargebäude | V1RS | 1,2 | 0,1 | 18,6 | 10,4 |
| Institutsgebäude | V1RS | 1,2 | 4,0 | 18,5 | 10,3 |
| City-Hochhaus | V2R | 1,2 | 0,1 | 92,4 | 80,8 |

  Mittig kostet Luft: Im Neuen Augusteum liegt die LED jetzt unter dem niedrigen Mitteltrakt (Dach 7,0 mm, Luft 4,1 mm); vorher, in der Ecke unter dem höheren Dach, waren es 9,6 mm. Im Institutsgebäude begrenzt der L-Grundriss die Mitte (LED 4,0 mm daneben).

### Neues Augusteum und Platzierungs-App (2026-10-16)

- **Neues Augusteum: LED unter dem hohen Dach** (Nutzer) statt exakt mittig: `PREFER_ROOF` in `plug/campus.py`; Ergebnis: Dach 12,0 mm über dem Schacht, LED 6,7 mm von der Mitte, Luft 9,1 mm (statt 4,1 bei mittiger Lage).
- **Platzierungs-App** `plug/scale1176/placer.html` (Artifact https://claude.ai/artifact/8DHMHzJuPVhD9cAyWWUkA2): Schächte ziehen, drehen, Kassette und Muldentiefe wechseln; Prüfungen: Wand um den Schacht (0,8 Mindestmaß, 1,2 bevorzugt), Dachhöhe über dem Schacht gegen die nötige Höhe, Luft über der LED (unter 5 rot, unter 8 gelb, Annahme), LED-Abstand zur Mitte (über 4 gelb, über 10 rot), Dock innerhalb der Platte (1 mm Rand) und ohne Überlappung mit anderen Docks, Hinweis bei Dock unter fremder Mulde. „Kopieren“ liefert JSON für `plug/scale1176/placements_1300.json`; danach `python3 -m plug.campus` (ohne `--replace`).

### Lagen vom Nutzer festgelegt (2026-10-16)

Der Nutzer hat die Lagen in der Platzierungs-App eingestellt (`plug/scale1176/placements_user_1300.json`); `python3 -m plug.scale1176.nudge` hat sie minimal angepasst, bis die Wand um den Schacht mindestens 1,2 mm beträgt (Verschiebung bis 0,8 mm, Drehung bis 3°), und `placements_1300.json` geschrieben. Ergebnis: nur das Paulinum musste (um dx −0,10, dy −0,10 mm, Wand 1,10 → 1,21 mm); alle anderen Lagen sind unverändert (Wand: Neues Augusteum 4,8, Hörsaal 6,7, Seminar 4,1, Institut 1,5, Hochhaus 4,7 mm). Docks innerhalb der Platte und ohne Überlappung. Grafik `vorschau/steckmodul_campus/positionen_diff.png` (`python3 -m plug.scale1176.nudge_plot`). Die Platte `stl/steckmodul_campus/steckplatte_1zu1300.stl` ist damit neu erzeugt. Die LED-Lage ist nicht mehr mittig erzwungen, sondern die des Nutzers.

### Abgleich mit dem Powerbank-Konzept (2026-10-17)

`plug/power/build_concept.py` (Konzeptseite, Stand 6) nutzt jetzt dieselbe Grundlage wie `plug/campus.py`: Laserscan-Grundrisse, Maßkette `params.stack_plan()` (F 14,2), die Oberplatte ist die **Steckplatte aus `plug.campus.build()`** (flache Unterseite 14,6 mm, Pin-Löcher, Hof 6 mm, Gravur), dazu nur V-Kanäle und Zapfenlöcher. Die Docks sitzen **alle sechs an den festgelegten Lagen** (`placements_1300.json`); die Powerbank liegt im Unterkasten unter dem durchgehenden Steckerraum (`STECKERRAUM` 3,5 mm Luft zwischen Plattenunterseite und Powerbank) und darf unter den Docks liegen. Nur die Stützen weichen den Dockzonen aus. Ergebnis bei 1:1300: Platte **115,6 × 220,8 mm**, Oberplatte 14,6 + Unterkasten 17,4 = **32,0 mm**, Powerbank-Fach Nordkante, Elektronik 60 × 35 mm, kein Dock fehlt.

- Der erste Abgleich (2026-10-16) rechnete noch mit der Tasche und der Nische in der Platte und zog die Powerbank von den Docks fern; das ist überholt. Die Nische (12 × 9,5 mm) entfällt im Konzept ebenso wie Steg-Anschlag, Stößel und Taste.
- Zapfen 2,5 (`PIN_PLAN`, wie das Test-Dock), Zapfenloch 2,8 tief nur außerhalb von Mulden und Hof, damit über dem Loch Platte steht. Der Unterkasten ist an keiner Stelle durch die Docks eingeschränkt.
- Die Seite `plug/power/layout.html` (Lösungsfindung „Fach gegen Docks“) ist überholt und trägt einen Hinweis.
- Test-Dock und Fachprobe bleiben bei den Steckprobe-2-Werten (`params.stack()`, F 10,2); nur das Konzept nutzt `stack_plan()`.

### Steckbare Hohlgebäude (2026-10-17, `plug/buildings.py`, ungedruckt)

Die sechs Laserscan-Gebäude bei 1:1300 als steckbare Hohlkörper: Fuß über den vollen Grundriss bis 14,2 mm unter die Plattenoberseite (wie die Mulde in `plug/campus.py`, Bettkante mit Fase), Gebäude und Fuß gemeinsam mit `hohl.py` ausgehöhlt (Wand 0,8), Boden 1,2 mm, Schachtrohr (Wand höchstens 1,2, im Paulinum die 1,2 aus der Platzierung), Aufnahme je Kassette (v4 / V1RS / V2R aus `params.CASSETTE`): Schacht mit Einpressspiel und Einführfase, Anschlag 1,2 mm breit mit 45°-Unterseite, darüber Freiraum für LED, Streifen und Blatt (Spiel 0,3) mit 45°-Walm.

Druckbarkeit ohne Support im Gebäude (Gebäude steht auf dem Boden, Schacht nach unten offen):
- **Gewölbe streng**: Decken ab 2 mm Spannweite werden 45°-Gewölbe (`BRUECKE_T` 2, im Generator 10). Mit 10 blieben unter den Dächern Decken mit bis zu 4,3 mm Auskragung (Neues Augusteum 540 mm²).
- **45°-Dach über allen Schnitten** (`dach45`): wo das niedrige Dach den Freiraum über der Kassette kappt, wird er von oben in 45° beschnitten; nur der echte Bedarf der Kassette bleibt.
- Prüfung je 0,2-mm-Lage, getrennt nach Brücken (ringsum getragen) und Kragstücken (freie Kante).

| Gebäude | Kassette | Volumen | Kollision | Brücken | Kragstücke |
|---|---|---|---|---|---|
| Paulinum | v4 | 7,9 cm³ | 0 | – | 22 mm², bis 0,7 mm |
| Neues Augusteum | v4 | 36,1 cm³ | 0 | – | 24 mm², bis 2,1 mm (über der LED-Box unter dem niedrigen Dach, unvermeidbar) |
| Hörsaalgebäude | v4 | 56,3 cm³ | 0 | bis 0,8 mm | – |
| Seminargebäude | V1RS | 11,7 cm³ | 0 | – | 5 mm², bis 0,7 mm |
| Institutsgebäude | V1RS | 18,7 cm³ | 0 | 4 mm², bis 1,4 mm | 13 mm², bis 0,7 mm |
| City-Hochhaus | V2R | 13,6 cm³ | 0 | bis 0,8 mm | 7 mm², bis 0,7 mm |

Alle dicht, Platz für die Kassette überall vollständig. Kragstücke bis 0,7 mm sind 45°-Treppen der Schichtung und unkritisch. Preis: mehr Material, weil das Gewölbe die Räume unter den Dächern füllt (Neues Augusteum 36 statt 21 cm³ mit Brücke 10). Schnittbilder: `vorschau/steckmodul_campus/gebaeude/` (`uebersicht_schnitte.png`).

#### Gewölbe überarbeitet (2026-10-17, Nutzer: „zu viel gewinkelt, das Gewölbe kann von mehreren Seiten und von der Aufnahme aus kommen“)

Befund: Das Gewölbe ist ein Feld aus 45°-Kegeln, die von den tragenden Teilen aufsteigen; jeder Wandpunkt bekommt seine Starthöhe aus dem entferntesten Deckenpunkt in seinem Einzugsgebiet. Tragend waren nur die Außenwände; das Schachtrohr in der Mitte zählte nicht. So reichten die Einzugsgebiete quer durchs Gebäude, das Gewölbe setzte sehr tief an (Neues Augusteum links bei −11 mm) und stieg nur von einer Seite auf. Wo zwei Kegel mit sehr verschiedenen Starthöhen aneinanderstoßen, blieben dünne Spalten im Hohlraum (Hörsaalgebäude bei x ≈ 16, Institutsgebäude bei −9 und 6 mm).

Umgesetzt (`hohl.py`, Optionen nur in `plug/buildings.py` an; `generate.py` unverändert):
- **Rohr als Stütze** (`hohl.ceiling(stuetzen=…)`): von der Rohroberkante (aufs Lagenraster abgerundet) steigen ebenfalls Kegel auf; jeder Raum wird von Wand und Rohr aus überwölbt, das Gewölbe setzt höher an. Stützpunkte, deren Oberkante unter der Starthöhe ihres Einzugsgebiets liegt, tragen nicht (sonst füllte der niedrige Rohrkopf einen hohen Raum, City-Hochhaus 54,9 statt 13,7 cm³); danach werden die Einzugsgebiete neu gerechnet.
- **Säule über dem Rohr** bis 0,4 mm über die Walmspitze, darüber flache Taschen unter 2 mm gefüllt: sonst griffe das Gewölbe eines Nachbarraums über den Rohrkopf und zwischen ihm und dem Walm über der LED bliebe eine nach unten hängende Kante (4,6 mm, gefunden in der Lagenprüfung).
- **Spalten füllen** (`hohl.spalten`, 2 mm): schmalere Teile des Hohlraums werden Material, gedruckt mit Füllung statt zwei Wänden und Spalt.
- **Je Gebäude mit und ohne Rohrstütze gebaut, das leichtere genommen**: das Rohr hilft unter niedrigen Dächern, in hohen, schmalen Gebäuden kostet die Säule nur.
- Geprüft und verworfen als Standard: `--umkreis 2` (Kegel nur im eigenen Bereich): Neues Augusteum 21,9 statt 23,7 cm³, aber senkrechte Stufen in der Decke statt glatter Grate.

| Gebäude | vorher | nachher | Rohrstütze | Kragstücke | Brücken |
|---|---|---|---|---|---|
| Paulinum | 7,9 cm³ | 8,0 cm³ | ohne (mit 10,3) | bis 1,0 mm | bis 2,1 mm |
| Neues Augusteum | 36,1 cm³ | **25,2 cm³** | mit (ohne 36,3) | bis 2,1 mm (über der LED-Box) | – |
| Hörsaalgebäude | 56,3 cm³ | **44,7 cm³** | mit (ohne 56,7) | bis 1,2 mm | – |
| Seminargebäude | 11,7 cm³ | 12,0 cm³ | ohne (mit 13,4) | bis 1,0 mm | – |
| Institutsgebäude | 18,7 cm³ | 19,0 cm³ | ohne (mit 19,9) | bis 1,5 mm | bis 1,7 mm |
| City-Hochhaus | 13,6 cm³ | 13,7 cm³ | ohne (mit 15,5) | bis 1,2 mm | bis 1,7 mm |
| zusammen | 144,2 cm³ | **122,5 cm³** (−15 %) | | | |

Alle dicht, keine Kollision, Platz für die Kassette vollständig. Die kleinen Zunahmen ohne Rohrstütze kommen vom Füllen der Spalten (Material statt zwei Wänden mit Spalt; gedruckt mit Füllung sparsamer als es das Volumen zeigt). Vorher/Nachher: Schnittbilder in `vorschau/steckmodul_campus/gebaeude/`.

#### Füllung im Slicer (Empfehlung, ungetestet)

Steht in [`plug/slicer.md`](../slicer.md) (eine Quelle für alle Slicer-Einstellungen der steckbaren Gebäude): Gyroid 10 %, 2 untere Deckschichten, „Ensure vertical shell thickness“ aus, Support aus.

Offen: ungedruckt; Licht durch Rohr (1,2) und Wand (0,8) und durch die Füllung der Keile; ob Brücke 10 mit echten Brücken (statt Gewölbe) im Slicer auch ginge (spart Material); Farbversion der steckbaren Gebäude.

#### Im Slicer massiv (2026-10-18, Nutzer: Paulinum „alles solid bis auf den Einsatz der Kassette“)

Befund (nachgewiesen mit PrusaSlicer 2.7.2 ohne Oberfläche, `prusa-slicer --info` und `--export-gcode` mit den Werten aus `plug/slicer.md`):
Geometrisch waren die STL hohl, aber der Slicer drehte beim Laden die ganze Innenschale des Paulinums um (18 772 Flächen umgedreht,
Volumen nach der Reparatur 46,0 statt 7,5 cm³ = Außenschale 26,8 plus Innenschale 19,3). Damit galt der Innenraum als Material: im G-Code
Gyroid-Füllung über den ganzen Grundriss ab etwa 18 mm über dem Bett (Höhe des Anschlagrings), darunter massive Füllung im Schacht und im
Westraum (Filament 10,4 statt 7,3 cm³). Ursache sind Netzfehler aus der Ausgabe, nicht die Form: Manifold rechnet in double, die STL hat float32;
dabei fielen 220 Splitterdreiecke (Paulinum; andere Gebäude 1 467 bis 6 962) auf Fläche null, dazu kamen 20 bis 708 Mikrohohlräume als eigene winzige
Schalen (|Volumen| unter 1 mm³), die die Wände nur an Kanten berühren (Berührkanten). Der Slicer (admesh, in PrusaSlicer, Bambu Studio und Orca)
löscht entartete Dreiecke, verbindet die Nachbarn neu und richtet danach die Normalen von Nachbar zu Nachbar aus; über die Berührkanten lief das
in die nur an 4 Punkten angebundene Innenschale und drehte sie um. Bei den anderen fünf Gebäuden blieb das Volumen nach der Reparatur gleich
(höchstens 124 umgedrehte Flächen, Neues Augusteum). Keine Ursache war die waagerechte Fläche über dem Schacht: der Anschlagring hat die
freie Öffnung, darüber ist beim Paulinum kein Material, im G-Code ist der Schacht hohl. Die senkrechte helle Linie an der Vorderseite im
Screenshot ist die Naht: 78 von 80 Schichten des Fußes beginnen die Außenwand an der Innenecke rechts neben dem Schachtvorsprung.

Abhilfe (`plug/buildings.py`, `sauber()`, als letzter Schritt in `gebaeude()`): Netz aus dem float32-Netz neu als Manifold aufbauen (Manifold zieht
die entarteten Dreiecke dabei selbst zusammen) und eigene Schalen mit |Volumen| unter `SPLITTER_MM3` (1 mm³) nach der Netztopologie (nicht nach Lage)
weglassen; fällt auf den alten Körper zurück, wenn das Ergebnis ungültig wäre oder das Volumen um mehr als 0,2 % abweicht. Werte je Gebäude in der JSON
(`netz`). `plug.export_campus` prüft zusätzlich entartete Dreiecke und, wenn PrusaSlicer installiert ist, das Volumen nach dessen Reparatur.

| Gebäude | Volumen | entartete Dreiecke | Berührkanten | Mikroschalen weg | Slicer-Volumen vorher → nachher | Filament (PrusaSlicer) vorher → nachher |
|---|---|---|---|---|---|---|
| Paulinum | 7,49 cm³ | 220 → 0 | 217 → 2 | 20 | **46,02 → 7,49 cm³** | **10,42 → 7,33 cm³** |
| Neues Augusteum | 24,04 → 24,05 | 4 902 → 3 | 3 998 → 5 | 325 | 24,04 → 24,05 | 14,47 → 14,26 |
| Hörsaalgebäude | 43,78 → 43,80 | 6 962 → 8 | 5 587 → 15 | 708 | 43,78 → 43,80 | 24,78 → 24,50 |
| Seminargebäude | 11,55 → 11,56 | 2 989 → 6 | 2 434 → 4 | 395 | 11,55 → 11,56 | 9,61 → 9,48 |
| Institutsgebäude | 18,52 → 18,53 | 6 467 → 1 | 5 358 → 1 | 616 | 18,52 → 18,53 | 13,20 → 12,96 |
| City-Hochhaus | 13,54 → 13,55 | 1 467 → 1 | 1 340 → 2 | 413 | 13,54 → 13,55 | 12,62 → 12,58 |

(Entartet hier: Fläche null in float32; nach der Zählung des Slicers, zwei gleiche Ecken, sind es überall 0.) Alle dicht, Kollision 0, Platz fehlt 0,
`plug.divider.check` ohne Kollisionen; Grundrisse, Schacht, Anschlag, Platte und Trennwand unverändert (Volumen +0,01 cm³ = entfernte Mikrohohlräume).
Nach der Reparatur in PrusaSlicer ist beim Paulinum, Hochhaus und allen anderen keine Fläche mit Inhalt umgedreht (Hörsaalgebäude 11 Splitter mit
zusammen 0,000 mm²). Nicht geprüft: Bambu Studio und Orca selbst (gleicher admesh-Kern, aber andere Versionen); der Druck.

Lehre: Hohlkörper nach jedem Booleschen Aufbau mit einem echten Slicer-Kern prüfen (Volumen nach dessen Reparatur = Netzvolumen), nicht nur mit
Manifold (das baut das Netz beim Laden selbst sauber auf und meldet „dicht“, auch wenn der Slicer es anders sieht). Die SLA-Ausgabe von PrusaSlicer
taugt dafür nicht, sie füllt geschlossene Innenräume immer.

## Ungetestete Planwerte (müssen noch getestet werden)

Alle Werte dieser Festlegung sind **Planwerte, nicht getestet**. Sie stehen in `plug/testcase/params.py` (`MULDE_EXTRA_T`, `CASSETTE`, `HOF_*`, `OUTLINE_CLR_T`, `SCALE_PLAN`) und `plug/scale1176/placements_1300.json`; `plug/parts.py` bleibt unverändert, bis ein Test sie bestätigt hat. Test: Steckprobe 3 (Reserve-Druck, `next.md`).

| Bereich | Wert | Stand | Was der Test zeigen muss |
|---|---|---|---|
| Mulde und Platte | Mulde 14,2 mm als eine Ebene mit vollem Gebäudeumriss (getestet war der L-Fuß mit 10,2 mm) | ungetestet | Einführen, Kippen, Klemmen, Ziehkraft, Verzug |
| | Spiel Umriss zur Mulde 0,1 mm je Seite (`OUTLINE_CLR_T`) | **r8: Hochhaus-Stummel geht nur mit Kraft hinein, sehr fest; 0,15 testen (Vorgabe des Nutzers)** | Ob 0,15 leicht, aber ohne Wackeln passt |
| | Muldenboden 0,4 mm unter sehr großen Mulden | im Kleinen bewährt, groß ungetestet | Druck ohne Support, Halt beim Einstecken |
| | Flache Unterseite 14,6 mm mit aufgeklebter Leiste (statt Dock in 20,2 mm) | ungetestet (Test-Dock steht aus) | Pin-Treffer, Halt des Klebers, Luft unter der Platte |
| | Platte 14,6 mm dick und 220,8 mm lang | ungetestet | Druckbett, Verzug, Druckzeit |
| | Zapfenaufnahmen unten: 2 Sacklöcher Ø 4,3 × 2,8 mit Fase 0,5 für Zapfen Ø 4,0 × 2,5 (Korrektur 6) | ungetestet (Zapfen 1,5 wackelte in r4, 2,5 nie gedruckt) | Sitz, Wackeln, Druck der Lochdecke Ø 4,3 ohne Support |
| | Fadentaschen unten: vier „halbe Pillen mit Steg“, Luft 4,0, Fase 2,0 / 1,0, Mündung 26 × 14 (Korrektur 6, `plug/thread/`) | P3 und P45 (Luft 3,0 und 4,5) gedruckt, Faden ging durch; Luft 4,0 und der Einbau in die große Platte ungetestet; Zugprobe offen (r6) | Einfädeln, Zug am Steg, Druck der Kuppel in der 14,6 mm Platte, Eckaussparungen im Unterkasten (noch nicht gebaut) |
| | Display-Mulde und Pin-Löcher am Ostrand (Korrektur 7, `plug/campus_display.py`): Maße des ersten Satzes (Mulde 14,16 × 15,78 mit Kodierecke, Spiel 0,15, Fase 0,5, Boden 0,4), Lage Kopf x = 111,5, y = 34,4 | Mulde und Pin-Löcher an der Mini-Platte D5 gedruckt und in Ordnung; in der großen Platte, die Lage (Kopf 1,56 mm über dem Nordpfeil) und der Einbau unter der Platte ungetestet; zweiter Satz des Display-Gebäudes (Fuß 2,52 mm kleiner) ungedruckt und passt nur lose | Sitz des Fußes, Pin-Treffer, Verzug der großen Platte, Platz für Lötenden und Adern, ob der zweite Satz eine eigene Mulde braucht (`SATZ = 2`) |
| Kassetten | V1RS (Seminar, Institut), V2R (Hochhaus) | nur Konzepte, nie gedruckt | Einpressen mit Streifen und Blatt, Adernweg, Verkettung der zwei LEDs |
| | Streifendicke 2,2 mm | nicht gemessen | am echten Streifen messen, vor jeder STL |
| | Blattdicke 1,2 oder 1,6 mm, 45°-Versatz über dem Aderschlitz | offen | Druckbarkeit, Bruch beim Biegen |
| | Wand um den Schacht (Paulinum 1,2, Institut 1,5, sonst über 4 mm) | nur gerechnet | Ob Einpressen hält und die Wand nicht reißt |
| | v4 im Paulinum bei 1,2 mm Wand | knapp | wie oben, Rückfall V1RS |
| Licht | Luft über der LED, Richtwert 8 mm | Annahme | Hotspots unter dem Dach |
| | Neues Augusteum: LED 6,7 mm neben der Mitte, 9,1 mm Luft | Nutzerentscheidung, ungetestet | Lichtverteilung im Trakt |
| | Licht durch die Wand | nie mit LED gesehen | Gebäude mit Hohlraum und LED |
| Innenhof | Hof-Einsatz 6 mm tief (`HOF_DEPTH_T`, Nutzerwunsch) | ungetestet | Sitz, Druck des dickeren Einsatzes |
| | Fuge 0,1 mm (`HOF_CLR_T`), Einführfase 0,4 mm (`HOF_CH_T`) | ungetestet | Einsetzen und Herausnehmen |
| | Blockiger Hof-Umriss bis an die Fassaden (Mindestbreite 4 mm), Treppen als Rechtecke mit Stufen 0,18 / 0,37 mm auf dem Einsatz, Gang im Süden als Teil der Platte | ungetestet | Sitz ohne Steg, Druck der Stufen |
| | Treppe der Platte in der Gasse am Paulinum: 9 Stufen à 0,2 mm bis zum Ostende (Korrektur 4) | ungetestet | Stufen von einer Schicht im Druck, Paulinum-Mulde mit gerader Nordwand |
| | Trennwand Hof zu Gebäude-Mulde 0,8 mm (`HOF_WALL_T`) | ungetestet | Wand steht im Druck (0,4 mm kam in r7 nicht), Führung der Gebäude |
| | Trennwand zwischen aneinanderstoßenden Gebäuden 0,8 mm, Fuge 1,0 mm (`plug/divider/geom.py`) | ungetestet | Wand steht im Druck, alle sechs Gebäude lassen sich gleichzeitig einsetzen |
| | Gang im Süden und Treppen in der Platte (Terrassenhöhe 2,35 mm über der Oberfläche, Stufen 0,39 und 0,30 mm) | ungetestet | Druckzeit, Verzug, Stufen |
| | Stämme 0,8 mm bei 1:1300 (1 mm Rückfall) | Probedruck geplant | sauberer Druck, kein Abbrechen |
| | Halt des Einsatzes (Reibrippen oder Kleber) | nicht festgelegt | bleibt er ohne Halt liegen |
| Maßstab | 1:1300 | ungetestet | feine Details bei Mindestbreite 0,8 mm |
