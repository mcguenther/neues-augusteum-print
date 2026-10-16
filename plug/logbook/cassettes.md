# Kassetten-Varianten (Register)

Stand: 2026-10-16. **Alle Varianten sind Konzepte: nicht abgenickt, keine STL, nichts gedruckt.** Sie lösen das Problem, dass die Kassette v4 (13,5 × 29,4 × 17,1, Streifen flach hinter der Buchse)
im Maßstab 1:1500 nicht in jeden Grundriss passt (Seminargebäude, City-Hochhaus, Paulinum; Institutsgebäude nur 0,4 mm Wand). Plan und Grafiken: `plug/testcase/plan3.html`
(Artifact https://claude.ai/artifact/RqSFYxH8ZggxvdjQY93nTe, privat). Geometrie: `plug/testcase/variants.py`. Vorgeschichte: [r4](rounds/r4_steckprobe2/summary.md), Nachträge 1 bis 4.

## Gemeinsamer Unterbau (wie v4, bewährte Werte gelten weiter)

Buchsentasche 10,56 × 2,94, Tasche 14,60 hoch (Plan Steckprobe 2), Schultern 0,5 dick, Aderschlitz 9,2 breit, Wand 1,2, Pin-Reihe bei y = 2,67 von der Vorderseite, Fase unten 0,5, Einpressen 0,06 je Seite.
Schulterfläche bei z = 15,10 (Kassettenunterkante bündig mit der Fußunterkante, Platte bei z = 10,2). Dock, Winkelleiste, Mulde und Pins bleiben unverändert.

Neu bei allen: der LED-Streifen steht auf einem dünnen **Blatt** (1,2 mm) über der Buchse; die LED blickt nach vorn (−y). Streifen 10 × 16,7 × 2,2 (Folie 0,3, Chip 5 × 5 × 1,9); **Streifendicke 2,2 ist nicht belegt, vor der STL messen.**

## Die Varianten

| Name | Streifen | Grundfläche | Kassette hoch | Gebäude ab | LED-Mitte über Platte | Besonderheit |
|---|---|---|---|---|---|---|
| v4 (Steckprobe 1) | flach, 1 | 13,5 × 29,4 | 17,1 | 8,1 | 6,9 | Podest, Rundung; bleibt für breite, niedrige Gebäude |
| **V1** | quer (16,7 waagerecht, 10 hoch), 1 | 17,2 × 5,34 | 26,4 | 17,3 | 10,9 | Adern seitlich unter dem Streifen zum Pad-Ende (verdrillt, ungetestet) |
| **V2** (bevorzugt) | hochkant (10 breit, 16,7 hoch), 1 | 12,96 × 5,34 | 33,5 | 24,5 | 14,8 | Adern gerade nach oben; Mast verlängerbar |
| **V2R** | hochkant, 2 (vorn und hinten) | 12,96 × 6,4 | 36,9 | 27,9 | 15,6 | Blatt oben 45° nach vorn versetzt; Verkettung über die Blattkante |
| **V1R** (oben) | quer, 2 | 17,2 × 6,4 | 30,2 | 21,2 | 12,2 | Versatz wie V2R; Verkettung über die Oberkante am rechten Ende (Blatt 2,5 höher) |
| **V1RS** (seitlich) | quer, 2 | 19,2 × 6,4 | 27,7 | 18,7 | 12,2 | Unterbau 2 mm breiter, Blatt samt Streifen 1 mm nach links; Verkettung am rechten Blattrand vorbei (2,0 Platz) |

Namen im Code: `V1`, `V2`, `V2R`, `V1R`, `V1RS` (`variants.dims(name)`). „Gebäude ab“ = Kassettenoberkante über der Platte (Fuß 10,2) plus 1,2 Dach.

## Rücken-LED (V2R, V1R, V1RS): warum der Versatz

Die Kassette wird mit dem Streifenende voran von unten durch den Schacht im Fuß geschoben, also muss jeder Querschnitt durch den Schacht passen. Mit dem Blatt hinten (y 4,14 bis 5,34) ragt der Rücken-Chip bis y = 7,54 und damit 2,1 mm hinter die Schachtwand.
Lösung (Vorschlag des Nutzers): Blatt oben in die Mitte versetzen (Vorderseite y = 2,6, Versatz 1,54 als 45°-Schräge, zuerst 0,8 an der hinteren Wand hoch). Chip zu Chip 5,6 (2 × 2,2 + 1,2), Unterbau 6,4 tief, Luft 0,4 vorn und hinten.
Der hintere Streifen ist um 180° gedreht aufgeklebt; die Streifen sind verkettet (DOUT des vorderen an DIN des hinteren, drei kurze Adern), nur ein Satz Adern von der Buchse. Zwei LEDs: etwa 120 mA bei Weiß.

## Offene Punkte

- **Fit in die Gebäude: zurückgestellt**, bis der Maßstab ganz genau feststeht. Zwischenstand (`plug/testcase/variants_fit.json`, Wand ab 1,2 mm, Schnitt in der nötigen Höhe): bei 1:1500 passt V2 in City-Hochhaus und Paulinum, V2R nur ins Hochhaus; bei 1:1000 kommt Neues Augusteum dazu. V1R und V1RS sind darin **nicht** enthalten.
  Seminargebäude 1:1500: geschlossenes Dach nur etwa 16,4 mm, nichts passt; flache Variante V3 (Streifen neben der Buchse, etwa 31 × 10,5) käme auf 1,0 mm Wand, ungeplant.
- Adernweg bei V1, V1R und V1RS (seitlich, Verdrillen zu den Pads): ungetestet.
- Blatt dünn und hoch (L06), Biegung quer zu den Schichten: Blattdicke 1,2 oder 1,6 (Empfehlung 1,6 mit Hohlkehle R 1) offen; bei zwei Streifen verschärft.
- Versatz als 45°-Überhang über dem Aderschlitz: druckbar, ungetestet.
- Anschlagleiste im Schacht über dem Unterbau (vorn etwa 1,7 mm): noch nicht gezeichnet.
- Licht: LED blickt seitlich auf die Wand (Hotspot im schmalen Gebäude); Streifenlänge 144 LED/m (13,9 lang, 12 breit) würde 2,8 mm sparen.
- Streifendicke 2,2 und Chiphöhe 1,9 messen.
- Entscheidungskarten in `plan3.html` (Rücken-LED, Verkettung, Varianten, Seminargebäude, Blatt, LED-Höhe, V1R-Probedruck, Streifenlänge, Probedruck) sind unbeantwortet.

## Vorschlag Probedruck (noch nicht abgenickt)

V2 einseitig ×2 (Blatt 1,2 und 1,6), V2R ×1, V1R ×1, V1RS ×1; Mini-Turm auf dem bisherigen L-Fuß (24 × 38), passend zur vorhandenen Mulde der Mini-Grundplatte B; Schacht je Unterbau (5,34 bzw. 6,4 tief).
Geprüft: Einpressen mit Blatt und Streifen (geht der Rücken-Streifen mit durch?), Kleben, Adernweg, Verkettung, Licht, Abziehen.

## Neu erzeugen

| Befehl | Erzeugt |
|---|---|
| `python3 -m plug.testcase.variants` | Konzeptgeometrie (Dichtheit), Bilder `vorschau/steckmodul_testcase/varianten_v1_v2.png`, `variante_v2r.png`, `variante_v1r.png`, `variante_v1rs.png` |
| `python3 -m plug.testcase.fit_study` (ca. 2 min) | Passstudie in den Laserscan-Grundrissen nach `plug/testcase/variants_fit.json` (V1R und V1RS fehlen noch) |
| `python3 -m plug.testcase.build_plan3` | `plug/testcase/plan3.html`, danach als Artifact veröffentlichen |
