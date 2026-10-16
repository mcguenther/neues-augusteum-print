# Maßstab, Mulden und Kassettenwahl (festgelegt am 2026-10-16)

Entscheidungen des Nutzers im Chat; Rechnung und Grafiken: `plug/scale1176/page.html` (Artifact https://claude.ai/artifact/S3qGmVQRr9tAPNqm2NyLQx, Ordnername von der ersten Fassung bei 1:1176).
**Alles Planung, nichts gedruckt, keine STL.** Werte in `plug/parts.py` und `plug/testcase/params.py` sind noch nicht umgestellt.

## Festgelegt

| Punkt | Entscheidung | Beleg |
|---|---|---|
| Größe der Platte | höchstens 230 × 230 mm (Druckbett mit Reserve) | Nutzer |
| Maßstab | **1:1250** (Grenze für 230 mm ist 1:1242); Platte 119,7 × 228,7 mm, einteilig | `plug/scale1176/page.html`, Abschnitt Maßstab |
| Muldentiefe | **überall 4 mm tiefer**: F 14,2 statt 10,2 mm, Platte 20,2 statt 16,2 mm; die LED liegt dadurch 4 mm tiefer gegenüber dem Dach | Nutzer, Vorschlag aus dem senkrechten Schnitt |
| Standard-Kassette | **v4** (LED strahlt nach oben), überall wo sie passt | Nutzer |
| City-Hochhaus | **V2R** (zwei LEDs, hochkant, Konzept aus `cassettes.md`), weil v4 dort nicht passt | Nutzer |
| Innenhof | eigenes Einsteckteil, Bäume angedruckt (Empfehlung, noch nicht ausdrücklich bestätigt) | Seite, Abschnitt Innenhof |

## Rechnung für diese Festlegung (Maßstab 1:1250, Mulde +4 mm, Wand 0,8 mm Mindestmaß)

Größte Wand um den Schacht bei Grundriss und Höhe zusammen und Luft von der LED-Mitte bis zum Dach an der höchsten Stelle, an der der Schacht passt. LED v4: 2,9 mm über der Platte (6,9 − 4).

| Gebäude | Kassette | Wand mm | Dachhöhe mm | Luft LED bis Dach mm |
|---|---|---|---|---|
| Paulinum | v4 | 1,2 | 23,9 | 21,0 |
| Neues Augusteum | v4 | ≥ 3,0 | 12,5 | 9,6 |
| Hörsaalgebäude | v4 | ≥ 3,0 | 14,6 | 11,7 |
| Seminargebäude | v4 | 0,9 (knapp) | 19,2 | 16,3 |
| Institutsgebäude | v4 | 1,9 | 7,3 | **4,4** |
| City-Hochhaus | V2R | ≥ 3,0 | 95,7 | 84,1 |

## Offen aus dieser Festlegung

- **Institutsgebäude:** nur 4,4 mm Luft über der LED, der Schacht darf nur unter dem niedrigen Dachteil (7,3 mm hoch) liegen. Richtwert 8 mm ist eine Annahme, ungetestet. Möglichkeiten: Kassette dort anders legen, V1 (Luft 12,3 mm bei +4 mm, LED dort 6,9 mm über der Platte, strahlt aber seitlich), oder nur dort tiefer.
- **Seminargebäude:** Wand nur 0,9 mm (knapp).
- **Hochhaus V2R:** Konzept, Streifendicke 2,2 mm nicht gemessen, Adern und Verkettung ungetestet; das Hochhaus braucht eine Kassette V2R mit Schacht 12,96 × 6,4 mm und Gebäude mindestens 23,9 mm hoch (es ist 116 mm hoch). Die LED blickt dort seitlich, nicht nach oben.
- **Fuß 14,2 mm** statt 10,2 mm ist nicht getestet (Führung in der Mulde, Kippen). Dock, Kabelraum, Muldenboden und Platte rücken 4 mm tiefer; Platte 20,2 mm dick.
- Schächte sind noch Vollkörper im Generator (kein Hohlraum, kein Lichtfenster im Gebäude).
- Licht durch die Wand und Druckbarkeit der 0,8-mm-Stämme des Hofs bei 1:1250: nur ein Probedruck zeigt es.
