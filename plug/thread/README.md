# `plug/thread/`: Fadenführung an den Plattenecken

Eigenes Paket für die Überarbeitung des Faden-V (Aufgabe: `plug/logbook/tasks/faden-v-ueberarbeiten.md`). Stand: **Plan Stand 2 abgenickt (Fase 2,0 / Luft beide / ohne Support / nur Faden); Eckmuster v1 gebaut (STL, ZIP), Testbogen liegt vor; noch nicht gedruckt.**
Berührt nicht: `plug/testcase/build2.py`, Dock-Nische, Zapfen, Schachttiefe, `plug/parts.py`. Neue Werte stehen nur in `params.py` (Regel 8).

| Datei | Inhalt |
|---|---|
| `params.py` | Vorschlagswerte: `PILL`/`pill()` (Stand 2, halbe Pille mit Steg), dazu die Varianten A bis D aus Stand 1 und Annahmen zu Nadel und Faden (ungemessen) |
| `build_plan.py`, `plan.template.html` | **aktueller Plan** (Stand 2) mit Zeichnungen, Reglern, Passprüfung, Maßkette, Entscheidungskarten (`python3 -m plug.thread.build_plan` → `plan.html`) |
| `fit.py`, `fit.json` | Passt die Tasche in die echte Platte? Umriss und gesperrte Flächen wie im Konzept, vier Ecken, 1:1000 und 1:1300 (`python3 -m plug.thread.fit --write`, wenige Sekunden) |
| `reach.py`, `reach.json` | Einfädelprobe im Schnitt: längste gerade Nadel, die durch einen V-Kanal bzw. um den Steg der Pille kommt (`python3 -m plug.thread.reach [--write]`, `--pill` nur die Pille, je ca. 30 s bis 1 min) |
| `build.py`, `stl/`, `vorschau/` | **Eckmuster P3 und P45** (je Plattenecke + Unterkasten-Ecke): `python3 -m plug.thread.build` (ca. 2,5 min) schreibt STL, `README.txt`, `pruefbericht.txt`, `faden_eckmuster_v1.zip` nach `plug/thread/stl/` und Bilder nach `plug/thread/vorschau/` |
| `build_feedback.py`, `feedback.template.html`, `feedback.html` | Testbogen zu den Eckmustern (`python3 -m plug.thread.build_feedback`), Ergebnistext zum Kopieren |
| `round/r5_eckmuster/` | vorläufiger Rundeneintrag (Auswertung, Ergebnistext wörtlich) für `plug/logbook/rounds/` |
| `build_plan1.py`, `plan1.html` | Archiv: Plan Stand 1 (Vergleich A bis D, Empfehlung C); nicht mehr aktuell |

## Plan-Artifact

https://claude.ai/artifact/PB7g6bhrdDhJx5oM7XRwax (privat; Version 3 = Stand 2 mit Fase, abgenickt)

Testbogen: https://claude.ai/artifact/9qinNK1GZiZTRRZJeqjXTx (privat)

## Stand 2 in Kürze

- Rückmeldung des Nutzers: Der Faden ließ sich nicht einschieben, weil der Kanal **zugeschmoddert** war (Druck), nicht nur wegen der Form. Variante A soll probiert werden, „super robust“: Tasche wie eine halbe Pille mit Steg in der Mitte, runde Decke, etwa 3 mm Luft über dem Steg, wenn es ins Modell passt.
- Form: offene Tasche an der Plattenunterseite (Länge 20, Breite 10, Decke 7,5 hoch mit Viertelkreis-Enden R 7,5, Steg 5,0 × 4,5 mit runder Kante von Wand zu Wand, Luft 3,0). Zweite Größe mit 4,5 mm Luft (Decke 9,0) zum Vergleich. Kein Tunnel, kein Trichter, kein freies Maß unter 3 mm; ohne Support planbar.
- **Fase** (Wunsch des Nutzers, damit man Ein- und Ausgang gut trifft): 2,0 × 45° ringsum am Taschenrand, 1,0 × 45° am Steg-Fuß. Mündung an der Unterseite 24 × 14, Eingang und Ausgang je 10,5 mm weit (ohne Fase 7,5). 45° druckt ohne Support und gleicht den Elefantenfuß aus. Werte `chamfer` und `steg_chamfer` in `params.PILL`.
- Passt ins Modell: ja, an allen vier Ecken der echten Platte bei 1:1000 und 1:1300; Material über der Decke 5,1 bzw. 3,6 mm bei 12,6 mm Plattendicke; Eckaussparung im Unterkasten (gefaste Mündung + 2 mm ringsum) 28 × 18 bzw. 31 × 18 mm; Platzbedarf in der Platte 26,8 × 16,8 mm.
- Einfädeln: gerade Nadel kommt nur etwa 10 mm (Luft 3,0) bzw. 12 mm (Luft 4,5) um den Steg; Nadel bringt den Faden über den Steg, Haken oder Pinzette zieht ihn herunter, oder ganz ohne Nadel mit Haken.
- Abgenickt am 2026-10-16: Fase A (2,0 / 1,0), Luft beide (P3 und P45), ohne Support, Werkzeug nur Faden (kein Haken, keine Nadel), Freigabe zum Bauen.
- Gebaut: `plug/thread/stl/` (vier STL, alle dicht, keine Kollisionen, 16 g, etwa 1 h auf dem Drucker des Nutzers). Prüfbericht misst im Modell: Luft über dem Steg 3,00 bzw. 4,50, Eingang und Ausgang 10,4 bzw. 11,9 mm weit an der Unterseite.

- **Ergebnis der Eckmuster (2026-10-16):** Decke glatt, Faden geht bei beiden durch. Nutzer wählt als Kompromiss **4,0 mm Luft** (`params.CHOSEN_AIR`, Standard von `pill()`); Widerspruch im Ergebnistext (ZIP „nicht gedruckt“); Zugprobe noch offen. Auswertung: `round/r5_eckmuster/summary.md`, `result.txt`.

## Neue Lehre für `plug/logbook/lessons.md` (beim Merge nachtragen)

Kanäle und Löcher unter etwa 3 mm schließen sich im Druck (hier: Faden-V Ø 2,2, Wulst und Stufen, vermutlich auch Brückenhänger). Fadenwege als **offene Taschen** mit mindestens 5 mm freiem Maß bauen, nicht als enge Tunnel; Einfädeln von Hand vor dem Plan mit der Reichweite der Nadel prüfen (`reach.py`).

## Beim Zusammenführen (Merge) nachzuziehen, außerhalb dieses Pakets

Absichtlich noch nicht angefasst, weil dieser Chat nur in `plug/thread/` schreibt:

- `plug/CLAUDE.md`: Zeilen für `python3 -m plug.thread.build_plan` (Plan), `plug.thread.fit` und `plug.thread.reach` in die Befehlstabelle.
- `plug/STATUS.md`: Artifact-Link oben in die Tabelle der Artifacts, Eintrag in der Chronologie.
- `plug/logbook/`: `next.md` (Fadenführung: Plan Stand 2 liegt vor), nach dem Test `rounds/r5_*`, `current.md`, `lessons.md` (Lehre oben).
- Nach dem Abnicken und dem Test: Fadenwerte aus `params.py` in `plug/power/params.py` und `plug/testcase/params.py` übernehmen (die V-Kanal-Geometrie `v_solid`/`place_vs` im Konzept wird dann durch die Tasche ersetzt).
