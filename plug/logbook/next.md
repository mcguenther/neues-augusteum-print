# Nächste Drucke und offene Punkte

Stand: nach Steckprobe 2 (r4) und Fachprobe Powerbank (r5), beide 2026-10-16 ausgewertet. Als Nächstes ein Plan für Steckprobe 3 (siehe unten). Priorität 1 = nächster Druck, 2 = danach, 3 = bei Gelegenheit.
Ablauf je Runde: siehe `README.md` (Plan, Abnicken, STL, Druck, Testbogen, Auswertung).

## Übergabe 2026-10-19: Passung bei anderen Filamenten, Probedruck ausgewertet (r10)

Ausgewertet in [`rounds/r10_passung_filament/summary.md`](rounds/r10_passung_filament/summary.md); Beschlüsse und Aufgabe: [`tasks/passung-filament.md`](tasks/passung-filament.md). **Stand:**

- **Bewährt (r10):** Mulden-Spiel 0,15 (0,10 zu fest, 0,20 wackelt); Kassette V1RS Spiel im Schacht **0,13** und Buchsentasche **10,46 × 2,84 × 14,40** (K5). Werte in `current.md`, Abschnitt 2g.
- **Umgesetzt, ungedruckt (Commit 0009967):** Platte mit `OUTLINE_CLR_T` 0,15, `HOF_CLR_T` 0,15, `ZUSCHNITT_CLR_T` 0,10, Gebäude je Naht 0,1 mm auseinander, Platte 115,63 × 220,90; Gebäude-STL unverändert. `plug.colour`, HTML-Seiten und Unterkasten nicht neu erzeugt.

| Prio | Aufgabe | Bedingung |
|---|---|---|
| 1 | Spiel 0,13 und Tasche 10,46 × 2,84 × 14,40 in die echten Kassetten (`variants.kassette`, V1RS) und den Gebäude-Generator (`plug/buildings.py`) übernehmen, Gebäude neu bauen (`plug.buildings`, `plug.colour`) | **erledigt 2026-10-19** (auf main `2531ac3`: `plug.filament.kassetten`, `variants.kassette` mit `schlank`/`enger`/`flacher`, Gebäude neu gebaut); v4 und V2R mit dem neuen Spiel ungetestet |
| 1 | Neue Steckplatte (0009967) drucken; Prüfung: sitzen die bestehenden beigen Gebäude (Fase 2,0) in den 0,15er Mulden gleich gut wie der Probefuß (Fase 4,0)? Hof-Einsatz mit 0,15 (ungetestet) | Nutzer druckt |
| 1 | ~~Entscheidung Fuß-Fase 4,0 gegen 2,0~~ | **erledigt**: Gebäude auf main mit 4,0 neu gebaut (`2531ac3`); Sitz in den 0,15er Mulden zeigt der Plattentest |
| 2 | ~~Schachttiefe 0,35~~ | **erledigt** (`SHAFT_EXTRA_T` 0,35 auf main, `2531ac3`) |
| 2 | Entscheidung Naht Paulinum/Neues Augusteum: Wand 0,70 (Zahn im Schlitz) oder Zuschnitt dieser Naht auf 1,1 für 0,80 | Nutzer |
| 2 | Eckaussparung Nordwest trifft laut Konzept das Fach (210 mm²; Zwischenspeicher `plug/scale1176/underside_1300.json` war veraltet, neu gerechnet): prüfen | vor dem Unterkasten-Druck |
| 2 | Flussraten-Kalibrierung je Filament (Nutzer, läuft), Messplättchen T4 erzeugen, Slicer-Kompensation je Farbe eintragen | Nutzer |
| 3 | Kassetten v4 (Hörsaal) und V2R (Hochhaus) mit dem neuen Spiel testen | nach Übernahme |

Die Abschnitte „Passung bei anderen Filamenten (Plan Schritt 1)“ und „VORGABE DES NUTZERS … r8“ darunter sind **überholt** (Spiel 0,15 ist bewährt und im Code).

## Passung bei anderen Filamenten (2026-10-19, Plan Schritt 1, wartet auf Abnicken) — überholt durch r10

Rückmeldung des Nutzers: Platte grau, Gebäude beige (Hörsaal-, Seminar-, Institutsgebäude) und eine Kassette quer (V1RS, beige) gedruckt. **Gebäude passen nicht mehr in die Mulden** (Hörsaal nur mit viel Kraft), **beige Kassetten passen nicht mehr in die beigen Gebäude**; die Dupont-Buchsen passen weiter gut in die Kassetten. Plan: `plug/filament/plan.html` (Artifact in `STATUS.md`): Filament kalibrieren statt zwei Dateisätze, Mulden-Spiel 0,15 bis 0,25 an einem Mulden-Block (T1, Institutsumriss, die vorhandenen beigen Gebäude sind die Lehre), schlankere Kassetten (T2, Spiel im Modell 0,12 bis 0,20), Messplättchen je Filament (T4), Stumpf (T3) als Eingangsprüfung neuer Farben. Offene Rückfragen und Entscheidungskarten K1 bis K7 stehen auf der Seite. Die Vorgabe 0,15 (r8) bleibt gültig.

## VORGABE DES NUTZERS für den nächsten Probedruck (2026-10-17, r8) — erledigt in r10 (0,15 bewährt, `OUTLINE_CLR_T` 0,15)

**Beim nächsten Probedruck mit Gebäuden in der Steckplatte das Spiel 0,15 mm je Seite testen** (nicht 0,10). Grund: r8, Hochhaus-Stummel mit 0,10 geht nur mit Kraft hinein und sitzt sehr fest (Fase 2,0 und Kassette V2R waren gut). Die gedruckte Platte hat Spiel 0,10; ein Stummel mit 0,15 bekommt den Umriss 0,05 mm je Seite kleiner (oder die Platte wird mit `OUTLINE_CLR_T = 0.15` neu gebaut). `OUTLINE_CLR_T` bleibt 0,10, bis der Test bestätigt; danach in `params.py` und `scale.md` umstellen, Gebäude und Platte neu bauen. Einzelheiten: `rounds/r8_passform_hochhaus/summary.md`, Lehre L43.

Folge aus r8 (erledigt 2026-10-17): Alle sechs Gebäude-STL in `stl/steckmodul_campus/gebaeude/` sind mit Fuß-Fase 2,0 neu gebaut (`python3 -m plug.buildings`). Beim Paulinum schnitt die Fase die Rohrwand ab und der Innenring der Fase ragte in den Schacht (Kollision 33,6 mm³ schon mit dem alten Grundriss, Wand 1,2 mm um die Kassette, nur 0,01 mm vom Rand). Jetzt entfällt die Fase samt Innenring auf dem Randstück vor dem Rohr, wenn Schacht und Rand näher als Fase plus Wand (2,8 mm) liegen (`plug/buildings.py`, `nah`, Eintrag `fase_entfaellt_mm2` in der JSON; nur das Paulinum, 280 mm² Randstreifen). **Ungetestet:** Einführen des Paulinums ohne Fase auf diesem Stück (die Mulde hat oben keine Fase); beim nächsten Probedruck mit dem Paulinum beobachten.

## Testdruck Unterkasten (Batteriefach): „sieht ok aus“ (Nutzer, 2026-10-18)

**Rückmeldung des Nutzers nach dem Druck: „Testdruck sieht ok aus“, ohne Einzelwerte (kein Testbogen, keine Maße zu Distanzplatte, Schalter, Faden); Einzelheiten bei Bedarf nachtragen.** Stand davor: Der Nutzer druckte `stl/steckmodul_unterkasten/` und testet es (Runde noch ohne Nummer, Eintrag unter `rounds/` folgt mit der Auswertung).** Teile: `U_unterkasten.stl`, `U_oberplatte.stl`, `U_distanz_3_4/3_6/3_8.stl` (Distanzplatte 20 × 20, klemmt die Powerbank). Zu prüfen: Kasten und Oberplatte passen aufeinander (Zapfen in den Zapfenlöchern, Auflage auf den Stützen), Powerbank liegt im Fach und trifft das Fenster, welche Distanzplatte klemmt (3,6 zuerst; 3,8 bei Spiel, 3,4 bei Pressung), Hauptschalter sitzt in der Westwand, Faden an den vier Ecken durch Aussparung und V-Kanal, Fenster oben offen ohne Brücke sauber, ESP32-Fläche 64 × 40,5 reicht. Nicht gemessen: Powerbank-Dicke (Zuschlag 0,2 aus r5 ist eingerechnet), ESP32-Board. Noch kein Testbogen; wenn der Nutzer Ergebnisse schickt: erst zusammenfassen, dann Logbuch, `lessons.md`, `current.md`, STATUS nachziehen.

## Offene Folge aus r9 (Hauptschalter, 2026-10-17)

Probeteil T2 (Loch 13,7 × 9,0, Wand am Loch 1,2) ist bewährt (`current.md`, Abschnitt 2f). Loch und Tasche sind im Unterkasten-Generator (`build_concept.switch_cut`, Westwand, y = 40 aus `SW_Y`, geprüft mit `python3 -m plug.power.check_switch`); der Unterkasten selbst ist noch nicht als STL gedruckt. Offen: Hakenspanne an der 13-mm-Seite nachmessen (die Brücke über dem Loch war in T2 sauber); Verdrahtung Powerbank → Schalter → INA226 (`docs/wippenschalter-kcd11.md`).

## Vorgabe 2026-10-20 (Batteriefach Stand 8)

- **Gänge 1 mm flacher: 8 × 4** (nach dem Druck von K4 mit 8 × 5), **Gangfase innen**, Wände 0,8, Decken über Aushöhlungen 0,48 (3 Lagen × 0,16), **keine Fase unten** an den Mündungen, Knopfraum nicht beschneiden, **1 mm Luft über dem Knopf** (Raum Ø 25 × 13,0 frei). Knopf Ø 22 × 12 ist eine Annahme, nachmessen.

## Vorgabe 2026-10-19 (Batteriefach Stand 8)

- **Befestigung mit Heißkleber** statt Fäden: Kasten auf den Hut, im Zweifel Platte auf den Kasten. Fäden und Ösen entfallen (Eckaussparungen im Kasten, Fadentaschen in der Platte); die Abschnitte zu Fäden weiter unten sind damit überholt.
- **Knopf des Huts** in der Plattenmitte: **Ø 22 × 12,0 hoch (Annahme, vom Nutzer zu bestätigen**; erste Nachricht „ca. 1,2 cm“, vorher als 1,2 mm gelesen). Die Kordel 3 × 5 kommt unten seitlich am Knopffuß heraus (Nutzer, `KORDEL_ANSATZ_OBEN = False`) und läuft in acht Gängen 8 × 5 nach außen. Über dem Knopf eine **Erhebung**: Raum Ø 25 × 12,2, 45°-Anstieg ab 8,7 mm vor dem Knopf, Decke Ø 20 bei 14,7, Plateau Ø 28 bei 15,9. **Steckerraum 6 mm**, Powerbank am Platz von Stand 7 auf Plateau und drei Auflagen: Kasten 34,7 (mit Platte 49,3, ca. 128 g). Gangfase in zwei Varianten (`GANG_FASE_MODUS` innen/außen, Vorschlag außen). Nächster Druck: **K4 F-außen** (`stl/steckmodul_kordelprobe/`), dabei Knopfhöhe messen. Plan: `plug/power/plan_kasten8.html`.

## Geklärt (2026-10-16)

- **Platte B** ist die getestete Platte (W, S, D); die Druckmängel gehören zu Platte A. Basis ist B.
- **Schrauben entfallen**; Deckel und Platte bekommen Löcher für den Faden, der beides andrückt.
- **Buchsen nachmessen entfällt**; das Delta reicht (Tasche mindestens 0,1 über 14,45).
- **Keine Schrauben** (feste Vorgabe): die Platte wird an einen Doktorhut genäht, vier Fäden an den Ecken.
- **Faden (Planungs-Zwischenstand, nicht abgenickt):** tritt **nicht an der Oberseite** aus. Unten eine breite Einführung (Trichter); der Faden läuft von unten
  **schräg durch eine Lasche** der Platte und **schräg nach unten wieder heraus** (V-Kanal an den vier Ecken). Der Plan Steckprobe 2 setzt das so um: Kanal Ø 2,2 mit 0,15 mm
  Überhang je Schicht (Platte-B-Böschung, etwa 53° zur Waagerechten), Scheitel 3,4 mm über der Unterseite, Trichter Radius 2,0, Mitte x ±15,6, Wände mindestens 1,4 mm,
  Ausschnitte im Deckel über den Trichtern (`plug/testcase/build_plan2.py`, `PROP`; Eintrag `rounds/r4_steckprobe2/summary.md`). Die Einzelheiten dürfen sich noch ändern.
- **Name „Steckprobe“** passt (bestätigt).

## Offene Fragen an den Nutzer (im Plan Steckprobe 2 als Entscheidungskarten)

1. **Körper der Winkelleiste kippt** (Platte B, ohne Halt von unten): Rippen an der hinteren Taschenwand, Heißkleber oder beides (Karte K)?
2. Deckel-Ausschnitte an den Ecken (Karte F) und Stempel nur als Anschlag mit 1,2 mm Luft (Karte D); alle Karten warten auf das Abnicken.

### Umgestellt (2026-10-16): halbe Nische und kein Stößel

`plug/power/params.py`: `NICHE = dict(w=12.0, l=6.46)` (12 × 9,5 mm ab der Körpertasche, eine Öffnung, keine Stege), `ROD` und die Taste aus `PB_PORT_V` entfernt; `build_concept.dock_windows` liefert eine Öffnung, `fach_parts` ohne `rod`; Konzeptseite, Plan und Testbogen der Fachprobe ohne Stößel und ohne Schablone. `plug/testcase/build2.py` baut mit der neuen Nische (der gedruckte Stand r4 liegt eingefroren in `rounds/r4_steckprobe2/`). Fadenführung bleibt unverändert (anderer Chat, wird später gemerged).

## Festgelegt am 2026-10-16 (Planung): siehe [`scale.md`](scale.md)

Maßstab **1:1300** (Platte 115,6 × 220,8 mm), Mulde überall 4 mm tiefer (F 14,2, Platte 20,2), Kassette v4 (Paulinum, Neues Augusteum, Hörsaal), V1RS (Seminar, Institut), V2R (Hochhaus). Offen: V1RS und V2R sind Konzepte ohne Test, Fuß 14,2 mm ungetestet, Hof bei 1:1300 neu rechnen. Steckprobe 2 muss die tiefere Mulde (14,2 mm) prüfen, wenn sie gedruckt wird.

**Ungetestet:** alle Planwerte der Festlegung stehen mit Test in [`scale.md`](scale.md), Abschnitt „Ungetestete Planwerte“; `plug/parts.py` erst nach bestandenem Test ändern.

**Umgesetzt (Planwerte, Steckplatte `python3 -m plug.campus`):** siehe `scale.md`, Abschnitt „Umgesetzt“. **Stand 2026-10-17: Rückmeldung zum Druck eingetragen (`rounds/r7_steckplatte/`), Fase oben 1,5, Mulden-Einführfase 0,5, Schrift erhaben als Vorschlag umgesetzt, 3D-Seite zur Prüfung.** **Stand 2026-10-16 abends: Steckplatte auf flache Unterseite umgestellt (14,6 mm, Pin-Löcher, keine Docks im Körper), siehe `scale.md`, Abschnitt „Umstellung auf flache Unterseite“.** Offen: Gebäude mit Fuß und Schacht, Kabelführung zwischen den Docks.

**To-do (anderer Chat):** Gebäude im Generator als Hohlkörper bauen (Aufnahme für die Kassette, Lichtfenster); heute Vollkörper.

### Befund Lösungsfindung 1:1300 (`plug/power/layout.html`, 2026-10-16)

Mit der halben Nische (12 × 9,5 mm) gibt der Generator bei 1:1300 an der Südkante **4 freie Docks** (Paulinum, Neues Augusteum, Hörsaalgebäude, Institut) und Elektronik 60 × 35; vorher mit 24 × 19 mm waren es 3 und 50 × 30. Offen bleiben Seminargebäude und City-Hochhaus: die Kassette (Schacht 13,62) ist zu breit; das Seminargebäude passt ab etwa 10,6 mm Schacht, das Hochhaus selbst bei 10,0 nicht. Weitere Hebel in der Seite: Ohr (Hut 240 breit, Platte 114), zweite Etage (+14 mm), kürzerer Steckerraum.

### Idee des Nutzers: ganze Fläche unter der Platte als Steckerraum (2026-10-16, nicht entschieden)

Statt Tasche, Schlitz, Nische, Steg und Rippen: Leiste nur 1 mm tief in der Platte, 1 mm ragt unten heraus, darunter ein durchgehender Raum (Powerbank, Stecker, Adern). Bewertung: geht, vereinfacht den Aufbau stark und lässt die Powerbank auch unter den Docks liegen (Docks begrenzt nur noch die Kassette). Luft über der Powerbank nicht 1 mm, sondern etwa 3,4 mm (1,0 Leiste + 0,6 Spiel + Lötende und Draht), Gesamthöhe dann 29,4 statt 27,0 mm (Oberplatte 11,6 statt 12,6). Offen: Halt der Leiste (flache Tasche mit Rippen, Heißkleber), Höhe der Elektronik daneben. Die Drähte brauchen **keine Führung** (Nutzer: alles ist ein Prototyp). Zeichnung `vorschau/steckmodul_power/steckerraum_idee.png`.

Ergänzung (Nutzer): eine **Auflage für die Lötenden** einplanen, damit Lötenden und Kunststoffkörper gemeinsam flach aufliegen (wie die bewährte Stufe aus r2 D). Gedruckt mit **vollflächigem Support unten, ausgenommen der Auflage-Steg**. Unsere Lesart: Oberplatte mit der Unterseite auf dem Bett; die 1 mm tiefe Tasche und die Rille für die Lötenden sind der einzige Hohlraum unter dem Muldenboden (0,4 mm) und werden vom Support gefüllt, der Steg bleibt massiv. Geklärt (Nutzer): der Steg ist eine **Stufe auf der Unterseite der Platte, wo die Gebäude eintauchen**, die Auflage für die Lötenden der Stiftleisten wie schon früher (nicht im Unterkasten).

**Test-Dock gebaut, wartet auf den Druck (`stl/steckmodul_testdock/`, Testbogen `plug/power/feedback_dock.html`; Plan abgenickt vom Nutzer: „ok, passt“). Prüfbericht: alle Teile dicht, keine Kollisionen, kein Support nötig, ≈ 10 g.** Plan `plug/power/plan_dock.html`, Stand nach der Vereinfachung des Nutzers (2026-10-16): alles auf gleicher Höhe, keine Tasche, keine Stufe, kein Support.** Mini-Oberplatte 40 × 50,4 × 10,6 mm mit Mulde und vier Pin-Löchern, flache Unterseite; der Körper der Leiste (2,0) liegt unter der Platte und wird aufgeklebt (Sekundenkleber, dann Heißkleber testen); Draht und Lötstelle bis etwa 2,9 unter der Platte; Luft zur Powerbank 3,5 (Gesamthöhe etwa 27,9 mm, wie vorher); zwei Füße-Sätze 3,5 und 2,5 mm mit Zapfen 2,5; Gebäude und Kassette aus Steckprobe 2. Hauptrisiko: der Kleber hält das Aufstecken (Druck zieht die Leiste von der Platte weg).

## Passform-Runde Hochhaus (r8, gedruckt und ausgewertet, 2026-10-17)

Siehe `rounds/r8_passform_hochhaus/summary.md`: Fase 2,0 und Kassette V2R gut, Spiel 0,10 zu eng bei großem Umriss, nächster Test mit 0,15 (Vorgabe oben).

## Priorität 1 neu: Steckprobe 3 (r6, nach r4 und r5)

Der Aufbau passt bis auf vier Dinge. Vorschläge (nicht abgenickt, zuerst als Plan mit Grafiken):

| Thema | Änderung | Grund |
|---|---|---|
| Faden-V | **eigene Aufgabe für einen anderen Chat**: `plug/logbook/tasks/faden-v-ueberarbeiten.md` (nicht in Steckprobe 3 dieses Chats); bis dahin Kanal mindestens 1 mm weiter, Support erlaubt | r4 F: Faden kommt nicht durch den untertauchenden Kanal |
| Kabelnische | **eine** Nische ohne Fenster und Stege, **halb so groß in beide Richtungen: 12 × 9,5 mm** statt 24 × 19 mm (Nutzer, 2026-10-16); mit Support gedruckt | r4 W |
| Zapfen | Höhe 2,5 statt 1,5, Löcher entsprechend tiefer | r4 U |
| Schachttiefe | Kassette + 0,35 | r4 E |
| Support | im Plan ausweisen, wo Support nötig ist; Brückenregel L04 gelockert | r4 W |
| Unklar aus r4 | Rippen und Steg an der Winkelleiste, Fase 0,5, Elefantenfuß: im Testbogen ausdrücklich abfragen; ZIP-Version abfragen (L35) | r4 leer |

Fachprobe Powerbank (r5) ist gedruckt und ausgewertet: Luft über der Powerbank 0,8 statt 0,6 (`PB_CLR_Z`), Deckplatte wackelte, Zaun nur als Ausschnitt, übrige Punkte ohne Rückmeldung (`rounds/r5_fachprobe/summary.md`).

**Offen nach r5 (Priorität 2, vor oder mit der großen Platte):**

| Thema | Idee | Bedingung |
|---|---|---|
| Dicke der Powerbank | mit der Schieblehre messen und in `PB_T` eintragen (dann `PB_CLR_Z` prüfen) | Nutzer |
| Fachprobe wiederholen? | nur mit vollem Zaun und Luft 0,8, Testbogen fragt Zaun, Seitenspiel, Länge, Kabelkanal, Fenster, Steckerraum, Wackeln einzeln ab und die ZIP-Version (L35, L38) | Nutzer entscheidet, ob nötig |
| Halt der Oberplatte | Zapfen oder Faden, damit sie nicht wackelt | Plan der großen Platte |
| Konzeptseite | Stößel und Taste entfernt, Seite mit Luft 0,8 neu veröffentlicht (Version 6) | erledigt (2026-10-16) |

**Aufgaben für andere Chats:** `plug/logbook/tasks/` (Faden-V überarbeiten; `fachprobe-auswerten.md` ist erledigt, r5).

## Priorität 1 (erledigt): Steckprobe 2 (r4)

Ziel: die in r3 gefundenen Mängel beheben und den Aufbau so weit bringen, dass er mit einem Controller leuchtet.

| Thema | Änderung | Grund |
|---|---|---|
| Kassette | Taschenhöhe 14,55 bis 14,60 (Delta aus r3 K, kein Nachmessen); die Variante mit 14,15 entfällt; Gesamthöhe so anpassen, dass die Schachttiefe passt | r3 K: Buchse steht minimal heraus; 14,15 passt keine Buchse |
| Gebäude | nur Schacht A (0,06 durchgehend), Schachttiefe + mindestens 0,3; Variante B (Passzone) entfällt | r3 E: A Sitz 3, B Sitz 5; Kassette ragt 0,2 heraus |
| Fase | Bettkanten und Schachteingang 0,5 statt 0,4 | leichter Wulst bleibt |
| Platte | B (Trichter, ohne Support) weiterentwickeln; Kabelraum unter den Lötenden so frei wie möglich (kein Trichter-Anschnitt im Bereich der Kabel); V-Kanäle für den Faden an den Ecken (siehe oben) | r3 W: zu wenig Platz hinter den Lötenden |
| Halt der Winkelleiste | Körper darf nicht kippen: Tasche und Rippen überprüfen (Körper in der +1,5 langen Tasche hat zu viel Spiel?), Alternative Heißkleber | r3 W: Körper kippt oder wackelt |
| Deckel und Befestigung | ohne Schrauben: Ausschnitte im Deckel über den Trichtern, Faden durch den V-Kanal der Platte; Stempel entfallen oder bekommen mehr als 1 mm Luft beim Aufsetzen | r3 W: Deckel passt nicht, Stempel stoßen an; Schrauben nicht vorhanden |
| Ösen | entfallen: die V-Kanäle mit Trichter übernehmen die Aufgabe (Faden von unten hinein, schräg durch die Lasche, nach unten heraus) | Doktorhut, vier Fäden an den Ecken |
| Funktionstest | Adern und LED bestücken, Controller anschließen (Schritt L im Testbogen): Licht, Wackeln, Zehnfach-Abziehen | r3 L: noch nicht getestet, Adern biegen rund |
| Testbogen | Feld „Luft unter der Buchse“ ersetzen durch ja/nein; Feld „Platte A oder B“ und Formular-Version aufnehmen | L24, L25 |

### Fachprobe Powerbank gebaut, wartet auf den Druck (`stl/steckmodul_fachprobe/`, Testbogen `plug/power/feedback_fach.html`)

Abgenickt: Variante B (nur Anschlussende, 67,9 × 74,8 × 14,4 mm, ≈ 26 g), Deckplatte 2 mm, **ohne Schablone, Taste und Stößel** (Nutzer: die Taste braucht es nicht, später fragt der Mikrocontroller alle 5 s kurz Strom ab). Der Ladeanschluss muss durch das Fenster erreichbar bleiben, die USB-A-Buchse samt geradem Stecker ist eingeplant. Kabelkanal nur 4,4 mm frei neben dem Zaun (Kabel bis etwa 4 mm). Im Konzept (`plug/power/concept.html`) ist der Stößel inzwischen entfernt (nach r5).

### Steckprobe 2 gebaut, wartet auf den Druck (Powerbank-Konzept Stand 5, 1:1300)

Die große Platte ist als Oberplatte 12,6 mm über einem hohlen Unterkasten 14,4 mm geplant (`plug/power/concept.html`, PLAN Kapitel 6; Maßstab 1:1300 vom Nutzer
gesetzt, Kassette passt dort in 4 von 6 Gebäuden, Dock frei an 3). Der Nutzer hat den Bau freigegeben: Steckprobe 2 (STL, README, ZIP, Prüfbericht in `stl/steckmodul_testcase2/`, Testbogen `plug/testcase/feedback2.html`) im Zwei-Lagen-Aufbau drucken (Mini-Oberplatte 12,6 + Mini-Unterkasten mit
Steg-Anschlag 1,2 Luft, Zentrierzapfen Ø 4 / Loch 4,3, Kabelnische hinter den Lötenden, **zwei Faden-V mit 53° und 40°**, Gebäude mit Fußfase 0,8); eine
**Fachprobe Powerbank** ist **nicht** mitgebaut (eigene Runde, siehe oben). Das Kassetten-Redesign läuft in einem separaten Chat und kann die Kassette ersetzen. Werte: `plug/power/params.py`.

## Kassetten-Varianten V1/V2 (Plan `plug/testcase/plan3.html`, wartet auf das Abnicken)

Register und Maße aller Varianten: [`cassettes.md`](cassettes.md). Fit in die Gebäude zurückgestellt, bis der Maßstab feststeht. Danach: Probedruck (Kassetten V1/V2 plus Mini-Gebäude auf dem bisherigen L-Fuß), Werte nach `params.py`, STL, Testbogen. Offene Punkte: Adernweg V1, Blattdicke V2, Licht (Hotspot im schmalen Gebäude), Anschlagleiste im Schacht.

## Hohlkörper-Gebäude (beschlossen und im Generator umgesetzt, Plan `plug/hollow/plan.html`)

Beschlossen (2026-10-16): Wand und Dach 0,8 mm, unten offen, keine Lichtfenster; Decke glatt, wo sie höchstens 10 mm frei spannt, sonst 45°-Gewölbe (für alle Gebäude, bei denen es nicht gut passt); Nachtrag: das Gewölbe ist eine glatte 45°-Fläche von den Wänden bis zum First, ohne Stufen, Kanten nach unten, Brücke oben oder Taschen darüber (`hohl.FIRST = 0`; mit 10 statt 0 bliebe oben ein 10-mm-Streifen, siehe Tabelle im Plan); Ausgabe zusätzlich in `einzeln_hohl/` (alle Quellen und Maßstäbe, `--no-hohl` lässt sie weg); Fuß und Kassette getrennt (kommen aus `plug/`); Licht wie die Kassette liegt; Farbe **beide Versionen**: STL einfarbig hell und `_farbig.3mf` mit Fassadenfarben.
Umsetzung: `hohl.py` (Verfahren), `generate.py` (`hohl_models`, `colour_hohl`), `fassaden.colour_mesh(ref=…)`; Studie, Ansichten (`views.py`, Bilder `vorschau/hohl/`) und Plan in `plug/hollow/`.

Offen:
1. **Lichtprobe** Wandstreifen 0,4 / 0,8 / 1,2 mit LED (Schritt L in Steckprobe 2): bestätigt oder ändert `hohl.WAND`.
2. **Brückenprobe**: Mini-Gebäude mit Decke 10 mm Spannweite und einem Gewölbe, im selben Druck wie die Lichtprobe; die Gewölbe sind ungedruckt.
3. **Fuß und Kassette in der Schale**: als Prototyp gebaut (2026-10-17, `python3 -m plug.buildings`, siehe `scale.md`, Abschnitt „Steckbare Hohlgebäude“); Gewölbe überarbeitet (Rohr als Stütze, Spalten gefüllt, zusammen −15 %), Füllungs-Empfehlung Gyroid 10 % dort; ungedruckt.
4. Licht in hohen Gebäuden (City-Hochhaus 96 mm, Paulinum 39 mm) und durch farbige Wände: ungetestet.
5. Slicer prüfen: 0,8-mm-Wände, `_farbig.3mf` mit bemalten Dreiecken (Innenflächen einfarbig).

Zahlen (Laserscan 1:1500, glattes Gewölbe bis zum First): alle sechs Hohlkörper dicht; freie Spannweite vorher bis 30 mm (Hörsaalgebäude), nachher höchstens etwa 10 mm; vom Hohlraum bleiben Paulinum und City-Hochhaus 100 %, Institutsgebäude 91 %, Seminargebäude 83 %, Neues Augusteum 79 %, Hörsaalgebäude 59 % (mit 10-mm-Streifen oben: 100 / 99 / 100 / 92 / 80 %).

## Priorität 2

| Thema | Idee | Bedingung |
|---|---|---|
| Muldenboden dünner (0,3 oder 0,2) | Nutzer: „wenn die Stärke es hergibt, Boden minimal dünner“; E steigt, das Gebäude zieht noch leichter ab | erst wenn die Brücke sauber druckt; eine einzelne Schicht ist ein Risiko |
| Muldenboden als **Einsatz** | 0,2 bis 0,4 mm dünnes Plättchen mit vier Löchern, flach auf dem Bett gedruckt (saubere Löcher, keine Brücke), von unten in die Platte gelegt oder geklebt | löst Brücke und Löcher auf einmal; Halt gegen Zug noch zu planen |
| Platte im echten Boden | Unter der Winkelleiste maximal Platz für Kabel; Support oder zweiteilige Platte statt Trichter | nach Steckprobe 2 |
| Elefantenfuß | Fase 0,6 oder kleine Kompensation im Slicer | wenn 0,5 nicht reicht |

## Priorität 3

- **Offen nach der Hof-Änderung (17.10.):** Powerbank-Seite (`plug/power/concept.html`, `plug.power.build_concept`) prüfen und neu erzeugen: Der Gang im Süden macht die Steckplatte bis zu 2,35 mm höher als der Rand, die Unterseite ist unverändert, aber Konzeptseite und Artifact zeigen noch den alten Hof. Ebenso `plug/views/campus/view.html` (Steckplatte Änderungsvorschau) neu erzeugen und veröffentlichen. Komplettmodell und Grundplatte aus `generate.py` haben Gang und Treppen nicht (Hof endet dort mit Stufe 2,35 mm), bei Bedarf nachziehen.
- **Steckprobe 3 (Reserve-Druck, wenn der Drucker frei ist; Nutzer: nicht so wichtig, weil schon viel geklappt hat):** Kassette v4 in Mulde 14,2 mm (Führung, Kippen); Hof-Einsatz bei 1:1300 mit Einführfase und 0,8-mm-Stämmen (1 mm als Rückfall), Trennwand 0,8 mm (`HOF_WALL_T`), Gang im Süden auf Terrassenhöhe mit Treppen in der Platte (`hof_einsatz_1zu1300.stl`, `steckplatte_1zu1300.stl`; Vergleich `plug/hof/page.html`); V1RS (Seminar, Institut) und V2R (Hochhaus) als Probestücke mit Adernweg, Verkettung und Streifendicke 2,2 mm; Paulinum mit v4 (0,9 mm Wand) gegen V1RS. Plan als HTML erst, wenn der Nutzer den Druck anstößt.

- Federzunge in der Mulde: bei CLR 0,10 vielleicht unnötig; „wenn es sich anbietet, mitdrucken, keine Priorität“.
- Heißkleber als Ausweg dokumentieren: Klecks Heißkleber auf die Winkelleiste, Stempel weglassen oder nachträglich abschneiden.
- Nach bewährter Steckprobe: Werte in `plug/parts.py` übernehmen, Probestück und Institutsgebäude umbauen (kein Schieber mehr, Einpress-Kassette, Podest), Seiten neu veröffentlichen.
- Licht durch die Wand (Lichtfenster bzw. dünne Wand des Hohlkörpers) mit LED prüfen, sobald die LED sitzt.
- Paket `plug/testcase/` in `plug/steckprobe/` umbenennen (nur, wenn gewünscht).
