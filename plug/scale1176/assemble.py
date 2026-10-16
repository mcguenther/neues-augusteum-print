#!/usr/bin/env python3
"""Sammelt die Ergebnisse der Passungsrechnung (Maßstab 1:1250, Platte höchstens 230 × 230 mm) in data.json.

Eingaben: fit.json (Maßstab 1:1176, analysis_fit.py), fit_1250.json (Maßstab 1:1250). Die Lage des Schachts wird hier gesucht,
je Gebäude für „Standard“ (Kassette über der Oberfläche, Gebäude muss 8,75 mm hoch sein) und „versenkt“ (Kassette unter der
Oberfläche, nur der Grundriss zählt). Start mit Wand und Länge aus fit_1250.json, bei Fehlschlag in 0,5-mm-Schritten kürzer.
Aufruf aus dem Wurzelverzeichnis: python3 -m plug.scale1176.assemble   (dauert einige Minuten)
"""
import json
import math
import os

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.prepared import prep

import generate as G
import innenhof
from plug.testcase import params as P

HERE = os.path.dirname(__file__)
SCALE = 1250
K = 1000 / SCALE
# (Wand, Länge) je Gebäude aus fit_1250.json
STANDARD = {"01_paulinum": (1.2, None), "02_neues_augusteum": (1.2, None), "03_hoersaalgebaeude": (1.2, None),
            "04_seminargebaeude": (0.8, None), "05_institutsgebaeude": (0.8, 28.56), "06_city_hochhaus": (0.8, 22.56)}
VERSENKT = {"05_institutsgebaeude": (1.2, None), "06_city_hochhaus": (0.8, 24.06)}


def rect(cx, cy, w, l, a):
    return affinity.translate(affinity.rotate(box(-w / 2, -l / 2, w / 2, l / 2), a, origin=(0, 0)), cx, cy)


def coords(g):
    return [[[round(x, 2), round(y, 2)] for x, y in p.exterior.coords] for p in (g.geoms if hasattr(g, "geoms") else [g])]


def slice_poly(solid, z, fp):
    g = None
    for ring in solid.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return g.buffer(0).intersection(fp.buffer(0.01))


def find(u, w, l, centre):
    pu, best = prep(u.buffer(1e-6)), None
    minx, miny, maxx, maxy = u.bounds
    for a in range(0, 180, 5):
        for x in np.arange(minx, maxx, 0.5):
            for y in np.arange(miny, maxy, 0.5):
                if pu.contains(Point(x, y)) and pu.contains(rect(x, y, w, l, a)):
                    c = math.hypot(x - centre.x, y - centre.y)
                    if best is None or c < best[0]:
                        best = (c, a, x, y)
    return best


def place(u, fp, KW, KL, wall, kl):
    kl = kl or KL
    while kl > 12:
        best = find(u, KW + 2 * wall, kl + 2 * wall, fp.centroid)
        if best:
            return dict(angle=best[1], cx=best[2], cy=best[3], kl=kl, wall=wall)
        kl -= 0.5
    return None


def main():
    G.FAST = True
    models = G.source_models("laserscan", K)
    d, kd = P.dims(), P.kass_dims()
    KW = kd["cw"] + 2 * P.KASS_CLR_T
    KL = d["y_kass1"] - d["y_kass0"] + 2 * P.KASS_CLR_T
    tail = (d["y_kass0"] - P.KASS_CLR_T) - d["y_tail"]
    hmin = d["box_top"] + 0.8
    fit = json.load(open(os.path.join(HERE, "fit_1250.json")))
    hof = innenhof.model(K, [v[1] for v in models.values()])[1]
    out = dict(scale=SCALE, K=K, KW=KW, KL=KL, tail=tail, hmin=hmin, F=d["F"], kass_top=d["kass_top"], plate_t=d["plate_t"],
               buildings={}, hof=coords(hof), hof_area=hof.area)
    for slug, (solid, fp, _) in models.items():
        if slug.startswith("08"):
            continue
        b = dict(fp=coords(fp), fit=fit[slug], area=fp.area, hmax=G.to_trimesh(solid).bounds[1][2])
        b["standard"] = place(slice_poly(solid, hmin / K * K, fp), fp, KW, KL, *STANDARD[slug])
        if slug in VERSENKT:
            b["versenkt"] = place(fp, fp, KW, KL, *VERSENKT[slug])
        out["buildings"][slug] = b
        print(slug, b["standard"], b.get("versenkt"), flush=True)
    json.dump(out, open(os.path.join(HERE, "data.json"), "w"))


if __name__ == "__main__":
    main()
