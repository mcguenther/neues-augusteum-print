# Bewährter Stand (nach Steckprobe 2, 2026-10-16)

Status: **bewährt** = im Testbogen mit „passt“ bewertet · **vorläufig** = funktioniert, mit Einschränkung oder noch nicht ganz belegt ·
**verworfen** = getestet, gestrichen · **offen** = nicht geklärt. Belege stehen in `rounds/`. Werte im Code: `plug/testcase/params.py`
(neue Sollwerte), `plug/parts.py` (Kaufteile und alte Werte; wird erst nach der Steckprobe umgestellt).

## 1. Aufbau in einem Satz

Ein Gebäude hat einen Fuß, in dessen Schacht eine **Kassette** (Dupont-Buchse, Adern, LED-Streifen) von unten eingepresst wird; der Fuß taucht in die
**Mulde** der Grundplatte, deren Muldenboden die Pins der abgewinkelten Winkelleiste durchlässt. Kein Schieber, keine Trichterplatte: die Pins gehen vom
Muldenboden direkt in die Buchse.

## 2. Werte

| Größe | Wert | Status | Beleg | Code |
|---|---|---|---|---|
| Körper der Winkelleiste (Höhe, Dicke) | 2,0 mm | bewährt | r0 Passprobe 4/5, Probestück | `HDR_BODY`, `HDR_T` (`parts.py`) |
| Stufe für das Lötende | für Körperhöhe 1,8 (2,0 und 1,8 liegen flach, 1,6 nicht) | bewährt | r2 D | `STEP_H_T` |
| Körpertasche zum Lötende verlängert | +1,5 mm | bewährt in der Passprobe, in der Platte offen (Körper kippt) | r2 D, r3 W | `BODY_EXT_T` |
| Pinloch | 1,4 mm, Fase beidseitig (0,3; im 0,4-Boden 0,15) | bewährt | r0, r1 | `HOLE` |
| Muldenboden (CEIL) | 0,4 mm; Durchgang stabil, Gebäude zieht sehr leicht ab | vorläufig | r2 K, r3 S, D | `CEIL_T` |
| Einstecktiefe E | 5,28 mm (HDR_UP 5,68 − 0,4), Durchgang stabil gemessen bis E 5,08 | vorläufig | r2 K, r3 S | `dims()["E"]` |
| Trichterplatte / Schieber | entfällt | verworfen | r1 N, r2 K | – |
| Schacht für die Kassette | 0,06 je Seite, **durchgehend**, eingepresst: Sitz 3, hält beim Schütteln, Herausdrücken nur mit kräftigem Druck | bewährt | r3 E (Gebäude A) | `KASS_CLR_T` |
| Schacht mit Passzone 8 mm (0,06) und Entlastung 0,20 | Sitz 5, lose | verworfen | r3 E (Gebäude B) | `KASS_RELIEF`, `KASS_FIT_LEN` |
| Schachttiefe | Kassette ragt nach dem Einpressen noch etwa 0,2 mm unten heraus: Schachttiefe = Kassettenhöhe + mindestens 0,3 | offen (Korrektur nötig) | r3 E | `building()` |
| Mulde (Fuß in der Mulde) | CLR 0,10 je Seite, L-förmiger Fuß, nur eine Lage, kein Wackeln | bewährt | r2 FM, r3 M | `MULDE_CLR_T` |
| Buchsentasche | 0,20 Spiel je Seite, ohne Rippen, Sitz 3 | bewährt | r1 R, r2 C, r3 K | `SNUG2` (`series2.py`) |
| Taschenhöhe der Kassette | **14,45 (Luft 0,45) passt**, die Buchse steht aber noch etwa 0,1 mm unten heraus: Tasche auf mindestens **14,55**; 14,15 passt keine Buchse (verworfen) | vorläufig | r3 K | `HSG_TOL_SAFE` |
| Höhe der echten Buchse | etwa 14,5 bis 14,6 mm; Nachmessen entfällt, das Delta (Tasche mindestens 0,1 über 14,45) reicht; Nennwert 14,0 stimmt nicht | bewährt als Delta | r3 K | `HSG_H` |
| Buchse bündig einsetzen | Buchse mit der Steckseite auf einen flachen Tisch, Kassette von oben darüberstülpen | bewährt | r3 K | – |
| Podest der Kassette | Oberseite 2,5 mm über der Tasche (0,5 + 2,0), Rundung R 2,5; Adern lassen sich rund biegen | vorläufig (Licht nicht getestet) | r3 L | `PODEST_T`, `FILLET_T` |
| LED-Fläche | flach, ohne Tasche; 10-mm-Streifen passt, 12 mm passt nicht durchs Fenster des Mini-Gebäudes | vorläufig | r2 C, r3 | – |
| Pins treffen die Buchse ohne Trichter | ohne Kraft, alle vier gleichzeitig; Gebäude sitzt danach fest | bewährt | r3 S | – |
| Elektrischer Durchgang | alle Kontakte vorhanden („durchgepiepst“) | bewährt | r3 S | – |
| Fase an Bettkanten und Schachteingang | 0,4 mm; ein leichter Wulst bleibt | vorläufig, nächster Test 0,5 | r2, r3 | `EF_CH_T`, `ENTRY_CH_T` |
| Beschriftung | erhaben 0,5 bis 0,6 mm plus Rang als Kerben, gut lesbar und fühlbar | bewährt | r2, r3 | `series2.emboss_*` |
| Winkelleiste im Dock | Pins treten gerade aus; **Körper kippt oder wackelt** | offen | r3 W | `plate()` |
| Platz hinter den Lötenden | für diese Probe zu wenig (Fasen und Trichter); im echten Boden soll darunter so viel wie möglich frei sein | offen | r3 W | `LOETRAUM_Y0`, `SLOT_END` |
| Deckel mit Stempeln | passt nicht (Stempel stoßen beim Aufsetzen an, mehr als 1 mm Luft nötig); Konzept neu | verworfen | r3 W | `lid()` |
| Befestigung | **keine Schrauben** (fest); Platte wird an einen Doktorhut genäht, vier Fäden an den Ecken. Fadenführung als Planungs-Zwischenstand: nicht oben austretend, breiter Trichter unten, schräg durch eine Lasche, schräg nach unten heraus (V-Kanal, Plan Steckprobe 2) | beschlossen (keine Schrauben), Ausführung Zwischenstand, ungetestet | r3 Nachtrag, r4 | `build_plan2.PROP`, `lid()` |
| Muldenboden und Kabelraum als Brücken (Platte A, erster Druck) | Muldenboden stark durchgehängt oder Löcher zu, Decke des Kabelraums stark durchgehängt (Thick bridges an) | verworfen für den Druck ohne Support | r3 | `plate("A")` |
| Platte B (Trichter, ohne Support) | Pin-Löcher offen, Pins treten gerade aus, Kontakt vorhanden; Körper kippt ohne Halt von unten; Platz für Kabel hinter den Lötenden durch die Fasen zu klein | **Basis**, mit Mängeln | r3 W, S | `plate("B")` |

## 2b. Nach Steckprobe 2 (r4, Zwei-Lagen-Aufbau)

| Größe | Wert | Status | Beleg | Code |
|---|---|---|---|---|
| Taschenhöhe der Kassette | 14,60, alle Buchsen passen, „alles super“ | **bewährt** | r4 K | `HSG_TOL_SAFE` |
| Schachttiefe | Kassette + 0,30 gut; **+ 0,35 gewünscht** | bewährt, Korrektur + 0,05 | r4 E | `SHAFT_EXTRA_T` |
| Mulde, Fußfase 0,8, Muldenfase 1,0 | passt alles | bewährt | r4 M | `MULDE_CLR_T`, `sd.CH_F`, `sd.CH_P` |
| Stecken, Einstecktiefe E | 5,28; Pins treffen ohne Kraft, Gebäude sitzt fest, Durchgang | bewährt | r4 S, D | `dims()["E"]` |
| Oberplatte 12,6 auf Unterkasten 14,4, Auflage | rundum flach, kein Spalt, bleibt beim Aufstecken liegen | bewährt | r4 U, S | `PP.UK_*` |
| Zapfen Ø 4, Loch 4,3, Höhe 1,5 | wackelt deutlich (5); **Höhe 2,5** | verworfen (zu kurz) | r4 U | `PP.PIN` |
| Faden-V (Kanal Ø 2,2, Scheitel 3,4, Trichter R 2,0), 53° und 40° | Faden geht durch keines; Kanal mindestens 1 mm weiter | verworfen (Maße), Winkel offen | r4 F | `P.V_*`, `PP.V` |
| Kabelnische 24 × 19 mm mit drei Fenstern und Stegen | zu groß, drei Fenster unnötig; **eine Nische 12 × 9,5 mm (halb so groß in beide Richtungen)**, Nutzer druckt mit Support | verworfen | r4 W | `PP.NICHE`, `BC.dock_cuts` |
| Support | vom Nutzer erlaubt (einmal bereinigen) | Vorgabe | r4 W | – |
| Rippen und Steg-Anschlag an der Winkelleiste | keine Rückmeldung | offen | r4 W | `PP.ANSCHLAG`, `build2.top_plate` |
| Fase 0,5 an Bettkanten | kein Feld ausgefüllt | vorläufig | r4 q | `EF_CH_T`, `ENTRY_CH_T` |
| LED und Adern über das Podest | später | offen | r4 L | – |

Eingefroren: `rounds/r4_steckprobe2/steckprobe2.zip` (Stand Commit `46d1e0a`).

## 3. Maßkette (gesteckt, z = 0 Plattenoberseite)

| Größe | Wert |
|---|---|
| Fußhöhe F (Mulde) | 10,2 mm |
| Muldenboden | 0,4 mm (z −10,6 bis −10,2) |
| Oberkante Winkelleistenkörper | z −10,6; Unterkante −12,6 |
| Pin-Spitze | z −4,92 (HDR_UP 5,68 über dem Körper) |
| Buchse bündig mit der Fußunterkante | z −10,2; E = 5,28 |
| Kassette (Stand der Steckprobe 1) | 13,5 × 29,44 × 16,95; Tasche 10,56 × 2,94 × 14,45 |
| Mini-Gebäude | 24 × 38 mm (L-Fuß, Ausschnitt 3,5 × 9), 18,15 hoch (Anschlagrand 1,2) |
| Mini-Grundplatte | 38 × 52 × 16,2 mm, Deckel 2,0 |

Worst-Case: Hängt die Buchse oben an den Schultern, geht die Luft darunter von E ab (Taschenhöhe − Buchsenhöhe).

## 4. Druckeinstellungen

Bambu A1, schwarzes PLA, Düse 0,4, Schichthöhe 0,2, 3 Wände, 15 % Füllung, Thick bridges an. Ausrichtung: Kassette Tasche unten am Bett; Gebäude Fuß unten
(Schacht öffnet am Bett); Platte Mulde oben, Kabelraum am Bett; Deckel flach. Keine Brücke über etwa 10 mm.

## 5. Dateien der Steckprobe 1

`rounds/r3_steckprobe1/` enthält die ZIP (Stand `69fb76f`: 2 Kassetten v4, Gebäude A und B, Platte A mit Support, Platte B ohne Support, Deckel mit Streben)
und die Update-ZIP. Die erste ZIP (Platte nur A, erster Deckel) steht im Commit `f4a995c`. Generator: `python3 -m plug.testcase.build`.
