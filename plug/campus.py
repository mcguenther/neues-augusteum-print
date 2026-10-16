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


def led_local(var):
    """Lage der LED im Gebäudesystem (x, y; Pin-Reihe bei y = 0): v4 Mitte der LED-Auflage, V-Varianten Chip auf dem Blatt (R-Varianten zwischen beiden)."""
    y0 = P.dims()["y_kass0"]
    if var == "v4":
        k = P.kass_dims()
        return 0.0, y0 + (k["seat0"] + k["seat1"]) / 2
    d = V.dims(var)
    y = d["yb"] + V.BLATT_T / 2 if var in V.RVARS else d["y_face"] + 0.95
    return d["x_off"], y0 + y


def candidates(poly, A, B, off, target, astep=5, gstep=0.5, keep=400):
    """Alle Lagen des Rechtecks A × B (Drehung 0 bis 355°) im Polygon, sortiert nach dem Abstand der LED (Versatz off zur Rechteckmitte) vom Ziel."""
    import shapely
    er = poly.buffer(-min(A, B) / 2)
    if er.is_empty:
        return []
    x0, y0, x1, y1 = er.bounds
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-9, gstep), np.arange(y0, y1 + 1e-9, gstep))
    X, Y = X.ravel(), Y.ravel()
    ins = shapely.contains_xy(er, X, Y)
    X, Y = X[ins], Y[ins]
    shapely.prepare(poly)
    corners = np.array([[-A / 2, -B / 2], [A / 2, -B / 2], [A / 2, B / 2], [-A / 2, B / 2], [-A / 2, -B / 2]])
    out = []
    for ang in range(0, 360, astep):
        a = math.radians(ang)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        coords = np.stack([X[:, None] + (corners @ rot.T)[None, :, 0], Y[:, None] + (corners @ rot.T)[None, :, 1]], axis=2)
        ok = shapely.contains(poly, shapely.polygons(coords))
        if ok.any():
            lx, ly = rot @ np.asarray(off)
            dist = np.hypot(X[ok] + lx - target.x, Y[ok] + ly - target.y)
            out += [(float(dd), ang, float(xx), float(yy)) for dd, xx, yy in zip(dist, X[ok], Y[ok])]
    out.sort()
    return out[:keep]


def roof_local(solid, fp, rect_poly, hmax):
    """Dachhöhe über dem Schacht: größte Höhe, bei der das Schachtrechteck noch im Querschnitt des Gebäudes liegt."""
    z, best = 0.5, 0.0
    while z < hmax:
        u = slice_poly(solid, z, fp)
        if u is None or u.is_empty or not u.buffer(1e-6).contains(rect_poly):
            break
        best, z = z, z + 0.5
    return best


def place_all(models, scale, outline, replace=False):
    """Lage je Gebäude: die LED möglichst nahe der Gebäudemitte (Schwerpunkt), Schacht mit Wand 1,2 (sonst 0,8) im Gebäude an einer Stelle,
    die hoch genug ist; Dock und Lötraum innerhalb der Platte und ohne Überlappung mit anderen Docks."""
    path = CACHE % scale
    if os.path.exists(path) and not replace:
        return json.load(open(path))
    F0, dl = P.dims()["F"], P.MULDE_EXTRA_T
    d = P.dims_plan()
    res, others = {}, []
    for slug, (solid, fp, _) in models.items():
        if slug not in P.CASSETTE:
            continue
        var = P.CASSETTE[slug]
        t, led_h = W.top_led(var)
        need = t - F0 - dl + P.STOP_T                       # Mindesthöhe des Gebäudes über der Platte
        w, dep = shaft_size(var)
        hmax = float(G.to_trimesh(solid).bounds[1][2])
        u = slice_poly(solid, max(need - 0.2, 0.3), fp)
        target = fp.centroid if fp.buffer(-1.0).contains(fp.centroid) else fp.representative_point()
        lx, ly = led_local(var)
        best = None
        for wall in WALL_PREF:
            A, B = w + 2 * wall, dep + 2 * wall
            yc = foot_local(var, wall).centroid.y
            cuts = local_cuts(var, wall, d)
            env0 = unary_union([Polygon(r) for r in union(cuts).project().to_polygons()])
            for dist, ang, cx, cy in candidates(u, A, B, (lx, ly - yc), target):
                p = dict(var=var, wall=wall, cx=cx, cy=cy, angle=ang)
                env = affinity.translate(affinity.rotate(affinity.translate(env0, 0.0, -yc), ang, origin=(0, 0)), cx, cy)
                bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in others)
                if bad < 0.05:
                    shaft = affinity.translate(affinity.rotate(sbox(-w / 2, -dep / 2, w / 2, dep / 2), ang, origin=(0, 0)), cx, cy)
                    roof = roof_local(solid, fp, shaft, hmax)
                    p.update(dist=round(dist, 1), roof=round(roof, 1), need=round(need, 2), luft=round(roof - (led_h - F0 - dl), 1))
                    best = (p, env)
                    break
            if best:
                break
        if best is None:
            raise SystemExit("%s: kein Platz für %s (Wand %.1f)" % (slug, var, WALL_PREF[-1]))
        res[slug] = best[0]
        others.append(best[1])
        print("  %-22s %-5s Wand %.1f, LED %.1f mm von der Gebäudemitte, Dach %.1f, Luft %.1f" % (
            slug, var, best[0]["wall"], best[0]["dist"], best[0]["roof"], best[0]["luft"]), flush=True)
    json.dump(res, open(path, "w"), indent=1)
    return res


def local_cuts(var, wall, d):
    """Fuß-Mulde (gerade Wände, Spiel MULDE_CLR_T, 45°-Fase oben, Tiefe F − MULDE_EXTRA_T = 10,2, um die Umrisstiefe nach unten verschoben)
    und Dock im Gebäudesystem (z = 0 Plattenoberseite). Keine Stufen in der Mulde."""
    cs = I.rounded(I.hcs(foot_local(var, wall)))
    ex, ch, clr = P.MULDE_EXTRA_T, P.MULDE_CH_T, P.MULDE_CLR_T
    zt = -ex
    body = ext(cs.offset(clr, m3d.JoinType.Round), -d["F"], zt - ch + 0.01)
    fase = m3d.Manifold.batch_hull([ext(cs.offset(clr, m3d.JoinType.Round), zt - ch, zt - ch + 0.01),
                                    ext(cs.offset(clr + ch, m3d.JoinType.Round), zt - 0.01, zt + 0.01)])
    return [body, fase] + TB.dock_cuts_b(d)


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
    fps = {k: v[1] for k, v in models.items()}
    outline = G.plate_outline(unary_union(list(fps.values())))
    places = place_all({k: v for k, v in models.items() if k in P.CASSETTE}, scale, outline, replace)
    d = P.dims_plan()
    T = d["plate_t"]
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
        for flip in (0.0,):                      # die Drehung 0 bis 355° steckt im Winkel; die LED-Lage hängt daran
            env = envelope(cuts, p, yc, flip)
            bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in others)
            if best is None or bad < best[0]:
                best = (bad, flip, env)
        bad, flip, env = best
        others.append(env)
        report.append((slug, p["var"], wall, flip, bad))
        clip = G.extrude(fps[slug].buffer(P.OUTLINE_CLR_T, join_style=2), T - d["F"] - 1.0, T + 1.0)
        for i, c in enumerate(cuts):
            w = to_world(c, p, yc, flip).translate([0, 0, T])
            cut_all.append(w ^ clip if i < 2 else w)              # Mulde und Fase nicht über die Umriss-Aussparung hinaus
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
