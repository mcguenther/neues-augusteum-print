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

Die dicken Gewölbe-Keile druckt der Slicer mit Füllung, nicht massiv. Für gleichmäßiges Licht:
- **Gyroid 10 %** (Rückfall 15 %): gleich in alle Richtungen, ohne durchgehende Ebenen, streut das Licht gleichmäßig und wirft keine Streifen auf die Wand; trägt sich ohne Brücken selbst. Gitter, Linien und Dreiecke werfen gerade Schatten, die man durch die 0,8-mm-Wand sieht. Blitz (Lightning) spart am meisten und lässt am meisten Licht durch, gibt aber unregelmäßige, fleckige Schatten.
- Wandlinien 2 (0,8 mm Wand = 2 × 0,4), Dach oben 4 Lagen (0,8 mm bei 0,2 mm Schicht).
- **Untere Deckschichten 2** statt 3 bis 4: die 45°-Unterseiten der Gewölbe zählen als Unterseite und bekämen sonst eine dichte Haut, die Licht schluckt.
- „Senkrechte Wandstärke sicherstellen“ (Bambu Studio: Ensure vertical shell thickness) aus: sonst füllt der Slicer an den Schrägen zusätzlich massiv.
- Weißes oder naturfarbenes PLA leitet am meisten Licht.

Offen: ungedruckt; Licht durch Rohr (1,2) und Wand (0,8) und durch die Füllung der Keile; ob Brücke 10 mit echten Brücken (statt Gewölbe) im Slicer auch ginge (spart Material); Farbversion der steckbaren Gebäude.

## Ungetestete Planwerte (müssen noch getestet werden)

Alle Werte dieser Festlegung sind **Planwerte, nicht getestet**. Sie stehen in `plug/testcase/params.py` (`MULDE_EXTRA_T`, `CASSETTE`, `HOF_*`, `OUTLINE_CLR_T`, `SCALE_PLAN`) und `plug/scale1176/placements_1300.json`; `plug/parts.py` bleibt unverändert, bis ein Test sie bestätigt hat. Test: Steckprobe 3 (Reserve-Druck, `next.md`).

| Bereich | Wert | Stand | Was der Test zeigen muss |
|---|---|---|---|
| Mulde und Platte | Mulde 14,2 mm als eine Ebene mit vollem Gebäudeumriss (getestet war der L-Fuß mit 10,2 mm) | ungetestet | Einführen, Kippen, Klemmen, Ziehkraft, Verzug |
| | Spiel Umriss zur Mulde 0,1 mm je Seite (`OUTLINE_CLR_T`) | ungetestet auf großen Flächen | Ob das Gebäude bei langen Kanten sauber hineingeht |
| | Muldenboden 0,4 mm unter sehr großen Mulden | im Kleinen bewährt, groß ungetestet | Druck ohne Support, Halt beim Einstecken |
| | Flache Unterseite 14,6 mm mit aufgeklebter Leiste (statt Dock in 20,2 mm) | ungetestet (Test-Dock steht aus) | Pin-Treffer, Halt des Klebers, Luft unter der Platte |
| | Platte 14,6 mm dick und 220,8 mm lang | ungetestet | Druckbett, Verzug, Druckzeit |
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
| | Wand 0,4 mm zwischen Hof- und Gebäude-Aussparung | ungetestet | Druck, Stehenbleiben |
| | Stämme 0,8 mm bei 1:1300 (1 mm Rückfall) | Probedruck geplant | sauberer Druck, kein Abbrechen |
| | Halt des Einsatzes (Reibrippen oder Kleber) | nicht festgelegt | bleibt er ohne Halt liegen |
| Maßstab | 1:1300 | ungetestet | feine Details bei Mindestbreite 0,8 mm |
