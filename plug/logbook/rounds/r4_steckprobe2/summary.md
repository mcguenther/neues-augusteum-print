# r4: Steckprobe 2 (gedruckt, Gesamturteil „passt alles“, 2026-10-16)

Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorener Satz: [`steckprobe2.zip`](steckprobe2.zip) (Stand `3ccceeb`).

**Ergebnis (2026-10-16): gedruckt, Nutzer: „passt alles super“.** Das ist ein **pauschales Urteil im Chat, kein ausgefüllter Testbogen**. Es gilt für den ganzen Satz
(Kassette, Mini-Gebäude, Oberplatte, Unterkasten): Zwei-Lagen-Aufbau, Kabelnische, Faden-V und Steckmechanismus haben beim Zusammenbau keine Beanstandung ergeben.
Daraus lässt sich ableiten (als Gesamturteil, nicht je Fuge belegt):

| Thema | Wert | Status |
|---|---|---|
| Kassette Tasche 14,60, Fase 0,5, nur eine Kassette | passt | bewährt (pauschal) |
| Gebäude: Schacht 0,06 durchgehend, 17,40 tief, Fußfase 0,8 | passt | bewährt (pauschal) |
| Zwei-Lagen-Aufbau: Oberplatte 12,6 auf hohlem Unterkasten 14,4, Zapfen, Steg-Anschlag | passt | bewährt (pauschal) |
| Dock mit Kabelnische 24 × 19, Rippen an der Körpertasche, Schlitz bis -8,0 | passt, kein Kippen gemeldet | bewährt (pauschal) |
| Faden-V (53° links, 40° rechts) | kein Problem gemeldet; **Winkel nicht gewählt** | vorläufig, Vergleich offen |
| Steckprobe als Ganzes (Stecken, Durchgang) | „passt alles“ | bewährt (pauschal) |

**Nicht belegt (Nutzer hat dazu nichts gesagt):** welcher Faden-Winkel besser druckt und läuft (Feld F-best), ob die Faden-V wirklich mit Faden und Nadel probiert wurden, Licht der LED
(Schritt L), ob Heißkleber nötig war (W-glue), Durchgang mit dem Multimeter und zehnfaches Abziehen (Schritt D), Muldenboden 0,4 (z-boden), Wunsch für den nächsten Schritt (z-next).
Diese Werte bleiben in `current.md` „vorläufig“ oder „offen“, bis der Nutzer sie nennt.

**Vorgeschichte (Nachtrag 2026-10-16): gebaut, danach gedruckt (Ergebnis oben).** Der Nutzer hat den Bau freigegeben („lass die Steckprobe 2 jetzt bauen“). Nur **eine** Kassette, keine Reserve; die Buchsenhöhe wird nicht mehr gemessen (Nutzer). Zwei-Lagen-Aufbau statt Platte mit Deckel: Mini-Oberplatte 12,6 + hohler Mini-Unterkasten 14,4, Dock mit Kabelnische, Steg-Anschlag, zwei Zapfen, vier Faden-V (links 53°, rechts 40°). STL, README, ZIP, Prüfbericht: `stl/steckmodul_testcase2/` (`python3 -m plug.testcase.build2`; alle Teile dicht, keine Kollisionen, Material ≈ 40 g, ≈ 2,2 h auf dem Drucker des Nutzers). Testbogen: `plug/testcase/feedback2.html`, Artifact https://claude.ai/artifact/W51dFmAeAUjF6gNUwPC3SB. Neue Werte stehen in `plug/testcase/params.py` und `plug/power/params.py`, nicht in `plug/parts.py`. Auswertung, `result.txt` und eingefrorene ZIP: siehe oben.

**Ursprünglicher Planstand (davor):** Plan noch nicht abgenickt, keine STL erzeugt.
Plan als Seite: `plug/testcase/plan2.html` (Generator `python3 -m plug.testcase.build_plan2`), Artifact https://claude.ai/artifact/TmuFSSVHgjMBQVKkzvKEG9 (privat).
Commits: Plan `ce47e6e`, Zeichnungskorrektur `e2dbb03`.

## Was der Nutzer festgelegt hat

- **Keine Schrauben.** Das ist die feste Vorgabe. Die Platte wird später an einen Doktorhut genäht, vier Fäden an den Ecken.
- **Fadenführung (Zwischenstand, kein bewährter Wert):** Der Faden soll nicht an der Oberseite austreten. An der Unterseite gibt es eine breite Einführung; der Faden läuft von unten
  schräg durch eine Lasche und schräg nach unten wieder heraus. Die Ausführung im Plan (V-Kanal, siehe unten) ist ein Vorschlag von Claude, den der Nutzer als Planungsstand
  übernommen hat; Details dürfen sich noch ändern.
- **Name „Steckprobe“** passt.
- Platte B ist die Basis; Buchsen werden nicht nachgemessen (Delta aus r3 genügt).

## Vorschlag im Plan (Zwischenstand, `PROP` in `plug/testcase/build_plan2.py`)

| Thema | Vorschlag | Herkunft / Grund |
|---|---|---|
| Faden-Lasche | V-Kanal Ø 2,2 in jeder Plattenecke, Überhang 0,15 mm je Schicht (etwa 53° zur Waagerechten, Platte-B-Böschung), Scheitel 3,4 mm über der Unterseite, Trichter Radius 2,0 am Bett, Mitte x ±15,6, y 6,0 vom Plattenrand, Wände mindestens 1,4 mm | Wunsch Faden unten ein und aus; L05 (Böschung statt Brücke) |
| Deckel | Ausschnitte über den Trichtern; Stempel nur noch als Anschlag mit 1,2 mm Luft zum Körper | L21, L28; **offen:** Ausschnitte an den Ecken in Ordnung? |
| Kassette | Tasche 14,60 (Buchse etwa 14,55), Kassette 17,10, nur eine Variante, zweite als Reserve | L13, L17 |
| Gebäude | Schacht 0,06 durchgehend, 17,40 tief (Kassette + 0,3), Anschlagrand 1,2, gesamt 18,60 | L10, L12 |
| Fase | 0,5 an Bettkanten und Schachteingang | L03 |
| Platte B2 | Lötschlitz 1 mm länger (Ende bei −8,0), Rippen an der hinteren Taschenwand gegen das Kippen, keine Schraublöcher | L20, L21 |

Maßkette (Worst-Case, im Plan gerechnet): E 5,28 bei bündig eingesetzter Buchse, 5,23 wenn sie an die Schultern rutscht (Luft 0,05); stabil gemessen bis E 5,08.

## Offen (Entscheidungskarten im Plan)

F Fadenführung (V-Kanal A, Ohren B, gerade Löcher C) · T Taschenhöhe · S Schachttiefe · K Halt des Körpers (Rippen, Heißkleber oder beides) · D Stempel · E Fase · L Lötschlitz.
Der Nutzer hat die Karten noch nicht beantwortet. Erst nach dem Abnicken: Werte nach `plug/testcase/params.py`, STL, Prüfbericht, ZIP.

## Lehre aus dieser Planung

L29: Bei Verbindungsmitteln den ganzen Weg abfragen (Eintritt, Austritt, welche Seite zugänglich), statt Löcher durchgehend anzunehmen.

## Nachtrag: Kassetten-Varianten V1 und V2 (Planung)

Anlass (Nutzer): Die Kassette v4 passt nicht in alle Gebäude, z. B. nicht in das Seminargebäude und das City-Hochhaus. Gewünscht: V1 = Streifen gekippt, steht auf der langen Kante und klebt auf einer Wand;
V2 für das City-Hochhaus = Streifen hochkant, schlanker, nur die Buchse, Streifen an einer flacheren Wand. Konzepte als HTML mit Grafik.

- Seite `plug/testcase/plan3.html` (`python3 -m plug.testcase.build_plan3`), Geometrie `plug/testcase/variants.py`, Passstudie `plug/testcase/fit_study.py` (`variants_fit.json`). **Konzept, keine STL, nicht abgenickt.**
- Passstudie (Wand 1,2 um den Schacht, Schnitt 2 mm über dem Boden): bei 1:1500 passt v4 nicht in Paulinum, Seminargebäude, City-Hochhaus, im Institutsgebäude nur 0,4 Wand; bei 1:1000 überall. V1 und V2 passen überall in den Grundriss.
- Höhen: V1 braucht Gebäude ab 17,3 mm (Hörsaalgebäude 16,4: zu niedrig; Seminargebäude 18,8: 1,5 Reserve), V2 ab 24,5 mm (Hochhaus, Paulinum, knapp Neues Augusteum).
- Aufbau: gleicher Unterbau wie v4 (Dock, Pins, Einpressen bleiben gültig), darüber ein Blatt (1,2) als Fortsetzung der hinteren Taschenwand, Streifen davor, LED blickt nach vorn.
  V1 17,2 × 5,3 × 26,4 (Adern seitlich zum Pad-Ende), V2 13,0 × 5,3 × 33,5 (Adern gerade nach oben).
- Offene Karten: Varianten (A: drei Kassetten), Lichtrichtung, Blattdicke V2 (Empfehlung 1,6), LED-Höhe V2, Unterbaubreite V1, Streifenbreite, Probedruck.

## Nachtrag 2: V2 bevorzugt, Höhe und Rücken-LED

Nutzer: V2 ist besser; passt es von der Höhe? Zweite LED auf der Rückseite gegenüber; geht das von unten? Idee: Blatt nach oben verlängern und oben nach vorn zur Mitte versetzen.

- Höhe V2: Gebäude ab 24,5 mm. Grundriss und Höhe zusammen (Schnitt in der nötigen Höhe): 1:1500 nur City-Hochhaus und Paulinum; 1:1000 Paulinum, Neues Augusteum, Hochhaus (Institutsgebäude 0,9 Wand, knapp nicht).
  Seminargebäude: geschlossene Dachfläche nur etwa 16,4 mm (die 18,8 sind eine kleine Aufsicht), V1 (17,3) und V2 passen nicht, v4 passt nicht in den Grundriss; V3 (flach neben der Buchse, etwa 31 × 10,5) käme auf 1,0 Wand. Offen.
- Rücken-LED: Streifen am hinteren Blatt ragt 2,1 mm hinter die Schachtwand, kommt von unten nicht durch. V2R: Blatt in der Mitte, oben 45° nach vorn versetzt, Unterbau 6,4 tief (Chip zu Chip 5,6, Luft 0,4), Verkettung DOUT → DIN über die Blattkante,
  Kassette 13,0 × 6,4 × 36,9, Gebäude ab 27,9. Streifendicke 2,2 ist nicht belegt (vor der STL messen).
- Seite jetzt als Artifact: https://claude.ai/artifact/RqSFYxH8ZggxvdjQY93nTe. Neue Vorgabe: HTML-Seiten immer als Artifact präsentieren (CLAUDE.md).

## Nachtrag 3: V1R (V1 mit Rücken-LED)

Nutzer: auch für V1 eine Rückenvariante; der Fit in die Gebäude folgt, sobald der Maßstab ganz genau feststeht (V1R ist daher nicht in der Fit-Tabelle).
V1R: Unterbau 17,2 × 6,4, Kassette 30,2 hoch (Gebäude ab 21,2 mm), Blatt in der Mitte und oben 45° nach vorn versetzt wie V2R, Streifen quer auf beiden Seiten, Verkettung über die Oberkante am rechten Ende
(Alternative am rechten Rand vorbei: Blatt 2 mm breiter, Gebäude ab 18,7). Generator `plug/testcase/variants.py` (`V1R`), Bild `vorschau/steckmodul_testcase/variante_v1r.png`, Abschnitt und Karte „V1R“ in `plan3.html`.

## Nachtrag 4: V1R in zwei Varianten

Nutzer: zwei Varianten für V1R, eine mit den Leitungen oben vorbei, eine seitlich vorbei. `V1R` (oben, Blatt 2,5 über den Streifen, Kassette 17,2 × 6,4 × 30,2, Gebäude ab 21,2) und `V1RS` (seitlich: Unterbau 19,2 breit, Blatt samt Streifen 1 mm nach links,
2,0 Platz rechts für die drei Adern, Kassette 19,2 × 6,4 × 27,7, Gebäude ab 18,7). Bilder `variante_v1r.png`, `variante_v1rs.png`; Karte Q fragt, welche in den Probedruck kommt (Empfehlung: beide).
