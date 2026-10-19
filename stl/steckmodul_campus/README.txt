Druckpaket Steckplatte Campus Augustusplatz, Maßstab 1:1300
===========================================================

Stand 18.10.2026. Alle Maße in mm. Ungedruckt: Die Werte unten sind Empfehlungen, noch nicht erprobt.
Erzeugt mit `python3 -m plug.campus`, `python3 -m plug.buildings` und `python3 -m plug.export_campus`.

Inhalt
------
  steckplatte_1zu1300.stl              Platte 115,6 x 220,9 x 14,6 (mit Gang und Treppen im Süden und Nordosten bis 16,9 hoch) mit Mulden
                                       für alle sechs Gebäude, Aussparung für den Hof, Wänden zwischen den Mulden (0,8; Paulinum/Neues Augusteum an den Zahnflanken 0,7)
                                       und Pin-Löchern (24 Stück, vier je Gebäude);
                                       unten 2 Zapfenlöcher (20|20) und (100|180) und 4 Fadentaschen (halbe Pille) an den Ecken;
                                       am Ostrand (y = 34,4) Mulde und Dock (4 Pin-Löcher) für das Display-Gebäude, Maße des ersten,
                                       gedruckten Satzes
  hof_einsatz_1zu1300.stl              Innenhof (Pflaster, Beete, Bänke, Denkmal, Bäume), 6 mm tief in die Aussparung
  01_paulinum_1zu1300.stl              je ein Hohlgebäude mit Fuß (14,2 mm) zum Stecken, Schacht für die LED-Kassette,
  02_neues_augusteum_1zu1300.stl       Boden unten, Gewölbe innen, ohne Support druckbar
  03_hoersaalgebaeude_1zu1300.stl
  04_seminargebaeude_1zu1300.stl
  05_institutsgebaeude_1zu1300.stl
  06_city_hochhaus_1zu1300.stl
  pruefbericht.txt                     Prüfung: dicht, Maße, Volumen, Gebäude untereinander, Überhänge
  uebersicht_aufgeschnitten.png        alle sechs Gebäude aufgeschnitten: Wand 0,8, Gewölbe, Schacht für die Kassette
  uebersicht_unterseiten.png           die Kassettenaufnahme von unten (Schacht im Boden)
  uebersicht_schacht_schnitt.png       Schnitte durch die Schachtmitte der drei v4-Gebäude (Anschlagring, Platz darüber)

Die Gebäude sind hohl (22 bis 41 % des Volumens eines massiven Gebäudes mit Fuß), aber geschlossen: Boden 1,2 mm unten, Dach oben.
Von außen sieht man deshalb nur den Schacht für die Kassette; der Hohlraum zeigt sich im Schnitt und in der Schichtvorschau.

Kassettenaufnahme: Der Schacht (13,6 x 29,6 bei v4, 19,3 x 6,5 bei V1RS, 13,1 x 6,5 bei V2R) ist von unten frei bis 4 mm über der Platte.
Die v4-Gebäude haben dort einen Anschlagring (4 bis 4,5 mm, 45° auf der Unterseite) mit 11,3 mm freier Öffnung; V1RS und V2R haben keinen Ring.

Aufbau und Maße
---------------
  Spiel Gebäude zur Mulde        0,15 mm je Seite (0,10 war bei großen Umrissen zu fest, Passungsserie: 0,15 passt, 0,20 wackelt)
  Fuge zwischen Gebäuden         1,0 mm beim Zuschnitt der Gebäude (Spiel 0,10 + Wand 0,8 + Spiel), über die ganze Höhe; an vier Nähten; auf der Platte stehen die
                                 Gebäude um bis zu 0,14 mm auseinandergerückt (Fuge 1,1 = 0,15 + Wand 0,8 + 0,15), die Gebäude selbst sind unverändert
  Hof-Einsatz                    Fuge 0,15 mm, 6 mm unter der Plattenoberfläche
  Platte                         Muldenboden 0,4 mm, flache Unterseite, Fase 1,5 an der Oberkante, Schrift erhaben
  Kassetten je Gebäude           Paulinum, Neues Augusteum, Hörsaalgebäude: v4; Seminar- und Institutsgebäude: V1RS; Hochhaus: V2R
                                 (die Kassetten selbst sind nicht Teil dieses Pakets)

Slicer (Gebäude, ausführlich in plug/slicer.md)
-----------------------------------------------
  Ausrichtung wie exportiert (Boden auf dem Bett), Support aus, 0,2 mm Schicht, Düse 0,4, 2 Wandlinien, Arachne,
  obere Deckschichten 4, untere 2, Füllung Gyroid 10 %, "Ensure vertical shell thickness" aus, PLA weiß oder natur.
  City-Hochhaus: Rand (Brim) 5 mm, es ist 125 mm hoch auf 36 x 35 mm Grundfläche.
  Platte: flache Unterseite auf das Bett, Support aus; 220,9 mm Länge, Druckbett mindestens 230 x 230 mm.
  Hof-Einsatz: Support aus; die Bäume haben unten höchstens 45° Überhang, Stämme sind 0,8 mm dick.

Display-Gebäude: Das Gebäude selbst liegt nicht im Paket (`stl/steckmodul_display/`). Seine Mulde in der Platte ist nach dem ersten Satz gebaut;
der zweite Satz (kleinerer Hals) passt hinein, sitzt aber mit etwa 1,4 mm Luft je Seite lose.

Hinweise
--------
  * Farben sind nicht Teil dieses Pakets (kommen später); alle Dateien sind einfarbig.
  * Die Gebäude sind hohl (Wand 0,8, Gewölbe innen). In der Schichtvorschau zeigt jede Schicht im Fuß und im Gebäude nur dünne
    Wandringe; Füllung (Gyroid) gibt es nur in den Keilen über den Gewölben. Ist der Innenraum gefüllt, hat der Slicer beim Laden
    Flächen umgedreht: dann mit einer älteren Datei verwechselt (Stand vor dem 18.10.2026, Paulinum war betroffen) - neu laden.
  * Der Slicer kann beim Laden einzelne "nicht-mannigfaltige Kanten" melden und reparieren (Berührstellen im Dach und Gewölbe, im
    Prüfbericht als Berührkanten gezählt; dort steht auch das Volumen, das PrusaSlicer nach dem Laden sieht). Die senkrechte helle
    Linie an der Außenwand in der Vorschau ist die Naht (Seam), kein Spalt.
  * Dünnste Stellen: Wände 0,8 mm (zwei Linien), Zipfel des Paulinums im Osten 1,0 x 3,3 mm, Stämme der Bäume 0,8 mm.
  * Die Platte hat ein Mulden-Spiel von 0,15 mm je Seite. Passt ein Gebäude nur mit Kraft oder wackelt es, die Mulde nicht aufbohren,
    sondern Rückmeldung geben.
