#!/usr/bin/env python3
"""Daten für die Planseite der Passform-Stummel: Umriss, Schacht, Umfang je Höhe des City-Hochhauses (Laserscan 1:1300, Lage aus placements_1300.json).

Aufruf: python3 -m plug.footfit.data   (ca. 1 min, schreibt plug/footfit/data.json)
"""
import json
import os

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon

import generate as G
from plug import campus as C
from plug.scale1176 import variants1250 as W
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "06_city_hochhaus"


def ring(g):
    return [[round(x, 3), round(y, 3)] for x, y in g.exterior.coords]


def main():
    G.FAST = True
    scale = P.SCALE_PLAN
    models = G.source_models("laserscan", 1000.0 / scale)
    solid, fp, _ = models[SLUG]
    fp = max(fp.geoms, key=lambda g: g.area) if hasattr(fp, "geoms") else fp
    place = json.load(open(C.CACHE % scale))[SLUG]
    var = place["var"]
    d = P.dims_plan()
    w, dep = C.shaft_size(var)
    yc = C.foot_local(var, 0.0).centroid.y
    y0 = d["y_kass0"] - P.KASS_CLR_T
    from shapely.geometry import box
    shaft = box(-w / 2, y0, w / 2, y0 + dep)
    shaft = affinity.translate(affinity.rotate(affinity.translate(shaft, 0, -yc), place["angle"], origin=(0, 0)), place["cx"], place["cy"])
    from shapely.geometry import Point
    import math
    a = math.radians(place["angle"])
    def world(x, y):
        y -= yc
        return [round(place["cx"] + x * math.cos(a) - y * math.sin(a), 3), round(place["cy"] + x * math.sin(a) + y * math.cos(a), 3)]
    pins = [world(x, 0.0) for x in __import__("plug.dupont", fromlist=["x"]).pin_x()]
    lx, ly = C.led_local(var)
    led_xy = world(lx, ly)
    top, led = W.top_led(var)
    need = top - P.dims()["F"] - P.MULDE_EXTRA_T + P.STOP_T
    hmax = float(G.to_trimesh(solid).bounds[1][2])
    prof = []
    z = 0.5
    while z < hmax:
        s = C.slice_poly(solid, z, fp)
        if s is not None and not s.is_empty:
            prof.append([round(z, 1), round(s.length, 1), round(s.area, 1)])
        z += 2.0
    out = dict(slug=SLUG, scale=scale, var=var, wall=place["wall"], F=d["F"], plate_t=C.plate_thickness(d), ceil=P.CEIL_T,
               clr=P.OUTLINE_CLR_T, hmax=round(hmax, 2), need=round(need, 2), led_z=round(led, 2),
               shaft_w=round(w, 3), shaft_d=round(dep, 3), outline=ring(fp.simplify(0.02)), shaft=ring(shaft),
               pin_x=[round(x, 3) for x in __import__("plug.dupont", fromlist=["x"]).pin_x()], place=place, profile=prof, pins=pins, led_xy=led_xy, top=round(top, 2),
               area=round(fp.area, 1), perimeter=round(fp.length, 1))
    json.dump(out, open(os.path.join(HERE, "data.json"), "w"))
    print({k: v for k, v in out.items() if k not in ("outline", "shaft", "profile")})
    print(len(prof), "Profile; Umfang bei z:", prof[:3], prof[-2:])


if __name__ == "__main__":
    main()
