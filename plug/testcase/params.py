#!/usr/bin/env python3
"""Sollwerte für den kompletten Testfall (Kassette v4, Mini-Gebäude, Mini-Grundplatte) nach Nachtdruck 2.

Gemeinsame Quelle für die Planungsseite (plug/testcase/plan/) und die späteren STL. Die Werte in plug/parts.py bleiben unverändert,
solange Probestück und Institutsgebäude nicht umgebaut sind (sie rechnen noch mit Schieber und Trichterplatte). Erst nach dem
Testfall werden diese Werte dort übernommen.

Herkunft der Werte (Testbogen Nachtdruck 2, Antworten im Chat):
  K  Durchgang stabil bei Plättchen 0,4 und 0,6, bei 0,8 und 1,0 Aussetzer; am liebsten 0,4
  E  Einpressen: Spiel 0,06 je Seite geht gut hinein und sitzt fest
  C  Buchse passt, LED 10 und 12 mm passen; Adern knicken stark → LED-Fläche als Podest 2 mm höher
  D  Stufe für 1,8 (2,0 und 1,8 liegen flach), Körpertasche +1,5
  FM Mulde: Spiel 0,10; Federzunge zunächst weglassen
  Schieber und Trichterplatte entfallen (nehmen Pin-Länge weg)
"""
from plug import dupont as sd
from plug import institute as I
from plug import series2 as N2

# ---- Stapelhöhe über der Winkelleiste: nur noch der Muldenboden (Schieber und Trichterplatte entfallen)
CEIL_T = 0.4            # Muldenboden über der Winkelleiste (alt 0,8); Plättchen 0,4 hielt, 0,6 war die Grenze
FUNNEL_T_T = 0.0        # keine Trichterplatte, Buchse liegt bündig an der Fußunterkante (alt 1,0)

# ---- Passungen
KASS_CLR_T = 0.06       # Kassette eingepresst im Schacht, je Seite (Test E)
KASS_RELIEF = 0.20      # Variante B: Schacht hinter der Passzone entlastet
KASS_FIT_LEN = 8.0      # Länge der Passzone ab Schachteingang (Test E: 7 mm Berührung gingen gut)
MULDE_CLR_T = 0.10      # Fuß in der Mulde (Fuß-Lehre: 0,10 und 0,15 gut, 0,20 wackelt)
STEP_H_T = 1.8          # Stufe für das Lötende wie für Körperhöhe 1,8 (2,0 und 1,8 liegen flach)
BODY_EXT_T = 1.5        # Körpertasche zum Lötende hin länger

# ---- Festlegung Maßstab 1:1300 (plug/logbook/scale.md); ALLE folgenden Planwerte sind NOCH NICHT GETESTET (Liste: scale.md, „Ungetestete Planwerte“): Mulde überall 4 mm tiefer, damit die LED nicht direkt unter dem Dach sitzt.
# Die Steckprobe 1 (getestet, eingefroren) bleibt bei 0: dims() ohne Argument ist unverändert, dims(MULDE_EXTRA_T) ist der Planwert.
# Die Mulde ist eine einzige Ebene: der volle Gebäudeumriss, durchgehend bis zur Fußunterkante (F 14,2); keine Stufe, keine zweite Ebene in Form der
# Kassette. Die Kassette sitzt im Gebäudekörper und schließt unten bündig mit ihm ab; die Umrisse der Gebäude sind auf der Platte erkennbar.
MULDE_EXTRA_T = 4.0
SCALE_PLAN = 1300       # Maßstab 1:N; Platte dann 115,6 × 220,8 mm (höchstens 230 × 230 mm)
# Kassette je Gebäude (Konzepte V1RS und V2R: plug/logbook/cassettes.md); v4 ist der Standard (LED strahlt nach oben)
CASSETTE = {"01_paulinum": "v4", "02_neues_augusteum": "v4", "03_hoersaalgebaeude": "v4",
            "04_seminargebaeude": "V1RS", "05_institutsgebaeude": "V1RS", "06_city_hochhaus": "V2R"}
HOF_CH_T = 0.4          # Einführfase an der Unterkante des Hof-Einsatzes, wie bei den Gebäudefüßen
HOF_DEPTH_T = 3.0       # Hof-Einsatz: so tief unter der Oberfläche (nicht die 4 mm der Gebäude; vorher 1 mm war zu flach, Annahme, offen)
HOF_CLR_T = 0.1         # Fuge Einsatz zu Aussparung je Seite; die Wand zwischen Hof- und Gebäude-Aussparung bleibt 0,4 mm (Fuge Hof zu Gebäude 0,5 minus 0,1)
MULDE_CH_T = 0.5        # Einführfase oben an der Fußmulde (45°), keine Stufen, kein Band, keine Entlastung
OUTLINE_CLR_T = 0.1     # Umriss-Aussparung der Gebäude: Spiel je Seite

# ---- Fasen
ENTRY_CH_T = 0.4        # Einführfase an jeder Öffnung (Schachteingang liegt im Gebäude am Druckbett und gleicht den Elefantenfuß aus)
EF_CH_T = 0.4           # Fase an Bettkanten von Steckteilen (0,3 ließ einen leichten Wulst)

# ---- Taschenhöhe über der Buchse: sie bestimmt, wie weit die Buchse hinter der Kassettenunterkante sitzen kann (Einstecktiefe E sinkt um diesen Wert)
HSG_TOL_SAFE = 0.45     # Kassette 1: wie Nacht 2 (Buchse ging ganz hinein)
HSG_TOL_TIGHT = 0.15    # Kassette 2: engere Tasche, begrenzt den Verlust an E auf 0,15 (Buchse muss dazu höchstens 14,15 mm hoch sein)

# ---- Kassette v4: Oberseite als Podest über der Buchse
PODEST_T = 2.0          # LED-Fläche so viel höher als in Kassette v2 (dort 0,5 über der Taschenoberkante)
FILLET_T = 2.5          # Rundung der Kante Tasche → Podest (= Podesthöhe über der Taschenoberkante, Adern laufen sofort im Bogen)

# ---- Mini-Gebäude (oben offen, Anschlag am Rand) und Mini-Grundplatte
STOP_T = 1.2            # Anschlagrand über der Kassette (im Gebäude der Kammerboden)
BOX_W, BOX_L = 24.0, 38.0          # Grundriss des Mini-Gebäudes (Hauptbalken-Ausschnitt)
NOTCH_W, NOTCH_L = 3.5, 9.0        # Ausschnitt an der Ecke (+x, −y): konkave Ecke wie bei echten Grundrissen
PLATE_MARGIN = 7.0                 # Platte ragt so weit über den Fuß hinaus (Mulde + Fase + Wand)
LID_T_T = 2.0


def e_of_t():
    return sd.HDR_UP - CEIL_T


def kass_dims(tol=None):
    """Kassette v4 (Konstruktionslage: Unterkante z = 0, Mitte x = 0, y = 0 an der Taschenseite).
    Die Gesamthöhe ist für beide Taschenhöhen gleich (Schultern sind bei der engen Tasche dicker), damit beide Kassetten am selben Anschlag stehen."""
    tol = HSG_TOL_SAFE if tol is None else tol
    k = dict(N2.kass2_dims())
    k["top"] = sd.HSG_H + HSG_TOL_SAFE + N2.SEAT_RISE + PODEST_T
    k["zp"] = sd.HSG_H + tol
    k["zs"] = k["top"]
    return k


def dims(extra=0.0):
    """Maßkette im gesteckten Zustand: z = 0 Plattenoberseite (= Mulden-Oberkante), Fußunterkante bei −F, Pin-Reihe bei y = 0.
    extra: Zusatztiefe der Mulde (mm); 0 = getestete Steckprobe 1, MULDE_EXTRA_T = Planwert (dims_plan())."""
    g1 = sd.HDR_UP - CEIL_T
    F = sd.layer_up(g1 + sd.GUIDE + sd.CH_F + sd.CH_P + extra)
    z_hb = -F - CEIL_T                       # Oberkante Winkelleistenkörper
    z_bb = z_hb - sd.HDR_BODY                # Unterkante
    z_tip = z_hb + sd.HDR_UP
    z_bm = z_hb - sd.HDR_BODY / 2            # Höhe der waagerechten Pins
    z_bend = z_bb - 0.5
    z_lt = sd.layer_down(z_bend - 3.0)
    k = kass_dims()
    y_off = sd.HDR_T / 2 + sd.RA_BACK + sd.PIN_SQ / 2      # Pin-Reihe liegt so weit hinter der Körpermitte
    yb = -y_off                                              # Körpermitte
    y_tail = yb - sd.HDR_T / 2 - sd.RA_TAIL                  # Spitze der Lötenden
    y_kass0 = -k["ypin"]                                     # Kassette beginnt (Taschenseite) bei y_kass0
    y_kass1 = y_kass0 + k["L"]
    yc = (y_kass0 + y_kass1) / 2
    top = -F + k["top"]                                      # Oberkante Kassette
    return dict(F=F, E=sd.HDR_UP - CEIL_T, z_hb=z_hb, z_bb=z_bb, z_tip=z_tip, z_bm=z_bm, z_lt=z_lt, plate_t=-z_lt,
                y_off=y_off, yb=yb, y_tail=y_tail, y_kass0=y_kass0, y_kass1=y_kass1, yc=yc, kass_top=top,
                kass_h=k["top"], box_top=top + STOP_T, box_h=F + top + STOP_T,
                guide=F - g1 - sd.CH_F - sd.CH_P, step=sd.step_z(z_hb, STEP_H_T, sd.STEP_CLR))


def dims_plan():
    """Maßkette mit der festgelegten Zusatztiefe (F 14,2, Platte 20,2 mm)."""
    return dims(MULDE_EXTRA_T)


def footprint():
    """Grundriss des Mini-Gebäudes (Mitte der Kassette im Ursprung der Fußform, x zur Pin-Reihe, y wie im Testfall); L-Form."""
    w, l = BOX_W / 2, BOX_L / 2
    return [(-w, -l), (w - NOTCH_W, -l), (w - NOTCH_W, -l + NOTCH_L), (w, -l + NOTCH_L), (w, l), (-w, l)]


def plate_size():
    return BOX_W + 2 * PLATE_MARGIN, BOX_L + 2 * PLATE_MARGIN


if __name__ == "__main__":
    d = dims()
    k = kass_dims()
    for key, v in d.items():
        print("%-10s %8.2f" % (key, v))
    print("Kassette v4 %.2f × %.2f × %.2f, Tasche %.2f" % (k["cw"], k["L"], k["top"], k["zp"]))
    print("Platte %.1f × %.1f" % plate_size())
