"""Planseite Unterkasten Stand 8: Kasten 5 mm höher, Knopfraum Ø 30 × 1,4 und acht Kordelgänge 8 × 5 für den Doktorhut, Heißkleber statt Fäden.

Zeigt den Kasten aus `plug/power/kasten8.py` (Powerbank am Platz von Stand 7, auf den Gangdächern über dem Knopf) im 3D-Zusammenbau mit
allen Teilen, die es gibt: Steckplatte, sechs Gebäude, Hof-Einsatz, Display-Gebäude (zweiter Satz), Unterkasten Stand 7 (gedruckt) zum Vergleich,
Powerbank, ESP32, Hauptschalter, Doktorhut mit Knopf und Kordel. Dazu Draufsicht, Höhenkette, Prüfzeilen, Hinweise und Entscheidungen.
Die Gebäude-STL werden für die Ansicht ausgedünnt (fast_simplification, sonst volle Netze).

Aufruf: python3 -m plug.power.build_plan_kasten8   (ca. 1 min)  ->  plug/power/plan_kasten8.html   (Vorlage plan_kasten8.template.html; Artifact)
Keine STL: der Kasten wird erst nach dem Abnicken gebaut.
"""
import json
import os
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
from plug.geom import encode  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.power import kasten8 as K8  # noqa: E402
from plug.power import params as PP  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "plan_kasten8.template.html")
OUT = os.path.join(HERE, "plan_kasten8.html")
STL = os.path.join(ROOT, "stl")
PLATE = os.path.join(STL, "steckmodul_campus", "steckplatte_1zu1300.stl")
HOF = os.path.join(STL, "steckmodul_campus", "hof_einsatz_1zu1300.stl")
GEB = os.path.join(STL, "steckmodul_campus", "gebaeude")
UK7 = os.path.join(STL, "steckmodul_unterkasten", "U_unterkasten.stl")
DECK = -BC.H0["plate_t"]                 # Unterseite der Steckplatte, z = −14,6 (Oberfläche 0)


def thin(tm, faces):
    """Netz für die Ansicht ausdünnen; ohne fast_simplification bleibt es voll."""
    if len(tm.faces) <= faces:
        return tm
    try:
        return tm.simplify_quadric_decimation(face_count=faces)
    except Exception as e:                  # noqa: BLE001
        print("  (nicht ausgedünnt: %s)" % e)
        return tm


def enc(tm, dx=0.0, dy=0.0, dz=0.0, faces=None):
    tm = tm.copy()
    tm.apply_translation([dx, dy, dz])
    return encode(thin(tm, faces) if faces else tm)


def ring(p):
    return [[round(float(x), 2), round(float(y), 2)] for x, y in list(p.exterior.coords)[:-1]]


def rings(g):
    return [ring(p) for p in G.polys_of(g)]


def var_data(r):
    return dict(
        H=r["H"], plus=r["plus"], total=r["total"], grams=r["grams"], pb_top=r["pb_top"], esp_top=r["esp_top"], esp_z0=r["esp_z0"],
        checks=[dict(n=n, ok=bool(ok), t=t) for n, ok, t in r["checks"]],
        body=ring(r["body"]), plug=ring(r["plug"]), win=ring(r["win"]), z0=r["z_pb"], unter_pb=r["unter_pb"], pb_luft=r["pb_luft"],
        posts=[dict(r=ring(p), pin=i in r["pins"]) for i, p in enumerate(r["posts"])], pin_rows=r["pin_rows"],
        esp_box=[round(float(x), 2) for x in G.to_trimesh(r["esp_m"]).bounds.flatten()],
        pb_box=[round(float(x), 2) for x in G.to_trimesh(r["pb_m"]).bounds.flatten()],
        plug_box=[round(float(x), 2) for x in G.to_trimesh(r["plug_m"]).bounds.flatten()],
        sw_z=r["sw"]["z"], mesh=enc(G.to_trimesh(r["uk"]), dz=DECK - r["H"]),
    )


def main():
    v = K8.stand7()
    W, L = v["plate"]
    res = K8.build(v)
    K = res["K"]

    plate = trimesh.load(PLATE)
    minx, miny = plate.bounds[0][:2]
    sh = (-minx, -miny)
    meshes = dict(plate=enc(plate, *sh, DECK), hof=enc(trimesh.load(HOF), *sh), buildings={})
    for f in sorted(os.listdir(GEB)):
        if f.endswith("_1zu1300.stl"):
            meshes["buildings"][f[:-12]] = enc(trimesh.load(os.path.join(GEB, f)), *sh, faces=12000)
    try:
        from plug import campus_display as CD
        from plug.display import body4 as B
        parts, _ = B.parts()
        s2 = CD.satz(2)
        meshes["display"] = {k: encode(G.to_trimesh(CD.pose(parts[k], s2, 0.0, 0.0, 0.0))) for k in ("body", "lid", "blende") if k in parts}
        disp = dict(mulde=ring(CD.mulde_poly()), zone=ring(CD.dock_zone()))
    except Exception as e:                  # noqa: BLE001
        print("Display nicht eingebaut:", e)
        meshes["display"], disp = {}, None
    uk7 = trimesh.load(UK7)
    meshes["uk7"] = enc(uk7, 0, 0, DECK - K8.H7)

    pins7 = [[round(Polygon(p["r"]).centroid.x, 1), round(Polygon(p["r"]).centroid.y, 1)] for p in v["posts"] if p["pin"]]
    data = dict(
        W=W, L=L, deck=DECK, plate_t=BC.H0["plate_t"], h7=K8.H7, floor=PP.UK_FLOOR, wall=PP.UK_WALL, gap=PP.STECKERRAUM, pb_t=K8.PB_T,
        adern=PP.ADERN_ZONE, esp_h=PP.ESP_H, knopf=PP.HUT_KNOPF, raum_d=2 * K8.R_KNOPF, kordel=PP.KORDEL, steckerraum=PP.STECKERRAUM_8, gang=PP.KORDEL_GANG, dach=PP.KORDEL_DACH, knopf_z=K8.KNOPF_Z, gang_z=K8.GANG_Z,
        knopf_h=K8.KNOPF_H, hut=PP.HUT, plug7=PP.PB_PLUG, pin=PP.PIN_PLAN, post=PP.POST,
        c=[round(K["c"][0], 2), round(K["c"][1], 2)], aus=K["aus"], gaenge=[rings(g) for g in K["gaenge"]], hoecker=[rings(g) for g in K["hoecker"]],
        notches7=[n["notch"] for n in v["vs"]], docks=[dict(slug=d["slug"], title=d["title"], zone=d["zone"]) for d in v["docks"] if d["ok"]],
        buildings=[dict(slug=b["slug"], title=b["title"], poly=b["poly"]) for b in v["buildings"]], hof=v["hof"], disp=disp,
        old=dict(body=v["body"][0], plug=v["plug"][0], win=v["window"][0], elec=v["elec"][0], posts=[p["r"] for p in v["posts"]], pins=pins7,
                 grams=v["material"]["uk"]),
        elec=v["elec"][0], sw=dict(y=PP.SW_Y, hole=PP.SW_HOLE, depth=BC.SW_DEPTH, z7=v["switch"]["z"]),
        v=var_data(res), meshes=meshes,
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=float))
    open(OUT, "w", encoding="utf-8").write(html)
    r = res
    print("Stand 8: Kasten %.1f (+%.1f), mit Platte %.1f, %s g, Prüfung %s" % (r["H"], r["plus"], r["total"], r["grams"][0],
                                                                         "alles ok" if all(c[1] for c in r["checks"]) else [c[0] for c in r["checks"] if not c[1]]))
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
