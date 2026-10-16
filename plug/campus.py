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
import shapely
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


def led_local(var):
    """LED (Mitte) im Gebäudesystem (Pin-Reihe y = 0): (x, y). Bei zwei LEDs (V2R, V1RS) die Mitte zwischen beiden."""
    d = P.dims()
    if var == "v4":
        k = P.kass_dims()
        return 0.0, (k["seat0"] + k["seat1"]) / 2 + d["y_kass0"]
    v = V.dims(var)
    yf = v["y_face"] + 0.95
    if var in V.RVARS:
        yf = (yf + v["yb_back"] + V.FPC + 0.95) / 2
    return v["x_off"], yf + d["y_kass0"]


def foot_local(var, wall):
    """Schacht plus Wand im Gebäudesystem (Pin-Reihe bei y = 0); Rechteck. Nur für die Wandprüfung und die Lage."""
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


def target_point(fp):
    """Mitte der Grundfläche: Schwerpunkt, sonst (liegt er außerhalb) die Stelle mit dem größten Abstand zum Rand."""
    c = fp.centroid
    if fp.contains(c):
        return c
    from shapely.ops import polylabel
    big = max(fp.geoms, key=lambda g: g.area) if hasattr(fp, "geoms") else fp
    return polylabel(big, 0.1)


def candidates(u, A, B, led_dxy, tgt, astep=5, gstep=0.5):
    """Alle Lagen des Rechtecks A × B (Drehung 0 bis 355°) im Polygon u, sortiert nach Abstand der LED zur Zielmitte.
    led_dxy: LED relativ zur Rechteckmitte (x quer, y längs). Liefert Liste (Abstand, Winkel, cx, cy)."""
    r = min(A, B) / 2
    er = u.buffer(-r)
    if er.is_empty:
        return []
    x0, y0, x1, y1 = er.bounds
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-9, gstep), np.arange(y0, y1 + 1e-9, gstep))
    X, Y = X.ravel(), Y.ravel()
    ins = shapely.contains_xy(er, X, Y)
    X, Y = X[ins], Y[ins]
    shapely.prepare(u)
    corners = np.array([[-A / 2, -B / 2], [A / 2, -B / 2], [A / 2, B / 2], [-A / 2, B / 2], [-A / 2, -B / 2]])
    out = []
    for ang in range(0, 360, astep):
        a = math.radians(ang)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        off = corners @ rot.T
        coords = np.stack([X[:, None] + off[None, :, 0], Y[:, None] + off[None, :, 1]], axis=2)
        ok = shapely.contains(u, shapely.polygons(coords))
        if ok.any():
            lx, ly = rot @ np.array(led_dxy)
            dist = np.hypot(X[ok] + lx - tgt.x, Y[ok] + ly - tgt.y)
            out += list(zip(dist.tolist(), [ang] * int(ok.sum()), X[ok].tolist(), Y[ok].tolist()))
    out.sort()
    return out


def roof_over(solid, fp, rect, hmax):
    """Dachhöhe über dem Schacht: größte Höhe, bei der das Rechteck noch ganz im Gebäudeschnitt liegt."""
    lo, hi = 0.3, hmax - 0.2
    for _ in range(8):
        mid = (lo + hi) / 2
        u = slice_poly(solid, mid, fp)
        if u is not None and not u.is_empty and u.buffer(1e-6).contains(rect):
            lo = mid
        else:
            hi = mid
    return lo


def mulde_body(slug_fp, d):
    """Mulde: der volle Gebäudeumriss, durchgehend bis zur Fußunterkante (eine Ebene, keine Stufen)."""
    return G.extrude(slug_fp.buffer(P.OUTLINE_CLR_T, join_style=2), -d["F"] - 0.0, 0.01)


def dock_local(var, wall, d):
    """Dock (Winkelleiste, Lötraum, Kabelraum) im Gebäudesystem und sein Grundriss (shapely)."""
    cuts = TB.dock_cuts_b(d)
    cs = union(cuts).project()
    env = unary_union([Polygon(r) for r in cs.to_polygons()])
    return cuts, env


def place_all(models, scale, replace=False):
    path = CACHE % scale
    if os.path.exists(path) and not replace:
        return json.load(open(path))
    F0, dl = P.dims()["F"], P.MULDE_EXTRA_T
    d = P.dims_plan()
    res, placed_env = {}, []
    order = ["06_city_hochhaus", "05_institutsgebaeude", "04_seminargebaeude", "01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude"]
    for slug in order:
        solid, fp, _ = models[slug]
        var = P.CASSETTE[slug]
        t, _led = W.top_led(var)
        need = t - F0 - dl + P.STOP_T                       # Mindesthöhe des Gebäudes über der Platte
        w, dep = shaft_size(var)
        hmax = float(G.to_trimesh(solid).bounds[1][2])
        lx, ly = led_local(var)
        yc = foot_local(var, 0.0).centroid.y
        led_dxy = (lx, ly - yc)
        tgt = target_point(fp)
        _, env_local = dock_local(var, 0.0, d)
        best = None
        for wall in WALL_PREF:
            z_use = max(need - 0.2, 0.3)
            if slug in PREFER_ROOF:                         # höchste Dachhöhe, bei der der Schacht noch passt, dann dort möglichst mittig
                lo, hi = z_use, hmax - 0.2
                for _ in range(7):
                    mid = (lo + hi) / 2
                    um = slice_poly(solid, mid, fp)
                    if um is not None and not um.is_empty and FS.fit(um, w + 2 * wall, dep + 2 * wall) is not None:
                        lo = mid
                    else:
                        hi = mid
                z_use = lo - 0.3
            u = slice_poly(solid, z_use, fp)
            if u is None or u.is_empty:
                continue
            cand = candidates(u, w + 2 * wall, dep + 2 * wall, led_dxy, tgt)
            for dist, ang, cx, cy in cand[:4000]:
                env = affinity.translate(affinity.rotate(affinity.translate(env_local, 0, -yc), ang, origin=(0, 0)), cx, cy)
                if not outline_ok(env) or any(env.intersection(o).area > 0.01 for o in placed_env):
                    continue
                best = dict(var=var, wall=wall, cx=cx, cy=cy, angle=ang, led_dist=round(dist, 1))
                rect = affinity.translate(affinity.rotate(sbox(-w / 2, -dep / 2, w / 2, dep / 2), ang, origin=(0, 0)), cx, cy)
                best["roof"] = round(roof_over(solid, fp, rect, hmax), 1)
                best["need"] = round(need, 2)
                placed_env.append(env)
                break
            if best:
                break
        if best is None:
            raise SystemExit("%s: kein Platz für %s (Wand %.1f)" % (slug, var, WALL_PREF[-1]))
        res[slug] = best
        print("  %-22s %-5s Wand %.1f, LED %.1f mm von der Mitte, Dach %.1f (nötig %.1f)" % (
            slug, var, best["wall"], best["led_dist"], best["roof"], best["need"]), flush=True)
    json.dump(res, open(path, "w"), indent=1)
    return res


OUTLINE = None
# Gebäude, bei denen die LED unter dem hohen Dach sitzen soll statt exakt mittig (Nutzer: Neues Augusteum)
PREFER_ROOF = {"02_neues_augusteum"}


def outline_ok(env):
    return OUTLINE is None or env.within(OUTLINE.buffer(-1.0))


def build(scale=P.SCALE_PLAN, replace=False):
    global OUTLINE
    s = 1000.0 / scale
    G.FAST = True
    models = G.source_models("laserscan", s)
    models[G.HOF["slug"]] = innenhof.model(s, [v[1] for v in models.values()], P.HOF_DEPTH_T, P.HOF_CLR_T)
    fps = {k: v[1] for k, v in models.items()}
    outline = G.plate_outline(unary_union(list(fps.values())))
    OUTLINE = outline
    places = place_all({k: v for k, v in models.items() if k in P.CASSETTE}, scale, replace)
    d = P.dims_plan()
    T = d["plate_t"]
    hof_solid = models[G.HOF["slug"]][0]
    plate = G.extrude(outline, 0.0, T)
    plate = G.engrave_labels(plate, outline, scale, "Campus Augustusplatz · Universität Leipzig", T, "laserscan")
    cut_all, report, envs = [], [], []
    for slug, p in places.items():
        w, dep = shaft_size(p["var"])
        yc = foot_local(p["var"], 0.0).centroid.y
        cuts, env_local = dock_local(p["var"], p["wall"], d)
        for c in cuts:
            cut_all.append(c.translate([0.0, -yc, 0.0]).rotate([0.0, 0.0, p["angle"]]).translate([p["cx"], p["cy"], T]))
        env = affinity.translate(affinity.rotate(affinity.translate(env_local, 0, -yc), p["angle"], origin=(0, 0)), p["cx"], p["cy"])
        bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in envs)
        envs.append(env)
        report.append((slug, p["var"], p["wall"], p.get("led_dist", 0.0), bad))
        # Mulde: voller Gebäudeumriss, durchgehend bis zur Fußunterkante
        cut_all.append(mulde_body(fps[slug], d).translate([0, 0, T]))
        # Muldenboden bleibt 0,4 mm; Pin-Löcher kommen aus dock_cuts_b
    # Hof-Aussparung: HOF_DEPTH_T tief, Einsatz mit Fuge HOF_CLR_T und Einführfase unten (innenhof.model); ohne Fase oben, damit die Wand
    # zu den Gebäude-Aussparungen 0,4 mm bleibt
    hof = innenhof.flaeche_mm([v[1] for k, v in models.items() if k in P.CASSETTE], s)
    cut_all.append(G.extrude(hof, T - P.HOF_DEPTH_T, T + 0.01))
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
        print("  %-22s %-5s Wand %.1f, LED %.1f mm von der Mitte, Dock außerhalb/überlappt %.2f mm²" % (slug, var, wall, flip, bad))
        ok &= bad < 0.05
    print("keine Kollisionen" if ok else "ACHTUNG: Kollision oder Hohlraum außerhalb der Platte")
    import preview
    preview.render([(tm, "#9aa7b4")], size=(1000, 1300), azim=-90, elev=89).save(os.path.join(PREV, "steckplatte_1zu%d_oben.png" % a.scale))
    preview.render([(tm, "#9aa7b4")], size=(1100, 900), azim=-50, elev=35).save(os.path.join(PREV, "steckplatte_1zu%d_schraeg.png" % a.scale))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
