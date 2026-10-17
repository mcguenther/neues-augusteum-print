MODULPROBE DISPLAY-GEBÄUDE: AUFNAHME UND FRONTBLENDE MIT ZAPFEN
==============================================================

Anlass: Modulprobe 1 (stl/steckmodul_display_modul/): Das Modul passt, die Decke über der Tasche löste sich vom Support, die Zapfen kamen nur etwa 0,5 mm ins Loch.
Entscheidung des Nutzers nach Plan 4: Decke A (Kappe) und Zapfen P1, Loch Ø 2,55. Alle Werte sind Planwerte (plug/display/params.py), nichts davon ist gedruckt.

Was sich gegenüber Modulprobe 1 geändert hat
  Aufnahme         Oben offen, keine Decke mehr, kein Support. Die Seitenwände und die Rückwand enden an der Oberkante der Tasche (34,10 über dem Boden).
  Blende (Kappe)   Hat oben eine Lippe 1,0 mm dick, die über die Tasche und 1,0 mm über die Rückwand reicht und als Dach auf den Wänden liegt. Die Blende liegt flach, die Lippe steht als Rippe nach oben.
  Tasche           Breite 35,94 (0,32 Luft je Seite), Höhe 34,10 (Modul als 33,80 angenommen, oben 0,30 Luft), Dicke 5,10.
  Sackloch         Ø 2,55 (Modulprobe 1: 2,5), 2,6 tief, Einführfase 0,3.
  Zapfen P1        Spitze Ø 1,8, Kegel über 2,2 mm (11 Lagen) auf den vollen Durchmesser, dann zylindrisch. Blende M2: Enddurchmesser 2,4, Blende M3: 2,5
                   (etwas fester). Im Sackloch 2,4 tief. Im echten Körper bleibt hinter dem Sackloch mindestens 1,0 mm Material.

Teile
  M1_aufnahme.stl             8,7 × 38,3 × 35,3 mm  Kopf mit Tasche (oben und vorn offen), Kabelfenster in der Rückwand, vier Sacklöcher
  M2_blende_A_zapfen_2_4.stl  36,3 × 38,3 × 8,7 mm  Blende mit Lippe, Fenster und vier Zapfen, Ende Ø 2,4
  M3_blende_B_zapfen_2_5.stl  36,3 × 38,3 × 8,7 mm  dieselbe Blende, Zapfen Ende Ø 2,5

Druckausrichtung (so liegen die Dateien schon)
  M1  stehend auf der Kopfunterseite (Tasche und Sacklöcher liegen waagerecht wie im echten Körper), kein Support nötig.
  M2, M3  flach, Außenfläche unten, Zapfen und Lippe zeigen nach oben, kein Support. Eine Blende reicht, die zweite für den Vergleich.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3, kein Brim. Druckzeit geschätzt (nicht kalibriert):
M1 25 min, M2 14, M3 14 min.

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
