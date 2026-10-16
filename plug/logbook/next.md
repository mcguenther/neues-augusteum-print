# Nächste Drucke und offene Punkte

Stand: nach Steckprobe 1 (r3, 2026-10-16). Priorität 1 = nächster Druck, 2 = danach, 3 = bei Gelegenheit.
Ablauf je Runde: siehe `README.md` (Plan, Abnicken, STL, Druck, Testbogen, Auswertung).

## Geklärt (2026-10-16)

- **Platte B** ist die getestete Platte (W, S, D); die Druckmängel gehören zu Platte A. Basis ist B.
- **Schrauben entfallen**; Deckel und Platte bekommen Löcher für den Faden, der beides andrückt.
- **Buchsen nachmessen entfällt**; das Delta reicht (Tasche mindestens 0,1 über 14,45).

## Offene Fragen an den Nutzer (vor dem Plan klären)

1. **Faden:** Läuft er durch Löcher an den vier Ecken von Deckel **und** Platte (durchgehend, 16,2 mm), und wo tritt er oben aus (Muldenrand, Gebäude steht dazwischen)? Oder sind „Körper“ die Gebäudewände?
2. **Körper der Winkelleiste kippt** (Platte B, ohne Halt von unten): Ist das mit dem Faden-Deckel erledigt, oder soll die Tasche ihn auch ohne Deckel halten?
3. **Name** „Steckprobe“ in Ordnung?

## Priorität 1: Steckprobe 2 (r4)

Ziel: die in r3 gefundenen Mängel beheben und den Aufbau so weit bringen, dass er mit einem Controller leuchtet.

| Thema | Änderung | Grund |
|---|---|---|
| Kassette | Taschenhöhe 14,55 bis 14,60 (Delta aus r3 K, kein Nachmessen); die Variante mit 14,15 entfällt; Gesamthöhe so anpassen, dass die Schachttiefe passt | r3 K: Buchse steht minimal heraus; 14,15 passt keine Buchse |
| Gebäude | nur Schacht A (0,06 durchgehend), Schachttiefe + mindestens 0,3; Variante B (Passzone) entfällt | r3 E: A Sitz 3, B Sitz 5; Kassette ragt 0,2 heraus |
| Fase | Bettkanten und Schachteingang 0,5 statt 0,4 | leichter Wulst bleibt |
| Platte | B (Trichter, ohne Support) weiterentwickeln; Kabelraum unter den Lötenden so frei wie möglich (kein Trichter-Anschnitt im Bereich der Kabel); Fadenlöcher an den Ecken | r3 W: zu wenig Platz hinter den Lötenden |
| Halt der Winkelleiste | Körper darf nicht kippen: Tasche und Rippen überprüfen (Körper in der +1,5 langen Tasche hat zu viel Spiel?), Alternative Heißkleber | r3 W: Körper kippt oder wackelt |
| Deckel und Befestigung | ohne Schrauben: Löcher in Deckel und Platte für den Faden; Stempel entfallen oder bekommen mehr als 1 mm Luft beim Aufsetzen | r3 W: Deckel passt nicht, Stempel stoßen an; Schrauben nicht vorhanden |
| Ösen | 4 Ösen für Fadenschlaufen an den Ecken, von unten zugänglich | Doktorhut, Gebäude wird an vier Fäden angenäht |
| Funktionstest | Adern und LED bestücken, Controller anschließen (Schritt L im Testbogen): Licht, Wackeln, Zehnfach-Abziehen | r3 L: noch nicht getestet, Adern biegen rund |
| Testbogen | Feld „Luft unter der Buchse“ ersetzen durch ja/nein; Feld „Platte A oder B“ und Formular-Version aufnehmen | L24, L25 |

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
- Licht durch die Wand (Lichtfenster) mit LED prüfen, sobald die LED sitzt.
- Paket `plug/testcase/` in `plug/steckprobe/` umbenennen (nur, wenn gewünscht).
