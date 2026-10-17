# Slicer-Einstellungen für die steckbaren Gebäude

Gilt für die Hohlgebäude der Steckplatte (`stl/steckmodul_campus/gebaeude/*.stl`, erzeugt mit `python3 -m plug.buildings`, Maßstab 1:1300).
Stand 2026-10-17. **Alle Werte sind Empfehlungen, noch nicht gedruckt.** Nach dem ersten Druck hier eintragen, was sich bewährt hat
(Abschnitt „Erfahrungen“ unten), und den Stand im Logbuch (`plug/logbook/scale.md`) nachziehen.

Für Claude-Agenten: Diese Datei ist die eine Quelle für Slicer-Einstellungen der steckbaren Gebäude. Verweise stehen in `CLAUDE.md`,
`plug/CLAUDE.md` und in `stl/steckmodul_campus/gebaeude/README.md`. Werte hier ändern, nicht in Kopien.

## Kurzfassung

| Einstellung | Wert | Warum |
|---|---|---|
| Ausrichtung | wie exportiert: Boden auf dem Bett, Schacht nach unten offen | Gebäude ist dafür gebaut (45°-Gewölbe, 45°-Anschlag) |
| Support | **aus** | im Gebäude ist nichts über 2,1 mm frei auskragend (Prüfung je 0,2-mm-Lage) |
| Schichthöhe | 0,2 mm | Prüfung und Dachstärke (0,8 = 4 Lagen) sind darauf gerechnet |
| Düse | 0,4 mm | Wand 0,8 = 2 Linien |
| Wandlinien (Wall loops / Perimeter) | 2 | Wand 0,8 mm, keine Füllung in der Wand |
| Wandgenerator | Arachne (Standard in Bambu Studio und Orca) | sauberere dünne Stellen |
| Obere Deckschichten | 4 | Dach 0,8 mm |
| **Untere Deckschichten** | **2** | die 45°-Unterseiten der Gewölbe zählen als Unterseite; mehr Schichten geben dort eine dichte, lichtschluckende Haut |
| **Füllmuster** | **Gyroid** | gleichmäßig in alle Richtungen, keine durchgehenden Ebenen: Licht streut gleichmäßig, keine Schattenstreifen auf der Wand; trägt sich selbst |
| **Fülldichte** | **10 %** (Rückfall 15 %) | wenig Material, viel Licht; die Keile tragen nur das Dach |
| **„Ensure vertical shell thickness“** (Bambu/Orca; PrusaSlicer: „Ensure vertical shell thickness“) | **aus** | sonst füllt der Slicer an den 45°-Schrägen zusätzlich massiv |
| Bügeln (Ironing) | aus | unnötig |
| Rand (Brim) | City-Hochhaus: ja, 5 mm; sonst nein | Hochhaus ist 125 mm hoch auf 36 × 35 mm Grundfläche |
| Filament | PLA weiß oder natur | leitet am meisten Licht |

## Füllmuster im Vergleich (für das Licht der LED)

Die LED sitzt über dem Schachtrohr; ihr Licht geht durch die Füllung der Gewölbe-Keile und dann durch die Wand (0,8 mm). Die Füllungsart
bestimmt also, wie gleichmäßig das Gebäude leuchtet.

| Muster | Licht | Material | Bemerkung |
|---|---|---|---|
| **Gyroid** | gleichmäßig gestreut | mittel | Empfehlung |
| Blitz (Lightning) | am meisten Licht | am wenigsten | unregelmäßige Äste, fleckige Schatten; trägt nur das Dach |
| 3D-Waben (3D Honeycomb) | ähnlich gleichmäßig | mittel | Rückfall, wenn Gyroid Probleme macht |
| Gitter, Linien, Dreiecke | gerade, harte Schattenstreifen | mittel | vermeiden, Streifen sieht man durch die dünne Wand |

## Was das Modell schon mitbringt (nicht im Slicer nachbauen)

- Gewölbe in 45° über allen Räumen, Spalten unter 2 mm sind gefüllt, keine Taschen über dem Gewölbe.
- Schacht für die Kassette mit Einführfase am Bett und Anschlag mit 45°-Unterseite; Freiraum für LED, Streifen und Blatt mit 45°-Walm.
- Boden 1,2 mm über die ganze Grundfläche, Fuß 14,2 mm mit Fase an der Bettkante.
- Prüfwerte je Gebäude (Volumen, Brücken, Kragstücke, Kollision mit der Kassette): `stl/steckmodul_campus/gebaeude/<slug>_1zu1300.json`.

## Erfahrungen

Noch keine (ungedruckt). Nach dem ersten Druck hier eintragen: Drucker, Slicer und Version, Abweichungen von den Werten oben, Ergebnis
(Gewölbe sauber? Licht gleichmäßig? Kassette passt?).
