# `plug/thread/`: Fadenführung an den Plattenecken

Eigenes Paket für die Überarbeitung des Faden-V (Aufgabe: `plug/logbook/tasks/faden-v-ueberarbeiten.md`). Stand: **Plan Stand 2 liegt vor, noch nicht abgenickt, keine STL.**
Berührt nicht: `plug/testcase/build2.py`, Dock-Nische, Zapfen, Schachttiefe, `plug/parts.py`. Neue Werte stehen nur in `params.py` (Regel 8).

| Datei | Inhalt |
|---|---|
| `params.py` | Vorschlagswerte: `PILL`/`pill()` (Stand 2, halbe Pille mit Steg), dazu die Varianten A bis D aus Stand 1 und Annahmen zu Nadel und Faden (ungemessen) |
| `build_plan.py`, `plan.template.html` | **aktueller Plan** (Stand 2) mit Zeichnungen, Reglern, Passprüfung, Maßkette, Entscheidungskarten (`python3 -m plug.thread.build_plan` → `plan.html`) |
| `fit.py`, `fit.json` | Passt die Tasche in die echte Platte? Umriss und gesperrte Flächen wie im Konzept, vier Ecken, 1:1000 und 1:1300 (`python3 -m plug.thread.fit --write`, wenige Sekunden) |
| `reach.py`, `reach.json` | Einfädelprobe im Schnitt: längste gerade Nadel, die durch einen V-Kanal bzw. um den Steg der Pille kommt (`python3 -m plug.thread.reach [--write]`, `--pill` nur die Pille, je ca. 30 s bis 1 min) |
| `build_plan1.py`, `plan1.html` | Archiv: Plan Stand 1 (Vergleich A bis D, Empfehlung C); nicht mehr aktuell |

## Plan-Artifact

https://claude.ai/artifact/PB7g6bhrdDhJx5oM7XRwax (privat; Version 2 = Stand 2; Entscheidungskarten L, D, N, F)

## Stand 2 in Kürze

- Rückmeldung des Nutzers: Der Faden ließ sich nicht einschieben, weil der Kanal **zugeschmoddert** war (Druck), nicht nur wegen der Form. Variante A soll probiert werden, „super robust“: Tasche wie eine halbe Pille mit Steg in der Mitte, runde Decke, etwa 3 mm Luft über dem Steg, wenn es ins Modell passt.
- Form: offene Tasche an der Plattenunterseite (Länge 20, Breite 10, Decke 7,5 hoch mit Viertelkreis-Enden R 7,5, Steg 5,0 × 4,5 mit runder Kante von Wand zu Wand, Luft 3,0). Zweite Größe mit 4,5 mm Luft (Decke 9,0) zum Vergleich. Kein Tunnel, kein Trichter, kein freies Maß unter 3 mm; ohne Support planbar.
- Passt ins Modell: ja, an allen vier Ecken der echten Platte bei 1:1000 und 1:1300; Material über der Decke 5,1 bzw. 3,6 mm bei 12,6 mm Plattendicke; Eckaussparung im Unterkasten 26 × 16 bzw. 29 × 16 mm.
- Einfädeln: gerade Nadel kommt nur etwa 10 mm (Luft 3,0) bzw. 12 mm (Luft 4,5) um den Steg; Nadel bringt den Faden über den Steg, Haken oder Pinzette zieht ihn herunter, oder ganz ohne Nadel mit Haken.
- Nächster Schritt nach dem Abnicken: `plug/thread/build.py` (zwei Eckmuster F2-P3 und F2-P45, je Plattenecke und Unterkasten-Ecke; STL, README, ZIP, Prüfbericht), dann Testbogen.

## Neue Lehre für `plug/logbook/lessons.md` (beim Merge nachtragen)

Kanäle und Löcher unter etwa 3 mm schließen sich im Druck (hier: Faden-V Ø 2,2, Wulst und Stufen, vermutlich auch Brückenhänger). Fadenwege als **offene Taschen** mit mindestens 5 mm freiem Maß bauen, nicht als enge Tunnel; Einfädeln von Hand vor dem Plan mit der Reichweite der Nadel prüfen (`reach.py`).

## Beim Zusammenführen (Merge) nachzuziehen, außerhalb dieses Pakets

Absichtlich noch nicht angefasst, weil dieser Chat nur in `plug/thread/` schreibt:

- `plug/CLAUDE.md`: Zeilen für `python3 -m plug.thread.build_plan` (Plan), `plug.thread.fit` und `plug.thread.reach` in die Befehlstabelle.
- `plug/STATUS.md`: Artifact-Link oben in die Tabelle der Artifacts, Eintrag in der Chronologie.
- `plug/logbook/`: `next.md` (Fadenführung: Plan Stand 2 liegt vor), nach dem Test `rounds/r5_*`, `current.md`, `lessons.md` (Lehre oben).
- Nach dem Abnicken und dem Test: Fadenwerte aus `params.py` in `plug/power/params.py` und `plug/testcase/params.py` übernehmen (die V-Kanal-Geometrie `v_solid`/`place_vs` im Konzept wird dann durch die Tasche ersetzt).
