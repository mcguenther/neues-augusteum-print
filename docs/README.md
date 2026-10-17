# Komponenten-Doku

Datenblatt-Notizen, Identifikation und Anschluss der verbauten Elektronik-Bauteile (Display, Schalter, ESP32 usw.). Je Bauteil eine Markdown-Datei,
Fotos in `bilder/`, Hersteller-Datenblätter in `datenblaetter/`. Was gemessen und was nur von Referenzmodulen übernommen ist, steht in der jeweiligen Datei.

| Datei | Bauteil | Stand |
|---|---|---|
| `oled-1k3-i2c.md` | 1,3″-I²C-OLED 128 × 64 (SH1106 wahrscheinlich) | identifiziert, Funktionstest am ESP32 offen |
| `wippenschalter-kcd11.md` | Wippenschalter 10 × 15 mm, 2 Pins (KCD11-Bauart), Hauptschalter für das Plus der Powerbank | identifiziert, Maße grob, Probeteil T1 gebaut, nachmessen und drucken offen |

Steckmechanismus und LED-Gebäude (Controller, 74AHCT125 usw.): `plug/PLAN.md`.
