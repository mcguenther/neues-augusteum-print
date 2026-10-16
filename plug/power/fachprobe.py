"""Fachprobe Powerbank: Ausschnitt des Unterkastens mit Fach und Deckplatte (Plan: plug/power/plan_fach.html).

Nach Regel 2 im Logbuch gibt es erst nach dem Abnicken des Plans STL; dieses Modul liefert bis dahin nur Geometrie für die Zeichnungen
und die Massen im Plan. Maße kommen aus `plug/power/params.py` (Powerbank, Fach, Unterkasten) und `plug/power/build_concept.py` (Fach-Geometrie).
Koordinaten: u entlang der Powerbank (0 in der Fachmitte), v quer, z über dem Tisch (Boden 0, Oberkante Unterkasten 14,4).
"""
import math

from shapely.geometry import box as sbox
from shapely.ops import unary_union

from plug import series as SR
from plug.power import build_concept as BC
from plug.power import params as PP

G = BC.G
F = BC.Frame(0.0, 0.0, 0, 1)
FP = BC.fach_parts(F)
H = BC.H0
TOP = H["uk_t"]                      # 14,4: Oberkante Unterkasten über dem Tisch
ZF = PP.UK_FLOOR                     # Oberkante Boden
WALL = PP.UK_WALL
CH = PP.CH_BED
LB = 30.0                            # Variante B: so viel von der Powerbank steckt im Fach, der Rest ragt hinten heraus
PLATE_T = 2.0                        # Deckplatte (ersetzt hier die Oberplatte)


def region(variant):
    """Fachfläche der Probe: A ganzes Fach, B nur das Anschlussende (hinten offen)."""
    u1 = BC.U1 if variant == "A" else BC.BU0 + LB
    return u1, sbox(BC.U0, BC.V0, u1, BC.V1)


def outer(variant):
    u1, fach = region(variant)
    return sbox(BC.U0 - WALL, BC.V0 - WALL, u1 + (WALL if variant == "A" else 0), BC.V1 + WALL)


def box_part(variant):
    """Unterkasten-Ausschnitt: Boden, Wände (Vorderwand mit Fenster), Zaun; Variante B hinten offen."""
    u1, fach = region(variant)
    out = outer(variant)
    inner = sbox(BC.U0, BC.V0, u1 + (0 if variant == "A" else 5.0), BC.V1)
    shell = BC.slab_ch(out, 0.0, TOP, CH) - G.extrude(inner, ZF, TOP + 1)
    fence = FP["fence"].intersection(sbox(BC.U0 - 1, BC.V0 - 3, u1, BC.V1 + 3))
    solids = [shell, G.extrude(fence, ZF - 0.01, ZF + PP.FENCE[1])]
    window = G.extrude(FP["window"], ZF, TOP + 0.5)
    return G.union(solids) - window


def lid_part(variant):
    return BC.slab_ch(outer(variant), 0.0, PLATE_T, CH)


def masses(variant):
    out = {}
    for n, man in (("box", box_part(variant)), ("lid", lid_part(variant))):
        if variant == "A":                   # Variante A: Schätzung über das Volumen (15 % Füllung, 3 Wände), die Schichtschätzung rechnet zu lange
            g = float(man.volume()) / 1000.0 * (1.37 if n == "box" else 1.08 if n == "lid" else 1.0)   # g je cm³, aus Variante B kalibriert
        else:
            g, layers = SR.estimate(man)
        out[n] = float(g)
    return out


def sizes(variant):
    x0, y0, x1, y1 = outer(variant).bounds
    return x1 - x0, y1 - y0


if __name__ == "__main__":
    for v in "AB":
        print(v, sizes(v), masses(v))
