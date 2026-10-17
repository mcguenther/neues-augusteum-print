# r7: Steckplatte 1:1300 (gedruckt, Rückmeldung 2026-10-17)

**Status: gedruckt, Rückmeldung eingetragen; Änderungen umgesetzt als Vorschlag, wartet auf die Prüfung des Nutzers an der 3D-Seite.**
Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorene gedruckte Fassung: [`steckplatte_v1_gedruckt.stl`](steckplatte_v1_gedruckt.stl) (Platte 115,6 × 220,8 × 14,6 mm, flache Unterseite, 24 Pin-Löcher, Schrift graviert).

Teil: `stl/steckmodul_campus/steckplatte_1zu1300.stl` aus `python3 -m plug.campus` (Konzept des Test-Docks: Muldenboden 0,4 als unterste Schicht, keine Hohlräume, ohne Support).

## Ergebnis

| Beobachtung | Bewertung | Folge |
|---|---|---|
| Druck insgesamt | funktioniert | – |
| Unten kein Elefantenfuß (Bettfase 0,5) | **bewährt** | `EF_CH_T` 0,5 gilt auch für die Steckplatte |
| Oben ein Wulst über die letzten 5 bis 7 Schichten | schlecht | Fase an der oberen Außenkante **1,5 mm** (`PLATE_TOP_CH_T`, Nutzer: 1,5 bis 2 mm) |
| Schrift und Nordpfeil graviert nicht lesbar | schlecht (L01 bestätigt) | **erhaben** 0,6 mm (`LABEL_RAISE_T`), `engrave_labels(raised=…)` |
| Wand zwischen Hof und Institut/Seminar (0,4 mm) fehlt | in Ordnung | keine Änderung; Hof zuletzt einsetzen, die Gebäude sind die Trennwände |
| Öffnungen der Gebäude-Mulden | Zuquetschung befürchtet | Einführfase oben mindestens **0,5 mm** (`MULDE_CH_T`, in Stufen, bis über die Oberkante) |

## Umgesetzt (Planwerte, ungetestet)

`plug/campus.py`: `top_edge()` (Fase oben), `mulde_body()` mit Einführfase, erhabene Schrift; `generate.py`: `engrave_labels(..., raised=0.0)`, Standard unverändert; Werte in `plug/testcase/params.py`.
Beschriftungsblock um die Fasenbreite (1,5) nach innen gerückt (`engrave_labels(inset=…)`), Abstand zur ebenen Fläche mindestens 1,9 mm. Prüfung: dicht, kein Überhang (nur die Stufen der Bettfase, 0,2 mm), Schrift liegt komplett im Beschriftungsstreifen weiter als 1,8 mm vom Rand.
Interaktive Vorschau: `python3 -m plug.views.campus.build_view` → `plug/views/campus/view.html` (neu und gedruckt umschaltbar, feste Ansichten je Änderung).

## Offen

- Fase 1,5 oder 2 mm oben: erst der nächste Druck zeigt, ob der Wulst weg ist (Fase wirkt, wenn sie tiefer ist als der Wulst, 5 bis 7 Schichten = 1,0 bis 1,4 mm).
- Fase oben am Hof aufgenommen? Nein, der Hof bleibt ohne (Wand zu den Gebäuden); sagen, falls gewünscht.
- Halt der aufgeklebten Winkelleisten, Unterkasten, Faden: unverändert offen (Test-Dock steht aus).

## Lehren

L40 Oben bildet sich ein Wulst über mehrere Schichten wie unten der Elefantenfuß; L41 Einführfasen an Öffnungen immer mindestens 0,5 mm, in Stufen bis über die Oberkante (kein Rest-Überhang); L42 Schrift immer erhaben (L01 gilt auch für die Steckplatte).
