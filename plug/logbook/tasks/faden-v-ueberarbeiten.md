# Aufgabe für einen anderen Chat: Fadenführung (Faden-V, „Ösen“) überarbeiten

Stand: 2026-10-16, nach Steckprobe 2 (r4). Aufgabe ist **offen**, noch niemand arbeitet daran. Dieser Chat (Steckprobe 3, Dock, Zapfen) fasst die Fadenführung nicht an.

## Ziel

Die Platte wird an einen Doktorhut genäht: **vier Fäden an den Ecken**, der Boden wird nach unten genäht und drückt dabei die Oberplatte auf den Unterkasten. Keine Schrauben.
Der Faden soll **nicht an der Oberseite** austreten. Er soll von unten durch einen breiten Trichter in einen Kanal laufen, **schräg durch eine Lasche** der Oberplatte und **schräg nach unten wieder heraus** (V-Kanal). Der Unterkasten hat dafür an jeder Ecke eine Aussparung.

## Was getestet wurde und scheiterte (Steckprobe 2, r4)

- V-Kanal: Ø 2,2 mm, Scheitel 3,4 mm über der Plattenunterseite, Trichter R 2,0, Wand 1,4; zwei Böschungen nebeneinander: links 53° (0,15 mm Überhang je Schicht), rechts 40° (0,24 mm).
- Ergebnis des Nutzers (wörtlich in `plug/logbook/rounds/r4_steckprobe2/result.txt`): „faden geht durch keins der löcher durch, hier brauchen wir nen millimeter mehr spiel. die öffnungen sind ok, aber dann der bereich der untertaucht, da kommt man nicht durch“ und „faden lässt sich nicht in kanal einfädeln. ist ja auch ein overhang sozusagen, also einfach deutlich mehr platz einplanen, schadet ja auch nicht“.
- Der Winkelvergleich 53° gegen 40° ist damit **nicht entschieden**.

## Vorgaben des Nutzers

- Kanal **mindestens 1 mm weiter**, am besten deutlich mehr Platz (Ø 3,2 oder mehr).
- **Support ist erlaubt** (der Nutzer bereinigt einmal). Überhang-Rücksichten von 0,15 oder 0,24 mm je Schicht sind nicht mehr nötig, der Kanal darf offener oder steiler werden.
- Keine Schrauben. Kein Faden an der Oberseite.
- Antworten und Texte auf Deutsch. Neue Dateien und Ordner mit englischen Namen.

## Wo der Code liegt

- Werte: `plug/testcase/params.py` (`V_LEG_D`, `V_APEX`, `V_ENTRY_R`, `V_WALL`, `V_SLOPE_A`, `V_SLOPE_B`) und `plug/power/params.py` (`V`, `V_PLAN2`, `NOTCH_PAD`).
- Geometrie: `plug/power/build_concept.py` (`v_hs`, `v_geom`, `place_vs`, `v_solid`, `mouth_ch`) und `plug/testcase/build2.py` (`top_plate`, `under_box`, `vs_placed`).
- Zeichnungen: `plug/testcase/build_feedback2.py` (`svg_faden`), Plan: `plug/testcase/build_plan2.py` (`PROP`), Konzept: `plug/power/concept.template.html` (Faden-Ecke).
- Logbuch: `plug/logbook/README.md` (Arbeitsmodus), `lessons.md` (L02, L05, L29, L30), `current.md` (Abschnitt 2b), `rounds/r4_steckprobe2/summary.md`.

## Vorgehen (Arbeitsmodus des Repos)

1. `plug/logbook/README.md`, `lessons.md`, `current.md` und `CLAUDE.md` lesen.
2. **Zuerst ein Plan als HTML mit Grafiken** (Schnitt durch die Ecke mit Regler, Maßkette im Worst-Case, Entscheidungskarten mit Empfehlung, Risiken), als Artifact veröffentlichen. Kein STL ohne Abnicken.
3. Optionen im Plan vergleichen, mindestens: (a) weiterer V-Kanal mit Support, (b) halboffene Rinne oder Schlitz statt geschlossenem Kanal, (c) Nadel-freundliche Öse oder Schlaufe durch ein größeres Loch, (d) Faden von unten durch die Ecke des Unterkastens. Empfehlung begründen, auch den Einfädelvorgang (Nadel, Schlaufe) zeigen.
4. Nach dem Abnicken: ein **eigenes kleines Testteil** (Ecke der Oberplatte mit Kanal, ohne Gebäude und Dock) mit STL, README, ZIP, Prüfbericht und Testbogen bauen. Neue Werte nur in `plug/<paket>/params.py` (Regel 8), `plug/parts.py` nicht anfassen.
5. Das Ergebnis im Logbuch nachziehen (`rounds/`, `current.md`, `lessons.md`, `next.md`, `plug/STATUS.md`).

## Abgrenzung (damit sich die Chats nicht in die Quere kommen)

Dieser andere Chat arbeitet nur am Faden-V und legt Neues in einem **eigenen Paket `plug/thread/`** an (Generator, Plan, Testbogen). Er ändert **nicht** `plug/testcase/build2.py`, die Dock-Nische, die Zapfen und die Schachttiefe; das bleibt im Chat zu Steckprobe 3. Übernommen wird später per Merge, die neuen Fadenwerte stehen dann in `plug/thread/params.py`.

## Ergebnis, das erwartet wird

Ein abgenickter Plan und ein Testteil, an dem der Faden von unten durch Trichter und Kanal läuft und sich einfädeln lässt, mit klaren Maßen für Kanal, Trichter, Scheitel und Eckaussparung, die danach in die Oberplatte und den Unterkasten übernommen werden.
