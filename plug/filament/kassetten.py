#!/usr/bin/env python3
"""Kassetten der sechs steckbaren Gebäude im Stand der Passung bei wechselnden Filamenten (19.10.2026): je Gebäude eine STL nach `stl/steckmodul_campus/kassetten/`.

Wie K5 der Passungsserie (`plug/filament/build.py`): Außenmaß des Unterbaus je Seite 0,07 kleiner als die Kassette der gebauten Gebäude (Spiel im Schacht 0,13 statt 0,06;
K4 mit 0,14 saß im Schacht noch zu locker), Buchsentasche in Breite und Tiefe insgesamt 0,10 enger (K4: die Buchse passt „fantastisch“) und 0,20 flacher (14,40 statt 14,60);
Oberkante des Unterbaus, Blatt und Anschlag bleiben, der Schacht der Gebäude ist unverändert. Kassettentyp je Gebäude aus `plug/testcase/params.py` (CASSETTE):
v4 (Paulinum, Neues Augusteum, Hörsaalgebäude), V1RS (Seminar-, Institutsgebäude), V2R (Hochhaus). Lage wie im Schacht (Unterkante z = 0, Tasche unten), also so, wie sie gedruckt wird.
Der LED-Streifen ist nicht in der STL (Kaufteil), wird aber mitgeprüft. Geprüft: dicht, Kollision der Kassette samt LED-Streifen mit dem fertigen Gebäude-STL
(Weltlage über `plug.buildings.place`), Streifen überschneidet die Kassette nicht und liegt auf Podest bzw. Blatt auf (Oberkante der Kassette wie im Schacht gebaut).

Aufruf (aus dem Wurzelverzeichnis, erst `python3 -m plug.buildings`):
    python3 -m plug.filament.kassetten
"""
import json
import os

import trimesh
from manifold3d import Manifold, Mesh

from plug import buildings as B
from plug import campus as C
from plug.geom import to_tm
from plug.testcase import kassette as KA
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_campus", "kassetten")
SPIEL = 0.13            # Spiel im Schacht je Seite wie K5 (K1 0,12 sehr stramm, K2 0,16 zu locker, K4 0,14 zu locker)
SCHLANK = SPIEL - P.KASS_CLR_T
TASCHE_ENGER = 0.10
TASCHE_FLACHER = 0.20


def kassette(var):
    if var == "v4":
        return KA.kassette4(tol=P.HSG_TOL_SAFE - TASCHE_FLACHER, schlank=SCHLANK, enger=TASCHE_ENGER)
    return V.kassette(var, schlank=SCHLANK, enger=TASCHE_ENGER, flacher=TASCHE_FLACHER)


def streifen(var):
    """LED-Streifenstück (10 × 16,7 × 2,2) in der Lage auf der Kassette, Konstruktionslage wie die Kassette."""
    if var == "v4":
        k = P.kass_dims()
        yc = (k["seat0"] + k["seat1"]) / 2
        return Manifold.cube([V.STRIP_W, V.STRIP_L, V.STRIP_T]).translate([-V.STRIP_W / 2, yc - V.STRIP_L / 2, k["top"]])
    return V.strip(var)


def mf(t):
    return Manifold(Mesh(vert_properties=t.vertices.astype("float32"), tri_verts=t.faces.astype("uint32")))


def main():
    os.makedirs(OUT, exist_ok=True)
    places = json.load(open(C.CACHE % P.SCALE_PLAN))
    ok = True
    for slug, var in P.CASSETTE.items():
        m = kassette(var)
        tm = to_tm(m)
        path = os.path.join(OUT, "%s_kassette_%s.stl" % (slug, var))
        tm.export(path)
        text = "  %-62s %5.2f × %5.2f × %5.2f mm  %5.0f mm³  dicht=%s" % (os.path.relpath(path, HERE), *tm.extents, tm.volume, tm.is_watertight)
        led = streifen(var)
        ueber = (mf(tm) ^ mf(to_tm(led))).volume()                      # Streifen in der Kassette (soll 0 sein)
        text += "  Streifen in Kassette %.3f mm³" % ueber
        ok &= ueber < 0.01
        if var == "v4":                                                 # Podest: Streifenunterseite liegt auf der Oberkante der Kassette
            ok &= abs(float(to_tm(led).bounds[0][2]) - float(tm.bounds[1][2])) < 1e-3
        gpath = os.path.join(B.OUT, "%s_1zu%d.stl" % (slug, P.SCALE_PLAN))
        if os.path.exists(gpath):
            yc = C.foot_local(var, 0.0).centroid.y
            gm = to_tm(B.place((m + led).translate([0, 0, -P.dims_plan()["F"]]), places[slug], yc))
            geb = trimesh.load(gpath)
            kol = (mf(geb) ^ mf(gm)).volume()
            text += "  Kollision Gebäude mit Kassette und Streifen %.3f mm³" % kol
            ok &= kol < 0.5
        ok &= bool(tm.is_watertight)
        print(text)
    print("alle dicht, keine Kollisionen" if ok else "ACHTUNG: nicht dicht oder Kollision")


if __name__ == "__main__":
    main()
