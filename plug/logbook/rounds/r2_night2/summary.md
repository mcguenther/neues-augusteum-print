# r2: Nachtdruck 2 (2026-10-15)

Wörtlicher Ergebnistext: [`result.txt`](result.txt).

## Ziel

Die Entscheidungen aus r1 umsetzen und die noch offenen Fugen testen: K (Kontakt-Tiefe mit gecrimpten Kontakten, Plättchen 0,4 bis 1,0), C (Kassette v2, LED-Fläche flach),
N (Schieber noch einmal, mit mehr Spiel; Platte A mit Brücke, Platte B ohne), E (Kassette v3 mit Trichterboden zum Einpressen, Spiel 0,06 / 0,09 / 0,12),
D (Passprobe v7: Tasche +1,5, Körperhöhe 2,0 / 1,8 / 1,6), FM (Fuß-Lehre für die Mulden-Ringe aus r1).

## Teile und Quellen

`plug/series2.py` → `stl/steckmodul_night2/` (`night2_series.zip`, README). Commit `cd49a2f`; Entscheidungsdokument `plug/decision` (`6adfdae`); Testbogen
`plug/feedback/build_night2.py` (`47fd575`). Planung als Artifact (Entscheidungen) vor dem Druck.

## Ergebnis

| Serie | Ergebnis | Status |
|---|---|---|
| K | Durchgang stabil bei Plättchen 0,4 und 0,6 (E 5,28 und 5,08), 0,8 (E 4,88) und 1,0 Aussetzer; Haltekraft der Buchse klein, bei 0,4 noch „hält“ | bewährt: Muldenboden höchstens 0,6, Ziel 0,4 |
| C | Buchse Sitz 3, geht ganz hinein, hält fest; LED 10 und 12 mm passen; Adern knicken stark | Podest 2 mm höher gewünscht |
| N | nicht getestet, der Nutzer will den Schieber weglassen (kostet Pin-Länge) | verworfen |
| E | Spiel 0,06 lässt sich gut eindrücken und sitzt fest; Trichterboden nicht nötig | bewährt (nur 7 mm Berührung) |
| D | 2,0 und 1,8 liegen flach, 1,6 leicht schief; Körper in der Tasche Sitz 4 | Stufe für 1,8 |
| FM | 0,10 und 0,15 Sitz 4, 0,20 wackelt deutlich | Mulde CLR 0,10; Federzunge vielleicht unnötig |
| Druck | Elefantenfuß leichter Wulst trotz Fase 0,3; Schrift und Kerben gut; Decke über der Nut leicht durchgehängt | Fase 0,4 testen |

## Entscheidungen

Kein Schieber, kein Trichterboden; Kassette eingepresst; LED-Fläche als Podest 2 mm höher; Stufe für Körperhöhe 1,8; Mulde 0,10; Zunge zunächst weglassen.
Danach der Plan zur Steckprobe (`plug/testcase/plan.html`).

## Folgen

Lehren L03, L05 (Vorstufe), L10, L14, L16, L19; neue Sollwerte in `plug/testcase/params.py`.
Nicht geklärt: Einpressen in der echten Länge (17 mm), Pin-Treffer ohne Trichter, Verhalten der Winkelleiste in der Platte → r3.
