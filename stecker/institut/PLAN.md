# Institutsgebäude mit Kassette (Plan B, Rückfallebene am echten Gebäude)

Zeigt, wie die Kassette aus `stecker/dupont/PLAN.md` in einem echten Gebäude funktioniert: dem
Institutsgebäude (Laserscan, 1:1000), mit Fuß, Lichtkammer, Lichtfenstern und einer Platte mit Dock A.

- Anschauen: `stecker/institut/ansicht.html` (Zusammenbau-Animation, Einstecken, Schnitte, Explosion)
- Erzeugen: `python3 steckmodul_institut.py` (STL nach `stl/steckmodul_institut/`, Bilder nach
  `vorschau/steckmodul_institut/`, Daten nach `stecker/institut/daten.json`, rund 45 s), danach
  `python3 stecker/institut/baue_ansicht.py`.

## Was anders ist als beim Würfel

- **Großzügige LED-Ablage** (`SEAT_W` × `SEAT_L` = 13,0 × 21,0 mm, vorher 10,3 × 17,0 mm): Streifen bis 12 mm
  Breite und 21 mm Länge, Lage frei, Din-Ende zur Buchse. Die Bodenöffnung im Gebäude ist 0,15 mm je Seite größer.
  Die Kassette ist dadurch 15,7 × 29,1 mm groß.
- **Schieber quer durch die lange Wand** (Schwalbenschwanz entlang x, 20,1 × 33,8 × 1,0 mm) statt längs durch
  das Gebäude: kurzer Weg von etwa 21 mm. Er schließt mit der Fußfase bündig ab, die Muldenwand sperrt ihn.
- **Fuß aus dem echten Grundriss**: Grundriss nach unten extrudiert, Kanten gerundet (0,5 mm), unten 0,8 mm Fase in
  Schichtstufen (0,2 mm); Mulde folgt mit 0,25 mm Spiel im Führungsband, darunter 0,55 mm, oben 1,0 mm Fase.
  Keine Kodier-Ecke: Der Grundriss passt nur in einer Richtung.
- **Lichtkammer**: je Höhe der um 1,2 mm geschrumpfte Querschnitt des Gebäudes in 1,2 mm höherer Lage, damit Wand und
  Dach überall mindestens 1,2 mm dick bleiben (`chamber()`). Zwei Reihen Lichtfenster, auf 0,4 mm abgedünnt.
- **Platte**: Mulde nach dem Fußumriss, nur Dock A (20,0 mm dick mit Deckel), Federzunge in der langen Muldenwand.

## Maßstab

Bei 1:1000 ist der Hauptbalken 22,0 mm breit (Wand neben dem Schacht 3,0 mm). Bei 1:1500 sind es 14,7 mm: Die Kassette
passt dort nicht. Dafür bräuchte sie eine schmalere Ablage (etwa 5-mm-Streifen).

## Offene Punkte

- Der Schieber ist nur 1,0 mm dick und kann sich verziehen; zuerst Kassette und Schieber allein in einem Probestück testen.
- Das Dach der Kammer überbrückt im breiten Flügel bis etwa 30 mm; Brückenerkennung des Slicers nutzen.
- Federzunge und Haltekräfte stammen aus dem Dupont-Plan und sind für diese Wand nicht neu gerechnet.
