#!/usr/bin/env python3
"""Nimmt Flickr-Fotos (Openverse, CC BY / CC BY-SA, 2048 px) in den Messkatalog data/messfotos.json auf.

    python3 werkzeuge/farbmessung/katalog_flickr.py <katalog.json der Recherche> <nr> [<nr> ...]

Der Suchbereich der Pose (prior) steht hier je Foto, abgeschätzt aus Ansicht und Beschreibung:
  bereich = [xmin, xmax, ymin, ymax] in lokalen Metern (x Ost, y Nord, Ursprung generate.ORIGIN),
  yaw = [von, bis] Kompasskurs der Blickrichtung (0 = Nord, 90 = Ost), pitch/hfov in Grad.
Die Zeit ist die Aufnahmezeit laut Flickr (Ortszeit); „bedeckt“ markiert Fotos ohne Sonnenlicht.
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import registrierung as R

# nr: (gebaeude, bereich, yaw_von, yaw_bis, pitch, hfov, extra)
PRIOR = {
    71: ("02 01", [0, 90, -80, 20], 280, 345, (-3, 15), (45, 95), {}),
    72: ("01 02", [-10, 60, 20, 90], 245, 300, (0, 30), (35, 85), {}),
    82: ("02 01", [10, 110, -10, 80], 250, 295, (-3, 12), (45, 90), {}),
    83: ("01 02", [30, 120, -10, 70], 255, 305, (-3, 25), (30, 70), {}),
    84: ("06 01 02", [60, 210, -70, 50], 255, 305, (-3, 15), (35, 85), {}),
    85: ("06", [40, 210, -120, 20], 235, 295, (-3, 20), (30, 75), {}),
    88: ("01 02", [-10, 60, 35, 95], 235, 305, (5, 40), (40, 100), {}),
    92: ("01", [-10, 45, 45, 95], 235, 305, (10, 50), (40, 100), {}),
    87: ("08 02", [-135, -95, 0, 50], 60, 120, (-5, 20), (45, 90), {}),
    89: ("01 08 02", [-140, -90, -10, 60], 20, 110, (0, 30), (40, 90), {}),
    90: ("01", [-140, -90, 0, 60], 30, 110, (10, 45), (40, 100), {}),
    91: ("01 08 02", [-140, -90, -10, 60], 20, 110, (0, 30), (40, 90), {}),
    97: ("02", [-20, 50, -80, 0], 320, 390, (-3, 20), (45, 100), {}),
    98: ("02", [-15, 50, -5, 50], 240, 300, (0, 30), (40, 100), {}),
    99: ("01 02", [-10, 70, 30, 95], 235, 305, (0, 35), (35, 90), {}),
    100: ("02", [-10, 50, -75, -5], 320, 395, (-3, 20), (45, 100), {}),
    112: ("06", [-110, -20, -130, -60], 0, 360, (20, 55), (40, 100), {}),
    115: ("06 01 02", [40, 220, -100, 60], 235, 305, (-3, 15), (35, 85), {}),
    81: ("06 02 01", [30, 160, -40, 60], 245, 300, (-3, 12), (45, 95), {"bedeckt": True}),
}

if __name__ == "__main__":
    src = json.load(open(sys.argv[1]))
    by_nr = {x["nr"]: x for x in src}
    kat = R.lade_katalog()
    for nr in map(int, sys.argv[2:]):
        x, p = by_nr[nr], PRIOR[nr]
        fid = "fl_%s" % x["seite"].rstrip("/").split("/")[-1]
        os.makedirs(R.CACHE, exist_ok=True)
        shutil.copy(x["datei"], os.path.join(R.CACHE, fid + ".jpg"))
        e = dict(quelle="flickr", url=x["url"], seite=x["seite"], lizenz=x["lizenz"], urheber=x["urheber"],
                 zeit=x["datum"], gebaeude=p[0].split(), titel=x.get("titel", ""), licht=x["licht"],
                 prior=dict(bereich=p[1], yaw_bereich=[p[2], p[3]], pitch=list(p[4]), hfov=list(p[5]), z=[1.2, 3.5]))
        e.update(p[6])
        kat["fotos"].setdefault(fid, {}).update(e)
        print(nr, fid)
    R.speichere_katalog(kat)
