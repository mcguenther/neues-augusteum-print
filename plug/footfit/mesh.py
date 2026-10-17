#!/usr/bin/env python3
"""Mesh und Schichtdaten des steckbaren Hohlgebäudes (City-Hochhaus) für die 3D-Vorschau der Planseite.

Quelle: stl/steckmodul_campus/gebaeude/06_city_hochhaus_1zu1300.stl (aus dem Branch jolly-pascal, `python3 -m plug.buildings`).
Schreibt plug/footfit/mesh.json: Dreiecke als Int16 (Einheit QUANT mm, base64) und je 0,2-mm-Lage Pfadlänge und Materialfläche (für die Druckzeit).
Aufruf: python3 -m plug.footfit.mesh   (ca. 1 min)
"""
import base64
import json
import os

import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stl", "steckmodul_campus", "gebaeude", "06_city_hochhaus_1zu1300.stl")
QUANT = 0.005
LAYER = 0.2


def main():
    m = trimesh.load(STL)
    m.merge_vertices()
    lo, hi = m.bounds
    ctr = (lo + hi) / 2
    tri = (m.triangles - ctr) / QUANT                        # Mitte als Ursprung, damit Int16 reicht
    assert np.abs(tri).max() < 32767
    q = np.round(tri).astype(np.int16).reshape(-1)
    lay = []
    z = lo[2] + LAYER / 2
    while z < hi[2]:
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            lay.append([0.0, 0.0])
        else:
            g = None                                           # Gerade-Ungerade über alle Ringe (Löcher ziehen sich ab)
            for ring in sec.discrete:
                r = Polygon(ring[:, :2]).buffer(0)
                g = r if g is None else g.symmetric_difference(r)
            lay.append([round(float(sec.length), 1), round(float(g.area), 1)])
        z += LAYER
    out = dict(quant=QUANT, center=[round(float(c), 3) for c in ctr], bounds=[[round(float(v), 3) for v in lo], [round(float(v), 3) for v in hi]],
               tris=base64.b64encode(q.tobytes()).decode(), ntri=len(m.faces), z0=round(float(lo[2]), 3), layer=LAYER, layers=lay,
               volume_cm3=round(float(m.volume) / 1000, 2))
    json.dump(out, open(os.path.join(HERE, "mesh.json"), "w"))
    print(len(m.faces), "Dreiecke,", len(lay), "Lagen, Volumen", out["volume_cm3"], "cm3, mesh.json", os.path.getsize(os.path.join(HERE, "mesh.json")) // 1024, "KB")
    print(lay[:3], lay[10], lay[100], lay[-3:])


if __name__ == "__main__":
    main()
