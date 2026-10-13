# Laufzeit von `generate.py`

Messung vom 13.10.2026 auf 4 Kernen. Ist-Stand = Stand vor der Optimierung
(`phasen_ist_stand.py` misst ihn über Funktions-Wrapper; Zahlen in `messwerte.json`).

![Laufzeit je Phase](laufzeit_vergleich.png)

## Wo die Zeit hinging (Ist-Stand, 1416 s)

| Phase | Zeit | Anteil |
|---|---|---|
| Farbvorschauen (Software-Renderer, 12 Aufrufe à 2 Ansichten + Kacheln) | 587 s | 41 % |
| Vorschaubilder je Quelle + Quellenvergleich | 390 s | 28 % |
| Modelle bauen, färben, exportieren | 175 s | 12 % |
| README-Bilder | 189 s | 13 % |
| Fassaden-Prüfansichten | 74 s | 5 % |

Die **Geometrie** (OSM, LoD2, Laserscan zusammen) braucht nur ~17 s. Die Laserdaten bremsen
indirekt: Das Laser-Modell hat ~500 000 Dreiecke, und der Renderer rasterte jedes einzeln in
einer Python-Schleife (~85 µs je Dreieck). 82 % der Laufzeit sind Rendering.

## Maßnahmen

| Maßnahme | Wirkung | Ergebnis |
|---|---|---|
| `preview.rasterize`: kleine Dreiecke gestapelt vektorisiert statt einzeln | Rendern 3–12× schneller | pixelgleich (getestet gegen alte Funktion) |
| `colourise`-Cache: `campus` ist Teilmenge von `campus_mit_extras` | Färben halbiert | gleiche Geometrie (Fläche/Volumen, dicht); einzelne Mikrodreiecke können durch Rundung abweichen |
| `fassaden.colour_mesh`: Dichtheitsprüfung nur am Ende statt nach jedem Schnitt | Färben −30 % | bitidentisch, Rückfall auf die alte Schleife, falls nicht dicht |
| `parallel.py`: Builds, Render-Jobs, Vorschauen, README-Bilder, Fassadenansichten auf alle Kerne | ~2× auf 4 Kernen | identisch |
| `--fast` | siehe unten | gleiche Daten, gröber |

## Vergleich

| Variante | Zeit | Faktor |
|---|---|---|
| Ist-Stand | 1416 s (23:36) | 1× |
| Rasterizer + Färb-Cache, seriell | 600 s | 2,4× |
| + Parallel (Standardlauf heute) | 313 s | 4,5× |
| Standardlauf nur `--scale 1500` | 170 s | 8,3× |
| `--fast`, beide Maßstäbe | 147 s | 9,6× |
| `--fast` (nur 1:1500) | 74 s | 19× |
| `--fast --quelle laserscan` | 68 s | 21× |
| `--fast --jobs 1` (seriell) | 125 s | 11× |

`--fast`: Laser-Raster 0,6 statt 0,3 m (¼ der Dreiecke), Vorschau ohne Kantenglättung,
nur Maßstab 1:1500, keine README-/Fassaden-/Vergleichsbilder; schreibt nach `stl-fast/` und
`vorschau-fast/`. Die Zeiten schwanken durch Last auf der Maschine um etwa ±10 %.
