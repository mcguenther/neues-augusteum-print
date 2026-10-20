#!/usr/bin/env python3
"""Passprobe im Rechner: die fertigen Gebäude-STL und der Hof-Einsatz in den Mulden der fertigen Steckplatte (beide aus stl/steckmodul_campus/).

Die Gebäude-STL liegen in Weltlage und sind mit der Fuge 1,0 zugeschnitten; auf der Platte stehen sie um `plug.campus.SHIFTS` auseinandergerückt (Mulden-Spiel
`OUTLINE_CLR_T`). Hier wird jedes Gebäude an seine Lage auf der Platte gesetzt und geprüft:
  - keine Überschneidung mit der Platte (Fuß in der Mulde, Unterkante auf dem Muldenboden),
  - Spalt zwischen Fuß und Muldenwand in mehreren Höhen: kleinster Wert = Mulden-Spiel (Toleranz 0,02: die Fußwand aus dem Laserscan läuft nach oben stellenweise
    bis 0,017 mm nach außen, Paulinum), größter Wert (Hausdorff-Abstand der Umrisse) an den Ecken, weil die Mulde mit Gehrung versetzt ist (90°: Spiel · √2 = 0,21,
    spitze Ecken mehr; Grenze `SPALT_MAX`); die Fuß-Fase unten und die Einführfase oben liegen außerhalb der Schnitte,
  - Kontrolle: um 0,2 mm verschoben stößt das Gebäude an (die Prüfung greift),
  - die Pin-Löcher des Docks im Muldenboden liegen im Schacht des Gebäudes (Dock und Schacht sind gleich verschoben).
Dazu der Hof-Einsatz in seiner Aussparung (Spiel `HOF_CLR_T`).

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 30 s; erst `python3 -m plug.campus`):
    python3 -m plug.check_platte
Gibt „keine Kollisionen“ aus, wenn alles passt; Exit-Code 1 sonst.
"""
import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from plug.testcase import params as P  # noqa: E402

DIR = os.path.join(HERE, "stl", "steckmodul_campus")
SLUGS = ["01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus"]
T = P.dims_plan()["F"] + P.CEIL_T                       # Plattendicke 14,6; Gebäude-STL: z = 0 an der Plattenoberfläche
Z_GEB = (9.0, 10.5, 12.0, 13.5)                         # Schnitthöhen in Plattenkoordinaten: über dem Ende der Fuß-Fase (Muldenboden 0,4, Fase 4,0; schmale Teile wachsen 45° aus der Wand und sind beim Seminargebäude erst bei 8,6 voll, `fase_lagen` im JSON), unter der Einführfase 0,5 oben
Z_HOF = (T - 1.5, T - 1.0, T - 0.7)                     # Hof-Aussparung 6,0 tief, Einführfase unten 4,0: Spalt nur oberhalb der Fase messen
SPALT_MAX = 0.35                                        # größter Spalt an Gehrungsecken (Hörsaalgebäude 0,26 an einer spitzen Ecke)


def manifold(tm):
    tm = tm.copy()
    tm.merge_vertices()
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))


def section(man, z):
    g = None
    for ring in man.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return Polygon() if g is None else g.buffer(0)


def outer(g):
    """Umriss ohne Löcher (Fuß samt Schacht als volle Fläche)."""
    return unary_union([Polygon(p.exterior) for p in getattr(g, "geoms", [g])])


def spalt(teil, platte, z):
    """(kleinster, größter Spalt) zwischen dem Umriss des Teils und der Wand der Aussparung in der Höhe z."""
    f = outer(section(teil, z))
    if f.is_empty:
        return None
    box = f.buffer(3.0, join_style=2)
    loch = box.difference(section(platte, z))                 # Aussparung um das Teil (Mulde bzw. Hof, dazu Nachbarmulden im Rand)
    loch = max(getattr(loch, "geoms", [loch]), key=lambda q: q.intersection(f).area)
    wand = section(platte, z).intersection(box)
    return f.exterior.distance(wand), f.exterior.hausdorff_distance(Polygon(loch.exterior).exterior)


def pruefe(name, teil, platte, zs, spiel, rows, pins=None):
    ok = True
    v = float((teil ^ platte).volume())
    ok &= v < 0.05
    sp = [s for s in (spalt(teil, platte, z) for z in zs) if s]
    smin, smax = min(s[0] for s in sp), max(s[1] for s in sp)
    ok_sp = abs(smin - spiel) <= 0.02 and smax <= SPALT_MAX
    k = [float((teil.translate([dx, dy, 0]) ^ platte).volume()) for dx, dy in ((0.2, 0), (-0.2, 0), (0, 0.2), (0, -0.2))]
    ok_k = min(k) > 0.05
    b = teil.bounding_box()
    boden = b[2] - (P.CEIL_T if pins is not None else T - P.HOF_DEPTH_T)
    txt = "%-22s Überschneidung %.3f mm³ · Spalt %.3f bis %.3f mm (Soll %.2f, Ecken mehr) · 0,2 verschoben stößt an (≥ %.1f mm³) · Unterkante %+.2f über dem Boden" % (
        name, v, smin, smax, spiel, min(k), boden)
    ok &= ok_sp and ok_k and abs(boden) < 0.02
    if pins is not None:
        txt += " · Pin-Löcher im Schacht %d/%d" % pins
        ok &= pins[0] == pins[1] and pins[1] > 0
    rows.append((name, ok, txt))
    return ok


def pin_loecher(platte, teil):
    """Pin-Löcher im Muldenboden unter dem Teil, die im Schacht des Teils liegen: (im Schacht, alle)."""
    boden = section(platte, P.CEIL_T / 2)
    fuss = outer(section(teil, P.CEIL_T + 1.0))
    loecher = [p for p in getattr(fuss.difference(boden), "geoms", [fuss.difference(boden)]) if 0.5 < p.area < 5.0]   # Löcher Ø 1,4 im Boden unter dem Fuß
    schacht = outer(section(teil, P.CEIL_T + 1.0)).difference(section(teil, P.CEIL_T + 1.0))
    return sum(schacht.contains(p.centroid) for p in loecher), len(loecher)


def pruefung():
    """Alle Prüfungen; Rückgabe (ok, Zeilen [(Name, ok, Text)], Kopfzeile, Verschiebungen)."""
    from plug import campus as C
    C.platte_lage(C.models_plan(1000.0 / P.SCALE_PLAN, P.SCALE_PLAN))      # setzt C.SHIFTS
    platte = manifold(trimesh.load(os.path.join(DIR, "steckplatte_1zu1300.stl")))
    rows, ok = [], True
    kopf = "Gebäude in der Steckplatte (Lage auf der Platte, Mulden-Spiel %.2f, Schnitte bei z = %s; Verschiebung je Gebäude %s):" % (
        P.OUTLINE_CLR_T, ", ".join("%.1f" % z for z in Z_GEB), ", ".join("%s (%+.3f | %+.3f)" % (k[:2], *v) for k, v in C.SHIFTS.items()))
    alle = []
    for s in SLUGS:
        tm = trimesh.load(os.path.join(DIR, "gebaeude", "%s_1zu1300.stl" % s))
        g = manifold(tm).translate([*C.SHIFTS.get(s, (0.0, 0.0)), T])
        alle.append(g)
        ok &= pruefe(s, g, platte, Z_GEB, P.OUTLINE_CLR_T, rows, pins=pin_loecher(platte, g))
    hof = manifold(trimesh.load(os.path.join(DIR, "hof_einsatz_1zu1300.stl"))).translate([0, 0, T])
    ok &= pruefe("Hof-Einsatz", hof, platte, Z_HOF, P.HOF_CLR_T, rows)
    vg = max(float((a ^ b).volume()) for i, a in enumerate(alle) for b in alle[i + 1:] + [hof])
    rows.append(("Gebäude und Hof untereinander", vg < 0.05, "Gebäude und Hof untereinander: größte Überschneidung %.4f mm³" % vg))
    ok &= vg < 0.05
    return ok, rows, kopf, dict(C.SHIFTS)


def main():
    ok, rows, kopf, _ = pruefung()
    print(kopf)
    for _, o, t in rows:
        print("  %s  %s" % ("ok    " if o else "FEHLER", t))
    print("keine Kollisionen" if ok else "ACHTUNG: Passung stimmt nicht")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
