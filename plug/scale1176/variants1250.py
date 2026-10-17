#!/usr/bin/env python3
"""Kassetten-Varianten (v4, V1, V2, V2R, V1R, V1RS) bei Maßstab 1:1250 und verschiedener Muldentiefe.

Je Gebäude, Variante und Zusatztiefe der Mulde (0, 4, 8 mm): größte Wand um den Schacht bei Grundriss UND Höhe (Schnitt in der Höhe, die die
Kassettenoberkante plus Dach über der Platte braucht), dazu die Dachhöhe über dem Schacht und der Abstand LED bis Dach.
Ergebnis: plug/scale1176/variants1250.json. Aufruf aus dem Wurzelverzeichnis (einige Minuten): python3 -m plug.scale1176.variants1250
"""
import json
import os

from shapely.geometry import Polygon, box
from shapely import affinity

import generate as G
from plug.scale1176 import assemble as A
from plug.testcase import fit_study as FS
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(__file__)
K = A.K
DELTAS = (0, 4, 8)
VARS = ("v4", "V1", "V2", "V2R", "V1R", "V1RS")
F0 = P.dims()["F"]


def size(var):
    if var == "v4":
        k = P.kass_dims()
        return k["cw"], k["L"]
    d = V.dims(var)
    return d["w"], d["depth"]


def top_led(var):
    """Kassettenoberkante und LED-Mitte über der Kassettenunterkante."""
    if var == "v4":
        t = V.base()["z_b"] + P.PODEST_T
        return t, t
    d = V.dims(var)
    return d["top"], d["z0"] + d["sh"] / 2


def slice_at(solid, z, fp):
    g = None
    for ring in solid.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return None if g is None else g.buffer(0).intersection(fp.buffer(0.01))


def roof_local(solid, fp, shaft):
    z, best = 0.5, 0.0
    while z < G.to_trimesh(solid).bounds[1][2]:
        u = slice_at(solid, z, fp)
        if u is None or u.is_empty or not u.buffer(1e-6).contains(shaft):
            break
        best, z = z, z + 0.5
    return best


def main():
    G.FAST = True
    models = G.source_models("laserscan", K)
    data = json.load(open(os.path.join(HERE, "data.json")))
    out = dict(scale=A.SCALE, F0=F0, deltas=DELTAS, stop=P.STOP_T, plate_t=P.dims()["plate_t"], vars={}, buildings={})
    for var in VARS:
        t, led = top_led(var)
        w, d = size(var)
        out["vars"][var] = dict(w=round(w, 2), d=round(d, 2), top=round(t, 2), led=round(led, 2),
                                led_over=round(led - F0, 2), top_over=round(t - F0, 2), need=round(t - F0 + P.STOP_T, 2))
    for slug, (solid, fp, _) in models.items():
        if slug.startswith("08"):
            continue
        p = data["buildings"][slug]["standard"]
        shaft = affinity.translate(affinity.rotate(box(-A.P.kass_dims()["cw"] / 2, -p["kl"] / 2, A.P.kass_dims()["cw"] / 2, p["kl"] / 2), p["angle"], origin=(0, 0)), p["cx"], p["cy"])
        row = dict(hmax=round(G.to_trimesh(solid).bounds[1][2], 1), roof=round(roof_local(solid, fp, shaft), 1), walls={})
        for var in VARS:
            a, b = size(var)
            a, b = a + 2 * FS.SHAFT_CLR, b + 2 * FS.SHAFT_CLR
            row["walls"][var] = {}
            for dl in DELTAS:
                t, _ = top_led(var)
                need = t - F0 - dl + P.STOP_T
                u = slice_at(solid, max(need - 0.2, 0.3), fp)
                w = None
                if u is not None and not u.is_empty:
                    w = FS.max_wall(u, a, b, wmax=3.0)
                row["walls"][var][str(dl)] = None if w is None else round(w, 1)
        row["roof_best"] = {}
        for var in VARS:                                   # höchste Dachhöhe, bei der der Schacht (Wand 0,8) noch in den Grundriss passt
            a, b = size(var)
            a, b = a + 2 * FS.SHAFT_CLR + 1.6, b + 2 * FS.SHAFT_CLR + 1.6
            lo, hi = 0.3, row["hmax"] - 0.2
            u = slice_at(solid, lo, fp)
            if FS.fit(u, a, b) is None:
                row["roof_best"][var] = None
                continue
            for _ in range(7):
                mid = (lo + hi) / 2
                u = slice_at(solid, mid, fp)
                if u is not None and not u.is_empty and FS.fit(u, a, b) is not None:
                    lo = mid
                else:
                    hi = mid
            row["roof_best"][var] = round(lo, 1)
        out["buildings"][slug] = row
        print(slug, row, flush=True)
    json.dump(out, open(os.path.join(HERE, "variants1250.json"), "w"))


if __name__ == "__main__":
    main()
