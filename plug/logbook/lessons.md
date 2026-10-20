# Lehren: nicht noch einmal

Jede Zeile ist ein Fehler oder eine Beobachtung aus einem Druck, mit der Regel, die daraus folgt. `rN` verweist auf `rounds/`.
Neue Lehren oben in der jeweiligen Gruppe ergänzen.

## Druck

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L40 | Steckplatte: oben bildet sich ein Wulst über die letzten 5 bis 7 Schichten, Gegenstück zum Elefantenfuß unten (der durch die Bettfase 0,5 weg war) | Obere Außenkanten großer Platten mit Fase mindestens 1,5 mm (45°, in Stufen) versehen; die Fase muss tiefer sein als der Wulst (5 bis 7 Schichten) | r7 |
| L41 | Öffnungen der Mulden ohne Fase: Zuquetschung befürchtet | Einführfase an jeder Mulden-Öffnung mindestens 0,5 mm, in Stufen bis über die Oberkante der Platte (endet sie darunter, bleibt ein Rest-Überhang) | r7 |
| L42 | Gravierte Schrift und Nordpfeil auf der Steckplatte nicht lesbar (wie L01) | Beschriftung immer erhaben 0,6 mm, auch auf großen Platten | r7 |
| L43 | Spiel 0,10 zwischen Mulde und Gebäude: an der kleinen Fuß-Lehre bewährt (r4), beim 36 × 35 mm großen Hochhaus-Umriss geht der Stummel nur mit Kraft hinein und sitzt sehr fest | Spiel wächst mit der Umrissgröße: für große Umrisse mehr Spiel; **Vorgabe des Nutzers: nächster Probedruck mit 0,15** (Stummel Umriss 0,05 je Seite kleiner oder Platte `OUTLINE_CLR_T` 0,15); **in r10 bestätigt: 0,15 passt gut** (L47) | r8, r10 |
| L44 | Fuß-Fase 2,0 mm (45°) ohne Muldenfase: fängt das Gebäude, kein Wulst, sitzt auf. Eine Fase im Volumenkörper vor dem Aushöhlen macht die Wände darüber zu Gewölbe (Volumen verdoppelt sich) | Fase nach dem Aushöhlen anbringen und die Wand innen nachführen (`plug/buildings.py`, `FUSS_FASE_T`) | r8 |
| L45 | Zeitschätzung der Planseite: 47 min, gedruckt 55 min | Schätzung mit 1,2 multiplizieren; echte Zeit aus dem Slicer in den Testbogen eintragen lassen | r8 |
| L46 | Loch für ein Einschnapp-Bauteil mit 0,3 mm Spiel je Seite (13,6 × 8,6 für Kasten 13 × 8): passt, aber sehr stramm | Loch = Kastenmaß + 0,7 (Länge) und + 1,0 (Höhe), also 13,7 × 9,0, ließ sich sehr gut einsetzen und hielt fest; Wand 1,2 mm genügt für die Haken | r9 |
| L01 | Gravierte Schrift in schwarzem PLA kaum lesbar | Schrift **erhaben** (0,5 bis 0,6 mm), Rang als **Kerben** in einer Kante; nie in Passflächen (dort fehlt das Spiel) | r1, r2 |
| L02 | Pin-Löcher auf der ersten Schicht schließen sich (Elefantenfuß); einzelne Löcher auch sonst zugequollen | Lochmündungen nie unfasst am Bett; Fase beidseitig (0,3, in dünnen Platten höchstens die halbe Dicke) | r0, r1, r3 |
| L03 | Elefantenfuß etwa 0,2 mm; Fase 0,3 an Bettkanten half nur teilweise, mit 0,4 bleibt ein leichter Wulst | Bettkanten von Steckteilen anfasen (0,4), Schachteingang am Bett zugleich als Einführfase; nächster Test 0,5 | r1 bis r3 |
| L04 | 34 mm lange Brücke über der Schieber-Nut hing stark durch, Fäden in der Nut | keine Brücke über etwa 10 mm; vor jeder STL die waagerechten Decken prüfen (`overhangs()`) | r1 |
| L05 | Muldenboden 0,4 mm über der Körpertasche (etwa 11 × 6 mm) mit Pin-Löchern: stark durchgehängt, Löcher zu; Kabelraum-Decke 15 × 15 hing durch, trotz Thick bridges | Löcher nie in dünne Brücken legen. Entweder mit Support drucken oder Hohlräume als 45°-Böschung bauen (Platte B: 37°, 0,15 Überhang je Schicht) | r3 |
| L06 | Freistehende Stempel am Deckel (1,35 × 2 mm, 3,6 hoch) brachen sofort ab | Freistehende Teile mindestens etwa 2,5 × 1,7 mm Querschnitt, mit Streben (45°); besser das Konzept vermeiden (Heißkleber als Ausweg) | r3 |
| L07 | Teile ohne Blick auf die Druckausrichtung entworfen | je Teil festlegen, welche Seite am Bett liegt, und die Überhänge dazu zeigen | r0, r3 |
| L32 | Faden-V (Kanal Ø 2,2, 53° und 40°): Faden geht durch keins; Öffnungen gut, der untertauchende Kanal zu eng | Kanal mindestens 1 mm weiter (Ø 3,2 oder mehr), Fadenwege großzügig; der Nutzer druckt ohne Rücksicht auf kleine Überhänge mit **Support** | r4 |
| L33 | Nische mit drei Fenstern und Stegen nur, um Brücken zu vermeiden; Nutzer: unnötig und zu groß | Der Nutzer druckt mit Support (einmal bereinigen): Konstruktionen, die nur Brücken vermeiden, vereinfachen. Eine mittelgroße Nische statt drei Fenstern | r4 |

## Passung und Maße

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L49 | K4: Buchsentasche 14,60 hoch, Buchse taucht ca. 0,2 mm zu tief ein und kostet Einstecktiefe E (Grenze stabiler Durchgang 5,08 von 5,28); mit 14,40 „passt fantastisch“. Alte Tasche 10,56 × 2,94 hatte zu viel Spiel, 10,46 × 2,84 passt | Taschenhöhe der Buchse an die echte Einstecktiefe E koppeln, nicht nur an die Buchsenhöhe plus Luft (L13, L17); nach jeder Taschenänderung E nachrechnen | r10 |
| L48 | Kassettenserie 0,12 (sehr stramm, rutscht mit Schwung zu tief), 0,16 (rutscht zu doll), 0,20 (frei); ohne Markierung, Zuordnung nach Gefühl; erst K4 0,14 (zu locker) und K5 0,13 (passt) brachten die Antwort | Passungsserien eng abstufen (Schritt 0,01 bis 0,02 um den vermuteten Wert) und **jedes Teil kennzeichnen** (Punkte, Anzahl = (Spiel − 0,10) / 0,02, oder Name), sonst bleibt die Zuordnung nach Gefühl; Probefuß und echtes Gebäude passen verschieden (K5 im Gebäude etwas strammer), im Plan als Spanne ausweisen | r10 |
| L47 | Wechsel von schwarzem auf beiges PLA: Gebäude passten nicht mehr in die Mulden (Hörsaal nur mit viel Kraft), beige Kassetten nicht mehr in die beigen Gebäude; mit Spiel 0,15 (Mulde) und 0,13 (Schacht) passt es wieder | Spiel gilt je Filament: bei jedem neuen Filament eigene Spielwerte oder zuerst die Flussrate kalibrieren (Messplättchen T4), Wert und Filament im Logbuch notieren; vorhandene Gebäude des alten Filaments nicht als Maßstab für neue Farben nehmen; löst die Vorgabe aus L43 ein (0,15 bewährt, 0,10 zu fest, 0,20 wackelt) | r10 |
| L37 | Fachprobe Powerbank: Luft über der Powerbank 0,6 bei Datenblattdicke 12,6; die echte Powerbank ist „minimal dicker“, die Deckplatte wackelte (Nutzer: ca. 0,2 mm mehr Höhe). Der Prüfbericht hatte den Worst-Case 13,0 mit nur 0,2 Luft noch als „ok“ gemeldet | Bei ungemessenen Kaufteilen Luft aus dem **Worst-Case** wählen, nicht aus dem Nennmaß (hier 13,0 + 0,6 Luft), und die Dicke vor der nächsten Runde mit der Schieblehre notieren; lose aufliegende Deckel brauchen Luft und Halt (Zapfen, Faden) | r5 |
| L38 | Zaun der Fachprobe: README und Prüfbericht nennen einen Zaun um die Powerbank, der Nutzer sagt, nur der Ausschnitt am Anschlussende sei gedruckt | Bei Ausschnitt-Proben (Variante B) im Plan und im Testbogen ausdrücklich benennen, **was nicht im Druck ist**, und das Ergebnis dazu abfragen (Sitz im Zaun nur mit vollem Zaun testbar) | r5 |
| L08 | Datenblattmaße wichen vom Kit ab: Körper der Winkelleiste 2,0 statt 2,54; Buchse etwa 14,5 statt 14,0 hoch | Kaufteile am echten Teil messen, bevor Geometrie daran hängt; ungemessene Werte im Plan als „ungemessen“ markieren | r0, r3 |
| L09 | Spalt unter 0,5 mm nicht messbar | Spielwerte als Serie mit Kennzeichnung drucken, nach Gefühl beurteilen (1 bis 5) | r1 |
| L10 | Kassette im Schacht: 0,05 passt nicht, 0,10 nur mit Kraft, 0,15 ideal zum Gleiten, **0,06 eingepresst** ideal | Einpressen: 0,06 je Seite durchgehend; mit Passzone und Entlastung (8 mm + 0,20) zu lose | r1, r3 |
| L11 | Test mit 7 mm Berührungslänge sagte nichts über 17 mm im echten Aufbau | Passungen in der echten Länge und Druckrichtung testen | r2, r3 |
| L12 | Kassette ragt nach dem Einpressen etwa 0,2 mm unten heraus | Schachttiefe = Kassettenhöhe + mindestens 0,3 | r3 |
| L13 | Buchse sitzt in Tasche 14,15 nicht (keine passt), in 14,45 steht sie noch minimal heraus | Taschenhöhe aus der **gemessenen** Buchsenhöhe plus Spiel; mindestens 14,55 bis zur Messung | r3 |
| L34 | Zapfen Ø 4 / Loch 4,3, nur 1,5 mm hoch: wackelt deutlich (5) | Zapfen und Loch mindestens 1 mm länger (2,5), Gleitspiel 0,15 bleibt | r4 |
| L36 | Schachttiefe Kassette + 0,30: Kassette sitzt, aber Nutzer wünscht noch 0,05 Luft | Kassette + 0,35 | r4 |
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
| L50 | Mulden-Spiel 0,15 statt 0,10 hätte über Fuge = 2 × Spiel + Wand 0,8 jeden Zuschnitt der Gebäude an den Nähten geändert | Spiel (Mulde, `OUTLINE_CLR_T`) und Fuge (Zuschnitt, `ZUSCHNITT_CLR_T`) im Code trennen; sonst schneidet jede Spielkorrektur die Gebäude neu zu. Das Spiel wirkt dann nur über die Lage auf der Platte (`plug/divider/geom.py`) | r10 |
| L19 | Adern knickten stark, wenn die LED-Fläche nur 0,5 mm über der Tasche lag | Podest 2,5 mm über der Tasche mit R 2,5: Adern laufen rund | r2, r3 |
| L20 | Hinter den Lötenden zu wenig Platz (Fasen und Trichter schränken ein) | im echten Boden unter der Winkelleiste so viel wie möglich freilassen; Kabel sollen ohne Wand wegführen | r3 |
| L21 | Deckelstempel stoßen beim Aufsetzen an, Körper der Winkelleiste kippt in der Tasche | Konzept neu planen; Heißkleber auf die Winkelleiste und Stempel weglassen ist der Ausweg (Stützen nachträglich abschneiden) | r3 |
| L22 | Gebäude ohne Kodierecke, aber mit L-Fuß: nur eine Lage, Mulde passt | echte Gebäude folgen dem Grundriss; Kodierecke ist nicht nötig | r3 |
| L30 | Kassette mit Rücken-LED: der Rücken-Chip ragte 2,1 mm hinter die Schachtwand, kommt von unten nicht durch | Beim Einschieben von unten muss jeder Querschnitt der Kassette (auch Streifen und Chips) durch den Schacht im Fuß; im Plan die Hülle über alle z prüfen | Plan Kassetten-Varianten |
| L31 | Gebäudehöhe aus der Bounding-Box täuscht: Seminargebäude 18,8 mm, geschlossene Dachfläche nur etwa 16,4 | Höhenprüfung als Schnitt in der nötigen Höhe (Grundriss und Höhe zusammen), nicht über die Gesamthöhe | Plan Kassetten-Varianten |
| L51 | Fuß-Fase (Paulinum, Neues Augusteum, Seminar-, Institutsgebäude): Wo die Fase endet (vor dem Schachtrohr), lief die um die Fasentiefe nach innen versetzte Fasen-Wand ohne Berührung an der vollen Wand vorbei; im Slicer klaffte 1,3 bis 2,9 mm über dem Bett ein Spalt, der Hohlraum war seitlich offen. `dicht=True` und „keine Kollisionen“ sahen das nicht | Übergänge zwischen Fase und Stück ohne Fase mit einer Querwand schließen (`fase_querwand_mm2`); Hohlkörper zusätzlich auf Löcher prüfen: Lagen roh schneiden, je Kontur füllen, Boden virtuell schließen, Leerraum-Komponenten zählen (Hohlraum muss ein eigenes Stück sein; Prüfskript im Chat, nicht im Repo; `hohl._cs_poly` zum Rastern nicht nehmen, es zeichnet dünne Wände lückenhaft) | Befund 20.10. |

## Prozess

| Nr. | Beobachtung | Regel | Runde |
|---|---|---|---|
| L51 | Aufgabe nahm für größeres Mulden-Spiel 1 bis 2 mm mehr Plattenplatz an; gerechnet wuchs die Platte nur von 115,58 × 220,84 auf 115,63 × 220,90 (Verschiebung höchstens 0,14 mm je Gebäude) | Plattenverschiebung durch Spielerhöhung (0,1 bis 0,2 mm) vorab rechnen statt Platz auf Vorrat einzuplanen; Docks, Zapfen und Unterkasten folgen dem gerechneten Maß (Abweichung höchstens 0,138 mm geprüft) | r10 |
| L23 | Plan nahm „Buchse bündig“ an, ohne die Toleranzkette zu rechnen; erst die Nachprüfung der fertigen Teile zeigte den Verlust an E | Im Plan die Maßkette mit Worst-Case rechnen und zeigen, bevor STL entstehen | r3 |
| L24 | Messfeld „Abstand der Buchse in mm“ war nicht ausfüllbar („wie soll man das messen?“) | Nur Felder, die der Nutzer fühlen oder ja/nein beantworten kann | r3 |
| L25 | Im Ergebnistext fehlte, welche Platte (A oder B) gedruckt wurde | Variante immer abfragen und im Ergebnistext nennen; Version der ZIP nennen | r3 |
| L26 | Ein Generatorlauf überschreibt die Dateien in `stl/` | getesteten Satz einfrieren (ZIP im Rundenordner, Commit-Hash) | r3 |
| L28 | Schrauben nicht vorhanden; Befestigung des Bodens am Hut ist genäht | Deckel und Platte mit Löchern für Fäden planen, keine Schrauben; vor der Planung fragen, welche Verbindungsmittel vorhanden sind | r3 |
| L29 | Faden zunächst durch Löcher geplant, die oben austreten würden; gemeint war ein Austritt an der Unterseite durch eine Lasche | Bei Verbindungsmitteln den Weg des Fadens oder Teils ganz abfragen (Eintritt, Austritt, welche Seite zugänglich) und im Plan als Schnitt zeigen | r3 Nachtrag |
| L35 | Im Ergebnistext von Steckprobe 2 fehlte, welche ZIP gedruckt wurde (L25 noch einmal); zwischen erstem Bau und Neubau lag eine Änderung (eine statt zwei Kassetten) | Der Testbogen fragt Datum oder Kommit der ZIP ab und trägt es in den Ergebnistext; Neubau nach Rückmeldung nur mit neuer Versionsnummer in README und Dateinamen | r4 |
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
