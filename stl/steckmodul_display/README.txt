DISPLAY-GEBÄUDE E4, ZWEITER SATZ (alles in einem, Maßstab 1:1300)
================================================================

Gebaut nach Probedruck 1 und der Modulprobe 1 und 2. Alle Werte sind Planwerte (plug/display/params.py), der Körper als Ganzes ist nicht gedruckt.
Aus den Proben übernommen: Modul als 35,3 × 33,8 × 4,4 angenommen (Tasche 35,94 × 34,10 × 5,00, Luft 0,32 je Seite),
Zapfen mit Kegelspitze P1 (Ø 1,8 auf 2,5 über 2,2 mm) im Sackloch Ø 2,55 (Ø 2,5 passte gut), Kappe mit Lippe 1,0, Fuß-Fase 2,0 und Spiel zur Mulde 0,15
(Probedruck 1: der Rest war in Ordnung). Neu und ungeprüft: die Buchsentasche im Hals (statt der Kassette K0), der kleinere Hals, die Schultern, der Rückdeckel zur niedrigeren Oberkante.

Teile (je 1 Stück)
  D1_koerper.stl       Körper 20,4 × 38,3 × 49,8 mm, 6,6 cm³: Kopf mit Tasche (oben und vorn offen), Kabelfenster, Rückenkeil mit Kammer, Hals mit Buchsentasche, Fuß mit Kodierecke
  D2_rueckdeckel.stl   Rückdeckel 32,1 × 15,2 × 1,2 mm
  D3_frontblende.stl   Frontblende mit Lippe (Kappe), Fenster und vier Zapfen 36,3 × 38,3 × 8,6 mm
  D4_mini_platte.stl   Mini-Platte 23,6 × 25,3 × 14,6 mm: Mulde mit Kodierecke, Einführfase 0,5, vier Pin-Löcher mit Fase, Unterseite flach

Buchsentasche im Hals: 10,56 × 2,94 mm, 14,6 mm hoch von der Fußunterkante, unten offen mit Einführfase 0,5. Oben liegen Schultern (0,5 mm dick) mit dem
Aderschlitz (9,2 breit, ganze Tiefe der Tasche). Die Buchse wird von unten eingeschoben; die Schultern halten sie gegen die Steckkraft.

Druckausrichtung (so liegen die Dateien schon)
  D1 Körper    Fuß unten (Tasche öffnet am Bett), Kopf oben. Kein Support für die Decke mehr (Tasche oben offen). Support braucht nur noch die Unterseite des Kopfs über dem Fuß (422 mm² Kragstück laut Lagenprüfung,
               alles von der Bauplatte aus erreichbar: Support „nur vom Bett“ genügt).
  D2 Rückdeckel   flach, die schräge Außenfläche liegt auf dem Bett.
  D3 Frontblende  flach, Außenfläche (mit dem Fenster) auf dem Bett, Zapfen und Lippe zeigen nach oben.
  D4 Mini-Platte  flach, Unterseite auf dem Bett; Muldenboden 0,4 mm ist die unterste Schicht, kein Support.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3 oder mehr, kein Brim, Kante ohne Elefantenfuß-Kompensation. Druckzeit geschätzt (nicht kalibriert):
D1 35 min, D2 8, D3 14, D4 29 min. Bitte die echten Zeiten melden.

Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen im Zusammenbau, Verdrehsicherung, Überhang je Lage).

Zusammenbau
  1. Dupont-Buchse mit vier Adern (etwa 60 mm) crimpen. Adern von unten durch die Buchsentasche und den Aderschlitz in die Kammer fädeln (Rückdeckel ist ab), Buchse von unten in die Tasche schieben, bis sie an den Schultern anliegt.
  2. Adern an die Pinenden des Moduls löten (Header bleibt am Modul), Reserve (3 bis 4 cm) als Schleife in die Kammer legen.
  3. Modul von oben oder vorn in die Tasche setzen (Pins zuerst durch das Kabelfenster).
  4. Frontblende mit den Zapfen durch die Löcher stecken, die Lippe deckt die Tasche oben ab; Zapfen enden im Sackloch.
  5. Rückdeckel von hinten in die schräge Öffnung drücken (Rastnasen in die Nuten).
  6. Körper in die Mini-Platte stecken (die Kodierecke vorn Süd lässt nur eine Lage zu), Luft zwischen Kopf und Platte 0,3 mm.

Verpolung: Die Buchsentasche ist symmetrisch, die Buchse passt in zwei Lagen. Gedreht liegen GND und 3,3 V (und SDA, SCL) vertauscht an den Pins, das Modul verträgt höchstens 3,5 V. Pin 1 der Buchse beim Einsetzen
markieren (Strich am Körper unten) und vor dem ersten Stecken am Modul durchmessen. Eine Kodierung in der Tasche ist ein Vorschlag für den nächsten Satz.

Zu fühlen und zu melden: Buchse in der Tasche (Sitz, Schultern, geht der Draht durch den Schlitz?), Körper in die Mulde (ohne Kraft, Fase fängt, wackelfrei, verdreht nicht aufsetzbar), Modul in der Tasche, Zapfen (wie in Modulprobe 2),
Frontblende bündig mit Lippe, Rückdeckel (Rast, Spiel), Kabelreserve in der Kammer, trifft die Buchse die Pins der Mini-Platte (Winkelleiste geklebt)?
