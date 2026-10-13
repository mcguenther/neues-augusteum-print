# Steckmechanismus mit Dupont-Teilen (Plan B)

Alternative zum JST-XH-Plan (`stecker/PLAN.md`): gleicher Zweck (Gebäude mit WS2812B-LED leuchtet,
sobald es in der Grundplatte steckt), aber gebaut aus dem vorhandenen 2,54-mm-Dupont-Set
(Preciva 1550 Teile). Gebäude haben immer einen Fuß, der in eine tiefe Mulde taucht.

- Anschauen: `stecker/dupont/ansicht.html` (3D-Ansicht, Einsteck-Animation, Druckablauf, Maßkette, Tabellen)
- Erzeugen: `python3 steckmodul_dupont.py` (STL nach `stl/steckmodul_dupont/`, Bilder nach
  `vorschau/steckmodul_dupont/`, Daten nach `stecker/dupont/daten.json`), danach
  `python3 stecker/dupont/baue_ansicht.py`
- Alle Zahlen unten stammen aus `dims()`/`forces()`/`building_table()` im Generator. Wer einen
  Parameter ändert, erzeugt neu und liest die Werte aus der Ausgabe oder der Seite.

Kennzeichnung: **B** belegt (Zeichnung/Datenblatt), **A** abgeleitet, **S** geschätzt.

## Entscheidung in Kürze

| Frage | Entscheidung |
|---|---|
| Stecker in der Platte | **Abgewinkelte Stiftleiste, 4 Pins, Stifte nach oben, Lötenden waagrecht in den Kabelraum** (Dock A). Wird von unten in eine Tasche geschoben: Der Muldenboden hält sie gegen Zug, ein Stempel im Deckel gegen Druck. Lötfreie Alternative: Dupont-Gehäuse mit Male-Crimp-Pins (Dock C), kostet 10,8 mm Plattendicke. |
| Stecker im Gebäude | Dupont-Gehäuse 1×4 mit Female-Crimp-Pins, senkrecht, Steckseite nach unten, über einer gedruckten Trichterplatte im Fuß. |
| Montage (Kernproblem) | **Hauptlösung: Druckpause.** Druck hält bei 16,60 mm über dem Bett an (nach Schicht 83 bei 0,2 mm). Buchse, Adern und LED liegen als fertige Einheit in Tasche und Kammerboden, alles unterhalb der Pausenebene. Die erste Schicht danach ist ein Riegel, der Buchse und Adern formschlüssig festhält. |
| Rückfallebene | **Kassette von unten:** Buchse und LED sitzen in einer gedruckten Kassette, die von unten in einen Schacht im Fuß geschoben wird. Ein Schieber in einer Schwalbenschwanz-Nut ist zugleich die Trichterplatte und hält alles. Ohne Druckpause, ohne Kleber, reparierbar. |
| Halten des Gebäudes | Reibung der 4 Kontakte plus Federzunge in der Muldenwand, die in eine V-Nut am Fuß rastet. Zusammen etwa 3,9 bis 6,7 N (S). |
| Kodierung | Gebäude: abgeschrägte Ecke an Fuß und Mulde. Leiste A: nur in einer Lage einschiebbar (Lötenden müssen in den Kabelraum). Buchse: durch die vorgefertigte Einheit (LED-Pads bestimmen die Lage) und eine Pin-1-Kerbe am Sockel. |

## 1. Bauteile und Maße

Quellen: Würth WR-PHD 61300411121 (gerade) und 61300411021 (abgewinkelt), Zeichnungen gelesen;
Pololu-Maßzeichnungen für Dupont-Gehäuse (Produkt 1903) und Crimpkontakte (1930/1931). Das Kit ist
No-Name, die Teile können um einige Zehntel abweichen. Alle Werte stehen oben in
`steckmodul_dupont.py` und werden mit der Passprobe nachgemessen.

| Teil | Maß | Wert | Quelle |
|---|---|---|---|
| Gehäuse 1×4 | Breite × Dicke × Höhe | 10,16 (±0,3) × 2,54 × 14,00 (±0,25) | B |
| | Rastzungen-Zone ab Kabelseite | 8,3 | B |
| | Eintrittsöffnung je Kammer | ≈ 1,0 | S |
| | Pin-1-Marke | Dreieck auf der Seite mit den Rastfenstern | B (Foto, Zeichnung) |
| | Einführtrichter | keiner nennenswert, daher gedruckter Trichter | A |
| | Kabelabgang | gerade nach oben aus der Mitte jeder Kammer | B |
| Female-Crimp-Pin | Länge, Kontaktkasten | 11,7; Kasten 1,6 × 1,6 × 4,5 | B |
| | Isolationskralle / Drahtkralle | 2,3 × 2,6 / 1,6 × 1,6 | B |
| | Rastlanze | federnde Lasche, Gesamtdicke über Lanze 1,55 | B |
| | Kontakt beginnt nach | ≈ 1,5 mm Stifttiefe | S |
| Male-Crimp-Pin | Länge, Stift | 18,0; Stift 0,64 × 6,08 | B |
| | Überstand über das Gehäuse | ≈ 6,0 | S |
| Stiftleiste gerade | Körper, oben, unten | 2,54; 6,0 (±0,2); 3,0 (±0,2); gesamt 11,54 | B |
| Stiftleiste abgewinkelt | Körper | 2,54 × 2,54 | B |
| | Steckseite | 6,0 (±0,2) ab Körper | B |
| | Biegung hinter dem Körper | 1,5 (±0,2) | B |
| | Lötende über die Körperseite hinaus | 3,0 (±0,2) | B |
| | Biegeradius | klein (≈ 0,3), im Modell scharf | S |
| Stift | Vierkant | 0,64 (Diagonale 0,91) | B |
| Flachbandkabel | Ader | 28 AWG, Isolation ≈ 0,9, Raster 1,27 | S |
| LED-Stück | B × L × Dicke | 10 × 16,7 × 2,2, Pads 5V/DIN/GND | Randbedingung |

## 2. Welche Stiftleiste, wie in der Platte?

Alle drei Docks stehen im Prototyp nebeneinander (`platte_ABC.stl`). Der Steckerteil wird jeweils
**von unten** in eine Tasche unter dem Muldenboden geschoben. Der 0,8 mm dicke Muldenboden hat
vier Löcher mit 1,1 mm (Stiftdiagonale 0,91) und hält den Körper gegen Zug. Gegen den Steckdruck
drückt ein Stempel des Deckels auf die Stirnenden des Körpers. Crush-Rippen (0,15 mm) halten das
Teil, bis der Deckel zu ist.

| | A Winkelleiste | B gerade Leiste | C Male-Crimp-Gehäuse |
|---|---|---|---|
| Stifte | nach oben, 6,0 über Körper | nach oben, 6,0 | nach oben, ≈ 6,0 (S) |
| Anschluss | Lötenden waagrecht nach hinten (+y) | Lötenden senkrecht nach unten | gecrimpte Adern unten |
| Löten | 4 Lötstellen, gut zugänglich im Kabelraum | 4 Lötstellen, senkrecht, enger | keine |
| Plattendicke (mit Deckel) | **20,0 mm** | 22,0 mm | 30,8 mm |
| Lagegenauigkeit der Stifte | gut (Stifte im Kunststoff fest) | gut | Stifte wackeln im Gehäuse, Muldenboden richtet sie |
| Verpolsicherheit in der Platte | **selbstkodierend**: andersherum passen die Lötenden nicht | symmetrisch, Pin-1-Marke nötig | symmetrisch, Pin-1-Marke nötig |
| Tausch | Deckel ab, auslöten | Deckel ab, auslöten | Deckel ab, Stecker herausziehen |

Die Idee „gerade Leiste mit zweitem Dupont-Gehäuse unter der Platte“ ist verworfen: Die Lötseite
ist nur 3,0 mm lang, eine Buchse erreicht darauf kaum ihren Kontaktpunkt (≈ 1,5 mm plus Toleranz).
Wer den Körper verschiebt (4,5/4,5), hat oben zu wenig Stift. Lötfrei geht es sauberer mit Dock C.

**Empfehlung:** Dock A für die große Platte (dünn, verpolsicher, Lötstellen frei zugänglich). Dock C,
wenn jemand gar nicht löten will und 31 mm Plattenhöhe in Kauf nimmt.

**Leiste abbrechen:** Mit der Flachzange zwischen Pin 4 und 5 über die Kante biegen; der Körper
bricht in der Kerbe. Bruchkante mit dem Cutter glätten, sonst klemmt sie in der Tasche (Tasche
hat 0,1 mm Spiel je Seite).

**Kodierung und Prüfregel:** Pin 1 (GND) liegt auf der Seite der Kodier-Ecke (−x), sofern die
Pads des LED-Streifens von −x nach +x „GND, DIN, 5V“ lauten (Parameter `PADS`; bei umgekehrter
Reihenfolge spiegelt der Generator die Belegung). Prüfregel vor dem ersten Stecken:
1. Platte: Zwischen den Stiften 1 und 3 liegen 5 V (rot an 3).
2. Gebäude: Durchgang zwischen Buchsenkontakt 1 und 4 (DETECT-Brücke), etwa 0 Ω.
3. Gebäude: Diodenprüfung Kontakt 1 (+) gegen Kontakt 3 zeigt die Schutzdiode der LED; Kontakt 2
   gegen 1 ebenfalls. Vertauschte Belegung fällt hier auf.

## 3. Fuß und Mulde

### Maßkette (z = 0 Plattenoberseite, gesteckt)

| Größe | Wert | Rechnung |
|---|---|---|
| Stift über Muldenboden | 5,20 | 6,0 − 0,8 Muldenboden |
| Fußhöhe = Muldentiefe F | **10,00** | 5,2 + 3,0 Führung + 0,8 Fußfase + 1,0 Muldenfase, auf Schichten gerundet |
| Trichterplatte | 1,00 | unter der Buchse, Trichter 2,4 → 1,1 mm |
| Steckseite der Buchse | −9,00 | −F + 1,0 |
| Einstecktiefe E | **4,20** | Stiftspitze −4,8 minus −9,0 |
| Kabelseite der Buchse | 5,00 (Tasche bis 5,25) | −9,0 + 14,0 (+0,25 Toleranz) |
| Pausenebene | **6,60** | 5,25 + 1,0 Ader + 0,2 Luft, auf Schicht gerundet |
| LED-Unterseite / Chip oben | 4,20 / 6,40 | Pausenebene − 0,2 − 2,2 |
| Kammerboden | 4,60 | LED liegt 0,4 tief |
| Riegel | 6,60 bis 7,80 | 1,2 dick |
| Druckhöhe der Pause | **16,60 mm über dem Bett** | 6,60 + 10,0 |

Phasen beim Stecken (Hub g über dem Sitz):

| g | Ereignis |
|---|---|
| 10,0 | Fußfase trifft Muldenfase, fängt bis ±2,05 mm Versatz (0,8 + 1,0 + 0,25) |
| 8,2 | Fasen durchlaufen, Fuß gleitet gerade im Führungsband |
| 5,2 | Stiftspitzen erreichen die Trichterplatte. Der Fuß steckt hier **3,0 mm** gerade in der Mulde. |
| 4,2 | Stiftspitzen erreichen die Buchse |
| ≈ 2,7 | erster elektrischer Kontakt (S) |
| 0 | Fuß sitzt auf dem Muldenboden; Federzunge rastet in die Nut |

### Toleranzkette (seitlich, ungünstigster Fall)

Fuß in Mulde ±0,25, Buchse in Tasche ±0,1, Leiste in Tasche ±0,1, Stiftlage der Leiste ±0,15 (B),
Druckfehler ±0,1 je Teil: zusammen etwa ±0,7 mm. Der Trichter fängt ±0,65 mm (Öffnung 2,4 gegen
Stift 0,64 und Hals 1,1), danach führt der Hals den Stift mit ±0,23 mm in die 1,0-mm-Öffnung der
Buchse. Kritisch ist nur der Fall, dass alle Fehler in dieselbe Richtung gehen; dann schiebt der
Trichter das Gebäude um den Rest (das Spiel der Mulde lässt das zu).

### Klemmgefahr, Ecken, Führungsband

- Die Mulde ist nur in einem Band von 5 mm unter der Fase eng (0,25 mm Spiel je Seite), darunter
  0,55 mm. Das verkürzt die Reibfläche und lässt bei schiefem Drücken weniger klemmen. Der Fuß
  wird nur in diesem Band geführt; beim Kontakt sind davon 3,0 mm im Eingriff.
- Senkrechte Fußkanten sind mit 0,5 mm gerundet, weil die Innenecken der gedruckten Mulde nicht
  scharf werden. Bei echten Gebäudeumrissen: Umriss um 0,5 mm nach innen und wieder nach außen
  versetzen (öffnen), damit spitze Außenecken verschwinden.
- Lange flache Gebäude (Hörsaalgebäude 55 × 91 mm) in der Mitte drücken. Bei 0,25 mm Spiel und
  91 mm Länge kippt das Gebäude höchstens 0,3°, das klemmt nicht, wenn man nicht an einem Ende drückt.
- Kodierung: abgeschrägte Ecke (3 mm) an Fuß und Mulde. Unsymmetrische Umrisse kodieren sich
  selbst; symmetrische bekommen die Fase an einer Ecke.

### Fuß voll oder hohl

Voll modellieren, im Slicer 3 Wände und 10 bis 15 % Infill. Ein hohler Fuß bräuchte über der
Kammer eine Brücke über den ganzen Grundriss (Hörsaalgebäude 90 mm), das geht nicht ohne Rippen.
Material beim Hörsaalgebäude 1:1500 etwa 50 cm³ Hüllvolumen, mit Infill 12 bis 15 g.

### Mindestwände und schmale Gebäude

Die Einheit (Sockel + LED) braucht 12,8 × 23,4 mm, mit 2 mm Rand 16,8 × 27,4 mm. Das
Seminargebäude (26,3 mm breit bei 1:1500) nimmt sie längs. Wand zwischen Tasche und Fußaußenseite
beim Würfel 4,4 mm.

### Fuß-Tabelle

Kriterium: Luft = sichtbare Höhe − 1,2 Dach − 6,6 Pausenebene. passt ≥ 6 mm, knapp ≥ 2 mm.

| Gebäude | 1:1500 | 1:1000 |
|---|---|---|
| Paulinum | passt (31,4) | passt (51,0) |
| Neues Augusteum | passt (17,2) | passt (29,7) |
| Hörsaalgebäude | passt (8,6) | passt (16,8) |
| Seminargebäude | passt (11,0) | passt (20,4) |
| Institutsgebäude | passt (13,3) | passt (23,9) |
| City-Hochhaus | passt (88,6), aber mehrere LEDs nötig | passt (136,8) |
| Moritzbastei | nein (−1,7); ginge mit Fuß 13,8 | nein (1,3); ginge mit Fuß 10,8 |

Das niedrige Hörsaalgebäude passt, weil die 14 mm hohe Buchse zu 9 mm im Fuß steckt und nur 5 mm
ins sichtbare Gebäude ragt. Für die Moritzbastei kann die Mulde dieses einen Gebäudes tiefer werden
(Fuß 13,8 mm); die Platte muss dafür an der Stelle 3,8 mm dicker sein. Sie bleibt wie geplant ohne LED.

### Plattenaufbau

- Mini-Platte des Prototyps: 115 × 43 × 28,8 mm plus Deckel 2 mm, Dicke durch Dock C bestimmt.
  Nur mit Dock A wären es 20,0 mm.
- Große Platte: Tablett. Oberteil mit den Mulden und Taschen, darunter Kabelräume je Dock, die in
  Kanäle (8 mm breit, 4 mm hoch) zu einer Sammelrinne an der Hinterkante münden. Deckel in
  Segmenten bis 200 mm, mit M3-Blechschrauben (Pilotloch 2,5). Die Deckel-Stempel tragen die
  Steckerteile.
- Kabelräume sind 18 mm breit, die Decke wird beim Druck als Brücke gedruckt (bis 30 mm unkritisch).

## 4. Montage in den Druck (Kernthema)

### Bewertete Wege

| Weg | Beschreibung | Urteil |
|---|---|---|
| a) Druckpause | Druck bis zur Pausenebene, Einheit (Buchse + Adern + LED) einlegen, weiterdrucken. Der Riegel überdruckt Buchse und Adern. | **Hauptlösung.** Keine Zusatzteile, formschlüssig, gleiche Höhe für alle Gebäude, auch das niedrige Hörsaalgebäude. |
| b) Von unten einschieben, LED durch Kanal | Buchse von unten in einen Schacht, LED hochkant vorweg durch denselben Schacht (10 × 2,2 passt durch 10,4 × 2,8). | Verworfen als Hauptweg: Die LED steht dann senkrecht über der Buchse; das braucht 14 + 3 + 16,7 mm Höhe und passt nur in hohe Gebäude. Kein Anschlag für die Buchse, weil LED und Buchse fast gleich breit sind. |
| c) Separates Steckmodul (Plan 1) | Modul mit Buchse und LED rastet von unten in den Boden. | Als **Kassette** übernommen (Rückfallebene), aber mit Schieber statt Schnapparmen. |
| d) Zweiteiliges Gebäude | Dach oder Boden abnehmbar. | Möglich, aber sichtbare Fuge am Modell, und jedes Gebäude braucht eine eigene Trennstelle und Rastung. Nur für das City-Hochhaus (mehrere LEDs) sinnvoll. |
| e) Kassette mit Schieber | Kassette von unten, gehalten von einem Schieber in einer Schwalbenschwanz-Nut, der zugleich Trichterplatte ist. Die Muldenwände blockieren den Schieber, solange das Gebäude steckt. | **Rückfallebene.** Reparierbar, ohne Pause. Kostet einen Schacht von 13,2 × 25,2 mm im Fuß und zwei Zusatzteile. |
| f) Heißkleber | Buchse in offene Tasche kleben, LED auf Kammerboden. | Nur, wenn die Kammer offen ist, also nur mit d). Rückfall für Reparaturen. |

### Ablauf mit Druckpause

1. **Einheit vorbereiten** (Montagelehre `montagelehre.stl`, gleiche Geometrie wie im Gebäude):
   LED in die Mulde der Lehre kleben, Adern an die Pads löten (GND, DIN, 5V; DETECT ebenfalls an
   GND), Adern über den Sockel zur Tasche legen, ablängen, crimpen, Kontakte in der Reihenfolge
   1 bis 4 ins Gehäuse stecken (Dreieck = Pin 1 zur Kerbe am Sockel). DETECT läuft in der
   Querrinne unter den anderen Adern. Einheit prüfen (Durchgang 1–4, LED am Testdock).
2. **Slicen und Pause setzen.** Pause **vor Schicht 84** (Oberkante 16,80 mm), also nach Schicht 83
   (16,60 mm) bei 0,2 mm Schichthöhe. In der Vorschau prüfen: Tasche offen, Riegel noch nicht gedruckt.
   - PrusaSlicer: Vorschau, rechten Schichtregler auf 16,80 stellen, auf das „+“ am Regler
     klicken (Rechtsklick → „Pause einfügen“). Druckereinstellungen → Benutzerdefinierter G-Code →
     „Pause-Druck G-Code“ muss `M601` enthalten (bei Prusa voreingestellt).
   - Bambu Studio: Vorschau, Schichtregler auf 16,80, Rechtsklick → „Pause hinzufügen“.
   - Cura: Erweiterungen → Nachbearbeitung → G-Code ändern → Skript hinzufügen → „Pause at
     height“; „Pause at“ = Höhe 16,8 mm (oder Schicht 84), Methode passend zur Firmware
     (Marlin `M0`/`M25`, Klipper `PAUSE`, Prusa `M601`).
   - Brückenerkennung an, Z-Hop bei Fahrten an (0,4 mm), Bett bleibt warm.
3. **Pause:** Einheit einlegen: Buchse mit der Steckseite nach unten in die Tasche drücken (Rippen
   klemmen sie), Adern flach über die Kerbe legen, LED in die Mulde drücken. Prüfen: Mit einer
   Karte (Visitenkarte) über die Sockeloberkante streichen; nichts darf hängen bleiben. Innerhalb
   von 10 Minuten fortsetzen.
4. **Weiterdrucken:** Die erste Schicht ist der Riegel (Brücke über 10,4 mm), er drückt die Adern
   leicht auf die Buchse und wirkt als Zugentlastung. Danach Kammer und Dach.
5. **Nachbearbeiten:** Trichter von unten mit 1,0-mm-Bohrer von Hand entgraten, Fußfase prüfen.
6. **Stecken:** Gebäude über die Mulde, Kodier-Ecke beachten, in der Mitte drücken.

Risiken und Gegenmittel: Düse streift eine hochstehende Ader (Kartenprobe, `WIRE_GAP` auf 0,4);
Schichthaftung nach der Pause (PLA unkritisch bis etwa 15 min, Bett warm lassen); Riegel
hängt durch (Brücke nur 10,4 mm, Durchhang wirkt als Klemmung); Buchse zu hoch (Tasche ist für
14,25 mm ausgelegt, längere Gehäuse vorher aussortieren). Die Pausenprobe (`pausenprobe.stl`,
17,8 mm hoch, etwa 20 min) übt genau diesen Ablauf vorher.

**Pausenhöhe aus dem Generator:** `dims()["pause_mm"]` (16,60) und `dims()["pause_layer"]` (83);
der Generator druckt beides aus. Bei anderer Schichthöhe `LAYER` ändern; alle Höhen werden auf
Schichten gerundet.

**Reparierbarkeit:** Die überdruckte Buchse ist nicht lösbar. Eine defekte LED heißt: Gebäude neu
drucken (Würfel etwa 2 h, 15 g). Darum wird die Einheit vor dem Einlegen geprüft. Wer
Reparierbarkeit braucht, nimmt die Kassette.

**Schrägdach:** Die Pause liegt 6,6 mm über der Platte, weit unter jedem Dach. Die Kammer folgt
dem Gebäudeumriss; Dachflächen ab 45° drucken ohne Stützen, flachere Dächer bekommen innen eine
45°-Zeltdecke (wie im ersten Plan). Bei spitz zulaufender Kammer ändert sich an Buchse und LED nichts.

## 5. Halten ohne Kleber

| Stelle | Richtung | Lösung | Kraft |
|---|---|---|---|
| Buchse im Gebäude | Druck nach oben beim Stecken | Riegel über Adern (0,6 mm Luft, Adern wirken als Polster) | Riegel trägt > 50 N (A) |
| | Zug nach unten beim Ziehen | Trichterplatte unter der Steckseite | > 50 N (A) |
| | seitlich, Klappern | Crush-Rippen an Stirnseiten und glatter Seite (0,15 mm). Die Seite mit den Rastfenstern bleibt frei, sonst drücken die Rippen die Rastzungen ein und die Kontakte rutschen heraus. | – |
| Adern | Zug an der LED | Riegel klemmt die Adern auf der Buchse (Zugentlastung) | – |
| Leiste in der Platte | Zug nach oben | Muldenboden 0,8 mm, Stifte durch 1,1-mm-Löcher | > 30 N (A) |
| | Druck nach unten | Stempel im Deckel unter den Körperenden | > 50 N (A) |
| Gebäude | Herausziehen | Kontaktreibung 1,2 bis 4,0 N (S, 0,3 bis 1,0 N je Kontakt) + Federzunge 2,7 N axial (A) | **3,9 bis 6,7 N**, Ziel 3 bis 8 N |
| | Stecken | 4,0 bis 8,0 N (S) + 2,7 N | 6,7 bis 10,7 N, Ziel < 15 N |
| Platte | Mitheben beim Ziehen | Mini-Platte (≈ 50 g) hebt mit: mit der anderen Hand halten. Große Platte (≈ 500 g) liegt bei 5 N Zugkraft an der Grenze; Gummifüße helfen nicht gegen Abheben, Gewicht oder Festschrauben schon. | – |

Federzunge: waagrechter Biegebalken in der Muldenwand (10 mm lang, 1,2 mm dick, 3,8 mm hoch,
in der XY-Ebene gedruckt), Nase 0,5 mm mit 45°-Flanken, Auslenkung 0,25 mm. Normalkraft
3·E·I·δ/L³ = 1,44 N bei E = 3500 N/mm², über die Flanke mit μ = 0,3 etwa 2,7 N axial,
Randdehnung 0,45 % (PLA verträgt 4 bis 8 %).

Option Magnete: 6 × 2 mm N35 in Fuß und Muldenboden, je unter 0,6 mm Wand. Etwa 2 bis 4 N (S).
Nur nötig, wenn die Federzunge im Test nicht reicht. Abstand zu den Stiften ≥ 8 mm.

Messen mit Federwaage (oder Kofferwaage bis 10 kg mit Haken): Schlaufe aus Faden um das Gebäude
(unter das Dach kleben) bzw. Haken in eine Bohrung am Prüfling, senkrecht ziehen, Höchstwert ablesen.
Platte dabei festhalten. Je Test 5 Messungen, Mittelwert und kleinster Wert notieren.

## 6. Elektrik und Kabel (kurz)

- Pins: 1 GND, 2 DIN, 3 +5 V, 4 DETECT (im Gebäude an GND). Controller liest DETECT mit Pull-up, LOW =
  Gebäude steckt. Eine Datenleitung je Dock.
- Crimpen: Abisolieren 2,0 mm (Drahtkralle 1,6 lang), Isolation endet unter der Isolationskralle.
  Kleinstes Nest der Zange; bei 28 AWG die Isolationskralle fest zudrücken oder die Ader vor dem
  Crimpen um 2 mm umlegen. Kontakt mit der Rastlanze zur Fensterseite des Gehäuses einschieben, bis
  er klickt; mit 5 N an der Ader ziehen, er darf nicht herauskommen.
- LED: Pads verzinnen, Adern 1 mm abisoliert anlöten, DETECT-Ader in der Querrinne zum GND-Pad.
- Platte: Flachbandkabel ist brauchbar (10 Adern). Je Dock 4 Adern auftrennen und an die Lötenden
  löten (Schrumpfschlauch 1,5 mm). Für 5 V und GND bei mehr als 4 Docks eine dickere Sammelleitung
  (22 AWG) entlang der Sammelrinne, die Docks zweigen davon ab.
- Controller: ESP32, je Dock ein Ausgang für DIN und ein Eingang für DETECT. Pegel 3,3 → 5 V mit
  74AHCT125, 330 Ω in Reihe je Datenleitung, 1000 µF am 5-V-Eingang.
- Strom: 60 mA je LED bei Vollweiß, sieben LEDs unter 0,5 A; 28 AWG trägt das auf kurzen Wegen.
- Hot-Plug: Alle Stifte sind gleich lang. Datenleitung erst nach DETECT = LOW plus 100 ms freigeben.

## 7. Vergleich mit dem JST-XH-Plan

| | JST XH (Plan 1) | Dupont (dieser Plan) |
|---|---|---|
| Haltekraft Stecker | höher, Header-Hülse führt, Buchse sitzt fest | geringer, nur Kontaktreibung (S: 1,2–4 N), plus Federzunge |
| Platzbedarf im Gebäude | Modul 23,7 × 17 mm im Boden | Einheit 12,8 × 23,4 mm, Buchse 14 mm hoch (9 mm im Fuß) |
| Kosten / vorhanden | Header, Buchsen, Kabel kaufen | alles im Set außer LED-Streifen |
| Lötarbeit | Header auf Platine (Variante B) | Platte: 4 Lötstellen je Dock (A) oder keine (C); LED immer |
| Wiederholbarkeit | Fertigteile, gleichmäßig | Crimpen von Hand, No-Name-Toleranzen |
| Kodierung | Header-Hülse ist gepolt | keine am Stecker; über Fuß, Leistenform, Einheit |
| Stapelhöhe | Header 7 + Buchse 7,75 | Leiste 2,54 + Stift 6 + Buchse 14 |
| Montage im Gebäude | Modul von unten, Schnapparme | Druckpause oder Kassette |
| Risiko | Schnapparme (PLA), Modul-Toleranzkette | Kontaktqualität bei 4,2 mm Einstecktiefe, Pausen-Handgriff |

**Empfehlung:** Mit dem vorhandenen Set zuerst den Dupont-Prototyp drucken. Wenn die Passprobe und
die Pausenprobe gelingen und die Kontakte bei 4,2 mm Einstecktiefe sicher sind, ist dieser Plan
für die ganze Platte besser: kein Zukauf, kein Steckmodul, weniger Teile im Gebäude. Die Platte
wird mit Dock A etwas dicker (20,0 mm statt 17,45 mm). Der JST-Plan ist besser, wenn Gebäude oft gesteckt werden (Steckzyklen,
gepolter Stecker) oder wenn die Dupont-Kontakte im Test unter 3 N halten oder aussetzen.

## 8. Testplan mit Abbruchkriterien

| # | Test | Erfolg | Abbruch / Änderung |
|---|---|---|---|
| 1 | Passprobe, Maße nachmessen | Buchse sitzt in der 0,1-Tasche mit leichtem Druck, Leiste ebenso; Stift durch 1,1-Loch ohne Klemmen | Keine Tasche passt: Maße oben im Generator eintragen |
| 2 | Kontakt bei 4,2 mm | Leiste mit 1,8-mm-Distanzstück in eine Buchse stecken: Durchgang stabil beim Wackeln | Aussetzer: `CEIL`/`FUNNEL_T` auf 0,6 senken (E = 4,6); bleibt es unsicher: JST-Plan |
| 3 | Pausenprobe | Düse streift nichts, Buchse wackelt nicht, Ader hält 5 N | Streift: `WIRE_GAP` 0,4; Buchse lose: `RIB` 0,2 |
| 4 | Platte mit Docks A, B, C, Deckel | Steckerteil hält 30 N Zug und 30 N Druck | Hält nicht: Muldenboden 1,2 mm, Stempel breiter |
| 5 | Würfel mit Pause, stecken | Stecken < 15 N, Ziehen 3–8 N, LED an, DETECT LOW | Ziehen < 3 N: Nase 0,6 mm oder Magnete; > 8 N: Nase 0,4 mm |
| 6 | Kodierung | Gedrehter Würfel fällt nicht in die Mulde | – |
| 7 | 50 Steckzyklen | Ziehkraft fällt um weniger als 30 %, kein Aussetzer | Aussetzer: Kontakte vergoldet kaufen oder JST |
| 8 | Kassette | Schieber hält, Tausch in < 2 min | Schieber fällt heraus: Raste am Schieber ergänzen |
| 9 | Licht | 0,4 oder 0,8 mm Wand leuchtet gleichmäßig | – |

## 9. Offene Annahmen (an den echten Teilen prüfen)

- Gehäusemaße des Kits (10,16 × 2,54 × 14,0) und die Eintrittsöffnung (≈ 1,0 mm).
- Stiftlänge der Leisten im Kit (6,0 oben, 3,0 unten) und bei der Winkelleiste die Lage der Biegung (1,5).
- Überstand der Male-Crimp-Pins aus dem Gehäuse (≈ 6,0) für Dock C.
- Kontakt sicher bei 4,2 mm Einstecktiefe (Kontaktpunkt bei ≈ 1,5 mm angenommen).
- Halte- und Steckkraft je Kontakt (0,3–1,0 N / 1–2 N angenommen).
- Aderdurchmesser des Flachbandkabels (≈ 0,9 mm) und ob 28 AWG sicher crimpt.
- Pad-Reihenfolge und Pad-Abstand des eigenen LED-Streifens (`PADS`, `PAD_X`).
- Biegemodul und Reibwert des Filaments (Federzunge).
- Seite der Rastfenster des Gehäuses: Im Modell −y (zur Gebäudemitte abgewandt).

## Quellen

- Würth Elektronik WR-PHD 61300411121 (gerade) und 61300411021 (abgewinkelt), Maßzeichnungen.
- Pololu: „0.1″ Crimp Connector Housing 1×4“ (Produkt 1903) mit Maßzeichnung; Crimpkontakte
  (1930, 1931) mit Maßzeichnungen.
- ProtoSupplies: Dupont-Gehäuse 14 × 2,54 mm je Pol, Hinweise zur Rastzunge.
- Kräfte: keine Herstellerangabe für das Kit; Größenordnung aus Buchsenleisten-Datenblättern, als
  Schätzung gekennzeichnet.
