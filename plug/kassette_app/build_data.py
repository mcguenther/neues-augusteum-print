#!/usr/bin/env python3
"""Daten für die Kassetten-App Neues Augusteum (plug/kassette_app/app.html): Platte, Gebäude, Höhenraster des Augusteums, Docks,
Batteriefach (Powerbank, Kanal, Stecker, Elektronik, Schalter, Knopf und Kordelgänge Stand 8) und die Stützenraster des Unterkastens.

Alles in Plattenkoordinaten (x Osten, y Norden, Ursprung Südwestecke des Unterkastens, wie plug/power/batteriefach.html).
Aufruf aus dem Wurzelverzeichnis: python3 -m plug.kassette_app.build_data   (ca. 40 s, schreibt data.json)
"""
import json
import math
import os
import sys

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
from plug import campus as C  # noqa: E402
from plug.power import build_batteriefach as BF  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.power import kasten8 as K8  # noqa: E402
from plug.power import params as PP  # noqa: E402
from plug.scale1176 import app_data as AD  # noqa: E402
from plug.scale1176 import variants1250 as W  # noqa: E402
from plug.testcase import params as TP  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "02_neues_augusteum"
VARS = ("v4", "V1", "V1R", "V1RS", "V2", "V2R")


def rings(g, sh=(0.0, 0.0), nd=2):
    return [[[round(x + sh[0], nd), round(y + sh[1], nd)] for x, y in p.exterior.coords] for p in (g.geoms if hasattr(g, "geoms") else [g])]


def poly(rs):
    return unary_union([Polygon(r) for r in rs])


def main():
    v = BF.final_variant()
    v.pop("meshes")
    sh = BC.LAST["sh"]
    W_, L_ = v["plate"]
    print("Platte %.1f × %.1f, Verschiebung Welt -> Platte (%.3f | %.3f)" % (W_, L_, sh[0], sh[1]), flush=True)

    # Gebäude in der Lage auf der Platte (wie im Unterkasten-Lauf), Höhenraster des Augusteums
    G.FAST = True
    scale = 1300
    models = C.models_platte(1000.0 / scale, scale)
    solid, fp, _ = models[SLUG]
    hmax = float(G.to_trimesh(solid).bounds[1][2])
    grid = AD.height_grid(solid, fp, hmax)
    grid["minx"] = round(grid["minx"] + sh[0], 3)
    grid["maxy"] = round(grid["maxy"] + sh[1], 3)
    tg = C.target_point(fp)
    shift = C.SHIFTS.get(SLUG, (0.0, 0.0))

    # Startlage: placements_1300.json (Weltlage) + Verschiebung der Naht + Verschiebung in die Plattenkoordinaten
    places = json.load(open(C.CACHE % scale))
    pl = places[SLUG]
    start = dict(var=pl["var"], cx=round(pl["cx"] + shift[0] + sh[0], 3), cy=round(pl["cy"] + shift[1] + sh[1], 3), angle=pl["angle"])
    to_welt = [round(shift[0] + sh[0], 4), round(shift[1] + sh[1], 4)]

    # Kassetten-Varianten
    variants = {}
    for var in VARS:
        w, dep = C.shaft_size(var)
        lx, ly = C.led_local(var)
        yc = C.foot_local(var, 0.0).centroid.y
        top, ledz = W.top_led(var)
        variants[var] = dict(w=round(w, 3), d=round(dep, 3), led=[round(lx, 3), round(ly - yc, 3)], yc=round(yc, 3), top=round(top, 3), ledz=round(ledz, 3))

    # Dock im Gebäudesystem (Ursprung der Pin-Reihe, y nach vorn)
    dk = BC.DK
    zone_l = BC.dock_zone(dk)
    body_l = box(-dk["hw"], dk["y_slot"], dk["hw"], dk["yb"] + dk["hd"])
    env_l = C.dock_local("v4", 0.0, TP.dims_plan())[1]

    def welt(g, phi, p):
        return affinity.translate(affinity.rotate(g, phi, origin=(0, 0)), p[0], p[1])

    others = []
    for d in v["docks"]:
        if d["slug"] == SLUG or not d["ok"]:
            continue
        env = welt(env_l, d["phi"], d["p"])
        others.append(dict(slug=d["slug"], title=d["title"], zone=[[round(x, 2), round(y, 2)] for x, y in d["zone"]],
                           body=[[round(x, 2), round(y, 2)] for x, y in d["body"]], env=rings(env.convex_hull if env.geom_type != "Polygon" else env)))

    # Knopf und Kordelgänge (Stand 8)
    Kd = K8.kordel(W_, L_)
    knopf = dict(c=[round(Kd["c"][0], 2), round(Kd["c"][1], 2)], plateau_r=K8.R_PLATEAU, kuppel_r=K8.R_RAMPE + K8.WAND, knopf_r=K8.R_KN,
                 hoecker=[rings(h)[0] for h in Kd["hoecker"]])

    # Stützenraster des Unterkastens Stand 8: Kandidaten, frei von allem außer der Dockzone des Augusteums (die prüft die App)
    body, plug, elec = Polygon(v["body"][0]), Polygon(v["plug"][0]), Polygon(v["elec"][0])
    inner = box(0, 0, W_, L_).buffer(-PP.UK_WALL, join_style=2)
    zones_o = [Polygon(o["zone"]) for o in others]
    hoeck_all = unary_union(Kd["hoecker"])
    block = [body.buffer(3), plug.buffer(3), elec.buffer(3), Kd["kuppel"].buffer(3), hoeck_all.buffer(1.5)] + [z.buffer(3) for z in zones_o]
    free0 = inner.buffer(-PP.POST[0]).difference(unary_union(block))
    no_pin = unary_union([Polygon(r) for b in v["buildings"] for r in b["poly"]] + [Polygon(r) for r in v["hof"]]).buffer(K8.TP_CLR + PP.PIN_PLAN["d"] / 2 + 1.5)
    cands = []
    for x in np.arange(PP.POST[1] / 2, W_, PP.POST[1]):
        for y in np.arange(PP.POST[1] / 2, L_, PP.POST[1]):
            r = box(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2)
            if free0.contains(r):
                cands.append(dict(x=round(float(x), 2), y=round(float(y), 2), pin_ok=not r.centroid.within(no_pin)))
    old_pins = [[round(Polygon(p["r"]).centroid.x, 2), round(Polygon(p["r"]).centroid.y, 2)] for p in v["posts"] if p["pin"]]

    sw = v["switch"]
    out = dict(
        plate=[W_, L_], to_welt=to_welt, outline=rings(poly(v["outline"])), hof=rings(poly(v["hof"])),
        buildings={b["slug"]: dict(title=b["title"], poly=b["poly"]) for b in v["buildings"]},
        aug=dict(slug=SLUG, name="Neues Augusteum", fp=rings(fp, sh, 3), hmax=round(hmax, 2), target=[round(tg.x + sh[0], 3), round(tg.y + sh[1], 3)],
                 grid=grid, start=start),
        variants=variants, dock=dict(zone=rings(zone_l)[0], body=rings(body_l)[0], env=rings(env_l.convex_hull if env_l.geom_type != "Polygon" else env_l)),
        others=others,
        fach=dict(fach=v["fach_poly"][0], body=v["body"][0], channel=v["channel"][0], plug=v["plug"][0], window=v["window"][0], cable=v["cable"]),
        elec=v["elec"][0], switch=dict(y=sw["y"], hole=sw["hole"], room=[0, round(sw["y"] - 7.0, 1), BC.SW_DEPTH, round(sw["y"] + 7.0, 1)]),
        knopf=knopf, posts=dict(cands=cands, size=PP.POST[0], old_pins=old_pins, pin_d=PP.PIN_PLAN["d"]),
        zapfen=[[20.0, 20.0], [100.0, 180.0]],
        k=dict(F0=TP.dims()["F"], delta=TP.MULDE_EXTRA_T, stop=TP.STOP_T, uk_wall=PP.UK_WALL, steckerraum=PP.STECKERRAUM_8, h_total=K8.H8,
               wall_min=0.8, wall_pref=1.2, dock_edge=1.0),
    )
    path = os.path.join(HERE, "data.json")
    json.dump(out, open(path, "w", encoding="utf-8"), separators=(",", ":"), default=float)
    print("Augusteum Start:", start, "Dockzonen der Nachbarn:", [o["slug"][:2] for o in others], "Stützen:", len(cands), "Pins alt:", old_pins)
    print("data.json: %.0f kB" % (os.path.getsize(path) / 1000))


if __name__ == "__main__":
    main()
