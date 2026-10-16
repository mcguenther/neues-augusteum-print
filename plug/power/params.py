"""Sollwerte für Powerbank, Oberplatte, Unterkasten und Fadenführung der großen Grundplatte (Konzept, Stand 3).

Nach Regel 8 im Logbuch (`plug/logbook/README.md`) stehen neue, noch nicht bewährte Werte hier und nicht in `plug/parts.py`.
Werte des Steckmechanismus kommen aus der Steckprobe (`plug/testcase/params.py`, Plan Steckprobe 2 `plug/testcase/build_plan2.PROP`),
damit Oberplatte und Steckprobe dieselbe Maßkette haben. Status je Wert wie im Logbuch:
B belegt (Datenblatt), M gemessen, A abgeleitet, S geschätzt, E Entscheidung; dazu bewährt / vorläufig / Vorschlag.
"""
from plug.testcase import build_plan2 as P2
from plug.testcase import params as TP

# ---- aus der Steckprobe übernommen (nicht hier ändern)
MULDE_CLR = TP.MULDE_CLR_T          # 0,10 je Seite, bewährt (r2 FM, r3 M)
CEIL = TP.CEIL_T                    # Muldenboden 0,4, vorläufig (r2 K, r3 S)
V = dict(leg_d=P2.PROP["LEG_D"], apex=P2.PROP["APEX"], slope=P2.PROP["SLOPE"], entry_r=P2.PROP["ENTRY_R"],
         y=P2.PROP["LASCHE_Y"], wall=1.4)   # V-Kanal für den Faden, Zwischenstand r4 (nicht abgenickt)
STAMP_AIR = P2.PROP["STAMP_AIR"]    # Anschlag unter dem Leistenkörper: 1,2 mm Luft (Vorschlag r4, Karte D)
EF_CH = P2.PROP["EF_CH"]            # Fase an Bettkanten 0,5 (Vorschlag r4)


def stack():
    """Maßkette der Steckprobe (z = 0 Plattenoberseite): F, E, z_hb, z_bb, z_tip …"""
    return TP.dims()


# ---- Powerbank Intenso XS5000 (weiß 7313522). Quellen: Intenso-Datenblatt (2026), Bedienungsanleitung v1.10, TonUINO-Forum
PB_L, PB_W, PB_T = 90.0, 63.0, 12.6   # B  Außenmaße (Anleitung rundet auf 13); ungemessen
PB_G = 103                # B  Gewicht in g
PB_WH = 5.0 * 3.7         # A  18,5 Wh
PB_IMAX = 2.1             # B  5 V / 2,1 A gesamt für USB-A und USB-C
PB_SLEEP_S = 30           # B  Standby nach etwa 30 s ohne Verbraucher
PB_KEEP_MA = 50           # S  bleibt an ab etwa 50 mA (Forum)
PB_PORTS = ("LEDs", "Taste", "microUSB in", "USB-C in/out", "USB-A out")   # B  an einer Schmalseite (Bild der Anleitung)
PB_PORT_V = dict(usb_a=22.0, usb_c=8.0, micro=-5.0, taste=-16.0, leds=-24.0)   # S  Lage quer zur Schmalseite ab Mitte; ungemessen

# ---- Fach im Unterkasten
PB_CLR = 0.5              # S  Spiel je Seite (Kaufteil ungemessen; Fachprobe klärt es)
PB_CLR_Z = 0.6            # S  Luft über der Powerbank bis zur Oberplatte
PB_PLUG = 35.0            # S  Platz vor der Anschlussseite: gerader USB-A-Stecker (Griff etwa 25 mm) plus Biegung; ungemessen
PB_CABLE = 6.0            # S  Kabelkanal entlang der Längsseite (USB-Kabel bis 4,5 mm)
FENCE = (1.6, 5.0)        # E  Zaun um die Powerbank: Breite, Höhe über dem Boden
ROD = 4.0                 # E  Stößel zur Taste, Querschnitt (Führung mit 0,15 Gleitspiel, L10)
WINDOW_PAD = 2.0          # E  Fenster in der Kante reicht so weit über LEDs und Buchsen hinaus

# ---- Unterkasten
UK_FLOOR = 1.2            # E  Boden
UK_WALL = 2.4             # E  Außenwand (3 Linien + Rand)
POST = (6.0, 40.0)        # E  Stützen unter der Oberplatte: Kante, Raster
PIN = dict(d=4.0, h=1.5, clr=0.15)   # E  Zentrierzapfen auf Stützen, Loch in der Oberplatte mit Gleitspiel 0,15 (L10)
NOTCH_PAD = 0.4           # E  Eckaussparung im Unterkasten reicht so weit über die Fadentrichter hinaus

# ---- Elektronik, Doktorhut
ESP_BOX = (60.0, 35.0)    # S  ESP32-Board, 2 × 74AHCT125, 1000 µF, Schalter
HUT = 240.0               # S  Doktorhut, Kantenlänge des Deckbretts; ungemessen

# ---- Druck und Material
BED = 250.0               # Druckbett Bambu A1 (256, mit Rand)
PLA = 1.24                # g/cm³
SHELL, INFILL = 1.0, 0.15  # Materialschätzung: 1 mm Hülle (3 Wände, 4 Decken/Böden), 15 % Füllung
