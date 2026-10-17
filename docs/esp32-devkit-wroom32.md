# ESP32-DevKit WROOM-32 (30 Pin, USB-C)

Identifikation vom 17.10.2026 aus einem Foto der Oberseite (`bilder/esp32-devkit-wroom32-oben.jpg`). Maße sind typische Werte für diese Bauform,
das Exemplar ist nicht mit der Schieblehre vermessen.

**Ergebnis:** Klassisches ESP32-Entwicklungsboard mit Modul ESP-WROOM-32 (Aufdruck „ESP-32, WIFI+BT SoC Inside, ISM2.4G 802.11/b/g/n“), 2 × 15 Lochreihen
(ohne eingelötete Stiftleisten), USB-C, Tasten EN und BOOT, LEDs PWR und D2. Die Beschriftung entspricht dem üblichen 30-Pin-DOIT-Board, die Pinbelegung des
Projekts steht auf `plug/power/pinout.html`.

## Eigenschaften

| Punkt | Wert | Sicherheit |
|---|---|---|
| Modul | ESP-WROOM-32, 18 × 25,5 mm, Höhe 3,1 mm (WROOM-32D; ältere Revision 2,8 mm) | Datenblatt, Revision des Moduls unbekannt |
| Platine | etwa 51,8 × 28,2 mm, vier Befestigungslöcher | Referenz (DOIT DevKit V1), nachmessen |
| Platinendicke | 1,6 mm | typisch |
| USB-C-Buchse | etwa 3,3 mm über der Platine | typisch, nachmessen |
| Lochreihen | 2,54 mm Raster, 15 Pins je Seite | Foto |
| Versorgung | VIN 5 V (Boardregler), Pin 3V3 als Ausgang | Referenz |
| Rückspeise-Diode | neben dem USB-Anschluss ein SOD-123-Bauteil „SL“, vermutlich Schottky zwischen USB und 5-V-Netz | Foto, nicht verifiziert |

## Einbauhöhe im Unterkasten

Innenhöhe 16,2 mm (Konzept Stand 6), die obersten 2,9 mm gehören den Dock-Adern.

| Aufbau | Höhe | Luft zur Platte |
|---|---|---|
| A: Winkelleisten oben, Dupont-Buchsen waagerecht | etwa 5,9 mm | etwa 10,3 mm |
| B: Stiftleisten nach unten (6 mm Pins, 2,5 mm Kunststoff), Draht an den Spitzen | 13,4 mm | 2,8 mm, Adernzone braucht 2,9 mm |

Aufbau B berührt also die Adernzone. Empfohlen ist Aufbau A, braucht aber etwa 56 × 54 mm Fläche statt der 60 × 35 mm der Elektronikbox.
Zeichnung, Schaltplan und Lötanleitung: `plug/power/wiring.html` (Artifact, Quelle `plug/power/build_wiring.py`).

## Noch nachzumessen

1. Platine (Länge, Breite, Dicke), Abstand der Lochreihen, Lage der Befestigungslöcher.
2. Höhe von Modul und USB-C-Buchse über der Platine.
3. Höhe der Winkelleiste auf der Platine, Länge der waagerechten Pins.
4. Den Aufdruck am Board mit der Pin-Tabelle vergleichen (Klone vertauschen Pins).

## Foto

| Datei | Inhalt |
|---|---|
| `bilder/esp32-devkit-wroom32-oben.jpg` | Oberseite: Modul, Beschriftung beider Pinreihen, USB-C, EN- und BOOT-Taste |

## Quellen

1. Espressif, ESP32-WROOM-32 Datenblatt, Abschnitt Physical Dimensions: <https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf>
2. Mischianti, DOIT ESP32 DevKit v1 Pinout und Maße (28,2 × 51,8 mm): <https://mischianti.org/doit-esp32-dev-kit-v1-high-resolution-pinout-and-specs/>
