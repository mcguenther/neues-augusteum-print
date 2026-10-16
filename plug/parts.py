"""Kaufteile, Passungen und Druckmaße des Dupont-Steckmechanismus (Plan B, Institutsgebäude, Probestück).

Nur Zahlenkonstanten (und reine Arithmetik daraus), keine Geometrie und keine Importe. Der Generator
`plug/dupont.py` holt alles per `from plug.parts import *` und gibt die Namen unverändert weiter,
also gehen `sd.HDR_BODY`, `sd.SNUG` usw. wie bisher. Hier ändern, wenn nachgemessen wurde.
Alle Maße in mm. Festgelegt (nicht ändern ohne neue Messung): Winkelleistenkörper HDR_BODY = HDR_T = 2,0.
"""

# --------------------------------------------------------------------------
# Kaufteile. Quelle je Wert: B = belegt (Zeichnung), M = gemessen am eigenen Teil, A = abgeleitet, S = geschätzt.
# Mit der Schieblehre nachmessen und hier eintragen (Passprobe: plug/fit_test/).
# --------------------------------------------------------------------------
PITCH = 2.54          # B  Raster
NPIN = 4
HSG_W = 10.16         # B  Gehäuse 1×4: Breite n·2,54 (Pololu-Zeichnung, ±0,3)
HSG_T = 2.54          # B  Gehäuse: Dicke
HSG_H = 14.00         # B  Gehäuse: Höhe 14,00 ±0,25
HSG_TOL = 0.25        # B  Plus-Toleranz der Höhe (Tasche wird so viel höher)
HSG_HOLE = 1.0        # S  Eintrittsöffnung je Kammer in der Steckseite
HSG_LATCH = 8.3       # B  Rastzungen-Zone ab Kabelseite (Pololu: 8,30)
TERM_L = 11.7         # B  Female-Crimp-Pin Länge (Pololu-Zeichnung)
TERM_BOX = 1.6        # B  Kontaktkasten 1,6 × 1,6
TERM_BOX_L = 4.5      # B  Kontaktkasten Länge
TERM_OFF = 0.5        # S  Kontaktkasten beginnt so weit hinter der Steckseite
CONTACT = 1.5         # S  Stift muss so tief in der Buchse stecken, bis die Feder anliegt
PIN_SQ = 0.64         # B  Vierkant der Stifte
HDR_W = NPIN * PITCH + 0.5   # M  Leistenstück, 4 Pins abgebrochen: Körper gemessen etwa 0,5 mm länger (Abbruchrest), Passprobe v4
HDR_BODY = 2.0        # M  Winkelleiste: Körperhöhe (Taschentiefe-Richtung) gemessen 2,0 (frühere Annahme 2,54 war falsch; Passprobe v5: Körper fiel zu tief)
HDR_LEG = 7.0         # M  Winkelleiste: senkrechter Pin vom Ende bis zur Außenkante der Biegung, gemessen 7 ±0,5
HDR_T = 2.0           # M  Winkelleiste: Körperdicke in Pin-Richtung, gemessen 2 (Passprobe v4: mit 2,54 wackelte der Körper)
HDR_UP = HDR_LEG - PIN_SQ / 2 - HDR_BODY / 2   # A  Stiftspitze über der Körperoberkante, wenn die Biegung auf halber Körperhöhe liegt (= 5,68)
HDR_TAIL = 3.0        # B  gerade Leiste: Lötende unter dem Körper (3,0 ±0,2)
RA_BACK = 1.0         # M  Winkelleiste: gerader Pin zwischen Körper und senkrechtem Pin: gemessen 1 ±0,5. Der Körper sitzt NEBEN dem senkrechten Pin
RA_TAIL = 3.0         # M  Winkelleiste: Pin hinter dem Körper (Lötende), gemessen 3 ±0,5; zeigt von den senkrechten Pins weg
MPIN_UP = 6.0         # S  Male-Crimp-Pin: so weit ragt der Stift aus dem Gehäuse
WIRE_D = 1.0          # S  Ader des Flachbandkabels (28 AWG, Isolation ≈ 0,9)
LED_W, LED_L, LED_T = 10.0, 16.7, 2.2   # WS2812B-Streifenstück (60 LED/m): Breite, Länge, Dicke
LED_FPC = 0.3         # S  Streifen ohne Chip (Folie + Klebeband)
PADS = ("GND", "DIN", "5V")  # Lötpads von −x nach +x, Din-Ende zum Gehäuse, Chip oben (am Streifen prüfen!)
PAD_X = 3.5           # S  Abstand der äußeren Pads von der Streifenmitte

# Passungen (FDM, 0,4er Düse)
CLR = 0.25            # Spiel je Seite: Fuß in der Mulde (Führungsband)
RELIEF = 0.30         # zusätzliches Spiel unter dem Führungsband (gegen Klemmen)
BAND = 5.0            # Höhe des engen Führungsbands unter der Muldenfase
SNUG = 0.22           # Spiel je Seite: Gehäuse in der Tasche (Passprobe v4: Gehäuse 0,25 sitzt gut, darf etwas kleiner)
SNUG_HDR = 0.1        # M  Spiel je Seite: Winkelleistenkörper in der Tasche, x und y (Entscheidung nach Passprobe v5)
STEP_CLR = 0.1        # M  Luft zwischen Stufe (Decke des Lötendenschlitzes) und Pin-Oberseite im Dock A der Platte (Passprobe: 0)
RIB = 0.12            # Übermaß der Crush-Rippen
HOLE = 1.4            # M  Stiftloch (Muldenboden, Trichterhals); Vierkant-Diagonale 0,91. Entscheidung nach Passprobe v5 (v4: 1,2 ging ohne Kraft, Winkelpins etwas schief)
FUNNEL_D = 2.4        # Trichteröffnung unten
WALL = 1.2
CH_F = 0.8            # 45°-Fase unten am Fuß
CH_P = 1.0            # 45°-Fase oben an der Mulde
FOOT_R = 0.5          # Rundung der senkrechten Fußkanten (Muldenecken drucken nicht scharf)
GUIDE = 3.0           # Fuß steckt so lang gerade in der Mulde, bevor eine Stiftspitze den Fuß erreicht
CEIL = 0.8            # Muldenboden über dem Steckerteil (hält es gegen Zug)
FUNNEL_T = 1.0        # Trichterplatte unter dem Gehäuse (= Schieber bei der Kassette)

# Druck
LAYER = 0.2           # Schichthöhe, auch erste Schicht
WIRE_GAP = 0.2        # Luft über den Adern bis zur ersten Schicht nach der Pause
LED_GAP = 0.2         # Luft über dem LED-Chip bis zur Pausenebene
RIEGEL_T = 1.2        # Riegel über Gehäuse und Adern
LED_REC = 0.4         # LED liegt so tief in einer Mulde im Kammerboden
GROOVE = (1.2, 1.2)   # Querrinne für die DETECT-Brücke (Breite, Tiefe)
GAP_L = 1.6           # Abstand Sockel – LED (Platz für die Querrinne)

# Würfel / Platte
CUBE = 30.0
CUBE_H = 24.0         # sichtbare Höhe
SHELL = 1.2
ROOF = 1.2
KEY = 3.0             # Kodier-Ecke (−x, −y)
DOCK_PITCH = 36.0
VARIANTS = ("A", "B", "C")
LID_T = 2.0
SCREW_PILOT, SCREW_CLR = 2.5, 3.2      # M3-Blechschraube / Gewindeformer
TONGUE = dict(L=10.0, t=1.2, z0=-5.0, z1=-1.2, gap=0.6, bump=0.5)   # Federzunge in der Muldenwand
KASS_CLR = 0.2        # Kassette im Fußschacht
KEY_CLR = 0.15        # Schieber in der Schwalbenschwanz-Nut

# Gebäude (Laserscan 1:1500, B × T × H in mm, aus dem ersten Plan)
BUILDINGS = [("Paulinum", 39.6, 24.6, 39.2), ("Neues Augusteum", 42.1, 51.9, 25.0),
             ("Hörsaalgebäude", 55.1, 90.7, 16.4), ("Seminargebäude", 26.3, 66.7, 18.8),
             ("Institutsgebäude", 70.3, 29.9, 21.1), ("City-Hochhaus", 31.3, 30.4, 96.4)]
# Moritzbastei (44,6 × 43,0 × 6,1 mm) vorerst zurückgestellt, siehe archiv/moritzbastei/README.md

# --------------------------------------------------------------------------
# Kräfte (Abschätzung; Kontaktkräfte sind für Kit-Teile nicht belegt)
# --------------------------------------------------------------------------
E_PLA = 3500.0        # N/mm², Biegemodul PLA (PETG ≈ 2000)
MU = 0.3              # Reibwert PLA/PLA
PIN_PULL = (0.3, 1.0)   # S  Haltekraft je Stift in einer Dupont-Buchse, N
PIN_PUSH = (1.0, 2.0)   # S  Steckkraft je Stift, N

# --------------------------------------------------------------------------
# Stromversorgung (Konzept, plug/power/): Powerbank Intenso XS5000 (weiß 7313522) in der Grundplatte.
# Quellen: Intenso-Datenblatt XS5000/XS10000/XS20000 (2026) und Bedienungsanleitung v1.10; Abschaltung: TonUINO-Forum.
# --------------------------------------------------------------------------
PB_L, PB_W, PB_T = 90.0, 63.0, 12.6   # B  Außenmaße (Anleitung rundet auf 13); am eigenen Gerät nachmessen
PB_G = 103                # B  Gewicht in g
PB_WH = 5.0 * 3.7         # A  5000 mAh bei 3,7 V = 18,5 Wh
PB_EFF = 0.85             # S  Wirkungsgrad Zelle → 5 V
PB_IMAX = 2.1             # B  5 V / 2,1 A gesamt für USB-A und USB-C (kein PD)
PB_SLEEP_S = 30           # B  Standby nach etwa 30 s ohne Verbraucher, Taste weckt (Anleitung)
PB_KEEP_MA = 50           # S  Dauerlast, bei der sie an bleibt (Forum: 100 Ω an 5 V hält sie an, 10 bis 20 mA nicht)
PB_PORTS = ("LEDs", "Taste", "microUSB in", "USB-C in/out", "USB-A out")   # B  alle an einer Schmalseite (63 mm, aus dem Bild der Anleitung)
PB_CLR = 0.5              # E  Spiel je Seite im Fach
PB_CLR_Z = 0.6            # E  Luft über der Powerbank
PB_PLUG = 35.0            # S  Platz vor der Anschlussseite: gerader USB-A-Stecker (Griff etwa 25 mm) plus Biegung des Kabels
PB_CABLE = 6.0            # S  Kabelkanal entlang der Längsseite (USB-Kabel bis 4,5 mm)
PB_PORT_V = dict(usb_a=22.0, usb_c=8.0, micro=-5.0, taste=-16.0, leds=-24.0)   # S  Lage quer zur Schmalseite ab Mitte (Bild der Anleitung)
UK_FLOOR = 1.2            # E  Boden des Unterkastens
UK_WALL = 2.4             # E  Außenwand des Unterkastens
UK_CABLE_H = 4.0          # E  Mindesthöhe des Kabelraums im Unterkasten (Variante Hof-Fach)
HOF_LEDGE = 2.0           # E  Auflage des Innenhof-Teils rund um das Fach (Variante Hof-Fach)
OESE = dict(L=14.0, B=7.0, hole=3.0, pitch=7.0, pin=1.5, up=4.0)   # E  Öse je Ecke: Block im Unterkasten mit zwei Fadenlöchern, Zapfen in die Oberplatte, Tunnel darüber
HUT = 240.0               # S  Doktorhut, Kantenlänge des Deckbretts (nachmessen)
ESP_BOX = (60.0, 35.0)    # S  Elektronik im Unterkasten: ESP32-Board, 2 × 74AHCT125, 1000 µF, Schalter
