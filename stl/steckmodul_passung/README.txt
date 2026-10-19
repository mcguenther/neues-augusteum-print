Passungs-Probedrucke bei wechselnden Filamenten (Plan: plug/filament/plan.html)
=====================================================================================
Stand 2026-10-19. Alles ungedruckt. Zwei Varianten, beide mit derselben Kassettenserie K1 bis K3.

Variante A: die vorhandenen beigen Gebäude sind die Lehre (Institutsgebäude für Mulde und Kassette; Hörsaal und Seminar zur Gegenprobe)
  A1_mulden_block_institut.stl   GRAU. Platte 92 x 99 x 14,6 mm mit drei Mulden im Umriss des Institutsfußes, Spiel je Seite
                                 0,10 (ein Balken) / 0,15 (zwei) / 0,20 (drei Balken, erhaben links); Mulde 14,2 tief, Boden 0,4, Fase oben 0,5.
                                 Das beige Institutsgebäude in jede Mulde stecken. Druckzeit etwa 125 min (Schätzung).
Variante B: eigener kompakter Probedruck, kein Gebäude nötig
  B1_probefuss_fase4.stl         BEIGE (oder die Farbe, die geprüft wird). Fuß 31 x 18 mm mit Kodierecke (verdrehsicher), Fuß-Fase 4,0 (die Gebäude haben heute 2,0),
                                 oben offen (kein Dach): der Schacht der Kassette V1RS geht durch, die Kassette lässt sich von oben herausdrücken; 22 mm hoch, 7,8 mm ragen als Griff aus der Mulde. Kein Anschlag: Kassette bündig einsetzen, indem man sie mit der Unterseite auf den Tisch stellt und den Fuß darüberdrückt. Etwa 29 min.
  B3_mulden_block_probe.stl      GRAU. Platte 40 x 63 x 14,6 mm mit drei Mulden im Umriss des Probefußes, Spiele wie A1. Etwa 48 min.
Beide Varianten:
  K1_kassette_V1RS_12.stl        BEIGE. Unterbau der Kassette V1RS (nur dort sitzt die Passung; ohne Blatt und Streifen), Tasche unten am Bett.
  K2_kassette_V1RS_16.stl        Spiel im Schacht je Seite 0,12 / 0,16 / 0,20 (heute 0,06): Außenmaß 0,06 / 0,10 / 0,14 je Seite kleiner.
  K3_kassette_V1RS_20.stl        Kerben/Kennung: Dateiname; mit Stift auf der Unterseite markieren. Je etwa 16 min.

Druckzeit (Schätzung nach dem Muster der r8-Schätzung, mal 1,2 nach L45; nicht kalibriert; bitte die echte Zeit aus dem Slicer melden):
  Variante A: Block 125 min + Kassetten 49 min = 174 min
  Variante B: Fuß 29 min + Block 48 min + Kassetten 49 min = 126 min 

Slicer: PLA, Düse 0,4, Schicht 0,2, Wände 3, Füllung 15 %, Support aus, Ausrichtung wie exportiert (Fuß bzw. Plattenunterseite und Kassettentasche am Bett).
Filament: Fluss möglichst vorher kalibrieren (Plan, Abschnitt 6, Messplättchen T4).
Auswertung nach Gefühl: Fuß in Mulde 1 bis 3 (geht es ohne Kraft hinein, wie fest zieht man heraus, wackelt es), Kassette 1 bis 3 im Schacht
(Sitz 1 bis 5, Ziel wie in Schwarz: hält beim Schütteln, Herausdrücken nur mit Druck). Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen, Überhang).
Schachtdecke im Probefuß 0,35 über dem Unterbau (im Code der Gebäude steht noch 0,30).
