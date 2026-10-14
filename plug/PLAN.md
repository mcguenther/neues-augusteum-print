# Steckmechanismus für beleuchtete Gebäude: Plan

Gebäude des Campusmodells leuchten von innen (WS2812B-LED), sobald sie in der Grundplatte stecken. Dieser Plan fasst
die früheren drei Pläne zusammen: Plan B mit Dupont-Teilen (Kapitel 2), das Institutsgebäude mit Kassette (Kapitel 3)
und den verworfenen JST-Plan (Kapitel 4, nur Zusammenfassung). Chronologie, Passprobe-Runden und die Herkunft der
Konstanten stehen in `plug/STATUS.md`.

Kennzeichnung der Werte: **B** belegt (Zeichnung/Datenblatt), **M** am eigenen Teil gemessen, **A** abgeleitet
(gerechnet), **S** geschätzt. „Unbelegt“ heißt: Der Wert steht so im ursprünglichen Plan und lässt sich weder aus dem
Generator noch aus einer Messung bestätigen.

Alle Zahlen zu Maßkette, Kräften, Plattendicken und Gebäudetabelle stammen aus `dims()`, `forces()` und
`building_table()` in `plug/dupont.py` (Konstanten in `plug/parts.py`) und stehen in `plug/views/dupont/data.json`;
beim Institut aus `plug/build/institute/data.json`. Wer einen Parameter ändert, erzeugt neu (Kapitel 5) und liest die
Werte aus der Ausgabe oder der Ansichtsseite.

## 1. Überblick und Entscheidungen

### 1.1 Wie es zu Plan B und zur Kassette kam

| Frage | Entscheidung | Grund |
|---|---|---|
| Stecker | 2,54-mm-Dupont-Teile (Plan B) statt JST XH (Kapitel 4) | Das Dupont-Set (Preciva 1550 Teile) ist vorhanden. Eine gesonderte Begründung im Plan ist unbelegt. |
| Gebäude | Immer mit Fuß, der in eine tiefe Mulde der Platte taucht | Am Gebäude steht nichts heraus; die Mulde führt beim Stecken. |
| Stecker in der Platte | Abgewinkelte Stiftleiste (Dock A), Alternativen gerade Leiste (B) und Male-Crimp-Gehäuse (C) | A ist dünn, verpolsicher und hat gut zugängliche Lötstellen. |
| Montage der Buchse im Gebäude | Hauptlösung Druckpause, Rückfallebene Kassette mit Schieber | Die Lichtkammer ist nach dem Druck geschlossen; Buchse, Adern und LED müssen vorher eingelegt werden. |
| Kassette am echten Gebäude | Institutsgebäude (Kapitel 3) | Zeigt, dass die Rückfallebene an einem echten Grundriss funktioniert. |
| Passungen und Kaufteilmaße | Mit gedruckten Proben am eigenen Kit nachmessen (`plug/fit_test/`, `plug/sample.py`) | Das Kit ist No-Name; Datenblattwerte stimmten teils nicht (Körper der Winkelleiste 2,0 statt 2,54 mm). |

Die Runden der Passprobe (Spiel der Taschen, Pinlöcher, Körperabmessungen der Winkelleiste) und die Ergebnisse des
Probestücks stehen in `plug/STATUS.md`, Abschnitte 2 bis 4.

### 1.2 Festgelegte Maße der Winkelleiste (nicht ändern ohne neue Messung)

| Größe | Wert | Konstante | Quelle |
|---|---|---|---|
| Körper, Höhe (quer zur Pin-Reihe) | **2,0** | `HDR_BODY` | M |
| Körper, Dicke (in Pin-Richtung) | **2,0** | `HDR_T` | M |
| Körper, Länge (4 Pins, abgebrochen) | 10,66 (4 · 2,54 + 0,5 Abbruchrest) | `HDR_W` | M |
| Pin-Vierkant | 0,64 | `PIN_SQ` | B |
| Senkrechter Pin (Spitze bis Außenkante der Biegung) | 7,0 ±0,5 | `HDR_LEG` | M |
| Gerader Pin zwischen Körper und Knick | 1,0 ±0,5 | `RA_BACK` | M |
| Lötende hinter dem Körper | 3,0 ±0,5 | `RA_TAIL` | M |
| Stiftspitze über Körperoberkante | 5,68 (= 7,0 − 0,32 − 1,0) | `HDR_UP` | A |

Passungen (alle Spiele je Seite): Leistenkörper in der Tasche 0,1 (`SNUG_HDR`), Buchse in der Tasche 0,22 (`SNUG`),
Fuß in der Mulde 0,25 (`CLR`, unter dem Führungsband 0,55 = `CLR` + `RELIEF`). Stiftlöcher 1,4 (`HOLE`, in der Passprobe
mit 0,3 mm Senkung auf der Bettseite), Muldenboden über dem Steckerteil 0,8 (`CEIL`), Fase 0,5 an den Taschenrändern der
Passprobe, Stufe des Lötendenschlitzes auf der Pin-Oberkante plus 0,1 (`STEP_CLR`). Die 0,3-mm-Senkung und die 0,5-mm-Fase
sind nur in der Passprobe (`plug/sample.py`) modelliert, nicht in der Platte (`dock_cuts()`); ob sie dort nötig sind, ist
unbelegt.

## 2. Plan B: Dupont-Teile

Gleicher Zweck wie der JST-Plan, gebaut aus dem vorhandenen 2,54-mm-Dupont-Set.

- Anschauen: `plug/views/dupont/view.html` (3D-Ansicht, Einsteck-Animation, Druckablauf, Maßkette, Tabellen)
- Erzeugen: `python3 -m plug.dupont`, danach `python3 -m plug.views.build_views dupont` (Kapitel 5)

### 2.1 Entscheidung in Kürze

| Frage | Entscheidung |
|---|---|
| Stecker in der Platte | **Abgewinkelte Stiftleiste, 4 Pins, senkrechte Stifte nach oben, Lötenden waagrecht in den Kabelraum** (Dock A). Der Körper sitzt neben den senkrechten Pins. Die Leiste wird von unten in eine Tasche geschoben: Der Muldenboden hält sie gegen Zug, ein Stempel im Deckel gegen Druck. Lötfreie Alternative: Dupont-Gehäuse mit Male-Crimp-Pins (Dock C), kostet 12,4 mm Plattendicke mehr. |
| Stecker im Gebäude | Dupont-Gehäuse 1×4 mit Female-Crimp-Pins, senkrecht, Steckseite nach unten, über einer gedruckten Trichterplatte im Fuß. |
| Montage (Kernproblem) | **Hauptlösung: Druckpause.** Der Druck hält bei 16,60 mm über dem Bett an (nach Schicht 83 bei 0,2 mm). Buchse, Adern und LED liegen als fertige Einheit in Tasche und Kammerboden, alles unterhalb der Pausenebene. Die erste Schicht danach ist ein Riegel, der Buchse und Adern formschlüssig festhält. |
| Rückfallebene | **Kassette von unten:** Buchse und LED sitzen in einer gedruckten Kassette, die von unten in einen Schacht im Fuß geschoben wird. Ein Schieber in einer Schwalbenschwanz-Nut ist zugleich die Trichterplatte und hält alles. Ohne Druckpause, ohne Kleber, reparierbar. |
| Halten des Gebäudes | Reibung der 4 Kontakte plus Federzunge in der Muldenwand, die in eine V-Nut am Fuß rastet. Zusammen etwa 3,9 bis 6,7 N (S). |
| Kodierung | Gebäude: abgeschrägte Ecke an Fuß und Mulde. Leiste A: nur in einer Lage einschiebbar (der versetzte Körper und der Lötendenschlitz passen nur so in die Tasche). Buchse: durch die vorgefertigte Einheit (LED-Pads bestimmen die Lage) und eine Pin-1-Kerbe am Sockel. |

### 2.2 Bauteile und Maße

Quellen: Würth WR-PHD 61300411121 (gerade) und 61300411021 (abgewinkelt), Zeichnungen gelesen; Pololu-Maßzeichnungen für
Dupont-Gehäuse (Produkt 1903) und Crimpkontakte (1930/1931). Das Kit ist No-Name, die Teile können um einige Zehntel
abweichen. Alle Werte stehen in `plug/parts.py` und werden mit der Passprobe nachgemessen.

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
| | Kontakt beginnt nach | ≈ 1,5 mm Stifttiefe (`CONTACT`) | S |
| Male-Crimp-Pin | Länge, Stift | 18,0; Stift 0,64 × 6,08 | B |
| | Überstand über das Gehäuse | ≈ 6,0 (`MPIN_UP`) | S |
| Stiftleiste gerade | Körper, oben, unten | 2,54; 6,0 (±0,2); 3,0 (±0,2); gesamt 11,54 | B |
| | im Modell (Dock B) | Körper 2,0 wie die Winkelleiste, Spitze 5,68 über Körper; ob die gerade Leiste des Kits so ist | unbelegt |
| Stiftleiste abgewinkelt | Körper (gemessen, Datenblatt 2,54 × 2,54 passt nicht) | 10,66 × 2,0 × 2,0 | M |
| | senkrechter Pin bis Außenkante der Biegung | 7,0 (±0,5) | M |
| | gerader Pin zwischen Körper und Knick | 1,0 (±0,5) | M |
| | Lötende hinter dem Körper, von den senkrechten Pins weg | 3,0 (±0,5) | M |
| | Biegeradius | klein (≈ 0,3), im Modell scharf | S |
| Stift | Vierkant | 0,64 (Diagonale 0,91) | B |
| Flachbandkabel | Ader | 28 AWG, Isolation ≈ 0,9 (`WIRE_D` 1,0), Raster 1,27 | S |
| LED-Stück | B × L × Dicke | 10 × 16,7 × 2,2, Pads 5V/DIN/GND | Randbedingung |

### 2.3 Stiftleiste in der Platte

Alle drei Docks stehen im Prototyp nebeneinander (`platte_ABC.stl`, Raster 36 mm). Der Steckerteil wird jeweils **von
unten** in eine Tasche unter dem Muldenboden geschoben. Der 0,8 mm dicke Muldenboden (`CEIL`) hat vier Löcher mit 1,4 mm
(Stiftdiagonale 0,91) und hält den Körper gegen Zug. Gegen den Steckdruck drückt ein Stempel des Deckels auf die
Stirnenden des Körpers. Crush-Rippen (Übermaß 0,12) halten das Teil, bis der Deckel zu ist.

**Geometrie von Dock A (Winkelleiste).** Die senkrechten Pins stehen in der Pin-Reihe bei y = `HY`. Der Körper
(10,66 × 2,0 × 2,0) liegt **neben** den senkrechten Pins: Seine Mitte sitzt 2,32 mm hinter der Pin-Reihe (halbe
Körperdicke 1,0 + 1,0 gerader Pin + halber Pin 0,32), die Lötenden zeigen nach −y. Der waagerechte Pin geht in
Körpermitte-Höhe **durch den Körper**; auf der Seite der senkrechten Pins folgen 1,0 mm gerader Pin, dann der Knick und
der senkrechte Pin (7,0 mm bis zur Spitze, 5,68 mm über der Körperoberkante); auf der Gegenseite ragen 3,0 mm Lötende
heraus. Die Tasche im Plattenblock besteht aus drei von unten offenen Aussparungen:

| Aussparung | Maß | Zweck |
|---|---|---|
| Körpertasche | 10,86 × 2,2 (Körper + 0,1 je Seite), Höhe 2,0 | Körper, Oberkante an der Unterseite des Muldenbodens (z = −10,6) |
| Schacht für Knick und senkrechte Pins | Breite 9,86 (Pinreihe + 0,8 Luft je Seite), von der Körpermitte bis hinter die Pins | Knick und 1 mm Pin hinter dem Körper |
| Lötendenschlitz | Breite wie der Schacht, Länge 5,0 ab Körpermitte (halbe Tasche 1,1 + 3,0 Lötende + 0,9 Luft) | Lötende liegt flach unter der Stufe |

Die Stufe (Decke des Lötendenschlitzes) liegt auf der Pin-Oberkante plus `STEP_CLR` 0,1, also bei z = −11,18 (Körper-
oberkante −10,6, minus halbe Körperhöhe 1,0, plus halber Pin 0,32, plus 0,1). Der Körper wird in x durch Crush-Rippen an den
Stirnseiten gehalten; in y halten ihn die Pins in den Löchern des Muldenbodens.

| | A Winkelleiste | B gerade Leiste | C Male-Crimp-Gehäuse |
|---|---|---|---|
| Stifte | nach oben, 5,68 über Körper | nach oben, im Modell 5,68 (Datenblatt 6,0) | nach oben, ≈ 6,0 (S); die Maßkette rechnet mit 5,68 |
| Anschluss | Lötenden waagrecht nach −y | Lötenden senkrecht nach unten | gecrimpte Adern unten |
| Löten | 4 Lötstellen, gut zugänglich im Kabelraum | 4 Lötstellen, senkrecht, enger | keine |
| Plattendicke (mit Deckel) | **18,2 mm** | 21,2 mm | 30,6 mm |
| Lagegenauigkeit der Stifte | gut (Stifte im Kunststoff fest) | gut | Stifte wackeln im Gehäuse, Muldenboden richtet sie |
| Verpolsicherheit in der Platte | **selbstkodierend** (A): andersherum passen versetzter Körper und Lötendenschlitz nicht | symmetrisch, Pin-1-Marke nötig | symmetrisch, Pin-1-Marke nötig |
| Tausch | Deckel ab, auslöten | Deckel ab, auslöten | Deckel ab, Stecker herausziehen |

Plattendicke: Unterkante des Kabelraums (A: Körperunterkante −12,6 minus 0,5 minus 3,0 Höhe für die Lötstellen = −16,1, auf
Schicht −16,2; B: Lötstiftende −15,6 minus 3,5 = −19,1, auf −19,2; C: Gehäuse-Kabelseite −24,6 minus 4,0 = −28,6) plus
2,0 mm Deckel.

Die Idee „gerade Leiste mit zweitem Dupont-Gehäuse unter der Platte“ ist verworfen: Die Lötseite ist nur 3,0 mm lang,
eine Buchse erreicht darauf kaum ihren Kontaktpunkt (≈ 1,5 mm plus Toleranz). Wer den Körper verschiebt (4,5/4,5), hat
oben zu wenig Stift. Lötfrei geht es sauberer mit Dock C.

**Empfehlung:** Dock A für die große Platte (dünn, verpolsicher, Lötstellen frei zugänglich). Dock C, wenn jemand gar
nicht löten will und 30,6 mm Plattenhöhe in Kauf nimmt.

**Leiste abbrechen:** Mit der Flachzange zwischen Pin 4 und 5 über die Kante biegen; der Körper bricht in der Kerbe.
Der Abbruchrest macht den Körper etwa 0,5 mm länger (10,66). Bruchkante mit dem Cutter glätten, sonst klemmt sie in der
Tasche (Spiel 0,1 je Seite).

**Kodierung und Prüfregel:** Pin 1 (GND) liegt auf der Seite der Kodier-Ecke (−x), sofern die Pads des LED-Streifens von
−x nach +x „GND, DIN, 5V“ lauten (Parameter `PADS`; bei umgekehrter Reihenfolge spiegelt der Generator die Belegung).
Prüfregel vor dem ersten Stecken:
1. Platte: Zwischen den Stiften 1 und 3 liegen 5 V (rot an 3).
2. Gebäude: Durchgang zwischen Buchsenkontakt 1 und 4 (DETECT-Brücke), etwa 0 Ω.
3. Gebäude: Diodenprüfung Kontakt 1 (+) gegen Kontakt 3 zeigt die Schutzdiode der LED; Kontakt 2 gegen 1 ebenfalls.
   Vertauschte Belegung fällt hier auf.

### 2.4 Fuß und Mulde

#### Maßkette (z = 0 Plattenoberseite, gesteckt)

| Größe | Wert | Rechnung |
|---|---|---|
| Stift über Muldenboden (`g1`) | 4,88 | 5,68 (7,0 − 0,32 − 1,0) − 0,8 Muldenboden |
| Fußhöhe = Muldentiefe F | **9,80** | 4,88 + 3,0 Führung + 0,8 Fußfase + 1,0 Muldenfase = 9,68, auf Schichten gerundet |
| Oberkante Leistenkörper | −10,60 | −F − 0,8 Muldenboden |
| Stiftspitzen | −4,92 | −10,6 + 5,68 |
| Trichterplatte | 1,00 | unter der Buchse, Trichter 2,4 → 1,4 mm |
| Steckseite der Buchse | −8,80 | −F + 1,0 |
| Einstecktiefe E | **3,88** | Stiftspitze −4,92 minus −8,80 |
| Kabelseite der Buchse | 5,20 (Tasche bis 5,45) | −8,8 + 14,0 (+0,25 Toleranz) |
| Pausenebene | **6,80** | 5,45 + 1,0 Ader + 0,2 Luft = 6,65, auf Schicht gerundet (16,45 → 16,60 über dem Bett) |
| LED-Unterseite / Chip oben | 4,40 / 6,60 | Pausenebene − 0,2 − 2,2 |
| Kammerboden | 4,80 | LED liegt 0,4 tief |
| Riegel | 6,80 bis 8,00 | 1,2 dick |
| Druckhöhe der Pause | **16,60 mm über dem Bett** (Schicht 83) | 6,80 + 9,8 |

Einheit (Gehäusetasche, Sockel, LED, Querrinne): Tasche 10,6 × 2,98 (Gehäuse + 0,22 je Seite), Sockel 13,0 × 5,38 (Wand
1,2), zusammen mit LED 13,0 × 23,7 mm.

Phasen beim Stecken (Hub g über dem Sitz):

| g | Ereignis |
|---|---|
| 11,8 | Gebäude über der Mulde (Ausgangslage im Modell) |
| 9,8 | Fußfase trifft Muldenfase, fängt bis ±2,05 mm Versatz (0,8 + 1,0 + 0,25) |
| 8,0 | Fasen durchlaufen, Fuß gleitet gerade im Führungsband |
| 4,88 | Stiftspitzen erreichen die Trichterplatte. Der Fuß steckt hier **3,12 mm** gerade in der Mulde. |
| 3,88 | Stiftspitzen erreichen die Buchse (g = E) |
| 2,38 | erster elektrischer Kontakt (S, E − 1,5) |
| 1,0 | 1 mm vor Anschlag |
| 0 | Fuß sitzt auf dem Muldenboden; Federzunge rastet in die Nut |

#### Toleranzkette (seitlich, ungünstigster Fall)

Fuß in Mulde ±0,25, Buchse in Tasche ±0,1 (A: die Crush-Rippen zentrieren; ohne sie wären es ±0,22 = `SNUG`), Leiste in
Tasche ±0,1, Stiftlage der Leiste ±0,15 (B, gerade Leiste; für die Winkelleiste unbelegt), Druckfehler ±0,1 je Teil:
zusammen etwa ±0,7 mm (A). Der Trichter (Öffnung 2,4) fängt Stiftspitzen bis ±0,88 mm (Öffnungsradius 1,2 minus halber
Stift 0,32, A). Danach liegt der Stift im Hals (`HOLE` 1,4) mit höchstens ±0,38 mm Restversatz ((1,4 − 0,64)/2, A); die
Buchsenöffnung (≈ 1,0, S) verträgt bei 0,64 mm Stift nur ±0,18 mm, den Rest muss die Spitze der Kontakte ausgleichen.
Ob das reicht, zeigt Test 2 (Abschnitt 2.9); unbelegt. Kritisch ist der Fall, dass alle Fehler in dieselbe Richtung
gehen; dann schiebt der Trichter das Gebäude um den Rest (das Spiel der Mulde lässt das zu).

Die Toleranz des senkrechten Pins (7,0 ±0,5) wirkt 1:1 auf die Einstecktiefe: E liegt dann zwischen 3,4 und 4,4 mm (A).

#### Klemmgefahr, Ecken, Führungsband

- Die Mulde ist nur in einem Band von 5 mm unter der Fase eng (0,25 mm Spiel je Seite), darunter 0,55 mm. Das verkürzt die
  Reibfläche und lässt bei schiefem Drücken weniger klemmen. Der Fuß wird nur in diesem Band geführt; beim Kontakt sind
  davon 3,12 mm im Eingriff.
- Senkrechte Fußkanten sind mit 0,5 mm gerundet (`FOOT_R`), weil die Innenecken der gedruckten Mulde nicht scharf werden.
  Bei echten Gebäudeumrissen: Umriss um 0,5 mm nach innen und wieder nach außen versetzen (öffnen), damit spitze
  Außenecken verschwinden.
- Lange flache Gebäude (Hörsaalgebäude 55 × 91 mm) in der Mitte drücken. Bei 0,25 mm Spiel und 91 mm Länge kippt das
  Gebäude höchstens 0,3°, das klemmt nicht, wenn man nicht an einem Ende drückt.
- Kodierung: abgeschrägte Ecke (3 mm, `KEY`) an Fuß und Mulde. Unsymmetrische Umrisse kodieren sich selbst; symmetrische
  bekommen die Fase an einer Ecke.

#### Fuß voll oder hohl

Voll modellieren, im Slicer 3 Wände und 10 bis 15 % Infill. Ein hohler Fuß bräuchte über der Kammer eine Brücke über den
ganzen Grundriss (Hörsaalgebäude 90 mm), das geht nicht ohne Rippen. Material beim Hörsaalgebäude 1:1500 etwa 49 cm³
Hüllvolumen (55,1 × 90,7 × 9,8), mit Infill 12 bis 15 g (S, unbelegt).

#### Mindestwände und schmale Gebäude

Die Einheit (Sockel + LED) braucht 13,0 × 23,7 mm, mit 2 mm Rand 17,0 × 27,7 mm. Das Seminargebäude (26,3 mm breit bei
1:1500) nimmt sie längs. Wände beim Würfel (30 mm): Tasche bis Fußaußenseite 4,2 mm (−y-Rand), Sockel bis Fußaußenseite
3,0 mm in y und 8,5 mm in x (A, aus `HY` −9,3 und den Einheitsmaßen).

#### Fuß-Tabelle

Kriterium: Luft = sichtbare Höhe − 1,2 Dach − 6,8 Pausenebene. passt ≥ 6 mm, knapp ≥ 2 mm. Ergebnis aus
`building_table()`.

| Gebäude | 1:1500 | 1:1000 |
|---|---|---|
| Paulinum | passt (31,2) | passt (50,8) |
| Neues Augusteum | passt (17,0) | passt (29,5) |
| Hörsaalgebäude | passt (8,4) | passt (16,6) |
| Seminargebäude | passt (10,8) | passt (20,2) |
| Institutsgebäude | passt (13,1) | passt (23,7) |
| City-Hochhaus | passt (88,4), aber mehrere LEDs nötig | passt (136,6) |
| Moritzbastei | nein (−1,9); ginge mit Fuß 13,8 | nein (1,1); ginge mit Fuß 10,8 |

Das niedrige Hörsaalgebäude passt, weil die 14 mm hohe Buchse zu 8,8 mm im Fuß steckt und nur 5,2 mm ins sichtbare
Gebäude ragt. Für die Moritzbastei kann die Mulde dieses einen Gebäudes tiefer werden (Fuß 13,8 mm); die Platte muss
dafür an der Stelle 4,0 mm dicker sein. Sie bleibt wie geplant ohne LED.

#### Plattenaufbau

- Mini-Platte des Prototyps: 115,1 × 43,1 × 28,6 mm plus Deckel 2,0 mm (zusammen 30,6), Dicke durch Dock C bestimmt. Nur
  mit Dock A wären es 18,2 mm.
- Große Platte (nur Plan, nicht im Generator, unbelegt): Tablett. Oberteil mit den Mulden und Taschen, darunter
  Kabelräume je Dock, die in Kanäle (8 mm breit, 4 mm hoch) zu einer Sammelrinne an der Hinterkante münden. Deckel in
  Segmenten bis 200 mm, mit M3-Blechschrauben (Pilotloch 2,5). Die Deckel-Stempel tragen die Steckerteile.
- Kabelräume sind 18 mm breit, die Decke wird beim Druck als Brücke gedruckt (bis 30 mm unkritisch, S).

### 2.5 Montage in den Druck (Kernthema)

#### Bewertete Wege

| Weg | Beschreibung | Urteil |
|---|---|---|
| a) Druckpause | Druck bis zur Pausenebene, Einheit (Buchse + Adern + LED) einlegen, weiterdrucken. Der Riegel überdruckt Buchse und Adern. | **Hauptlösung.** Keine Zusatzteile, formschlüssig, gleiche Höhe für alle Gebäude, auch das niedrige Hörsaalgebäude. |
| b) Von unten einschieben, LED durch Kanal | Buchse von unten in einen Schacht, LED hochkant vorweg durch denselben Schacht (10 × 2,2 passt durch 10,4 × 2,8). | Verworfen als Hauptweg: Die LED steht dann senkrecht über der Buchse; das braucht 14 + 3 + 16,7 mm Höhe und passt nur in hohe Gebäude. Kein Anschlag für die Buchse, weil LED und Buchse fast gleich breit sind. |
| c) Separates Steckmodul (JST-Plan) | Modul mit Buchse und LED rastet von unten in den Boden. | Als **Kassette** übernommen (Rückfallebene), aber mit Schieber statt Schnapparmen. |
| d) Zweiteiliges Gebäude | Dach oder Boden abnehmbar. | Möglich, aber sichtbare Fuge am Modell, und jedes Gebäude braucht eine eigene Trennstelle und Rastung. Nur für das City-Hochhaus (mehrere LEDs) sinnvoll. |
| e) Kassette mit Schieber | Kassette von unten, gehalten von einem Schieber in einer Schwalbenschwanz-Nut, der zugleich Trichterplatte ist. Die Muldenwände blockieren den Schieber, solange das Gebäude steckt. | **Rückfallebene.** Reparierbar, ohne Pause. Kostet einen Schacht von 13,4 × 25,4 mm im Fuß (Kassette 13,0 × 25,0 × 15,1, Spiel 0,2 je Seite) und zwei Zusatzteile (Schieber beim Würfel 17,7 × 30,0 × 1,0). |
| f) Heißkleber | Buchse in offene Tasche kleben, LED auf Kammerboden. | Nur, wenn die Kammer offen ist, also nur mit d). Rückfall für Reparaturen. |

#### Ablauf mit Druckpause

1. **Einheit vorbereiten** (Montagelehre `montagelehre.stl`, gleiche Geometrie wie im Gebäude): LED in die Mulde der Lehre
   kleben, Adern an die Pads löten (GND, DIN, 5V; DETECT ebenfalls an GND), Adern über den Sockel zur Tasche legen,
   ablängen, crimpen, Kontakte in der Reihenfolge 1 bis 4 ins Gehäuse stecken (Dreieck = Pin 1 zur Kerbe am Sockel).
   DETECT läuft in der Querrinne unter den anderen Adern. Einheit prüfen (Durchgang 1–4, LED am Testdock).
2. **Slicen und Pause setzen.** Pause **vor Schicht 84** (Oberkante 16,80 mm), also nach Schicht 83 (16,60 mm) bei 0,2 mm
   Schichthöhe. In der Vorschau prüfen: Tasche offen, Riegel noch nicht gedruckt.
   - PrusaSlicer: Vorschau, rechten Schichtregler auf 16,80 stellen, auf das „+“ am Regler klicken (Rechtsklick →
     „Pause einfügen“). Druckereinstellungen → Benutzerdefinierter G-Code → „Pause-Druck G-Code“ muss `M601` enthalten
     (bei Prusa voreingestellt).
   - Bambu Studio: Vorschau, Schichtregler auf 16,80, Rechtsklick → „Pause hinzufügen“.
   - Cura: Erweiterungen → Nachbearbeitung → G-Code ändern → Skript hinzufügen → „Pause at height“; „Pause at“ = Höhe
     16,8 mm (oder Schicht 84), Methode passend zur Firmware (Marlin `M0`/`M25`, Klipper `PAUSE`, Prusa `M601`).
   - Brückenerkennung an, Z-Hop bei Fahrten an (0,4 mm), Bett bleibt warm.
3. **Pause:** Einheit einlegen: Buchse mit der Steckseite nach unten in die Tasche drücken (Rippen klemmen sie), Adern
   flach über die Kerbe legen, LED in die Mulde drücken. Prüfen: Mit einer Karte (Visitenkarte) über die Sockeloberkante
   streichen; nichts darf hängen bleiben. Innerhalb von 10 Minuten fortsetzen.
4. **Weiterdrucken:** Die erste Schicht ist der Riegel (Brücke über 10,6 mm), er drückt die Adern leicht auf die Buchse
   und wirkt als Zugentlastung. Danach Kammer und Dach.
5. **Nachbearbeiten:** Trichter von unten mit 1,0-mm-Bohrer von Hand entgraten (der Trichterhals ist 1,4 mm, der Bohrer
   entgratet also nur den Rand; unbelegt, ob nötig), Fußfase prüfen.
6. **Stecken:** Gebäude über die Mulde, Kodier-Ecke beachten, in der Mitte drücken.

Risiken und Gegenmittel: Düse streift eine hochstehende Ader (Kartenprobe, `WIRE_GAP` auf 0,4); Schichthaftung nach der
Pause (PLA unkritisch bis etwa 15 min, Bett warm lassen, S); Riegel hängt durch (Brücke nur 10,6 mm, Durchhang wirkt als
Klemmung); Buchse zu hoch (Tasche ist für 14,25 mm ausgelegt, längere Gehäuse vorher aussortieren). Die Pausenprobe
(`pausenprobe.stl`, 17,0 × 27,7 × 17,8 mm, etwa 20 min, S) übt genau diesen Ablauf vorher.

**Pausenhöhe aus dem Generator:** `dims()["pause_mm"]` (16,60) und `dims()["pause_layer"]` (83); der Generator druckt
beides aus. Bei anderer Schichthöhe `LAYER` ändern; alle Höhen werden auf Schichten gerundet.

**Reparierbarkeit:** Die überdruckte Buchse ist nicht lösbar. Eine defekte LED heißt: Gebäude neu drucken (Würfel etwa
2 h, 15 g, S). Darum wird die Einheit vor dem Einlegen geprüft. Wer Reparierbarkeit braucht, nimmt die Kassette.

**Schrägdach:** Die Pause liegt 6,8 mm über der Platte, weit unter jedem Dach. Die Kammer folgt dem Gebäudeumriss;
Dachflächen ab 45° drucken ohne Stützen, flachere Dächer bekommen innen eine 45°-Zeltdecke. Bei spitz zulaufender Kammer
ändert sich an Buchse und LED nichts.

### 2.6 Halten ohne Kleber

Alle Kräfte mit A oder S sind Abschätzungen, keine Messungen (unbelegt, bis der Probedruck ausgewertet ist).

| Stelle | Richtung | Lösung | Kraft |
|---|---|---|---|
| Buchse im Gebäude | Druck nach oben beim Stecken | Riegel über Adern (0,6 mm Luft, Adern wirken als Polster) | Riegel trägt > 50 N (A) |
| | Zug nach unten beim Ziehen | Trichterplatte unter der Steckseite | > 50 N (A) |
| | seitlich, Klappern | Crush-Rippen an Stirnseiten und glatter Seite (0,12). Die Seite mit den Rastfenstern bleibt frei, sonst drücken die Rippen die Rastzungen ein und die Kontakte rutschen heraus. | – |
| Adern | Zug an der LED | Riegel klemmt die Adern auf der Buchse (Zugentlastung) | – |
| Leiste in der Platte | Zug nach oben | Muldenboden 0,8 mm, Stifte durch 1,4-mm-Löcher | > 30 N (A) |
| | Druck nach unten | Stempel im Deckel unter den Körperenden | > 50 N (A) |
| Gebäude | Herausziehen | Kontaktreibung 1,2 bis 4,0 N (S, 0,3 bis 1,0 N je Kontakt) + Federzunge 2,7 N axial (A) | **3,9 bis 6,7 N**, Ziel 3 bis 8 N |
| | Stecken | 4,0 bis 8,0 N (S) + 2,7 N | 6,7 bis 10,7 N, Ziel < 15 N |
| Platte | Mitheben beim Ziehen | Mini-Platte (≈ 50 g, S) hebt mit: mit der anderen Hand halten. Große Platte (≈ 500 g, S) liegt bei 5 N Zugkraft an der Grenze; Gummifüße helfen nicht gegen Abheben, Gewicht oder Festschrauben schon. | – |

Federzunge: waagrechter Biegebalken in der Muldenwand (10 mm lang, 1,2 mm dick, 3,8 mm hoch, in der XY-Ebene gedruckt),
Nase 0,5 mm mit 45°-Flanken, Auslenkung 0,25 mm. Normalkraft 3·E·I·δ/L³ = 1,44 N bei E = 3500 N/mm², über die Flanke mit
μ = 0,3 etwa 2,7 N axial (2,67), Randdehnung 0,45 % (PLA verträgt 4 bis 8 %). Die Werte stammen aus `forces()`.

Option Magnete: 6 × 2 mm N35 in Fuß und Muldenboden, je unter 0,6 mm Wand. Etwa 2 bis 4 N (S). Nur nötig, wenn die
Federzunge im Test nicht reicht. Abstand zu den Stiften ≥ 8 mm.

Messen mit Federwaage (oder Kofferwaage bis 10 kg mit Haken): Schlaufe aus Faden um das Gebäude (unter das Dach kleben)
bzw. Haken in eine Bohrung am Prüfling, senkrecht ziehen, Höchstwert ablesen. Platte dabei festhalten. Je Test
5 Messungen, Mittelwert und kleinster Wert notieren.

### 2.7 Elektrik und Kabel (kurz)

- Pins: 1 GND, 2 DIN, 3 +5 V, 4 DETECT (im Gebäude an GND). Controller liest DETECT mit Pull-up, LOW = Gebäude steckt.
  Eine Datenleitung je Dock.
- Crimpen: Abisolieren 2,0 mm (Drahtkralle 1,6 lang), Isolation endet unter der Isolationskralle. Kleinstes Nest der
  Zange; bei 28 AWG die Isolationskralle fest zudrücken oder die Ader vor dem Crimpen um 2 mm umlegen. Kontakt mit der
  Rastlanze zur Fensterseite des Gehäuses einschieben, bis er klickt; mit 5 N an der Ader ziehen, er darf nicht
  herauskommen.
- LED: Pads verzinnen, Adern 1 mm abisoliert anlöten, DETECT-Ader in der Querrinne zum GND-Pad.
- Platte: Flachbandkabel ist brauchbar (10 Adern). Je Dock 4 Adern auftrennen und an die Lötenden löten (Schrumpfschlauch
  1,5 mm). Für 5 V und GND bei mehr als 4 Docks eine dickere Sammelleitung (22 AWG) entlang der Sammelrinne, die Docks
  zweigen davon ab.
- Controller: ESP32, je Dock ein Ausgang für DIN und ein Eingang für DETECT. Pegel 3,3 → 5 V mit 74AHCT125, 330 Ω in
  Reihe je Datenleitung, 1000 µF am 5-V-Eingang.
- Strom: 60 mA je LED bei Vollweiß, sieben LEDs unter 0,5 A; 28 AWG trägt das auf kurzen Wegen.
- Hot-Plug: Alle Stifte sind gleich lang. Datenleitung erst nach DETECT = LOW plus 100 ms freigeben.

### 2.8 Vergleich mit dem JST-XH-Plan

| | JST XH (Kapitel 4) | Dupont (dieser Plan) |
|---|---|---|
| Haltekraft Stecker | höher, Header-Hülse führt, Buchse sitzt fest | geringer, nur Kontaktreibung (S: 1,2–4 N), plus Federzunge |
| Platzbedarf im Gebäude | Modul 23,7 × 17 mm im Boden (Wert aus dem früheren Vergleich, im JST-Plan nicht belegt) | Einheit 13,0 × 23,7 mm, Buchse 14 mm hoch (8,8 mm im Fuß) |
| Kosten / vorhanden | Header, Buchsen, Kabel kaufen | alles im Set außer LED-Streifen |
| Lötarbeit | Header auf Platine (Variante B) | Platte: 4 Lötstellen je Dock (A) oder keine (C); LED immer |
| Wiederholbarkeit | Fertigteile, gleichmäßig | Crimpen von Hand, No-Name-Toleranzen |
| Kodierung | Header-Hülse ist gepolt | keine am Stecker; über Fuß, Leistenform, Einheit |
| Stapelhöhe | Header 7 + Buchse 7,75 | Leiste 2,0 + Stift 5,68 + Buchse 14 |
| Montage im Gebäude | Modul von unten, Schnapparme | Druckpause oder Kassette |
| Risiko | Schnapparme (PLA), Modul-Toleranzkette | Kontaktqualität bei 3,88 mm Einstecktiefe, Pausen-Handgriff |

**Empfehlung:** Mit dem vorhandenen Set zuerst den Dupont-Prototyp drucken. Wenn die Passprobe und die Pausenprobe
gelingen und die Kontakte bei 3,88 mm Einstecktiefe sicher sind, ist dieser Plan für die ganze Platte besser: kein
Zukauf, kein Steckmodul, weniger Teile im Gebäude. Die Platte wird mit Dock A etwas dicker (18,2 mm statt 17,45 mm im
JST-Plan). Der JST-Plan ist besser, wenn Gebäude oft gesteckt werden (Steckzyklen, gepolter Stecker) oder wenn die
Dupont-Kontakte im Test unter 3 N halten oder aussetzen.

### 2.9 Testplan mit Abbruchkriterien

| # | Test | Erfolg | Abbruch / Änderung |
|---|---|---|---|
| 1 | Passprobe v6 (Winkelleiste, `plug/fit_test/`): Körper in Tasche (Körper + 0,2), Stufe auf drei Körperhöhen (2,0 / 1,8 / 1,6), Löcher 1,4 | Körper sitzt ohne Wackeln, Lötende liegt flach auf der Stufe, Pins kommen gerade durch die Löcher | Körper wackelt oder fällt zu tief: `HDR_BODY`, `HDR_T`, `SNUG_HDR` anpassen; Lötende liegt nicht auf: `STEP_CLR` |
| 2 | Kontakt bei 3,88 mm | Leiste mit 1,8-mm-Distanzstück (Muldenboden 0,8 + Trichterplatte 1,0) in eine Buchse stecken: Durchgang stabil beim Wackeln | Aussetzer: `CEIL`/`FUNNEL_T` auf 0,6 senken (E = 4,48, Fußhöhe 10,0); bleibt es unsicher: JST-Plan |
| 3 | Pausenprobe | Düse streift nichts, Buchse wackelt nicht, Ader hält 5 N | Streift: `WIRE_GAP` 0,4; Buchse lose: `RIB` 0,2 |
| 4 | Platte mit Docks A, B, C, Deckel | Steckerteil hält 30 N Zug und 30 N Druck | Hält nicht: Muldenboden 1,6 mm, Stempel breiter |
| 5 | Würfel mit Pause, stecken | Stecken < 15 N, Ziehen 3–8 N, LED an, DETECT LOW | Ziehen < 3 N: Nase 0,6 mm oder Magnete; > 8 N: Nase 0,4 mm |
| 6 | Kodierung | Gedrehter Würfel fällt nicht in die Mulde | – |
| 7 | 50 Steckzyklen | Ziehkraft fällt um weniger als 30 %, kein Aussetzer | Aussetzer: Kontakte vergoldet kaufen oder JST |
| 8 | Kassette | Schieber hält, Tausch in < 2 min | Schieber fällt heraus: Raste am Schieber ergänzen |
| 9 | Licht | 0,4 oder 0,8 mm Wand leuchtet gleichmäßig | – |

### 2.10 Offene Annahmen (an den echten Teilen prüfen)

- Gehäusemaße des Kits (10,16 × 2,54 × 14,0) und die Eintrittsöffnung (≈ 1,0 mm).
- Winkelleiste: Die Maße 7 / 1 / 3 mm sind auf ±0,5 gemessen; die Einstecktiefe schwankt damit zwischen 3,4 und 4,4 mm.
- Gerade Leiste (Dock B): Körper 2,0 wie die Winkelleiste? Stiftlänge 6,0 oben und 3,0 unten laut Datenblatt, im Modell
  5,68 oben.
- Überstand der Male-Crimp-Pins aus dem Gehäuse (≈ 6,0) für Dock C.
- Kontakt sicher bei 3,88 mm Einstecktiefe (Kontaktpunkt bei ≈ 1,5 mm angenommen).
- Wirkung des Trichterhalses von 1,4 mm: Er führt die Stifte weniger eng als der frühere Hals von 1,1 mm.
- Halte- und Steckkraft je Kontakt (0,3–1,0 N / 1–2 N angenommen).
- Aderdurchmesser des Flachbandkabels (≈ 0,9 mm) und ob 28 AWG sicher crimpt.
- Pad-Reihenfolge und Pad-Abstand des eigenen LED-Streifens (`PADS`, `PAD_X`).
- Biegemodul und Reibwert des Filaments (Federzunge).
- Seite der Rastfenster des Gehäuses: Im Modell −y (zur Gebäudemitte abgewandt).

### 2.11 Quellen

- Würth Elektronik WR-PHD 61300411121 (gerade) und 61300411021 (abgewinkelt), Maßzeichnungen (für die Winkelleiste des
  Kits durch eigene Messung ersetzt).
- Pololu: „0.1″ Crimp Connector Housing 1×4“ (Produkt 1903) mit Maßzeichnung; Crimpkontakte (1930, 1931) mit
  Maßzeichnungen.
- ProtoSupplies: Dupont-Gehäuse 14 × 2,54 mm je Pol, Hinweise zur Rastzunge.
- Kräfte: keine Herstellerangabe für das Kit; Größenordnung aus Buchsenleisten-Datenblättern, als Schätzung
  gekennzeichnet.

### 2.12 Geänderte Werte gegenüber dem ursprünglichen Plan

Alt = Stand des Dupont-Plans vor der Zusammenführung (teils noch Werte vor Passprobe-Runde 4), neu = aktueller Generator.

- Körper der Winkelleiste: 2,54 × 2,54 → 2,0 × 2,0 (`HDR_BODY`, `HDR_T`), Länge → 10,66 (abgebrochen, `HDR_W`).
- Geometrie Dock A: „Stifte durch den Körper, Lötenden darunter, Biegung 1,5 hinter dem Körper“ → Körper neben den
  senkrechten Pins, waagerechter Pin durch den Körper, 1,0 gerader Pin, 3,0 Lötende (±0,5 gemessen statt ±0,2).
- Stiftspitze über Körper (Dock A): 6,0 → 5,68 (`HDR_UP`).
- Richtung der Lötenden: nach hinten (+y) → −y (so im Generator).
- Muldenboden: 1,2 (Abschnitt Stiftleiste) → 0,8 (`CEIL`).
- Stiftlöcher: 1,25 → 1,4 (`HOLE`); Trichterhals 1,1 → 1,4.
- Spiel Buchse in Tasche: 0,1 → 0,22 (`SNUG`); Leistenkörper 0,1 unverändert (`SNUG_HDR`).
- Crush-Rippen: 0,15 → 0,12 (`RIB`).
- Pausenebene: 6,60 → 6,80; Rechnung 5,25 + 1,0 + 0,2 → 5,45 + 1,0 + 0,2 = 6,65, auf Schicht 6,80.
- Druckhöhe der Pause: 6,60 + 10,0 → 6,80 + 9,8 (Ergebnis 16,60 und Schicht 83 unverändert).
- LED-Unterseite / Chip oben: 4,20 / 6,40 → 4,40 / 6,60; Kammerboden 4,60 → 4,80; Riegel 6,60–7,80 → 6,80–8,00.
- Gerade Führung beim Kontakt: 3,0 → 3,12 mm.
- Hub-Phasen: 10,0 / 8,2 / 5,2 / 4,2 / 2,7 → 9,8 / 8,0 / 4,88 / 3,88 / 2,38.
- Trichter: Fangbereich ±0,65 → ±0,88, Rest im Hals ±0,23 → ±0,38 (neu gerechnet, A).
- Plattendicke mit Deckel: Dock A 20,0 → 18,2; B 22,0 → 21,2; C 30,8 → 30,6. Mehrdicke Dock C gegenüber A: 10,8 → 12,4.
- Mini-Platte: 115 × 43 × 28,8 → 115,1 × 43,1 × 28,6 (plus 2,0 Deckel).
- Platte mit Dock A gegenüber JST: „20,0 statt 17,45“ → „18,2 statt 17,45“.
- Fuß-Tabelle (Luft 1:1500 / 1:1000): Paulinum 31,4 / 51,0 → 31,2 / 50,8; Neues Augusteum 17,2 / 29,7 → 17,0 / 29,5;
  Hörsaalgebäude 8,6 / 16,8 → 8,4 / 16,6; Seminargebäude 11,0 / 20,4 → 10,8 / 20,2; Institutsgebäude 13,3 / 23,9 →
  13,1 / 23,7; City-Hochhaus 88,6 / 136,8 → 88,4 / 136,6; Moritzbastei −1,7 / 1,3 → −1,9 / 1,1.
- Moritzbastei: Platte 3,8 mm dicker → 4,0 mm (Fuß 13,8 und 10,8 unverändert).
- Kriterium der Fuß-Tabelle: Pausenebene 6,6 → 6,8.
- Buchse im Fuß / im Gebäude: 9 / 5 mm → 8,8 / 5,2 mm.
- Einheit Sockel + LED: 12,8 × 23,4 (mit Rand 16,8 × 27,4) → 13,0 × 23,7 (mit Rand 17,0 × 27,7).
- Wand Tasche bis Fußaußenseite beim Würfel: 4,4 → 4,2 mm (zusätzlich Sockel 3,0 in y, 8,5 in x).
- Hörsaalgebäude Material: 50 → 49 cm³ Hüllvolumen.
- Riegel-Brücke und Gehäusetasche: 10,4 → 10,6 mm.
- Schacht der Kassette im Fuß: 13,2 × 25,2 → 13,4 × 25,4 mm.
- Einstecktiefe in Tests und Vergleich: 4,2 → 3,88 mm; Test 2 mit 0,6-mm-Maßen: E = 4,6 → 4,48.
- Stapelhöhe Dupont: Leiste 2,54 + Stift 6 → Leiste 2,0 + Stift 5,68.
- Test 1 (Passprobe): „Buchse in 0,1-Tasche, Stift durch 1,1-Loch“ → Passprobe v6 (Stufenhöhe, Loch 1,4).
- Offene Annahme „Lage der Biegung (1,5)“ → entfällt (gemessen: 1,0 gerader Pin).

## 3. Institutsgebäude mit Kassette

Zeigt, wie die Kassette aus Kapitel 2 in einem echten Gebäude funktioniert: dem Institutsgebäude (Laserscan, 1:1000),
mit Fuß, Lichtkammer, Lichtfenstern und einer Platte mit Dock A. Es ist die Rückfallebene von Plan B, keine zweite
Konstruktion.

- Anschauen: `plug/build/institute/view.html` (Zusammenbau-Animation, Einstecken, Schnitte, Explosion; gitignoriert,
  wird erzeugt)
- Erzeugen: `python3 -m plug.institute` (STL nach `stl/steckmodul_institut/`, Bilder nach
  `vorschau/steckmodul_institut/`, Daten und `gebaeude.stl` nach `plug/build/institute/`, rund 45 s), danach
  `python3 -m plug.views.build_views institute`.

### 3.1 Was anders ist als beim Würfel

- **Großzügige LED-Ablage** (`SEAT_W` × `SEAT_L` = 13,0 × 21,0 mm, vorher 10,3 × 17,0 mm): Streifen bis 12 mm Breite und
  21 mm Länge, Lage frei, DIN-Ende zur Buchse. Die Bodenöffnung im Gebäude ist 0,15 mm je Seite größer (`SEAT_M`). Die
  Kassette ist dadurch 15,7 × 29,3 mm groß (beim Würfel 13,0 × 25,0).
- **Schieber quer durch die lange Wand** (Schwalbenschwanz entlang x, 20,1 × 34,0 × 1,0 mm) statt längs durch das
  Gebäude: kurzer Weg von etwa 21 mm. Er schließt mit der Fußfase bündig ab, die Muldenwand sperrt ihn.
- **Fuß aus dem echten Grundriss**: Grundriss nach unten extrudiert, Kanten gerundet (0,5 mm), unten 0,8 mm Fase in
  Schichtstufen (0,2 mm); Mulde folgt mit 0,25 mm Spiel im Führungsband, darunter 0,55 mm, oben 1,0 mm Fase. Keine
  Kodier-Ecke: Der Grundriss passt nur in einer Richtung.
- **Lichtkammer**: je Höhe der um 1,2 mm geschrumpfte Querschnitt des Gebäudes in 1,2 mm höherer Lage, damit Wand und
  Dach überall mindestens 1,2 mm dick bleiben (`chamber()`). Zwei Reihen Lichtfenster (Unterkanten 9,0 und 15,0 mm über der
  Plattenoberseite, je 3,6 × 4,5 mm im Abstand 6,0 mm), auf 0,4 mm abgedünnt.
- **Platte**: Mulde nach dem Fußumriss, nur Dock A (18,2 mm dick mit Deckel: 16,2 mm Platte plus 2,0 mm Deckel),
  Federzunge in der langen Muldenwand. Pin-Reihe, Maßkette, Pausen- und Kassettenhöhen sind die aus Abschnitt 2.4
  (F 9,8, E 3,88).

### 3.2 Maße (aus `plug/build/institute/data.json`)

| Größe | Wert |
|---|---|
| Gebäude mit Fuß (B × T × H) | 38,8 × 102,7 × 41,5 mm (sichtbar 31,7, Fuß 9,8) |
| Kassette | 15,7 × 29,3 × 15,1 mm |
| Schieber | 20,1 × 34,0 × 1,0 mm, Weg etwa 21,1 mm |
| Platte / Deckel | 51,8 × 115,8 × 16,2 mm / 51,8 × 115,8 × 5,6 mm (mit Stempeln) |
| LED-Ablage | 13,0 × 21,0 mm; Streifen 60 LED/m (10 × 16,7) und 144 LED/m (12 × 13,9) |

### 3.3 Maßstab

Bei 1:1000 ist der Hauptbalken 22,0 mm breit (Wand neben dem Schacht 2,95 mm). Bei 1:1500 sind es 14,7 mm: Die Kassette
passt dort nicht (Hauptbalken müsste mindestens 20,1 mm breit sein). Dafür bräuchte sie eine schmalere Ablage (etwa
5-mm-Streifen).

### 3.4 Offene Punkte

- Der Schieber ist nur 1,0 mm dick und kann sich verziehen; zuerst Kassette und Schieber allein in einem Probestück testen
  (`python3 -m plug.sample`, Kapitel 5).
- Das Dach der Kammer überbrückt im breiten Flügel bis etwa 30 mm (unbelegt); Brückenerkennung des Slicers nutzen.
- Federzunge und Haltekräfte stammen aus Plan B und sind für diese Wand nicht neu gerechnet.

## 4. Archiv: JST (verworfen)

Der erste Plan nutzte einen 4-poligen JST-XH-Stecker (Header B4B-XH-A in der Platte, Buchse XHP-4 mit Kabel in einem
Steckmodul, das von unten in den Gebäudeboden rastet; Pinbelegung wie in Plan B). Einstecktiefe 4,95 mm, Plattendicke
17,45 mm (16,45 mm mit Fuß-Variante). Er wurde durch Plan B abgelöst; der Grund (Dupont-Set vorhanden) ist im Plan nicht
gesondert belegt. Der Plan, der JST-Generator, die Ansicht und die STL-Dateien liegen unverändert in `plug/archive/jst/`
(Plan: `plug/archive/jst/PLAN.md`). Die Kassette von Plan B übernimmt die Idee des Moduls, der Fuß die Idee „nichts steht
am Gebäude heraus“. Der JST-Code wird nicht mehr gepflegt.

## 5. Dateiübersicht und Aufrufe

Alle Aufrufe aus dem Repo-Wurzelverzeichnis.

| Aufruf | Dauer | Schreibt |
|---|---|---|
| `python3 -m plug.dupont` | | `stl/steckmodul_dupont/` (Platte ABC, Deckel, Würfel Pause/Kassette, Kassette, Schieber, Pausenprobe, Montagelehre), `vorschau/steckmodul_dupont/`, `plug/views/dupont/data.json` |
| `python3 -m plug.institute` | rund 45 s | `stl/steckmodul_institut/` (ohne `gebaeude.stl`), `vorschau/steckmodul_institut/`, `plug/build/institute/` (`data.json`, `gebaeude.stl`; gitignoriert) |
| `python3 -m plug.sample` | rund 15 s | `stl/steckmodul_probe/` (Probestück, `0_passprobe.stl`, `README.txt`, `probedruck_kassette.zip`), `vorschau/steckmodul_probe/` |
| `python3 -m plug.views.build_views [dupont\|institute\|all]` | | `plug/views/dupont/view.html`, `plug/build/institute/view.html` |
| `python3 -m plug.fit_test.build_page` | | `plug/fit_test/page.html` (Anleitung der Passprobe) |
| `python3 -m plug.build_all [--skip-institute]` | | alles oben in der richtigen Reihenfolge |
| `python3 -m plug.check [--skip-institute]` | | prüft, dass alle STL `dicht=True` melden und „keine Kollisionen“ gemeldet wird |

Module: `plug/geom.py` (Geometriewerkzeuge), `plug/parts.py` (Kaufteile und Passungen, einzige Quelle der Konstanten),
`plug/dupont.py` (Plan B), `plug/institute.py` (Kapitel 3), `plug/sample.py` (Probestück), `plug/fit_test/` (Passprobe
Winkelleiste, Anleitungsseite, Maßseite `angled_pin.html`), `plug/views/` (Ansichtsseiten), `plug/archive/jst/` (Kapitel 4).
Chronologie, Passprobe-Ergebnisse und offene Aufgaben: `plug/STATUS.md`.

Die Ausgabe von `plug.dupont`, `plug.institute` und `plug.sample` muss je Teil `dicht=True` und „keine Kollisionen“ zeigen.
