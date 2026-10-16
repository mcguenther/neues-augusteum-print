# r5: Eckmuster Fadenführung P3 und P45 (Auswertung, 2026-10-16)

Vorläufiger Rundeneintrag für `plug/logbook/rounds/` (dieser Chat schreibt nur in `plug/thread/`; beim Merge dorthin verschieben und `current.md`, `lessons.md`, `next.md`, `plug/STATUS.md` nachziehen).
Wörtlicher Ergebnistext: [`result.txt`](result.txt). Stand der Teile: `plug/thread/stl/faden_eckmuster_v1.zip` (Commit `1f1529a`). Plan: Artifact https://claude.ai/artifact/PB7g6bhrdDhJx5oM7XRwax, Testbogen https://claude.ai/artifact/9qinNK1GZiZTRRZJeqjXTx.

## Ziel

Faden an den Plattenecken: Variante A als „halbe Pille mit Steg“ (offene Tasche von unten, runde Decke, Steg von Wand zu Wand, Fase 2,0 am Rand und 1,0 am Steg-Fuß), Luft über dem Steg 3,0 (P3) gegen 4,5 mm (P45). Ohne Support gedruckt, gefädelt nur mit Faden.

## Ergebnis

| Punkt | P3 (3,0) | P45 (4,5) | Status |
|---|---|---|---|
| Decke der Tasche von unten | glatt | glatt | bewährt |
| Faden einfädeln (nur Faden) | geht durch | geht durch | bewährt |
| Eingang und Ausgang treffen, Wirkung der Fase | nicht beantwortet | nicht beantwortet | offen |
| Anziehen, kräftig ziehen, Steg unter Last, Scheuern | nicht beantwortet | nicht beantwortet | **offen** (wichtigster Rest) |

Nutzer: „beide ok“, „faden lässt sich bei beiden durchfädeln“.

## Unklar (benannt, nicht erraten)

Im Ergebnistext steht bei der ZIP „nicht gedruckt“, zugleich sind Decke und Einfädeln bewertet. Das passt nicht zusammen (L35, L25). Möglich: die Teile wurden gedruckt und nur das Feld falsch ausgefüllt, oder die Bewertung stammt von anderem Material. Die Werte oben gelten deshalb als **vorläufig**, bis der Nutzer bestätigt, dass P3 und P45 gedruckt wurden.

## Entscheidung

**Luft über dem Steg 4,0 mm** als Kompromiss zwischen 3,0 und 4,5 (Nutzer). `params.CHOSEN_AIR = 4.0` (Standard von `params.pill()`, die gedruckten Muster `TESTED_AIRS`). Daraus: Decke 8,5, Länge am Boden 22, Material über der Decke 4,1, Mündung mit Fase 26 × 14, Eingang und Ausgang je 11,5 mm weit, Eckaussparung im Unterkasten 30 × 18, Platzbedarf in der Platte 28,8 × 16,8. Passprüfung (`fit.py`): an allen vier Ecken der echten Platte frei, 1:1000 und 1:1300. Gerade Nadel um den Steg: etwa 12 mm (Ø 1,2). 4,0 liegt zwischen zwei Mustern, die beide gingen; ein eigener Druck ist nicht nötig, außer der Nutzer will ihn.

## Folgen für Werte und Geometrie

- Fadenführung der großen Platte: Tasche mit Luft 4,0, Fasen 2,0 und 1,0, gebaut mit den Funktionen aus `plug/thread/build.py` (`cavity`, `chamfer_cutter`, `steg`); Eckaussparung 30 × 18 im Unterkasten.
- `v_solid` und `place_vs` im Konzept (`plug/power/build_concept.py`) werden durch die Tasche ersetzt (nach Merge, nicht in diesem Paket).
- Neue Lehre L37 (Entwurf; höchste Nummer im Logbuch ist L36): Kanäle und Löcher unter etwa 3 mm schließen sich im Druck; Fadenwege als offene Taschen mit mindestens 5 mm freiem Maß bauen. Offene Tasche mit runder Decke und 3 bis 4,5 mm Luft: glatt, ohne Support.

## Was die Runde nicht klärte

- Ob die Teile wirklich gedruckt wurden (Widerspruch oben).
- Zug: hält die Plattenecke bei kräftigem Ziehen, bleibt der Steg heil (Last 20 N angenommen, ungemessen)?
- Ob die Fase beim Treffen von Ein- und Ausgang spürbar hilft und ob 2,0 mm passen.
- Scheuern des Fadens an Steg, Decke und Fase.
