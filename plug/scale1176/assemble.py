#!/usr/bin/env python3
"""Sammelt die Ergebnisse der Passungsrechnung für Maßstab 1:1176 (15 % kleiner als 1:1000) in data.json.

Eingaben: fit.json (analysis_fit.py: größtes Wandmaß je Gebäude und Maßstab, kleinster Maßstabsfaktor) und die Lagen
aus analysis_place.py (hier fest eingetragen, weil die Suche etwa 2 min dauert; Lage des Uniriesen wird hier gesucht).
Aufruf aus dem Wurzelverzeichnis: python3 -m plug.scale1176.assemble
"""
import json
import math
import os

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely.prepared import prep

import generate as G
import innenhof
from plug.testcase import params as P

HERE = os.path.dirname(__file__)
K = 1000 / 1176.47
PLACE = {  # Winkel (Grad, gegen den Uhrzeigersinn, Schacht längs y), Mittelpunkt in m bei 1:1000, Wand 1,2 mm
    "01_paulinum": (80, -53.744, 62.320), "02_neues_augusteum": (170, -55.172, 17.160),
    "03_hoersaalgebaeude": (0, -117.575, -62.084), "04_seminargebaeude": (170, -130.163, 37.252),
    "05_institutsgebaeude": (170, -118.812, 96.897)}
UNI_KL = 25.56      # gekürzter Schacht des City-Hochhauses (analysis_place.py)


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
        for x in np.arange(minx, maxx, 0.25):
            for y in np.arange(miny, maxy, 0.25):
                if pu.contains(Point(x, y)) and pu.contains(rect(x, y, w, l, a)):
                    c = math.hypot(x - centre.x, y - centre.y)
                    if best is None or c < best[0]:
                        best = (c, a, x, y)
    return best


def main():
    G.FAST = True
    models = G.source_models("laserscan", K)
    d, kd = P.dims(), P.kass_dims()
    KW = kd["cw"] + 2 * P.KASS_CLR_T
    KL = d["y_kass1"] - d["y_kass0"] + 2 * P.KASS_CLR_T
    tail = (d["y_kass0"] - P.KASS_CLR_T) - d["y_tail"]        # Lötende ragt so weit hinter das Schachtende
    hmin = d["box_top"] + 0.8
    fit = json.load(open(os.path.join(HERE, "fit.json")))
    hof = innenhof.model(K, [v[1] for v in models.values()])[1]
    out = dict(K=K, KW=KW, KL=KL, tail=tail, hmin=hmin, buildings={}, hof=coords(hof), hof_area=hof.area)
    for slug, (solid, fp, _) in models.items():
        if slug.startswith("08"):
            continue
        if slug in PLACE:
            a, x, y = PLACE[slug]
            cx, cy, kl, wall = x * K, y * K, KL, 1.2
        else:
            u = slice_poly(solid, hmin, fp)
            kl, wall = UNI_KL, 0.8
            while True:
                best = find(u, KW + 1.6, kl + 1.6, fp.centroid)
                if best:
                    break
                kl -= 0.5
            _, a, cx, cy = best
        out["buildings"][slug] = dict(fp=coords(fp), fit=fit[slug], angle=a, cx=cx, cy=cy, kl=kl, wall=wall,
                                      area=fp.area, hmax=G.to_trimesh(solid).bounds[1][2])
        print(slug, a, round(cx, 1), round(cy, 1))
    json.dump(out, open(os.path.join(HERE, "data.json"), "w"))


if __name__ == "__main__":
    main()
