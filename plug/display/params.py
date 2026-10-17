"""Sollwerte für das Display-Gebäude (OLED 0,96", GME12864-70, I²C) auf der großen Grundplatte (Konzept, Stand 1).

Nach Regel 8 im Logbuch (`plug/logbook/README.md`) stehen neue, noch nicht bewährte Werte hier und nicht in `plug/parts.py`.
Status je Wert: B belegt (Datenblatt), M gemessen, A abgeleitet, S geschätzt/typisch, E Entscheidung. **Alle Modulmaße sind S**, bis der Nutzer
das Modul mit der Schieblehre gemessen hat.
"""
from plug.power import params as PP
from plug.testcase import params as TP

# ---- OLED-Modul: GME12864-70 ist laut Hersteller ein nacktes 1,3"-Panel (CH1116G/SH1106, 128 × 64, FPC 30 pol.); das Teil des Nutzers sitzt auf einer
# Platine „1.30" IIC“ mit 4-Pin-Header (VDD GND SCK SDA). Maße aus den Fotos der Vorder- und Rückseite (Stand 2026-10-17): Maßstab aus dem Pinraster
# 2,54 mm (Header 10,2 mm = 318 px) und aus dem Lochraster 30,3 × 28,4 mm des Halters „Simple holder 1.3 inch 128x64“ (Printables 59743); beide Maßstäbe
# stimmen auf 1 % überein (31,3 und 31,2 px/mm). Genauigkeit etwa ± 0,5 mm. Dicke aus der Zeichnung des Schwestermoduls GME12864-79 (Datenblatt):
# Glas vor der Platine 1,3 bis 1,7, Platine 1,0, Bauteile hinten bis 1,2 (Header 2,5). Keine Schieblehre vorhanden: Passprobe (Schlitz in drei Breiten) klärt es.
DISP = dict(
    pcb_w=35.3,        # M  Platine, Breite (Foto ± 0,5; Schwestermodul -79: 35,5 ± 0,2)
    pcb_h=33.0,        # M  Platine, Höhe (Foto ± 0,5; Schwestermodul -79: 32,0, andere Platine)
    pcb_t=1.0,         # S  Platinendicke (Schwestermodul -79: 1,0)
    mod_t=4.5,         # S  Dicke Glas 1,7 + Platine 1,0 + Bauteile 1,2 = 3,9, ohne Header; mit 0,6 Reserve
    hdr_t=2.5,         # B  Kunststoff der Pinleiste hinten (Zeichnung -79: 2,5 max; die Pins ragen bis 11,3 von der Glasfront)
    hole_d=3.0,        # M  Befestigungsbohrung (Foto 2,9 bis 3,2; Lötring 3,8)
    hole_dx=30.3,      # M  Lochabstand quer (Foto 30,3)
    hole_dy=28.6,      # M  Lochabstand hoch (Foto 28,6; Halter 59743: 28,4)
    hole_edge=2.3,     # M  Mitte der Bohrung bis zum Plattenrand
    hdr_edge=1.8,      # M  Pin-Reihe bis zum Platinenrand (Foto 1,3 bis 2,4)
    hdr_pitch=2.54,    # B
    notch_w=14.4,      # M  Ausschnitt am Rand gegenüber den Pins (FPC), Breite
    notch_d=4.0,       # M  Ausschnitt, Tiefe
    panel_w=34.5,      # B  Panel-Außenmaß GME12864-70, Datenblatt S. 5
    panel_h=23.0,      # B
    aa_w=29.42,        # B  aktive Fläche 128 × 64 Pixel, Pixel 0,21 mm
    aa_h=14.70,        # B
    aa_top=9.4,        # M  Abstand der aktiven Fläche vom Platinenrand gegenüber den Pins (Glas 3,3 + Rand 6,4 mit dem Controllerstreifen)
    aa_bottom=8.9,     # M  Abstand der aktiven Fläche vom Platinenrand mit den Pins (Glas 7,0 darüber + Rand 1,9)
    vdd_max=3.5,       # B  VDD1 1,65 bis 3,5 V des Panels; ein SOT-23-Bauteil neben C9 ist vermutlich ein Regler (nicht belegt)
)
WINDOW_MARGIN = 0.4    # E  Sichtfenster im Rahmen größer als die aktive Fläche: Rand je Seite (A: Panelrand sichtbar halten)

# ---- Gehäuse
WALL = 1.2             # E  Wand um Modul und Kassette (wie KASS_WALL)
CLR = 0.3              # E  Spiel um die Platine
BACK = 1.6             # E  Rückwand/Deckel hinter dem Modul
CAVITY = 4.0           # S  Kabelkanal zwischen Modul und Kassette bei direkt angelöteten Adern (= CHAN; mit Dupont-Buchse auf der Pinleiste etwa 17: Entscheidungskarte)
CAVITY_DUPONT = 17.0    # S  Kabelraum hinter dem Modul mit aufgesteckter Dupont-Buchse (Pinleiste 2,5 + Gehäuse etwa 14) und Biegung der Adern
GAP_FRONT = 1.5        # E  Unterkante des Sichtfensters über der Plattenoberfläche (Nutzer: möglichst nah am Boden)
TILT_DEG = 15.0        # E  Neigung der Variante „Pult“

# ---- Nutzer 2026-10-17: Block über der Kassette einstufig, mindestens 4 mm Luft über der Kassette für die Adern
AIR_MIN = 4.0          # E  Luft über der Kassettenoberkante, Mindestmaß (Nutzer)
AIR = 4.5              # E  Plan: 0,5 Reserve
LID_T = 1.2            # E  Deckel der Kabelkammer, bündig im Blockdach
CHAN = 4.0             # S  Kabelkanal hinter der Rückwand des Moduls (vier Adern 28 AWG, Silikon, bündeln etwa 2,5 mm)
SLIT_W = 13.2          # E  Plan 2: Kabelfenster, so breit wie der Schacht (überholt durch WIN_W)
TOP_CAP = 1.2          # E  Kopfdach über dem Modul (Teil des Körpers; das Modul geht von vorn hinein, die Frontblende schließt)
BLENDE_T = 1.2         # E  Frontblende (eigenes Teil, liegend gedruckt, Fenster als Loch)
WIRE_LEN = 55.0        # A  Länge der Adern: Weg etwa 22 mm plus 30 mm zum Anlöten außerhalb des Körpers

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


# ---- Plan 3 (Nutzer 2026-10-17): Kopf ganz über der Platte, Hals = Halter der Kassette, Header bleibt am Modul (Adern an die Pinenden)
WIN_BOTTOM = 10.0      # E  Unterkante des Sichtfensters über der Platte (Nutzer: 5 bis 10 mm; 10 mm = Modul sitzt ganz über der Platte)
FLOOR_T = 1.2          # E  Boden der Modultasche (drei Wände)
PIN_TIP = 11.3         # B  Stiftspitze von der Glasfront (Zeichnung GME12864-79; ± 0,5, Pinlänge dieses Moduls ungemessen)
GLASS_T = 1.7          # S  Glas vor der Platine (Zeichnung -79: 1,3 bis 1,7)
PIN_CLEAR = 3.5        # E  Raum zwischen den Stiftspitzen (Lötstelle) und der Säule der Kassette
ROUND_R = 2.0          # E  Innenkanten der Kabelkammer in der Biegeebene, Radius
SPILL = 0.15           # E  Spiel um den Rückdeckel
LID_W = 14.4           # E  Breite des Rückdeckels (Kammer 13,2 plus 0,6 Auflage je Seite)

# ---- Plan 3, zweite Fassung (Nutzer 2026-10-17): Kabelfenster hoch, Verdrehsicherung, Fase wie main, Zapfen und Klick
WIN_W = 20.0           # E  Kabelfenster in der Rückwand: Breite (Langloch mit Rundbogen oben, ohne Brücke)
WIN_TOP_GAP = 4.5      # E  Oberkante des Kabelfensters unter der Oberkante des Körpers
FOOT_EXT = 6.0         # E  Fuß und Mulde nach vorn (Osten, zur Bildschirmfront) verlängert, Platz für die Kodierecke und die große Fase
KEY = 3.0              # B  Kodierecke (parts.py KEY, Steckprobe 1 bewährt), Ecke vorn Süd
FOOT_CH_FRONT = 2.0    # B  Fase vorn und an der Kodierecke: FUSS_FASE_T 2,0 (plug/buildings.py, r8 bewährt: fängt, kein Wulst)
FOOT_CH_SIDE = 0.6     # E  Fase an den Längsseiten und hinten: Wand um den Schacht ist 1,2, bei 2,0 würde die Fase in den Schacht schneiden
CLR_MULDE = 0.15       # E  Spiel Fuß zur Mulde je Seite (Vorgabe des Nutzers für den nächsten Probedruck, r8; 0,10 war an der kleinen Lehre bewährt)
PEG_D = 2.4            # E  Zapfen der Frontblende durch die Befestigungslöcher des Moduls (Loch etwa Ø 3,0)
PEG_HOLE_D = 2.6       # E  Sackloch in der Rückwand
PEG_HOLE_T = 1.2       # E  Tiefe des Sacklochs in der Rückwand (Wand 1,6)
CHAMBER_FRONT_W = WIN_W   # E  Breite der Kammer am Kabelfenster, nach hinten bis auf die Breite des Schachts schmaler
BUMP = dict(h=0.4, len=3.0, t=0.8, groove=0.5, u=(6.0, 22.0))   # E  Rastnasen an den Längskanten des Rückdeckels (je Seite zwei) und Nuten im Körper; u = Abstand vom oberen Ende entlang der Schräge
