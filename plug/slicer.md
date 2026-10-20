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

## Farbig drucken (`stl/steckmodul_campus/gebaeude_farbig/`)

Dieselben Gebäude als 3MF mit bemalten Außenflächen (`python3 -m plug.colour`), je Gebäude höchstens 4 Filamente aus Beige, Graublau, Weinrot,
Space Grey (Hauptfarben) und Schwarz, Grasgrün (Reserve; Weiß vorerst nicht, wird Beige); welcher Satz zu welchem Gebäude gehört, steht in der README dort.
Einstellungen wie oben; dazu im Slicer die vier Filamente in der Reihenfolge der 3MF (F1 … F4) den Slots zuordnen. Der Fuß ist einfarbig
(kein Wechsel in den ersten 14 mm), die Innenflächen tragen die Farbe der nächsten Außenwand, damit die 0,8-mm-Wand durchgefärbt ist.
Wenig Wechsel: `*_einfarbig.3mf` (jedes Gebäude eine Farbe, nur der Hof-Einsatz wechselt in den Lagen der Baumkronen auf Grasgrün); Gebäude derselben Farbe zusammen auf ein Bett legen. Farbiges PLA lässt weniger LED-Licht durch als weißes; ungetestet. Spülmenge (Flush/Purge) je Wechsel ist der größte Materialposten:
im Slicer „Flush into objects' infill“ an, wo vorhanden.

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

## Prüfen, ob der Slicer das Gebäude hohl sieht

In der Schichtvorschau eine Schicht im Fuß (etwa 8 mm über dem Bett) und eine auf Höhe des Anschlagrings (etwa 18,4 mm) ansehen: es
dürfen nur dünne Wandringe (Außenwand, Schachtrohr, innere Wände) zu sehen sein, Füllung (Gyroid) nur in den Keilen über den Gewölben.
Eine durchgehende Füllfläche über den ganzen Grundriss heißt: der Slicer hat beim Laden Flächen umgedreht und den Innenraum zu Material
gemacht (so beim Paulinum bis 2026-10-18, Ursache und Abhilfe in `plug/logbook/scale.md`, Abschnitt „Steckbare Hohlgebäude“, „Im Slicer
massiv“). Die senkrechte helle Linie an einer Außenwand ist die Naht (Seam, „Aligned“), kein Spalt.

Ohne Drucker prüfbar: `python3 -m plug.export_campus` vergleicht, wenn `prusa-slicer` installiert ist (`apt-get install prusa-slicer`),
das Volumen nach dessen Reparatur beim Laden mit dem Netzvolumen (Spalte „Slicer-Volumen“ im Prüfbericht). Schichten selbst ansehen:
`prusa-slicer --export-gcode --load <ini> datei.stl` mit den Werten der Kurzfassung (`use_relative_e_distances = 1`), dann die Linienarten
(`;TYPE:`) je Schicht auswerten. Die SLA-Ausgabe (`--export-sla`) taugt dafür nicht: sie füllt geschlossene Innenräume immer.

## Erfahrungen

- **r8 (2026-10-17), Passform-Stummel Hochhaus und Kassette V2R, Bambu A1, schwarzes PLA, Düse 0,4, 0,2 mm, Wände 2 oder mehr, kein Support:** beide Teile ohne Support sauber gedruckt, auch das frei stehende 1,2-mm-Blatt der Kassette; Fuß-Fase 2,0 mm ohne Elefantenfuß-Wulst; Druckzeit beide Teile ca. 55 min (Schätzung der Planseite 47 min). Das ganze Gebäude (Gyroid 10 %, Brim) ist noch nicht gedruckt.

- **City-Hochhaus, Slicer-Vorschau (2026-10-20, noch nicht gedruckt):** der Slicer meldete „schwebende Regionen“ und zeigte am Fuß einen Wulst, der nach einigen Schichten verschwindet. Behoben im Modell (Fuß-Fase rundum, gefüllte Gewölbespitzen hängen am Material, siehe `plug/logbook/lessons.md` L45). Die STL von Paulinum, Augusteum, Hörsaal-, Seminar- und Institutsgebäude sind noch im alten Stand und können dieselbe Meldung geben. Eine Insel im Sinn des Slicers ist eine Lage mit Material, das in der Lage darunter keinen Nachbarn hat; sie lässt sich ohne Slicer lagenweise prüfen (Skript in der Chat-Sitzung, noch nicht im Repo).

Weitere Erfahrungen hier eintragen: Drucker, Slicer und Version, Abweichungen von den Werten oben, Ergebnis (Gewölbe sauber? Licht gleichmäßig? Kassette passt?).
