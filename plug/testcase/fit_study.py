#!/usr/bin/env python3
"""Passt die Kassette in den Grundriss? Rechteck-Suche in den Laserscan-Gebäuden (Schnitt 2 mm über dem Boden).

Je Gebäude und Maßstab: größte Wandstärke um den Schacht, bei der das Außenrechteck (Kassette + Spiel + 2 × Wand) noch in den
Grundriss passt (beliebige Drehung und Lage). Ergebnis nach plug/testcase/variants_fit.json (klein, eingecheckt), damit die
Planungsseite ohne die STL-Dateien auskommt.

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 2 min):
    python3 -m plug.testcase.fit_study
"""
import json
import math
import os
import warnings

import numpy as np
import shapely
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

from plug.testcase import variants as V

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "plug", "testcase", "variants_fit.json")
NAMES = ("01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus")
SCALES = ("1zu1500", "1zu1000")
WALL_MIN = 1.2          # Wand um den Schacht (wie sd.WALL)
SHAFT_CLR = 0.06        # Spiel je Seite im Schacht


def footprint(scale, name, z=2.0):
    m = trimesh.load(os.path.join(HERE, "stl", "laserscan", scale, "einzeln", name + ".stl"))
    sec = m.section(plane_origin=[0, 0, m.bounds[0][2] + z], plane_normal=[0, 0, 1])
    p2, _ = sec.to_planar()
    ps = [Polygon(e).buffer(0) for e in p2.discrete if len(e) > 3]
    ps = [p for p in ps if p.area > 0.5]
    return unary_union(ps), float(m.bounds[1][2] - m.bounds[0][2])


def fit(poly, A, B, astep=5, gstep=0.5):
    """Sucht eine Lage des Rechtecks A × B (beliebiger Winkel) im Polygon; liefert (cx, cy, Winkel in Grad) oder None."""
    r = min(A, B) / 2
    er = poly.buffer(-r)
    if er.is_empty:
        return None
    x0, y0, x1, y1 = er.bounds
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-9, gstep), np.arange(y0, y1 + 1e-9, gstep))
    X, Y = X.ravel(), Y.ravel()
    ins = shapely.contains_xy(er, X, Y)
    X, Y = X[ins], Y[ins]
    shapely.prepare(poly)
    corners = np.array([[-A / 2, -B / 2], [A / 2, -B / 2], [A / 2, B / 2], [-A / 2, B / 2], [-A / 2, -B / 2]])
    for ang in range(0, 180, astep):
        a = math.radians(ang)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        off = corners @ rot.T
        coords = np.stack([X[:, None] + off[None, :, 0], Y[:, None] + off[None, :, 1]], axis=2)
        ok = shapely.contains(poly, shapely.polygons(coords))
        if ok.any():
            i = int(np.argmax(ok))
            return (float(X[i]), float(Y[i]), ang)
    return None


def max_wall(poly, a, b, wmax=4.0):
    """Größte Wandstärke w, bei der (a + 2w) × (b + 2w) noch passt; None, wenn schon das Innenmaß nicht passt."""
    if fit(poly, a, b) is None:
        return None
    lo, hi = 0.0, wmax
    for _ in range(7):
        mid = (lo + hi) / 2
        if fit(poly, a + 2 * mid, b + 2 * mid) is not None:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    cas = {k: (v["w"] + 2 * SHAFT_CLR, v["d"] + 2 * SHAFT_CLR) for k, v in V.outlines().items()}
    res = {}
    for sc in SCALES:
        for n in NAMES:
            poly, h = footprint(sc, n)
            row = dict(height=round(h, 1), area=round(poly.area), walls={}, place={}, poly=None)
            for k, (a, b) in cas.items():
                w = max_wall(poly, a, b)
                row["walls"][k] = None if w is None else round(w, 2)
                pl = fit(poly, a + 2 * WALL_MIN, b + 2 * WALL_MIN)
                row["place"][k] = pl
            simp = poly.simplify(0.15)
            row["poly"] = [[round(x, 2), round(y, 2)] for x, y in (simp.exterior.coords if simp.geom_type == "Polygon" else max(simp.geoms, key=lambda g: g.area).exterior.coords)]
            res["%s/%s" % (sc, n)] = row
            print(sc, n, row["height"], row["walls"], flush=True)
    res["_meta"] = dict(wall_min=WALL_MIN, shaft_clr=SHAFT_CLR, cassettes={k: [round(a, 2), round(b, 2)] for k, (a, b) in cas.items()})
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    print("geschrieben:", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
