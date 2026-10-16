# r0: Passproben und Probestück (vor dem Logbuch)

Kurzfassung. Die ausführliche Fassung mit Konstanten und Herkunft steht in `plug/STATUS.md` (Abschnitte 2, 3 und 4).

## Ziel

Maße der Kaufteile (Dupont-Buchse, abgewinkelte Winkelleiste) und Passungen am echten Material klären, dann ein Probestück (22 × 36 mm) mit Kassette, Schieber,
Mini-Platte und Deckel drucken.

## Teile

Passproben Runde 1 bis 5 (`plug/fit_test/`), Probestück (`plug/sample.py`, `stl/steckmodul_probe/`).

## Ergebnis (bewährt)

- Körper der Winkelleiste **2,0 mm** (Datenblatt 2,54 ist falsch), Länge 10,66, Pin-Vierkant 0,64, senkrechter Pin 7 mm, 3 mm Lötende.
- Buchse in der Tasche: 0,25 sitzt sehr gut; Pin-Loch 1,4 mm; Spiel des Leistenkörpers 0,10; Stufe für das Lötende passend zur Körperhöhe.
- Löcher nie auf der ersten Schicht (Elefantenfuß schließt sie).
- Probestück: wackelt überall etwas (Heißkleber), mit 2,0 mm für die Winkelleiste passt es.

## Folgen

Konstanten in `plug/parts.py`; Übergang zu Passungsserien (r1), weil Spalte unter 0,5 mm nicht messbar sind.
