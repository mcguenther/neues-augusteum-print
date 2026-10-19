#!/usr/bin/env python3
"""Prüfung der fertigen Gebäude untereinander (stl/steckmodul_campus/gebaeude/): kein gemeinsames Volumen und an den Nähten mindestens die Fuge, gemessen am Umriss in einem
Schnitt durch den Fuß (z = -7 mm) und einem knapp über der Plattenoberfläche (z = +0,5 mm).

Die STL liegen in Weltlage und sind mit der Fuge 1,0 zugeschnitten (`plug.divider.geom.fuge`, Spiel `ZUSCHNITT_CLR_T` 0,10 und Wand 0,8). Auf der Platte stehen die Gebäude je Naht
um das größere Mulden-Spiel (`OUTLINE_CLR_T` 0,15) auseinandergerückt (`plug.campus.SHIFTS`, `plug.divider.geom.verschiebungen`); geprüft wird die Lage auf der Platte:
Abstand mindestens `fuge_platte()` (1,1 mm, Wand zwischen den Mulden 0,8 mm). Ausnahme Paulinum/Neues Augusteum: Der Zahn des Paulinums steht im Schlitz des Neuen Augusteums, seine
beiden Flanken lassen sich durch Verschieben nicht beide vergrößern und behalten die Fuge 1,0 (Wand dort 0,7 mm).

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 10 s; erst `python3 -m plug.buildings` laufen lassen):
    python3 -m plug.divider.check
Die Ausgabe enthält „keine Kollisionen“, wenn alles passt; Exit-Code 1 sonst.
"""
import itertools
import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, HERE)
import generate as G  # noqa: E402
from plug.divider import geom as D  # noqa: E402
from plug.testcase import params as P  # noqa: E402

DIR = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude")
SLUGS = ["01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus"]


def umriss(tm, z):
    """Äußerer Umriss des Schnitts in der Höhe z (größte geschlossene Kontur, gefüllt)."""
    sec = tm.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    polys = [Polygon(np.asarray(e)[:, :2]).buffer(0) for e in sec.discrete if len(e) > 3]
    return max(polys, key=lambda q: q.area)


def manifold(tm):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))


# Nähte, an denen gegenüberliegende Flanken nur die Fuge des Zuschnitts halten können (siehe oben)
FLANKEN = {("01_paulinum", "02_neues_augusteum")}


def main(scale=P.SCALE_PLAN):
    from plug import campus as C
    C.platte_lage(C.models_plan(1000.0 / scale, scale))           # setzt C.SHIFTS (Lage der Gebäude auf der Platte)
    fuge = D.fuge_platte()
    tms = {s: trimesh.load(os.path.join(DIR, "%s_1zu%d.stl" % (s, scale))) for s in SLUGS}
    for s_, t_ in tms.items():
        t_.apply_translation([*C.SHIFTS.get(s_, (0.0, 0.0)), 0.0])
    mans = {s: manifold(t) for s, t in tms.items()}
    ok = True
    print("Gebäude untereinander in der Lage auf der Platte (Fuge %.2f mm, Wand zwischen den Mulden %.2f mm bei Spiel %.2f; Zuschnitt der STL: Fuge %.2f mm; Verschiebung %s):" % (
        fuge, fuge - 2 * P.OUTLINE_CLR_T, P.OUTLINE_CLR_T, D.fuge(), ", ".join("%s (%.3f | %.3f)" % (k[:2], *v) for k, v in C.SHIFTS.items())))
    for a, b in itertools.combinations(SLUGS, 2):
        vol = (mans[a] ^ mans[b]).volume()
        d = min(umriss(tms[a], z).distance(umriss(tms[b], z)) for z in (-7.0, 0.5))
        # Wand zwischen den Mulden der Platte (Grundriss des Fußes mit Mitre-Puffer Mulden-Spiel, wie plug.campus.mulde_body)
        wand = umriss(tms[a], -7.0).buffer(P.OUTLINE_CLR_T, join_style=2).distance(umriss(tms[b], -7.0).buffer(P.OUTLINE_CLR_T, join_style=2))
        naht = d < 4.0
        flag = ""
        wand_soll = D.WAND_T if (a, b) not in FLANKEN else D.fuge() - 2 * P.OUTLINE_CLR_T
        if vol > 1e-3:
            flag = "  KOLLISION"
            ok = False
        elif naht and (d < ((D.fuge() if (a, b) in FLANKEN else fuge) - 0.02) or wand < wand_soll - 0.02):
            flag = "  ZU NAH"
            ok = False
        if naht or vol > 1e-3:
            print("  %-20s %-20s Abstand %.3f mm, Wand zwischen den Mulden %.3f mm, gemeinsames Volumen %.4f mm³%s%s" % (
                a[3:], b[3:], d, wand, vol, flag, "  (Zahnflanken: Wand dort höchstens 0,7)" if naht and (a, b) in FLANKEN else ""))
    print("keine Kollisionen" if ok else "ACHTUNG: Gebäude kollidieren oder liegen enger als die Fuge")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
