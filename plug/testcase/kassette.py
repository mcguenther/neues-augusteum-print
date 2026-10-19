#!/usr/bin/env python3
"""Kassette v4: wie v2 (Tasche unten offen, Schultern, Aderschlitz), aber die flache Oberseite liegt als Podest PODEST_T höher und
die Kante zur Tasche ist mit FILLET_T gerundet, damit die Adern im Bogen statt im Knick zur LED laufen.

Konstruktionslage: Unterkante z = 0, Mitte x = 0, y = 0 an der Taschenseite. Bild: python3 -m plug.testcase.kassette
"""
import math
import os

import manifold3d as m3d

from plug import dupont as sd
from plug import series2 as N2
from plug.geom import box, cbox, diff, prism_x, to_tm, vol_int, xcut, capsule, union
from plug.testcase import params as P

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREV = os.path.join(HERE, "vorschau", "steckmodul_testcase")


def kassette4(tol=None, centered=False, notches=0, schlank=0.0, enger=0.0):
    """tol = Luft über der Buchse (Taschenhöhe − 14,0); notches = Kerben in der +x-Seite als Kennzeichnung.
    schlank = Außenmaß in Breite und Tiefe je Seite so viel kleiner (Passung bei wechselnden Filamenten, `plug.filament.kassetten`), enger = Buchsentasche in Breite und Tiefe insgesamt so viel enger."""
    k = P.kass_dims(tol)
    L, cw, top = k["L"], k["cw"], k["top"]
    body = N2.chamfered_block(cw - 2 * schlank, L - 2 * schlank, top, P.EF_CH_T, P.ENTRY_CH_T).translate([0, L / 2, 0])
    cuts = [cbox(k["pk_w"] - enger, k["pk_d"] - enger, -0.01, k["zp"], cy=k["ypin"]),                                  # Tasche, unten offen
            N2.chamfer_hole(k["pk_w"] - enger, k["pk_d"] - enger, 0.0, P.ENTRY_CH_T, True, cy=k["ypin"]),            # Einführfase
            box(-N2.WIRE_W / 2, N2.WIRE_W / 2, k["y_p0"], k["y1"], k["zp"] - 0.01, top + 0.01)]       # Aderschlitz
    r, y1 = P.FILLET_T, k["y1"]
    arc = [(y1 + r + r * math.cos(a), top - r + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 20 for j in range(21)]]
    prof = [(y1 - 0.01, top - r), (y1 - 0.01, top + 0.01), (y1 + r, top + 0.01)] + arc[1:-1] + [(y1, top - r)]
    cuts.append(prism_x(prof, -N2.WIRE_W / 2, N2.WIRE_W / 2))
    gx = sorted([sd.pin_x()[3], sd.pad_x("GND")])
    cuts.append(box(gx[0] - 0.9, gx[1] + 0.9, k["seat0"] - 1.7, k["seat0"] - 0.5, top - sd.GROOVE[1], top + 0.01))   # Rinne für DETECT
    cuts += N2.notches_x(notches, 6.0, 2.0, top - 2.0, cw / 2, pitch=2.4)
    m = diff(body, *cuts)
    return m.translate([0, -L / 2, 0]) if centered else m


def housing(k):
    """Buchse (Nennmaß) an den Schultern, Kassette nicht zentriert (y = 0 an der Taschenseite)."""
    return sd.housing_part(k["zp"] - sd.HSG_H).translate([0, -sd.dims()["HY"] + k["ypin"], 0])


def wire_points(k, n=24):
    """Mittellinie einer Ader (y, z): senkrecht aus der Buchse, sanfter Bogen über die gerundete Kante, dann flach zur LED.
    Bézier-Kurve; sie hält mindestens Aderradius Abstand zur Rundung (geprüft in main)."""
    r, y1, top, zp, yb = P.FILLET_T, k["y1"], k["top"], k["zp"], k["ypin"]
    wr = sd.WIRE_D / 2
    p0, p1, p2, p3 = (yb, zp), (yb, zp + 3.4), (y1 + 0.6, top + wr + 0.3), (y1 + r + 1.6, top + wr)
    pts = []
    for j in range(n + 1):
        t = j / n
        pts.append(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d
                         for a, b, c, d in zip(p0, p1, p2, p3)))
    pts.append((k["seat0"] + 2.0, top + wr))
    return pts


def wire_clearance(k):
    """Kleinster Abstand der Aderachse zur gerundeten Kante minus Aderradius (soll ≥ 0 sein)."""
    r, y1, top = P.FILLET_T, k["y1"], k["top"]
    cy, cz = y1 + r, top - r
    best = 9.9
    for y, z in wire_points(k):
        if y < cy and z < top:                      # nur Punkte neben der Rundung zählen
            best = min(best, math.hypot(y - cy, z - cz) - r - sd.WIRE_D / 2)
    return best


def main():
    os.makedirs(PREV, exist_ok=True)
    k = P.kass_dims()
    kc = kassette4()
    tm = to_tm(kc)
    print("Kassette v4: %.2f × %.2f × %.2f mm, dicht=%s, Podest %.1f über v2" % (k["cw"], k["L"], k["top"], tm.is_watertight, P.PODEST_T))
    h = housing(k)
    v = vol_int(h, kc)
    kt = P.kass_dims(P.HSG_TOL_TIGHT)
    v += vol_int(housing(kt), kassette4(P.HSG_TOL_TIGHT, notches=2))
    print("Ader: kleinster Abstand zur Rundung %.2f mm (≥ 0 = frei), Länge der Kurve ca. %.1f mm" % (wire_clearance(k), sum(math.dist(a, b) for a, b in zip(wire_points(k), wire_points(k)[1:]))))
    print("Buchse (Nennmaß) in der Tasche: Überschneidung %.3f mm³  %s, Luft über der Buchse %.2f" % (v, "ok" if v < 0.05 else "KOLLISION", k["zp"] - h.bounding_box()[5]))
    # Bild: schräg, Schnitt mit Buchse und Ader, daneben Kassette v2 (alt)
    import preview
    from PIL import Image
    k2 = N2.kass2_dims()
    old = N2.kassette2()
    ho = N2.housing_in(k2, centered=False)
    wire = union([capsule((0, y, z), (0, y2, z2), sd.WIRE_D / 2) for (y, z), (y2, z2) in zip(wire_points(k), wire_points(k)[1:])])
    wire_o = None
    tiles = [preview.render([(to_tm(old), "#c9a27a")], size=(640, 480), azim=-55, elev=38),
             preview.render([(to_tm(kc), "#e3862a")], size=(640, 480), azim=-55, elev=38),
             preview.render([(to_tm(xcut(old, 0.0)), "#c9a27a"), (to_tm(xcut(ho, 0.0)), "#f4f1e8")], size=(640, 480), azim=0, elev=0),
             preview.render([(to_tm(xcut(kc, 0.0)), "#e3862a"), (to_tm(xcut(h, 0.0)), "#f4f1e8"), (to_tm(wire), "#c8423b")], size=(640, 480), azim=0, elev=0)]
    sheet = Image.new("RGB", (1280, 960), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * 640, (i // 2) * 480))
    sheet.save(os.path.join(PREV, "kassette_v4.png"))
    print("Bild: vorschau/steckmodul_testcase/kassette_v4.png")
    return 0 if (tm.is_watertight and v < 0.05) else 1


if __name__ == "__main__":
    raise SystemExit(main())
