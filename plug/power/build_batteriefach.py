"""Batteriefach (Unterkasten) final: Übersichtsseite mit 3D-Ansicht, Draufsicht, Höhenkette und Schnittstelle zur Steckplatte.

Stand 7: Unterkasten ohne Zaun um die Powerbank (die Powerbank liegt lose, notfalls Heißkleber), Fenster in der Kante bleibt, Elektronik
als freie Fläche für das ESP32-DevKit (30 Pin, mit Isoband, keine Box), Hauptschalter in der Westwand. Geometrie und Lagen kommen aus
`build_concept.variant(1300)` (gleiche Platte wie die Konzeptseite); die Seite zeigt zusätzlich, was am Unterkasten an der Oberplatte hängt
(Schnittstelle: Außenmaß, Oberkante, Zapfen, Stützen, Eckaussparungen, Dockzonen) und wie viel Spielraum die Oberplatte dort noch hat.

Aufruf: python3 -m plug.power.build_batteriefach   (ca. 30 s)  ->  plug/power/batteriefach.html
Keine STL: der Unterkasten wird erst nach dem Abnicken gebaut.
"""
import json
import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from plug.power import build_concept as BC  # noqa: E402
from plug.power import params as PP  # noqa: E402
from plug.testcase import params as TP  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "batteriefach.template.html")
OUT = os.path.join(HERE, "batteriefach.html")


def _poly(rings):
    return unary_union([Polygon(r) for r in rings])


def interface(v):
    """Was am Unterkasten an der Oberplatte hängt, mit Spielraum (mm), den die Oberplatte dort noch hat."""
    outline = _poly(v["outline"])
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    posts = [Polygon(p["r"]) for p in v["posts"]]
    pins = [p for p in v["posts"] if p["pin"]]
    sw = v["switch"]
    switch_room = box(0, sw["y"] - 7.0, BC.SW_DEPTH, sw["y"] + 7.0)
    notches = [Polygon(x["notch"]) for x in v["vs"]]
    wall = outline.difference(inner)
    obst = unary_union(posts + notches + [wall])
    docks = []
    for d in v["docks"]:
        zone = Polygon(d["zone"])
        docks.append(dict(slug=d["slug"], title=d["title"], free=round(zone.distance(obst), 1),
                          near="Stütze" if zone.distance(unary_union(posts)) <= zone.distance(wall) else "Außenwand"))
    mulden = unary_union([_poly(b["poly"]).buffer(TP.OUTLINE_CLR_T) for b in v["buildings"]] + [_poly(v["hof"])])
    pin_rows = []
    for p in pins:
        c = Polygon(p["r"]).centroid
        hole = Point(c.x, c.y).buffer(PP.PIN_PLAN["d"] / 2 + PP.PIN_PLAN["clr"])
        pin_rows.append(dict(x=round(c.x, 1), y=round(c.y, 1), free=round(hole.distance(mulden), 1)))
    post_rows = [dict(x=round(Polygon(p["r"]).centroid.x, 1), y=round(Polygon(p["r"]).centroid.y, 1), pin=p["pin"]) for p in v["posts"]]
    elec = Polygon(v["elec"][0])
    return dict(
        outline=[round(float(x), 1) for x in outline.bounds], docks=docks, pins=pin_rows, posts=post_rows,
        notch_pad=PP.NOTCH_PAD, notch_free=round(min(n.distance(unary_union(posts)) for n in notches), 1),
        switch_free=round(switch_room.distance(unary_union(posts)), 1), switch_room=[0, round(sw["y"] - 7.0, 1), BC.SW_DEPTH, round(sw["y"] + 7.0, 1)],
        elec_box=[round(float(x), 1) for x in elec.bounds],
        elec_post=round(elec.distance(unary_union(posts)), 1),
    )


def final_variant():
    """Platte 1:1300 mit Unterkasten Stand 7 (ohne Zaun, ESP32-Fläche); `BC.LAST` hält danach den Kasten als Manifold (Rohkoordinaten)."""
    BC.FENCE_ON = False
    BC.WINDOW_OPEN = True
    BC.FIX_ON = True
    with BC.patched(PP, ESP_BOXES=PP.ESP_ZONES):
        return BC.variant(1300)


def main():
    v = final_variant()
    meshes = v.pop("meshes")
    h = BC.H0
    ifc = interface(v)
    assert all(abs(a - b) < 0.05 for a, b in zip(v["plate"], PP.UK_OUTLINE)), "Außenmaß weicht von UK_OUTLINE ab: %s" % v["plate"]
    inner_h = round(h["uk_t"] - PP.UK_FLOOR, 2)
    data = dict(
        v=v, meshes=meshes, ifc=ifc,
        h=dict(deck=h["deck"], uk_bot=h["uk_bot"], uk_t=round(h["uk_t"], 2), inner=inner_h, floor=PP.UK_FLOOR, plate_t=round(-h["deck"], 2),
               total=round(h["total"], 1), gap=PP.STECKERRAUM, body=h["body"], adern=PP.ADERN_ZONE,
               esp_free=round(inner_h - PP.ADERN_ZONE, 1), esp_h=PP.ESP_H, z_bm=h["z_bm"]),
        pb=dict(L=PP.PB_L, W=PP.PB_W, T=PP.PB_T + PP.PB_T_ZUSCHLAG, t0=PP.PB_T, g=PP.PB_G, plug=PP.PB_PLUG, cable=PP.PB_CABLE, clr=PP.PB_CLR, clr_z=PP.PB_CLR_Z,
                port_v=PP.PB_PORT_V),
        fach=dict(L=BC.FACH_L, W=BC.FACH_W, H=BC.FACH_H, u0=BC.U0, bu0=BC.BU0, bv0=BC.BV0, kv0=BC.KV0, win=BC.WIN),
        uk=dict(floor=PP.UK_FLOOR, wall=PP.UK_WALL, post=PP.POST, pin=PP.PIN_PLAN),
        esp=dict(board=PP.ESP_BOARD, tape=PP.ESP_TAPE, ring=PP.ESP_RING, h=PP.ESP_H, zones=[list(z) for z in PP.ESP_ZONES], old=list(PP.ESP_BOX)),
        sw=dict(hole=PP.SW_HOLE, wall=PP.SW_WALL, y=PP.SW_Y, depth=BC.SW_DEPTH), dock=BC.DK, v_ap=PP.V["apex"],
        grams=v["material"]["uk"],
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=float))
    open(OUT, "w", encoding="utf-8").write(html)
    print("Kopplung:", json.dumps({k: ifc[k] for k in ("docks", "pins", "notch_free", "switch_free", "elec_post")}, ensure_ascii=False, default=float))
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
