# Aufgabe für einen neuen Chat: Fachprobe Powerbank auswerten

**Erledigt (2026-10-16): ausgewertet in `rounds/r5_fachprobe/`.** Stößel und Taste sind von der Konzeptseite entfernt, die Seite ist neu veröffentlicht.

Stand bei Anlage: 2026-10-16. Die Fachprobe ist **gebaut, aber noch nicht gedruckt**. Dieser Chat beginnt, sobald der Nutzer den Ergebnistext des Testbogens einfügt. Liegt noch kein Ergebnistext vor, frage danach und baue nichts.

## Worum es geht

Die große Grundplatte hat über dem Unterkasten ein Fach für die Powerbank (Intenso XS5000, 90 × 63 × 12,6 mm laut Datenblatt, **ungemessen**), die ESP und LEDs mit Strom versorgt. Die Fachprobe ist der Ausschnitt vom Anschlussende dieses Fachs (Variante B), um zu prüfen, ob die Powerbank hineinpasst und wie sie sitzt.

Vorgaben des Nutzers: **keine Taste und kein Stößel** (der Mikrocontroller fragt später alle 5 s kurz Strom ab). Der **Ladeanschluss** (micro-USB, USB-C) muss durch das Fenster erreichbar bleiben. Die **USB-A-Buchse mit geradem Stecker** versorgt die Elektronik. Sonst muss es nur reinpassen und gut sitzen.

## Was gedruckt wurde und wo es liegt

- Teile: `F_fach.stl` (Boden, Wände, Fenster in der Vorderwand, Zaun, Kabelkanal, hinten offen) und `F_deckplatte.stl` (2 mm, steht für die Oberplatte). Zusammen etwa 26 g.
- ZIP und Prüfbericht: `stl/steckmodul_fachprobe/` (`fachprobe.zip`, `pruefbericht.txt`, `README.txt`), Bilder `vorschau/steckmodul_fachprobe/`.
- Generator: `python3 -m plug.power.build_fach`; Geometrie `plug/power/fachprobe.py`; Fach-Maße `plug/power/build_concept.py` (`fach_parts`) und `plug/power/params.py` (`PB_*`, `FENCE`, `UK_*`).
- Plan: `plug/power/plan_fach.html`, Testbogen: `plug/power/feedback_fach.html` (Artifact https://claude.ai/artifact/FKLje3Pq8eSphqzvaohz7W).
- Commits: Plan `fed8228`, Bau und Testbogen `3ccceeb`.

## Offene Punkte, die der Ergebnistext klären soll

1. **Kabelkanal:** nur 4,4 mm frei neben dem Zaun (Kanal 6 mm minus Zaun 1,6). Geprüft wird mit einem 4-mm-Kabel. Schritt S und das Feld `p-cab` (Kabeldicke) zeigen, ob es klemmt.
2. **Fenster:** LEDs liegen mit nur 2 mm Rand im Fenster; micro-USB und USB-C mit 2 bis 16 mm. Alle Anschluss-Lagen sind Schätzung. Schritt F.
3. **Steckerraum 35 mm** für den geraden USB-A-Stecker (Schätzung). Schritt S.
4. **Luft über der Powerbank** 0,6 mm (Worst-Case bei 13,0 mm Dicke: 0,2 mm). Schritt D.
5. **Sitz im Zaun** (Spiel 0,5 je Seite) und die **Länge 90 mm** (mit dem Lineal). Schritt P.
6. **ZIP-Version:** im Ergebnistext von Steckprobe 2 fehlte sie (L35). Nach der Version fragen, falls sie fehlt.

## Vorgehen (Arbeitsmodus des Repos)

1. Vorher `CLAUDE.md`, `plug/logbook/README.md`, `lessons.md` und `current.md` lesen.
2. **Zuerst auswerten, noch nichts bauen:** Erkenntnisse zusammenfassen und bewerten, Unklarheiten und widersprüchliche Angaben benennen, nichts erraten. Die Antwort an den Nutzer auf Deutsch.
3. Dann ins Logbuch eintragen: `rounds/r5_fachprobe/summary.md` und `result.txt` (wörtlich), `current.md`, `lessons.md`, `next.md`, `plug/STATUS.md`. Den getesteten Satz einfrieren: `fachprobe.zip` in den Rundenordner kopieren, Commit-Hash in `summary.md`.
4. Werte, die sich ändern, nur in `plug/power/params.py` eintragen (Regel 8), `plug/parts.py` nicht anfassen. Danach `python3 -m plug.power.build_concept` ausführen und die Konzeptseite (Artifact https://claude.ai/artifact/WPkLCy4M1m8ehMzJTTr5iS) neu veröffentlichen.
5. Committen und pushen auf den Branch, den der Nutzer vorgibt. Keine PR, außer er verlangt sie.

## Zu beachten

- Die Konzeptseite (`plug/power/concept.template.html`, `build_concept.fach_parts`) zeigt noch einen **Stößel** und die Taste. Beides entfällt laut Nutzer; im Zug der Auswertung entfernen und die Seite neu bauen.
- Der Maßstab ist **1:1300**; Fachlänge und Platzbedarf hängen davon ab (siehe `plug/PLAN.md` Kapitel 6).
- Der Nutzer druckt mit **Support** (Support ist erlaubt).
