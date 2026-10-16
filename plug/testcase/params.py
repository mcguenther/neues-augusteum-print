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

# ---- Fasen
ENTRY_CH_T = 0.5        # Einführfase an jeder Öffnung (Schachteingang liegt im Gebäude am Druckbett und gleicht den Elefantenfuß aus); Steckprobe 2: 0,5 (vorher 0,4, ließ einen Wulst)
EF_CH_T = 0.5           # Fase an Bettkanten von Steckteilen; Steckprobe 2: 0,5 (0,3 und 0,4 ließen einen leichten Wulst)

# ---- Taschenhöhe über der Buchse: sie bestimmt, wie weit die Buchse hinter der Kassettenunterkante sitzen kann (Einstecktiefe E sinkt um diesen Wert)
HSG_TOL_SAFE = 0.60     # Steckprobe 2: Tasche 14,60 (Buchse etwa 14,55; bei 14,45 stand sie 0,1 heraus). Steckprobe 1: 0,45
HSG_TOL_TIGHT = 0.15    # nur Steckprobe 1 (Kassette 2, passte keine Buchse); in Steckprobe 2 entfällt die Variante

# ---- Kassette v4: Oberseite als Podest über der Buchse
PODEST_T = 2.0          # LED-Fläche so viel höher als in Kassette v2 (dort 0,5 über der Taschenoberkante)
FILLET_T = 2.5          # Rundung der Kante Tasche → Podest (= Podesthöhe über der Taschenoberkante, Adern laufen sofort im Bogen)

# ---- Mini-Gebäude (oben offen, Anschlag am Rand) und Mini-Grundplatte
STOP_T = 1.2            # Anschlagrand über der Kassette (im Gebäude der Kammerboden)
BOX_W, BOX_L = 24.0, 38.0          # Grundriss des Mini-Gebäudes (Hauptbalken-Ausschnitt)
NOTCH_W, NOTCH_L = 3.5, 9.0        # Ausschnitt an der Ecke (+x, −y): konkave Ecke wie bei echten Grundrissen
PLATE_MARGIN = 7.0                 # Platte ragt so weit über den Fuß hinaus (Mulde + Fase + Wand)
LID_T_T = 2.0


# ---- Steckprobe 2 (Plan plug/testcase/plan2.html, Empfehlungen A abgenickt am 2026-10-16; Zwei-Lagen-Aufbau und Faden-V 40° neu aus plug/power/)
SHAFT_EXTRA_T = 0.30    # Schacht so viel tiefer als die Kassette hoch ist (Kassette ragte 0,2 heraus, L12)
SLOT_END_T = -8.0       # Lötende-Schlitz 1 mm länger (Ende bei −8,0 statt −7,0), L20
STAMP_AIR_T = 1.2       # Luft zwischen Anschlag-Steg und Körper der Winkelleiste (Karte D)
S2_MARGIN = 8.0         # Rand der Mini-Oberplatte um den Fuß: Wand zwischen Mulde und Faden-V mindestens 1,4 (bei 7,0 nur 1,2)
V_LEG_D, V_APEX, V_ENTRY_R, V_WALL = 2.2, 3.4, 2.0, 1.4      # Faden-V (Plan Steckprobe 2, Karte F)
V_SLOPE_A, V_SLOPE_B = 0.75, 1.2   # Böschung: A = 53° zur Waagerechten (Plan, 0,15 mm Überhang je Schicht), B = 40° (flacher, 0,24 mm je Schicht)


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


def dims():
    """Maßkette im gesteckten Zustand: z = 0 Plattenoberseite (= Mulden-Oberkante), Fußunterkante bei −F, Pin-Reihe bei y = 0."""
    g1 = sd.HDR_UP - CEIL_T
    F = sd.layer_up(g1 + sd.GUIDE + sd.CH_F + sd.CH_P)
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
