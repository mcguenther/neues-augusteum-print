TESTFALL KASSETTE (Planung: plug/testcase/plan.html)
====================================================

Ein kompletter Aufbau aus Mini-Gebäude, Kassette und Mini-Grundplatte mit Winkelleiste. Gedruckt wird alles in einem Lauf.

Dateien (alle in Druckausrichtung)
  T_cassette_v4_x2.stl   2 × Kassette v4 (13,5 × 29,4 × 16,95 mm), Tasche unten offen, Podest, R 2,5   ≈ 7,6 g
                         Kassette 1 (1 Kerbe an der Seite): Taschenhöhe 14,45, Luft über der Buchse 0,45
                         Kassette 2 (2 Kerben): Taschenhöhe 14,15, Luft 0,15 (passt nur, wenn die Buchse höchstens 14,15 mm hoch ist)
  T_building_A.stl       Mini-Gebäude, L-Fuß 24 × 38, 18,15 hoch, Schacht 0,06 durchgehend   ≈ 7,0 g
  T_building_B.stl       wie A, Schacht nur die ersten 8 mm mit 0,06, dahinter 0,20   ≈ 7,0 g
  T_plate_A_support.stl  Mini-Grundplatte 38 × 52 × 16,2 mm, Mulde 10,2 tief (Spiel 0,10), Muldenboden 0,4, Dock A mit Kasten-Hohlräumen.
                         MIT SUPPORT drucken (Hohlräume unter dem Muldenboden und Kabelraum)   ≈ 13,1 g
  T_plate_B_nosupport.stl  dieselbe Platte, aber alle Hohlräume unter dem Muldenboden als Trichter (Böschung 37° zur Senkrechten, je Schicht
                         0,15 mm Überhang), Pin-Löcher konisch. OHNE SUPPORT drucken. Längste Brücke 3,7 mm   ≈ 13,1 g
  T_lid.stl              Mini-Deckel 2,0 mm mit Fenster; zwei kräftige Stempel (2,9 × 1,76 mm, 3,6 hoch) mit Böschungsstreben an
                         drei Seiten und einem Quersteg dazwischen; passt zu beiden Platten   ≈ 4,2 g
  Zusammen ≈ 52 g (mit beiden Platten); bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa 2,8 h.

Kaufteile: Winkelleiste (4 Pins), Dupont-Buchse mit gecrimpten Adern, LED-Streifen 10 mm, 4 Schrauben M3.
  Das Fenster im Mini-Gebäude ist 11,2 mm breit: der 10-mm-Streifen passt, der 12-mm-Streifen nicht.

Slicer wie Nacht 1 (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung). Gebäude, Kassetten und Deckel ohne Stützen.
  Platte A: mit Support (nur auf dem Bett, „normal“), die Brücken sind Muldenboden (0,4 mm) und Kabelraum (15,0 × 15 mm).
  Platte B: ohne Support. Unten ist der Kabelraum ein offener Trichter, der Muldenboden hängt nur über der Körpertasche (3,7 mm). Die Treppenstufen
  der Böschung sind gewollt. „Thick bridges“ trotzdem einschalten.
  Mini-Gebäude: Der Schacht öffnet am Druckbett. Die Fase 0,4 am Eingang gleicht den Elefantenfuß aus.
  Die Beschriftung ist erhaben: GEB A / GEB B (1 bzw. 2 Punkte) am Gebäude, PLATTE an der Platte.

Vorab: Höhe der Buchsengehäuse mit der Schieblehre messen (Soll 14,0, kleinster und größter Wert aufschreiben).
  Die Buchse soll unten bündig mit der Kassette sitzen. Jeder Millimeter, den sie zu hoch sitzt, kostet Einstecktiefe:
  E = 5,28 bündig, 5,13 bei Kassette 2 an den Schultern, 4,83 bei Kassette 1 an den Schultern (Aussetzer-Bereich!).

Zusammenbau
  1. Winkelleiste von unten (durch den Kabelraum) in die Platte schieben: Pins nach oben durch den Muldenboden, Körper in die Tasche,
     die Lötenden nach hinten (zur offenen Seite). Deckel mit 4 Schrauben M3 schließen; die Stempel halten den Körper.
     Bei Platte B ist der Schacht unten ein Trichter und lässt die Leiste von selbst in die Tasche gleiten.
  2. Buchse mit gecrimpten Adern bündig einsetzen: Buchse mit der Steckseite auf einen flachen Tisch stellen, Adern durch den Schlitz der
     Kassette fädeln, Kassette von oben darüberstülpen, bis sie auf dem Tisch steht. Nicht von unten bis an die Schultern schieben.
     Adern über die runde Kante, flach zur LED. LED-Streifen auf das Podest legen.
  3. Kassette mit der offenen Seite voran von unten in das Mini-Gebäude drücken, bis sie am Rand anschlägt (Buchse bündig mit der Fußunterkante).
  4. Mini-Gebäude in die Mulde der Platte setzen.

Prüfung
  1  Kassette ins Gebäude: nur mit Daumendruck, schlägt am Rand an, sitzt fest. A und B vergleichen.
  2  Gebäude in die Mulde: mit Fingerdruck, kein spürbares Spiel, nur in einer Lage, sinkt bis zum Boden.
  3  Pins treffen die Buchse ohne Trichter: geht ohne Kraft ein. Danach prüfen, ob die Buchse beim Aufstecken nach oben gerutscht ist
     (Unterkante der Buchse gegen die Fußunterkante halten).
  4  Durchgang aller vier Kontakte mit dem Multimeter, dabei wackeln. Mit Kassette 1 und Kassette 2 vergleichen.
  5  Gebäude zehnmal abziehen und aufstecken: Kassette und Buchse bleiben, Durchgang bleibt.
  6  Adern über das Podest: kein Knick, LED liegt flach.
  7  Lötseite: Kabel anlöten und nach unten durch das Fenster führen.
  8  Optional: Controller anschließen, LED leuchten lassen.
