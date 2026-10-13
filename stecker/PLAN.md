# Steckmechanismus für beleuchtete Gebäude

Ziel: Jedes Gebäude enthält eine WS2812B-LED und leuchtet von innen, sobald es in die
Grundplatte gesteckt wird. Strom, Daten und ein Erkennungssignal laufen über einen 4-poligen
JST-XH-Stecker. Der Stecker ragt unten nicht aus dem Gebäude, sondern sitzt im Gebäude; aus
der Platte ragt der Gegenstecker nach oben.

Anschauen: `stecker/ansicht.html` (3D-Ansicht mit Animation, Plan, Testliste).
Prototyp erzeugen: `python3 steckmodul.py` (STL nach `stl/steckmodul/`, Bilder nach
`vorschau/steckmodul/`, Daten für die Ansicht nach `stecker/daten.json`), danach
`python3 stecker/baue_ansicht.py`.

## Entscheidung

| Frage | Entscheidung | Grund |
|---|---|---|
| Wer führt beim Stecken? | Zapfen am Modul im Schacht der Platte, mindestens 3,0 mm vor dem Kontakt | Die Gebäude-Aussparung ist nur 1 mm tief und greift erst nach dem Kontakt. Eine 9 mm tiefe Aussparung über die ganze Grundfläche würde jedes Gebäude 9 mm versenken. |
| Wo sitzt der Stecker im Gebäude? | In einem Steckmodul, das von unten in ein Loch im Gebäudeboden rastet | Die Lichtkammer ist nach dem Druck geschlossen. LED und Kabel müssen vorher auf einem Bauteil sitzen, das man von unten einsetzt. Das Modul ist für alle Gebäude gleich. |
| Welcher Stecker? | JST XH 2,5 mm, 4-polig: Header B4B-XH-A in der Platte, Buchse XHP-4 mit Kabel im Modul | Der Header hat eine Hülse, die Stifte schützt. Fertige XH-Kabel sind billig. PH (9,9 × 4,5 mm) wäre kleiner, die Datenblattmaße sind aber widersprüchlich. |
| Pinbelegung | 1 GND, 2 DIN, 3 +5 V, 4 DETECT (im Modul an GND) | Ein Datenkanal je Dock, keine Bypass-Schaltung für leere Docks nötig. |

## Maßkette (mm, gesteckt, Gebäudeboden z = 0)

| Größe | Wert | Berechnung |
|---|---|---|
| Einstecktiefe E | 4,95 | Buchse 7,75 hoch, gesteckt 9,8 über Platine, Header 7,0: Buchse ragt 2,8 heraus, also 7,75 − 2,8 (abgeleitet) |
| Führung | 3,0 | Parameter `GUIDE` |
| Zapfenlänge P | 7,95 | E + Führung |
| Schachttiefe D | 8,45 | P + 0,5 Luft |
| Header-Unterkante | −10,45 | Header sitzt 2 mm im Schachtboden |
| Header-Oberkante | −3,45 | + 7,0 |
| Buchsenstirn gesteckt | −8,40 | Oberkante − E |
| Buchsenrückseite | −0,65 | + 7,75 |
| Platte | 17,45 dick | 1,0 Aussparung + 8,45 Schacht + 3,0 Boden + 5,0 Kabelraum |

Die Rechnung steht in `dims()` in `steckmodul.py`. Beim ersten Kontakt ist das Gebäude
`E = 4,95 mm` über seinem Sitz, der Zapfen steckt dann `P − E = 3,0 mm` im Schacht.

## Halten

Header und Buchse haben keine Flansche. Je Seite gibt es drei Varianten, alle im Prototyp:

- Platte A: Presssitz in Tasche mit Crush-Rippen (0,15 mm Übermaß)
- Platte B: Header auf Lochraster-Platine (22 × 11 mm), von unten mit 2 × M2 verschraubt
- Platte C: lockere Tasche, Heißkleber durch Fenster zum Kabelraum
- Modul A: Presssitz der Buchse mit Rippen
- Modul B: Kabel-Zugentlastung durch zwei Querstifte (S-Führung der Adern)
- Modul C: Heißkleber durch seitliche Fenster

Offen: Das Datenblatt gibt für die XHP-Buchse 4,1 mm Tiefe im Körper und 5,7 mm mit Stufe an.
Zeigt die Stufe nach unten, kann ein zweiteiliges Modul sie als Anschlag nutzen (Buchse fällt
von oben ein). Das hält besser als alle drei Varianten, braucht aber die echte Buchse zum Messen.

## Änderungen am Generator (nächster Schritt, noch nicht umgesetzt)

1. Gebäude hohl erzeugen: Volumen 1,2 mm nach innen versetzen, Boden 2,4 mm.
2. Je Gebäude Modulposition und Ausrichtung wählen (Punkt größter Entfernung zum Rand, längere
   Achse). Modulloch 21 × 14,3 mm mit Kragennische 24,1 × 17,4 mm, Kodier-Ecke.
3. Grundplatte: je Gebäude ein Dock (Schacht, Header-Halterung, Kabelraum, Rinne). Für die große
   Platte als Tablett mit Unterseite aus Kabelraum und Deckel statt Vollmaterial.
4. Moritzbastei (6 mm hoch) bekommt keine LED. Das City-Hochhaus braucht mehrere LEDs.

## Quellen und Verlässlichkeit

- Steckermaße: JST-Katalog eXH (`https://www.jst-mfg.com/product/pdf/eng/eXH.pdf`), Zeichnungen
  gelesen; Einstecktiefe und Hülsenwand sind abgeleitet. Vor dem Druck mit der Schieblehre prüfen.
- Steck- und Haltekräfte nennt JST nicht. Die Zielwerte im Testplan sind Schätzungen.
- WS2812B: Datenblatt (VIH = 0,7 × VDD in der älteren Fassung), Strom 60 mA bei Vollweiß.
- Bestehende Lösungen: Magnet-Pogo für Leuchtfiguren und LED-Würfel (MakerWorld, Hackster),
  FDM-Passungen nach Sovol (Presssitz 0,05–0,15 mm, Gleitsitz 0,2–0,3 mm je Seite).
