# Wippenschalter 10 × 15 mm, 2 Pins (KCD11-Bauart)

Identifikation vom 17.10.2026 aus vier Fotos (`docs/bilder/`), Maße teils vom Nutzer grob gemessen, teils aus den Fotos abgeleitet, Händlerangaben
für die Bauform. Das gekaufte Exemplar ist nicht mit der Schieblehre vermessen; kein Hersteller, kein Datenblatt zum konkreten Artikel.

**Ergebnis:** Standard-Einbauschalter der Bauform **KCD11** (Wippe 10 × 15 mm, Einschnappmontage), **einpolig, zwei Pins (SPST, Ein/Aus)**,
Aufdruck „O“ (aus) und „I“ (ein). Er schaltet im Projekt das **Plus der Powerbank**: Powerbank → Schalter → INA226 VIN+.

## Eigenschaften

| Punkt | Wert | Sicherheit |
|---|---|---|
| Bauform | Wippenschalter KCD11, Einbau durch Schnapphaken | sehr sicher (Foto, Händlerbilder) |
| Kontakte | 2 Pins, flache Lötfahnen, Abstand etwa 4,8 mm; im Gehäuse ist ein dritter Schlitz ohne Pin | Foto, Abstand abgeleitet, nachmessen |
| Aufdruck | „O“ und „I“ auf der Wippe; auf der Seite CQC-Zeichen und CE | sicher |
| Nennwerte | meist 3 A bei 250 V AC (6 A bei 125 V AC) laut Händlern, am Teil nicht gelesen; bei 5 V und höchstens 2,1 A (Powerbank) reichlich | Referenz |
| Frontplatte (Rand) | 15 × 10 mm, etwa 1 mm Rand je Seite um den Kasten | vom Nutzer gemessen, grob |
| Kasten (verschwindet in der Wand) | 13 × 8 mm | vom Nutzer gemessen, grob; Händler nennen Ausschnitt 13,5 × 8,5 bis 9 |
| Tiefe ab Außenfläche der Wand | Kasten etwa 9 mm, Pins dazu etwa 7 mm, zusammen etwa 16 mm | aus Foto 1 abgeleitet, nachmessen |
| Haken | an den beiden Enden der 13-mm-Seite, im Schnitt nicht zu sehen | Foto, Hakenspanne ungemessen |
| Schaltrichtung | Wippe kippt in der Richtung der 15-mm-Seite | Foto |

## Einbau im Projekt

Der Schalter sitzt in der Westwand des Unterkastens (Seite gegenüber dem Paulinum, bei y = 36 mm südlich der Elektronikbox), die Frontplatte liegt
außen auf. Die Langseite liegt waagerecht, weil die Wand nur 17,4 mm hoch ist. Planseite mit Schieber und Warnungen: `plug/power/plan_switch.html`
(Artifact, Link in `plug/STATUS.md`), Generator `plug/power/build_plan_switch.py`.

| Größe | Wert | Status |
|---|---|---|
| Loch in der Wand | **13,7 × 9,0 mm** (T1 mit 13,6 × 8,6 passte, war aber sehr stramm: horizontal +0,1, vertikal +0,4; Händler 13,5 × 8,5 bis 9) | **bewährt** (T2: „sehr gut einzusetzen, hält trotzdem sehr fest“) |
| Wand am Loch | **1,2 mm** (drei Linien), sonst 2,4 mm; Innentasche 17,7 × 12,0 × 1,2 tief mit 45°-Dach | **bewährt** (T1 und T2), Werte in `plug/power/params.py` (`SW_*`) |
| Lage | Westwand, y = 36 (Platte 1:1300, Süden 0, Norden 220,8) | Wunsch des Nutzers; Schieber zeigt frei von Konflikten |
| Schalterraum | etwa 20 mm tief ab Außenfläche, 14 mm breit; 2,4 mm Luft bis zum Fach (Streifen 22,4 mm) | abgeleitet |

Verdrahtung: roter Draht der Powerbank-Zuleitung durch den Schalter, danach zu INA226 VIN+ und Shunt; Masse (schwarz) direkt an INA226 GND.
Schalter vor dem Shunt, damit der INA226 beim Ausschalten stromlos ist. Lötstellen mit Schrumpfschlauch isolieren.

## Probeteile T1 und T2

Wandstück 24 × 17,4 × 2,4 mm mit Loch und Tasche, dazu Bodenstreifen (≈ 1 g, 5 bis 10 Minuten), Generator `python3 -m plug.power.build_switch_probe`.

| Teil | Loch | Wand am Loch | Ergebnis |
|---|---|---|---|
| T1 (`stl/steckmodul_schalterprobe/T1_wand_schalter.stl`, Bild `vorschau/steckmodul_schalterprobe/T1.png`) | 13,6 × 8,6 | 1,2 | gedruckt am 17.10.2026: „passt schon so, aber sehr stramm“ (Nutzer); Halt der Haken und Brücke nicht gesondert gemeldet |
| T2 (`stl/steckmodul_schalterprobe/T2_wand_schalter.stl`, README_T2, pruefbericht_T2, schalterprobe_T2.zip, Bild `T2.png`) | 13,7 × 9,0 | 1,2 | gedruckt am 17.10.2026: „jetzt lässt er sich sehr gut einsetzen und hält trotzdem sehr fest, super“ (Nutzer); **bewährt** |

Eingefroren in `plug/logbook/rounds/r9_schalterprobe/` (ZIP, `summary.md`, `result.txt`). Die Brücke über dem Loch war sauber (ohne Stützen gedruckt); die Hakenspanne ist weiter ungemessen.

## Noch nachzumessen (Schieblehre)

1. Spanne über die beiden Haken an der 13-mm-Seite; muss größer als das Loch (13,7 mm) sein, sonst hält der Schalter nicht.
2. Abstand von der Unterseite der Frontplatte bis zur Hakenkante: maximale Wandstärke, in die er einrastet (Wand am Loch ist 1,2).
3. Kasten (B × L), Frontplatte (B × L) und deren Dicke, Wippe über der Frontplatte.
4. Tiefe des Kastens hinter der Frontplatte, Länge, Breite und Abstand der Pins (Lötfahne oder 4,8-mm-Flachstecker).

Ergebnisse hier eintragen und in `plug/power/build_plan_switch.py` (`SW`) nachziehen.

## Fotos

| Datei | Inhalt |
|---|---|
| `bilder/wippenschalter-kcd11-seite.jpg` | Seitenansicht: Frontplatte links, Haken oben und unten, zwei Pins rechts, CQC-/CE-Zeichen |
| `bilder/wippenschalter-kcd11-unterseite.jpg` | Blick auf die Hinterseite in der Hand: Metallkontakt, Kastenkante |
| `bilder/wippenschalter-kcd11-vorderseite.jpg` | Vorderseite mit „O“ und „I“, Frontplatte und Wippe |
| `bilder/wippenschalter-kcd11-rueckseite.jpg` | Rückseite: zwei Lötfahnen, dritter Schlitz, Haken am Rand |

## Quellen

1. Händlerangaben zur Bauform, Ausschnitt 13,5 × 8,5 bis 9 mm: [Makers Electronics KCD11-101](https://makerselectronics.com/product/kcd11-101-on-off-switch-250v-3a/)
2. Händlerangaben, 15,2 × 10 × 16,5 mm Körper, Ausschnitt 13,5 × 9 mm: [eBay KCD11 (10 Stück)](https://www.ebay.com/p/13026640396)
