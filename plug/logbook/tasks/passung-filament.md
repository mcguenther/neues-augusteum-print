# Aufgabe: Passung bei wechselnden Filamenten umsetzen (Übergabe, 2026-10-19)

Zweig `claude/dazzling-davinci-ch966n`. Plan: `plug/filament/plan.html` (Artifact https://claude.ai/artifact/6XbKN3t1Aj9bnv5DRwT1pP, Quelle `plug/filament/build_plan.py` und `plan.template.html`). Probedruck-Generator: `python3 -m plug.filament.build` (Ausgabe `stl/steckmodul_passung/`, Prüfbericht dort). Vorher `plug/logbook/lessons.md` und `current.md` lesen.

## Was gedruckt und ausgewertet ist (Nutzer, Variante B, grau und beige)

- Mulden-Block mit Spiel I 0,10 / II 0,15 / III 0,20 (Probefuß Fase 4,0): I zu fest (nur mit Zange wieder raus), **II passt gut** (minimal zu viel Spiel), III wackelt.
- Kassetten K1 0,12 / K2 0,16 / K3 0,20 Spiel im Schacht (ohne Markierung, Zuordnung nach Gefühl): K1 sehr stramm und rutscht mit Schwung zu tief, K2 minimale Reibung aber rutscht zu doll, K3 frei. Die Dupont-Buchse hat in der Tasche zu viel Spiel.

## Beschlossen (Nutzer)

1. **Mulden-Spiel 0,15** (`OUTLINE_CLR_T`), **Hof-Aussparung (Leibniz-Forum) `HOF_CLR_T` ebenfalls 0,15**.
2. **Fuß-Fase 4,0** für neue Gebäude beibehalten (`FUSS_FASE_T` in `plug/buildings.py`; sie entfällt weiter neben dem Schacht, wo Schacht und Rand näher als Fase plus Wand liegen). Die gedruckten Gebäude (Hörsaal, Seminar, Institut, beige, Fase 2,0) bleiben nutzbar; ihre Mulden-Außenform ändert sich nicht.
3. **Gebäude auf der Platte auseinanderrücken** statt die Trennwände zu verdünnen: Mulden-Spiel und Fuge im Code entkoppeln. Heute gilt `plug/divider/geom.py` Fuge = 2 × `OUTLINE_CLR_T` + Wand 0,8, und `plug.buildings` schneidet die Gebäude an den Nähten damit zu. Mit 0,15 darf sich der Zuschnitt der **bestehenden** Gebäude nicht ändern (Fuge für den Zuschnitt bei 1,0 lassen); stattdessen die Lage der Gebäude je Naht um 2 × (0,15 − 0,10) = 0,1 mm auseinanderschieben, sodass die Wand zwischen den Mulden 0,8 bleibt (Fuge in der Platte 1,1). Die Summe der Verschiebungen über die Platte beträgt höchstens 1 bis 2 mm.
4. **Platte größer, Ränder oben wie heute:** Der Umriss der Platte (115,6 × 220,8) wächst um die Verschiebungen, der Rand um die Gebäude (Fase 1,5 oben, Beschriftungsstreifen) bleibt unverändert. Docks (Pin-Löcher, Display-Dock), Fadentaschen, Zapfenaufnahmen, Batteriefach und Unterkasten (`plug/power/`) folgen dem Maß; Zapfenlagen (`ZAPFEN_LOKAL`) und die Passprobe `plug.campus_underside` neu prüfen. Platz laut Nutzer 1 bis 2 mm in beide Richtungen.
5. **Buchsentasche** der Kassette 0,10 enger in Breite und Tiefe insgesamt (10,46 × 2,84, Höhe 14,60 unverändert): **zu testen**, noch nicht gedruckt. Kassette neu mit Spiel im Schacht **0,14** (Zwischenstufe K1/K2, Kassette 0,08 je Seite schlanker), mit zwei erhabenen Punkten als Kennung (Anzahl = (Spiel − 0,10) / 0,02): `K4_kassette_V1RS_14.stl` in `stl/steckmodul_passung/`, ZIP `passung_kassette_14.zip`. Wenn K4 nicht passt: 0,13 und 0,15 nachlegen.
6. Schachttiefe der Gebäude von 0,30 auf **0,35** (`SHAFT_EXTRA_T`, L36), gilt nur für künftig gebaute Gebäude.

## Offen

- Flussraten-Kalibrierung je Filament (Nutzer, Bambu Lab, läuft); Messplättchen T4 aus dem Plan ist noch nicht erzeugt. Slicer-Kompensation je Farbe danach eintragen.
- Kassetten v4 (Hörsaal) und V2R (Hochhaus) sind in den Serien nicht getestet; die Ergebnisse gelten für V1RS (Seminar, Institut).
- Probefuß hatte Fase 4,0; ob die Gebäude mit 2,0 in den 0,15er Mulden gleich gut sitzen, ist offen (A1 mit dem beigen Institutsgebäude zeigt es).
- Logbuch: Runde (nächste freie Nummer) in `plug/logbook/rounds/` mit `summary.md` und `result.txt` (Ergebnistext wörtlich: siehe oben), `current.md`, `lessons.md`, `next.md`, `plug/STATUS.md` nachziehen (Agent `logbuch-pfleger`). `plug/parts.py` erst ändern, wenn der Wert bewährt ist.
- Nach den Umstellungen: `python3 -m plug.campus`, `python3 -m plug.buildings` (nur wenn nötig), `python3 -m plug.divider.check`, `python3 -m plug.export_campus`, `python3 -m plug.check`; Bilder ansehen, `dicht=True` und „keine Kollisionen“.
