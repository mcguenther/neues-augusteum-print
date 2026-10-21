#!/usr/bin/env python3
"""Ausrichtung der Kassetten: plug/kassette_orient/page.html (Vorlage page.template.html).

Zeigt je Gebäude, in welche Himmelsrichtung die schmale Seite (Rand 1,18 mm vorn, dort blickt die LED hin) der Kassette im Gebäude zeigt, und die
Ränder der Kassetten von oben auf den Boden gesehen. Daten: Drehwinkel und Lage je Gebäude aus `plug/scale1176/placements_1300.json` (Zwischenspeicher
`plug.campus.CACHE`), Umriss des Fußes aus den fertigen Gebäude-STL (Schnitt bei z = 7), Maße der Kassetten aus den STL in `stl/steckmodul_campus/kassetten/`.
Voraussetzung: `python3 -m plug.buildings` ist gelaufen.

Aufruf (aus dem Wurzelverzeichnis, ca. 15 s):
    python3 -m plug.kassette_orient.build_page
"""
import json
import math
import os

import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

from plug import buildings as B
from plug import campus as C
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KASSETTEN = os.path.join(ROOT, "stl", "steckmodul_campus", "kassetten")
NAMEN = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}
KOMPASS = ["Nord", "Nordost", "Ost", "Südost", "Süd", "Südwest", "West", "Nordwest"]


def kassette_masse(path):
    """Außenmaß und Ränder am Boden (Schnitt bei z = 8, unterhalb der Schulter) in Konstruktionslage (y = 0 vorn)."""
    m = trimesh.load(path)
    v = m.section(plane_origin=[0, 0, 8.0], plane_normal=[0, 0, 1]).vertices
    xs, ys = sorted(set(round(float(a), 2) for a in v[:, 0])), sorted(set(round(float(a), 2) for a in v[:, 1]))
    return dict(hx=max(abs(xs[0]), abs(xs[-1])), y0=ys[0], y1=ys[-1], hoehe=round(float(m.bounds[1][2]), 2))


def tasche(var):
    """Tasche am Boden: halbe Breite, vorn, hinten (aus der Konstruktion: Wand 1,2, Tasche 10,46 × 2,84 um y = 2,67 mittig)."""
    from plug.testcase import variants as V
    d = V.dims(var) if var != "v4" else None
    ypin = d["ypin"] if d else P.kass_dims()["ypin"]
    return dict(hx=(10.56 - 0.10) / 2, y0=ypin - (2.94 - 0.10) / 2, y1=ypin + (2.94 - 0.10) / 2)


def umriss(slug):
    m = trimesh.load(os.path.join(B.OUT, "%s_1zu%d.stl" % (slug, P.SCALE_PLAN)))
    s = m.section(plane_origin=[0, 0, 7.0], plane_normal=[0, 0, 1])
    polys = sorted((Polygon(d[:, :2]).buffer(0) for d in s.discrete), key=lambda g: -g.area)
    aussen = [g for i, g in enumerate(polys) if not any(h.contains(g) for h in polys[:i])]
    g = unary_union(aussen).simplify(0.05)
    geos = list(g.geoms) if hasattr(g, "geoms") else [g]
    return [[[round(x, 2), round(y, 2)] for x, y in p.exterior.coords] for p in geos]


def main():
    places = json.load(open(C.CACHE % P.SCALE_PLAN))
    out = []
    for slug, p in places.items():
        var = p["var"]
        yc = C.foot_local(var, 0.0).centroid.y
        a = math.radians(float(p["angle"]))
        dx, dy = math.sin(a), -math.cos(a)
        b = math.degrees(math.atan2(dx, dy)) % 360
        pfad = os.path.join(KASSETTEN, "%s_kassette_%s.stl" % (slug, var))
        out.append(dict(slug=slug, name=NAMEN[slug], var=var, angle=float(p["angle"]), cx=p["cx"], cy=p["cy"], yoff=round(P.dims_plan()["y_kass0"] - yc, 4),
                        bearing=round(b), kompass=KOMPASS[int((b + 22.5) // 45) % 8], kassette=kassette_masse(pfad), tasche=tasche(var), umriss=umriss(slug)))
    tpl = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    html = tpl.replace("/*DATA*/null", json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    path = os.path.join(HERE, "page.html")
    open(path, "w", encoding="utf-8").write(html)
    for o in out:
        print("%-22s %-5s schmale Seite → %-9s %3d°" % (o["slug"], o["var"], o["kompass"], o["bearing"]))
    print("geschrieben:", os.path.relpath(path, ROOT), "%d KB" % (len(html) // 1024))


if __name__ == "__main__":
    main()
