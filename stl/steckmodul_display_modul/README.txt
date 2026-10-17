MODULPROBE DISPLAY-GEBÄUDE: AUFNAHME UND FRONTBLENDE MIT ZAPFEN
==============================================================

Anlass: Probedruck 1 (stl/steckmodul_display/). Das Modul passte nicht in die Tasche (etwa 0,75 mm zu hoch), die Breite passte, die Zapfen griffen kaum und waren kurz.
Diese Probe enthält nur die Aufnahme des Moduls und die Blende; die Kassette ist hier nicht dabei (sie kommt später in den Körper).
Alle Werte sind Planwerte (plug/display/params.py), nichts davon ist gedruckt.

Was sich gegenüber Probedruck 1 geändert hat
  Tasche Höhe      34,35 mm (vorher 33,30): Modul als 34,05 hoch angenommen (alte Tasche 33,3 plus 0,75), oben 0,30 Luft. Falls das Modul nur 33,75 hoch ist, bleibt 0,3 mehr Luft.
  Tasche Breite    36,10 mm (vorher 35,90): 0,4 Luft je Seite statt 0,3 (Wunsch des Nutzers: 0,1 mehr). Kopf damit 38,5 breit.
  Tasche Dicke     5,10 mm (unverändert; Modul 4,5 angenommen, Dicke blieb unbeanstandet).
  Sackloch         Ø 2,5 (vorher 2,6), 2,6 tief (vorher 1,2), Einführfase 0,3.
  Zapfen           A: Ø 2,4 (0,05 Luft je Seite, wie die bewährte Kassette mit 0,06), B: Ø 2,5 (ohne Luft); Länge 7,50 mm von der Rückseite der Blende,
                   im Sackloch 2,4 tief (vorher 1,0), Spitze 0,4 gefast. Im echten Körper bleibt hinter dem Sackloch mindestens 1,1 mm Material.

Teile
  M1_aufnahme.stl             8,7 × 38,5 × 36,8 mm  Kopf mit Tasche von vorn (offen), Kabelfenster in der Rückwand, vier Sacklöcher
  M2_blende_A_zapfen_2_4.stl  36,8 × 38,5 × 8,7 mm  Blende mit Fenster und vier Zapfen Ø 2,4
  M3_blende_B_zapfen_2_5.stl  36,8 × 38,5 × 8,7 mm  Blende mit vier Zapfen Ø 2,5

Druckausrichtung (so liegen die Dateien schon)
  M1  stehend auf der Kopfunterseite (wie der Körper im Probedruck 1; Tasche und Sacklöcher liegen waagerecht, so wie im echten Körper). Support in der Tasche für die Decke
      (wie im Probedruck 1, von vorn herauszuziehen). Liegend auf der Rückseite geht es ohne Support, aber die Sacklöcher entstehen dann senkrecht und fallen anders aus.
  M2, M3  flach, Außenfläche unten, Zapfen nach oben, kein Support. Eine Blende reicht, die zweite für den Vergleich.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3, Thick bridges an, kein Brim. Druckzeit geschätzt (nicht kalibriert):
M1 27 min, M2 14, M3 14 min.

Ablauf und was zu melden ist
  1. Modul in die Tasche schieben (Pins zuerst durch das Kabelfenster). Passt es jetzt in der Höhe? Wie viel Luft oben ungefähr (mm), und seitlich (leicht, saugend, klemmt)?
     Liegt es unten auf dem Taschenboden? Passt der Header durch das Kabelfenster?
  2. Durch die Befestigungslöcher des Moduls auf die Sacklöcher schauen: stimmen sie überein (mittig, nach oben, unten, links, rechts versetzt, ungefähr wie viel)?
     Das ist die Lochlage, die ich aus dem Foto geschätzt habe (Lochabstand 30,3 × 28,6, untere Löcher 2,3 über der Pinkante). Die Zapfen haben
     0,3 Luft je Seite im Modulloch: bei mehr Versatz gehen sie nicht durch die Platine. Das Modul ist höher als gedacht; wo die zusätzlichen 0,75 mm liegen (oben oder an der Pinkante), weiß ich nicht.
     Stoßen die beiden oberen Zapfen am Glas des Moduls an (das Glas darf die Löcher nicht verdecken)?
  3. Blende A aufstecken: gehen die vier Zapfen durch die Modullöcher? Greifen sie im Sackloch (1 lose bis 5 fest), wie viel Kraft zum Abziehen? Dasselbe mit Blende B.
     Ist eine Variante zu fest (bricht, reißt die Rückwand), eine zu lose?
  4. Sichtfenster: Ist die aktive Fläche des Displays vollständig sichtbar? Wie viel Rand bleibt oben, unten, links und rechts (mm, grob)? Ist das Display zu hoch oder zu tief im Fenster?
  5. Sitzt das Modul zwischen Blende und Rückwand mit Spiel (wackelt es in der Dicke)?

Prüfbericht: pruefbericht.txt.
