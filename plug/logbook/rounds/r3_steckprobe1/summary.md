# r3: Steckprobe 1 (2026-10-16)

Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorener Satz: [`testcase_series.zip`](testcase_series.zip) und
[`testcase_update_plate_lid.zip`](testcase_update_plate_lid.zip).

## Ziel

Der komplette Steckmechanismus im Kleinen: bestückte Kassette (Buchse, Adern, LED) wird in ein Mini-Gebäude mit L-Fuß gepresst, das in die Mulde einer Mini-Grundplatte mit
Winkelleiste gesteckt wird. Ohne Schieber und ohne Trichterplatte, Muldenboden 0,4 mm, E 5,28 mm.

## Teile und Quellen

`plug/testcase/` (`params.py`, `kassette.py`, `build.py`) → `stl/steckmodul_testcase/`. Commits: Plan `44d5013`, erste STL `f4a995c`, Testbogen `2bbaad7`, Platte B und neuer Deckel
`69fb76f` (Update-ZIP nach Rückmeldung: Muldenboden und Löcher nicht gut gedruckt, Stempel gebrochen). Artifacts: Planung (`plan.html`) und Testbogen (`feedback.html`) in
`plug/testcase/`.

Teile: 2 × Kassette v4 (Taschenhöhe 14,45 und 14,15), Mini-Gebäude A (Schacht 0,06 durchgehend) und B (Passzone 8 mm + 0,20), Mini-Grundplatte A (Kasten-Hohlräume, Support)
und B (Trichter, ohne Support), Mini-Deckel (zuerst mit dünnen Stempeln, dann mit Streben).

## Ergebnis

| Fuge | Ergebnis | Status |
|---|---|---|
| Kassette bestücken | Kassette 2 (14,15) passt keine Buchse; Kassette 1 (14,45) Sitz 3, bündig, hält fest, Buchse steht aber minimal (etwa 0,1 mm) heraus | 1 bewährt mit +0,1 |
| Einpressen | A: Sitz 3, hält, Herausdrücken nur mit kräftigem Druck; B: Sitz 5, lose; Kassette ragt etwa 0,2 mm unten heraus | A bewährt, B verworfen, Schachttiefe +0,3 |
| Mulde | L-Fuß: Sitz 3, nur eine Lage, kein Wackeln, sinkt bis zum Boden („top“) | bewährt |
| Winkelleiste in der Platte | Pins gerade, alle vier; **Körper kippt oder wackelt**; Platz hinter den Lötenden zu wenig (Fasen) | offen |
| Deckel | schließt nicht, Stempel stoßen beim Aufsetzen an, mehr als 1 mm Luft nötig; Schrauben nicht vorhanden | verworfen, Konzept neu |
| Stecken | Pins treffen die Buchse ohne Kraft (kein Trichter), Gebäude sitzt fest, **elektrischer Kontakt da** | bewährt |
| Durchgang und Abziehen | alles passt; Gebäude geht sehr leicht ab, Pins tauchen nicht tief ein, Kontakt trotzdem da | bewährt (Haltekraft klein) |
| Druck | Muldenboden stark durchgehängt oder Löcher zu, Kabelraum-Decke stark durchgehängt (Thick bridges an), einzelne Pin-Löcher zu, leichter Wulst; Schrift und Kerben gut | siehe Lehre L05 |
| Adern und LED | Adern lassen sich rund biegen; Licht nicht getestet | offen |

## Entscheidungen aus dem Feedback

- Kassette 1 weiterverfolgen, Tasche mindestens 0,1 mm höher; Variante 14,15 entfällt.
- Gebäude A weiterverfolgen, Schacht tiefer (Kassette ragte heraus); B entfällt.
- Winkelleiste: Körper darf nicht kippen. Deckel mit Stempeln neu planen, der Heißkleber-Weg (Stützen weglassen) ist ein Ausweg mit niedriger Priorität.
- Für den echten Boden: Raum unter der Winkelleiste für die Kabel so frei wie möglich.
- Ösen für Fadenschlaufen (Doktorhut, vier Fäden an den Ecken, der Boden wird nach unten genäht; das soll den Deckel andrücken).
- Muldenboden eventuell minimal dünner.

## Nachtrag (2026-10-16, Antworten des Nutzers)

- **Platte B war die getestete Platte** für Winkelleiste, Stecken und Durchgang (Schritte W, S, D; der Hinweis „durch die Fase kaum Platz für die Kabel“ passt nur zu B). Die Druckmängel im Schritt „Druckqualität“
  (durchgehängter Muldenboden, durchgehängte Kabelraum-Decke, zugequollene Löcher) stammen vom ersten Druck mit Platte A. Bei B waren alle vier Pin-Löcher offen und der Kontakt vorhanden. Platte A ist damit für
  den Druck ohne Support verworfen, **B ist die Basis**.
- **Schrauben entfallen ganz.** Deckel und Platte bekommen Löcher; ein Faden wird durch beide gefädelt und drückt sie zusammen (die Platte wird an einen Doktorhut genäht, vier Fäden an den Ecken).
- **Buchsen nachmessen entfällt:** das Delta ist bekannt (Tasche der Kassette 1 braucht mindestens 0,1 mm mehr als 14,45).
- Offen bleiben Licht der LED und der Heißkleber-Weg (siehe `next.md`).

