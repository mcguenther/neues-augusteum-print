# ESPHome-Firmware „Doktorhut Max“

`doktorhut-max.yaml` ist die Firmware für den ESP32 (WROOM-32) in der Steckplatte. Erster Entwurf, **noch nicht auf der Hardware getestet**;
geprüft ist nur, dass `esphome config` (ESPHome 2026.4.0) die Datei akzeptiert. Kompiliert wurde sie nicht.

## Pinbelegung

| Dock | Gebäude (Vorschlag, noch nicht festgelegt) | DIN (LED-Daten) | DETECT (Steckerkennung) |
|---|---|---|---|
| 1 | Paulinum | GPIO23 | GPIO32 |
| 2 | Neues Augusteum | GPIO19 | GPIO33 |
| 3 | Hörsaalgebäude | GPIO18 | GPIO25 |
| 4 | Seminargebäude | GPIO17 | GPIO26 |
| 5 | Institutsgebäude | GPIO16 | GPIO27 |
| 6 | City-Hochhaus | GPIO4 | GPIO13 |

| Bauteil | Pin |
|---|---|
| I²C SDA (INA226 0x40, OLED 0x3C) | GPIO21 |
| I²C SCL | GPIO22 |
| Gate des MOSFET für den Strompuls der Powerbank | GPIO14 |

Quelle der Belegung ist `plug/power/build_pinout.py` (`DIN`, `DETECT`); ändert sie sich, die YAML nachziehen. Der Kippschalter in der
Westwand trennt nur das Plus der Powerbank und hat keinen GPIO.

## Verhalten

- Gebäude gesteckt (DETECT = LOW, 100 ms entprellt): LED blinkt zweimal grün, dann warmweißes Dauerlicht. Abgezogen: LED aus.
- Jede LED ist in Home Assistant einzeln schalt- und färbbar; nach dem Booten sind alle aus, bis ein Gebäude steckt.
- INA226: Spannung, Strom, Leistung (1 s); dazu „Gebäude gesteckt“ (Anzahl) und WLAN-Signal.
- OLED: Spannung, Strom, Leistung, Anzahl Gebäude und sechs Kästchen (gefüllt = steckt).
- Strompuls der Last alle 5 s für 300 ms (`last_abstand`, `last_dauer`), in Home Assistant über „Powerbank-Puls“ abschaltbar.

## Benutzen

1. `secrets.example.yaml` als `secrets.yaml` kopieren (bzw. in den Secrets des ESPHome-Dashboards `wifi_ssid` und `wifi_password` anlegen).
2. Erste Installation per USB-C (Powerbank dabei abziehen), danach OTA: `esphome run esphome/doktorhut-max.yaml`.
3. Im Log: I²C-Scan muss 0x3C und 0x40 zeigen; DETECT-Wechsel erscheinen als Binärsensor-Meldungen.

## Offen beim ersten Lauf

- OLED: bleibt es leer, `model` auf `SSD1306 128x64` oder Adresse auf 0x3D (`docs/oled-1k3-i2c.md`).
- INA226: `shunt_resistance` mit dem Aufdruck auf dem Modul abgleichen (R100 = 0,1 Ω).
- Sechs RMT-Strips gleichzeitig (je 64 von 512 Symbolen): zeigt erst der erste Lauf.
- Strompuls: ob er nötig ist und wie lang, klärt ein Test mit der Powerbank und dem INA226.
- Dock-Zuordnung zu den Gebäuden (Namen in `substitutions`) ist noch nicht festgelegt.
