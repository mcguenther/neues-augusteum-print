#!/usr/bin/env python3
"""Lagen aus der Platzierungs-App (placements_user_1300.json) minimal anpassen, bis die Wand um den Schacht mindestens WALL_TARGET beträgt.

Prüft wie die App: Wand = Abstand des Schachtrechtecks zum Rand des nutzbaren Gebäudeschnitts (Höhe mindestens die nötige), Dock innerhalb der Platte
(1 mm Rand) und ohne Überlappung mit anderen Docks. Sucht kleinste Verschiebung (bis 0,8 mm) und Drehung (bis 3°); alles, was schon passt, bleibt unverändert.
Schreibt placements_1300.json und die Gegenüberstellung nudge_diff.json. Aufruf aus dem Wurzelverzeichnis: python3 -m plug.scale1176.nudge
"""
import json
import math
import os

from shapely import affinity
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import campus as C
from plug.scale1176 import variants1250 as W
from plug.testcase import params as P

HERE = os.path.dirname(__file__)
WALL_TARGET = 1.2
MAX_SHIFT, MAX_ROT = 0.8, 3.0


def rect_of(p, w, d):
    return affinity.translate(affinity.rotate(sbox(-w / 2, -d / 2, w / 2, d / 2), p["angle"], origin=(0, 0)), p["cx"], p["cy"])


def main():
    G.FAST = True
    scale = P.SCALE_PLAN
    s = 1000.0 / scale
    models = G.source_models("laserscan", s)
    hof = innenhof.flaeche_mm([v[1] for v in models.values()], s)
    outline = G.plate_outline(unary_union([v[1] for v in models.values()] + [hof]))
    user = json.load(open(os.path.join(HERE, "placements_user_1300.json")))
    F0, dl = P.dims()["F"], P.MULDE_EXTRA_T
    d = P.dims_plan()
    envs_local = C.dock_local("v4", 0.0, d)[1]
    info = {}
    for slug, p in user.items():
        solid, fp, _ = models[slug]
        t, _ = W.top_led(p["var"])
        need = t - F0 - dl + P.STOP_T
        u = C.slice_poly(solid, max(need - 0.2, 0.3), fp)
        w, dep = C.shaft_size(p["var"])
        yc = C.foot_local(p["var"], 0.0).centroid.y
        info[slug] = dict(u=u, w=w, d=dep, yc=yc, need=need, var=p["var"])

    def wall(slug, p):
        i = info[slug]
        r = rect_of(p, i["w"], i["d"])
        if not i["u"].buffer(1e-6).contains(r):
            return 0.0
        return i["u"].exterior.distance(r) if i["u"].geom_type == "Polygon" else i["u"].boundary.distance(r)

    def dock(slug, p):
        i = info[slug]
        return affinity.translate(affinity.rotate(affinity.translate(envs_local, 0, -i["yc"]), p["angle"], origin=(0, 0)), p["cx"], p["cy"])

    new, diff = {}, {}
    for slug, p in user.items():
        p0 = dict(p)
        w0 = wall(slug, p0)
        best = p0
        if w0 < WALL_TARGET:
            cand = []
            for ang in [p0["angle"] + a * 0.5 for a in range(-int(MAX_ROT * 2), int(MAX_ROT * 2) + 1)]:
                for dx in [x * 0.1 for x in range(-8, 9)]:
                    for dy in [y * 0.1 for y in range(-8, 9)]:
                        q = dict(p0, cx=p0["cx"] + dx, cy=p0["cy"] + dy, angle=ang)
                        sh = math.hypot(dx, dy)
                        if sh > MAX_SHIFT:
                            continue
                        w1 = wall(slug, q)
                        if w1 >= WALL_TARGET:
                            cand.append((sh + 0.15 * abs(ang - p0["angle"]), q, w1))
            cand.sort(key=lambda c: c[0])
            for cost, q, w1 in cand:
                env = dock(slug, q)
                if env.difference(outline.buffer(-1.0)).area > 0.01:
                    continue
                if any(env.intersection(dock(o, new.get(o, user[o]))).area > 0.01 for o in user if o != slug and o in new):
                    continue
                best = q
                break
            else:
                print("ACHTUNG: %s: keine passende kleine Anpassung" % slug)
        wn = wall(slug, best)
        new[slug] = dict(var=best["var"], wall=round(wn, 1), cx=round(best["cx"], 3), cy=round(best["cy"], 3), angle=round(best["angle"], 1))
        diff[slug] = dict(old=dict(cx=p0["cx"], cy=p0["cy"], angle=p0["angle"], wall=round(w0, 2)), new=dict(cx=best["cx"], cy=best["cy"], angle=best["angle"], wall=round(wn, 2)))
        print("%-22s Wand %.2f -> %.2f   dx %+.2f dy %+.2f dθ %+.1f°" % (slug, w0, wn, best["cx"] - p0["cx"], best["cy"] - p0["cy"], best["angle"] - p0["angle"]))
    # alle Docks gegeneinander
    keys = list(new)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ov = dock(a, new[a]).intersection(dock(b, new[b])).area
            if ov > 0.01:
                print("ACHTUNG: Dock %s und %s überlappen (%.2f mm²)" % (a, b, ov))
    for slug in keys:
        if dock(slug, new[slug]).difference(outline.buffer(-1.0)).area > 0.01:
            print("ACHTUNG: Dock %s reicht an den Plattenrand" % slug)
    json.dump(new, open(os.path.join(HERE, "placements_%d.json" % scale), "w"), indent=1)
    json.dump(diff, open(os.path.join(HERE, "nudge_diff.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
