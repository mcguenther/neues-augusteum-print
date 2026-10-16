#!/usr/bin/env python3
"""Daten für die Platzierungs-App (plug/scale1176/placer.html): Umrisse, Höhenraster, Dock-Grundriss, Kassetten-Varianten, Startlagen.

Aufruf aus dem Wurzelverzeichnis: python3 -m plug.scale1176.app_data   (schreibt app_data.json, ca. 30 s)
"""
import base64
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import campus as C
from plug.scale1176 import variants1250 as W
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(__file__)
RES = 0.25       # mm je Rasterzelle
PAD = 1.5        # mm Rand um den Grundriss
VARS = ("v4", "V1", "V1R", "V1RS", "V2", "V2R")


def rings(g):
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in (g.geoms if hasattr(g, "geoms") else [g])]


def height_grid(solid, fp, hmax):
    minx, miny, maxx, maxy = fp.bounds
    minx, miny, maxx, maxy = minx - PAD, miny - PAD, maxx + PAD, maxy + PAD
    nx, ny = int(np.ceil((maxx - minx) / RES)), int(np.ceil((maxy - miny) / RES))
    h = np.zeros((ny, nx), np.uint8)
    z = 0.5
    while z < hmax:
        u = C.slice_poly(solid, z, fp)
        if u is None or u.is_empty:
            break
        im = Image.new("L", (nx, ny), 0)
        dr = ImageDraw.Draw(im)
        for p in (u.geoms if hasattr(u, "geoms") else [u]):
            if p.geom_type != "Polygon":
                continue
            dr.polygon([((x - minx) / RES, (maxy - y) / RES) for x, y in p.exterior.coords], fill=1)
            for r in p.interiors:
                dr.polygon([((x - minx) / RES, (maxy - y) / RES) for x, y in r.coords], fill=0)
        m = np.array(im, bool)
        h[m] = min(int(round(z * 2)), 255)
        z += 0.5
    return dict(minx=minx, maxy=maxy, nx=nx, ny=ny, res=RES, h=base64.b64encode(h.tobytes()).decode())


def main():
    G.FAST = True
    scale = P.SCALE_PLAN
    s = 1000.0 / scale
    models = G.source_models("laserscan", s)
    hof_fp = innenhof.flaeche_mm([v[1] for v in models.values()], s)
    d = P.dims_plan()
    cuts, env = C.dock_local("v4", 0.0, d)
    outline = G.plate_outline(unary_union([v[1] for v in models.values()] + [hof_fp]))
    vj = json.load(open(os.path.join(HERE, "variants1250.json")))["vars"]
    variants = {}
    for v in VARS:
        w, dep = C.shaft_size(v)
        lx, ly = C.led_local(v)
        yc = C.foot_local(v, 0.0).centroid.y
        variants[v] = dict(w=round(w, 3), d=round(dep, 3), led=[round(lx, 3), round(ly - yc, 3)], yc=round(yc, 3),
                           top=vj[v]["top"], ledz=vj[v]["led"], need0=vj[v]["need"])
    places = json.load(open(os.path.join(HERE, "placements_%d.json" % scale)))
    out = dict(scale=scale, F0=P.dims()["F"], stop=P.STOP_T, delta=P.MULDE_EXTRA_T, outline=rings(outline), hof=rings(hof_fp),
               dock=rings(env), variants=variants, buildings={})
    names = {b["slug"]: b["title"] for b in G.OBJEKTE}
    for slug in P.CASSETTE:
        solid, fp, _ = models[slug]
        hmax = float(G.to_trimesh(solid).bounds[1][2])
        yc = C.foot_local(P.CASSETTE[slug], 0.0).centroid.y
        tg = C.target_point(fp)
        p = places[slug]
        out["buildings"][slug] = dict(name=names[slug], fp=rings(fp), hmax=round(hmax, 2), target=[round(tg.x, 3), round(tg.y, 3)],
                                      grid=height_grid(solid, fp, hmax),
                                      start=dict(var=p["var"], cx=round(p["cx"], 3), cy=round(p["cy"], 3), angle=p["angle"]))
        print(slug, hmax, flush=True)
    json.dump(out, open(os.path.join(HERE, "app_data.json"), "w"), separators=(",", ":"))
    print("app_data.json: %.0f kB" % (os.path.getsize(os.path.join(HERE, "app_data.json")) / 1000))


if __name__ == "__main__":
    main()
