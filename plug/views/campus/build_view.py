#!/usr/bin/env python3
"""Interaktive 3D-Vorschau der Steckplatte (neu gegenüber der gedruckten Fassung): plug/views/campus/view.html.

Baut die Platte mit plug.campus.build() (Lagen aus der Zwischenspeicherung), legt die eingefrorene gedruckte Fassung
(plug/logbook/rounds/r7_steckplatte/steckplatte_v1_gedruckt.stl) daneben und schreibt eine einzelne HTML-Seite mit three.js
(cdnjs) und eingebetteten Dreiecken. Feste Ansichten gehören zu den Änderungen aus dem Rückmeldung zum ersten Druck.

Aufruf (aus dem Wurzelverzeichnis):
    python3 -m plug.views.campus.build_view
"""
import base64
import json
import os

import numpy as np
import trimesh
from shapely.geometry import Point as shapely_point
from shapely.geometry import Polygon
from shapely.ops import nearest_points, unary_union

import innenhof
from plug import campus as C
from plug.fit_test.generator import overhangs
from plug.geom import to_tm
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD = os.path.join(ROOT, "plug", "logbook", "rounds", "r7_steckplatte", "steckplatte_v1_gedruckt.stl")


def de(v, nd=1):
    return ("%.*f" % (nd, v)).replace(".", ",")


def pack(tm):
    """Dreiecke ohne Indizes als float32 (flache Schattierung), base64."""
    return base64.b64encode(np.asarray(tm.triangles, dtype="<f4").tobytes()).decode()


def main():
    plate, report, models, places, outline, hof_solid = C.build()
    tm = to_tm(plate)
    old = trimesh.load(OLD)
    ov = overhangs(plate, "steckplatte")
    d = P.dims_plan()
    T = C.plate_thickness(d)
    s = 1000.0 / P.SCALE_PLAN

    # Schrift: Ringe über der Plattenoberfläche liegen alle weiter innen als Fase + 0,3 mm
    rings = plate.slice(T + P.LABEL_RAISE_T / 2).to_polygons()
    text = [Polygon(r) for r in rings]
    inner = outline.buffer(-P.PLATE_TOP_CH_T - 0.3)
    text_ok = all(inner.contains(p) for p in text)
    tb = np.array([p.bounds for p in text])
    flat = outline.buffer(-P.PLATE_TOP_CH_T)
    clear = min(flat.exterior.distance(p) for p in text)
    label = ((tb[:, 0].min() + tb[:, 2].max()) / 2, (tb[:, 1].min() + tb[:, 3].max()) / 2)

    # Hof und Institutsgebäude: nächster Punkt zwischen Aussparung und Hof
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    hof = innenhof.flaeche_mm(list(fps.values()), s)
    pi, ph = nearest_points(fps["05_institutsgebaeude"], hof)
    nx, ny = (pi.x + ph.x) / 2, (pi.y + ph.y) / 2
    gap = pi.distance(ph)

    # Mulden-Rand: Mitte der längsten Kante des Institutsgebäudes, Kamera innen in der Mulde vor der Wand
    fp = fps["05_institutsgebaeude"]
    fp = max(fp.geoms, key=lambda g: g.area) if hasattr(fp, "geoms") else fp
    pts = list(fp.exterior.coords)
    a, c = max(zip(pts[:-1], pts[1:]), key=lambda e: np.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
    mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
    ex, ey = c[0] - a[0], c[1] - a[1]
    ln = np.hypot(ex, ey)
    nxv, nyv = -ey / ln, ex / ln
    if not fp.contains(shapely_point(mx + 0.3 * nxv, my + 0.3 * nyv)):
        nxv, nyv = -nxv, -nyv
    mulde_az = float(np.degrees(np.arctan2(nyv, nxv)))

    b = tm.bounds
    cx, cy = (b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2
    ymid_east = cy + 20
    views = [
        dict(name="Übersicht", t=[cx, cy, 7.0], d=370, az=-62, el=50, which="neu",
             text="Die ganze Platte, Gebäude-Mulden und Hof-Aussparung. Ziehen dreht, Rad zoomt."),
        dict(name="Schrift", t=[label[0], label[1], T + 0.3], d=62, az=-90, el=42, which="neu",
             text="Titel, Quellenzeile, Nordpfeil und „N“ stehen jetzt %s mm hoch auf der Oberseite, um die Breite der Randfase nach innen gerückt (Abstand zur ebenen Fläche min. %s mm). Mit „Gedruckt“ siehst du dieselbe Stelle graviert." % (de(P.LABEL_RAISE_T), de(clear))),
        dict(name="Oberkante", t=[b[1][0] - 7.0, b[0][1], T - 1.5], d=17, az=-90, el=4, which="neu",
             text="Blick auf die Stirnseite im Südosten: die obere Außenkante läuft mit einer Fase von %s mm unter 45° aus (in Schichtstufen). Im Druck wölbten sich dort die letzten 5 bis 7 Schichten nach außen." % de(P.PLATE_TOP_CH_T)),
        dict(name="Mulden-Rand", t=[mx, my, T - 0.5], d=8, az=mulde_az, el=18, which="neu",
             text="Blick aus der Mulde des Institutsgebäudes auf ihre Wand: oben läuft die Öffnung mit einer Einführfase von %s mm (in Stufen) aus, damit sie sich nicht wie beim Elefantenfuß zuzieht. Mit „Gedruckt“ ist die Kante scharf." % de(P.MULDE_CH_T)),
        dict(name="Hof und Institut", t=[nx, ny, T - 3.0], d=64, az=-90, el=58, which="neu",
             text="Die Grundrisse von Hof und Institutsgebäude liegen %s mm auseinander, die Wand zwischen den Aussparungen ist noch dünner und fehlte im Druck. Der Hof wird nach den Gebäuden eingesetzt, die Gebäude bilden dann die Trennwand." % de(gap)),
        dict(name="Unterseite", t=[cx, cy, 0.0], d=370, az=-62, el=-52, which="neu",
             text="Unverändert: ebene Unterseite, 24 Pin-Löcher (6 Gebäude × 4) mit Fase. Unten gab es keinen Elefantenfuß."),
    ]
    changes = [
        dict(name="Schrift erhaben", val="+%s mm" % de(P.LABEL_RAISE_T), view=1,
             text="Titel, Quellenzeile, Nordpfeil und „N“ lagen vertieft und waren nicht lesbar. Jetzt sitzen sie oben auf der Platte (L01: erhaben 0,5 bis 0,6 mm)."),
        dict(name="Fase an der Oberkante", val="%s mm × 45°" % de(P.PLATE_TOP_CH_T), view=2,
             text="Der Druck zeigte oben einen Wulst über die letzten 5 bis 7 Schichten. Die Fase ist deutlich tiefer als die 2 bis 3 Schichten der Bettfase. Nutzer: 1,5 bis 2 mm."),
        dict(name="Einführfase der Mulden", val="%s mm" % de(P.MULDE_CH_T), view=3,
             text="Alle Gebäude-Mulden bekommen oben eine kleine Fase, mindestens 0,5 mm, gegen das Zuquellen der Öffnung. Der Hof bleibt ohne."),
        dict(name="Hof-Trennwand", val="keine Änderung", view=4,
             text="Die 0,4 mm Wand zwischen Hof und Institut- oder Seminargebäude kam im Druck nicht. Das ist in Ordnung: erst die Gebäude einsetzen, dann den Hof."),
    ]
    data = dict(neu=pack(tm), alt=pack(old), views=views, changes=changes,
                dimNeu="%s × %s × %s mm" % (de(tm.extents[0]), de(tm.extents[1]), de(tm.extents[2])),
                dimAlt="%s × %s × %s mm" % (de(old.extents[0]), de(old.extents[1]), de(old.extents[2])))
    html = open(os.path.join(HERE, "view.template.html"), encoding="utf-8").read()
    for k, v in {"@DATA@": json.dumps(data, ensure_ascii=False),
                 "@DIM@": data["dimNeu"],
                 "@DICHT@": "ja" if tm.is_watertight else "NEIN",
                 "@OVERHANG@": "%.0f mm²" % ov["steep_area"],
                 "@HOEHE@": de(tm.extents[2]),
                 "@VOL@": de(tm.volume / 1000.0),
                 "@TEXT_OK@": "ja" if text_ok else "NEIN",
                 "@CLEAR@": de(clear)}.items():
        html = html.replace(k, v)
    path = os.path.join(HERE, "view.html")
    open(path, "w", encoding="utf-8").write(html)
    print("%s: %.1f MB, dicht=%s, Überhang %.0f mm², Schrift im Rand=%s, Wand Hof–Institut %.2f mm" % (
        os.path.relpath(path, ROOT), os.path.getsize(path) / 1e6, tm.is_watertight, ov["steep_area"], text_ok, gap))
    return tm.is_watertight and text_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
