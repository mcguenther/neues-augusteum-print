"""Sollwerte für das Display-Gebäude (OLED 0,96", GME12864-70, I²C) auf der großen Grundplatte (Konzept, Stand 1).

Nach Regel 8 im Logbuch (`plug/logbook/README.md`) stehen neue, noch nicht bewährte Werte hier und nicht in `plug/parts.py`.
Status je Wert: B belegt (Datenblatt), M gemessen, A abgeleitet, S geschätzt/typisch, E Entscheidung. **Alle Modulmaße sind S**, bis der Nutzer
das Modul mit der Schieblehre gemessen hat.
"""
from plug.power import params as PP
from plug.testcase import params as TP

# ---- OLED-Modul: GME12864-70 ist laut Hersteller ein nacktes 1,3"-Panel (CH1116G/SH1106, 128 × 64, FPC 30 pol.); das Teil des Nutzers sitzt auf einer
# Platine mit 4-Pin-Header (VDD GND SCK SDA). Platinenmaße aus dem Foto geschätzt (Platine etwa 35 mm breit) und aus dem Datenblatt des
# Schwestermoduls GME12864-79 (35,5 × 32 × 1,0). Alles mit (S) vor dem Bau mit der Schieblehre messen.
DISP = dict(
    pcb_w=35.5,        # S  Platine, Breite (Foto etwa 35; Schwestermodul -79: 35,5)
    pcb_h=32.0,        # S  Platine, Höhe (Schwestermodul -79: 32,0)
    pcb_t=1.0,         # S  Platinendicke (Schwestermodul -79: 1,0)
    mod_t=4.5,         # S  Dicke Panel 1,45 + Klebeband + Platine + Bauteile, ohne Pinleiste
    hole_d=3.0,        # S  Befestigungsbohrung (auf dem Foto zwei Löcher oben links und rechts sichtbar)
    hole_dx=31.0,      # S  Lochabstand quer, aus dem Foto geschätzt (Schwestermodul -79: Langlöcher 25,4 × 27,7)
    panel_w=34.5,      # B  Panel-Außenmaß GME12864-70, Datenblatt S. 5
    panel_h=23.0,      # B
    aa_w=29.42,        # B  aktive Fläche 128 × 64 Pixel, Pixel 0,21 mm
    aa_h=14.70,        # B
    aa_top=5.0,        # S  Abstand der aktiven Fläche vom oberen Platinenrand
    vdd_max=3.5,       # B  VDD1 1,65 bis 3,5 V (Datenblatt); die Herstellerseite nennt „3 bis 5 V“, widerspricht dem Datenblatt
)
WINDOW_MARGIN = 0.4    # E  Sichtfenster im Rahmen größer als die aktive Fläche: Rand je Seite (A: Panelrand sichtbar halten)

# ---- Gehäuse
WALL = 1.2             # E  Wand um Modul und Kassette (wie KASS_WALL)
CLR = 0.3              # E  Spiel um die Platine
BACK = 1.6             # E  Rückwand/Deckel hinter dem Modul
CAVITY = 4.0           # S  Kabelraum zwischen Modul und Kassette bei direkt angelöteten Adern (mit Dupont-Buchse auf der Pinleiste etwa 17: Entscheidungskarte)
CAVITY_DUPONT = 17.0    # S  Kabelraum hinter dem Modul mit aufgesteckter Dupont-Buchse (Pinleiste 2,5 + Gehäuse etwa 14) und Biegung der Adern
GAP_FRONT = 1.5        # E  Unterkante des Sichtfensters über der Plattenoberfläche (Nutzer: möglichst nah am Boden)
TILT_DEG = 15.0        # E  Neigung der Variante „Pult“

# ---- Kassette ohne LED-Streifen: Unterbau der V2 (nur Buchsentasche und Aderschlitz), Schacht mit Spiel aus plug.campus.shaft_size
KASS_W, KASS_D = 13.08 + 2 * TP.KASS_CLR_T, 5.46 + 2 * TP.KASS_CLR_T      # Schacht 13,2 × 5,58 (A, V2 ohne Blatt)
KASS_TOP = 2.9         # A  Oberkante der Kassette über der Plattenoberfläche (Maßkette Campus: F 14,2 + 2,9 = 17,1)

# ---- Abstände auf der Platte
EDGE = 3.5             # E  Mulde bis Plattenkante (Fase 1,5 + Wand 2,0)
WALL_MULDE = 2.0       # E  Wand zwischen Display-Mulde und fremden Mulden
LABEL_Y = 15.0         # A  Schrift und Nordpfeil (erhaben) reichen bis y ≈ 13 von der Südkante; darüber ist frei
V_PAD = 3.0            # E  Abstand zu den Fadenkerben in den Ecken

# ---- Sicht
VIEW_ANGLES = (15, 25, 35, 45)   # Blickwinkel über der Waagerechten, aus Osten
