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
NOTCH_PAD = 2.0           # E  Eckaussparung im Unterkasten reicht so weit über die Fadentrichter hinaus; war 0,4, jetzt 2,0 (Nutzer 2026-10-17: V-Kanäle der Oberplatte dürfen etwa ±1,6 mm wandern)
FACH_FIX = ("N", 45.4)      # E  Fach (Powerbank) festgeschrieben: Nordkante, Mitte des Fachs bei x = 45,4 (Plattenkoordinaten). Die Suche nach dem Innenhof-Überdeckungswert ließ das Fach bei jeder Hof-Änderung wandern (Paulinum-Durchgang: 20 mm nach Osten); der Unterkasten soll von der Oberplatte unabhängig bleiben
UK_OUTLINE = (115.6, 220.8)   # E  Außenmaß des Unterkastens, festgeschrieben (Nutzer 2026-10-17): die Steckplatte bleibt in diesem Rechteck; build_batteriefach prüft es
PB_T_ZUSCHLAG = 0.2       # E  Dickenzuschlag der Powerbank aus der Fachprobe r5 ("ca. 0,2 mm mehr Höhe", Nutzer): Unterkasten innen für 12,8 statt 12,6, keine Messung

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
ESP_BOARD = (51.8, 28.2)  # A  ESP32-DevKit WROOM-32 (30 Pin), Platine; typisch (docs/esp32-devkit-wroom32.md), ungemessen
ESP_H = 5.9               # A  Aufbau A (Lötstellen 1,0 + Platine 1,6 + USB-C-Buchse 3,3), Einbauhöhe in plug/power/build_wiring.py
ESP_TAPE = 1.0            # E  Isoband um das Board, je Seite (keine feste Box: das Board liegt lose, Leitungen hängen frei)
ESP_RING = 5.0            # E  freier Rand um das Board ohne Stützen, damit die Leitungen biegen können
ADERN_ZONE = 2.9          # A  Leiste 2,0 + Lötstelle/Draht unter der Platte (plug/power/build_wiring.py ZONE)
ESP_ZONES = ((64.0, 40.5), (54.0, 30.5))   # E  Elektronikfläche final (Board + Isoband + Ring) und Rückfall ohne Ring; ersetzt 60 × 35 der Box im Batteriefach
HUT = 240.0               # S  Doktorhut, Kantenlänge des Deckbretts; ungemessen

# ---- Hauptschalter (Wippe KCD11 10 × 15, Kasten 13 × 8, Frontplatte 15 × 10), Probeteil T2 gedruckt und bewährt (r9, 2026-10-17)
SW_HOLE = (13.7, 9.0)     # B  Loch in der Wand, Langseite waagerecht: T1 13,6 × 8,6 war sehr stramm, T2 "sehr gut einzusetzen und hält trotzdem sehr fest"
SW_WALL = 1.2             # B  Wand am Loch (drei Linien), sonst UK_WALL 2,4; mit T1 und T2 getestet
SW_POCKET_PAD = (4.0, 3.0)   # B  Innentasche = Loch + 4,0 (Länge) + 3,0 (Höhe), 1,2 tief, oben 45°-Dach; in T1 und T2 gedruckt
SW_Y = 40.0               # E  Lage auf der Westwand (Platte 1:1300, Süden 0): Mitte zwischen den Stützen bei y 17 bis 23 und 57 bis 63, kleinster Abstand 9,3 mm (bei 36: 6,0); frei von Konflikten, noch nicht in der echten Platte gedruckt

# ---- Druck und Material
BED = 250.0               # Druckbett Bambu A1 (256, mit Rand)
SCALES = (1300,)        # 1300 aus Platzgründen gewählt (Nutzer), Platte passt dann mit Rand auf den Hut; keine Referenz mehr (Lagen der Docks nur für 1300)
STECKERRAUM = 3.5       # E  Luft zwischen flacher Plattenunterseite und Oberkante der Powerbank: Leistenkörper 2,0 + Draht (Test-Dock PROP GAP 3,5; 2,5 als Rückfall)
PIN_PLAN = dict(PIN, h=2.5)   # E  Zentrierzapfen 2,5 (Test-Dock: 1 mm länger als in Steckprobe 2), Zapfenloch 2,8 tief nur außerhalb der Mulden
PLA = 1.24                # g/cm³
SHELL, INFILL = 1.0, 0.15  # Materialschätzung: 1 mm Hülle (3 Wände, 4 Decken/Böden), 15 % Füllung

# ---- Stand 8 (Plan, noch keine STL; Nutzer 19.10.2026): Kasten höher, Knopf und Kordel des Doktorhuts unter der Plattenmitte (plug/power/kasten8.py)
STECKERRAUM_8 = 6.0       # E  Luft über der Powerbank bis zur Platte (Nutzer 19.10.: am Ende liegen viele Leitungen dort; Stand 7: 3,5); der Kasten wird so hoch wie nötig
HUT_KNOPF = dict(d=22.0, h=12.0, luft=1.0, r=12.5)   # A  Knopf in der Hutmitte Ø 22 × 12,0 hoch. ANNAHME, vom Nutzer zu bestätigen: erste Nachricht „ca. 1,2 cm Höhe“, später „viel höher als die Gänge“ (vorher als 1,2 mm gelesen). Knopfraum mindestens Ø 25 (Radius r = 12,5, 1,5 Luft je Seite) × 13,0 (Luft 1,0 oben, Nutzer 20.10.: 1 mm Luft über dem Knopf)
KORDEL_ANSATZ_OBEN = False  # M  Nutzer 19.10.: die Kordel kommt unten seitlich am Knopffuß heraus (Hut-Höhe 0 bis 3) und läuft nie über die Oberseite. False = am Fuß, sie verlässt den Knopf auf Hut-Höhe (0 bis 3); True = oben auf dem Knopf, dann braucht der Raum 12 + 3 + 0,2 = 15,2 Höhe und Radius 14,4 (Kordelecke bei 11 + 3 und 2,5 seitlich, plus 0,2)
KNOPF_RAMPE = dict(vor=10.5, decke_d=20.0)   # E  Anstieg von Gang-Höhe (4) auf Knopfhöhe als 45°-Kegel: beginnt vor = 10,5 mm vor dem Knopfkörper (Radius 11 + 10,5 = 21,5; so trifft der Kegel genau die Oberkante des Raums Ø 25 × 13,0), endet mit einer flachen Decke Ø 20 (Brücke höchstens 20). vor = 10 (Nutzer: „etwa 1 cm“) macht die Erhebung 1,3 mm höher
KNOPF_PLATEAU_D = 28.0      # E  Oberseite der Erhebung über dem Knopf Ø 28 (Auflage der Powerbank); senkrechter Rand, darunter folgt die Außenseite dem Kegel mit Wand 1,2
PB_AUFLAGE = dict(on=True, a=12.0, abstand=0.5)   # E  Auflagen der Powerbank auf Plateauhöhe in den Ecken ihrer Fläche (je bis a × a, abstand zu den Höckern), damit sie nicht über die Erhebung kippt (Schwerpunkt 31 mm neben der Knopfmitte)
KORDEL = dict(h=3.0, b=5.0)                 # M  Kordel des Huts etwa 3 hoch × 5 breit (Nutzer 19.10.)
KORDEL_GANG = dict(w=8.0, h=4.0, n=8, fase=1.5)   # S  Gang für die Kordel in 45°-Schritten von der Mitte zur Außenwand: 8 × 4, Fase 1,5 × 45° an den oberen Kanten (Decke 5 breit); Lage der Fase nach GANG_FASE_MODUS. Die Kordel 3 × 5 hat 2,0 in der Höhe und 3,0 seitlich Spiel
GANG_FASE_MODUS = "innen"   # E  Nutzer 20.10.: für die Gänge ist "innen" ok (Fase 1,5 × 45° in den oberen Ecken des Rechtecks 8 × 4, Decke bei 5; die Kordel 5 × 3 passt weiter). "aussen" (Rechteck 8 × 4 ganz frei, Dachschrägen darüber, Höcker 1,5 höher) bleibt im Code umschaltbar
KORDEL_DACH = 0.48        # E  Nutzer 20.10.: Decke über den Aushöhlungen (Knopfraum, Gänge) 3 Lagen × 0,16 = 0,48 (vorher 1,2)
KORDEL_WAND = 0.8         # E  Nutzer 20.10.: Wandstärke an Gängen und Knopfraum 0,8 (vorher 1,2); gilt in beiden Fasen-Modi (Höcker 8 + 2 · 0,8 = 9,6 breit). Außenwand UK_WALL und Boden UK_FLOOR des Kastens sind gedruckt und bleiben
CH_MUENDUNG = 0.0         # E  Nutzer 20.10.: keine Fase unten an den Mündungen von Gängen und Knopfraum (an der Wand unten bei der Kordel), die Bettkante CH_BED gilt nur noch für die Außenkante des Kastens
BEFESTIGUNG = "Heißkleber"   # E  Nutzer 19.10.: Kasten auf den Hut kleben, im Zweifel die Steckplatte auf den Kasten; Fäden und Ösen (Eckaussparungen, Fadentaschen) entfallen
