# Nächste Drucke und offene Punkte

Stand: nach Steckprobe 1 (r3, 2026-10-16); Plan Steckprobe 2 liegt vor (`plug/testcase/plan2.html`), wartet auf das Abnicken. Priorität 1 = nächster Druck, 2 = danach, 3 = bei Gelegenheit.
Ablauf je Runde: siehe `README.md` (Plan, Abnicken, STL, Druck, Testbogen, Auswertung).

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

## Priorität 1: Steckprobe 2 (r4)

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

## Kassetten-Varianten V1/V2 (Plan `plug/testcase/plan3.html`, wartet auf das Abnicken)

Register und Maße aller Varianten: [`cassettes.md`](cassettes.md). Fit in die Gebäude zurückgestellt, bis der Maßstab feststeht. Danach: Probedruck (Kassetten V1/V2 plus Mini-Gebäude auf dem bisherigen L-Fuß), Werte nach `params.py`, STL, Testbogen. Offene Punkte: Adernweg V1, Blattdicke V2, Licht (Hotspot im schmalen Gebäude), Anschlagleiste im Schacht.

## Hohlkörper-Gebäude (Plan `plug/hollow/plan.html`, wartet auf das Abnicken)

Gebäude im Generator als Hohlkörper mit dünner Wand (Wand 0,8, Dach 0,8, unten offen, keine Lichtfenster). Studie in `plug/hollow/` (`shell.py`, `study.py`, `build_plan.py`), noch **nicht** in `generate.py`; keine STL, keine Prototypen, solange offen ist:

1. Wandstärke 0,4 / 0,8 / 1,2: Lichtprobe mit Controller (Schritt L in Steckprobe 2), bis dahin Parameter 0,8.
2. Decke des Hörsaalgebäudes (flaches Dach, Brücke 18 mm; alle anderen höchstens 11 mm): glatt, Gewölbe 45° oder Rippe; Brückenprobe 10 / 14 / 18 / 24 mm.
3. Ausgabe: neuer Ordner `einzeln_hohl/` neben den massiven Dateien (Vorschlag) oder Ersatz.
4. Fuß und Kassette: Schale ab Plattenoberseite, Fuß voll aus `plug/`; hängt an Kassettenwahl und Maßstab (zurückgestellt).
5. Licht in hohen Gebäuden (City-Hochhaus 96 mm, Paulinum 39 mm), Farbe der Wand: ungetestet.

Ergebnis der Studie (Laserscan 1:1500): alle 6 Gebäude hohl und dicht, Schale 14 bis 21 % des Volumens; mit 0,8 statt 1,2 mm Wand kommt nur das Institutsgebäude bei 1:1000 mit V2 neu in die Passung.

## Priorität 2

| Thema | Idee | Bedingung |
|---|---|---|
| Muldenboden dünner (0,3 oder 0,2) | Nutzer: „wenn die Stärke es hergibt, Boden minimal dünner“; E steigt, das Gebäude zieht noch leichter ab | erst wenn die Brücke sauber druckt; eine einzelne Schicht ist ein Risiko |
| Muldenboden als **Einsatz** | 0,2 bis 0,4 mm dünnes Plättchen mit vier Löchern, flach auf dem Bett gedruckt (saubere Löcher, keine Brücke), von unten in die Platte gelegt oder geklebt | löst Brücke und Löcher auf einmal; Halt gegen Zug noch zu planen |
| Platte im echten Boden | Unter der Winkelleiste maximal Platz für Kabel; Support oder zweiteilige Platte statt Trichter | nach Steckprobe 2 |
| Elefantenfuß | Fase 0,6 oder kleine Kompensation im Slicer | wenn 0,5 nicht reicht |

## Priorität 3

- Federzunge in der Mulde: bei CLR 0,10 vielleicht unnötig; „wenn es sich anbietet, mitdrucken, keine Priorität“.
- Heißkleber als Ausweg dokumentieren: Klecks Heißkleber auf die Winkelleiste, Stempel weglassen oder nachträglich abschneiden.
- Nach bewährter Steckprobe: Werte in `plug/parts.py` übernehmen, Probestück und Institutsgebäude umbauen (kein Schieber mehr, Einpress-Kassette, Podest), Seiten neu veröffentlichen.
- Licht durch die Wand (Lichtfenster bzw. dünne Wand des Hohlkörpers) mit LED prüfen, sobald die LED sitzt.
- Paket `plug/testcase/` in `plug/steckprobe/` umbenennen (nur, wenn gewünscht).
