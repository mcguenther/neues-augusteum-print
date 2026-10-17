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
V_PLAN2 = dict(leg_d=P2.PROP["LEG_D"], apex=P2.PROP["APEX"], slope=P2.PROP["SLOPE"], entry_r=P2.PROP["ENTRY_R"],
               y=P2.PROP["LASCHE_Y"], wall=1.4)   # V-Kanal wie im Plan Steckprobe 2 (Zwischenstand r4, nicht abgenickt): 53° zur Waagerechten
# Stand 4: flacher (Nutzer: der Faden läuft zu steil). Böschung 1,2 mm je mm Höhe = 40° zur Waagerechten, 0,24 mm Überhang je Schicht
# (Plan Steckprobe 2: 0,15). Vorschlag, ungetestet; T1 druckt beide Winkel nebeneinander.
V = dict(V_PLAN2, slope=1.2)
V["y"] = round(V["apex"] * V["slope"] + V["entry_r"] + V["wall"], 2)   # Mitte des V von der Kante: Trichter mit Wand 1,4 zur Kante
STAMP_AIR = P2.PROP["STAMP_AIR"]    # Anschlag unter dem Leistenkörper: 1,2 mm Luft (Vorschlag r4, Karte D)
EF_CH = P2.PROP["EF_CH"]            # Fase an Bettkanten 0,5 (Vorschlag r4)


def stack():
    """Maßkette der Steckprobe (z = 0 Plattenoberseite): F, E, z_hb, z_bb, z_tip … (F 10,2; für Steckprobe 2, Fachprobe und Test-Dock)."""
    return TP.dims()


def stack_plan():
    """Maßkette der Campus-Platte nach plug/logbook/scale.md: Mulde überall 4 mm tiefer (F 14,2, Platte 20,2; wie plug/campus.py)."""
    return TP.dims_plan()


# ---- Powerbank Intenso XS5000 (weiß 7313522). Quellen: Intenso-Datenblatt (2026), Bedienungsanleitung v1.10, TonUINO-Forum
PB_L, PB_W, PB_T = 90.0, 63.0, 12.6   # B  Außenmaße (Anleitung rundet auf 13); ungemessen. Fachprobe r5: "tatsächlich minimal dicker" (ohne Zahl), Luft darüber um 0,2 erhöht (PB_CLR_Z)
PB_G = 103                # B  Gewicht in g
PB_WH = 5.0 * 3.7         # A  18,5 Wh
PB_IMAX = 2.1             # B  5 V / 2,1 A gesamt für USB-A und USB-C
PB_SLEEP_S = 30           # B  Standby nach etwa 30 s ohne Verbraucher
PB_KEEP_MA = 50           # S  bleibt an ab etwa 50 mA (Forum)
PB_PORTS = ("LEDs", "microUSB in", "USB-C in/out", "USB-A out")   # B  an einer Schmalseite (Bild der Anleitung)
PB_PORT_V = dict(usb_a=22.0, usb_c=8.0, micro=-5.0, leds=-24.0)   # S  Lage quer zur Schmalseite ab Mitte; ungemessen

# ---- Fach im Unterkasten
PB_CLR = 0.5              # S  Spiel je Seite (Kaufteil ungemessen; Fachprobe klärt es)
PB_CLR_Z = 0.8            # S  Luft über der Powerbank bis zur Oberplatte; war 0,6, Fachprobe r5: Powerbank minimal dicker, "ca. 0,2 mm mehr Höhe" (Nutzer), Deckplatte wackelte
PB_PLUG = 35.0            # S  Platz vor der Anschlussseite: gerader USB-A-Stecker (Griff etwa 25 mm) plus Biegung; ungemessen
PB_CABLE = 6.0            # S  Kabelkanal entlang der Längsseite (USB-Kabel bis 4,5 mm)
FENCE = (1.6, 5.0)        # E  Zaun um die Powerbank: Breite, Höhe über dem Boden
WINDOW_PAD = 2.0          # E  Fenster in der Kante reicht so weit über LEDs und Buchsen hinaus

# ---- Unterkasten
UK_FLOOR = 1.2            # E  Boden
UK_WALL = 2.4             # E  Außenwand (3 Linien + Rand)
POST = (6.0, 40.0)        # E  Stützen unter der Oberplatte: Kante, Raster
PIN = dict(d=4.0, h=1.5, clr=0.15)   # E  Zentrierzapfen auf Stützen, Loch in der Oberplatte mit Gleitspiel 0,15 (L10)
NOTCH_PAD = 0.4           # E  Eckaussparung im Unterkasten reicht so weit über die Fadentrichter hinaus

# ---- Dock in der Oberplatte: Kabelnische hinter den Lötenden (Nutzer: Lötenden brauchen viel Freiluft, das Kabel muss nach unten fallen)
SLOT_END = P2.PROP["SLOT_END"]   # Ende des Lötendenschlitzes -8,0 (Plan Steckprobe 2)
NICHE = dict(w=12.0, l=6.46)   # E  eine Nische hinter dem Schlitz, halb so groß wie vorher (Nutzer, r4): 12 × 9,5 mm ab der Körpertasche (l zählt ab SLOT_END), ohne Fenster und Stege, Support erlaubt
ANSCHLAG = dict(w=18.0, t=1.8, gusset=6.0)          # E  Steg unter dem Körper der Leiste im Unterkasten (Länge, Dicke, Strebe), 1,2 Luft
ZONE_PAD = 2.0                                      # E  Platz rund um Nische und Körper, in dem Unterkasten und Powerbank nichts haben
KASS_WALL = 1.2                                     # E  Wand des Gebäudes um den Schacht der Kassette

# ---- Fasen (Bettkanten gegen den Elefantenfuß, Einführfasen), Quelle Logbuch L02, L03
CH_BED = 0.5                                        # Bettkanten von Steckteilen und Mündungen am Bett (Plan Steckprobe 2: 0,5)
CH_HOF = 0.4                                        # Innenhof-Teil unten (nur 1 mm in der Vertiefung)
CH_PIN = 0.5                                        # Spitze der Zentrierzapfen

# ---- Elektronik, Doktorhut
ESP_BOX = (60.0, 35.0)    # S  ESP32-Board, 2 × 74AHCT125, 1000 µF, Schalter
ESP_BOXES = (ESP_BOX, (50.0, 30.0))   # Rückfall bei knappem Platz (1:1300): nur ESP32-DevKit 51 × 28 mm ohne Beiwerk (S)
HUT = 240.0               # S  Doktorhut, Kantenlänge des Deckbretts; ungemessen

# ---- Hauptschalter (Wippe KCD11 10 × 15, Kasten 13 × 8, Frontplatte 15 × 10), Probeteil T2 gedruckt und bewährt (r9, 2026-10-17)
SW_HOLE = (13.7, 9.0)     # B  Loch in der Wand, Langseite waagerecht: T1 13,6 × 8,6 war sehr stramm, T2 "sehr gut einzusetzen und hält trotzdem sehr fest"
SW_WALL = 1.2             # B  Wand am Loch (drei Linien), sonst UK_WALL 2,4; mit T1 und T2 getestet
SW_POCKET_PAD = (4.0, 3.0)   # B  Innentasche = Loch + 4,0 (Länge) + 3,0 (Höhe), 1,2 tief, oben 45°-Dach; in T1 und T2 gedruckt
SW_Y = 36.0               # E  Lage auf der Westwand (Platte 1:1300, Süden 0); frei von Konflikten, noch nicht in der echten Platte gedruckt

# ---- Druck und Material
BED = 250.0               # Druckbett Bambu A1 (256, mit Rand)
SCALES = (1300,)        # 1300 aus Platzgründen gewählt (Nutzer), Platte passt dann mit Rand auf den Hut; keine Referenz mehr (Lagen der Docks nur für 1300)
STECKERRAUM = 3.5       # E  Luft zwischen flacher Plattenunterseite und Oberkante der Powerbank: Leistenkörper 2,0 + Draht (Test-Dock PROP GAP 3,5; 2,5 als Rückfall)
PIN_PLAN = dict(PIN, h=2.5)   # E  Zentrierzapfen 2,5 (Test-Dock: 1 mm länger als in Steckprobe 2), Zapfenloch 2,8 tief nur außerhalb der Mulden
PLA = 1.24                # g/cm³
SHELL, INFILL = 1.0, 0.15  # Materialschätzung: 1 mm Hülle (3 Wände, 4 Decken/Böden), 15 % Füllung
