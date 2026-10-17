DISPLAY-GEBÄUDE E4, ERSTER PROBEDRUCK (Standardwerte, Maßstab 1:1300)
====================================================================

Alle Werte sind Planwerte (plug/display/params.py), nichts davon ist gedruckt. Bewährt (r8, L10, L34): Fuß-Fase 2,0 vorn, Kassette im Schacht mit Spiel 0,06 je Seite,
Einführfasen 0,5, Muldenboden 0,4. Das Spiel Fuß zur Mulde ist 0,15 je Seite (Vorgabe des Nutzers für den nächsten Probedruck). NICHT bewährt: Zapfen Ø 2,4 in Sackloch
Ø 2,6 (0,1 je Seite) und durch das Modulloch Ø 3,0 (0,3 je Seite, Lage des Lochs ± 0,5 aus dem Foto), Rastnasen 0,4 hoch in Nuten (Spiel 0,15 bis 0,5),
Rückdeckel mit Spiel 0,15, Fase 0,6 an den Längsseiten, die Modultasche (Platine 35,3 × 33,0, Dicke 4,5 angenommen: ungemessen).

Teile (je 1 Stück):
  D1_koerper.stl       Körper 23,0 × 38,3 × 50,2 mm, 7,5 cm³
  D2_rueckdeckel.stl   Rückdeckel 33,6 × 15,2 × 1,2 mm
  D3_frontblende.stl   Frontblende 35,7 × 38,3 × 7,3 mm
  D4_kassette.stl      Kassette K0 5,3 × 13,0 × 15,1 mm (Unterbau V2 ohne Blatt: nur Buchsentasche und Aderschlitz)
  D5_mini_platte.stl   Mini-Platte 26,2 × 27,8 × 14,6 mm: Mulde mit Kodierecke, Einführfase 0,5, vier Pin-Löcher mit Fase, Unterseite flach

Druckausrichtung (so liegen die Dateien schon):
  D1 Körper    Fuß unten (Schacht öffnet am Bett), Kopf oben. Support unter dem Kopf nötig (Unterseite des Kopfs über dem Fuß, 583 mm² Kragstück laut Lagenprüfung),
               dazu in der Modultasche (Decke der Tasche, von vorn offen) und über dem Kabelfenster; die Schräge hinten liegt flach genug (kein Support).
               Support mit „überall“ einstellen, nicht nur vom Bett; die Tasche liegt offen nach vorn, der Support lässt sich von dort herausziehen.
  D2 Rückdeckel   flach, die schräge Außenfläche liegt auf dem Bett, die Rastnasen stehen seitlich ab (0,2 mm über dem Bett, Überhang nur 0,4 mm).
  D3 Frontblende  flach, Außenfläche (mit dem Fenster) auf dem Bett, die vier Zapfen zeigen nach oben.
  D4 Kassette  stehend, Tasche unten (wie die Kassetten der Gebäude).
  D5 Mini-Platte  flach, Unterseite auf dem Bett; Muldenboden 0,4 mm ist die unterste Schicht, kein Support.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3 oder mehr, Füllung egal, Thick bridges an, kein Brim, Kante ohne
Elefantenfuß-Kompensation (die Fase ist eingerechnet). Druckzeit geschätzt (nicht kalibriert): D1 38 min, D2 8, D3 13, D4 14, D5 32 min.
Bitte die echten Zeiten aus dem Slicer melden.

Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen im Zusammenbau, Verdrehsicherung, Überhang je Lage).

Zusammenbau (Reihenfolge)
  1. Kassette K0 mit der Dupont-Buchse bestücken (Tasche unten), Adern durch den Aderschlitz nach oben führen, ca. 3 bis 4 cm Reserve in der Kammer.
  2. K0 von unten in den Schacht des Körpers pressen (bündig mit der Fußunterkante). Die Adern kommen durch die Öffnung in die Kammer.
  3. Adern an die Pinenden des Moduls löten (Header bleibt am Modul), Adern in einer Schleife in die Kammer legen.
  4. Modul von vorn in die Tasche schieben (Pins zuerst durch das Kabelfenster), Frontblende mit den Zapfen durch die Löcher stecken (Zapfen enden im Sackloch).
  5. Rückdeckel von hinten in die schräge Öffnung drücken (Rastnasen in die Nuten).
  6. Körper in die Mini-Platte stecken (die Kodierecke vorn Süd lässt nur eine Lage zu), Luft zwischen Kopf und Platte 0,3 mm.

Verpolung: Die Buchsentasche der Kassette K0 ist symmetrisch, die Kassette passt in zwei Lagen in den Schacht. Gedreht stecken GND und 3,3 V (und SDA, SCL) vertauscht an
den Pins, und das Modul verträgt höchstens 3,5 V. Deshalb Pin 1 der Buchse beim Bestücken markieren (z. B. mit einem Strich auf der Kassette) und vor dem ersten Stecken am
Modul durchmessen (Plug-Prüfregel, plug/PLAN.md). Eine Kodierecke an Kassette und Schacht ist ein Vorschlag für den nächsten Satz; sie ist hier nicht enthalten.

Zu fühlen und zu melden (Testbogen kommt nach dem Druck): geht der Körper ohne Kraft in die Mulde, fängt ihn die Fase, sitzt er wackelfrei, lässt er sich verdreht nicht aufsetzen? Kassette im Schacht (1 lose bis 5 fest), Modul in
der Tasche (Spiel), Zapfen durch Modul (lose/fest), Zapfen im Sackloch, Rückdeckel (Rast, Spiel), Frontblende bündig, Kabelreserve in der Kammer, trifft die Buchse die Pins der Mini-Platte (Winkelleiste geklebt)?

Hinweis zur Maßkette: In Plan 3 stand die Kassette mit 13,2 × 5,58 × 17,1 mm (Maße der v4, Spiel doppelt gerechnet). Richtig für den V2-Unterbau sind Schacht 13,08 × 5,46 und Oberkante
0,9 mm über der Platte (Unterbau 15,1 minus Fuß 14,2). Die Geometrie hier ist darauf umgestellt: Luft über der Kassette 4,5 mm, Schräge hinten 6,6 mm hoch statt 8,6.
