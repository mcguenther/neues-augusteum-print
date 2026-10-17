# Komponenten-Doku

Datenblatt-Notizen, Identifikation und Anschluss der verbauten Elektronik-Bauteile (Display, Schalter, ESP32 usw.). Je Bauteil eine Markdown-Datei,
Fotos in `bilder/`, Hersteller-Datenblätter in `datenblaetter/`. Was gemessen und was nur von Referenzmodulen übernommen ist, steht in der jeweiligen Datei.

| Datei | Bauteil | Stand |
|---|---|---|
| `oled-1k3-i2c.md` | 1,3″-I²C-OLED 128 × 64 (SH1106 wahrscheinlich) | identifiziert, Funktionstest am ESP32 offen |
| `wippenschalter-kcd11.md` | Wippenschalter 10 × 15 mm, 2 Pins (KCD11-Bauart), Hauptschalter für das Plus der Powerbank | identifiziert, Einbauloch mit Probeteil T2 bewährt, Hakenspanne nachmessen offen |
| `esp32-devkit-wroom32.md` | ESP32-DevKit WROOM-32, 30 Pin, USB-C | identifiziert, Maße und Einbauhöhe typisch, nachmessen |

Steckmechanismus und LED-Gebäude (Controller, 74AHCT125 usw.): `plug/PLAN.md`.
Pinbelegung des ESP32 (Docks, I²C für INA226 und Display, ESPHome-Skizze): `plug/power/pinout.html` (Artifact, Quelle `plug/power/build_pinout.py`).
Schaltplan, Einbauhöhe, Verbindungsliste und Lötanleitung der Elektronik: `plug/power/wiring.html` (Artifact, Quelle `plug/power/build_wiring.py`).
ESPHome-Firmware (Docks, INA226, Display, Strompuls) mit der Pinbelegung als Config: `esphome/doktorhut-max.yaml`, Beschreibung `esphome/README.md`.
