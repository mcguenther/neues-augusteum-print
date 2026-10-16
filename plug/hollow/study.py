#!/usr/bin/env python3
"""Hohlkörper-Studie: Kennzahlen und Zeichnungsdaten der sechs Gebäude für `plug/hollow/plan.html`.

Liest `stl/<quelle>/1zu1500/einzeln/*.stl` (Boden bei z=0, ohne Fuß), höhlt sie mit `hohl.py` aus (Wand und Dach 0,8 mm, unten offen, Gewölbe ab 10 mm Spannweite) und schreibt
`plug/hollow/study.json` (klein, eingecheckt): Maße, Schalenanteil, Brücken der Decke (Spannweitenklassen als Flächen für die Draufsicht),
Schnitt durch die Mitte. Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 1 min): python3 -m plug.hollow.study
"""
import json
import os
import sys
import time

import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

import hohl
from plug.hollow import shell as S

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "plug", "hollow", "study.json")
NAMES = ("01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus")
WALL, ROOF = 0.8, 0.8


def rings(g, tol=0.12):
    """Polygon(e) -> Liste Ringe [(x, y), ...] (Außen- und Innenringe), vereinfacht, auf 0,01 mm gerundet."""
    if g.is_empty:
        return []
    g = g.simplify(tol)
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if not isinstance(p, Polygon) or p.is_empty:
            continue
        out.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords[:-1]])
        for r in p.interiors:
            out.append([[round(x, 2), round(y, 2)] for x, y in r.coords[:-1]])
    return out


def intervals(g, y, axis=0):
    """Schnittintervalle (x0, x1) der Fläche g mit der Geraden bei y (axis=0, Schnitt in x-Richtung) bzw. bei x = y (axis=1, Schnitt in y-Richtung)."""
    if g.is_empty:
        return []
    if axis == 1:
        from shapely import transform
        g = transform(g, lambda a: a[:, ::-1])
    b = g.bounds
    ln = LineString([(b[0] - 1, y), (b[2] + 1, y)])
    it = g.intersection(ln)
    out = []
    for s in (it.geoms if hasattr(it, "geoms") else [it]):
        if s.is_empty or s.length < 1e-3:
            continue
        xs = [c[0] for c in s.coords]
        out.append([round(min(xs), 2), round(max(xs), 2)])
    return out


def best_cut(maxpt, lay):
    """Schnitt durch die größte freie Decke (Punkt maxpt aus der Brückenmessung) quer zur schmaleren Richtung: (axis, Wert)."""
    x, y, li = maxpt
    e = lay[max(li - 1, 0)][2]          # Hohlraum unter der Decke (die Lage li ist schon Decke)
    wx = max([b - a for a, b in intervals(e, y, 0) if a <= x <= b] or [1e9])
    wy = max([b - a for a, b in intervals(e, x, 1) if a <= y <= b] or [1e9])
    return (0, y) if wx <= wy else (1, x)


def main():
    res = {}
    for quelle in ("laserscan", "osm"):
        for name in NAMES:
            t0 = time.time()
            man = S.load(os.path.join(HERE, "stl", quelle, "1zu1500", "einzeln", name + ".stl"))
            layers = hohl.layers(man, WALL, ROOF, bruecke=hohl.BRUECKE)
            lay0 = hohl.layers(man, WALL, ROOF, bruecke=None)
            br0, classes0 = S.bridge_analysis(lay0)
            vol = man.volume()
            cav_vol = sum(S.LAYER * (e.area if not e.is_empty else 0.0) for _, _, e in layers)
            br, classes = S.bridge_analysis(layers)
            H = layers[-1][0]
            c_mid = layers[len(layers) // 3][1]
            axis, cy = (0, float(c_mid.centroid.y)) if name == "01_paulinum" or br0["maxpt"] is None else best_cut(br0["maxpt"], lay0)
            sect = [[z1, intervals(c, cy, axis), intervals(e, cy, axis)] for z1, c, e in layers]
            sect0 = [[z1, intervals(c, cy, axis), intervals(e, cy, axis)] for z1, c, e in lay0]
            cav0 = sum(S.LAYER * (e.area if not e.is_empty else 0.0) for _, _, e in lay0)
            # Hohlraum-Inseln je Höhe (abgeschlossene Kammern)
            islands = {}
            for hz in (2.0, 6.0, 12.0):
                k = min(len(layers) - 1, int(hz / S.LAYER))
                e = layers[k][2]
                islands[str(hz)] = 0 if e.is_empty else (len(e.geoms) if hasattr(e, "geoms") else 1)
            foot = layers[0][1]
            d = dict(H=round(H, 1), vol=round(vol), cav=round(cav_vol), shell=round(vol - cav_vol),
                     shell_pct=round(100 * (vol - cav_vol) / vol, 1),
                     foot=rings(foot, 0.1), cavity_low=rings(layers[min(len(layers) - 1, int(2.0 / S.LAYER))][2], 0.1),
                     cut_y=round(cy, 2), cut_axis=axis, sect=sect, sect0=sect0, cav_ohne_gewoelbe=round(cav0), islands=islands,
                     bridge=dict(maxr=round(br["maxr"], 2), maxr_ohne_gewoelbe=round(br0["maxr"], 2), area=round(br["area"]),
                                 area_cls={str(k): round(v) for k, v in br["area_cls"].items()}),
                     footprint_area=round(foot.area))
            # Draufsicht: je Spannweitenklasse die Vereinigung der Flächen
            d["bridge_polys"] = {str(k): rings(unary_union(v), 0.1) if v else [] for k, v in classes.items()}
            d["bridge_polys0"] = {str(k): rings(unary_union(v), 0.1) if v else [] for k, v in classes0.items()}
            res["%s/%s" % (quelle, name)] = d
            print("%-28s H=%5.1f  Schale %4.1f%%  max. Spannweite %.1f mm  %.1fs" % (
                quelle + "/" + name, H, d["shell_pct"], 2 * br["maxr"], time.time() - t0), flush=True)
    json.dump(res, open(OUT, "w"), separators=(",", ":"))
    print("->", os.path.relpath(OUT, HERE), "%d KB" % (os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    main()
