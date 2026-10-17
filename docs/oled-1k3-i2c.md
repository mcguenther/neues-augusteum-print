# 1,3″-I²C-OLED, 128 × 64 (AliExpress)

Identifikation vom 17.10.2026 aus drei Fotos und öffentlichen Unterlagen (Recherche als PDF, Fotos in `docs/bilder/`).
Keine Herstellerbestätigung für den konkreten AliExpress-Artikel; Angaben zu Chip und Versorgung stammen teils von Referenzmodulen.

**Ergebnis:** 1,30″-OLED-Modul, monochrom, I²C, 128 × 64 Pixel, 4 Anschlüsse (sicher). Treiber-IC vermutlich **SH1106**, **CH1116G**
ist als Alternativbestückung möglich (nicht bestätigt, nur per Funktionstest klärbar).

## Eigenschaften

Das Datenblatt der ETT CO., LTD. für das baugleiche Referenzmodul liegt als `datenblaetter/oled-1k3-i2c-sh1106-ett.pdf` im Repo
(Quelle: [robu.in](https://robu.in/wp-content/uploads/2019/12/1.3-Inch-I2C-IIC-OLED-LCD-Module-4pin-with-VCC-GND-Blue-1.pdf)). Es nennt
SH1106, 3,3–5 V, 128 × 64, I²C, PCB 33,7 × 35,5 mm, Gesamtstrom ca. 8 mA und die Pinfolge VDD, GND, SCK (= SCL), SDA; Signale dürfen
direkt an 3,3-V- und 5-V-Controller, und es gibt Weiß- und Blau-Varianten. Es betrifft das Referenzmodul, nicht das gekaufte Exemplar.

| Punkt | Wert | Sicherheit |
|---|---|---|
| Modulfamilie | 1,3″ OLED, monochrom, 128 × 64 | sehr sicher |
| Schnittstelle | I²C (Aufdruck „IIC“), vier Anschlüsse | sicher |
| Controller | SH1106 wahrscheinlich, CH1116G denkbar | nicht bestätigt |
| Panelkennung | GME12864-70 (vom Flexkabel abgelesen); wird beim Panelanbieter als weiß geführt | Farbe nicht per Foto bestätigt |
| Weitere Aufdrucke | `1.30″ IIC` (Rückseite), `9E3042A1` (Displayfolie, keine bestätigte Verkaufs-/Controllerbezeichnung), 30-poliges Flexkabel | – |
| Versorgung | 3,3–5 V laut Unterlagen vergleichbarer SH1106-Platinen; am ESP32 zuerst 3,3 V | Referenz |
| I²C-Adresse | typisch 0x3C, ggf. 0x3D; am Modul scannen | Referenz |
| Platine | ca. 33,7 × 35,5 mm, vier Befestigungslöcher (Maß vom Referenzmodul, nicht nachgemessen) | Referenz, nachmessen |

## Anschluss an den ESP32

Pin-Reihenfolge laut Aufdruck auf der Vorderseite: **VDD, GND, SCK, SDA**. „SCK“ ist hier der I²C-Takt SCL, kein SPI.

| Display | ESP32 (klassisch) |
|---|---|
| VDD | 3,3 V |
| GND | GND |
| SCK | SCL (GPIO22) |
| SDA | SDA (GPIO21) |

GPIO21/22 gelten für den klassischen ESP32, bei anderen Varianten anpassen. Reihenfolge am echten Aufdruck prüfen.

## ESPHome: erster Funktionstest

```yaml
i2c:
  sda: GPIO21   # klassischer ESP32; ggf. anpassen
  scl: GPIO22
  scan: true

display:
  - platform: ssd1306_i2c
    model: "SH1106 128x64"
    address: 0x3C   # I²C-Scan prüfen
    lambda: |-
      it.rectangle(0, 0, 128, 64);
      it.line(0, 0, 127, 63);
```

Das ist nur der Ausschnitt für I²C und Display; die bestehende `esphome:`/`esp32:`-Grundkonfiguration bleibt unverändert.

## Identifikation bestätigen

1. Mit 3,3 V versorgen, SCK an SCL, SDA an SDA.
2. ESPHome starten, im Log den I²C-Scan prüfen (0x3C üblich).
3. Treiber `SH1106 128x64` testen: Rahmen und Diagonale sollten erscheinen.
4. Bleibt die Anzeige leer oder fehlerhaft: Verkabelung und Adresse prüfen, danach CH1116G erwägen (ggf. anderer Treiber).

Ergebnis des Tests hier eintragen (Treiber, Adresse, Displayfarbe, nachgemessene Platinenmaße).

## Fotos

| Datei | Inhalt |
|---|---|
| `bilder/oled-1k3-vorderseite.jpg` | Vorderseite: Panel, vier Befestigungslöcher, Anschlussreihe VDD/GND/SCK/SDA |
| `bilder/oled-1k3-rueckseite.jpg` | Rückseite: Aufdruck 1.30″ IIC, SMD-Bauteile, Flexkabel |
| `bilder/oled-1k3-kennzeichnung.jpg` | Nahaufnahme Displayfolie mit `9E3042A1` |

## Quellen

1. ETT-Modul-Datenblatt (SH1106, 1,3″, I²C, 128 × 64, 3,3–5 V, PCB-Maße): `datenblaetter/oled-1k3-i2c-sh1106-ett.pdf`, Original-Link oben
2. GoldenMorning GME12864-70: Panelkennzeichnung, mögliche Controller SH1106/CH1116G
3. ESPHome-Dokumentation, Plattform `ssd1306_i2c` (inkl. SH1106)

(Die Links zu 2 und 3 standen nur als Text im Recherche-PDF; bei Bedarf nachtragen.)
