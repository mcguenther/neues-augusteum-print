# Steckbare Gebäude farbig (1:1300)

Erzeugt mit `python3 -m plug.colour` aus den Gebäuden in `../gebaeude/` (gleiche Geometrie, gleiche Lage) und dem Hof-Einsatz.
Filamente des Nutzers (Hex-Werte geschätzt, in `farben.FILAMENTE` anpassen): Beige `#e6d6bc`, Graublau `#6b7d8c`, Weinrot `#7b2433`, Space Grey `#4a4e54`, Weiß `#f3f3f0` (vorerst nicht verwendet), Schwarz `#1f2022` (Reserve), Grasgrün `#4f9a3c` (Reserve).
Höchstens 4 Filamente je Druck. 3D-Ansicht: `plug/views/farbig/view.html`. Slicer-Einstellungen: `plug/slicer.md`.

| Datei | Filamente (Slot 1–4) | Anteile der Außenfläche | ΔE (nur Hauptfarben) | einfarbig (`*_einfarbig.3mf`) |
|---|---|---|---|---|
| `01_paulinum_1zu1300_farbig.3mf` | Beige, Graublau, Space Grey | Beige 4 %, Graublau 83 %, Space Grey 12 % | 9.3 (9.3) | Graublau |
| `02_neues_augusteum_1zu1300_farbig.3mf` | Beige, Graublau, Space Grey | Beige 16 %, Graublau 70 %, Space Grey 14 % | 8.4 (8.4) | Graublau |
| `03_hoersaalgebaeude_1zu1300_farbig.3mf` | Beige, Graublau, Weinrot, Space Grey | Beige 62 %, Graublau 17 %, Weinrot 19 %, Space Grey 2 % | 18.3 (18.3) | Beige |
| `04_seminargebaeude_1zu1300_farbig.3mf` | Beige, Graublau, Weinrot, Space Grey | Beige 66 %, Graublau 3 %, Weinrot 4 %, Space Grey 27 % | 14.4 (14.4) | Beige |
| `05_institutsgebaeude_1zu1300_farbig.3mf` | Beige, Graublau, Weinrot, Space Grey | Beige 61 %, Graublau 10 %, Weinrot 7 %, Space Grey 23 % | 16.0 (16.0) | Beige |
| `06_city_hochhaus_1zu1300_farbig.3mf` | Beige, Graublau, Space Grey | Beige 27 %, Graublau 70 %, Space Grey 3 % | 21.6 (21.6) | Graublau |
| `08_innenhof_1zu1300_farbig.3mf` | Beige, Space Grey, Grasgrün | Beige 65 %, Space Grey 29 %, Grasgrün 6 % | 23.4 (22.8) | Beige, Grasgrün |

`alle_1zu1300_hauptfarben.3mf`: alle Gebäude und der Hof-Einsatz in einem Druck mit den vier Hauptfarben (Lage wie auf der Steckplatte).

Einfarbig (wenig Filamentwechsel): jedes Gebäude in einer Farbe, nur der Hof-Einsatz hat grüne Baumkronen (Wechsel nur in den Lagen der Kronen).
Gebäude mit derselben Farbe lassen sich zusammen ohne Wechsel drucken.

Im Slicer die Filamentfarben einmal den Slots zuordnen (die 3MF nennt die Namen als Material F1 … F4); bemalt sind die Außenflächen,
Innenflächen haben die Farbe der nächsten Außenwand, der Fuß eine einzige Farbe. Ungedruckt.
