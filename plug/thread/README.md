# `plug/thread/`: Fadenführung an den Plattenecken

Eigenes Paket für die Überarbeitung des Faden-V (Aufgabe: `plug/logbook/tasks/faden-v-ueberarbeiten.md`). Stand: **Plan liegt vor, noch nicht abgenickt, keine STL.**
Berührt nicht: `plug/testcase/build2.py`, Dock-Nische, Zapfen, Schachttiefe, `plug/parts.py`. Neue Werte stehen nur in `params.py` (Regel 8).

| Datei | Inhalt |
|---|---|
| `params.py` | Vorschlagswerte für die Varianten A (V weit), B (Rinne), C (zwei Schrägbohrungen), D (Eckschacht), dazu Annahmen zu Nadel und Faden (ungemessen) |
| `reach.py` | Einfädelprobe im Schnitt: längste gerade Nadel, die durch einen gebogenen V-Kanal kommt (`python3 -m plug.thread.reach [--write]`, ca. 1 min, schreibt `reach.json`) |
| `reach.json` | Ergebnis der Einfädelprobe (wird vom Plan gelesen) |
| `build_plan.py`, `plan.template.html` | Plan als HTML mit Zeichnungen, Reglern, Maßkette und Entscheidungskarten (`python3 -m plug.thread.build_plan` → `plan.html`) |
| `plan.html` | erzeugte Seite (nicht lesen, 70 kB) |

## Plan-Artifact

https://claude.ai/artifact/PB7g6bhrdDhJx5oM7XRwax (privat; Entscheidungskarten V, S, N, K, T)

## Befund und Empfehlung (Kurzform)

- Das V ist ein geschlossener, gebogener Tunnel. Gerade Nadeln kommen nicht durch: gerechnet höchstens 6 mm bei Ø 4,0 und 53°, 20 mm bei 70°; eine Stopfnadel hat 45 mm. Mehr Durchmesser allein löst das Einfädeln nicht.
- Der Faden liegt über dem Keil zwischen den Schenkeln und zieht ihn nach unten; die Decke über dem Kanal trägt nichts.
- **Empfehlung C:** zwei gerade Schrägbohrungen (Ø 3,6, 58°) von der Eckaussparung zur Seitenwand, der Faden liegt zwischen den Austritten in einer Rille außen. Test: drei Eckmuster (A, B, C).

## Beim Zusammenführen (Merge) nachzuziehen, außerhalb dieses Pakets

Absichtlich noch nicht angefasst, weil dieser Chat nur in `plug/thread/` schreibt:

- `plug/CLAUDE.md`: Zeilen für `python3 -m plug.thread.build_plan` (Plan) und `python3 -m plug.thread.reach` in die Befehlstabelle.
- `plug/STATUS.md`: Artifact-Link oben in die Tabelle der Artifacts, Eintrag in der Chronologie.
- `plug/logbook/`: `next.md` (Fadenführung: Plan liegt vor), nach dem Test `rounds/r5_*`, `current.md`, `lessons.md`.
- Nach dem Abnicken und dem Test: Fadenwerte aus `params.py` in `plug/power/params.py` und `plug/testcase/params.py` übernehmen.
