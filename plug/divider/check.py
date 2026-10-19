#!/usr/bin/env python3
"""Prüfung der fertigen Gebäude untereinander (stl/steckmodul_campus/gebaeude/): kein gemeinsames Volumen und an den Nähten mindestens die Fuge
(`plug.divider.geom.fuge`, 1,0 mm bei 0,1 mm Spiel und 0,8 mm Wand) Abstand, gemessen am Umriss in einem Schnitt durch den Fuß (z = -7 mm) und
einem knapp über der Plattenoberfläche (z = +0,5 mm).

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


def main(scale=P.SCALE_PLAN):
    fuge = D.fuge()
    tms = {s: trimesh.load(os.path.join(DIR, "%s_1zu%d.stl" % (s, scale))) for s in SLUGS}
    mans = {s: manifold(t) for s, t in tms.items()}
    ok = True
    print("Gebäude untereinander (Fuge %.2f mm):" % fuge)
    for a, b in itertools.combinations(SLUGS, 2):
        vol = (mans[a] ^ mans[b]).volume()
        d = min(umriss(tms[a], z).distance(umriss(tms[b], z)) for z in (-7.0, 0.5))
        naht = d < 4.0
        flag = ""
        if vol > 1e-3:
            flag = "  KOLLISION"
            ok = False
        elif naht and d < fuge - 0.02:
            flag = "  ZU NAH"
            ok = False
        if naht or vol > 1e-3:
            print("  %-20s %-20s Abstand %.3f mm, gemeinsames Volumen %.4f mm³%s" % (a[3:], b[3:], d, vol, flag))
    print("keine Kollisionen" if ok else "ACHTUNG: Gebäude kollidieren oder liegen enger als die Fuge")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
