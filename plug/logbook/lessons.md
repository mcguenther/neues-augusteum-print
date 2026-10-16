# Lehren: nicht noch einmal

Jede Zeile ist ein Fehler oder eine Beobachtung aus einem Druck, mit der Regel, die daraus folgt. `rN` verweist auf `rounds/`.
Neue Lehren oben in der jeweiligen Gruppe ergänzen.

## Druck

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L01 | Gravierte Schrift in schwarzem PLA kaum lesbar | Schrift **erhaben** (0,5 bis 0,6 mm), Rang als **Kerben** in einer Kante; nie in Passflächen (dort fehlt das Spiel) | r1, r2 |
| L02 | Pin-Löcher auf der ersten Schicht schließen sich (Elefantenfuß); einzelne Löcher auch sonst zugequollen | Lochmündungen nie unfasst am Bett; Fase beidseitig (0,3, in dünnen Platten höchstens die halbe Dicke) | r0, r1, r3 |
| L03 | Elefantenfuß etwa 0,2 mm; Fase 0,3 an Bettkanten half nur teilweise, mit 0,4 bleibt ein leichter Wulst | Bettkanten von Steckteilen anfasen (0,4), Schachteingang am Bett zugleich als Einführfase; nächster Test 0,5 | r1 bis r3 |
| L04 | 34 mm lange Brücke über der Schieber-Nut hing stark durch, Fäden in der Nut | keine Brücke über etwa 10 mm; vor jeder STL die waagerechten Decken prüfen (`overhangs()`) | r1 |
| L05 | Muldenboden 0,4 mm über der Körpertasche (etwa 11 × 6 mm) mit Pin-Löchern: stark durchgehängt, Löcher zu; Kabelraum-Decke 15 × 15 hing durch, trotz Thick bridges | Löcher nie in dünne Brücken legen. Entweder mit Support drucken oder Hohlräume als 45°-Böschung bauen (Platte B: 37°, 0,15 Überhang je Schicht) | r3 |
| L06 | Freistehende Stempel am Deckel (1,35 × 2 mm, 3,6 hoch) brachen sofort ab | Freistehende Teile mindestens etwa 2,5 × 1,7 mm Querschnitt, mit Streben (45°); besser das Konzept vermeiden (Heißkleber als Ausweg) | r3 |
| L07 | Teile ohne Blick auf die Druckausrichtung entworfen | je Teil festlegen, welche Seite am Bett liegt, und die Überhänge dazu zeigen | r0, r3 |

## Passung und Maße

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L08 | Datenblattmaße wichen vom Kit ab: Körper der Winkelleiste 2,0 statt 2,54; Buchse etwa 14,5 statt 14,0 hoch | Kaufteile am echten Teil messen, bevor Geometrie daran hängt; ungemessene Werte im Plan als „ungemessen“ markieren | r0, r3 |
| L09 | Spalt unter 0,5 mm nicht messbar | Spielwerte als Serie mit Kennzeichnung drucken, nach Gefühl beurteilen (1 bis 5) | r1 |
| L10 | Kassette im Schacht: 0,05 passt nicht, 0,10 nur mit Kraft, 0,15 ideal zum Gleiten, **0,06 eingepresst** ideal | Einpressen: 0,06 je Seite durchgehend; mit Passzone und Entlastung (8 mm + 0,20) zu lose | r1, r3 |
| L11 | Test mit 7 mm Berührungslänge sagte nichts über 17 mm im echten Aufbau | Passungen in der echten Länge und Druckrichtung testen | r2, r3 |
| L12 | Kassette ragt nach dem Einpressen etwa 0,2 mm unten heraus | Schachttiefe = Kassettenhöhe + mindestens 0,3 | r3 |
| L13 | Buchse sitzt in Tasche 14,15 nicht (keine passt), in 14,45 steht sie noch minimal heraus | Taschenhöhe aus der **gemessenen** Buchsenhöhe plus Spiel; mindestens 14,55 bis zur Messung | r3 |
| L14 | Ein Schieber in einer Schwalbenschwanz-Nut klemmte bei allen Spielen (0,05 bis 0,20), Nut durch die Wand | Schieber und Trichterplatte entfallen; sie kosten Pin-Länge | r1 |

## Kontakt

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L15 | Kontakttest mit leerem Buchsengehäuse war wertlos | Kontakte nur **mit gecrimpten Kontakten** testen | r1 |
| L16 | Durchgang stabil ab E etwa 5,1 mm (Plättchen 0,4 und 0,6); bei E 4,88 und 4,68 Aussetzer; darunter nichts | Stapel nach unten rechnen: E = Pin über Körper − Muldenboden − Luft unter der Buchse. Muldenboden höchstens 0,6, Ziel 0,4 | r2 |
| L17 | Luft über der Buchse in der Tasche kostet E (Buchse an den Schultern hängt zu hoch) | Buchse **bündig** einsetzen (Kassette über die stehende Buchse stülpen); Taschenhöhe nur so groß wie nötig | r3 |
| L18 | Haltekraft der Buchse auf den Pins ist klein (Gebäude zieht „sehr leicht“ ab) | ist für das Modell gewollt (Fuß in der Mulde hält); nicht mit Klemmung der Pins kompensieren | r3 |

## Konstruktion

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L19 | Adern knickten stark, wenn die LED-Fläche nur 0,5 mm über der Tasche lag | Podest 2,5 mm über der Tasche mit R 2,5: Adern laufen rund | r2, r3 |
| L20 | Hinter den Lötenden zu wenig Platz (Fasen und Trichter schränken ein) | im echten Boden unter der Winkelleiste so viel wie möglich freilassen; Kabel sollen ohne Wand wegführen | r3 |
| L21 | Deckelstempel stoßen beim Aufsetzen an, Körper der Winkelleiste kippt in der Tasche | Konzept neu planen; Heißkleber auf die Winkelleiste und Stempel weglassen ist der Ausweg (Stützen nachträglich abschneiden) | r3 |
| L22 | Gebäude ohne Kodierecke, aber mit L-Fuß: nur eine Lage, Mulde passt | echte Gebäude folgen dem Grundriss; Kodierecke ist nicht nötig | r3 |

## Prozess

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L23 | Plan nahm „Buchse bündig“ an, ohne die Toleranzkette zu rechnen; erst die Nachprüfung der fertigen Teile zeigte den Verlust an E | Im Plan die Maßkette mit Worst-Case rechnen und zeigen, bevor STL entstehen | r3 |
| L24 | Messfeld „Abstand der Buchse in mm“ war nicht ausfüllbar („wie soll man das messen?“) | Nur Felder, die der Nutzer fühlen oder ja/nein beantworten kann | r3 |
| L25 | Im Ergebnistext fehlte, welche Platte (A oder B) gedruckt wurde | Variante immer abfragen und im Ergebnistext nennen; Version der ZIP nennen | r3 |
| L26 | Ein Generatorlauf überschreibt die Dateien in `stl/` | getesteten Satz einfrieren (ZIP im Rundenordner, Commit-Hash) | r3 |
| L28 | Schrauben nicht vorhanden; Befestigung des Bodens am Hut ist genäht | Deckel und Platte mit Löchern für Fäden planen, keine Schrauben; vor der Planung fragen, welche Verbindungsmittel vorhanden sind | r3 |
| L27 | Wertänderungen in `plug/parts.py` würden Probestück und Institut brechen (sie rechnen mit Schieber) | neue Werte in `plug/<paket>/params.py`; `parts.py` erst nach bewährter Runde ändern | r3 |

## Vorab-Checkliste vor jeder STL

1. `lessons.md` und `current.md` gelesen; im Plan stehen die berücksichtigten Lehren.
2. Maße der Kaufteile gemessen oder als „ungemessen“ im Plan markiert (Buchsenhöhe, kürzester Pin).
3. Maßkette gerechnet, mit Worst-Case (E, Höhen, Taschenluft); Ergebnis im Plan.
4. Druckausrichtung je Teil; `overhangs()` gelesen: keine Brücke über 10 mm, keine Löcher in dünnen Brücken, Böschungen höchstens etwa 45°.
5. Fasen: Bettkanten 0,4, Löcher beidseitig, Einführfasen an allen Steckstellen; nichts Erhabenes in Passflächen.
6. Kollisionsprüfung gegen die Kaufteile; Kontrolle, dass ein zu enges Spiel tatsächlich anstößt.
7. Varianten klar benannt (A/B), mit Kerben oder Schrift gekennzeichnet; im Testbogen abgefragt.
8. Formularfelder fühlbar oder ja/nein; keine Messung, die der Nutzer nicht machen kann.
9. Plan zeigt Alternativen und Empfehlung; Nutzer hat abgenickt.
10. ZIP mit README, Prüfbericht und Vorschaubildern; nach dem Druck wird der Satz im Logbuch eingefroren.
