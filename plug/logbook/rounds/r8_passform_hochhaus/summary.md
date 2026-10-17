# r8: Passform Hochhaus (gedruckt und ausgewertet, 2026-10-17)

**Status: gedruckt und ausgewertet.** Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorener Satz: [`passform_stummel_hochhaus.zip`](passform_stummel_hochhaus.zip) (Stand Commit „STL der ersten Passform-Runde Hochhaus“).

## Ziel und Teile

Ob ein Gebäude (City-Hochhaus, Laserscan 1:1300) mit dem vollen Grundriss in die Mulde der gedruckten flachen Steckplatte (14,6 mm, Spiel 0,10) passt, und ob die Kassette V2R in den Schacht geht.

- `H1_stummel_hochhaus.stl`: Hohlgebäude `06_city_hochhaus_1zu1300_fase2.stl` bei 25 mm über der Plattenoberfläche abgeschnitten (gesamt 39,2 mm), Fuß 14,2, Boden 1,2, Schacht V2R, Wand 0,8, **Fuß-Fase 2,0 mm** (45°), Spiel 0,10.
- `H2_kassette_V2R.stl`: Probeteil Kassette V2R (Konzept), 13,0 × 6,4 × 36,9 mm.
- Generator `python3 -m plug.footfit.build_stub`, Plan `plug/footfit/plan.html` (https://claude.ai/artifact/4y69fZRDpEMGBtrZSbDt1c), Testbogen `plug/footfit/feedback.html` (https://claude.ai/artifact/8u4RqPrrBj2tM8PKUa32q2). Prüfbericht: dicht, Kassette im Schacht ohne Kollision, Stummel in der echten Steckplatte ohne Kollision (Kontrollen stoßen an).

## Ergebnis

| Punkt | Ergebnis | Status |
|---|---|---|
| Einsetzen in die Mulde (Spiel 0,10) | **nur mit Kraft** | **verworfen (zu eng)** für die große Fläche |
| Herausziehen | **sehr fest** | zu fest, gleiche Ursache |
| Wackeln eingesetzt | nein | – |
| Fase unten 2,0 mm | fängt das Gebäude: ja; Wulst unten: keiner; sitzt auf dem Muldenboden auf: ja | **bewährt** |
| Kassette V2R: Druck | sauber (dünnes Blatt, frei stehend) | bewährt (nur Probeteil) |
| Kassette V2R im Schacht | Sitz gut, Wand nicht gerissen, unten bündig | bewährt (nur Unterbau im Schacht; Streifen, Adern, Licht nicht getestet) |
| Pins treffen die Buchse | ja | bewährt |
| Druckzeit | ca. 55 min (beide Teile) gegen geschätzt 47 min | Schätzung etwa 17 % zu niedrig |

## Entscheidungen und Folgen

- **Spiel 0,15 beim nächsten Probedruck testen (Vorgabe des Nutzers).** Der Nutzer will genau diese Zahl; 0,10 war an der kleinen Fuß-Lehre bewährt (r4), geht bei einem 36 × 35 mm großen Umriss aber nur mit Kraft. Umsetzung: Die Mulde der gedruckten Platte hat 0,10; ein Stummel mit 0,15 hat den Umriss 0,05 mm je Seite kleiner (Skalieren oder Umriss-Versatz im Generator); eine neue Platte bekäme `OUTLINE_CLR_T = 0.15`. Bis zum Test bleibt 0,10 im Code.
- **Fuß-Fase 2,0 mm bleibt**: jetzt in `plug/buildings.py` (`FUSS_FASE_T`, nach dem Aushöhlen angebracht, Wand bleibt 0,8). Die eingecheckten Gebäude-STL (`stl/steckmodul_campus/gebaeude/`) haben noch die alte Fase 0,5; neu bauen mit `python3 -m plug.buildings`.
- Kassette V2R ist als Unterbau im Schacht bewährt; offen bleiben LED-Streifen auf dem Blatt, Adern, Verkettung, Licht.
- Zeitschätzung der Planseite mit Faktor 1,2 multiplizieren (Start und Mindestzeit je Lage eher höher ansetzen).
