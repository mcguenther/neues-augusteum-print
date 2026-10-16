# r4: Steckprobe 2 (gedruckt und ausgewertet, 2026-10-16)

**Status: gedruckt und ausgewertet (2026-10-16).** Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorener Satz: [`steckprobe2.zip`](steckprobe2.zip) (Stand Commit `46d1e0a`, nur eine Kassette). Frühere Stände: erster Bau `5c91a0e` mit zwei Kassetten. Welche der beiden ZIP gedruckt wurde, steht nicht im Ergebnistext (L33); der Befund ist von der Kassette unabhängig.

Bau (Stand vor dem Druck): Der Nutzer hat den Bau freigegeben („lass die Steckprobe 2 jetzt bauen“). Nur **eine** Kassette, keine Reserve; die Buchsenhöhe wird nicht mehr gemessen (Nutzer). Zwei-Lagen-Aufbau statt Platte mit Deckel: Mini-Oberplatte 12,6 + hohler Mini-Unterkasten 14,4, Dock mit Kabelnische, Steg-Anschlag, zwei Zapfen, vier Faden-V (links 53°, rechts 40°). STL, README, ZIP, Prüfbericht: `stl/steckmodul_testcase2/` (`python3 -m plug.testcase.build2`; alle Teile dicht, keine Kollisionen, Material ≈ 40 g, ≈ 2,2 h auf dem Drucker des Nutzers). Testbogen: `plug/testcase/feedback2.html`, Artifact https://claude.ai/artifact/W51dFmAeAUjF6gNUwPC3SB. Neue Werte stehen in `plug/testcase/params.py` und `plug/power/params.py`, nicht in `plug/parts.py`. Ergebnis des Drucks fehlt noch; danach Auswertung, `result.txt` und Einfrieren.

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

## Ergebnis (Auswertung)

Im Prinzip hat alles gepasst; der Nutzer fand vier Dinge, die geändert werden müssen.

| Fuge | Ergebnis | Status |
|---|---|---|
| Kassette bestücken | alle Buchsen passen, „alles super“ (Tasche 14,60) | bewährt |
| Einpressen | super; **0,05 mm mehr Luft über der Kassette** (Schachttiefe + 0,35 statt + 0,30) | bewährt mit +0,05 |
| Gebäude in die Mulde | passt alles (Fußfase 0,8, Muldenfase 1,0, Mulde 0,10) | bewährt |
| Oberplatte auf Unterkasten | rundum flach, kein Spalt; **Zapfen wackeln deutlich (5)**, Zapfen und Löcher 1 mm länger | Auflage bewährt, Zapfen verworfen (zu kurz) |
| Stecken | Pins treffen die Buchse ohne Kraft, alle vier; Kraft leicht; sitzt fest; Oberplatte bleibt liegen; E 5,28 bleibt | bewährt |
| Durchgang und Abziehen | „passt“ (keine Felder ausgefüllt, nur Notiz) | bewährt |
| Faden-V (53° und 40°) | **Faden geht durch keines der V; Öffnungen (Trichter) sind in Ordnung, der untertauchende Bereich (Kanal unter der Lasche) ist zu eng**; etwa 1 mm mehr Spiel, „deutlich mehr Platz einplanen“; Winkelvergleich dadurch nicht entschieden | verworfen (Maße), Winkel offen |
| Dock mit Kabelnische | die **drei Fenster der Nische** braucht es nicht, die Nische ist zu groß; **lieber eine mittelgroße**; der Nutzer druckt mit **Support** (einmal bereinigen) | umbauen |
| Winkelleiste, Rippen und Steg | nichts gemeldet, Felder leer (Körper kippt?, Steg-Luft?) | offen (unklar) |
| Druckqualität | nur der Faden-Befund; Elefantenfuß, Fenster, Stege, Zapfen-Löcher nicht bewertet | unklar |
| Adern, LED, Licht | später | offen |

## Entscheidungen und Folgen

- **Support ist erlaubt** (Nutzer: nur einmal bereinigen). Damit entfallen die Böschungs- und Fenster-Konstruktionen, die nur Brücken vermeiden sollten: Kabelnische als **eine mittelgroße Nische** ohne Stege, Faden-V ohne die Rücksicht auf den Überhang von 0,15 oder 0,24 mm je Schicht. L04 und L05 gelten für den Nutzer nicht mehr als harte Regel (Support einplanen, Prüfbericht nennt die Stellen).
- **Faden-V:** Kanal mindestens 1 mm weiter (Ø 2,2 → 3,2 oder mehr), Eintritt und Austritt großzügig. Die Neigung 53° gegen 40° bleibt offen; mit Support lässt sich der Kanal auch steiler oder offener bauen.
- **Zapfen:** 1 mm länger (Höhe 1,5 → 2,5), Lochtiefe entsprechend.
- **Schachttiefe:** Kassettenhöhe + 0,35.
- **Kabelnische:** eine mittelgroße Nische statt 24 × 19 mm mit drei Fenstern. Die Größe ist offen und wird im nächsten Plan als Karte vorgeschlagen.
- Werte bleiben in `plug/testcase/params.py` und `plug/power/params.py` (Regel 8), bis die nächste Runde sie bestätigt.

## Was die Runde nicht klärte

- Ob Rippen und Steg den Körper der Winkelleiste halten (keine Antwort).
- 53° gegen 40°.
- Elefantenfuß mit Fase 0,5 (kein Feld ausgefüllt).
- Die Größe der einen Nische (der Nutzer sagt nur „mittelgroß“).
- Licht der LED und Adern (Schritt L, später).
