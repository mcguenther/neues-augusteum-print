Druckpaket Steckplatte Campus Augustusplatz, Maßstab 1:1300
===========================================================

Stand 18.10.2026. Alle Maße in mm. Ungedruckt: Die Werte unten sind Empfehlungen, noch nicht erprobt.
Erzeugt mit `python3 -m plug.campus`, `python3 -m plug.buildings` und `python3 -m plug.export_campus`.

Inhalt
------
  steckplatte_1zu1300.stl              Platte 115,6 x 220,8 x 14,6 (mit Gang und Treppen im Süden und Nordosten bis 16,9 hoch) mit Mulden
                                       für alle sechs Gebäude, Aussparung für den Hof, Wänden zwischen den Mulden (0,8)
                                       und Pin-Löchern (24 Stück, vier je Gebäude)
  hof_einsatz_1zu1300.stl              Innenhof (Pflaster, Beete, Bänke, Denkmal, Bäume), 6 mm tief in die Aussparung
  01_paulinum_1zu1300.stl              je ein Hohlgebäude mit Fuß (14,2 mm) zum Stecken, Schacht für die LED-Kassette,
  02_neues_augusteum_1zu1300.stl       Boden unten, Gewölbe innen, ohne Support druckbar
  03_hoersaalgebaeude_1zu1300.stl
  04_seminargebaeude_1zu1300.stl
  05_institutsgebaeude_1zu1300.stl
  06_city_hochhaus_1zu1300.stl
  pruefbericht.txt                     Prüfung: dicht, Maße, Volumen, Gebäude untereinander, Überhänge
  uebersicht_aufgeschnitten.png        alle sechs Gebäude aufgeschnitten: Wand 0,8, Gewölbe, Schacht für die Kassette

Die Gebäude sind hohl (22 bis 41 % des Volumens eines massiven Gebäudes mit Fuß), aber geschlossen: Boden 1,2 mm unten, Dach oben.
Von außen sieht man deshalb nur den Schacht für die Kassette; der Hohlraum zeigt sich im Schnitt und in der Schichtvorschau.

Aufbau und Maße
---------------
  Spiel Gebäude zur Mulde        0,10 mm je Seite (Hochhaus-Stummel in r8 mit 0,10 nur mit Kraft eingesteckt; 0,15 ist vorgemerkt)
  Fuge zwischen Gebäuden         1,0 mm (Spiel + Wand 0,8 + Spiel), über die ganze Höhe; an vier Nähten
  Hof-Einsatz                    Fuge 0,10 mm, 6 mm unter der Plattenoberfläche
  Platte                         Muldenboden 0,4 mm, flache Unterseite, Fase 1,5 an der Oberkante, Schrift erhaben
  Kassetten je Gebäude           Paulinum, Neues Augusteum, Hörsaalgebäude: v4; Seminar- und Institutsgebäude: V1RS; Hochhaus: V2R
                                 (die Kassetten selbst sind nicht Teil dieses Pakets)

Slicer (Gebäude, ausführlich in plug/slicer.md)
-----------------------------------------------
  Ausrichtung wie exportiert (Boden auf dem Bett), Support aus, 0,2 mm Schicht, Düse 0,4, 2 Wandlinien, Arachne,
  obere Deckschichten 4, untere 2, Füllung Gyroid 10 %, "Ensure vertical shell thickness" aus, PLA weiß oder natur.
  City-Hochhaus: Rand (Brim) 5 mm, es ist 125 mm hoch auf 36 x 35 mm Grundfläche.
  Platte: flache Unterseite auf das Bett, Support aus; 220,8 mm Länge, Druckbett mindestens 230 x 230 mm.
  Hof-Einsatz: Support aus; die Bäume haben unten höchstens 45° Überhang, Stämme sind 0,8 mm dick.

Hinweise
--------
  * Farben sind nicht Teil dieses Pakets (kommen später); alle Dateien sind einfarbig.
  * Der Slicer kann beim Laden "nicht-mannigfaltige Kanten" melden und reparieren (Berührstellen im Dach und Gewölbe, im Prüfbericht
    als Berührkanten gezählt). Danach die Schichtvorschau auf Löcher in Wänden und Dach ansehen.
  * Dünnste Stellen: Wände 0,8 mm (zwei Linien), Zipfel des Paulinums im Osten 1,0 x 3,3 mm, Stämme der Bäume 0,8 mm.
  * Die Platte hat ein Mulden-Spiel von 0,10 mm je Seite. Passt ein Gebäude nur mit Kraft, die Mulde nicht aufbohren,
    sondern Rückmeldung geben (Vorgabe: nächster Probedruck mit 0,15 mm).
