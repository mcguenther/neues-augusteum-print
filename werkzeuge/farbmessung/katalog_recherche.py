#!/usr/bin/env python3
"""Nimmt Fotos aus einem Recherche-Katalog (Flickr/Wikimedia Commons über Openverse) in den Messkatalog
data/messfotos.json auf.

    python3 werkzeuge/farbmessung/katalog_recherche.py <katalog.json> <nr> [<nr> ...]

Eintrag der Recherche (je Foto): nr, datei (heruntergeladenes JPEG), url, seite, lizenz, urheber, datum (Ortszeit,
ISO), titel, licht, gebaeude, quelle_id ("flickr:<id>" oder "commons:<hash>"), prior mit bereich [xmin, xmax,
ymin, ymax] in lokalen Metern (x Ost, y Nord, Ursprung generate.ORIGIN), yaw_von/yaw_bis (Kompasskurs, 0 = Nord,
auch negativ), pitch, hfov (Grad). Die Kamerahöhe z wird hier aus der Geländehöhe am Standort gesetzt.
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import registrierung as R

Z_PLATZ = (1.5, 3.0)          # Augenhöhe über dem Platzniveau (z = 0,45 m) plus Spielraum
Z_HOF = (3.6, 4.9)            # Innenhof liegt 2,3 m höher


def fotoid(x):
    kind, _, ident = x["quelle_id"].partition(":")
    return ("fl_" if kind == "flickr" else "cm_") + ident


if __name__ == "__main__":
    src = json.load(open(sys.argv[1]))
    by_nr = {x["nr"]: x for x in src}
    kat = R.lade_katalog()
    for nr in map(int, sys.argv[2:]):
        x = by_nr[nr]
        p = x["prior"]
        fid = fotoid(x)
        os.makedirs(R.CACHE, exist_ok=True)
        shutil.copy(x["datei"], os.path.join(R.CACHE, fid + ".jpg"))
        hof = x["gebaeude"][0] == "08"
        e = dict(quelle="flickr" if fid.startswith("fl_") else "commons", url=x["url"], seite=x["seite"], lizenz=x["lizenz"],
                 urheber=x["urheber"], zeit=x["datum"], gebaeude=x["gebaeude"], titel=x["titel"], licht=x["licht"],
                 prior=dict(bereich=p["bereich"], yaw_bereich=[p["yaw_von"], p["yaw_bis"]], pitch=p["pitch"],
                            hfov=p["hfov"], z=list(Z_HOF if hof else Z_PLATZ)))
        kat["fotos"].setdefault(fid, {}).update(e)
        print(nr, fid)
    R.speichere_katalog(kat)
