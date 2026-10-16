#!/usr/bin/env python3
"""Steckplatte des Campus: Grundplatte mit Umriss-Aussparung (4 mm), Fuß-Mulde und Dock (Winkelleiste) je Gebäude und Aussparung für den Innenhof-Einsatz.

Festlegung (plug/logbook/scale.md): Maßstab 1:1300, Mulde überall 4 mm tiefer (F 14,2, Platte 20,2 mm), Kassette je Gebäude aus
params.CASSETTE (v4, V1RS, V2R). Die Lage der Mulde im Grundriss wird gesucht (Rechteck um den Schacht, beliebige Drehung, höchste Dachhöhe
bei mindestens 0,8 mm Wand, bevorzugt 1,2 mm) und in plug/scale1176/placements_<N>.json zwischengespeichert.

Aufruf (aus dem Wurzelverzeichnis):
    python3 -m plug.campus [--scale 1300] [--replace]    # STL nach stl/steckmodul_campus/, Bilder nach vorschau/steckmodul_campus/
Die Gebäude selbst (Fuß mit Schacht, Hohlkörper) sind noch nicht Teil davon (To-do, siehe plug/logbook/next.md).
"""
import argparse
import json
import math
import os

import manifold3d as m3d
import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import dupont as sd
from plug import institute as I
from plug.geom import diff, ext, to_tm, union
from plug.scale1176 import variants1250 as W
from plug.testcase import build as TB
from plug.testcase import fit_study as FS
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "stl", "steckmodul_campus")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus")
CACHE = os.path.join(HERE, "plug", "scale1176", "placements_%d.json")
WALL_PREF = (1.2, 0.8)          # Wand um den Schacht: bevorzugt, Mindestmaß


def shaft_size(var):
    """Schacht (Breite in x, Tiefe in y) der Kassette mit Spiel."""
    if var == "v4":
        k = P.kass_dims()
        w, d = k["cw"], k["L"]
    else:
        v = V.dims(var)
        w, d = v["w"], v["depth"]
    return w + 2 * P.KASS_CLR_T, d + 2 * P.KASS_CLR_T


def foot_local(var, wall):
    """Fuß (Schacht plus Wand) im Gebäudesystem: Pin-Reihe bei y = 0, Kassette ab y_kass0; Rechteck."""
    d = P.dims_plan()
    w, dep = shaft_size(var)
    y0 = d["y_kass0"] - P.KASS_CLR_T
    return sbox(-w / 2 - wall, y0 - wall, w / 2 + wall, y0 + dep + wall)


def slice_poly(solid, z, fp):
    g = None
    for ring in solid.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return None if g is None else g.buffer(0).intersection(fp.buffer(0.01))


def place_all(models, scale, replace=False):
    path = CACHE % scale
    if os.path.exists(path) and not replace:
        return json.load(open(path))
    F0, dl = P.dims()["F"], P.MULDE_EXTRA_T
    res = {}
    for slug, (solid, fp, _) in models.items():
        if slug not in P.CASSETTE:
            continue
        var = P.CASSETTE[slug]
        t, _led = W.top_led(var)
        need = t - F0 - dl + P.STOP_T                       # Mindesthöhe des Gebäudes über der Platte
        w, dep = shaft_size(var)
        hmax = float(G.to_trimesh(solid).bounds[1][2])
        best = None
        for wall in WALL_PREF:
            A, B = w + 2 * wall, dep + 2 * wall
            lo = max(need - 0.2, 0.3)
            u = slice_poly(solid, lo, fp)
            if u is None or u.is_empty or FS.fit(u, A, B) is None:
                continue
            hi = hmax - 0.2
            for _ in range(7):                              # höchste Dachhöhe, bei der der Schacht noch passt
                mid = (lo + hi) / 2
                um = slice_poly(solid, mid, fp)
                if um is not None and not um.is_empty and FS.fit(um, A, B) is not None:
                    lo = mid
                else:
                    hi = mid
            pos = FS.fit(slice_poly(solid, lo, fp), A, B)
            best = dict(var=var, wall=wall, cx=pos[0], cy=pos[1], angle=pos[2], roof=round(lo, 1), need=round(need, 2))
            break
        if best is None:
            raise SystemExit("%s: kein Platz für %s (Wand %.1f)" % (slug, var, WALL_PREF[-1]))
        res[slug] = best
        print("  %-22s %-5s Wand %.1f, Dach %.1f (nötig %.1f)" % (slug, var, best["wall"], best["roof"], best["need"]), flush=True)
    json.dump(res, open(path, "w"), indent=1)
    return res


def local_cuts(var, wall, d):
    """Fuß-Mulde (getestete Tiefe 10,2, um die Umrisstiefe nach unten verschoben) und Dock im Gebäudesystem (z = 0 Plattenoberseite)."""
    cs = I.hcs(foot_local(var, wall))
    old = sd.CLR
    sd.CLR = P.MULDE_CLR_T
    try:
        mulde = [c.translate([0.0, 0.0, -P.MULDE_EXTRA_T]) for c in I.pocket_cuts(cs, P.dims()["F"])]
    finally:
        sd.CLR = old
    return mulde + TB.dock_cuts_b(d)


def to_world(man, p, yc, flip):
    return man.translate([0.0, -yc, 0.0]).rotate([0.0, 0.0, p["angle"] + flip]).translate([p["cx"], p["cy"], 0.0])


def envelope(cuts, p, yc, flip):
    """Grundriss aller Hohlräume (shapely) in Weltlage."""
    cs = union(cuts).project()
    poly = unary_union([Polygon(r) for r in cs.to_polygons()])
    poly = affinity.translate(poly, 0.0, -yc)
    poly = affinity.rotate(poly, p["angle"] + flip, origin=(0, 0))
    return affinity.translate(poly, p["cx"], p["cy"])


def build(scale=P.SCALE_PLAN, replace=False):
    s = 1000.0 / scale
    G.FAST = True
    models = G.source_models("laserscan", s)
    models[G.HOF["slug"]] = innenhof.model(s, [v[1] for v in models.values()], P.HOF_DEPTH_T, P.HOF_CLR_T)
    places = place_all({k: v for k, v in models.items() if k in P.CASSETTE}, scale, replace)
    d = P.dims_plan()
    T = d["plate_t"]
    fps = {k: v[1] for k, v in models.items()}
    outline = G.plate_outline(unary_union(list(fps.values())))
    hof_solid = models[G.HOF["slug"]][0]
    plate = G.extrude(outline, 0.0, T)
    plate = G.engrave_labels(plate, outline, scale, "Campus Augustusplatz · Universität Leipzig", T, "laserscan")
    # Hohlräume je Gebäude; Spiegelung (180°) so, dass die Löträume möglichst frei und innerhalb der Platte bleiben
    others = []
    cut_all, report = [], []
    for slug, p in places.items():
        wall = p["wall"]
        cuts = local_cuts(p["var"], wall, d)
        yc = foot_local(p["var"], wall).centroid.y
        best = None
        for flip in (0.0, 180.0):
            env = envelope(cuts, p, yc, flip)
            bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in others)
            if best is None or bad < best[0]:
                best = (bad, flip, env)
        bad, flip, env = best
        others.append(env)
        report.append((slug, p["var"], wall, flip, bad))
        for c in cuts:
            cut_all.append(to_world(c, p, yc, flip).translate([0, 0, T]))
    # Hof-Aussparung: HOF_DEPTH_T tief, Einsatz mit Fuge HOF_CLR_T und Einführfase unten (innenhof.model); ohne Fase oben, damit die Wand
    # zu den Umriss-Aussparungen der Gebäude 0,4 mm bleibt
    hof = innenhof.flaeche_mm([v[1] for k, v in models.items() if k in P.CASSETTE], s)
    cut_all.append(G.extrude(hof, T - P.HOF_DEPTH_T, T + 0.01))
    # Umriss-Aussparungen der Gebäude, MULDE_EXTRA_T tief: auf der Platte sind die Umrisse erkennbar, der Gebäudekörper reicht so weit hinein
    for slug in P.CASSETTE:
        cut_all.append(G.extrude(fps[slug].buffer(P.OUTLINE_CLR_T, join_style=2), T - P.MULDE_EXTRA_T, T + 0.01))
    plate = diff(plate, *cut_all)
    return plate, report, models, places, outline, hof_solid


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("--replace", action="store_true", help="Lage der Mulden neu suchen")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    plate, report, models, places, outline, hof_solid = build(a.scale, a.replace)
    tm = to_tm(plate)
    path = os.path.join(OUT, "steckplatte_1zu%d.stl" % a.scale)
    tm.export(path)
    b = outline.bounds
    print("Platte %.1f × %.1f × %.1f mm, dicht=%s, Mulde %.1f, Plattendicke %.1f" % (
        b[2] - b[0], b[3] - b[1], P.dims_plan()["plate_t"], tm.is_watertight, P.dims_plan()["F"], P.dims_plan()["plate_t"]))
    hof_tm = to_tm(hof_solid)
    hof_path = os.path.join(OUT, "hof_einsatz_1zu%d.stl" % a.scale)
    hof_tm.export(hof_path)
    print("Hof-Einsatz %.1f × %.1f × %.1f mm, dicht=%s, %.1f mm unter der Oberfläche" % (*hof_tm.extents, hof_tm.is_watertight, P.HOF_DEPTH_T))
    ok = tm.is_watertight and hof_tm.is_watertight
    for slug, var, wall, flip, bad in report:
        print("  %-22s %-5s Wand %.1f, Dock-Drehung %d°, Überlappung/außerhalb %.2f mm²" % (slug, var, wall, flip, bad))
        ok &= bad < 0.05
    print("keine Kollisionen" if ok else "ACHTUNG: Kollision oder Hohlraum außerhalb der Platte")
    import preview
    preview.render([(tm, "#9aa7b4")], size=(1000, 1300), azim=-90, elev=89).save(os.path.join(PREV, "steckplatte_1zu%d_oben.png" % a.scale))
    preview.render([(tm, "#9aa7b4")], size=(1100, 900), azim=-50, elev=35).save(os.path.join(PREV, "steckplatte_1zu%d_schraeg.png" % a.scale))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
