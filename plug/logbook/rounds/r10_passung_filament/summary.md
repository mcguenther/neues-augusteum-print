# r10: Passung bei wechselnden Filamenten (gedruckt und ausgewertet, 2026-10-19)

**Status: gedruckt und ausgewertet** (Mulden-Block, Kassetten K1 bis K5); die daraus abgeleitete Platte (Commit `0009967`) ist gebaut, aber **noch nicht gedruckt**. Wörtlicher Ergebnistext: [`result.txt`](result.txt) (Aussagen des Nutzers im Chat, kein Testbogen-Formular). Aufgabe: [`../../tasks/passung-filament.md`](../../tasks/passung-filament.md), Plan `plug/filament/plan.html`.

## Ziel und Anlass

Der Nutzer wechselte das Filament (Platte grau, Gebäude und Kassetten beige): Die beigen Gebäude (Hörsaal-, Seminar-, Institutsgebäude) gingen nicht mehr in die Mulden (Hörsaal nur mit viel Kraft), die beigen Kassetten nicht mehr in die beigen Gebäude. Gefragt: Welche Spiele passen bei diesem Filament (Bambu A1, PLA), und passt die Dupont-Buchse noch in die Kassette?

## Gedruckte Teile (Generator `python3 -m plug.filament.build`, Ausgabe `stl/steckmodul_passung/`)

| Teil | Inhalt | Eingefrorene ZIP (in diesem Ordner) | Stand |
|---|---|---|---|
| B1, B3 | Probefuß (31 × 18, Kodierecke, Fase 4,0, Schacht V1RS) und Mulden-Block (Spiel je Seite 0,10 / 0,15 / 0,20) | `passung_variante_B.zip` (mit K1 bis K3, README, Prüfbericht) | Generator `plug/filament/build.py`, Vorgänger-Commits von `93da3a4` |
| K1, K2, K3 | Kassette V1RS (Unterbau), Spiel im Schacht je Seite 0,12 / 0,16 / 0,20, ohne Markierung | in `passung_variante_B.zip` | wie oben |
| K4 | Spiel 0,14, Buchsentasche 10,46 × 2,84 (0,10 enger), Höhe zunächst 14,60, dann 14,40; zwei Punkte | `passung_kassette_14.zip` | `93da3a4` (Tasche 14,40) |
| K5 | Spiel 0,13, Tasche 10,46 × 2,84 × 14,40, ein Punkt | `passung_kassette_13.zip` | `7e1cfa5` |

Nicht berichtet: Variante A (A1, Mulden-Block mit Institutsumriss) und B3b (zweiter Mulden-Block); zu beiden liegt keine Aussage vor (offen). Plan: `plug/filament/plan.html` (Artifact in `STATUS.md`).

Druckeinstellungen: Bambu A1, PLA, Düse 0,4, Schicht 0,2, 3 Wände, 15 %, Support aus; Fluss je Filament **nicht kalibriert**.

## Ergebnis je Teil

| Punkt | Ergebnis | Status |
|---|---|---|
| Mulden-Block B3, Spiel 0,10 je Seite | zu fest, nur mit Zange wieder raus | verworfen |
| Mulden-Block B3, Spiel **0,15** | passt gut, minimal zu viel Spiel | **bewährt** (Probefuß Fase 4,0, beige in grau) |
| Mulden-Block B3, Spiel 0,20 | wackelt | verworfen |
| K1 (Spiel 0,12) | sehr stramm, rutscht mit Schwung zu tief | verworfen (zu eng) |
| K2 (0,16) | minimale Reibung, rutscht zu doll | verworfen (zu locker) |
| K3 (0,20) | frei | verworfen |
| Buchsentasche alt (10,56 × 2,94) | Dupont-Buchse hat zu viel Spiel | verworfen |
| K4 mit Tasche 10,46 × 2,84 × 14,60 | Buchse taucht ca. 0,2 mm zu tief ein, kostet E (Grenze stabiler Durchgang 5,08 von 5,28) | verworfen (Höhe) |
| K4 mit Tasche 10,46 × 2,84 × **14,40** | „Dupont-Buchse passt fantastisch rein“ | **bewährt** (Tasche) |
| K4, Schacht-Spiel 0,14 | noch zu locker | verworfen |
| K5, Schacht-Spiel **0,13** | „passt super im Probefuß, schwerer bei bestehenden Gebäuden, passt aber so“ | **bewährt** als Sollwert für V1RS (bei den bestehenden beigen Gebäuden etwas strammer als im Probefuß, akzeptiert) |

## Entscheidungen

1. `OUTLINE_CLR_T` und `HOF_CLR_T` 0,15 (Hof ungetestet, Übernahme der Mulden-Passung).
2. Kassette V1RS: Spiel im Schacht **0,13** je Seite (Außenmaß je Seite 0,07 schlanker als die Kassette mit 0,06), Buchsentasche **10,46 × 2,84 × 14,40**. Taschenhöhe an die echte Einstecktiefe E koppeln (L49).
3. Gebäude auf der Platte auseinanderrücken statt Trennwände zu verdünnen: Zuschnitt der Gebäude bleibt bei Fuge 1,0 (neu `ZUSCHNITT_CLR_T` 0,10), die Platte schiebt die Gebäude je Naht um 0,1 mm auseinander (L50).
4. Fuß-Fase 4,0 für neue Gebäude und Schachttiefe 0,35 (Aufgabendatei): **noch nicht umgesetzt**, siehe offen.

## Folgen für Werte und Geometrie

- **Umgesetzt (Commit `0009967`, Platte, noch nicht gedruckt und nicht getestet):** `plug/testcase/params.py` mit `OUTLINE_CLR_T` 0,15, `HOF_CLR_T` 0,15, neu `ZUSCHNITT_CLR_T` 0,10; Zuschnitt und STL der Gebäude unverändert; `plug/divider/geom.py` (`fuge_platte`, `verschiebungen`, `schiebe`) und `plug/campus.py` rücken die Gebäude je Naht um 0,1 mm auseinander, Verschiebung höchstens 0,14 mm je Gebäude. Platte **115,63 × 220,90** statt 115,58 × 220,84 (nur 0,05 größer, nicht 1 bis 2 mm wie in der Aufgabe vermutet). Wand zwischen den Mulden 0,80, nur an den Zahnflanken Paulinum/Neues Augusteum 0,70 (Zahn im Schlitz; für 0,80 müsste der Zuschnitt dieser Naht auf 1,1: offene Entscheidung). Docks weichen höchstens 0,138 mm (Hochhaus) vom gedruckten Unterkasten ab (`ZAPFEN_LOKAL` unverändert). Geprüft: `plug.check`, `divider.check`, `export_campus`, `campus_underside` ok.
- Auffälligkeit: Der Zwischenspeicher `plug/scale1176/underside_1300.json` war veraltet (Fach bei x 30 bis 100 statt `FACH_FIX` Mitte 45,4) und wurde neu gerechnet; die Eckaussparung Nordwest trifft jetzt laut Konzept das Fach (210 mm²), **zu prüfen**.
- Nicht neu erzeugt: `plug.colour` (farbiger Hof-Einsatz), HTML-Seiten, Unterkasten.
- **Noch nicht übernommen:** Spiel 0,13 und Tasche 10,46 × 2,84 × 14,40 stehen nur in `plug/filament/build.py`, **nicht** in den echten Kassetten (`variants.kassette`) und im Gebäude-Generator (Folgeaufgabe). Gilt zunächst für V1RS; v4 und V2R ungetestet. `KASS_CLR_T` in `params.py` bleibt 0,06, `plug/parts.py` unverändert.

## Was die Runde nicht klärte (offen)

- Fase 4,0 (Aufgabendatei, Probefuß) gegen 2,0 (Code `FUSS_FASE_T`, r8 bewährt): welche gilt für neue Gebäude?
- Ob Gebäude mit Fase 2,0 in den 0,15er Mulden gleich gut sitzen (erst mit der neuen Platte sichtbar; B3 hatte Fase 4,0).
- Schachttiefe 0,35 (`SHAFT_EXTRA_T` im Code 0,30).
- Flussraten-Kalibrierung je Filament (läuft beim Nutzer); Messplättchen T4 nicht erzeugt.
- Kassetten v4 (Hörsaal) und V2R (Hochhaus) mit dem neuen Spiel; Hof-Einsatz mit 0,15.
- Entscheidung Naht Paulinum/Neues Augusteum (0,70 oder Zuschnitt 1,1); Eckaussparung Nordwest.
- Variante A (Institutsumriss) und B3b: keine Rückmeldung; Druckzeit und Messwerte in mm nicht gemeldet.
- Die Passung hängt vom Filament ab (beige gegen schwarz); die Werte gelten für dieses beige PLA ohne Flusskalibrierung.
