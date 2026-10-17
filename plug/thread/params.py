#!/usr/bin/env python3
"""Vorschlagswerte für die Fadenführung an den Plattenecken (Paket plug/thread/, Plan `plan.html`).

Nach Regel 8 im Logbuch (`plug/logbook/README.md`) stehen neue, noch nicht bewährte Werte in einem eigenen Paket und nicht in `plug/parts.py`.
**Alle Werte sind Vorschläge, noch nicht abgenickt, ungetestet.** Status wie im Logbuch: B belegt, M gemessen, A abgeleitet, S geschätzt, E Entscheidung.
Die bisherigen Werte (Steckprobe 2, r4) stehen unverändert in `plug/testcase/params.py` und `plug/power/params.py`; sie werden hier nur zum Vergleich wiederholt
(`OLD`), damit das Paket von den anderen Paketen unabhängig bleibt.

Koordinaten wie in den Zeichnungen des Plans: z = Höhe über der Plattenunterseite (Oberplatte reicht bis `PLATE_T`), darunter der Unterkasten.
"""
import math

# ---- Maße des Aufbaus (aus Steckprobe 2, nur gelesen)
PLATE_T = 12.6          # B/E Oberplatte (plug/power/build_concept.H0)
UK_H = 14.4             # E  hohler Unterkasten darunter
UK_WALL = 2.4           # E  Außenwand des Unterkastens
WALL_MIN = 1.4          # E  Wand zwischen Kanal und Plattenrand bzw. Mulde, mindestens

# ---- Annahmen zu Faden und Nadel (ungemessen, S; im Plan als Rückfrage)
THREAD_D = 0.8          # S  Faden doppelt genommen (Nähgarn, Zwirn)
NEEDLES = (("Nähnadel", 0.8), ("Sticknadel", 1.2), ("Stopfnadel", 1.6))   # S  Durchmesser am dicksten Teil (Öhr)
NEEDLE_D = 1.6          # S  Worst-Case: Stopfnadel
NEEDLE_L = 45.0         # S  Länge einer Stopfnadel
KNOT_D = 3.0            # S  Knoten im Faden (soll nicht durch die Löcher passen müssen)

# ---- Druckverlust am Kanal (Worst-Case)
PRINT_LOSS = 0.4        # E  Kanal-Ø im Druck bis zu 0,4 kleiner: Wulst, Stufen, Stützreste (L02, L03: 0,2 je Seite)

# ---- bisheriger Stand (Steckprobe 2, gescheitert)
OLD = dict(leg_d=2.2, apex=3.4, slope=0.75, entry_r=2.0, wall=1.4)

# ---- A: V-Kanal weiter, mit Support (geschlossener Tunnel)
A = dict(leg_d=4.0, apex=5.5, slope=0.75, entry_r=3.0, wall=1.4)
# ---- A2: Stand 2 nach Rückmeldung des Nutzers: Variante A als „halbe Pille mit Steg“ (offene Tasche statt Tunnel; der Faden war zugeschmoddert)
CHOSEN_AIR = 4.0         # E  Luft über dem Steg: Kompromiss aus den Eckmustern P3 (3,0) und P45 (4,5), beide gingen (Nutzer, 2026-10-16); noch nicht gedruckt
TESTED_AIRS = (3.0, 4.5)  # gedruckte Eckmuster P3 und P45 (plug/thread/build.py, SAMPLES)
PILL = dict(steg_w=5.0, steg_top=4.5, width=10.0, fillet=3.0, air=CHOSEN_AIR, chamfer=2.0, steg_chamfer=1.0)   # Steg: Breite, Höhe; Tasche: Breite quer zum Steg, Rundung Decke/Wand; Luft über dem Steg; Fase 45° am Taschenrand (Ein- und Ausgänge) und am Steg-Fuß
NOTCH_PAD = 2.0          # Eckaussparung im Unterkasten reicht so weit über die gefaste Mündung hinaus


def pill(air=None):
    """Maße der Tasche (Standard: gewählte Luft 4,0): Decke so hoch wie Steg + Luft, Endrundung R = Deckenhöhe (Viertelkreis bis zum Boden), Länge = 2 R + Stegbreite."""
    d = dict(PILL)
    if air is not None:
        d["air"] = air
    d["ceil"] = d["steg_top"] + d["air"]
    d["r"] = d["ceil"]
    d["length"] = 2 * d["r"] + d["steg_w"]
    d["roof"] = PLATE_T - d["ceil"]                  # Material über der Decke
    d["gap0"] = (d["length"] - d["steg_w"]) / 2      # Luft links und rechts vom Steg am Boden der Tasche
    c, cs = d["chamfer"], d["steg_chamfer"]
    d["mouth_l"], d["mouth_w"] = d["length"] + 2 * c, d["width"] + 2 * c          # Mündung an der Plattenunterseite samt Fase
    d["gap_mouth"] = d["gap0"] + c + cs                                            # Weite jedes Eingangs am Bett (Rand bis Steg-Fuß)
    d["notch_l"], d["notch_w"] = d["mouth_l"] + 2 * NOTCH_PAD, d["mouth_w"] + 2 * NOTCH_PAD   # Eckaussparung im Unterkasten
    d["gap_top"] = d["gap0"] - d["r"] + math.sqrt(max(0.0, d["r"] ** 2 - d["steg_top"] ** 2))   # Luft seitlich in Höhe der Stegkante
    return d


# ---- B: halboffene Rinne an der Seitenwand (Λ-Nut, nach außen offen)
B = dict(groove_w=4.0, depth=2.4, apex=5.5, slope=0.75)
# ---- C: zwei gerade Schrägbohrungen, die Scheitelstrecke liegt in einer Rille außen an der Seitenwand
C = dict(hole_d=3.6, run=4.4, rise=7.0, spacing=9.0, entry_r=3.0, groove_w=4.0, groove_depth=1.0, edge_r=1.0)
# ---- D: senkrechter Eckschacht im Unterkasten, Steg im Fenster der Plattenunterseite
D = dict(shaft_d=7.0, window=(12.0, 8.0, 8.0), bar_d=3.0)


def slope_deg(slope):
    """Winkel der Schenkel zur Waagerechten; slope = Lauf je mm Höhe (0,75 → 53°)."""
    return math.degrees(math.atan2(1.0, slope))


def angle_c():
    """Neigung der Schrägbohrungen in C zur Waagerechten."""
    return math.degrees(math.atan2(C["rise"], C["run"]))


def exit_span(c=None):
    """Austritt der Schrägbohrung C an der Seitenwand: Höhe der Ellipse, untere und obere Kante über der Plattenunterseite, Rest der Wand darüber."""
    c = c or C
    a = math.atan2(c["rise"], c["run"])
    h = c["hole_d"] / math.cos(a)
    lo, hi = c["rise"] - h / 2, c["rise"] + h / 2
    return dict(height=h, lo=lo, hi=hi, lip=PLATE_T - hi)


def notch_shift(angle_deg, height=UK_H):
    """Wie weit die verlängerte Bohrungsachse auf der Höhe des Unterkastens seitlich wandert: so weit muss die Eckaussparung reichen, damit die Nadel entlang der Achse zugänglich ist."""
    return height / math.tan(math.radians(angle_deg))


def hole_eff(d):
    """Wirksamer Durchmesser im Druck (Worst-Case)."""
    return d - PRINT_LOSS


def tilt_tolerance(hole_d, needle_d, length):
    """Winkel, um den eine gerade Nadel in einer geraden Bohrung der Länge `length` schräg stehen darf (Grad)."""
    return math.degrees(math.asin(max(0.0, min(1.0, (hole_eff(hole_d) - needle_d) / length))))


if __name__ == "__main__":
    for k, v in (("OLD", OLD), ("A", A), ("B", B), ("C", C), ("D", D)):
        print(k, v)
    print("C: Winkel %.1f°, Eckaussparung muss %.1f mm nach innen reichen" % (angle_c(), notch_shift(angle_c())))
    ln = math.hypot(C["run"], C["rise"])
    for name, d in NEEDLES:
        print("C Nadel %s %.1f: Kippspielraum %.1f° bei Bohrungslänge %.1f" % (name, d, tilt_tolerance(C["hole_d"], d, ln), ln))
