# r4: Steckprobe 2 (Planung, Zwischenstand 2026-10-16)

**Status: Planung. Plan noch nicht abgenickt, keine STL erzeugt, nichts gedruckt.** Dieser Eintrag hält den Zwischenstand fest, damit er nicht verloren geht.
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
